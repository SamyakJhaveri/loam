# Rules and their enforcers

Each standing rule for Loam work, paired with what fails when an agent breaks it.
"Prose" means nothing fails; prefer a check, and keep prose for judgment calls.
When the owner corrects an agent, fix the mistake and add or update its row here.
If the row already says "prose" and the rule is checkable, add the check in the same change.
Keep rows a check enforces, so each enforcer stays findable; drop a row only when its mistake can no longer happen at all.

| Rule | Home | Enforcer |
|------|------|----------|
| No em dash (U+2014), raw or JSON-escaped, in Loam-owned text | owner rule, #237 | check: `bin/check` step "no em dash in Loam-owned text" (exempt paths listed there) |
| Run `bin/check` before every commit | `AGENTS.md` rule 3 | prose, kept by ruling; CI runs `bin/check` after every push and on PRs, and the GitHub ruleset "main requires CI" requires it for PR merges, but an admin push to `main` bypasses it |
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

Mistakes that have a cheap check but no enforcer yet, each tracked as an issue.
Move a row into the table above when its check lands.

| Mistake | Evidence | Issue |
|---------|----------|-------|
| `cmd \| grep -q` or `\| head` under `pipefail`, where the early exit fails the pipe | 687fc04, b086ef1, a2ec7df; live in `bin/factory` `precondition_lines` | #279 |
| bash 4 or GNU-only forms that break on macOS bash 3.2 and BSD tools | c29ef01, dfd7f3b, 0171ae5, 4c008a2; live in `bin/factory` `build_evidence` (`mapfile`) | #280 |
| Docs name paths that no longer exist | 40297f1, 3fc894f, c9ccc45 | #281 |
| Trailing whitespace in a new file not yet added passes locally, then fails in CI | `git diff --check` in `bin/check` reads only tracked files | #282 |
