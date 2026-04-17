# Phase 2 CONTEXT Adversarial Review

**Reviewer:** critic (advisor, opus) · **Date:** 2026-04-16
**Files reviewed:**
- `.planning/phases/02-llm-eval-testing/02-CONTEXT.md`
- `.planning/STATE.md`
- `/home/samyak/.claude/plans/gsd-discuss-phase-2-elegant-lagoon.md` (source plan)

## Summary

The CONTEXT doc is broadly sound — line numbers (878, 956, 1000–1002, 861, 61–115, argparse block) all grep-verified; plan decomposition is atomic; decision set is coherent with §2.4 of the NeurIPS plan. **However, four factual errors block planning** (most damaging: the D-27 smoke-test kernel list references a constant name that does not exist in the codebase), and several SHOULD-FIX items expose either hidden scope (new result-JSON fields undeclared) or internal inconsistencies (`api_model` symmetry claim, `PROJECT_ROOT` constant naming). The STATE.md file is consistent but understates that 02-CONTEXT is not yet reflected in its "Decisions" section. Recommend FIX BLOCKING items, then proceed to `/gsd-plan-phase 2`.

## Findings

### MUST-FIX (blocking)

- **F-01** `02-CONTEXT.md:106` and `:146` · **Constant name is wrong.**
  D-27 and Canonical Refs cite `SUITE_SAMPLE_SPECS` from `tests/test_spec_loader_integration.py`. The actual constant in that file is **`SUITE_SPECS`** (line 34 of `tests/test_spec_loader_integration.py`). Verified via grep — `SUITE_SAMPLE_SPECS` returns zero matches project-wide.
  · Evidence: `grep -n SUITE_SAMPLE_SPECS` → no matches; `test_spec_loader_integration.py:34: SUITE_SPECS = {...}` with the exact 5 suite entries named.
  · Fix: Global replace `SUITE_SAMPLE_SPECS` → `SUITE_SPECS` in D-27 and the Canonical Refs bullet. Also rename in Phase 1 context alignment — Phase 1's `01-CONTEXT.md:25` uses the actual file's naming (it cites the 5 specs inline, not the constant, so Phase 1 is untouched).

