# Session Guardrails

> Always loaded. Behavioral constraints derived from usage-report analysis (2026-05-20).
> These address the three most common friction categories: premature execution,
> over-engineering, and unsanctioned edits.

## 1. Workflow Ordering

Run `/validate` before committing or pushing — that is the required gate. The
correct sequence is:

**Implement → `/validate` → `/commit` → `/pr`**

`/session-critique` is available to invoke manually when you want adversarial
review; it is **not** required before commit and does not auto-run. If `/ship`
is available, it runs critique → validate → commit → PR when you choose it.

See also: `workflow.md` §6 (Pipeline Gate) for the validation loop protocol.

## 2. Plan vs Execute

When asked to produce a plan or handoff document, do NOT begin executing tasks
or creating task lists until the user explicitly approves execution. "Write a plan"
means ONLY write the plan. Do not create TaskCreate calls, do not start implementing,
do not scaffold files. Stop after presenting the plan and wait.

See also: `workflow.md` anti-pattern #1.

## 3. Avoid Over-Engineering

Prefer the simplest solution that meets the requirement. Do not add extra
deliverables, subcommands, or verbose surgical-change preambles unless asked.
When in doubt, ask before expanding scope. One clean solution beats three options
with tradeoff matrices.

## 4. Settings Protection

Never modify or revert the user's `settings.json` beyond what a plan explicitly
specifies. Never re-apply settings changes without asking. If a direct JSON edit
tool fails, use a `python3 -c` workaround rather than silently reverting to a
prior state.

## 5. Skill Placement

Place `/commit`, `/pr`, and other repo workflow skills inside the git repo
(under `.claude/skills/`), not at user level (`~/.claude/skills/`). Default to
generic-core placement rather than duplicating skills across flavors.

## 6. Context Freshness

At session end, check these files for staleness before committing:
- `CLAUDE.md` — does the reference table match the actual rules that exist?
- Active `CONTEXT.md` files — do they reflect current directory contents?
- `known-issues.md` — any new gotchas discovered this session?
- Relevant rule files — if a convention changed, update the rule, not just the code.

Anti-pattern: "I'll update the docs later" — you won't. Update in the same session.
