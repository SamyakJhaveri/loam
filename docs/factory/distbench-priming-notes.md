# Distbench priming: notes for the session that continues

Written 2026-11-12 by the Mac coordinator agent, cut short when the Mac session closed.
A fresh session on jhaveris (tmux factory-prime) continues from this branch.
The raw evidence is in `docs/factory/distbench-priming/` beside this file (copied from the Mac folder `~/.local/state/distbench/evidence/2026-11-12-factory/`).

## Goal

Make Loam's factory build distbench tickets the way Samyak's attended sessions worked 8-11 Nov 2026, unattended, and able to improve itself.
The full goal, Samyak's words, items (a)-(h) and the fences are in `distbench-priming/design-goal.md`.

## Done checks (written before building)

1. A parity check script prints FAIL on runs W24 and W35 and names the failing behaviours (router not read among them).
2. A factory run on jhaveris of one real distbench ticket that needs the full gate: the worker runs `bin/check` inside its round and gets `check: PASSED` or a real failure, not the sandbox refusal; the parity check PASSes on it.
   Start it only when no `f-*` tmux session is live and the build lead is not waiting on locks.
   Use a separate Loam checkout (for example `~/.local/state/loam/worktrees/factory-distbench-test` from this branch), a separate runs folder (`FACTORY_RUNS_ROOT`) and a separate distbench clone; never modify `~/loam`, `~/distbench` or `~/distbench-isc` on jhaveris tonight.
   If that cannot run, use a synthetic distbench-shaped repo and mark the real-target proof unverified.
3. The factory files one self-improvement ticket from a failure in that run, reviewed by Fable and Codex.
4. Loam's and distbench's tests pass on the branches.

## Step 1, the inventory (done)

Four read-only scouts wrote the checklist, one file per source:

- `distbench-priming/inventory-distbench.tsv`: 50 behaviours (D01-D50) from distbench main and origin/redesign-1030, with file:line.
- `distbench-priming/inventory-global.tsv`: 55 behaviours (G01-G55) from `~/.claude/CLAUDE.md`, rules, agents, memory files and the sam-cc-setup skills, with a `factory_sees` column.
- `distbench-priming/inventory-jhaveris.tsv`: 24 facts (J01-J24) on how tonight's unattended lead runs (loop, hand-off, locks, settings).
- `distbench-priming/runs-w24-w34-w35.md`: the three finished runs round by round, with the repeatable jq that detects a router read.

Columns: id, class, behaviour, source, observable (what a run folder or transcript shows when the behaviour happened).

## Step 2, the gap (draft)

All four known blockers are confirmed against code (`distbench-priming/factory-today.md`, blocker table at the end):

1. The worker runs with `--setting-sources ''` (`bin/factory:2350`), so distbench's settings, CLAUDE.md, AGENTS.md, project skills and `~/.claude/{CLAUDE.md,rules,agents}` never reach it (`docs/factory/LOOP.md:239,243`); user-scope plugins do.
2. The worker sandbox refuses AF_UNIX (`bin/factory.d/worker-settings.json:22-25`, `docs/factory/LESSONS.md:637`), and distbench `bin/check:10-27` exits 1 in any sandbox. In W24, W34 and W35 every in-round `bin/check` hit the refusal or the 10-minute tool limit.
3. The Stop hook passes `guard bin/check` unrun when `LOAM_HOOK` is set (`bin/lib.sh:24`).
4. The overnight panel never reviews distbench (`bin/overnight/protocol.md:24`, `bin/overnight/settings.json:11-12`); file tickets open no PR (`bin/factory:2866`).

Router reads: W24 top-level 0 of 2 rounds (its 3 workflow builders read it in round 1), W34 1 of 2 (first 60 lines), W35 0 of 2.

Draft map of the checklist:

