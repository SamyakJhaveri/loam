---
phase: 02-llm-eval-testing
plan: 08
type: execute
wave: 7
depends_on:
  - "02-01"
  - "02-02"
  - "02-03"
  - "02-05"
  - "02-06"
  - "02-07"
files_modified:
  - tests/test_eval_integration_smoke.py
  - docs/neurips2026-gpt5-handoff.md
autonomous: true
requirements: []
must_haves:
  truths:
    - "tests/test_eval_integration_smoke.py exists with Part 1 (dry-run matrix, @pytest.mark.integration only) and Part 2 (real-API E2E, @pytest.mark.integration + @pytest.mark.llm)"
    - "Dry-run matrix covers 5 suites × 6 directions × 2 models = 60 parametrized cases (minus KNOWN_FAIL and missing-target skips)"
    - "KNOWN_FAIL set is loaded at test-collection time by parsing .claude/rules/known-issues.md — NOT hard-coded"
    - "Real-API tests use tmp_path as --project-root and never touch the real results/evaluation/ tree"
    - "test_real_e2e_canonical_to_ablation: if canonical L0 produces 0 passers, pytest.fail is called — empty-passer is the signal, not a green light"
    - "pass@1-of-any defined on first use: a cell is a passer if ≥1 of its 3 canonical samples has overall_status == PASS (D-18)"
    - "Token+cost teardown fixture logs actual prompt_tokens + completion_tokens + estimated cost from result JSONs"
    - "docs/neurips2026-gpt5-handoff.md runbook contains all 8 required sections: context, repo setup, secrets, pre-flight, stage commands, output layout, cost model, artifact delivery"
    - "docs/neurips2026-gpt5-handoff.md pins reasoning_effort=medium as a hardcoded semantic of --thinking on (D-08), NOT a user-tunable flag"
    - "Azure pricing cited: $2.50/1M input, $15.00/1M output (verified 2026-04-17)"
  artifacts:
    - path: "tests/test_eval_integration_smoke.py"
      provides: "Integration smoke test: dry-run matrix + real-API E2E canonical→derive→ablation + omp-to-cuda direction independence"
      min_lines: 150
    - path: "docs/neurips2026-gpt5-handoff.md"
      provides: "GPT-5.4 campaign runbook for Le: repo setup, secrets, pre-flight, stage commands, cost model, artifact delivery"
      min_lines: 80
  key_links:
    - from: "SUITE_SPECS (tests/test_spec_loader_integration.py:34)"
      to: "dry-run parametrization (5 suites)"
      via: "dict values are Path objects; smoke test derives spec_id via Path.stem"
      pattern: "SUITE_SPECS"
    - from: ".claude/rules/known-issues.md KNOWN_FAIL table"
      to: "KNOWN_FAIL_IDS set in test module"
      via: "_load_known_fail_ids() parses markdown at collection time"
      pattern: "_load_known_fail_ids\\|KNOWN_FAIL_IDS"
    - from: "tmp_path (pytest fixture)"
      to: "--project-root flag in subprocess calls"
      via: "str(tmp_path) passed as --project-root; real results/ tree never touched"
      pattern: "tmp_path.*--project-root"
    - from: "pytest.fail"
      to: "zero-passer canonical result"
      via: "empty passer.json → pytest.fail with descriptive message"
      pattern: "pytest\\.fail"
---

<objective>
Plan 02-08 is "Integration smoke + GPT-5.4 handoff runbook". It folds three previously-proposed plans (02-08 dry-run matrix, 02-09 real-API ablation slice, 02-10 handoff runbook) into a single atomic plan per Karpathy's simplicity principles (S-1 minimum code, S-2 no speculative features, S-3 each changed line traces to the request).

The plan has three concerns:

**Part 1 — Zero-API dry-run matrix.** Exercises every (suite, direction, model) combination — 5 suites × 6 directions × 2 models = 60 cases — via `run_eval_batch.py --dry-run`. Widest surface coverage, zero API cost. Proves prompt construction + task-list-builder + CLI surface works for every direction the NeurIPS paper reports before Phase 3 spends any money.

