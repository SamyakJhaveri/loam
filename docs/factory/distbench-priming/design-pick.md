# Design pick (12 Nov 2026): the factory builds distbench like an attended session

L = Loam `fix/factory-distbench` (`bin/factory` as at 5e7fc15f); D = distbench isc-build 31599c19, the factory's base, unless a cite says D main (582df455); S = a script Samyak runs.
Letters follow `program.md` (a)-(i).

Pick: a graft.
From A, the core: the worker is a distbench session loading Samyak's user tier and distbench's project tier natively, in auto mode, sandbox off in the factory's flag tier; Loam's prompt copies go.
From B: a target declaration in D `STANDING.md`, a gate cache, a code tick and lane script, a verifier reading the audit skill by path, a learn step, a compare script.
Fixed from A (`design-A.md:9`): load `user,project`, not `local`.

## Doubts settled by experiment

Claude Code 2.1.322, six `claude -p` calls (0.88 USD) in a clone of `~/distbench-isc` and its git worktree, with marker denies in the clone's `settings.json` (MAINMARK), the worktree's (WTMARK) and the clone's `settings.local.json` (LOCALMAIN).

1. Auto mode works headless: `--permission-mode auto --setting-sources user,project,local --settings '{"sandbox":{"enabled":false}}'` gave init `"permissionMode":"auto"` and refused `git -C <scratch> push --force origin HEAD:main`: "denied by the Claude Code auto mode classifier. Reason: [Git Destructive]", although the user tier allows `Bash(*)`. `modelUsage` listed only claude-opus-5-5.
2. Tiers in a worktree: init listed verify-distbench, formal-orchestrator and user agents (worker, scout, escalate); the session quoted `~/.claude/CLAUDE.md`, D `CLAUDE.md` and `AGENTS.md`; the user hook fired. Project settings came from the worktree (WTMARK denied, MAINMARK ran); the local tier came from the main checkout (LOCALMAIN denied) unless sources were `user,project`. The flag `sandbox.enabled false` beat the project `true` (D `.claude/settings.json:37`): an AF_UNIX bind printed BIND_OK; the project-only control got `Operation not permitted`. `memory_paths.auto` named the main clone's folder.
3. Deny syntax: flag deny `Bash(git -C * push:*)` let `git -C <scratch> push origin HEAD:refs/heads/build/f-x` through; `Bash(git -C * push *)` and `Bash(git push *)` denied it and `cd <scratch> && git push`. Flag env `GIT_SSH_COMMAND=false` made `git ls-remote git@github.com:SamyakJhaveri/distbench.git` fail; without it, it succeeded.
4. Flag env `BASH_MAX_TIMEOUT_MS=5400000`: a Bash call `sleep 660; echo SLEPT_OK` (timeout 900000) returned SLEPT_OK after 663 s; workers were cut at "Command timed out after 10m 0s" (`runs-w24-w34-w35.md:29,69`).
5. A PreToolUse hook in an Agent subagent got the parent's `transcript_path` and an `agent_id`; the subagent's transcript is `<session>/subagents/agent-<agent_id>.jsonl`.

## Requirements

