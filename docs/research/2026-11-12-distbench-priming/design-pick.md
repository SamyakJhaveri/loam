# Design pick, buildable (12 Nov 2026): the factory builds distbench like an attended session

L = Loam `fix/factory-distbench`; D = distbench `isc-build` 2d2a59f5; S = a script Samyak runs; G = `~/.local/state/distbench/evidence/2026-11-12-factory/` (C, A and F ids: its `audit-verify-*.md`).

Pick: A's core with B's machinery, cut to the proof's critical path.
For a non-Loam target (today only distbench) the worker is a native session: user, project and local tiers, auto mode, sandbox off in the factory's flag tier, Samyak's plugin from the run's own Loam checkout.
The rest is factory tickets.

## Doubts settled by experiment

Claude Code 2.1.322, `claude -p`, 1.24 USD.
1. `--permission-mode auto --setting-sources user,project,local`, flag `sandbox.enabled false`: init auto; the classifier refused a force push despite the user tier's `Bash(*)`.
2. In a worktree user and project tiers load (verify-distbench, user agents, both CLAUDE.md, hooks); flag sandbox off beats D `.claude/settings.json:37` (AF_UNIX bind ok).
3. Denies `Bash(git push *)` and `Bash(git -C * push *)` match, `Bash(git -C * push:*)` does not; `GIT_SSH_COMMAND=false` stops ssh git.
4. Flag env `BASH_MAX_TIMEOUT_MS=5400000` let a 660 s command finish.
5. `--plugin-dir <L>/cultivation/marketplace/sam-cc-setup` replaces the installed plugin (C1); a `paths:` frontmatter key drops a skill from init (F1).

## Requirements

| Req | Mechanism | When | Observable; parity |
|---|---|---|---|
| (a) sandbox | Native shell (U3): flag tier = `worker-settings.json` minus sandbox plus `worker-settings-native.json`, no user-tier merge; call `--permission-mode auto --setting-sources user,project,local --plugin-dir`. Loam targets keep their sandbox; the pstack gate hook (U5) runs on every target, Loam included. | tonight | init auto, frozen sandbox off, digests equal; P7 |
| (b) gate cap | Flag env `BASH_DEFAULT_TIMEOUT_MS` = `BASH_MAX_TIMEOUT_MS` = 5400000 and `DISTBENCH_GATE_CLASS=factory`; F48 (Appendix) runs every spelling of `bin/check` as `--parallel`. | tonight | in-round `check: PASSED` or `FAILED`; P4 |
| (c) pstack | Router log line (U2) in D plan line 203's five fields; native user CLAUDE.md and `_common.md:14` name the router; P2 and P3 as fixed (U1). Hook: U5's PreToolUse gate (`pstack-gate.py`, parity's P2 and P3) on every target; it fails open on a host with no pstack method file or router. | tonight | decisions.md `pstack:` lines; P2, P3 |
| (d) reviews | `FACTORY_REVIEWER_MODEL=claude-fable-5-2` at high, `availableModels` in frozen role settings; Codex from the ticket's `codex-review: yes`; `verify_round` (U4) reproduces each blocking finding before `fixes`. Default, blind bundle: T7; audit, surprise-me: T9. | tonight | reviewer `served_models`; `verify.json`; P8 |
| (e) proof | verify-distbench loads natively; plan steps 1-3 run in-round on jhaveris. Steps 4-6: T3, T10. | tonight | P1, P4; P6 N/A for F48 |
| (f) scheduling | Proof launched by hand under the launch condition. Tick, lane, land, slots, scopes: T3, T4. | ticket | - |
| (g) unattended | Rounds compact at 450K (`worker-settings.json:3-4`; closed ruling L `docs/RULES.md:41`). Wake-up, watcher, NEEDS-SAMYAK: T8. | ticket | - |
| (h) self-improvement | A file ticket writes `followups.md`; `learn_run` (U4) drafts one ticket that Fable, Codex and the verifier review (today nothing, `bin/factory:2866,2880`). Dedupe, filing: T5. | tonight | `$RUN/learn/` |
| (i) measurement | `compare.py` exists (L 64ec111a). Attended map, serious rule, wiring: T6. | ticket | - |

The memory view (U3, surprise panel) puts the distbench memory, read-only, in every worker prompt; P1 checks it.

## Why this pick

- Native tiers load the instruction set itself (exp. 2): nothing copied, P1 holds without code.
- Auto mode reviews every unapproved action (exp. 1); `bypassPermissions` leaves only prefix denies.
- From design C (same outcome, simpler): both Bash timeouts (no timeout argument needed); no gate cache or split (a worker-writable cache is untrusted); a separate `REVIEWER_MODEL` with `availableModels`; one verifier call giving verdict, command and output per finding; follow-ups before the file ticket's early exit; `user,project,local`.
- Scope: the dry run found 15 units unbuildable in parallel (G `agent-reports/audit-dry-run.md`).

## (a) What is lost, what still guards

Lost against today's sandbox (`worker-settings.json:22-25`): the PyPI-only network allowlist; the Bash write fence (other checkouts and runs, `~/.claude`, the crontab, the run's `frozen/`); process isolation (signals, Docker, GPU); the egress barrier for credentials, whose reads were never blocked.
`WebSearch` stays allowed, since workers need it: an egress path that carries search queries only.
Still guards: the classifier on Bash, network included; `WebFetch` denied (F9); denies unioned across tiers (`rm -rf`, `git push`, `gh`, `pkill`, `killall`, `ssh`, `scp`, `crontab`); `GIT_SSH_COMMAND=false`, `GH_CONFIG_DIR=/nonexistent`; per-run worktree and branch; `do_not_touch_hits`; `check_frozen`; `tree_signature`; the supervisor's check-green; `bin/integrate --land` on the merged tree.
`Edit` and `Write` were never fenced.
P7 detects, never prevents, a write to `~/.claude` or the run's checkouts.

