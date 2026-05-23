# Known Issues & Gotchas

> Always loaded. Add active guardrails here to prevent recurring mistakes.
> Keep entries actionable — each should describe what NOT to do and why.

## Skill Tiering Convention (Session I)

**What:** Skills are tiered by `auto-activate` field to control auto-invocation.
**Don't:** Add new skills without deciding their tier first. Don't leave specialized/heavy skills at default (auto-activate: true).
**Do:** Core workflow skills (agent-team, catchup, commit, feature-dev, fix-bug, gen-spec, handoff, multi-review, pr, scaffold-context, session-critique, ship, validate) keep default. Specialized skills (auto-phase, create-skill, critique-swarm, dream, render-gate, researcher, techdebt, template-sync) use `auto-activate: false` — user invokes with `/skill-name`.
**Why:** With 60+ skills competing for auto-invocation, false positives waste tokens and confuse sessions. See `.claude/skills/create-skill/reference.md:19-31` for the invocation control matrix.

## YAML colons in skill descriptions

**What:** Unquoted colons in description strings (e.g., `4 waves: basics`) break YAML parsers.
**Don't:** Write single-line descriptions containing colons without quoting.
**Do:** Use folded scalar (`description: >`) for multi-sentence descriptions containing colons, or quote the string.
**Why:** Claude Code may use regex matching (tolerant), but strict YAML parsers (linter, CI tools) will reject the file.

## Copier resolves from git tags, not HEAD

**What:** `copier copy gh:samyakjhaveri/loam ./proj` resolves to the latest git tag, not the latest commit on main. If the tag is stale, new features won't land in bootstrapped projects.
**Don't:** Push new features without creating a corresponding release tag. Don't write smoke-test commands that assume HEAD content ships.
**Do:** After pushing significant changes, bump `VERSION`, create a tag (`git tag v<version>`), and push the tag (`git push origin v<version>`). Use `bin/release.sh <version>` which automates this.
**Why:** In v3.1.0 release, the diagrams skill and drawio MCP were committed and pushed but the `v3.0.0` tag pointed 28 commits behind. Smoke tests failed because Copier fetched the old tag.

## Copier `--trust` flag required for this template

**What:** This template uses `_tasks` in `copier.yml` (post-generation shell commands). Copier refuses to run tasks without `--trust`.
**Don't:** Write `uvx copier copy gh:samyakjhaveri/loam ./proj` in docs or handoffs without `--trust`.
**Do:** Always include `--trust`: `uvx copier copy --trust gh:samyakjhaveri/loam ./proj`. For `copier update`, also use `--trust`.
**Why:** Without `--trust`, the research flavor overlay, git init, and seed directory creation all silently skip, producing an incomplete project.
