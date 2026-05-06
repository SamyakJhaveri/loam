# ParEval2024

## Bib Entry

```bibtex
@inproceedings{ParEval2024,
  author    = {Daniel Nichols and Joshua H. Davis and Zhaojun Xie and
               Arjun Rajaram and Abhinav Bhatele},
  title     = {Can Large Language Models Write Parallel Code?},
  booktitle = {Proceedings of the 33rd International Symposium on
               High-Performance Parallel and Distributed Computing ({HPDC})},
  pages     = {281--294},
  year      = {2024},
  publisher = {ACM},
  doi       = {10.1145/3625549.3658689},
  url       = {https://doi.org/10.1145/3625549.3658689},
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1145/3625549.3658689
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:407 — SUPPORTS — ParEval~\cite{ParEval2024} & Parallel code generation with limited translation settings; task level & Public benchmark with correctness checks & Includes generation and some translation settings, but not \parbench{}'s fixed executable kernel corpus or broader cross-API direction coverage.
- appendices_neurips.tex:571 — SUPPORTS — } Parallel code generation benchmarks such as ParEval and PCEBench ask whether a model can synthesize a parallel program from a natural-language description, and ParEval also includes limited translation settings~\cite{ParEval2024,PCEBench2025}.
- sections/1-introduction.tex:49 — SUPPORTS — Parallel code-generation benchmarks such as ParEval~\cite{ParEval2024} primarily evaluate synthesis from natural-language descriptions, rather than translation of existing implementations across APIs.
- sections/related-work.tex:14 — SUPPORTS — } ParEval~\cite{ParEval2024} combines parallel code generation with limited translation settings, while PCEBench~\cite{PCEBench2025} emphasizes synthesis from natural-language descriptions.
