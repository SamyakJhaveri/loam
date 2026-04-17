---
phase: 02-llm-eval-testing
plan: 08
plan_name: integration-smoke-and-handoff
subsystem: scripts/evaluation, tests, docs
tags: [tests, integration-smoke, handoff-runbook, gpt-5.4, dry-run-matrix, neurips]
dependency_graph:
  requires:
    - 02-01-add-azure-gpt54-registry
    - 02-02-supports-thinking-capability
    - 02-03-thinking-cli-flag
    - 02-05-derive-l0-passers
    - 02-06-task-list-flag
    - 02-07-eval-e2e-smoke
  provides:
    - dry-run integration matrix (5 suites × 6 directions × 2 models)
    - real-API E2E canonical→derive→ablation guardrail (gated by PARBENCH_RUN_LLM_TESTS=1)
    - GPT-5.4 handoff runbook for Le (8 sections, all anchors verified)
  affects:
    - tests/test_eval_integration_smoke.py
    - docs/neurips2026-gpt5-handoff.md
tech_stack:
  added: []
  patterns:
    - "collection-time KNOWN_FAIL parsing from .claude/rules/known-issues.md (single source of truth)"
    - "manifest-derived target spec set (suite-kernel-api) — skips missing variants gracefully"
    - "parametrized dry-run matrix using llm_evaluate.py --dry-run (run_eval_batch.py has no --dry-run)"
    - "tmp_path as --project-root for real-API tests (never touches results/evaluation/)"
    - "autouse teardown fixture logs token usage + estimated cost"
key_files:
  created:
    - tests/test_eval_integration_smoke.py
  modified:
    - docs/neurips2026-gpt5-handoff.md  # pre-flight 4a/4d fixed (run_eval_batch has no --dry-run)
decisions:
  - "Dry-run matrix uses llm_evaluate.py --dry-run, not run_eval_batch.py --dry-run (the batch launcher has no such flag, per 02-07 module docstring; both call the same evaluate_translation() prompt path)"
  - "Manifest unique_id derived from {source_suite}-{kernel_name}-{parallel_api} (manifest entries do NOT carry a unique_id field — Rule 1 deviation from PLAN snippet)"
  - "Pre-flight step 4a/4d in runbook split into batch-launcher checks vs llm_evaluate.py --dry-run check; runbook previously instructed Le to run a non-existent flag"
metrics:
  duration_minutes: 12
  completed_at: "2026-04-17T23:55:00.000Z"
  tasks_completed: 2
  files_created: 1
  files_modified: 1
---

# Phase 2 Plan 08: Integration Smoke + GPT-5.4 Handoff Summary

**One-liner:** Pre-Phase-3 guardrails — 60-case zero-API dry-run matrix + real-API canonical→derive→ablation E2E + Le's GPT-5.4 runbook with verified Azure pricing — that catch a broken `--task-list × Azure × ablation` path before Phase 3 spends real money.

## What Was Built

### Task 1 — `tests/test_eval_integration_smoke.py` (489 lines)

Three concerns in one file:

1. **`test_dryrun_matrix`** (Part 1 — `@pytest.mark.integration` only, no `llm`):
   - Parametrized over 60 nominal cases (5 suites × 6 directions × 2 models)
   - 52 actually executable; 8 SKIPPED for missing target variants (hecbench `bezier-surface` has no opencl spec — confirmed via `manifest.jsonl`)
   - Each case shells out to `llm_evaluate.py --dry-run --json` and verifies: returncode 0, trailing JSON blob has `dry_run=True` + `overall_status=DRY_RUN` + `model` matches, prompt banners present
   - KNOWN_FAIL set + manifest-target set both loaded at collection time (single source of truth)

2. **`test_real_e2e_canonical_to_ablation`** (Part 2a — `@pytest.mark.integration + @pytest.mark.llm`):
   - Per model: canonical L0 (3 samples) → `derive_l0_passers` → ablation L1–L4 (1 sample each)
   - All paths use `tmp_path` as `--project-root` — never touches real `results/evaluation/`
   - **Zero-passer guard:** if `derive_l0_passers` returns `[]`, calls `pytest.fail` with explicit guidance (this IS the signal the test exists to catch)
   - Asserts 7 D-29 schema fields + canonical config guardrails on every result JSON

3. **`test_real_direction_independence_omp_to_cuda`** (Part 2b — `@pytest.mark.integration + @pytest.mark.llm`):
   - One omp-to-cuda invocation per model (1 sample to cap spend)
   - Proves direction independence (the pipeline is not cuda-to-omp-only)