**Part 2 — Two real-API E2E tests.** Exercises the full Phase 3 sequence — canonical → `derive_l0_passers` → `--task-list --augment-levels 1 2 3 4` — on one kernel pair for each of {Qwen, GPT-5.4}. A second test exercises one `omp-to-cuda` cell to prove direction independence. The highest-risk integration bug surface is `--task-list` × augmented source × Azure `reasoning_effort` × result-JSON schema; one traced E2E run on real API is the cheapest guardrail against burning money in Phase 3 on an undetected pipeline bug.

**Part 3 — `docs/neurips2026-gpt5-handoff.md`.** A plain-markdown runbook for Le to run GPT-5.4 on his own clone of the repo and hand back result JSONs. Contains repo setup, secrets checklist, pre-flight verification commands, Phase 3 stage commands with every flag pinned, output layout, cost model ($2.50/$15.00 Azure standard tier, verified 2026-04-17), and artifact delivery instructions.

**Terminology (defined on first use, per `feedback_explain_terms_first`):**
- *pass@1-of-any*: a (source, target) cell is a passer if ≥1 of its 3 canonical samples has `overall_status == "PASS"`. This is the filter D-18 in 02-CONTEXT.md uses to decide which cells proceed to ablation. It is deliberately permissive (one passing sample is enough) so the ablation exercises the broadest possible set of translation-capable kernels.

**Why not 02-07 alone?** Plan 02-07 exercises the canonical half (5 kernels × 2 models × cuda-to-omp, ~30 samples). Plan 02-08 extends this by (a) widening to all 6 directions via dry-run (zero cost), (b) tracing the full ablation path (canonical → derive → `--task-list`) on one kernel pair end-to-end, and (c) producing the runbook that unblocks Le's two-track Phase 3 execution.
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/phases/02-llm-eval-testing/02-CONTEXT.md
@.planning/phases/02-llm-eval-testing/02-07-eval-e2e-smoke-PLAN.md
@tests/test_spec_loader_integration.py
@tests/conftest.py
@.claude/rules/known-issues.md
@.claude/rules/evaluation.md
@scripts/evaluation/run_eval_batch.py
@./CLAUDE.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create tests/test_eval_integration_smoke.py</name>
  <files>tests/test_eval_integration_smoke.py</files>
  <read_first>
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md (D-16 derive_l0_passers CLI, D-18 pass@1-of-any filter, D-19 passer JSON schema, D-27 SUITE_SPECS, D-28 llm marker, D-30 cost model)
    - tests/test_spec_loader_integration.py:34 (SUITE_SPECS is a dict: suite_name → Path to JSON spec file; values are Path objects, NOT spec-id strings; derive spec_id via Path.stem, e.g. "rodinia-bfs-cuda")
    - tests/conftest.py (PROJECT_ROOT is public after 02-07; _PROJECT_ROOT is the private alias; llm marker skip gate uses PARBENCH_RUN_LLM_TESTS=1)
    - .claude/rules/known-issues.md §"KNOWN_FAIL Specs (8 — exclude from eval batches)" (parse the 8-entry table at collection time; do NOT hard-code)
    - .claude/rules/evaluation.md §"Result File Layout" and §"OMP Spec Run Argument Patterns"
    - scripts/evaluation/run_eval_batch.py (--dry-run, --task-list, --thinking, --augment-levels flags; all post-02-06)
    - scripts/evaluation/derive_l0_passers.py (post-02-05; --canonical-dir --model --out CLI)
  </read_first>
  <action>
Create `tests/test_eval_integration_smoke.py`. The file must contain:

