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

## Session 4b: Unified Figure Script — Deduplicate, Fix, Consolidate

**Owner:** Samyak
**Created:** 2026-04-01 (brainstorming session output)
**Objective:** Merge two inconsistent figure-generation scripts into one unified script
with consistent Okabe-Ito palette, scienceplots IEEE styling, deduplicated figures, and
a critical data-selection bug fix. Produces 10 generated figures (6 main body + 4 appendix)
plus the T2 LaTeX table.

**Dependency:** Session 4 complete. No Gemini data needed — script handles multi-model
dynamically when data arrives.

### Why This Session Exists

Two figure scripts exist with incompatible visual styles:

| Script | Figures | Palette | Style Library |
|--------|---------|---------|---------------|
| `scripts/evaluation/generate_paper_figures.py` (1,460 lines) | F1-F9, T2 | **Okabe-Ito** (colorblind-safe) | `scienceplots` + IEEE + hatching |
| `scripts/generate_appendix_c_figures.py` (946 lines) | C.1-C.7 | **Custom hex** (NOT colorblind-safe) | Plain matplotlib + serif |

**Problems discovered in 2026-04-01 session:**
1. **Color palette clash** — f-series uses Okabe-Ito (`#009E73` green, `#D55E00` vermillion),
   c-series uses custom colors (`#27ae60` green, `#C8607A` rose). A colorblind reviewer
   will struggle with c-series. ~20-35% chance at least one SC reviewer is colorblind.
2. **Visual inconsistency** — Different fonts, no hatching in c-series, no scienceplots.
   Looks like two different people made figures with no coordination.
3. **Overlapping figures** — C.1 ≈ F5 (heatmaps), C.7 ≈ F7 (augmentation), C.6 ≈ F9 (XSBench).
4. **Blocking data bug** — C.1 and C.5 use `sample_id is not None` filter which includes ALL
   1,018 records (base + samples + augmented) instead of just 468 true sample files. This
   corrupts the majority vote in the heatmap and invalidates pass@k calculations.
5. **Misplaced figures** — pass@k (C.5) and XSBench comparison (C.6) belong in main body,
   not appendix. These are standard LLM eval metrics and a core contribution argument.

### Design Decisions (approved in brainstorming)

1. **One unified script** — merge both into `scripts/generate_paper_figures.py`
2. **Deduplicate aggressively** — 10 generated figures, down from 16
3. **Okabe-Ito palette** + `scienceplots` IEEE style + hatching throughout
4. **Fix sample_id bug** — use filename-based `is_sample` flag (regex `-s\d+$`)
5. **Promote C.5 and C.6 to main body**, demote F2 and F4 to appendix
6. **`scienceplots` required** — ensure installed in `env_parbench`

### Figure Roster (Final)

**Main body (6 generated + 1 external drawio):**

| New ID | Old Source | Function Name | Description |
|--------|-----------|---------------|-------------|
| F1 | External `parbench_architecture.drawio` | N/A — not generated | System architecture |
| F2 | f-series F3 | `generate_f2_repo_vs_kernel()` | Repo vs kernel translation pair counts |
| F3 | f-series F5 | `generate_f3_kernel_heatmap()` | Kernel×model heatmap, multi-panel by direction |
| F4 | f-series F6 | `generate_f4_failure_taxonomy()` | Failure taxonomy stacked bars by model |
| F5 | c-series C.5 | `generate_f5_pass_at_k()` | pass@1 vs pass@3 by direction (**uses `is_sample` filter**) |
| F6 | c-series C.6 | `generate_f6_xsbench_comparison()` | ParBench kernel-level vs ParEval-Repo repo-level (0%) |
| F7 | f-series F7 | `generate_f7_augmentation()` | Augmentation robustness line chart, per-model |

**Appendix (4 generated):**

| New ID | Old Source | Function Name | Description |
|--------|-----------|---------------|-------------|
| C.1 | c-series C.2a | `generate_c1_repair_transitions()` | Self-repair transition matrix |
| C.2 | c-series C.2b | `generate_c2_repair_rate()` | Self-repair rate by direction |
| C.3 | c-series C.3 | `generate_c3_transform_frequency()` | Transform frequency heatmap per kernel |
| C.4 | f-series F4 | `generate_c4_selection_funnel()` | HeCBench selection funnel |

