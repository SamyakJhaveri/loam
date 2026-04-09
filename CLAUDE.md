# CLAUDE.md — ParBench

ParBench: benchmark for LLM-based parallel code translation (CUDA ↔ OpenMP ↔ OpenCL).

## Environment

- `python3` always, never `python`. Venv: `source env_parbench/bin/activate`
- Platform: `/home/samyak/` = Linux GPU machine, `/Users/samyakjhaveri/` = macOS dev
- `config/paths.json` has macOS paths. On Linux, project root = `/home/samyak/Desktop/parbench_sam`
- Linux NVIDIA HPC SDK 24.3 (non-standard):
  nvcc: `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc`
  CUDA/OpenCL: `/opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/{include,lib64}`

## Key Architecture

| Path | What it is |
|------|-----------|
| `specs/` | Kernel spec JSONs (`{suite}-{slug}-{api}.json`) |
| `manifest.jsonl` | Append-only kernel registry — never modify existing entries |
| `harness/` | Build→Run→Verify pipeline. Invoke: `python3 -m harness` |
| `c_augmentation/` | AST transforms (libclang). Tests: `pytest c_augmentation/test_transforms.py` |
| `scripts/evaluation/` | LLM eval pipeline (`run_eval_batch.py`, `llm_evaluate.py`) |
| `results/` | Immutable eval + augmentation result JSONs |
| `rodinia/rodinia-src/` | Git submodule (commit `9c10d3ea`) — **empty in worktrees** |
| `HeCBench-master/` | Gitignored but **cloned locally** (1874 benchmark dirs) — specs in `specs/hecbench-*.json` |

## Invariants

1. **`manifest.jsonl` is append-only** — never modify existing entries
2. **Result JSONs are immutable** — use `--resume` to skip existing
3. **Never run evaluations in worktrees** — submodules are empty there
4. **Never change spec run args** without reading the source's `argc` check first
5. **~15 `validate_schema.py --all` errors are expected** (phantom specs only — HeCBench **is** cloned locally) — do not fix
6. **8 KNOWN_FAIL specs** — exclude from eval batches (list in `known-issues.md`)

## Quality

- Read before editing. No partial implementations. Verify before reporting done.
- `ultrathink` for: architecture, eval pipeline, spec correctness, augmentation, published results.
- If unsure, say so explicitly — never guess silently.
- `/validate` before every commit. Pre-commit hook requires waves 1-3; wave 4 (self-critic/opus) is optional.
- **Model selection:** Use Opus for main work. Before commit/push: manually run `/model haiku` (faster, cheaper for transactional git ops).

## Conditional Rules (`.claude/rules/`, auto-loaded by file path)

| File | Triggers on | Key content |
|------|------------|-------------|
| `known-issues.md` | Always | KNOWN_FAIL list, build gotchas, spec status |
| `workflow.md` | Always | 6-stage workflow, agents, teams, anti-patterns |
| `spec-conventions.md` | `specs/`, `manifest.jsonl` | Naming, categories, run arg verification protocol |
| `evaluation.md` | `scripts/evaluation/` | `--suite` required, `--project-root` required, result schema |
| `augmentation.md` | `c_augmentation/`, `scripts/augmentation/` | `--project-root` required, transform bugs |
| `known-issues-archive.md` | `c_augmentation/`, `harness/`, `scripts/augmentation/`, `scripts/evaluation/`, `results/augmentation/`, `results/evaluation/`, `specs/`, `visualizations/` | Historical fix details, moved guardrails |
| `python.md` | `*.py` | `python3`, harness CLI flag ordering (`-v` before subcommand) |
| `validation-loop.md` | hooks, validation agents | 4-wave protocol (gate requires 1-3, wave 4 optional), sentinel, fix loop |
| `github-pages.md` | `visualizations/` | URL, staticrypt, data refresh |
| `frontend-design.md` | `visualizations/` | Design system, styling conventions |

<!-- GSD:project-start source:PROJECT.md -->
## Project

**SC26 Paper Completion Sprint**

A focused sprint to complete and strengthen the SC26 ParBench paper (`docs/paper/latex/paper.tex`) before the April 8, 2026 submission deadline. The paper presents ParBench, a build-run-verify benchmark framework for evaluating LLM-based parallel code translation across CUDA, OpenMP, and OpenCL. This sprint covers all tasks achievable with existing Qwen 3.5 397B evaluation data, focusing on pre-results sections (Sections 1-5) and quantitative rigor.

**Core Value:** Every data claim in the paper must be verifiable against actual result files on disk, and every methodology description must be precise enough to withstand SC-level peer review.

### Constraints

- **Deadline**: April 8, 2026 -- hard SC26 submission deadline
- **Data availability**: Only existing Qwen Rodinia data is complete; non-Rodinia and GPT data pending
- **Running evals**: Two tmux sessions MUST NOT be touched (qwen_hecbench, qwen_small)
- **Result immutability**: Never modify existing result JSONs
- **Page limit**: ~10 pages IEEE double-column format
- **Framing**: Benchmark paper, not model evaluation paper
- **HeCBench source**: Cloned locally (gitignored, 1874 dirs) — not a git submodule, so no version pinning
<!-- GSD:project-end -->

