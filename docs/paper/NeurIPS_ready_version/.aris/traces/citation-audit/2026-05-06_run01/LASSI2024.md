# LASSI2024

## Bib Entry

```bibtex
@inproceedings{LASSI2024,
  author    = {Matthew T. Dearing and Yiheng Tao and Xingfu Wu and
               Zhiling Lan and Valerie Taylor},
  title     = {{LASSI}: An {LLM}-Based Automated Self-Correcting Pipeline
               for Translating Parallel Scientific Codes},
  booktitle = {2024 {IEEE} International Conference on Cluster Computing
               Workshops ({CLUSTER} Workshops)},
  pages     = {136--143},
  year      = {2024},
  publisher = {IEEE},
  doi       = {10.1109/CLUSTERWorkshops61563.2024.00029},
  url       = {https://doi.org/10.1109/CLUSTERWorkshops61563.2024.00029},
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1109/CLUSTERWorkshops61563.2024.00029
- Metadata: correct
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:440 — SUPPORTS — LASSI~\cite{LASSI2024} & Agentic parallel-code translation; kernel level & Curated HeCBench subset with build-run-verify & Closest in verification style, but smaller in scope and focused on iterative repair.
- appendices_neurips.tex:577 — SUPPORTS — LASSI evaluates an automated self-correcting pipeline for parallel scientific-code translation on a curated HeCBench subset~\cite{LASSI2024}.
- appendices_neurips.tex:580 — SUPPORTS — Others incorporate build, run, and functional validation, especially in agentic or repository-level settings~\cite{LASSI2024,ParEvalRepo2025,ParaCodex2026}.
- sections/related-work.tex:20 — SUPPORTS — } LASSI~\cite{LASSI2024} is the nearest prior work in granularity and verification, evaluating an agentic self-correction pipeline on 10 HeCBench kernels across two translation directions.
