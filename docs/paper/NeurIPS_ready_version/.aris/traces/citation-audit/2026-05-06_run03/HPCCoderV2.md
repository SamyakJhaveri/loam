# HPCCoderV2

## Bib Entry

```bibtex
@inproceedings{HPCCoderV2,
  title = {{HPC-Coder-V2}: Studying Code {LLM}s Across Low-Resource Parallel Languages},
  author = {Chaturvedi, Aman and Nichols, Daniel and Singh, Siddharth and Bhatele, Abhinav},
  booktitle = {ISC High Performance 2025 Research Paper Proceedings},
  pages = {1--14},
  publisher = {IEEE},
  year = {2025},
  doi = {10.23919/ISC.2025.11017585},
  url = {https://doi.org/10.23919/ISC.2025.11017585}
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.23919/ISC.2025.11017585
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:455 — SUPPORTS — HPC-Coder-V2~\cite{HPCCoderV2} & Code LLMs across low-resource parallel languages; task level & Parallel-language tasks with pass@$k$ and task checks & Relevant to parallel-code LLMs, but not controlled executable kernel translation.
- appendices_neurips.tex:568 — SUPPORTS — Later LLM-based systems for automatic parallelization, porting, and HPC code modeling continued this pattern, evaluating on paper-specific mixtures of OpenMP, MPI, CUDA, mini-applications, or benchmark-suite kernels~\cite{OMPar2024,AutoParLLM2025,OpenMPAssessment2024,HPCCoder2024,HPCCoderV2,LargeLLMEvalHPC2024,ChatMPI2026,VibeCodeHPC2025}.
- appendices_neurips.tex:577 — SUPPORTS — CodeRosetta and HPC-Coder-style models demonstrate the value of domain-specific corpora and model adaptation for HPC and parallel code~\cite{CodeRosetta2024,HPCCoder2024,HPCCoderV2}.
- appendices_neurips.tex:580 — SUPPORTS — Some works report prediction accuracy, pragma classification, compilation success, similarity, or pass@$k$ on task-specific checks~\cite{LearningToParallelize2023,OMPify2023,CodeRosetta2024,HPCCoderV2}.
- sections/related-work.tex:20 — SUPPORTS — CodeRosetta~\cite{CodeRosetta2024} and HPC-Coder-V2~\cite{HPCCoderV2} demonstrate specialized fine-tuning for parallel code; ParaCodex~\cite{ParaCodex2026} introduces profiling-guided agentic translation.