- Carried: fail-first round 0; `check-green` needs `check: PASSED` (supervisor, outside the sandbox); integrate by script through `factory-isc` and `bin/integrate --land`; 3 runs at once (`FACTORY_MAX_PARALLEL=3`); gate, gpu and mpi locks taken inside distbench's own `bin/check` and `conftest.py` (J17-J19), so any caller of the gate is bounded the same way; 450K compaction (`LOOP.md:241`); Codex review when the ticket says `codex-review: yes`; the judge's honesty row.
- Missing: any check that the router and the chosen pstack SKILL.md were read; distbench project skills (verify-distbench, formal-orchestrator); the global how-to-work rules (G01-G12); Fable 5.2 blind review plus an Opus verifier that reproduces each finding; audit and surprise-me at the points `distbench docs/WORKERS.md:23-29` names; the gate inside the worker's round; self-improvement tickets from failures and reviews (file tickets file no follow-ups, `bin/factory:2866,2880`); a wake-up loop, hand-off and NEEDS-SAMYAK path for factory runs (the lead has them; the factory's driver and watchdog cron lines are off since 4 Nov).
- Stale copies (the /correct class, hand-synced text): `bin/factory.d/_common.md:13` says Explore where Samyak's rule says scout; `_common.md:8` says to carry every done check into tests against `~/.claude/CLAUDE.md:32-33`; `bin/factory.d/factory-round.js:213` runs builders at xhigh against worker high; `bin/factory:2071-2074` always reads the pstack adapter, the router says only when the skill asks; Fable 5.1 in `docs/factory/ARCHITECTURE.md:83,86`, `bin/overnight/protocol.md:26` and `cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md:6`; surprise-me cadence in `protocol.md:64`; the router line in `_common.md:14` copies the global CLAUDE.md.

Contradictions inside distbench's own sources (for the review session, not edited here): who runs the gate (`SESSION-PROTOCOL.md:76,96` against `implementation-plan.md:179,192`), lock names (`WORKERS.md:9` against `implementation-plan.md:195`), when Codex runs (`AGENTS.md:11` against `SESSION-PROTOCOL.md:50`), the removed mattpocock skill still named at `SESSION-PROTOCOL.md:40` and `docs/agents/triage-labels.md:5`.

## Step 3, the design (in progress when cut)

Two designers with the same goal and different briefs were running:

- Design A (Opus xhigh): make the worker a distbench session by loading distbench's project tier and Samyak's user tier from the files themselves, the way the attended jhaveris lead runs (user, project and local tiers, sandbox off in `settings.local.json`, auto mode; J09-J12); the factory adds only judge, reviews, gates, scheduling and evidence; delete Loam's copies.
- Design B (Fable high): first principles; "the way we work" is a contract the factory proves from run evidence; keep isolation only where it buys safety; load instructions from their one source or a view generated at run start.

Their files, if they finished, are `distbench-priming/design-A.md` and `design-B.md`. No design has been picked; the next session picks one and logs why.

Points for the pick, from the evidence:

- Sandbox. W34's in-round failures included namespace denials as well as AF_UNIX, so sandbox settings alone (allowLocalBinding, unix sockets) may not let the full gate run; running the worker unsandboxed matches the attended lead and Samyak's ruling. What that gives up: write confinement to the worktree, Bash reads of credentials (`~/.claude/.credentials.json`, `~/.codex/auth.json`, gh token, ssh keys) since permission deny rules cover the Read tool only, and the network allowlist (a worker could push or call paid APIs). What still guards: the git worktree per run, permission deny rules on tools and Bash patterns, the supervisor's own unsandboxed gate, the judge and reviews, and `factory-isc` pushing only `build/f-*`.
- Gate load. Each round already runs the full gate once in the supervisor (about 1 h, holding a gate slot; J21). A worker gate in the round doubles that unless the design shares or bounds it; the gate slots in distbench's `bin/check` bound concurrency either way.

## Step 4, the lever (in progress when cut)

A worker was building `bin/factory-parity` (stdlib Python, PASS/FAIL/N/A per behaviour, last line `parity: PASS|FAIL (<ids>)`) with tests in `bin/tests/test_factory_parity.py`, on branch `fix/factory-parity`.
First-unit behaviours: P1 project skills loaded (init event lists verify-distbench), P2 router read before the first edit in every editing transcript, P3 a pstack SKILL.md read after the router and every method named in the decision log has a matching read, P4 `bin/check` run in the round with `check: PASSED` or a real failure and no sandbox refusal, P5 Opus 5.5 high everywhere and no haiku or max, P6 verify-distbench read and run when the diff touches its paths.
Second unit after the design pick: review route (Fable, Codex, verifier), self-improvement tickets, owner escalation.
The three runs were being copied read-only to the Mac evidence folder `runs/` for the baseline.

## Requests for the build lead and the review session

- Build lead: the W27 orphan scope holds `mpi-0.lock` and blocked landings from about 05:19Z (its own report); Samyak must clear it.
- Review session: the four distbench contradictions above.

## Decision log

`distbench-priming/decisions.tsv` (show-me-your-work format), one row per decision so far.
