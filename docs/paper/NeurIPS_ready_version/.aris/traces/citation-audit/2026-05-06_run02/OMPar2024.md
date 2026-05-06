# OMPar2024

## Bib Entry

```bibtex
@misc{OMPar2024,
  title = {{OMPar}: Automatic Parallelization with AI-Driven Source-to-Source Compilation},
  author = {Kadosh, Tal and Hasabnis, Niranjan and Soundararajan, Prema and Vo, Vy A. and Capot{\u{a}}, Mihai and Ahmed, Nesreen K. and Pinter, Yuval and Oren, Gal},
  year = {2024},
  eprint = {2409.14771},
  archivePrefix = {arXiv},
  primaryClass = {cs.SE},
  howpublished = {arXiv preprint arXiv:2409.14771},
  doi = {10.48550/arXiv.2409.14771},
  url = {https://arxiv.org/abs/2409.14771}
}
```

## Verification

- Existence: YES
- Verifying URL: https://arxiv.org/abs/2409.14771
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:392 — SUPPORTS — OMPar~\cite{OMPar2024} & AI-driven OpenMP source-to-source parallelization; program/loop level & Paper-specific OpenMP evaluation set & Automatic parallelization rather than translation of existing parallel kernels.
- appendices_neurips.tex:568 — SUPPORTS — Later LLM-based systems for automatic parallelization, porting, and HPC code modeling continued this pattern, evaluating on paper-specific mixtures of OpenMP, MPI, CUDA, mini-applications, or benchmark-suite kernels~\cite{OMPar2024,AutoParLLM2025,OpenMPAssessment2024,HPCCoder2024,HPCCoderV2,LargeLLMEvalHPC2024,ChatMPI2026,VibeCodeHPC2025}.
- appendices_neurips.tex:571 — SUPPORTS — Automatic-parallelization systems such as OMPar, AutoParLLM, and related OpenMP-focused assessments measure yet another capability: identifying and introducing parallelism into serial or partially parallel code~\cite{OMPar2024,AutoParLLM2025,OpenMPAssessment2024}.
