# HANDOFF: NeurIPS 2026 Paper — Section-by-Section Quality Review Pipeline

**Date:** 2026-04-25
**Author:** Claude Code session (structural rewrite complete, quality pipeline designed)
**Status:** STRUCTURAL REWRITE COMPLETE. Ready to execute quality review pipeline on 7 sections.
**Audience:** Written for undergraduate software engineering clarity. Every path is absolute. Every number is verified. Every command is copy-paste ready.

---

## What Is This Document?

The ParBench NeurIPS 2026 paper just went through a major structural rewrite:
- Modularized from one big LaTeX file into 9 section files using `\input{}`
- All numbers corrected from a purged dataset to canonical evaluation data
- Model swap from GPT-4.1 mini to GPT-5.4 (with `\tbd{}` placeholders for incomplete data)
- Self-repair narrative removed (no data exists)
- KNOWN_FAIL counts corrected (9 not 8, 87 PASS not 88)

**This document defines the NEXT phase:** a systematic 3-tool quality pipeline applied section-by-section to ensure every claim is data-grounded, the prose meets NeurIPS standards, and cross-model review catches blind spots.

---

## What Was Already Done (DO NOT REPEAT)

### Structural Changes (Complete)
1. Created `sections/macros.tex` — centralized model names, failure taxonomy, `\tbd{}` command
2. Restructured `main_neurips.tex` — 9 `\input{sections/}` calls, no inline content
3. Extracted 5 inline sections to separate files (abstract, experimental-setup, results, related-work, discussion)
4. Deleted conflicting standalone `results.tex` from NeurIPS_ready_version/ root
5. Regenerated all figures (5 Qwen + 4 GPT-5.4) via `scripts/generate_paper_figures.py`
6. Removed broken `\graphicspath` entry for `../../analysis/visualizations/`

### Data Corrections (Complete)
1. All GPT-4.1 mini → GPT-5.4 in active .tex files (0 remaining in main + appendices_neurips + sections/)
2. All Qwen numbers updated to canonical data from `quantitative_findings.json`
3. Self-repair tables and narrative blocks removed from `appendices_neurips.tex`
4. Model config table: temperature 0 → 0.7
5. Per-kernel table caption: 710 → 626

