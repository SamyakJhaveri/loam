# SC26 Paper — Adversarial Critic Report

**Generated:** 2026-03-29
**Reviewer:** T7 (Adversarial Critic, Claude Opus with ultrathink)
**Draft reviewed:** `docs/paper/paper_draft.md` (710 lines, all sections S1--S8 + Abstract)
**Audit baseline:** `docs/sc26_paper_audit_report.md` (W1--W17)
**Severity scale:** BLOCKER (must fix before submission) / MAJOR (weakens paper significantly) / MINOR (polish)

---

## 1. Audit Weakness Checklist (W1--W17)

| ID | Weakness | Status | Evidence / What Remains |
|----|----------|--------|------------------------|
| **W1** | Small-N evaluation corpus | **ADDRESSED** | 5-suite expansion to 96 specs / 88 PASS. Primary direction cuda-to-omp now has ~24 kernels across 5 suites. S6.6 explicitly caveats non-primary directions as "exploratory" with a `[PLACEHOLDER: min_n_threshold]` marker. S7.6 acknowledges sample size limitation. |
| **W2** | Missing LASSI comparison | **ADDRESSED** | S2.3 has a full dedicated paragraph on LASSI (lines 104--106) comparing methodology, 80--85% pass rates, and positioning ParBench as complementary. S6.4 references the three-tier agentic gap. S7.3 frames the LASSI comparison quantitatively. |
| **W3** | Missing CodeRosetta comparison | **ADDRESSED** | S2.2 has a dedicated paragraph (line 100) covering encoder-decoder vs. general-purpose LLM, BLEU vs. build+run+verify, and single-direction limitation. Table 1 includes CodeRosetta row. |
| **W4** | No statistical rigor | **ADDRESSED (structurally)** | S5.D defines Wilson CIs, chi-squared, Cochran-Armitage, McNemar tests. S6.8 has a full Statistical Summary table (Table 13). All numbers are [PLACEHOLDER] pending campaign data. The statistical framework is correct and comprehensive. |
| **W5** | Temperature=0 methodology | **ADDRESSED** | S5.D redefines metric as "greedy-decode pass@1". S6.7 adds a full pass@k section (Table 12) with T=0.7, 5 samples. S7.6 acknowledges the limitation. Three orthogonal axes (self-repair, pass@k, augmentation) are cleanly separated. |
| **W6** | Format (ACM vs IEEE) | **ADDRESSED** | Writing roadmap (G.1) and decisions log both say IEEE IEEEtran. However, line 6 of paper_draft.md still says "ACM sigconf" -- see BLOCKER B1 below. |
| **W7** | 4-model vs 3-model inconsistency | **ADDRESSED (superseded)** | Draft is fully rewritten for 2-model (Qwen 3.5 + Gemini 2.5 Flash). No references to "3 models" or "4 models" in the main body (lines 1--670). Pilot models mentioned only in S5.A line 335 as supplementary material and in archived data notes (lines 674--709). |
| **W8** | Augmentation confound (L0 different directions than L1-L4) | **ADDRESSED** | S6.5 Table 10 restricts to "CUDA-to-OpenMP direction only" to eliminate direction-composition confound. S5.C states augmentation is evaluated "across all six directions" in the campaign design (D2). Per-model curves are explicitly required in S6.5 placeholders. |
| **W9** | No performance data | **ADDRESSED (acknowledged)** | S5.D explicitly excludes timing. S7.6 cites TRACY and discusses why correctness-only is insufficient for deployment. S8.2 lists performance analysis as future work. |
| **W10** | 5+ missing papers | **ADDRESSED** | All papers now cited: LASSI (S2.3), CodeRosetta (S2.2), HPC-Coder-V2 (S2.3), TRACY (S2.4), SWE-bench Illusion (S2.2, S2.5), OMPGPT (S2.4), RepoTransBench (S2.4), AlphaTrans (S2.4). Table 1 includes rows for LASSI, CodeRosetta, HPC-Coder-V2, TRACY. |
| **W11** | Rodinia generalizability | **ADDRESSED** | S4.B explicitly discusses training-data familiarity concern and 5-suite mitigation. S7.6 has a dedicated paragraph on "Rodinia training-data familiarity" acknowledging algorithmic memorization as an irreducible threat. RSBench, mixbench, HeCBench provide varying degrees of training-data exposure. |
| **W12** | Self-repair methodology incomplete | **ADDRESSED (structurally)** | S6.2 adds Table 7b (self-repair failure mode transitions). S6.4 Table 9 includes per-model self-repair breakdown with first-attempt, repaired, persistent, regression categories. All numbers are [PLACEHOLDER]. |
| **W13** | XSBench asymmetric reporting | **ADDRESSED** | S6.6 explicitly separates per-suite direction results with a `[PLACEHOLDER: per_suite_direction_prose]`. S6.3 covers all 5 suites in the per-kernel table. With 5 suites, XSBench is no longer the sole non-Rodinia data point. |
| **W14** | Wrong numbers in draft | **ADDRESSED (superseded)** | All pilot numbers replaced with [PLACEHOLDER] markers. Archived pilot data is clearly labeled at lines 674--709. No stale pilot numbers remain in the main body (verified by search -- see Section 4 below). |
| **W15** | No LaTeX draft | **NOT ADDRESSED** | No LaTeX transfer has occurred. The paper remains Markdown-only. This is a parallel workstream per the roadmap, not a writing issue. |
| **W16** | Non-primary directions missing Rodinia data | **ADDRESSED by campaign design** | New campaign (D2) runs all 6 standard directions for all suites. S5.B enumerates per-direction pair counts: cuda-to-omp (24), omp-to-cuda (24), cuda-to-opencl (20), opencl-to-cuda (20), omp-to-opencl (18), opencl-to-omp (18). This eliminates the XSBench-only problem for non-primary directions. |
| **W17** | No anonymous repo | **NOT ADDRESSED** | No anonymous repository exists. This is a submission-mechanics item, not a writing issue. |

