# Phase 4: Methodology & Reviewer Defense - Research

**Researched:** 2026-04-05
**Domain:** SC26 paper methodology writing (LaTeX), statistical justification, reviewer defense prose
**Confidence:** HIGH

## Summary

Phase 4 writes methodology defense text into four locations in `paper.tex`: (1) kernel isolation defense paragraph in Section 3.4, (2) statistical test justification rewrite in Section 5.4, (3) conjunction verification defense in Section 3.2, and (4) reproducibility version pins in Section 5.5. All four METHOD requirements involve writing prose into existing LaTeX sections -- no new data generation, no new analysis scripts, no figure production.

The research identifies exact line numbers, verifies all quantitative claims against ground truth files, confirms the specific VERIFY_FAIL kernel example for the conjunction defense, and documents the discrepancies between old Rodinia-only analysis files and the new all-suite quantitative_findings.json. The Bonferroni alpha correction update (0.0167 to 0.0125) is confirmed as required. The factual error at line 644 (Fisher's exact test, should be McNemar's) is confirmed.

**Primary recommendation:** Execute all four edits as independent tasks against paper.tex, each with a verification step that greps the modified text and confirms provenance comments cite `quantitative_findings.json` field paths.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Consolidate kernel isolation into ONE authoritative paragraph at the TOP of Section 3.4. Reviewer reads WHY first (rationale), then HOW (existing technical description becomes second paragraph).
- **D-02:** Include preemptive defense against the "making it too easy" reviewer objection. Use analytical framing: "We isolate translation skill from build-system generation because they are orthogonal competencies."
- **D-03:** Three-layer evidence structure: (1) XSBench same-kernel comparison -- ParEval-Repo 0% vs ParBench 64.2% CUDA-to-OMP overall across all 5 suites (77/120 tasks; 68.8% at L0 on the 16-kernel balanced Rodinia subset). (2) 31/35 kernels exceeding ParEval-Repo's 133 SLoC threshold. (3) 33.9% BUILD_FAIL rate (237/700 across all 5 suites).
- **D-04:** Keep existing XSBench mentions in abstract, related work, and results as-is. The new consolidated paragraph is the authoritative version.
- **D-05:** Full rewrite of the statistical sentence at line ~644 (Metrics subsection). Current text says "Fisher's exact test" -- factually incorrect. Rewrite to name all three tests with brief rationale.
- **D-06:** Justify all three tests used: Wilson CI, Cochran-Armitage, and McNemar. Each gets 1-2 sentences in the Metrics subsection.
- **D-07:** Briefly name the rejected alternative for each test.
- **D-07b:** Update Bonferroni correction threshold from alpha=0.0167 (3 tests) to alpha=0.0125 (4 tests, matching statistical_analysis.json). Update the source comment at line ~992.
- **D-08:** Place conjunction verification defense at end of Section 3.2 (Harness Pipeline), after describing the verify stage.
- **D-09:** Use a compilation-only misclassification example: a real VERIFY_FAIL kernel from the Qwen results where the translation compiles and runs (exit_code=0) but produces wrong output.
- **D-10:** Cite the 7.3% VERIFY_FAIL rate (51/700 across all 5 suites) as the quantitative backing.
- **D-11:** Keep focused on core conjunction (exit_code AND stdout_pattern) vs alternatives. Do NOT repeat the clBuildProgram kernel-only scan.
- **D-12:** Add 2-3 sentences at end of Section 5.5 (after the hardware/software table, after line ~681).
- **D-13:** Content: ParBench commit hash, Rodinia submodule commit pin (9c10d3ea), model API version dates, data availability statement.
- **D-14:** Tone: factual pins, not boilerplate.

### Claude's Discretion
- Exact wording and sentence structure of each paragraph
- Whether to add a LaTeX source comment citing the data source for each number
- How to handle the transition between the new rationale paragraph and existing technical paragraph in Section 3.4
- Specific VERIFY_FAIL kernel to use as the conjunction verification example (pick from Qwen results during planning)
- Exact commit hash to cite (use `git rev-parse HEAD` at execution time)

