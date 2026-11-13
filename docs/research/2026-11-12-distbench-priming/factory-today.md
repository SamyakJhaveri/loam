# Loam software factory today (Loam main 5e7fc15f), as it applies to DistBench

Paths: `L/` = /Users/samyakjhaveri/loam at 5e7fc15f (jhaveris ~/loam is the same commit). `D/` = /Users/samyakjhaveri/distbench at 582df455. `J:` = read on jhaveris, 2026-11-12.
Claims marked (inference) are read from code but not run.

## 1. Instructions the worker sees

The Claude worker gets one prompt file: the ticket body, then `_common.md` with the router path filled in, then one "read <SKILL.md>" line per `skills:` name, then from round 2 the failing check lines and blocking findings (`L/bin/factory:2053`, `:2059-2079`, `:2093-2100`; `L/docs/factory/LOOP.md:273`).
`unattended.md` (do not stop to ask; carry on) is appended to the system prompt (`L/bin/factory:2351`; `L/bin/factory.d/unattended.md:1`).
It runs with `--setting-sources ''` and `--settings <run>/frozen/worker-settings.json` (`L/bin/factory:2350`), so DistBench's project and local settings, project skills, `CLAUDE.md` and `AGENTS.md` do not load (`L/docs/factory/LOOP.md:305`), nor `~/.claude/CLAUDE.md`, `~/.claude/rules/` or `~/.claude/agents/` (`L/docs/factory/LOOP.md:239`, `:243`).
The frozen worker settings are `worker-settings.json` merged over the runner's user tier `~/.claude/settings.json` minus its `sandbox`, OAuth token, `permissions.allow` and `additionalDirectories` (`L/bin/factory:1451-1467`). So the runner's user-tier plugins (`enabledPlugins`), env, and (inference) user-tier hooks reach the worker; DistBench's `.claude/settings.json` (`D/.claude/settings.json`: `allowLocalBinding`, `excludedCommands`) does not.
`skills:` may name only a line of `bin/factory.d/skills.txt`, which is empty, or a `pstack:<name>` (`L/docs/factory/CONTRACT.md:47`; `L/bin/factory.d/skills.txt` has 0 lines). DistBench's project skill `verify-distbench` therefore cannot be named; `_common.md` only says "Gather evidence with the target's own verification tool" (`L/bin/factory.d/_common.md:15`).
MCP servers are off (`--strict-mcp-config`, `L/bin/factory:2349`).
A Codex worker runs with a factory-only `CODEX_HOME` (operator `~/.codex` AGENTS.md, rules and memories excluded), skills and plugins off, and the worktree trusted so the target's `.codex` config and rules bind it (`L/docs/factory/LOOP.md:250-266`); (inference) Codex then also reads the worktree's own `AGENTS.md`.
Graders see only their frozen rubric plus the evidence bundle, with `--tools Read,Grep,Glob`, `--setting-sources ''`, a private `CLAUDE_CONFIG_DIR`, and a read fence to the worktree (`L/bin/factory:2539-2544`; `L/bin/factory.d/role-settings.json:7`; `L/docs/factory/LOOP.md:161-166`).
The overnight driver call, unlike the worker, does not pass `--setting-sources ''`: it loads the normal tiers plus `bin/overnight/settings.json` (`L/bin/overnight/driver.sh:150`).

## 2. pstack

The router is named by path, not by skill call: `_common.md:14` says "A Claude worker, before a non-trivial task, reads the pstack router at <router> and follows the method it picks; ... this prompt's subagent rule wins over the method" (`L/bin/factory.d/_common.md:14`).
`router_file` resolves `<seed-skills installLocation>/sam-cc-setup/skills/pstack/SKILL.md` from `~/.claude/plugins/known_marketplaces.json` (`L/bin/factory:669-674`); `build_worker_prompt` fills `<router>`, or writes "(missing on this host, so skip this line)" and logs FAIL (`L/bin/factory:2048-2052`); fan-out builders get it in the Workflow args (`L/bin/factory:2086`; `L/bin/factory.d/factory-round.js:213`).
`bin/factory status` prints PASS/FAIL for the router file (`L/bin/factory:3899-3901`).
The "drift guard" of 5e7fc15f is a unit test that every name the router lists is an installed pstack skill (`L/bin/tests/test_pstack_router.py:57-65`); it does not check workers.
Nothing checks that a worker read the router: the only references are prompt build and status (`git grep router L/bin/factory`). Evidence from J: of the four DistBench file-ticket runs, the router path is in every post-5e7fc15f round prompt, a worker `Bash sed ... pstack/SKILL.md` read appears in W34 round 1 only, W24 round 1 passed it to Workflow builders, and W35 rounds 1-2 and every round 2 show no read (`J: runs/SamyakJhaveri__distbench/*/round-*.jsonl`).
`skills: pstack:<name>` adds "read <SKILL.md>" lines and pstack's Claude Code adapter (`L/bin/factory:2071-2076`).