**Summary:** 13/17 ADDRESSED, 2/17 NOT ADDRESSED (W15 LaTeX, W17 anon repo -- both are parallel workstreams), 2/17 ADDRESSED but with residual issues flagged below.

---

## 2. Internal Consistency Check

### 2.1 Abstract vs S6 Claims
- **CONSISTENT.** Abstract uses [PLACEHOLDER] markers that directly correspond to S6 tables. Both reference "two LLMs," "six directions," "five augmentation levels," "96 specifications," "five HPC benchmark suites."
- **MINOR ISSUE (M1):** Abstract line 14 says "all non-KNOWN\_FAIL specs across all five suites PASS at every level L1--L4." S5.C line 357 says "68 non-KNOWN\_FAIL specs." S3.C line 229 says "54 of 60 Rodinia specs." The Abstract uses the vague "all" while S5.C gives the specific number 68. These should be reconciled -- the Abstract should either say "68" or "all 68."

### 2.2 S1.3 Contributions vs S6 Actual Content
- **CONSISTENT.** Three contributions listed in S1.3 map to S3 (framework), S3.C (augmentation), and S6 (empirical evaluation). Each contribution bullet corresponds to specific sections.
- **MINOR ISSUE (M2):** Contribution 3 (line 50) mentions "failure taxonomy" but does not mention pass@k, which is a new evaluation dimension added in S6.7. Consider adding pass@k as a fourth contribution bullet or folding it into contribution 3.

### 2.3 Model Names Consistency
- **CONSISTENT across main body (lines 1--670).** "Qwen 3.5 397B-A17B" and "Gemini 2.5 Flash" are used consistently throughout.
- **ACCEPTABLE:** Line 335 mentions pilot models (Claude Sonnet 4.6, Gemini 2.5 Flash-Lite, Llama 3.3 70B) in the context of "supplementary material" -- this is appropriate framing.
- **ACCEPTABLE:** Line 243 mentions "Anthropic, OpenAI, Azure OpenAI, Google, Groq, and Together AI" as supported providers in a framework capability description -- this is about the framework, not the evaluation.
- **ISSUE (M3):** Lines 674--709 contain archived pilot data with pilot model names. These are clearly labeled "Archived pilot data (3-model, 562 tasks, superseded)" and should be REMOVED before submission -- they are working notes, not paper content.