### Deferred Ideas (OUT OF SCOPE)
None -- all four METHOD requirements are now active (METHOD-03 promoted from deferred).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| METHOD-01 | Kernel isolation methodology explicitly justified: ParEval-Repo 0% on XSBench vs ParBench 68.8% on same kernel | Verified: quantitative_findings.json Campaign 1 direction_pass_rates cuda-to-omp L0=66.7% (24 tasks); all-levels=64.2% (77/120); 68.8% is balanced Rodinia L0 subset (16 kernels). SLoC: 31/35 above 133 SLoC threshold [VERIFIED: sloc_analysis.json]. BUILD_FAIL: 237/700=33.9% [VERIFIED: quantitative_findings.json] |
| METHOD-02 | Statistical test choices justified in text: why Cochran-Armitage, McNemar, Wilson CIs | Verified: paper currently says "Fisher's exact test" at line 644 which is WRONG -- actual analysis uses McNemar. Wilson CIs, Cochran-Armitage, and McNemar are the three tests used. Line 1012 has partial justification already; line 644 needs full rewrite. Bonferroni alpha should be 0.0125 (4 tests) per D-07b |
| METHOD-03 | Reproducibility claims backed by specific version pins | Verified: git hash = befe2ac (will use HEAD at execution time), Rodinia submodule = 9c10d3ea, CUDA 12.3/nvcc V12.3.103, GCC 12.4.0, Ubuntu 24.04 LTS, Python 3.12.3, RTX 4070 [VERIFIED: compiler_inventory.txt, git submodule status] |
| METHOD-04 | Conjunction verification (exit_code AND stdout_pattern) justified vs alternatives | Verified: 51/700=7.3% VERIFY_FAIL [VERIFIED: quantitative_findings.json]. Best example: rodinia-gaussian-opencl-to-gaussian-cuda L0 -- compiles, runs (exit_code=0), but stdout missing "Total:" pattern. All 3 attempts: build=pass, run=pass, verify=fail. Compilation-only would misclassify as PASS |
</phase_requirements>

## Project Constraints (from CLAUDE.md)

- `python3` always, never `python`
- Result JSONs are immutable -- never modify existing result JSONs
- Read before editing; no partial implementations; verify before reporting done
- `ultrathink` for architecture, eval pipeline, spec correctness, augmentation, published results
- `/validate` before every commit
- Pre-commit hook enforces `.validation_passed` sentinel
- Ruff runs automatically via PostToolUse hook on every Edit/Write to `.py` files
- Phase 4 edits `paper.tex` only -- no Python files, no result JSONs

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| LaTeX (IEEE) | IEEEtran | Paper formatting | SC26 requires IEEE double-column format [VERIFIED: paper.tex documentclass] |
| quantitative_findings.json | 2026-04-05 | Primary provenance source | Phase 9 output; provenance-tracked findings with field-level source attribution [VERIFIED: file metadata] |
| statistical_analysis.json | 2026-04-04 | McNemar/Wilson/Cochran-Armitage values | Cross-check source for statistical test values [VERIFIED: file exists] |
| sloc_analysis.json | — | SLoC data and ParEval threshold | 31/35 kernels above 133 SLoC [VERIFIED: file content] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| compiler_inventory.txt | — | Version pins for reproducibility section | When writing METHOD-03 reproducibility paragraph |
| error_taxonomy.json | — | Per-kernel failure breakdown | If needed for VERIFY_FAIL detail beyond quantitative_findings |

## Architecture Patterns

### Edit Locations in paper.tex (VERIFIED line numbers)

```
docs/paper/latex/paper.tex
├── Line 299  \subsection{Harness Pipeline: Build, Run, Verify}     # METHOD-04 target (end of section, before line 312)
├── Line 356  \subsection{Evaluation Pipeline: Kernel-Centric Translation}  # METHOD-01 target (new paragraph at TOP)
├── Line 635  \subsection{Metrics}                                   # METHOD-02 target (line 644 full rewrite)
├── Line 648  \subsection{Hardware and Software}                     # METHOD-03 target (after table, after line 681)
├── Line 985  \subsection{Statistical Summary}                       # Bonferroni alpha update (line 992 comment + line 1005-1007 values)
└── Line 1012 Methodological notes                                   # Extended justification text
```

