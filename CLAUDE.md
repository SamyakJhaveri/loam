# CLAUDE.md — ParBench

## Environment

- **Platform:** Linux (Ubuntu, kernel 6.8)
- **Python:** 3.12.3 — use `python3`, never bare `python`
- **Venv:** ALWAYS activate first: `source env_parbench/bin/activate`
- **Install packages:** `python3 -m pip install <pkg>` inside activated venv

## System Paths (hardcoded on this machine)

```
nvcc:        /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/bin/nvcc
CUDA_DIR:    /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda
OPENCL_INC:  /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/include
OPENCL_LIB:  /opt/nvidia/hpc_sdk/Linux_x86_64/24.3/cuda/lib64
GPU:         NVIDIA GeForce RTX 4070
```

## config/paths.json (Linux values — do not revert to Mac paths)

```json
{
    "project_root": "/home/samyak/Desktop/parbench_sam",
    "downloads_root": "/home/samyak/Desktop/parbench_sam",
    "hecbench_root": "/home/samyak/Desktop/parbench_sam/HeCBench-master"
}
```

`downloads_root` equals `project_root`. `source_dir` fields in `manifest.jsonl` are relative to `downloads_root`.

## Common Commands

```bash
# Validate all specs (120 HeCBench errors are expected and pre-existing — do not fix)
source env_parbench/bin/activate
python3 scripts/validate_schema.py --all

# Validate one spec
python3 scripts/validate_schema.py --spec specs/<name>.json

# Harness — IMPORTANT: global flags (-v, --json) MUST come BEFORE the subcommand
python3 -m harness -v verify specs/rodinia-bfs-cuda.json
python3 -m harness --json verify specs/rodinia-bfs-cuda.json
python3 -m harness prompt specs/rodinia-bfs-cuda.json --augment_level 2

# Unit tests (augmentation transforms)
python3 -m pytest c_augmentation/test_transforms.py -v

# Augment → build → run → verify pipeline
python3 scripts/augmentation/augment_verify.py specs/<name>.json --augment_level 2 --seed 42 -v
```

## Project Layout

```
specs/              {suite}-{slug}-{api}.json per kernel-API variant
manifest.jsonl      append-only; never modify existing entries
schema/             spec_schema.json (v1.0.0), manifest_schema.json
scripts/
  validate_schema.py          top-level validator (path unchanged)
  generators/                 spec generation scripts
  survey/                     codebase surveying scripts
  analysis/                   results analysis & reporting
  baselines/                  baseline population scripts
  augmentation/               augment_verify.py, run_augment_batch.py, combine_aug_results.py
  batch/                      shell batch runners (.sh files)
  archive/                    one-time fix scripts
c_augmentation/     AST-driven augmentation transforms (libclang-backed)
harness/            build/run/verify pipeline; CLI via python3 -m harness
docs/               design docs (json_schema_design.md, integrate_augmentation_into_harness.md)
docs/plans/         hecbench pilot + phase5 planning docs
presentations/      pptx, xlsx, speaking notes for team/research lead
rodinia/rodinia-src/ Rodinia source (commit 9c10d3ea)
results/            phase3/ (CUDA/OMP), phase5/ (HeCBench), augmentation reports
analysis/data/      CSV matrices, JSON surveys
analysis/reports/   markdown reports, augmentation bug report
```

## Spec & Manifest Rules

### Slugification (IMPORTANT — validator enforces this)

`identity.unique_id` regex: `^[a-z0-9_]+-[a-z0-9_][a-z0-9_-]*-[a-z0-9_]+$`

- `kernel_name` must be the slug: lowercase, `+` removed, no uppercase
- `unique_id` = `{source_suite}-{slug}-{parallel_api}`
- Filename = `{source_suite}-{slug}-{parallel_api}.json`
- Examples: `b+tree`→`btree`, `hotspot3D`→`hotspot3d`, `lavaMD`→`lavamd`

### Category enum (manifest.jsonl)

Allowed: `ml graph physics linear_algebra stencil reduction sort molecular_dynamics image crypto financial other`

**Forbidden aliases:** `simulation`, `image_processing`, `data_structures`, `compression`, `sorting`, `bioinformatics`, `scientific`, `data_mining`, `algorithms`

Mappings: image processing→`image` | simulation/physics/fluid→`physics` | sorting→`sort` | data structures/compression/bioinformatics/data mining→`other`

### Cross-check

Validator asserts `manifest.kernel_name == spec.identity.kernel_name`. Both must be identical slugs.

## Known Issues / Gotchas

### HeCBench missing
120 `source_dir` disk-not-found errors from `validate_schema.py --all` are pre-existing. HeCBench is not cloned locally. Do not try to fix these errors.

### Augmentation transform bugs (c_augmentation — as of 2026-03-10)

Three bugs cause BUILD_FAIL at augment level 3–4. Levels 1–2 with seed=42 currently apply no transforms (randomly selects a transform with no candidates).

