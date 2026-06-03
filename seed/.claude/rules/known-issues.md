# Known Issues & Gotchas

> Always loaded. Add active guardrails here to prevent recurring mistakes.
> Keep entries actionable — each should describe what NOT to do and why.

## Claude Code hooks receive JSON on stdin, not env vars

**What:** Hooks receive a JSON envelope on stdin (`{"tool_name": "Write", "tool_input": {...}}`). There is no `CLAUDE_TOOL_NAME` environment variable.
**Don't:** Use `TOOL_NAME="${CLAUDE_TOOL_NAME:-}"` or any env-var-based tool detection in hooks.
**Do:** Parse `tool_name` from the JSON envelope: `TOOL_NAME=$(python3 -c "import sys,json; print(json.loads(sys.stdin.read()).get('tool_name',''))" <<< "$INPUT" 2>/dev/null)`. See `pre-commit-gate.sh` for the reference pattern.
**Why:** Two research hooks (`validate-experiment-config.sh`, `protect-results.sh`) were completely inert for months because they read an env var that doesn't exist. Fixed in the 16-bug session (2026-05-28).

## Skill Tiering Convention (Session I)

**What:** Skills are tiered by `auto-activate` field to control auto-invocation.
**Don't:** Add new skills without deciding their tier first. Don't leave specialized/heavy skills at default (auto-activate: true).
**Do:** Core workflow skills (agent-team, align-prompt, catchup, commit, feature-dev, fix-bug, gen-spec, handoff, multi-review, pr, scaffold-context, ship, validate) keep default (no `auto-activate` field). Specialized skills (auto-phase, create-skill, critique-swarm, diagrams, dream, grill-with-docs, improve-codebase-architecture, plan-review-invoke, render-gate, researcher, session-critique, techdebt, template-sync) use `auto-activate: false` — user invokes with `/skill-name`. (`session-critique` was moved to manual-only on 2026-06-03 by user request — it runs adversarial review on demand, not before every commit.)
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

## Upstream skill adoption: verify all linked files exist

**What:** When replacing skill files with upstream originals, the new SKILL.md may reference sibling `.md` files (e.g., `[tests.md](tests.md)`) that weren't pulled locally.
**Don't:** Adopt a SKILL.md without checking that every relative markdown link in it resolves to an existing local file.
**Do:** After replacing, run: `grep -oE '\([^)]+\.md\)' SKILL.md | tr -d '()' | while read f; do test -f "$f" || echo "MISSING: $f"; done`
**Why:** In the Pocock upstream replacement (2026-05-23), 6 broken links were caught only by Wave 3 self-critic. TDD's SKILL.md linked to tests.md, mocking.md, etc. that hadn't been fetched.

## Verification greps must be case-insensitive

**What:** When replacing a string (model ID, skill name, etc.) across the repo, the verification `grep` that confirms "zero remaining" can give a false all-clear if it's case-sensitive.
**Don't:** Write `grep -rn 'old-string' seed/` as the verification step. Don't scope the grep to only the file where the bug was reported.
**Do:** Always use `grep -rni 'old-string' seed/` (case-insensitive, repo-wide). For model IDs, also check prose variants (e.g., `GPT-5.4` vs `gpt-5.4`).
**Why:** In the 16-bug fix session (2026-05-28), `grep -rn 'gpt-5\.4'` passed but 5 uppercase `GPT-5.4` survived. Similarly, `/experiment-audit` was fixed in one file but 7 references survived in other files. The session critique caught both.

## Copier `--trust` flag required for this template

**What:** This template uses `_tasks` in `copier.yml` (post-generation shell commands). Copier refuses to run tasks without `--trust`.
**Don't:** Write `uvx copier copy gh:samyakjhaveri/loam ./proj` in docs or handoffs without `--trust`.
**Do:** Always include `--trust`: `uvx copier copy --trust gh:samyakjhaveri/loam ./proj`. For `copier update`, also use `--trust`.
**Why:** Without `--trust`, the research flavor overlay, git init, and seed directory creation all silently skip, producing an incomplete project.

## Count skills by SKILL.md, not by directory

**What:** A skill is a directory containing a `SKILL.md`. Some directories under `skills/` are support bundles, not skills — e.g. `seed/_research/skills/shared-references/` holds shared reference docs and has NO `SKILL.md`.
**Don't:** Count skills with `ls -d seed/.../skills/*/ | wc -l` — it counts support directories as skills, inflating the number.
**Do:** Count with `find seed/.../skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l`. (Core `seed/.claude/skills/` = 26; research `seed/_research/skills/` = 18 skills + 1 `shared-references/` support dir = 19 raw dirs.)
**Why:** In the visual-overview session (2026-05-31), the raw `ls -d */` count reported 19 research skills; the doc was "corrected" 18→19 and three reviewers (incl. two Wave 3 agents) confirmed it — all using the same flawed command. The true count is 18. A count is only as trustworthy as the definition baked into the command; when every reviewer shares one method, they share its blind spot.

## `paths:` frontmatter fires on Read, not Write

**What:** A rule's `paths:` frontmatter auto-loads it only when Claude **reads** a file matching the glob. It does NOT fire on Write/create (Claude Code [#23478](https://github.com/anthropics/claude-code/issues/23478), closed `NOT_PLANNED` — permanent behavior).
**Don't:** Path-scope a rule whose trigger is *authoring a new file* (e.g., `L0-budget` for a fresh `CLAUDE.md`, `context-md-anatomy` for a new `CONTEXT.md`, `naming-conventions` for creating files). Scoping those makes them absent at the exact moment they're needed, because creating a file is a Write with no prior Read.
**Do:** Keep authoring/creation rules always-loaded (no `paths:`) and indexed in `CLAUDE.md`. Only path-scope rules whose trigger maps to a real file-**read** (e.g., `stage-contract` → reading the `validate`/`feature-dev`/`fix-bug` skill files). When in doubt, ask: "does this rule's trigger involve reading an existing file, or writing a new one?"
**Why:** In the path-specific-rules session (2026-06-01), a 5-agent plan review caught the original plan over-applying `paths:` to all 7 of its candidate on-demand rules; it was narrowed to the 3 read-triggered ones (commit `e039c78f`). The other 4 — `L0-budget`, `context-md-anatomy`, `naming-conventions`, `PROJECT-BACKGROUND` — stay always-loaded because their trigger is a Write (authoring) or no file-read at all. (Separately, `validation-loop` was already path-scoped before this work and is not part of that count.)
