## Ticket

~~~~~~~~~~~~ evidence
# S2: park skills and archive docs

Part of #14

Execution ticket. Stays blocked until the decision tickets that feed it close. Spec: `02-IMPLEMENTATION-SPEC.md` commit 4 (parking and archive parts only). Runs concurrently with S1 (disjoint files). Branch from main, which already carries PR #13. This branch has no `bin/check`; gate on `bin/verify-template.sh`.

## Goal and why

Ship 3 marketplace skills and park 23; archive spent docs; delete committed `__pycache__`. `DESIGN.md` L5 and L6, law 7. Decision 1 (park the research lane), decision 7 (plugin ships no hooks).

## Files owned

- `cultivation/marketplace/sam-cc-setup/`: keep `plan-review` (with the plan-reviewer agent), `codex-review`, `surprise-me`; move the other 23 skills, unused agents, `plan-review-fanout.js`, and the plugin `hooks/` to `cultivation/parked/sam-cc-setup/` preserving subpaths; delete `__pycache__`; `marketplace.json` plugin entry unchanged
- `cultivation/parked/README.md` (one line) and `cultivation/parked/research-lane/` (from `cultivation/wip`)
- `docs/archive/` (rebuild research, reviews, `docs/tickets/`, old handoffs, `docs/findings/`), delete marketing drafts under `docs/plans/marketing/`
- `docs/BACKLOG.md` (the LATER items from `01-PENDING-WORK.md`)
- `bin/tests/test_marketplace_skill_routes.py` (delete; it asserts parked skills exist)
- `docs/specs/` skill-count prose (update, archive, or exempt every "N skills" assertion so `verify-template.sh` stage 7 `check_stale_counts.py` passes)

Do not touch `docs/agents/`, `docs/adr/`, or the `## Agent skills` block in root `AGENTS.md` (S4 keeps them). Do not touch `bin/check` or `.github/` (S1).

## Rows measured

- Marketplace skills shipped: `find cultivation/marketplace -name SKILL.md | wc -l` (baseline 26, target 3).
- Skill-listing tokens: `python3 bin/skill_listing_weight.py --root . --json` before and after (baseline ratchet 2750).
- `claude plugin validate --strict cultivation/marketplace` passes.

## Done checks

1. `find cultivation/marketplace -name SKILL.md | wc -l` prints 3.
2. `cultivation/parked/README.md` exists; `cultivation/parked/research-lane/` exists; `cultivation/wip` has no shipped content left.
3. The plugin ships no hooks: `find cultivation/marketplace -path '*hooks*' -type f` prints nothing.
4. `git ls-files | grep __pycache__` prints nothing.
5. `claude plugin validate --strict cultivation/marketplace` exits 0.
6. `docs/BACKLOG.md` exists and lists every LATER item from `01-PENDING-WORK.md`; `docs/archive/` holds tickets, findings, old handoffs, rebuild research; `docs/plans/marketing/` is gone.
7. `bin/tests/test_marketplace_skill_routes.py` is deleted and `pytest bin/tests` exits 0.
8. `bin/verify-template.sh` exits 0 on the branch, stage 7 included.
9. Verification protocol below completed; PR body carries the numbers.

## Verification protocol (every execution ticket, before its PR)

1. Measure the rows this ticket owns with the commands in the measurement section of `02-IMPLEMENTATION-SPEC.md`.
2. Work sample: render a project from the branch into a temp dir (`uvx copier copy --trust --defaults --vcs-ref HEAD -d project_name=sample . <dir>`), run the fixed task from `.superpowers/lean-v3/baseline/S0-BASELINE.md` with `claude -p "<task>" --model fable --output-format stream-json --verbose --include-hook-events > sample.jsonl`, then `python3 .superpowers/lean-v3/tools/summarize_sample.py sample.jsonl --check "<the task's own test>"`.
3. Fresh-context judge: one Agent tool call, `subagent_type: general-purpose`, `model: fable`, no history, given only this ticket, `git diff main...HEAD`, the measurement table, the work-sample summary, and the rubric in `04-SESSION-PLAN.md`. It scores each rubric row pass or fail with evidence and lists concrete fixes.
4. The judge applies fixes inside this ticket's file-ownership list only. Anything outside goes to `docs/BACKLOG.md`.
5. Re-run the check after the judge's fixes.
6. Open the PR with the before/after table (baseline from S0-BASELINE.md) and the judge's report in the body.

Run under `/goal` with the done checks above as the condition. Worktree: `git worktree add ../loam-s<N> -b lean/s<N> main` (repo sibling, never nested). Session runs in bypassPermissions because `.claude/` is a protected path. Plain dashes only.


## Count correction (2026-09-06)

cultivation/marketplace holds 27 SKILL.md files: 26 under sam-cc-setup/skills plus the separate impeccable plugin. Keep 3, park 24. Move cultivation/marketplace/impeccable to cultivation/parked/impeccable/ as well, and make marketplace.json consistent with that move; say which way in the PR body.

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS marketplace-skill-count (3)
PASS parked-readme
PASS parked-research-lane
PASS marketplace-no-hooks
PASS no-pycache
PASS plugin-validate
PASS backlog
PASS marketing-removed
PASS skill-routes-test-removed
PASS pytest-bin-tests
PASS verify-template
PASS run-artefacts
SKIP wip-emptied: needs a human to confirm cultivation/wip has no shipped content left, since which files count as shipped is a judgement call
SKIP archive-contents: needs a human to confirm docs/archive holds the tickets, findings, old handoffs, and rebuild research, since completeness of a move is not mechanically decidable
SUMMARY pass=12 fail=0 skip=2

~~~~~~~~~~~~ evidence

## PR body draft (worker-authored)

~~~~~~~~~~~~ evidence
# S2: park skills and archive docs

Closes #22. Part of #14.

## Goal

Cut the `sam-cc-setup` marketplace plugin from 27 shipped skills to 3, and move everything with no recorded use into `cultivation/parked/` instead of deleting it.
Archive the spent documents to `docs/archive/`, and turn the audit's still-live items into `docs/BACKLOG.md`.
This is `DESIGN.md` L5 and L6 under design law 7: the burden of proof is on keeping.

## What changed

1. `cultivation/marketplace/sam-cc-setup/` keeps 3 skills (`plan-review`, `codex-review`, `surprise-me`) and 1 agent (`plan-reviewer`). It ships no hooks and no workflows.
2. Parked to `cultivation/parked/sam-cc-setup/`, subpaths preserved: 23 skills, 5 agents, the whole `hooks/` directory, `workflows/plan-review-fanout.js`, and `THIRD_PARTY_LICENSES/`.
3. The `impeccable` plugin moved to `cultivation/parked/impeccable/` and its `marketplace.json` entry was deleted. `cultivation/wip/research-assets/` moved to `cultivation/parked/research-lane/` and `cultivation/wip` is gone. `cultivation/parked/README.md` added.
4. `docs/archive/` now holds the rebuild research, the session reviews, `docs/tickets/`, `docs/findings/`, `docs/superpowers/`, both old handoffs, and the distbench note, with a `README.md` saying what is in it and that none of it is live.
5. `docs/BACKLOG.md` added, carrying all 9 ranked LATER items from `01-PENDING-WORK.md` plus the folded-in `FINDINGS.md` rows. `bin/tests/test_marketplace_skill_routes.py` deleted.
6. Two done checks are SKIP, not PASS, and need human review before merge: `wip-emptied` (whether `cultivation/wip` has no shipped content left) and `archive-contents` (whether the `docs/archive/` move is complete). Both are judgement calls, so no command decides them. See Unverified below.

## Before and after

| Row | Before | After | Command |
|---|---|---|---|
| Marketplace skills shipped | 27 | 3 | `find cultivation/marketplace -name SKILL.md \| wc -l` |
| Skill-listing tokens (`sam-cc-setup`, the gated source) | 2591 | 421 | `python3 bin/skill_listing_weight.py --root . --json` |
| Listing against the 2750 ratchet | 2591 | 421 | stage 8 of `bin/verify-template.sh` |
| Listed skills / manual / agents / workflows | 18 / 8 / 6 / 1 | 2 / 1 / 1 / 0 | same JSON |
| Plugin hook files under `cultivation/marketplace` | 10 | 0 | `find cultivation/marketplace -path '*hooks*' -type f` |
| Tracked `__pycache__` paths | 0 | 0 | `git ls-files \| grep __pycache__` |
| `bin/tests` modules | 12 | 11 | `ls bin/tests/test_*.py \| wc -l` |
| `pytest bin/tests` | 401 passed | 400 passed | `python3 -m pytest bin/tests -q` |
| `claude plugin validate --strict cultivation/marketplace` | exit 0 | exit 0 | as written |
| `bin/verify-template.sh` | PASSED | PASSED, 121 s, stages 1 to 9 | `bash bin/verify-template.sh` |
| Diff size | | 121 files, +142 / -294 | `git diff --stat main...HEAD` |

The skill-listing weight drops by 2170 tokens on every request that lists the plugin.

## Work sample

Rendered from this branch with Copier, then the fixed `S0-BASELINE.md` task, `claude -p --model fable`.

| Row | S0 baseline (main) | S2 branch |
|---|---|---|
| elapsed_seconds | 125.7 | 17.8 |
| turns | 18 | 4 |
| cost_usd | 1.10 | 0.62 |
| output_tokens | 5639 | 784 |
| tool_calls | 16 | 2 |
| hook_events | 306 | 60 |
| denials | 0 | 0 |
| task check | 1 passed | 1 passed |

## Decisions taken without a human

The unattended worker made these calls. Full reasoning is in `.superpowers/lean-v3/loops/runs/S2/decisions.md`.

