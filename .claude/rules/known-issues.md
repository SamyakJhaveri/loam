# Known Issues & Gotchas

> Always loaded. Add active guardrails here to prevent recurring mistakes.
> Keep entries actionable — each should describe what NOT to do and why.

## Skill Tiering Convention (Session I)

**What:** Skills are tiered by `auto-activate` field to control auto-invocation.
**Don't:** Add new skills without deciding their tier first. Don't leave specialized/heavy skills at default (auto-activate: true).
**Do:** Core workflow skills (commit, validate, fix-bug, feature-dev, catchup, navigate, karpathy-guidelines, security, scalability, frontend-design, handoff, pr, multi-review, know-me) keep default. Specialized skills use `auto-activate: false` — user invokes with `/skill-name`.
**Why:** With 60+ skills competing for auto-invocation, false positives waste tokens and confuse sessions. See `.claude/skills/create-skill/reference.md:19-31` for the invocation control matrix.

## agent-team directory/name mismatch

**What:** `.claude/skills/agent-team/` directory contains `name: creating-agent-teams` in SKILL.md.
**Don't:** Assume directory name = skill name.
**Do:** Fix this by renaming the `name:` field to `agent-team` (matching directory per convention in `reference.md:9`).
**Why:** Convention says name must match directory name. This is a pre-existing inconsistency.
