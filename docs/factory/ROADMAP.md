# Loam Factory: roadmap

One behavior change per session.
Items are in short form here until F0 publishes them as GitHub issues in the contract form; then this file keeps only the order, the dependency, and the issue link.
Items marked Track A need no ticket and no loop.

| Order | Item | Blocked by | Runs under |
|---|---|---|---|
| 0 | F0 Track A fixes | none | any session |
| 1 | F2 ticket contract and lint | F0, `docs/factory` on main | `loop.sh` with a hand-authored prompt and checks |
| 2 | F5 `/brief` skill | F2 | interactive Track B |
| 3 | F6 grader replay | F2 | `loop.sh`, the last hand-authored ticket |
| 4 | F1 `bin/factory run` | S5 merged, v3.0.0, F2 | the first ticket the factory runs on itself |
| 5 | F3 graders | F1, F6 | `bin/factory run` |
| 6 | F4 Codex worker and review stage | F1 | `bin/factory run` |
| 7 | F9 frontier timer | two clean F1 tickets | `bin/factory run` |
| 8 | F7 model-upgrade ablation step | F3 | Track A |
| 9 | F8 promote `bin/factory` up a layer | distbench needs it | `bin/factory run` |

## F0 Track A fixes (now, any session)

- Set `cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md` model to `claude-fable-5-1`, effort stays high; bump the plugin; check the listing weight.
- Fix `gh` on the Mac: re-login the keyring and trust the proxy CA, or install a three-line shim over `ssh jhaveris gh "$@"` that rewrites `--body-file X` to stdin; prove it with `gh api rate_limit`.
- Remove the stale `~/Desktop/loam-s3` worktree.
- Add `bin/runner` (`LOOP.md` Commands) and use it for every remote command from then on.
- Commit `bin/factory.d/fixtures/`: `S5.before.md` and `S1.md` to `S5.md`, the lean-v3 tickets rewritten into the contract form (`CONTRACT.md`).
- Chart the factory as a `wayfinder` map, convert F1 to F9 below into the contract form, publish them through `to-tickets` as GitHub issues with native blocking edges, and replace the bodies here with links. Each ticket then runs as its own loop and merges to `main` before the next starts, so every merged ticket improves the loop that runs the following one.
- Reinstall bradautomates/claude-video, run it on the four unparsed videos, append findings to `../research/community.md`.

## F2 ticket contract and lint

The worked ticket in `CONTRACT.md` is this ticket's body.
Running it under `loop.sh`: F0 publishes the issue unlinted; `tickets/F2.env` names it; `prompts/F2.md` is the worked ticket plus `_common.md`; `checks/F2.sh` is `source lib.sh`, an inline `guard() { "$@"; }`, the done-checks block, and `exit $((n_fail > 0))`; the judge prompt for this run reads "Files owned" as everything not under Do not touch, scores `lean` on the diff alone, and marks `helpful` not applicable.

## F5 `/brief` skill

Goal and why: move the brief section of `CONTRACT.md` into `cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md`, manual-only, so Track B publishes a ticket from one session.
Do not touch: the standing list.
Done checks: the skill validates with `claude plugin validate --strict`; `CONTRACT.md` keeps one line pointing at the skill and no second copy of the form; `bin/skill_listing_weight.py` delta at most 60 tokens; a Track B brief run through the skill publishes an issue that `bin/factory lint` accepts.
Merge checklist: bump the plugin version.

## F6 grader replay

Goal and why: a replay suite on the production grader call path, so no grader edit lands unmeasured.
Do not touch: the standing list, `judge.md`, `reviewer.md`, `lean-critic.md`. Except: `bin/factory`, `bin/factory.d/` (this ticket adds `eval`).
Done checks: `evals/judge`, `evals/reviewer`, `evals/lean-critic` each hold the four cases named in `LOOP.md`, copied from `jhaveris:~/Desktop/loam/.superpowers/lean-v3/loops/runs/`; `bin/factory eval judge` exits 0 on the live judge and exits 1 when one `expected.json` is deliberately flipped; the driver is derived from `git show 8d567f3:bin/harness-smoke.sh`.
Merge checklist: record the first replay run in the PR body.

## F1 `bin/factory run`

Goal and why: `loop.sh` becomes `bin/factory run <issue>` as specified in `LOOP.md`, minus Codex.
Do not touch: the standing list, `seed/`. Except: `bin/factory`, `bin/factory.d/`, the plugin `agents/` directory (this ticket moves `judge.md` and `reviewer.md` there).
Done checks: `bin/factory run` on a trivial Track B ticket in Loam reaches `pr-opened` with `Closes #<issue>` as the PR body's first line and the metrics in it; round 0 exits `ticket-defect` on a ticket whose check passes on base; a killed model call produces `stopped-environment` without consuming a round; the three graders run with `--tools Read,Grep,Glob`; `judge.md` and `reviewer.md` exist under the plugin agents directory with `model: claude-fable-5-1`, `effort: medium`, `tools: Read, Grep, Glob`; the frozen judge and reviewer prompts carry the run's fence string, not a fixed one; `grep -c 'SamyakJhaveri\|jhaveris\|loam-s' bin/factory bin/factory.d/lib.sh` prints 0; `bin/factory status` lists denials per round.
Merge checklist: replace the judge rubric copy in `.superpowers/lean-v3/04-SESSION-PLAN.md` with a link; delete `.superpowers/lean-v3/` on the Mac and the runner.

## F3 graders

Goal and why: the ticket grader, the round-0 probe prompt, the target judge rubric (row names `correct`, `verified`, `honest`; `green` removed), and the lean-critic slop tells, each with a JSON schema.
First try a ticket-specific prompt to the existing `plan-reviewer`; add a `ticket-grader.md` agent only if the eval shows a gap, since each agent costs about 200 always-on tokens per session.
Do not touch: the standing list. Except: the plugin `agents/` directory.
Done checks: `bin/factory eval` passes on every grader before and after with zero verdict changes, row sets re-baselined in the same PR; the ticket grader fails the S1 before case and passes the S1 contract fixture; the round-0 probe on the S4 ticket at `38eefc8` names done check 2 with the payload evidence.
Merge checklist: bump the plugin version; check the listing weight.

## F4 Codex worker and review stage

Goal and why: `worker: codex` and `codex-review: yes` as specified in `LOOP.md`.
Do not touch: the standing list. Except: `bin/factory`, `bin/factory.d/`.
Done checks: a Track B ticket with `worker: codex` reaches `pr-opened`; `codex-review: yes` adds one review section shaped by `review-output.schema.json`; Codex token counts appear in the ledger; whether `codex exec -s workspace-write` blocks a `.env` read is recorded in the PR body either way; `codex login status` is a preflight line.

## F9 frontier timer

Goal and why: `bin/factory next` on a ten-minute runner timer, as specified in `LOOP.md`.
Done checks: after a merge, the next run's ledger start line is within ten minutes with zero operator commands; removing the label parks the ticket; `FACTORY_STOP` at the runs root pauses the timer.

## F7 model-upgrade ablation step

Add one step to `/new-model-workflow`: run `bin/factory eval` for every grader with the new model, then with each rubric body replaced by its one-line stance, and open a Track A change for any row that changed no verdict.

## F8 promote `bin/factory` up a layer

When distbench needs the loop, move `bin/factory` and `bin/factory.d/` to `seed/bin/` or a plugin skill script per `../ASSET-LAYERS.md`, and give `run` a `-C <repo>` argument.
