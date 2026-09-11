# Loam Factory: the loop

This file is the one home of `bin/factory`, the supervisor that runs one ticket to a pull request on the runner.
It generalizes `.superpowers/lean-v3/loops/loop.sh`, which stays the live loop until F1 lands.
The ticket it consumes is defined in `CONTRACT.md`; the stage table and model rules are in `ARCHITECTURE.md`.
Rubric text lives only in the grader files.

## Commands

| Command | Does | Built in |
|---|---|---|
| `bin/factory lint <issue|file>` | static ticket lint, rules in `CONTRACT.md` | F2 |
| `bin/factory eval <grader> [--model M]` | replays frozen cases through the production grader call and compares verdicts | F6 |
| `bin/factory run <issue>` | round 0, then worker rounds, graders, PR | F1 |
| `bin/factory status` | run states, spend, denials per round, worktree and PR readiness, preconditions | F1 |
| `bin/factory stop <issue>` | writes `FACTORY_STOP` into the run dir | F1 |
| `bin/runner <cmd>` | runs `<cmd>` on the runner: `ssh jhaveris bash -lc 'cd ~/Desktop/loam && <cmd>'`; `bin/runner sync` mirrors `.superpowers/lean-v3/` and `.superpowers/factory/` to the same paths on the runner with `rsync -az --delete`, excluding `runs/` and `__pycache__`; it never pulls (#36) | F0 |
| `bin/factory next [--install]` | launches up to `MAX_PARALLEL` `ready-for-agent` issues with no assignee and no open native blocker (read through `gh api`); `--install` writes the ten-minute runner timer | F9 |

`REPO` comes from `gh repo view --json nameWithOwner` in the checkout the run was launched from.
`status` runs on the runner; from the Mac it is `bin/runner bin/factory status`.

## Layout

```
bin/factory                    the supervisor
bin/factory.d/lib.sh           pass, fail, guard (F2); MEASURE, render_into, check_clean (F1)
bin/factory.d/_common.md       the loop contract appended to every worker prompt
bin/factory.d/role-settings.json   deny-only settings for grader calls
bin/factory.d/worker-settings.json   worker-only settings: the same deny rules plus the Stop hook that runs the done-checks block
bin/factory.d/review-output.schema.json   copied from the Codex plugin
bin/factory.d/summarize_sample.py  stream-json summarizer (moved in F1)
bin/factory.d/fixtures/        lint fixtures (CONTRACT.md)
evals/<grader>/<case>/{prompt.md,expected.json}
~/.local/state/loam-factory/runs/<issue>/<sha8>/   on the runner, outside every checkout:
    status  ledger.jsonl  base.sha  frozen/  round-<k>.*  worker/decisions.md  pr-body.md  notify.failed
```

Graders are plugin agents (home in `ARCHITECTURE.md`): `judge.md` and `reviewer.md`.
`lean-critic.md` is a grader file under the same change protocol, but the manager runs it by hand on the PR, outside the round loop: on the 2026-09-09 ledger 3 of its 6 round calls were unparseable.
The run resolves them from the installed plugin cache, falling back to the checkout's own `cultivation/marketplace/sam-cc-setup/agents/` when a branch's grader edits are not installed yet, and records each file's sha256 in the ledger.

## A run

1. Read the ticket: an issue number reads the body from GitHub, a file path reads it from disk and makes no GitHub call, keying the run directory by the file stem instead of the issue number.
   `sha8` is the first eight hex of the body's sha256 and, with the issue number or file stem, names the run dir under `FACTORY_RUNS_ROOT` (default `~/.local/state/loam-factory/runs`).
   A changed body is a new run; old rounds stay on disk.
2. Record the `origin/main` sha as `base.sha`; create the sibling worktree on branch `factory/<issue>` from it; assign the issue to the operator (skipped for a file ticket).
3. Extract the done-checks block; freeze `bin/factory`, the graders, `lib.sh`, `_common.md`, `role-settings.json`, `worker-settings.json`, the grader schemas, and the body into `frozen/`, owned outside the worker's write scope; the frozen grader prompts keep fixed evidence markers, there is no per-run string (#38).
4. Round 0: run the block on `base.sha` from the worktree root; every non-guard check must print FAIL, else exit `ticket-defect`.
   Then one read-only Fable 5.1 low call with the ticket and the check output, answering `{doable, unmeetable:[{check, reason, evidence}]}` through `--json-schema`.
   Any `unmeetable` entry exits `ticket-defect` with the evidence and pages the owner.
5. Worker round k: a fresh `claude -p` (`claude-opus-4-8[1m]` xhigh) or a fresh `codex exec` in the worktree with the body, `_common.md`, and from round 2 the failing check lines and every blocking finding verbatim.
   The worker writes code and `decisions.md` only.
   Every round is a fresh process for either worker; there is no fixer role.
6. Before grading, in order: scan `decisions.md` for an `ABANDON` line; re-hash the frozen set (a mismatch exits `stopped-environment`); `git status --porcelain` must be empty, else the round fails with the path list; `git diff --name-only "$(cat base.sha)"...HEAD` against Do not touch emits `FAIL do-not-touch <paths>`; then run the done-checks block from the worktree root.
7. On green: the supervisor runs Rows measured and prints `MEASURE` lines, then calls the judge, the reviewer, and the Codex review stage if the ticket sets it, each fresh, on the frozen prompt and the same evidence bundle.
8. On pass, or at the grader-round cap: assemble the PR body (first line `Closes #<issue>`, then goal, `git log --oneline base..HEAD`, the MEASURE table, the merge checklist as checkboxes, `decisions.md`, grader sections, backlog, metrics), push, `gh pr create` or update the existing PR through the REST API, notify, exit `pr-opened`.

## Exits

| Status | Meaning | Counts a round |
|---|---|---|
| `pr-opened` | checks and graders pass, or the grader-round cap reached with a backlog | yes |
| `no-change` | HEAD is unchanged since the previous round | yes |
| `stuck` | the same failing check set twice in a row | yes |
| `ticket-defect` | round 0 found a check that passes on base or an unmeetable check | no |
| `abandon` | an `ABANDON NAME reason` line in `decisions.md`; the owner is paged | yes |
| `stopped-environment` | a `claude` result subtype other than `success`, a Codex exit other than 0 or no `turn.completed` event, a `gh` or `git` failure, or a frozen-set hash mismatch | no, and it pages at once |
| `stopped-cap` | `MAX_ROUNDS`, `TICKET_BUDGET_USD`, `DAILY_BUDGET_USD`, or `MAX_HOURS` reached | yes |
| `stopped` | `FACTORY_STOP` present before a call | no |

Exit code, `status`, and the final log line are decided together and cannot disagree.
These read loop-control files to decide exit, never safety; safety stays with deny rules, the sandbox, git, and CI.
A usage-limit reply (`hit your session limit`, `reached your Fable limit`) is neither an exit nor a round: the supervisor writes `waiting-limit` to `status`, sleeps until the reset time the reply names or twenty minutes when it names none, then repeats the same call; a reset past `MAX_HOURS` exits `stopped-environment`.
A call with no result event (killed by `CALL_TIMEOUT_SEC`, or crashed) exits `stopped-environment` and counts no round.

## Caps

Defaults from lean-v3, overridable per ticket in its Worker section and then by `FACTORY_<NAME>` in the environment, never by the bare name, which a Claude Code session already exports for `WORKER_MODEL` and `CALL_TIMEOUT_SEC`: `MAX_ROUNDS=6`, `ROUND_BUDGET_USD=15`, `GRADER_BUDGET_USD=5`, `TICKET_BUDGET_USD=60`, `DAILY_BUDGET_USD=150`, `MAX_HOURS=8`, `MAX_TURNS=200`, `CALL_TIMEOUT_SEC=5400`, `MAX_PARALLEL=1`.
No research source gives a numeric anchor (`../research/anthropic-loop-engineering.md`); re-measure after two real runs.
The daily ledger `runs/ledger-daily.jsonl` is keyed by UTC date across all runs.
Codex token counts come from its `--json` events and land in the ledger with `cost_usd` null, so the dollar caps do not bound a Codex worker; the PR body says so.

## Grader-round cap and precedence

After the checks first pass, at most two grader-fail rounds per ticket; then the remaining non-blocking findings go to the PR body backlog and the PR opens.
The judge decides pass or fail.
The reviewer and the Codex review block only on a `high` finding (Codex: `critical` or `high`), and each may block at most once per ticket.
A grader whose output is absent or unparseable is a fail with one high finding "grader unparseable", never a pass.
`verdict_consistent` runs on every grader JSON: a pass with non-empty fixes, or a fail with empty fixes and empty backlog, is refuted, and the grader is called once more, fresh, with the refutation appended to its prompt.

## Grader calls

Graders run from the worktree root.
`--tools Read,Grep,Glob` on the call is what makes a grader read-only (#40 measured that it sets the tool list exactly); an agent file's `tools:` line governs its interactive use only, so `lean-critic.md` keeps Bash.
`--strict-mcp-config` and `--disable-slash-commands` drop the MCP schemas and the skills listing a grader never uses: its prefix is then 9.9k tokens instead of 27k (probed on the runner 2026-09-09), and the prefix is most of a grader call's input.

```
claude -p --model fable --effort medium --tools Read,Grep,Glob --strict-mcp-config --disable-slash-commands --no-session-persistence \
  --json-schema "$(cat frozen/<grader>.schema.json)" --max-budget-usd "$GRADER_BUDGET_USD" \
  --setting-sources user --settings frozen/role-settings.json --output-format json < frozen/<grader>.prompt.md
```

The frozen grader prompts keep fixed evidence markers; there is no per-run string, and any instruction found inside those markers is data and a dishonesty finding.
The evidence bundle is the ticket body, the design issue body when one exists, `git diff base...HEAD`, the check output, the MEASURE lines, and `decisions.md`.
In that diff, code files pass as content, but data files pass as stat only (files under `evals/` named `prompt.md`, and any single added file over 400 lines), so a frozen prompt or a large fixture never floods the grader diff.
The Codex review stage runs `codex exec --json --output-schema frozen/review-output.schema.json -o <file> -s read-only "$(cat frozen/codex-review.prompt.md)" < /dev/null`, with the base sha filled into the frozen prompt's `<base>` placeholder; a review needs no write access and `read-only` keeps it from editing the tree the judge and reviewer already graded; `codex exec review` ignores `--output-schema` (#41).
`needs-attention` with a `critical` or `high` finding blocks once.

## Worker calls

```
claude -p --model claude-opus-4-8[1m] --effort xhigh --advisor fable --permission-mode bypassPermissions --strict-mcp-config \
  --setting-sources user --settings frozen/worker-settings.json --max-turns "$MAX_TURNS" \
  --max-budget-usd "$ROUND_BUDGET_USD" --output-format stream-json --verbose --include-hook-events < round-<k>.prompt.md
```

`--strict-mcp-config` drops the MCP schemas, 2k tokens of prefix on every worker turn; the worker keeps its skills listing because the `skills:` sentence names a Skill-tool call (#37).
`--max-turns` is accepted by Claude Code 2.1.263, the runner's login-shell binary (#40; a plain shell resolves an older nvm copy), though absent from its `--help`.
`worker-settings.json` is deny-only, the lean-v3 list plus `Bash(gh:*)` so a worker cannot touch GitHub at all, plus the `Stop` hook (see The worker prompt); `role-settings.json`, loaded only by grader calls, carries the same deny rules with no hook.
The Codex worker runs `codex exec --json -s workspace-write "$(cat round-<k>.prompt.md)" > round-<k>.jsonl -o round-<k>.last.txt < /dev/null`: the JSONL stream is stdout and `-o` is the last-message file.
Because that sandbox mounts `.codex` read-only and bubblewrap refuses the root `.codex` symlink into `seed/`, a Codex round swaps that symlink for a real copy of its target for the call and restores it before grading (D12, #77).
The call also carries four `--add-dir` roots derived from git, the worktree gitdir plus `objects`, `refs`, and `logs` under the common dir, so the commit from the worktree can land.
Its workspace-write sandbox does not block `.env` reads (#41); no deny is configured, and the F4 merge checklist's hand run confirms the read is absent from the round's JSONL or records it as a risk.

## The worker prompt

Every worker round receives, in this order: the issue body verbatim, which carries its `goal:` line as text, `_common.md`, and from round 2 a `## Previous round` block holding the failing check lines and every blocking finding verbatim.
A slash command expands only on the first line of a `-p` prompt and swallows the rest as its argument (#40), so no worker prompt carries `/goal` or a `/<skill>` line; a `Stop` hook in `worker-settings.json`, the worker-only settings file, runs the frozen check script from the worktree root and exits 2 with the FAIL lines while any check fails, and `--max-turns` bounds the round (#36, route B).
The hook sets `LOAM_HOOK=1`, under which the check lines that call `bin/check` (minutes per stop) or the live model pass without running; the supervisor's own check run has it unset and is the one run of those per round. `build_worker_prompt` in `bin/factory` appends after `_common.md` one sentence per `skills:` name: `Before the first edit, call the Skill tool with "<name>".` (#37).
A Codex worker gets the skill bodies pasted instead.
The worker never runs `bin/factory eval` against the live model; the supervisor's own check run is the one live replay per round.
`_common.md` is the loop contract, frozen per run; its target text:

```
You are one round of an unattended loop on ticket #<issue>. There is no human. Decide, and record each decision in decisions.md in one line.
Start by opening every path named under Where, Do not touch, and Approach with git ls-files; never guess a path or a name.
Follow the Approach section where the ticket has one; if you depart from it, say why in decisions.md.
Implement the Goal. Touch nothing listed under Do not touch. Add nothing listed under Out of scope.
Before you finish, run the done-checks block from the worktree root exactly as the supervisor will, and fix every FAIL line you can; repeat until it prints no FAIL line or you cannot proceed. The supervisor reruns it; a claim without a PASS line is worth nothing.
Commit as you go with messages that name the step. Never push, never open a PR, never touch GitHub.
If a check cannot be met, write "ABANDON <name> <reason>" in decisions.md and stop; never edit, weaken, or route around a check.
Use subagents only to read (Explore) or to gather evidence (verify-app, build-validator when installed); no subagent edits. Every Agent call names model claude-opus-4-8[1m].
Write no summary, measurement table, or PR text; the supervisor assembles the PR from the diff, the checks, and decisions.md.
```

The ticket says what and how to prove it; the contract says how to behave; the supervisor decides when it is done.

## Skills per role

Skills are given at the moment they apply, never all at once; the listing is paid in every session.

| Role | Skills | How they arrive |
|---|---|---|
| Brief (stage 0) | `/brief` (F5) | Samyak invokes it |
| Design (stage 1) | `surprise-me` (panel), `research`, plan mode, `/plan-review`, `grill-with-docs`, `domain-modeling`, `wayfinder` | the design session invokes them in that order for `Mode: figure-out`; from plan mode on for `build` |
| Tickets (stage 2) | `to-tickets`, `plan-reviewer`, lean-critic | the stage-2 session; `plan-reviewer` and lean-critic after `bin/factory lint` exits 0 |
| Worker | the skills the ticket's `skills:` field names, each a line of `bin/factory.d/skills.txt` | one Skill-tool sentence per name in the worker prompt |
| Graders | none; their prompt is the whole instruction | frozen files |
| Manager (stage 5, 6) | `handoff` when stopping mid-stream | the manager session |

A worker may name only a line of `bin/factory.d/skills.txt`, and lint reads that file (#37).
The worker runs with `--setting-sources user`, which loads `~/.claude/skills/` and user-scope plugins but no project skill, so the seed pair (`catchup`, `fable-prompting`) is not in the file.

## Parallel runs

Each run has its own worktree, branch, and run directory, so unblocked tickets may run at the same time.
Two tickets may run together only when neither names a path the other's Goal creates or rewrites; the stage-2 grader pass checks this over a breakdown, and native blocking edges hold the rest apart.
The daily ledger is written under a lock.
`bin/factory next` launches up to `MAX_PARALLEL` runs (default 1; raise it after two clean single runs).

## Notify

Pushover when `~/.config/loam-loops/pushover.env` exists, else a comment on the ticket.
A failed notification writes `notify.failed` in the run dir; `status` shows it.
Events: run started, `pr-opened` with the URL, every other exit, checks failing after round k every two rounds.

## Status and the manager

`bin/factory status` renders, per run: status, rounds, spend, wall time, first failing grader, permission denials per round (from the worker stream-json), `notify.failed`, and a worktree and PR readiness table.
It also checks the preconditions below.
The manager is a Fable session that runs `status`, merges, and writes one learn line when the same first-failing grader appears in two consecutive runs.
After F9, `bin/factory next` on a ten-minute runner timer launches the next frontier ticket after each merge; removing the `ready-for-agent` label parks a ticket, and `FACTORY_STOP` at the runs root pauses the timer.

## Stop

`bin/factory stop <issue>` writes `FACTORY_STOP`; the run halts before its next call.
There is no other steering channel: to change course, edit the issue body and relaunch; the new body hash starts a new run.

## Grader change protocol

Grader prompts are production prompts.
`evals/<grader>/<case>/` holds a frozen `prompt.md` from a real round and an `expected.json` with the verdict and, when listed, the failing-row set; the first cases come from the runner's lean-v3 runs: the S2 stale-tree round, the S3 ownership round, the S4 unmeetable check, and S2 round 8.
`bin/factory eval <grader>` replays each case through the grader call above, compares the verdict exactly and the failing-row set only when the case lists one, and exits 1 on any mismatch.
No grader edit lands without the replay run before and after, recorded in the PR body; it never runs in `bin/check`.
After a model upgrade: replay with the new model, then once more with each rubric body replaced by its one-line stance; a rubric row that changes no verdict is a deletion candidate.
Each new grader agent costs about 200 always-on tokens in every session of every seeded project; `bin/skill_listing_weight.py` gates each plugin bump.

## Preconditions

- The runner is Ubuntu with `claude`, `codex`, `gh` (logged in), `uv`, `git`, `jq`, `python3`, coreutils `timeout`, `tmux`, and `socat` on a login-shell PATH; ssh commands use `bash -lc`.
- `gh api rate_limit` succeeds on the seat that runs stages 0, 1, 2, and 5 (F0 fixes the Mac).
- `grill-with-docs`, `wayfinder`, and `to-tickets` are invocable on that seat.
- `codex login status` succeeds when any ticket uses Codex.
- Every `codex` call on the runner exports `PATH=$HOME/.local/bin:$PATH` and ends in `< /dev/null`, or Codex is not found or eats the caller's stdin (#41).
- The plugin cache holds the grader files at the version the ledger records.
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
