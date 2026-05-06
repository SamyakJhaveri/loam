# LearningToParallelize2023

## Bib Entry

```bibtex
@inproceedings{LearningToParallelize2023,
  title = {{POSTER}: Learning to Parallelize in a Shared-Memory Environment with Transformers},
  author = {Harel, Re'em and Pinter, Yuval and Oren, Gal},
  booktitle = {Proceedings of the 28th ACM SIGPLAN Annual Symposium on Principles and Practice of Parallel Programming},
  pages = {450--452},
  publisher = {ACM},
  year = {2023},
  doi = {10.1145/3572848.3582565},
  url = {https://doi.org/10.1145/3572848.3582565}
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1145/3572848.3582565
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:357 — SUPPORTS — Learning to Parallelize~\cite{LearningToParallelize2023} & OpenMP parallelization prediction; loop/region level & Curated OpenMP training and evaluation corpus & Shows local corpus construction for OpenMP assistance, not executable cross-API translation.
- appendices_neurips.tex:568 — SUPPORTS — Earlier OpenMP and MPI work constructed curated datasets for source-to-source parallelization, pragma recommendation, parallel-region classification, MPI API assistance, and domain-specific model training~\cite{LearningToParallelize2023,MPIRICAL2023,OMPify2023,OMPGPT2024,MPIrigen2024,MonoCoder2024,PragFormer2025,CuratedOpenMPDataset2026}.
- appendices_neurips.tex:580 — SUPPORTS — Some works report prediction accuracy, pragma classification, compilation success, similarity, or pass@$k$ on task-specific checks~\cite{LearningToParallelize2023,OMPify2023,CodeRosetta2024,HPCCoderV2}.
