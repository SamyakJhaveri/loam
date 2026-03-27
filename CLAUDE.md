# CLAUDE.md — ParBench

## Environment

- **Primary platform:** macOS (development, spec editing, analysis)
- **GPU platform:** Linux (Ubuntu, kernel 6.8, NVIDIA RTX 4070) — used for build/run/verify
- **Python:** 3.12.3 — always `python3`, never bare `python`
- **Venv:** `source env_parbench/bin/activate` (created on Linux — may need recreation on Mac)
- **Install packages:** `python3 -m pip install <pkg>` inside activated venv

## System Paths

### macOS (current development machine)
```
project_root:  /Users/samyakjhaveri/Desktop/parbench_sam
downloads_root: /Users/samyakjhaveri/Desktop/parbench_sam
```

### Linux (GPU machine — for build/run/verify only)
```
project_root:  /home/samyak/Desktop/parbench_sam
nvcc:          /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc
CUDA_DIR:      /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda
OPENCL_INC:    /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/include
OPENCL_LIB:    /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64
GPU:           NVIDIA GeForce RTX 4070
```

## config/paths.json

```json
{
    "project_root": "/Users/samyakjhaveri/Desktop/parbench_sam",
    "downloads_root": "/Users/samyakjhaveri/Desktop/parbench_sam",
    "hecbench_root": "/Users/samyakjhaveri/Desktop/parbench_sam/HeCBench-master"
}
```

`downloads_root` equals `project_root`. `source_dir` fields in `manifest.jsonl` are relative to `downloads_root`.

## Common Commands

```bash
# Validate all specs (120 HeCBench errors are expected — do not fix)
python3 scripts/validate_schema.py --all

# Validate one spec
python3 scripts/validate_schema.py --spec specs/<name>.json

# Harness — global flags (-v, --json) MUST come BEFORE the subcommand
python3 -m harness -v verify specs/rodinia-bfs-cuda.json
python3 -m harness --json verify specs/rodinia-bfs-cuda.json
python3 -m harness prompt specs/rodinia-bfs-cuda.json --augment_level 2

# Unit tests
python3 -m pytest c_augmentation/test_transforms.py -v

# Augment pipeline — ALWAYS pass --project-root (auto-detection broken)
python3 scripts/augmentation/augment_verify.py specs/<name>.json \
  --augment_level 2 --seed 42 -v \
  --project-root /home/samyak/Desktop/parbench_sam

# LLM Evaluation — ALWAYS pass --suite to avoid cross-suite name collisions
python3 scripts/evaluation/run_eval_batch.py \
  --suite rodinia --direction cuda-to-omp \
  --models claude-sonnet-4-20250514 \
  --project-root /home/samyak/Desktop/parbench_sam \
  --resume -v
```

## Project Layout

```
specs/              {suite}-{slug}-{api}.json per kernel-API variant
manifest.jsonl      append-only; never modify existing entries
schema/             spec_schema.json (v1.0.0), manifest_schema.json
scripts/
  validate_schema.py          top-level validator
  generators/                 spec generation scripts
  survey/                     codebase surveying scripts
  analysis/                   results analysis & reporting
  baselines/                  baseline population scripts
  augmentation/               augment_verify.py, run_augment_batch.py, combine_aug_results.py
  evaluation/                 llm_evaluate.py, run_eval_batch.py
  batch/                      shell batch runners (.sh files)
  archive/                    one-time fix scripts
c_augmentation/     AST-driven augmentation transforms (libclang-backed)
harness/            build/run/verify pipeline; CLI via python3 -m harness
docs/               design docs, plans
presentations/      pptx, xlsx, speaking notes
rodinia/rodinia-src/ Rodinia source (commit 9c10d3ea) — git submodule
xsbench/xsbench-src/ XSBench source (commit ba08e52) — regular clone, gitignored
results/            phase3/ (CUDA/OMP), phase5/ (HeCBench), augmentation/, evaluation/
analysis/           data/ (CSV, JSON surveys), reports/ (markdown)
```

## Spec & Manifest Rules

> Full details in `.claude/rules/spec-conventions.md`

