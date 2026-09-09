## Ticket

~~~~~~~~~~~~ evidence
# S4: prose, recall, and rendered docs

Part of #14

Execution ticket. Blocked on S3 merging and on the judgment-rules decision. Spec: `02-IMPLEMENTATION-SPEC.md` commit 3 (prose) and the docs parts of commits 4 and 5; `03-RECALL-LAYER.md` for frontmatter. Runs alone, after S3, because S3 deleted the contract test that asserted the old hook names in the rendered `CLAUDE.md`.

## Goal and why

Always-on context under 400 tokens per rendered project, with the judgment rules surviving where the decision ticket put them, and every living doc pointing at the two commands. `DESIGN.md` L1, L6, law 5; decision 6 (ratchet), decision 12 (push guard), decision 13 (no path-scoped rules unless recall misses).

## Files owned

- `seed/CLAUDE.md.jinja` (under 12 lines: `@AGENTS.md` plus the Claude gotchas) and `seed/AGENTS.md.jinja` (under 35 lines)
- `seed/docs/`: add `HARNESS.md` (two hooks, both deny lists, two commands, accepted risks, push-guard status by case, `.claude/` protected-path note, the measured listing weight, one line on the owner's global config) and `WORKERS.md` (moved worker prose)
- `seed/_gh_setup.sh` (repository ruleset step via `POST /repos/{owner}/{repo}/rulesets`, no bypass actors, requires the `check` status, prints the outcome)
- `seed/.agents/skills/*/SKILL.md` frontmatter only, and the three marketplace skills' frontmatter, per `03-RECALL-LAYER.md`
- The one `LISTING_BUDGET` default line in `bin/check`, set to the measured three-skill listing weight (decision 6)
- `docs/COPIER.md`, `README.md`, `CONTRIBUTING.md`, root `AGENTS.md` and `CLAUDE.md` (updated to `bin/check` and `bin/release.sh`; keep the `## Agent skills` block, `docs/agents/`, and `docs/adr/`)

Do not touch `settings.json`, hooks, `seed/bin/`, or `seed/.github/` (S3, already merged).

### Addendum (2026-09-07, owner decisions after round 1)

1. Done check 2: keep `fable-session-brief.sh` gated on the model field. Do not make the brief unconditional. Revert the unconditional part of commit b91aca3 (keep the folded judgment-rules text and the budget refit). The second half of done check 2 is met by interactive evidence: the brief fires in an interactive Fable session, where SessionStart carries `model`. The `claude -p` work sample is exempt, because on Claude Code 2.1.263 its startup payload has no model field; say exactly that in measurements.md and the PR body under Unverified.
2. Scope ratified: S4 also owns `docs/archive/` (moving retired living docs there, plus `docs/archive/README.md`), `docs/ASSET-LAYERS.md`, and `seed/docs/decisions/RULINGS.md` (deleted). The judge scores "correct" with these included.
3. Done check 3: `docs/archive/` is exempt from the `verify-template` grep. The checks script already excludes it.
4. Hooks: the only hook file S4 may edit is `seed/.claude/hooks/fable-session-brief.sh`, and only its brief text (decision 15).

## Rows measured

- Always-on bytes and approximate tokens: `cat CLAUDE.md AGENTS.md | wc -c` in a rendered project (baseline 7862 bytes, about 1970 tokens; target under 1600 bytes, under 400 tokens).
- Skill-listing weight after parking: `python3 bin/skill_listing_weight.py --root . --json`.
- Recall test: the 8 scenarios in `03-RECALL-LAYER.md` section 4.

## Done checks

1. Rendered `CLAUDE.md` plus `AGENTS.md` under 1600 bytes; rendered `CLAUDE.md` under 12 lines; rendered `AGENTS.md` under 35 lines.
2. The judgment rules live where the decision ticket put them, with the exact text, and the work sample shows them present for a Fable session.
3. `docs/HARNESS.md` and `docs/WORKERS.md` exist in the rendered project; `grep -rn verify-template docs README.md CONTRIBUTING.md AGENTS.md CLAUDE.md` returns nothing in Loam.
4. The 8 recall scenarios each name the mechanism that fires, and scenarios 1, 2, 4, and 8 were exercised live in a rendered project with the transcript lines quoted in the PR body.
5. `bin/check` `LISTING_BUDGET` equals the measured three-skill weight and that number plus the prose budget are both written in `docs/HARNESS.md` (decision 6 wants both stated).
6. `_gh_setup.sh` ruleset step present, exit status checked, outcome printed; the no-guard cases are stated in `docs/HARNESS.md`.
7. `time bin/check` exits 0; the PR's `check` run is green.
8. Verification protocol below completed; PR body carries the numbers.

## Verification protocol (every execution ticket, before its PR)

1. Measure the rows this ticket owns with the commands in the measurement section of `02-IMPLEMENTATION-SPEC.md`.
2. Work sample: render a project from the branch into a temp dir (`uvx copier copy --trust --defaults --vcs-ref HEAD -d project_name=sample . <dir>`), run the fixed task from `.superpowers/lean-v3/baseline/S0-BASELINE.md` with `claude -p "<task>" --model fable --output-format stream-json --verbose --include-hook-events > sample.jsonl`, then `python3 .superpowers/lean-v3/tools/summarize_sample.py sample.jsonl --check "<the task's own test>"`.
Steps 3 to 6 (frozen checks, fresh-context judge, fixer, push, PR) belong to the loop supervisor; see `loops/DESIGN.md`.

## Decision feeding this ticket (issue 15, closed 2026-09-06)

The Fable judgment rules live in the output of fable-session-brief.sh. Fold them into the brief text (under 400 words), add one line to docs/HARNESS.md about the owner-only global targeted-edits hook, and leave the fable-prompting skill as the long form. Done check 2 is met when the rendered brief contains the rules and the work sample shows them for a Fable session.

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS worktree-clean
PASS always-on-bytes (1125 bytes)
PASS claude-md-lines (9 lines)
PASS agents-md-lines (23 lines)
PASS rendered-docs
PASS no-verify-template-in-prose
PASS listing-budget (448)
PASS gh-setup-ruleset
PASS bin-check-runs (5s)
PASS run-artefacts
SKIP gh-setup-exit-status: needs a human to read seed/_gh_setup.sh and confirm the ruleset call checks its exit status and prints the outcome, and that the no-guard cases are stated in docs/HARNESS.md
SKIP recall-scenarios: needs a human to run the 8 recall scenarios from 03-RECALL-LAYER.md section 4 and quote the transcript lines for scenarios 1, 2, 4, and 8
SKIP judgment-rules-location: needs the judgment-rules decision ticket to say where the rules live, then a human to confirm the exact text and that a Fable work sample sees them
SKIP pr-check-green: needs a pushed branch and a GitHub check run
SUMMARY pass=10 fail=0 skip=4

~~~~~~~~~~~~ evidence

## pr-body.md (worker-authored)

~~~~~~~~~~~~ evidence
# S4: prose, recall, and rendered docs

Closes #24.

A generated project now pays about 282 always-on tokens of prose instead of about 1966, and the
machinery narration it used to carry lives in two read-on-demand docs.
Every living doc in Loam points at `bin/check` and `bin/release.sh`; the spent plans that
routed work through the deleted `bin/verify-template.sh` moved to `docs/archive/`.

## What changed

1. `seed/CLAUDE.md.jinja` is 9 lines: three Claude-only gotchas plus `@AGENTS.md`.
   `seed/AGENTS.md.jinja` is 23 lines. The editing-discipline, invariants, session-continuity,
   and parallel-worker blocks are gone from the always-on file.
2. New `seed/docs/HARNESS.md` (both deny lists, the two hooks, the push guard case by case,
   the always-on budgets, the accepted risks, the owner global-config note) and
   `seed/docs/WORKERS.md` (worktrees, roles, the seven-field `HANDOFF.md`).
   `seed/docs/decisions/RULINGS.md` is deleted; it shipped empty (decision 4).
3. `seed/.claude/hooks/fable-session-brief.sh` now prints the Fable judgment rules, folded
   into the brief, per closed decision 15. It stays gated on the model field. Text only; the
   wiring and `settings.json` are untouched.
4. `seed/_gh_setup.sh` posts a repository ruleset on the default branch: pull request plus the
   `check` status, no bypass actors. The exit status is checked and both outcomes print.
5. `bin/check` `LISTING_BUDGET` default drops from 2750 to 448, the measured plugin listing
   weight. Both that number and the 400-token prose budget are stated in `docs/HARNESS.md`
   (decision 6).
6. Skill frontmatter per `03-RECALL-LAYER.md`: `plan-review` gains
   `disable-model-invocation: true`; `catchup` loses a redundant parenthetical.
7. `README.md`, `CONTRIBUTING.md`, root `AGENTS.md`, `docs/COPIER.md`, and
   `docs/ASSET-LAYERS.md` now name `bin/check`. Nine spent plan and spec docs moved to
   `docs/archive/`. Four dead cross-references were repaired at the same time.

## Numbers

| Row | Before | After |
|---|---|---|
| Always-on bytes (rendered `CLAUDE.md` + `AGENTS.md`) | 7862 | 1125 |
| Always-on tokens | ~1966 | ~281 |
| Rendered `CLAUDE.md` lines | 37 | 9 |
| Rendered `AGENTS.md` lines | 62 | 23 |
| Seed skill listing | 143 tokens | 131 tokens |
| `sam-cc-setup` listing | 566 tokens | 448 tokens |
| `LISTING_BUDGET` default | 2750 | 448 |
| `verify-template` in living prose | 49 references | 0 |
| `bin/check` wall time | not this ticket's row | 5 s, exit 0 |

Work sample, the fixed S0 task run with `--model fable` in a project rendered from this branch:

| Row | S0 baseline | This branch |
|---|---|---|
| elapsed_seconds | 125.7 | 11.5 |
| turns | 18 | 2 |
| tool_calls | 16 | 1 |
| hook_events | 306 | 14 |
| cost_usd | 1.10 | 0.46 |
| denials | 0 | 0 |
| task check | 1 passed | 1 passed |

Most of that drop belongs to S1 to S3. S4's share is the prose row.

`.superpowers/lean-v3/loops/runs/S4/measurements.md` carries the full tables, the
8-scenario recall walk, and the scenario 2 transcript.

## The Fable brief and `claude -p`

The brief is gated on the session model, per the owner's 2026-09-07 addendum.
On Claude Code 2.1.263 the `claude -p` `SessionStart` payload carries no `model` field, so the
brief does not fire in the work sample. Measured with a hook that dumps its stdin:

```
{"session_id":"...","transcript_path":"...","cwd":"...","hook_event_name":"SessionStart","source":"startup"}
```

Interactive `SessionStart` does carry `model`, which is where the brief fires; the owner
accepts that as the evidence for done check 2. `docs/HARNESS.md` states the `claude -p` gap.

## Unverified

- Scenario 1 (the ruleset blocks a push to `main`). Both branches of the `_gh_setup.sh` call
  were exercised against a stub `gh`, and the JSON payload parses with the right rules and an
  empty `bypass_actors`. The real `POST /repos/{owner}/{repo}/rulesets` needs a GitHub repo,
  which this round must not create.
- Scenarios 4 and 8 (`plan-review` manual-only, `surprise-me` trigger phrases). Verified in the
  frontmatter, not fired: the `sam-cc-setup` plugin resolves from the main checkout, not from
  this branch, so a live fire would test the old frontmatter.
- The PR `check` run. This round never pushes.
- The claim that `bin/release.sh` needs a green CI run on HEAD is read from the script, not
  exercised.
- The brief firing in an interactive Fable session. This round has no interactive session, so
  the owner's interactive evidence is taken as given. The non-interactive side is measured:
  `grep -c 'Judgment rules this harness does not inject' sample.jsonl` returns 0.

~~~~~~~~~~~~ evidence

## Diff (main...HEAD)

~~~~~~~~~~~~ evidence
 AGENTS.md                                                                           | 26 ++++++++++++--------------
 CONTRIBUTING.md                                                                     | 24 ++++++++++++------------
 README.md                                                                           | 43 +++++++++++++++++++++++--------------------
 bin/check                                                                           |  2 +-
 cultivation/marketplace/sam-cc-setup/skills/plan-review/SKILL.md                    | 13 ++++++-------
 docs/ASSET-LAYERS.md                                                                |  6 +++---
 docs/COPIER.md                                                                      |  4 ++--
 docs/archive/README.md                                                              |  5 +++++
 docs/{ => archive}/specs/2026-09-01-harness-smoke-rig-design.md                     |  0
 docs/{ => archive}/specs/clief-claude-code-plan-mode-handoff.md                     |  0
 docs/{ => archive}/specs/routing-doc-repair-plan.md                                 |  0
 docs/{ => archive}/specs/sam-cc-consolidation-design.md                             |  0
 docs/{ => archive}/specs/sam-cc-consolidation-plan.md                               |  0
 docs/{ => archive}/superpowers/plans/2026-08-30-rendered-harness-contract.md        |  0
 docs/{ => archive}/superpowers/plans/2026-09-05-agent-efficiency.md                 |  0
 docs/{ => archive}/superpowers/specs/2026-08-30-rendered-harness-contract-design.md |  0
 seed/.agents/skills/catchup/SKILL.md                                                |  2 +-
 seed/.claude/hooks/fable-session-brief.sh                                           | 20 ++++++++++++++------
 seed/AGENTS.md.jinja                                                                | 61 +++++++++++--------------------------------------------------
 seed/CLAUDE.md.jinja                                                                | 34 +++-------------------------------
 seed/_gh_setup.sh                                                                   | 37 ++++++++++++++++++++++++++++++++++---
 seed/docs/HARNESS.md                                                                | 86 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 seed/docs/WORKERS.md                                                                | 40 ++++++++++++++++++++++++++++++++++++++++
 seed/docs/decisions/RULINGS.md                                                      |  8 --------
 24 files changed, 253 insertions(+), 158 deletions(-)

diff --git a/AGENTS.md b/AGENTS.md
index eb4ee8c..a3bf7c8 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1,4 +1,4 @@
-# AGENTS.md — Loam
+# AGENTS.md - Loam

 > The shared prose home for agents working on Loam.
 > Claude Code imports this file from `CLAUDE.md`. Codex reads it directly.
@@ -25,8 +25,8 @@ uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
 # Pull the latest released template into an existing project.
 cd my-project && uvx copier update --trust

-# Verify Loam before a commit or release.
-bin/verify-template.sh
+# Check Loam before a commit or release.
+bin/check
 ```

 ## Layout
@@ -35,11 +35,11 @@ bin/verify-template.sh
 |------|---------|
 | `seed/` | Copier source. Everything here renders into projects. |
 | `seed/.agents/skills/` | Skills shared by Claude Code and Codex. |
-| `seed/.claude/` | Claude Code hooks and settings. |
-| `seed/.codex/` | Codex configuration, hook policy, and execution rules. |
+| `seed/.claude/` | Claude Code settings, deny rules, and two hooks. |
+| `seed/.codex/` | Codex configuration and execution rules. |
 | `cultivation/marketplace/` | Optional plugin agents, skills, hooks, and bundles. |
-| `cultivation/wip/` | Staging for assets with no placement verdict. New files are ignored by default; some parked research assets remain tracked. |
-| `bin/` | Verification, release, and intellectual-property checks. |
+| `cultivation/parked/` | Skills, agents, and hooks removed from the shipped plugin. Not installed. |
+| `bin/` | Check, release, and intellectual-property tooling. |
 | `docs/` | Current template documentation and historical design records. |
 | `copier.yml` | Copier questions, exclusions, and post-render tasks. |
 | `VERSION` | Template release version. |
@@ -50,15 +50,14 @@ bin/verify-template.sh
    `main`. Changes to seed behavior, hooks, `copier.yml`, or releases use a branch
    and pull request.
 2. Keep rendered content generic. Project-specific material stays outside `seed/`.
-3. Run `bin/verify-template.sh` before every commit. Require
-   `verify-template: PASSED`.
+3. Run `bin/check` before every commit. Require `check: PASSED`.
 4. Treat source and command output as authority. Repair prose when it disagrees.
 5. Keep one behavior change per session.
 6. Keep one directive in one home. Read `docs/ASSET-LAYERS.md` before placing a
    new asset.
 7. Give one integration owner the final source snapshot. Give one validation
-   owner the single full `bin/verify-template.sh` run for that snapshot. Other
-   workers run focused checks and return bounded reports.
+   owner the single full `bin/check` run for that snapshot. Other workers run
+   focused checks and return bounded reports.

 ## Gotchas

@@ -71,12 +70,11 @@ bin/verify-template.sh

 | Resource | Read when |
 |----------|-----------|
-| `bin/rendered_harness_contract.py`, `bin/tests/test_rendered_harness_contract.py` | Changing the Rendered Harness Contract. |
+| `seed/docs/HARNESS.md` | Changing hooks, settings, or the deny lists; or needing the accepted risks. |
 | `docs/ASSET-LAYERS.md` | Deciding where an agent asset belongs. |
 | `docs/SYNC.md` | Updating projects or promoting a reusable asset. |
 | `docs/BOOTSTRAP.md`, `docs/COPIER.md` | Changing bootstrap or update behavior. |
-| `docs/specs/rebuild-structure-design.md` | Needing the rationale for the current tree. |
-| `docs/specs/rebuild-research/` | Checking the research behind the rebuild. |
+| `docs/archive/specs/rebuild-structure-design.md` | Needing the rationale for the current tree. |

 ## Agent skills

diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 35f9ada..efe4438 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -1,28 +1,28 @@
 # Contributing to Loam

-Thanks for your interest! Loam is a Copier template — the things it ships live under
-`seed/`, and the repo runs on its own config via the `.claude → seed/.claude` symlink.
+Thanks for your interest! Loam is a Copier template; the things it ships live under
+`seed/`, and the repo runs on its own config via the `.claude -> seed/.claude` symlink.

 ## Development setup

 ```bash
 git clone https://github.com/samyakjhaveri/loam && cd loam
-bin/verify-template.sh   # renders and checks the complete harness; expect "verify-template: PASSED"
+bin/check   # ruff, shell syntax, tests, plugin validate, render smoke; expect "check: PASSED"
 ```

 Requirements: [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier`), `python3`, `bash`, the Claude Code and Codex CLIs, and Ruff.
 Missing agent CLIs fail the gate; `LOAM_ALLOW_MISSING_AGENT_CLIS=1` permits a reduced local run (CI never sets it).