1. The plugin ships **no** hooks, including `codex-review-reminder.sh`. 00-DECISIONS row 7 and the ticket's done check 3 beat the spec's older note that kept it.
2. `impeccable`'s `marketplace.json` entry was **deleted**, not repointed at `../parked/impeccable`. A marketplace should not advertise a parked plugin.
3. Four files outside the ticket's stated ownership got path-only edits, because parking moved files they name by literal path: `bin/verify-template-stages.sh` (stage 7's `check_stale_counts.py`), `bin/rendered_harness_contract.py` (the `concurrent-checkout-guard.sh` distribution mirror), `bin/tests/test_rendered_harness_contract.py` (5 fixture paths), `bin/tests/test_agent_parity.py` (8 paths). No assertion was weakened or removed; each still runs against the parked copy. `bin/skill_listing_weight.py` also dropped its now-empty `impeccable` source. These are S3's files, and S3 starts after this merges.
4. `docs/archive/specs/seed-skill-promotion.md` got one `<!-- stale-counts: allow -->` marker above its "26 sam-cc-setup skills" line. It is a dated record of decision D2, which v3 reversed, and the checker's own docstring prescribes a marker for exactly this case. It was the only stale count in the repo after parking.
5. `copier.yml` was not touched. The spec's commit 4 also covers the dead `agent-parity.toml` exclude line, but the session plan assigns that file to S3.

## Unverified

- **Unverified: the work-sample improvement is not an S2 effect.** S2 changed nothing under `seed/`, so the rendered project on this branch has the same 15 hooks and the same always-on prose as the baseline. The baseline run built a `.venv` and a root `conftest.py` first; this run did not. Treat the row as evidence that S2 broke nothing, not as a speedup.
- **Unverified: the work sample's `--check` string differs from the baseline's.** The baseline used `.venv/bin/python -m pytest -q tests`; this run has no `.venv`, so `python3 -m pytest -q tests` was used. It exits 0 with `1 passed`.
- **Unverified: `docs/plans/marketing/` was never present.** `ls docs/plans` returns nothing on this branch. Done check 6 is satisfied vacuously. Nothing was deleted.
- **Unverified: no tracked `__pycache__` existed.** `git ls-files | grep __pycache__` was already empty on `main` at 9d9d5e6. Nothing was deleted.
- **Unverified: whether every parked asset is genuinely unused.** Parking followed the spec's list plus the two decision files. The worker did not independently re-audit usage of each of the 23 skills.
- **Unverified: the 421-token listing figure as a permanent ratchet.** The ratchet is still 2750. 00-DECISIONS row 6 assigns the tightening to S4, which sets `LISTING_BUDGET` in `bin/check` and records the number in `docs/HARNESS.md`.
- **Unverified: `cultivation/wip` has no shipped content left (check SKIP wip-emptied).** The supervisor's done checks skip this row; it needs a human to confirm, since which files count as shipped is a judgement call.
- **Unverified: the `docs/archive/` move is complete (check SKIP archive-contents).** The supervisor's done checks skip this row; it needs a human to confirm that the archive holds the tickets, findings, old handoffs, and rebuild research, since completeness of a move is not mechanically decidable.
- **Not measured: check wall time and hook latency per Bash call.** `bin/check` does not exist on this branch, and S2 owns no hook.
- **Not run by this worker: the fresh-context judge.** The supervisor runs verification-protocol steps 3 to 6.

~~~~~~~~~~~~ evidence

## Diff (main...HEAD)

~~~~~~~~~~~~ evidence
 bin/rendered_harness_contract.py                                                                             |   2 +-
 bin/skill_listing_weight.py                                                                                  |   2 --
 bin/tests/test_agent_parity.py                                                                               |  18 +++++------
 bin/tests/test_marketplace_skill_routes.py                                                                   | 138 ----------------------------------------------------------------------------------
 bin/tests/test_rendered_harness_contract.py                                                                  |  10 +++---
 bin/verify-template-stages.sh                                                                                |   2 +-
 cultivation/marketplace/.claude-plugin/marketplace.json                                                      |  10 ------
 cultivation/marketplace/README.md                                                                            |  10 +++---
 cultivation/marketplace/sam-cc-setup/README.md                                                               | 139 ++++++++++-------------------------------------------------------------------------
 cultivation/parked/README.md                                                                                 |   1 +
 cultivation/{marketplace => parked}/impeccable/.claude-plugin/plugin.json                                    |   0
 cultivation/{marketplace => parked}/impeccable/LICENSE.upstream                                              |   0
 cultivation/{marketplace => parked}/impeccable/README.md                                                     |   0
 cultivation/{marketplace => parked}/impeccable/skills/impeccable/SKILL.md                                    |   0
 cultivation/{wip => parked/research-lane}/research-assets/reassess-protect-results.sh                        |   0
 cultivation/{wip => parked/research-lane}/research-assets/reassess-research-consistency.md                   |   0
 cultivation/{wip => parked/research-lane}/research-assets/reassess-research-memory.md                        |   0
 cultivation/{wip => parked/research-lane}/research-assets/seed-docs/CHANGELOG.research.md.jinja              |   0
 cultivation/{wip => parked/research-lane}/research-assets/seed-docs/EXPERIMENT-PROTOCOL.md.jinja             |   0
 cultivation/{wip => parked/research-lane}/research-assets/seed-docs/EXPERIMENTS.md.jinja                     |   0
 cultivation/{wip => parked/research-lane}/research-assets/seed-docs/FINDINGS.md.jinja                        |   0
 cultivation/{wip => parked/research-lane}/research-assets/seed-docs/REFERENCES.md.jinja                      |   0
 cultivation/{wip => parked/research-lane}/research-assets/seed-docs/RESULTS.md.jinja                         |   0
 cultivation/{marketplace => parked}/sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt                   |   0
 cultivation/{marketplace => parked}/sam-cc-setup/agents/build-validator.md                                   |   0
 cultivation/{marketplace => parked}/sam-cc-setup/agents/code-architect.md                                    |   0
 cultivation/{marketplace => parked}/sam-cc-setup/agents/consistency-checker.md                               |   0
 cultivation/{marketplace => parked}/sam-cc-setup/agents/read-only.md                                         |   0
 cultivation/{marketplace => parked}/sam-cc-setup/agents/test-synthesizer.md                                  |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/check_stale_counts.py                                 |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/codex-review-reminder.sh                              |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/concurrent-checkout-guard.sh                          |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/generated-file-guard.sh                               |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/hooks.json                                            |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/pre-commit.sh                                         |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/protect-paths.sh                                      |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/protect_paths.py                                      |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/test_check_stale_counts.py                            |   0
 cultivation/{marketplace => parked}/sam-cc-setup/hooks/test_protect_paths.py                                 |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/agent-team/SKILL.md                                  |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/agent-team/advisor-prompt.md                         |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/agent-team/brief-report-template.md                  |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/agent-team/scenarios.md                              |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/agent-team/teammate-prompt.md                        |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/align-prompt/SKILL.md                                |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/authoring-context-docs/SKILL.md                      |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/auto-phase/SKILL.md                                  |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md                          |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/bootstrap-cc-setup/templates/CLAUDE-skeleton.md      |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/bootstrap-cc-setup/templates/workflow-model-notes.md |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/SKILL.md                               |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/scripts/frame-template.html            |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/scripts/helper.js                      |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/scripts/server.cjs                     |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/scripts/start-server.sh                |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/scripts/stop-server.sh                 |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/spec-document-reviewer-prompt.md       |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/brainstorming/visual-companion.md                    |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/codex-plan-review/SKILL.md                           |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/dream/SKILL.md                                       |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/gen-spec/SKILL.md                                    |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/hypothesis-tree/SKILL.md                             |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/reflect/SKILL.md                                     |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/sam_handoff/SKILL.md                                 |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/scaffold-context/SKILL.md                            |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/session-critique/SKILL.md                            |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/ship/SKILL.md                                        |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/sync-to-hub/SKILL.md                                 |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/sync-to-hub/sync.sh                                  |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/tech-selection/SKILL.md                              |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/techdebt/SKILL.md                                    |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/unknowns/ARTIFACT-FORMAT.md                          |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/unknowns/IMPLEMENTATION-NOTES.md                     |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/unknowns/SKILL.md                                    |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/validate/SKILL.md                                    |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/vet-skill/SKILL.md                                   |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/worktree-status/SKILL.md                             |   0
 cultivation/{marketplace => parked}/sam-cc-setup/skills/writing-plans/SKILL.md                               |   0
 cultivation/{marketplace => parked}/sam-cc-setup/workflows/plan-review-fanout.js                             |   0
 docs/BACKLOG.md                                                                                              |  85 +++++++++++++++++++++++++++++++++++++++++++++++++++
 docs/{ => archive}/2026-09-03-distbench-archive-note.md                                                      |   0
 docs/{ => archive}/HANDOFF-2026-09-01-harness.md                                                             |   0
 docs/{ => archive}/HANDOFF-2026-09-03-audit-sessions.md                                                      |   0
 docs/archive/README.md                                                                                       |  18 +++++++++++
 docs/{ => archive}/findings/AGENT-EFFICIENCY.md                                                              |   0
 docs/{ => archive}/findings/CI-PERFORMANCE-DIAGNOSIS.md                                                      |   0
 docs/{ => archive}/findings/FINDINGS.md                                                                      |   0
 docs/{ => archive}/findings/PROMPT-AUDIT-2026-09-06.md                                                       |   0
 docs/{ => archive}/findings/prompt-audit-2026-09-06.patch                                                    |   0
 docs/{ => archive}/reviews/2026-09-03-session-2-review.md                                                    |   0
 docs/{ => archive}/reviews/2026-09-03-session-3-review.md                                                    |   0
 docs/{ => archive}/reviews/2026-09-04-session-4-review.md                                                    |   0
 docs/{ => archive}/reviews/2026-09-04-session-5-review.md                                                    |   0
 docs/{ => archive}/reviews/2026-09-05-fable-prompting-review.md                                              |   0
 docs/{ => archive}/specs/concurrent-checkout-hook-ownership-plan.md                                          |   0
 docs/{ => archive}/specs/rebuild-ledger.md                                                                   |   0
 docs/{ => archive}/specs/rebuild-research/clief-claims-validation-method.md                                  |   0
 docs/{ => archive}/specs/rebuild-research/clief-claims-verdicts.md                                           |   0
 docs/{ => archive}/specs/rebuild-research/refagents-merge-review.md                                          |   0
 docs/{ => archive}/specs/rebuild-research/refagents-sweep.md                                                 |   0
 docs/{ => archive}/specs/rebuild-research/refagents-vercel.md                                                |   0
 docs/{ => archive}/specs/rebuild-research/refagents-voltagent.md                                             |   0
 docs/{ => archive}/specs/rebuild-research/refagents-zglass.md                                                |   0
 docs/{ => archive}/specs/rebuild-research/research-cc-docs.md                                                |   0
 docs/{ => archive}/specs/rebuild-research/research-codex-docs.md                                             |   0
 docs/{ => archive}/specs/rebuild-research/research-context-rules.md                                          |   0
 docs/{ => archive}/specs/rebuild-research/slim-audit-bundles.md                                              |   0
 docs/{ => archive}/specs/rebuild-session-brief.md                                                            |   0
 docs/{ => archive}/specs/rebuild-structure-design-review-elegance.md                                         |   0
 docs/{ => archive}/specs/rebuild-structure-design-review.md                                                  |   0
 docs/{ => archive}/specs/rebuild-structure-design.md                                                         |   0
 docs/{ => archive}/specs/seed-skill-promotion.md                                                             |   1 +
 docs/{ => archive}/superpowers/plans/2026-08-30-rendered-harness-contract.md                                 |   0
 docs/{ => archive}/superpowers/plans/2026-09-05-agent-efficiency.md                                          |   0
 docs/{ => archive}/superpowers/specs/2026-08-30-rendered-harness-contract-design.md                          |   0
 docs/{ => archive}/tickets/README.md                                                                         |   0
 docs/{ => archive}/tickets/session-2.md                                                                      |   0
 docs/{ => archive}/tickets/session-3.md                                                                      |   0
 docs/{ => archive}/tickets/session-4.md                                                                      |   0
 docs/{ => archive}/tickets/session-5.md                                                                      |   0
 docs/{ => archive}/tickets/session-6.md                                                                      |   0
 121 files changed, 142 insertions(+), 294 deletions(-)