**Bug A — PointerArithmeticToArrayIndex: overlapping nested subscripts**
When nested `ARRAY_SUBSCRIPT_EXPR` (e.g., `iS[i]` inside `J[iS[i]*cols+j]`) and its parent are both selected, combined byte-offset edits corrupt the output. Fix: validate the combined `RewriteCandidate` in `AstTransform.apply()`, or filter overlapping candidates before selection.

**Bug B — PointerArithmeticToArrayIndex: struct member access precedence**
`arr[i].member` → `*((arr)+(i)).member` is wrong; `.` binds tighter than `*`. Must emit `(*((arr)+(i))).member`.

**Bug C — SwapCondition: assignment-in-condition**
`fp = fopen(...) == 0` → `0 == fp = fopen(...)` produces `(0 == fp) = fopen(...)` — non-lvalue error. Fix: skip `BINARY_OPERATOR ==` nodes where either child contains an assignment.

### .cl file inconsistency
`harness/spec_loader.py:get_prompt_payload` (line 195) does NOT augment `.cl` files (missing from suffix list). `scripts/augmentation/augment_verify.py` DOES augment `.cl` files via `AUGMENTABLE_SUFFIXES`. Fix: add `.cl` to the list in `spec_loader.py`.

### hotspot3d double-include (NOT a bug)
`3D.cu` includes `opt1.cu` via `#include "opt1.cu"`. No double-augmentation occurs because `_cursor_in_main_file` in `augment_dataset.py` skips cursors from included files.

### Smoke tests (verified 2026-03-06 — all PASS)
```
rodinia-bfs-cuda    BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-hotspot-omp BUILD: PASS | RUN: PASS | VERIFY: PASS
rodinia-bfs-opencl  BUILD: PASS | RUN: PASS | VERIFY: PASS
```
Fixes applied: CUDA_DIR path, `make hotspot` target, OpenCL include/lib paths, `CC_FLAGS=-std=c++14`, data path symlinks (`rodinia/rodinia-src/data/` → `rodinia-data/`).

## GitHub Pages

Visualizations are hosted at: **https://samyakjhaveri.github.io/parbench_sam/**

- Source: `visualizations/` directory (9 files: 7 HTML + 2 JS data files)
- Deployment: GitHub Actions workflow at `.github/workflows/deploy-pages.yml`
- Triggers: any push to `main` that touches `visualizations/**`, or manual `workflow_dispatch`
- Entry point: `visualizations/index.html` redirects to `overview.html`
- MCP plugins added to `.mcp.json`: `puppeteer` (browser preview), `css-docs` (CSS reference)
- To re-enable Pages after repo transfer: Settings → Pages → Source = "GitHub Actions"
- **Privacy:** Site is password-protected via `staticrypt` (AES-256 browser encryption). Password stored as GitHub secret `PAGES_PASSWORD`. See `.github/PAGES_SETUP.md` for setup instructions.
- **Limitation:** True private Pages (GitHub SSO auth) requires GitHub Enterprise Cloud — not available on GitHub Pro.
- **Data refresh:** Run `python3 scripts/generate_viz_data.py` to regenerate `results_data.js` and `build_results_data.js` from source JSON files in `results/augmentation/`. Then commit and push to redeploy.

### Adding a New Dashboard
1. Create `visualizations/<name>.html` (copy nav structure from any existing page)
2. Add a nav link to the new page in ALL 6 existing HTML files' nav bars
3. Add it to the dashboard list in `README.md`
4. Push to `main` — workflow auto-deploys

## User Working Style & Claude Code Preferences

### Collaboration Model
- **Evaluate before implementing** — always explore, test, and document the current state before writing fixes
- **Plan approval required** — never implement without showing the plan first and getting explicit go-ahead
- **Visual artifacts** — create HTML/visual presentations to explain architecture and results
- **Parallel exploration** — use multiple subagents (up to 5) for comprehensive codebase exploration
- **Deep reasoning** — use ultrathink for complex analysis; break problems into tasks and sub-tasks

### Session Workflow
1. Explore the codebase thoroughly (parallel agents)
2. Identify solved and unsolved problems
3. Create visual artifacts explaining the system
4. Present a comprehensive plan
5. Get user approval before any implementation
6. Test and verify after implementation

### Mistakes to Avoid
- Don't implement fixes before the user understands the problem space
- Don't skip plan approval — always present the plan and wait
- Don't run agents sequentially when they can be parallelized
- Don't use `augment_verify.py` without `--project-root` flag (auto-detection is broken)
- Always record learnings in CLAUDE.md for cross-session persistence

## Adding New Benchmark Suites

1. Clone source into `parbench_sam/<suite>/<suite>-src/`
2. Update `config/paths.json` only if `downloads_root` changes
3. Write generator script in `scripts/`
4. Spec filenames: `{suite}-{slug}-{api}.json`
5. Run `python3 scripts/validate_schema.py --all` — fix all non-HeCBench errors before committing
