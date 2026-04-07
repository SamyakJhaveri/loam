# Phase 17 Plan: Paper Integration — Dual-Model Results, Comparison & Differentiation

## Goal
Update paper.tex with GPT-4.1 mini data, fill all markers, write new sections, and stay within 10-page limit.

## GSD Execution Notes
- **Run** `/gsd-discuss-phase 17` with context about corrected counts (19 pending, 18 tbd)
- **Run** `/gsd-plan-phase 17` — planner MUST grep paper.tex for exact positions first
- Agent team STRONGLY recommended for Wave 2 (sequential paper edits)
- LaTeX compile checkpoint after EACH sub-task

## Split Strategy
- **17A + 17A-tbd** start immediately once Phase 16 outputs exist (mechanical fills)
- **17B-D** require chi-squared + Cohen's h numbers from cross_model_comparison.json

## Tasks

### 17A: Fill all `\pending{}` markers (19 total — CORRECTED from 11)

**GSD command:** `/gsd-fast`

**FIRST:** grep paper.tex for all `\pending{}` with line numbers (expect 19). Do NOT use approximate line numbers from this plan — they drift with edits.

**All 19 `\pending{}` locations** (grep to verify):
1. Line ~84 (Abstract) — "Qwen 38.3% vs GPT-4.1 mini 26.6%, BUILD_FAIL dominant for both"
2. Line ~151 (Introduction Contributions) — GPT task count expansion
3. Line ~170 (Introduction) — TBD from grep
4. Line ~631 (Hardware section) — collaborator machine GPU/CPU/OS (fill ONLY if Niranjan replied; else leave with comment)
5. Line ~663 (Evaluation cost) — GPT-4.1 mini Azure API costs
6. Line ~672 (Results intro) — GPT campaign task count (606 primary)
7. Line ~697 (Results) — TBD from grep
8. Line ~702 (Results) — task counts + chi-squared result
9. Line ~797 (Results) — TBD from grep
10. Line ~836 (Kernel difficulty tiers) — tier boundary note
11. Line ~917 (Augmentation) — cross-model augmentation comparison
12. Line ~969 (Table tab:direction-rates) — fill GPT column (use "—" + footnote for omp_target-to-cuda)
13. Line ~986 (Section 6.6) — cross-model direction comparison
14. Line ~1016 (Section 7.1) — cross-model implications
15. Line ~1030 (Section 7.2) — direction asymmetry + augmentation sensitivity
16. Line ~1033 (Section 7.2) — cross-provider sensitivity
17. Line ~1061 (Section 7.3) — Threats: coverage gap (7 vs 8 directions), model size disparity
18. Line ~1094 (Section 8 Conclusion) — GPT summary
19. Line ~1033 area (Discussion augmentation validation) — verify with grep

**Data sources:**
- `results/analysis/paper_data_gpt41mini.json` for all GPT numbers
- `results/analysis/cross_model_comparison.json` for statistical claims

**After filling all 19:** LaTeX compile checkpoint.

---

### 17A-tbd: Fill all `\tbd{}` table cells (18 total)

**GSD command:** `/gsd-fast`

**Table: tab:overall-pass (9 cells, lines ~690-691):**
- GPT row: pass rate, build fail rate, run fail rate, verify fail rate, task count
- Aggregate row: sums (NOT averages of model rates)

**Table: tab:direction-rates (6 cells, lines ~939-944):**
- GPT column per direction for 7 directions
- omp_target-to-cuda row → "—" with footnote explaining coverage gap

**IMPORTANT:** Aggregate row is sum of per-direction counts, NOT average of model rates.

**Data source:** `results/analysis/paper_data_gpt41mini.json`

**After filling all 18:** LaTeX compile checkpoint.

---

### 17B: Write NEW Section 6.9 — Cross-Model Comparison

**GSD command:** Part of `/gsd-execute-phase 17` wave 2

**PREREQUISITE:** `cross_model_comparison.json` must exist with actual chi-squared p-value and Cohen's h values. Do NOT write placeholder statistics.

**Insert after Section 6.8 (~line 1000, verify with grep).**

