# Critic Review — Paper Survey Integration

**Reviewer:** Critic agent (Opus)
**Date:** 2026-03-29
**Files reviewed:**
- `docs/paper/drafts/s1_s2_updates.md` (S1+S2 surgical updates)
- `docs/paper/drafts/s4_benchmark_curation.md` (Rewritten S4 section)
- `analysis/reports/kernel_level_analysis.md` (source data)
- `analysis/reports/kernel_selection_candidates.md` (source data)
- `analysis/reports/workstream1_completion_report.md` (source data)
- `analysis/reports/benchmark_inventory_complete_v3.md` (source data)
- `analysis/data/API_pairwise_coverage_matrix__counts_.csv` (source data)
- `scripts/evaluation/generate_paper_figures.py` (figure generator)
- `docs/paper/paper_draft.md` (current paper)
- `docs/paper/writing_roadmap.md` (authoritative plan)

---

## Verdict: NEEDS FIXES

Three issues are blocking: (1) the CUDA-OpenMP repository count contradiction between the CSV and all prose, (2) the RAJAPerf kernel count discrepancy between source reports, and (3) the figure numbering conflict between the S4 draft and the existing paper draft S6 figure references. All other issues are non-blocking notes or integration items.

---

## Data Accuracy Issues

### DA-1: CRITICAL — "21 repositories" for CUDA+OpenMP contradicts the CSV

The S4 draft (line 9), the S1/S2 updates (line 139), the paper_draft (line 38), and the kernel_level_analysis.md (line 13) all claim "21 repositories containing both CUDA and OpenMP."

However, `analysis/data/API_pairwise_coverage_matrix__counts_.csv` shows the CUDA-OpenMP cell = **6**, not 21. The diagonal values (CUDA=13, OpenMP=13) represent total repos with each API. The off-diagonal CUDA-OpenMP = 6 is the pairwise count.

**Possible explanation:** The "21" may come from a different counting methodology in the kernel-level analysis (e.g., counting individual benchmark sub-directories within HeCBench as separate "repositories," or including RAJAPerf sub-modules). But if the CSV is the authoritative pairwise matrix, then 6 is the correct repository count.

**Action required:** Reconcile this discrepancy before publication. If the CSV uses a different definition of "repository" than the kernel-level analysis, document which definition the paper uses. If the CSV is wrong, regenerate it. If "21" is wrong, update all occurrences across S1.2, S4.A, S4.C, and Table 3.

### DA-2: MODERATE — RAJAPerf kernel count: 80 vs 106

`benchmark_inventory_complete_v3.md` (line 90) says RAJAPerf has **80** kernels. `kernel_level_analysis.md` (line 37) says **106** kernels. The S4 draft uses 106 in Table 3 ("RAJAPerf (106)").

**Possible explanation:** The 80 may be from the initial repository-level survey, and 106 from a more detailed kernel enumeration. Or 80 refers to base kernels and 106 includes variant configurations.

**Action required:** Verify the correct count and ensure consistency. If 106 is correct, update the inventory. If 80 is correct, update the kernel-level analysis and Table 3.

### DA-3: MINOR — HeCBench total kernels: 506 vs 513

`kernel_level_analysis.md` says "HeCBench (506 kernels)" (line 32). `benchmark_inventory_complete_v3.md` says "513" (line 85). The S4 draft uses "513 kernels" (line 39).

**Possible explanation:** The 506 may exclude kernels without Makefiles or with other filtering, while 513 is the raw directory count.

**Action required:** Pick one number and use it consistently. The S4 draft currently uses 513, which matches the inventory but not the kernel-level analysis.

### DA-4: MINOR — Rodinia CUDA-OpenMP pairs: 19 vs 18

The kernel_level_analysis.md says "Rodinia (19)" for CUDA-OpenMP kernel pairs. But the paper_draft says "22 CUDA, 18 OpenMP" -- meaning at most 18 kernels have both CUDA and OpenMP. The number 19 comes from `kernel_level_analysis.md` line 44 which describes "19 kernels with CUDA+OpenCL+OpenMP" (3-API intersection), but this exceeds the 18 OMP spec count in the paper.

**Action required:** Verify whether Rodinia has 18 or 19 CUDA+OpenMP pairs. If 18 is correct (limited by OMP spec count), update Table 3 sources. Note that "Rodinia (19)" appears in both the S4 rewrite Table 3 and the kernel_level_analysis.

### DA-5: VERIFIED — "35 repos surveyed"

