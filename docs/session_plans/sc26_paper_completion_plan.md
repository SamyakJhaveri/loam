# SC26 Paper Completion Plan — 5+1 Sessions

**Created:** 2026-03-31
**Deadline:** April 8, 2026
**Status:** Session 1 (Audit) complete. Sessions 2-6 pending.

---

## Context

ParBench SC26 paper deadline is April 8, 2026. The paper framework (S1-S4) is publication-ready.
S5-S8 have 201 [PENDING] placeholders awaiting empirical data. Qwen 3.5 397B campaign is
complete (1,018 result files, 906 tasks, 27.7% overall pass rate). Gemini 2.5 Flash campaign
will arrive April 3-5. Analysis scripts exist and are 95% functional but need updates for
evolved architecture (5 suites, kernel-only OpenCL, Qwen model).

### Decisions Made
- **Two-model paper** (Qwen + Gemini) — Qwen-first, Gemini integration later
- **Data first, narrative second** — scripts → tables/figures → paper text
- **Samyak owns the drawio diagram** — agent team handles caption + cross-refs
- **Raw data is primary source** — update scripts to extract max insight; findings log is supplementary
- **Findings log:** 2-3 key findings inline in paper, rest referenced in appendix

### Owner Split (Zero Merge Conflicts)

| Owner | Sessions | Files Owned |
|-------|----------|-------------|
| **Samyak** | S1-S4 | `paper_draft.md`, `scripts/`, `results/`, figures (PNG/PDF), `eval_findings_log.md` |
| **Erel** | S5-S6 | Appendix files (new), Overleaf/LaTeX project, figure/table LaTeX labeling, Gemini data integration |

Samyak completes the markdown draft. Erel converts to LaTeX and writes appendix content.
Sequential handoff — no parallel edits on the same file.

### Audit Findings (Session 1 Output)

**What we have:**
- Qwen campaign: 1,018 result files, 906 tasks, 27.7% pass rate, eval_summary.json
- Legacy model data (backup): Claude Sonnet (238), Gemini Flash-Lite (237), Groq Llama (237) in `evaluation_backup_20260328/`
- Paper draft: 707 lines, ~60% complete, all 8 sections exist, S1-S4 solid, 201 [PENDING] in S5-S8
- All 8 figures exist as PDF+PNG (F1-F8), but F5-F8 likely contain stale pilot data
- Analysis scripts: 37 scripts, 95% functional, Qwen integrated in MODEL_DISPLAY/pricing
- Statistical toolkit: Wilson CI, chi-squared, Fisher's exact, Cochran-Armitage, McNemar — all implemented
- Findings log: 487 lines of forensic analysis (lavamd multi-file failure)
- Architecture diagram: `parbench_architecture.drawio` (36KB)

**What's missing:**
- Gemini 2.5 Flash campaign results (arriving April 3-5)
- All empirical tables (Tables 7-13) — structures exist, no numbers
- Figures F5-F8 need regeneration with Qwen data
- Teaser figure has no detailed caption or cross-referencing in paper
- Appendix content (API selection rationalization, kernel survey depth)
- McNemar direction asymmetry not wired into main() in statistical_analysis.py
- Per-model augmentation curves with CIs not plotted
- Paper narrative S6/S7 all placeholder-heavy

### Qwen Data Snapshot (from eval_summary.json)

| Metric | Value |
|--------|-------|
| Total tasks | 906 |
| Overall pass rate | 27.7% (251/906) |
| BUILD_FAIL | 40.4% (366) |
| RUN_FAIL | 22.0% (199) |
| VERIFY_FAIL | 7.6% (69) |
| EXTRACTION_FAIL | 2.3% (21) |
| First-attempt PASS | 160 |
| Fixed by retry | 91 |

**By direction:**

| Direction | Pass Rate | Pass/Total |
|-----------|-----------|------------|
| omp_target-to-cuda | 60.0% | 18/30 |
| cuda-to-omp | 50.0% | 76/152 |
| omp-to-cuda | 36.8% | 56/152 |
| opencl-to-omp | 32.6% | 42/129 |
| omp-to-opencl | 25.6% | 33/129 |
| cuda-to-opencl | 13.8% | 20/145 |
| opencl-to-cuda | 4.1% | 6/145 |
| cuda-to-omp_target | 0.0% | 0/24 |