### 2.4 Spec Counts
- **CONSISTENT.** "96 total, 88 PASS, 8 KNOWN\_FAIL" appears in: Abstract (line 14), S1.3 (line 46), S3.A (line 188), S4.B (line 297--298), Table 4 (line 302--309), S6.1 Table 7 header (line 391).
- **CLEAN.** No residual "184 specs" or "64 specs" references in the main body.

### 2.5 Direction Counts
- **CONSISTENT.** "Six translation directions" (standard) + "two additional OpenMP-target directions" (case study) is used in: Abstract (line 14), S1.3 (line 46), S5.B (lines 341--347), S6.6 Table 11 (line 507--516).
- **CLEAN.** No residual "12 directions" references in the main body.

### 2.6 Augmentation Level Descriptions
- **CONSISTENT.** L0--L4 with six transforms described identically in S3.C (Table 2, lines 218--226) and S5.C (line 355).
- **MINOR ISSUE (M4):** S3.C line 229 says "54 of 60 Rodinia specs pass ... at all levels L1--L4." But S5.C line 357 says "68 non-KNOWN\_FAIL specs across all five suites." The S3.C text is Rodinia-only; S5.C is the 5-suite figure. Both are correct but S3.C is stale relative to the 5-suite scope -- it should be updated to mention all 5 suites.

### 2.7 Transform Names vs Code
- Paper lists (S3.C lines 208--213): SwapCondition, ArithmeticTransform, ChangeNames, TypedefExpansion, PointerArithmeticToArrayIndex, ChangeFunctionNames.
- **NEEDS VERIFICATION:** These names should be checked against actual class names in `c_augmentation/augment_dataset.py`. I flag this for source-code verification but did not read the source per my role constraints.

### 2.8 Augmentation Verified Count
- **INCONSISTENCY (MAJOR B2).** Three different numbers appear:
  - S3.C line 229: "54 of 60 Rodinia specs" (Rodinia only, correct for Rodinia)
  - S5.C line 357: "68 non-KNOWN\_FAIL specs across all five suites (54 Rodinia, 4 XSBench, 3 RSBench, 3 mixbench, and 4 spot-checked HeCBench)"
  - Abstract line 14: "all non-KNOWN\_FAIL specs across all five suites"
  - S8.1 line 652: "all non-KNOWN\_FAIL specs across all five suites"
  - The decisions log D6 says "64+ non-KNOWN\_FAIL specs verified level-invariant"
  - known-issues.md says augmentation verified for 54/60 Rodinia + 4/4 XSBench = 58 fully verified, with RSBench/mixbench/HeCBench as "smoke test" not full verification
  - **The 68 count (S5.C) includes 4 "spot-checked" HeCBench specs, not the full 21 non-KNOWN\_FAIL HeCBench.** The claim "all non-KNOWN\_FAIL specs" is technically incorrect -- 13 HeCBench specs were NOT verified for augmentation invariance.
  - **Fix:** Either verify the remaining 13 HeCBench specs, or change "all" to "68 of 88" everywhere.

### 2.9 Task Counts
- **INCONSISTENCY (MAJOR B3).** Multiple task-count formulations appear:
  - S5.C line 355: "710 translation tasks per model" (142 L0 pairs x 5 levels)
  - Writing roadmap D2: "790 tasks per model" (including KNOWN\_FAIL specs handled gracefully)
  - Decisions log D4: "790" for pass@k sweep
  - Abstract line 14: "[PLACEHOLDER: total_tasks]"
  - Data verification table line 682: "710 (142 x 5 levels)" and line 683: "~1,420 (710 x 2 models)"
  - **The discrepancy is 710 vs 790.** The difference is whether KNOWN\_FAIL specs are included in the count. The campaign script handles them "gracefully" (they produce expected failures), so they ARE run but excluded from analysis. The paper should use 710 (non-KNOWN\_FAIL tasks per model) for the headline task count, and note that 8 KNOWN\_FAIL specs produce expected failures.
  - **Fix:** Standardize on 710 per model / ~1,420 total in all sections. Explain the 790 vs 710 distinction in S5.

---

## 3. Grounding Check

### 3.1 Well-Grounded Sections (no issues)