-**Windows note:** template *development* relies on the `.claude → seed/.claude` symlink.
+**Windows note:** template *development* relies on the `.claude -> seed/.claude` symlink.
 Use WSL, or enable Developer Mode and `git config core.symlinks true` before cloning.
-Rendered projects are unaffected — Copier writes real directories.
+Rendered projects are unaffected: Copier writes real directories.

 ## Making changes

-- **Docs, content, small fixes** → commit directly to `main` (or open a PR if you're external).
-- **Behavior changes** (`seed/` guidance, skills, hooks, policy, `copier.yml`, or release tooling) → branch + PR, always.
-- Run `bin/verify-template.sh` before every PR. CI runs it too; a red render blocks merge.
-- Before merging any PR, run `bash bin/verify-template.sh && bash bin/ip-sweep.sh`.
+- **Docs, content, small fixes**: commit directly to `main` (or open a PR if you're external).
+- **Behavior changes** (`seed/` guidance, skills, hooks, policy, `copier.yml`, or release tooling): branch and PR, always.
+- Run `bin/check` before every PR. CI runs the same script; a red run blocks merge.
+- Before merging any PR, run `bin/check && bash bin/ip-sweep.sh`.
   Without `bin/.ip-terms`, the non-strict IP sweep warns that it skips the content
   sweep and can still pass.
 - Skills follow the [agentskills.io](https://agentskills.io/specification) SKILL.md format.
@@ -46,10 +46,10 @@ Promotion PRs should state which project battle-tested the skill and what it was
 Copier resolves from **git tags**, not HEAD. After merging significant changes:

 ```bash
-bin/release.sh <version>   # bumps VERSION, tags, pushes — CI verifies and publishes the release
+bin/release.sh <version>   # needs a green CI run on HEAD; runs the IP sweep, bumps VERSION, tags, pushes
 ```

 ## Reporting issues

-Open a GitHub issue with your Copier version and the output of
-`bin/verify-template.sh` if the template fails to render.
+Open a GitHub issue with your Copier version and the output of `bin/check`
+if the template fails to render.
diff --git a/README.md b/README.md
index 89dc53f..f3786ae 100644
--- a/README.md
+++ b/README.md
@@ -4,7 +4,7 @@

 ![Loam](docs/assets/hero-identity.jpg)

-Loam is a [Copier](https://copier.readthedocs.io/) template. It renders shared agent guidance, Claude Code hooks and settings, and Codex policy into a new or existing project. A release gate verifies the complete rendered harness before a Loam release ships.
+Loam is a [Copier](https://copier.readthedocs.io/) template. It renders shared agent guidance, Claude Code settings, and Codex policy into a new or existing project. One check, `bin/check`, gates every change.

 ```bash
 uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
@@ -22,16 +22,18 @@ Loam fixes both:

 - **One shared prose home.** Codex reads `AGENTS.md` directly. Claude Code imports it from `CLAUDE.md` and adds only Claude-specific guidance.
 - **Tag-based updates.** `copier update` pulls released template changes into an existing project. Reusable optional assets move back into the plugin marketplace by a reviewed manual promotion.
-- **Rendered policy.** Claude hooks enforce checkout and turn-end checks. A Codex hook rejects recognized force pushes. Codex execution rules add defense in depth.
-- **One public release gate.** `bin/verify-template.sh` renders a project and checks the complete generated harness before release.
+- **Native policy, no text parsing.** Claude Code deny rules and `.codex/rules/loam.rules` block the destructive command families in both harnesses, and a repository ruleset guards the default branch. Two SessionStart-class hooks remain, so a tool call pays no hook latency.
+- **One check.** `bin/check` runs lint, shell syntax, tests, plugin validation, and a render smoke. The agent and CI run the same script.

 ## What you get

 - `AGENTS.md` and `CLAUDE.md` with fill-in project guidance.
-- `.claude/` settings and hook scripts.
+- `.claude/` settings, deny rules, and two SessionStart-class hooks.
 - A shared `/catchup` skill under `.agents/skills/`.
 - A shared `/fable-prompting` skill under `.agents/skills/`: which Fable 5.1 guide sections a prompt can act on.
-- `.codex/` configuration, hook policy, and execution rules.
+- `.codex/` configuration and execution rules.
+- `bin/check` and a CI workflow that runs it.
+- `docs/HARNESS.md` and `docs/WORKERS.md`, read on demand.
 - Optional agents and skills from `cultivation/marketplace/`.

 ## Quick start
@@ -46,45 +48,46 @@ cd my-project && uvx copier update --trust

 ## Scope, honestly

-Loam supports Claude Code and Codex through different native mechanisms. Both read the shared skill source and project guidance. Claude Code uses `.claude/settings.json` for its hooks. Codex uses `.codex/hooks.json` and execution rules. Optional plugin skills and agents are Claude Code assets unless their own documentation says otherwise.
+Loam supports Claude Code and Codex through different native mechanisms. Both read the shared skill source and project guidance. Claude Code uses `.claude/settings.json` for permissions, the sandbox, and hooks. Codex uses `.codex/config.toml` and execution rules. Optional plugin skills and agents are Claude Code assets unless their own documentation says otherwise.

 ## Project structure

 ```
 loam/
-├── seed/                    # Copier subdirectory — everything rendered to projects
+├── seed/                    # Copier subdirectory: everything rendered to projects
 │   ├── .agents/skills/      # Skills shared by Claude Code and Codex
-│   ├── .claude/             # Claude Code hooks and settings
-│   ├── .codex/              # Codex hook policy and execution rules
-│   └── *.jinja              # Template files (CLAUDE.md, AGENTS.md, README.md, …)
+│   ├── .claude/             # Claude Code settings, deny rules, two hooks
+│   ├── .codex/              # Codex config and execution rules
+│   └── *.jinja              # Template files (CLAUDE.md, AGENTS.md, README.md, ...)
 ├── cultivation/marketplace/ # Optional plugin bundles
 ├── soil/                    # Local-only knowledge base (gitignored)
-├── bin/                     # Verification and release tooling
+├── bin/                     # Check and release tooling
 ├── docs/                    # Template documentation
 └── copier.yml               # Template config
 ```

 ## Verification

-Run `bin/verify-template.sh` when changing Loam. It renders the template, checks the Rendered Harness Contract, and runs native Claude or Codex checks when those tools are installed.
+Run `bin/check` when changing Loam. It lints, checks shell syntax and whitespace, runs the tests including a render smoke, and validates the shipped plugins.

 ## Documentation

-- `docs/BOOTSTRAP.md` — First-session setup guide
-- `docs/COPIER.md` — Template configuration details
-- `docs/SYNC.md` — Forward updates, reverse promotion, and attach mode
-- `docs/ASSET-LAYERS.md` — Asset organization
+- `docs/BOOTSTRAP.md` - First-session setup guide
+- `docs/COPIER.md` - Template configuration details
+- `docs/SYNC.md` - Forward updates, reverse promotion, and attach mode
+- `docs/ASSET-LAYERS.md` - Asset organization
+- `seed/docs/HARNESS.md` - What the shipped harness guards, and the accepted risks

 ## Roadmap

-- **Marketplace polish** — one-command install for every bundle via the plugin marketplace
-- **Policy coverage** — extend native harness checks when a repeated failure earns a new guardrail
+- **Marketplace polish** - one-command install for every bundle via the plugin marketplace
+- **Policy coverage** - extend the native deny lists when a repeated failure earns a new guardrail

 ## Requirements

 - [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier` needs no install)
-- Python 3.11 or newer for the Rendered Harness Contract checker
-- [Claude Code](https://code.claude.com/docs) and Codex CLIs, plus [Ruff](https://docs.astral.sh/ruff/): the verification gate fails without them (set `LOAM_ALLOW_MISSING_AGENT_CLIS=1` for a reduced local run)
+- Python 3.11 or newer, with `pytest` and `ruff`, to run `bin/check`
+- [Claude Code](https://code.claude.com/docs) and Codex CLIs: `bin/check` fails without them (set `LOAM_ALLOW_MISSING_AGENT_CLIS=1` for a reduced local run)

 ## Contributing

diff --git a/bin/check b/bin/check
index 2fd0776..0005b68 100755
--- a/bin/check
+++ b/bin/check
@@ -51,7 +51,7 @@ while IFS= read -r skill; do
 done < <(find seed cultivation/marketplace -name SKILL.md -not -path '*/node_modules/*')

 step "skill-listing token weight"
-python3 bin/skill_listing_weight.py --root "$ROOT" --budget-tokens "${LISTING_BUDGET:-2750}" \
+python3 bin/skill_listing_weight.py --root "$ROOT" --budget-tokens "${LISTING_BUDGET:-448}" \
   || bad "skill-listing weight over budget"

 step "claude plugin validate"
diff --git a/cultivation/marketplace/sam-cc-setup/skills/plan-review/SKILL.md b/cultivation/marketplace/sam-cc-setup/skills/plan-review/SKILL.md
index 0b4ca64..939d2bf 100644
--- a/cultivation/marketplace/sam-cc-setup/skills/plan-review/SKILL.md
+++ b/cultivation/marketplace/sam-cc-setup/skills/plan-review/SKILL.md
@@ -1,13 +1,12 @@
 ---
 name: plan-review
+disable-model-invocation: true
 description: >
-  Run the merged blind plan review (correctness checklist + elegance gate in one
-  agent) on a plan, spec, or design doc before execution. Accepts the artifact
-  path as the argument. Use in a fresh session on a plan authored earlier, or
-  before executing any non-trivial or hard-to-reverse plan.
-  NOT for: reviewing shipped code or
-  diffs (use /code-review), or reviews where the author's rationale must be
-  weighed (this flow deliberately withholds it).
+  Run the merged blind plan review (correctness checklist + elegance gate in one agent)
+  on a plan, spec, or design doc before execution. Accepts the artifact path as the argument.
+  Use in a fresh session on a plan authored earlier, or before executing any non-trivial or
+  hard-to-reverse plan. NOT for reviewing shipped code or diffs (use /code-review), or reviews
+  where the author's rationale must be weighed (this flow deliberately withholds it).
 argument-hint: <path-to-plan>
 ---

diff --git a/docs/ASSET-LAYERS.md b/docs/ASSET-LAYERS.md
index e31bd1f..579065d 100644
--- a/docs/ASSET-LAYERS.md
+++ b/docs/ASSET-LAYERS.md
@@ -6,7 +6,7 @@ A duplicate across layers is a bug unless it is an explicit distribution mirror

 | Layer | Lives in | Reaches a project | Context cost |
 |-------|----------|-------------------|--------------|
-| Always-on seed harness | `seed/` (shared guidance and skill, Claude hooks and settings, Codex hook policy and rules) | Rendered by Copier at bootstrap; updated by `copier update` on new tags | Paid in every session; priced highest |
+| Always-on seed harness | `seed/` (shared guidance and skills, Claude settings and the two hooks, Codex config and rules) | Rendered by Copier at bootstrap; updated by `copier update` on new tags | Paid in every session; priced highest |
 | Plugin layer | `cultivation/marketplace/sam-cc-setup/` (agents + optional skills + the plan-review workflow) | Installed as a plugin; updates in place | Skill descriptions only, until invoked |
 | Marketplace bundles | `cultivation/marketplace/<name>/` | Install-on-demand | Zero until enabled |

@@ -16,5 +16,5 @@ Rules of thumb:
 - Anything that must hold every time is a hook in the seed, not prose anywhere.
 - The shared skill location for both harnesses is `seed/.agents/skills/` (Codex reads it directly; Claude Code reads it through a checked-in symlink in `.claude/skills/`).
 - A seed skill may be pure reference material when the owner requires it in every generated project; keep its description near 40 tokens, because the listing is paid in every session.
-- The canonical concurrent-checkout guard is `seed/.claude/hooks/concurrent-checkout-guard.sh`. The `sam-cc-setup` plugin carries a byte-identical distribution mirror for projects that do not use the Loam seed. `bin/rendered_harness_contract.py` rejects drift or a missing copy.
-- `cultivation/wip/` stages work that has no placement verdict yet.
+- The seed ships two SessionStart-class hooks and no tool-matcher hooks. Command policy is native: `.claude/settings.json` deny rules and `.codex/rules/loam.rules`. See `seed/docs/HARNESS.md`.
+- `cultivation/parked/` holds assets removed from the shipped plugin. Nothing installs from it.
diff --git a/docs/COPIER.md b/docs/COPIER.md
index 867d2c8..e258e7e 100644
--- a/docs/COPIER.md
+++ b/docs/COPIER.md
@@ -38,11 +38,11 @@ The public repo restarted history at v1.0.0, so older `_commit` refs no longer r
 **Copier always resolves the latest tag, never main's HEAD.** Push without tagging and nothing ships.

 ```bash
-bin/release.sh 5.0.0    # verify gate + IP sweep, bump VERSION, commit, tag, push
+bin/release.sh 5.0.0    # green CI run + IP sweep, bump VERSION, commit, tag, push
 uvx copier copy --trust --vcs-ref v5.0.0 gh:samyakjhaveri/loam ./proj   # pin a version
 ```

-Use `--vcs-ref=HEAD` against a local clone to test unreleased changes (this is what `bin/verify-template.sh` does).
+Use `--vcs-ref=HEAD` against a local clone to test unreleased changes (this is what the render smoke in `bin/check` does).

 ## Copier visibility map

diff --git a/docs/archive/README.md b/docs/archive/README.md
index 5fd5fac..66d45ae 100644
--- a/docs/archive/README.md
+++ b/docs/archive/README.md
@@ -13,4 +13,9 @@ Archived in v3.0.0 (2026-09-06):
 - `findings/` - the findings tracker. v3 drops the tracker; the PR description is the record.
 - `HANDOFF-2026-09-01-harness.md`, `HANDOFF-2026-09-03-audit-sessions.md` - old handoffs. `docs/BACKLOG.md` names its own source; it was not built from these.

+Archived in S4 (2026-09-07), after S3 deleted the machinery they describe:
+
+- `specs/2026-09-01-harness-smoke-rig-design.md`, `specs/routing-doc-repair-plan.md`, `specs/sam-cc-consolidation-*.md`, `specs/clief-claude-code-plan-mode-handoff.md` - spent plans that route work through `bin/verify-template.sh`.
+- `superpowers/` - the rendered-harness-contract and agent-efficiency plans and specs, all built on deleted checkers.
+
 `docs/plans/marketing/` did not exist on this branch at v3 time, so nothing from it was archived.
diff --git a/docs/specs/2026-09-01-harness-smoke-rig-design.md b/docs/archive/specs/2026-09-01-harness-smoke-rig-design.md
similarity index 100%
rename from docs/specs/2026-09-01-harness-smoke-rig-design.md
rename to docs/archive/specs/2026-09-01-harness-smoke-rig-design.md
diff --git a/docs/specs/clief-claude-code-plan-mode-handoff.md b/docs/archive/specs/clief-claude-code-plan-mode-handoff.md
similarity index 100%
rename from docs/specs/clief-claude-code-plan-mode-handoff.md
rename to docs/archive/specs/clief-claude-code-plan-mode-handoff.md
diff --git a/docs/specs/routing-doc-repair-plan.md b/docs/archive/specs/routing-doc-repair-plan.md
similarity index 100%
rename from docs/specs/routing-doc-repair-plan.md
rename to docs/archive/specs/routing-doc-repair-plan.md
diff --git a/docs/specs/sam-cc-consolidation-design.md b/docs/archive/specs/sam-cc-consolidation-design.md
similarity index 100%
rename from docs/specs/sam-cc-consolidation-design.md
rename to docs/archive/specs/sam-cc-consolidation-design.md
diff --git a/docs/specs/sam-cc-consolidation-plan.md b/docs/archive/specs/sam-cc-consolidation-plan.md
similarity index 100%
rename from docs/specs/sam-cc-consolidation-plan.md
rename to docs/archive/specs/sam-cc-consolidation-plan.md
diff --git a/docs/superpowers/plans/2026-08-30-rendered-harness-contract.md b/docs/archive/superpowers/plans/2026-08-30-rendered-harness-contract.md
similarity index 100%
rename from docs/superpowers/plans/2026-08-30-rendered-harness-contract.md
rename to docs/archive/superpowers/plans/2026-08-30-rendered-harness-contract.md
diff --git a/docs/superpowers/plans/2026-09-05-agent-efficiency.md b/docs/archive/superpowers/plans/2026-09-05-agent-efficiency.md
similarity index 100%
rename from docs/superpowers/plans/2026-09-05-agent-efficiency.md
rename to docs/archive/superpowers/plans/2026-09-05-agent-efficiency.md
diff --git a/docs/superpowers/specs/2026-08-30-rendered-harness-contract-design.md b/docs/archive/superpowers/specs/2026-08-30-rendered-harness-contract-design.md
similarity index 100%
rename from docs/superpowers/specs/2026-08-30-rendered-harness-contract-design.md
rename to docs/archive/superpowers/specs/2026-08-30-rendered-harness-contract-design.md
diff --git a/seed/.agents/skills/catchup/SKILL.md b/seed/.agents/skills/catchup/SKILL.md
index 83aba57..4778e7a 100644
--- a/seed/.agents/skills/catchup/SKILL.md
+++ b/seed/.agents/skills/catchup/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: catchup
-description: Fast 30s session bootstrap briefing. Use when resuming work after any break, at the start of a fresh session, or when unsure of current project state. Reports git status, recent commits, environment state, memory-index staleness, pending tasks, and red flags (uncommitted changes, detached HEAD, stale memory). NOT for deep code exploration or planning - it only reports state, it does not change it.
+description: Fast 30s session bootstrap briefing. Use when resuming work after any break, at the start of a fresh session, or when unsure of current project state. Reports git status, recent commits, environment state, memory-index staleness, pending tasks, and red flags. NOT for deep code exploration or planning - it only reports state, it does not change it.
 ---

 # Session Catchup Briefing
diff --git a/seed/.claude/hooks/fable-session-brief.sh b/seed/.claude/hooks/fable-session-brief.sh
index 3be0da5..f1c7410 100755
--- a/seed/.claude/hooks/fable-session-brief.sh
+++ b/seed/.claude/hooks/fable-session-brief.sh
@@ -37,11 +37,19 @@ if model is None or "fable" not in model.lower():

 print(
     "Fable session. Ask one question before acting only if a reading of the "
-    "request would change the architecture; otherwise act. When writing a handoff or plan for another session, "
-    "give it five headings: Goal and why; Constraints; Done check per task; "
-    "Session conduct; Target model and effort. Do not paste the autonomy block, "
-    "the Delivering work block, the progress-updates line, or the batching nudge; "
-    "Claude Code already injects all four. Prefer targeted edits over whole-file "
-    "rewrites. When the deliverable is prose, remove all mannered prose."
+    "request would change the architecture; otherwise act.\n"
+    "Judgment rules this harness does not inject:\n"
+    "- Prefer a targeted edit over a whole-file rewrite.\n"
+    "- Keep the diff to what the task asks. Report a nearby bug or cleanup as a "
+    "follow-up line, not as a change in this diff.\n"
+    "- Keep prose plain and short.\n"
+    "- Mark reused wording as a quote; do not restate it as your own.\n"
+    "- A benign request stays benign. Do not refuse work that only sounds "
+    "sensitive.\n"
+    "In a handoff or plan for another session use five headings: Goal and why; "
+    "Constraints; Done check per task; Session conduct; Target model and effort. "
+    "Do not paste the autonomy block, the Delivering work block, the "
+    "progress-updates line, or the batching nudge; Claude Code injects all four. "
+    "The `fable-prompting` skill is the long form."
 )
 ' 2>/dev/null || exit 0
diff --git a/seed/AGENTS.md.jinja b/seed/AGENTS.md.jinja
index b404902..8f84114 100644
--- a/seed/AGENTS.md.jinja
+++ b/seed/AGENTS.md.jinja
@@ -1,62 +1,23 @@
 # AGENTS.md - {{ project_name }}

-> The ONE prose home for agent guidance in this project.
-> Claude Code loads it through the `@AGENTS.md` import in CLAUDE.md; Codex reads it directly.
-> Every line here loads in every session of every harness. Add a line only if removing it would cause a mistake.
-
 ## What this project is

-(Two or three sentences. What the codebase does, and what an agent should keep in mind while working on it. Replace this placeholder.)
-
-## Conventions
-
-(Record only what an agent cannot derive from the code: naming rules that differ from defaults, layout decisions, review etiquette. Replace this placeholder; delete the section if nothing qualifies yet.)
-
-## Gotchas
+(Two or three sentences: what the codebase does, and what to keep in mind while working on it. Replace this.)

-Recurring traps. Add entries when something bites twice; delete entries when the machinery they describe is gone.
+## Commands

-- Copier resolves git TAGS, not HEAD. Template updates reach this project only after a new tag; always run copier with `--trust`.
-- In YAML frontmatter, quote description strings containing colons; strict parsers reject them unquoted.
-- Parallel workers: give each its own worktree (`claude --worktree <name>`); one checkout is safe only for disjoint files. For a shared GPU or database use `flock /tmp/<resource>.lock <cmd>` (util-linux; absent on stock macOS); build no other lock.
-- Parallel work has one integration owner and one validation owner. Workers run focused checks and return bounded reports. Only the validation owner runs the configured full gate on a given source fingerprint.
+- Check: `bin/check` (lint, shell syntax, whitespace, tests). Run it before you call work done.

-## Editing discipline
-
-Prefer a surgical edit to a whole-file rewrite when the end result is the same.
-Keep the change to what the request needs. A pre-existing bug, a performance concern, or
-nearby cleanup you notice while working is a follow-up line in your summary, not a change
-in this diff. Commit tests only where the task asks for them or this repo already keeps
-tests for that kind of change.
-A verification claim must carry its evidence. Reuse a valid content-bound receipt across
-turns only when `python3 .agents/lib/validation.py check --root .` accepts the current
-source and command definitions. Changed inputs need new checks. If no valid evidence
-exists, write "not verified" and name the command that would verify it.
-For a bug fix or behavior change, record the focused test failing for the expected reason
-before the fix. Commit the regression test with the fix unless this project requires a
-separate test commit. Never require a deliberately broken shared commit.
-
-Reviewers inspect one fixed diff. They do not rerun an unchanged full suite unless they
-name a concrete unresolved risk. Keep one independent final review for security,
-trust-boundary, or cross-cutting changes, and save its findings in a durable report.
-
-## Invariants
+## Conventions

-Standing constraints for this project, one per line, dated.
-A ticket or worker prompt says "obey the Invariants in AGENTS.md" instead of restating them.
-This list starts empty; add a line only when a constraint has been violated once or will bind more than one session.
+(Record only what an agent cannot derive from the code: naming, layout, review etiquette. Replace or delete.)

-## Session continuity
+## Gotchas

-Before stopping mid-task, write `HANDOFF.md` at the repo root with these fields, one heading each, in this order: Goal; Files touched; Commands run (each with its exit code); Tried and failed; Open assumptions; Next single action; Written at (the output of `git rev-parse HEAD`).
-The verify command that proves the work belongs under Commands run.
-`/catchup` reads it on resume and flags it stale when that hash is no longer HEAD, when its mtime is older than the last commit, or when its status words contradict git.
-It is gitignored and local-only; delete it when the task finishes.
-Keep it bounded: cite file sections and command summaries instead of pasting whole files
-or logs. When in doubt, the repository state wins over the handoff.
-A worker brief (`.superpowers/sdd/<task>/brief.md`) and its report (`report.md`) use the same seven fields, so an interrupted worker's findings are read from its report, never rebuilt from a transcript.
+- Copier resolves git TAGS, not HEAD; run `copier update --trust`.
+- In YAML frontmatter, quote description strings containing colons.

-## Codex note
+## Read on demand

-The `.codex/` layer (config, execution rules) is inert until you mark this project trusted in Codex and review its hooks via `/hooks`.
-Codex-side skills live in `.agents/skills/`.
+- `docs/HARNESS.md` - what the harness guards, what it does not, the accepted risks. Read it before editing a hook, `.claude/settings.json`, or `.codex/`.
+- `docs/WORKERS.md` - parallel-worker roles and the `HANDOFF.md` format.
diff --git a/seed/CLAUDE.md.jinja b/seed/CLAUDE.md.jinja
index a38d3be..6d9db3f 100644
--- a/seed/CLAUDE.md.jinja
+++ b/seed/CLAUDE.md.jinja
@@ -2,36 +2,8 @@

 @AGENTS.md

-## Environment
-
-- `python3` always, never `python`. Venv: (path, if any).
-- Verified commands (fill in and keep current):
-  - Test: (e.g. `pytest -q`)
-  - Lint: (e.g. `ruff check .`)
-  - Run: (how to launch the thing)
-
 ## Claude-specific gotchas

-- Hooks receive a JSON envelope on stdin (`tool_name`, `tool_input`); there is no `CLAUDE_TOOL_NAME` env var.
-- Hook event and matcher names are exact strings; a wrong name fails silently. Verify against the documented event list before wiring a hook.
-- A rule's `paths:` frontmatter fires when Claude READS a matching file, never on Write. Rules whose trigger is authoring a new file must stay always-loaded.
-- `auto-activate` is not a real skill-frontmatter field. To make a skill manual-only, use `disable-model-invocation: true`.
-- `/goal` is unavailable when `disableAllHooks` or `allowManagedHooksOnly` is set; never set either in a rendered project.
-
-## Shipped machinery
-
-- The Stop hook (`.claude/hooks/stop-verify-gate.sh`) blocks turn-end on changed-file check failures. It accepts a content-bound `.validation_passed` receipt across turns only while `python3 .agents/lib/validation.py check --root .` accepts the current source and command definitions. Fix failures instead of fighting the gate.
-- `sentinel-cleanup.sh` clears validation and review receipts after source edits; ignored artifacts keep them. Receipt checks also detect changes made outside Edit/Write hooks.
-- `/catchup` (in `.agents/skills/`, shared with Codex via symlink): session bootstrap briefing.
-- `/fable-prompting` (in `.agents/skills/`, shared via symlink): which Fable 5.1 guide sections you can act on and which Claude Code already injects; load before writing a Fable prompt or handoff.
-- Other hooks: `bash-audit-log.sh` (command log with exit code and experiment name, gitignored), `concurrent-checkout-guard.sh` (blocks two sessions racing one checkout), `ruff-after-edit.sh` (auto-fixes changed Python files), `write-rewrite-guard.sh` (advises Edit over Write on files of 80 or more lines), `bash-length-advisory.sh` (advises splitting commands over 400 characters), `post-compact-reinject.sh` (re-injects the working rules after compaction), and `fable-session-brief.sh` (prints a short prompting brief on a model switch, and at session start when the event names the model, for any Fable model).
-- Commit gates on `git commit`: `test-tamper-scan.sh` (blocks new skip, mock, loosened tolerance, or expected-equals-new-return lines in staged tests unless the message has a `Test-changes:` line), `mutation-gate.sh` (blocks when cosmic-ray finds surviving mutants on the changed lines; opt-in by installing cosmic-ray; justify under `Mutants:`), and `pre-commit-gate.sh` (requires a valid versioned JSON receipt at `.validation_passed`; run `.claude/hooks/run-validate-waves.sh` or the shared validator's `run` command to create it). The receipt is evidence for exact contents, Git state, command definitions, and runtime identity. File age does not make it valid.
-- Session logs: `harness-hygiene.sh` prints dead paths and commands named in CLAUDE.md, AGENTS.md, STATE.md, HANDOFF.md at session start; `skill-usage-log.sh` appends every skill invocation to `.claude/skill-usage.log` (gitignored).
-
-## Routing (read on demand)
-
-| Resource | Use when |
-|----------|----------|
-| `/plan-review <path>` (sam-cc-setup plugin, if installed) | Before executing a non-trivial or hard-to-reverse plan |
-| `scaffold-context` skill (sam-cc-setup plugin, if installed) | Authoring a CONTEXT.md for a subdirectory |
-| `docs/decisions/RULINGS.md` | A design choice was already decided; check or record the ruling |
+- Hook event and matcher names are exact strings; a wrong name fails silently.
+- Editing any file under `.claude/` needs bypassPermissions mode; other modes deny or prompt.
+- `auto-activate` is not a skill field. Use `disable-model-invocation: true` for a manual-only skill.
diff --git a/seed/_gh_setup.sh b/seed/_gh_setup.sh
index 9dd6d16..f568cda 100755
--- a/seed/_gh_setup.sh
+++ b/seed/_gh_setup.sh
@@ -22,15 +22,46 @@ fi
 BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"

 if gh repo view "${REPO}" >/dev/null 2>&1; then
-  echo "[copier] Repo ${REPO} already exists — connecting..."
+  echo "[copier] Repo ${REPO} already exists; connecting..."
   git remote add origin "https://github.com/${REPO}.git" 2>/dev/null ||
     git remote set-url origin "https://github.com/${REPO}.git"
   if ! git push -u origin "${BRANCH}"; then
-    echo "[copier] Push failed — remote may have existing commits."
+    echo "[copier] Push failed; the remote may have existing commits."
     echo "  Try: git pull --rebase origin ${BRANCH} && git push -u origin ${BRANCH}"
   fi
 else
   echo "[copier] Creating repo ${REPO}..."
   gh repo create "${REPO}" --private --source=. --remote=origin --push ||
-    echo "[copier] Repo creation failed. Create manually: https://github.com/new"
+    echo "[copier] Repo creation failed. Create it by hand: https://github.com/new"
+fi
+
+# Repository ruleset on the default branch: pull request plus a green `check`,
+# no bypass actors. Without it, main is directly pushable; docs/HARNESS.md
+# states that case. Needs admin rights on the repo, so the call can legitimately
+# fail on a token scope or a plan that lacks rulesets.
+if gh api --method POST "/repos/${REPO}/rulesets" \
+  --input - >/dev/null 2>&1 <<'RULESET'
+{
+  "name": "loam-default-branch",
+  "target": "branch",
+  "enforcement": "active",
+  "bypass_actors": [],
+  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
+  "rules": [
+    { "type": "pull_request" },
+    {
+      "type": "required_status_checks",
+      "parameters": {
+        "strict_required_status_checks_policy": false,
+        "required_status_checks": [ { "context": "check" } ]
+      }
+    }
+  ]
+}
+RULESET
+then
+  echo "[copier] Ruleset added: the default branch needs a PR and a green 'check'."
+else
+  echo "[copier] Ruleset call failed; the default branch is directly pushable."
+  echo "  Add it by hand under repo Settings > Rules, or re-run with an admin token."
 fi
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
new file mode 100644
index 0000000..3b38f2f
--- /dev/null
+++ b/seed/docs/HARNESS.md
@@ -0,0 +1,86 @@
+# The harness: what it guards, and what it does not
+
+## Safety, native only
+
+Nothing parses your command text to decide safety, and no hook runs on a tool
+matcher. Two native deny lists do the blocking.
+
+- Claude Code, `.claude/settings.json` `permissions.deny`: `rm -rf` and its
+  spellings (`-fr`, `-Rf`, `-r -f`, `-f -r`), `git push --force` / `-f` /
+  `--force-with-lease` / `--force-if-includes`, `git reset --hard`,
+  `git clean -f|-d|-x`, `git checkout -- .` / `git checkout .` /
+  `git restore .`, `git stash clear|drop`, and read or edit of `.env*`.
+  Deny applies in every permission mode, including bypassPermissions.
+- Codex, `.codex/rules/loam.rules`: the same families, one `prefix_rule` per
+  spelling, `decision = "forbidden"`. Codex splits command chains itself.
+- The Claude sandbox is on (`sandbox.enabled`), with `.env*` denied for read and
+  write. `failIfUnavailable` is false, so a host without sandbox support still
+  runs; the deny list is then the only file guard.
+- `.codex/config.toml` denies `.env*` in the workspace and leaves network on.
+  All of `.codex/` is inert until you mark this project trusted in Codex.
+
+## Push guard, by case
+
+When `github_repo` was answered, `_gh_setup.sh` posts a repository ruleset on the
+default branch requiring a pull request and the `check` status, with no bypass
+actors. Three cases, and the setup output says which one you got:
+
+| Case | Guard on the default branch |
+|---|---|
+| Ruleset created | Direct push rejected; PR plus a green `check` required. |
+| Ruleset call failed (token scope, plan, or permissions) | None. Add it by hand in repo Settings, Rules. |
+| No GitHub repo, or `gh` missing or unauthenticated | None. The branch is directly pushable. |
+
+There is no `ask` rule on `git push`, on purpose: an unattended run must not stop
+on a prompt.
+
+## The two hooks
+
+Both are SessionStart-class, so they add no per-tool latency.
+
+- `fable-session-brief.sh` (SessionStart, PostModelSwitch): prints the Fable
+  judgment rules Claude Code does not inject, when the event names a Fable
+  model; silent otherwise. It reads `model` on SessionStart and `to_model` on
+  PostModelSwitch. Measured on Claude Code 2.1.263: a non-interactive
+  `claude -p` startup payload carries no `model` field, so the brief does not
+  fire there.
+- `post-compact-reinject.sh` (SessionStart `compact`): re-injects the task after
+  a compaction.
+
+## The one check
+
+`bin/check` runs ruff, shell syntax, whitespace, and pytest. The agent runs it by
+choice; `.github/workflows/check.yml` runs the same script on every push and pull
+request. Nothing else lints or tests.
+
+## Always-on budget
+
+`AGENTS.md` is the one prose home for agent guidance; Claude Code imports it
+via `CLAUDE.md`, Codex reads it directly. Add a line to either file only if
+removing it would cause a mistake.
+
+- Prose (`CLAUDE.md` plus `AGENTS.md`): 400 tokens. The skill listing and the
+  session brief are separate always-on costs and are not inside that number.
+- Skill listing: the two seed skills weigh 131 tokens, so a fresh project pays
+  about 400 + 131 tokens before any work starts.
+- In the Loam template repo the `sam-cc-setup` plugin listing weighs 448 tokens.
+  That is the `LISTING_BUDGET` ratchet `bin/check` asserts. Lower it when the
+  listing shrinks; never raise it without saying why.
+
+## Accepted risks, stated rather than hidden
+
+- Git recovers committed work only. A command that dodges the deny prefixes and
+  destroys uncommitted or untracked files is unrecoverable.
+- The `.env` deny rules do not stop a Python or Node subprocess opening the file.
+  The sandbox filesystem deny is the real containment, where the host supports it.
+- Secrets typed into an ordinary source file are not caught locally.
+- Test tampering and mutation coverage have no gate. Pull-request review owns
+  test integrity.
+- Editing any file under `.claude/` needs bypassPermissions mode. An unattended
+  `dontAsk` agent cannot change its own harness.
+
+## Owner global config, outside this project
+
+The owner's `~/.claude/` files are personal and are not shipped by the template.
+A global hook in `~/.claude/hooks/` repeats the "prefer targeted edits" rule for
+every project on that machine, so the owner sees it twice; nobody else does.
diff --git a/seed/docs/WORKERS.md b/seed/docs/WORKERS.md
new file mode 100644
index 0000000..1ac73f5
--- /dev/null
+++ b/seed/docs/WORKERS.md
@@ -0,0 +1,40 @@
+# Parallel workers and handoffs
+
+Read on demand. None of this is loaded in a normal session.
+
+## Worktrees
+
+Give each parallel worker its own worktree (`claude --worktree <name>`). One
+checkout is safe only for disjoint files. For a shared GPU or database, wrap the
+command in `flock /tmp/<resource>.lock <cmd>` (util-linux; absent on stock
+macOS). Build no other lock.
+
+## Roles
+
+Parallel work has one integration owner and one validation owner. Workers run
+focused checks and return bounded reports; only the validation owner runs
+`bin/check` on a given source snapshot. Reviewers inspect one fixed diff and do
+not rerun an unchanged suite unless they name a concrete unresolved risk.
+
+## HANDOFF.md
+
+Before stopping mid-task, write `HANDOFF.md` at the repo root with these seven
+headings, in this order:
+
+1. Goal
+2. Files touched
+3. Commands run (each with its exit code, including the `bin/check` run)
+4. Tried and failed
+5. Open assumptions
+6. Next single action
+7. Written at (the output of `git rev-parse HEAD`)
+
+`/catchup` reads it on resume and calls it stale when that hash is no longer
+HEAD, when its mtime predates the last commit, or when its status words
+contradict git. It is gitignored and local-only; delete it when the task ends.
+
+Keep it bounded: cite file sections and command summaries instead of pasting
+whole files or logs. The repository state wins over the handoff.
+
+A worker brief and its report use the same seven headings, so an interrupted
+worker's findings are read from its report, never rebuilt from a transcript.
~~~~~~~~~~~~ evidence
