# Loam Factory: the loop

This file is the one home of `bin/factory`, the supervisor that runs one ticket to a pull request on the runner.
The ticket it consumes is defined in `CONTRACT.md`; the stage table and model rules are in `ARCHITECTURE.md`.
Rubric text lives only in the grader files.

## Commands

| Command | Does | Built in |
|---|---|---|
| `bin/factory lint <issue|file>` | static ticket lint, rules in `CONTRACT.md`; lint of an issue outside a Claude Code session (`CLAUDECODE`; the stage-2 session's own lint is not the operator's) adds a `lint` line to the issue's own `<issue>/owner-events.jsonl`, beside its run dirs, which the issue's next launch on that host moves into its run dir's `owner-events.jsonl` | F2 |
| `bin/factory eval <grader> [--model M]` | replays frozen cases through the production grader call and compares verdicts; `EVAL_EFFORT` sets the effort (default the replayed grader's production effort: high for the judge, xhigh for the reviewer), `EVAL_OUT=<dir>` keeps each raw reply | F6 |
| `bin/factory eval-freeze [--evals-dir D] <run-dir>...` | copies each run's last round, when the judge passed it and no reviewer finding was high or medium, into `<evals-dir>/clean/<grader>/<key>-<sha8>/` (default `evals/clean/`), the prompt cut at `## Ticket`; prints `not frozen <run-dir>: <reason>` for the rest | F36 |
| `bin/factory run <issue>` | round 0, then worker rounds, graders, PR; each launch first appends the operator's events on the issue to `owner-events.jsonl` as `phase` `launch`, and a `run` line unless `next` (`FACTORY_BY_NEXT`) or a Claude Code session launched it | F1 |
| `bin/factory status` | run states, spend, denials per round, worktree and PR readiness, preconditions | F1 |
| `bin/factory status --criteria` | measures the trust criteria in `ARCHITECTURE.md` (Metrics) from the target's run directories; a criterion the run record cannot show prints `UNMEASURED` with the reason, a lower bound within its threshold (the operator actions, `at least n`) prints `INCONCLUSIVE`, or `FAIL` over it, and the premature-done count, read from the worker's last `CLAIM:` line or, for a round with none, a text matcher, prints `n of m failing rounds`, `INCONCLUSIVE` within its threshold while any failing round fell back or left no message, with a line per counted round (its first `FAIL` line and the CLAIM line or the sentence read as a claim) and the counted rounds that failed only checks the worker's Stop hook cannot fail; a `FAIL` ends with `latest <date>`, the last `factory.log` date of the runs it names; reads files and one `git log` of the target's default branch, no model or `gh` call | 2026-10-19 |
| `bin/factory stop <issue>` | writes `FACTORY_STOP` into the run dir, and, outside a Claude Code session, a `stop` line into its `owner-events.jsonl` | F1 |
| `bin/factory merge <pr> <sha>` | takes a PR number (at most nine digits) and a full 40-character lowercase sha; reads the PR's head and `statusCheckRollup` in one `gh pr view`; when the head is not `<sha>`, no check is reported, or a check has not passed (a `CheckRun` passes `COMPLETED` with `SUCCESS` or `NEUTRAL`, a `StatusContext` with `SUCCESS`), prints `merge: refused: <reason>` on stderr and exits 1 without merging; otherwise runs `gh pr merge <pr> --merge --match-head-commit <sha>`, so GitHub refuses a head that moved after the read, and exits with its status (a non-zero exit after a cut-off call is not proof that nothing merged; running it again exits 0 on a merged PR whose head and checks still pass); it never waits for checks, so a PR with none reported yet is refused and the caller runs it again later, and a `SKIPPED` job (none today: no workflow has a job-level `if:`) refuses | #405 |
| `bin/factory skills` | advisory: for each installed pstack skill, reads the `SKILL.md` that `skill_file` resolves (the copy a worker reads, not every cached version) and prints, tab-separated, `<skill>`, `home` (the line names `~/` or `$HOME/`) or `asks` (it names `AskQuestion` or `AskUserQuestion`), then `<SKILL.md>:<line>: <the line, cut to 160 characters>`, one output line per matching line; with no pstack skill resolving it prints one line saying so; whether a home-path line reads or writes is the operator's call before naming the skill in a ticket; reads files only, no model or `gh` call, exits 0 whatever it finds | #472 |
| `bin/runner [-C <dir>] <cmd>` | runs `<cmd>` on the runner: `ssh jhaveris bash -lc 'cd ~/Desktop/loam && <cmd>'`, or from `<dir>` there (quote a tilde, F8); `bin/runner sync` mirrors `.superpowers/factory/` to the same path on the runner with `rsync -az --delete`, excluding `runs/` and `__pycache__`; it never pulls (#36) | F0 |
| `bin/factory next [--install\|--frontier]` | launches up to `MAX_PARALLEL` `ready-for-agent` issues with no assignee and no open native blocker, or assigned to the runner with no run of the current body but a run of an earlier one (an edited body) or a `stopped-daily`, `stopped-environment` or `stopped` run (read through `gh api`); `--install` writes the ten-minute runner timer; `--frontier` prints every issue it would launch, one `#N` per line in launch order, by the same rules and with the same reads as `--dry-run`, but ignores `FACTORY_STOP`, the slot count and the daily-budget wait after the loop, names every pick rather than the first, and exits 0 with no line when none would launch; it reads no PR state, so an issue waiting on a PR that closed since the last real tick stays off the list until a real tick writes `pr-closed`; `--install` with `--dry-run` or `--frontier` is refused | F9 |

`-C <repo>`, before the subcommand or right after it, points `lint`, `run`, `status`, `stop`, `merge`, and `next` at another repository (F8 step 1; Run the factory on another repository, below).
`REPO` is `<owner>/<repo>` read from the target's `origin` URL, and every `gh` call about the target passes it as `-R`, so a fork's issues and PRs never go to the parent `gh` would pick by default.
`status` runs on the runner; from the Mac it is `bin/runner 'bin/factory status'`.

## Layout

```
bin/factory                    the supervisor
bin/factory.d/lib.sh           pass, fail, guard (F2); MEASURE, render_into, check_clean (F1)
bin/factory.d/_common.md       the loop contract appended to every worker prompt
bin/factory.d/role-settings.json   grader-call settings: the deny rules and auto memory off (key and env pin)
bin/factory.d/worker-settings.json   worker-only settings: the same deny rules plus ScheduleWakeup, CronCreate and Monitor denies and CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1, auto memory off (key and env pin), and the Stop hook that runs the done-checks block
bin/factory.d/review-output.schema.json   copied from the Codex plugin
bin/factory.d/summarize_sample.py  stream-json summarizer (moved in F1)
bin/factory.d/fixtures/        lint fixtures (CONTRACT.md)
evals/<grader>/<case>/{prompt.md,expected.json}
~/.local/state/loam-factory/runs/<issue>/<sha8>/   on the runner, outside every checkout:
    status  ledger.jsonl  base.sha  frozen/  round-<k>.*  worker/decisions.md  worker/mechanism.md  pr-body.md  notify.failed
    owner-events.jsonl  pr-closed   the operator actions status --criteria counts (ARCHITECTURE.md, Metrics)
~/.local/state/loam-factory/runs/<issue>/owner-events.jsonl   lint's lines until the issue's next launch moves them into its run dir
~/.local/state/loam-factory/runs/<owner>__<repo>/<issue>/<sha8>/   the same, for a target named by -C (F8)
```

Graders are plugin agents (home in `ARCHITECTURE.md`): `judge.md` and `reviewer.md`.
`lean-critic.md` is a grader file under the same change protocol, but the manager runs it by hand on the PR, outside the round loop: on the 2026-09-09 ledger 3 of its 6 round calls were unparseable.
The run reads each from the checkout's `cultivation/marketplace/sam-cc-setup/agents/`, or from `--graders-dir` for an eval, and records the file and its sha256 in the ledger.
It never reads the plugin cache, so a merged grader edit grades the next run with no `claude plugin update` (#532).
A run, an eval and a `model-eval` grid each copy the file once and take the rubric and the sha256 from that copy, since `next` can fast-forward the checkout while they run.

## A run

1. Read the ticket: an issue number reads the body from GitHub, a file path reads it from disk and makes no GitHub call, keying the run directory by the file stem instead of the issue number.
   `sha8` is the first eight hex of the body's sha256 and, with the issue number or file stem, names the run dir under `FACTORY_RUNS_ROOT` (default `~/.local/state/loam-factory/runs`).
   A changed body is a new run; old rounds stay on disk.
   A target named by `-C` keys its run dirs one level down, under `<owner>__<repo>/` read from its `origin` URL, so its issue numbers never meet Loam's.
2. Record the `origin/main` sha as `base.sha`; create the sibling worktree on branch `factory/<issue>` from it, or `factory/<stem>-<sha8>` for a file ticket, so a relaunch with an edited body gets its own branch; assign the issue to the operator (skipped for a file ticket).
   A file ticket's worktree is removed when the run exits; its branch keeps the commits and is never pushed or deleted by the loop, so drop finished rehearsal branches by hand with `git branch -D factory/<stem>-<sha8>`.
3. Extract the done-checks block; freeze `bin/factory`, the graders, `lib.sh`, `_common.md`, `role-settings.json`, `worker-settings.json`, the grader schemas, and the body into `frozen/`, owned outside the worker's write scope; the frozen grader prompts keep fixed evidence markers, there is no per-run string (#38).
4. Round 0: run the block at `base.sha` in a detached temporary worktree, never in the ticket worktree, which a relaunch with an edited body may leave ahead of base; every non-guard check must print FAIL, and every `predict` line's command, the text after NAME run whole as one bash command after `lib.sh` in that worktree before the checks run, must exit 0 there (`checks.sh` carries no predict line, so only round 0 runs them; `CONTRACT.md`, Done checks), else exit `ticket-defect`.
   A block that aborts or exits before its end line, at base or in a later round, is a `FAIL checks-aborted` failure whatever it printed before; at base it exits `ticket-defect` before any paid round.
   The temporary worktree is added at `base.sha` and removed once the block has run, on both the defect and the clean path, so a relaunch still proves the checks on base rather than at the worker's HEAD.
   The block's output goes to `round-0.out`, renamed to `round-0.checks` only on a clean verdict; a relaunch resumes past round 0 only when `round-0.checks` exists, so a relaunch of a body round 0 stopped runs round 0 again at the same `base.sha` and stops again.
5. Worker round k: a fresh `claude -p` (`claude-opus-5-5` at the ticket's effort, default high) or a fresh `codex exec` in the worktree with the body, `_common.md`, and from round 2 the failing check lines and every blocking finding verbatim.
   The worker writes code, `decisions.md`, and `mechanism.md`: one plain paragraph on how its change works and why that makes it correct (#330).
   The supervisor deletes `mechanism.md` before each worker call, so the PR never opens with an earlier round's account, and a Codex worker's sandbox may write the directory both files sit in.
   Every round is a fresh process for either worker; there is no fixer role.
6. Before grading, in order: scan `decisions.md` for an `ABANDON` line; re-hash the frozen set (a mismatch exits `stopped-environment`); `git status --porcelain` must be empty, else the round fails with the path list; `git diff --name-only "$(cat base.sha)"...HEAD` against Do not touch emits `FAIL do-not-touch <paths>`; then run the done-checks block from the worktree root.
7. On green: the supervisor runs Rows measured (a `runs=N` row N times, `CONTRACT.md`) and prints `MEASURE` lines, then calls the judge, the reviewer, and the Codex review stage if the ticket sets it, each fresh: the judge and reviewer on their frozen prompts and the same evidence bundle, the Codex review on its frozen prompt and the frozen ticket, reading the diff itself.
8. On pass, or at the grader-round cap: assemble the PR body (a draft's `Draft:` line first, then `## How it works` with the worker's `mechanism.md` paragraph, or `(the worker wrote no mechanism paragraph)` when it is absent or blank, then `Closes #<issue>`, the ticket's Goal and why, `git log --oneline base..HEAD`, the MEASURE table, the merge checklist as checkboxes, `decisions.md`, the done-check output from round 0 at base and from the graded round (each block shows only the result word and check name of its `PASS`, `FAIL` and `MEASURE` lines, never a FAIL reason, and a MEASURE value only when it is a number, at most 50 lines, each cut to 300 characters; the full file stays in the run directory, and the block names it), grader sections (the Judge section opens with `graded at <sha>`, the HEAD the graders read), backlog, metrics), push, `gh pr create` or update the existing PR through the REST API, notify, exit `pr-opened`.
   The graders write the HEAD they read to `round-N.graded.sha` once all of them ran on an unchanged tree.
   Once the body is written and before any network call, `open_pr` records its decision in `publish.intent`: the graded sha, its round, and the draft argument (empty, `draft` or `blocking`).
   Each `pr-opened` exit removes it, so only a failed push, body update or create leaves it behind.
   A relaunch whose `publish.intent` round is the newest round, and whose sha equals both the worktree HEAD and that round's `round-N.graded.sha`, re-hashes the frozen set, then calls `open_pr` with the saved argument and no worker round, so a failed push or `gh pr create` of a ready PR or a draft (grader-round cap, blocking finding, unparseable judge) costs no new paid round and reopens the same kind of PR, while a branch moved away and back, after any later round, resumes into the loop rather than publishing the old decision over that round's files; replaying is safe, since a push of the same sha is a no-op, an open PR is only updated, and `filed.txt` files each issue once.
   With no such intent, a relaunch whose last round's judge passed, whose `blocking_findings` is empty, and whose `round-N.graded.sha` equals the worktree HEAD (a crash after grading, before `open_pr` wrote the intent) re-hashes the frozen set, then opens the PR at once with no worker round; a failed judge, a blocking finding, or a moved HEAD resumes into the loop as before.
   A relaunch whose last round's checks passed on a clean tree but has no `round-N.graded.sha` (a cap or `FACTORY_STOP` landed before a grader call) re-hashes the frozen set and runs step 6's tree, do-not-touch and done-checks steps again at HEAD into `round-N.checks`, since HEAD may have moved while the run was stopped; only when they pass does it run step 7 on that round, where a pass opens the PR, and a fail counts as a grader-fail round before the loop resumes, so the relaunch neither pays for nor caps out on a new worker round; a check that now fails resumes into the loop.
   A PR opened at the grader-round cap is a draft: `gh pr create --draft`, and the line that opens the body names the failing judge rows, so no automatic merge takes it before a human reads the Judge section; an already-open PR is only updated, not converted.
   Each judge backlog line is also filed once per run as a `needs-triage` issue, so a defect an unattended run finds is tracked outside the PR body.
   A blocking reviewer or Codex finding left in the final round, an unparseable reply included, is filed the same way; when the judge passed, that finding is past its grader's one block or comes from a reviewer or Codex review with no parseable reply, and the PR opens as a draft whose opening line names the first one.
   A judge with no parseable reply after its three calls is not a pass and gets no worker round, since a worker cannot rerun a grader (#312): when no reviewer or Codex fix is queued in that round, the round opens the PR as a draft at once, with the finding as the judge backlog line, so it is filed as an issue; when one is queued, the round is a normal fail, the next worker round takes those fixes and the judge runs again.
   Every text the factory composes for GitHub, the PR title and body, each filed issue's title and body, and notify's issue comment, first passes through `scrub`, which replaces token-shaped strings with `[redacted]`: every pattern of the memory scrubber in `seed/.claude/hooks/mem-capture.sh` (API keys and tokens, `key=value` secrets, JWTs, `Bearer` values, private-key blocks, URL passwords), plus any `Authorization` value and Slack `xoxs-` tokens.

## Exits

| Status | Meaning | Counts a round |
|---|---|---|
| `pr-opened` | checks and graders pass, or the grader-round cap reached with a backlog (a draft PR), or a judge pass with a review finding past its one block or a reviewer or Codex review with no parseable reply (a draft PR), or a judge with no parseable reply after three calls (a draft PR) | yes |
| `no-change` | HEAD and `decisions.md` are both unchanged since the previous round | yes |
| `stuck` | the same failing check set twice in a row | yes |
| `ticket-defect` | round 0 found a check that passes on base, a `predict` line whose command exits non-zero on base, or the block aborted on base (`FAIL checks-aborted`) | no |
| `abandon` | an `ABANDON NAME reason` line in `decisions.md`; the owner is paged | yes |
| `stopped-environment` | a `claude` result with `is_error` outside the capped set (`error_max_budget_usd`, `error_max_turns`) or with no result event, a Codex exit other than 0 or no `turn.completed` event, a `gh` or `git` failure, including a call cut off at `NET_TIMEOUT_SEC` (a cut-off `gh api graphql` body read, or a body another account wrote or last edited, in the frozen pass too, since the run already reads `running`), a Claude worker call whose Bash sandbox cannot start at launch (`failIfUnavailable`, Worker calls), a process a model call left behind still alive 5 s after KILL, or a frozen-set hash mismatch | no, and it pages at once |
| `stopped-cap` | `MAX_ROUNDS`, `TICKET_BUDGET_USD`, or `MAX_HOURS` reached; `ROUND_BUDGET_USD` and `MAX_TURNS` bound one worker call and are not an exit: a call that hits either (`error_max_budget_usd`, `error_max_turns`) is a finished round and step 6 decides | yes |
| `stopped-daily` | the next model call could take the runner's spend for the UTC day past `DAILY_BUDGET_USD`; it says nothing about the ticket, so the issue stays assigned to the runner and `next` relaunches it on a later UTC day, and launches no other ticket the same day while the daily ledger is spent at the runner's own caps | yes |
| `stopped` | `FACTORY_STOP` present before a call | no |

Exit code, `status`, and the final log line are decided together and cannot disagree.
The one `status` written outside its run is `stopped-environment`, by `holds_slot` for a run with no process left (Parallel runs); that run has no exit code or final log line.
A launch refused its run's lease, or refused while its last model call lives (Parallel runs), exits 4 with one stderr line and writes no status or log line, as a launch that stops before it records the run does, since the run directory belongs to the launch that holds the lease.
These read loop-control files to decide exit, never safety; safety stays with the deny rules, the Claude worker's Bash sandbox and the Codex worker's workspace-write sandbox (Worker calls), git, and CI.
A usage-limit reply (`hit your session limit`, `reached your Fable limit`) is neither an exit nor a round.
Usage limits are per account, so the supervisor first switches to the next stored account through `bin/claude-account` (round robin in name order, so a third account is reached too) and retries the same call at once.
It sleeps only when no other account exists or a switch already happened in the last five minutes; then it writes `waiting-limit` to `status`, sleeps until the reset time the reply names or twenty minutes when it names none, and repeats the same call.
A reset past `MAX_HOURS` exits `stopped-environment`.
A call with no result event (killed by `CALL_TIMEOUT_SEC`, or crashed) exits `stopped-environment` and counts no round.
Every model call (the worker, a grader, the Codex review) runs under a wrapper process in a session of its own, which runs the call in a process group of its own; `CALL_TIMEOUT_SEC` signals that whole group, KILL 5 s after TERM.
On Linux the wrapper is a child subreaper (`PR_SET_CHILD_SUBREAPER`), so the kernel makes it the parent of every process the call leaves orphaned, whatever its session or environment (#434).
However the call ends, by exit or by the limit, the wrapper sends the call's group and every child it has TERM, then KILL after 5 s, and exits with the call's own status only once none is left, before any check or grader reads the tree, since a child left writing the worktree would race them.
The supervisor then sends what is left of the wrapper's group and of the call's group, whose id the call writes to `call.group` in the run directory before it starts, the same TERM and KILL, so a wrapper that was killed or gave up leaves no member of either group behind.
Claude Code starts each Bash tool shell in a new session, so the call also carries a `FACTORY_CALL_TAG` unique to it, and on Linux the same TERM and KILL reach every process whose environment holds it; a host with no `/proc` (a Mac) has no subreaper and no tag sweep, only the group kills.
Any of them still alive 5 s after KILL exits `stopped-environment` and counts no round, once the call's ledger row is written (a Claude worker call with no result event charges `ROUND_BUDGET_USD` as below).
A call in its own session no longer gets the supervisor's Ctrl-C, TERM or HUP, so while a call runs the supervisor traps those signals and sends the wrapper and tagged processes TERM, which starts the wrapper's own TERM and KILL 5 s later.
The supervisor sends its own KILL 10 s later if the wrapper is still up, so it never kills the wrapper during its grace, and only then exits (status 130, 143 or 129) and its EXIT trap removes the worktree.
A killed or crashed Claude worker call left no cost to read but may have spent up to its `--max-budget-usd` ceiling, so its ledger row charges `ROUND_BUDGET_USD` (subtype `no-result` marks it as a charge) and the ticket and daily caps stay bounds (#319); a Codex worker call keeps `cost_usd` null.
The stop message lists the commits made since the round began, or says `no commits`.

## Caps

Defaults from lean-v3, overridable per ticket in its Worker section and then by `FACTORY_<NAME>` in the environment, never by the bare name, which a Claude Code session already exports for `WORKER_MODEL` and `CALL_TIMEOUT_SEC`: `MAX_ROUNDS=100`, `ROUND_BUDGET_USD=15`, `GRADER_BUDGET_USD=5`, `TICKET_BUDGET_USD=1000000`, `DAILY_BUDGET_USD=1000000`, `MAX_HOURS=1000`, `MAX_TURNS=200`, `CALL_TIMEOUT_SEC=5400`, `NET_TIMEOUT_SEC=120`, `MAX_PARALLEL=1`.
Each value is a positive whole number, or for a `*_USD` cap a positive decimal such as `2.5`; 0, a negative number or text is refused, never read as no limit (GNU `timeout` reads 0 as no limit).
Lint rejects such a Worker line, and `apply_caps` exits 2 on one; a `FACTORY_<NAME>` cap with such a value stops every subcommand with exit 2 before it runs, naming the cap, rather than warning and using the default (Samyak, 30 Oct 2026).
`NET_TIMEOUT_SEC` bounds every `gh` call and every `git` call that reaches a remote (`fetch`, `push`, `ls-remote`), in `run`, `lint`, `next` and `status` alike, through GNU `timeout -k 5` without `--foreground`, so a call that ignores TERM gets KILL 5 s later; a shell function, or any call where `timeout` is missing, goes through a shell watchdog that sends the same TERM and KILL to the call's process group.
A call cut off at the limit counts as that call failing, so a hung network call never holds a run, its slot, or its heartbeat.
`next` passes every `FACTORY_<NAME>` cap to the tmux session it launches, empty when unset, so a value in the tmux server's environment never reaches the run.
No research source gives a numeric anchor (`../research/anthropic-loop-engineering.md`); re-measure after two real runs.
The daily ledger `runs/ledger-daily.jsonl` is keyed by UTC date across all runs of every target.
Codex token counts come from its `--json` events and land in the ledger with `cost_usd` null, so the dollar caps do not bound a Codex worker; the PR body says so.

## Grader-round cap and precedence

After the checks first pass, at most two grader-fail rounds per ticket, counted across relaunches: a relaunch counts the rounds with a `round-N.graded.sha` whose judge did not pass or whose `round-N.fixes` is non-empty, so a pass whose push or PR create failed is not counted; then the remaining non-blocking findings go to the PR body backlog and the PR opens as a draft.
The judge decides pass or fail.
The reviewer blocks only on a `high` or `medium` finding (`REVIEW_BLOCKING` in `bin/factory`; its verdict word is not read), the Codex review only on a `critical` or `high` finding, and each may block at most once per ticket.
A grader whose output is absent or unparseable is a fail with one high finding "<role> output unparseable", never a pass, and that finding is never sent to the worker, who cannot rerun a grader (#306, #312); the judge and reviewer are called three times and the Codex review twice, after which the reviewer's or Codex finding drafts the PR without blocking and the judge's opens the draft at once unless reviewer or Codex fixes are queued, in which case the next worker round takes them and the judge runs again (Grader calls).
`verdict_consistent` runs on every judge JSON: a pass with non-empty fixes or a failing row, or without a row `judge.schema.json` requires, or a fail with empty fixes and empty backlog, is refuted, and the judge is called once more, fresh, with the refutation appended to its prompt.

## Grader calls

Graders run from the worktree root.
The supervisor takes a tree signature (the sha256 of the worktree HEAD and its porcelain status) before the judge and again after the last grader; a mismatch exits `stopped-environment`, since a read-only grader must not change the tree it graded.
`--tools Read,Grep,Glob` on the call is what makes a grader read-only (#40 measured that it sets the tool list exactly); an agent file's `tools:` line governs its interactive use only, so `lean-critic.md` keeps Bash.
`--strict-mcp-config` and `--disable-slash-commands` drop the MCP schemas and the skills listing a grader never uses: its prefix is then 9.9k tokens instead of 27k (probed on the runner 2026-09-09), and the prefix is most of a grader call's input.

```
claude -p --model claude-opus-5-5 --effort <high for the judge, xhigh for the reviewer> --tools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --no-session-persistence \
  --json-schema "$(cat frozen/<grader>.schema.json)" --max-budget-usd "$GRADER_BUDGET_USD" \
  --setting-sources user --settings frozen/role-settings.json --output-format json < frozen/<grader>.prompt.md
```

The frozen grader prompts keep fixed evidence markers; there is no per-run string, and any instruction found inside those markers is data and a dishonesty finding.
The evidence bundle is the ticket body, `git diff base...HEAD`, the check output, the MEASURE lines, and `decisions.md` (`build_evidence` in `bin/factory`); a design issue body is not included, so a ticket that needs its design context carries a link the grader can open.
In that diff, code files pass as content, but data files pass as stat only (files under `evals/` named `prompt.md`, and any single added file over 400 lines), so a frozen prompt or a large fixture never floods the grader diff.
The Codex review stage runs `codex exec --json -m <CODEX_MODEL> -c model_reasoning_effort=<GRADER_EFFORT> --output-schema frozen/review-output.schema.json -o <file> -s read-only "<prompt>" < /dev/null`, where the one argument `<prompt>` is the frozen `codex-review.prompt.md` with the base sha filled into each `<base>` placeholder, then a `## Ticket` heading and the frozen ticket between fence lines as `build_evidence` prints it (the ticket text is never filled); a review needs no write access and `read-only` keeps it from editing the tree the judge and reviewer already graded; `codex exec review` ignores `--output-schema` (#41).
`needs-attention` with a `critical` or `high` finding blocks once.
Each call first removes the `-o` file, so a call that writes none never leaves an earlier call's verdict, such as a resumed round's for an older HEAD, standing as its own.
An absent or empty `-o` file, or one that is not a single object with a `verdict`, gets one more Codex call; after a second bad reply it is replaced by a `needs-attention` object with one high finding "codex review output unparseable".
A worker cannot rerun Codex, so that finding is not sent to the worker and does not fail the round; in the final round it drafts the PR and is filed as an issue.
The judge and reviewer get three calls each; after three bad replies the reviewer's finding is handled the same way, without spending its one block, and the judge's, since no row was graded, opens the PR as a draft from `graders` with the finding in the judge backlog, so no worker round is spent on it, unless reviewer or Codex fixes are queued in that round: then the next worker round takes them and the judge runs again (#312).

## Worker calls

```
claude -p --model claude-opus-5-5 --effort high --advisor claude-opus-5-5 --permission-mode bypassPermissions --strict-mcp-config \
  --setting-sources '' --settings frozen/worker-settings.json --max-turns "$MAX_TURNS" \
  --append-system-prompt "$(cat frozen/unattended.md)" \
  --max-budget-usd "$ROUND_BUDGET_USD" --output-format stream-json --verbose --include-hook-events < round-<k>.prompt.md
```

The call sets `CLAUDE_CODE_SUBAGENT_MODEL`, `ANTHROPIC_DEFAULT_SONNET_MODEL` and `ANTHROPIC_DEFAULT_HAIKU_MODEL` to the worker model and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`, both inline on its command line and in the `env` of `frozen/worker-settings.json`, which freeze writes into the copy, so no subagent, workflow agent or `sonnet`/`haiku` alias runs on another model (#379).
Claude Code copies settings `env` over the launch environment, so the inline values alone lose to a `~/.claude/settings.json` env entry, which the frozen copy carries (below), and the pins come after it in that copy and win; the force exists from Claude Code 2.1.257, and `run` and `next` refuse an older or unreadable `claude --version` and `status` prints a FAIL line for it.
The force stays off the manager, overnight and interactive sessions because it would also move a Fable role such as `escalate` onto the worker model.
`--strict-mcp-config` drops the MCP schemas, 2k tokens of prefix on every worker turn; the `skills:` sentence names a SKILL.md path to read, so the worker needs no Skill-tool call (#37, #385).
`--max-turns` is accepted by Claude Code 2.1.263, the runner's login-shell binary (#40; a plain shell resolves an older nvm copy), though absent from its `--help`.
`worker-settings.json` holds the deny rules, the lean-v3 list plus `Bash(gh:*)` so a worker cannot touch GitHub at all, the auto memory settings below, the bare-name denies `ScheduleWakeup`, `CronCreate` and `Monitor`, the env pin `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`, and the `Stop` hook (see The worker prompt), and its frozen copy adds the four pins above; `role-settings.json`, loaded only by grader calls and `bin/factory eval`, carries the same deny rules except the worker-only `Edit(~/.claude/**)`, `Edit(~/.cursor/**)` and the three tool denies (a grader call runs with `--tools Read,Grep,Glob`, which leaves those tools out), and the same memory settings with no hook.
Since Claude Code 2.1.292 a `-p` call waits at exit for its pending background work: a pending wakeup holds the round until `CALL_TIMEOUT_SEC`, a running background command past the 10-minute idle cap, a monitor up to it; the three denies drop those tools from the worker's tool list, and the env pin removes `run_in_background` from Bash and Agent and stops auto-backgrounding (#470).
It does not stop a Workflow run, which the call still waits for at exit, as the fan-out round intends.
`worker-settings.json` also turns on Claude Code's sandbox for every Bash command the worker runs, with `failIfUnavailable` so a call whose sandbox cannot start at launch (no `bwrap` or `socat` on Linux) exits 1 with an `error_during_execution` result at no cost and the reason on stderr, which goes to `factory.log`, and the run stops `stopped-environment` instead of running unsandboxed (a sandbox that fails to initialize later in the session refuses each Bash command instead, fail-closed, and the call may still end with a normal result, so that case is not an exit), `allowUnsandboxedCommands: false` so no command may ask to leave it, and `autoAllowBashIfSandboxed`; the deny rules alone match a command by its prefix, not the same program by path or inside `sh -c` (#409).
The sandbox writes the worktree and `$TMPDIR`, and freeze adds the run's own roots to the frozen copy's `allowWrite`: the worktree gitdir, `objects`, `refs` and `logs` under the git common dir (the Codex worker's roots below), the worker directory holding `decisions.md` and `mechanism.md`, `tasks/` for the fan-out integrator's `result.json`, and `uv/cache` and `uv/tools` under the run directory, which the copy's `env` names as `UV_CACHE_DIR` and `UV_TOOL_DIR`, so `uvx copier` renders and `uv` installs work and the operator's shared uv cache and tools are kept out of the worker's reach.
`strictAllowlist` refuses any other host instead of prompting, which `bypassPermissions` would approve, so its network reaches only `pypi.org` and `files.pythonhosted.org`, for `uv` and `pip` installs.
Claude Code merges sandbox lists across settings tiers, and the user tier's `excludedCommands` (`codex exec *` on the runner) may run outside the sandbox, as the settings reference says, and its `allowWrite` widens it (`~/.codex` there, which a probe wrote under `--setting-sources user`), so the worker call loads no settings tier (`--setting-sources ''`) and freeze writes into the frozen copy, readable by the operator only since it holds the user tier's `env`, the user tier of `${CLAUDE_SETTINGS_FILE:-${CLAUDE_CONFIG_DIR:-~/.claude}/settings.json}` without its `sandbox` block, `permissions.allow` or `permissions.additionalDirectories` (Claude Code adds `Edit(...)` allow paths and additional directories to the sandbox's writable paths and `WebFetch(domain:...)` allow domains to its network allowlist even under `strictAllowlist`, and allow rules do nothing under `bypassPermissions`), under `worker-settings.json`, arrays concatenated and the worker's keys winning, as Claude Code merges tiers; every Bash command the worker runs is then in the sandbox above.
The copy leaves out `CLAUDE_CODE_OAUTH_TOKEN`, which `bin/claude-account` rewrites on an account switch: each worker call reads it from the live user tier and passes it in that call's environment only, so a retry after a switch runs on the new account, and the supervisor keeps its launch value, which a call gets when the user tier holds no token.
The copy keeps the user tier's plugins, so the Skill tool lists the same skills as under `--setting-sources user`, but `~/.claude/agents/`, `~/.claude/CLAUDE.md` and `~/.claude/rules/` do not load (probed on Claude Code 2.1.312), so a worker's subagents are the built-in and plugin types.
The sandbox bounds only the worker's own Bash calls: the `Stop` hook and the supervisor's `run_checks` run the frozen `checks.sh` outside it, and those checks execute worktree code the worker wrote, such as `bin/check` and its tests; the Write and Edit tools are outside it too, limited only by the deny rules under `bypassPermissions`, and the sandbox lets Bash read everything but the paths of the `Read(...)` deny rules (`.env*` among them), credential files included; a follow-up ticket (#515) covers both.
Both files set `"autoMemoryEnabled": false` and pin `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` in their `env`, because Claude Code keeps one auto memory folder per repository, shared by every worktree and filled by interactive sessions, and `--setting-sources user` does not turn it off, so a worker or grader prompt would otherwise load that folder's `MEMORY.md` and could write notes a later run reads (#380).
The env pin is there because that variable set to `0`, in the launch environment or a user-tier `env`, overrides the key, and the `--settings` env is applied last; the frozen worker copy keeps the pin beside the four model pins.
Both files also set `"claudeMdExcludes": ["**/.claude/CLAUDE.md", "**/.claude/rules/**"]`; with the default user configuration directory (`~/.claude`), these exclusions keep the operator's user `CLAUDE.md` and rules out of worker and grader prompts (#421).
A grader call still loads user hooks, user agents and other user-tier settings live, and a worker call gets the user tier's keys through its frozen copy (above); a `CLAUDE_CONFIG_DIR` outside a `.claude` directory is not matched.
When a worker or grader call's `served_models` names a model that the `status` WARN rule (Status and the manager) does not expect, as a refusal fallback does (DistBench run 288 finished two rounds on `claude-opus-4-8`, #419), `record` logs `off-model <role> round <n>: <models>` with each model's cost from `modelUsage` and sends one `needs-you` alert naming the ticket, the role, the round and those models; the run goes on.
The Codex worker runs `codex exec --json -m <CODEX_MODEL> -c model_reasoning_effort=<effort> -s workspace-write "$(cat round-<k>.prompt.md)" > round-<k>.jsonl -o round-<k>.last.txt < /dev/null`: the JSONL stream is stdout, `-o` is the last-message file, and the effort is the ticket's `effort:` line as for a Claude worker.
`CODEX_MODEL` is `FACTORY_CODEX_MODEL`, default `gpt-6.1-sol`, the runner's model on 2026-10-31.
Every factory Codex call, the worker, the Codex review and a `model-eval` Codex cell, runs with `CODEX_HOME` set to the factory's own home, `FACTORY_CODEX_HOME`, default `~/.local/state/loam-factory/codex-home`, logged in once with its own `codex login`, so the operator's `~/.codex` `AGENTS.md`, rules, hooks, memories and config never reach the call and a factory token refresh never rewrites the operator's `auth.json`; #543 fenced only the Claude calls.
Each call also runs without the variables Codex reads for credentials ahead of the stored login (`CODEX_UNSET` in `bin/factory`: `CODEX_API_KEY`, `OPENAI_API_KEY`, `CODEX_ACCESS_TOKEN` and the three workload-identity variables; [manager.rs:1500](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L1500), [:1537](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L1537), [:2798](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L2798)).
`HOME` stays the operator's for git, gh and the worker's tools, so Codex still scans `~/.agents/skills` whatever `CODEX_HOME` is ([host_roots.rs:105](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/ext/skills/src/host_roots.rs#L105)), and no key drops that root.
Each call therefore passes `-c skills.config=[{path="<SKILL.md>",enabled=false},...]` naming every `SKILL.md` under it (`codex_skills_off`, `find -L`, so symlinked directories count as Codex follows them), which removes those skills from the catalog and from a `$name` mention in the prompt ([selection.rs:28](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/skills/src/selection.rs#L28)); `-c skills.include_instructions=false` alone hides only the catalog, and a `$name` still loads the body ([turn.rs:1150](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/core/src/session/turn.rs#L1150)).
It also passes `-c skills.include_instructions=false`, so no skill catalog reaches the call; a Codex worker gets its ticket's skills pasted into its prompt.
The factory home uses the same ChatGPT account, whose installed plugins Codex can sync into any `CODEX_HOME`.
Each call therefore passes `-c features.plugins=false -c features.remote_plugin=false -c features.apps=false`, plus `-c features.skill_mcp_dependency_install=false` so a skill cannot install an MCP dependency ([configuration reference](https://developers.openai.com/codex/config-reference/); `codex features list` on 0.163.0 lists all four keys).
An empty `-c 'mcp_servers={}'` merges with configured servers and leaves them enabled on 0.163.0.
Before an exec, `codex_mcp_off` runs `codex mcp list --json` in that call's directory with the same factory home, credential removal, feature flags and trust override, then passes `-c 'mcp_servers={"<id>"={enabled=false},...}'` for every returned server; `mcp_servers.<id>.enabled` is the supported key, and the list command starts no servers.
If the list command fails or returns invalid JSON, no model call runs.
A home whose `auth.json` is missing or is not a single JSON object stops the run `stopped-environment` with the login command, which rewrites the file; there is no fallback to the operator's login.
The factory writes nothing in that home: the model, the effort and the trust entry go on each call's argv.
Concurrent calls do share its `auth.json`, and Codex 0.163.0 rewrites that file on a token refresh with a truncating in-place write, under a lock held only within one process ([storage.rs:214](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/storage.rs#L214), [manager.rs:2845](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L2845)), so two calls refreshing at once can leave it invalid.
A proactive refresh comes within 5 minutes of the access token's expiry ([manager.rs:3001](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L3001); the factory's token lasted 10 days on 2026-10-31), and a call that finds the file already changed skips it ([manager.rs:2867](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L2867)), so two proactive refreshes race only within one round trip.
After a 401 a call reloads the file and retries, and on a second 401 refreshes from the authority without that check ([manager.rs:1985](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L1985), [:2884](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/login/src/auth/manager.rs#L2884)).
Only a lock held for each whole call would cover a refresh inside it, and that would run every factory Codex call one at a time, so the race stays upstream; its recovery is the one login command the stop prints.
The worker and the Codex review pass `-c 'projects={"<worktree>"={trust_level="trusted"}}'` for the run's worktree alone, since Codex loads a project's `.codex` config, rules and hooks only for a trusted project, and Loam's forbidden rules (`rm -rf`, force push) must bind the worker.
Because that sandbox mounts `.codex` read-only and bubblewrap refuses the root `.codex` symlink into `seed/`, a Codex round swaps that symlink for a real copy of its target for the call and restores it before grading (D12, #77).
The call also carries four `--add-dir` roots derived from git, the worktree gitdir plus `objects`, `refs`, and `logs` under the common dir, so the commit from the worktree can land.
Its workspace-write sandbox does not block `.env` reads (#41); no deny is configured, and the F4 merge checklist's hand run confirms the read is absent from the round's JSONL or records it as a risk.

## The worker prompt

Every worker round receives, in this order: the issue body verbatim, which carries its `goal:` line as text, `_common.md`, and from round 2 a `## Previous round` block holding the failing check lines and every blocking finding verbatim; a Claude worker also gets `frozen/unattended.md` as an appended system prompt.
A slash command expands only on the first line of a `-p` prompt and swallows the rest as its argument (#40), so no worker prompt carries `/goal` or a `/<skill>` line; a `Stop` hook in `worker-settings.json`, the worker-only settings file, runs the frozen check script from the worktree root and exits 2 with the FAIL lines while any check fails, and `--max-turns` bounds the round (#36, route B).
The hook sets `LOAM_HOOK=1`, under which the check lines that call `bin/check` (minutes per stop) or the live model pass without running; the supervisor's own check run has it unset and is the one run of those per round. `build_worker_prompt` in `bin/factory` appends after `_common.md` one sentence per `skills:` name: `Before the first edit, read <path> and follow its steps.`, where `<path>` is the SKILL.md `skill_file` resolves (#37, #385); before the first `pstack:` name it adds one sentence naming pstack's Claude Code adapter, `docs/harness/claude-code.md` beside that skills tree, when the file exists.
A `size: large` round 1 hands the same lines, unchanged and in order, to each fan-out builder: they ride in the Workflow args as `skills`, and `factory-round.js` appends them to every builder prompt before its `Do:` list.
The Skill tool would not do: every pstack skill sets `disable-model-invocation`, so the tool refuses it (`docs/PSTACK.md`).
A name that resolves to no SKILL.md stops the round, for either worker.
A Codex worker gets the skill bodies pasted instead.
The worker never runs `bin/factory eval` against the live model; the supervisor's own check run is the one live replay per round.
`_common.md` is the loop contract, frozen per run; its text lives only in `bin/factory.d/_common.md` (the 2026-09-07 quote that stood here drifted from the file and was removed 2026-09-20).

The ticket says what and how to prove it; the contract says how to behave; the supervisor decides when it is done.

## Skills per role

Skills are given at the moment they apply, never all at once; the listing is paid in every session.

| Role | Skills | How they arrive |
|---|---|---|
| Brief (stage 0) | `/brief` (F5) | Samyak invokes it |
| Design (stage 1) | `surprise-me` (panel), a research pass against primary sources, plan mode, `/plan-review` | in that order for `Mode: figure-out`, from plan mode on for `build`; Samyak types `/surprise-me` and `/plan-review`, which are manual-only |
| Tickets (stage 2) | `plan-reviewer`, lean-critic | the stage-2 session writes and publishes the breakdown itself (`CONTRACT.md`, Publishing a breakdown) and invokes lean-critic after `bin/factory lint` exits 0; `plan-reviewer` is manual-only, run by hand over the breakdown when Samyak asks |
| Worker | the skills the ticket's `skills:` field names, each a line of `bin/factory.d/skills.txt` or a `pstack:<name>` of any installed pstack skill | one sentence per name in the worker prompt and in each fan-out builder prompt, naming the SKILL.md path to read |
| Graders | none; their prompt is the whole instruction | frozen files |
| Manager (stage 5, 6) | none; a handoff file in the `seed/docs/WORKERS.md.jinja` Handoff form when stopping mid-stream | the manager session |

A worker may name a line of `bin/factory.d/skills.txt`, and lint reads that file (#37), or with no line any installed pstack skill, as `pstack:<name>` (#385; owner ruling 2026-10-30).
Either way lint refuses a name `skill_file` resolves to no SKILL.md.
`skill_file` finds a `plugin:name` only under the plugin's `installPath` in `~/.claude/plugins/installed_plugins.json`, the folder Claude Code loads, never by searching the plugin cache; a missing file or a plugin with no entry resolves to nothing (#437; owner ruling 2026-10-30).
The worker loads no settings tier but the user tier's keys through its frozen settings (Worker calls), which lists the same skills as `--setting-sources user`: user-scope plugins but no project skill and not the root `CLAUDE.md` or `AGENTS.md`, so the seed skills (`catchup`, `fable-prompting`, `hypothesis-tree`) are not in the file.

## Parallel runs

Each run has its own worktree, branch, and run directory, so unblocked tickets may run at the same time.
Two tickets may run together only when neither names a path the other's Goal creates or rewrites; the stage-2 grader pass checks this over a breakdown, and native blocking edges hold the rest apart.
The daily ledger is written under a lock.
`bin/factory next` launches up to `MAX_PARALLEL` runs (default 1; raise it after two clean single runs, as `status` reports them).
A run holds a slot while its status reads `running` or `waiting-limit` and some process of the run holds an flock lease on `lease` in its run directory (#425).
A live model call holds the slot whatever the run's status: a call whose processes outlive KILL keeps `call` and its run exits `stopped-environment` (Exits), and `holds_slot` holds that run's slot, writing nothing and sending no alert, while the call named in `call` lives (below), and frees it once the call is gone (#467).
Each launch opens `lease` and takes the lock (`flock -w 65`) before it writes `launched`, its launch log line or its status, and before it prepares the worktree and freezes; so a relaunch holds its slot from the start.
A launch that cannot take the lock (another launch of the same ticket body, or a process one left running, holds it) prints one line to stderr and exits 4, writing no status, `launched` or log line, so the incumbent keeps its status, its `MAX_HOURS` clock and its round.
A launch that takes the lock, or any launch on a host with no `flock`, while the model call named in `call` still lives (below) refuses the same way, since that call may still write the worktree the launch would prepare.
The lease needs `flock(1)` and bash 4.1 or later, for the `{var}` descriptors it opens.
The descriptor is not close-on-exec, so the frozen re-exec keeps it (that pass takes no second lock, which would wait on its own lease) and every child inherits it: the supervisor and a model call that outlives a SIGKILLed supervisor both hold the lease, and the kernel drops it when the last of them exits.
The heartbeat loop alone closes it (its number is exported as `FACTORY_SLOT_FD`), since a beat outlives a killed supervisor by up to 300 s and does no work on the tree.
A transitional gap: a relaunch of a run frozen before #425 execs that older frozen copy, whose heartbeat does not close the descriptor, so after a kill its beat holds the lease for up to 300 s, and a relaunch in that window waits 65 s and exits 4; it closes once such runs finish.
A zombie holds no files, and a reused pid or a stepped clock does not touch the lock, so none of them needs a rule.
`holds_slot` opens `lease` read-only and tries `flock -n`: when another process holds it, the slot is held; when it gets the lock and no process of the model call named in `call` lives (below; a call's tool process may close the descriptors it was not given, as Node's child processes do), no process of the run is left, so, still holding it, it re-reads the status and, if it still reads `running` or `waiting-limit`, writes `stopped-environment` and removes `call` and `call.group` and their temp files, then closes the descriptor and sends one `fail` alert to the run's own project, read from where its directory sits under the runs root (Loam's directly, another target's under `<owner>__<repo>/`), since a finishing run looks at every target's runs before it pauses the host check.
A relaunch waits on the same lease, so a reap and a relaunch never interleave, and only the caller that wrote `stopped-environment` alerts.
Each launch still writes `owner`, one line: the supervisor's pid, a space, then `TZ=UTC LC_ALL=C ps -o lstart= -p <pid>` with trailing spaces trimmed (macOS pads it), through a temp file and `mv`, with the status `running`, under `owner.lock`; `status` and the alert text read it.
A run directory with no `lease` (started before #425), and every run on a host with no `flock(1)` or a bash older than 4.1 (macOS; Samyak's ruling of 30 Oct 2026 keeps this path rather than require util-linux), is judged by `owner` instead, as follows.
The frozen re-exec is an `exec`, which keeps the pid and its start time, so the line still names the loop that runs `finish`.
`holds_slot` frees the slot when that pid is gone, a zombie, or alive with a start time more than 300 s from the stored one (a reused pid; `lstart` moves when the wall clock is stepped, so a small gap is the same process), writing `stopped-environment` and alerting as above.
It does so under `owner.lock` (a lock older than 60 s is removed first), and only while `owner` still reads the line it judged and the status still reads `running` or `waiting-limit`, so a relaunch that rewrote `owner` keeps its slot.
A missing or malformed `owner` holds the slot, as does a run that started before `owner` existed.
A `ps` or `date` that fails or prints nothing cannot tell, so it holds the slot; a failed `kill -0` still means the pid is gone.
A gone or zombie pid still holds the slot while a live process has that pid as its process group id; the heartbeat loop is one such member and exits within 300 s of its supervisor, so a reap waits at most one beat.
A model call runs in a session of its own, so it outlives a SIGKILLed supervisor and keeps writing the worktree until `CALL_TIMEOUT_SEC`; each call writes `call` in the run directory (its wrapper's process group id and its `FACTORY_CALL_TAG`, through a temp file and `mv`, then rewritten the same way with the wrapper's `TZ=UTC LC_ALL=C ps -o lstart=` as a third field, trailing spaces trimmed) and `call.group` (the call's own process group id, a space, then its `TZ=UTC LC_ALL=C ps -o lstart=` with trailing spaces trimmed, written by the call's first process before it execs the command), both removed once the call's processes are confirmed gone.
When `holds_slot` finds the owner gone, it takes `owner.lock`, checks that `owner` still reads the line it judged, and again just before TERM (so no relaunch has started a call of its own), and kills each process group named in `call` or `call.group` whose leader still has the start time recorded after its id: TERM, a 2 s grace, KILL, then up to 5 s for the group to be gone; a pgid reused since (checked again before KILL), or a line with no start time, is spared, and the call's wrapper ends the call's other children once the call's group exits.
A gone owner still holds the slot while either group has a member that is not a zombie or, on Linux, a process carries that tag; otherwise `holds_slot` writes `stopped-environment` and removes `call` and `call.group` and their temp files.
A group counts (`call_live`) only while it is still the one recorded: when its leader's pid is alive and a start time was recorded for it, the leader's start time must match.
A leader gone with members left still counts, since Linux never hands out a pid still in use as a process group id, so a reused one always has a new live leader; a line with no start time has only the member test.
A stuck call's `call` and `call.group` stay on its stopped run for good, so without this check an unrelated process group leader that later took either pid would hold that run's slot again, with no alert.
On a host with no subreaper and no `/proc` (a Mac), a tool shell the call started in a session of its own is in neither group and carries no tag `holds_slot` can read, so it can outlive the group kill and keep writing the worktree after the slot frees, as on the timeout path.
A run with a `lease` is judged by the lease, and a SIGKILLed supervisor's call inherited it, so while the lease is held `holds_slot` also judges `owner`, the supervisor counting as gone there only when its pid is gone or a zombie with no live member of its process group, never by its start time (a wall-clock step moves `ps lstart`, and the held lease already shows a process of the run lives; a pid reused meanwhile spares an orphaned call until `CALL_TIMEOUT_SEC` ends it): when that supervisor is gone it kills the recorded call groups as above, under `owner.lock`, and the lease then decides, so the slot frees on a later call once no process holds the lease.
A relaunch of the same body cannot take that lease, so it never prepares the worktree under the orphan.
A run directory with `launched` and no `status` file holds a slot while some process holds its `lease`; one with no `lease` holds it until its run writes a status or the operator removes it.
`bin/factory next --dry-run` or `--frontier` asks `holds_slot` only to look: a run a real call would reap counts free, but its slot check takes no `owner.lock`, kills no call group, leaves the status as it reads and sends no alert; a later real tick, or another issue's launch, reaps it.
A gone owner's run whose call still lives counts held under a dry run, since only a real call kills that call.

## Notify

`notify` hands each alert to `bin/alert`, which appends one line to the host's event log and posts the line to the project's Slack webhook; when the post fails, `notify` comments on the ticket instead.
A failure of both writes `notify.failed` in the run dir; `status` shows it.
Events: run started, `pr-opened` with the URL, every other exit, checks failing after round k every two rounds, and a call answered by a model nobody configured.
Each message names the ticket as `issue <n> (<title>)` and says the exit in words (`exit_words`), never a bare status.
`pr-opened` on another target, `ticket-defect`, `abandon`, an off-model call and `next` parking a ticket after three `stopped-environment` stops (Status and the manager) are `needs-you` (a Loam `pr-opened` is `info`: the overnight driver reviews, fixes and merges it, and alerts on one it leaves open) and `stopped-cap`, `stuck`, `no-change` and `stopped-environment` are `fail`; both post with `@channel`, and the rest post quietly as `info`.
The text passes `scrub` before Slack, the log and the comment; `scrub` also removes Slack webhook and healthchecks ping URLs and every value of 8 or more characters in the alert config files.
The checks-failing and `stuck` messages name the failing checks, never a FAIL line or its reason, as the PR body's checks blocks do; a name outside `[A-Za-z0-9_.-]` shows as `?`, and the checks-failing message names at most ten plus the `round-<k>.checks` file.

Config lives in `~/.config/loam/alerts/`, one secret per file, mode 600: `slack-<project>` (the project is the target repo's name in lower case) with `slack` as the shared fallback, `hc-ping-url` (this host's healthchecks.io check, `https://hc-ping.com/<uuid>`), and `hc-api-key`.
`status` reports which of them are present.
On jhaveris, `slack-distbench` may be a link to `~/.distbench/slack-webhook`, the file DistBench's own scripts read.

healthchecks: one check per host.
Set the check once in the healthchecks UI: period 5 minutes, grace 10 minutes, the Slack integration on (or a red check reaches no one), and manual resume off (or a beat cannot resume a paused check).
A run beats the check at launch, right after the frozen re-exec and before round 0, and every 5 minutes while its process lives.
At its end it stops beating (waiting for a beat in flight), and the host's last live run pauses the check through the API, so a run that ends on purpose raises no alarm and the next run's beat resumes it.
After the pause it looks for live runs once more and beats again if one launched meanwhile, since a run writes `launched` before its first beat; a run counts as live while it holds its slot, which it does from before its first beat.
A killed run, or a dead host, stops the beats without a pause, so the check goes red and healthchecks posts to Slack.
A hard-killed run keeps its slot (above), so no later run pauses the check while its directory stands.

### The event log and watch sessions

The log is `~/.local/state/loam/alerts.jsonl` on each host, one JSON object per line, appended after the Slack post: `t` (UTC), `host`, `project`, `source`, `run`, `level`, `slack` (`sent`, or `failed: <why>`), `text`.
Every caller of `bin/alert` writes here, the factory (through the run's frozen copy) and later stall-watch, limit-alarm and supervisor sessions, so a watch session reads one file per host.

A watch session reads it two ways.
1. A Monitor on `tail -n0 -F ~/.local/state/loam/alerts.jsonl`, for jhaveris through `ssh jhaveris tail -n0 -F '$HOME/.local/state/loam/alerts.jsonl'`; re-arm it every 30 minutes.
2. A line-cursor check on each watch tick, which shows every line after the last one it showed, because a Monitor can die without a sound.

Each line goes to Samyak in plain words in that tick, and a line whose `slack` is not `sent` goes as a line he has not seen.
The watch may make only these moves on its own, and reports each one with the line that caused it (owner ruling 2026-10-27):
- re-arm a dead Monitor or rerun its own check;
- stop a factory run that the log shows looping or spending with no progress: `bin/factory [-C <repo>] stop <issue>`, which halts the run before its next call;
- pause the host's healthchecks check with `bin/alert --ping pause`, after it has checked that no factory process runs there and `bin/factory status` shows no live run.
Everything else is Samyak's: merging or pushing, launching, relaunching or rerunning a ticket, editing a ticket, deleting a run directory or worktree, starting paid compute, and any change to results.

The overnight driver, which reviews, fixes and merges Loam's factory PRs on jhaveris, lives in `bin/overnight/`: `driver.sh` starts one headless call per PR with `settings.json` and `protocol.md` from that directory, and `watchdog.sh`, run by cron, restarts a dead driver.
Its run state (`log.md`, `followups.md`, `driver.log`, the `pr-*` files, `STOP`) stays in `~/.local/state/loam/overnight/`, outside the checkout `next` must find clean before it pulls; each call's lessons go into `docs/factory/LESSONS.md` on the PR's branch.
A call's settings deny it any write to `~/loam/bin/overnight/` (Edit, Write and the sandbox), so the driver changes only through a reviewed PR: a `driver.sh` change takes effect when the driver restarts, a `protocol.md` change at the next call after `next` pulls it.
Each call runs in a session of its own under a child-subreaper wrapper, which ends the call's tool children too, with `pid before out` in the state directory's `call.pid`: a stopped driver, or one whose terminal closed, leaves its call to finish, and the next driver adopts it, ending it 120 s after its outcome line as its own, before it starts a call of its own; to end a call on purpose, touch `STOP`, then `pkill -TERM -s <pid>`.

## Status and the manager

`bin/factory status` renders, per run: status, rounds, spend, wall time, first failing grader, permission denials per round (from the worker stream-json), `notify.failed`, and a worktree and PR readiness table.
It also shows a `clean` column (D09 Option A): `yes` when the run reached `pr-opened` with zero grader-fail rounds and no other exit on the way, `no` when it reached `pr-opened` some other way (an earlier exit, or a round that queued fixes), and `-` for a run not yet at `pr-opened`.
It also prints one `WARN <ticket>/<sha8> served by <models>` line under the table for each run whose ledger names, in a line's `served_models` (the sorted `modelUsage` keys of the call's result, `[]` for a Codex round or an unreadable result), a model that starts with none of `WORKER_MODEL`, `GRADER_MODEL`, the worker's advisor and that line's own requested `model`, so a `[1m]` or dated suffix still counts as the configured model and a run launched with a model override does not warn; the warning stops nothing.
Each line is matched on its own, and a malformed line is skipped.
Set the model variables as full ids: an alias such as `fable` never prefix-matches `claude-fable-5-1`, so it warns.
The advisor is not in the ledger, so a run launched with a different advisor than the shell running `status` warns.
It also checks the preconditions below.
The manager is a Fable session that runs `status`, merges, and writes one learn line when the same first-failing grader appears in two consecutive runs.
It merges only through `bin/factory merge <pr> <sha>`, with `<sha>` the head commit it read `check: PASSED` on, so the command holds the merge grant's head-commit condition in code and requires every check reported at that head to have passed; it does not know which checks are expected, so a workflow not yet reported is not waited for; the reviews the grant asks for stay with the manager.
After F9, `bin/factory next` on a ten-minute runner timer launches the next frontier ticket after each merge; removing the `ready-for-agent` label parks a ticket, and `FACTORY_STOP` at the runs root pauses the timer; a logged-out runner makes `next` print `login expired` on stderr and exit 1 without launching.
A ticket is parked only by a run of its current body, so editing the body relaunches it on the next tick.
A run at `stopped` relaunches on the next tick, and one at `stopped-daily` on the first tick after the UTC date of its `status` file; until then `next` prints `waiting #N: daily budget spent; relaunches after 00:00 UTC` on stderr and launches nothing for it.
A run at `stopped-environment` relaunches on the first tick an hour (`ENV_BACKOFF_SEC`) after the mtime of its `status` file, since that exit pages at once and a lasting machine fault relaunched every tick would page every ten minutes; until then `next` prints `waiting #N: last run stopped on the environment; relaunches 3600s after its stop` on stderr and launches nothing for it.
A worker call with no result event stops `stopped-environment` before its `round-N.checks` is written, and a relaunch reruns that round, so `MAX_ROUNDS` never trips (#547).
So each launch, under `owner.lock` together with its first status write and in the live checkout (a run frozen earlier counts too), writes `env-stops` in the run dir: the highest N of its `round-N.checks`, the `stopped-environment` stops since that N last moved, and a launch number.
A new round or a `pr-opened` clears the count; any other status, such as a `stopped-daily` or `stopped` that made no worker call, keeps it; a run `holds_slot` reaped counts as a stop.
While the run reads `stopped-environment` for the third such stop (`ENV_PARK_STOPS`), `next` prints `parked #N: stopped on the environment 3 times in a row with no new round since; fix the cause, then relaunch it by hand or edit the body` on stderr every tick and launches nothing for it.
Outside `--dry-run` or `--frontier` it reads `env-stops` and the park together under `owner.lock`, releases it, and sends one `needs-you` alert per stop, only when that line differs from `env-parked`, and then writes to `env-parked` the line it read before the alert, so a launch that rewrites `env-stops` meanwhile keeps its own alert.
Alerts are serialized by `next.lock`, which the runner's cron line and `bin/overnight/driver.sh` take with `flock -n` around `next`; a `next` run by hand outside it can at worst send one duplicate alert, an accepted risk.
Every other exit except `pr-opened` parks the ticket.
While the run dir of the issue's current body holds `FACTORY_STOP` (`bin/factory stop`), `next` skips the issue without a line whatever its status, so no `parked` or `lint failed` line prints for it either, since `run` would exit `stopped` at once and the issue would take the pick from every later candidate each tick; removing the file makes it eligible again.
A run that would relaunch also waits while a process of it still runs, since `run` refuses a relaunch then, exiting 4 with no status written: the model call its `call` file names (a stuck call outlives the `stopped-environment` exit), or, where flock(1) is present, any process holding its `lease`; `next` prints `waiting #N: a process of its last run still runs; kill it or wait for it to exit` on stderr and tries the next candidate.
A launch assigns the issue to the runner and no exit unassigns it, so `next` also reads the runner's own `ready-for-agent` issues in the repository (`gh api /issues?filter=assigned --paginate`, every page, since the query spans all the runner's repositories) and takes one only when its current body has no run but an earlier body has one, since an edited body is a new ticket (an issue with no run at all was assigned by hand, to hold it), or its run is `stopped-daily`, `stopped-environment` or `stopped`, under the waits above; it skips every other one without a line.
Every body of an issue shares its branch and worktree, so while a run of another body holds a slot, still runs a process, or is `pr-opened` with a PR that has no `pr-closed` marker (whatever its worktree), `next` prints `waiting #N: a run of another body still runs or awaits merge; it shares the issue's worktree` on stderr and tries the next candidate, and `run` refuses a launch the same way, exiting 4 with no status written.
The daily ledger is the runner's across targets, so while any run under the runs base reads `stopped-daily` with a `status` file dated today (UTC), and that ledger has no room for one more `ROUND_BUDGET_USD` under `DAILY_BUDGET_USD` at the runner's own caps (the defaults and any `FACTORY_<NAME>` override, not a ticket's Worker section, which may have stopped that run lower), `next` launches nothing and prints `waiting: a run stopped at today's daily budget; nothing launches before 00:00 UTC` on stderr.
Each tick that is not a `--dry-run` or `--frontier`, is not paused and passes the login, version and target gates reads, before the slot count, for each `pr-opened` run with no `pr-closed` file, its PR's state through `gh api`; once the PR is closed it appends the operator's events on the PR to the run's `owner-events.jsonl` as `phase` `pr` and writes `pr-closed`, and a `gh` failure leaves the run for the next tick.
Before it lints a candidate, `next` checks its owner (#389): the worker runs the body unattended and the repository is public, so an issue whose author (`user.login` in the frontier query), or whose last editor (one `gh api graphql` call for `repository.issue.editor.login`, null for a body never edited), is not `SamyakJhaveri` is passed over with one stderr line (`not owner #N: written or last edited by <login>; edit the body as SamyakJhaveri or remove ready-for-agent`), and so is one whose editor call fails, or whose editor is null with a `lastEditedAt` (an account GitHub no longer names); the next candidate is tried.
Once a candidate is picked, later ones skip the editor call, so a stalled GraphQL costs one tick one timeout; `--frontier` picks none, so every candidate gets the call, one timeout each.
`run` makes the same check again on the body it freezes, which it reads with its author, editor and `lastEditedAt` in one `gh api graphql` call, so an edit by another account after `next`'s check, or between the run's first pass and its frozen one, is refused there (exit 4, or `stopped-environment` once the run is recorded) and never runs.
Before it picks a ticket, `next` runs the `lint` rules on each candidate's body; a candidate that fails is skipped with one stderr line (`lint failed #N: <first error>; edit the body or remove ready-for-agent`) and the next candidate is tried, so a labelled issue with no done-checks block never launches (#314).

## Stop

`bin/factory stop <issue>` writes `FACTORY_STOP`; the run halts before its next call.
There is no other steering channel: to change course, edit the issue body and relaunch; the new body hash starts a new run.

## Grader change protocol

Grader prompts are production prompts.
`evals/<grader>/<case>/` holds a frozen `prompt.md` from a real round and an `expected.json` with the verdict and, when listed, the failing-row set; the first cases come from the runner's lean-v3 runs: the S2 stale-tree round, the S3 ownership round, the S4 unmeetable check, and S2 round 8.
`bin/factory eval <grader>` replays each case through the grader call above, compares the verdict exactly and the failing-row set only when the case lists one, and exits 1 on any mismatch.
A reviewer reply's verdict is what the loop does with it, `fix` when a finding is high or medium and `merge` otherwise, never its own verdict word; `eval_score.py` scores the reviewer the same way.
`evals/clean/` holds the last round of each runner run that both graders passed, frozen by `bin/factory eval-freeze` from `~/.local/state/loam-factory/runs/*/*/`, and `bin/factory eval <grader> --evals-dir evals/clean` replays the corpus.
A frozen label is the in-run graders' own verdict, never a person's, so a replay finding on a frozen case is checked against the diff and main's history before it counts as a false alarm; a base whose finding held carries it in its `expected.json` as defect class `real`, with `known_defects` and the fixing commit, and the rest carry a `checked` line (`evals/planted/CASES.md`, Replay check).
`mutate.py` plants defects only into bases whose label is still clean, so a grader that reports a base's own defect is never credited with the planted one.
`evals/clean` as of 2026-11-01 is a development set: its labels were adjudicated and the 2026-11-01 grader edits drafted on it, so a grader PR reports it apart from held-out cases, and a held-out set under evals/holdout, which the first such freeze creates, takes the next ten rounds eval-freeze accepts (`bin/factory eval-freeze --evals-dir evals/holdout <run-dir>...`), which no grader edit is drafted or relabeled on before the PR that first reports them merges.
A grader model comparison scores saved replies on a set with known defects, `evals/planted/` or a corpus `mutate.py` plants them into, with one script:

```sh
python3 bin/factory.d/mutate.py evals/clean <scratch>/cases   # only for the mutated corpus
MODEL_EVAL_SET=<scratch>/cases MODEL_EVAL_OUT=<scratch> EVAL_BUDGET_USD=<usd> bin/factory.d/model-eval <model>...
```

`mutate.py` writes a `--clean` copy of every base and one copy per defect class that applies (`skip`, `false-claim`, `logic-bug`, `stale-ref`, `vacuous-check`, `half-goal`, `out-of-scope`), labeled in its `expected.json`; reviewer bases also feed `lean-critic/`.
Every class is one the supervisor lets through, so only a grader can catch it; `evals/planted/CASES.md` lists them and the hand-written cases beside it.
The mutants are generated into the scratch directory at eval time and never committed.
`model-eval` runs one cell per grader (`MODEL_EVAL_GRADERS`, default `judge reviewer lean-critic`), model, effort (`MODEL_EVAL_EFFORTS`, default `high`; `max` is refused) and repeat (`MODEL_EVAL_REPEATS`, default 2), into `<scratch>/replies/<model>@<effort>/r<k>/`.
A `codex:<model>` model grades each case through `codex exec -s read-only --skip-git-repo-check`, run in the case's tree (below) under the factory's `CODEX_HOME` with no trust entry, instead of `bin/factory eval`, a second model family against same-family grading bias; `codex exec --output-schema` accepts only a strict schema, so `model-eval` closes every object, requires every property and makes an optional one nullable, and drops the judge's free-form `evidence`, which no score reads.
The cells run in a shuffled order, `random.Random(MODEL_EVAL_SEED)`, written to `<scratch>/order.txt`, so a config that drifts mid-run lands on every model alike.
A scored reply has a `.key` beside it, the sha256 of the grader file, its schema and rubric, `role-settings.json`, `bin/factory` and `bin/factory.d/model-eval` as they are on disk (so an edit to either between runs, committed or not, regrades every case: do not pull mid-grid expecting reuse), the case, the model, the effort, the mode and the cell's harness (the Claude Code version, the `config-drift.sh` md5, the Codex model, and the raw `~/.claude/settings.json` and `~/.codex/config.toml`, since `config-drift.sh` names settings without their values); a Codex cell hashes the factory home's `config.toml` in place of `~/.codex/config.toml`, and its mode names how it runs, so a reply cached before #566 changed that is graded again; an error, unparseable or off-model reply has none and is retried.
A rerun calls the grader only for a case whose reply or key is missing or whose key differs, so it fills gaps and never mixes an old reply into a changed experiment.
A Claude Code update or a config change between runs therefore invalidates every reply, and a gap-fill after one re-grades the whole grid.
Each cell's `fingerprint-<grader>.txt` names the config that grader's replies ran on: model, effort, grader and eval set hashes, the `config-drift.sh` md5, the Claude Code version and the Codex model; `fingerprint.txt` holds the same fields for the cell's whole grader list.
Right after each Claude cell's calls, every new reply's `modelUsage` must name only the cell's model; a reply served by another model stops the script at once with exit 3, no further call and no table.
`EVAL_BUDGET_USD` (default 10) bounds each cell's `bin/factory eval` call and must cover its cases: a case the eval never reaches has no reply, and the next run retries it.
`eval_score.py` prints one TSV row per grader, model, and metric: recall per defect class, false alarms on clean copies (`cut_rate` for the lean-critic, whose job is cuts), run-to-run agreement, cost, `infra` (missing, unparseable or `is_error` replies), and `n:` trial counts; a repeat model-eval ran but saved no reply for a grader in (every call failed, or none was made) still counts, each case a missing reply.
Each pair of models also gets an `A+B` row, the recall and false alarms of a two-model jury, scored from the same replies with no extra call, and an `A~B` row set: per metric the paired counts of cases only A caught, only B caught, both and neither, and `moved`, the fingerprint fields that differ between the pair; a pair whose cells differ in more than one field is marked `descriptive:`, since its difference cannot be put on any one of them.
`model-eval` prints that table with a Wilson 95% interval per rate, over cases, never trials, and a `not comparable:` line for each cell whose infra count is over 20% of its cases.
Each grader call in an eval runs outside the checkout in a fresh export with `evals/` removed, and the evals directory too when it lies inside the checkout, so no case's `expected.json`, which holds its verdict and planted class, is in the tree the grader reads; the export is removed when the eval ends.
The export is the tree the round was graded in, rebuilt by `case_tree` in `bin/factory`: the case's `tree_base` in `expected.json` (eval-freeze records the merge base of the run's base and graded commits, which the three-dot Diff starts from), else the commit its `## Diff (<base>...HEAD)` heading names, with every Diff file applied; a Diff file that does not apply fails the case (`TREE ... not graded`, a mismatch) instead of grading a half-built tree, and the checkout's `HEAD` export serves only a case whose base the checkout lacks (the run-only and lean-v3 cases).
`model-eval`'s Codex cells grade in the same per-case tree, in a directory that holds no case file, and each reuse key names the tree's commit.
This fences the working directory, not the grader's permissions: a Read, Grep or Glob of an absolute path into the checkout still reaches the keys, and user memory names the checkout's path.
A case may not depend on the live tree: its expected verdict must follow from `prompt.md` alone, since the grader reads the tree it runs in and a case whose verdict rests on that tree drifts as the repo changes (the lean-critic s4-round-4 case did, and was dropped 2026-09-11; two reviewer cases drifted on `HEAD` in 2026-11, so every case with a base commit grades in its base tree since).
No grader edit lands without the replay run before and after, recorded in the PR body; it never runs in `bin/check`.
The replay is local: `bin/factory eval` runs `claude -p` on the machine that calls it, so it needs no runner.
After a model upgrade: replay with the new model, then once more with each rubric body replaced by its one-line stance; a rubric row that changes no verdict is a deletion candidate.
Each new grader agent costs about 200 always-on tokens in every session of every seeded project; `bin/skill_listing_weight.py` gates each plugin bump.

## Run the factory on another repository

F8 step 1 keeps the factory's code, graders, and prompts in this checkout and adds `-C <repo>`, which points `lint`, `run`, `status`, `stop`, and `next` at another repository, such as a project Loam seeded.
Without `-C` the target is this checkout, and a Loam run behaves as before.

The target supplies the tree lint reads, the issues and PRs (`gh -R` its origin), the worktrees (siblings of its main checkout, `<checkout>-<issue>`), and the `bin/check` a done-checks block guards.
Its run dirs sit under `<runs root>/<owner>__<repo>/`, and so do its `FACTORY_STOP`, `nav-order`, `MAX_PARALLEL` count, and tmux logs: the runs root's own `FACTORY_STOP` pauses Loam only, and one target's runs do not count against another's `MAX_PARALLEL`.
The daily ledger stays at `<runs root>/ledger-daily.jsonl`, so `DAILY_BUDGET_USD` bounds every target's spend together.
The toolchain exports gate Loam only.
Another target's gate is an executable `bin/check` and a standing do-not-touch list with at least one entry: `run` and `next` refuse the target without either, and `status` prints FAIL.
That list is the `- ` lines under a `## Standing do-not-touch list` heading in the target's `docs/factory/STANDING.md`, in the format of Loam's own list in `ARCHITECTURE.md`; other lines and other sections are not read.
A token on a `- ` line is an entry when its first path segment is tracked in the target (a bare word that names a tracked top-level entry counts too); anything else on the line is dropped, and a changed path equal to or under an entry fails the round as `do-not-touch`.
The list cannot say append-only or add-only: a ticket that must append to a listed file or add a file under a listed directory names that path on its `Except:` line.

A target needs a GitHub `origin` whose default branch is `main` (runs branch from `origin/main`, and PRs target `main`), an executable `bin/check`, `docs/factory/STANDING.md` committed on `main`, the `ready-for-agent` and `needs-triage` labels, a clone on the runner beside Loam's, and whatever its `bin/check` needs there.
Setup, once per project `<owner>/<project>`: commit its `docs/factory/STANDING.md` to `main`, shaped like this, then run the commands below from the Mac.

```markdown
## Standing do-not-touch list

- `bin/check`
- `.claude/` and `.codex/`
```

```sh
bin/runner 'gh label create ready-for-agent -R <owner>/<project>'
bin/runner 'gh label create needs-triage -R <owner>/<project>'
bin/runner 'gh repo clone <owner>/<project> ~/Desktop/<project>'
bin/runner 'bin/factory -C ~/Desktop/<project> status'
```

Then per ticket, or once for the ten-minute timer:

```sh
bin/runner 'bin/factory -C ~/Desktop/<project> lint 12'
bin/runner 'tmux new -d -s <owner>__<project>-12 "bin/factory -C ~/Desktop/<project> run 12"'
bin/runner 'bin/factory -C ~/Desktop/<project> stop 12'
bin/runner 'bin/factory -C ~/Desktop/<project> next --install'
bin/runner 'touch ~/.local/state/loam-factory/runs/<owner>__<project>/FACTORY_STOP'
```

`next --install` adds one cron line per target beside Loam's, `cd ~/Desktop/loam && bin/factory -C <dir> next`; a reinstall replaces only that target's line.
After a merge, remove the ticket worktree (`git -C ~/Desktop/<project> worktree remove ~/Desktop/<project>-12`) so `next` frees the slot, as for Loam.
A project may carry a `bin/factory` that forwards to Loam's with itself as the target; it is not in `seed/` yet:

```sh
#!/usr/bin/env bash
exec "${LOAM_HOME:-$HOME/Desktop/loam}/bin/factory" -C "$(git rev-parse --show-toplevel)" "$@"
```

## Preconditions

- The runner is Ubuntu with `claude`, `codex`, `gh` (logged in), `uv`, `git`, `jq`, `python3`, coreutils `timeout`, `tmux`, `socat` and `bwrap` (bubblewrap, which the worker's Bash sandbox needs on Linux; `bin/factory status` prints a FAIL line without it) on a login-shell PATH; ssh commands use `bash -lc`.
- `claude --version` on the runner reports 2.1.257 or later, the first release with `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`: `bin/factory status` prints `PASS claude version` or a FAIL line naming what it read, and `bin/factory run` and `bin/factory next` refuse to launch on an older or unreadable version (#379).
- `claude auth status` reports `loggedIn: true` on the runner; `claude` on PATH is not `claude` logged in, so a logged-out Claude fails every worker call while `status` still shows it on PATH, and `bin/factory status` prints `FAIL claude login` (#78). `bin/factory next` refuses to launch on the same probe: a logged-out runner makes it print `login expired` on stderr and exit 1 before it queries the frontier.
- When the target is Loam, `LOAM_FACTORY_TOOLCHAIN` (a Node distribution with `bin/node`) and `LOAM_FACTORY_COPIER` (an executable `copier`) are exported in `~/.profile` on the runner: `bin/factory run` and `bin/factory next` refuse to launch and `bin/factory status` prints a PASS or FAIL line per variable.
- A target named by `-C` has a GitHub `origin`, an executable `bin/check`, and at least one entry in its `docs/factory/STANDING.md`: `-C` exits 2 on a checkout without the first, `run` and `next` refuse to launch without the other two, and `status` prints a PASS or FAIL line for each.
- `bin/claude-account status` names an active account and at least one other stored account on the runner when the usage-limit switch is wanted; with a single stored account the loop sleeps through a usage limit as before.
- Outside the factory, `bin/limit-alarm` (installed on jhaveris by `bin/limit-alarm-install`, which the owner runs) keeps a long-running lead session on an account with usage and stops the paid rental when every account is limited for more than two hours.
- `gh api rate_limit` succeeds on the seat that runs stages 0, 1, 2, and 5 (F0 fixes the Mac).
- `CODEX_HOME=~/.local/state/loam-factory/codex-home codex login status` succeeds when any ticket uses Codex; log that home in once with `mkdir -p -m 700 ~/.local/state/loam-factory/codex-home && CODEX_HOME=~/.local/state/loam-factory/codex-home codex login --device-auth`.
- Every `codex` call on the runner exports `PATH=$HOME/.local/bin:$PATH` and ends in `< /dev/null`, or Codex is not found or eats the caller's stdin (#41).
- Neither `DISABLE_TELEMETRY` nor `CLAUDE_CODE_DISABLE_ADVISOR_TOOL` is set in the runner's environment: either turns the worker's advisor silently off, and `bin/factory run` refuses to launch when one is set (F11). `FACTORY_STATUS_PROBE=1 bin/factory status` makes one paid Opus call to prove the advisor attaches.
- Sessions that edit `bin/factory` run in `acceptEdits`, not auto mode, because the auto-mode classifier blocks tool calls whose text names a permission mode (observed, not documented).
- `gh pr edit` has failed on a GraphQL deprecation; PR bodies are updated through the REST API.
- macOS lacks coreutils `timeout`; the supervisor runs only on the runner.

From the Mac sandbox, re-checked on 2026-09-09 (#34):

- Native `gh` fails on two faults: the Mac keyring token is invalid, and the sandbox blocks Go's call into the macOS Security framework (`x509: OSStatus -26276`), which no CA file fixes because the proxy does not intercept TLS.
- `gh` works through the runner: `bin/runner 'gh api rate_limit'` succeeds, stdin passes through, so `bin/runner 'gh issue comment N --body-file -' < file` is the GitHub write path from a sandboxed session.
- `bin/runner`, `ssh`, `scp`, and `rsync` to the runner are excluded from the sandbox by the global settings and work.
- `raw.githubusercontent.com` returns 200; `git ls-remote`, `git fetch`, `git push`, and unauthenticated `curl https://api.github.com` work.
- `reddit.com` returns 403; `youtube.com` returns 200.