## (b) Gate load

Round 0 and each supervisor check-green stay serial outside the slice (1679 s); a worker gate is serial until F48's edit, then `--parallel` in the slice (landing g8: 330.6, 116.5, 22.0 s).
Two gate locks allow two gates per host; slot priority: T4.

## Build tonight

Step 0: merge `fix/factory-distbench-parity` (a3750d5b) and `fix/factory-distbench-compare` (64ec111a) into L; each unit branches from that in its own worktree.

Shared interfaces (writer; reader):
- `$RUN/frozen/plugin-dir`: the `--plugin-dir` path (U3; U1 P1).
- `$RUN/frozen/memory-view.md`: line 1 `# Memory view (written for the lead)`; line 2 says lines telling the lead to push, merge, rent or hand Samyak a `!` command do not apply; then `$FACTORY_MEMORY_DIR/MEMORY.md`, links absolute; appended to each `round-N.prompt.md` (U3; U1 P1).
- `$RUN/shell-digest.start`, `.end`: `sha256sum` of `~/.claude/{settings.json,settings.local.json,CLAUDE.md}` and files under `~/.claude/{rules,agents,skills}`, plus `<sha256 of git status --porcelain>  git-status:<dir>` for `$ROOT` and the main checkout (U3 at launch and finish; U1 P7).
- `round-N.findings.json`: `[{id, source, severity, file, line, claim}]`, `id` `reviewer-<i>` or `codex-<i>` (index in that file's `.findings`); blocking: reviewer high or medium, Codex critical or high (U4).
- `round-N.verify.json`: `{sha, findings: [{id, verdict, cmd, output, note}]}`, verdict CONFIRMED, PARTLY or REJECTED; REJECTED needs `cmd` and `output` (`verify.schema.json`; U4; U1 P8 recomputes blocking ids).
- `round-N.rejected`: the `fixes` line plus ` REJECTED: <note>` (U4).
- `$RUN/followups.md`: `- <source> [<severity>] <file>:<line> <text>`, source judge-backlog, reviewer, codex, mutation or rejected (U4).
- `$RUN/learn/`: `draft.md`, `draft.json` (`{repo: loam|distbench, title, source_line}`), `review-fable.json`, `review-codex.md`, `findings.json`, `verify.json` (U4).
- decisions.md: `pstack: <skill> | <SKILL.md path> | <sha256> | <quoted line> | <decision>` (U2; U1 reads fields 1-2).
- `bin/factory.d/review.sh`, frozen, sourced from `$RUN/frozen/`: `verify_round ROUND` returns 1 when it queued a fix, `learn_run` returns 0; ledger roles `verifier`, `learn-writer`, `learn-review` (U4; U3 calls).
- Launch env: `FACTORY_REVIEWER_MODEL` (default `GRADER_MODEL`), `FACTORY_REVIEWER_EFFORT` (default xhigh), `FACTORY_MEMORY_DIR` (unset: no view).

| Unit | Owns | Builds | Done check, and why it fails while broken |
|---|---|---|---|
| U1 parity | `bin/factory-parity`, its test, `bin/tests/fixtures/parity/` | Only a full read counts (a Read without offset or limit, a `cat`, the router's Skill call), never `sed -n`, `head` or `git cat-file`. P1: plugin path = `frozen/plugin-dir`, view line 1 in each prompt. P2 also counts a full read of a SKILL.md the brief names (C4); writes under `$RUN/worker/` are not changes (F5). P3: a method read anywhere before the first change; a changing round without a `pstack:` line FAILs (F3). P7: init auto, frozen sandbox off, digests equal; lists classifier `permission_denied` events (A3). P8 per graded round: reviewer `served_models == ["claude-fable-5-2"]`, `codex-review.json`, `verify.json` ids = blocking ids, REJECTED with `cmd` and `output`. `--attended FILE...`: P2, P3, P6 on session transcripts. | `pytest bin/tests/test_factory_parity.py` passes with a real-cut FAIL and a PASS fixture per new rule, and each rule's mutation turns a test red, so a rule that never bites fails; W24 and W35 FAIL P7 and P8. |
| U2 router | router `SKILL.md` (after :10), `plugin.json` 0.9.28 | `- Log each method you follow in your decision log (decisions.md in a factory run): pstack: <skill> \| <SKILL.md path read> \| <sha256 of that file> \| <one line quoted from it> \| <the decision it changed>` | In an empty scratch folder, `claude -p --model claude-opus-5-5 --plugin-dir <U2 worktree>/cultivation/marketplace/sam-cc-setup`, told to call the router for "add a test" and print only its log line, prints a match for `^pstack: \S+ \| /\S+/SKILL\.md \| [0-9a-f]{64} \| .+ \| .+$` (under 0.2 USD); nothing else it loads states that format. |
| U3 shell | `bin/factory`, `bin/factory.d/worker-settings-native.json` (new), `role-settings.json`, `bin/tests/test_factory_native.py`, `probe-native.sh` (new) | Non-Loam: freeze per (a), the native file holding (a)'s env and denies and `sandbox.enabled false`; `skill_file` reads `enabledPlugins` from the user tier; a user env with `CLAUDE_CODE_OAUTH_TOKEN` refuses the launch. All targets: `--plugin-dir` on worker and grader calls; `router_file` and `sam-cc-setup:` skills under `$ROOT`; reviewer model per role; `availableModels`; memory view; digests; `run_review` and `run_codex_review` stop writing `fixes`, `graders()` calls `verify_round`; `open_pr`'s file-ticket branch calls `learn_run` before `finish`. | Tests: Loam-target settings and argv byte-identical to today; non-Loam values as above; stubbed `verify_round` and `learn_run` called. Paid probe (under 0.3 USD): `probe-native.sh <scratch distbench clone>` runs the built argv two turns and prints `permissionMode=auto plugin=<L>/... verify-distbench=yes BIND_OK` from the real init and tool result, so wrong flags cannot print it. |
| U4 review | `bin/factory.d/review.sh`, `verify.md`, `verify.schema.json`, `learn.md`, `learn.schema.json`, `bin/tests/test_factory_review.py` (all new) | `verify_round`: one Opus 5.5 high call in auto mode (Bash, Read, Grep, Glob) in a detached worktree at `GRADED_SHA`, reading audit `SKILL.md:47-49` by path through `--add-dir`; CONFIRMED and PARTLY to `fixes` (block-once kept), REJECTED to `.rejected`, a REJECTED high or critical notifies needs-you (A2); no blocking finding, no call; a failed call counts all CONFIRMED, as today. `learn_run`: writes `followups.md`; if non-empty, an Opus writer drafts one ticket from the target's `docs/WORKERS.md` hand-off rules and ticket format, then `check_factory` (distbench) or `bin/factory lint` (Loam), Fable and Codex read-only reviews, the verifier, a needs-you notice; no call past `DAILY_BUDGET_USD`. | Stub tests: each routing above, no draft from empty follow-ups, the daily cap. Paid (under 0.6 USD): in a scratch repo a real off-by-one gets CONFIRMED and an invented defect REJECTED with `cmd` and `output`, so a yes-to-everything verifier fails. |

Merge order: U2, U4, U1, U3 (its call sites need U4; its tests stub it); then E1, Loam `bin/check` on the merged branch, the proof.

E1, attended control (after U1, no spend): `bin/factory-parity --attended` on the 8 sessions `find ~/.claude/projects/-home-samyak-distbench -maxdepth 1 -name '*.jsonl' -newermt 2026-11-08 ! -newermt 2026-11-12 -size +200k` lists, into G `attended-control.txt`.
A FAIL the rule caused, not the session, is fixed in U1 before the proof's verdict counts.

## Proof run

Ticket: F48 (Appendix), the distbench half of the gate route: real, needs the full gate, in nobody's queue, changes the gate only under a variable only the factory sets.
Base: own clone `~/.local/state/distbench/factory-proof/distbench` of `git@github.com:SamyakJhaveri/distbench.git` with refspec `+refs/heads/isc-build:refs/remotes/origin/main`, so `origin/main` is isc-build (`~/.local/bin/factory-isc:32-34`); Loam worktree `~/.local/state/loam/worktrees/factory-distbench-test` at merged L; runs root `~/.local/state/distbench/factory-proof/runs`.
Launch condition, read-only: no `f-*` tmux session; no `->` waiter in `/proc/locks` on the inode of any `~/.local/state/distbench/{gate-0,gate-1,gpu,mpi-0,mpi-1,integrate}.lock`, and `integrate.lock` free; `systemctl --user show distbench-build.slice -p MemoryCurrent --value` at most 8G (16 OOM kills at 24G, F7); F48 unused in D `docs/tickets/`.
Command, in tmux `f-f48-proof`:
`bash -lc 'FACTORY_RUNS_ROOT=$HOME/.local/state/distbench/factory-proof/runs FACTORY_DAILY_BUDGET_USD=9.5 FACTORY_REVIEWER_MODEL=claude-fable-5-2 FACTORY_REVIEWER_EFFORT=high FACTORY_MEMORY_DIR=$HOME/.claude/projects/-home-samyak-distbench/memory ~/.local/state/loam/worktrees/factory-distbench-test/bin/factory -C ~/.local/state/distbench/factory-proof/distbench run ~/.local/state/distbench/factory-proof/F48-factory-gate-class.md'`
`bash -lc` brings the profile's `FACTORY_CALL_TIMEOUT_SEC=14400` and `FACTORY_MAX_TURNS=2000` (F6).
Spend: this runs root's daily ledger holds only this run; bin/factory and `learn_run` refuse a call when spend plus its cap passes 9.5 USD; every call has `--max-budget-usd` (worker 2.5, others 1.5); `TICKET_BUDGET_USD=6` leaves learn room. Expected 5-7 USD (W35: 3.65, two rounds).
Done: `bin/factory-parity <runs root>/SamyakJhaveri__distbench/F48-factory-gate-class > G/parity-F48.txt` prints PASS for P1-P5, P7, P8, `N/A P6` (`bin/check` is outside verify-distbench's paths) and `parity: PASS`; `$RUN/learn/` holds a draft, two reviews and `verify.json`; a needs-you alert names it.
The run pushes nothing; `build/f-f48` and its listing are the lead's, and `Except: bin/check` needs his or Samyak's yes before landing.

## Factory tickets

Ticket: done check.
- T1 in-round pstack hook (`factory-parity --hook`, PreToolUse, U1's rules): replayed on W34 and W35 round 1, it exits 2 exactly where P2 FAILs.
- T2 P2, P3, P7, P8 after each worker round, into the judge bundle: a planted router-less round fails the judge.
- T3 lane and tick (D `bin/factory-lane` for `factory-isc`, L `tick.sh`, S timer with `EnvironmentFile`; admission by runs, heavy class, slice headroom; a scope per run; each tick lands the oldest finished group, C5): a timer-launched ticket logs `launch`, `land gN ok`, timeout 14400, 2000 turns; lane parity P9 passes.
- T4 gate slots (factory class takes only gate-1 while `integrate.lock` is held; slot-wait seconds in `metrics.json`; STALL ignores a waiting gate; A4; a gate cache only if over two gates per round): holding `integrate.lock`, a plain `bin/check` under the class prints `gate: slot 1`.
- T5 learn dedupe and filing (`learn.tsv` by class and blamed path; drafts to a pushed `retro/<date>` branch or a needs-triage issue; dry run and fix pass; A5): a second pass over the same runs drafts nothing.
- T6 measurement (attended map per item; rate table; one serious-finding rule; `metrics.json`; C3): every attended cell names its source; `compare.tsv` has a row per batch-2 item.
- T7 Fable reviewer default, `reviewer.md`, bundle without decisions.md, Codex default yes for distbench (paid replay, `LOOP.md:470`): `graders-check` passes, replay recorded.
- T8 NEEDS-SAMYAK render with acknowledgement, healthchecks beat, STALL watcher, alert on a classifier refusal of `bin/check`, docker or mpirun (A3): a planted refusal reaches NEEDS-SAMYAK.md.
- T9 audit and surprise-me where D `docs/WORKERS.md:34-36` puts them: a batch end writes `audit.md`.
- T10 plan steps 5-6: a planted `UNVERIFIED` proof line becomes a NEEDS-SAMYAK line.
- T11 stale copies (`LOOP.md`, `ARCHITECTURE.md`, `CONTRACT.md`, `bin/overnight/protocol.md`, `_common.md:13`, `factory-round.js:213,219`): lean-critic finds no stale sandbox, reviewer or model sentence.
- T12 analogist ideas 3 and 4 (a read-back; learning from Samyak's corrections): a planted misread brief is flagged.

## Findings closed

| Id | Closed by |
|---|---|
| C1, L3 1 | U3 `--plugin-dir`; U1 P1 |
| C2 | proof shows (a)-(e), (h); (f), (g): T3, T8, checked timer-launched |
| C3, L7 1 | T6 |
| A4, A5 | T4, T5 |
| C4 | U1 P2 brief-named read |
| A2 | U1 P8 id sets, REJECTED evidence; U4 alert |
| A3 | U1 P7 lists denials; alert T8 |
| A6 | rejected: L `docs/RULES.md:41` |
| F1, D4 1 | D4 dropped; P6 keeps its covered list |
| F2 | U3 class env plus F48 |
| F3 | U2 line reaches workers by `--plugin-dir`; U1 P3 FAILs without a line |
| F4 | U1 P8 `served_models`, id sets; U3 `availableModels` |
| F5 | U1 P2, P3; `_common.md:14` and its tie-break kept for Loam targets |
| C5, F6, F7 | T3 (`land` each tick, `EnvironmentFile`, scopes, headroom); the proof's `bash -lc` and launch condition |
| F8 | U1 P7 digests; (a) says it detects |
| F9 | U3 denies `WebFetch` |
| Dry-run L1 1-5 | `gate.sh` dropped; F48 routes every spelling |
| L2 1 | schemas above; P4 unchanged |
| L5 1-3, D3 1-2, S1 2 | T3 |
| L6 1-2 | drafts in `$RUN/learn/`; classes T5 |
| L8 1 | `FACTORY_REVIEWER_MODEL`; `reviewer.md` waits for T7 |
| L8 2 | native shell for non-Loam targets; Fable by launch env; Codex by ticket |
| D1 1 | no D policy unit; F48 is the only D change |
| Proof 1-3 | Proof run |

## Would not do

- A sandbox with exceptions (ruled off, 22:55 PT 11 Nov); a separate OS user (Samyak's setup; a follow-up); an LLM lead for scheduling.
- A per-run `MemoryMax` scope tonight: `bin/check` re-execs only from outside the slice, so the in-round gate would run under the run's cap.
- A 450K hand-off file (L `docs/RULES.md:41`); edits to origin/redesign-1030.

## Risks

- The classifier may refuse `systemd-run`, docker or mpirun (it refused the lead, inventory J09); P7 lists refusals; T8 alerts.
- F48's worker edits the gate that grades it; reviewers, the verifier and the landing's rerun stand between.
- The slice check holds only at launch; a landing shares the 24G with the worker's `--parallel` gate.
- Fable through the grader config is unrun; P8 fails a fallback.
- With no follow-up, (h) stays unshown.
- Program spend so far: 7.02 USD notional (G `spend.txt`); proof up to 9.5, probes 1.1.

## Appendix: proof ticket

Save as `~/.local/state/distbench/factory-proof/F48-factory-gate-class.md`; on a scratch copy of D, `bin/factory lint` and `check_factory` pass and the block prints the predicted FAIL.

````markdown
# F48: With DISTBENCH_GATE_CLASS=factory, a plain bin/check runs as bin/check --parallel
**GitHub issue:** none; a file ticket, never published as an issue
**Status:** draft
Brief:
A Loam factory worker runs the gate in any spelling (`guard bin/check`, a bare `bin/check`); only `--parallel` runs it inside `distbench-build.slice`.
Where: `bin/check` (before its argument `case`), `tests/test_repository_gate.py`.
Done means: with the variable set and no argument, `bin/check` prints one line and re-execs as `bin/check --parallel` in the slice; unset, nothing changes; a test carries it; `bin/check` ends `check: PASSED`.
Out of scope: gate slots, a gate cache, the supervisor's own gate.
Track: B    Risk: low    Mode: build    Open question: none
Runs: the Loam factory from its own clone (Loam's design-pick.md).
Blocked by: none

## Goal and why
The factory's worker shell puts `DISTBENCH_GATE_CLASS=factory` in every worker Bash call (Loam branch fix/factory-distbench).
A plain `bin/check` runs serially outside the 24G slice, holding a gate slot 1679 s (W13a); `--parallel` ran landing g8's pytest phases in 330.6, 116.5 and 22.0 s inside it (audit finding F2).

## Do not touch
The standing list. Except: `bin/check`.
Also: `bin/gate.py`, `conftest.py`, `bin/integrate`.

## Out of scope
Slot priority while `integrate.lock` is held; a gate cache; a fallback when `--parallel` is refused (the refusal stays visible); the supervisor's own gate.

## Approach
Before the argument `case`: with no argument and `DISTBENCH_GATE_CLASS` equal to `factory`, print `bin/check: DISTBENCH_GATE_CLASS=factory runs as bin/check --parallel`, then `unset DISTBENCH_GATE_CLASS` and `set -- --parallel`.
The unset keeps a gate a test starts on its own path.
Carry `class-route` into `tests/test_repository_gate.py` as a test named with `gate_class` (its `_repo` helper, fake `systemd-run` and `systemctl` first on `PATH`).

## Done checks
```done-checks
predict class-route ! grep -q DISTBENCH_GATE_CLASS bin/check
T=$(mktemp -d "${TMPDIR:-/tmp}/f48.XXXXXX"); mkdir -p "$T/r/bin" "$T/f"; cp bin/check "$T/r/bin/check"; git -C "$T/r" init -q; printf '#!/usr/bin/env bash\nprintf "%%s\\n" "$*" >> "%s/f/argv"\n' "$T" > "$T/f/systemd-run"; printf '#!/usr/bin/env bash\necho /x/distbench-build.slice\n' > "$T/f/systemctl"; chmod +x "$T/f/systemd-run" "$T/f/systemctl"; on=$(cd "$T/r" && HOME="$T" PATH="$T/f:$PATH" DISTBENCH_GATE_CLASS=factory timeout 120 bin/check 2>&1); a=$(cat "$T/f/argv" 2>/dev/null); : > "$T/f/argv"; off=$(cd "$T/r" && HOME="$T" PATH="$T/f:$PATH" env -u DISTBENCH_GATE_CLASS timeout 120 bin/check 2>&1); grep -q 'DISTBENCH_GATE_CLASS=factory runs as bin/check --parallel' <<<"$on" && { grep -q /distbench-build.slice/ /proc/self/cgroup || grep -qE -- '--slice=distbench-build.slice .*/bin/check --parallel$' <<<"$a"; } && ! grep -q DISTBENCH_GATE_CLASS <<<"$off" && [ ! -s "$T/f/argv" ] && pass class-route || fail class-route "with the class and no argument, bin/check must print its route line and re-exec as systemd-run --slice=distbench-build.slice <root>/bin/check --parallel; unset, it must not call systemd-run; got: $(tail -n 2 <<<"$on" | tr '\n' ' ') systemd-run: $a"
out=$(guard bin/check 2>&1); rc=$?; last=$(tail -n 1 <<<"$out"); { [ -n "${LOAM_HOOK:-}" ] || { [ "$rc" = 0 ] && [ "$last" = "check: PASSED" ]; }; } && pass check-green || fail check-green "bin/check must exit 0 and end check: PASSED; rc $rc, last line: $last"
```

## Worker
worker: claude
codex-review: yes
effort: high
contract: 2
skills: pstack:tdd
goal: the done-checks block prints no FAIL line, or stop after 60 turns
MAX_ROUNDS=3
TICKET_BUDGET_USD=6
ROUND_BUDGET_USD=2.5
GRADER_BUDGET_USD=1.5

## Decisions
On jhaveris, 12 Nov 2026, at `isc-build` `2d2a59f5` in a scratch copy: the predict line exits 0 and `class-route` FAILs; with the Approach's five lines it passes and the fake records `--slice=distbench-build.slice <tmp>/r/bin/check --parallel`.
Inside the slice `bin/check` does not re-exec, which `class-route` accepts.
````
