# Requirements: ParBench

**Defined:** 2026-04-09
**Core Value:** Every evaluation result is reproducible and pipeline-correct -- so model comparisons in the NeurIPS paper are defensible under peer review.

## Phase 1: Pipeline Testing & Uniformity

- [ ] Spec loading works for all 5 suites (paths resolve, source files exist, prompt payloads correct)
- [ ] Build works for 1+ program per suite per API (cuda, omp, opencl)
- [ ] Run + verify works for all non-KNOWN_FAIL specs
- [ ] `EXCLUDED_SPECS` centralized as one importable constant (no stale duplicates)
- [ ] Suite-specific analysis code generalized (`analyze_rodinia_batch.py` replaced or generalized)
- [ ] No `if suite == "rodinia"` special-casing in pipeline code
- [ ] Unit tests (synthetic data) cover: path resolution, EXCLUDED_SPECS filtering, campaign classification
- [ ] Integration smoke tests (real builds) cover: 1+ spec per suite builds, runs, verifies
- [ ] Portability audit documented: hardcoded compiler paths acknowledged, `config/paths.json` usage verified

## Phase 2: LLM Eval Testing

- [ ] `campaign_for(record)` helper classifies results as C1 or C2 from existing `temperature` + `sample_id` fields
- [ ] `--campaign c1|c2` convenience flag added to `run_eval_batch.py` with correct defaults
- [ ] Prompt construction verified for each suite (via `--dry-run`)
- [ ] End-to-end eval tested with real Qwen/Together calls (1 program per suite, cuda-to-omp)
- [ ] `pass_at_k()` verified with actual C2 data (do NOT reimplement -- already exists)
- [ ] Campaign 2 config validated end-to-end (temp=0.7, num_samples=3, max_retries=1, augment_level=0)
- [ ] AskSage adapter -- **BLOCKED** until Le provides API docs/credentials

## Phase 3: Full Evaluation Runs

- [ ] Campaign 1 complete: all suites, all directions (including cuda<->omp_target for XSBench/RSBench), Qwen via `--resume`
- [ ] Campaign 2 complete: all suites, all directions, Qwen via `--resume`
- [ ] AskSage runs complete (when unblocked)
- [ ] Analysis regenerated: `analyze_eval.py` for each model + campaign

## Phase 4: NeurIPS Paper

- [ ] Rewrite sections of `docs/paper/latex/overleaf_main.tex`
- [ ] Every quantitative claim traceable to specific result JSON files on disk
- [ ] Submit to NeurIPS 2026 Datasets & Benchmarks track by **May 1, 2026**

## Out of Scope

| Feature | Reason |
|---------|--------|
| Repository-level (full build-system) translation | Kernel isolation is deliberate design -- different paper |
| New benchmark suites beyond current 5 | Scope fixed for NeurIPS submission |
| SYCL/HIP as primary evaluation directions | Case study status only; not in main paper claims |
| CI/CD for compilation or eval runs | All evals are manual on the Linux GPU machine by design |
| Real-time eval dashboard redesign | Only update if driven by results analysis changes |
| Full spec portability (compiler path templating) | Deferred to post-NeurIPS; document machine config in paper |
| GPT-4.1 mini re-runs | All GPT results botched -- ignore entirely |
| Speculative AskSage adapter | BLOCKED until Le provides API docs |

---
*Requirements defined: 2026-04-09*
*Last updated: 2026-04-09 after plan simplification to 4 phases*