4. **`_log_token_costs`** (autouse teardown fixture):
   - Walks `tmp_path/results/evaluation/`, logs per-result `prompt_tokens` + `completion_tokens` + estimated cost using verified 2026-04-17 pricing (Azure $2.50/$15.00, Together $0.60/$3.60 per 1M tokens)
   - Silent for dry-run tests (no result JSONs in tmp_path)

### Task 2 — `docs/neurips2026-gpt5-handoff.md` (301 lines)

GPT-5.4 campaign runbook for Le with all 8 required sections:
1. Context (canonical + L0-conditional ablation design, two-track execution split)
2. Repo setup (clone, venv, pip install)
3. Secrets checklist (`AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, deployment name)
4. Pre-flight verification (4 commands, all must exit 0)
5. Phase 3 stage commands (Stage A canonical, Stage B derive, Stage C ablation — all flags pinned)
6. Output layout + result JSON schema (canonical/ablation paths + 11-row field table)
7. Cost model (verified 2026-04-17 Azure pricing $2.50/$15.00, $559 tentative ceiling, $600 abort threshold + monitoring snippet)
8. Artifact delivery (tarball-only, no branches/no merges)

`reasoning_effort=medium` documented as a hardcoded semantic of `--thinking on` (D-08), NOT a user-tunable flag.

## Verification

```
$ python3 -m pytest tests/test_eval_integration_smoke.py -v
52 passed, 12 skipped in 2.33s

$ python3 -m pytest tests/ -q --ignore=tests/test_harness_integration.py --ignore=tests/test_spec_loader_integration.py -m "not llm"
204 passed, 11 skipped, 26 deselected in 2.53s
```

(a) **Dry-run matrix collection:** 64 tests collected (60 dry-run + 2 e2e canonical→ablation + 2 direction independence).

(b) **Dry-run matrix coverage:** 60 nominal cases → 52 executable + 8 SKIPPED (hecbench bezier-surface has no opencl variant in manifest — all 8 skips fall on that suite/kernel × 4 opencl-touching directions × 2 models). KNOWN_FAIL skips: 0 (no KNOWN_FAIL spec lies on the suite-representative kernels).

(c) **`tmp_path` confinement:**
```
$ grep -n -- "tmp_path.*--project-root" tests/test_eval_integration_smoke.py
269:        "--project-root", str(tmp_path),
345:        "--project-root", str(tmp_path),
397:        "--project-root", str(tmp_path),
```
Every real-API subprocess call passes `tmp_path` as `--project-root`. The real `results/evaluation/` tree is never touched.

(d) **Token+cost log:** Real-API tests are SKIPPED in this run (`PARBENCH_RUN_LLM_TESTS` not set). The `_log_token_costs` autouse fixture is verified present (grep + collection); it will emit `[token-log] ...` lines and a TOTAL line when LLM tests run on the GPU machine.

(e) **Date executed:** 2026-04-17. Real-API model: SKIPPED (gated). Dry-run matrix executed against current `MODEL_REGISTRY` (azure-gpt-5.4 + together-qwen-3.5-397b-a17b), all 52 executable cases PASSED.

## Plan Verification Block Results

All `<verify>` commands from the plan exit 0:

| Check | Result |
|-------|--------|
| `pytest --collect-only tests/test_eval_integration_smoke.py -q` | 64 tests collected |
| `grep -q "tmp_path.*--project-root"` | OK |
| `grep -q "_load_known_fail_ids\|KNOWN_FAIL_IDS"` | OK |
| `grep -q "pytest.fail"` | OK |
| `grep -Eq "@pytest.mark.llm"` | OK |
| `python3 -c "ast.parse(...)"` | syntax OK |
| `grep -q "AZURE_OPENAI_API_KEY"` (runbook) | OK |
| `grep -q "AZURE_OPENAI_ENDPOINT"` (runbook) | OK |
| `grep -q "reasoning_effort=medium"` (runbook) | OK |
| `grep -qi "pre-flight"` (runbook) | OK |
| `grep -Eq '\$2\.50\|2\.50/1M'` (runbook) | OK |
| `grep -q "derive_l0_passers"` (runbook) | OK |
| `grep -- "--task-list"` (runbook) | OK |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Manifest `unique_id` field does not exist**
- **Found during:** Task 1, drafting `_load_manifest_targets()`
- **Issue:** The plan's snippet uses `entry.get("unique_id")` to read manifest entries, but `manifest.jsonl` entries carry `kernel_name` / `parallel_api` / `source_suite` instead. Using `entry.get("unique_id")` would silently return `None` for every entry, producing an empty `MANIFEST_IDS` set, which would cause every dry-run case to skip with "target not in manifest" (false negative — the bezier-surface-opencl SKIPPED cases would mask real coverage failures).
- **Fix:** Derive `unique_id` as `f"{source_suite}-{kernel_name}-{parallel_api}"` (matches the spec_file stem convention). Documented inline in the helper docstring.
- **Files modified:** `tests/test_eval_integration_smoke.py` (`_load_manifest_targets`)
- **Verification:** Manifest now yields 211 derived unique_ids; spot-check confirms `rodinia-bfs-cuda`, `mixbench-mixbench-omp`, `hecbench-bezier-surface-cuda` all present.

**2. [Rule 1 - Bug] Dry-run output mixes prompt text and JSON**
- **Found during:** Task 1, first test run (52 dry-run cases failed)
- **Issue:** `llm_evaluate.py --dry-run --json` prints the SYSTEM/USER prompt to stdout BEFORE `_print_result(as_json=True)` emits the JSON. `json.loads(result.stdout)` therefore fails on the leading prompt banner. (The 02-07 `test_smoke_dry_run` would hit the same bug, but is gated by `llm` marker so it was never executed.)
- **Fix:** Locate the trailing JSON object in stdout (`stdout.rfind("\n{")`), parse only that segment. Also added explicit `"SYSTEM MESSAGE"` / `"USER MESSAGE"` banner assertions as functional smoke.
- **Files modified:** `tests/test_eval_integration_smoke.py` (test_dryrun_matrix body)
- **Verification:** All 52 executable dry-run cases now pass.

**3. [Rule 1 - Bug] Runbook pre-flight step 4a/4d uses non-existent `run_eval_batch.py --dry-run`**
- **Found during:** Task 2, verifying the existing runbook
- **Issue:** Pre-flight step 4d instructed Le to run `run_eval_batch.py --dry-run`, but `run_eval_batch.py` has no `--dry-run` flag (only `llm_evaluate.py` does, per the 02-07 module docstring and verified via `--help`). Le would have hit a confusing argparse error before any paid call.
- **Fix:** Split step 4a into batch-launcher CLI checks (`--thinking`, `--task-list`) + `llm_evaluate.py --dry-run` check. Rewrote step 4d to invoke `llm_evaluate.py --dry-run` directly with explicit `--source` / `--target` spec paths. Added inline comment explaining the launcher does not carry `--dry-run`.
- **Files modified:** `docs/neurips2026-gpt5-handoff.md` (Section 4)

### Out-of-scope discoveries

None. All findings traced to the two plan-modified files and were fixed inline.

## Phase 2 Status

**This is the FINAL plan of Phase 2.** All 8 plans complete:

- [x] 02-01 add azure-gpt-5.4 registry
- [x] 02-02 supports_thinking capability field
- [x] 02-03 --thinking CLI flag + result JSON schema bump
- [x] 02-04 purge gpt-4.1-*
- [x] 02-05 derive_l0_passers.py
- [x] 02-06 --task-list flag on run_eval_batch.py
- [x] 02-07 end-to-end smoke (5 suites × 2 models × cuda-to-omp)
- [x] 02-08 integration smoke + GPT-5.4 handoff runbook (this plan)

**Handoff to Phase 3:**

Phase 2 is code + tests + handoff doc only — it does NOT launch any evaluation run. Phase 3 launch (Phase A canonical) remains BLOCKED on:
1. Gal sign-off on GPT budget overshoot (~$559 vs $400 target) — pending as of 2026-04-17
2. Le's confirmation of Azure GPT-5.4 deployment + sustained TPM ≥200k

When both unblocks land, the runbook at `docs/neurips2026-gpt5-handoff.md` is Le's entry point. Samyak runs the Qwen track on the Linux GPU machine (`/home/samyak/Desktop/parbench_sam`) using the same stage commands with `--models together-qwen-3.5-397b-a17b`.

## Self-Check: PASSED

- [x] `tests/test_eval_integration_smoke.py` exists (489 lines)
- [x] `docs/neurips2026-gpt5-handoff.md` exists (301 lines)
- [x] All 10 plan grep anchors pass
- [x] Dry-run matrix: 52 PASSED, 12 SKIPPED, 0 FAIL
- [x] Full unit+integration suite: 204 PASSED, 11 SKIPPED, 0 FAIL
- [x] No purged model IDs (`gpt-4.1`, `azure-gpt-4.1`) anywhere in new artifacts
- [x] No real API keys/secrets in any new file
- [x] `tmp_path` confinement verified (3 occurrences, all real-API tests)
