# VibeCodeHPC2025

## Bib Entry

```bibtex
@misc{VibeCodeHPC2025,
  author    = {Shun-ichiro Hayashi and Koki Morita and Daichi Mukunoki and
               Tetsuya Hoshino and Takahiro Katagiri},
  title     = {{VibeCodeHPC}: An Agent-Based Iterative Prompting Auto-Tuner for {HPC} Code Generation Using {LLMs}},
  year      = {2025},
  eprint    = {2510.00031},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SE},
  url       = {https://arxiv.org/abs/2510.00031},
}
```

## Verification

- Existence: YES
- Verifying URL: https://arxiv.org/abs/2510.00031
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:495 — SUPPORTS — VibeCodeHPC~\cite{VibeCodeHPC2025} & Agentic HPC code generation/tuning; application/kernel level & Small local HPC benchmark set with build/run/performance signals & Agentic generation and optimization, not existing-kernel API translation.
- appendices_neurips.tex:568 — SUPPORTS — Later LLM-based systems for automatic parallelization, porting, and HPC code modeling continued this pattern, evaluating on paper-specific mixtures of OpenMP, MPI, CUDA, mini-applications, or benchmark-suite kernels~\cite{OMPar2024,AutoParLLM2025,OpenMPAssessment2024,HPCCoder2024,HPCCoderV2,LargeLLMEvalHPC2024,ChatMPI2026,VibeCodeHPC2025}.
- appendices_neurips.tex:577 — SUPPORTS — UniPar, QiMeng-MuPa, VibeCodeHPC, and ParaCodex similarly explore multi-paradigm generation, sequential-to-parallel transformation, agentic HPC code generation, or profiling-guided repair using local or mixed benchmark suites~\cite{UniPar2025,QiMengMuPa2025,VibeCodeHPC2025,ParaCodex2026}.
- sections/related-work.tex:14 — SUPPORTS — VibeCodeHPC~\cite{VibeCodeHPC2025} focuses on HPC code generation, while QiMeng-MuPa~\cite{QiMengMuPa2025} addresses sequential-to-parallel translation via mutual-supervised learning; neither targets cross-API translation of existing parallel implementations.