`benchmark_inventory_complete_v3.md` line 8: "35 parallel computing benchmark repositories" -- confirmed.
40 archives downloaded, 3 failed, 35 analyzed. The S4 draft says "40 candidate archives... After excluding 3 failed downloads and 2 repositories with insufficient documentation, 35 repositories were analyzed." The math (40-3-2=35) is consistent, but the "2 with insufficient documentation" is inferred from the arithmetic and not explicitly stated in the inventory. This is acceptable but thin.

### DA-6: VERIFIED — "472 CUDA-OpenMP kernel pairs"

`kernel_level_analysis.md` line 13: "CUDA + OpenMP | 21 repos | 472 kernels" -- confirmed for the kernel count (repo count disputed per DA-1).

### DA-7: VERIFIED — "327 kernels with all 4 APIs"

`kernel_selection_candidates.md` line 4: "327 kernels with all 4 API variants found in HeCBench" -- confirmed.

### DA-8: VERIFIED — "325 with Makefiles"

`kernel_selection_candidates.md` line 5: "325 with Makefiles" -- confirmed.

### DA-9: VERIFIED — "242 with self-checking patterns"

`kernel_selection_candidates.md` line 5: "242 with self-checking patterns" -- confirmed.

### DA-10: VERIFIED — "60 selected" HeCBench kernels

`workstream1_completion_report.md` line 11: "60 HeCBench kernels" -- confirmed. Note: 60 is the working set from which 10 curated kernels were selected for the evaluation corpus.

### DA-11: VERIFIED — Table 4 numbers

All Table 4 numbers verified against specs on disk:
- Rodinia: 22 kernels, 60 specs (22 CUDA confirmed), 54 PASS, 6 KNOWN_FAIL -- matches known-issues.md
- HeCBench curated: 10 kernels, 25 specs (verified by file listing), 23 PASS, 2 KNOWN_FAIL -- matches
- XSBench: 1 kernel, 4 specs -- confirmed
- RSBench: 1 kernel, 4 specs -- confirmed
- mixbench: 1 kernel, 3 specs -- confirmed
- Total: 35 kernels, 96 specs, 88 PASS, 8 KNOWN_FAIL -- arithmetic correct

### DA-12: VERIFIED — "35 kernels" in S1/S2 Table 1 update

22 Rodinia + 10 HeCBench curated + 1 XSBench + 1 RSBench + 1 mixbench = 35. Confirmed.

### DA-13: VERIFIED — "41 distinct domains"

`workstream1_completion_report.md` line 71: "41 distinct domains" -- confirmed.

### DA-14: VERIFIED — "20-60x" multiplier claim

`kernel_level_analysis.md` line 17: "The kernel-level count is ~20-60x higher" -- confirmed.

### DA-15: NOTE — "2 with insufficient documentation" is unattested

The S4 draft's claim "After excluding 3 failed downloads and 2 repositories with insufficient documentation" derives the "2" from 40 - 3 - 35 = 2. The inventory does not explicitly describe 2 repos excluded for insufficient documentation. While the math is consistent, a reviewer could challenge the specificity of this claim. Consider either: (a) identifying the 2 excluded repos by name, or (b) softening to "after excluding 5 repositories for download failures or insufficient documentation."

---

## Cross-Section Consistency Issues

### CS-1: CRITICAL — Figure numbering conflict between S4 rewrite and existing paper_draft S6

The S4 rewrite uses:
- F2 = API co-occurrence heatmap (matches paper_draft S4)
- F3 = repo vs kernel comparison (NEW figure)
- F4 = selection funnel (NEW figure)

The existing paper_draft S6 uses:
- F3 = failure taxonomy stacked bar (line 412)
- F4 = kernel-by-model heatmap (line 439)
- F5 = augmentation robustness (line 485)
- F6 = cross-direction bar chart (line 508)

The figure generator (`generate_paper_figures.py`) uses the NEW numbering: f2=co-occurrence, f3=repo-vs-kernel, f4=funnel, f5=heatmap, f6=taxonomy, f7=augmentation, f8=cross-direction, f9=xsbench. This is correct.

The S1/S2 writer correctly uses the new numbering (F2, F3, F5 for the formerly-F2 heatmap).

**Action required:** When the lead integrates, ALL figure references in S6 must be renumbered: F3->F6, F4->F5 (or appropriate new numbers), F5->F7, F6->F8. The figure generator already has the correct numbering. The paper_draft S6 references are stale.

### CS-2: MINOR — "2 models" vs "2 models" consistency

