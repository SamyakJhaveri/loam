# ParEvalRepo2025

## Bib Entry

```bibtex
@inproceedings{ParEvalRepo2025,
  author    = {Joshua H. Davis and Daniel Nichols and Ishan Khillan and
               Abhinav Bhatele},
  title     = {On the Limits of {LLM}-Based Repository-Level {HPC} Code
               Translation},
  booktitle = {Proceedings of the 54th International Conference on Parallel
               Processing ({ICPP})},
  pages     = {94--103},
  year      = {2025},
  publisher = {ACM},
  doi       = {10.1145/3754598.3754669},
  url       = {https://doi.org/10.1145/3754598.3754669},
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1145/3754598.3754669
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:460 — SUPPORTS — ParEval-Repo~\cite{ParEvalRepo2025} & Repository-level HPC translation & Public HPC repository benchmark with build and functional tests & Motivates \parbench{} by showing that repository integration can dominate failures.
- appendices_neurips.tex:574 — SUPPORTS — SWE-bench and RepoTransBench demonstrate the importance of repository-level executable evaluation in general software settings~\cite{SWEbench2024,Wang2026RepoTransBench}, while ParEval-Repo shows that full-repository HPC translation can be dominated by build-system and scaffolding failures~\cite{ParEvalRepo2025}.
- appendices_neurips.tex:580 — SUPPORTS — Others incorporate build, run, and functional validation, especially in agentic or repository-level settings~\cite{LASSI2024,ParEvalRepo2025,ParaCodex2026}.
- appendices_neurips.tex:1982 — SUPPORTS — \ ParEval-Repo~\cite{ParEvalRepo2025}).
- appendices_neurips.tex:2104 — SUPPORTS — \ ParEval-Repo's 0\% at $>$133~SLoC~\cite{ParEvalRepo2025}).
- sections/1-introduction.tex:49 — SUPPORTS — Repository-level translation work exposes important integration challenges, but it also entangles kernel translation with build-system reconstruction, file organization, dependency management, and execution setup~\cite{ParEvalRepo2025,Wang2026RepoTransBench}\footnote{An extended comparison with code-generation benchmarks, repository-level translation studies, HPC-specific LLM evaluation, and robustness benchmarks in Appendix~\ref{sec:appendix-d}.
- sections/benchmark-curation.tex:40 — SUPPORTS — Kernel complexity spans more than an order of magnitude---80 to 3{,}304~SLoC, median 271---and 31 of 35 kernels (89\%) exceed the 133-SLoC scale at which prior repository-level translation reports 0\% pass@1~\cite{ParEvalRepo2025}.
- sections/framework.tex:56 — SUPPORTS — This separation isolates parallel API translation from repository reconstruction---the confound that drives ParEval-Repo's 0\% pass rate on applications above 133~SLoC~\cite{ParEvalRepo2025}.
- sections/related-work.tex:14 — SUPPORTS — ParEval-Repo~\cite{ParEvalRepo2025} and RepoTransBench~\cite{Wang2026RepoTransBench} study full-repository translation and reveal a severe integration bottleneck at build systems and scaffolding.
- sections/results.tex:60 — SUPPORTS — Prior work such as ParEval-Repo reports 0\% pass@1 on repository-level applications larger than 133~SLoC~\cite{ParEvalRepo2025}; 89\% of our kernels exceed that threshold, yet \parbench{}'s kernel isolation enables \qwenshort{} to achieve 40.
