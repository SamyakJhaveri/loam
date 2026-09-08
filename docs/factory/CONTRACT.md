# Loam Factory: the brief and the ticket contract

This file is the one home of the brief form (stage 0) and the ticket contract (stage 2).
The stage table and model rules live in `ARCHITECTURE.md`; the supervisor that consumes tickets lives in `LOOP.md`.

## The brief

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

### Finding the open question

Run a blindspot pass: what in this request depends on a fact you have not read; what would a second engineer read differently; which named file, command, or number have you not verified; what does "done" look like to them that a command cannot see.
Keep the one question whose two answers produce different work.
Drop the rest or answer them from the codebase.

### When the solution is not known

`Mode: figure-out` is set when the ask is a question, names no solution, or says "help me figure out".
It is always Track C.
Stage 1 then opens with `surprise-me` in panel mode and `research` subagents against primary sources before any plan is written; the actors and order are in the `ARCHITECTURE.md` stage table.
The design issue records the options considered, the evidence for each, and the ones rejected with a reason.

### Tracks, by blast radius

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

### Worked brief, Track A

```
Remove the stale loam-s3 worktree registered at ~/Desktop/loam-s3.
Where: git worktree list shows it on branch lean/s3; PR #29 merged that branch.
Done means: git worktree list no longer shows loam-s3 and git status is clean.
Out of scope: pruning any other worktree; deleting the lean/s3 remote branch.
Track: A    Risk: low    Mode: build    Open question: none
```

### Worked brief, Track B

```
Add a static linter for factory tickets so a bad ticket is rejected before a loop starts.
Where: bin/ (new bin/factory with a lint subcommand), bin/factory.d/fixtures/ (committed by F0).
Done means: bin/factory lint rejects the pre-addendum S5 body, accepts the five contract-form bodies, and bin/check runs it.
Out of scope: running any check command; the ticket grader; bin/factory run.
Track: B    Risk: high    Mode: build    Open question: none
```

## The ticket contract

A ticket is a GitHub issue whose body has these sections in this order.
It is the shipped `fable-prompting` handoff rubric with fixed names: Goal and why, Do not touch (Constraints), Done checks (Done check per task), Worker (Target model and effort); Session conduct is always unattended.
The body starts at `Brief:` or `Part of`; in a file fixture the first `#` line is the title.

1. Title, then `Part of <design issue>` for Track C or `Brief:` followed by the four brief lines for Track B, then `Blocked by:` with issue links or `none` (display only; native blocking edges are what the loop reads).
   The `Brief:` lines are display only; lint and the loop read the sections below.
2. `## Goal and why`: two to four lines, linking the decision, ADR, or design doc.
3. `## Do not touch`: the standing list from `ARCHITECTURE.md`, ticket-specific paths, and any `Except:` line.
4. `## Out of scope`: one line each.
5. `## Approach` (optional): the how where it matters to Samyak, in a few lines: patterns to follow, files to model on, approaches tried and rejected.
   The worker follows it; a departure needs a `decisions.md` line, which the judge reads.
6. `## Done checks`: one fenced block tagged `done-checks`, a bash body sourced after `lib.sh`, run from the worktree root.
   A check is one line of the block and ends in `pass NAME` or `fail NAME reason`, in the form `A && pass N || fail N "why"`.
   A line prefixed `guard` is a regression guard allowed to pass on `main`; every other check must print FAIL on `main`.
   The block is green when it prints no FAIL line and every named check prints exactly one PASS or FAIL line.
   No `skip`.
   Written before implementation.
   A check leaves the ticket only through the `abandon` exit in `LOOP.md`.
7. `## Merge checklist` (optional): steps a human or a post-merge action performs, one line each with its command.
   Rendered into the PR body as checkboxes; lint accepts it; the judge ignores it; the loop never converts a done check into one.
8. `## Rows measured` (optional): one line per row, `command | baseline`, run by the supervisor after the checks pass and printed as `MEASURE <row> <value>`.
   This is the only per-project extension point.
9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium`, `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must invoke, from the set decided in #37, and any cap override from `LOOP.md`.
10. `## Decisions`: links to ADRs, closed decision tickets, or the design doc.