Both S1/S2 and S4 correctly reference 2 models (Qwen 3.5 + Gemini 2.5 Flash). However, the S1/S2 writer proposes removing "2 models" from Table 1's ParBench row, arguing it's an evaluation parameter, not a framework scale metric. This is a reasonable editorial decision but the lead should verify that the model count is stated somewhere accessible (S5.A covers it).

### CS-3: MINOR — "6 dirs" in Table 1 vs "6 translation directions" in S4/S5

Table 1 says "6 dirs." S4.D says "six standard translation directions, with two additional OMP-target directions evaluated as case studies." S5.B says "Six primary translation directions... Two additional directions involving OpenMP target offload." These are consistent. The "6 dirs" in Table 1 refers to the standard directions; the 2 additional are case studies. This is clear.

### CS-4: NOTE — "96 specs" vs "206 specs"

The S1/S2 writer correctly notes (line 62): "the full spec directory contains 206 specs (including 135 bulk HeCBench), but the paper's '96 specs' refers to the curated evaluation set only." The paper should clarify that 96 refers to the curated set. The S4 draft does this well in 4.B by explaining the HeCBench selection funnel.

### CS-5: VERIFIED — 5 suites consistent across all sections

S1 (contributions): "five HPC benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench)"
S2.6 (updated): mentions 5 suites implicitly
S4 (all): consistently references 5 suites
Table 4: lists all 5 suites

---

## Figure-Text Alignment Issues

### FT-1: VERIFIED — Figure files exist

All three new figure files exist on disk:
- `docs/paper/figures/f2_api_cooccurrence_survey.png` (225 KB)
- `docs/paper/figures/f3_repo_vs_kernel.png` (118 KB)
- `docs/paper/figures/f4_selection_funnel.png` (180 KB)

### FT-2: S4 draft F2 and F3 references

S4.A references F2 (API co-occurrence heatmap) at line 11 and F3 (repo vs kernel) at line 13. The S4 draft also has descriptive figure captions inline. These match the generated figure content.

### FT-3: S4 draft F4 reference

S4.B references F4 (selection funnel) at line 39. The description says "Starting from 327 kernels with all 4 API variants, successive filters for build infrastructure (325), self-checking patterns (242), complexity bounds, and domain diversity yield the 60-kernel working set." This matches the selection methodology.

### FT-4: NOTE — S4 funnel figure endpoint ambiguity

The S4 text says the funnel yields "the 60-kernel working set" (F4), but the paper's evaluation corpus uses the 10-kernel curated subset, not the 60-kernel working set. The figure and text should clarify that 60 is the intermediate working set from which 10 were curated for the evaluation corpus. The S4 prose does this in the paragraph following the funnel, but the figure caption should be explicit to avoid confusion.

### FT-5: S1/S2 F2 and F3 references

The S1/S2 update inserts "(Figure 2 visualizes API co-occurrence across surveyed repositories; Figure 3 illustrates how repository-level counting understates kernel-level translation opportunities by 20--60x)" into S1.2. This is appropriate and matches the generated figures.

### FT-6: NOTE — S6 figure references need renumbering

As noted in CS-1, the paper_draft S6 figure references (F3, F4, F5, F6) use the old numbering and must be updated to (F6, F5, F7, F8) or equivalent when the lead integrates. The writing_roadmap (line 228-231) also uses the old numbering (F3 = failure taxonomy, F4 = kernel heatmap), which needs updating.

---

## Missing Content

### MC-1: HIP-OpenMP and SYCL pair data missing from Table 3

The kernel_level_analysis.md reports six API pairs including HIP-SYCL (615) and OpenMP-SYCL (453). The S4 rewrite Table 3 includes only 5 rows and omits HIP-SYCL and OpenMP-SYCL. The paper_draft's existing Table 3 omits these as well. Since HIP and SYCL are not ParBench evaluation targets, this omission is defensible, but including HIP-SYCL would strengthen the argument that the survey was comprehensive and that CUDA-OpenMP was selected from a broader landscape. Consider adding a footnote or expanding the table.

### MC-2: CloverLeaf, BabelStream, miniBUDE contributions absent from S4

The kernel_level_analysis.md identifies CloverLeaf (16 kernels), BabelStream (5 kernels), and miniBUDE (1 kernel) as significant multi-API benchmark sources. The S4 draft does not mention these by name when discussing the survey results. While they were not selected for ParBench, mentioning them briefly would demonstrate the survey's breadth and strengthen the selection rationale (why 5 suites were chosen over alternatives).

### MC-3: Tier A/B classification not in S4