- **S3.A Spec Schema** (lines 142--188): Grounded in actual JSON schema fields (`identity`, `provenance`, `files`, `build`, `run`, `verification`). BFS example is concrete. References actual field names and conventions.
- **S3.B Harness Pipeline** (lines 191--200): Grounded in actual pipeline stages (builder, runner, verifier). References actual CLI behavior (`--resume` flag), failure classifications, timeout defaults.
- **S3.C Augmentation Engine** (lines 202--229): Grounded in actual transform names, libclang API, level definitions with concrete fractions. Transform application frequency data (SwapCondition: 162, etc.) from actual augmentation runs.
- **S3.D Evaluation Pipeline** (lines 231--244): Grounded in actual pipeline behavior -- prompt structure, self-repair loop, complexity taxonomy, model registry.
- **S4 Benchmark Curation** (lines 247--317): Grounded in actual survey data, specific kernel counts, API pair analysis, per-suite details with KNOWN\_FAIL explanations.
- **S2 Related Work** (lines 68--131): Grounded in specific claims from cited papers (LASSI 80--85%, TransCoder 3.1% exact match / 60.9% unit test pass, CodeRosetta +2.9 BLEU, HPC-Coder-V2 pass@1 31.17, HPCorpus 45% OpenMP / 27% MPI / 21% CUDA).

### 3.2 Sections Needing Grounding Improvement

**G1. S1.2 "Training data contamination" paragraph (line 36) -- MINOR**
The claim "at least one evaluated model exhibits sharp pass-rate degradation under augmentation" is forward-referencing S6.5, which is entirely [PLACEHOLDER]. This claim cannot be verified until campaign data arrives. It may or may not be true for the new 2-model lineup. **Flag:** This sentence should be guarded with "pilot data suggests" or removed until campaign results confirm it.

**G2. S2.5 "Training Data Contamination" section (line 126) -- MINOR**
The six transform descriptions are listed as "(variable renaming, loop restructuring, condition swapping, format string modification, type aliasing, and comment injection)." These do NOT match the actual six transform names from S3.C: SwapCondition, ArithmeticTransform, ChangeNames, TypedefExpansion, PointerArithmeticToArrayIndex, ChangeFunctionNames. Specifically:
- "loop restructuring" -- no such transform exists. ArithmeticTransform converts compound assignments, not loops.
- "format string modification" -- no such transform exists.
- "comment injection" -- no such transform exists.
- "type aliasing" matches TypedefExpansion.
- Missing: PointerArithmeticToArrayIndex, ChangeFunctionNames, ArithmeticTransform.
**This is a factual error.** The S2.5 description was written without checking the actual transforms in S3.C.

**G3. S6.2 BUILD\_FAIL analysis placeholder (line 416) -- MINOR (structural)**
The placeholder text describes expected patterns ("retained cudaMalloc, missing #pragma omp") which is grounded in pilot observations. These patterns should be verified against new campaign data when it arrives, but the expected-pattern framing is reasonable for a placeholder.

**G4. S7.2 BUILD\_FAIL discussion (line 572) -- acceptable**
References specific error patterns (retained `cudaMalloc`/`cudaFree`, missing OpenMP pragma directives, incorrect type coercions). These are grounded in pilot error taxonomy data. Should be verified against new campaign data.

**G5. S5.B Direction pair counts (line 349) -- NEEDS VERIFICATION**
Claims specific per-direction pair counts: "cuda-to-omp (24), omp-to-cuda (24), cuda-to-opencl (20), opencl-to-cuda (20), omp-to-opencl (18), opencl-to-omp (18), cuda-to-omp\_target (8), and omp\_target-to-cuda (10)." Sum = 142. This should be verified against actual spec-pair enumeration in `campaign_direction_matrix.md`. The numbers are plausible but unverified.

---

## 4. Stale Data Sweep

### 4.1 Pilot Model Names in Main Body
- **"Claude Sonnet"**: Line 335 only -- in context of "supplementary material." ACCEPTABLE.
- **"Flash-Lite"**: Line 335 only -- same context. ACCEPTABLE.
- **"Llama 3.3 70B"**: Line 335 only -- same context. ACCEPTABLE.
- **"Groq"**: Line 243 only -- in framework provider list. ACCEPTABLE (framework capability, not evaluation).
- **"azure-gpt" / "GPT-4.1"**: NOT FOUND in main body. CLEAN.

