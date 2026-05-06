# HumanEval2021

## Bib Entry

```bibtex
@misc{HumanEval2021,
  author    = {Mark Chen and Jerry Tworek and Heewoo Jun and Qiming Yuan and
               Henrique Ponde de Oliveira Pinto and Jared Kaplan and
               Harri Edwards and Yuri Burda and Nicholas Joseph and
               Greg Brockman and Alex Ray and Raul Puri and Gretchen Krueger and
               Michael Petrov and Heidy Khlaaf and Girish Sastry and
               Pamela Mishkin and Brooke Chan and Scott Gray and Nick Ryder and
               Mikhail Pavlov and Alethea Power and Lukasz Kaiser and
               Mohammad Bavarian and Clemens Winter and Philippe Tillet and
               Felipe Petroski Such and Dave Cummings and Matthias Plappert and
               Fotios Chantzis and Elizabeth Barnes and Ariel Herbert-Voss and
               William Hebgen Guss and Alex Nichol and Alex Paino and
               Nikolas Tezak and Jie Tang and Igor Babuschkin and Suchir Balaji and
               Shantanu Jain and William Saunders and Christopher Hesse and
               Andrew N. Carr and Jan Leike and Josh Achiam and Vedant Misra and
               Evan Morikawa and Alec Radford and Matthew Knight and
               Miles Brundage and Mira Murati and Katie Mayer and Peter Welinder and
               Bob McGrew and Dario Amodei and Sam McCandlish and Ilya Sutskever and
               Wojciech Zaremba},
  title     = {Evaluating Large Language Models Trained on Code},
  year      = {2021},
  eprint    = {2107.03374},
  archiveprefix = {arXiv},
  primaryclass  = {cs.LG},
  howpublished  = {arXiv preprint arXiv:2107.03374},
  doi           = {10.48550/arXiv.2107.03374},
  url           = {https://arxiv.org/abs/2107.03374},
}
```

## Verification

- Existence: YES
- Verifying URL: https://arxiv.org/abs/2107.03374
- Metadata: correct
- Verdict: KEEP

## Citation Uses

- appendices_neurips.tex:309 — SUPPORTS — HumanEval~\cite{HumanEval2021} & General code generation; function level & Public benchmark with unit tests & Establishes execution-based evaluation, but does not exercise parallel API semantics.
- appendices_neurips.tex:698 — SUPPORTS — } For pass@$k$, following \citet{HumanEval2021}, we use the unbiased estimator $1 - \binom{n-c}{k}/\binom{n}{k}$, where $c$ is the number of passing samples out of $n$~total.
- sections/1-introduction.tex:49 — SUPPORTS — Widely adopted code-generation benchmarks such as HumanEval and SWE-bench~\cite{HumanEval2021, SWEbench2024} are predominantly sequential and therefore do not exercise parallel programming semantics.
- sections/experimental-setup.tex:107 — SUPPORTS — } The primary metric is \textbf{pass@$k$}, using the unbiased estimator from \citet{HumanEval2021} with normal-approximation confidence intervals on the task-level mean.
- sections/related-work.tex:8 — SUPPORTS — HumanEval~\cite{HumanEval2021} and TransCoder~\cite{TransCoder2020} operate at function granularity, while SWE-bench~\cite{SWEbench2024} targets repository-level issue resolution—neither exercises GPU memory models, thread synchronization, or host-device coordination.
