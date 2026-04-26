# ParBench NeurIPS Rewrite Memo

## Outputs

- New NeurIPS entry point: `main_neurips.tex`
- New appendix file: `appendices_neurips.tex`
- Compiled PDF: `main_neurips.pdf`
- Original extracted source preserved: `source_original/extracted/`

The repository directory was not a Git worktree and initially contained only `parbench.zip`, so the original archive was preserved and a separate `neurips_rewrite/` source version was created.

## What Stayed In The Main

- A compact abstract with the problem, ParBench framework, corpus scale, main pass rates, failure bottleneck, augmentation trend result, and pass@k takeaway.
- A self-contained introduction covering the evaluation gap, repository-level confound, contamination concern, and three contributions.
- A concise framework section covering declarative specs, kernel-centric evaluation, build-run-verify correctness, failure taxonomy, bounded self-repair, and AST-driven augmentation.
- Survey-grounded benchmark construction, including API-selection rationale and a compact corpus table.
- Essential experimental setup: models, directions, protocol, metrics, statistical tests, and correctness-only scope.
- Main results: overall pass rates, direction-level pass rates, representative per-kernel difficulty, file-cardinality effects, failure taxonomy, self-repair, augmentation robustness, and pass@k.
- A compact related-work section and a combined discussion/limitations/conclusion.

## What Moved To The Appendix

- Full framework details: spec schema, condensed spec listing, augmentation level definitions, and prompt anonymization.
- Full API-selection evidence: repository/API co-occurrence, kernel-level API network, API exclusion rationale, and OpenMP-target case-study rationale.
- Full benchmark curation details: repository inventory, quality tiers, HeCBench selection funnel, Rodinia inventory, extra suite profiles, and exclusion log.
- Extended related-work comparison table and detailed positioning.
- Detailed evaluation support: repair transition matrices, per-direction repair rates, augmentation transform frequencies, multi-file case study, model/hardware tables, API characteristics, augmentation/pass@k/statistical tables, full per-kernel results, prompt template, GPT figures, and cost summary.

## Wording And Coherence Changes

- Reframed claims about augmentation as evidence against monotonic surface-form degradation, while preserving the power limitation and avoiding proof-of-invariance language.
- Reframed build failures as incomplete API adaptation rather than a simple syntax-vs-reasoning dichotomy.
- Kept the repository-level comparison but clarified that kernel isolation reveals capability; it does not make all kernels easy.
- Reconciled the main text around the current GPT-4.1 mini totals used in the manuscript body: 177/577 primary tasks, 30.7% [27.1%, 34.6%].
- Kept performance/efficiency explicitly out of scope and preserved KNOWN_FAIL/platform caveats.

## Compile And Page Notes

- Compiled with `tectonic --keep-logs --keep-intermediates main_neurips.tex`.
- The produced PDF is `main_neurips.pdf`.
- The log has no undefined references, undefined citations, duplicate LaTeX labels, or overfull boxes.
- The main body reaches the discussion on page 8; references precede the appendix, and Appendix A starts on page 10. This puts the core narrative at approximately the requested 8-page body before references.
- Remaining warnings are non-fatal underfull boxes, a `lineno.sty` UTF-8 warning from the style dependency, and Tectonic rerun/object warnings that did not indicate broken references or citations.

## Move Log

| Original section/item | Action taken | New location | Rationale |
|---|---|---|---|
| Long abstract/comments in `main.tex` | Rewritten compactly | `main_neurips.tex` abstract | Make abstract conference-style while preserving core numbers and caveats |
| Long introduction and gap exposition | Compressed and reorganized | Main Introduction | Preserve motivation, gap, contributions, and findings without SC-style buildup |
| Related-work catalog | Condensed in main; expanded moved | Main Related Work; Appendix `Extended Related Work` | Keep positioning self-contained while moving detailed comparison out of body |
| Full spec schema explanation and listing | Summarized in main; listing moved | Appendix `Framework and Evaluation Details` | Main needs concept, appendix holds reproducibility detail |
| Prompt structure and anonymization details | Summarized in main; full template moved | Appendix `Translation Prompt Template` | Important for trust but too detailed for main |
| Harness implementation minutiae | Compressed | Main Overview; Appendix framework/setup material | Keep build-run-verify semantics visible without artifact-documentation depth |
| API survey heatmaps/network and exclusion rationale | Moved | Appendices `API Selection Rationale` and `Benchmark Curation Details` | Supports survey-grounded selection without crowding main |
| HeCBench funnel, Rodinia inventory, exclusion log | Moved | Appendix benchmark curation sections | Detailed curation evidence belongs in appendix |
| Corpus summary | Kept compact | Main Table `Evaluation corpus` | Load-bearing for understanding benchmark scale |
| Model/hardware/software tables | Moved | Appendix Tables `model-config`, `hardware` | Needed for reproducibility, not first-pass narrative |
| Overall result table | Kept | Main Results | Central empirical evidence |
| Direction breakdown | Kept compact | Main Table `direction-rates` | Direction dependence is a primary finding |
| Full per-kernel table | Moved; representative table retained | Main representative table; Appendix full per-kernel table | Main shows difficulty tiers; appendix preserves exhaustive data |
| Failure taxonomy figure and explanation | Kept compact | Main Failure Modes | Dominant bottleneck is a core finding |
| Repair transition details | Moved | Appendix Tables/Figures on self-repair | Main keeps headline improvement; appendix keeps mechanics |
| Augmentation robustness table/heatmap | Moved; headline retained | Main robustness subsection; Appendix augmentation table/figures | Main needs trend result; appendix holds detailed rates |
| pass@k curve/table | Moved; headline retained | Main sampling paragraph; Appendix pass@k table/figure | Sampling result is important but full curve is secondary |
| Cross-suite and GPT-specific figures | Moved | Appendix GPT figures and cross-suite figure | Useful supporting views, not load-bearing main evidence |
| Multi-file case study | Moved; summary added | Main file-coordination subsection; Appendix multi-file case study | Makes coordination difficulty visible without long example |
| Cost/token accounting | Moved | Appendix cost summary | Artifact detail, not main scientific narrative |
| Discussion/threats/future-work list | Compressed | Main Discussion, Limitations, and Conclusion | Preserve limitations and next-step space without long catalog |
