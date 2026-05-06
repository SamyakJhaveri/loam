# QiMengMuPa2025

## Bib Entry

```bibtex
@misc{QiMengMuPa2025,
  author    = {Changxin Ke and Rui Zhang and Shuo Wang and Li Ding and
               Guangli Li and Yuanbo Wen and Shuoming Zhang and Ruiyuan Xu and
               Jin Qin and Jiaming Guo and Chenxi Wang and Ling Li and
               Qi Guo and Yunji Chen},
  title     = {{QiMeng-MuPa}: Mutual-Supervised Learning for Sequential-to-Parallel
               Code Translation},
  year      = {2025},
  eprint    = {2506.11153},
  archivePrefix = {arXiv},
  primaryClass  = {cs.SE},
  howpublished = {arXiv preprint arXiv:2506.11153},
  doi       = {10.48550/arXiv.2506.11153},
  url       = {https://arxiv.org/abs/2506.11153},
}
```

## Verification

- Existence: YES
- Verifying URL: https://arxiv.org/abs/2506.11153
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:470 — SUPPORTS — QiMeng-MuPa~\cite{QiMengMuPa2025} & Sequential-to-parallel translation; task/program level & Curated training/evaluation corpus with local correctness checks & Related parallelization/translation work, but different from API-to-API translation of existing kernels.
- appendices_neurips.tex:577 — SUPPORTS — UniPar, QiMeng-MuPa, VibeCodeHPC, and ParaCodex similarly explore multi-paradigm generation, sequential-to-parallel transformation, agentic HPC code generation, or profiling-guided repair using local or mixed benchmark suites~\cite{UniPar2025,QiMengMuPa2025,VibeCodeHPC2025,ParaCodex2026}.
- sections/related-work.tex:14 — SUPPORTS — VibeCodeHPC~\cite{VibeCodeHPC2025} focuses on HPC code generation, while QiMeng-MuPa~\cite{QiMengMuPa2025} addresses sequential-to-parallel translation via mutual-supervised learning; neither targets cross-API translation of existing parallel implementations.
