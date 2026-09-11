---
name: brief
disable-model-invocation: true
description: "Turn a raw request (often a transcribed voice note) into a brief: four lines and three fields, echoed back for correction, then handed to the ticket contract for a Track B ticket. Use when you type /brief or start a ticket from a request. Manual only. NOT for writing the ticket body itself (docs/factory/CONTRACT.md) or breaking a large request into several tickets (Track C)."
argument-hint: "[the raw request, often a transcribed voice note]"
---

# brief

**Trigger:** user types `/brief [raw request]`. Manual-only (`disable-model-invocation: true`).
`$ARGUMENTS` is the raw request. If it is empty, ask for the request; never guess it.

You turn a raw request, often a transcribed voice note, into four lines and three fields, then echo them back for correction.
If you catch yourself improving the idea rather than the sentence, stop.

| You may | You may not |
|---|---|
| carry every constraint forward, verbatim | quietly drop a requirement because it looks hard or odd |
| fix grammar, cut rambling, order the steps | soften a strong ask ("rewrite" into "refactor a bit") |
| name the files you verified exist | invent files, numbers, or done conditions |
| ask one question when two readings produce different work | ask a second question, or ask one the codebase can answer |

The form:

```
<the ask, one imperative sentence, their words where they were specific>
Where: <files or dirs verified to exist>
Done means: <observable result: a passing command, a rendered element, a merged PR>
Out of scope: <what you were tempted to add, named so nobody adds it>
Track: A | B | C    Risk: low | high    Mode: build | figure-out    Open question: <at most one>
```

Before echoing, diff your draft against the request: every specific thing they said still there, anything in your draft they did not say deleted.
Do not address the harness in the brief; retry counts, models, and reviewers are configuration.

## Finding the open question

Run a blindspot pass: what in this request depends on a fact you have not read; what would a second engineer read differently; which named file, command, or number have you not verified; what does "done" look like to them that a command cannot see.
Keep the one question whose two answers produce different work.
Drop the rest or answer them from the codebase.

## When the solution is not known

`Mode: figure-out` is set when the ask is a question, names no solution, or says "help me figure out".
It is always Track C.
Stage 1 then opens with `surprise-me` in panel mode and `research` subagents against primary sources before any plan is written; the actors and order are in the `docs/factory/ARCHITECTURE.md` stage table.
The design issue records the options considered, the evidence for each, and the ones rejected with a reason.

## Tracks, by blast radius

- Track A touches none of `seed/**`, `.claude/**`, `bin/factory*`, plugin `agents/**`, trust roots, keychains, or release files.
  It is done in the same session with `bin/check`, one in-session lean-critic pass, and the branch policy in `AGENTS.md` rule 1.
  The commit or PR body is the spec.
- Track B is one feature that fits one ticket.
  The brief becomes the ticket: the ask becomes Goal and why, Done means becomes the done-checks block, Out of scope carries over.
  The author runs the block on `main` by hand once and confirms every non-guard check prints FAIL; lint never runs it; round 0 repeats it on the runner.
  Then lint, then publish.
- Track C is several tickets.
  The brief becomes the top section of a design issue; stage 1 follows, then `to-tickets`.

Risk high means anything Track A excludes, plus outward-facing behavior.
It sets `codex-review: yes` on every ticket once F4 ships the stage, and asks for a human diff read before merge; until F4, `codex-review: no` is valid on a high-risk ticket and the diff read carries the weight.

For a Track B brief, hand these lines to the ticket contract (`docs/factory/CONTRACT.md`, `## The ticket contract`) and publish the issue from this same session; the mapping above (ask to Goal and why, Done means to the done-checks block, Out of scope carried over) is the template, and the sections there are written before implementation.

## Worked brief, Track A

```
Remove the stale loam-s3 worktree registered at ~/Desktop/loam-s3.
Where: git worktree list shows it on branch lean/s3; PR #29 merged that branch.
Done means: git worktree list no longer shows loam-s3 and git status is clean.
Out of scope: pruning any other worktree; deleting the lean/s3 remote branch.
Track: A    Risk: low    Mode: build    Open question: none
```

## Worked brief, Track B

```
Add a static linter for factory tickets so a bad ticket is rejected before a loop starts.
Where: bin/ (new bin/factory with a lint subcommand), bin/factory.d/fixtures/ (committed by F0).
Done means: bin/factory lint rejects the pre-addendum S5 body, accepts the five contract-form bodies, and bin/check runs it.
Out of scope: running any check command; bin/factory run.
Track: B    Risk: high    Mode: build    Open question: none
```
