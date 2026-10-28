---
name: implement-spec
disable-model-invocation: true
description: >
  Implement a spec whose tickets form a task graph as one branch and one PR: plan a schedule from the
  blocking edges and the files each ticket touches, run parallel workers in their own worktrees, merge
  each into one integration branch, then run one full check and one review. Use when Samyak types it
  with a spec issue or file. Not for a single ticket: give it to one worker. Not for queued tickets run
  unattended: use bin/factory.
argument-hint: <spec issue number, URL or file>
---

# Implement a spec

The goal is one branch and one PR that implement the whole spec.
The tickets are a task graph: blocking edges decide what may start, and the files each ticket touches decide what may run side by side.
The lead reads, plans, schedules and merges; workers implement; the lead never implements a ticket inline.
Talk to workers through pointers (the spec, the ticket, `<run>/notes.md`, a commit), not pasted copies.

## 1. Read the graph

- GitHub: the spec is an issue and its tickets are its sub-issues (`gh api repos/<o>/<r>/issues/<spec>/sub_issues`) or the issues whose body says `Part of #<spec>`.
  A ticket's blockers: `gh api repos/<o>/<r>/issues/<n>/dependencies/blocked_by --jq '.[]|"\(.number) \(.state)"'`; a closed blocker is done.
  Fall back to the body's `Blocked by:` line only when a ticket has no native edges.
- Files: the spec is a file and its tickets are files beside it, each with a `Blocked by:` line.
- No tickets: draft the graph yourself into `<run>/plan.md`, one ticket per slice that ends in a checkable state, show it, and wait for Samyak's approval.
- Stop and say so if the graph has a cycle or a ticket waits on work outside the spec that is not done.

## 2. Plan the schedule

`<run>` is `~/.local/state/implement-spec/<repo>-<spec>/`, outside the repo; notes, the plan, reports and worktrees live there.
List the paths each ticket will touch from its own text (Where, Approach, Do not touch).
When the tickets do not say, spawn one agent with `subagent_type: scout` to map them and write `<run>/notes.md`: the paths per ticket and the code facts an implementer needs.
Two tickets that change the same file never run at once: add an edge, lower ticket number first.
A one-line addition to the same list or index is not an overlap; the merge handles it.
Start ready tickets in order of how many tickets wait on them, directly or through others, most first.
Run at most 4 workers at once unless Samyak sets another cap; if the run needs more than 12 agents in all, say the count before the first spawn.
Give each ticket effort `high`, or `xhigh` when its core is design, concurrency or a subtle algorithm.
Write `<run>/plan.md` as one row per ticket (ticket, blocked by, touches, effort, status) and print it.

## 3. Branches and worktrees

Make the integration branch in its own worktree, never in the shared checkout, from the base the spec names or the default branch:

```bash
git worktree add -b spec-<spec> <run>/wt/spec <base>
```

Give each ticket its worktree when it starts, branched from the integration tip so it carries every merged blocker:

```bash
git worktree add -b spec-<spec>-t<n> <run>/wt/t<n> spec-<spec>
```

Make these yourself; the Agent tool's `isolation: "worktree"` bases a worktree on the lead's checkout, not on the integration tip.

## 4. Implement

Spawn each ready ticket as one background agent with `subagent_type: worker` and the ticket's effort.
The brief names the ticket and the spec by number or path, `<run>/notes.md` when it exists, the worktree and branch, and these rules:

- Work and commit only in that worktree, on that branch, with the repo's git identity and no agent co-author; never push.
- Done means the ticket's acceptance holds: its `done-checks` block prints no FAIL line, or each acceptance line has a command whose output shows it. Run the project's focused checks for the touched files, not the full suite.
- At a blocker, or a check that looks wrong, stop and say so with the evidence; never weaken a check.
- Near 150K context, commit `wip:`, write your state into the report and stop.
- Write the report to `<run>/t<n>.md` (files changed, commands with exit codes, open items) and reply exactly `DONE <run>/t<n>.md`.

## 5. Merge and refill

The lead is the only writer on the integration branch, so merge finished tickets one at a time.
In `<run>/wt/spec`, run `git merge --no-ff spec-<spec>-t<n>`, then the project's quick check.
On a conflict or a red check, spawn one worker in `<run>/wt/spec` to repair it, with both tickets' reports as pointers, and hold other merges until it reports.
A ticket whose worker is blocked or fails its checks gets one fresh worker with the first report as a pointer.
After a second failure, mark it blocked in the plan, go on with tickets that do not wait on it, and report it.
After each merge, update `plan.md` and start the tickets the merge unblocked, up to the cap.

## 6. Finish

1. Run the project's full check once, on the final integration tip; this is the one validation run.
2. Run `/code-review` on the integration branch against `<base>`, plus any extra review the project's rules require for this kind of change.
   Give the findings you confirm to one fresh worker in `<run>/wt/spec`, then rerun the full check.
3. Typing this skill is Samyak's word to push this one branch and open its PR, never to merge it.
   Push and open the PR; draft when a ticket is blocked or a check is red.
   The body opens with a short paragraph on how the change works and why that makes it correct, then `Closes #<n>` for the spec and each finished ticket, then the blocked tickets.
   With no remote, skip this and name the branch.
4. Remove each ticket worktree (`git worktree remove`) and delete its merged branch (`git branch -d`); remove `<run>/wt/spec` last and keep its branch.
5. Report the plan table with final status, the PR link, the full check's exit code, and end with `Risks:`.