**Module docstring** (document all three parts, cost model, worst-case envelope, candidate-kernel rule):
```
Phase 2 / Plan 02-08: Integration smoke + GPT-5.4 handoff runbook.

Three parts:
  Part 1 — Zero-API dry-run matrix: 5 suites × 6 directions × 2 models = 60 cases.
           Marker: @pytest.mark.integration ONLY (no llm). Runs on every default pytest tests/.
  Part 2 — Real-API E2E slice: canonical → derive_l0_passers → ablation on one kernel pair.
           Marker: @pytest.mark.integration + @pytest.mark.llm (gated by PARBENCH_RUN_LLM_TESTS=1).
  Part 3 — docs/neurips2026-gpt5-handoff.md: plaintext runbook for Le (documented separately).

Why this test exists (pre-Phase-3 guardrail):
  The highest-risk integration bug surface is --task-list × augmented source ×
  Azure reasoning_effort × result-JSON schema. If that path has a bug, we burn money
  in Phase 3. One dry-run matrix plus one real E2E canonical→derive→ablation trace
  is the cheapest guardrail.

Cost model (updated 2026-04-17 against live provider pricing):
  azure-gpt-5.4 (GPT-5 standard tier, Azure, <272K context):
    $2.50/1M input tokens, $15.00/1M output tokens
    Source: https://azure.microsoft.com/en-us/pricing/details/azure-openai/
    Per-sample assumption: 5k prompt + 20k output → ~$0.3125/sample
  together-qwen-3.5-397b-a17b (Together AI serverless):
    $0.60/1M input tokens, $3.60/1M output tokens
    Source: https://www.together.ai/models/qwen3-5-397b-a17b
    Per-sample assumption: 5k prompt + 20k output → ~$0.075/sample
  Reasoning tokens at reasoning_effort=medium bill as output tokens on both providers.
  Worst-case envelope ≈ $10/run (GPT-5.4 emitting ~80k output tokens/sample at 4× inflation).
  02-08 real-API budget: 8 samples × 2 models worst-case → ~$3.10 typical, ~$10 worst-case.

Candidate-kernel rule (D-19 / plan file §Part 2):
  CANDIDATE_SOURCE = "rodinia-bfs-cuda", CANDIDATE_TARGET = "rodinia-bfs-omp".
  These are candidates, NOT known passers. The canonical step determines pass/fail.
  If canonical produces 0 passers, pytest.fail is called — that IS the signal this
  test exists to catch before Phase 3 burns money on a broken code path.

pass@1-of-any (D-18): a (source, target) cell is a passer if ≥1 of its 3 canonical
  samples has overall_status == "PASS".
```

**Imports:**
```python
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import PROJECT_ROOT
from tests.test_spec_loader_integration import SUITE_SPECS
```

**Constants and helpers:**

1. `MODELS_UNDER_TEST = ["together-qwen-3.5-397b-a17b", "azure-gpt-5.4"]`

2. `DIRECTIONS = ["cuda-to-omp", "omp-to-cuda", "cuda-to-opencl", "opencl-to-cuda", "omp-to-opencl", "opencl-to-omp"]`

3. `CANDIDATE_SOURCE = "rodinia-bfs-cuda"` and `CANDIDATE_TARGET = "rodinia-bfs-omp"` — module-level constants with a comment that these are candidates, not known passers.

4. `_load_known_fail_ids()` helper:
```python
def _load_known_fail_ids() -> set[str]:
    """Parse the 8-entry KNOWN_FAIL table from .claude/rules/known-issues.md at collection time.

    Reads the markdown table under §"KNOWN_FAIL Specs (8 — exclude from eval batches)".
    Returns a set of spec_id strings like {'rodinia-kmeans-cuda', ...}.
    Never hard-codes the list — sourced from the authoritative known-issues.md.
    """
    known_issues_path = PROJECT_ROOT / ".claude" / "rules" / "known-issues.md"
    text = known_issues_path.read_text()
    # Find the KNOWN_FAIL section
    section_match = re.search(
        r"##\s+KNOWN_FAIL Specs.*?(?=\n##|\Z)", text, re.S
    )
    if not section_match:
        return set()
    section = section_match.group()
    # Parse table rows: | `spec-id` | ... |
    spec_ids = set()
    for line in section.splitlines():
        m = re.match(r"\|\s*`([a-z0-9][a-z0-9_-]+)`\s*\|", line)
        if m:
            spec_ids.add(m.group(1))
    return spec_ids


KNOWN_FAIL_IDS: set[str] = _load_known_fail_ids()
```

5. `_load_manifest_targets()` helper — reads manifest.jsonl at collection time, returns a `set[str]` of spec unique_ids that exist:
```python
def _load_manifest_targets() -> set[str]:
    """Read manifest.jsonl and return a set of all known spec unique_ids."""
    manifest_path = PROJECT_ROOT / "manifest.jsonl"
    ids: set[str] = set()
    with manifest_path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                uid = entry.get("unique_id")
                if uid:
                    ids.add(uid)
            except json.JSONDecodeError:
                continue
    return ids


MANIFEST_IDS: set[str] = _load_manifest_targets()
```