### 4.2 Pilot Numbers
- **"54.26%", "8.56%", "10.16%", "22.44%"**: NOT FOUND. CLEAN.
- **"562"**: Line 674, 694, 698 -- in archived data notes only. ACCEPTABLE if removed before submission.
- **"468"**: NOT FOUND in main body. CLEAN.
- **"184 specs"**: NOT FOUND. CLEAN.
- **"3 suites"**: NOT FOUND (only "five suites" / "five benchmark suites"). CLEAN.
- **"12 direction"**: NOT FOUND (only "six translation directions" / "eight" with case study). CLEAN.
- **"4 models" / "3 models"**: NOT FOUND in main body. CLEAN.

### 4.3 Residual Issues
- **Lines 674--709** contain archived pilot data and verification notes. These are clearly labeled but should be REMOVED before LaTeX transfer. They are working notes, not paper content. (MINOR M5)

---

## 5. Unsupported Claims

| # | Location | Claim | Issue | Severity |
|---|----------|-------|-------|----------|
| U1 | S1.2 line 36 | "at least one evaluated model exhibits sharp pass-rate degradation under augmentation" | Forward-references S6.5 which is all [PLACEHOLDER]. This was true for the pilot (Gemini Flash-Lite L4=0%), but may not hold for the new models. | MAJOR |
| U2 | S2.5 line 126 | Six transforms described as "variable renaming, loop restructuring, condition swapping, format string modification, type aliasing, and comment injection" | Factual error -- does not match actual transforms in S3.C. See G2 above. | BLOCKER |
| U3 | Abstract line 14 | "all non-KNOWN\_FAIL specs across all five suites PASS at every level L1--L4" | 13 HeCBench specs not verified for augmentation. Should say "68 of 88" or verify remaining specs. See 2.8 above. | MAJOR |
| U4 | S8.1 line 652 | Same "all non-KNOWN\_FAIL specs" claim repeated | Same issue as U3. | MAJOR |
| U5 | S8.2 line 668 | `\cite{HPCCoderV2_2024}` | Bib key does not exist. See Section 7 below. | BLOCKER |
| U6 | S6.7 line 530 | `\cite{Codex2021}` | Bib key does not exist. See Section 7 below. | BLOCKER |

---

## 6. Missing Citations

| # | Location | Claim Needing Citation | Severity |
|---|----------|----------------------|----------|
| C1 | S4.B line 292 | "RSBench is a simplified reactor simulation proxy application derived from the same OpenMC cross-section lookup problem" | No \cite{} for RSBench. Needs a citation (Tramm et al. or the RSBench README). | MAJOR |
| C2 | S4.B line 294 | "mixbench is a GPU micro-benchmark designed to measure the balance between compute throughput and memory bandwidth" | No \cite{} for mixbench. Needs a citation (Konstantinidis & Cotronis, or the mixbench repo). | MAJOR |
| C3 | S5.D line 361 | "the standard pass@k formulation of Chen et al." | Uses `\cite{Codex2021}` which does not exist in bib. The correct key is `HumanEval2021`. | BLOCKER |
| C4 | S5.E line 374 | "NVIDIA HPC SDK 24.3 (CUDA 12.3)" | No citation for NVIDIA HPC SDK. Not strictly required but good practice. | MINOR |

---

## 7. Citation-Bib Cross-Check

### 7.1 Citations in paper NOT in references.bib

| \cite{} Key | Location(s) | Status |
|-------------|-------------|--------|
| `Codex2021` | S5.D line 361, S6.7 line 530 | **MISSING from bib.** The Codex/HumanEval paper is cited as `HumanEval2021` in the bib but referenced as `Codex2021` in two places. Either add a `Codex2021` entry or change the cite keys to `HumanEval2021`. |
| `HPCCoderV2_2024` | S8.2 line 668 | **MISSING from bib.** The bib has `HPCCoderV2` (no year suffix). The cite key must match: either change the bib key to `HPCCoderV2_2024` or change the cite to `HPCCoderV2`. |

### 7.2 Bib entries NOT cited in paper

All 18 bib entries are cited at least once. No orphaned entries.

### 7.3 Bib entry completeness

All entries have author, title, year, and venue. DOIs are present for all published work. arXiv entries use `eprint` field correctly. **No issues.**

---

## 8. Prose Quality