The inventory classifies repositories as Tier A (30) or Tier B (5). The S4 draft mentions Tier A/B but does not explain the criteria in detail. A brief parenthetical could add rigor: "(Tier A: documented build, automated verification, active maintenance; Tier B: partial verification or limited API coverage)."

### MC-4: No discussion of WHY the 10 curated HeCBench kernels were chosen

The S4 rewrite explains that 10 kernels were selected from the 60-kernel working set "for verified correctness across multiple APIs and maximum domain diversity." This is thin. The kernel_selection_candidates.md contains much richer detail about the selection criteria (file count bounds, external data exclusion, domain diversity maximization). A sentence or two about the exclusion criteria (complexity bounds, external data requirements) would strengthen the rationale.

### MC-5: "68 of 88" augmentation baseline mentioned in S4.B but not elaborated

The S4 rewrite (line 49) says "All 60 CUDA variants pass build/run/verify on the evaluation platform; 41 of the 60 OpenMP variants pass (68.3%)." This is for the 60 HeCBench working set, not the curated 10. This is correctly stated but the reader might confuse the 60-kernel working set statistics with the 10-kernel curated subset statistics.

---

## Redundancy

### R-1: HeCBench selection funnel described in both S4 rewrite and workstream1_completion_report

The S4 rewrite (4.B, lines 39-51) and the workstream1_completion_report (Check 6, line 71) both describe the 60-kernel selection with domain breakdown. This is expected (one is source data, one is paper text) and not a problem in the paper itself.

### R-2: Rodinia KNOWN_FAIL enumeration appears in both S4 rewrite and paper_draft

The S4 rewrite (lines 53-60) enumerates the 6 Rodinia KNOWN_FAIL specs. The existing paper_draft (lines 280-286) has the identical enumeration. Since the S4 rewrite replaces the existing S4, this is not redundancy -- it is a replacement. The lead should verify the old text is fully removed.

### R-3: "Survey-grounded curation" appears in both S1.2 and S2.6

The S1/S2 writer adds Figure 2/3 references to S1.2 (Change Block 1) and adds "survey-grounded benchmark curation" as the 6th differentiator in S2.6 (Change Block 5). Both mention the 35-repo survey and the 472 kernel pairs. This is acceptable -- S1.2 introduces the survey briefly, S2.6 positions it as a differentiator -- but the lead should ensure the phrasing is varied enough to avoid the impression of repetition.

### R-4: Table 3 data appears in both S4.A prose and Table 3 itself

The S4 rewrite describes CUDA-OpenMP (472), CUDA-HIP (633), CUDA-SYCL (616) in the prose (line 9) and again in Table 3 (lines 17-23). This is standard academic writing (prose introduces the finding, table provides the data) and not problematic.

---

## SC26 Quality Notes

### SQ-1: Academic tone is appropriate throughout

Both the S1/S2 updates and the S4 rewrite maintain proper academic register. No informal language detected.

### SQ-2: Citation format consistent

The S4 rewrite uses `\cite{...}` format consistently: `\cite{HeCBench2023}`, `\cite{Rodinia2009}`, `\cite{XSBench2014}`, `\cite{RSBench2014}`, `\cite{mixbench2017}`, `\cite{ParEvalRepo2025}`. The S1/S2 updates do not add new citations (only figure references).

### SQ-3: Table/figure formatting

Tables 3 and 4 in the S4 rewrite use consistent markdown formatting with aligned columns. Figure references use `[Figure N]` convention. This is consistent with the rest of the paper_draft.

### SQ-4: Minor style note — "~200" in Table 3

The CUDA-OpenCL row uses "~200" while all other rows use exact numbers. This is acceptable if the exact count is uncertain, but ideally all rows should have the same precision. If an exact count is available, use it.

### SQ-5: The S4 rewrite is well-structured

The four-subsection structure (4.A Suite Selection, 4.B Kernel Selection, 4.C API Coverage, 4.D Evaluation Corpus) is clean and follows the paper_draft's existing organization. The progression from survey methodology to selection criteria to corpus summary is logical and builds the argument effectively.

### SQ-6: LASSI venue citation note from S1/S2 writer

The S1/S2 writer flags (line 98): "LASSI's venue citation should be double-checked against the actual paper. The writing_roadmap says 'CLUSTER Workshops 2024' while the draft says 'LLMxHPC Workshop, IEEE CLUSTER'24'." This is a valid concern but not a content issue -- it affects `references.bib`, not the draft text. Flag for final bibliography review.

---

## Figure Generator Code Issues

### FG-1: VERIFIED — Renumbering done correctly

