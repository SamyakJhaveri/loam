# ParaCodex2026

## Bib Entry

```bibtex
@misc{ParaCodex2026,
  title = {{ParaCodex}: A Profiling-Guided Autonomous Coding Agent for Reliable Parallel Code Generation and Translation},
  author = {Kaplan, Erel and Bitan, Tomer and Ghrayeb, Lian and Chen, Le and Yotam, Tom and Hasabnis, Niranjan and Oren, Gal},
  year = {2026},
  eprint = {2601.04327},
  archivePrefix = {arXiv},
  primaryClass = {cs.SE},
  howpublished = {arXiv preprint arXiv:2601.04327},
  doi = {10.48550/arXiv.2601.04327},
  url = {https://arxiv.org/abs/2601.04327}
}
```

## Verification

- Existence: YES
- Verifying URL: https://arxiv.org/abs/2601.04327
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:500 — SUPPORTS — ParaCodex~\cite{ParaCodex2026} & Profiling-guided agentic parallel generation/translation; kernel/program level & Curated suite mixture with build-run-verify and profiling feedback & Directly relevant method-side work; \parbench{} can evaluate such systems under fixed specs.
- appendices_neurips.tex:577 — SUPPORTS — UniPar, QiMeng-MuPa, VibeCodeHPC, and ParaCodex similarly explore multi-paradigm generation, sequential-to-parallel transformation, agentic HPC code generation, or profiling-guided repair using local or mixed benchmark suites~\cite{UniPar2025,QiMengMuPa2025,VibeCodeHPC2025,ParaCodex2026}.
- appendices_neurips.tex:580 — SUPPORTS — Others incorporate build, run, and functional validation, especially in agentic or repository-level settings~\cite{LASSI2024,ParEvalRepo2025,ParaCodex2026}.
- sections/related-work.tex:20 — SUPPORTS — CodeRosetta~\cite{CodeRosetta2024} and HPC-Coder-V2~\cite{HPCCoderV2} demonstrate specialized fine-tuning for parallel code; ParaCodex~\cite{ParaCodex2026} introduces profiling-guided agentic translation.