## 3. Models and effort per role

| Role | Model, effort | Source |
|---|---|---|
| Worker (Claude) | `claude-opus-5-5`, ticket `effort:` (default high) | `L/bin/factory:1067`, `:1071` |
| Worker advisor | `claude-opus-5-5` (`--advisor`) | `L/bin/factory:1070`, `:2349` |
| Worker subagents, sonnet/haiku aliases | pinned to worker model, `SUBAGENT_MODEL_FORCE=1` | `L/bin/factory:2347-2348`, `:1461-1462` |
| Fan-out builders and integrator (`size: large`) | xhigh | `L/bin/factory.d/factory-round.js:213`, `:219` |
| Worker (Codex) | `gpt-6.1-sol`, ticket effort | `L/bin/factory:1069`, `:2311` |
| Judge | Opus 5.5 high | `L/bin/factory:1068`, `:1072` |
| Reviewer | Opus 5.5 xhigh | `L/bin/factory:1075` |
| In-run Codex review (`codex-review: yes`) | `gpt-6.1-sol`, `GRADER_EFFORT` (high), read-only | `L/bin/factory:2629` |
| lean-critic | Opus 5.5 high, by hand outside the loop | `L/docs/factory/ARCHITECTURE.md:82` |
| plan-reviewer, brief, design | "Fable 5.1 at high", by hand | `L/docs/factory/ARCHITECTURE.md:83`, `:86` |
| Overnight driver call | Opus 5.5 high, max-turns 400 | `L/bin/overnight/driver.sh:150` |
| Overnight panel | Codex read-only high; Fable via `escalate` ("Fable 5.1"); Opus scouts verify; Opus worker fixes | `L/bin/overnight/protocol.md:26`, `:61-66` |

No Fable runs inside the factory loop (`L/docs/factory/ARCHITECTURE.md:81`). The "Fable 5.1" strings are older than the owner's current Fable 5.2 (global CLAUDE.md, "Agents and models").

## 4. Review route

In-run, per round whose checks pass: judge, then (only after a judge pass) the mutation sweep, then the reviewer, then the Codex review if the ticket sets it, each fresh and read-only (`L/bin/factory:2707-2716`).
Blocking: judge verdict fail; reviewer high or medium finding; Codex critical or high; any surviving mutant (`L/bin/factory:117`, `:120`; `L/docs/factory/LOOP.md:141-143`). Reviewer, Codex and sweep may each block once per ticket (`L/bin/factory:2594-2598`, `:2652-2656`, `:2695-2700`).
Blocking findings go verbatim into `round-N.fixes` and the next worker prompt (`L/bin/factory:2600-2601`, `:2657-2658`); there is no in-run verifier that reproduces a finding before it reaches the worker, and no fixer role (`L/docs/factory/LOOP.md:70`).
At most two grader-fail rounds, then a draft PR with the backlog (`L/bin/factory:1079`, `:2889-2895`).
A judge pass that contradicts its own rows is re-asked once (`L/bin/factory:2504-2513`, `:2552-2556`).
The verifier-and-fix route (panel of Codex, Fable, optional surprise-me; Opus scouts mark CONFIRMED/REJECTED/PARTLY; Opus worker fixes; Codex re-review of the fix up to twice more) exists only in the overnight protocol, for Loam PRs (`L/bin/overnight/protocol.md:61-68`, `:24`).

## 5. Proof