**Also generated:** `generate_t2_model_table()` — LaTeX model comparison table.

**Dropped entirely:**

| Old ID | Why Dropped |
|--------|-------------|
| f-series F1 (architecture) | External drawio — not script-generated |
| f-series F2 (API co-occurrence) | Survey detail — describe in Appendix A prose instead |
| f-series F8 (cross-direction bars) | Superseded by pass@k (F5) — more standard metric |
| f-series F9 (XSBench multi-model heatmap) | Superseded by F6 ParBench-vs-ParEval argument |
| c-series C.1 (kernel×direction heatmap) | Absorbed into F3 multi-model heatmap |
| c-series C.7 (level invariance) | Absorbed into F7 multi-model augmentation chart |

### Agent Team Structure

Use `/agent-team` with 3 teammates. **Critical: data-scout reports verified numbers
directly to BOTH script-writer and critic** so the critic has independent ground truth.

| Teammate | Role | Scope (file ownership) | Reports to |
|----------|------|------------------------|------------|
| **data-scout** | Extract verified stats from eval + augmentation data | `results/` (read-only) | script-writer AND critic |
| **script-writer** | Write unified `scripts/generate_paper_figures.py` | `scripts/generate_paper_figures.py` (overwrite), `docs/paper/appendix_findings.md` (edit), `docs/paper/paper_draft.md` (edit figure refs) | team lead |
| **critic** | Verify script output matches data-scout's numbers | All files (read-only) | team lead |

### Tasks

#### 4b.1 Install scienceplots
```bash
source env_parbench/bin/activate
pip install scienceplots
python3 -c "import scienceplots; print('OK')"
```

