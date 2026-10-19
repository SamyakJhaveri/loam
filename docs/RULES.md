# Rules and their enforcers

Each standing rule for Loam work, paired with what fails when an agent breaks it.
"Prose" means nothing fails; prefer a check, and keep prose for judgment calls.
When the owner corrects an agent, fix the mistake and add or update its row here.
If the row already says "prose" and the rule is checkable, add the check in the same change.
Drop a row once its mistake cannot happen.

| Rule | Home | Enforcer |
|------|------|----------|
| No em dash (U+2014) in Loam-owned text | owner rule, #237 | check: `bin/check` step "no em dash in Loam-owned text" (exempt paths listed there) |
| Run `bin/check` before every commit | `AGENTS.md` rule 3 | prose, kept by ruling; CI runs `bin/check` on every push and PR, and the GitHub ruleset "main requires CI" gates `main` |
| Commit identities are public or noreply | `bin/ip-sweep.sh` | check: `bin/check` step "commit identities" |
| A plugin file change bumps its version | `bin/plugin_versions.py` | check: `bin/check` step "plugin versions" |
| Skills and agents name only paths, skills and agents that exist | `bin/check` | check: `bin/check` step "skill and agent frontmatter + references" |
| Always-loaded prose does not grow | `bin/always_loaded_prose.py` | check: `bin/check` step "always-loaded prose cap" |
| Skill listings stay within their token budget | `bin/skill_listing_weight.py` | check: `bin/check` step "skill-listing token weight" |
| No trailing whitespace or conflict markers | `bin/check` | check: `git diff --check` in `bin/check` |
| Graders run on their pinned model and effort | `bin/factory` | check: `bin/check` step "factory grader model and effort" |
| Release only from a verified HEAD | `bin/release.sh` | script: `bin/release.sh` refuses without a clean verify-loam run |
| One behavior change per session | `AGENTS.md` rule 5 | prose (judgment) |
| Rendered content stays generic | `AGENTS.md` rule 2 | prose (judgment) |
| Verification searches are case-insensitive and repository-wide | `AGENTS.md` Gotchas | prose (judgment) |

## Checkable, not yet enforced

Repeated mistakes found by the `/pstack:correct` pass of 2026-10-19.
Each has a cheap check; none is built yet.

| Mistake | Evidence | Live instance | Cheapest check |
|---------|----------|---------------|----------------|
| `cmd \| grep -q` or `\| head` under `pipefail`, where the early exit fails the pipe | 687fc04, b086ef1, a2ec7df | `bin/factory:1869` | grep tracked `pipefail` shell files for a pipe into `grep -q` or `head`; capture output first instead |
| bash 4 or GNU-only forms that break on macOS bash 3.2 and BSD tools | c29ef01, dfd7f3b, 0171ae5, 4c008a2 | `bin/factory:1224` (`mapfile`) | grep tracked shell files for `mapfile`, `readarray`, `xargs -r`, `stat -c`, `timeout`, `grep -P`; or a macOS CI job |
| Docs name paths that no longer exist | 40297f1, 3fc894f, c9ccc45 | not measured | run the `bin/check` path check on `docs/**/*.md` (not `docs/archive/`) and `seed/docs/` |
| Trailing whitespace in a new file not yet added passes locally, then fails in CI | blast-radius pass of 2026-10-19 | `bin/check` `git diff --check` steps skip untracked files | add `git diff --check --no-index /dev/null <file>` for each `git ls-files --others --exclude-standard` file |
