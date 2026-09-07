# Backlog

Everything from the v3 audit that is still worth doing after v3.0.0 ships.
Source: `.superpowers/lean-v3/01-PENDING-WORK.md`, the ranked LATER list.
Ranked by value to the stated goal, a research partner. Highest first.
One item per session, same verification protocol as the v3 sessions.

Nothing here is scheduled. An item moves out of this file only when a real project needs it (design law 7: the burden of proof is on keeping).

## 1. Research-lane bundle

Sources: RD, S6-2, S6-4, G6, W1, W2, W3, RG.
Ship the parked bundle at `cultivation/parked/research-lane/` as one plugin: vendored skills (rigor, experiment-loop, research-writing, ml-paper-writing), the empty doc templates, the `run.json` plus run-folder convention, and `bin/` verifiers (claims ledger, citation, figure) the agent runs by choice.
Promote to shipped only when a new distbench dogfoods it and a session measures it.
No hooks, no commit gates: file conventions plus verifiers.
Why first: it is the one thing Loam was for and the one thing never built.

## 2. Experiment contract as a file convention

Sources: S6-1, G7 contract half.
A `CONTRACT.md` (question, done-when shell command, budget, seeds, protocol hash) plus a `bin/` verifier.
The done-when check is native `/goal`, not a Stop hook.
Why: the smallest unit of the research lane; it makes unattended runs verifiable without the deleted gate machinery.

## 3. Headless conveyor for the remote eval host

Sources: G7, RF notification half.
A thin `bin/conveyor.sh`: `claude -p` in tmux on the eval host, results sync, Pushover on halt.
Drop the in-loop Codex gate; it is harness-policing.
Notification via the script or a Routine, never a hook.
Why: the owner runs walk-away work on a remote host, but this waits until the contract exists to feed it.

## 4. Ideation chain

Sources: S6-3, G5.
One parked `ideate` skill: frame, diverge with a mandatory retrieval pass, react, ground on an external anchor, plan.
Reuses the already-parked `unknowns` and the shipped `surprise-me`.
Why: retrieval-grounded ideas measured 2.5x impact, but it duplicates native plan mode, so it waits behind the lane it serves.

## 5. Reading room and skill acquisition

Sources: S6-4, G2.
Parked skills `read` (labelled Verified/Likely/Relayed readings into `RESOURCES.md`) and `adopt-skill` (find, vet, eval, adopt).
Plus the "write a skill at the second repetition" rule as one `docs/WORKERS.md` line.
Why: genuine hygiene, low urgency, no platform gap forcing it now.

## 6. Decision ledger and structured handoff prose

Sources: G1 RULINGS half, RC, S6-5, S6-8, G3 brief/report half.
An on-demand `RULINGS.md`, plus the seven-field handoff, worktree isolation, loop, and inline-mermaid guidance, all as `docs/WORKERS.md` prose.
Never always-loaded.
Why: cheap and useful for multi-session work, but it must stay out of the 400-token always-on budget.

## 7. Attach mode

Source: S5, `bin/loam-attach.sh` half.
Keep `bin/loam-attach.sh` for adding the harness to an existing repo.
Why: already built and working; the one forward-sync mechanism with a live use.

## 8. align-prompt and brainstorming polish

Sources: H3, H4d.
Ride with the parked plugin skills; manual only, never auto-wired.
Why: lowest value; a convenience on skills that are themselves parked.

## 9. Owner global-config pass

Source: G8.
Outside Loam entirely: retune `~/.claude/CLAUDE.md`, `FABLE-BRAIN.md`, and the model-split env vars as a personal task.
v3 notes it in one `docs/HARNESS.md` line.
Why: real, but not the template's job.

## Smaller items folded in from the same audit

- F7: `bin/check`'s render smoke renders defaults only. A `project_kind=typescript` render is a LATER item (00-DECISIONS row 3 deferred it).
- Every other open `FINDINGS.md` row (F1 to F6, F8, F9) targets a component v3 deletes or parks, so those fixes are moot. The tracker itself is archived at `docs/archive/findings/FINDINGS.md`.

## S3-owned cleanups created by the v3 park

These exist only because v3.0.0 parked code that other files still point at. Each must land before `cultivation/parked/` can be treated as inert reference material.

- Move `cultivation/parked/sam-cc-setup/hooks/check_stale_counts.py` into `bin/`. Stage 7 of `bin/verify-template-stages.sh` executes it today, so the release gate depends on parked code.
- Drop the parked mirror row for `cultivation/parked/sam-cc-setup/hooks/concurrent-checkout-guard.sh` from `DISTRIBUTION_MIRRORS` in `bin/rendered_harness_contract.py`, plus its five fixtures in `bin/tests/test_rendered_harness_contract.py`. The mirror no longer distributes anything, but it still forces every edit to the shipped seed hook to be copied into a parked file.
- Delete or retarget the three tests in `bin/tests/test_agent_parity.py` that read `cultivation/parked/` skills (`validate`, `ship`, `agent-team`, `session-critique`, `codex-plan-review`). They assert seed prose agrees with content the plugin no longer ships, so they pass regardless of the plugin surface.
- Re-add version-parity coverage for the `sam-cc-setup` plugin. `bin/tests/test_marketplace_skill_routes.py` was deleted in v3.0.0, and it held the only assertion that `plugin.json` and `marketplace.json` versions stay equal, so `cultivation/marketplace/sam-cc-setup/README.md` still claims a parity that nothing now enforces.
- Bump the `sam-cc-setup` plugin version and add an `UPGRADING.md` entry before the v3.0.0 tag. v3 removed 23 skills, 5 agents, the plugin hooks, and the fanout workflow, but the ticket froze the `marketplace.json` entry, so installed consumers running `/plugin update` currently see no change.
