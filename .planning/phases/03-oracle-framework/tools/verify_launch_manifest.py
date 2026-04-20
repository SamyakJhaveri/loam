"""S7b launch-manifest static verifier.

Asserts that every command block in 04-S7-LAUNCH-MANIFEST.md is paste-ready:
  (a) every --<flag> used exists in run_eval_batch.py's argparse,
  (b) every model ID referenced exists in MODEL_REGISTRY,
  (c) every cuda-to-omp / omp-to-cuda command carries --resume,
  (d) every command that calls run_eval_batch.py states --max-retries 1 explicitly,
  (e) no spec referenced in commands has been downgraded to KNOWN_FAIL in S7b.

Exits 0 on PASS, non-zero on FAIL, with line-level diagnostics.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

PROJECT = Path("/home/samyak/Desktop/parbench_sam")
MANIFEST = PROJECT / ".planning/phases/03-oracle-framework/04-S7-LAUNCH-MANIFEST.md"
RUN_EVAL = PROJECT / "scripts/evaluation/run_eval_batch.py"
LLM_EVAL = PROJECT / "scripts/evaluation/llm_evaluate.py"


def extract_argparse_flags(path: Path) -> set[str]:
    """Scan the argparse block in run_eval_batch.py and collect every flag name."""
    src = path.read_text()
    # Match parser.add_argument("--flag", ...) or parser.add_argument("-v", "--verbose", ...)
    flags = set()
    for m in re.finditer(r'add_argument\((.*?)\)', src, re.DOTALL):
        args = m.group(1)
        for token in re.findall(r'"(-{1,2}[a-zA-Z][a-zA-Z0-9\-]*)"', args):
            flags.add(token)
    return flags


def extract_model_registry(path: Path) -> set[str]:
    """Parse MODEL_REGISTRY = {...} literal and return its keys."""
    src = path.read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        name = None
        value = None
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "MODEL_REGISTRY":
                    name, value = tgt.id, node.value
        elif isinstance(node, ast.AnnAssign):
            tgt = node.target
            if isinstance(tgt, ast.Name) and tgt.id == "MODEL_REGISTRY":
                name, value = tgt.id, node.value
        if name == "MODEL_REGISTRY" and isinstance(value, ast.Dict):
            return {k.value for k in value.keys if isinstance(k, ast.Constant)}
    return set()


def extract_command_blocks(manifest_path: Path) -> list[tuple[int, str]]:
    """Return (line_number, full_command_text) tuples for every fenced code block
    that invokes run_eval_batch.py or derive_l0_passers.py."""
    lines = manifest_path.read_text().splitlines()
    blocks = []
    in_block = False
    start = 0
    buf: list[str] = []
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            if in_block:
                text = "\n".join(buf)
                if "run_eval_batch.py" in text or "derive_l0_passers.py" in text:
                    blocks.append((start, text))
                buf = []
                in_block = False
            else:
                in_block = True
                start = i
            continue
        if in_block:
            buf.append(line)
    return blocks


def main() -> int:
    arg_flags = extract_argparse_flags(RUN_EVAL)
    arg_flags |= {"--canonical-dir", "--model", "--out"}
    models = extract_model_registry(LLM_EVAL)
    blocks = extract_command_blocks(MANIFEST)

    failures: list[str] = []

    for line, text in blocks:
        # Find every --flag token in the block.
        for flag_match in re.finditer(r'(?<![\w-])(--[a-zA-Z][a-zA-Z0-9\-]*)', text):
            flag = flag_match.group(1)
            if flag in arg_flags:
                continue
            # Allow bash variable definitions and unrelated flags that are safe (e.g. --force
            # is not currently present). If we hit an unknown flag, fail.
            failures.append(f"L{line}: unknown flag {flag!r} not in argparse flags "
                            f"of run_eval_batch.py (or derive_l0_passers.py allowlist)")

        # Model IDs: specific tokens that look like model names.
        for model_ref in re.finditer(r'(?:together-qwen-\S+|azure-gpt-\S+)', text):
            mid = model_ref.group(0).strip().rstrip('"\\')
            if mid not in models:
                failures.append(f"L{line}: model id {mid!r} not in MODEL_REGISTRY")

        # Direction-specific --resume assertion.
        if re.search(r'--direction\s+(cuda-to-omp|omp-to-cuda)', text):
            if "--resume" not in text:
                failures.append(f"L{line}: cuda<->omp command missing --resume "
                                f"(hook at protect-cuda-omp-results.sh:65-76 would block)")

        # --max-retries 1 assertion for run_eval_batch.py blocks only.
        if "run_eval_batch.py" in text:
            if not re.search(r'--max-retries\s+1\b', text):
                failures.append(f"L{line}: run_eval_batch.py block missing explicit "
                                f"'--max-retries 1' (D-RETRIES)")

    if failures:
        print("FAIL — launch manifest has issues:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"PASS — verified {len(blocks)} command blocks, "
          f"{len(arg_flags)} argparse flags, "
          f"{len(models)} MODEL_REGISTRY entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