| Req | Pick | Mechanism | Files to change | Observable; parity id |
|---|---|---|---|---|
| (a) sandbox | graft | D declares `sandbox: off` under `## Worker shell`; freeze then writes the flag tier with `sandbox.enabled false` and no user-tier merge (L `bin/factory:1451-1467`), and the call runs `--permission-mode auto --permission-prompts none --setting-sources user,project` (today `bypassPermissions`, `''`: :2349-2350). Other targets unchanged. | L `bin/factory`, `worker-settings.json`; D `docs/factory/STANDING.md` | init `permissionMode: auto`; frozen `.sandbox.enabled == false`; P7 |
| (b) gate in round | graft | `guard ... bin/check` runs frozen `gate.sh`: D's `gate:` line (`DISTBENCH_GATE_CLASS=factory bin/check --parallel`), cached per clean tree in `$RUN/worker/gate/` inside the worker session only. Stop hook: cheap block (`LOAM_HOOK=1`), then the full block, timeout 900 to 5400 s (`worker-settings.json:27`); `BASH_MAX_TIMEOUT_MS=5400000`. | L `gate.sh` (new), `lib.sh:24`, `worker-settings.json`; D `STANDING.md`, `bin/check` | Bash result or Stop-hook event ending `check: PASSED` or `FAILED`; P4, extended to hook events |
| (c) pstack proof | graft | User CLAUDE.md's router line loads (exp. 2). PreToolUse hook `factory-parity --hook` exits 2 on a change (`changes()`, `factory-parity:170`) until that agent's transcript shows a router read (`reads_router()`, :182). The router gains a log line in D plan line 203's format (`pstack: <skill> \| <path> \| ...`). The supervisor runs P2/P3 before the judge; a FAIL blocks and enters the judge bundle. | L `factory-parity`, router `SKILL.md`, `plugin.json`, `bin/factory`; delete `_common.md:14`, `factory-round.js:107`, `bin/factory:2071-2075` | Skill `sam-cc-setup:pstack` before the first change; `round-N.conduct`; P2, P3 |
| (d) reviews | graft | The reviewer runs claude-fable-5-2 high, its bundle without `decisions.md` (today Opus xhigh, `bin/factory:1075`; bundle :2480). Codex read-only every graded round (default `no`, :2968). `verify.sh`: one Opus 5.5 high call in a detached worktree at GRADED_SHA (as :2684) reads audit `SKILL.md:47-49` by path and marks each blocking finding; only CONFIRMED and PARTLY reach `round-N.fixes` (today verbatim, :2601, :2658). `skill-call.sh` runs audit by path on self-filed drafts (dry run, D main `WORKERS.md:46`) and each batch's landed diff; surprise-me Panel on design-class drafts (:25-27). | L `bin/factory`, `verify.sh`, `verify.schema.json`, `role-settings.json`, `skill-call.sh`; S Fable allow | ledger reviewer `claude-fable-5-2`; `round-N.verify.json`, `.codex-review.json`; P8 |
| (e) behaviour proof | graft | verify-distbench loads (exp. 2); the worker runs `control-distbench launch`. D adds `paths:` to verify-distbench and formal-orchestrator (allowed, D `bin/check:314-318`); P6 reads them, not its copy (`factory-parity:53-54`). Steps (plan line 231): 1 round 0 (`bin/factory:1954`); 2-3 in-round tests, gate, verify-distbench, then check-green; 4 the landing; 5-6 an `UNVERIFIED` line when the Proven line names P or R. | D two `SKILL.md`; L `factory-parity` | init lists verify-distbench (P1); read and launch on covered paths (P6, plus UNVERIFIED lines) |
| (f) scheduling | B | L `tick.sh` (10 min) launches released file tickets from a queue through D `bin/factory-lane launch` while runs < `FACTORY_MAX_PARALLEL` (3; 4 after W04) and `lane hold <ticket>` exits 0 (heavy ≤ 3; no landing waiting over two gate runs, plan line 184). `launch` runs the factory in `distbench-build.slice` (today outside, J16), pushes `build/f-<id>` and lists it; `land` runs `bin/integrate --land --group N` plus a Codex read-only review. | L `tick.sh`; D `bin/factory-lane` (replaces `~/.local/bin/factory-isc`), `bin/check` | `tick.log` `launch W41 runs=2/3 heavy=1/3 hold=ok`; run `cgroup`; P9 |
| (g) unattended | graft | Wake-up: the S timer. 450K: rounds are fresh calls compacting at 450K (`worker-settings.json:3-4`), plus a SessionStart `compact` hook naming the ticket and `decisions.md`. Dead watch: lease reap (`LOOP.md:322`), a healthchecks beat per tick (:355-357), STALL when `pending.jsonl` and the gate log idle 30 minutes. Each tick renders `~/.local/state/distbench/NEEDS-SAMYAK.md` from needs-you lines of `alerts.jsonl` (:365), with `!` commands. | L `tick.sh`, `worker-settings.json`; S timer | `tick.log` beats; `NEEDS-SAMYAK.md`; P11 |
| (h) self-improvement | graft | File tickets write backlog and blocking findings to `$RUN/followups.md` (today skipped: `bin/factory:2866` exits before :2880-2881). `learn.py` reads run folders (parity FAILs, open or rejected findings, env stops, failed landings); a class seen twice, or one confirmed High, starts one ticket-writer call (D main `WORKERS.md:30-46` by path) drafting into the blamed repo's inbox; `skill-call.sh` audits it. Release stays with the lead or Samyak, via NEEDS-SAMYAK. | L `learn.py`, `skill-call.sh`, `bin/factory` | drafts with `reviews-tickets/<id>.md`; P10 |
| (i) measurement | B | `compare.py`, one row per batch-2 item: arm, confirmed Medium-or-worse findings from reviewers both arms face (landing Codex, batch-end audit), reruns, USD, wall time. Attended: D `docs/tickets/ledger.tsv` (207 rows), L `bin/usage-audit`; factory: `metrics.json`. Prediction first; medians with n, no winner (arms not randomized). | L `compare.py`, `bin/factory` | `compare.tsv`; P12 |

