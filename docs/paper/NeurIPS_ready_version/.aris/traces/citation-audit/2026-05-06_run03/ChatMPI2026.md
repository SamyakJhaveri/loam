# ChatMPI2026

## Bib Entry

```bibtex
@inproceedings{ChatMPI2026,
  title = {{ChatMPI}: {LLM}-Driven {MPI} Code Generation for {HPC} Workloads},
  author = {Valero-Lara, Pedro and Young, Aaron and Naughton, Thomas III and Engelmann, Christian and Geist, Al and Vetter, Jeffrey S. and Teranishi, Keita and Godoy, William F.},
  booktitle = {Proceedings of Supercomputing Asia and International Conference on High Performance Computing in Asia Pacific Region},
  pages = {19--30},
  publisher = {ACM},
  year = {2026},
  doi = {10.1145/3773656.3773659},
  url = {https://doi.org/10.1145/3773656.3773659}
}
```

## Verification

- Existence: YES
- Verifying URL: https://doi.org/10.1145/3773656.3773659
- Metadata: correct for the published-first policy used in this pass
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:485 — SUPPORTS — ChatMPI~\cite{ChatMPI2026} & MPI code generation; function/workload level & MPI-focused local evaluation with functional checks & Distributed-parallel generation, not cross-API kernel translation.
- appendices_neurips.tex:568 — SUPPORTS — Later LLM-based systems for automatic parallelization, porting, and HPC code modeling continued this pattern, evaluating on paper-specific mixtures of OpenMP, MPI, CUDA, mini-applications, or benchmark-suite kernels~\cite{OMPar2024,AutoParLLM2025,OpenMPAssessment2024,HPCCoder2024,HPCCoderV2,LargeLLMEvalHPC2024,ChatMPI2026,VibeCodeHPC2025}.