The figure generator (`generate_paper_figures.py`) implements the correct renumbering:
- f1 = system architecture (unchanged)
- f2 = API co-occurrence heatmap (NEW survey figure)
- f3 = repo vs kernel comparison (NEW survey figure)
- f4 = selection funnel (NEW survey figure)
- f5 = kernel-by-model heatmap (was formerly f2 in pilot code)
- f6 = failure taxonomy (was formerly f3)
- f7 = augmentation robustness (was formerly f4)
- f8 = cross-direction (was formerly f5)
- f9 = XSBench (was formerly f6)

Functions `generate_f2_api_cooccurrence`, `generate_f3_repo_vs_kernel`, `generate_f4_selection_funnel` are defined at lines 498, 610, 698 respectively. All nine figure functions are registered in the dispatch block (lines 1514-1562).

### FG-2: NOTE — Old model references in figure generator

`MODEL_COLORS`, `MODEL_DISPLAY`, `MODEL_LINESTYLE` (lines 73-115) still reference the pilot models (claude-sonnet-4-6, azure-gpt-4.1, groq-llama-3.3-70b-versatile, gemini-2.5-flash-lite). These need updating for the new 2-model campaign (Qwen 3.5, Gemini 2.5 Flash). This is outside the scope of the current integration task but should be done before the campaign results are visualized.

### FG-3: NOTE — Hardcoded pilot data in figure generator

`AUG_ROBUSTNESS` (line 177), `RODINIA_DIRECTION` (line 186), `RODINIA_DIR_TAXONOMY` (line 193), and `XSBENCH_L0` (line 199) contain hardcoded pilot data for the old 3-model evaluation. These need to be replaced with new campaign data or made data-driven (loading from result files). Again, outside the current integration scope.

### FG-4: VERIFIED — New figure output paths

The figure generator saves to `docs/paper/figures/f{N}_{name}.png`, which matches the verified file paths.

---

## Recommendations for Lead Integration

1. **BLOCKING: Resolve the "21 repositories" vs CSV "6 repositories" discrepancy (DA-1).** Before integrating, determine the correct CUDA+OpenMP repository count. If "21" comes from a different methodology than the CSV, add a footnote explaining the methodology. If the CSV is the authoritative source, "6" must replace "21" in S1.2, S4.A, S4.C, Table 3, and the kernel_level_analysis.md.

2. **BLOCKING: Resolve the RAJAPerf kernel count discrepancy (DA-2).** Verify whether 80 or 106 is correct and update the inconsistent source.

3. **BLOCKING: Renumber S6 figure references (CS-1).** When integrating the S4 rewrite and S1/S2 updates, all figure references in S6 (and the writing_roadmap) must be updated to the new numbering scheme: old F3 (failure taxonomy) -> F6, old F4 (kernel heatmap) -> F5, old F5 (augmentation) -> F7, old F6 (cross-direction) -> F8. The figure generator already uses the correct numbering.

4. **Apply S1/S2 Change Blocks 1 and 5 to paper_draft.md.** These are surgical inserts -- apply them as described, verifying the exact line numbers match the current draft (the draft may have shifted since the S1/S2 writer read it).

5. **Apply S1/S2 Change Block 2 (Table 1 update) to paper_draft.md.** Replace the ParBench row with the updated version. Verify that "35 kernels" is correct per DA-12.

6. **Replace the existing S4 section in paper_draft.md with the S4 rewrite.** The S4 rewrite is a complete replacement for the existing S4 (lines 247-316 of the current draft). Verify no orphaned text remains.

7. **Add the HIP-OpenMP repo count to S4 Table 3 or leave as "--".** The current S4 rewrite Table 3 has "--" for the HIP-OpenMP repos column. This is acceptable (the kernel_level_analysis doesn't give a repo count for this pair), but a footnote explaining why would be cleaner.

8. **Review the "2 insufficient documentation" claim (DA-15).** Either name the 2 excluded repositories or soften the language.

9. **Verify the Rodinia CUDA-OpenMP pair count (DA-4).** Check whether 19 or 18 is correct by counting specs with both CUDA and OMP variants.

10. **Update the writing_roadmap.md figure numbering** (lines 228-231) to match the new scheme: F2 = co-occurrence, F3 = repo-vs-kernel, F4 = funnel, F5 = heatmap, F6 = taxonomy, F7 = augmentation, F8 = cross-direction.

11. **Consider adding CloverLeaf/BabelStream to S4.A prose (MC-2)** as evidence of survey breadth, even though they were not selected.

12. **Update figure generator model references (FG-2, FG-3)** before campaign visualization, as a separate task from this integration.
