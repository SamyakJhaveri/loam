# mixbench2017

## Bib Entry

```bibtex
@Article{mixbench2017,
  author    = {Elias Konstantinidis and Yiannis Cotronis},
  journal   = {Journal of Parallel and Distributed Computing},
  title     = {A quantitative roofline model for {GPU} kernel performance estimation using micro-benchmarks and hardware metric profiling},
  year      = {2017},
  pages     = {37--56},
  volume    = {107},
  doi       = {10.1016/j.jpdc.2017.04.002},
  url       = {https://doi.org/10.1016/j.jpdc.2017.04.002},
  publisher = {Elsevier},
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1016/j.jpdc.2017.04.002
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:1053 — SUPPORTS — \textbf{mixbench}~\cite{mixbench2017} (3~specs: CUDA, OpenMP, OpenCL): A micro-benchmark that sweeps a range of compute-to-memory operation ratios, mapping the practical roofline boundary of a compute device.
- sections/benchmark-curation.tex:35 — SUPPORTS — \textbf{XSBench}~\cite{XSBench2014} and \textbf{RSBench}~\cite{RSBench2014} contribute nuclear-physics proxy kernels, each with 4~specs, while \textbf{mixbench}~\cite{mixbench2017} contributes 3~GPU roofline micro-benchmark specs.