### 8.1 Length Assessment (vs IEEE 10-page budget)

| Section | Roadmap Budget (cols) | Estimated Actual (cols) | Assessment |
|---------|:---------------------:|:-----------------------:|------------|
| S1 | 2.0 | ~2.5 | **OVER by ~0.5 col.** S1.2 "Gap in Existing Evaluation" is very long (~600 words). The training-data-contamination paragraph (line 36) alone is ~250 words. Consider compressing. |
| S2 | 2.5 | ~3.0 | **OVER by ~0.5 col.** The LASSI and CodeRosetta paragraphs are thorough but verbose. Table 1 takes ~0.5 col. |
| S3 | 3.0 | ~3.0 | On budget. BFS JSON example could be trimmed. |
| S4 | 1.5 | ~2.0 | **OVER by ~0.5 col.** RSBench and mixbench paragraphs are each ~100 words; could be combined. Table 4 takes ~0.3 col. |
| S5 | 2.0 | ~2.0 | On budget. |
| S6 | 4.5 | ~5.0+ | **OVER by ~0.5+ col** when placeholders are filled. 8 subsections with 7+ tables and 4 figures. S6.7 (pass@k) and S6.8 (statistical summary) are entirely new sections. |
| S7 | 2.5 | ~3.0 | **OVER by ~0.5 col.** S7.6 Threats to Validity is very comprehensive (7 paragraphs). |
| S8 | 1.0 | ~1.0 | On budget. |
| Refs | 1.0 | ~1.0 | 18 entries, fits in ~0.5--1.0 col. |
| **Total** | **20.0** | **~22.5+** | **OVER by ~2.5 columns (~1.25 pages).** |

