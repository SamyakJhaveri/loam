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

- **HeCBench missing:** 120 `source_dir` errors — pre-existing, ignore
- **Augmentation bugs A/B/C:** BUILD_FAIL at levels 3-4
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

## Frontend Theme & Design Standards

> Full spec in `visualizations/DESIGN.md`. Reference it on every frontend task.

### Aesthetic Direction
"Clean, minimal, academic — like a Nature paper's online appendix."
Light theme throughout. Data-dense but not cluttered. Professional enough for SC26 reviewers.

### Design Decisions (locked)
- **Theme:** Light — `#f9fafb` background, `#ffffff` card surfaces
- **Fonts:** Inter (UI/labels) + JetBrains Mono (data values, code, hashes)
- **Charts:** Chart.js v4 (CDN, no build step) — never fake HTML div-width bars
- **Colors (charts):** Okabe-Ito colorblind-safe palette — see DESIGN.md for hex values
- **Spacing:** 8pt grid — all padding/margin/gap are multiples of 4 or 8
- **Mobile:** Desktop-only (research dashboard)
- **Print:** @media print stylesheet on all public pages (for paper figures)

### Frontend Generation Rules (anti-"AI slop")
When writing or editing any HTML/CSS/JS in visualizations/:

1. **Commit to the aesthetic** — dark backgrounds and purple gradients are banned. Use the DESIGN.md token values exactly.
2. **Use design tokens** — never hardcode hex values in components; always use `var(--color-*)` tokens defined in the `:root` block.
3. **Real charts only** — no `<div style="width:68%">` fake bars. Use Chart.js with proper axes, tooltips, and legends.
4. **Typography matters** — use Inter with appropriate weights (400/500/600/700). Data values and kernel names use JetBrains Mono. Max 4 font sizes per page.
5. **One shadow rule** — `box-shadow: 0 1px 3px hsl(220deg 40% 15% / 0.08), 0 4px 12px hsl(220deg 40% 15% / 0.08)` — layered, hue-matched, never `rgba(0,0,0,0.1)`.
6. **Section comments** — wrap every major section in `<!-- === SECTION: Name === -->` / `<!-- === END SECTION === -->` for targeted editing.
7. **Print stylesheet** — every public page must include `@media print { ... }` that hides nav, sets white bg, adjusts fonts for publication quality.
8. **No Tailwind CDN** — plain CSS with custom properties is the correct choice for single-file HTML pages.
9. **Accessibility** — ARIA roles on tabs (`role="tablist"`, `role="tab"`, `aria-selected`). No color-only status indication; add text labels.
10. **Error handling** — if a page depends on an external .js data file, show a visible fallback message if it fails to load; never silently show empty tables.

---

## Claude Code Extensions

### Rules (`.claude/rules/`) — routing table

| File | Loads when | Purpose |
|------|-----------|---------|
| `workflow.md` | Always | Session workflow, thinking levels, anti-patterns |
| `mentoring.md` | Always | PhD mentoring directive, Insight blocks |
| `known-issues.md` | Always | All known bugs, workarounds, smoke test results |
| `augmentation.md` | `c_augmentation/**`, `scripts/augmentation/**` | Transform rules, --project-root, batch commands |
| `evaluation.md` | `scripts/evaluation/**` | LLM eval pipeline, --suite flag, OMP arg patterns |
| `github-pages.md` | `visualizations/**`, `.github/workflows/**` | Deployment, privacy, data refresh |
| `spec-conventions.md` | `specs/**`, `manifest.jsonl` | Slugification, categories, validation |
| `python.md` | `**/*.py` | Interpreter, testing, style conventions |
| `validation-loop.md` | Always | Post-session validation protocol, wave structure, fix loop |

### Agents (`.claude/agents/`) — invoke by name

| Agent | When to use |
|-------|-------------|
| `plan-reviewer` | Before any non-trivial implementation — adversarial plan review (uses Opus) |
| `verify-app` | Before committing — runs schema validation, unit tests, manifest check |
| `code-simplifier` | Post-implementation cleanup — finds duplication, dead code, over-engineering |
| `spec-auditor` | After generating new specs — validates slugs, categories, manifest entries |
| `explorer` | Start of any new task — maps files, traces call chains, finds gotchas |
| `rodinia-verifier` | After submodule resets or spec edits — runs all 54+6 harness checks |
| `eval-batcher` | SC26 eval sessions (2, 3, 7, 9, 10) — runs LLM eval batches (background) |
| `xsbench-explorer` | Session 4 only — extracts build/run/verify info from XSBench source |
| `dashboard-refresher` | After eval runs or spec changes — regenerates JS data, fixes stale HTML |
| `paper-drafter` | Sessions 12, 13, 15 — writes paper sections with actual data (uses Opus) |
| `diff-reviewer` | Validation Wave 1 — git diff for regressions, partial implementations |
| `security-scanner` | Validation Wave 1 — secrets, injection, OWASP in changed files |
| `test-synthesizer` | Validation Wave 2 — writes+runs temp test programs for changed code |
| `regression-checker` | Validation Wave 2 — before/after metrics comparison |
| `consistency-checker` | Validation Wave 3 — docs vs code vs known-issues cross-check |
| `self-critic` | Validation Wave 4 — Opus adversarial self-review for rationalization |

### Skills (`.claude/skills/`) — invoke via `/skill-name`

| Skill | Command | Purpose |
|-------|---------|---------|
| Feature Dev | `/feature-dev <name>` | Full feature lifecycle: explore → plan → implement → verify |
| Fix Bug | `/fix-bug <desc>` | Bug fix lifecycle: reproduce → diagnose → fix → verify |
| Review | `/review [files]` | Multi-agent code review (style, correctness, security, perf) |
| Gen Spec | `/gen-spec <suite>` | Generate specs for a new benchmark suite |
| Augment Test | `/augment-test <spec>` | Test augmentation transforms on a spec |
| Validate | `/validate [quick\|full\|fix]` | Post-session validation: 10+ agents, 4 waves, pre-commit gate |
