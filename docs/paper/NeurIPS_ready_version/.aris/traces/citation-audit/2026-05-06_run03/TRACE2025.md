# TRACE2025

## Bib Entry

```bibtex
@misc{TRACE2025,
  author    = {Zhihao Gong and Zeyu Sun and Dong Huang and Qingyuan Liang and
               Jie M. Zhang and Dan Hao},
  title     = {{TRACE}: Evaluating Execution Efficiency of {LLM}-Based
               Code Translation},
  year      = {2025},
  eprint    = {2508.11468},
  archiveprefix = {arXiv},
  primaryclass  = {cs.SE},
  howpublished  = {arXiv preprint arXiv:2508.11468},
  doi = {10.48550/arXiv.2508.11468},
  url           = {https://arxiv.org/abs/2508.11468},
}
```

## Verification

- Existence: YES
- Verifying URL: https://arxiv.org/abs/2508.11468
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:528 — SUPPORTS — TRACE~\cite{TRACE2025} & Efficiency of LLM-based code translation; function/task level & Efficiency benchmark with correctness and runtime & Complementary performance axis; \parbench{} focuses first on correctness.
- appendices_neurips.tex:583 — SUPPORTS — TRACE, KernelBench, Mercury, and related GPU-kernel or efficiency benchmarks study runtime, kernel quality, optimization, or resource behavior~\cite{TRACE2025,KernelBench2025,Mercury2024}.
- appendices_neurips.tex:1955 — SUPPORTS — TRACE~\cite{TRACE2025} addresses this gap.
- sections/discussion.tex:10 — SUPPORTS — A harness-passing translation may still be unusably slow, a concern also raised by TRACE~\cite{TRACE2025}.
- sections/related-work.tex:23 — SUPPORTS — \parbench{} evaluates correctness only; efficiency-oriented work such as TRACE~\cite{TRACE2025} shows that functional correctness and runtime performance are separable objectives, making performance-aware evaluation a natural extension.