**CRITICAL: Line numbers are approximate.** The paper is actively being edited. The planner MUST grep for subsection labels (`\subsection{Harness Pipeline}`, `\subsection{Metrics}`, etc.) to find actual boundaries before creating edit tasks.

### Pattern 1: Provenance Comment Convention
**What:** Every numerical claim gets a LaTeX source comment pointing to the JSON field path
**When to use:** Every time a number from analysis files is cited in paper text
**Example:**
```latex
% src: quantitative_findings.json > campaign_1.failure_taxonomy.status_counts.VERIFY_FAIL = 51/700 = 7.3%
conjunction verification catches 7.3\% of translations (51 of 700 tasks)
```
[VERIFIED: This pattern is already established in paper.tex -- see lines 651-656, 898, 990-992]

### Pattern 2: Analytical Framing (not Rebuttal Tone)
**What:** Defense text uses "measurement design choice" language, not "one might argue" language
**When to use:** All four methodology paragraphs
**Example:**
```latex
% GOOD (analytical):
We isolate translation skill from build-system generation because
they are orthogonal competencies.

% BAD (rebuttal):
One might argue that providing build infrastructure makes the
task too easy, but we contend that...
```
[VERIFIED: D-02 explicitly requires this framing]

### Anti-Patterns to Avoid
- **Do NOT rewrite existing technical paragraphs.** The kernel-centric methodology paragraph (line 361) already describes HOW kernel isolation works. Phase 4 adds WHY at the top, not replacing what's there.
- **Do NOT update the statistical summary TABLE values.** Phase 4 writes methodology justification TEXT and updates Bonferroni alpha. The table values (McNemar n, p, h) may need updating for all-suite scope, but that is Phase 11's job unless they are directly part of the methodology sentence rewrite.
- **Do NOT introduce new \pending{} markers.** Phase 4 should not create new TODOs -- it resolves methodology gaps.
- **Do NOT repeat the clBuildProgram false-positive scan** already described at line 369. D-11 explicitly prohibits this.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Statistical test justifications | Inventing rationale from scratch | Standard statistical methodology literature | SC reviewers are domain experts who know these tests |
| Number verification | Manually counting from result files | `quantitative_findings.json` field paths | Phase 9 already computed and provenance-tracked all numbers |
| Commit hash | Hardcoding a specific hash | `git rev-parse HEAD` at execution time | Hash changes with every commit; must be current at paper-writing time |

## Verified Data for Each Requirement

### METHOD-01: Kernel Isolation Defense Numbers [VERIFIED]

| Claim | Source | Value | JSON Path |
|-------|--------|-------|-----------|
| ParEval-Repo 0% on XSBench | Literature cite | 0% | `\cite{ParEvalRepo2025}` (external) |
| ParBench CUDA-to-OMP all-suite all-levels | quantitative_findings.json | 64.2% (77/120) | `campaign_1.augmentation_trends.per_direction.cuda-to-omp` (sum across L0-L4: 16+14+17+14+16=77 of 24*5=120) |
| ParBench CUDA-to-OMP L0 balanced Rodinia | quantitative_findings.json | 66.7% at L0 (n=24) | `campaign_1.direction_pass_rates.standard.cuda-to-omp` |
| 31/35 kernels above 133 SLoC | sloc_analysis.json | 31 (88.6%) | `summary.kernels_above_pareval_threshold` |
| BUILD_FAIL rate all-suite | quantitative_findings.json | 237/700 = 33.9% | `campaign_1.failure_taxonomy.status_counts.BUILD_FAIL` |

**NOTE on 68.8%:** The CONTEXT.md cites "68.8% at L0 on the 16-kernel balanced Rodinia subset." This is from the OLD Rodinia-only paper_data.json scope (11/16 = 68.75%). The all-suite L0 rate is 66.7% (16/24). The 68.8% remains valid for the parenthetical reference since the paper's Results section (Section 6) uses the balanced Rodinia subset for augmentation analysis. The primary figure for methodology defense is the 64.2% all-suite rate. [VERIFIED: 16/24 L0 = 66.7%; 77/120 all-levels = 64.2%; 11/16 balanced = 68.75%]

