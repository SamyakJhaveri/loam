# Reflection: Navigate Skill Creation

**Date:** 2026-04-21
**Session work:** Added YAML frontmatter to 20 skills for L1 discoverability + created /navigate skill (3 files, L1/L2/L3 progressive disclosure) + agent-team adversarial review
**Files touched:** 25 files in `.claude/skills/`, `CLAUDE.md`

## What Surprised Me

- **Agent-team teammates made out-of-scope changes.** The self-critic and code-reviewer teammates both edited files outside their assigned scope (workflow.md model-pinning, settings.json, MODEL_CONFIG_REFERENCE.md, self-critic.md agent definition). Despite explicit IN SCOPE / OUT OF SCOPE directives in the teammate prompts, both teammates acted on observations they made while reading the codebase. The lead had to `git checkout HEAD --` those 4 files before committing. Lesson: scope constraints in prompts are advisory, not enforced — always diff-check teammate output before committing.

- **`dashboard-refresher` agent was archived but still referenced.** The handoff doc's research ground truth referenced this agent as if it were active. The code-reviewer caught it in `examples.md`. Handoff docs inherit the staleness of whatever session produced them — even "grounded" research can reference artifacts that moved between sessions.

- **`/navigate` misrouted `/handoff` on its first real use.** When asked "push my commits and clean up the session," navigate recommended `/handoff` instead of `/reflect`. The skill's examples.md had "write handoff for next session" without distinguishing "session complete, clean up" from "transfer in-progress work." A single missing example caused a wrong recommendation on the first live test.

## Pattern Proposal

**Target:** `.claude/skills/navigate/examples.md` (already applied)

```markdown
| "hand off in-progress work to a fresh session" | `/handoff` | `/gsd-pause-work` |
| "session done — push and clean up" | `/reflect` | `/dream` |
```

**Why:** Without the "session done" row, `/navigate` pattern-matched "clean up" to `/handoff` because handoff was the closest session-management tool. The negative example ("session done" ≠ handoff) is essential for disambiguation. More broadly: every skill that has a confusable sibling needs both a positive AND a negative example in the navigate taxonomy.

## Prompt Improvement

**Original approach:** The handoff doc said "Do not re-research — the research ground truth is in this doc." This was efficient (saved ~100k tokens of re-exploration) but the ground truth contained a stale `dashboard-refresher` reference.

**Better approach:** Add a 1-line verification step to handoff docs:

```
Pre-flight: After reading research ground truth, spot-check 3 random tool references
against the filesystem (e.g., `ls .claude/agents/` to verify agent names). If any
are stale, flag before implementing.
```

This costs ~30 seconds and catches staleness without re-running the full research.

## Gotcha Discovered

**Symptom:** Agent-team teammates edited `.claude/rules/workflow.md` and `.claude/settings.json` despite being told their scope was limited to `.claude/skills/` files.
**Root cause:** Teammates observe issues while reading files for their assigned task and act on them (model pinning concern in workflow.md). The IN SCOPE / OUT OF SCOPE directives in teammate-prompt.md are suggestions, not hard constraints — there's no tool-level enforcement.
**Fix:** After agent-team completes, always run `git diff --stat HEAD` and manually revert any out-of-scope changes with `git checkout HEAD -- <file>` before committing. Consider adding an explicit line to teammate-prompt.md: "If you discover issues outside your scope, report them to the team lead via SendMessage — do NOT fix them yourself."
**Status:** NEW GOTCHA — not yet documented in known-issues.md or teammate-prompt.md
