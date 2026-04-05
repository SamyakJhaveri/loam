# Phase 4: Methodology & Reviewer Defense - Context

**Gathered:** 2026-04-05 (updated from 2026-04-04)
**Status:** Ready for planning

<domain>
## Phase Boundary

Make Section 3-5 methodology descriptions precise enough to withstand SC-level reviewer scrutiny. Write explicit justifications for kernel isolation, statistical test choices, conjunction verification, and reproducibility pins. This phase writes/strengthens methodology TEXT in paper.tex — it does not produce new data or analysis artifacts.

</domain>

<decisions>
## Implementation Decisions

### Kernel Isolation Defense (METHOD-01)
- **D-01:** Consolidate into ONE authoritative paragraph at the TOP of Section 3.4 (Evaluation Pipeline: Kernel-Centric Translation). Reviewer reads WHY first (rationale), then HOW (existing technical description becomes second paragraph).
- **D-02:** Include preemptive defense against the "making it too easy" reviewer objection. Use analytical framing: "We isolate translation skill from build-system generation because they are orthogonal competencies. Conflating them produces artificially low pass rates that obscure translation capability."
- **D-03:** Three-layer evidence structure: (1) Lead with XSBench same-kernel comparison — ParEval-Repo 0% vs ParBench **64.2% CUDA-to-OMP overall across all 5 suites** (77/120 tasks; 68.8% at L0 on the 16-kernel balanced Rodinia subset). All-suite is the primary figure; L0 balanced figure can be mentioned parenthetically. (2) Add 31/35 kernels exceeding ParEval-Repo's 133 SLoC threshold — this stat already covers all 5 suites (Rodinia, XSBench, RSBench, mixbench, HeCBench). (3) Add **33.9% BUILD_FAIL rate (237/700 across all 5 suites)** — even with build infrastructure provided, kernel-level translation remains challenging.
- **D-04:** Keep existing XSBench mentions in abstract, related work, and results as-is. The new consolidated paragraph is the authoritative version; other mentions reinforce it. SC reviewers read sections independently — repetition is expected.

### Statistical Test Justification (METHOD-02)
- **D-05:** **Full rewrite** of the statistical sentence at line ~644 (Metrics subsection, Section 5.4). The current text says "Fisher's exact test for pairwise model comparison" — this is factually incorrect. The actual analysis uses McNemar's test for direction asymmetry (paired kernel design). Rewrite the entire sentence to name all three tests with brief rationale: Wilson score CIs (better coverage near boundary proportions), McNemar's test for direction asymmetry (paired kernel design), and Cochran-Armitage for augmentation trends (exploits ordinal structure of L0-L4 levels).
- **D-06:** Justify all three tests used: Wilson CI, Cochran-Armitage, and McNemar. Each gets 1-2 sentences in the Metrics subsection.
- **D-07:** Briefly name the rejected alternative for each test: Wilson over Wald (better coverage near 0 and 1), Cochran-Armitage over chi-squared (exploits ordinal structure of L0-L4 levels), McNemar over unpaired chi-squared (paired design — same kernel in both directions). Shows deliberate choice.
- **D-07b:** Update Bonferroni correction threshold from α=0.0167 (3 tests) to **α=0.0125 (4 tests, matching statistical_analysis.json)**. The script corrects for all 4 direction pairs including omp_target. Update the source comment at line ~992 accordingly. No significance conclusions change (all p-values well above both thresholds).

### Conjunction Verification Defense (METHOD-04)
- **D-08:** Place defense paragraph at end of Section 3.2 (Harness Pipeline: Build, Run, Verify), after describing the verify stage. Natural home for "why we verify this way."
- **D-09:** Use a compilation-only misclassification example: a real VERIFY_FAIL kernel from the Qwen results where the translation compiles and runs (exit_code=0) but produces wrong output. Pick the specific kernel name from result JSONs during planning phase.
- **D-10:** Cite the **7.3% VERIFY_FAIL rate (51/700 across all 5 suites)** as the quantitative backing — these are tasks that compilation-only verification would misclassify as PASS.
- **D-11:** Keep focused on core conjunction (exit_code AND stdout_pattern) vs alternatives. Do NOT repeat the clBuildProgram kernel-only scan (already described at lines ~369-370).

### Reproducibility Pins (METHOD-03) — PROMOTED from deferred
- **D-12:** Add 2-3 sentences at end of Section 5.5 (after the hardware/software table, after line ~681). Minimal but sufficient for SC reviewer expectations.
- **D-13:** Content: ParBench commit hash, Rodinia submodule commit pin (9c10d3ea), model API version dates (Qwen 3.5 accessed via Together AI), data availability statement (results JSON on GitHub).
- **D-14:** Tone: factual pins, not boilerplate. "To support reproducibility, ParBench is pinned at commit X; Rodinia at commit Y (git submodule); Qwen 3.5 397B-A17B accessed via Together AI API on [date range]."

