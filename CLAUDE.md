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
| `HeCBench-master/` | Gitignored but **cloned locally** (1874 benchmark dirs) |

Full details: `.claude/rules/architecture.md` (conditional on harness/, scripts/, c_augmentation/).

## Invariants

1. **`manifest.jsonl` is append-only** — never modify existing entries
2. **Result JSONs are immutable** — use `--resume` to skip existing
3. **Never run evaluations in worktrees** — submodules are empty there
4. **Never change spec run args** without reading the source's `argc` check first
5. **~15 `validate_schema.py --all` errors are expected** (phantom specs only) — do not fix
6. **8 KNOWN_FAIL specs** — exclude from eval batches (list in `known-issues.md`)
7. **`git push origin main` is blocked** by Bash permissions — push to a feature branch, or ask the user to run `! git push origin main`. Don't retry the blocked push.

## Quality

- Read before editing. No partial implementations. Verify before reporting done.
- `ultrathink` for: architecture, eval pipeline, spec correctness, augmentation, published results.
- If unsure, say so explicitly — never guess silently.
- `/validate` before every commit. Pre-commit hook requires waves 1-3; wave 4 optional.
- `.validation_passed` sentinel is single-use — clears after each commit. Multi-commit sessions must re-run waves 1-3 every commit. Docs-only commits still require validation (~90s).
- When citing code identifiers in docs (line numbers, `MODEL_REGISTRY` keys, function names), grep to verify BEFORE commit. Line numbers drift.
- **Model selection:** Use Opus for main work. Before commit/push: `/model haiku` (faster, cheaper).
- **Multi-worker orchestration:** Use `/agent-team` as default for 2+ parallel workers. Opus advisor + Sonnet workers. `--all-opus` only when deep reasoning from every worker is required. Do NOT use `dispatching-parallel-agents`.

Behavioral guidelines (Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution): see `karpathy-guidelines` plugin (listed under External Plugin Skills below).

## Conditional Rules (`.claude/rules/`, auto-loaded by file path)

| File | Triggers on | Key content |
|------|------------|-------------|
| `known-issues.md` | Always | KNOWN_FAIL list, build gotchas, spec status |
| `workflow.md` | Always | 6-stage workflow, agents, teams, anti-patterns |
| `tech-stack.md` | `*.py`, `requirements*.txt`, `pyproject.toml`, `Makefile` | Languages, deps, compilers, config |
| `architecture.md` | `harness/**`, `scripts/**`, `c_augmentation/**` | Layers, data flow, entry points, abstractions |
| `python.md` | `*.py` | `python3`, CLI flag ordering, style, naming, module/function design, logging |
| `spec-conventions.md` | `specs/`, `manifest.jsonl` | Naming, categories, run arg verification protocol |
| `evaluation.md` | `scripts/evaluation/` | `--suite`/`--project-root` required, result schema |
| `augmentation.md` | `c_augmentation/`, `scripts/augmentation/` | `--project-root` required, transform bugs |
| `active-gotchas.md` | `harness/**`, `scripts/evaluation/**`, `scripts/analysis/**`, `visualizations/**` | Hook protection, submodule patches, checksums, `overall_status` rule, timing caveat, OpenCL predicate |
| `known-issues-archive.md` | `scripts/evaluation/**`, `c_augmentation/**`, `scripts/augmentation/**`, `results/evaluation/**` | Historical eval/augmentation fix details, cited by planning docs |
| `validation-loop.md` | hooks, validation agents | 4-wave protocol, sentinel, fix loop |
| `github-pages.md` | `visualizations/` | URL, staticrypt, data refresh |
| `frontend-design.md` | `visualizations/` | Design system, styling |

<!-- GSD:project-start source:PROJECT.md -->
## Project

**ParBench**

Kernel-centric benchmark framework for evaluating LLM-based parallel code translation (CUDA ↔ OpenMP ↔ OpenCL). 88 curated non-KNOWN_FAIL specs (206 JSON total) across 5 suites, build-run-verify harness, AST-driven augmentation engine, canonical + L0-conditional ablation protocol. Current sprint runs multi-model evaluations for NeurIPS 2026.

**Core Value:** Every evaluation result is reproducible and pipeline-correct — so model comparisons are defensible under peer review.

### Constraints

- **Timeline:** NeurIPS 2026 deadline **May 1, 2026** (Datasets & Benchmarks track)
- **Data immutability:** Never modify existing result JSONs — use `--resume`
- **Audit-first:** Pipeline must be hardened before new model evals are trusted
- **Lean planning:** PROJECT.md stays lightweight; phases added incrementally
<!-- GSD:project-end -->

<!-- GSD:skills-start source:skills/ -->
## Project Skills