### METHOD-02: Statistical Test Values [VERIFIED]

| Test | Current Paper | Correct Value | Source |
|------|--------------|---------------|--------|
| Line 644: "Fisher's exact test" | Fisher's exact | **McNemar's test** (paired kernel design) | CONTEXT.md D-05 + actual analysis |
| Wilson CI | Correctly named | Wilson score 95% CI | quantitative_findings.json (all CIs) |
| Cochran-Armitage | z=-0.17, p=0.87 (old Rodinia) | z=-0.77, p=0.44 (all-suite Campaign 1) | quantitative_findings.json > campaign_1.augmentation_trends.aggregate.cochran_armitage |
| McNemar Bonferroni alpha | 0.0167 (3 tests) | **0.0125 (4 tests)** | quantitative_findings.json + statistical_analysis.json (alpha_corrected=0.0125) |
| McNemar cuda-omp | n=16, p=0.625, h=0.26 (old Rodinia) | n=24, p=0.6875, h=-0.1724 (all-suite) | quantitative_findings.json > campaign_1.direction_asymmetry |

**CRITICAL DISCREPANCY:** The Cochran-Armitage and McNemar values in the paper come from old Rodinia-only scope (paper_data.json, statistical_analysis.json). The quantitative_findings.json has updated all-suite Campaign 1 values that are different. Phase 4 writes the METHODOLOGY TEXT justifying the tests; whether to update the TABLE VALUES with all-suite numbers is a decision for Phase 11 (Paper TeX Integration) or must be coordinated. The planner should note this: methodology text can justify the tests generically (the justification is the same regardless of scope), but the Bonferroni alpha update (D-07b) changes a specific number.

### METHOD-03: Reproducibility Pins [VERIFIED]

| Pin | Value | Source |
|-----|-------|--------|
| ParBench commit hash | `befe2ac` (use HEAD at execution) | `git rev-parse HEAD` |
| Rodinia submodule commit | `9c10d3ea` | `git submodule status` |
| CUDA toolkit | HPC SDK 24.3, CUDA 12.3, nvcc V12.3.103 | compiler_inventory.txt |
| GCC | 12.4.0 (Ubuntu 12.4.0-2ubuntu1~24.04) | compiler_inventory.txt |
| OS | Ubuntu 24.04 LTS, kernel 6.8.0-40-generic | paper.tex line 657 |
| GPU | NVIDIA GeForce RTX 4070 (sm_89) | paper.tex line 657 |
| Python | 3.12.3 | compiler_inventory.txt |
| Qwen 3.5 397B-A17B | Via Together AI API | CONTEXT.md D-13 |

**NOTE:** The existing Section 5.5 (lines 657-681) already contains most hardware/software details. D-12 adds 2-3 sentences AFTER the table (after line 681) with commit hash, submodule pin, API access dates, and data availability. This is a small addition, not a rewrite.

### METHOD-04: Conjunction Verification VERIFY_FAIL Example [VERIFIED]

**Recommended example: `rodinia-gaussian-opencl-to-rodinia-gaussian-cuda` (L0)**

| Property | Value |
|----------|-------|
| File | `results/evaluation/together-qwen-3.5-397b-a17b/rodinia-gaussian-opencl-to-rodinia-gaussian-cuda.json` |
| Kernel | gaussian |
| Direction | OpenCL to CUDA |
| Augmentation | L0 (unmodified source) |
| Overall status | VERIFY_FAIL |
| Build status | pass (all 3 attempts) |
| Run status | pass (all 3 attempts) |
| Run exit code | 0 |
| Verify strategy | stdout_pattern |
| Error message | "Pattern 'Total:' NOT found in stdout" |
| Stdout snippet | "WG size of kernel 1 = 256, WG size of kernel 2= 16 X 16\nCreate matrix internally..." |

