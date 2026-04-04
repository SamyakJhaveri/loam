---
date: "2026-04-04 05:22"
promoted: false
---

Multi-file translation targets (not kernel complexity) are the dominant predictor of failure in Qwen 3.5 397B evals. Rodinia controlled comparison: 48.5% pass rate for single-file targets vs 12.5% for multi-file targets (same model, same pipeline). RSBench/XSBench fail at 0% because their CUDA targets always require 2 files (simulation.cu+init.cu, Simulation.cu+GridInit.cu). RSBench OMP→CUDA is a code decomposition task (1 file → 2 files), not just translation — model must invent an architectural boundary. Paper framing: "multi-file translation requires architectural decomposition across file boundaries" not "model fails on complex kernels." Confirmed by adversarial agent review 2026-04-04.
