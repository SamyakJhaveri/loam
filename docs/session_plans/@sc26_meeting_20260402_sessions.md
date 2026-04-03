# SC26 Paper Sessions — Meeting Action Items (2026-04-02)

> **Source:** Meeting between Samyak Jhaveri and Niranjan Hasabnis, April 2, 2026.
> **Deadline:** SC26 paper submission 2026-04-08.
> **Created:** 2026-04-03. Plan-reviewed and corrected before writing.

---

## How to Use This File

Each session below is a self-contained unit of work for one Claude Code session.
Copy-paste the **Prompt** block into a fresh `/clear` session. Each prompt includes
all context needed — no prior conversation required.

**Before each session:**
1. `git checkout main && git pull`
2. Create branch: `git checkout -b session-<CODE>`
3. Activate venv: `source env_parbench/bin/activate`

**After each session:**
1. Run `/validate` before committing
2. Merge to main only after validation passes

---

## Parallel Tracks & Dependencies

```
Track A (augmentation story):
  [confound fix - DONE?] --> Session A1 (motivating examples) --> Session A2 (graphs)

Track B (benchmark characterization, independent):
  Session B1 (characterization table) --> feeds into Session E1

Track C (paper model update):
  Session C1 (Gemini->GPT replacement, can start NOW)
  [Le delivers GPT results] --> Session D1 (table review with real data)

Track D (paper writing, depends on A+B):
  Sessions A1 + B1 --> Session E1 (intro + multi-file emphasis)
```

**Can start TODAY (no blockers):** B1, C1
**Blocked on confound fix:** A1, A2
**Blocked on Le's GPT results:** D1 (partially)

---

## Cross-Cutting Directive (APPLIES TO ALL SESSIONS)

> **FRAMING RULE:** This is a BENCHMARK paper, not an LLM evaluation paper. When
> writing results, frame them as "demonstrating the benchmark" not "evaluating the
> models." The paper's contribution is ParBench (the tool), not which model is better.
> Source: Niranjan Hasabnis, 2026-04-02 meeting.

---

## Session A1: Find Augmentation Motivating Examples + LASSI Positioning

**Code:** `S-AUGMOTIV`
**Priority:** P0 (Niranjan: "most important task")
**Effort:** 3-5 hours
**Prerequisite:** Augmentation confound fix must be complete.

### Prompt

