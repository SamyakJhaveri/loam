# Wang2026RepoTransBench

## Bib Entry

```bibtex
@article{Wang2026RepoTransBench,
  author  = {Yanli Wang and Yanlin Wang and Suiquan Wang and Daya Guo and Jiachi Chen and John Grundy and Xilin Liu and Yuchi Ma and Mingzhi Mao and Hongyu Zhang and Zibin Zheng},
  title   = {{RepoTransBench}: A Real-World Multilingual Benchmark for Repository-Level Code Translation},
  journal = {IEEE Transactions on Software Engineering},
  volume  = {52},
  number  = {2},
  pages   = {675--690},
  year    = {2026},
  doi     = {10.1109/TSE.2025.3645056}
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1109/TSE.2025.3645056
- Metadata: correct
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:324 — SUPPORTS — RepoTransBench~\cite{Wang2026RepoTransBench} & Repository-level code translation & Public repository benchmark with build/test signals & Shows repository translation complexity, but confounds kernel translation with scaffolding.
- appendices_neurips.tex:574 — SUPPORTS — SWE-bench and RepoTransBench demonstrate the importance of repository-level executable evaluation in general software settings~\cite{SWEbench2024,Wang2026RepoTransBench}, while ParEval-Repo shows that full-repository HPC translation can be dominated by build-system and scaffolding failures~\cite{ParEvalRepo2025}.
- sections/1-introduction.tex:49 — SUPPORTS — Repository-level translation work exposes important integration challenges, but it also entangles kernel translation with build-system reconstruction, file organization, dependency management, and execution setup~\cite{ParEvalRepo2025,Wang2026RepoTransBench}\footnote{An extended comparison with code-generation benchmarks, repository-level translation studies, HPC-specific LLM evaluation, and robustness benchmarks in Appendix~\ref{sec:appendix-d}.
- sections/related-work.tex:14 — SUPPORTS — ParEval-Repo~\cite{ParEvalRepo2025} and RepoTransBench~\cite{Wang2026RepoTransBench} study full-repository translation and reveal a severe integration bottleneck at build systems and scaffolding.