**MAJOR (B4):** The paper is estimated at ~11.25 pages, exceeding the 10-page limit by ~1.25 pages. Compression targets:
1. S1.2: Cut the training-data-contamination paragraph by 50% (it's partially redundant with S2.5 and S3.C).
2. S4.B: Merge RSBench and mixbench into a single paragraph.
3. S7.6: Remove 2--3 of the 7 threat paragraphs (single augmentation seed and KNOWN\_FAIL exclusions are least essential).
4. S6: Consider making S6.7 (pass@k) more compact or merging S6.8 into a footnote + supplementary table.

### 8.2 Repetitive Content

| Topic | Locations | Issue |
|-------|-----------|-------|
| Training-data contamination / augmentation motivation | S1.2 line 36, S2.5 lines 123--127, S3.C lines 202--204, S4.B line 288 | Discussed in 4 places. S1.2 and S2.5 partially overlap. Recommend: brief mention in S1.2, full discussion in S2.5, technical details in S3.C. |
| Kernel-centric advantage over ParEval-Repo 0% | S1.2 line 34, S1.4 line 56, S2.1 line 92, S2.3 line 108, S3.D line 235, S6.1 line 401, S7.1 lines 566--568, S8.1 line 650 | Referenced in 8 places. The "0% repo-level vs N% kernel-level" comparison appears at least 5 times. Recommend: once in S1, once in S2, once in S6, once in S7. |
| LASSI comparison / agentic gap | S1.4 line 64, S2.3 lines 104--106, S6.4 line 472, S7.3 lines 584--588, S7.7 line 640, S8.2 line 666 | Referenced in 6 places. The three-tier framing (raw < self-repair < agentic) appears 3 times. Recommend: define once in S2.3, reference by shorthand elsewhere. |

### 8.3 Unclear or Jargon-Heavy Passages

- **S3.C line 227:** "the fraction mapping applies to choose how many of the six transforms to run: 33% at L2, 66% at L3, and 100% at L4. Within each selected transform, the same fraction determines how many eligible AST nodes to rewrite, with a minimum of one applied via $\max(1, \lfloor n \cdot f \rfloor)$." -- This is precise but dense. A reviewer unfamiliar with AST transforms may struggle. Consider a concrete example: "At L2, 2 of 6 transforms are selected, and each rewrites 33% of its eligible sites (minimum 1)."

- **S5.A line 329:** "MoE architecture tests whether massive parameter count with sparse activation -- where only a fraction of parameters are consulted per token -- benefits HPC translation" -- Good explanation, but "consulted" is an unusual word choice for parameter activation. Consider "activated."

### 8.4 Passive Voice
Generally acceptable. The paper uses active voice for claims and passive for methodology description, which is standard for IEEE papers. No systemic overuse.

---

## 9. [PLACEHOLDER] Inventory

### Abstract (7 placeholders)
- `[PLACEHOLDER: total_tasks]`
- `[PLACEHOLDER: kernel_count]`
- `[PLACEHOLDER: capability_gap_description]`
- `[PLACEHOLDER: model1_name]`, `[PLACEHOLDER: model1_overall_rate]`, `[PLACEHOLDER: model1_ci]`
- `[PLACEHOLDER: model2_name]`, `[PLACEHOLDER: model2_overall_rate]`, `[PLACEHOLDER: model2_ci]`
- `[PLACEHOLDER: statistical_comparison]`
- `[PLACEHOLDER: best_model_cuda_to_omp_L0_description]`
- `[PLACEHOLDER: build_fail_rate]`, `[PLACEHOLDER: verify_fail_rate]`
- `[PLACEHOLDER: failure_taxonomy_interpretation]`
- `[PLACEHOLDER: augmentation_trend_description]`

### S1 Introduction (12 placeholders)
- S1.3 line 50: `[PLACEHOLDER: total_tasks]`, `[PLACEHOLDER: build_fail_rate]`, `[PLACEHOLDER: verify_fail_rate]`
- S1.4 line 56: `[PLACEHOLDER: best_model_name]`, `[PLACEHOLDER: best_model_cuda_to_omp_L0_rate]`, `[PLACEHOLDER: best_model_cuda_to_omp_L0_count]`
- S1.4 line 58: `[PLACEHOLDER: model_comparison_description]`, `[PLACEHOLDER: model1_name]` etc. (6 sub-placeholders)
- S1.4 line 60: `[PLACEHOLDER: augmentation_overall_trend_description]`, `[PLACEHOLDER: augmentation_per_model_description]`
- S1.4 line 62: `[PLACEHOLDER: direction_asymmetry_description]`
- S1.4 line 64: `[PLACEHOLDER: self_repair_description]`

### S5 Experimental Setup (3 placeholders)
- S5.E line 377: `[PLACEHOLDER: gemini_hardware]`

### S6 Results (~100+ placeholders)
- S6.1 Table 7: 18 cell placeholders + 3 prose placeholders
- S6.2: 12 count/pct placeholders + 3 prose placeholders + Table 7b (16 cell placeholders)
- S6.3: 5 prose placeholders (per-kernel table, tier description, anomalies, sample size)
- S6.4 Table 9: 21 cell placeholders + 1 prose placeholder
- S6.5 Table 10: 10 cell placeholders + 2 prose placeholders + Cochran-Armitage values
- S6.6 Table 11: 24 cell placeholders + 4 prose placeholders
- S6.7 Table 12: 12 cell placeholders + 1 prose placeholder
- S6.8 Table 13: 18 cell placeholders

### S7 Discussion (~15 placeholders)
- S7.1: 1 rate placeholder
- S7.2: 2 rate/pct placeholders
- S7.3: 1 large prose placeholder + 3 rate placeholders
- S7.4: 1 prose placeholder
- S7.5: 1 prose placeholder
- S7.6: 4 count/threshold placeholders
- S7.7: 3 rate/prose placeholders

### S8 Conclusion (~8 placeholders)
- S8.1: `[PLACEHOLDER: total_tasks]`, `[PLACEHOLDER: capability_gap_summary]`, etc. (6 sub-placeholders)

**Total: approximately 160+ [PLACEHOLDER] markers across the paper.** This is expected -- the paper was deliberately written with placeholders pending campaign data. The fill-in task will be substantial but mechanical once data arrives.

---

## 10. Consolidated Issue List (Priority Order)

### BLOCKERS (must fix before submission)

| ID | Section | Issue | Fix |
|----|---------|-------|-----|
| **B1** | Line 6 | Paper header says "ACM sigconf" but should be "IEEE IEEEtran" per decisions log and roadmap | Change line 6 to "IEEE IEEEtran" |
| **B2** | Abstract, S3.C, S5.C, S8.1 | Augmentation verified count inconsistency: "all" vs "68" vs "54 of 60 Rodinia." 13 HeCBench specs NOT verified. Claiming "all non-KNOWN\_FAIL specs" is inaccurate. | Either verify remaining 13 HeCBench specs or standardize on "68 of 88 non-KNOWN\_FAIL specs" |
| **B3** | S5, Roadmap | Task count discrepancy: 710 vs 790 per model. Paper says 710 (S5.C), roadmap says 790 (D2). | Standardize on 710 (excluding KNOWN\_FAIL) in paper; explain the 80-task difference |
| **B4** | Whole paper | Estimated ~11.25 pages, exceeding 10-page IEEE limit by ~1.25 pages | Compress S1.2, S4.B, S7.6; reduce repetition (see 8.2) |
| **B5** | S2.5 line 126 | Transform descriptions are factually wrong ("loop restructuring," "format string modification," "comment injection" -- none of these exist) | Replace with actual transform names matching S3.C |
| **B6** | S6.7, S5.D | `\cite{Codex2021}` -- bib key does not exist (should be `HumanEval2021` or add a `Codex2021` entry) | Add `Codex2021` bib entry OR change cite to `HumanEval2021` |
| **B7** | S8.2 line 668 | `\cite{HPCCoderV2_2024}` -- bib key does not exist (bib has `HPCCoderV2` without year suffix) | Change cite to `\cite{HPCCoderV2}` |

### MAJOR (weakens paper significantly)

| ID | Section | Issue | Fix |
|----|---------|-------|-----|
| **J1** | S1.2 line 36 | "at least one evaluated model exhibits sharp pass-rate degradation" -- unsupported for new models | Guard with "pilot data suggests" or defer to S6.5 |
| **J2** | S4.B | RSBench (line 292) and mixbench (line 294) have no citations | Add bib entries and \cite{} for both |
| **J3** | Abstract, S8.1 | "all non-KNOWN\_FAIL specs" claim overstates augmentation verification scope (same root cause as B2) | Fix as part of B2 |
| **J4** | S1.3 line 50 | Contribution 3 does not mention pass@k as evaluation dimension | Add pass@k mention |
| **J5** | Whole paper | ParEval-Repo 0% comparison appears in 8 locations -- repetitive | Reduce to 4 occurrences: S1, S2, S6, S7 |

### MINOR (polish)

| ID | Section | Issue | Fix |
|----|---------|-------|-----|
| **M1** | Abstract | "all non-KNOWN\_FAIL" should state the count (68 or 88) | Specify the number |
| **M2** | S1.3 | No mention of pass@k in contributions | Add brief mention |
| **M3** | Lines 674--709 | Archived pilot data and working notes in the draft | Remove before LaTeX transfer |
| **M4** | S3.C line 229 | Still says "54 of 60 Rodinia" -- should mention 5-suite scope | Update to include 5-suite augmentation baseline |
| **M5** | S3.C line 227 | Dense mathematical notation for augmentation levels | Add concrete example |
| **M6** | S5.A line 329 | "consulted" as word choice for parameter activation | Change to "activated" |
| **M7** | S1.2, S2.5, S3.C, S4.B | Training-data-contamination motivation discussed 4 times | Consolidate: brief S1.2, full S2.5, technical S3.C only |

---

## 11. Decision Gates

**No factually incorrect stale pilot numbers remain in the main body.** The W14 crisis from the audit is fully resolved -- all pilot numbers are replaced with [PLACEHOLDER] markers. The archived data section (lines 674--709) should be removed before LaTeX transfer but is clearly labeled.

**No section restructuring is recommended.** The 8-section structure (S1--S8) with the subsection organization is sound and matches the IEEE convention. The new S6.7 (pass@k) and S6.8 (statistical summary) are good additions.

**The paper will exceed 10 pages.** This requires compression (B4) but not restructuring. The most productive cuts are in repetitive content (training-data-contamination motivation x4, ParEval-Repo 0% comparison x8, LASSI three-tier framing x3).

---

*End of adversarial critic report. 7 BLOCKERS, 5 MAJOR, 7 MINOR issues identified. The paper's structure, argumentation, and scientific rigor are strong. The primary risks are (1) page overflow, (2) factual errors in S2.5 transform descriptions, (3) missing bib entries, and (4) the augmentation verification count overstatement. All are fixable.*