6. `_api_from_direction(direction)` helper that returns `(src_api, tgt_api)` tuple:
```python
def _api_from_direction(direction: str) -> tuple[str, str]:
    src, _, tgt = direction.partition("-to-")
    return src, tgt
```

**Part 1 — Dry-run matrix (marker: integration only, NOT llm):**

```python
def _dry_run_cases():
    """Build parametrize cases for dry-run matrix (5 suites × 6 directions × 2 models).

    SUITE_SPECS maps suite_name → Path to JSON spec file (dict shape from
    tests/test_spec_loader_integration.py:34). Spec-id is Path.stem, e.g. "rodinia-bfs-cuda".
    Kernel slug is derived by stripping the trailing -<api> suffix: "rodinia-bfs".
    """
    cases = []
    for suite, spec_path in SUITE_SPECS.items():
        spec_id = spec_path.stem  # e.g. "rodinia-bfs-cuda"
        # strip trailing -<api> to get kernel slug used by --kernels
        # convention: spec_id = <suite>-<kernel_slug>-<api>
        parts = spec_id.rsplit("-", 1)
        kernel_slug = parts[0].split("-", 1)[1] if len(parts) == 2 else spec_id
        for direction in DIRECTIONS:
            src_api, tgt_api = _api_from_direction(direction)
            # Derive expected source/target spec_ids
            src_spec_id = f"{suite}-{kernel_slug}-{src_api}"
            tgt_spec_id = f"{suite}-{kernel_slug}-{tgt_api}"
            for model in MODELS_UNDER_TEST:
                cases.append((suite, kernel_slug, direction, src_spec_id, tgt_spec_id, model))
    return cases


@pytest.mark.integration
@pytest.mark.parametrize(
    "suite,kernel_slug,direction,src_spec_id,tgt_spec_id,model",
    _dry_run_cases(),
    ids=[
        f"{s}-{k}-{d}-{m.split('-')[0]}"
        for s, k, d, _, _, m in _dry_run_cases()
    ],
)
def test_dryrun_matrix(suite, kernel_slug, direction, src_spec_id, tgt_spec_id, model):
    """Part 1: dry-run matrix — zero API calls, asserts prompt construction + task list."""
    # Skip if either source or target is a KNOWN_FAIL spec.
    if src_spec_id in KNOWN_FAIL_IDS:
        pytest.skip(f"source {src_spec_id!r} is in KNOWN_FAIL — skip")
    if tgt_spec_id in KNOWN_FAIL_IDS:
        pytest.skip(f"target {tgt_spec_id!r} is in KNOWN_FAIL — skip")
    # Skip if target spec does not exist in manifest (e.g. mixbench has no omp_target).
    if tgt_spec_id not in MANIFEST_IDS:
        pytest.skip(f"target {tgt_spec_id!r} not in manifest (suite {suite!r} may not have {_api_from_direction(direction)[1]!r} variant)")

    cmd = [
        sys.executable, "-m", "scripts.evaluation.run_eval_batch",
        "--suite", suite,
        "--kernels", kernel_slug,
        "--direction", direction,
        "--models", model,
        "--augment-levels", "0",
        "--num-samples", "1",
        "--temperature", "0.7",
        "--thinking", "on",
        "--dry-run",
        "--project-root", str(PROJECT_ROOT),
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=120
    )
    assert result.returncode == 0, (
        f"dry-run exited {result.returncode} for ({suite}, {direction}, {model})\n"
        f"stdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"
    )
    combined = (result.stdout + result.stderr).lower()
    # Dry-run must produce evidence of prompt construction (task listed) and no API call.
    assert "dry" in combined or "prompt" in combined or "task" in combined, (
        f"Dry-run output lacks prompt/task evidence.\nstdout: {result.stdout[:500]}"
    )
```

**Part 2 — Real-API E2E slice (markers: integration + llm):**