```
/clear

I need to find 2-3 specific benchmark kernels where augmentation reveals LLM weakness
— kernels that PASS at L0 but FAIL at higher augmentation levels (L3/L4), or show
degrading status (PASS -> VERIFY_FAIL -> BUILD_FAIL) as augmentation increases.

## Context

This is for the SC26 ParBench paper. Niranjan Hasabnis asked us to find "2 or 3 corner
benchmarks from our raw results where the quality of model output reduces at increasing
levels of augmentation from L0 to L4." The purpose is to MOTIVATE why augmentation is
needed in ParBench — to show it can reveal model weakness, differentiating us from LASSI
and other benchmarks.

## Current Statistical State

The AGGREGATE result is NULL: Cochran-Armitage z=-0.17, p=0.87 on cuda-to-omp (n=16
kernels per level). But individual kernels may show degradation even if the aggregate
does not (ecological fallacy). The aggregate result is actually a STRENGTH — it means
augmentation is safe. But we need individual examples to motivate the approach.

## CRITICAL: Data Filtering

- Parse individual result JSONs from `results/evaluation/together-qwen-3.5-397b-a17b/`
- Filter to PRIMARY campaign only — EXCLUDE pass@k files (those with `-s0`, `-s1`, `-s2` suffixes)
- For augmentation analysis: filter to cuda-to-omp direction files with `-L1` through `-L4` suffixes (no suffix = L0)
- Expected: ~16 kernels x 5 levels = ~80 files for cuda-to-omp augmentation
- NO pre-computed per-kernel x per-level matrix exists — you must build it from the raw JSONs

## What to Produce

1. A per-kernel x per-level matrix (kernel rows, L0-L4 columns, cells = overall_status)
   for cuda-to-omp direction. Save as `results/analysis/augmentation_per_kernel_matrix.json`

2. Identify 2-3 kernels showing ANY of:
   - PASS at L0, FAIL at L3 or L4
   - Status degradation across levels (e.g., PASS -> VERIFY_FAIL)
   - Interesting failure mode transitions (BUILD_FAIL at one level, different error at another)

3. If NO clear degradation examples exist, reframe: the null result itself is the finding.
   Models are robust to surface changes — augmentation probes a DIFFERENT axis (robustness)
   than difficulty. Write 1-2 paragraphs explaining this interpretation.

4. Write 2-3 paragraphs positioning against LASSI (arxiv:2407.01638):
   - LASSI achieves 80-85% with agentic self-correction
   - ParBench augmentation tests robustness to surface variation, not agentic repair
   - These are complementary, not competing — LASSI answers "can agents fix translations?"
     while ParBench augmentation answers "does the model rely on memorized patterns?"
   - The motivating examples (or null result) demonstrate the value of this probe

## Paper Context

- Augmentation robustness section: `docs/paper/latex/paper.tex` lines 756-820
- Current LASSI discussion: paper.tex line 754 and lines 913-919
- The paper already has the null result text (line 788) — we need to ADD motivating
  examples or strengthen the null-result interpretation

## Ground Truth Files

- `results/analysis/statistical_analysis.json` — check `generated_at` timestamp first;
  if it predates today, re-run the analysis script before proceeding
- `results/analysis/paper_data.json` — aggregated data
- Individual JSONs: `results/evaluation/together-qwen-3.5-397b-a17b/*.json`

## Verification

After producing the matrix, cross-check 3 random cells against the actual JSON files
to verify correctness. Report the matrix and any motivating examples found.
```

### Files Reference

| File | What | Lines |
|------|------|-------|
| `results/evaluation/together-qwen-3.5-397b-a17b/*-L*.json` | Raw augmented eval results | N/A |
| `results/analysis/statistical_analysis.json` | Aggregated stats (verify timestamp) | N/A |
| `docs/paper/latex/paper.tex` | Augmentation robustness section | 756-820 |
| `docs/paper/latex/paper.tex` | LASSI comparison | 754, 913-919 |

### Success Criteria

- [ ] Per-kernel x per-level matrix produced and saved
- [ ] 2-3 motivating examples found OR null-result interpretation strengthened
- [ ] LASSI positioning paragraphs written
- [ ] Paper text updated in augmentation robustness section
- [ ] All numbers cross-checked against raw JSON files

---

## Session A2: Augmentation Trend Graphs

**Code:** `S-AUGGRAPH`
**Priority:** P2 (Niranjan: "lower priority")
**Effort:** 2-3 hours
**Prerequisite:** Session A1 must be complete (need the motivating kernels).

### Prompt

```
/clear

Create publication-quality matplotlib figures showing augmentation level trends for
the SC26 ParBench paper.

## Context

Session A1 identified motivating kernels (or confirmed a null result) for augmentation
robustness. I need graphs for the paper's intro/motivation and results sections.

## What to Produce

1. **Per-kernel L0-L4 line plot** for 2-3 motivating kernels from Session A1:
   - X-axis: augmentation level (L0, L1, L2, L3, L4)
   - Y-axis: pass/fail status or pass rate
   - One line per kernel, with markers
   - If null result: show the flat lines as evidence of robustness

2. **Aggregate augmentation robustness plot** (update existing Figure 7):
   - X-axis: L0-L4
   - Y-axis: pass rate (%) with Wilson 95% CIs as error bars
   - One line for Qwen, placeholder for GPT-4.1-mini
   - Currently at `docs/paper/latex/f7_augmentation_robustness.pdf`

## Design Requirements

- Publication quality: use matplotlib with serif fonts, proper axis labels
- Color scheme: use Okabe-Ito colorblind-safe palette (project standard)
  - PASS: teal (#1B6573), BUILD_FAIL: rose (#E8384F), RUN_FAIL: saffron (#FFB347)
- Figure size: single-column (3.5 inches wide) for ACM/IEEE format
- Save as both PDF and PNG in `docs/paper/figures/`
- Include proper captions as comments in the script

## Data Source

- `results/analysis/augmentation_per_kernel_matrix.json` (produced by Session A1)
- `results/analysis/statistical_analysis.json` (aggregate CIs)
- Existing figure script: `scripts/generate_paper_figures.py` (extend, don't rewrite)

## Verification

- Visual check: do the plots match the numbers in the matrix?
- CI check: do error bars match Wilson CIs in statistical_analysis.json?
```

### Success Criteria

- [ ] Per-kernel trend plot(s) generated as PDF+PNG
- [ ] Aggregate robustness plot updated (Figure 7)
- [ ] Figures placed in `docs/paper/figures/`
- [ ] Paper.tex figure references updated if new figures added

---

## Session B1: Benchmark Characterization Table

**Code:** `S-BENCHCHAR`
**Priority:** P1
**Effort:** 3-4 hours
**Prerequisite:** None — can start immediately.

### Prompt

```
/clear

Build a quantitative benchmark characterization table for the SC26 ParBench paper.
Niranjan Hasabnis requested this to demonstrate ParBench's comprehensiveness with
concrete numbers, not just qualitative claims.

## FRAMING RULE
This is a BENCHMARK paper. The characterization table describes the benchmark itself,
independent of any LLM evaluation results.

## Dimensions to Include

### 1. Source Lines of Code (SLoC) per Kernel
- Extend existing `scripts/analysis/sloc_analysis.py` to cover ALL 35 kernels
  (currently only 18 evaluated Rodinia kernels have SLoC data)
- Count per-KERNEL, NOT per-spec (CUDA/OMP/OpenCL variants share source — count once)
- Existing data is in `results/analysis/sloc_analysis.json`
- Report: min, max, median, mean, total
- Existing finding: range 195-3,304 SLoC, median 309 (for 18 kernels)

### 2. Domain Category Distribution
- Source: `manifest.jsonl` has `category` field for each entry
- 12 categories exist: physics, ml, linear_algebra, graph, stencil, crypto,
  image, sort, molecular_dynamics, financial, reduction, other
- Produce a count per category

### 3. Single-File vs Multi-File Translation
- Check `translation_targets` arrays in spec JSONs
- Current data: 130 single-file, 76 multi-file out of 206 total specs
- Report breakdown per suite and per API

### 4. API Coverage Cross-Tab
- Rows: suites (Rodinia, HeCBench, XSBench, RSBench, mixbench)
- Columns: APIs (CUDA, OpenMP, OpenCL, OMP-target)
- Known data:
  - HeCBench: 65 CUDA, 60 OMP, 0 OpenCL, 10 OMP-target = 135
  - Rodinia: 22 CUDA, 18 OMP, 20 OpenCL, 0 OMP-target = 60
  - XSBench: 1+1+1+1 = 4
  - RSBench: 1+1+1+1 = 4
  - mixbench: 1+1+1+0 = 3
  Verify these against actual spec files on disk.

### 5. Language Feature Grep (SCOPED DOWN)
Niranjan suggested API version analysis. This is complex, so scope down to:
grep source files for 5-8 version-indicative features per API and report
presence/absence (not exhaustive version coverage).

Feature -> Version mapping table:

**OpenMP features:**
- `#pragma omp parallel` -> OpenMP 1.0
- `#pragma omp task` -> OpenMP 3.0
- `#pragma omp simd` -> OpenMP 4.0
- `#pragma omp target` -> OpenMP 4.5
- `omp_get_team_num` -> OpenMP 5.0

**CUDA features:**
- `__syncthreads` -> CUDA basic (all versions)
- `texture<` -> CUDA texture refs (deprecated in 12.0)
- `cudaMallocManaged` -> Unified Memory (CUDA 6.0+)
- `cooperative_groups` -> CUDA 9.0+
- `__shfl_sync` -> CUDA 9.0+ (replaced `__shfl`)

**OpenCL features:**
- `clCreateCommandQueue` -> OpenCL 1.x (deprecated 2.0)
- `clCreateCommandQueueWithProperties` -> OpenCL 2.0
- `clSVMAlloc` -> OpenCL 2.0

Grep these in the Rodinia, HeCBench, XSBench source directories.
Report: "ParBench kernels exercise OpenMP features from v1.0 through v4.5,
CUDA features from basic through 9.0+, etc."

### 6. Language Standard Distribution
- From spec JSONs: `implementation.language_standard` field
- Known: C++17 (majority), C++14, C++11, C11
- Report count per standard

## Where to Put the Table

Add to Section 4 (Benchmark Curation) of `docs/paper/latex/paper.tex` (after line 498,
before Section 5). The table should be called `tab:benchmark-characterization` and have
a clear caption explaining its purpose.

## Proposed Table Format (LaTeX)

Two tables:
1. **Suite-level summary** — rows = suites, cols = API counts + kernel count + SLoC range
2. **Feature coverage summary** — compact paragraph or small table listing API feature ranges

## Source Files

| File | Purpose |
|------|---------|
| `scripts/analysis/sloc_analysis.py` | Extend to all 35 kernels |
| `results/analysis/sloc_analysis.json` | Existing SLoC data (18 kernels) |
| `manifest.jsonl` | Category data, kernel names |
| `specs/*.json` | translation_targets (multi-file), language_standard |
| `rodinia/rodinia-src/` | Source files for Rodinia grep |
| `HeCBench-master/` | NOT AVAILABLE locally (gitignored) |
| `xsbench-src/` | XSBench source for grep |

NOTE: HeCBench source is NOT cloned locally. For the feature grep, focus on
Rodinia + XSBench + any sources that ARE on disk. Report which suites were analyzed.

## Verification

- Cross-check SLoC totals: sum of per-kernel SLoC should equal reported total
- Cross-check API counts against `ls specs/ | grep -c <api>`
- Verify category counts match `grep -c '"category"' manifest.jsonl` groupings
```

### Files Reference

| File | What |
|------|------|
| `scripts/analysis/sloc_analysis.py` | SLoC computation script (extend) |
| `results/analysis/sloc_analysis.json` | Existing 18-kernel SLoC data |
| `manifest.jsonl` | Kernel registry with categories |
| `specs/*.json` | Spec metadata |
| `docs/paper/latex/paper.tex` lines 350-498 | Benchmark Curation section |

### Success Criteria

- [ ] SLoC analysis extended to all 35 kernels
- [ ] Suite x API cross-tab verified against disk
- [ ] Category distribution computed
- [ ] Single-file vs multi-file breakdown per suite
- [ ] Language feature grep completed (Rodinia + XSBench)
- [ ] LaTeX table added to paper.tex Section 4
- [ ] All numbers verified against source files

---

## Session C1: Gemini to GPT-4.1-Mini Paper Replacement

**Code:** `S-MODELSWAP`
**Priority:** P0
**Effort:** 2-3 hours
**Prerequisite:** None — can start immediately.

### Prompt

```
/clear

Systematically replace all "Gemini 2.5 Flash" references in the SC26 ParBench paper
with "GPT-4.1 mini" (Azure deployment). This is NOT a simple find-and-replace — several
sections require rewriting because the model architecture framing changes.

## FRAMING RULE
This is a BENCHMARK paper, not an LLM evaluation paper. When updating model descriptions,
frame them as "demonstrating the benchmark on diverse models" not "comparing models."

## Context

The paper was written with Gemini 2.5 Flash as the second model. That has been replaced
by GPT-4.1 mini (via Azure OpenAI). Le Chen (ANL collaborator) is running the GPT evals.
GPT data has NOT arrived yet — use \pending{} placeholders for data, but update all
model identity references NOW.

## Scope of Changes

The paper has ~40+ lines referencing Gemini. Here is the complete inventory:

### Macro definitions (line 26-30)
- Line 28: `\newcommand{\pending}[1]{...PENDING-GEMINI...}` -> rename to PENDING-GPT
- Line 30: `\tbd` macro is fine (model-neutral)

### Abstract (line 60)
- "\pending{Gemini 2.5 Flash comparative results}" -> "\pending{GPT-4.1 mini comparative results}"

### Contributions (line 103)
- "\pending{Gemini 2.5 Flash comparative evaluation...MoE vs. dense}" -> update

### Key Findings (line 113)
- "\pending{Cross-model comparison awaiting Gemini data}" -> "awaiting GPT-4.1 mini data"

### Section 5.1 Models (lines 507-532) — REQUIRES REWRITING
- Line 512: Gemini 2.5 Flash description -> GPT-4.1 mini description
  GPT-4.1 mini: OpenAI model, accessed via Azure OpenAI. Architecture details
  may not be public — describe as "a compact model from the GPT-4.1 family"
- Line 517: "MoE vs. dense" framing -> RETHINK. GPT-4.1 mini architecture
  is not publicly documented as MoE or dense. Reframe as:
  "Two models were chosen to maximize provider diversity (Alibaba via Together AI
  vs. OpenAI via Azure), enabling cross-provider comparison under identical
  evaluation conditions."
- Line 529: Table row: Gemini -> GPT-4.1 mini, Google AI -> Azure OpenAI,
  Dense -> \pending{arch}, \pending{size} -> \pending{size}

### Section 5.5 Hardware (lines 576-596) — update column header
- Line 576: "Gemini 2.5 Flash evaluations are conducted by a collaborator" -> 
  "GPT-4.1 mini evaluations are conducted by a collaborator"
- Line 585: Table header "Gemini (collaborator)" -> "GPT-4.1 mini (collaborator)"
- Lines 587-593: Keep \pending{} placeholders (Le will provide hardware info)

### Results tables
- Line 621: "Gemini 2.5 Flash" row -> "GPT-4.1 mini" row (keep \tbd values)
- Line 739: Self-repair table "Gemini Flash" column -> "GPT-4.1 mini"
- Line 770: Augmentation table "Gemini Flash" column -> "GPT-4.1 mini"
- Line 804: Direction table "Gemini Flash" column -> "GPT-4.1 mini"
- Line 841: pass@k table "Gemini 2.5 Flash" -> "GPT-4.1 mini"

### Discussion
- Line 631: "\pending{Chi-squared...awaiting Gemini}" -> "awaiting GPT-4.1 mini"
- Line 677: "\pending{Expand to multi-model...Gemini}" -> "GPT-4.1 mini"
- Line 717: "\pending{Tier boundaries...two-model consensus}" -> keep as-is (model-neutral)
- Line 790: "\pending{Cross-model augmentation...Gemini}" -> "GPT-4.1 mini"
- Line 824: "\pending{Per-suite...Gemini data}" -> "GPT-4.1 mini data"
- Line 876: Stats summary table "Gemini augmentation" -> "GPT-4.1 mini augmentation"
- Line 878: Same table
- Line 911: "\pending{Cross-model...Gemini campaign}" -> "GPT-4.1 mini campaign"
- Line 928: "\pending{Cross-model...Gemini data}" -> "GPT-4.1 mini data"
- Line 935: "\pending{MoE vs. dense...Gemini}" -> rewrite to match new framing
- Line 950: "Two-model...MoE and dense" -> "Two models...distinct providers"
- Line 963: "\pending{...Gemini data}" -> "GPT-4.1 mini data"

### Conclusion (line 983)
- "\pending{Gemini 2.5 Flash comparative results}" -> "GPT-4.1 mini"

## Key Rewriting Decisions

1. **"MoE vs. dense" framing** (appears ~5 times): Replace with "provider diversity" or
   "cross-provider comparison." Only use architecture framing if GPT-4.1 mini's architecture
   is publicly documented. If uncertain, say "architecture details for GPT-4.1 mini are
   not publicly documented" and use provider-diversity framing.

2. **Model description paragraph** (line 512): Write new paragraph for GPT-4.1 mini.
   Key facts: OpenAI model family, accessed via Azure OpenAI endpoint, temperature=0,
   reasoning/chain-of-thought disabled. Don't fabricate parameter counts.

3. **\pending{} macro**: Rename from PENDING-GEMINI to PENDING-GPT or just PENDING.

## Verification

After all changes:
1. `grep -n "Gemini\|gemini" docs/paper/latex/paper.tex` -> should return 0 lines
2. `grep -n "PENDING-GEMINI" docs/paper/latex/paper.tex` -> should return 0 lines
3. `grep -c "pending" docs/paper/latex/paper.tex` -> count remaining placeholders
4. Read the Models section (lines 507-532) end-to-end for coherence
5. Read the Discussion model capability section (lines 908-919) for coherence
```

### Files Reference

| File | Lines | What Changes |
|------|-------|-------------|
| `docs/paper/latex/paper.tex` | 28 | `\pending` macro rename |
| `docs/paper/latex/paper.tex` | 60, 103, 113 | Abstract + contributions |
| `docs/paper/latex/paper.tex` | 507-532 | Models section (REWRITE) |
| `docs/paper/latex/paper.tex` | 576-596 | Hardware table |
| `docs/paper/latex/paper.tex` | 621, 739, 770, 804, 841 | Results tables |
| `docs/paper/latex/paper.tex` | 631, 677, 790, 824, 876, 878, 911, 928, 935, 950, 963 | Discussion |
| `docs/paper/latex/paper.tex` | 983 | Conclusion |

### Success Criteria

- [ ] Zero occurrences of "Gemini" or "PENDING-GEMINI" in paper.tex
- [ ] Models section coherently describes Qwen + GPT-4.1 mini
- [ ] "MoE vs. dense" framing replaced with provider-diversity framing
- [ ] All \pending{} placeholders updated to reference GPT-4.1 mini
- [ ] Paper compiles without errors (if LaTeX toolchain available)

---

## Session D1: Review and Fix Paper Tables

**Code:** `S-TABLEFIX`
**Priority:** P1
**Effort:** 2-3 hours
**Prerequisite:** Session C1 should be done first (model references). Partially blocked on Le's GPT results.

### Prompt

```
/clear

Review all tables in the SC26 ParBench paper for relevance, correctness, labeling,
and caption quality. Verify every number against ground truth data files.

## FRAMING RULE
This is a BENCHMARK paper. Tables should demonstrate benchmark coverage and
evaluation methodology, not focus on model comparison rankings.

## Tables to Review

The paper has 10+ table environments. For each one:
1. Is it relevant? Does it contribute to the paper's argument?
2. Are column labels clear and intuitive?
3. Is the caption self-contained (reader can understand the table without reading body text)?
4. Does every number match the ground truth data?

### Table Inventory

| Table | Line | Caption | Ground Truth Source |
|-------|------|---------|-------------------|
| tab:augmentation-levels | 304 | Augmentation level defs | `c_augmentation/augment_dataset.py:111` LEVEL_FRACTIONS |
| tab:survey | 369 | Survey kernel pair counts | `analysis/data/API_pairwise_coverage_matrix*.csv` |
| tab:suite-summary | 467 | Suite summary (kernels, specs) | `manifest.jsonl` + `specs/` file count |
| tab:model-config | 519 | Model configurations | Pipeline MODEL_REGISTRY + provider docs |
| tab:hardware | 578 | Hardware/software config | Actual system (`nvcc --version`, `gcc --version`) |
| Overall pass rates | 611 | Pass rates per model | `results/analysis/paper_data.json` |
| tab:self-repair-transitions | 655 | Self-repair transitions | `results/analysis/selfrepair_analysis.json` |
| tab:self-repair | 732 | Self-repair effectiveness | `results/analysis/selfrepair_analysis.json` |
| tab:augmentation-rates | 763 | Augmentation level pass rates | `results/analysis/statistical_analysis.json` |
| tab:direction-rates | 797 | Direction pass rates | `results/analysis/paper_data.json` |
| pass@k table | 833 | pass@k results | `results/analysis/paper_data.json` |
| tab:stats-summary | 862 | Statistical tests summary | `results/analysis/statistical_analysis.json` |

### Specific Checks

1. **tab:suite-summary (line 467):** Claims "35 kernels, 96 specs". Verify:
   - Count unique kernel names in manifest.jsonl
   - Count spec files on disk: `ls specs/*.json | wc -l`
   - These should match the table

2. **tab:model-config (line 519):** After Session C1, this should show GPT-4.1 mini
   instead of Gemini. Verify the replacement was done correctly.

3. **Overall pass rates (line 611):** Qwen row claims 36.2% [32.1%, 40.6%].
   Verify against `paper_data.json` -> `overall` -> `pass_rate`.

4. **tab:augmentation-rates (line 763):** All 5 level rows for Qwen.
   Cross-check each cell against `statistical_analysis.json` -> `by_level`.

5. **tab:direction-rates (line 797):** 6 direction rows.
   Cross-check each against `paper_data.json` -> `by_direction`.

6. **tab:stats-summary (line 862):** Statistical test results.
   Verify p-values, test statistics against `statistical_analysis.json`.

## Write for Qwen-Only + Placeholders

GPT-4.1 mini data hasn't arrived from Le Chen yet. All GPT columns should use
\tbd or \pending{} placeholders. Do NOT fabricate numbers.

## Ground Truth Files

- `results/analysis/paper_data.json` (44 KB) — primary aggregated data
- `results/analysis/statistical_analysis.json` (31 KB) — all statistical tests
- `results/analysis/selfrepair_analysis.json` (9.4 KB) — self-repair stats
- `results/analysis/error_taxonomy.json` (393 KB) — failure classification
- `manifest.jsonl` — kernel/spec counts

## Verification

For each table, report: "Table X: [N] cells checked, [M] corrections made, [details]."
If a number is wrong, fix it AND note the source of the error.
```

### Success Criteria

- [ ] Every table reviewed for relevance and clarity
- [ ] Every numerical cell cross-checked against ground truth JSON
- [ ] Captions are self-contained and intuitive
- [ ] Column labels are clear
- [ ] All corrections documented with before/after values
- [ ] GPT-4.1 mini columns use \pending{} or \tbd (no fabricated numbers)

---

## Session E1: Quantitative Intro Highlights + Multi-File Emphasis

**Code:** `S-INTROHIGH`
**Priority:** P1
**Effort:** 2-3 hours
**Prerequisite:** Session B1 (characterization data) should be done first.

### Prompt

```
/clear

Strengthen the SC26 ParBench paper's introduction with quantitative benchmark highlights,
and elevate the multi-file translation handling as a key differentiator.

## FRAMING RULE
This is a BENCHMARK paper. The introduction should sell ParBench as a comprehensive,
well-engineered evaluation tool — not as a model comparison study.

## Context

Niranjan Hasabnis (2026-04-02 meeting) emphasized: "These are the highlights of the
benchmark and we should bring this point also in the introduction... that way it's easy
to distinguish our benchmark than existing ones." He also stressed that "reviewers will
point out if you are trying to standardize all of these kernels... how are you making
sure that the LLM is evaluated on kernel writing capacity and not the capacity to write
helper functions."

## Task 1: Quantitative Highlights in Introduction

Read the current introduction (paper.tex lines 66-123). It has qualitative claims that
need quantitative backing. Weave in these numbers (verify against Session B1 output):

- 35 kernels across 5 benchmark suites (Rodinia, HeCBench, XSBench, RSBench, mixbench)
- 96 / 206 specifications (96 primary evaluation, 206 total including HeCBench)
- 4 parallel APIs (CUDA, OpenMP, OpenCL, OpenMP-target)
- SLoC range from Session B1 output (currently 195-3,304, median 309 for 18 kernels —
  will be updated with all 35 kernels after B1)
- Multi-file translation: 36.9% of specs require multi-file translation
- 6 AST-driven augmentation transforms at 5 levels
- Build-run-verify (not just syntax/compilation checking)
- Comparison: ParBench median SLoC is 2.3x larger than ParEval-Repo's ~133 SLoC average

Keep the introduction concise — aim for 1-2 additional sentences per highlight, woven
into existing paragraphs. Do NOT add a bulleted list of numbers.

## Task 2: Multi-File Emphasis

The complexity taxonomy (single_file, multi_to_single, single_to_multi, multi_to_multi)
is currently defined at paper.tex line 343 in Section 3.4. It needs:

1. **More prominent mention in intro** (Section 1): Add 1-2 sentences explaining that
   ParBench handles multi-file kernels by isolating translation targets from support
   infrastructure. This is a key engineering achievement that reviewers will look for.

2. **Quantitative breakdown in Section 4** (Benchmark Curation, lines 462-498):
   Add the file-cardinality distribution from Session B1's characterization data.
   How many specs are single_file vs multi_to_single vs multi_to_multi?

3. **Reviewer defense point**: Emphasize that by feeding only `translation_targets`
   to the LLM (not Makefiles, headers, serial baselines), ParBench evaluates kernel
   writing capacity specifically, not peripheral helper function generation.

## Task 3: Benchmark Differentiation in Introduction

Read the "Gap in Existing Evaluation" subsection (lines 76-91). Strengthen the
differentiation from:
- HumanEval/SWE-bench: sequential code only (already stated)
- ParEval: synthesis from description, not translation (already stated)
- ParEval-Repo: repository-level, 0% pass (already stated)
- LASSI: agentic repair, not robustness probing (may need strengthening)

Add any differentiation points that emerged from the meeting:
- Real HPC benchmark codes (not synthetic)
- Multi-suite, multi-API coverage
- Quantitative evidence of comprehensiveness (from B1 characterization)

## Files

| File | Lines | What |
|------|-------|------|
| `docs/paper/latex/paper.tex` | 66-123 | Introduction |
| `docs/paper/latex/paper.tex` | 76-91 | Gap in Existing Evaluation |
| `docs/paper/latex/paper.tex` | 326-343 | Eval Pipeline + Complexity taxonomy |
| `docs/paper/latex/paper.tex` | 462-498 | Evaluation Corpus |
| `results/analysis/sloc_analysis.json` | N/A | SLoC data (updated by B1) |

## Verification

1. Word count check: introduction should fit in ~1.5 columns (not grow to 2+ pages)
2. All numbers cited in intro must appear with sources in later sections
3. grep for any numbers you added — verify each against the source file
```

### Success Criteria

- [ ] Introduction has quantitative highlights woven in naturally
- [ ] Multi-file translation emphasized in intro + Section 4
- [ ] Kernel isolation / translation target methodology highlighted
- [ ] Benchmark differentiation strengthened with numbers
- [ ] Introduction length stays within ~1.5 columns
- [ ] All added numbers verified against data files

---



## Session 7 (Conditional): Final Review & Submission Prep

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

## Summary: Session Execution Order

| Order | Session | Code | Priority | Blocked On |
|-------|---------|------|----------|------------|
| 1 | Benchmark Characterization | S-BENCHCHAR | P1 | Nothing (start now) |
| 2 | Gemini->GPT Replacement | S-MODELSWAP | P0 | Nothing (start now) |
| 3 | Augmentation Motivating Examples | S-AUGMOTIV | P0 | Confound fix session |
| 4 | Intro Highlights + Multi-File | S-INTROHIGH | P1 | B1 done |
| 5 | Table Review | S-TABLEFIX | P1 | C1 done; partially on Le's GPT data |
| 6 | Augmentation Trend Graphs | S-AUGGRAPH | P2 | A1 done |