#### 4b.2 Data Extraction (data-scout teammate)
Extract from actual result files (NOT from this plan's numbers — they may be stale):

**From `results/evaluation/together-qwen-3.5-397b-a17b/` (1,018 files):**
- All unique kernels grouped by suite
- All unique directions with per-direction status counts
- Sample file count (filename matches `-s\d+$`): expect 468
- Base file count (no `-s\d+` or `-L\d+` suffix): expect 110
- Augmented file count (filename matches `-L\d+$`): expect 440
- Multi-attempt stats: count with `total_attempts > 1`, max attempts
- Self-repair transitions: initial attempt failure mode → final `overall_status`
- pass@k raw data: per kernel-direction, how many of [s0, s1, s2] PASS

**From `results/augmentation/`:**
- `eval_cuda.json`, `eval_omp.json`, `eval_opencl.json`: entry counts, transform type names from `transforms_applied`, per-kernel transform site counts
- `phase{3,4,5}_*.json`: entry counts per level per suite, PASS counts

Report as structured markdown tables. Send to script-writer and critic.

#### 4b.3 Write Unified Script (script-writer teammate)

Overwrite `scripts/generate_paper_figures.py` with a unified script containing:

**Shared foundation:**
- `scienceplots` with `["science", "ieee", "no-latex"]`
- Okabe-Ito status colors:
  ```python
  STATUS_COLORS = {
      "PASS": "#009E73",
      "BUILD_FAIL": "#D55E00",
      "RUN_FAIL": "#E69F00",
      "VERIFY_FAIL": "#0072B2",
      "EXTRACTION_FAIL": "#CC79A7",
  }
  ```
- Hatching patterns for b/w printing (same as current f-series `STATUS_HATCH`)
- 300 DPI PNG + vector PDF
- White backgrounds, `plt.tight_layout()`
- Single `load_eval_results(project_root, file_filter=None)` with `is_sample` field
  on every record (determined by filename regex `-s\d+$`, NOT by `sample_id` field)

**CLI:**
```bash
python3 scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir docs/paper/figures
# Single: --figure F3, --figure C.1, etc.
```

**Source code to reference:**
- Current f-series implementations: `scripts/evaluation/generate_paper_figures.py`
  - Lines 80-109: Okabe-Ito palette, STATUS_COLORS, STATUS_HATCH, MODEL_COLORS, MODEL_LINESTYLE
  - Lines 402-564: `generate_f1_architecture()` — SKIP (external drawio)
  - Lines 565-676: `generate_f2_api_cooccurrence()` — SKIP (dropped)
  - Lines 677-760: `generate_f3_repo_vs_kernel()` → becomes **F2**
  - Lines 761-939: `generate_f4_selection_funnel()` → becomes **C.4**
  - Lines 940-1070: `generate_f5_heatmap()` → becomes **F3** (absorb C.1 concept)
  - Lines 1071-1131: `generate_f6_taxonomy()` → becomes **F4**
  - Lines 1132-1210: `generate_f7_augmentation()` → becomes **F7**
  - Lines 1211-1307: `generate_f8_cross_direction()` — SKIP (replaced by F5 pass@k)
  - Lines 1308-1392: `generate_f9_xsbench()` — SKIP (replaced by F6)
  - Lines 1393+: `generate_t2_latex()` → keep as **T2**

- Current c-series implementations: `scripts/generate_appendix_c_figures.py`
  - Lines 274-394: `generate_c1_heatmap()` — SKIP (absorbed into F3)
  - Lines 395-469: `generate_c2a_transition_matrix()` → becomes **C.1**
  - Lines 470-539: `generate_c2b_repair_rate()` → becomes **C.2**
  - Lines 540-633: `generate_c3_transform_frequency()` → becomes **C.3**
  - Lines 634-713: `generate_c5_pass_at_k()` → becomes **F5** (FIX: use `is_sample` filter)
  - Lines 714-787: `generate_c6_xsbench_comparison()` → becomes **F6**
  - Lines 788-860: `generate_c7_level_invariance()` — SKIP (absorbed into F7)

**Critical bug fix for F5 (pass@k):**
```python
# WRONG (all 1,018 records pass this filter):
sample_records = [r for r in records if r.get("sample_id") is not None]

# CORRECT (only 468 true sample files):
sample_records = [r for r in records if r.get("is_sample", False)]
```

#### 4b.4 Update Paper References (script-writer teammate)

**`docs/paper/paper_draft.md`** — Update all figure/table references to new numbering:
- Old F3 → F2, old F5 → F3, old F6 → F4, C.5 → F5, C.6 → F6, old F7 → F7
- Remove references to dropped F2 (API co-occurrence), F8 (cross-direction), F9 (XSBench heatmap)
- Search for: `Figure 2`, `Figure 3`, `Figure 4`, `Figure 5`, `Figure 6`, `Figure 7`, `Figure 8`, `Figure 9`, `[FIGURE`

**`docs/paper/appendix_findings.md`** — Update C.1-C.4 references:
- Old C.2a → C.1, old C.2b → C.2, old C.3 → C.3, old F4 → C.4
- Remove old C.1 (kernel heatmap), old C.5 (promoted), old C.6 (promoted), old C.7 (absorbed)

#### 4b.5 Critic Review (critic teammate)

Using data-scout's verified numbers as ground truth, verify:
1. Every figure function uses Okabe-Ito hex values (not custom hex)
2. `is_sample` filter used in F3 and F5 (not `sample_id is not None`)
3. F5 pass@k formula: `pass@k = 1 - C(n-c, k) / C(n, k)` with n=3 (not n=8)
4. C.1 transition matrix counts match data-scout's self-repair numbers
5. C.3 transform types match data-scout's list (5 types, not 6)
6. All 10 figures generate without errors
7. Output file count: 20 PNG + 20 PDF = 22 total (10 figures × 2 formats + T2 .tex)
8. Paper draft figure references renumbered correctly (no stale F8/F9/old C.1)

#### 4b.6 Run and Verify
```bash
source env_parbench/bin/activate
python3 scripts/generate_paper_figures.py \
  --project-root /home/samyak/Desktop/parbench_sam \
  --figure all \
  --output-dir docs/paper/figures -v
```
Verify:
- 22 output files (10 figures × {png,pdf} + t2_model_comparison.tex + possibly old files to clean)
- Single-figure mode: `--figure F3` works, `--figure C.1` works
- No matplotlib warnings about missing fonts or styles

#### 4b.7 Cleanup
- Delete `scripts/generate_appendix_c_figures.py` (absorbed)
- Delete stale figure files: `docs/paper/figures/f1_*.{png,pdf}` (external drawio),
  `docs/paper/figures/f8_*.{png,pdf}`, `docs/paper/figures/f9_*.{png,pdf}`,
  `docs/paper/figures/c1_kernel_*.{png,pdf}`, `docs/paper/figures/c5_*.{png,pdf}`,
  `docs/paper/figures/c6_*.{png,pdf}`, `docs/paper/figures/c7_*.{png,pdf}`
- Update `scripts/evaluation/test_generate_paper_figures.py` if it imports from old locations

### Acceptance Criteria

- [ ] Single script `scripts/generate_paper_figures.py` generates all 10 figures + T2
- [ ] `scripts/generate_appendix_c_figures.py` deleted
- [ ] All figures use Okabe-Ito palette (verified by critic against hex values)
- [ ] All figures use scienceplots IEEE style with hatching
- [ ] F5 pass@k uses `is_sample` filter (468 records, not 1,018)
- [ ] F3 heatmap majority vote uses `is_sample` filter
- [ ] Paper draft figure references renumbered (no stale F8/F9/old C references)
- [ ] Appendix references updated (C.1-C.4 only)
- [ ] 22 output files generated without errors
- [ ] Critic confirms all numbers match data-scout's verified ground truth
- [ ] No stale figure files remain in `docs/paper/figures/`

### Key Files Reference

| File | Purpose | Action |
|------|---------|--------|
| `scripts/evaluation/generate_paper_figures.py` | Current f-series script (1,460 lines) | OVERWRITE with unified script |
| `scripts/generate_appendix_c_figures.py` | Current c-series script (946 lines) | DELETE after merge |
| `scripts/evaluation/test_generate_paper_figures.py` | Tests for figure script | UPDATE imports |
| `docs/paper/paper_draft.md` | Main paper | EDIT figure references |
| `docs/paper/appendix_findings.md` | Appendix C | EDIT figure references |
| `docs/paper/figures/` | Output directory | REGENERATE + DELETE stale |
| `results/evaluation/together-qwen-3.5-397b-a17b/` | 1,018 eval JSONs | READ (data-scout) |
| `results/augmentation/eval_*.json` | Augmentation eval data | READ (data-scout) |
| `results/augmentation/phase{3,4,5}_*.json` | Phase augmentation data | READ (data-scout) |

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: scienceplots` | `pip install scienceplots` in env_parbench |
| Figures look different from before | Expected — Okabe-Ito replaces custom palette |
| pass@k values changed from c-series | Expected — bug fix: n=3 not n=8 |
| `KeyError: 'is_sample'` | Ensure `load_eval_results()` sets `is_sample` on every record |
| Stale figures in output dir | Run 4b.7 cleanup step |

### Copy-Pasteable Claude Code Prompt

```
Session 4b: Unified Figure Script

Use /agent-team with 3 teammates: data-scout, script-writer, critic.

CONTEXT: Two figure scripts exist with incompatible styles:
- scripts/evaluation/generate_paper_figures.py (f-series, Okabe-Ito, scienceplots)
- scripts/generate_appendix_c_figures.py (c-series, custom hex, plain matplotlib)

Read the full Session 4b plan at:
docs/session_plans/sc26_paper_completion_plan.md (search for "Session 4b")

It contains the complete figure roster, agent team structure, source line references,
bug fix details, file ownership map, and acceptance criteria.

Key deliverables:
1. Unified scripts/generate_paper_figures.py with 10 figures (F2-F7 main, C.1-C.4 appendix) + T2
2. Delete scripts/generate_appendix_c_figures.py
3. Fix sample_id bug (use is_sample filename flag, not sample_id field)
4. Update paper_draft.md and appendix_findings.md figure references
5. All figures use Okabe-Ito + scienceplots + hatching
6. Critic verifies output against data-scout ground truth

Ground truth source: actual result JSON files in results/evaluation/ and results/augmentation/
Do NOT trust numbers in this prompt — extract fresh from data files.
```

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