```python
@pytest.mark.integration
@pytest.mark.llm
@pytest.mark.parametrize("model", MODELS_UNDER_TEST)
def test_real_e2e_canonical_to_ablation(model, tmp_path):
    """Part 2a: full Phase 3 sequence on CANDIDATE_SOURCE→CANDIDATE_TARGET.

    Canonical (L0, 3 samples) → derive_l0_passers → ablation (L1–L4, 1 sample each).
    Uses tmp_path as --project-root; never touches real results/evaluation/ tree.

    CANDIDATE_SOURCE and CANDIDATE_TARGET are candidates, NOT known passers.
    If canonical L0 produces zero passers, pytest.fail is called — that is the signal.
    pass@1-of-any (D-18): cell is a passer if ≥1 of 3 canonical samples has overall_status==PASS.
    """
    suite = CANDIDATE_SOURCE.split("-")[0]  # "rodinia"
    kernel_slug = CANDIDATE_SOURCE[len(suite) + 1:CANDIDATE_SOURCE.rfind("-")]  # "bfs"

    # Step 1: Canonical run (L0, 3 samples)
    canonical_cmd = [
        sys.executable, "-m", "scripts.evaluation.run_eval_batch",
        "--suite", suite,
        "--kernels", kernel_slug,
        "--direction", "cuda-to-omp",
        "--models", model,
        "--augment-levels", "0",
        "--num-samples", "3",
        "--temperature", "0.7",
        "--thinking", "on",
        "--project-root", str(tmp_path),
        "-v",
    ]
    r = subprocess.run(
        canonical_cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=600
    )
    assert r.returncode == 0, (
        f"Canonical run failed.\nstdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )

    # Step 2: Assert 3 result JSONs with 02-03 schema fields
    model_results_dir = tmp_path / "results" / "evaluation" / model
    result_jsons = list(model_results_dir.rglob("*.json")) if model_results_dir.exists() else []
    assert result_jsons, f"No result JSONs in {model_results_dir}"
    for rf in result_jsons:
        data = json.loads(rf.read_text())
        for field in ("thinking_enabled", "num_samples", "augment_level", "temperature", "model", "overall_status", "sample_id"):
            assert field in data, f"{rf.name} missing field {field!r}"
        assert data["augment_level"] == 0
        assert data["num_samples"] == 3
        assert data["thinking_enabled"] is True
        assert data["temperature"] == 0.7
        assert data["model"] == model

    # Step 3: Derive L0 passers
    passer_json = tmp_path / "passer.json"
    derive_cmd = [
        sys.executable, "-m", "scripts.evaluation.derive_l0_passers",
        "--canonical-dir", str(model_results_dir),
        "--model", model,
        "--out", str(passer_json),
    ]
    r2 = subprocess.run(
        derive_cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=120
    )
    assert r2.returncode == 0, (
        f"derive_l0_passers failed.\nstdout: {r2.stdout}\nstderr: {r2.stderr}"
    )
    assert passer_json.exists(), "passer.json was not created"

    # Step 4: If empty passer list → pytest.fail (this IS the signal)
    passers = json.loads(passer_json.read_text())
    if not passers:
        pytest.fail(
            f"Canonical L0 for {CANDIDATE_SOURCE}→{CANDIDATE_TARGET}/{model} produced no passers. "
            "Ablation code path unexercised. "
            "Pick a different candidate kernel or investigate the canonical failure."
        )

    # Step 5: Ablation run (L1–L4, 1 sample each)
    ablation_cmd = [
        sys.executable, "-m", "scripts.evaluation.run_eval_batch",
        "--task-list", str(passer_json),
        "--models", model,
        "--augment-levels", "1", "2", "3", "4",
        "--num-samples", "1",
        "--temperature", "0.7",
        "--thinking", "on",
        "--direction", "cuda-to-omp",
        "--project-root", str(tmp_path),
        "-v",
    ]
    r3 = subprocess.run(
        ablation_cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=1200
    )
    assert r3.returncode == 0, (
        f"Ablation run failed.\nstdout: {r3.stdout[-2000:]}\nstderr: {r3.stderr[-2000:]}"
    )

    # Step 6: Assert 4 ablation result JSONs (one per level L1..L4)
    ablation_jsons = [
        rf for rf in model_results_dir.rglob("*.json")
        if rf.stem.endswith(("-L1", "-L2", "-L3", "-L4"))
    ]
    assert len(ablation_jsons) >= 4, (
        f"Expected ≥4 ablation JSONs (L1..L4), found {len(ablation_jsons)}: "
        + str([f.name for f in ablation_jsons])
    )
    ablation_levels = set()
    for rf in ablation_jsons:
        data = json.loads(rf.read_text())
        assert data["augment_level"] in (1, 2, 3, 4), f"{rf.name}: augment_level={data['augment_level']!r}"
        assert data["num_samples"] == 1, f"{rf.name}: num_samples={data['num_samples']!r}"
        for field in ("thinking_enabled", "num_samples", "augment_level", "temperature", "model", "overall_status", "sample_id"):
            assert field in data, f"{rf.name} missing field {field!r}"
        ablation_levels.add(data["augment_level"])
    assert ablation_levels == {1, 2, 3, 4}, f"Expected levels {{1,2,3,4}}, got {ablation_levels}"


@pytest.mark.integration
@pytest.mark.llm
@pytest.mark.parametrize("model", MODELS_UNDER_TEST)
def test_real_direction_independence_omp_to_cuda(model, tmp_path):
    """Part 2b: one real omp-to-cuda cell — proves direction swap is not cuda-to-omp-only.

    Canonical L0, num_samples=1 (pass@1) to cap spend.
    Uses tmp_path as --project-root.
    """
    suite = CANDIDATE_TARGET.split("-")[0]  # "rodinia"
    kernel_slug = CANDIDATE_TARGET[len(suite) + 1:CANDIDATE_TARGET.rfind("-")]  # "bfs"

    cmd = [
        sys.executable, "-m", "scripts.evaluation.run_eval_batch",
        "--suite", suite,
        "--kernels", kernel_slug,
        "--direction", "omp-to-cuda",
        "--models", model,
        "--augment-levels", "0",
        "--num-samples", "1",
        "--temperature", "0.7",
        "--thinking", "on",
        "--project-root", str(tmp_path),
        "-v",
    ]
    r = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(PROJECT_ROOT), timeout=600
    )
    assert r.returncode == 0, (
        f"omp-to-cuda run failed.\nstdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-2000:]}"
    )
    model_results_dir = tmp_path / "results" / "evaluation" / model
    result_jsons = list(model_results_dir.rglob("*.json")) if model_results_dir.exists() else []
    assert result_jsons, f"No result JSONs in {model_results_dir}"
    for rf in result_jsons:
        data = json.loads(rf.read_text())
        for field in ("thinking_enabled", "num_samples", "augment_level", "temperature", "model", "overall_status", "sample_id"):
            assert field in data, f"{rf.name} missing schema field {field!r} (D-29 / 02-03)"
        assert data["model"] == model
```