**By augmentation level:**

| Level | Pass Rate |
|-------|-----------|
| L0 | 22.6% |
| L1 | 34.4% |
| L2 | 36.5% |
| L3 | 37.5% |
| L4 | 30.2% |

---

## Timeline

| Date | Session | Owner | Blocker |
|------|---------|-------|---------|
| Mar 31 | S1: Audit & Plan | Samyak | None |
| Apr 1 | S2: Scripts & Data | Samyak | None |
| Apr 1-2 | S3: Paper Narrative | Samyak | S2 complete |
| Apr 2 | S4: Teaser + Polish | Samyak | S3 complete |
| Apr 3-5 | S5: Appendix + LaTeX + Gemini | Erel | S4 complete + Gemini data |
| Apr 6-7 | S6: Final Review | Both | S5 complete |
| **Apr 8** | **DEADLINE** | | |

---

## Session 1: Comprehensive Audit & Gap Analysis ✅ COMPLETE

**Owner:** Samyak
**Objective:** SC reviewer-style audit producing this plan document.
**Status:** DONE — this document IS the output.

---

## Session 2: Script Updates & Qwen Data Extraction

**Owner:** Samyak
**Objective:** Update analysis scripts to handle evolved project architecture. Run all analysis
pipelines on Qwen data. Generate all tables (7-13) and figures (F5-F8) from raw results.

### Why This Session Exists
The scripts were written for a 3-model pilot (Claude/Gemini-Lite/Groq). The project now has
5 suites, kernel-only OpenCL translation logic, and Qwen as primary model. Scripts need
targeted updates before they can produce correct paper-ready output.

### Tasks

#### 2.1 Verify/Update Script Model Configuration
**Files to modify:**
- `scripts/evaluation/generate_paper_figures.py` (lines 121-135: MODEL_DISPLAY)
  - Verify Qwen entry exists (audit says YES but verify against current 2-model scope)
  - Remove legacy models not in paper (azure-gpt-4.1, etc.) — keep only Qwen + Gemini placeholder
- `scripts/analysis/token_analysis.py` (lines 34-42: MODEL_PRICING)
  - Verify Qwen pricing is current ($0.50/$1.50)
- `scripts/analysis/selfrepair_analysis.py` (lines 42-50: MODEL_DISPLAY)
  - Verify Qwen display name

#### 2.2 Run Core Analysis Pipeline
**Commands (sequential):**
```bash
source env_parbench/bin/activate

# 1. Regenerate eval summary from raw Qwen results
python3 scripts/evaluation/analyze_eval.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 2. Run statistical analysis (Wilson CIs, chi-squared, Fisher's, Cochran-Armitage)
python3 scripts/analysis/statistical_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 3. Run self-repair analysis
python3 scripts/analysis/selfrepair_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 4. Run error taxonomy classification
python3 scripts/analysis/build_error_taxonomy.py \
  --project-root /home/samyak/Desktop/parbench_sam -v

# 5. Run token/cost analysis
python3 scripts/analysis/token_analysis.py \
  --project-root /home/samyak/Desktop/parbench_sam -v
```

#### 2.3 Generate Paper Figures (F5-F8)
```bash
python3 scripts/evaluation/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --output-dir docs/paper/figures/ -v
```
**Expected outputs:**
- `f5_kernel_model_heatmap.{pdf,png}` — per-kernel pass/fail heatmap
- `f6_failure_taxonomy.{pdf,png}` — stacked bar of failure categories
- `f7_augmentation_robustness.{pdf,png}` — L0-L4 curves with CIs
- `f8_cross_direction_comparison.{pdf,png}` — grouped bar by direction

#### 2.4 Wire McNemar Direction Asymmetry Test
**File:** `scripts/analysis/statistical_analysis.py`
- The McNemar test code exists (~line 500) but is not called from `main()`
- Wire it into the main output so direction asymmetry p-values are generated
- This feeds Table 13 (Statistical Summary) in the paper

#### 2.5 Extract Per-Augmentation-Level Statistics
**What's needed for Table 10:**
- Pass rate at each level L0-L4, per model, with Wilson CIs
- Cochran-Armitage trend test statistic and p-value
- Data exists in eval_summary.json `by_augmentation_level` but needs CI computation

