# Rodinia2009

## Bib Entry

```bibtex
@inproceedings{Rodinia2009,
  author    = {Shuai Che and Michael Boyer and Jiayuan Meng and David Tarjan and
               Jeremy W. Sheaffer and Sang-Ha Lee and Kevin Skadron},
  title     = {{Rodinia}: A Benchmark Suite for Heterogeneous Computing},
  booktitle = {2009 {IEEE} International Symposium on Workload Characterization
               ({IISWC})},
  pages     = {44--54},
  year      = {2009},
  publisher = {IEEE},
  doi       = {10.1109/IISWC.2009.5306797},
  url       = {https://doi.org/10.1109/IISWC.2009.5306797},
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1109/IISWC.2009.5306797
- Metadata: correct
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:1031 — SUPPORTS — Rodinia~\cite{Rodinia2009} provides the foundation of \parbench{}'s evaluation corpus.
- appendices_neurips.tex:2113 — SUPPORTS — } The five suites are well-established in HPC research (Rodinia: IISWC 2009~\cite{Rodinia2009}, HeCBench: 2023~\cite{HeCBench2023}, XSBench: ANL~\cite{XSBench2014}).
- appendices_neurips.tex:2521 — SUPPORTS — \item[] Answer: \answerYes{} \item[] Justification: All five benchmark suites are cited (Rodinia~\cite{Rodinia2009}, XSBench, RSBench, mixbench, HeCBench).
- sections/benchmark-curation.tex:34 — SUPPORTS — \textbf{Rodinia}~\cite{Rodinia2009} is the largest contributor, providing 60~specs across 22~kernels over CUDA, OpenMP, and OpenCL; 53 pass baseline verification and 7 are \knownfail{}.
- sections/framework.tex:48 — SUPPORTS — Widely used suites such as Rodinia~\cite{Rodinia2009} are likely present in LLM training data, so success on unmodified source may reflect memorization.