**Token-logging teardown fixture (module-scoped, autouse for llm-marked tests):**

```python
@pytest.fixture(autouse=True)
def _log_token_costs(request, tmp_path):
    """Teardown: read result JSONs from tmp_path and log actual token usage + estimated cost.

    Only active when the test uses tmp_path (real-API tests). Dry-run tests have no result JSONs.
    Pricing (2026-04-17):
      azure-gpt-5.4: $2.50/1M input, $15.00/1M output
      together-qwen-3.5-397b-a17b: $0.60/1M input, $3.60/1M output
    """
    yield  # run the test first
    # Only log if tmp_path contains result JSONs
    results_root = tmp_path / "results" / "evaluation"
    if not results_root.exists():
        return
    pricing = {
        "azure-gpt-5.4": (2.50 / 1_000_000, 15.00 / 1_000_000),
        "together-qwen-3.5-397b-a17b": (0.60 / 1_000_000, 3.60 / 1_000_000),
    }
    total_cost = 0.0
    for rf in results_root.rglob("*.json"):
        try:
            data = json.loads(rf.read_text())
        except Exception:
            continue
        model = data.get("model", "unknown")
        prompt_tokens = data.get("prompt_tokens", 0) or 0
        completion_tokens = data.get("completion_tokens", 0) or 0
        in_rate, out_rate = pricing.get(model, (0.0, 0.0))
        cost = prompt_tokens * in_rate + completion_tokens * out_rate
        total_cost += cost
        print(
            f"\n[token-log] {rf.name}: "
            f"prompt={prompt_tokens} completion={completion_tokens} "
            f"cost≈${cost:.4f} ({model})"
        )
    if total_cost > 0:
        print(f"\n[token-log] TOTAL estimated cost for this test: ${total_cost:.4f}")
```

