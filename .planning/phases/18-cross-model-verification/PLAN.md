# Phase 18 Plan: Cross-Model Verification Sprint

## Goal
Verify every data claim in the updated paper against on-disk result files. Final quality gate before submission.

## GSD Execution Notes
- **Skip** `/gsd-plan-phase 18` — verification tasks are enumerated and deterministic
- **Run first:** `/gsd-validate-phase 16` and `/gsd-validate-phase 17` (Nyquist retroactive audits)
- **Primary tool:** `/cite-check` skill — designed for paper claim verification

## Tasks

### Wave 1: Claim Verification (parallel)

#### T1: Verify GPT table numbers
**GSD command:** `/cite-check`

Verify all GPT numbers in tables against `results/analysis/paper_data_gpt41mini.json`:
- Pass rate (expect ~26.6%)
- BUILD_FAIL rate (expect ~56.4%)
- RUN_FAIL rate (expect ~9.7%)
- VERIFY_FAIL rate (expect ~7.1%)
- Task counts (606 primary, 291 pass@k)
- Per-direction rates for 7 directions

---

#### T2: Verify statistical claims
**GSD command:** `/cite-check`

Verify statistical claims are reproducible from `results/analysis/cross_model_comparison.json`:
- Chi-squared p-value (must match exactly)
- Wilson 95% confidence intervals
- Cohen's h effect sizes (overall and per-direction)
- Per-kernel agreement matrix counts

---

#### T3: Verify prose claims
**GSD command:** `/cite-check`

Verify prose claims match data:
- All percentages cited in text
- Rankings and orderings
- BUILD_FAIL dominance framing (56.4% GPT vs 33.9% Qwen)
- Aggregate trends (L0→L4 decline numbers)

---

### Wave 2: Spot Checks (parallel)

#### T4: Verify lavamd augmentation example
**GSD command:** `/gsd-fast`

Verify lavamd example in paper matches actual result JSON:
- L0: PASS
- L1: BUILD_FAIL
- L2: BUILD_FAIL
- L3: VERIFY_FAIL
- L4: PASS (CORRECTED — must be stated explicitly)

**Files:** Result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/` for lavamd cuda-to-omp at each augmentation level.

---

#### T4b: Verify bptree augmentation example
**GSD command:** `/gsd-fast`

Verify bptree example in paper matches actual result JSON:
- L0: PASS
- L1: RUN_FAIL
- L2: RUN_FAIL
- L3: PASS (CORRECTED — model partially recovers)
- L4: RUN_FAIL

**Files:** Result JSONs in `results/evaluation/together-qwen-3.5-397b-a17b/` for bptree omp-to-opencl at each augmentation level.

---

#### T5: Verify anonymization description
**GSD command:** `/gsd-fast`

Verify `build_translation_prompt()` at `scripts/evaluation/llm_evaluate.py` line 570 matches the 6-row anonymization table in paper Section 3:
1. Kernel name & description omitted
2. Source comments stripped (`_strip_comments()`)
3. Source filenames genericized
4. Target filenames genericized
5. Build commands sanitized
6. Header files genericized

---

#### T6: Verify figure data visibility
**GSD command:** `/gsd-fast`

Spot-check f3 and f7 figure PDFs against paper_data JSONs:
- Verify GPT series is visible (color #56B4E9, not grey #E0E0E0)
- Verify dual-model data renders correctly

---

### Wave 3: Final Checks (sequential)

#### T7: Grep for remaining markers
**GSD command:** `/gsd-fast`

```bash
grep -n '\\pending{}' docs/paper/latex/paper.tex
grep -n '\\tbd{}' docs/paper/latex/paper.tex
```

**Expected:** 0 results (or 1 for hardware specs if Niranjan hasn't replied).

---

#### T8: Verify table edge cases
**GSD command:** `/gsd-fast`

- tab:direction-rates omp_target-to-cuda row has "—" with footnote
- tab:overall-pass aggregate row is sum of counts, NOT average of model rates

---

#### T9: Run full validation loop
**GSD command:** `/validate`

Full 4-wave validation loop — mandatory pre-commit gate:
- Wave 1: verify-app + diff-reviewer + security-scanner
- Wave 2: test-synthesizer + regression-checker + spec-auditor
- Wave 3: consistency-checker + code-simplifier
- Wave 4: self-critic (Opus) + plan-reviewer

**GATE:** `.validation_passed` sentinel must exist before commit.

---

#### T10: Final LaTeX compile
**GSD command:** `/gsd-fast`

```bash
cd docs/paper/latex && latexmk -pdf paper.tex
```

Verify:
- Page count ≤ 10 (SC limit)
- No orphan references
- All figures render
- No undefined refs or missing citations

---

## Phase 18 Verification
**GSD command:** `/gsd-validate-phase 18` (Nyquist audit)

**Final gate:** `.validation_passed` sentinel must exist before commit.

## Post-Phase 18
- Commit all changes
- Push to remote
- Paper ready for April 8 submission
