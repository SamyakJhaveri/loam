# Loam Factory: the brief and the ticket contract

This file is the home of the ticket contract (stage 2); the brief form (stage 0) lives in `cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md`.
The stage table and model rules live in `ARCHITECTURE.md`; the supervisor that consumes tickets lives in `LOOP.md`.

## The brief

The brief form - stage 0 - lives in `cultivation/marketplace/sam-cc-setup/skills/brief/SKILL.md`, invoked by hand: the you-may table, the four-line form, the blindspot pass, the tracks by blast radius, and the two worked briefs.
The brief becomes the ticket: the ask becomes Goal and why, Done means becomes the done-checks block, Out of scope carries over.

## The ticket contract

A ticket is a GitHub issue whose body has these sections in this order.
It is the shipped `fable-prompting` plan rubric with fixed names: Goal and why, Do not touch (Constraints), Done checks (Done check per task), Worker (Target model and effort); Session conduct is always unattended.
The body starts at `Brief:` or `Part of`; in a file the first `#` line is the title, or the file opens with the `title:` front matter publish.sh reads, ending in `---`.

1. Title, then `Part of <design issue>` for Track C or `Brief:` followed by the four brief lines for Track B, then `Blocked by:` with issue links or `none` (display only; native blocking edges are what the loop reads).
   The `Brief:` lines are display only; lint and the loop read the sections below.
