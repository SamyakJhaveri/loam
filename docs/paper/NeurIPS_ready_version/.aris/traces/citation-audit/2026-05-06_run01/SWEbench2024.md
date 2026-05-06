# SWEbench2024

## Bib Entry

```bibtex
@inproceedings{SWEbench2024,
  author    = {Carlos E. Jimenez and John Yang and Alexander Wettig and
               Shunyu Yao and Kexin Pei and Ofir Press and
               Karthik Narasimhan},
  title     = {{SWE-bench}: Can Language Models Resolve Real-World {GitHub}
               Issues?},
  booktitle = {Proceedings of the Twelfth International Conference on
               Learning Representations ({ICLR})},
  year      = {2024},
  url       = {https://openreview.net/forum?id=VTF8yNQM66},
}
```

## Verification

- Existence: YES
- Verifying URL: https://openreview.net/forum?id=VTF8yNQM66
- Metadata: correct
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:319 — SUPPORTS — SWE-bench~\cite{SWEbench2024} & Repository issue repair; repository level & Public GitHub-issue benchmark with repository tests & Demonstrates executable repository evaluation, but is mostly non-HPC and non-parallel.
- appendices_neurips.tex:574 — SUPPORTS — SWE-bench and RepoTransBench demonstrate the importance of repository-level executable evaluation in general software settings~\cite{SWEbench2024,Wang2026RepoTransBench}, while ParEval-Repo shows that full-repository HPC translation can be dominated by build-system and scaffolding failures~\cite{ParEvalRepo2025}.
- sections/1-introduction.tex:49 — SUPPORTS — Widely adopted code-generation benchmarks such as HumanEval and SWE-bench~\cite{HumanEval2021, SWEbench2024} are predominantly sequential and therefore do not exercise parallel programming semantics.
- sections/related-work.tex:8 — SUPPORTS — HumanEval~\cite{HumanEval2021} and TransCoder~\cite{TransCoder2020} operate at function granularity, while SWE-bench~\cite{SWEbench2024} targets repository-level issue resolution—neither exercises GPU memory models, thread synchronization, or host-device coordination.