The complete file must be at least 150 lines. All subprocess calls for real-API tests MUST contain `tmp_path` on the same line as `--project-root` (verification gate: `grep -q "tmp_path.*--project-root" tests/test_eval_integration_smoke.py`).
  </action>
  <verify>
    <automated>python3 -m pytest tests/test_eval_integration_smoke.py --collect-only -q 2>&1 | head -80</automated>
    <automated>grep -q "tmp_path.*--project-root" tests/test_eval_integration_smoke.py && echo OK</automated>
    <automated>grep -q "_load_known_fail_ids\|KNOWN_FAIL_IDS" tests/test_eval_integration_smoke.py && echo OK</automated>
    <automated>grep -q "pytest.fail" tests/test_eval_integration_smoke.py && echo OK</automated>
    <automated>grep -Eq "@pytest.mark.llm" tests/test_eval_integration_smoke.py && echo OK</automated>
    <automated>python3 -c "import ast, pathlib; src=pathlib.Path('tests/test_eval_integration_smoke.py').read_text(); ast.parse(src); print('syntax OK')"</automated>
  </verify>
  <acceptance_criteria>
    - `pytest --collect-only tests/test_eval_integration_smoke.py -q` lists at least 60 dry-run parametrized cases plus the real-API tests (minus KNOWN_FAIL/missing-target skips).
    - `grep -q "tmp_path.*--project-root" tests/test_eval_integration_smoke.py` exits 0.
    - `_load_known_fail_ids` function is present and parses .claude/rules/known-issues.md at collection time.
    - `pytest.fail` call is present (zero-passer guard).
    - `@pytest.mark.llm` marker appears on real-API test functions.
    - `_log_token_costs` fixture is present and autouse.
    - Module docstring contains cost model with "$2.50" and "pass@1-of-any" definition.
    - File is ≥150 lines.
  </acceptance_criteria>
  <done>tests/test_eval_integration_smoke.py created with Part 1 dry-run matrix, Part 2 real-API E2E + direction-independence tests, KNOWN_FAIL loader, manifest-target loader, and token-logging teardown fixture.</done>
</task>

<task type="auto">
  <name>Task 2: Create docs/neurips2026-gpt5-handoff.md (GPT-5.4 runbook for Le)</name>
  <files>docs/neurips2026-gpt5-handoff.md</files>
  <read_first>
    - i-want-you-to-drifting-salamander.md §"Part 3 — GPT-5.4 handoff runbook" and §"Concrete design of 02-08" (authoritative spec for the 8 required sections)
    - .claude/rules/evaluation.md §"Result File Layout" (canonical + ablation output paths)
    - .planning/phases/02-llm-eval-testing/02-CONTEXT.md D-08 (reasoning_effort=medium semantics), D-16 (derive_l0_passers CLI), D-19 (passer JSON schema)
    - .planning/ROADMAP.md Phase 3 SC-5 ($600 abort threshold) — for cost model section
  </read_first>
  <action>
Create `docs/neurips2026-gpt5-handoff.md` with exactly the 8 sections specified in the plan.

