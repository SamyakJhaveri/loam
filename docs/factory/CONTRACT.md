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
   A check that fails on `main` proves the ticket only when it fails for the reason its author predicted, so a ticket whose Worker section says `contract: 2` gives each non-guard check one line `predict NAME CMD...`, NAME being the word after that check's `pass`, and CMD exiting 0 exactly when base shows the predicted failure (for example `predict greet test -f greeting.txt` for a check that wants `hello` in an existing `greeting.txt`).
   Round 0 runs CMD at base and refuses the ticket as `ticket-defect`, naming the check, when CMD exits non-zero or the line has no CMD; it records a miss in a file of its own, and runs CMD in a subshell, so neither a redirect nor CMD itself can hide one.
   CMD is one simple command: lint rejects a predict line with no CMD, with an unquoted `;`, `&`, `|`, `<` or `>`, or whose CMD is a shell keyword such as `!` or `[[`; write `test ! ...`, and put a compound prediction in `bash -c '...'`.
   In every later round, and under the worker's Stop hook, a predict line prints nothing and returns 0.
   A guard takes no predict line; a body with no contract line may carry predict lines, which round 0 runs, but needs none.
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
9. `## Worker`: `worker: claude|codex`, `codex-review: yes|no`, `effort: low|medium|high|xhigh`, `size: small|large` (optional, default small; large routes round 1 through the fan-out workflow, F12), `contract: 2` (optional; every new ticket carries it, and the done-checks block then has one predict line per non-guard check), `goal:` the condition the round's `/goal` holds until, always the done-checks block printing no FAIL line, ending "or stop after 60 turns", `skills:` (optional) a comma list of skill names the worker must read and follow, each a line of `bin/factory.d/skills.txt` written as the Skill tool lists it (a bare `rigor`, or `plugin:name` for a plugin skill) or a `pstack:<name>` of any installed pstack skill (owner ruling 2026-10-30), which needs no line, and any cap override from `LOOP.md`.
    A Claude worker's prompt names each skill's SKILL.md path, resolved by `skill_file` in `bin/factory`, for it to read; a Codex worker's prompt holds the body (#385).
    A `pstack:` skill sets `disable-model-invocation`, so the Skill tool never lists it, and it needs no line.
    Samyak adds any other line by hand, direct to `main`, after `bin/runner 'claude -p --setting-sources user --max-turns 1 "print skill names"'` prints the name on the runner; a worker runs with `--setting-sources user`, so a project skill such as `catchup` never loads there and never enters the file (#37).
10. `## Decisions`: links to ADRs, closed decision tickets, or the design doc.
11. `## Comments` (optional, always last): answers and notes appended to a ticket file after it is written, where the target keeps tickets as files and its own tracker rules say comments go there, as DistBench's `docs/tickets/` does (owner ruling 2026-10-19).
    Lint rejects any section after it.

Every path under Where, Do not touch, and Approach is verified with `git ls-files` when the ticket is written, or is a path the Goal creates; a guessed path is the commonest small defect and lint rejects it.

`lib.sh` (`bin/factory.d/lib.sh`): F2 ships `pass`, `fail`, and `guard CMD...` (runs CMD and returns its status, and copies each `SKIPPED:` line CMD prints to the checks file even when the guard line sends its output to `/dev/null`); F1 adds `MEASURE`, `render_into`, `check_clean`; #388 adds `predict NAME CMD...` (runs CMD at round 0 only).

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
  A line that starts with `predict` is not a check line and is accepted in every body, unless it has no command after the name, holds an unquoted `;`, `&`, `|`, `<` or `>`, or its command is a shell keyword.
- No text a reader on GitHub cannot see (#389): a character of Unicode category `Cf` (zero-width, bidi controls, tags, BOM, word joiner), a `Cc` other than tab, newline and carriage return, the variation selectors and the other default-ignorable code points a `Cf` rule misses (U+FE00 to U+FE0F, the whole block U+E0000 to U+E0FFF, U+FFF0 to U+FFF8, and U+034F, U+115F, U+1160, U+17B4, U+17B5, U+180B to U+180D, U+180F, U+3164, U+FFA0), the same through a character reference such as `&#x200B;`, or a carriage return with no newline after it.
  Other unassigned code points pass, since Python's Unicode data reads newer emoji as unassigned.
  Lint matches by category, as loop-engineering's triage does (`/[\p{Cc}\p{Cf}]/gu`, MIT), reads the body as UTF-8 through `python3`, names the line and the code point but never the hidden text, and never edits the body; ordinary non-ASCII text such as `café 如果` passes.
- No markdown GitHub hides or draws over its text (#452), found by one offline scan that fails closed: text is code only in the two exact forms below, and all other text is prose.
  A fence opens at column 0 with three or more backticks or tildes (a backtick fence's info string holds no backtick) and closes at the CommonMark closer or the end of the body; its info string is one word of ASCII letters, digits, `_`, `+`, `#` or `-`, and a `mermaid`, `geojson`, `topojson`, `stl` or `math` fence is rejected, since GitHub draws it.
  A fence indented or inside a list item or quote is rejected, since GitHub ends it with its container.
  Outside fences, a backtick run pairs with the next run of the same length on the same line, an odd backslash run before it makes its first backtick literal, and a run left unpaired, a backtick in a link destination, or a `|` inside a span in a block with a table delimiter row turns code spans off to the end of the block (a blank line or a fence).
  In prose, lint rejects every `<` (comments, tags, autolinks, declarations, processing instructions, CDATA), every `$` (math), `![` (an image), `]:` (a link reference or footnote definition), and a link whose `(` holds a space or does not close on its line (a title); a `]` inside a code span after a `[` left open in its block is rejected, since GitHub reads a link reference definition before it pairs code spans; a row with more cells than the narrowest table delimiter row above it in its block (pipes optional when that row holds a `:`, any quote or list prefix dropped) is rejected, since GitHub drops the excess.
  A misread rejects a visible example and never passes a hidden one; an HTML comment in a code span or a fence passes, since GitHub shows it.
  The rule runs on every body, fixtures included.
- In a body whose Worker section says `contract: 2`, each non-guard check name has exactly one predict line; a predict line that names a guard, a name no non-guard check reports, or a name another predict line already names is an error that names it, as is a non-guard check line with no literal name after a command-word `pass`.
  The contract line is exactly one line `contract: 2`; anything else is an error, and a body with no contract line lints as before #388.
  The rule is skipped under `bin/factory.d/fixtures/`, as the path rule is.
- A check line containing a token matching `*test*.py`, `*_test.sh`, or `pytest` that names a path not listed under Do not touch is flagged as a self-graded oracle.
- `worker`, `codex-review`, `effort`, `goal`, and caps take valid values; every `skills:` name is a line of `bin/factory.d/skills.txt`, matched byte for byte (#37), or a `pstack:<name>` of letters, digits, `-` or `_` naming any installed pstack skill (#385; owner ruling 2026-10-30), and resolves through `skill_file` to a SKILL.md under `$HOME`, so a skill missing on the host fails lint there. Lint prints an advisory `warning:` line, never a refusal, for each named pstack skill on its short list of skills that write under `~/` (`setup-pstack`, `reflect`, `automate-me`), since the worker's shell is not sandboxed (#409).
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
predict syntax test ! -e bin/factory
predict rejects-skip test ! -e bin/factory
predict accepts-contract test ! -e bin/factory
predict wired-into-check test -f bin/check
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
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/factory/CONTRACT.md, docs/factory/ROADMAP.md
~~~

On `main` the check `syntax` fails on the missing files, `rejects-skip` because `bin/factory` is missing, and `accepts-contract` because lint is missing, so each one's predict line tests that `bin/factory` does not exist.
`wired-into-check` fails because `bin/check` has no lint step, not because `bin/check` is missing, so its predict line tests that `bin/check` exists.
The guard `check-green` passes and takes no predict line.
