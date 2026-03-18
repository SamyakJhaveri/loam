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
  --project-root /Users/samyakjhaveri/Desktop/parbench_sam

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
results/            phase3/ (CUDA/OMP), phase5/ (HeCBench), augmentation/, evaluation/
analysis/           data/ (CSV, JSON surveys), reports/ (markdown)
```

## Spec & Manifest Rules

> Full details in `.claude/rules/spec-conventions.md`

### Slugification (validator enforces this)

`identity.unique_id` regex: `^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$`

- `kernel_name` = slug: lowercase, `+` removed, no uppercase
- `unique_id` = `{source_suite}-{slug}-{parallel_api}`
- Filename = `{source_suite}-{slug}-{parallel_api}.json`
- Examples: `b+tree`→`btree`, `hotspot3D`→`hotspot3d`, `lavaMD`→`lavamd`

### Category enum (manifest.jsonl)

Allowed: `ml graph physics linear_algebra stencil reduction sort molecular_dynamics image crypto financial other`

Forbidden aliases: `simulation`, `image_processing`, `data_structures`, `compression`, `sorting`, `bioinformatics`, `scientific`, `data_mining`, `algorithms`

### Cross-check

`manifest.kernel_name == spec.identity.kernel_name` — both must be identical slugs.

## Known Issues

> Full details in `.claude/rules/known-issues.md`

- **HeCBench missing:** 120 `source_dir` errors from `validate_schema.py --all` — pre-existing, ignore
- **Augmentation bugs A/B/C:** BUILD_FAIL at levels 3-4 — see `.claude/rules/known-issues.md`
- **`.cl` file inconsistency:** `spec_loader.py` doesn't augment `.cl` files, `augment_verify.py` does
- **hotspot3d double-include:** NOT a bug — `_cursor_in_main_file` handles it
- **needle.h missing:** `rodinia-src/openmp/nw/` needs `needle.h` copied from `cuda/nw/` after submodule init
- **Git worktrees + submodules:** Never run evaluations in worktrees — `rodinia/` submodule is empty there

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

---

## Session Workflow

Follow these 6 stages for every non-trivial task:

### 1. Orient
- Check context and set model appropriately
- Review relevant `.claude/rules/` files for the task area

### 2. Explore
- Use 3-5 parallel subagents to explore relevant code areas
- Do NOT read files directly in main context — delegate to subagents
- Summarize findings before proceeding

### 3. Plan
- Enter plan mode for non-trivial changes
- Use ultrathink for complex analysis
- Get adversarial review via `plan-reviewer` agent
- **Wait for user approval before implementing**

### 4. Implement
- Work through the plan step by step
- Use subagents for independent subtasks (worktree isolation for parallel changes)
- Verify each step before moving on

### 5. Record
- Update CLAUDE.md or `.claude/rules/` after discovering new conventions/gotchas
- Write session notes for complex multi-step work

### 6. Verify
- Launch 2-4 parallel verification subagents
- Run `python3 scripts/validate_schema.py --all`
- Run relevant unit tests

## Context Management

- `/compact` at ~50% context usage (don't wait until 100%)
- `/clear` between unrelated tasks
- Subagents keep main context clean — only summaries return
- `/compact "focus on X"` for guided compression

## Thinking Levels

| Level | When to use |
|-------|-------------|
| `think` | Simple lookups, single-file edits |
| `think hard` | Multi-file changes, debugging |
| `think harder` | Architecture decisions, complex refactors |
| `ultrathink` | Security review, complex planning, adversarial analysis |

## Subagent Patterns

| Phase | Pattern |
|-------|---------|
| Exploration | "Use 3-5 subagents to explore [area]. Each covers a different angle." |
| Planning | "Use plan-reviewer agent to review this plan adversarially." |
| Implementation | "Use subagents for independent subtasks. Worktree isolation for parallel." |
| Verification | "Use 2-4 subagents: correctness, edge cases, quality, integration." |

## Anti-Patterns (avoid these)

1. Don't implement without a plan — always plan first, get approval
2. Don't explore in main session — use subagents to keep context clean
3. Don't push forward when something breaks — stop and re-plan
4. Don't bundle multiple behavior changes in one session
5. Don't skip verification — always run validators and tests
6. Don't skip recording — update docs after discovering gotchas
7. Keep CLAUDE.md under 350 lines — move details to `.claude/rules/`

## Course Correction

When implementation goes wrong, don't keep pushing. Instead:
> "Stop. This isn't working. Re-plan from scratch knowing what we know now."

Re-enter plan mode, reassess assumptions, and get approval for the new approach.

---

## Claude Code Extensions

### Rules (`.claude/rules/`) — auto-loaded by file context

| File | Loads when | Purpose |
|------|-----------|---------|
| `known-issues.md` | augmentation/harness work | All known bugs, workarounds, smoke test results |
| `github-pages.md` | `visualizations/` work | Deployment, privacy, data refresh, adding dashboards |
| `augmentation.md` | `c_augmentation/` or `scripts/augmentation/` | Transform rules, --project-root requirement, batch commands |
| `evaluation.md` | `scripts/evaluation/` | LLM eval pipeline, --suite flag, header staging, OMP arg patterns |
| `spec-conventions.md` | `specs/` or `manifest.jsonl` | Slugification, categories, validation |
| `python.md` | `*.py` files | Interpreter, testing, style conventions |

### Agents (`.claude/agents/`) — invoke by name

| Agent | When to use |
|-------|-------------|
| `plan-reviewer` | After drafting any plan, before implementation |
| `verify-app` | After implementation, before committing — runs all validators |
| `code-simplifier` | Post-implementation cleanup — reduce complexity |
| `spec-auditor` | After generating new specs — validates slugs, categories, manifest |
| `explorer` | Start of any new task — structured codebase exploration |

### Skills (`.claude/skills/`) — invoke via `/skill-name`

| Skill | Command | Purpose |
|-------|---------|---------|
| Feature Dev | `/feature-dev <name>` | Full feature lifecycle: explore → plan → implement → verify |
| Fix Bug | `/fix-bug <desc>` | Bug fix lifecycle: reproduce → diagnose → fix → verify |
| Review | `/review [files]` | Multi-agent code review (style, correctness, security, perf) |
| Gen Spec | `/gen-spec <suite>` | Generate specs for a new benchmark suite |
| Augment Test | `/augment-test <spec>` | Test augmentation transforms on a spec |

## User Working Style

- **Evaluate before implementing** — explore, test, document the current state first
- **Plan approval required** — never implement without showing the plan and getting go-ahead
- **Visual artifacts** — create HTML/visual presentations for architecture and results
- **Parallel exploration** — use multiple subagents (up to 5) for comprehensive exploration
- **Deep reasoning** — use ultrathink for complex analysis; break problems into tasks