### Claude's Discretion
- Exact wording and sentence structure of each paragraph
- Whether to add a LaTeX source comment citing the data source for each number
- How to handle the transition between the new rationale paragraph and existing technical paragraph in Section 3.4
- Specific VERIFY_FAIL kernel to use as the conjunction verification example (pick from Qwen results during planning)
- Exact commit hash to cite (use `git rev-parse HEAD` at execution time)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper (primary edit target)
- `docs/paper/latex/paper.tex` — All edits go here. **Line numbers are approximate — planner must grep for actual subsection boundaries before editing.** Key sections:
  - Section 3.2 (Harness Pipeline, ~line 299): conjunction verification defense goes here
  - Section 3.4 (Evaluation Pipeline, ~line 356): kernel isolation defense goes here
  - Section 5.4 (Metrics, ~line 635): statistical test full rewrite goes here
  - Section 5.5 (Hardware and Software, ~line 648): reproducibility sentences go after table (~line 681)
  - Section 6.8 (Statistical Summary, ~line 985): extend existing methodological notes (~line 1012), update Bonferroni α

### Data sources for numbers cited (Phase 4 uses quantitative_findings.json as primary provenance)
- `results/analysis/quantitative_findings.json` — **Primary provenance source.** Campaign 1 (700 primary tasks, all 5 suites): failure_taxonomy.status_counts gives BUILD_FAIL=237, VERIFY_FAIL=51. Direction rates, asymmetry stats, and augmentation trends all present with field-level provenance.
- `results/analysis/statistical_analysis.json` — McNemar p-values (all 4 pairs), Bonferroni α=0.0125, Cochran-Armitage results. Cross-check against quantitative_findings.json.
- `results/analysis/sloc_analysis.json` — SLoC for all 35 kernels across 5 suites. summary.kernels_above_pareval_threshold = 31.
- `results/evaluation/together-qwen-3.5-397b-a17b/` — Raw result JSONs for finding a specific VERIFY_FAIL kernel example

### Related work for context
- ParEval-Repo cite key: `\cite{ParEvalRepo2025}` — 0% pass rate, 133 SLoC threshold
- TransCoder cite key: `\cite{TransCoder2020}` — reference matching vs functional correctness argument
- CodeRosetta cite key: `\cite{CodeRosetta2024}` — BLEU/compilation-only alternative

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/analysis/generate_paper_data.py` — Can be queried to verify exact numbers before writing text
- `scripts/analysis/quantitative_findings.py` — Phase 9 output; provenance-tracked findings for paper claims
- `results/analysis/error_taxonomy.json` — Contains per-kernel failure mode breakdown, useful for finding the VERIFY_FAIL example

### Established Patterns
- Phase 1 established inline LaTeX source comments (e.g., `% src: paper_data.json > field`). Continue this pattern, now pointing to `quantitative_findings.json` field paths for new methodology text.
- Phase 1-3 work means all data is freshly verified — numbers can be cited with confidence.
- Phase 9 quantitative_findings.json has a `paper_claims` array mapping claim IDs to exact source values — use this for provenance comments.
- Existing line 1012 already has methodological notes for Wilson/Cochran-Armitage/McNemar — Phase 4 extends these, not replaces.

### Integration Points
- New paragraphs insert into existing Section 3.2, 3.4, 5.4, and 5.5 — must flow with surrounding text
- Cross-references to existing related work paragraphs (TransCoder, ParEval-Repo) should use `\cite{}` consistently
- Bonferroni α update at line ~992 requires updating the source comment that currently documents the discrepancy

</code_context>

<specifics>
## Specific Ideas

- Kernel isolation paragraph should use analytical framing, not rebuttal tone: "measurement design choice" language, not "one might argue" language
- Three-layer evidence for kernel isolation: XSBench comparison -> SLoC threshold -> BUILD_FAIL rate (escalating from specific to general)
- Statistical test justifications should each be one clause naming the rejected alternative (e.g., "Wilson rather than Wald")
- The VERIFY_FAIL example should be a specific named kernel — to be identified from result JSONs during planning
- All-suite numbers are primary for methodology claims (700 primary campaign tasks across 5 suites); Rodinia-only figures used only where Section 6 scope consistency requires it
- Statistical sentence at line ~644 gets a FULL rewrite, not just a swap of "Fisher's" → "McNemar's"

</specifics>

<deferred>
## Deferred Ideas

None — all four METHOD requirements are now active (METHOD-03 promoted from deferred).

</deferred>

---

*Phase: 04-methodology-reviewer-defense*
*Context gathered: 2026-04-04, updated: 2026-04-05*
