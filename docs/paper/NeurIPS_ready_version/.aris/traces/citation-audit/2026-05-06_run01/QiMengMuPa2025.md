# QiMengMuPa2025

## Bib Entry

```bibtex
@inproceedings{QiMengMuPa2025,
  author    = {Changxin Ke and Rui Zhang and Shuo Wang and Li Ding and
               Guangli Li and Yuanbo Wen and Shuoming Zhang and Ruiyuan Xu and
               Jin Qin and Jiaming Guo and Chenxi Wang and Ling Li and
               Qi Guo and Yunji Chen},
  title     = {{QiMeng-MuPa}: Mutual-Supervised Learning for Sequential-to-Parallel
               Code Translation},
  booktitle = {Advances in Neural Information Processing Systems 38 ({NeurIPS})},
  year      = {2025},
  eprint    = {2506.11153},
  archivePrefix = {arXiv},
  primaryClass  = {cs.AI},
  url       = {https://arxiv.org/abs/2506.11153},
}
```

## Verification

- Existence: YES
- Verifying URL: https://dblp.org/rec/journals/corr/abs-2506-11153.html
- Metadata: wrong/needs update: Verified as arXiv preprint 2506.11153 / "QiMeng-MuPa"; no published NeurIPS proceedings record was found, so the inproceedings metadata should be replaced with an arXiv-style entry.
- Verdict: FIX

## Citation Uses

- appendices_neurips.tex:470 — SUPPORTS — QiMeng-MuPa~\cite{QiMengMuPa2025} & Sequential-to-parallel translation; task/program level & Curated training/evaluation corpus with local correctness checks & Related parallelization/translation work, but different from API-to-API translation of existing kernels.
- appendices_neurips.tex:577 — SUPPORTS — UniPar, QiMeng-MuPa, VibeCodeHPC, and ParaCodex similarly explore multi-paradigm generation, sequential-to-parallel transformation, agentic HPC code generation, or profiling-guided repair using local or mixed benchmark suites~\cite{UniPar2025,QiMengMuPa2025,VibeCodeHPC2025,ParaCodex2026}.
- sections/related-work.tex:14 — SUPPORTS — VibeCodeHPC~\cite{VibeCodeHPC2025} focuses on HPC code generation, while QiMeng-MuPa~\cite{QiMengMuPa2025} addresses sequential-to-parallel translation via mutual-supervised learning; neither targets cross-API translation of existing parallel implementations.

## Note

Verified as arXiv preprint 2506.11153 / "QiMeng-MuPa"; no published NeurIPS proceedings record was found, so the inproceedings metadata should be replaced with an arXiv-style entry.