diff --git a/bin/rendered_harness_contract.py b/bin/rendered_harness_contract.py
index 29c9a0a..b7b88f0 100644
--- a/bin/rendered_harness_contract.py
+++ b/bin/rendered_harness_contract.py
@@ -267,7 +267,7 @@ DISTRIBUTION_MIRRORS = (
     (
         "seed/.claude/hooks/concurrent-checkout-guard.sh",
         (
-            "cultivation/marketplace/sam-cc-setup/hooks/"
+            "cultivation/parked/sam-cc-setup/hooks/"
             "concurrent-checkout-guard.sh"
         ),
     ),
diff --git a/bin/skill_listing_weight.py b/bin/skill_listing_weight.py
index 710af8b..945175a 100755
--- a/bin/skill_listing_weight.py
+++ b/bin/skill_listing_weight.py
@@ -39,8 +39,6 @@ SOURCES = {
     "sam-cc-setup": {"skills": f"{_MP}/sam-cc-setup/skills",
                      "agents": f"{_MP}/sam-cc-setup/agents",
                      "workflows": f"{_MP}/sam-cc-setup/workflows", "gated": True},
-    "impeccable": {"skills": f"{_MP}/impeccable/skills", "agents": None,
-                   "workflows": None, "gated": False},
 }
 
 _FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
diff --git a/bin/tests/test_agent_parity.py b/bin/tests/test_agent_parity.py
index cb1a48e..3d1c4b9 100644
--- a/bin/tests/test_agent_parity.py
+++ b/bin/tests/test_agent_parity.py
@@ -137,7 +137,7 @@ class AgentParityTests(unittest.TestCase):
         agents = (ROOT / "seed/AGENTS.md.jinja").read_text(encoding="utf-8")
         claude = (ROOT / "seed/CLAUDE.md.jinja").read_text(encoding="utf-8")
         validate = (
-            ROOT / "cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md"
+            ROOT / "cultivation/parked/sam-cc-setup/skills/validate/SKILL.md"
         ).read_text(encoding="utf-8")
         combined = "\n".join((agents, claude, validate))
         self.assertIn("validation.py check", combined)
@@ -148,10 +148,10 @@ class AgentParityTests(unittest.TestCase):
 
     def test_shipping_stages_intended_inputs_before_validation(self) -> None:
         validate = (
-            ROOT / "cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md"
+            ROOT / "cultivation/parked/sam-cc-setup/skills/validate/SKILL.md"
         ).read_text(encoding="utf-8")
         ship = (
-            ROOT / "cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md"
+            ROOT / "cultivation/parked/sam-cc-setup/skills/ship/SKILL.md"
         ).read_text(encoding="utf-8")
         self.assertIn("intended source changes are staged", validate)
         self.assertLess(ship.index("git add <paths>"), ship.index("Invoke `/validate`."))
@@ -159,26 +159,26 @@ class AgentParityTests(unittest.TestCase):
 
     def test_expensive_review_workflows_are_conditional_and_bounded(self) -> None:
         team = (
-            ROOT / "cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md"
+            ROOT / "cultivation/parked/sam-cc-setup/skills/agent-team/SKILL.md"
         ).read_text(encoding="utf-8")
         scenarios = (
-            ROOT / "cultivation/marketplace/sam-cc-setup/skills/agent-team/scenarios.md"
+            ROOT / "cultivation/parked/sam-cc-setup/skills/agent-team/scenarios.md"
         ).read_text(encoding="utf-8")
         teammate = (
             ROOT
-            / "cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md"
+            / "cultivation/parked/sam-cc-setup/skills/agent-team/teammate-prompt.md"
         ).read_text(encoding="utf-8")
         critique = (
             ROOT
-            / "cultivation/marketplace/sam-cc-setup/skills/session-critique/SKILL.md"
+            / "cultivation/parked/sam-cc-setup/skills/session-critique/SKILL.md"
         ).read_text(encoding="utf-8")
         fanout = (
             ROOT
-            / "cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js"
+            / "cultivation/parked/sam-cc-setup/workflows/plan-review-fanout.js"
         ).read_text(encoding="utf-8")
         codex_plan = (
             ROOT
-            / "cultivation/marketplace/sam-cc-setup/skills/codex-plan-review/SKILL.md"
+            / "cultivation/parked/sam-cc-setup/skills/codex-plan-review/SKILL.md"
         ).read_text(encoding="utf-8")
         self.assertIn("one validation owner", team.lower())
         self.assertIn("fixed diff", critique.lower())
diff --git a/bin/tests/test_rendered_harness_contract.py b/bin/tests/test_rendered_harness_contract.py
index 6ad8c49..e40905e 100644
--- a/bin/tests/test_rendered_harness_contract.py
+++ b/bin/tests/test_rendered_harness_contract.py
@@ -448,7 +448,7 @@ class RenderedHarnessContractTest(unittest.TestCase):
         plugin_checkout_hook = self.write(
             self.source,
             (
-                "cultivation/marketplace/sam-cc-setup/hooks/"
+                "cultivation/parked/sam-cc-setup/hooks/"
                 "concurrent-checkout-guard.sh"
             ),
             canonical_hook,
@@ -510,7 +510,7 @@ class RenderedHarnessContractTest(unittest.TestCase):
         self.write(
             self.source,
             (
-                "cultivation/marketplace/sam-cc-setup/hooks/"
+                "cultivation/parked/sam-cc-setup/hooks/"
                 "concurrent-checkout-guard.sh"
             ),
             "different hook\n",
@@ -530,7 +530,7 @@ class RenderedHarnessContractTest(unittest.TestCase):
         paths = (
             "seed/.claude/hooks/concurrent-checkout-guard.sh",
             (
-                "cultivation/marketplace/sam-cc-setup/hooks/"
+                "cultivation/parked/sam-cc-setup/hooks/"
                 "concurrent-checkout-guard.sh"
             ),
         )
@@ -552,7 +552,7 @@ class RenderedHarnessContractTest(unittest.TestCase):
         self.build_good_fixture()
         canonical = self.source / "seed/.claude/hooks/concurrent-checkout-guard.sh"
         mirror = self.source / (
-            "cultivation/marketplace/sam-cc-setup/hooks/"
+            "cultivation/parked/sam-cc-setup/hooks/"
             "concurrent-checkout-guard.sh"
         )
         mirror.unlink()
@@ -573,7 +573,7 @@ class RenderedHarnessContractTest(unittest.TestCase):
     ) -> None:
         self.build_good_fixture()
         mirror = self.source / (
-            "cultivation/marketplace/sam-cc-setup/hooks/"
+            "cultivation/parked/sam-cc-setup/hooks/"
             "concurrent-checkout-guard.sh"
         )
         mirror.chmod(mirror.stat().st_mode & ~(stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))
diff --git a/bin/verify-template-stages.sh b/bin/verify-template-stages.sh
index 0f8d746..6b17780 100644
--- a/bin/verify-template-stages.sh
+++ b/bin/verify-template-stages.sh
@@ -209,7 +209,7 @@ if [ ! -f seed/.claude/stale-counts.json ]; then
   # The checker treats a missing config as clean; the gate must not.
   echo "FAIL: seed/.claude/stale-counts.json is missing; stage 7 cannot run."
   FAIL=1
-elif python3 cultivation/marketplace/sam-cc-setup/hooks/check_stale_counts.py \
+elif python3 cultivation/parked/sam-cc-setup/hooks/check_stale_counts.py \
     --root "$ROOT" --quiet; then
   echo "stale-counts: OK"
 else
diff --git a/cultivation/marketplace/.claude-plugin/marketplace.json b/cultivation/marketplace/.claude-plugin/marketplace.json
index c6dfbd1..5d3cd0e 100644
--- a/cultivation/marketplace/.claude-plugin/marketplace.json
+++ b/cultivation/marketplace/.claude-plugin/marketplace.json
@@ -16,16 +16,6 @@
         "email": "39847642+SamyakJhaveri@users.noreply.github.com"
       }
     },