#### 2.6 Generate pass@k Data (if multi-sample data exists)
- Check for `*_s1.json`, `*_s2.json` pattern in Qwen results directory
- If yes: compute pass@k statistics for Table 12
- If no: mark Table 12 as "Qwen greedy-only; pass@k deferred to Gemini integration"

### Acceptance Criteria
- [ ] All 5 analysis scripts run without errors on Qwen data
- [ ] `eval_summary.json` regenerated with correct totals (906 tasks, 251 PASS)
- [ ] All 4 paper figures (F5-F8) regenerated as PDF+PNG
- [ ] Statistical output includes: Wilson CIs, chi-squared, Cochran-Armitage, McNemar p-values
- [ ] Data files exist for Tables 7-13 (JSON or CSV format)

### Key Files Reference

| File | Purpose | Lines of Interest |
|------|---------|-------------------|
| `results/evaluation/together-qwen-3.5-397b-a17b/` | 1,018 raw result JSONs | All |
| `results/evaluation/eval_summary.json` | Aggregated summary | Regenerated by analyze_eval.py |
| `scripts/evaluation/analyze_eval.py` | Aggregation pipeline | Full script |
| `scripts/evaluation/generate_paper_figures.py` | Figure generation | 121-135 (MODEL_DISPLAY) |
| `scripts/analysis/statistical_analysis.py` | Statistical tests | ~500 (McNemar draft) |
| `scripts/analysis/selfrepair_analysis.py` | Retry outcome analysis | 42-50 (MODEL_DISPLAY) |
| `scripts/analysis/build_error_taxonomy.py` | Failure classification | Regex patterns |
| `scripts/analysis/token_analysis.py` | Token/cost metrics | 34-42 (MODEL_PRICING) |

---

## Session 3: Paper Narrative — Results & Discussion (Qwen-First)

**Owner:** Samyak
**Objective:** Fill all [PENDING] placeholders in S6 (Results) and S7 (Discussion) using
Qwen data generated in Session 2. Incorporate key findings log insights inline.

**Dependency:** Session 2 must be complete (tables/figures/statistical output available).

### Tasks

#### 3.1 Fill S6 Results Sections (38 [PENDING] markers)
Using output from Session 2, fill every placeholder in:
- **S6.1 Overall Pass Rates** — Table 7 (model × outcome), prose interpreting Qwen's 27.7% overall
- **S6.2 Failure Taxonomy** — Figure 5, BUILD_FAIL (40.4%), RUN_FAIL (22.0%), VERIFY_FAIL (7.6%), EXTRACTION_FAIL (2.3%)
- **S6.3 Per-Kernel Analysis** — Table 8, kernel difficulty tiers, heatmap discussion
- **S6.4 Self-Repair** — Table 9, attempt-1 vs repaired counts (160 first-attempt + 91 repaired)
- **S6.5 Augmentation Robustness** — Table 10, L0-L4 curve (22.6%→34.4%→36.5%→37.5%→30.2%), Cochran-Armitage
- **S6.6 Cross-Direction Analysis** — Table 11, direction pass rates (cuda-to-omp=50%, opencl-to-cuda=4.1%)
- **S6.7 pass@k Analysis** — Table 12 (fill if data exists, mark deferred if not)
- **S6.8 Statistical Summary** — Table 13 with all test statistics

#### 3.2 Fill S7 Discussion Sections
- **S7.3 Model Capability Analysis** — Qwen-specific analysis (MoE architecture, 27.7%). Leave Gemini placeholder.
- **S7.4 Direction Asymmetry** — McNemar results (cuda-to-omp 50% vs omp-to-cuda 36.8%)
- **S7.5 Augmentation Robustness** — Interpret non-monotonic curve (peaks L3=37.5%, drops L4=30.2%)

#### 3.3 Incorporate Findings Log Key Insights (2-3 inline)
**Source:** `docs/paper/drafts/eval_findings_log.md`
- **Finding 1 (multi-file translation consistency failure):** lavamd opencl-to-cuda, all 15 attempts fail across L0-L4. Different failure modes per level. Self-repair introduces NEW errors without converging. → Place in S6.2 and S7.2.

