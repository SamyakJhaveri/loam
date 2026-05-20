# Flavor Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce 4 flavors (research, software-eng, ml, hpc) to 2 (research, software-eng) by absorbing ml+hpc content into research.

**Architecture:** The ml and hpc flavors never stood alone — they always stacked with research. Merging them into research removes maintenance burden (4 copies of python.md → 2) and eliminates a flavor-selection decision that never had a "just ml" or "just hpc" answer for this user's domain (AI for SWE for HPC). After consolidation, research includes HPC skills (cuda-omp-translator, hpc-code-reviewer) and the ML seed-docs are superseded by research's more generic versions.

**Tech Stack:** Bash scripts, Markdown, shell verification

**Design Decision (A vs B resolved):** Keep 2 copies of python.md/tech-stack.md (one per flavor), enforce identity via verify-template.sh. This is simpler than a symlink/inheritance mechanism and the verify script already implements this pattern.

---

### Task 1: Move HPC skills into research

**Files:**
- Move: `flavors/hpc/skills/cuda-omp-translator/SKILL.md` → `flavors/research/skills/cuda-omp-translator/SKILL.md`
- Move: `flavors/hpc/skills/hpc-code-reviewer/SKILL.md` → `flavors/research/skills/hpc-code-reviewer/SKILL.md`

- [ ] **Step 1: Move cuda-omp-translator into research**

```bash
cp -R flavors/hpc/skills/cuda-omp-translator/ flavors/research/skills/cuda-omp-translator/
```

- [ ] **Step 2: Move hpc-code-reviewer into research**

```bash
cp -R flavors/hpc/skills/hpc-code-reviewer/ flavors/research/skills/hpc-code-reviewer/
```

- [ ] **Step 3: Verify skills exist in new location**

```bash
test -f flavors/research/skills/cuda-omp-translator/SKILL.md && echo OK
test -f flavors/research/skills/hpc-code-reviewer/SKILL.md && echo OK
```

- [ ] **Step 4: Commit**

```bash
git add flavors/research/skills/cuda-omp-translator/ flavors/research/skills/hpc-code-reviewer/
git commit -m "feat: absorb HPC skills into research flavor"
```

---

### Task 2: Remove ml and hpc flavor directories

**Files:**
- Delete: `flavors/ml/` (entire directory)
- Delete: `flavors/hpc/` (entire directory)

- [ ] **Step 1: Confirm research has everything ml added**

ml added: `rules/python.md`, `rules/tech-stack.md` (already in research, verified identical), `seed-docs/EXPERIMENTS.md.tmpl`, `seed-docs/RESULTS.md.tmpl` (research has its own generic versions already). Nothing unique to absorb.

- [ ] **Step 2: Confirm research has everything hpc added**

hpc added: `rules/python.md`, `rules/tech-stack.md` (already in research), `skills/cuda-omp-translator/`, `skills/hpc-code-reviewer/` (moved in Task 1). Nothing remaining.

- [ ] **Step 3: Remove ml and hpc directories**

```bash
git rm -rf flavors/ml/
git rm -rf flavors/hpc/
```

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor: remove ml and hpc flavors (absorbed into research)"
```

---

### Task 3: Update init-project.sh

**Files:**
- Modify: `bin/init-project.sh:17` — change VALID_FLAVORS

- [ ] **Step 1: Change VALID_FLAVORS array**

Change line 17 from:
```bash
readonly VALID_FLAVORS=(research software-eng ml hpc)
```
to:
```bash
readonly VALID_FLAVORS=(research software-eng)
```

- [ ] **Step 2: Verify script still parses**

```bash
bash -n bin/init-project.sh && echo "syntax OK"
```

- [ ] **Step 3: Commit**

```bash
git add bin/init-project.sh
git commit -m "refactor: remove ml/hpc from VALID_FLAVORS"
```

---

### Task 4: Update verify-template.sh

**Files:**
- Modify: `bin/verify-template.sh`

- [ ] **Step 1: Rewrite verify-template.sh**

Remove all ml/hpc test blocks (lines 29-68). Replace with a simpler structure that only tests the 2 flavors and checks python.md/tech-stack.md identity between them.

New content for verify-template.sh:

```bash
#!/usr/bin/env bash
# verify-template.sh — sanity-check that bootstrapping produces valid projects.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

cd "$TEMPLATE_ROOT"