- `unique_id` / filename: `{source_suite}-{slug}-{parallel_api}` (all lowercase, `+` removed)
- Category enum: `ml graph physics linear_algebra stencil reduction sort molecular_dynamics image crypto financial other`
- `manifest.jsonl` is append-only — never modify existing entries

## Known Issues

> Full details in `.claude/rules/known-issues.md`

- **HeCBench missing:** ~135 validation errors — pre-existing, ignore
- **6 KNOWN_FAIL specs:** Exclude from eval batches (see known-issues.md)
- **Git worktrees + submodules:** Never run evaluations in worktrees

## GitHub Pages

> Full details in `.claude/rules/github-pages.md`

URL: https://samyakjhaveri.github.io/parbench_sam/ (password-protected via staticrypt)
Data refresh: `python3 scripts/generate_viz_data.py`, then commit and push.

## Adding New Benchmark Suites

1. Clone source into `parbench_sam/<suite>/<suite>-src/`
2. Update `config/paths.json` only if `downloads_root` changes
3. Write generator script in `scripts/generators/`
4. Spec filenames: `{suite}-{slug}-{api}.json`
5. Run `python3 scripts/validate_schema.py --all` — fix all non-HeCBench errors before committing

Or use: `/gen-spec <suite>` for the full guided workflow.

## Quality Standards — Non-Negotiable

**Every file touched in this project is reviewed line-by-line after every session.**
Incomplete, superficial, or "good enough" work will be caught immediately.

- **No shortcuts.** Read the file before editing. Understand the code before changing it. Verify the change is correct before reporting done.
- **No partial implementations.** If a task requires touching 5 files, touch all 5. Do not stop at 3 and call it done.
- **Use `ultrathink` for any task involving:** architecture decisions, eval pipeline changes, spec correctness, augmentation transform logic, or anything that affects published results.
- **Verify before closing.** Run validators, unit tests, or harness smoke tests as appropriate. Do not mark work complete without evidence it works.
- **If unsure, say so explicitly** and ask — do not silently guess, make assumptions, or produce plausible-looking output that hasn't been verified.

Samyak reviews all output. Laziness is not acceptable. Thoroughness is the baseline.

## Post-Session Validation Loop

> Full protocol in `.claude/rules/validation-loop.md`

**Every session must pass `/validate` before committing.** Enforced by pre-commit gate hook.

| Command | What it does |
|---------|-------------|
| `/validate` | Full 4-wave validation (10+ agents, ~3 min) |
| `/validate quick` | Wave 1 only: schema + diff + security (~30s) |
| `/validate fix` | Re-run failed waves after implementing fixes |

Waves: (1) verify-app + diff-reviewer + security-scanner → (2) test-synthesizer + regression-checker + spec-auditor → (3) consistency-checker + code-simplifier → (4) self-critic (Opus). On failure: plan mode → user approval → fix → re-validate.

---

## Claude Code Extensions

**Rules** (`.claude/rules/`, 11 files): Each file declares its own `paths:` loading conditions.
Always-loaded: `workflow.md`, `mentoring.md`, `known-issues.md`.
Conditional: `augmentation.md`, `evaluation.md`, `github-pages.md`, `spec-conventions.md`,
`python.md`, `validation-loop.md`, `frontend-design.md`, `known-issues-archive.md`.

**Agents** (`.claude/agents/`, 16 agents): Invoke by name. Each agent file documents its purpose.
Key agents: `plan-reviewer`, `verify-app`, `explorer`, `eval-batcher`, `paper-drafter`, `self-critic`,
`dashboard-refresher`, `rodinia-verifier`, `xsbench-explorer`.

**Skills** (`.claude/skills/`, 9 skills): `/feature-dev`, `/fix-bug`, `/review`, `/gen-spec`,
`/augment-test`, `/validate`, `/eval-run`, `/session-start`, `/dream`. Invoke via `/skill-name`.

**Agent Teams** (experimental): Spawn coordinated Claude Code sessions for multi-model
analysis, paper drafting, debugging. See `.claude/rules/workflow.md` § Agent Teams.