- **F-02** `02-CONTEXT.md:145` · **`PROJECT_ROOT` constant name is wrong.**
  Canonical Refs says `tests/conftest.py — PROJECT_ROOT constant`. Actual `conftest.py` uses a **private** `_PROJECT_ROOT` (line 21); there is no public `PROJECT_ROOT` importable from conftest. Downstream plans that assume `from tests.conftest import PROJECT_ROOT` will break at import time.
  · Evidence: `tests/conftest.py:21` — `_PROJECT_ROOT = Path(__file__).parent.parent`. No public `PROJECT_ROOT`.
  · Fix: Either (a) say `_PROJECT_ROOT (private, module-local)` in D-28/Canonical Refs, making clear that Phase 2 tests must replicate the `Path(__file__).parent.parent` idiom rather than import, or (b) promote `_PROJECT_ROOT` → `PROJECT_ROOT` in `conftest.py` as a one-line scope addition to Plan 02-07. Option (b) matches what Phase 1 integration tests already pattern on (Phase 1's test files use their own module-local constants).

- **F-03** `02-CONTEXT.md:110` and `:161–162` · **Hidden new result-JSON fields.**
  D-09 locks `thinking_enabled` as the "only new top-level field", but D-29 smoke-test step 2 additionally asserts `num_samples` as a top-level field. Current result JSONs (verified against `results/evaluation/together-qwen-3.5-397b-a17b/rodinia-bfs-cuda-to-rodinia-bfs-omp-s0.json`) have **`sample_id`** and **`temperature`** and **`augment_level`** — but **no `num_samples`**. That means D-29 either (a) asserts a field that doesn't exist, or (b) silently expands the schema beyond what D-09 declares.
  · Evidence: `python3 -c "import json; print(sorted(json.load(open('results/evaluation/together-qwen-3.5-397b-a17b/rodinia-bfs-cuda-to-rodinia-bfs-omp-s0.json')).keys()))"` → has `temperature`, `sample_id`, `augment_level`; no `num_samples`, no `thinking_enabled`.
  · Fix: Reconcile D-09 and D-29. Either (i) add `num_samples` to D-09's new-field list (making the 02-03 commit scope wider) and document the schema bump in `.claude/rules/evaluation.md`, or (ii) change D-29 step 2 to assert `sample_id` instead of `num_samples` (which is what already exists). Choose (i) if downstream analysis needs to know the k in pass@k without grouping files; choose (ii) if `sample_id` is sufficient. Either way, record the decision.

- **F-04** `02-CONTEXT.md:67` and source plan `:66` · **Dangling `.continue-here.md` reference.**
  D-13 says "Skip `le_code/example_query.py` (external/untracked per `.continue-here.md` Infrastructure State)." There is **no `.continue-here.md` at the project root**. The file is at `.planning/.continue-here.md`.
  · Evidence: `ls /home/samyak/Desktop/parbench_sam/.continue-here.md` → No such file. `ls .planning/.continue-here.md` → exists; line 119 mentions `le_code/`.
  · Fix: Update the reference to `.planning/.continue-here.md` Infrastructure State (line 116–119 of that file).

### SHOULD-FIX (quality)

- **F-05** `02-CONTEXT.md:34` (D-01) · **`api_model` symmetry claim is inaccurate.**
  D-01 says "do not introduce a new `api_model` override field for Azure (keeps symmetry with the existing `azure-gpt-4.1` entry)". The symmetry claim is true *among Azure entries* (the existing `azure-gpt-4.1` has no `api_model`) — but MODEL_REGISTRY as a whole does use `api_model` for Together-AI (`llm_evaluate.py:112: "api_model": "Qwen/Qwen3.5-397B-A17B"`). A reader new to the codebase could read "the registry has no api_model field" from D-01. State the scope of symmetry narrowly.
  · Evidence: `llm_evaluate.py:110–114` (Qwen entry has `api_model`); `llm_evaluate.py:94–97` (Azure entry has no `api_model`).
  · Fix: Reword D-01 as: "do not introduce an `api_model` override for Azure — Azure already uses prefix-strip resolution; matching the existing `azure-gpt-4.1` entry. (`api_model` exists elsewhere in the registry, e.g. for Together-AI Qwen, where the displayed key and API model ID differ.)"

- **F-06** `02-CONTEXT.md:140` · **argparse range off by one.**
  Canonical Refs says `run_eval_batch.py:361–473 — argparse block`. The actual block is `362–473` (line 362 is `parser = argparse.ArgumentParser(...`). Line 361 is `def main() -> None:`. Not fatal — downstream implementers will find it — but triggers the line-number-drift discipline in CLAUDE.md. Fix to `362–473` or just `main() in run_eval_batch.py`.
  · Evidence: `grep -n argparse.ArgumentParser run_eval_batch.py` → line 362.

- **F-07** `02-CONTEXT.md:224` (Verification step #3) · **Grep command will still match historical docs as "live references".**
  `grep -rn "gpt-4\.1" scripts/ docs/ .planning/ tests/` will match:
  - `docs/guide_rerun_gpt41mini_evals.md` (historical guide, should remain per D-15 spirit)
  - `.planning/PROJECT.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/.continue-here.md` (all legitimately discuss the purge itself)
  - `docs/experimental_decisions_log.md` (historical record)
  - `.planning/codebase/{INTEGRATIONS,STRUCTURE}.md` (codebase snapshots)
  - `.planning/phases/02-llm-eval-testing/02-CONTEXT.md` (this doc!)
  The step says "historical references are OK" but doesn't define them. Implementer will hit hundreds of "matches" and need a triage rule. This is a verification step that doesn't actually verify.
  · Evidence: `grep -l gpt-4\.1 .planning/ docs/ -r` → 8 files in `.planning/`, 7 in `docs/`.
  · Fix: Replace step #3 with a targeted command that scopes to live code:
  ```bash
  grep -rn "gpt-4\.1" scripts/ tests/ --include='*.py' --include='*.sh' | grep -v 'results/evaluation/' | grep -v 'batch_.*\.json'
  ```
  And change the acceptance rule to: "returns zero live model-ID references in Python/shell source; markdown files in `docs/` and `.planning/` may legitimately mention the purged IDs as historical context."

- **F-08** `02-CONTEXT.md:108` · **D-29 assertion list is incomplete for what D-09 requires.**
  D-29 step 2 asserts `{thinking_enabled, temperature, num_samples, augment_level}`. It omits `sample_id` (which identifies the kth sample in pass@3) — critical for pass@k reconstruction. Also omits `model` (the whole point of the multi-model smoke). If the smoke test is the guardrail against result-schema drift, it should check all six fields.
  · Fix: Expand the D-29 assertion set to `{thinking_enabled, temperature, sample_id, augment_level, model, overall_status}`.

- **F-09** `02-CONTEXT.md:52` (D-10) and Phase 1 alignment · **Gemini line-number correctness.**
  D-10 says `llm_evaluate.py:956` is the Gemini `reasoning_effort="none"` line and "is not touched." Verified — line 956 is exactly `reasoning_effort="none",`. However, the "2026-04-16 incident" (in the briefing) notes that someone previously "fixed" `:879` → `:956` incorrectly. Azure's `reasoning_effort` injection point in D-08 is **878** (`response = client_az.chat.completions.create(...)` — the keyword-argument site within the call). Verified too. The CONTEXT doc gets both numbers right — commend, but flag that downstream plans must preserve this distinction and not conflate them (the historical incident hints that a fixer might "consolidate" both under one patch).
  · Fix (defensive): In 02-03 plan text, explicitly call out: "Do NOT modify line 956 (Gemini). Modify line 878 (Azure) by injecting `reasoning_effort=...` conditionally."

- **F-10** `02-CONTEXT.md:111` (D-30) · **Per-sample cost mislabel.**
  D-30 says "GPT-5.4 standard thinking ≈ $0.2/sample". The NeurIPS plan §3.1 line 144 says **$0.206/sample**, and calls the model **"GPT-5 standard (reasoning_effort=medium)"**, not "GPT-5.4". Registry uses `azure-gpt-5.4` as the *deployment* name (Le's naming, per PROJECT.md warning at line 3). Flag for consistency: "GPT-5.4" is ParBench's internal key; the Azure SKU/tier is "GPT-5 standard". Sanity: 5 kernels × 2 models × 3 samples = 30 samples total; 15 GPT-5 × $0.206 + 15 Qwen × $0.025 = $3.09 + $0.38 = **$3.47**, which is inside the $3–$5 claim. OK numerically.
  · Fix: Rename "GPT-5.4" → "GPT-5 standard tier via `azure-gpt-5.4` deployment" once in D-30 for traceability to the budget table.

- **F-11** `02-CONTEXT.md:147–153` (New Files Created) · **Test fixture files are missing from the list.**
  Section lists four new test files and the passer JSONs, but **02-02's test file `tests/test_model_registry.py` is absent from "New Files Created" (§Existing Code Insights)**. The plan table at line 205 references it, so the plan-level view is consistent, but the "New Files Created" canonical list is incomplete.
  · Fix: Add `tests/test_model_registry.py` and `tests/test_thinking_flag.py` (referenced in plan 02-03, also absent) to the New Files Created bullet list.

- **F-12** `02-CONTEXT.md:116` (Claude's Discretion) · **Load-bearing item.**
  "Exact argparse group structure (`mutually_exclusive_group` vs runtime check) in D-23" is under Claude's Discretion. This is **load-bearing** — D-26 test case 3 (`--task-list + --kernels → argparse error`) specifically depends on argparse-native enforcement. If the implementer picks runtime check, the test error message differs and the test needs rewriting. Lock this: use `mutually_exclusive_group` (argparse-native, auto-generated error message).
  · Fix: Move this decision out of Claude's Discretion and into D-23 as: "Implement via `parser.add_mutually_exclusive_group()` so the CLI rejects `--task-list + --kernels` with argparse's standard error message; D-26 test asserts that error message."

### CONSIDER (non-blocking)

- **F-13** `02-CONTEXT.md:41` (D-04) · **Four-way "True" list may drift.**
  D-04 enumerates which registry entries are `supports_thinking=True`: `azure-gpt-5.4`, `o3-2025-04-16`, `o4-mini-2025-04-16`, `together-qwen-3.5-397b-a17b`. The MODEL_REGISTRY (`llm_evaluate.py:61–115`) contains exactly those keys for o3 and o4-mini; Qwen exists; `azure-gpt-5.4` is the new entry. All 4 entries exist or are being added — good. However, `gpt-4.1-2025-04-14` is listed under the "purge" targets in D-11 but **not** under the supports_thinking=False list in D-04 (because it's being removed). The sequencing is correct (`D-04` adds the field to survivors only after `D-11` runs) — but D-04 should explicitly say "post-purge entries" or cite the plan ordering (`02-02 runs after 02-04`).
  · Fix: Add a one-liner: "D-04's enumeration assumes the purge (02-04) has already run. If 02-02 lands before 02-04, the `gpt-4.1-2025-04-14` entry would also need `supports_thinking=False`."
  · Note: The plan table orders 02-01 (add gpt-5.4) → 02-02 (add capability) → 02-03 (wire CLI) → 02-04 (purge). So 02-02 runs **before** 02-04. This means the purged entries **must** receive `supports_thinking=False` during 02-02, then get removed during 02-04. The current D-04 wording skips this transient state.

- **F-14** `02-CONTEXT.md:173` · **Marker registration scope.**
  Claims "`tests/` does not yet have an `llm` pytest marker. Register it in `tests/conftest.py` and `pyproject.toml` (or `pytest.ini` — confirm which configures markers in this repo)." Answer: **`pyproject.toml`** — verified. No `pytest.ini` exists. Remove the "(or pytest.ini — confirm…)" hedge; this is a grep-verifiable fact.
  · Fix: "Register in `pyproject.toml` `[tool.pytest.ini_options].markers` (no `pytest.ini` — markers are configured via pyproject per verified 2026-04-16)."

- **F-15** `02-CONTEXT.md:164` (Reusable Assets) · **`_load_complexity_lookup` mirror pattern.**
  Suggests mirroring `_load_complexity_lookup()` defensive `{}` fallback. Fine as a pattern, but `derive_l0_passers.py` is processing a *directory* of per-task JSONs, not a single CSV. The defensive-fallback analogue here is per-file parse error handling (e.g., skip unparseable JSON with warning), not `{}`. Slight analogy mismatch; could mislead the implementer into the wrong pattern.
  · Fix: Reframe as: "Use the same try/except-and-warn-continue pattern for per-file JSON parsing that `_load_complexity_lookup` uses for its CSV read; **not** a `{}` fallback for the whole input."

- **F-16** `02-CONTEXT.md:106` · **Kernel names lose the slug-normalization check.**
  D-27 lists `hecbench-bezier-surface-cuda`. Verified that `specs/hecbench-bezier-surface-cuda.json` AND `specs/hecbench-bezier-surface-omp.json` both exist, so `cuda-to-omp` smoke test is runnable. No fix needed; this is commendation with verification trail.
  · Evidence: `ls specs/hecbench-bezier-surface-*.json` → both exist.

- **F-17** `STATE.md:24` · **Minor stale-sounding line.**
  "Current focus: Phase 2: LLM Eval Testing (pending Tasks 7-8 code edits)". "Tasks 7-8" is a holdover from the older numbering scheme (when Phase 2 was "register gpt-5.4" = Task 7, etc.). Under the current 7-plan decomposition, those are `02-01` and `02-04`. Low priority — reader can figure it out — but tidy up to match the 02-NN plan numbering.
  · Fix: Change "pending Tasks 7-8 code edits" → "pending 7 atomic plans (02-01…02-07)".

- **F-18** `02-CONTEXT.md:142` · **Correct line range for Azure call site but missing post-header.**
  Says `llm_evaluate.py:878–883 — Azure call site`. Verified — the `client_az.chat.completions.create(...)` block spans 878–883. Good.
  · Evidence: Lines 878–883 read:
  ```
  response = client_az.chat.completions.create(
      model=azure_model,
      max_completion_tokens=32768,
      temperature=temperature,
      messages=full_messages,
  )
  ```
  · No fix — commend.

- **F-19** `02-CONTEXT.md:143` · **Qwen line range shifted by 5.**
  Says `llm_evaluate.py:1000–1002 — Qwen enable_thinking flag site`. Actual site is lines **1000–1002** for the `extra_body={...}` block — verified. Good.
  · No fix — commend.

- **F-20** `02-CONTEXT.md:140` · **MODEL_REGISTRY range verified.**
  Says `llm_evaluate.py:61–115`. Verified — dict spans exactly 61–115.
  · No fix — commend.

## Verification Evidence

Key grep outputs backing the findings:

```
# F-01
$ grep -rn SUITE_SAMPLE_SPECS /home/samyak/Desktop/parbench_sam
(no matches)

$ grep -n SUITE_SPECS /home/samyak/Desktop/parbench_sam/tests/test_spec_loader_integration.py
30:SPECS_DIR = PROJECT_ROOT / "specs"
34:SUITE_SPECS = {
35:    "rodinia": SPECS_DIR / "rodinia-bfs-cuda.json",
36:    "xsbench": SPECS_DIR / "xsbench-xsbench-cuda.json",
37:    "rsbench": SPECS_DIR / "rsbench-rsbench-cuda.json",
38:    "mixbench": SPECS_DIR / "mixbench-mixbench-cuda.json",
39:    "hecbench": SPECS_DIR / "hecbench-bezier-surface-cuda.json",

# F-02
$ grep -n PROJECT_ROOT /home/samyak/Desktop/parbench_sam/tests/conftest.py
21:_PROJECT_ROOT = Path(__file__).parent.parent
22:_RODINIA_SRC = _PROJECT_ROOT / "rodinia" / "rodinia-src"
23:_HECBENCH_SRC = _PROJECT_ROOT / "HeCBench-master"

# F-03 — result JSON keys (note: no thinking_enabled, no num_samples)
KEYS: ['attempts', 'augment_level', 'baseline_wall_time_seconds',
       'build_error_snippet', 'build_status', 'build_time_seconds',
       'completion_tokens', 'error_message', 'kernel',
       'llm_response_time_seconds', 'max_retries', 'metrics',
       'model', 'overall_status', 'prompt_tokens', 'run_args_mode',
       'run_arguments_used', 'run_exit_code', 'run_status',
       'run_stderr_snippet', 'run_stdout_snippet', 'run_time_seconds',
       'sample_id', 'source_spec', 'speedup_ratio',
       'target_files_expected', 'target_files_extracted', 'target_spec',
       'temperature', 'timestamp', 'timing_method', 'total_attempts',
       'translated_cpu_time_seconds', 'translated_files',
       'translated_kernel_time_seconds', 'translated_wall_time_seconds',
       'translation_mode', 'translation_type', 'verification_mode',
       'verify_status', 'verify_strategy']

# F-04 — .continue-here.md location
$ ls /home/samyak/Desktop/parbench_sam/.continue-here.md
(no such file)
$ ls /home/samyak/Desktop/parbench_sam/.planning/.continue-here.md
(exists)

# F-05 — api_model asymmetry
$ grep -n 'api_model' /home/samyak/Desktop/parbench_sam/scripts/evaluation/llm_evaluate.py
112:        "api_model": "Qwen/Qwen3.5-397B-A17B",

# F-06 — argparse starts at 362 not 361
$ grep -n 'argparse.ArgumentParser' /home/samyak/Desktop/parbench_sam/scripts/evaluation/run_eval_batch.py
362:    parser = argparse.ArgumentParser(

# F-09 — Azure and Gemini sites both verified
(Azure) llm_evaluate.py:878  response = client_az.chat.completions.create(
(Gemini) llm_evaluate.py:956  reasoning_effort="none",

# F-14 — pytest markers are in pyproject.toml
pyproject.toml:33:[tool.pytest.ini_options]
pyproject.toml:34:markers = [
pyproject.toml:35:    "integration: requires real benchmark files on disk (GPU machine only)",
(no pytest.ini exists)
```

## Out-of-Scope Findings (informational, not part of Phase 2)

- **(Memory guardrails):** The doc correctly cites `feedback_protect_cuda_omp_results`, `feedback_protect_qwen_results`, and `feedback_no_primary_benchmark`. No violations detected. D-15 explicitly protects existing result JSONs (correct); D-27 samples one spec per suite (respecting `feedback_no_primary_benchmark`).
- **(Undefined terms):** "pass@1-of-any" is defined in D-18 and PROJECT.md. "canonical" is defined via §2.4 reference. "L0-conditional ablation" is defined in §2.4. "reasoning_effort" is a standard OpenAI SDK term. All novel terms appear defined before use.
- **(Phantom sections):** No orphan headings detected.
