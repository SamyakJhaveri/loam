# Design B: the factory proves the way we work from run evidence

L = Loam 5e7fc15f, D = distbench origin/isc-build 2d2a59f5 (the factory's base; it contains main 582df455).
Written under a stop order: sections marked "unfinished" were designed but not checked to the same depth.

Stages, all started by one timer tick: admit -> build -> prove (checks, gate, conduct) -> review (judge, sweep, Fable, Codex, Opus verify) -> land -> learn -> admit.
An instruction reaches the worker only as a read-only view generated at freeze from its one source, and counts only where the conduct stage reads its trace.

## (a) Sandbox
Mechanism: worker Bash runs unsandboxed for a target whose `docs/factory/STANDING.md` carries `sandbox: off` under a new `## Worker shell` heading; other targets keep `L/bin/factory.d/worker-settings.json:22-25`.
No sandbox setting can run the gate: its tests start nested bwrap, Docker, GPU and systemd scopes (runs-w24-w34-w35.md, W34 round 1 and W35 check.log:44).
Lost: Bash writes confined to the worktree and run roots (`L/docs/factory/LOOP.md:235`); the PyPI-only network (`LOOP.md:236`); namespace isolation from Docker, signals and other sessions.
Never protected, so not lost: credential reads other than `.env*`, the Write and Edit tools, and worker-written code in the Stop hook, `run_checks` and the sweep (`LOOP.md:240`).
Still guards: one worktree and branch per run; the deny list (prefix match only, `LOOP.md:234`), now built from the target's own list (`D/.claude/settings.json:7-28`) plus `git push`, `git tag`, `gh`; `--setting-sources ''` kept (`L/bin/factory:2350`), so the worker cannot change its own harness; worker env with `GIT_SSH_COMMAND=false` and an empty `GH_CONFIG_DIR`; the whole run in `distbench-build.slice` (`D/bin/build-slice:13`); the frozen hash held in the supervisor's memory, not the worker-writable `frozen/sha256` (`L/bin/factory:1485-1492`); conduct rows that fail any tool call naming `frozen/`, `gate/`, another checkout, `pkill`, `ssh` or `crontab`; and `bin/integrate --land`, which reruns the gate on the merged tree (`D/bin/integrate:28-37`).
Network: nothing technical guards it.
Gate in round: `guard bin/check` goes to a new `gate.sh`, which runs the gate once per committed tree in a detached snapshot worktree, caches exit code and log, and waits at most 540 s per call (the Bash tool killed 10-minute gates in all three runs).
The Stop hook, the worker and the supervisor share that cache, so the `LOAM_HOOK` skip (`L/bin/factory.d/lib.sh:24`) is deleted.
Files: L `bin/factory.d/gate.sh` (new), `lib.sh`, `view.sh` (new), `bin/factory`; D `docs/factory/STANDING.md`.
Observable: `gate/<tree>.log` with no `AF_UNIX bind denied` line and a last line `check: PASSED` or a named failure; `frozen/view/settings.json` `.sandbox.enabled == false`.

## (b) pstack with proof
Mechanism: a PreToolUse hook `router-first.sh` blocks the first Edit or Write of a round until the transcript holds a Skill call of `sam-cc-setup:pstack` or a full read of the router file.
The router file itself gains one line: log each chosen skill as `METHOD <name> <SKILL.md path>: <decision it changed>`.
Conduct fails `method-unread` when a METHOD path has no full read in the round's or its subagents' transcripts, and `router-first` when HEAD moved with no router call.
This is code ahead of the judge, so no rubric edit and no grader replay is owed (`LOOP.md:470`); the judge gets the conduct file as evidence.
Delete the copies: `_common.md:14`, the always-read adapter line (`L/bin/factory:2071-2074`), `factory-round.js:107`, empty `skills.txt`.
Files: L `bin/factory.d/hooks/router-first.sh` (new), `cultivation/marketplace/sam-cc-setup/skills/pstack/SKILL.md`, plugin version.
Observable: `round-N.jsonl` Skill tool_use before the first edit, hook events, `worker/decisions.md` METHOD lines, `round-N.conduct`.

## (c) Models and review
Workers: Opus 5.5 high; fan-out builders drop from xhigh to high (`L/bin/factory.d/factory-round.js:213,219`); conduct fails any `max`, Haiku or Sonnet in the ledger's `served_models`.
Review: the reviewer role keeps its rubric and schema but runs `claude-fable-5-2` at high through a new `FACTORY_REVIEWER_MODEL` (today Opus xhigh, `L/bin/factory:1075`), on a bundle without `decisions.md` so it is blind (`L/bin/factory:2480`).
Codex read-only runs whenever the diff names a code file, whatever the ticket says (today opt-in, `L/bin/factory:2967-2968`).
New `verify.sh`: one fresh Opus 5.5 high call in a detached worktree reads audit step 4 by path (`sam-cc-setup/skills/audit/SKILL.md:47-49`) and marks each blocking finding CONFIRMED, PARTLY or REJECTED with its reproduction; only confirmed lines enter `round-N.fixes` (today verbatim, `L/bin/factory:2600-2601`).
Audit and surprise-me run as skill calls (section g) at the points `D/docs/WORKERS.md:25-29,46` names: dry run at admit, audit at batch end, surprise-me when a failure class recurs.
Observable: ledger rows `reviewer claude-fable-5-2`, `round-N.verify.json`, `round-N.rejected`, a review prompt with no decisions block.

## (d) Behaviour proof
The view carries `D/AGENTS.md:18-19` and a skills index built from the base tree, so the worker reads `.agents/skills/verify-distbench/SKILL.md` in its own worktree; unsandboxed, it can now run `control-distbench` itself.
D adds `paths:` globs to the verify-distbench and formal-orchestrator frontmatter; conduct reads the same globs and fails a diff that matches with no read and no launch-to-cleanup command.
Six steps (implementation-plan.md:229): 1 is `round-0.checks`; 2 and 3 are done checks and the gate log; 4 is the lane's merge-log line; 5 and 6 are paid and the owner's, so conduct requires an `UNVERIFIED` line in `decisions.md` when the ticket's Proven line names them.
Observable: transcript reads and commands, `<run>/evidence/drives.jsonl`, `round-N.conduct`.

## (e) Scheduling
Mechanism: `tick.sh` on cron launches released file tickets from a queue folder, reusing `bin/factory run` and its relaunch rules (`LOOP.md:398-403`).
Admission per tick: live runs under `FACTORY_MAX_PARALLEL` (4 after W04, plan:193); heavy runs at most 3; and the target's `hold` hook, which refuses while a landing has waited two gate runs (plan:184).
Gate load: one gate per committed tree per run through the cache, base-tree results shared across runs; factory gates hold one of the two gate slots (`D/bin/check:139-158`) and the second only while `integrate.lock` is free.
Target hooks live in D `bin/factory-lane publish|hold|land`, replacing the untracked `~/.local/bin/factory-isc`; `land` runs `bin/integrate --land --group N` and one Codex read-only review per landing.
Observable: `tick.log` lines (`launch W34 runs=3/4 heavy=1/3 gates=1/1`), `run/cgroup`, integration rows, merge-log.

## (f) Unattended
Wake-up is code: the cron tick, not a lead session, so the `/loop` tick, the lead hand-off and night-watch are not needed for factory work.
450K: each round is a fresh process whose hand-off is commits and `decisions.md` (`LOOP.md:67-70`); `autoCompactWindow 450000` bounds one call (`worker-settings.json:3-4`); judgment calls are fresh per task.
Dead sessions: the lease reap and alert (`LOOP.md:322`), the healthchecks beat (`LOOP.md:355-357`), and a STALL alert when a running round's transcript is 30 minutes old.
NEEDS-SAMYAK.md is rendered each tick from unacknowledged `needs-you` lines of `alerts.jsonl` (`LOOP.md:365`), each with its `!` command: merges to main, spend over 10 USD, paid creates, ruling or frozen-contract changes, `ticket-defect`, `abandon`, parks, design-class self-tickets.
Observable: `tick.log`, `alerts.jsonl`, `NEEDS-SAMYAK.md`, `compact_boundary` events.

## (g) Self-improvement (partly unfinished)
`learn.py` reads run folders, not GitHub, so file tickets are covered (today they skip filing, `L/bin/factory:2866`): conduct FAIL rows, non-clean exits, confirmed findings left open, rejected findings, failed landings.
A class seen twice, or one confirmed High, starts one ticket-writer call that reads `D/docs/WORKERS.md:31-46` and `L/docs/factory/CONTRACT.md` by path and writes a draft against the repo the evidence blames.
`skill-call.sh` then runs the audit skill by path on the draft, as for any ticket: lint, round 0 on base, Fable and Codex blind, Opus verify, dry run; result in `reviews-tickets/<id>.md`.
A fix-class ticket with no High open is released to the queue; a design-class one waits in NEEDS-SAMYAK.md.
Loam tickets take the same file queue; Loam's publish hook opens a draft PR, and merges stay Samyak's.
Unfinished: the class-key definition and the Loam publish hook.

## (h) Measurement (unfinished)
`compare.py` prints one row per batch 2 item: arm, confirmed Medium-or-worse findings from the same downstream reviewers (landing Codex, batch-end audit, verified), reruns, cost (ledger or transcript usage), wall time, diff size.
Items were not assigned at random, so report medians with n and no winner; alternate arms in batch 3.

## Parity rows made observable
Run folder: D08-D14, D16, D17, D19, D23-D26, D28, D35, D41, D42, D47, D49, G02, G13-G16, G19, G21, G22, G26-G28, G33, G46.
Tick, queue and lane logs: D29-D32, J15-J22, J24.
Admit and batch folders: D18, D20, D22, D48, G30, G31, G55.
Loaded but not provable as followed (`frozen/view/MANIFEST.tsv` only): G01, G04, G07, G39, G47, G50.

## Build units
U1-U8 and X1-X3 touch disjoint files and run in parallel; U9 then U10 both edit `bin/factory`.

| Unit | Repo, files | Done check |
|---|---|---|
| U1 view | L `bin/factory.d/view.sh`, test | `view.sh ~/distbench origin/isc-build $T` lists CLAUDE.md, AGENTS.md and `~/.claude/CLAUDE.md` in `$T/MANIFEST.tsv` |
| U2 gate | L `gate.sh`, `lib.sh`, test | two calls on one tree: second prints `gate: cached`, the stub gate ran once |
| U3 router | L `hooks/router-first.sh`, router SKILL.md, plugin version | hook JSON without the call exits 2, with it exits 0 |
| U4 verify | L `verify.sh`, schema, test | fixture with one CONFIRMED and one REJECTED leaves 1 line in fixes, 1 in rejected |
| U5 tick | L `tick.sh`, `tick.crontab`, test | `tick.sh --dry-run` on 5 queued tickets at cap 4 prints 4 `launch` lines and 1 `hold` |
| U6 learn | L `learn.py`, `skill-call.sh`, test | two run folders with one shared FAIL class print one `draft` line; one folder prints none |
| U7 compare | L `compare.py` | on the W24, W34, W35 folders prints a factory row with n=3 |
| U8 host setup | L `bin/factory.d/host-setup.sh` (Samyak runs it) | `jq '.availableModels|index("claude-fable-5-2")' ~/.claude/settings.json` is not null; crontab holds the tick line |
| X1 standing | D `docs/factory/STANDING.md` | `grep -c '^sandbox: off' docs/factory/STANDING.md` prints 1 |
| X2 lane | D `bin/factory-lane`, test | on scratch repos `publish` adds one integration row; `hold` exits 1 while a row waits |
| X3 paths | D two SKILL.md frontmatters | `bin/check` skill-key step passes |
| U9 worker wiring | L `bin/factory`, `worker-settings.json`, `_common.md`, `factory-round.js`, delete `skills.txt` | a jhaveris run of one real ticket: no `AF_UNIX bind denied` in `gate/*.log`; parity PASS on router, method, gate |
| U10 review wiring | L `bin/factory`, LOOP.md, ARCHITECTURE.md, CONTRACT.md | same run: `round-N.verify.json` exists; ledger shows `claude-fable-5-2` |

## Not doing
A separate OS user for workers: the real boundary on a shared host, but it needs sudoers, Docker and GPU setup that are Samyak's and would take days.
Loading the user and project tiers natively: the worktree's settings and the shared memory folder would become worker-writable inputs (`LOOP.md:237,241`).
A long-lived lead session as scheduler: it needs a wake loop, a 450K hand-off and a watcher, all of which code removes.
Editing `judge.md`, or anything on redesign-1030.
Rewriting the overnight driver now: its panel (`L/bin/overnight/protocol.md:61-66`) becomes a copy of the review stage; delete it after one clean Loam run.

## Risks
Unverified, read from the binary and not run: `--append-system-prompt-file`, `--agents`, a Skill call of the router under `--setting-sources ''`, and `transcript_path` in subagent hooks; U3 and U9 probe them.
jhaveris `availableModels` lists `claude-fable-5-1` only, while `escalate.md:4` names `claude-fable-5-2`; until U8, Fable 5.2 calls may be refused.
A same-user worker can forge the gate cache; conduct detects only what the transcript shows, and the landing gate is the authority.
Moving the reviewer to Fable is a grader change; the replay (`LOOP.md:470`) is paid and may pass 10 USD, so it needs Samyak's yes.
The build block still says the lead launches each run and the worker shell is always sandboxed (implementation-plan.md:185-189); that text is on a fenced branch, and the 11 Nov ruling has no APPROVALS entry yet.
The real-target done check needs no live f-* session and a paid run.
Other finding, not fixed: `D/docs/tickets/SESSION-PROTOCOL.md:40` names a banned skill pack.