### Section Rewrites (Complete but NOT yet quality-reviewed)
- **Abstract:** Full rewrite (canonical numbers, stochastic framing, \tbd{} for GPT-5.4)
- **Introduction:** Moderate edit (removed deterministic decoding, removed specific file-coordination numbers, updated contribution #3)
- **Framework:** Moderate edit (removed 6 self-repair references, reframed as optional capability, fixed KNOWN_FAIL to 9/87)
- **Benchmark Curation:** Minor edit (Rodinia 53/7, total 87/9)
- **Experimental Setup:** Full rewrite (temp=0.7, 3 samples, 626 records, no self-repair)
- **Results:** Major rewrite (new tables, new pass@k subsection, dropped self-repair and file coordination subsections, balanced augmentation table)
- **Related Work:** Moderate update (reorganized with \paragraph{} headings, added 3 new citations)
- **Discussion:** Full rewrite (2-model framing, honest limitations, self-repair as future work)

### Backup Location
`/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version.bak` — complete pre-rewrite snapshot.

---

## Skills to Load at Session Start

Load these skills BEFORE doing any work. They control HOW you approach every task.

```
Skill("andrej-karpathy-skills:karpathy-guidelines")  -- Think before coding, surgical changes, simplicity (plugin at ~/.claude/plugins/)
Skill("ml-paper-writing")                              -- NeurIPS paper conventions (global skill)
Skill("deslop")                                        -- Remove AI writing patterns, apply inline (global skill)
Skill("test-driven-development")                       -- ONLY if editing Python scripts (e.g., generate_paper_figures.py). Not needed for LaTeX-only edits.
```

For each section's review pipeline:
```
Skill("paper-claim-audit")     -- Stage 1: Verify every number traces to data files
Skill("paper-review-sim")      -- Stage 2: Simulate NeurIPS 5-reviewer panel
```

For cross-model review:
```
/codex:rescue                  -- Stage 3: GPT-5.4 review of each section
```

At verification points:
```
Skill("cite-check")            -- Verify citations match references.bib
Skill("validate")              -- Run waves 1-3 before any git commit
```

---

## Absolute Path Reference

| Short Name | Absolute Path |
|------------|---------------|
| PROJECT_ROOT | `/home/samyak/Desktop/parbench_sam` |
| PAPER_DIR | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version` |
| SECTIONS | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections` |
| FIGURES | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/figures` |
| MAIN_TEX | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/main_neurips.tex` |
| APPENDIX | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/appendices_neurips.tex` |
| REFS_BIB | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/references.bib` |
| QF_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/quantitative_findings.json` |
| PD_JSON | `/home/samyak/Desktop/parbench_sam/results/analysis/paper_data.json` |
| BACKUP | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version.bak` |
| ORIGINAL | `/home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version.bak/main_neurips.tex` |

---

## Data Ground Truth (Canonical Qwen 3.5 397B-A17B)

**Source:** `QF_JSON` → `canonical` section. ALL numbers below verified 2026-04-25.

### Overall
| Metric | Value | JSON Path |
|--------|-------|-----------|
| Valid records | 626 | metadata.file_counts.valid_after_exclusion |
| Excluded (KNOWN_FAIL) | 82 | metadata.file_counts.excluded_known_fail |
| Total on disk | 708 | metadata.file_counts.total_on_disk |
| KNOWN_FAIL specs | 9 | metadata.excluded_specs_count |
| Overall pass rate | 36.7% [33.1%, 40.6%] | canonical.aggregate_pass_rates.overall |
| Temperature | 0.7 | all result files |
| Max retries | 1 (no self-repair) | all result files |
| L0 records | 426 | canonical.augmentation_trends.aggregate.per_level.L0.n |
| Ablation records (L1-L4) | 200 (50 each) | canonical.augmentation_trends.aggregate.per_level |
| Unique L0 pairs | 142 | canonical.pass_at_k.total_tasks.value |

### pass@k (142 unique L0 pairs, 3 samples each)
| Metric | Value |
|--------|-------|
| pass@1 | 23.9% [17.9%, 30.0%] |
| pass@3 | 35.2% [27.3%, 43.1%] |
| Always pass (3/3) | 19 tasks (13.4%) |
| Hard fail (0/3) | 92 tasks (64.8%) |
| Noisy (1-2/3) | 31 tasks (21.8%) |

### Direction Pass Rates (L0, all 3 samples per task)
| Direction | Rate | n | Type |
|-----------|------|---|------|
| cuda-to-omp | 40.3% [29.7%, 51.8%] | 72 | Standard |
| omp-to-opencl | 33.3% [22.0%, 47.0%] | 51 | Standard |
| omp-to-cuda | 25.0% [16.4%, 36.1%] | 72 | Standard |
| opencl-to-omp | 9.8% [4.3%, 21.0%] | 51 | Standard |
| cuda-to-opencl | 7.0% [2.8%, 16.7%] | 57 | Standard |
| opencl-to-cuda | 0.0% [0.0%, 6.3%] | 57 | Standard |
| omp_target-to-cuda | 66.7% [46.7%, 82.0%] | 24 | Case study |
| cuda-to-omp_target | 0.0% [0.0%, 13.8%] | 24 | Case study |

**Additional directions in JSON (not in current paper tables — ask user before adding):**
| Direction | Rate | n | Type |
|-----------|------|---|------|
| omp-to-omp_target | 44.4% [18.9%, 73.3%] | 9 | Standard in JSON |
| omp_target-to-omp | 100% [70.1%, 100%] | 9 | Standard in JSON |

Note: QF_JSON categorizes these as `standard`, but they are excluded from the main direction table because n=9 is too small for meaningful comparison. Ask user before adding.

### Failure Taxonomy (all 626 records)
| Status | Count | Rate |
|--------|-------|------|
| PASS | 230 | 36.7% |
| BUILD_FAIL | 245 | 39.1% |
| RUN_FAIL | 121 | 19.3% |
| VERIFY_FAIL | 29 | 4.6% |
| EXTRACTION_FAIL | 1 | 0.2% |

### Per-Suite Pass Rates
| Suite | Rate | n |
|-------|------|---|
| hecbench | 65.2% | 184 |
| rodinia | 28.2% | 380 |
| mixbench | 9.1% | 22 |
| xsbench | 4.5% | 22 |
| rsbench | 0.0% | 18 |

### Augmentation (Balanced 12-Kernel CUDA-to-OMP Subset)
| Level | Pass/Total | Rate | Kernels with any pass |
|-------|-----------|------|----------------------|
| L0 | 29/36 | 80.6% | 12/12 (100%) |
| L1 | 9/12 | 75.0% | 9/12 (75%) |
| L2 | 10/12 | 83.3% | 10/12 (83%) |
| L3 | 9/12 | 75.0% | 9/12 (75%) |
| L4 | 10/12 | 83.3% | 10/12 (83%) |

**The 12 balanced kernels are:** bfs, cfd, floydwarshall, heat2d, hotspot3d, iso2dfd, lud, nw, particlefilter, pathfinder, srad, stencil1d.
These are the CUDA-to-OMP pairs with both L0 (s0/s1/s2) and L1-L4 result files. Reproduce with:
```bash
ls /home/samyak/Desktop/parbench_sam/results/evaluation/together-qwen-3.5-397b-a17b/*cuda-to-*-omp-L1.json | sed 's/.*together-qwen-3.5-397b-a17b\///' | sed 's/-cuda-to-.*//' | sort -u
```

**WARNING: The aggregate Cochran-Armitage z=7.65 in QF_JSON is a Simpson's paradox artifact (L1-L4 test an easier subset). Do NOT report this z-statistic. Report only the balanced 12-kernel descriptive rates above.**

### GPT-5.4 Data
81 result files in `/home/samyak/Desktop/parbench_sam/results/evaluation/azure-gpt-5.4/` (incomplete). All GPT-5.4 cells use `\tbd{}` placeholders.

---

## NeurIPS 2026 Formatting Constraints

| Constraint | Value |
|-----------|-------|
| Main body page limit | 9 pages (to end of Conclusion) |
| References | Do NOT count toward page limit |
| Appendix | Unlimited (reviewers not required to read) |
| Text width | 5.5 inches |
| Text height | 9 inches |
| Font size | 10pt (11pt leading) |
| Anonymous | Yes (submission mode) |
| Natbib | Auto-loaded; use `\citep{}` and `\citet{}` |
| Checklist | Required — `\answerYes`, `\answerNo`, `\answerNA` |
| Style file | `neurips_2026.sty` (already in PAPER_DIR) |

---

## Section-by-Section Quality Pipeline

### Pipeline per Section (3 Stages + Manual Gate)

For EACH of the 7 sections below, execute these stages IN ORDER:

#### Stage 1: paper-claim-audit
**Skill:** `Skill("paper-claim-audit")`

What it does: Traces every numeric claim in the section back to a raw data file. Flags claims that don't match.

**Before running:** Read the section file AND the Data Ground Truth table above. Know what the correct numbers are.

**After running:** Fix any flagged mismatches. Apply `deslop` principles to any rewritten prose (no AI-isms, active voice, specific claims). Do NOT introduce new claims not supported by data.

**Verification after Stage 1:**
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
grep -n "38\.3\|710\b\|64\.2\|GPT-4.1\|self-repair" sections/{current_section}.tex | grep -v '%'
# Should return 0 non-comment hits
# EXPECTED exceptions: framework.tex (~line 94: optional self-repair), experimental-setup.tex (line 4: no self-repair), discussion.tex (lines 6,8: limitation/future-work)
```

#### Stage 2: paper-review-sim
**Skill:** `Skill("paper-review-sim")`

What it does: Simulates 5 NeurIPS reviewers (EIC + 3 peers + Devil's Advocate) reading the section. Scores on quality, clarity, significance, originality.

**Before running:** Provide the section text AND the paper context (what the paper is about, which section this is, what comes before and after).

**After running:** Address CRITICAL and MAJOR issues. Document MINOR issues. If a reviewer suggests a narrative change (e.g., "this section should emphasize X instead of Y"), STOP and ask the user with options.

**Narrative Guardrail:** Compare any proposed narrative changes against the original paper at `ORIGINAL` (the backup). If the proposed change diverges from the original paper's narrative intent, flag it to the user:
> "Reviewer suggests [X]. The original paper says [Y]. Options: (A) keep original framing, (B) adopt reviewer suggestion, (C) compromise with [Z]."

#### Stage 3: codex:rescue
**Command:** `/codex:rescue review sections/{current_section}.tex for NeurIPS quality, data consistency, and prose clarity`

What it does: Sends the section to GPT-5.4 for a cross-model review. Catches things that same-model self-review misses.

**After running:** Implement fixes for legitimate issues. Ignore style-only preferences that conflict with the paper's established voice.

**Fallback:** If `/codex:rescue` fails (sandbox/network error), substitute `Skill("session-critique")` or `Skill("review")` for a local Claude self-review instead. Proceed to the manual gate either way.

#### Manual Gate
After all 3 stages complete for a section, tell the user:
> "Section [name] has passed all 3 review stages. Changes made: [list]. Please review sections/{file}.tex and approve before I proceed to the next section."

**WAIT for user approval before proceeding to the next section.**

---

### Section Processing Order

Process front-to-back. Each section builds on the reader's understanding from previous sections, so narrative consistency is best checked in reading order.

---

### Section 1: Introduction
**File:** `SECTIONS/1-introduction.tex` (33 lines)
**Rewrite level:** Moderate edit
**Key claims to audit:**
- 25% of specs require multi-file translation → verify against corpus data
- 472 CUDA-OpenMP kernel pairs across 6 repositories → verify against survey data
- 0% pass@k on 133+ SLoC from ParEval-Repo → citation claim, verify reference
- "626 valid translation records" in contribution #3 → must match QF_JSON
- Contribution #3 uses `\qwenshort{}` and `\gptnew{}` macros — verify they expand correctly

**Narrative check:** Compare against ORIGINAL lines 90-107. The rewrite removed specific file-coordination numbers (51.3% vs 22.2%) because those were from the old purged dataset. Confirm the qualitative claim ("single-file translations pass at substantially higher rates") still holds for canonical data.

**Potential issue:** The `\ref{sec:contamination}` was removed in the prior session because no such label exists. Verify with:
```bash
grep -n "ref{sec:contamination}" /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version/sections/1-introduction.tex
# Should return 0 hits (confirmed clean as of 2026-04-25)
```

**File-coordination claim:** "single-file translations pass at substantially higher rates" is a qualitative claim. Canonical L0 data supports it (single-file ~39.4% vs multi-file ~11.1% from L0 results, verified 2026-04-25), but the specific percentages are not stated in the text since they weren't precomputed into QF_JSON.

---

### Section 2: Framework
**File:** `SECTIONS/framework.tex` (146 lines)
**Rewrite level:** Moderate edit (self-repair removal)
**Key claims to audit:**
- 206 JSON specs (60+4+4+3+25=96 curated, 206 total including HeCBench bulk) → verify
- 68 of 87 non-KNOWN_FAIL specs pass at all augmented levels → this number is from the augmentation baseline (harness verify on original source, NOT LLM evaluation). It is NOT in QF_JSON. Verify with: `python3 -m harness verify --all-suites` or check sweep log at `.planning/phases/03-oracle-framework/03-S6-SWEEP.log`
- 9 KNOWN_FAIL specs → must be 9, not 8
- 53 Rodinia PASS → must be 53, not 54
- Figure caption says "optional self-repair path not exercised" → verify this framing is consistent with experimental-setup and results

**Narrative check:** The framework section describes infrastructure, not results. It should NOT contain specific pass rates from the evaluation. If any slipped in, remove them.

---

### Section 3: Benchmark Curation
**File:** `SECTIONS/benchmark-curation.tex` (207 lines)
**Rewrite level:** Minor edit
**Key claims to audit:**
- Suite summary table: 35 kernels, 96 specs, 87 PASS, 9 KNOWN_FAIL
- Rodinia: 22 kernels, 60 specs, 53 PASS, 7 KF
- HeCBench: 10 kernels, 25 specs, 23 PASS, 2 KF
- XSBench: 1 kernel, 4 specs, 4 PASS
- RSBench: 1 kernel, 4 specs, 4 PASS
- mixbench: 1 kernel, 3 specs, 3 PASS
- SLoC range 80-3304, median 271
- 24/96 (25%) multi-file
- 31/35 kernels exceed 133 SLoC
- Characterization table (Table benchmark-characterization): SLoC ranges, medians, multi-file percentages, language standards

**Narrative check:** This section is largely stable — it describes the corpus, not evaluation results. Verify no evaluation numbers leaked in.

---

### Section 4: Experimental Setup
**File:** `SECTIONS/experimental-setup.tex` (8 lines)
**Rewrite level:** Full rewrite
**Key claims to audit:**
- Temperature 0.7 → correct (verified against result files)
- 3 independent samples per task → correct
- 142 unique L0 pairs → must match QF_JSON canonical.pass_at_k.total_tasks.value = 142
- 426 L0 records → must match QF_JSON per_level.L0.n = 426
- 50 records per level L1-L4 → must match QF_JSON
- 626 valid records = 426 + 200 → arithmetic check
- 82 excluded records → must match QF_JSON metadata
- 9 KNOWN_FAIL specs → must match
- 12-kernel balanced CUDA-to-OMP subset → verify this is the correct balanced set
- Wilson 95% CIs → methodology claim, verify usage in QF_JSON

**Narrative check:** Compare against ORIGINAL lines 175-182. The original said "temperature 0, up to three self-repair attempts." The rewrite says "temperature 0.7, three independent samples, no self-repair." This is correct — it reflects the actual canonical evaluation protocol. Verify no traces of the old protocol remain.

---

### Section 5: Results (HIGHEST RISK)
**File:** `SECTIONS/results.tex` (146 lines)
**Rewrite level:** Major rewrite
**Key claims to audit — EVERY NUMBER MUST MATCH QF_JSON:**

**Table: Overall pass rates (tab:overall-pass)**
- PASS=230, BUILD_FAIL=245, RUN_FAIL=121, VERIFY_FAIL=29, EXTR_FAIL=1, Total=626
- Rate=36.7% [33.1%, 40.6%]
- Arithmetic: 230+245+121+29+1 = 626 ✓

**Table: pass@k (tab:pass-at-k-main)**
- pass@1=23.9% [17.9%, 30.0%]
- pass@3=35.2% [27.3%, 43.1%]
- Always pass=19 (13.4%), Noisy=31 (21.8%), Hard fail=92 (64.8%)
- Arithmetic: 19+31+92 = 142 ✓

**Table: Direction rates (tab:direction-rates)**
- All 8 directions with rates, CIs, n values — cross-check every cell against Data Ground Truth above

**Table: Per-kernel (tab:per-kernel-main)**
- stencil1d 15/15=100%, floydwarshall 16/20=80%, heat2d 15/20=75%, iso2dfd 15/20=75%, hotspot 21/30=70%
- gaussian 0/10=0%, heartwall 0/30=0%, myocyte 0/30=0%, rsbench 0/30=0%, xsbench 0/30=0%

**Table: Augmentation balanced (tab:aug-balanced)**
- L0=29/36=80.6%, L1=9/12=75%, L2=10/12=83.3%, L3=9/12=75%, L4=10/12=83.3%

**Prose claims:**
- "39.1\% of all outcomes" for BUILD_FAIL → 245/626 = 0.3914... rounds to 39.1% ✓
- "61.9\% of all failures" for BUILD_FAIL → 245/(245+121+29+1) = 245/396 = 0.6187... rounds to 61.9% ✓
- "4.6\%" for VERIFY_FAIL → 29/626 = 0.0463... rounds to 4.6% ✓
- "19.3\%" for RUN_FAIL → 121/626 = 0.1933... rounds to 19.3% ✓

**Narrative check:** The old results section (ORIGINAL lines 184-313) had:
- File coordination subsection → DROPPED (data not precomputed for canonical eval)
- Self-repair subsection → DROPPED (no data)
- Augmentation used z=0.0, p=1.0 → REPLACED with balanced 12-kernel descriptive rates

Verify the new results section does NOT contain:
```bash
grep -n "file.coordination\|self.repair\|z=0.0\|p=1.0\|Cochran" SECTIONS/results.tex | grep -v '%'
# Should return 0 hits
```

**Decision needed from user:** The JSON has 2 additional directions (omp→omp_target at 44.4%, omp_target→omp at 100%) that are NOT in the current direction table. Flag these for the user's decision — should they be added?

---

### Section 6: Related Work
**File:** `SECTIONS/related-work.tex` (16 lines)
**Rewrite level:** Moderate update
**Key claims to audit:**
- All 12 `\cite{}` keys exist in references.bib: HumanEval2021, TransCoder2020, SWEbench2024, SWEbenchIllusion2025, ParEval2024, ParEvalRepo2025, VibeCodeHPC2025, QiMengMuPa2025, LASSI2024, CodeRosetta2024, HPCCoderV2, TRACY2025
- No numeric data claims (this section is citation-focused)
- Newly added citations (VibeCodeHPC2025, QiMengMuPa2025, SWEbenchIllusion2025) have correct BibTeX entries

**Run cite-check:**
```bash
# Verify all cite keys resolve
grep -oP '\\cite[tp]?\{([^}]+)\}' SECTIONS/related-work.tex | tr ',' '\n' | sort -u
# Cross-check each key against references.bib
```

**Narrative check:** Compare against ORIGINAL lines 315-324. The rewrite reorganized from flat paragraphs to `\paragraph{}` headings and added 3 new citations. Verify the positioning claims are accurate (e.g., "LASSI is the nearest prior work in granularity" — still true with new citations?).

---

### Section 7: Discussion
**File:** `SECTIONS/discussion.tex` (10 lines)
**Rewrite level:** Full rewrite
**Key claims to audit:**
- 36.7% overall → matches QF_JSON ✓
- 40.3% CUDA-to-OMP → matches direction rates ✓
- pass@1=23.9%, pass@3=35.2% → matches pass@k ✓
- 142 unique L0 tasks → matches ✓
- 39.1% build-stage → matches ✓
- 0% OpenCL-to-CUDA → matches ✓
- 75-83% augmentation stability → matches balanced subset ✓
- 12 kernels at L1-L4 → matches ✓

**Narrative check:** The discussion must NOT overclaim. Verify:
- Does not say "we show models can translate parallel code" (they fail 63.3% of the time)
- Does not say augmentation proves no memorization (small sample, can only say "no evidence of degradation")
- Correctly frames GPT-5.4 as "in progress" not "planned"
- Self-repair mentioned ONLY as "framework capability deferred to future work"
- Limitations are honest (small augmented subset, single model complete, no efficiency measurement)

---

### Final Whole-Paper Pass (After All 7 Sections)

After completing all 7 section pipelines:

1. **Run `paper-review-sim` on the ENTIRE paper** (all sections concatenated). This catches cross-section inconsistencies that per-section review misses:
   - Intro promises something that Results doesn't deliver
   - Terminology inconsistency (e.g., "pass rate" vs "success rate")
   - Redundant explanations across sections

2. **Run `cite-check`** on the whole paper to verify all citations resolve.

3. **Run global verification:**
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version

# Zero stale data
grep -r "GPT-4.1\|38\.3\%\|\b710\b\|64\.2" sections/ --include="*.tex" | grep -v '%'

# TBD markers present (GPT-5.4 placeholders)
grep -rc "\\\\tbd" sections/ --include="*.tex" | grep -v ':0$'

# No dangling references — collect all \ref keys and all \label keys, diff them
grep -rn '\\ref{' sections/ appendices_neurips.tex --include="*.tex" | grep -oP 'ref\{[^}]+\}' | sort -u > /tmp/refs.txt
grep -rn '\\label{' sections/ appendices_neurips.tex --include="*.tex" | grep -oP 'label\{[^}]+\}' | sed 's/label/ref/' | sort -u > /tmp/labels.txt
comm -23 /tmp/refs.txt /tmp/labels.txt
# Any output = dangling reference. Note: appendix labels are in appendices_neurips.tex, not sections/.

# Self-repair only in permitted locations
grep -rn "self.repair" sections/ --include="*.tex" | grep -v '%'
# Allowed in: framework.tex (optional capability), discussion.tex (future work), experimental-setup.tex (protocol description)
```

4. **Compile and check** (if LaTeX available):
```bash
cd /home/samyak/Desktop/parbench_sam/docs/paper/NeurIPS_ready_version
# Check compiler availability first
which tectonic || which pdflatex || find /opt /usr -name pdflatex 2>/dev/null | head -1
# Then compile:
tectonic main_neurips.tex   # or pdflatex + bibtex + pdflatex x2
# If no compiler found, skip — compilation is a nice-to-have, not a blocker for the review pipeline.
```

5. **Run `/validate`** before any commit (required by pre-commit hook).

6. **Run `/codex:rescue review the uncommitted changes`** for end-of-session cross-model review, then `touch .codex_review_done`.

---

## What Worked in the Prior Session

- **Data-first approach:** Reading `quantitative_findings.json` before touching any .tex file prevented propagating wrong numbers.
- **Modular extraction:** Converting inline sections to `\input{}` files made surgical editing possible.
- **Backup before changes:** `NeurIPS_ready_version.bak` provides a rollback and narrative reference.
- **Global grep verification:** Running `grep -r "GPT-4.1"` after each phase caught remaining references immediately.

## What Didn't Work / Traps to Avoid

- **Don't trust numbers in the existing .tex files** without verifying against QF_JSON.
- **Don't use the Cochran-Armitage z=7.65 from QF_JSON** — it's a Simpson's paradox artifact.
- **Don't add file-coordination analysis** — the data isn't precomputed for the canonical evaluation.
- **Don't add self-repair results** — no data exists.
- **Don't compile from project root** — compile from inside `NeurIPS_ready_version/` so `\graphicspath` resolves.
- **Don't confuse `appendices.tex` with `appendices_neurips.tex`** — only the latter is active. The former is a dead older version with 16 GPT-4.1 references (irrelevant).
- **Don't run `humanizer_academic`** — user found it ineffective. Use `deslop` principles inline instead.

---

## Figure Files (All Verified Present)

### Main Body Figures
| Figure | File | Referenced In |
|--------|------|---------------|
| Architecture diagram | `parbench_architecture.png` | framework.tex |
| Failure taxonomy (Qwen) | `f4_failure_taxonomy_qwen.pdf` | results.tex |

### Appendix Figures (20 total, all verified present in `FIGURES/`)
All `\includegraphics` paths in `appendices_neurips.tex` resolve correctly via `\graphicspath{{figures/}}`.

### Generated Figures (Qwen + GPT-5.4)
| File | Content |
|------|---------|
| `f3_kernel_model_heatmap_qwen.pdf` | Per-kernel heatmap (Qwen) |
| `f4_failure_taxonomy_qwen.pdf` | Failure distribution (Qwen) |
| `f5_pass_at_k_by_direction_qwen.pdf` | pass@k by direction (Qwen) |
| `f6_cross_suite_comparison_qwen.pdf` | Cross-suite comparison (Qwen) |
| `f7_augmentation_robustness.pdf` | Augmentation L0-L4 |
| `f3_kernel_model_heatmap_gpt.pdf` | Per-kernel heatmap (GPT-5.4, partial) |
| `f4_failure_taxonomy_gpt.pdf` | Failure distribution (GPT-5.4, partial) |
| `f5_pass_at_k_by_direction_gpt.pdf` | pass@k by direction (GPT-5.4, partial) |
| `f6_cross_suite_comparison_gpt.pdf` | Cross-suite comparison (GPT-5.4, partial) |

---

## Files to Work On (Complete List)

| File | Action in This Phase |
|------|---------------------|
| `SECTIONS/1-introduction.tex` | Quality review pipeline (3 stages) |
| `SECTIONS/framework.tex` | Quality review pipeline (3 stages) |
| `SECTIONS/benchmark-curation.tex` | Quality review pipeline (3 stages) |
| `SECTIONS/experimental-setup.tex` | Quality review pipeline (3 stages) |
| `SECTIONS/results.tex` | Quality review pipeline (3 stages) — HIGHEST PRIORITY |
| `SECTIONS/related-work.tex` | Quality review pipeline (3 stages) + cite-check |
| `SECTIONS/discussion.tex` | Quality review pipeline (3 stages) |
| `REFS_BIB` | Verify all cited keys exist (via cite-check) |
| `MAIN_TEX` | No changes expected — verify structure only |
| `APPENDIX` | Not in scope for this phase (already cleaned in prior session) |

## Read-Only Reference Files

| File | What It Provides |
|------|-----------------|
| `QF_JSON` | ALL canonical Qwen numbers (single source of truth) |
| `PD_JSON` | pass@k details (use `passk_campaign` section only) |
| `ORIGINAL` | Pre-rewrite paper for narrative comparison |
| `BACKUP` | Complete pre-rewrite directory snapshot |