| Skill | Description | Path |
|-------|-------------|------|
| creating-agent-teams | Coordinated agent teams via TeamCreate for multi-teammate tasks with cross-talk. NOT for independent parallel tasks. | `.claude/skills/agent-team/SKILL.md` |
| augment-test | Augmentation testing workflow | `.claude/skills/augment-test/SKILL.md` |
| catchup | Session bootstrap | `.claude/skills/catchup/SKILL.md` |
| cite-check | Paper citation checker | `.claude/skills/cite-check/SKILL.md` |
| dream | Memory consolidation | `.claude/skills/dream/SKILL.md` |
| eval-run | Eval batch launcher | `.claude/skills/eval-run/SKILL.md` |
| feature-dev | Feature development workflow | `.claude/skills/feature-dev/SKILL.md` |
| fix-bug | Bug fix workflow | `.claude/skills/fix-bug/SKILL.md` |
| gen-spec | Spec generation | `.claude/skills/gen-spec/SKILL.md` |
| grill-research | Research interrogation | `.claude/skills/grill-research/SKILL.md` |
| handoff | Handoff doc writer | `.claude/skills/handoff/SKILL.md` |
| hypothesis-tree | Hypothesis tree manager | `.claude/skills/hypothesis-tree/SKILL.md` |
| interpret-results | Hypothesis-first interpretation | `.claude/skills/interpret-results/SKILL.md` |
| mentoring | HPC/SE/research teaching framework grounded in ParBench | `.claude/skills/mentoring/SKILL.md` |
| model-route | Model route advisor | `.claude/skills/model-route/SKILL.md` |
| navigate | Intent → tool recommender across ParBench/GSD/superpowers | `.claude/skills/navigate/SKILL.md` |
| overnight-eval | Overnight eval campaign | `.claude/skills/overnight-eval/SKILL.md` |
| paper-review-sim | Paper review simulator | `.claude/skills/paper-review-sim/SKILL.md` |
| post-eval | Post-eval pipeline | `.claude/skills/post-eval/SKILL.md` |
| ralph-loop | Stateless loop | `.claude/skills/ralph-loop/SKILL.md` |
| reflect | Structured reflection | `.claude/skills/reflect/SKILL.md` |
| review | Multi-agent code review | `.claude/skills/review/SKILL.md` |
| spec-check | Spec health check | `.claude/skills/spec-check/SKILL.md` |
| techdebt | Tech debt inventory | `.claude/skills/techdebt/SKILL.md` |
| validate | Post-session validation | `.claude/skills/validate/SKILL.md` |
| workflow-ref | Skill/agent reference, agent teams, thinking levels | `.claude/skills/workflow-ref/SKILL.md` |
<!-- GSD:skills-end -->

### External Plugin Skills

| Skill | Plugin | Source |
|-------|--------|--------|
| karpathy-guidelines | `andrej-karpathy-skills` | https://github.com/forrestchang/andrej-karpathy-skills |

## Project Agents

Custom Task agents under `.claude/agents/`. Spawn via Agent tool with matching `subagent_type`. Validation agents orchestrated by `validate` skill.

| Agent | Description |
|-------|-------------|
| code-simplifier | Post-impl cleanup: duplication, dead code, unclear names. Wave 3. |
| consistency-checker | Cross-checks CLAUDE.md / known-issues.md / agent tables. Wave 3. |
| diff-reviewer | Reviews git diff for regressions/partial work. Wave 1. |
| eval-batcher | Runs LLM eval batches, knows kernel eligibility and phantom exclusions. |
| explorer | Maps files, call chains, dependencies, coverage. |
| plan-reviewer | Adversarial plan review. |
| regression-checker | Compares metrics against baselines. Wave 2. |
| rodinia-verifier | Runs `harness verify` on Rodinia specs. |
| security-scanner | Scans for secrets, injection, unsafe patterns. Wave 1. |
| self-critic | Opus adversarial self-review. Wave 4. |
| spec-auditor | Audits spec JSONs. Wave 2 (conditional). |
| test-synthesizer | Writes temp test scripts for changed files. Wave 2. |
| verification-lead | Hierarchical validation coordinator. |
| verify-app | Project health check: schema, tests, specs, manifest. Wave 1. |

<!-- GSD:workflow-start source:GSD defaults -->
## GSD Workflow Enforcement

Before Edit/Write/other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

- `/gsd-quick` — small fixes, doc updates, ad-hoc tasks
- `/gsd-debug` — investigation and bug fixing
- `/gsd-execute-phase` — planned phase work

Don't make direct repo edits outside GSD unless the user explicitly asks to bypass.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->
## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate.
> Managed by `generate-claude-profile` — do not edit manually.
<!-- GSD:profile-end -->

- challenge assumptions or offer corrections anytime you get a chance
- point out any flaws in the questions or solutions I suggest