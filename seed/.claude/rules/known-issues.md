# Known Issues & Gotchas

> Always loaded. Add active guardrails here to prevent recurring mistakes.
> Keep entries actionable — each should describe what NOT to do and why.

## Skill Tiering Convention (Session I)

**What:** Skills are tiered by `auto-activate` field to control auto-invocation.
**Don't:** Add new skills without deciding their tier first. Don't leave specialized/heavy skills at default (auto-activate: true).
**Do:** Core workflow skills (catchup, commit, create-skill, dream, feature-dev, fix-bug, handoff, karpathy-guidelines, know-me, multi-review, pr, reflect, researcher, scaffold-context, scalability, security, techdebt, template-sync, validate) keep default. Specialized skills use `auto-activate: false` — user invokes with `/skill-name`.
**Why:** With 60+ skills competing for auto-invocation, false positives waste tokens and confuse sessions. See `.claude/skills/create-skill/reference.md:19-31` for the invocation control matrix.

## YAML colons in skill descriptions

**What:** Unquoted colons in description strings (e.g., `4 waves: basics`) break YAML parsers.
**Don't:** Write single-line descriptions containing colons without quoting.
**Do:** Use folded scalar (`description: >`) for multi-sentence descriptions containing colons, or quote the string.
**Why:** Claude Code may use regex matching (tolerant), but strict YAML parsers (linter, CI tools) will reject the file.