2. `## Goal and why`: two to four lines, linking the decision, ADR, or design doc.
3. `## Do not touch`: the standing list from `ARCHITECTURE.md` (another target's `docs/factory/STANDING.md`), ticket-specific paths, and any `Except:` line.
4. `## Out of scope`: one line each.
5. `## Approach` (optional): the how where it matters to Samyak, in a few lines: patterns to follow, files to model on, approaches tried and rejected.
   The worker follows it; a departure needs a `decisions.md` line, which the judge reads.
6. `## Done checks`: one fenced block tagged `done-checks`, a bash body sourced after `lib.sh`, run from the worktree root.
   A check is one line of the block and ends in `pass NAME` or `fail NAME reason`, in the form `A && pass N || fail N "why"`.
   A check that calls `guard` (for example `guard bin/check` or `out=$(guard cmd)`) is a regression guard allowed to pass on `main`; every other check must print FAIL on `main`.
   The block is green when it prints no FAIL line; an abort or an `exit` anywhere in the block, at base or in a later round, adds `FAIL checks-aborted`, because `checks.sh` then stops before the end line freeze writes after the block (#180, #277).
   No `skip`.
   The block runs under `pipefail`, so a check never pipes a command that is meant to exit non-zero into `grep`; it captures the output first (`out=$(cmd 2>&1); grep -q pattern <<<"$out"`).
   Written before implementation.
   A check leaves the ticket only through the `abandon` exit in `LOOP.md`.
7. `## Merge checklist` (optional): steps a human or a post-merge action performs, one line each with its command.
   Rendered into the PR body as checkboxes; lint accepts it; the judge ignores it; the loop never converts a done check into one.
8. `## Rows measured` (optional): one line per row, `command | baseline`, run by the supervisor after the checks pass and printed as `MEASURE <row> <value>`.
   A row that measures time, tokens, or cost starts with `runs=N`: the supervisor runs it N times and prints the median and range of its last output lines, which must be numbers.
   A row whose label or command names such a word (`NOISY_ROW_RE` in `bin/factory`) and has no `runs=N` runs once, and its MEASURE line says single sample; `runs=1` marks a row deterministic.
   This is the only per-project extension point.
9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium|high|xhigh`, `size: small|large` (optional, default small; large routes round 1 through the fan-out workflow, F12), `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must read and follow, each a line of `bin/factory.d/skills.txt` written as the Skill tool lists it (a bare `rigor`, or `plugin:name` for a plugin skill) or a `pstack:<name>`, which needs no line, and any cap override from `LOOP.md`.
    A Claude worker's prompt names each skill's SKILL.md path, resolved by `skill_file` in `bin/factory`, for it to read; a Codex worker's prompt holds the body (#385).
    A `pstack:` skill sets `disable-model-invocation`, so the Skill tool never lists it, and it needs no line.
    Samyak adds any other line by hand, direct to `main`, after `bin/runner 'claude -p --setting-sources user --max-turns 1 "print skill names"'` prints the name on the runner; a worker runs with `--setting-sources user`, so a project skill such as `catchup` never loads there and never enters the file (#37).
10. `## Decisions`: links to ADRs, closed decision tickets, or the design doc.
11. `## Comments` (optional, always last): answers and notes appended to a ticket file after it is written, where the target keeps tickets as files and its own tracker rules say comments go there, as DistBench's `docs/tickets/` does (owner ruling 2026-10-19).
    Lint rejects any section after it.

Every path under Where, Do not touch, and Approach is verified with `git ls-files` when the ticket is written, or is a path the Goal creates; a guessed path is the commonest small defect and lint rejects it.

`lib.sh` (`bin/factory.d/lib.sh`): F2 ships `pass`, `fail`, and `guard CMD...` (runs CMD and returns its status); F1 adds `MEASURE`, `render_into`, `check_clean`.

### Done checks for a rendered-project change

A ticket that changes what a rendered project does proves it in a real render: any change under `seed/`, hooks and settings included, or to `copier.yml`.
A grep of the source proves the text, and a hook script fed JSON by hand proves the script; neither proves the harness.
At least one non-guard check renders the checkout and drives a session in the render with `control-loam`, the verify-loam CLI at `.claude/skills/verify-loam/control-loam`, and reads the result from the JSON it prints.
Use `--stub`: a scripted model on 127.0.0.1 answers, so a session costs $0 and a second or two, and the check also runs under the worker's Stop hook.
A paid session (no `--stub`) is only for what a real model must read, such as quote-back or the Fable brief; write its line to pass under `LOAM_HOOK` (`LOOP.md`, The worker prompt).
Each run of the block exports its own `LOAM_VERIFY_ROOT` from `mktemp -d`, so round 0, the Stop hook, and the supervisor never share a render.
`control-loam` points the session's hooks at `<run>/memstore` and unsets `LOAM_MEMSTORE_REMOTE`, so a check never writes `~/memstore`.
`render` copies the working tree, so the check sees uncommitted edits under the Stop hook and the committed tree in the supervisor's run.
The recipe for each behavior (memory, deny rules, the Fable brief, the rendered check) is in `.claude/skills/verify-loam/features/`.

This block proves memory recall: every hook in both stub sessions exits 0, and the second session's `SessionStart` hook prints the `## Memory (render)` block holding the INDEX line `mem-capture.sh` wrote for the first session, found by that session's `session_id`.
`session` does not fail when a hook exits nonzero, so the block reads each hook's `exit_code` itself.
It passes on today's `main` and fails when `seed/.claude/hooks/mem-recall.sh` prints nothing, prints only its heading, or exits nonzero; a ticket that adds a behavior writes its check in this shape, and the check prints FAIL on `main`.

```bash
C=.claude/skills/verify-loam/control-loam; export LOAM_VERIFY_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/verify.XXXXXX"); \
  $C render --run t >/dev/null && s1=$($C session t "Reply OK." --stub --name s1) && s2=$($C session t "Reply OK." --stub --name s2) && \
  jq -e 'all(.hooks[]; .exit_code == 0)' <<<"$s1" >/dev/null && \
  jq -e --arg sid "$(jq -r '.session_id' <<<"$s1")" 'all(.hooks[]; .exit_code == 0) and any(.hooks[]; .event == "SessionStart" and (.stdout | startswith("## Memory (render)")) and (.stdout | contains(" | " + $sid + " | ")))' <<<"$s2" >/dev/null \
  && pass memory-recalled || fail memory-recalled "a hook exited nonzero, or the second stub session's ## Memory block does not hold the first session's INDEX line; evidence in $LOAM_VERIFY_ROOT/t/evidence"
guard $C cleanup t >/dev/null && pass verify-cleanup || fail verify-cleanup "control-loam cleanup t"
```

Every `control-loam` command exits 1 when it fails, and `session --stub` also fails when no request reaches the stub, so a broken render or a wire-format change reads FAIL, never PASS.
The guarded `cleanup` removes the render (about 4 MB), its memstore, and its `~/.claude/projects/` directory, and keeps `evidence/`.

### Publishing a breakdown

The stage-2 session owns the breakdown into vertical slices, the native blocking edges, and publishing to GitHub once Samyak approves the breakdown.
It adds each edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<id>`, where `<id>` is the blocker's database id (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`), not its `#number`; `bin/factory next` reads `issue_dependencies_summary.blocked_by`.
This contract owns the issue body: each issue carries the sections above, and the acceptance checkboxes become the done-checks block.

### Lint rules (`bin/factory lint <issue|file>`, F2)

- Every section present, in order.
- The done-checks block plus `lib.sh` pass `bash -n`.
- Every check line ends in `pass` or `fail`; no `skip` anywhere.
- A check line containing a token matching `*test*.py`, `*_test.sh`, or `pytest` that names a path not listed under Do not touch is flagged as a self-graded oracle.
- `worker`, `codex-review`, `effort`, `goal`, and caps take valid values; every `skills:` name is a line of `bin/factory.d/skills.txt`, matched byte for byte (#37), or a `pstack:<name>` (#385), and resolves through `skill_file` to a SKILL.md under `$HOME`, so a skill missing on the host fails lint there.
- Every path named under Where, Do not touch, and Approach exists in the tree or is named by the Goal as created.
  The path rule is skipped under `bin/factory.d/fixtures/`, whose bodies are historical tickets and name paths that later tickets removed.
- At most three merge-checklist lines on a Track B ticket.
- At least one non-guard check line does not start with `grep`: checks that only grep source text prove the text, not the behavior.
- Lint is static; it never executes a check, though the `skills:` rule reads the installed skills and plugin cache.

Lint runs inside `bin/check` on its fixtures.
Fixtures live in `bin/factory.d/fixtures/`, committed by F0: `S5.before.md`, which lint must reject on its `skip` (the release check becomes a merge-checklist line), `S1.before.md` and `S4.before.md`, the pre-addendum bodies for the F3 evals, and `S1.md` to `S5.md`, the lean-v3 tickets rewritten into the contract form, which lint must accept.
S1's defect (contradictory checks) is semantic; the plan gate that would have caught it is `plan-reviewer`, run by hand over the breakdown before publish, not a dedicated ticket-checking agent.

### Worked ticket: F2

~~~
# F2: ticket contract and lint
Brief:
Add a static linter for factory tickets so a bad ticket is rejected before a loop starts.
Where: bin/ (new bin/factory with a lint subcommand), bin/factory.d/fixtures/ (committed by F0).
Done means: bin/factory lint rejects the pre-addendum S5 body, accepts the five contract-form bodies, and bin/check runs it.
Out of scope: running any check command; bin/factory run.
Blocked by: F0 (fixtures committed, issue published), docs/factory on main

## Goal and why
Reject a defective ticket before a loop spends a dollar on it.
Four of five lean-v3 tickets needed an owner addendum; a static lint catches the mechanical half.

## Do not touch
The standing list. Except: bin/factory, bin/factory.d/ (this ticket creates them).

## Out of scope
Executing any check; bin/factory run; publishing issues.

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