#### 3.4 Fix Known Inconsistencies (from Critic Report)
- **B2:** Change augmentation baseline claim to "68 of 88 non-KNOWN_FAIL"
- **B3:** Standardize task count to 710 per model; explain 906 vs 710
- **S1.3:** Verify contribution counts (96 specs, 5 suites, 2 LLMs)
- **Table 5:** Update for Qwen 3.5 + Gemini placeholder
- **Remove archived pilot data** (lines 674-709)

#### 3.5 Update Abstract with Qwen Numbers
Fill 7 [PENDING] markers. Leave Gemini as `[PENDING: Gemini — Session 5]`.

### Acceptance Criteria
- [ ] Zero [PENDING] in S6 (except Gemini-specific cells)
- [ ] S7.3-S7.5 have Qwen analysis (with Gemini placeholders)
- [ ] At least 2 findings log insights inline with data citations
- [ ] B2, B3, S1.3, Table 5 fixed
- [ ] Archived pilot data removed
- [ ] Abstract updated with Qwen numbers

### Key Files Reference

| File | Purpose | Action |
|------|---------|--------|
| `docs/paper/paper_draft.md` | Main paper | EDIT: fill S6/S7, fix inconsistencies |
| `docs/paper/drafts/eval_findings_log.md` | Findings | READ: extract key insights |
| `results/evaluation/eval_summary.json` | Qwen summary | READ: source data |
| `docs/paper/critic_report.md` | Known issues | READ: B2, B3, M1-M4 |

---

## Session 4: Teaser Figure Integration & Structural Polish

**Owner:** Samyak
**Objective:** Write detailed teaser figure caption. Walk through every section adding
explicit cross-references back to Figure 1. Ensure narrative flows end-to-end.
Create appendix stubs as handoff artifacts for Erel.

**Dependency:** Session 3 must be complete (paper has content in all sections).

### Tasks

#### 4.1 Write Detailed Teaser Figure Caption
Per Gal's instructions: caption should "outline the entire pipeline."
- 8-12 sentences covering all pipeline stages
- Reference 5 suites, 3 APIs, augmentation engine, build-run-verify harness

#### 4.2 Section-by-Section Cross-Referencing
Add explicit Figure 1 references to EVERY section, stating which part of the diagram:
- **S1:** "As illustrated in Figure 1 (top), the spec schema defines..."
- **S3.A:** "The spec schema (Figure 1, Stage 1) captures..."
- **S3.B:** "The harness pipeline (Figure 1, Stage 2) executes..."
- **S3.C:** "The augmentation engine (Figure 1, Stage 3) applies..."
- **S3.D:** "The evaluation pipeline (Figure 1, Stage 4) orchestrates..."
- **S4:** "Benchmark curation (Figure 1, Stage 0) is grounded in..."
- **S5:** "The experimental configuration (Figure 1, Stage 4 parameters)..."
- **S6:** "Results from the evaluation pipeline (Figure 1, output)..."
- **S7:** "The BUILD_FAIL bottleneck (Figure 1, Stage 2 failure path)..."

#### 4.3 Appendix Skeleton for Erel
Create stub files for Erel to flesh out:
- `docs/paper/appendix_api_selection.md` — API selection rationalization (per Gal: "convince reviewer you deeply surveyed open source benchmarks")
- `docs/paper/appendix_kernel_survey.md` — Kernel survey depth (35 repos, selection funnel)
- `docs/paper/appendix_findings.md` — Supplementary findings from findings log
- Include notes for Erel on content, data references, and expectations

#### 4.4 End-to-End Narrative Flow Check
- Story flow: gap → framework → curation → setup → results → discussion → conclusion
- Forward/backward references consistent
- All figures/tables referenced in prose
- Redundancy check (10-page IEEE limit)

### Acceptance Criteria
- [ ] Teaser figure caption written (8-12 sentences)
- [ ] Every section (S1-S8) has at least one Figure 1 cross-reference with part ID
- [ ] Appendix stub files created for Erel
- [ ] End-to-end narrative flow verified
- [ ] No [PENDING] except Gemini-specific placeholders

### Key Files Reference