Round 0 runs the frozen done-checks at `base.sha` in a detached worktree; every non-guard check must FAIL and every `predict` must hold, else `ticket-defect` (`L/bin/factory:1954-2002`).
The worker's own Bash runs in Claude Code's sandbox: `failIfUnavailable`, no unsandboxed escape, network only `pypi.org` and `files.pythonhosted.org` (`L/bin/factory.d/worker-settings.json:22-25`); the sandbox cannot bind a unix socket (`L/docs/factory/LESSONS.md:637`). DistBench's `bin/check` exits 1 on that AF_UNIX probe (`D/bin/check:10-27`).
The Stop hook runs `checks.sh` with `LOAM_HOOK=1` (`L/bin/factory.d/worker-settings.json:27-28`), under which `guard bin/check` returns 0 without running (`L/bin/factory.d/lib.sh:24`; `L/docs/factory/LOOP.md:275`).
The supervisor then runs the frozen block outside the sandbox from the worktree root (`L/bin/factory:1945-1952`; `L/docs/factory/LOOP.md:240`), which is the one real `bin/check` per round; J: W35 round 2 printed `PASS check-green`.
After green checks: Rows measured, worktree reset, graders, mutation sweep (pytest on the diff's tests, outside the sandbox, in a detached worktree) (`L/bin/factory:2415-2462`, `:2680-2705`).
The Stop hook and `run_checks` execute worker-written code outside the sandbox (`L/docs/factory/LOOP.md:240`; `L/docs/factory/LESSONS.md:322`).
No memory cap or GPU lock wraps `run_checks` (no `ulimit`, `systemd-run`, `MemoryMax` or `gpu.lock` in `L/bin/factory`); DistBench's `bin/integrate --land` runs its gate as `flock <state>/gpu.lock bin/check` (`J: ~/distbench-isc/bin/integrate` docstring, `--land`).

## 6. Scheduling

`MAX_PARALLEL=1` by default, counted per target (`L/bin/factory:1063`; `L/docs/factory/LOOP.md:481`); `run` itself refuses past the cap (`L/bin/factory:1816`).
Each run holds an flock lease; a second launch of the same body exits 4 (`L/docs/factory/LOOP.md:313-316`). `next` runs under `flock -n next.lock` (`L/docs/factory/LOOP.md:21`, `:405`). The daily ledger is shared across targets (`L/docs/factory/LOOP.md:482`).
`next` launches only GitHub issues labelled `ready-for-agent`, unassigned, unblocked, written and last edited by SamyakJhaveri, after lint (`L/docs/factory/LOOP.md:21`, `:415-417`).
DistBench's ISC work does not use `next`: `~/.local/bin/factory-isc TICKET.md GROUP` (J) lints and runs one file ticket in `~/distbench-isc` (whose `origin/main` is fetched from `isc-build`: `+refs/heads/isc-build:refs/remotes/origin/main`, J), pushes the branch as `build/f-<id>` without force, and appends a `merge` row to the integration lane's `docs/tickets/integration.tsv` under `integrate.lock`; landing is `bin/integrate --land`, which merges rows, runs contract tests and the gated `bin/check`, then fast-forwards `isc-build` (J: `~/distbench-isc/bin/integrate`).
`bin/integrate` is not on DistBench `main` (`git -C D ls-files bin/integrate` prints nothing); `~/distbench-isc` HEAD is `a15f4305 integrate: build/u16-tooling @ 11da7142 (group 2, U16)` (J).
J crontab: the Loam `next` line and the overnight watchdog line are commented out "disabled 2026-11-04 (all agents off before DistBench work)".

## 7. Unattended operation

Factory: `next` on a ten-minute cron beats healthchecks, relaunches `stopped`, `stopped-daily` and (after an hour) `stopped-environment` runs, parks after three environment stops, and alerts after an idle hour (`L/docs/factory/LOOP.md:354-361`, `:396-414`); usage limits switch accounts or sleep to reset (`L/docs/factory/LOOP.md:104-111`); `holds_slot` reaps dead runs (`L/docs/factory/LOOP.md:322`).
Alerts go through `bin/alert` to the host log and Slack; `needs-you` covers `ticket-defect`, `abandon`, off-model calls, parks, idle, and another target's `pr-opened` (`L/docs/factory/LOOP.md:342-346`; `L/bin/factory:1260-1262`, `:1565`).
A watch session may only re-arm its monitor or `bin/factory stop` a looping run; everything else is Samyak's (`L/docs/factory/LOOP.md:373-377`).
Overnight: `driver.sh` polls Loam PRs every 60 s, runs one fresh call per PR, frees slots, launches `next`, writes a 07:00 morning report (`L/bin/overnight/driver.sh:178-193`); `watchdog.sh` restarts a dead driver once per 30 min and alerts on a call over 3 h (`L/bin/overnight/watchdog.sh:11-24`). A PR it leaves open gets a `needs-you` alert and an `outcome ... left open` line (`L/bin/overnight/protocol.md:31`, `:71`). There is no "NEEDS-SAMYAK" string in the factory; the owner channel is the `needs-you` alert level and `ready-for-human` issues.
`factory-isc` has no driver, watchdog or alert of its own (J: the script).

## 8. Self-improvement

Each judge backlog line and each blocking reviewer, Codex or mutation finding left at PR time is filed once as a `needs-triage` issue in the target repo (`L/bin/factory:2754-2770`, `:2880-2881`; `L/docs/factory/LOOP.md:81-82`). A file ticket skips this: `open_pr` exits `pr-opened` before push and filing (`L/bin/factory:2866`), and every DistBench ISC run is a file ticket (J: W35 `factory.log` "file ticket: no GitHub call").
`next` launches only `ready-for-agent`, so a filed `needs-triage` issue is never built until someone relabels it; the overnight call may not relabel to `ready-for-agent` (`L/bin/overnight/protocol.md:25`).
Overnight step 7, Loam only: a `LESSONS.md` section per PR, one dated "Lesson from #n" line appended to the Decisions of the next three ready tickets (re-linted only), and new `ready-for-human` tickets for lessons needing work (`L/bin/overnight/protocol.md:69`).
The manager writes one learn line when the same first-failing grader repeats (`L/docs/factory/LOOP.md:394`; `L/docs/factory/ARCHITECTURE.md:45`). `round-N.stale-paths` logs paths the ticket, `CLAUDE.md` or `AGENTS.md` name that a Read found gone; it informs only (`L/bin/factory:2388-2393`).
Ticket review before build: lint at `next` and `lint`; `plan-reviewer` and lean-critic by hand over a breakdown (`L/docs/factory/CONTRACT.md:116-118`; `L/docs/factory/ARCHITECTURE.md:41`). No automatic review of auto-filed or lesson-edited tickets.

## 9. Run folder outputs

Root: `~/.local/state/loam-factory/runs/SamyakJhaveri__distbench/<key>/<sha8>/` (`L/docs/factory/LOOP.md:45`). J listing of W35-tooling/65a16a39:
`status`, `factory.log` (EXIT line, `mutation sweep:` line, notify lines), `ledger.jsonl` (per call: role, model, served_models, cost, advisor), `base.sha`, `started`, `launched`, `lease`, `owner`, `env-stops`, `pr-body.md`;
`frozen/` (`issue.md`, `checks.sh`, `_common.md`, `unattended.md`, `worker-settings.json`, `role-settings.json`, `judge.md`, `reviewer.md`, schemas, `protected.txt`, `exempt.txt`, `factory`, `lib.sh`, `mutation_sweep.py`, `sha256`);
per round: `round-0.checks`, `round-N.prompt.md`, `.jsonl` (worker stream-json with hook events), `.result.json`, `.checks`, `.measure`, `.diff`, `.fixes`, `.graded.sha`, `.judge.json`, `.judge.prompt.md`, `.judge.raw.K.json`, `.review.json`, `.review.prompt.md`, `.review.raw.K.json`, `.mutation.json`, `.stale-paths`; `worker/decisions.md` and `worker/mechanism.md`; `tasks/` (fan-out `result.json`); also, when they apply, `round-N.codex-review.json`, `publish.intent`, `filed.txt`, `owner-events.jsonl`, `pr-closed`, `notify.failed`, `FACTORY_STOP` (`L/docs/factory/LOOP.md:41-43`).
A checker can read the worker's last `CLAIM:` line from `.result` of `round-N.result.json` (`L/docs/factory/ARCHITECTURE.md:123`, `:126`) and `SKIPPED:` lines `guard` copies into `round-N.checks` (`L/bin/factory.d/lib.sh:18-20`).

## Blockers

| blocker | confirmed/refuted | file:line | note |
|---|---|---|---|
| (1) worker runs `--setting-sources ''` with Loam's settings, so DistBench settings, CLAUDE.md, rules, skills do not reach it | confirmed | `L/bin/factory:2350`; `L/docs/factory/LOOP.md:239`, `:305`; `L/bin/factory:1451-1467` | The runner's user-tier keys (plugins, env, likely hooks) do reach it through the frozen merge; DistBench's `.claude/settings.json`, project skills (`verify-distbench`), `CLAUDE.md`, `AGENTS.md` and `~/.claude/{CLAUDE.md,rules}` do not. `skills.txt` is empty, so only `pstack:` skills can be named. |
| (2) sandbox refuses AF_UNIX; DistBench `bin/check` exits 1 in any sandbox | confirmed | `L/bin/factory.d/worker-settings.json:22-25`; `L/docs/factory/LESSONS.md:637`; `D/bin/check:10-27` | Applies to the worker's own Bash. The supervisor's `run_checks`, the Stop hook and the mutation sweep run outside the sandbox (`L/docs/factory/LOOP.md:240`), so the round gate does run `bin/check` (J: W35 round 2 `PASS check-green`). |
| (3) Stop hook passes `guard bin/check` unrun | confirmed | `L/bin/factory.d/lib.sh:24`; `L/bin/factory.d/worker-settings.json:28`; `L/docs/factory/ARCHITECTURE.md:125`; `L/docs/factory/LOOP.md:275` | DistBench tickets add their own `[ -n "${LOAM_HOOK:-}" ] \|\|` pass (J: W35 `frozen/checks.sh:67`). The worker learns of a red gate only in the next round's prompt. |
| (4) overnight review panel never reviews DistBench | confirmed | `L/bin/overnight/protocol.md:24`; `L/bin/overnight/settings.json:11-12`; `L/bin/overnight/driver.sh:92-94` | Moot for ISC work in another way too: ISC runs are file tickets that open no PR (`L/bin/factory:2866`), and the driver and watchdog cron lines are disabled since 4 Nov (J crontab). |

Risks: user-tier hooks reaching the worker and Codex reading the worktree `AGENTS.md` are read from code, not run. The router-read evidence covers four runs only.
