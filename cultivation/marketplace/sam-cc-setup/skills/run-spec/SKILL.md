---
name: run-spec
disable-model-invocation: true
description: >
  Build a spec whose tickets form a task graph as one branch and one PR, in Loam or DistBench: plan a
  schedule from the blocking edges and the files each ticket touches, run parallel workers in their own
  worktrees, merge each into one integration branch, then run one full check and one review. Use when
  Samyak types it with a spec issue, a ticket list or a ticket file. Not for a single ticket: give it to
  one worker. Not for queued tickets run unattended: use bin/factory next.
argument-hint: <spec issue, ticket IDs, or file>
---

# Run a spec

The goal is one branch and one PR that build the whole spec.
The tickets are a task graph: blocking edges decide what may start, and the files each ticket touches decide what may run side by side.
The lead reads, plans, schedules and merges; workers implement; the lead never implements a ticket inline.
Talk to workers through pointers (the spec, the ticket, `<run>/notes.md`, a commit), not pasted copies.
Before step 1, read the project's column in Projects at the end.

## 1. Read the graph

- GitHub: the spec is an issue and its tickets are its sub-issues (`gh api --paginate repos/<o>/<r>/issues/<spec>/sub_issues`) or the issues whose body says `Part of #<spec>`.
  A ticket's blockers: `gh api --paginate repos/<o>/<r>/issues/<n>/dependencies/blocked_by --jq '.[]|"\(.number) \(.state) \(.state_reason)"'`; a blocker is done only when closed as `completed`.
  Fall back to the body's `Blocked by:` line only when a ticket has no native edges.
- Files: the tickets are files, each with a `Blocked by:` line.
- No tickets: draft the graph yourself into `<run>/plan.md`, one ticket per slice that ends in a checkable state, show it, and wait for Samyak's approval.
- Stop and say so if the graph has a cycle or a ticket waits on work outside the spec that is not done.

## 2. Plan the schedule

`<run>` is `~/.local/state/<repo>/run-spec/<spec>/`, outside the repo and inside the sandbox's writable state folder; notes, the plan, reports and worktrees live there.
If `<run>/plan.md` exists, this is a resume: keep the plan and the `spec-<spec>` branch, and schedule only tickets not yet merged.
List the paths each ticket will touch from its own text (Do not touch, Approach, Implementation notes).
When the tickets do not say, spawn one agent with `subagent_type: scout` to map them and write `<run>/notes.md`: the paths per ticket and the code facts an implementer needs.
Two tickets that change the same file never run at once: add an edge in the order the existing edges already imply, else lower ticket number first, and check the graph for a cycle again.
A one-line addition to the same list or index is not an overlap; resolve that merge conflict yourself.
Start ready tickets in order of how many tickets wait on them, directly or through others, most first.
Run at most 4 workers at once unless Samyak sets another cap; if the run needs more than 12 agents in all, say the count before the first spawn.
Give each ticket effort `high`, or `xhigh` when its core is design, concurrency or a subtle algorithm.
Write `<run>/plan.md` as one row per ticket (ticket, blocked by, touches, effort, status) and print it.

## 3. Branches and worktrees

`<base>` is the base the spec names, else the default branch; with a remote, run `git fetch origin` and use `origin/<base>`.
Make the integration branch in its own worktree, never in the shared checkout.
On a resume, reuse any worktree `git worktree list` already shows, and attach an existing branch without `-b`.

```bash
git worktree add --no-track -b spec-<spec> <run>/wt/spec <base>
```

Give each ticket its worktree when it starts, branched from the integration tip so it carries every merged blocker:

```bash
git worktree add -b spec-<spec>-t<n> <run>/wt/t<n> spec-<spec>
```

Make these yourself; the Agent tool's `isolation: "worktree"` bases a worktree on the lead's checkout, not on the integration tip.

## 4. Implement

Spawn each ready ticket as one background agent with `subagent_type: worker` and the ticket's effort.
The brief names the ticket and the spec by number or path, `<run>/notes.md` when it exists, the worktree and branch, the project's focused test command, and these rules:

- Work and commit only in that worktree, on that branch, with the repo's git identity and no agent co-author; never push.
- Done means the ticket's acceptance holds: its `done-checks` block runs to the end as the project's factory runs it and prints no FAIL line, or each acceptance line has a command whose output shows it. Run the focused tests for the touched files, not the full suite.
- At a blocker, or a check that looks wrong, stop and say so with the evidence; never weaken a check.
- If you cannot finish in this session, commit `wip:` and say where you stopped.
- Write the report to `<run>/t<n>.md`: a first line `Status: done`, `Status: wip` or `Status: blocked`, then files changed, acceptance commands with exit codes, and open items. Reply exactly `DONE <run>/t<n>.md`.

