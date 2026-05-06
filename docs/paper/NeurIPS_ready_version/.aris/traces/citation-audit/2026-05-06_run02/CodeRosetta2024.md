# CodeRosetta2024

## Bib Entry

```bibtex
@inproceedings{CodeRosetta2024,
  author    = {Ali TehraniJamsaz and Arijit Bhattacharjee and Le Chen and
               Nesreen K. Ahmed and Amir Yazdanbakhsh and Ali Jannesari},
  title     = {{CodeRosetta}: Pushing the Boundaries of Unsupervised Code
               Translation for Parallel Programming},
  booktitle = {Advances in Neural Information Processing Systems 37 ({NeurIPS})},
  year      = {2024},
  doi       = {10.52202/079017-3202},
  url       = {https://openreview.net/forum?id=V6hrg4O9gg},
}
```

## Verification

- Existence: YES
- Verifying URL: https://openreview.net/forum?id=V6hrg4O9gg
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:445 — SUPPORTS — CodeRosetta~\cite{CodeRosetta2024} & Parallel code translation and fine-tuning; function/kernel level & Model-specific C++/CUDA corpus with compile/similarity/local checks & Relevant translation work, but lacks fixed multi-API executable specifications.
- appendices_neurips.tex:577 — SUPPORTS — CodeRosetta and HPC-Coder-style models demonstrate the value of domain-specific corpora and model adaptation for HPC and parallel code~\cite{CodeRosetta2024,HPCCoder2024,HPCCoderV2}.
- appendices_neurips.tex:580 — SUPPORTS — Some works report prediction accuracy, pragma classification, compilation success, similarity, or pass@$k$ on task-specific checks~\cite{LearningToParallelize2023,OMPify2023,CodeRosetta2024,HPCCoderV2}.
- sections/framework.tex:77 — SUPPORTS — For example, a CUDA translation of Gaussian elimination compiles, runs to completion with exit code zero, and produces partial stdout---but omits the expected timing summary, indicating a systematic translation defect that compile-only (\cite{CodeRosetta2024}) or exit-code-only verification would miss.
- sections/related-work.tex:20 — SUPPORTS — CodeRosetta~\cite{CodeRosetta2024} and HPC-Coder-V2~\cite{HPCCoderV2} demonstrate specialized fine-tuning for parallel code; ParaCodex~\cite{ParaCodex2026} introduces profiling-guided agentic translation.
