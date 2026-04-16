# Session Handoff — 2026-04-09 (Session 2)

## What Was Done This Session

### Plan Revision for Milestone 2
- **Reviewed and simplified** the 6-phase, 26-requirement roadmap down to 4 focused phases
- **Ran adversarial plan review** (plan-reviewer agent, Opus) — found 9 grounded items, fixed 3 critical issues:
  1. Campaign separation: use existing `temperature` + `sample_id` fields + `campaign_for()` helper, NOT folder restructuring (would break `--resume`)
  2. AskSage adapter: marked BLOCKED — zero code/docs in codebase, wait for Le's API specs
  3. Portability: acknowledged hardcoded `/opt/nvidia/hpc_sdk/...` paths in specs, deferred full templating
- **Saved 6 new memories:** never touch benchmark source, GPT botched, Qwen both campaigns, no primary benchmark, paper rewrite overleaf_main.tex, extensible pipeline
- **Updated MEMORY.md index** — removed stale GPT re-run entry, added all new memories

### Key Discoveries
- Core pipeline (harness/, llm_evaluate.py) is already suite-agnostic — zero `if suite == "rodinia"` in core code
- Suite-specific code exists only in: `analyze_rodinia_batch.py`, batch scripts, `EXCLUDED_SPECS` duplication
- `pass_at_k()` already implemented in `statistical_analysis.py:706` and `quantitative_findings.py:1187`
- `run_eval_campaign.sh` already handles all 5 suites
- Existing Qwen results already have `temperature` and `sample_id` fields in every JSON
- XSBench and RSBench have `omp_target` specs not covered by current campaign batches
- `numeric_comparison` verifier is TODO/SKIP — tolerance handled by benchmarks' own stdout checks

## What Needs To Happen Next

### Execute the approved plan (4 phases)

The plan is at: `/home/samyak/.claude/plans/ethereal-wishing-bumblebee.md`

**Phase 1: Pipeline Testing & Uniformity** (Specs → Build → Run → Verify)
- Test each pipeline component with real programs from ALL 5 suites
- Fix suite-specific code: `analyze_rodinia_batch.py`, `EXCLUDED_SPECS` duplication, batch scripts
- Audit build workarounds for fairness (needle.h, OpenCL paths, data symlinks, HeCBench CMakeLists)
- Acknowledge portability limits (hardcoded compiler paths in s
- Write unit tests (synthetic data) + integration smoke tests (real builds)
- Test programs: bfs (Rodinia), xsbench, rsbench, mixbench, bezier-surface (HeCBench)

**Phase 2: LLM Eval Testing** (Real Calls)
- Add `campaign_for()` helper + `--campaign c1|c2` convenience flag to run_eval_batch.py
- Test prompt construction with `--dry-run` for each suite
- Test full eval with real Qwen/Together calls (1 program per suite)
- Verify existing `pass_at_k()` works correctly with actual C2 data
- AskSage: BLOCKED until Le provides API docs

**Phase 3: Full Evaluation Runs**
- Campaign 1 + Campaign 2, all suites, all directions (including omp_target for XSBench/RSBench)
- Qwen: use `--resume` to fill gaps in existing 1,248 results
- AskSage: when unblocked
- Delete old tmux sessions (qwen_hecbench, qwen_small)

**Phase 4: NeurIPS Paper**
- Rewrite sections of `docs/paper/latex/overleaf_main.tex`
- Every claim traceable to verified result files
- Deadline: May 1, 2026

### Also update `.planning/` docs
- Simplify PROJECT.md, ROADMAP.md, REQUIREMENTS.md, STATE.md to match the new 4-phase plan
- Remove the old 6-phase structure and 26 granular requirements

## Key State on Disk

- **Qwen 3.5 397B results:** 1,248 files at `results/evaluation/together-qwen-3.5-397b-a17b/`
  - C1 (~780): temp=0.0, L0-L4, no `-s` suffix
  - C2 (~468): temp=0.7, `-s0`/`-s1`/`-s2` suffix
- **GPT results:** 897 files — ALL BOTCHED, ignore entirely
- **Running tmux sessions:** `qwen_hecbench` and `qwen_small` — DONE, can be deleted
- **Plan file:** `/home/samyak/.claude/plans/ethereal-wishing-bumblebee.md`

## Hard Rules (from user)

1. NEVER touch original benchmark source code (.c, .cu, .cpp, .cl)
2. Supporting files (Makefiles) CAN be updated — record all changes
3. All 5 suites treated equally — no primary benchmark
4. Campaign 1 vs Campaign 2 clearly separated via `campaign_for()` helper
5. Pipeline must be extensible to new benchmarks
6. GPT results ignored entirely
7. Paper is a rewrite of `overleaf_main.tex`, not from scratch
8. AskSage is BLOCKED until Le provides API docs — do not speculatively build