Required content anchors (every grep check in the `<verify>` block must pass):
- `AZURE_OPENAI_API_KEY` in secrets section
- `AZURE_OPENAI_ENDPOINT` in secrets section
- `reasoning_effort=medium` mentioned explicitly (as hardcoded semantic of --thinking on per D-08, NOT a user-tunable flag)
- "pre-flight" heading or phrase (Section 4)
- "$2.50" or "2.50/1M" in cost model section (verified 2026-04-17)
- `derive_l0_passers` command present
- `--task-list` flag present in ablation command
- `$559` tentative ceiling cited as pending Gal sign-off
- `$600` abort threshold cited (ROADMAP Phase 3 SC-5)
- No real API key values
  </action>
  <verify>
    <automated>ls docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -q "AZURE_OPENAI_API_KEY" docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -q "AZURE_OPENAI_ENDPOINT" docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -q "reasoning_effort=medium" docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -qi "pre-flight" docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -Eq '\$2\.50|2\.50/1M' docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -q "derive_l0_passers" docs/neurips2026-gpt5-handoff.md && echo OK</automated>
    <automated>grep -q "\-\-task-list" docs/neurips2026-gpt5-handoff.md && echo OK</automated>
  </verify>
  <acceptance_criteria>
    - File exists at docs/neurips2026-gpt5-handoff.md.
    - All 8 sections present: Context, Repo setup, Secrets checklist, Pre-flight verification, Phase 3 stage commands, Output layout + result JSON schema, Cost model, Artifact delivery.
    - reasoning_effort=medium documented as a semantic of --thinking on (D-08), NOT a separate CLI flag.
    - $559 tentative ceiling + $600 abort threshold both cited.
    - No real API key values anywhere in the file.
    - All verify greps pass.
    - File is ≥80 lines.
  </acceptance_criteria>
  <done>docs/neurips2026-gpt5-handoff.md created with all 8 sections, verified against grep checks.</done>
</task>

</tasks>

<verification>
The following checks from the plan's verification list apply to 02-08 (checks 1, 6, 8, 9, 10, 11):

- **Check 1** (total plans count): `ls .planning/phases/02-llm-eval-testing/02-0*-PLAN.md | wc -l` returns `8`. (W2 updates CONTEXT §Plan Decomposition; this plan is the 8th.)
- **Check 6** (runbook exists + content pins): `ls docs/neurips2026-gpt5-handoff.md` AND `grep -q 'AZURE_OPENAI_API_KEY' docs/neurips2026-gpt5-handoff.md && grep -q 'reasoning_effort=medium' docs/neurips2026-gpt5-handoff.md && grep -qi 'pre-flight' docs/neurips2026-gpt5-handoff.md && grep -Eq '\$2\.50|2\.50/1M' docs/neurips2026-gpt5-handoff.md`.
- **Check 8** (frontmatter validity): `python3 -c "import yaml; ... assert d['autonomous'] is True; assert d['must_haves']['truths']; assert d['must_haves']['artifacts']"` passes.
- **Check 9** (`<verify>` blocks have real commands): `grep -A 20 '<verify>' ... | grep -Eq 'pytest|grep|python3|ls'` passes.
- **Check 10** (`depends_on` pins): `grep -A 3 'depends_on:' ... | grep -q '02-05'` AND `'02-06'` AND `'02-07'` all pass. `'02-04'` must NOT appear.
- **Check 11** (`git status` shows only expected files): After execution, `git status` shows only `tests/test_eval_integration_smoke.py` and `docs/neurips2026-gpt5-handoff.md` as new files added by this plan (plus W2's files as their separate changes).
</verification>

<success_criteria>
- `tests/test_eval_integration_smoke.py` exists with ≥150 lines.
- `docs/neurips2026-gpt5-handoff.md` exists with ≥80 lines.
- Dry-run matrix is parametrized over 5 suites × 6 directions × 2 models = 60 cases (minus skips).
- Real-API tests use `tmp_path` as `--project-root` (never touch real results/).
- KNOWN_FAIL_IDS loaded at collection time from .claude/rules/known-issues.md — not hard-coded.
- Zero-passer guard (`pytest.fail`) is present in `test_real_e2e_canonical_to_ablation`.
- Token-logging teardown fixture is autouse and logs estimated cost at teardown.
- Runbook contains all 8 sections, all required content anchors, no real secrets.
- All frontmatter constraints satisfied (autonomous: true, depends_on excludes 02-04, must_haves non-empty).
- All Task 1 and Task 2 `<verify>` block commands exit 0 after execution.
</success_criteria>

<output>
After execution, create `.planning/phases/02-llm-eval-testing/02-08-SUMMARY.md` documenting:
(a) `pytest --collect-only tests/test_eval_integration_smoke.py -q` test count (total collected, skips noted).
(b) Dry-run matrix coverage: number of cases before and after KNOWN_FAIL/missing-target skips.
(c) Confirmation that real-API tests use `tmp_path` as `--project-root` (include the grep output).
(d) Token+cost log from the last real-API run (copy from teardown output or pytest -s output).
(e) Date executed and model used (model that produced the real-API results).
</output>