**Content:**
1. Overall pass rate comparison with chi-squared test (actual p-value) and Wilson 95% CIs
2. Per-direction side-by-side for common 7 directions; explicitly note missing omp_target-to-cuda
3. Failure taxonomy comparison: BUILD_FAIL dominance in GPT (56.4%) vs Qwen (33.9%)
4. Per-kernel agreement matrix (which kernels both pass/fail, which diverge)
5. Effect sizes (Cohen's h) for overall and per-direction gaps

**Framing:** Benchmark paper — two models demonstrate ParBench's utility, NOT a model ranking.

**After Section 6.9:** LaTeX compile checkpoint.

---

### Page Budget Audit (after 17B, before 17C)

Compile paper and count pages after Section 6.9. If >10 pages:

| Cut candidate | Savings | Impact |
|---------------|---------|--------|
| Reduce augmentation examples from 5 to 2 | ~0.5 page | Lose diversity |
| Condense anonymization table into inline prose | ~0.3 page | Minor |
| Trim Section 6.4 self-repair prose | ~0.3 page | Low impact |
| Move per-kernel agreement matrix to appendix | ~0.5 page | Keeps 6.9 focused |

---

### 17C: Add Augmentation Degradation Evidence

**GSD command:** Part of `/gsd-execute-phase 17` wave 2

**Where:** Section 6.5 (Augmentation Robustness) or new subsection.

**Examples (CORRECTED — verify each against actual result files BEFORE inserting):**

1. **page-rank / cuda-to-omp_target:** L0=PASS, L1-L4 all FAIL (complete collapse)
2. **lavamd / cuda-to-omp:** L0=PASS, L1=BUILD_FAIL, L2=BUILD_FAIL, L3=VERIFY_FAIL, **L4=PASS** (3 of 4 fail, 3 different failure types, L4 recovers)
3. **bptree / omp-to-opencl:** L0=PASS, L1=RUN_FAIL, L2=RUN_FAIL, **L3=PASS**, L4=RUN_FAIL (3 of 4 fail, recovery at L3 then re-failure)
4. **opencl-to-cuda / AGGREGATE (Qwen):** L0=10.0% → L4=0.0% (monotonic decline to zero)
5. **opencl-to-cuda (GPT):** L0=16.7% → L1-L4=0.0% (cross-model validation)

**Aggregate trend:** Qwen omp-to-opencl: L0=33.3% → L4=16.7% (50% relative decline)

**Page budget:** 3 examples minimum; 5 only if pages allow after 17A+17B.

**After augmentation section:** LaTeX compile checkpoint.

---

### 17D: Emphasize Prompt Anonymization

**GSD command:** Part of `/gsd-execute-phase 17` wave 2

**Where:** Section 3 (ParBench Framework, ~lines 277-417)

**BEFORE writing:** Cross-check `build_translation_prompt()` in `scripts/evaluation/llm_evaluate.py` line 570 to verify 6 anonymization measures match actual code.

**6 Anonymization Measures:**
| What | How |
|------|-----|
| Kernel name & description | Completely omitted |
| Source code comments | `_strip_comments()` removes all |
| Source filenames | "Source File 1", "Source File 2" |
| Target filenames | `translated_0.cpp`, `translated_1.h` |
| Build commands | Kernel name replaced: `make bfs` → `make` |
| Header files | "Header File 1", "Code File 1" |

**Key argument:** LLM receives NO hints about which kernel it's translating → measures innate ability, not memorization. Other benchmarks (LASSI, HPC-Coder-v2) present identifiable names → contamination risk.

**After anonymization subsection:** LaTeX compile checkpoint.

---

### 17E: Update Figures in Paper

**GSD command:** `/gsd-fast`

**Do AFTER 17A-D to avoid conflicts.**

**Steps:**
1. Wire any NEW figure files from Phase 16 into paper.tex
2. Ensure `\includegraphics` paths match regenerated filenames
3. Add captions describing dual-model data where applicable
4. Do NOT replace existing Qwen-only figure references — update in-place

**After figure updates:** Final LaTeX compile — check page count ≤ 10.

---

## Phase 17 Verification

**GSD command:** `/gsd-verify-work` then `/gsd-secure-phase 17`

**Checklist:**
- [ ] `grep paper.tex '\pending{}'` → 0 results (or 1 if hardware specs not received)
- [ ] `grep paper.tex '\tbd{}'` → 0 results
- [ ] Section 6.9 exists with ACTUAL chi-squared p-value (no placeholder)
- [ ] lavamd example states L4:PASS explicitly
- [ ] bptree example states L3:PASS (recovery) explicitly
- [ ] tab:overall-pass rows filled; aggregate row is sum not average
- [ ] tab:direction-rates GPT column filled; omp_target-to-cuda = "—" + footnote
- [ ] LaTeX compiles clean (no undefined refs, no missing figures)
- [ ] PDF page count ≤ 10 (SC limit)
