#!/usr/bin/env python3
"""
scripts/evaluation/llm_evaluate.py — LLM-based code translation evaluation.

Given a source spec (e.g. CUDA) and target spec (e.g. OpenMP), sends the
source code to an LLM, asks it to translate to the target API, then runs the
harness build/run/verify pipeline on the translated code.

Metrics captured per ParEval (HPDC 2024), BabelTower (ICML 2022), LASSI-EE:
  - Compilation success rate
  - Functional correctness (Pass@1)
  - Performance preservation (speedup ratio via wall-clock timing)

Usage:
    python3 scripts/evaluation/llm_evaluate.py \\
        --source specs/rodinia-bfs-cuda.json \\
        --target specs/rodinia-bfs-omp.json \\
        --model claude-sonnet-4-20250514 \\
        --project-root /home/samyak/Desktop/parbench_sam -v

    python3 scripts/evaluation/llm_evaluate.py --list-models

    python3 scripts/evaluation/llm_evaluate.py \\
        --source specs/rodinia-bfs-cuda.json \\
        --target specs/rodinia-bfs-omp.json \\
        --model claude-sonnet-4-20250514 \\
        --project-root /home/samyak/Desktop/parbench_sam \\
        --dry-run -v
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import os
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any

# sys.path: scripts/evaluation/ -> scripts/ -> project_root/
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR.parent.parent))

from harness.builder import build_spec
from harness.models import MetricResult, RunResult, Status
from harness.runner import run_spec
from harness.spec_loader import get_prompt_payload, load_spec, resolve_paths
from harness.verifier import extract_metrics, verify_run

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL_REGISTRY: dict[str, dict[str, str]] = {
    "claude-sonnet-4-20250514": {
        "provider": "anthropic",
        "notes": "Primary eval model",
    },
    "claude-sonnet-4-6-20260218": {
        "provider": "anthropic",
        "notes": "Latest Sonnet",
    },
    "claude-opus-4-6-20260205": {
        "provider": "anthropic",
        "notes": "Strongest reasoning",
    },
    "claude-haiku-4-5-20251001": {
        "provider": "anthropic",
        "notes": "Fast/cheap baseline",
    },
    "gpt-4o": {
        "provider": "openai",
        "notes": "Strong general-purpose",
    },
    "gpt-4.1-2025-04-14": {
        "provider": "openai",
        "notes": "Latest GPT-4 class",
    },
    "o3-2025-04-16": {
        "provider": "openai",
        "notes": "Reasoning model",
    },
    "o4-mini-2025-04-16": {
        "provider": "openai",
        "notes": "Fast reasoning",
    },
    "azure-gpt-4.1": {
        "provider": "azure",
        "notes": "GPT-4.1 via Azure OpenAI (research lead deployment)",
    },
    "groq-llama-3.3-70b-versatile": {
        "provider": "groq",
        "notes": "Llama 3.3 70B via Groq (second eval model, Session 3)",
    },
    "gemini-2.5-flash-lite": {
        "provider": "google",
        "notes": "Gemini 2.5 Flash-Lite via Google AI (OpenAI-compatible endpoint)",
    },
}

# Human-readable API display names (fallback: .upper())
API_DISPLAY_NAMES: dict[str, str] = {
    "cuda": "CUDA",
    "hip": "HIP",
    "sycl": "SYCL",
    "opencl": "OpenCL",
    "omp": "OpenMP",
    "omp_target": "OpenMP Target Offload",
    "openacc": "OpenACC",
    "kokkos": "Kokkos",
    "raja": "RAJA",
    "mpi": "MPI",
    "omp_mpi": "OpenMP+MPI",
    "tbb": "Intel TBB",
    "stdpar": "C++ stdpar",
    "thrust": "Thrust",
    "serial": "Serial C/C++",
}

# Code fence language hint per API (used in prompts)
LANG_FOR_API: dict[str, str] = {
    "cuda": "cuda",
    "hip": "cpp",
    "sycl": "cpp",
    "opencl": "c",
    "omp": "cpp",
    "omp_target": "cpp",
    "openacc": "cpp",
    "kokkos": "cpp",
    "raja": "cpp",
    "mpi": "cpp",
    "omp_mpi": "cpp",
    "tbb": "cpp",
    "stdpar": "cpp",
    "thrust": "cpp",
    "serial": "c",
}

logger = logging.getLogger(__name__)

# Supported extensions for support file classification
_SUPPORT_HEADER_EXTS = frozenset({".h", ".hpp", ".cuh"})
_SUPPORT_CODE_EXTS = frozenset({".c", ".cpp", ".cu", ".cc", ".cxx"})


def _head_tail(text: str, max_len: int = 1500, head: int = 750, tail: int = 750) -> str:
    """Return head+tail of text if longer than max_len, else full text."""
    if len(text) <= max_len:
        return text
    return text[:head] + "\n...[truncated]...\n" + text[-tail:]


def _read_support_files(
    source_spec: dict[str, Any],
    project_root: Path,
    max_chars: int = 50_000,
) -> tuple[dict[str, str], dict[str, str]]:
    """Read support files from source spec, split into headers and code files.

    Returns:
        (headers_dict, code_dict) — both filename → content.
        headers_dict: all header files (.h, .hpp, .cuh)
        code_dict: code files (.c, .cpp, .cu, .cc, .cxx) up to max_chars cumulative
    """
    source_resolved = resolve_paths(source_spec, project_root)
    source_dir: Path = source_resolved["_resolved"]["source_dir"]
    support_names: list[str] = source_spec.get("files", {}).get("support_files", [])

    headers: dict[str, str] = {}
    code_files: dict[str, str] = {}
    code_chars = 0

    for fname in support_names:
        fp = source_dir / fname
        ext = Path(fname).suffix.lower()
        if ext in _SUPPORT_HEADER_EXTS:
            if fp.exists():
                headers[fname] = fp.read_text(encoding="utf-8", errors="replace")
            else:
                logger.warning("Support header not found on disk: %s", fp)
        elif ext in _SUPPORT_CODE_EXTS:
            if fp.exists():
                content = fp.read_text(encoding="utf-8", errors="replace")
                if code_chars + len(content) <= max_chars:
                    code_files[fname] = content
                    code_chars += len(content)
                else:
                    logger.debug(
                        "Skipping support code file %s (would exceed max_chars=%d)",
                        fname, max_chars,
                    )
        # Makefile, .sh, etc. are intentionally skipped

    return headers, code_files


def _read_target_infrastructure(
    target_spec: dict[str, Any],
    translation_targets: list[str],
    project_root: Path,
    max_chars: int = 50_000,
) -> dict[str, str]:
    """Read non-kernel files from the target spec as infrastructure context.

    Returns filename → content for:
    - prompt_payload files NOT in translation_targets (infrastructure source files)
    - support_files headers (.h, .hpp, .cuh) from the target spec

    The LLM sees these as read-only context — they exist in the target build
    directory and will not be modified.
    """
    target_resolved = resolve_paths(target_spec, project_root)
    source_dir: Path = target_resolved["_resolved"]["source_dir"]

    infrastructure: dict[str, str] = {}
    total_chars = 0
    tt_set = set(translation_targets)

    # Non-kernel prompt_payload files (everything in payload that the LLM won't produce)
    all_payload: list[str] = (target_spec.get("files") or {}).get("prompt_payload", [])
    for fname in all_payload:
        if fname in tt_set:
            continue
        fp = source_dir / fname
        if fp.exists():
            content = fp.read_text(encoding="utf-8", errors="replace")
            if total_chars + len(content) <= max_chars:
                infrastructure[fname] = content
                total_chars += len(content)
            else:
                logger.debug(
                    "Skipping target infra file %s (would exceed max_chars=%d)", fname, max_chars
                )

    # Support file headers from target spec (needed to understand interfaces)
    support_names: list[str] = (target_spec.get("files") or {}).get("support_files", [])
    for fname in support_names:
        if Path(fname).suffix.lower() not in _SUPPORT_HEADER_EXTS:
            continue
        fp = source_dir / fname
        if fp.exists():
            content = fp.read_text(encoding="utf-8", errors="replace")
            if total_chars + len(content) <= max_chars:
                infrastructure[fname] = content
                total_chars += len(content)
            else:
                logger.debug(
                    "Skipping target infra header %s (would exceed max_chars=%d)", fname, max_chars
                )

    return infrastructure


def _lang_hint_from_filename(fname: str) -> str:
    """Return a code fence language hint based on file extension."""
    ext = Path(fname).suffix.lower()
    return {
        ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp",
        ".cu": "cuda", ".cuh": "cpp",
        ".c": "c", ".h": "c", ".hpp": "cpp",
        ".cl": "c",
    }.get(ext, "c")


def _stage_support_headers(
    source_spec: dict[str, Any],
    target_spec_resolved: dict[str, Any],
    project_root: Path,
) -> list[Path]:
    """Copy source header files into target build directory (only if missing).

    Returns list of newly-created files for cleanup.
    """
    source_resolved = resolve_paths(source_spec, project_root)
    source_dir: Path = source_resolved["_resolved"]["source_dir"]
    target_dir: Path = target_spec_resolved["_resolved"]["source_dir"]
    support_names: list[str] = source_spec.get("files", {}).get("support_files", [])

    staged: list[Path] = []
    for fname in support_names:
        if Path(fname).suffix.lower() not in _SUPPORT_HEADER_EXTS:
            continue
        src_fp = source_dir / fname
        tgt_fp = target_dir / fname
        if src_fp.exists() and not tgt_fp.exists():
            tgt_fp.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_fp, tgt_fp)
            staged.append(tgt_fp)
            logger.debug("Staged header %s → %s", src_fp.name, target_dir)

    return staged


def _unstage_support_headers(staged_files: list[Path]) -> None:
    """Remove headers that were staged into the target build directory."""
    for fp in staged_files:
        fp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


def build_translation_prompt(
    source_spec: dict[str, Any],
    target_spec: dict[str, Any],
    source_payload: dict[str, str],
    project_root: Path,
    source_support: tuple[dict[str, str], dict[str, str]] | None = None,
    target_infrastructure: dict[str, str] | None = None,
) -> tuple[str, str]:
    """Build system + user messages for the translation request.

    Returns:
        (system_msg, user_msg) — both plain strings.
    """
    src_api = source_spec["identity"]["parallel_api"]
    tgt_api = target_spec["identity"]["parallel_api"]
    src_display = API_DISPLAY_NAMES.get(src_api, src_api.upper())
    tgt_display = API_DISPLAY_NAMES.get(tgt_api, tgt_api.upper())
    tgt_lang = LANG_FOR_API.get(tgt_api, "cpp")

    kernel_name = source_spec["identity"]["kernel_name"]
    description = source_spec["identity"].get("description", "")

    # Target filenames the LLM must produce (kernel-centric: always use translation_targets)
    target_filenames: list[str] = target_spec["files"]["translation_targets"]

    # Build command and environment from target spec
    build_cmd = (
        target_spec.get("build", {})
        .get("commands", {})
        .get("build", "(not specified)")
    )
    sys_deps: list[str] = (
        target_spec.get("build", {})
        .get("environment", {})
        .get("system", {})
        .get("dependencies", [])
    )

    # ---- System message ----
    system_msg = (
        f"You are a parallel programming expert specializing in {src_display} to "
        f"{tgt_display} translation. Translate the provided source code to {tgt_display}. "
        f"Output ONLY the translated code, no explanations. "
        f"For each file, output a markdown code fence with the filename on the opening line:\n\n"
        f"```{tgt_lang} filename={{filename}}\n<code>\n```\n\n"
        f"Preserve the algorithm, I/O behavior, data formats, and output format exactly. "
        f"The translated code must compile with the provided build command."
    )

    # ---- User message ----
    lines: list[str] = []
    lines.append("## Translation Task")
    lines.append(f"Kernel: {kernel_name}")
    if description:
        lines.append(f"Description: {description}")
    lines.append(f"Source API: {src_display} → Target API: {tgt_display}")
    lines.append("")

    lines.append("## Target Files to Produce")
    for fname in target_filenames:
        lines.append(f"- {fname}")
    if target_infrastructure:
        lines.append("")
        lines.append(
            "_These files will replace the corresponding files in the target project directory. "
            "All other project files (Makefile, headers, utilities) remain unchanged._"
        )
    lines.append("")

    lines.append("## Build Command (your code must work with this)")
    lines.append(f"```")
    lines.append(build_cmd)
    lines.append("```")
    lines.append("")

    if sys_deps:
        lines.append("## Build Environment")
        for dep in sys_deps:
            lines.append(f"- {dep}")
        lines.append("")

    lines.append(f"## Source Code ({src_display})")
    for fname, contents in source_payload.items():
        src_lang = LANG_FOR_API.get(src_api, "c")
        lines.append(f"### {fname}")
        lines.append(f"```{src_lang}")
        lines.append(contents)
        lines.append("```")
        lines.append("")

    if source_support:
        headers, code = source_support
        if headers or code:
            lines.append("## Support / Header Files")
            lines.append(
                "_These files exist in the **source** build directory but may NOT exist "
                "in the target directory. If your translated code needs definitions from "
                "them, inline the definitions directly rather than using `#include`._"
            )
            lines.append("")
            for fname, contents in {**headers, **code}.items():
                src_lang = LANG_FOR_API.get(src_api, "c")
                lines.append(f"### {fname}")
                lines.append(f"```{src_lang}")
                lines.append(contents)
                lines.append("```")
                lines.append("")

    if target_infrastructure:
        lines.append("## Target Infrastructure Context (DO NOT MODIFY — for reference only)")
        lines.append(
            "_These files exist in the target build directory and will NOT be modified. "
            "Your translated code must be compatible with them._"
        )
        lines.append("")
        for fname, contents in target_infrastructure.items():
            lang = _lang_hint_from_filename(fname)
            lines.append(f"### {fname}")
            lines.append(f"```{lang}")
            lines.append(contents)
            lines.append("```")
            lines.append("")

    user_msg = "\n".join(lines)
    return system_msg, user_msg


# ---------------------------------------------------------------------------
# LLM call (provider adapter)
# ---------------------------------------------------------------------------


def call_llm(
    model: str,
    system_msg: str,
    messages: list[dict[str, str]],
    verbose: bool = False,
) -> dict[str, Any]:
    """Call the LLM and return response + usage metadata.

    Args:
        model: Model ID string (routing by prefix).
        system_msg: System-level instruction string.
        messages: Conversation list of {"role": ..., "content": ...} dicts.
            Supports multi-turn for retry loops.
        verbose: Log request info to stderr.

    Returns:
        {response_text, prompt_tokens, completion_tokens, duration_seconds, finish_reason}

    Provider routing:
        claude-*          → Anthropic SDK (ANTHROPIC_API_KEY)
        gpt-* / o1-* / o3-* / o4-*  → OpenAI SDK (OPENAI_API_KEY)
        azure-*           → Azure OpenAI SDK (AZURE_OPENAI_API_KEY + AZURE_OPENAI_ENDPOINT)
                            Strips "azure-" prefix to get deployment name.
        groq-*            → OpenAI SDK (GROQ_API_KEY, base_url=https://api.groq.com/openai/v1)
                            Strips "groq-" prefix to get model name.
        gemini-*          → OpenAI SDK (GEMINI_API_KEY or GOOGLE_API_KEY,
                            base_url=https://generativelanguage.googleapis.com/v1beta/openai/)
                            Model name passed as-is (no prefix stripping).

    ParaCodex (future):
        Add `elif model.startswith("paracodex")` branch here.
        Same dict return format — rest of pipeline is unchanged.
    """
    t0 = time.monotonic()

    if model.startswith("claude-"):
        # ---- Anthropic path ----
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Set ANTHROPIC_API_KEY environment variable to use Anthropic models."
            )
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic package not installed. Run: python3 -m pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=api_key)
        if verbose:
            logger.info(
                "Calling Anthropic model=%s messages=%d", model, len(messages)
            )
        response = client.messages.create(
            model=model,
            max_tokens=16384,
            temperature=0,
            system=system_msg,
            messages=messages,
        )
        response_text: str = response.content[0].text
        prompt_tokens: int = response.usage.input_tokens
        completion_tokens: int = response.usage.output_tokens
        finish_reason: str = response.stop_reason or "unknown"

    elif model.startswith(("gpt-", "o1-", "o3-", "o4-")):
        # ---- OpenAI path ----
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Set OPENAI_API_KEY environment variable to use OpenAI models."
            )
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: python3 -m pip install openai"
            )

        client = openai.OpenAI(api_key=api_key)
        full_messages = [{"role": "system", "content": system_msg}] + messages
        if verbose:
            logger.info(
                "Calling OpenAI model=%s messages=%d", model, len(full_messages)
            )
        kwargs: dict[str, Any] = {
            "model": model,
            "max_completion_tokens": 16384,
            "messages": full_messages,
        }
        # o1/o3/o4 reasoning models do not accept temperature
        if not model.startswith(("o1-", "o3-", "o4-")):
            kwargs["temperature"] = 0

        response = client.chat.completions.create(**kwargs)
        response_text = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        finish_reason = response.choices[0].finish_reason or "unknown"

    elif model.startswith("azure-"):
        # ---- Azure OpenAI path ----
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        if not api_key:
            raise ValueError(
                "Set AZURE_OPENAI_API_KEY environment variable to use Azure models."
            )
        if not endpoint:
            raise ValueError(
                "Set AZURE_OPENAI_ENDPOINT environment variable to use Azure models."
            )
        try:
            from openai import AzureOpenAI
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: python3 -m pip install openai"
            )

        azure_model = model[len("azure-"):]  # e.g. "azure-gpt-4.1" → "gpt-4.1"

        # Strip any path/query from endpoint — SDK expects just scheme+host
        from urllib.parse import urlparse
        parsed = urlparse(endpoint)
        base_endpoint = f"{parsed.scheme}://{parsed.netloc}"

        client_az = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=base_endpoint,
            api_version="2025-01-01-preview",
        )
        full_messages = [{"role": "system", "content": system_msg}] + messages
        if verbose:
            logger.info(
                "Calling Azure OpenAI deployment=%s messages=%d", azure_model, len(full_messages)
            )
        response = client_az.chat.completions.create(
            model=azure_model,
            max_completion_tokens=16384,
            temperature=0,
            messages=full_messages,
        )
        response_text = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        finish_reason = response.choices[0].finish_reason or "unknown"

    elif model.startswith("groq-"):
        # ---- Groq (OpenAI-compatible) path ----
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "Set GROQ_API_KEY environment variable to use Groq models."
            )
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: python3 -m pip install openai"
            )

        groq_model = model[len("groq-"):]  # "groq-llama-3.3-70b-versatile" → "llama-3.3-70b-versatile"
        client_groq = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1",
        )
        full_messages = [{"role": "system", "content": system_msg}] + messages
        if verbose:
            logger.info(
                "Calling Groq model=%s messages=%d", groq_model, len(full_messages)
            )
        response = client_groq.chat.completions.create(
            model=groq_model,
            max_tokens=16384,
            temperature=0,
            messages=full_messages,
        )
        response_text = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        finish_reason = response.choices[0].finish_reason or "unknown"

    elif model.startswith("gemini-"):
        # ---- Google AI (OpenAI-compatible) path ----
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "Set GEMINI_API_KEY or GOOGLE_API_KEY environment variable to use Gemini models."
            )
        try:
            import openai
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: python3 -m pip install openai"
            )

        client_gemini = openai.OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        full_messages = [{"role": "system", "content": system_msg}] + messages
        if verbose:
            logger.info(
                "Calling Gemini model=%s messages=%d", model, len(full_messages)
            )
        response = client_gemini.chat.completions.create(
            model=model,
            max_tokens=16384,
            temperature=0,
            messages=full_messages,
        )
        response_text = response.choices[0].message.content or ""
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        finish_reason = response.choices[0].finish_reason or "unknown"

    else:
        raise ValueError(
            f"Unknown model provider for '{model}'. "
            "Expected prefix: claude-*, gpt-*, o1-*, o3-*, o4-*, azure-*, groq-*, gemini-*"
        )

    duration = time.monotonic() - t0
    return {
        "response_text": response_text,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "finish_reason": finish_reason,
        "duration_seconds": round(duration, 3),
    }


# ---------------------------------------------------------------------------
# Code block extraction
# ---------------------------------------------------------------------------


def extract_code_blocks(
    response_text: str,
    target_filenames: list[str],
) -> dict[str, str]:
    """Extract translated code from LLM response into a filename → code dict.

    Four-tier fallback:
        Tier 1   — Fenced blocks with ``filename=X`` annotation (Claude/GPT style).
        Tier 1.5 — Fenced blocks with space-separated filename (``lang filename.ext``; Llama style).
        Tier 2   — Filename mentioned near a code fence (fuzzy match).
        Tier 3   — Single target file + single code block in response.
    """
    result: dict[str, str] = {}

    # Tier 1: ```lang filename=X\n...\n```  (Claude / GPT-4 style)
    tier1_pattern = re.compile(
        r"```\w*\s+filename=([^\s`]+)\s*\n(.*?)```",
        re.DOTALL,
    )
    for match in tier1_pattern.finditer(response_text):
        raw_fname = match.group(1).strip("\"'")
        code = match.group(2)
        # Match against target filenames (exact or basename)
        for tgt in target_filenames:
            if tgt not in result and (
                raw_fname == tgt or Path(raw_fname).name == Path(tgt).name
            ):
                result[tgt] = code
                break

    unmatched = [f for f in target_filenames if f not in result]
    if not unmatched:
        return result

    # Tier 1.5: ```lang filename.ext\n...\n```  (Llama / space-separated style, no filename=)
    tier1b_pattern = re.compile(
        r"```\w*\s+([^\s`=]+\.[^\s`]+)\s*\n(.*?)```",
        re.DOTALL,
    )
    for match in tier1b_pattern.finditer(response_text):
        raw_fname = match.group(1).strip("\"'")
        code = match.group(2)
        for tgt in list(unmatched):
            if raw_fname == tgt or Path(raw_fname).name == Path(tgt).name:
                result[tgt] = code
                unmatched.remove(tgt)
                break

    if not unmatched:
        return result

    # Extract all generic code blocks for tiers 2 & 3
    generic_pattern = re.compile(r"```\w*\n(.*?)```", re.DOTALL)
    all_blocks = [m.group(1) for m in generic_pattern.finditer(response_text)]

    # Tier 2: filename mentioned within ~500 chars before a code fence
    for fname in list(unmatched):
        fname_pattern = re.compile(
            re.escape(fname) + r".{0,500}?```\w*\n(.*?)```",
            re.DOTALL,
        )
        m = fname_pattern.search(response_text)
        if m:
            result[fname] = m.group(1)
            unmatched.remove(fname)

    # Tier 3: exactly 1 target file remaining + exactly 1 code block total
    if len(unmatched) == 1 and len(all_blocks) == 1:
        result[unmatched[0]] = all_blocks[0]
        unmatched.clear()

    for fname in unmatched:
        logger.warning("Could not extract code for target file: %s", fname)

    return result


# ---------------------------------------------------------------------------
# File backup / restore
# ---------------------------------------------------------------------------


def backup_files(file_paths: list[Path]) -> dict[Path, bool]:
    """Copy each file to <path>.parbench_bak if it exists.

    Returns:
        dict mapping Path → bool (True = file existed before backup).
    """
    backup_info: dict[Path, bool] = {}
    for fp in file_paths:
        if fp.exists():
            shutil.copy2(fp, str(fp) + ".parbench_bak")
            backup_info[fp] = True
        else:
            backup_info[fp] = False
    return backup_info


def restore_files(backup_info: dict[Path, bool]) -> None:
    """Restore all backed-up files; delete any that were newly created."""
    for fp, existed in backup_info.items():
        bak = Path(str(fp) + ".parbench_bak")
        if existed and bak.exists():
            shutil.copy2(bak, fp)
            bak.unlink()
        elif not existed and fp.exists():
            fp.unlink()
        # Clean up orphaned .parbench_bak if original was removed
        if bak.exists():
            bak.unlink()


# ---------------------------------------------------------------------------
# Retry feedback
# ---------------------------------------------------------------------------


def _build_retry_message(
    build_result: Any | None,
    run_result: Any | None,
    verify_result: Any | None,
) -> str:
    """Format error feedback for the LLM retry message."""
    if build_result is not None and build_result.status != Status.PASS:
        # Trim to last 500 chars of stderr to stay within token budget
        stderr_snippet = (build_result.stderr or "")[-500:].strip()
        return (
            f"The translation failed to compile with this error:\n```\n"
            f"{stderr_snippet}\n```\nFix the code so it compiles with the "
            "provided build command."
        )
    if run_result is not None and run_result.status != Status.PASS:
        stderr_snippet = (run_result.stderr or "")[-300:].strip()
        return (
            f"The code compiled but execution failed (exit code {run_result.exit_code}):\n"
            f"```\n{stderr_snippet}\n```\nFix the runtime error."
        )
    if verify_result is not None and verify_result.status != Status.PASS:
        return (
            f"Build and run succeeded but output verification failed: "
            f"{verify_result.details}\n"
            "Ensure the translated code produces the same output format as the "
            "original."
        )
    return "The translation failed for an unknown reason. Please try again."


# ---------------------------------------------------------------------------
# Main orchestrator (importable by batch runner)
# ---------------------------------------------------------------------------


def evaluate_translation(
    source_path: Path,
    target_path: Path,
    model: str,
    project_root: Path,
    augment_level: int = 0,
    max_retries: int = 1,
    verbose: bool = False,
    dry_run: bool = False,
    use_cpu_timing: bool = False,
) -> dict[str, Any]:
    """Translate source → target using the LLM, then build/run/verify.

    Designed for import by run_eval_batch.py (Task 5).

    Args:
        source_path: Path to source spec JSON.
        target_path: Path to target spec JSON.
        model: LLM model ID string.
        project_root: Absolute path to parbench_sam root.
        augment_level: Augmentation level for source code (0 = no transforms).
        max_retries: Max LLM call attempts. 1 = zero-shot. >1 = iterative repair.
        verbose: Log verbose output.
        dry_run: Build and print prompt without calling LLM.
        use_cpu_timing: If True, measure CPU time (user+system) via
            /usr/bin/time -v when running translated code.  The cpu_time_seconds
            field is then preferred over wall_time_seconds for the speedup
            denominator (Linux/GNU time required).

    Returns:
        Result dict matching the schema documented in the plan.
    """
    source_spec = load_spec(source_path)
    target_spec = load_spec(target_path)
    target_spec_resolved = resolve_paths(target_spec, project_root)

    source_id = source_spec["identity"]["unique_id"]
    target_id = target_spec["identity"]["unique_id"]
    kernel_name = source_spec["identity"]["kernel_name"]

    if verbose:
        logger.info("Evaluating: %s → %s  model=%s", source_id, target_id, model)

    # Get source code (optionally augmented)
    source_payload = get_prompt_payload(source_spec, project_root, augment_level)

    # Read support files (headers + code) to include in prompt
    source_support = _read_support_files(source_spec, project_root)

    # Kernel-centric target filenames (all specs have translation_targets after SESSION 1.6)
    translation_mode = "kernel_centric"
    prompt_target_filenames: list[str] = target_spec["files"]["translation_targets"]

    # Read target infrastructure context (non-kernel files as read-only reference)
    # Returns {} for Family 3 specs where targets == prompt_payload (no infra to show)
    target_infrastructure = _read_target_infrastructure(
        target_spec, prompt_target_filenames, project_root
    )

    # Build prompt
    system_msg, user_msg = build_translation_prompt(
        source_spec, target_spec, source_payload, project_root,
        source_support=source_support,
        target_infrastructure=target_infrastructure,
    )

    if dry_run:
        print("=" * 70)
        print("SYSTEM MESSAGE")
        print("=" * 70)
        print(system_msg)
        print()
        print("=" * 70)
        print("USER MESSAGE")
        print("=" * 70)
        print(user_msg)
        return {
            "source_spec": source_id,
            "target_spec": target_id,
            "kernel": kernel_name,
            "model": model,
            "augment_level": augment_level,
            "dry_run": True,
            "overall_status": "DRY_RUN",
        }

    # Resolve target file paths for backup/restore
    # Use same kernel-centric target_filenames as the prompt (translation_targets or fallback)
    resolved: dict[str, Any] = target_spec_resolved.get("_resolved", {})
    source_dir: Path = resolved.get("source_dir", project_root)
    target_filenames: list[str] = prompt_target_filenames
    target_file_paths: list[Path] = [source_dir / fname for fname in target_filenames]

    # Backup originals (restored in finally regardless of outcome)
    backup_info = backup_files(target_file_paths)

    # Stage source headers into target build dir (safety net for missing includes)
    staged_headers = _stage_support_headers(source_spec, target_spec_resolved, project_root)

    # Baseline timing from target spec (may be null/absent)
    # Use `or {}` guard — .get(key, {}) returns None if key exists with null value
    baseline_wall_time: float | None = (
        (target_spec.get("baseline_results") or {})
        .get("configurations", {})
        .get("correctness", {})
        .get("wall_time_seconds")
    )

    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    attempts: list[dict[str, Any]] = []

    # Multi-turn conversation (supports iterative repair)
    messages: list[dict[str, str]] = [{"role": "user", "content": user_msg}]

    # Accumulated totals across attempts
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_llm_time = 0.0

    final_build_result = None
    final_run_result = None
    final_verify_result = None
    final_metrics: list[MetricResult] = []
    final_status = "ERROR"
    error_message: str | None = None
    last_llm_response: str = ""  # saved across loop iterations for preview

    try:
        for attempt_num in range(1, max_retries + 1):
            if verbose:
                logger.info("Attempt %d/%d", attempt_num, max_retries)

            attempt_record: dict[str, Any] = {
                "attempt": attempt_num,
                "llm_response_time_seconds": None,
                "prompt_tokens": None,
                "completion_tokens": None,
                "build_status": None,
                "run_status": None,
                "verify_status": None,
                "error_feedback_sent": None,
            }

            # -- Call LLM --
            try:
                llm_result = call_llm(model, system_msg, messages, verbose=verbose)
            except Exception as exc:
                error_message = f"LLM call failed: {exc}"
                logger.error(error_message)
                attempt_record["error"] = error_message
                attempts.append(attempt_record)
                break

            response_text = llm_result["response_text"]
            last_llm_response = response_text
            attempt_record["llm_response_time_seconds"] = llm_result["duration_seconds"]
            attempt_record["prompt_tokens"] = llm_result["prompt_tokens"]
            attempt_record["completion_tokens"] = llm_result["completion_tokens"]
            attempt_record["finish_reason"] = llm_result["finish_reason"]

            total_prompt_tokens += llm_result["prompt_tokens"]
            total_completion_tokens += llm_result["completion_tokens"]
            total_llm_time += llm_result["duration_seconds"]

            # -- Extract code blocks --
            extracted = extract_code_blocks(response_text, target_filenames)
            if verbose:
                logger.info(
                    "Extracted %d/%d target files", len(extracted), len(target_filenames)
                )

            # -- Warn on partial extraction: some files extracted but not all --
            # If only a subset is extracted, the build proceeds with the remaining
            # reference files intact — this can produce a misleading BUILD_FAIL
            # (wrong interface) or a false PASS (reference code runs correctly).
            if extracted and len(extracted) < len(target_filenames):
                missing = [f for f in target_filenames if f not in extracted]
                logger.warning(
                    "Partial extraction on attempt %d: extracted %d/%d target files; "
                    "missing: %s. Build will use original reference files for missing "
                    "targets — result may be misleading.",
                    attempt_num,
                    len(extracted),
                    len(target_filenames),
                    missing,
                )

            # -- Write extracted files to disk --
            for fname, code in extracted.items():
                fp = source_dir / fname
                fp.parent.mkdir(parents=True, exist_ok=True)
                fp.write_text(code, encoding="utf-8")

            # -- Guard: EXTRACTION_FAIL if no target files parsed from LLM response --
            # Building without extracted LLM code would compile the reference
            # implementation and produce a false-positive PASS. Fail fast instead.
            if not extracted:
                final_status = "EXTRACTION_FAIL"
                error_message = (
                    f"LLM response did not contain parseable code for any of the "
                    f"expected target files: {target_filenames}"
                )
                attempt_record["extraction_fail"] = True
                attempts.append(attempt_record)
                if attempt_num == max_retries:
                    break
                extraction_feedback = (
                    "Your response did not include any of the expected output files. "
                    "Please translate each target file using this format:\n\n"
                    + "".join(
                        f"```c {f}\n// your translated code here\n```\n\n"
                        for f in target_filenames
                    )
                )
                attempt_record["error_feedback_sent"] = extraction_feedback[:200]
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": extraction_feedback})
                restore_files(backup_info)
                backup_info = backup_files(target_file_paths)
                continue

            # -- Build --
            build_result = build_spec(
                target_spec_resolved, project_root, verbose=verbose
            )
            final_build_result = build_result
            attempt_record["build_status"] = build_result.status.value

            if build_result.status != Status.PASS:
                attempt_record["build_error_snippet"] = _head_tail(
                    build_result.stderr or ""
                )
                final_status = "BUILD_FAIL"
                error_message = f"Build failed: {(build_result.stderr or '')[-200:].strip()}"
            else:
                # -- Run --
                run_result = run_spec(
                    target_spec_resolved,
                    project_root,
                    verbose=verbose,
                    measure_cpu_time=use_cpu_timing,
                )
                final_run_result = run_result
                attempt_record["run_status"] = run_result.status.value

                if run_result.status != Status.PASS:
                    final_status = "RUN_FAIL"
                    error_message = f"Run failed (exit code {run_result.exit_code})"
                    attempt_record["run_stderr_snippet"] = (run_result.stderr or "")[-500:]
                    attempt_record["run_stdout_snippet"] = (run_result.stdout or "")[-500:]
                else:
                    # -- Verify --
                    verify_result = verify_run(target_spec, run_result)
                    final_verify_result = verify_result
                    attempt_record["verify_status"] = verify_result.status.value

                    # -- Extract metrics (stdout-parsed timing for HeCBench specs) --
                    final_metrics = extract_metrics(target_spec, run_result)

                    if verify_result.status == Status.PASS:
                        final_status = "PASS"
                        error_message = None  # clear any error from a previous attempt
                    else:
                        final_status = "VERIFY_FAIL"
                        error_message = f"Verify failed: {verify_result.details}"

            attempts.append(attempt_record)

            # If passed or last attempt, stop
            if final_status == "PASS" or attempt_num == max_retries:
                break

            # Build retry feedback for next attempt
            feedback = _build_retry_message(
                final_build_result, final_run_result, final_verify_result
            )
            attempt_record["error_feedback_sent"] = feedback[:200]  # abbreviated in record

            # Extend conversation: assistant response + user error feedback
            messages.append({"role": "assistant", "content": response_text})
            messages.append({"role": "user", "content": feedback})

            # Restore files to a clean state before the next attempt, so each
            # attempt starts from the original reference files (not stale LLM
            # output from the previous attempt).
            restore_files(backup_info)
            backup_info = backup_files(target_file_paths)

    finally:
        restore_files(backup_info)
        _unstage_support_headers(staged_headers)

    # -- Speedup ratio --
    # Numerator: baseline wall_time from the target spec (unchanged).
    # Denominator priority: kernel_time > cpu_time > wall_time.
    # Note: baseline is always wall_time (kernel/cpu baselines not stored in
    # specs yet), so mixing timing methods is imperfect but acceptable for now.
    translated_wall_time: float | None = None
    translated_cpu_time: float | None = None
    translated_kernel_time: float | None = None
    speedup_ratio: float | None = None
    timing_method: str | None = None

    if final_run_result is not None and final_run_result.status == Status.PASS:
        translated_wall_time = round(final_run_result.duration_seconds, 4)
        if final_run_result.cpu_time_seconds is not None:
            translated_cpu_time = round(final_run_result.cpu_time_seconds, 6)
        if final_run_result.kernel_time_seconds is not None:
            translated_kernel_time = round(final_run_result.kernel_time_seconds, 6)

        # Choose denominator with priority: kernel > cpu > wall
        if translated_kernel_time is not None:
            denominator = translated_kernel_time
            timing_method = "kernel_time"
        elif translated_cpu_time is not None:
            denominator = translated_cpu_time
            timing_method = "cpu_time"
        else:
            denominator = translated_wall_time
            timing_method = "wall_time"

        if baseline_wall_time and denominator:
            speedup_ratio = round(baseline_wall_time / denominator, 4)

    # -- Build result JSON --
    # last_llm_response was saved inside the loop before restore_files() ran
    extracted_last = extract_code_blocks(last_llm_response, target_filenames)
    translated_files_preview = {
        f: extracted_last[f][:200] for f in target_filenames if f in extracted_last
    }

    metrics_dict: dict[str, Any] = {}
    if final_metrics:
        metrics_dict = {m.name: {"value": m.value, "unit": m.unit} for m in final_metrics}

    result: dict[str, Any] = {
        "source_spec": source_id,
        "target_spec": target_id,
        "kernel": kernel_name,
        "model": model,
        "augment_level": augment_level,
        "translation_mode": translation_mode,
        "timestamp": timestamp,
        # LLM usage (totals across all attempts)
        "prompt_tokens": total_prompt_tokens,
        "completion_tokens": total_completion_tokens,
        "llm_response_time_seconds": round(total_llm_time, 3),
        # Build
        "build_status": (
            final_build_result.status.value if final_build_result else None
        ),
        "build_time_seconds": (
            round(final_build_result.duration_seconds, 3) if final_build_result else None
        ),
        "build_error_snippet": (
            _head_tail(final_build_result.stderr or "") if final_build_result and final_build_result.status != Status.PASS else None
        ),
        # Run
        "run_status": (
            final_run_result.status.value if final_run_result else None
        ),
        "run_time_seconds": (
            round(final_run_result.duration_seconds, 3) if final_run_result else None
        ),
        "run_exit_code": (
            final_run_result.exit_code if final_run_result else None
        ),
        "run_stderr_snippet": (
            (final_run_result.stderr or "")[-500:]
            if final_run_result and final_run_result.status != Status.PASS else None
        ),
        "run_stdout_snippet": (
            (final_run_result.stdout or "")[-500:]
            if final_run_result and final_run_result.status != Status.PASS else None
        ),
        # Verify
        "verify_status": (
            final_verify_result.status.value if final_verify_result else None
        ),
        "verify_strategy": (
            final_verify_result.strategy_used if final_verify_result else None
        ),
        # Overall
        "overall_status": final_status,
        "error_message": error_message,
        # Metrics / timing
        "metrics": metrics_dict,
        "baseline_wall_time_seconds": baseline_wall_time,
        "translated_wall_time_seconds": translated_wall_time,
        "translated_cpu_time_seconds": translated_cpu_time,
        "translated_kernel_time_seconds": translated_kernel_time,
        "timing_method": timing_method,
        "speedup_ratio": speedup_ratio,
        # Code
        "translated_files": translated_files_preview,
        "target_files_expected": target_filenames,
        "target_files_extracted": [
            f for f in target_filenames if f in translated_files_preview
        ],
        # Retry tracking
        "max_retries": max_retries,
        "total_attempts": len(attempts),
        "attempts": attempts,
    }

    # -- Save result to disk --
    out_dir = project_root / "results" / "evaluation" / model
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{source_id}-to-{target_id}.json"
    out_file.write_text(json.dumps(result, indent=2), encoding="utf-8")
    if verbose:
        logger.info("Result saved: %s", out_file)

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _print_models() -> None:
    """Print the model registry as a table."""
    print(f"{'Model ID':<40} {'Provider':<12} {'Notes'}")
    print("-" * 80)
    for model_id, info in MODEL_REGISTRY.items():
        print(f"{model_id:<40} {info['provider']:<12} {info['notes']}")
    print()
    print("Any model ID is accepted — the registry above is for reference only.")
    print("Routing: claude-* → Anthropic, gpt-*/o1-*/o3-*/o4-* → OpenAI, "
          "azure-* → Azure, groq-* → Groq, gemini-* → Google AI")


def _print_result(result: dict[str, Any], as_json: bool, verbose: bool) -> None:
    """Print final result to stdout."""
    if as_json:
        print(json.dumps(result, indent=2))
        return

    status = result.get("overall_status", "ERROR")
    src = result.get("source_spec", "?")
    tgt = result.get("target_spec", "?")
    model = result.get("model", "?")

    marker = "✓" if status == "PASS" else "✗"
    print(f"\n{marker} {src} → {tgt}  [{model}]  status={status}")
    print(
        f"  build={result.get('build_status')}  "
        f"run={result.get('run_status')}  "
        f"verify={result.get('verify_status')}"
    )
    if result.get("speedup_ratio") is not None:
        print(f"  speedup={result['speedup_ratio']:.3f}x  "
              f"(baseline={result.get('baseline_wall_time_seconds')}s  "
              f"translated={result.get('translated_wall_time_seconds')}s)")
    llm_time = result.get("llm_response_time_seconds")
    llm_time_str = f"{llm_time}s" if llm_time is not None else "N/A"
    print(
        f"  tokens={result.get('prompt_tokens')}+{result.get('completion_tokens')}  "
        f"llm_time={llm_time_str}  "
        f"attempts={result.get('total_attempts')}"
    )
    if result.get("error_message"):
        print(f"  error: {result['error_message']}")
    files_expected = result.get("target_files_expected", [])
    files_extracted = result.get("target_files_extracted", [])
    if verbose or files_expected != files_extracted:
        print(f"  files expected={files_expected}  extracted={files_extracted}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="LLM-based parallel code translation evaluation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Path to source spec JSON (e.g. specs/rodinia-bfs-cuda.json)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Path to target spec JSON (e.g. specs/rodinia-bfs-omp.json)",
    )
    parser.add_argument(
        "--model",
        help="Model ID string (e.g. claude-sonnet-4-20250514, gpt-4o)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        required=False,
        help="Absolute path to parbench_sam root directory (required for harness)",
    )
    parser.add_argument(
        "--augment-level",
        type=int,
        default=0,
        help="Augmentation level for source code (0=none, default: 0)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=1,
        help="Max LLM attempts with error feedback (1=zero-shot, default: 1)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Print result as JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print prompt without calling LLM",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="Print known model registry and exit",
    )
    parser.add_argument(
        "--use-cpu-timing",
        action="store_true",
        default=False,
        help=(
            "Measure CPU time (user+system) via /usr/bin/time -v when running "
            "translated code.  Uses cpu_time_seconds in speedup calculation "
            "instead of wall_time_seconds.  Linux only (GNU time required)."
        ),
    )
    parser.add_argument(
        "--use-profiler",
        action="store_true",
        default=False,
        help=(
            "Reserved for future kernel-level profiling (e.g. nsys/nvprof). "
            "Not yet implemented; accepted but has no effect."
        ),
    )

    args = parser.parse_args()

    if args.list_models:
        _print_models()
        return

    # Validate required args for non-list-models mode
    missing = []
    if not args.source:
        missing.append("--source")
    if not args.target:
        missing.append("--target")
    if not args.model:
        missing.append("--model")
    if not args.project_root:
        missing.append("--project-root")
    if missing:
        parser.error(f"Required arguments missing: {', '.join(missing)}")

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )

    project_root: Path = args.project_root.resolve()

    result = evaluate_translation(
        source_path=args.source,
        target_path=args.target,
        model=args.model,
        project_root=project_root,
        augment_level=args.augment_level,
        max_retries=args.max_retries,
        verbose=args.verbose,
        dry_run=args.dry_run,
        use_cpu_timing=args.use_cpu_timing,
    )

    _print_result(result, as_json=args.as_json, verbose=args.verbose)


if __name__ == "__main__":
    main()
