# Loam v3.0 — Release Checklist

> **For:** Fresh Claude Code session. **Project:** Loam (`/Users/samyakjhaveri/Desktop/loam`). **Date:** 2026-05-22.
> **Branch:** main (commit directly, no feature branches).

## Context

Loam is a Copier template that bootstraps Claude Code projects for researchers and hardcore SWEs. It's at v3.0 and structurally sound (`bin/verify-template.sh` passes). Four bugs need fixing and two files need writing before it can go public. Tool evaluation and skill adoption happen **after** release, not before.

**Goal:** Fix 4 bugs, clean 4 stale artifacts, write 1 README, ship.
**Estimated time:** 1 session (~2 hours).
**Skills to use:** `/validate` before commit, `/commit` for conventional commits.

---

## ~~Step 1: Rewrite LICENSE (CRITICAL)~~ ✅ DONE (commit 15fee966)

~~The current `LICENSE` is from a different project (ParBench). Lines 23-33 reference HPC benchmarks (Rodinia, XSBench, RSBench, mixbench, HeCBench).~~ **Fixed:** Clean MIT license with correct attribution to Samyak Jhaveri.

**File:** `LICENSE`

**Exact replacement content:**
```
MIT License

Copyright (c) 2026 Samyak Jhaveri

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

**Verify:** `wc -l LICENSE` should be 21 lines. `grep -c "ParBench\|Rodinia\|XSBench\|HeCBench\|mixbench\|RSBench" LICENSE` should return 0.

---

## ~~Step 2: Fix seed/README.md.jinja (2 bugs on 1 line)~~ ✅ DONE (commit 95f30b31)

**File:** `seed/README.md.jinja`, line 3

**Current (broken):**
```
> Created from project-template on {{ "%Y-%m-%dT%H:%M:%SZ" | strftime }}. Flavors: {{ flavors | join(", ") }}.
```

**Problems:**
1. References "project-template" instead of "loam"
2. `{{ flavors | join(", ") }}` — `flavors` is undefined in `copier.yml` — render error or empty string

**Exact replacement for line 3:**
```
> Created from [loam](https://github.com/samyakjhaveri/loam) on {{ "%Y-%m-%dT%H:%M:%SZ" | strftime }}. Research flavor: {{ "enabled" if is_research else "disabled" }}.
```

**Verify:**
```bash
grep "project-template" seed/README.md.jinja    # Expected: no results
grep "flavors" seed/README.md.jinja              # Expected: no results
grep "is_research" seed/README.md.jinja          # Expected: 1 result (line 3)
```

---

## ~~Step 3: Clean up stale artifacts~~ ✅ DONE (commit f57246c1)

Delete these files/directories — all are in git history and no longer needed:

```bash
git rm -rf better_use_of_graphify/    # 5 files, ~125KB — research for completed Graphify->CGC+Semble migration
git rm HANDOFF.md                     # References work already done in commit 5e85654a
# (plugin session artifacts already restructured into docs/specs/)
```

Also fix the marketplace README:

**File:** `cultivation/marketplace/README.md`

**Line 1 — replace:**
```
# seed-skills
```
**With:**
```
# Marketplace Skills
```

**Lines 10-12 — replace:**
```
# From a project bootstrapped from this template:
/plugin marketplace add /path/to/loam/seed-skills
/plugin install team-deliberation    # or: meta-improvement, helpers, business-process
```
**With:**
```
# From a project bootstrapped from this template:
/plugin marketplace add /path/to/loam/cultivation/marketplace
/plugin install team-deliberation    # or: meta-improvement, helpers, business-process
```

**Verify:**
```bash
ls better_use_of_graphify/ 2>/dev/null && echo "FAIL: directory still exists" || echo "OK"
ls HANDOFF.md 2>/dev/null && echo "FAIL: file still exists" || echo "OK"
ls docs/specs/ >/dev/null && echo "OK: docs/specs/ exists" || echo "FAIL: docs/specs/ missing"
grep "seed-skills" cultivation/marketplace/README.md && echo "FAIL: old path still present" || echo "OK"
```

---

## ~~Step 4: Write root README.md~~ ✅ DONE (commit 7c2fbb6d)

~~The repo has no `README.md` at root — GitHub landing page is blank. Write one.~~ **Fixed:** 99-line README with feature inventory, quick start, project structure, skill table, and doc index.

**File:** `README.md` (new file at repo root)

**Skeleton — fill in details, keep under 120 lines:**

```markdown
# Loam

A Copier template that bootstraps Claude Code projects with battle-tested skills, hooks, agents, and a structured memory stack. Built for researchers and software engineers working on advanced projects.

## What you get

When you run `copier copy`, Loam generates a project with:

- **21 skills** — feature-dev, fix-bug, commit, validate, ship, multi-review, session-critique, and more
- **7 hooks** — pre-commit validation gate, post-edit test runner, session-start context, audit logging, result immutability, sentinel cleanup, compact recovery
- **Structured memory** — 3-layer routing stack (CLAUDE.md -> CONTEXT.md -> stage contracts) + MCP tools (CodeGraphContext, Semble, Knowledge Graph)
- **Research flavor** (optional) — paper-write, cite-check, eval-run, experiment, hypothesis-tree, and 18 research-specific skills total

## Quick start

\```bash
# Bootstrap a new project
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# With the research flavor
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project  # answer "yes" to is_research

# Pull template updates into an existing project
cd my-project && uvx copier update --trust
\```

## Project structure

\```
loam/
├── seed/                    # Copier subdirectory — everything rendered to projects
│   ├── .claude/             # Skills, agents, hooks, rules, settings
│   │   ├── skills/          # 21 core skills
│   │   ├── agents/          # Specialized subagents
│   │   ├── hooks/           # Pre-commit gate, post-edit tests, etc.
│   │   └── rules/           # Workflow, guardrails, known issues
│   ├── _research/           # Research flavor overlay (optional)
│   │   ├── skills/          # 18 research-specific skills
│   │   └── rules/           # Research consistency, memory rules
│   └── *.jinja              # Template files (CLAUDE.md, README.md, etc.)
├── cultivation/             # Skill lifecycle management
│   ├── marketplace/         # Cut skills — installable bundles
│   ├── retired/             # Dissolved skills (reference material)
│   └── wip/                 # Skills in development
├── soil/                    # Knowledge base (JVC, foundation, playbooks)
├── bin/                     # verify-template.sh, template-sync.sh, etc.
├── docs/                    # Template documentation
└── copier.yml               # Template config
\```

## Skill inventory

### Core skills (shipped to every project)

| Skill | Purpose |
|-------|---------|
| `/feature-dev` | Feature development: explore -> plan -> implement -> verify |
| `/fix-bug` | Bug fix: reproduce -> diagnose -> plan -> fix -> verify |
| `/validate` | Pipeline gate — 3-wave checks before commit |
| `/ship` | Full pipeline: critique -> validate -> commit -> PR |
| `/commit` | Conventional commit with staging |
| `/pr` | Push and open GitHub PR |
| `/multi-review` | 4-reviewer parallel code review |
| `/session-critique` | Adversarial self-review before commit |
| `/catchup` | 30-second session bootstrap briefing |
| `/handoff` | Structured handoff for agent continuity |
| `/gen-spec` | Guided specification wizard |
| `/researcher` | Deep research with web search and synthesis |
| `/agent-team` | Coordinated multi-agent teams |
| `/critique-swarm` | 4-agent adversarial critique |
| `/auto-phase` | Autonomous multi-phase execution |
| `/dream` | Memory consolidation |
| `/techdebt` | Codebase tech debt scan |
| `/scaffold-context` | Author CONTEXT.md routing files |
| `/create-skill` | Create new skills |
| `/template-sync` | Sync assets with template buffer |
| `/render-gate` | TDD for Copier template files |

### Research-only skills (when `is_research=true`)

paper-write, cite-check, eval-run, experiment, hypothesis-tree, interpret-results, augment-test, auto-paper-improvement-loop, paper-review-sim, paper-claim-audit, rebuttal, citation-audit, overnight-eval, post-eval, cuda-omp-translator, hpc-code-reviewer, grill-research, eval-grader

## Documentation

- `docs/BOOTSTRAP.md` — First-session setup guide
- `docs/MEMORY.md` — Memory stack architecture
- `docs/COPIER.md` — Template configuration details
- `docs/FLAVORS.md` — Flavor system documentation
- `docs/SYNC.md` — Template sync workflow
- `docs/ASSET-LAYERS.md` — Asset organization

## Requirements

- [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`pip install copier` or `uvx copier`)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

## License

MIT — see [LICENSE](LICENSE).
```

**Verify:**
```bash
test -f README.md && echo "OK: README exists" || echo "FAIL"
wc -l README.md   # Should be ~100-120 lines
```

---

## Step 5: Verify and commit

Run these in order:

```bash
# 1. Template verification
bin/verify-template.sh
# Expected: ALL OK

# 2. Test fresh copier copy (default flavor)
tmpdir=$(mktemp -d) && uvx copier copy --trust --defaults . "$tmpdir/test-default" && echo "OK: default render" && rm -r "$tmpdir"

# 3. Test fresh copier copy (research flavor)
tmpdir=$(mktemp -d) && uvx copier copy --trust --defaults -d is_research=true . "$tmpdir/test-research" && echo "OK: research render" && rm -r "$tmpdir"

# 4. Test copier update (exercises conflict resolution + .copier-answers.yml merge)
tmpdir=$(mktemp -d) && uvx copier copy --trust --defaults . "$tmpdir/test-update" && cd "$tmpdir/test-update" && uvx copier update --trust --defaults && echo "OK: copier update" && cd - && rm -r "$tmpdir"
```

Then: `/validate` -> `/commit` -> make the repo public.

**Note on diagrams:** User decided to use Mermaid for any architecture diagrams (no need to evaluate other diagram tools for the release README).

**Commit message:** `chore: release prep — fix LICENSE, README, template bugs, clean stale artifacts`

---

## Must NOT

- Must NOT modify `copier.yml` (no new questions or tasks)
- Must NOT add new skills, hooks, or rules (that's post-release)
- Must NOT modify existing skill files
- Must NOT create feature branches (commit to main)
- Must NOT skip `/validate` before committing