**Why this is the ideal example:** The translation compiles successfully, runs to completion with exit_code=0, and even produces partial output (matrix creation messages). But it does NOT produce the expected "Total:" timing line that the reference implementation prints. A compilation-only verifier would classify this as PASS. Even an exit-code-only verifier would misclassify it (exit_code=0). Only the conjunction of exit_code=0 AND stdout_pattern matching catches this as a failure. The fact that ALL 3 self-repair attempts also fail with the same pattern makes it even more compelling: this is not a flaky failure but a systematic translation deficiency.

**Backup examples (also strong):**
- `rodinia-cfd-omp-to-rodinia-cfd-opencl` (L0): All 3 attempts build+run pass, verify fail
- `rodinia-kmeans-omp-to-rodinia-kmeans-opencl` (L0): All 3 attempts build+run pass, verify fail

**Quantitative backing:**
- 51/700 = 7.3% VERIFY_FAIL across Campaign 1 [VERIFIED: quantitative_findings.json]
- 46/51 are "wrong_numerical_output" subcategory [VERIFIED: quantitative_findings.json]
- 5/51 are "missing_output" [VERIFIED: quantitative_findings.json]

## Common Pitfalls

### Pitfall 1: Stale Line Numbers
**What goes wrong:** Paper is actively being edited. Hardcoded line numbers from CONTEXT.md or this research become wrong after any edit.
**Why it happens:** Multiple phases and sessions edit paper.tex.
**How to avoid:** ALWAYS grep for subsection labels (`\subsection{Harness Pipeline}`, `\label{sec:metrics}`, etc.) before editing. Never use line numbers without first verifying them.
**Warning signs:** Edit inserts text in the wrong location.

### Pitfall 2: Scope Confusion (Rodinia-only vs All-Suite)
**What goes wrong:** Citing numbers from old Rodinia-only analysis (paper_data.json, statistical_analysis.json) when CONTEXT.md calls for all-suite numbers from quantitative_findings.json.
**Why it happens:** The paper currently uses Rodinia-only scope in the Results section. The methodology defense uses all-suite Campaign 1 scope (700 tasks). These are different scopes with different values.
**How to avoid:** Use quantitative_findings.json as primary provenance (D-03 says "all 5 suites"). Cross-check against CONTEXT.md for which figure is primary vs parenthetical.
**Warning signs:** Numbers don't match between provenance comment and text.

### Pitfall 3: Confusing 64.2% vs 66.7% vs 68.8%
**What goes wrong:** Three CUDA-to-OMP pass rates exist at different scopes and levels.
**Why it happens:** Different analysis scopes produce different numbers.
**How to avoid:** Use these precisely:
- **64.2%** = 77/120 = all-suite, all-levels (L0-L4), Campaign 1 cuda-to-omp (PRIMARY for methodology)
- **66.7%** = 16/24 = all-suite, L0 only, Campaign 1 cuda-to-omp
- **68.8%** = 11/16 = balanced Rodinia subset, L0 only (parenthetical reference)