Every path under Where, Do not touch, and Approach is verified with `git ls-files` when the ticket is written, or is a path the Goal creates; a guessed path is the commonest small defect and lint rejects it.

`lib.sh` (`bin/factory.d/lib.sh`): F2 ships `pass`, `fail`, and `guard CMD...` (runs CMD and returns its status); F1 adds `MEASURE`, `render_into`, `check_clean`.

### Seam with to-tickets

`to-tickets` owns the breakdown into vertical slices, the blocking edges, the quiz, and publishing to GitHub.
This contract owns the issue body: the stage-2 session hands the sections above to `/to-tickets` as its issue template, and the acceptance checkboxes become the done-checks block.

### Lint rules (`bin/factory lint <issue|file>`, F2)

- Every section present, in order.
- The done-checks block plus `lib.sh` pass `bash -n`.
- Every check line ends in `pass` or `fail`; no `skip` anywhere.
- A check line containing a token matching `*test*.py`, `*_test.sh`, or `pytest` that names a path not listed under Do not touch is flagged as a self-graded oracle.
- `worker`, `codex-review`, `effort`, `goal`, and caps take valid values; every `skills:` name is in the set decided in #37.
- Every path named under Where, Do not touch, and Approach exists in the tree or is named by the Goal as created.
  The path rule is skipped under `bin/factory.d/fixtures/`, whose bodies are historical tickets and name paths that later tickets removed.
- At most three merge-checklist lines on a Track B ticket.
- Lint is static; it never executes a check.

Lint runs inside `bin/check` on its fixtures.
Fixtures live in `bin/factory.d/fixtures/`, committed by F0: `S5.before.md`, which lint must reject on its `skip` (the release check becomes a merge-checklist line), `S1.before.md` and `S4.before.md`, the pre-addendum bodies for the F3 evals, and `S1.md` to `S5.md`, the lean-v3 tickets rewritten into the contract form, which lint must accept.
S1's defect (contradictory checks) is semantic and becomes a ticket-grader eval case in F3.

### Ticket grader (Fable, fresh context, fixed prompt, F3)

It runs once over the whole breakdown and again on any edited ticket, and answers with JSON through `--json-schema`.
Its questions: do the tickets together deliver every line of the brief's ask and Done means (a line no ticket delivers is a gap even if no ticket named it); does each goal follow from the linked decision; are the checks sufficient for the goal; is anything contradictory; is each ticket one session of work; does any check's English name mismatch its command.
Its rubric text lives in its agent file only.

### Worked ticket: F2

~~~
# F2: ticket contract and lint
Brief:
Add a static linter for factory tickets so a bad ticket is rejected before a loop starts.
Where: bin/ (new bin/factory with a lint subcommand), bin/factory.d/fixtures/ (committed by F0).
Done means: bin/factory lint rejects the pre-addendum S5 body, accepts the five contract-form bodies, and bin/check runs it.
Out of scope: running any check command; the ticket grader; bin/factory run.
Blocked by: F0 (fixtures committed, issue published), docs/factory on main

## Goal and why
Reject a defective ticket before a loop spends a dollar on it.
Four of five lean-v3 tickets needed an owner addendum; a static lint catches the mechanical half.

## Do not touch
The standing list. Except: bin/factory, bin/factory.d/ (this ticket creates them).

## Out of scope
Executing any check; the ticket grader; bin/factory run; publishing issues.

## Done checks
```done-checks
bash -n bin/factory bin/factory.d/lib.sh && pass syntax || fail syntax "bash -n"
[ -x bin/factory ] && ! bin/factory lint bin/factory.d/fixtures/S5.before.md && pass rejects-skip || fail rejects-skip "S5.before.md not rejected, or lint missing"
ok=1; for f in bin/factory.d/fixtures/S[1-5].md; do bin/factory lint "$f" || { fail accepts-contract "$f"; ok=0; }; done; [ "$ok" = 1 ] && pass accepts-contract
grep -q 'bin/factory lint' bin/check && pass wired-into-check || fail wired-into-check "bin/check does not call lint"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: no
effort: medium
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/factory/CONTRACT.md, docs/factory/ROADMAP.md
~~~

On `main` the second line fails because `bin/factory` is missing, the third because lint is missing, the fourth because `bin/check` has no lint step; the first fails on the missing files; the guard passes.
