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
| Always-loaded prose does not grow, and its cap equals the measured size (a shrink lowers the cap in the same PR) | `bin/always_loaded_prose.py` | check: `bin/check` step "always-loaded prose cap" fails over and under the cap (#303) |
| Skill listings stay within their token budget | `bin/skill_listing_weight.py` | check: `bin/check` step "skill-listing token weight" |
| No trailing whitespace or conflict markers | `bin/check` | check: `git diff --check` in `bin/check` |
| Graders run on their pinned model and effort | `bin/factory` | check: `bin/check` step "factory grader model and effort" |
| Release only from a verified HEAD | `bin/release.sh` | script: `bin/release.sh` refuses without a clean verify-loam run |
| One behavior change per session | `AGENTS.md` rule 5 | prose (judgment) |
| Rendered content stays generic | `AGENTS.md` rule 2 | prose (judgment) |
| Verification searches are case-insensitive and repository-wide | `AGENTS.md` Gotchas | prose (judgment) |
| pstack planning, review and judgment roles, hardest tasks and arena runners run on Opus xhigh; implementation and exploration roles on Opus high (Opus 5.5 works well at high; subagent effort leaves the lead's prompt cache alone) | owner ruling 2026-10-19; `~/.claude/rules/pstack-models.md`, outside the repo | setting: that rule file, edited by hand, since a `/pstack:setup-pstack` re-run reverts effort-only changes (`seed/docs/WORKERS.md.jinja` pstack) |
| A project's `verify-<project>` skill proves on the real target; a step run on a stand-in stays marked unverified until it runs there. Renders without pstack keep `/run-skill-generator` (pstack scope ruling 2026-10-18: Loam and distbench) | owner ruling 2026-10-19; `seed/AGENTS.md.jinja` Commands | prose (judgment) |
| A project with costly concurrency keeps a pstack formal verification skill for its single costliest property | owner ruling 2026-10-19; `seed/docs/WORKERS.md.jinja` pstack | prose (judgment) |
| `/pstack:poteto-mode` only for a contested design, concurrency, or a cross-cutting change; small or obvious edits go straight to one worker (pilot: 1.9x cost, no quality gain, #236) | owner ruling 2026-10-19; `seed/docs/WORKERS.md.jinja` pstack | prose (judgment) |
| A project can opt out of the session-memory system with the Copier question `memory` (default `true`): `false` renders none of its hooks, hook registration, tools or prose, and `bin/sync-project --data memory=false` carries the answer. Reason: distbench keeps its no-hooks harness | owner ruling 2026-10-19; `copier.yml`, `docs/COPIER.md` | prose; the verify-loam render recipe `render-memory` proves a render |
| Fable and Codex review finished work read-only; an Opus worker confirms or rejects each finding and fixes only the confirmed ones | owner ruling 2026-10-19; `seed/docs/WORKERS.md.jinja` Roles | prose (judgment) |
| A worker checks each claim against a command output or file read in its session; stops and says so when a task cannot be done or a check looks wrong, never weakening or working around it; and opens a PR body with a plain paragraph on how the change works and why it is correct. The factory worker already has the first two (`bin/factory.d/_common.md:9,11`); factory PRs do not yet carry the paragraph (#330) | owner ruling 2026-10-21 (#329); `seed/docs/WORKERS.md.jinja` Roles | prose (judgment) |
| Factory ticket lint accepts a `## Comments` section, and only as the last section | owner ruling 2026-10-19; `docs/factory/CONTRACT.md` ticket contract, item 11 | check: `bin/tests/test_factory_ticket_sections.py` in `bin/check` step "pytest" |
| Agents and workers invoke the installed pstack copies on their own judgment; the lead's session never runs them inline and names them in briefs; the owner types `/pstack:<name>` to read output | owner ruling 2026-10-20; `seed/CLAUDE.md.jinja` | prose (judgment) |
| Every session, on the Mac and jhaveris, in Loam and DistBench, interactive or headless, moves to a fresh session at about 450K context (replaces the 24 Oct 250K figure, which was meant only for the jhaveris agents) | owner ruling 2026-10-26; global `~/.claude/CLAUDE.md` Context, outside the repo | setting: `~/.claude/hooks/context-handoff.sh` (UserPromptSubmit, `THRESHOLD = 450_000`) on both hosts adds an advisory note to interactive sessions; headless factory runs compact at 450K through the factory's own per-run settings (owner ruling 2026-10-26, built in unit U9, #348); until then headless sessions get only the CLAUDE.md line |
| A Loam capability reaches DistBench by a tailored transfer, one capability at a time, merged so DistBench's own instructions, rules, workflows, skills, operating procedures and learnings survive; `bin/sync-project` output is a diff source, not the delivery | owner ruling 2026-10-26; `docs/SYNC.md` | prose (judgment) |
| Snapshots of unpushed work live in a private archive repo, never as tags on the public Loam origin (they leak unlicensed files and make Copier record `archive/...` as the version) | owner ruling 2026-10-26 | prose until the archive-tag unit adds its check |
| Research-lane items are decided one at a time against how DistBench actually runs and builds, not built or parked wholesale; marketing material is out of scope | owner ruling 2026-10-26; `docs/BACKLOG.md` | prose (judgment) |
| The native-factory campaign (#102 and its children) is parked: no agent builds or reopens its tickets, and renders stop shipping `.loam/runtime` or `docs/runtime` | owner ruling R6 2026-10-25; `docs/archive/architecture-working/tickets/README.md` | `bin/tests/test_render_smoke.py` `test_factory_runtime_does_not_render` |
| The template sandbox runs `gh` outside (inside the macOS sandbox it fails TLS); `git push`, `git fetch` and `git pull` stay sandboxed (2d6070e's git exclusions are not ported) | owner ruling P8 2026-10-26; `seed/.claude/settings.json` `sandbox.excludedCommands`, `seed/docs/HARNESS.md.jinja` Accepted risks | `bin/tests/test_render_smoke.py` `test_sandbox_excludes_gh_but_not_git` |

## Checkable, not yet enforced

Mistakes that have a cheap check but no enforcer yet, each tracked as an issue.
Move a row into the table above when its check lands.

| Mistake | Evidence | Issue |
|---------|----------|-------|
| `cmd \| grep -q` or `\| head` under `pipefail`, where the early exit fails the pipe | 687fc04, b086ef1, a2ec7df; live in `bin/factory` `precondition_lines` | #279 |
| bash 4 or GNU-only forms that break on macOS bash 3.2 and BSD tools | c29ef01, dfd7f3b, 0171ae5, 4c008a2; live in `bin/factory` `build_evidence` (`mapfile`) | #280 |
| Docs name paths that no longer exist | 40297f1, 3fc894f, c9ccc45 | #281 |
| Trailing whitespace in a new file not yet added passes locally, then fails in CI | `git diff --check` in `bin/check` reads only tracked files | #282 |