-    {
-      "name": "impeccable",
-      "description": "UI polish workflow: deterministic anti-pattern rules plus an LLM critique. Vendored from pbakaus/impeccable, Apache-2.0.",
-      "version": "0.1.0",
-      "source": "./impeccable",
-      "author": {
-        "name": "Samyak Jhaveri",
-        "email": "39847642+SamyakJhaveri@users.noreply.github.com"
-      }
-    },
     {
       "name": "web-frontend-anthropics",
       "description": "Vetted web/UI skills from anthropics/skills, SHA-pinned via git-subdir: web-artifacts-builder (claude.ai bundle.html artifacts), webapp-testing (Playwright UI verification), theme-factory (challenger vs ui-ux-pro-max). Installs DISABLED (defaultEnabled:false) \u2014 enable to trial.",
diff --git a/cultivation/marketplace/README.md b/cultivation/marketplace/README.md
index 6875d63..9427a87 100644
--- a/cultivation/marketplace/README.md
+++ b/cultivation/marketplace/README.md
@@ -2,7 +2,8 @@
 
 Install-on-demand plugin bundles for Loam-adjacent projects.
 Nothing here ships to bootstrapped projects by default; installs are explicit.
-Slimmed 2026-08-29 in the rebuild (audit: `docs/specs/rebuild-research/slim-audit-bundles.md`).
+Slimmed 2026-08-29 in the rebuild.
+Slimmed again in v3.0.0: `sam-cc-setup` keeps 3 skills and ships no hooks; everything else moved to `cultivation/parked/` (design law 7, burden of proof is on keeping).
 
 ## Install
 
@@ -15,9 +16,8 @@ claude plugin marketplace add /path/to/loam/cultivation/marketplace
 
 | Bundle | Contents | Notes |
 |--------|----------|-------|
-| `sam-cc-setup` | `brainstorming` -> `writing-plans`, merged plan review, technology selection, validation, Codex cross-model review, and bootstrap support | The Loam-owned setup plugin. Upstream-derived design skills retain their MIT notice in `sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt` |
-| `impeccable` | UI polish workflow | Vendored; kept per rebuild ledger ruling |
+| `sam-cc-setup` | `plan-review` (blind merged plan review, with the `plan-reviewer` agent), `codex-review` (cross-model second opinion), `surprise-me` (ranked, evidence-backed ideas) | The Loam-owned setup plugin. No hooks, no workflows |
 | `web-frontend-*`, `deer-flow-public` | External skills, SHA-pinned via `git-subdir` | Ship `defaultEnabled:false`; enable to trial. Licenses per entry in `marketplace.json`; a `LICENSE.upstream` file in a vendored bundle is authoritative |
 
-Removed 2026-08-29 (zero or near-zero survivors under the rebuild criteria): `meta-improvement`, `helpers` (surprise-me rehomed into sam-cc-setup), `business-process`, `planning-with-files`, `ui-ux-pro-max`, `understand-anything`.
-Earlier removals (ledger): `pocock-engineering`, `team-deliberation`, `code-review-graph`, and the research bundles.
+Parked in v3.0.0 (moved to `cultivation/parked/`, not installed): 23 `sam-cc-setup` skills, 5 unused agents, the plugin `hooks/` directory, the `plan-review-fanout` workflow, the upstream MIT notice that covered the parked design skills, and the whole `impeccable` plugin.
+Removed 2026-08-29: `meta-improvement`, `helpers`, `business-process`, `planning-with-files`, `ui-ux-pro-max`, `understand-anything`.
diff --git a/cultivation/marketplace/sam-cc-setup/README.md b/cultivation/marketplace/sam-cc-setup/README.md
index 4dfdcb1..905ce8e 100644
--- a/cultivation/marketplace/sam-cc-setup/README.md
+++ b/cultivation/marketplace/sam-cc-setup/README.md
@@ -1,136 +1,29 @@
 # sam-cc-setup
 
-The portable core of Sam's Claude Code setup, extracted from a research repo where every
-piece earned its place in production use (except two, flagged below).
+The portable core of Sam's Claude Code setup.
+Cut to three skills in v3.0.0 under design law 7: the burden of proof is on keeping, and everything with zero recorded use is parked, not shipped.
 
-**Audience:** repositories that want optional planning, review, validation, and
-cross-model skills. This includes projects rendered by
-[Loam](https://github.com/SamyakJhaveri/loam). A Loam-rendered project already has
-the always-loaded harness, so it does not run `/bootstrap-cc-setup`.
+**Audience:** repositories that want optional planning-review and cross-model review skills.
+This includes projects rendered by [Loam](https://github.com/SamyakJhaveri/loam).
 
 ## What the plugin exposes after installation
 
-- **A concurrent-checkout guard** that blocks two sessions from racing on one working tree.
-  This plugin file is a distribution mirror for non-Loam projects. The canonical file is
-  `seed/.claude/hooks/concurrent-checkout-guard.sh`. Edit the canonical file first, copy it
-  here byte-for-byte, then run `bin/verify-template.sh` from the Loam root.
-- **Skills:** `plan-review` (blind merged plan review), `tech-selection` (bounded
-  component trade-off records), `surprise-me` (ranked, evidence-backed unsolicited
-  ideas; rehomed from the dissolved helpers bundle), `validate` (on-demand
-  deterministic gate through the build-validator agent),
-  `codex-review` and `codex-plan-review` (cross-model second opinions - require the
-  Codex CLI), `brainstorming` (approved design documents), `writing-plans` (exact,
-  testable implementation plans), `dream`, `align-prompt`, `scaffold-context`, `reflect`,
-  `sam_handoff`, `unknowns`, `bootstrap-cc-setup`.
-- **Agents:** `plan-reviewer` (merged 2026-08-29: correctness checklist + elegance
-  gate in ONE blind unit, bounded findings, coverage ledger), `consistency-checker`,
-  `test-synthesizer`, `code-architect`, `build-validator`, `read-only`.
-  Removed 2026-08-29 as natively superseded: `diff-reviewer`, `code-simplifier`,
-  `self-critic` (bundled `/code-review`, `/simplify`), `security-scanner`
-  (`/security-review`), and the baseline skeletons `verify-app` / `regression-checker`
-  (their `.claude/baselines.json` contract never shipped).
-- **Workflows:** `plan-review-fanout` (grounded adversarial plan review, parallel lenses).
+- **Skills:** `plan-review` (blind merged plan review: correctness checklist plus elegance gate in one unit), `codex-review` (cross-model second opinion; requires the Codex CLI), `surprise-me` (ranked, evidence-backed unsolicited ideas).
+- **Agents:** `plan-reviewer`, used by `plan-review`.
+- **Hooks:** none. The plugin installs no hook on any tool matcher (design law 3).
+- **Workflows:** none.
 
-## Design-to-plan workflow and provenance
+Everything else that used to ship here now sits unmodified in `cultivation/parked/sam-cc-setup/`, preserving its subpaths: 23 skills, 5 agents, the `hooks/` directory (`protect-paths`, `check_stale_counts`, `generated-file-guard`, `concurrent-checkout-guard`, `codex-review-reminder`, `pre-commit`, and their control suites), the `plan-review-fanout` workflow, and `THIRD_PARTY_LICENSES/`.
+Parked assets are kept for reference and can be promoted again when a real project uses one.
 
-`tech-selection` routes open-ended ideation to the local `brainstorming` skill.
-After the user approves the design, `brainstorming` writes it under `docs/specs/`
-and hands it to the local `writing-plans` skill. Plans go under `docs/plans/`.
-The planning handoff offers only execution methods available in the current host.
-
-The two design workflow skills are moved or adapted from obra/superpowers.
-Their upstream MIT notice is preserved verbatim at
-`THIRD_PARTY_LICENSES/obra-superpowers.txt`.
-
-## Opt-in guards (v0.2.0) - dormant until you declare their config
-
-Two more hooks and a checker ship inert; each activates only when its repo-local
-config file exists, so these v0.2.0 additions change nothing until you opt in.
-(The plugin is behavior-neutral on install since v0.3.0: commit enforcement starts
-only when `/bootstrap-cc-setup` installs the native pre-commit hook.)
-All come from originals proven in daily use upstream. The two generalized ones (`protect-paths`,
-`check_stale_counts`) each carry a control suite with positive AND negative controls -
-a guard that has never fired proves nothing. `generated-file-guard.sh` was vendored
-as-is (already registry-driven, proven in use upstream) and has no shipped suite;
-exercise it with a seeded registry row after install.
-
-| Guard | Config file | What it does |
-|---|---|---|
-| `protect-paths.sh` | `.claude/protected-paths.txt` (one glob per line) | Blocks Edit/Write to matching paths, Bash deletes (`rm`/`rmdir`/`shred`/`unlink` in the same command segment as a protected path, tokenized not regexed), and redirects onto them |
-| `generated-file-guard.sh` | `.claude/generated-outputs.tsv` (`glob<TAB>generator<TAB>block\|warn`) | Routes edits of generator output back to the generator - a doc-only fix to a generated file survives exactly one rerun |
-| `check_stale_counts.py` | `.claude/stale-counts.json` | Fails when prose asserts a number that disagrees with its declared source-of-truth command; a broken truth command aborts loudly rather than reporting clean. Not hook-wired - run it from `/validate` or CI |
-
-## What it cannot ship, and the workaround
+## What it cannot ship
 
 Plugins cannot inject always-loaded context (`CLAUDE.md`, `.claude/rules/*.md`).
-Run **`/bootstrap-cc-setup`** once in a new repo: it writes a minimal `CLAUDE.md`
-skeleton and a generic `workflow.md` rule (model-notes only), shows a diff before
-touching anything that exists, and prints how to undo everything it wrote. It also
-installs `hooks/pre-commit.sh` as the repository's native git pre-commit hook.
-Installing the plugin alone does not install that git hook. Loam-rendered projects
-already have their own harness and do not run this bootstrap skill.
-
-## Honesty labels
-
-- `unknowns` shipped 2026-08-02 with **zero usage evidence** at extraction time.
-  It encodes published guidance, not proven local habit.
-- Everything else ran in anger for weeks in the source repo.
-- Removed in v0.3.0 (2026-08-14 teardown rulings): the sentinel gate family,
-  `create-skill`, `mode-routing`, the `pr-review` agent, and
-  `codebase-review-fanout` (never exercised end-to-end).
-  (`techdebt` was later re-harvested and ships again as of v0.6.0.)
+A Loam-rendered project already carries that layer.
+The `bootstrap-cc-setup` skill that wrote it for non-Loam repos is parked.
 
 ## Versioning
 
-Semver in `.claude-plugin/plugin.json`. Behaviour changes (enforcement model, check
-sets) bump minor at least - enforcement that silently changes across machines is
-worse than none.
-
-## The release loop
-
-A reusable change follows the manual route in `docs/SYNC.md`.
-
-1. Copy the reviewed asset into `cultivation/marketplace/sam-cc-setup/` or the
-   bundle that owns it.
-2. Record what changed and why in `cultivation/marketplace/UPGRADING.md`.
-3. If plugin content changed, update its version in both the marketplace manifest
-   and the plugin manifest. Keep the two values equal.
-4. Run `python3 cultivation/marketplace/sam-cc-setup/hooks/test_check_stale_counts.py`
-   and `python3 cultivation/marketplace/sam-cc-setup/hooks/test_protect_paths.py`.
-   Require both control suites to pass.
-5. Run `bin/verify-template.sh` from the Loam root. Require
-   `verify-template: PASSED`.
-6. Run `bin/release.sh <version>`. It verifies again before changing the top-level
-   `VERSION`, then commits, tags, and pushes the release.
-7. Installed plugin consumers run `/plugin update`. Copier consumers run
-   `uvx copier update --trust` after the new tag exists.
-
-## What a release bumps, and what it does not
-
-`bin/release.sh` writes only the top-level `VERSION` file.
-That file is the Copier template version.
-
-It does not touch either per-plugin version field:
-
-- `cultivation/marketplace/.claude-plugin/marketplace.json` carries a `version` for local plugins.
-- Each plugin's own `.claude-plugin/plugin.json` carries its own `version`.
-
-These plugin versions are maintained by hand. The repository contract tests require both
-`sam-cc-setup` version fields to match each other and the value asserted in
-`bin/tests/test_marketplace_skill_routes.py`. The top-level `VERSION` remains the independent
-Copier template version.
-
-### Before you run bin/release.sh
-
-For every plugin whose content changed in this batch:
-
-1. Bump its `version` in `cultivation/marketplace/.claude-plugin/marketplace.json`.
-2. Bump the same `version` in that plugin's `.claude-plugin/plugin.json`.
-3. Keep the two numbers equal.
-4. Add the `UPGRADING.md` provenance line for the change.
-5. Run both plugin control suites named in the release loop above.
-6. Run `bin/verify-template.sh` and require `verify-template: PASSED`.
-7. Then run `bin/release.sh <version>`.
-
-A plugin whose content did not change keeps its current version.
-Bumping a version that ships identical content misleads every consumer running `/plugin update`.
+Semver in `.claude-plugin/plugin.json`, kept equal to the `sam-cc-setup` entry in `cultivation/marketplace/.claude-plugin/marketplace.json`.
+Bump both by hand when plugin content changes, and record the change in `cultivation/marketplace/UPGRADING.md`.
+`bin/release.sh` writes only the top-level `VERSION` (the Copier template version) and never touches either plugin version field.
diff --git a/cultivation/parked/README.md b/cultivation/parked/README.md
new file mode 100644
index 0000000..24f6835
--- /dev/null
+++ b/cultivation/parked/README.md
@@ -0,0 +1 @@
+Skills, agents, hooks, and workflows removed from the shipped `sam-cc-setup` plugin in v3.0.0, plus the `impeccable` plugin and the never-dogfooded research lane; kept for reference, not installed, and two files here are still load-bearing, so see the "S3-owned cleanups" section of `docs/BACKLOG.md` before deleting this tree.
diff --git a/cultivation/marketplace/impeccable/.claude-plugin/plugin.json b/cultivation/parked/impeccable/.claude-plugin/plugin.json
similarity index 100%
rename from cultivation/marketplace/impeccable/.claude-plugin/plugin.json
rename to cultivation/parked/impeccable/.claude-plugin/plugin.json
diff --git a/cultivation/marketplace/impeccable/LICENSE.upstream b/cultivation/parked/impeccable/LICENSE.upstream
similarity index 100%
rename from cultivation/marketplace/impeccable/LICENSE.upstream
rename to cultivation/parked/impeccable/LICENSE.upstream
diff --git a/cultivation/marketplace/impeccable/README.md b/cultivation/parked/impeccable/README.md
similarity index 100%
rename from cultivation/marketplace/impeccable/README.md
rename to cultivation/parked/impeccable/README.md
diff --git a/cultivation/marketplace/impeccable/skills/impeccable/SKILL.md b/cultivation/parked/impeccable/skills/impeccable/SKILL.md
similarity index 100%
rename from cultivation/marketplace/impeccable/skills/impeccable/SKILL.md
rename to cultivation/parked/impeccable/skills/impeccable/SKILL.md
diff --git a/cultivation/wip/research-assets/reassess-protect-results.sh b/cultivation/parked/research-lane/research-assets/reassess-protect-results.sh
similarity index 100%
rename from cultivation/wip/research-assets/reassess-protect-results.sh
rename to cultivation/parked/research-lane/research-assets/reassess-protect-results.sh
diff --git a/cultivation/wip/research-assets/reassess-research-consistency.md b/cultivation/parked/research-lane/research-assets/reassess-research-consistency.md
similarity index 100%
rename from cultivation/wip/research-assets/reassess-research-consistency.md
rename to cultivation/parked/research-lane/research-assets/reassess-research-consistency.md
diff --git a/cultivation/wip/research-assets/reassess-research-memory.md b/cultivation/parked/research-lane/research-assets/reassess-research-memory.md
similarity index 100%
rename from cultivation/wip/research-assets/reassess-research-memory.md
rename to cultivation/parked/research-lane/research-assets/reassess-research-memory.md
diff --git a/cultivation/wip/research-assets/seed-docs/CHANGELOG.research.md.jinja b/cultivation/parked/research-lane/research-assets/seed-docs/CHANGELOG.research.md.jinja
similarity index 100%
rename from cultivation/wip/research-assets/seed-docs/CHANGELOG.research.md.jinja
rename to cultivation/parked/research-lane/research-assets/seed-docs/CHANGELOG.research.md.jinja
diff --git a/cultivation/wip/research-assets/seed-docs/EXPERIMENT-PROTOCOL.md.jinja b/cultivation/parked/research-lane/research-assets/seed-docs/EXPERIMENT-PROTOCOL.md.jinja
similarity index 100%
rename from cultivation/wip/research-assets/seed-docs/EXPERIMENT-PROTOCOL.md.jinja
rename to cultivation/parked/research-lane/research-assets/seed-docs/EXPERIMENT-PROTOCOL.md.jinja
diff --git a/cultivation/wip/research-assets/seed-docs/EXPERIMENTS.md.jinja b/cultivation/parked/research-lane/research-assets/seed-docs/EXPERIMENTS.md.jinja
similarity index 100%
rename from cultivation/wip/research-assets/seed-docs/EXPERIMENTS.md.jinja
rename to cultivation/parked/research-lane/research-assets/seed-docs/EXPERIMENTS.md.jinja
diff --git a/cultivation/wip/research-assets/seed-docs/FINDINGS.md.jinja b/cultivation/parked/research-lane/research-assets/seed-docs/FINDINGS.md.jinja
similarity index 100%
rename from cultivation/wip/research-assets/seed-docs/FINDINGS.md.jinja
rename to cultivation/parked/research-lane/research-assets/seed-docs/FINDINGS.md.jinja
diff --git a/cultivation/wip/research-assets/seed-docs/REFERENCES.md.jinja b/cultivation/parked/research-lane/research-assets/seed-docs/REFERENCES.md.jinja
similarity index 100%
rename from cultivation/wip/research-assets/seed-docs/REFERENCES.md.jinja
rename to cultivation/parked/research-lane/research-assets/seed-docs/REFERENCES.md.jinja
diff --git a/cultivation/wip/research-assets/seed-docs/RESULTS.md.jinja b/cultivation/parked/research-lane/research-assets/seed-docs/RESULTS.md.jinja
similarity index 100%
rename from cultivation/wip/research-assets/seed-docs/RESULTS.md.jinja
rename to cultivation/parked/research-lane/research-assets/seed-docs/RESULTS.md.jinja
diff --git a/cultivation/marketplace/sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt b/cultivation/parked/sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt
rename to cultivation/parked/sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt
diff --git a/cultivation/marketplace/sam-cc-setup/agents/build-validator.md b/cultivation/parked/sam-cc-setup/agents/build-validator.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/agents/build-validator.md
rename to cultivation/parked/sam-cc-setup/agents/build-validator.md
diff --git a/cultivation/marketplace/sam-cc-setup/agents/code-architect.md b/cultivation/parked/sam-cc-setup/agents/code-architect.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/agents/code-architect.md
rename to cultivation/parked/sam-cc-setup/agents/code-architect.md
diff --git a/cultivation/marketplace/sam-cc-setup/agents/consistency-checker.md b/cultivation/parked/sam-cc-setup/agents/consistency-checker.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/agents/consistency-checker.md
rename to cultivation/parked/sam-cc-setup/agents/consistency-checker.md
diff --git a/cultivation/marketplace/sam-cc-setup/agents/read-only.md b/cultivation/parked/sam-cc-setup/agents/read-only.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/agents/read-only.md
rename to cultivation/parked/sam-cc-setup/agents/read-only.md
diff --git a/cultivation/marketplace/sam-cc-setup/agents/test-synthesizer.md b/cultivation/parked/sam-cc-setup/agents/test-synthesizer.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/agents/test-synthesizer.md
rename to cultivation/parked/sam-cc-setup/agents/test-synthesizer.md
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/check_stale_counts.py b/cultivation/parked/sam-cc-setup/hooks/check_stale_counts.py
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/check_stale_counts.py
rename to cultivation/parked/sam-cc-setup/hooks/check_stale_counts.py
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/codex-review-reminder.sh b/cultivation/parked/sam-cc-setup/hooks/codex-review-reminder.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/codex-review-reminder.sh
rename to cultivation/parked/sam-cc-setup/hooks/codex-review-reminder.sh
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/concurrent-checkout-guard.sh b/cultivation/parked/sam-cc-setup/hooks/concurrent-checkout-guard.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/concurrent-checkout-guard.sh
rename to cultivation/parked/sam-cc-setup/hooks/concurrent-checkout-guard.sh
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/generated-file-guard.sh b/cultivation/parked/sam-cc-setup/hooks/generated-file-guard.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/generated-file-guard.sh
rename to cultivation/parked/sam-cc-setup/hooks/generated-file-guard.sh
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/hooks.json b/cultivation/parked/sam-cc-setup/hooks/hooks.json
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/hooks.json
rename to cultivation/parked/sam-cc-setup/hooks/hooks.json
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/pre-commit.sh b/cultivation/parked/sam-cc-setup/hooks/pre-commit.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/pre-commit.sh
rename to cultivation/parked/sam-cc-setup/hooks/pre-commit.sh
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/protect-paths.sh b/cultivation/parked/sam-cc-setup/hooks/protect-paths.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/protect-paths.sh
rename to cultivation/parked/sam-cc-setup/hooks/protect-paths.sh
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/protect_paths.py b/cultivation/parked/sam-cc-setup/hooks/protect_paths.py
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/protect_paths.py
rename to cultivation/parked/sam-cc-setup/hooks/protect_paths.py
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/test_check_stale_counts.py b/cultivation/parked/sam-cc-setup/hooks/test_check_stale_counts.py
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/test_check_stale_counts.py
rename to cultivation/parked/sam-cc-setup/hooks/test_check_stale_counts.py
diff --git a/cultivation/marketplace/sam-cc-setup/hooks/test_protect_paths.py b/cultivation/parked/sam-cc-setup/hooks/test_protect_paths.py
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/hooks/test_protect_paths.py
rename to cultivation/parked/sam-cc-setup/hooks/test_protect_paths.py
diff --git a/cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md b/cultivation/parked/sam-cc-setup/skills/agent-team/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/agent-team/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/agent-team/advisor-prompt.md b/cultivation/parked/sam-cc-setup/skills/agent-team/advisor-prompt.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/agent-team/advisor-prompt.md
rename to cultivation/parked/sam-cc-setup/skills/agent-team/advisor-prompt.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/agent-team/brief-report-template.md b/cultivation/parked/sam-cc-setup/skills/agent-team/brief-report-template.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/agent-team/brief-report-template.md
rename to cultivation/parked/sam-cc-setup/skills/agent-team/brief-report-template.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/agent-team/scenarios.md b/cultivation/parked/sam-cc-setup/skills/agent-team/scenarios.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/agent-team/scenarios.md
rename to cultivation/parked/sam-cc-setup/skills/agent-team/scenarios.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md b/cultivation/parked/sam-cc-setup/skills/agent-team/teammate-prompt.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md
rename to cultivation/parked/sam-cc-setup/skills/agent-team/teammate-prompt.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/align-prompt/SKILL.md b/cultivation/parked/sam-cc-setup/skills/align-prompt/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/align-prompt/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/align-prompt/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/authoring-context-docs/SKILL.md b/cultivation/parked/sam-cc-setup/skills/authoring-context-docs/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/authoring-context-docs/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/authoring-context-docs/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/auto-phase/SKILL.md b/cultivation/parked/sam-cc-setup/skills/auto-phase/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/auto-phase/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/auto-phase/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md b/cultivation/parked/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/templates/CLAUDE-skeleton.md b/cultivation/parked/sam-cc-setup/skills/bootstrap-cc-setup/templates/CLAUDE-skeleton.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/templates/CLAUDE-skeleton.md
rename to cultivation/parked/sam-cc-setup/skills/bootstrap-cc-setup/templates/CLAUDE-skeleton.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/templates/workflow-model-notes.md b/cultivation/parked/sam-cc-setup/skills/bootstrap-cc-setup/templates/workflow-model-notes.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/templates/workflow-model-notes.md
rename to cultivation/parked/sam-cc-setup/skills/bootstrap-cc-setup/templates/workflow-model-notes.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md b/cultivation/parked/sam-cc-setup/skills/brainstorming/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/frame-template.html b/cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/frame-template.html
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/frame-template.html
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/frame-template.html
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/helper.js b/cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/helper.js
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/helper.js
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/helper.js
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/server.cjs b/cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/server.cjs
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/server.cjs
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/server.cjs
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/start-server.sh b/cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/start-server.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/start-server.sh
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/start-server.sh
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/stop-server.sh b/cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/stop-server.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/scripts/stop-server.sh
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/scripts/stop-server.sh
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/spec-document-reviewer-prompt.md b/cultivation/parked/sam-cc-setup/skills/brainstorming/spec-document-reviewer-prompt.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/spec-document-reviewer-prompt.md
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/spec-document-reviewer-prompt.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/brainstorming/visual-companion.md b/cultivation/parked/sam-cc-setup/skills/brainstorming/visual-companion.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/brainstorming/visual-companion.md
rename to cultivation/parked/sam-cc-setup/skills/brainstorming/visual-companion.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/codex-plan-review/SKILL.md b/cultivation/parked/sam-cc-setup/skills/codex-plan-review/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/codex-plan-review/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/codex-plan-review/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/dream/SKILL.md b/cultivation/parked/sam-cc-setup/skills/dream/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/dream/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/dream/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/gen-spec/SKILL.md b/cultivation/parked/sam-cc-setup/skills/gen-spec/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/gen-spec/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/gen-spec/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/hypothesis-tree/SKILL.md b/cultivation/parked/sam-cc-setup/skills/hypothesis-tree/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/hypothesis-tree/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/hypothesis-tree/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/reflect/SKILL.md b/cultivation/parked/sam-cc-setup/skills/reflect/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/reflect/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/reflect/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/sam_handoff/SKILL.md b/cultivation/parked/sam-cc-setup/skills/sam_handoff/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/sam_handoff/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/sam_handoff/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/scaffold-context/SKILL.md b/cultivation/parked/sam-cc-setup/skills/scaffold-context/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/scaffold-context/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/scaffold-context/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/session-critique/SKILL.md b/cultivation/parked/sam-cc-setup/skills/session-critique/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/session-critique/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/session-critique/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md b/cultivation/parked/sam-cc-setup/skills/ship/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/ship/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/sync-to-hub/SKILL.md b/cultivation/parked/sam-cc-setup/skills/sync-to-hub/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/sync-to-hub/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/sync-to-hub/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/sync-to-hub/sync.sh b/cultivation/parked/sam-cc-setup/skills/sync-to-hub/sync.sh
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/sync-to-hub/sync.sh
rename to cultivation/parked/sam-cc-setup/skills/sync-to-hub/sync.sh
diff --git a/cultivation/marketplace/sam-cc-setup/skills/tech-selection/SKILL.md b/cultivation/parked/sam-cc-setup/skills/tech-selection/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/tech-selection/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/tech-selection/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/techdebt/SKILL.md b/cultivation/parked/sam-cc-setup/skills/techdebt/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/techdebt/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/techdebt/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/unknowns/ARTIFACT-FORMAT.md b/cultivation/parked/sam-cc-setup/skills/unknowns/ARTIFACT-FORMAT.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/unknowns/ARTIFACT-FORMAT.md
rename to cultivation/parked/sam-cc-setup/skills/unknowns/ARTIFACT-FORMAT.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/unknowns/IMPLEMENTATION-NOTES.md b/cultivation/parked/sam-cc-setup/skills/unknowns/IMPLEMENTATION-NOTES.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/unknowns/IMPLEMENTATION-NOTES.md
rename to cultivation/parked/sam-cc-setup/skills/unknowns/IMPLEMENTATION-NOTES.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/unknowns/SKILL.md b/cultivation/parked/sam-cc-setup/skills/unknowns/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/unknowns/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/unknowns/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md b/cultivation/parked/sam-cc-setup/skills/validate/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/validate/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/validate/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/vet-skill/SKILL.md b/cultivation/parked/sam-cc-setup/skills/vet-skill/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/vet-skill/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/vet-skill/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/worktree-status/SKILL.md b/cultivation/parked/sam-cc-setup/skills/worktree-status/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/worktree-status/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/worktree-status/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/skills/writing-plans/SKILL.md b/cultivation/parked/sam-cc-setup/skills/writing-plans/SKILL.md
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/skills/writing-plans/SKILL.md
rename to cultivation/parked/sam-cc-setup/skills/writing-plans/SKILL.md
diff --git a/cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js b/cultivation/parked/sam-cc-setup/workflows/plan-review-fanout.js
similarity index 100%
rename from cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js
rename to cultivation/parked/sam-cc-setup/workflows/plan-review-fanout.js
diff --git a/docs/BACKLOG.md b/docs/BACKLOG.md
new file mode 100644
index 0000000..024a2e4
--- /dev/null
+++ b/docs/BACKLOG.md
@@ -0,0 +1,85 @@
+# Backlog
+
+Everything from the v3 audit that is still worth doing after v3.0.0 ships.
+Source: `.superpowers/lean-v3/01-PENDING-WORK.md`, the ranked LATER list.
+Ranked by value to the stated goal, a research partner. Highest first.
+One item per session, same verification protocol as the v3 sessions.
+
+Nothing here is scheduled. An item moves out of this file only when a real project needs it (design law 7: the burden of proof is on keeping).
+
+## 1. Research-lane bundle
+
+Sources: RD, S6-2, S6-4, G6, W1, W2, W3, RG.
+Ship the parked bundle at `cultivation/parked/research-lane/` as one plugin: vendored skills (rigor, experiment-loop, research-writing, ml-paper-writing), the empty doc templates, the `run.json` plus run-folder convention, and `bin/` verifiers (claims ledger, citation, figure) the agent runs by choice.
+Promote to shipped only when a new distbench dogfoods it and a session measures it.
+No hooks, no commit gates: file conventions plus verifiers.
+Why first: it is the one thing Loam was for and the one thing never built.
+
+## 2. Experiment contract as a file convention
+
+Sources: S6-1, G7 contract half.
+A `CONTRACT.md` (question, done-when shell command, budget, seeds, protocol hash) plus a `bin/` verifier.
+The done-when check is native `/goal`, not a Stop hook.
+Why: the smallest unit of the research lane; it makes unattended runs verifiable without the deleted gate machinery.
+
+## 3. Headless conveyor for the remote eval host
+
+Sources: G7, RF notification half.
+A thin `bin/conveyor.sh`: `claude -p` in tmux on the eval host, results sync, Pushover on halt.
+Drop the in-loop Codex gate; it is harness-policing.
+Notification via the script or a Routine, never a hook.
+Why: the owner runs walk-away work on a remote host, but this waits until the contract exists to feed it.
+
+## 4. Ideation chain
+
+Sources: S6-3, G5.
+One parked `ideate` skill: frame, diverge with a mandatory retrieval pass, react, ground on an external anchor, plan.
+Reuses the already-parked `unknowns` and the shipped `surprise-me`.
+Why: retrieval-grounded ideas measured 2.5x impact, but it duplicates native plan mode, so it waits behind the lane it serves.
+
+## 5. Reading room and skill acquisition
+
+Sources: S6-4, G2.
+Parked skills `read` (labelled Verified/Likely/Relayed readings into `RESOURCES.md`) and `adopt-skill` (find, vet, eval, adopt).
+Plus the "write a skill at the second repetition" rule as one `docs/WORKERS.md` line.
+Why: genuine hygiene, low urgency, no platform gap forcing it now.
+
+## 6. Decision ledger and structured handoff prose
+
+Sources: G1 RULINGS half, RC, S6-5, S6-8, G3 brief/report half.
+An on-demand `RULINGS.md`, plus the seven-field handoff, worktree isolation, loop, and inline-mermaid guidance, all as `docs/WORKERS.md` prose.
+Never always-loaded.
+Why: cheap and useful for multi-session work, but it must stay out of the 400-token always-on budget.
+
+## 7. Attach mode
+
+Source: S5, `bin/loam-attach.sh` half.
+Keep `bin/loam-attach.sh` for adding the harness to an existing repo.
+Why: already built and working; the one forward-sync mechanism with a live use.
+
+## 8. align-prompt and brainstorming polish
+
+Sources: H3, H4d.
+Ride with the parked plugin skills; manual only, never auto-wired.
+Why: lowest value; a convenience on skills that are themselves parked.
+
+## 9. Owner global-config pass
+
+Source: G8.
+Outside Loam entirely: retune `~/.claude/CLAUDE.md`, `FABLE-BRAIN.md`, and the model-split env vars as a personal task.
+v3 notes it in one `docs/HARNESS.md` line.
+Why: real, but not the template's job.
+
+## Smaller items folded in from the same audit
+
+- F7: `bin/check`'s render smoke renders defaults only. A `project_kind=typescript` render is a LATER item (00-DECISIONS row 3 deferred it).
+- Every other open `FINDINGS.md` row (F1 to F6, F8, F9) targets a component v3 deletes or parks, so those fixes are moot. The tracker itself is archived at `docs/archive/findings/FINDINGS.md`.
+
+## S3-owned cleanups created by the v3 park
+
+These exist only because v3.0.0 parked code that other files still point at. Each must land before `cultivation/parked/` can be treated as inert reference material.
+
+- Move `cultivation/parked/sam-cc-setup/hooks/check_stale_counts.py` into `bin/`. Stage 7 of `bin/verify-template-stages.sh` executes it today, so the release gate depends on parked code.
+- Drop the parked mirror row for `cultivation/parked/sam-cc-setup/hooks/concurrent-checkout-guard.sh` from `DISTRIBUTION_MIRRORS` in `bin/rendered_harness_contract.py`, plus its five fixtures in `bin/tests/test_rendered_harness_contract.py`. The mirror no longer distributes anything, but it still forces every edit to the shipped seed hook to be copied into a parked file.
+- Delete or retarget the three tests in `bin/tests/test_agent_parity.py` that read `cultivation/parked/` skills (`validate`, `ship`, `agent-team`, `session-critique`, `codex-plan-review`). They assert seed prose agrees with content the plugin no longer ships, so they pass regardless of the plugin surface.
+- Bump the `sam-cc-setup` plugin version and add an `UPGRADING.md` entry before the v3.0.0 tag. v3 removed 23 skills, 5 agents, the plugin hooks, and the fanout workflow, but the ticket froze the `marketplace.json` entry, so installed consumers running `/plugin update` currently see no change.
diff --git a/docs/2026-09-03-distbench-archive-note.md b/docs/archive/2026-09-03-distbench-archive-note.md
similarity index 100%
rename from docs/2026-09-03-distbench-archive-note.md
rename to docs/archive/2026-09-03-distbench-archive-note.md
diff --git a/docs/HANDOFF-2026-09-01-harness.md b/docs/archive/HANDOFF-2026-09-01-harness.md
similarity index 100%
rename from docs/HANDOFF-2026-09-01-harness.md
rename to docs/archive/HANDOFF-2026-09-01-harness.md
diff --git a/docs/HANDOFF-2026-09-03-audit-sessions.md b/docs/archive/HANDOFF-2026-09-03-audit-sessions.md
similarity index 100%
rename from docs/HANDOFF-2026-09-03-audit-sessions.md
rename to docs/archive/HANDOFF-2026-09-03-audit-sessions.md
diff --git a/docs/archive/README.md b/docs/archive/README.md
new file mode 100644
index 0000000..4609c75
--- /dev/null
+++ b/docs/archive/README.md
@@ -0,0 +1,18 @@
+# Archive
+
+Spent documents, kept as a record and not maintained.
+Nothing here is a live instruction.
+Numbers, paths, and file names inside these documents were true when written and many are now wrong.
+
+Archived in v3.0.0 (2026-09-06):
+
+- `specs/rebuild-*`, `specs/rebuild-research/` - the rebuild-epoch research and its design reviews.
+- `specs/concurrent-checkout-hook-ownership-plan.md`, `specs/seed-skill-promotion.md` - superseded by v3 (the harness cut and the park-not-grow decision).
+- `reviews/` - per-session reviews from the audit sessions.
+- `tickets/` - per-session tickets from the audit sessions.
+- `findings/` - the findings tracker. v3 drops the tracker; the PR description is the record.
+- `superpowers/` - old plans and specs for the rendered-harness contract (slated for removal in S3).
+- `HANDOFF-2026-09-01-harness.md`, `HANDOFF-2026-09-03-audit-sessions.md` - old handoffs. `docs/BACKLOG.md` names its own source; it was not built from these.
+- `2026-09-03-distbench-archive-note.md`.
+
+Marketing drafts under `docs/plans/marketing/` were deleted rather than archived; that directory did not exist on this branch at v3 time, so there was nothing to remove.
diff --git a/docs/findings/AGENT-EFFICIENCY.md b/docs/archive/findings/AGENT-EFFICIENCY.md
similarity index 100%
rename from docs/findings/AGENT-EFFICIENCY.md
rename to docs/archive/findings/AGENT-EFFICIENCY.md
diff --git a/docs/findings/CI-PERFORMANCE-DIAGNOSIS.md b/docs/archive/findings/CI-PERFORMANCE-DIAGNOSIS.md
similarity index 100%
rename from docs/findings/CI-PERFORMANCE-DIAGNOSIS.md
rename to docs/archive/findings/CI-PERFORMANCE-DIAGNOSIS.md
diff --git a/docs/findings/FINDINGS.md b/docs/archive/findings/FINDINGS.md
similarity index 100%
rename from docs/findings/FINDINGS.md
rename to docs/archive/findings/FINDINGS.md
diff --git a/docs/findings/PROMPT-AUDIT-2026-09-06.md b/docs/archive/findings/PROMPT-AUDIT-2026-09-06.md
similarity index 100%
rename from docs/findings/PROMPT-AUDIT-2026-09-06.md
rename to docs/archive/findings/PROMPT-AUDIT-2026-09-06.md
diff --git a/docs/findings/prompt-audit-2026-09-06.patch b/docs/archive/findings/prompt-audit-2026-09-06.patch
similarity index 100%
rename from docs/findings/prompt-audit-2026-09-06.patch
rename to docs/archive/findings/prompt-audit-2026-09-06.patch
diff --git a/docs/reviews/2026-09-03-session-2-review.md b/docs/archive/reviews/2026-09-03-session-2-review.md
similarity index 100%
rename from docs/reviews/2026-09-03-session-2-review.md
rename to docs/archive/reviews/2026-09-03-session-2-review.md
diff --git a/docs/reviews/2026-09-03-session-3-review.md b/docs/archive/reviews/2026-09-03-session-3-review.md
similarity index 100%
rename from docs/reviews/2026-09-03-session-3-review.md
rename to docs/archive/reviews/2026-09-03-session-3-review.md
diff --git a/docs/reviews/2026-09-04-session-4-review.md b/docs/archive/reviews/2026-09-04-session-4-review.md
similarity index 100%
rename from docs/reviews/2026-09-04-session-4-review.md
rename to docs/archive/reviews/2026-09-04-session-4-review.md
diff --git a/docs/reviews/2026-09-04-session-5-review.md b/docs/archive/reviews/2026-09-04-session-5-review.md
similarity index 100%
rename from docs/reviews/2026-09-04-session-5-review.md
rename to docs/archive/reviews/2026-09-04-session-5-review.md
diff --git a/docs/reviews/2026-09-05-fable-prompting-review.md b/docs/archive/reviews/2026-09-05-fable-prompting-review.md
similarity index 100%
rename from docs/reviews/2026-09-05-fable-prompting-review.md
rename to docs/archive/reviews/2026-09-05-fable-prompting-review.md
diff --git a/docs/specs/concurrent-checkout-hook-ownership-plan.md b/docs/archive/specs/concurrent-checkout-hook-ownership-plan.md
similarity index 100%
rename from docs/specs/concurrent-checkout-hook-ownership-plan.md
rename to docs/archive/specs/concurrent-checkout-hook-ownership-plan.md
diff --git a/docs/specs/rebuild-ledger.md b/docs/archive/specs/rebuild-ledger.md
similarity index 100%
rename from docs/specs/rebuild-ledger.md
rename to docs/archive/specs/rebuild-ledger.md
diff --git a/docs/specs/rebuild-research/clief-claims-validation-method.md b/docs/archive/specs/rebuild-research/clief-claims-validation-method.md
similarity index 100%
rename from docs/specs/rebuild-research/clief-claims-validation-method.md
rename to docs/archive/specs/rebuild-research/clief-claims-validation-method.md
diff --git a/docs/specs/rebuild-research/clief-claims-verdicts.md b/docs/archive/specs/rebuild-research/clief-claims-verdicts.md
similarity index 100%
rename from docs/specs/rebuild-research/clief-claims-verdicts.md
rename to docs/archive/specs/rebuild-research/clief-claims-verdicts.md
diff --git a/docs/specs/rebuild-research/refagents-merge-review.md b/docs/archive/specs/rebuild-research/refagents-merge-review.md
similarity index 100%
rename from docs/specs/rebuild-research/refagents-merge-review.md
rename to docs/archive/specs/rebuild-research/refagents-merge-review.md
diff --git a/docs/specs/rebuild-research/refagents-sweep.md b/docs/archive/specs/rebuild-research/refagents-sweep.md
similarity index 100%
rename from docs/specs/rebuild-research/refagents-sweep.md
rename to docs/archive/specs/rebuild-research/refagents-sweep.md
diff --git a/docs/specs/rebuild-research/refagents-vercel.md b/docs/archive/specs/rebuild-research/refagents-vercel.md
similarity index 100%
rename from docs/specs/rebuild-research/refagents-vercel.md
rename to docs/archive/specs/rebuild-research/refagents-vercel.md
diff --git a/docs/specs/rebuild-research/refagents-voltagent.md b/docs/archive/specs/rebuild-research/refagents-voltagent.md
similarity index 100%
rename from docs/specs/rebuild-research/refagents-voltagent.md
rename to docs/archive/specs/rebuild-research/refagents-voltagent.md
diff --git a/docs/specs/rebuild-research/refagents-zglass.md b/docs/archive/specs/rebuild-research/refagents-zglass.md
similarity index 100%
rename from docs/specs/rebuild-research/refagents-zglass.md
rename to docs/archive/specs/rebuild-research/refagents-zglass.md
diff --git a/docs/specs/rebuild-research/research-cc-docs.md b/docs/archive/specs/rebuild-research/research-cc-docs.md
similarity index 100%
rename from docs/specs/rebuild-research/research-cc-docs.md
rename to docs/archive/specs/rebuild-research/research-cc-docs.md
diff --git a/docs/specs/rebuild-research/research-codex-docs.md b/docs/archive/specs/rebuild-research/research-codex-docs.md
similarity index 100%
rename from docs/specs/rebuild-research/research-codex-docs.md
rename to docs/archive/specs/rebuild-research/research-codex-docs.md
diff --git a/docs/specs/rebuild-research/research-context-rules.md b/docs/archive/specs/rebuild-research/research-context-rules.md
similarity index 100%
rename from docs/specs/rebuild-research/research-context-rules.md
rename to docs/archive/specs/rebuild-research/research-context-rules.md
diff --git a/docs/specs/rebuild-research/slim-audit-bundles.md b/docs/archive/specs/rebuild-research/slim-audit-bundles.md
similarity index 100%
rename from docs/specs/rebuild-research/slim-audit-bundles.md
rename to docs/archive/specs/rebuild-research/slim-audit-bundles.md
diff --git a/docs/specs/rebuild-session-brief.md b/docs/archive/specs/rebuild-session-brief.md
similarity index 100%
rename from docs/specs/rebuild-session-brief.md
rename to docs/archive/specs/rebuild-session-brief.md
diff --git a/docs/specs/rebuild-structure-design-review-elegance.md b/docs/archive/specs/rebuild-structure-design-review-elegance.md
similarity index 100%
rename from docs/specs/rebuild-structure-design-review-elegance.md
rename to docs/archive/specs/rebuild-structure-design-review-elegance.md
diff --git a/docs/specs/rebuild-structure-design-review.md b/docs/archive/specs/rebuild-structure-design-review.md
similarity index 100%
rename from docs/specs/rebuild-structure-design-review.md
rename to docs/archive/specs/rebuild-structure-design-review.md
diff --git a/docs/specs/rebuild-structure-design.md b/docs/archive/specs/rebuild-structure-design.md
similarity index 100%
rename from docs/specs/rebuild-structure-design.md
rename to docs/archive/specs/rebuild-structure-design.md
diff --git a/docs/specs/seed-skill-promotion.md b/docs/archive/specs/seed-skill-promotion.md
similarity index 95%
rename from docs/specs/seed-skill-promotion.md
rename to docs/archive/specs/seed-skill-promotion.md
index b5b52a2..f86422a 100644
--- a/docs/specs/seed-skill-promotion.md
+++ b/docs/archive/specs/seed-skill-promotion.md
@@ -10,6 +10,7 @@ Full verdicts: `docs/specs/rebuild-research/clief-claims-verdicts.md`.
 
 ## Source pools, in preference order
 
+<!-- stale-counts: allow - dated record. v3.0.0 reversed decision D2: 3 skills ship, the rest are parked. The count below is history and is not corrected. -->
 1. `cultivation/marketplace/sam-cc-setup/skills/` (26 sam-cc-setup skills, Samyak-authored or adapted with license notices).
 2. The SkillSpector-vetted parked bundles in the marketplace manifest (enable-and-adapt, keep SHA pins and licenses).
 3. New skills, only after the trigger that justifies them fires twice.
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
diff --git a/docs/tickets/README.md b/docs/archive/tickets/README.md
similarity index 100%
rename from docs/tickets/README.md
rename to docs/archive/tickets/README.md
diff --git a/docs/tickets/session-2.md b/docs/archive/tickets/session-2.md
similarity index 100%
rename from docs/tickets/session-2.md
rename to docs/archive/tickets/session-2.md
diff --git a/docs/tickets/session-3.md b/docs/archive/tickets/session-3.md
similarity index 100%
rename from docs/tickets/session-3.md
rename to docs/archive/tickets/session-3.md
diff --git a/docs/tickets/session-4.md b/docs/archive/tickets/session-4.md
similarity index 100%
rename from docs/tickets/session-4.md
rename to docs/archive/tickets/session-4.md
diff --git a/docs/tickets/session-5.md b/docs/archive/tickets/session-5.md
similarity index 100%
rename from docs/tickets/session-5.md
rename to docs/archive/tickets/session-5.md
diff --git a/docs/tickets/session-6.md b/docs/archive/tickets/session-6.md
similarity index 100%
rename from docs/tickets/session-6.md
rename to docs/archive/tickets/session-6.md
~~~~~~~~~~~~ evidence
