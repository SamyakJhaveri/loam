# Handoff: GPT-5.4 Ablation Launch + Methodology Doc

**Date:** 2026-04-26
**From:** Research advisor session (Samyak + Claude)
**To:** Fresh Claude Code execution session
**Priority:** High — ablation launch is time-sensitive (NeurIPS deadline May 1)

---

## What You Need to Do (5 tasks, in order)

1. **Commit + push** the GPT-5.4 canonical eval results (426 JSON files + L0 passers derivation)
2. **Write** a literature-grounded methodology defense document (`docs/eval-findings/ablation-methodology.md`) explaining why ParBench ablation uses pass@1, not pass@3
3. **Commit + push** that document
4. **Launch** the GPT-5.4 ablation study (Phase C) in tmux
5. **Monitor** the ablation run every 4 minutes until completion

---

## Background (read this first)

### What is ParBench?

ParBench is a benchmark for evaluating how well LLMs can translate parallel code between CUDA, OpenMP, and OpenCL. We have 87 curated kernel specs across 5 benchmark suites (Rodinia, XSBench, RSBench, mixbench, HeCBench).

### The Experiment Design (NeurIPS 2026)

We run two phases per model:

- **Canonical (Phase A):** Tests baseline translation ability. pass@3 (3 samples per cell), L0 (no source augmentation), temp=0.7. This gives us the headline "how good is this model?" number.
- **Ablation (Phase C):** Tests robustness to source code augmentation. pass@1 (1 sample per cell), L1-L4 (4 augmentation levels), temp=0.7. Only runs on cells that passed L0 in canonical. This tells us "how fragile is the model when source code is perturbed?"

Between them is **Phase B (derive):** a script that reads canonical results and outputs the list of L0-passer cells for ablation.

### Current Status

| Phase | Qwen 3.5 397B | GPT-5.4 |
|-------|--------------|---------|
| A: Canonical | DONE (504 results, 36.7% pass) | DONE (426 results, 62.7% pass) |
| B: Derive | DONE (51 L0-passer cells) | DONE (99 L0-passer cells) |
| C: Ablation | DONE (204 results, 378 min) | **NOT STARTED — your job** |

### Why pass@1 for ablation? (the core research finding)

We researched 10 papers in the code generation evaluation literature (Chen et al. 2021/Codex, AlphaCode, ParEval, HPC-Coder-v2, ReCode, CodeFort, EvalPlus, TransCoder, CodeRosetta, LASSI). **Every single one uses pass@1 for ablation studies.** No paper uses pass@3.

The methodological reasons:
1. Ablations measure "does augmentation hurt?" (component contribution) — not "can the model ever succeed?" (capability ceiling). pass@1 is the right metric for the former.
2. pass@3 at temp=0.7 conflates two effects: the augmentation's impact AND the sampling diversity benefit of taking the best of 3 tries. This masks the signal you're trying to measure.
3. The comparison is apples-to-apples: pass@1 at L0 (derived from the first canonical sample, which we already have) vs pass@1 at L1-L4. Clean paired design.

The methodology doc you'll write captures this research with citations, statistical power analysis, and pre-written reviewer defense points.

---

## Detailed Execution Plan

The full step-by-step plan with exact commands, file paths, and verification checks is at:

**`/home/samyak/.claude/plans/check-the-status-of-cryptic-mitten.md`**

Read that file and follow it step by step. Below is a summary of the key points.

### Critical Project Rules

- **Venv:** Always `source /home/samyak/Desktop/parbench_sam/env_parbench/bin/activate` before Python
- **`python3` always**, never `python`
- **`/validate` before every commit** — pre-commit hook blocks without waves 1-3 passing
- **Codex review before every commit** — `touch .codex_review_done` at minimum
- **Result JSONs are immutable** — never modify existing files in `results/evaluation/`
- **No GSD commands** — this project no longer uses the GSD workflow
- **`git push origin main` works** — only `git push --force` is blocked

### Key File Paths

| File | What it is |
|------|-----------|
| `/home/samyak/Desktop/parbench_sam/results/evaluation/azure-gpt-5.4/` | 426 canonical result JSONs (uncommitted) |
| `/home/samyak/Desktop/parbench_sam/.planning/eval-selections/l0_passers_azure_gpt_5_4.json` | 99 L0-passer cells (uncommitted) |
| `/home/samyak/Desktop/parbench_sam/results/evaluation/eval_summary.json` | Updated eval summary (modified) |
| `/home/samyak/Desktop/parbench_sam/results/evaluation/eval_summary.md` | Updated eval summary markdown (modified) |
| `/home/samyak/Desktop/parbench_sam/docs/eval-findings/ablation-methodology.md` | Methodology doc to CREATE |
| `/home/samyak/Desktop/parbench_sam/scripts/batch/run_phase3.sh` | Phase 3 launcher script |
| `/home/samyak/Desktop/parbench_sam/docs/neurips2026-experiment-plan.md` | Authoritative experiment design (reference only) |

### Cost & Time for Ablation

| Metric | Value |
|--------|-------|
| API calls | 396 (99 cells × 4 augmentation levels) |
| Time | 10-15 hours (based on GPT-5.4 canonical: 2.3 min/result) |
| Cost | ~$124 (396 × $0.3125/sample at Azure pricing) |

### Skills to Use

| Skill | When | Purpose |
|-------|------|---------|
| `/validate` | Before each commit | Mandatory pre-commit validation |
| `/citation-audit` | After writing the methodology doc | Verify paper citations are real |
| `/loop 4m` | After launching ablation | Monitor every 4 minutes |
| `andrej-karpathy-skills:karpathy-guidelines` | During doc writing | Writing quality guidelines |

### Monitoring Protocol

After launching the ablation, use `/loop 4m` to check every 4 minutes:
- Count ablation results (target: 396)
- Check for done marker at `results/evaluation/azure-gpt-5_4_ablation_done.marker`
- Watch for 5+ consecutive API errors → kill + alert
- Use absolute paths in all monitoring commands (agent threads may reset cwd)

---

## What Success Looks Like

When you're done, the following should be true:

1. Two new commits on `main`, pushed to origin:
   - `data: GPT-5.4 canonical eval results (267/426 PASS, 62.7%) + L0 passer derivation (99 cells)`
   - `docs: ablation methodology defense with literature survey (10 papers)`
2. `docs/eval-findings/ablation-methodology.md` exists with 6 sections, 10 paper citations, statistical power analysis, and reviewer defense Q&A
3. tmux session `phase3-ablation` is running with the GPT-5.4 ablation
4. Monitoring loop is active, checking every 4 minutes
5. Results are accumulating in `results/evaluation/azure-gpt-5.4/` (ablation files with `augment_level > 0`)