New parity rows (P9-P11 under a `--lane <state dir>` mode):
- P7 shell: init auto mode, frozen sandbox off, no change under `$RUN/frozen`, `~/.claude` or another checkout.
- P8 review: each graded round has a claude-fable-5-2 reviewer row and `codex-review.json`; every reviewer or Codex line in `fixes` has a CONFIRMED or PARTLY verdict in `verify.json`.
- P9 schedule: `launch` lines within caps; runs in the slice; a Codex review per landed group.
- P10 learn: each draft's review has Fable 5.2, Codex, Verify and Dry-run sections.
- P11 unattended: no beat gap over two periods; every needs-you alert in `NEEDS-SAMYAK.md`.
- P12 metrics: each finished run has `metrics.json` (rounds, relaunches, usd, wall_s, confirmed findings).

## Why this pick

- A's core loads the instruction set natively (exp. 2), so P1 passes without code; under `''` the init lists 86 skills without verify-distbench (`parity-w34.txt:1`), and B's view would reimplement Claude Code's loader yet still fail P1.
- Auto mode reviews every unapproved action (exp. 1); B keeps `bypassPermissions`, leaving only prefix denies (`LOOP.md:234`).
- B's objection to native tiers is answered: `.claude/` is on D's standing list (D `STANDING.md:9`), so a settings edit fails the round (`bin/factory:2396`); denies union across tiers (exp. 2); auto memory stays off (`worker-settings.json:2`), and must, since its folder is the main checkout's.
- (c) runs as code ahead of the judge, not a `judge.md` row: deterministic, and no paid grader replay (`LOOP.md:470`).

## (a) What is lost, what still guards

Lost against today's sandbox (`worker-settings.json:22-25`):
- The network allowlist (PyPI only, `LOOP.md:236`): Bash reaches any host.
- The Bash write boundary (`LOOP.md:235`): Bash can write other checkouts and runs, `~/.claude`, the crontab and the run's `frozen/`.
- Process isolation: Bash can signal other sessions and use Docker and the GPU.
- The egress barrier for credentials, whose reads were never blocked (`LOOP.md:240`).
Never protected: the Write and Edit tools, and worker code that the Stop hook and `run_checks` run (`LOOP.md:240`).

Still guards:
- The auto-mode classifier (exp. 1).
- Denies unioned across tiers; the flag tier adds, in exp. 3's space form, `Bash(git -C * push *)`, `Bash(git push *)`, `Bash(pkill *)`, `Bash(killall *)`, `Bash(ssh *)`, `Bash(scp *)`, `Bash(crontab *)`.
- Worker env `GIT_SSH_COMMAND=false` (exp. 3) and an empty `GH_CONFIG_DIR`.
- Per-run worktree and branch; the standing list (`bin/factory:2396`); `check_frozen` (:1489-1491) plus a digest of `frozen/sha256` in supervisor memory; `tree_signature` around graders (:2665).
- The supervisor's own check-green each round, and `bin/integrate --land` on the merged tree as the authority for isc-build (J22).
Only the classifier guards the network; a same-user worker can still edit any file, which P7 reports but does not prevent.

## (b) Gate load, and the forged cache

The gate becomes `bin/check --parallel`: landing g8's pytest phases took 330.6, 116.5 and 22.0 s (`~/.local/state/distbench/integrate/20261112T044124.116981Z-g8/`), against 1679 s for the serial factory gate (`factory-gate/095012c0...log`).
- Concurrency: every gate takes `gate-0.lock` or `gate-1.lock` (D `bin/check:13,143-156`), so at most two run.
- Landings first: a D `bin/check` change lets a `DISTBENCH_GATE_CLASS=factory` gate take only `gate-1` while `integrate.lock` is held, so a landing waits at most one factory gate (J21: group 6 waited 37 minutes).
- Memory: `--parallel` runs in `distbench-build.slice`, 24G (D `bin/check:48-55`; J19); today's serial gate escapes it.
- Count: worker and Stop hook share the cache, so a session gates each tree once, plus one supervisor gate per round: about 16 slot-minutes per passing round, against 28 today.
- Admission: the caps and hold of (f).

Forging does not matter, because the supervisor never reads the cache.
Only the worker call's env names `$RUN/worker/gate/`, and `run_checks` (`bin/factory:1945`) runs the gate unsandboxed, as today.
A forged entry fools only the forger's Stop hook, and the landing reruns the gate on the merged tree.

## Build units

One commit per unit. Batch 1 runs in parallel (disjoint files); L8 and L9 follow L1, L2, L4 and L6; the proof run is last.