### Pitfall 4: Fisher's Exact Test Remnants
**What goes wrong:** Leaving "Fisher's exact test" in line 644 or any other location.
**Why it happens:** Line 644 currently says Fisher's. This is factually incorrect.
**How to avoid:** The rewrite at line 644 must replace Fisher's with McNemar's. Grep the entire paper for "Fisher" after the edit to ensure no remnants.
**Warning signs:** Reviewer finds contradiction between Metrics section (Fisher's) and Statistical Summary section (McNemar).

### Pitfall 5: Breaking the Verify Section Flow
**What goes wrong:** Conjunction verification defense paragraph disrupts the existing technical flow of Section 3.2.
**Why it happens:** Section 3.2 currently ends with the failure classification paragraph (line 310). Adding a defense paragraph after it needs a smooth transition.
**How to avoid:** Place the defense paragraph AFTER the failure classification paragraph (line 310), BEFORE Section 3.3 (line 312). Use a transitional sentence that connects "why we verify this way" to the existing "how we verify."

### Pitfall 6: Updating Bonferroni Without Consistency
**What goes wrong:** Updating alpha from 0.0167 to 0.0125 in one place but not others.
**Why it happens:** The alpha value appears in the source comment (line 992), the table cells (lines 1005-1007), and potentially in methodological notes.
**How to avoid:** Grep for "0.0167" across the entire paper and update ALL occurrences.

## Code Examples

### Kernel Isolation Defense Paragraph (METHOD-01)
```latex
% Template for the new paragraph at TOP of Section 3.4
% src: quantitative_findings.json > campaign_1.augmentation_trends.per_direction.cuda-to-omp
% src: sloc_analysis.json > summary.kernels_above_pareval_threshold = 31/35
% src: quantitative_findings.json > campaign_1.failure_taxonomy.status_counts.BUILD_FAIL = 237/700
\textbf{Rationale for kernel-centric isolation.} We isolate translation skill
from build-system generation because they are orthogonal competencies.
Conflating them produces artificially low pass rates that obscure the model's
actual parallel programming competence. Three observations support this design
choice. First, [XSBench comparison: ParEval-Repo 0% vs ParBench 64.2%].
Second, [31 of 35 kernels exceed 133 SLoC threshold].
Third, [237/700 = 33.9% BUILD_FAIL even with build infrastructure provided].
```

### Statistical Test Rewrite (METHOD-02)
```latex
% Template for line 644 full rewrite
% src: quantitative_findings.json > campaign_1.direction_asymmetry (McNemar)
% src: quantitative_findings.json > campaign_1.augmentation_trends.aggregate.cochran_armitage
Statistical analysis uses Wilson score 95\% confidence intervals for proportions
(preferred over Wald intervals for better coverage near boundary proportions),
McNemar's exact test for direction asymmetry (exploiting the paired design---each
kernel is evaluated in both directions), and the Cochran-Armitage trend test for
augmentation-level effects (exploiting the ordinal structure of L0--L4 levels,
preferred over chi-squared which ignores level ordering).
```

### Conjunction Verification Defense (METHOD-04)
```latex
% Template for defense paragraph at end of Section 3.2
% src: quantitative_findings.json > campaign_1.failure_taxonomy.status_counts.VERIFY_FAIL = 51/700
\textbf{Verification methodology.} The conjunction of exit-code and stdout-pattern
verification is essential: [X]~tasks ([Y]\%) across [N] translation tasks compile
and run successfully (exit\_code~$=~0$) but produce incorrect output.
For example, [gaussian example]. Compilation-only verification
\cite{CodeRosetta2024} would misclassify all such tasks as successful translations.
```

### Reproducibility Pins (METHOD-03)
```latex
% Template for 2-3 sentences after line 681
% src: git rev-parse HEAD, git submodule status
To support exact reproduction, ParBench is pinned at commit \texttt{[hash]};
Rodinia at submodule commit \texttt{9c10d3ea}. Qwen~3.5 397B-A17B was accessed
via the Together AI API during [date range]. All result JSONs and analysis
scripts are available in the ParBench repository.
```

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Manual LaTeX compilation + grep verification |
| Config file | None (paper.tex is the target) |
| Quick run command | `grep -n "Fisher" docs/paper/latex/paper.tex` (should return 0 after edit) |
| Full suite command | See per-requirement checks below |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| METHOD-01 | Kernel isolation paragraph exists in Section 3.4 | grep | `grep -c "orthogonal competencies\|kernel-centric isolation" docs/paper/latex/paper.tex` | N/A (paper edit) |
| METHOD-02 | Statistical sentence rewritten, no Fisher's | grep | `grep -c "Fisher" docs/paper/latex/paper.tex` (expect 0) + `grep -c "McNemar" docs/paper/latex/paper.tex` (expect 5+) | N/A |
| METHOD-03 | Reproducibility pins present after hardware table | grep | `grep -c "9c10d3ea\|commit.*hash" docs/paper/latex/paper.tex` | N/A |
| METHOD-04 | Conjunction verification defense in Section 3.2 | grep | `grep -c "compilation-only\|misclassif" docs/paper/latex/paper.tex` | N/A |
| D-07b | Bonferroni alpha updated | grep | `grep -c "0.0125" docs/paper/latex/paper.tex` (expect 3+) + `grep -c "0.0167" docs/paper/latex/paper.tex` (expect 0) | N/A |

### Sampling Rate
- **Per task commit:** Grep verification of each METHOD edit
- **Per wave merge:** Full grep sweep for Fisher remnants, Bonferroni consistency, provenance comments
- **Phase gate:** All 5 requirement greps pass + no regression in existing paper text

### Wave 0 Gaps
None -- Phase 4 edits existing paper.tex. No test infrastructure needed.

## Security Domain

Not applicable. Phase 4 is purely a paper-writing phase with no code execution, no API calls, no user input handling, and no data processing. Security enforcement is not relevant.

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The 68.8% balanced Rodinia L0 rate is 11/16 (from old paper_data.json scope) | METHOD-01 | LOW -- parenthetical figure only; primary is 64.2% all-suite |
| A2 | Qwen 3.5 API access dates should be stated as a range in reproducibility pins | METHOD-03 | LOW -- exact dates can be pulled from result JSON timestamps |
| A3 | The gaussian VERIFY_FAIL example is the most compelling for the conjunction defense | METHOD-04 | LOW -- 3 backup examples identified; any L0 VERIFY_FAIL with all-3-attempts build+run pass works |

**If this table is empty:** All other claims in this research were verified against on-disk files or cited from CONTEXT.md decisions.

## Open Questions

1. **Cochran-Armitage and McNemar TABLE values: update now or in Phase 11?**
   - What we know: The methodology TEXT justification (line 644 and line 1012) is Phase 4's job. The TABLE values at lines 1003-1007 are currently Rodinia-only scope. quantitative_findings.json has all-suite values.
   - What's unclear: Should Phase 4 update the TABLE numbers to all-suite scope, or leave that for Phase 11 (Paper TeX Integration)?
   - Recommendation: Phase 4 updates the Bonferroni alpha (D-07b) in the table and source comment. Leave McNemar n/p/h and Cochran-Armitage z/p table values for Phase 11, which does a full numbers sweep. The methodology justification text does not need specific numeric values -- it explains WHY these tests are appropriate, not the results.

2. **Qwen API access dates for METHOD-03**
   - What we know: D-13 says to include "model API version dates (Qwen 3.5 accessed via Together AI)."
   - What's unclear: The exact date range. Result JSON timestamps span multiple days.
   - Recommendation: At execution time, extract min/max timestamps from `results/evaluation/together-qwen-3.5-397b-a17b/*.json` to determine the evaluation period. Or use a general statement like "March--April 2026."

## Sources

### Primary (HIGH confidence)
- `results/analysis/quantitative_findings.json` -- Campaign 1 failure taxonomy, direction rates, augmentation trends [VERIFIED: read during research]
- `results/analysis/statistical_analysis.json` -- McNemar p-values, Bonferroni alpha, Wilson CIs [VERIFIED: read during research]
- `results/analysis/sloc_analysis.json` -- 31/35 kernels above 133 SLoC threshold [VERIFIED: read during research]
- `docs/paper/latex/paper.tex` -- Current section boundaries, line numbers, existing text [VERIFIED: read during research]
- `results/evaluation/together-qwen-3.5-397b-a17b/rodinia-gaussian-opencl-to-rodinia-gaussian-cuda.json` -- VERIFY_FAIL example [VERIFIED: read during research]
- `config/compiler_inventory.txt` -- Compiler version pins [VERIFIED: read during research]
- `git rev-parse HEAD` = `befe2ac`, `git submodule status` = `9c10d3ea` [VERIFIED: executed during research]

### Secondary (MEDIUM confidence)
- CONTEXT.md decisions (D-01 through D-14) -- user-locked methodology choices [VERIFIED: read from phase directory]

### Tertiary (LOW confidence)
- None -- all claims verified against on-disk files.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all data sources identified and verified on disk
- Architecture: HIGH -- paper.tex line numbers verified; edit locations confirmed via grep
- Pitfalls: HIGH -- scope confusion and line number staleness are documented hazards from prior phases

**Research date:** 2026-04-05
**Valid until:** 2026-04-08 (paper submission deadline; after that, scope changes)