## 5. Merge and refill

The quick check is the project's lint plus the focused tests for the files the merge touched.
The lead is the only writer on the integration branch, so merge one ticket at a time, and only a report whose first line is `Status: done` and whose acceptance commands exited 0.
In `<run>/wt/spec`, run `git merge --no-ff spec-<spec>-t<n>`, then the quick check.
On any other conflict or a red quick check, spawn one worker in `<run>/wt/spec` to repair it, with both tickets' reports as pointers.
Hold every merge and every new start until the repair is committed and the quick check passes; if the repair fails, stop integration and report.
A `wip` ticket, or one that failed its checks, gets one fresh worker on the same branch with the first report as a pointer.
A `blocked` ticket is not retried: mark it blocked, report the evidence, and go on with tickets that do not wait on it.
After a second failure, mark it blocked in the plan, go on with tickets that do not wait on it, and report it.
After each merge, update `plan.md` and start the tickets the merge unblocked, up to the cap.

## 6. Finish

1. Run the project's full check on the final integration tip; this is the validation run, rerun only after review fixes.
2. Run `/code-review high spec-<spec>`, plus the review the project's column names for this kind of change.
   Give the findings you confirm to one fresh worker in `<run>/wt/spec`, then rerun the full check.
3. Typing this skill is Samyak's word to push this one branch and open its PR, never to merge it.
   Push and open the PR; draft when a ticket is blocked or a check is red.
   The body opens with a short paragraph on how the change works and why that makes it correct, then `Closes #<n>` for each finished ticket and for the spec only when no ticket is blocked, then the blocked tickets.
   With no remote, skip this and name the branch.
4. For each merged ticket, confirm `git -C <run>/wt/t<n> status --porcelain --untracked-files=no` prints nothing, then `git worktree remove --force <run>/wt/t<n>` (the force also drops untracked files such as build output) and `git -C <run>/wt/spec branch -d spec-<spec>-t<n>` (`-d` checks merged-ness against the branch checked out where it runs).
   Keep a blocked ticket's worktree and branch and name them in the report; remove `<run>/wt/spec` last and keep its branch.
5. Report the plan table with final status, the PR link, the full check's exit code, and end with `Risks:`.

## Projects

| | Loam | DistBench |
|---|---|---|
| Read first | `docs/factory/CONTRACT.md` (the ticket shape) | `~/distbench/docs/design/ORIENTATION.md`, then its `SESSION-STATE.md` and `APPROVALS.md`; `~/distbench/docs/tickets/README.md` (ticket shapes, edges, files tickets share) |
| Tickets | GitHub issues with native blocking edges; the spec is the design issue they say `Part of` | Files `~/distbench/docs/tickets/F<NN>-*.md` with `Blocked by:` lines; the spec is a list of ticket IDs or a plan naming them. A session ticket (it needs Samyak, money or the Vast pair) is not run here: list it for Samyak |
| Done checks | A fresh `bash` from the worktree root sources `bin/factory.d/lib.sh`, then runs the block | The same prelude from `~/loam`; GPU and Docker checks run on jhaveris under the GPU lock in `~/distbench/docs/tickets/SESSION-PROTOCOL.md` section 6 |
| Focused tests | The tests for the touched files | `PYTHONPATH=$PWD/src ~/distbench/.venv/bin/python -m pytest -q -p no:cacheprovider <tests>` |
| Full check | `bin/check`, run by the lead | The operator gate (`bin/check`, then `~/distbench/bin/done-checks`) runs only in Samyak's shell: open with `NEEDS YOU:` and the exact command from SESSION-PROTOCOL section 6 |
| Review | Agent-facing text, a hook, a grader or the factory: one read-only Codex round (`/sam-cc-setup:codex-review`) and one Fable round, then an Opus verify. A `seed/` change needs a `verify-loam` proof | Codex read-only on the PR, each finding reproduced or rejected by an Opus verifier (SESSION-PROTOCOL section 3a) |
| Push and PR | `gh` runs outside the sandbox | `gh` fails in the sandbox: give Samyak the `git push` and `gh pr create` commands |