if command -v shellcheck >/dev/null; then
  shellcheck bin/*.sh .claude/hooks/*.sh || { echo "FAIL: shellcheck"; exit 1; }
  echo "OK: shellcheck"
else
  echo "SKIP: shellcheck not installed"
fi

bin/init-project.sh "$TMP/no-flavor" >/dev/null
test -f "$TMP/no-flavor/CLAUDE.md"              || { echo "FAIL: no CLAUDE.md (no-flavor)"; exit 1; }
test -f "$TMP/no-flavor/.claude/settings.json"   || { echo "FAIL: no settings.json (no-flavor)"; exit 1; }
python3 -m json.tool "$TMP/no-flavor/.claude/settings.json" >/dev/null || { echo "FAIL: invalid settings.json (no-flavor)"; exit 1; }
test ! -f "$TMP/no-flavor/.claude/audit.log"     || { echo "FAIL: audit.log propagated (no-flavor)"; exit 1; }
for rule in python.md tech-stack.md architecture.md frontend-design.md; do
  test ! -f "$TMP/no-flavor/.claude/rules/$rule" || { echo "FAIL: $rule leaked to no-flavor"; exit 1; }
done
echo "OK: flavor (none)"

for flavor in research software-eng; do
  bin/init-project.sh "$TMP/$flavor" --flavor "$flavor" >/dev/null
  test -f "$TMP/$flavor/.claude/settings.json"   || { echo "FAIL: $flavor missing settings.json"; exit 1; }
  python3 -m json.tool "$TMP/$flavor/.claude/settings.json" >/dev/null || { echo "FAIL: $flavor invalid settings.json"; exit 1; }
  echo "OK: flavor $flavor"
done

# Rule placement assertions
test -f "$TMP/research/.claude/rules/python.md"          || { echo "FAIL: research missing python.md"; exit 1; }
test -f "$TMP/research/.claude/rules/tech-stack.md"       || { echo "FAIL: research missing tech-stack.md"; exit 1; }
test ! -f "$TMP/research/.claude/rules/architecture.md"   || { echo "FAIL: research has architecture.md"; exit 1; }
test ! -f "$TMP/research/.claude/rules/frontend-design.md" || { echo "FAIL: research has frontend-design.md"; exit 1; }
echo "OK: research rules"

for rule in python.md tech-stack.md architecture.md frontend-design.md; do
  test -f "$TMP/software-eng/.claude/rules/$rule" || { echo "FAIL: software-eng missing $rule"; exit 1; }
done
echo "OK: software-eng rules"

# HPC skills should now be part of research
test -f "$TMP/research/.claude/skills/cuda-omp-translator/SKILL.md" || { echo "FAIL: research missing cuda-omp-translator"; exit 1; }
test -f "$TMP/research/.claude/skills/hpc-code-reviewer/SKILL.md"   || { echo "FAIL: research missing hpc-code-reviewer"; exit 1; }
echo "OK: research HPC skills"

# Duplication guard — python.md and tech-stack.md must be identical across flavors
cmp --silent "$TEMPLATE_ROOT/flavors/research/rules/python.md" "$TEMPLATE_ROOT/flavors/software-eng/rules/python.md" \
  || { echo "FAIL: python.md diverged between research and software-eng"; exit 1; }
cmp --silent "$TEMPLATE_ROOT/flavors/research/rules/tech-stack.md" "$TEMPLATE_ROOT/flavors/software-eng/rules/tech-stack.md" \
  || { echo "FAIL: tech-stack.md diverged between research and software-eng"; exit 1; }
echo "OK: duplicated rules identical"

echo "ALL OK"
```

- [ ] **Step 2: Run verify-template.sh**

```bash
bin/verify-template.sh
```

Expected: ALL OK

- [ ] **Step 3: Commit**

```bash
git add bin/verify-template.sh
git commit -m "refactor: update verify-template.sh for 2-flavor world"
```

---

### Task 5: Update docs/FLAVORS.md

**Files:**
- Modify: `docs/FLAVORS.md`

- [ ] **Step 1: Rewrite FLAVORS.md for 2 flavors**

```markdown
# Flavors

Flavors are opt-in packs that layer additional skills/agents/hooks/rules and seed-docs onto the generic core at bootstrap time. They stack — pass multiple `--flavor` flags.

## Available flavors

| Flavor | Adds | Pick when |
|--------|------|-----------|
| `research`     | Hypothesis workflow, paper-writing, citation audit, result protection, CUDA/OpenMP guides, HPC code review | Research projects, papers, ML experiments, HPC work |
| `software-eng` | Design records, architecture docs, frontend rules | Building software products, tools, websites |

## Usage examples

| Project type | Recommended flavors |
|--------------|---------------------|
| ML/HPC research with paper    | `research` |
| Greenfield SaaS               | `software-eng` |
| Personal tool with research   | `research --flavor software-eng` |

## What each flavor adds

See each flavor's `README.md`:

- `flavors/research/README.md`
- `flavors/software-eng/README.md`

## Layering semantics

When `init-project.sh` applies multiple flavors, they're overlaid in the order passed. Same-path collisions: later overlays win, with a warning. In practice, the two flavors don't collide today (they touch disjoint skill/agent/hook names).

If you discover a collision while developing flavors, prefer renaming over silently letting one win — overlap usually means a skill should live in `generic` instead of any specific flavor.

## Promoting a new flavor-specific asset

When you build a skill/agent/hook in a project that's clearly flavor-specific, promote it via:

```
template-sync promote <relpath>
```

Pick the target layer when prompted. Don't promote into `generic` to "save effort" — flavors exist to keep the generic core lean.
```

- [ ] **Step 2: Commit**

```bash
git add docs/FLAVORS.md
git commit -m "docs: update FLAVORS.md for 2-flavor consolidation"
```

---

### Task 6: Update docs/ASSET-LAYERS.md

**Files:**
- Modify: `docs/ASSET-LAYERS.md`

- [ ] **Step 1: Remove ml/hpc references from ASSET-LAYERS.md**

Replace the "But the skill suggests a layer based on what the asset references" section. Change:
```
- Mentions training loops, eval, model checkpoints → likely `flavor:ml`
- Mentions CUDA, OpenMP, MPI, kernel → likely `flavor:hpc`
```
to:
```
- Mentions training loops, eval, model checkpoints, CUDA, OpenMP, MPI → likely `flavor:research`
```

Also update the "Examples of correctly-flavor assets" section. Change:
```
- CUDA/OpenMP translator → `hpc` (most projects aren't HPC)
- Python style rules (`python.md`, `tech-stack.md`) → all Python-using flavors
```
to:
```
- CUDA/OpenMP translator → `research` (HPC work is research in this context)
- Python style rules (`python.md`, `tech-stack.md`) → both flavors (research + software-eng)
```

- [ ] **Step 2: Commit**

```bash
git add docs/ASSET-LAYERS.md
git commit -m "docs: update ASSET-LAYERS.md for 2-flavor world"
```

---

### Task 7: Update flavors/research/README.md

**Files:**
- Modify: `flavors/research/README.md`

- [ ] **Step 1: Rewrite research README to reflect absorbed content**

```markdown
# Flavor: research

Adds tooling for research-style projects: hypothesis-driven investigation, experiment tracking, results discipline, paper writing, and HPC/parallel-computing support.

## Adds to `.claude/`

### Rules
- `rules/python.md`     — Python style, testing, naming (loads on `*.py`)
- `rules/tech-stack.md` — Python 3.12+, pip, pyproject.toml (loads on Python/build files)

### Skills
- `skills/hypothesis-tree/`              — branching hypothesis manager
- `skills/interpret-results/`            — hypothesis-first interpretation of results
- `skills/paper-write/`                  — LaTeX section drafting with citation fetching
- `skills/citation-audit/`              — bibliographic verification
- `skills/cite-check/`                  — numeric claim tracing to raw results
- `skills/paper-claim-audit/`           — paper numbers vs raw result verification
- `skills/paper-review-sim/`            — conference-style peer review simulation
- `skills/rebuttal/`                    — reviewer rebuttal pipeline
- `skills/auto-paper-improvement-loop/` — iterative review-fix-recompile loop
- `skills/aris-shared-references/`      — academic writing standards and protocols
- `skills/cuda-omp-translator/`         — CUDA↔OpenMP translation pattern guide
- `skills/hpc-code-reviewer/`           — parallel-correctness checklist (data races, memory model, atomics)

### Agents
- `agents/paper-assembly-team.md` — multi-agent paper drafting team
- `agents/regression-checker.md`  — regression detection agent

### Hooks
- `hooks/protect-results.sh` — guards `results/` from accidental mutation

## Seeds at project root

- `EXPERIMENTS.md` — running ledger of experiments
- `FINDINGS.md`    — distilled insights from experiments
- `RESULTS.md`     — index of result artifacts (immutable)
- `REFERENCES.md`  — bibliography and reference tracking
- `ARCHITECTURE.md` — system architecture documentation
- `DESIGN.md`      — design decisions and rationale

## When to pick

- Research projects, applied research, exploratory analysis.
- Any project producing a paper or technical report.
- ML training, experiments, evaluation pipelines.
- HPC/parallel-computing work (CUDA, OpenMP, OpenCL, MPI).
- Any project where "what experiment have I run?" and "what did it tell me?" are recurring questions.

## When NOT to pick

- A standard SaaS feature build — pick `software-eng` instead.
- Pure product work with no research component.
```

- [ ] **Step 2: Commit**

```bash
git add flavors/research/README.md
git commit -m "docs: update research README with absorbed ml/hpc content"
```

---

### Task 8: Run full verification

- [ ] **Step 1: Run verify-template.sh**

```bash
bin/verify-template.sh
```

Expected output:
```
OK: shellcheck (or SKIP if not installed)
OK: flavor (none)
OK: flavor research
OK: flavor software-eng
OK: research rules
OK: software-eng rules
OK: research HPC skills
OK: duplicated rules identical
ALL OK
```

- [ ] **Step 2: Test edge case — invalid flavor name rejected**

```bash
bin/init-project.sh /tmp/test-bad --flavor ml 2>&1 | grep -q "unknown flavor" && echo "correctly rejected"
```

- [ ] **Step 3: Fix any failures, re-run verification**

If any step fails, diagnose and fix before proceeding.
