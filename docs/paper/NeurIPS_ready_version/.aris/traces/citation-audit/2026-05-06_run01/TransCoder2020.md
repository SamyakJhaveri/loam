# TransCoder2020

## Bib Entry

```bibtex
@inproceedings{TransCoder2020,
  author    = {Baptiste Rozi{\`e}re and Marie-Anne Lachaux and Lo{\"i}k Chanussot and
               Guillaume Lample},
  title     = {Unsupervised Translation of Programming Languages},
  booktitle = {Advances in Neural Information Processing Systems 33 ({NeurIPS})},
  year      = {2020},
  doi       = {10.5555/3495724.3497454},
  url       = {https://proceedings.neurips.cc/paper/2020/hash/ed23fbf18c2cd35f8c7f8de44f85c08d-Abstract.html},
}
```

## Verification

- Existence: YES
- Verifying URL: https://proceedings.neurips.cc/paper/2020/hash/ed23fbf18c2cd35f8c7f8de44f85c08d-Abstract.html
- Metadata: correct
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:314 — SUPPORTS — TransCoder~\cite{TransCoder2020} & General source-to-source translation; function level & Public multilingual corpus with unit tests & Provides a code-translation precedent, but not for HPC or parallel APIs.
- sections/related-work.tex:8 — SUPPORTS — HumanEval~\cite{HumanEval2021} and TransCoder~\cite{TransCoder2020} operate at function granularity, while SWE-bench~\cite{SWEbench2024} targets repository-level issue resolution—neither exercises GPU memory models, thread synchronization, or host-device coordination.