| File | Purpose | Action |
|------|---------|--------|
| `docs/paper/paper_draft.md` | Main paper | EDIT: caption, cross-refs, flow |
| `docs/paper/figures/parbench_architecture.drawio` | Teaser diagram | READ: understand layout |
| `docs/paper/appendix_api_selection.md` | NEW | WRITE: stub for Erel |
| `docs/paper/appendix_kernel_survey.md` | NEW | WRITE: stub for Erel |
| `docs/paper/appendix_findings.md` | NEW | WRITE: stub for Erel |

---

## Session 5: Erel — Appendix, LaTeX Conversion & Figure/Table Labeling

**Owner:** Erel
**Objective:** Write appendix content. Convert markdown draft to Overleaf/LaTeX (IEEE IEEEtran).
Label all figures and tables. Integrate Gemini data when available.

**Dependency:** Session 4 complete (Samyak's markdown draft finalized for Qwen).

### Tasks

#### 5.1 Write Appendix Content
Per Gal's instructions:
- **Appendix A: API Selection Rationalization** — 35-repo survey justification. Why CUDA/OMP/OpenCL not HIP/SYCL/Kokkos. Reference Figures 2-3, Table 3.
- **Appendix B: Kernel Survey Depth** — HeCBench 327→10 funnel. Rodinia categorization. XSBench/RSBench/mixbench justification.
- **Appendix C: Supplementary Findings** — Expanded failure analysis from findings log. Multi-file consistency failure. Per-level error taxonomy.

**Source files:**
- `docs/paper/appendix_*.md` (stubs from Session 4)
- `docs/paper/drafts/eval_findings_log.md`
- `analysis/data/` (survey CSVs)

#### 5.2 Markdown → LaTeX Conversion
- Convert `paper_draft.md` to IEEEtran format
- Proper `\section{}`, `\subsection{}`, `\label{}`
- `\cite{}` references linked to `references.bib`
- IEEE double-column, 10pt formatting

#### 5.3 Figure & Table LaTeX Labeling
- Figures F1-F8: `\begin{figure}`, `\includegraphics{}`, `\caption{}`, `\label{fig:X}`
- Tables 1-13: `\begin{table}`, column formatting, `\caption{}`, `\label{tab:X}`
- Replace markdown "Figure X" / "Table X" with `\ref{fig:X}` / `\ref{tab:X}`

#### 5.4 Gemini Integration (when data arrives, April 3-5)
- Run Session 2 analysis commands on Gemini data
- Fill Gemini cells in Tables 7-13
- Update S5.E hardware details (Erel's machine)
- Write S7.3 model comparison (Qwen MoE vs Gemini dense)
- Regenerate F5-F8 with two-model data
- Update Abstract Gemini placeholders

### Acceptance Criteria
- [ ] Appendix A, B, C written with data citations
- [ ] LaTeX compiles without errors in Overleaf
- [ ] All 8 figures labeled with `\label{fig:X}`
- [ ] All 13 tables formatted in LaTeX
- [ ] `\ref{}` replaces all markdown figure/table references
- [ ] (After Gemini) All Gemini cells populated, figures regenerated

### Key Files Reference

| File | Purpose | Action |
|------|---------|--------|
| `docs/paper/paper_draft.md` | Source markdown | READ: convert to LaTeX |
| `docs/paper/figures/*.pdf` | Figure PDFs | EMBED in LaTeX |
| `docs/paper/references.bib` | Bibliography | LINK via `\cite{}` |
| `docs/paper/appendix_*.md` | Appendix stubs | EXPAND into full appendix |
| `docs/paper/drafts/eval_findings_log.md` | Findings | READ: for Appendix C |

---

## Session 6 (Conditional): Final Review & Submission Prep

**Owner:** Samyak + Erel (joint)
**Objective:** End-to-end review per Gal's instruction #4. Final consistency. Submission prep.

**Dependency:** Session 5 complete. Gemini integrated.
**Only if timeline permits.** May merge into Session 5.

### Tasks
- [ ] Full end-to-end paper read (both authors)
- [ ] Verify all [PENDING] markers eliminated
- [ ] Verify teaser figure cross-references in every section
- [ ] Check 10-page limit compliance
- [ ] Anonymous GitHub repo created with code + specs
- [ ] Supplementary material packaged
- [ ] Final LaTeX compile + PDF review
