# OMPify2023

## Bib Entry

```bibtex
@inproceedings{OMPify2023,
  author    = {Tal Kadosh and Nadav Schneider and Niranjan Hasabnis and
               Timothy Mattson and Yuval Pinter and Gal Oren},
  title     = {Advising {OpenMP} Parallelization via a Graph-Based Approach
               with Transformers},
  booktitle = {OpenMP: Advanced Task-Based, Device and Compiler Programming
               ({IWOMP} 2023)},
  series    = {Lecture Notes in Computer Science},
  volume    = {14114},
  pages     = {3--17},
  year      = {2023},
  publisher = {Springer},
  doi       = {10.1007/978-3-031-40744-4_1},
  url       = {https://doi.org/10.1007/978-3-031-40744-4_1},
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1007/978-3-031-40744-4_1
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:367 — SUPPORTS — OpenMP Graph Transformer~\cite{OMPify2023} & OpenMP parallelization advice; loop/region level & Curated OpenMP corpus with recommendation/classification metrics & Relevant to pragma advice, but not translation evaluation.
- appendices_neurips.tex:568 — SUPPORTS — Earlier OpenMP and MPI work constructed curated datasets for source-to-source parallelization, pragma recommendation, parallel-region classification, MPI API assistance, and domain-specific model training~\cite{LearningToParallelize2023,MPIRICAL2023,OMPify2023,OMPGPT2024,MPIrigen2024,MonoCoder2024,PragFormer2025,CuratedOpenMPDataset2026}.
- appendices_neurips.tex:580 — SUPPORTS — Some works report prediction accuracy, pragma classification, compilation success, similarity, or pass@$k$ on task-specific checks~\cite{LearningToParallelize2023,OMPify2023,CodeRosetta2024,HPCCoderV2}.