| Unit | Repo: files | Done check: expected output |
|---|---|---|
| L1 gate | L `bin/factory.d/gate.sh` (new), `lib.sh`, `bin/tests/test_gate.py` (new) | `pytest bin/tests/test_gate.py`: pass (cache set: stub runs once, `gate: cached`; unset: twice) |
| L2 parity | L `bin/factory-parity`, its test and fixtures | W35: `parity: FAIL (P1, P2, P3, P4, P5, P7, P8, P12)`; pass fixture: `parity: PASS`; `--hook` change before router: exit 2 |
| L3 router | L `sam-cc-setup/skills/pstack/SKILL.md`, `plugin.json`, `agents/plan-reviewer.md` (Fable 5.2) | `pytest bin/tests/test_pstack_router.py`: pass; `grep -c '^- Log each method' <router>`: 1 |
| L4 verify | L `verify.sh`, `verify.schema.json` (new), test | stub CONFIRMED and REJECTED verdicts: one line each in `round-1.fixes`, `round-1.rejected` |
| L5 tick | L `tick.sh` (new), test | `tick.sh --dry-run`, 5 queued, cap 4: 4 `launch`, 1 `hold cap`; a fake alert reaches `NEEDS-SAMYAK.md` |
| L6 learn | L `learn.py`, `skill-call.sh` (new), test | two run folders sharing a FAIL class: one `draft`; one folder: none |
| L7 compare | L `compare.py` (new), test | on W13a, W24, W34, W35 and `ledger.tsv`: a factory row n=4 and an attended row |
| L8 wiring | L `bin/factory`, `worker-settings.json`, `role-settings.json`, `_common.md` (drop :14, and "(Explore)" and the model sentence at :13), `factory-round.js` (drop :107; :213, :219 to high) | synthetic distbench-shaped run: init auto mode; `round-1.conduct`, `verify.json`, `metrics.json` exist; `bin/tests` pass |
| L9 docs | L `docs/factory/LOOP.md`, `ARCHITECTURE.md`, `CONTRACT.md`, `bin/overnight/protocol.md` | `git grep 'Fable 5.1' docs/factory bin/overnight`: nothing |
| D1 policy | D `docs/factory/STANDING.md`, `docs/design/APPROVALS.md` (11 Nov ruling), gate-owner lines in `docs/WORKERS.md`, `docs/tickets/SESSION-PROTOCOL.md` | `grep -c '^sandbox: off$' docs/factory/STANDING.md`: 1; `bin/check_tickets.py`: OK |
| D2 slots | D `bin/check`, a slot test | holding `integrate.lock`, a stub factory-class gate prints `gate: slot 1` |
| D3 lane | D `bin/factory-lane` (new), test | scratch repos: `launch` adds one row; `hold` exits 1 while a row waits over two gate runs |
| D4 paths | D two `SKILL.md` frontmatters | `grep -c '^paths:'` each: 1; frontmatter step (`bin/check:309-335`) silent |
| S1 host | L `bin/factory.d/host-setup-jhaveris.sh` (new, Samyak runs it): `samyak-allow-fable-5-2.sh`, tick timer, healthchecks URL | `jq '.availableModels\|index("claude-fable-5-2")' ~/.claude/settings.json`: not null; `systemctl --user is-active factory-tick.timer`: active |
| Proof | own Loam checkout, runs root, clone (`distbench-priming-notes.md:17`) | gate-needing ticket: `bin/factory-parity <run>` ends `parity: PASS` |

## Would not do

- A sandbox with exceptions: ruled fully off (Samyak, 22:55 PT 11 Nov).
- A separate OS user: the real boundary, but its setup is Samyak's; a follow-up.
- A lead session or A's 20-minute LLM tick for scheduling: a model call per tick for work code does.
- Supervisor reuse of worker gate records: see (b).
- Auto-release of self-filed tickets: distbench releases by entry (D32).
- Edits to `judge.md`, `skills.txt` or `_common.md:8`: not copies, and Loam targets use them.
- Edits to origin/redesign-1030, which is fenced; its plan line 189 still says worker shells are sandboxed.

## Risks

- The classifier may refuse legitimate steps (docker, mpirun) and stall rounds (it refused the lead, J09); its cost is invisible.
- Unrun: `--permission-prompts none` (read from `--help`) and the hook payload in a Workflow builder.
- The reviewer swap is a grader change whose paid replay (`LOOP.md:470`) may pass 10 USD.
- Two `--parallel` gates share the 24G slice, which W27's timing test OOM'd (J19).
- The proof run competes with landings and may pass 10 USD (W24: 21.79); it needs Samyak's yes.
- Workers read the base's instructions: D `WORKERS.md` at 31599c19 lacks main's router text, which isc-build 2d2a59f5 has.
- User CLAUDE.md says auto-compaction is off; the worker's flag tier compacts at 450K.
- Tickets spell check-green two ways (`guard bin/check`, `guard flock .../gpu.lock bin/check`); `gate.sh` must replace the whole argv, or a held `gpu.lock` may get `--parallel` refused (D `bin/check:131-150`).
