---
name: workflow-ref
description: "Skill/agent reference table, agent teams, thinking levels, atomic task decomposition, memory hygiene, course correction"
---

# Workflow Reference (moved from workflow.md to reduce always-loaded overhead)

## Skill & Agent Quick Reference

Use these at the right phase — don't skip them, don't over-invoke them.

| When | Skill / Agent | Command | What it does |
|------|--------------|---------|-------------|
| After any code/spec change | `/validate` | `/validate` (full) or `/validate quick` | 4-wave validation; pre-commit gate requires waves 1-3, wave 4 optional |
| Full post-session validation (context-clean) | `verification-lead` agent | Invoke via Agent tool | Runs all 4 waves internally; returns single report |
| Before merging or after multiple file changes | `/review` | `/review` | 4-agent parallel code review (style, correctness, security, perf) |
| Launching an eval batch | `/eval-run` | `/eval-run rodinia cuda-to-omp` | Param collection → pre-flight → execute → analyze |
| After eval completes OR spec count changes | `dashboard-refresher` agent | Invoke via Agent tool | Fixes hardcoded numbers in all 12 viz files |
| Starting a sprint session | `/session-start` | `/session-start 9` | Extracts prompt, checks git, verifies prerequisites |
| New benchmark suite | `/gen-spec` | `/gen-spec xsbench` | Full guided spec generation wizard |
| Bug fix workflow | `/fix-bug` | `/fix-bug "description"` | Reproduce → diagnose → fix → verify loop |
| New feature | `/feature-dev` | `/feature-dev "name"` | Explore → plan → implement → verify |
| Stress-test research claims | `/grill-research` | `/grill-research` | Adversarial interrogation of paper claims |
| Simulate peer review | `/paper-review-sim` | `/paper-review-sim` | Multi-reviewer simulation (SC/ICSE style) |
| Draft SC26 paper sections | `paper-assembly-team` agent | Invoke via Agent tool | 3 parallel sub-agents gather eval data, related work, methodology; lead synthesizes |
| Overnight LLM eval | `/overnight-eval` | `/overnight-eval rodinia` | tmux-based long-running eval batch |
| Explore failure hypotheses | `/hypothesis-tree` | `/hypothesis-tree "why X fails"` | Structured hypothesis tree with evidence |
| Verify citations | `/cite-check` | `/cite-check` | Check paper citations against source data |
| Catch up on recent work | `/catchup` | `/catchup` | Summarize recent git/result changes |
| Interpret eval results | `/interpret-results` | `/interpret-results` | Hypothesis-first result interpretation |

**Critical ordering:** Implement → `/review` → `/validate` → commit → push → `dashboard-refresher` (if eval or spec data changed)

## Agent Teams

> Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json `env`.

Agent Teams spawn independent Claude Code sessions (teammates) with persistent context
windows, cross-talk, and shared task lists. Use `/agent-team` skill for full workflow,
scenario templates, mandatory directives, and context relay protocol.

**Quick decision:** Subagents for quick independent tasks (~30s-2min, report and done).
Agent teams for extended coordinated work (~5-30min, teammates share findings).

**Keep using subagents for:** `/validate` waves, `/review`, exploration, single-file work.
**Use `/agent-team` for:** multi-model analysis, paper drafting, failure investigation,
taxonomy building, post-batch analysis, augmentation audits.

## Thinking Levels

| Level | When to use |
|-------|-------------|
| `think` | Simple lookups, single-file edits |
| `think hard` | Multi-file changes, debugging |
| `think harder` | Architecture decisions, complex refactors |
| `ultrathink` | Security review, complex planning, adversarial analysis |

## Atomic Task Decomposition (for multi-step plans)

When facing a large plan (fix N issues, retest, update dashboard, push):

1. **Audit first** — Evaluate what's actually done vs. claimed. Check with real data.
2. **Decompose** — Each session gets ONE objective with concrete acceptance criteria.
3. **Map dependencies** — Which sessions are sequential? Which can run in parallel?
4. **Write session plan files** — Store in `docs/session_plans/session_N_<desc>.md`. Each must include:
   - Copy-pasteable Claude Code prompt (self-contained, all context included)
   - Files reference table (paths, line numbers, current content, what changes)
   - Cross-reference sources (so the session verifies against source, not docs)
   - Verification commands with expected output
   - Commit message template
   - Troubleshooting guide for likely failures
   - Success criteria checklist
5. **`/clear` between sessions** — Fresh context for each atomic task.
6. **Gate on verification** — Don't commit until verification passes with ACTUAL data.

**Why this works:** Context management IS quality management. A session doing 1 thing well
uses all its context budget on that thing. Errors don't compound across sessions. Each
commit is one verified, complete unit of work. Independent sessions can run in parallel.

## Memory Hygiene

Memory files are write-only by default — they grow but never get maintained.
Use `/dream` to consolidate periodically.

- **`/dream audit`** — Read-only health report (run weekly or when memory feels stale)
- **`/dream`** — Full 4-phase consolidation with user approval gate
- **`/dream prune <file>`** — Targeted cleanup of one file

### When to consolidate
- After major milestones (sprint phase completion, paper draft, eval batch)
- After 5+ sessions without consolidation
- When `/session-start` reports memory staleness
- Before long breaks (>3 days between sessions)

### Memory file conventions
- MEMORY.md: index only, <200 lines, no content — just `- [Title](file.md) — hook`
- Topic files: proper frontmatter (name, description, type)
- Prefer cross-references over duplication (point to `.claude/rules/` for canonical content)
- Convert all dates to absolute (YYYY-MM-DD) — relative dates rot immediately
- Staleness tiers: permanent (1) > active (2) > completed (3) > historical (4) > stale (5)

## Course Correction

When implementation goes wrong, don't keep pushing. Instead:
> "Stop. This isn't working. Re-plan from scratch knowing what we know now."

Re-enter plan mode, reassess assumptions, and get approval for the new approach.
