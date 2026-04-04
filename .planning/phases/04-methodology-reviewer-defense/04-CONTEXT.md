# Phase 4: Methodology & Reviewer Defense - Context

**Gathered:** 2026-04-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Make Section 3-5 methodology descriptions precise enough to withstand SC-level reviewer scrutiny. Write explicit justifications for kernel isolation, statistical test choices, and conjunction verification. This phase writes/strengthens methodology TEXT in paper.tex — it does not produce new data or analysis artifacts.

</domain>

<decisions>
## Implementation Decisions

### Kernel Isolation Defense (METHOD-01)
- **D-01:** Consolidate into ONE authoritative paragraph at the TOP of Section 3.4 (Evaluation Pipeline: Kernel-Centric Translation). Reviewer reads WHY first (rationale), then HOW (existing technical description at line 361 becomes second paragraph).
- **D-02:** Include preemptive defense against the "making it too easy" reviewer objection. Use analytical framing: "We isolate translation skill from build-system generation because they are orthogonal competencies. Conflating them produces artificially low pass rates that obscure translation capability."
- **D-03:** Three-layer evidence structure: (1) Lead with XSBench same-kernel comparison — ParEval-Repo 0% vs ParBench 68.8%, using the published 68.8% figure from paper_data.json. (2) Add 31/35 kernels exceeding ParEval-Repo's 133 SLoC threshold — kernel-level evaluation is not limited to trivial programs. (3) Add 30.8% BUILD_FAIL rate — even with build infrastructure provided, kernel-level translation remains challenging.
- **D-04:** Keep existing XSBench mentions in abstract (line 71), related work (line 198), and results (line 718) as-is. The new consolidated paragraph is the authoritative version; other mentions reinforce it. SC reviewers read sections independently — repetition is expected.

### Statistical Test Justification (METHOD-02)
- **D-05:** Expand inline in the Metrics subsection (Section 5.4, currently line 644). Add 1-2 sentences per test right after the current one-liner. Keeps all methodology in one place.
- **D-06:** Justify all three tests used: Wilson CI, Cochran-Armitage, and McNemar.
- **D-07:** Briefly name the rejected alternative for each test: Wilson over Wald (better coverage near 0 and 1), Cochran-Armitage over chi-squared (exploits ordinal structure of L0-L4 levels), McNemar over unpaired chi-squared (paired design — same kernel in both directions). Shows deliberate choice without over-explaining.

### Conjunction Verification Defense (METHOD-04)
- **D-08:** Place defense paragraph at end of Section 3.2 (Harness Pipeline: Build, Run, Verify), after describing the verify stage. Natural home for "why we verify this way."
- **D-09:** Use a compilation-only misclassification example: a real VERIFY_FAIL kernel from the Qwen results where the translation compiles and runs (exit_code=0) but produces wrong output. Pick the specific kernel name from result JSONs during planning phase.
- **D-10:** Cite the 9.8% VERIFY_FAIL rate as the quantitative backing — these are tasks that compilation-only verification would misclassify as PASS.
- **D-11:** Keep focused on core conjunction (exit_code AND stdout_pattern) vs alternatives. Do NOT repeat the clBuildProgram kernel-only scan (already described at lines 369-370).

### Claude's Discretion
- Exact wording and sentence structure of each paragraph
- Whether to add a LaTeX source comment citing the data source for each number
- How to handle the transition between the new rationale paragraph and existing technical paragraph in Section 3.4
- Specific VERIFY_FAIL kernel to use as the conjunction verification example (pick from Qwen results during planning)

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Paper (primary edit target)
- `docs/paper/latex/paper.tex` — All edits go here. Key locations:
  - Section 3.2 (Harness Pipeline, ~line 299): conjunction verification defense goes here
  - Section 3.4 (Evaluation Pipeline, ~line 356): kernel isolation defense goes here
  - Section 5.4 (Metrics, ~line 635): statistical test justifications go here

### Data sources for numbers cited
- `results/analysis/paper_data.json` — Source for 68.8% (L0 CUDA-to-OMP), 30.8% BUILD_FAIL rate, 9.8% VERIFY_FAIL rate
- `results/analysis/statistical_analysis.json` — Source for Cochran-Armitage z=-0.17, p=0.87; Wilson CIs; McNemar results
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
- `results/analysis/error_taxonomy.json` — Contains per-kernel failure mode breakdown, useful for finding the VERIFY_FAIL example

### Established Patterns
- Phase 1 established inline LaTeX source comments (e.g., `% src: paper_data.json > field`). Continue this pattern for new methodology text.
- Phase 1-3 work means all data is freshly verified — numbers can be cited with confidence.

### Integration Points
- New paragraphs insert into existing Section 3.2, 3.4, and 5.4 — must flow with surrounding text
- Cross-references to existing related work paragraphs (TransCoder at line 187, ParEval-Repo at line 198) should use `\cite{}` consistently

</code_context>

<specifics>
## Specific Ideas

- Kernel isolation paragraph should use analytical framing, not rebuttal tone: "measurement design choice" language, not "one might argue" language
- Three-layer evidence for kernel isolation: XSBench comparison -> SLoC threshold -> BUILD_FAIL rate (escalating from specific to general)
- Statistical test justifications should each be one clause naming the rejected alternative (e.g., "Wilson rather than Wald")
- The VERIFY_FAIL example should be a specific named kernel — to be identified from result JSONs during planning

</specifics>

<deferred>
## Deferred Ideas

- **Reproducibility claims paragraph** (METHOD-03) — User did not select for discussion. The hardware/software table (Section 5.5) already contains version pins. A dedicated reproducibility paragraph with commit hashes and data availability statement can be added if page budget allows, but is lower priority than the three selected areas.

</deferred>

---

*Phase: 04-methodology-reviewer-defense*
*Context gathered: 2026-04-04*
