# How DistBench runs and builds research, 2026-10

Study for unit U18, part 18.1.
It records what DistBench already does, so that each research-lane item in `docs/BACKLOG.md` (items 1-6) can be judged against it in 18.2.
DistBench was read at origin/main `fda685334f00f725f76d360614ebc8d9336a7c54` on 2026-10-27, only through `git show fda68533:<path>`, never a local branch or the working tree.
Three read-only scouts on Opus 5.5 read the four areas; the lead printed a sample of 30 cited lines and every one matched.
Every citation is `distbench@fda68533:<path>:<line>`.

## 1. Experiment runner: how a run launches and stops

### Launch

The runner is one HTTP job queue for all sessions, started with `python -m distbench.runner serve --config <file>` (`distbench@fda68533:src/distbench/runner.py:1-6`).
With `executor: local` it makes two local node copies; any other executor builds ssh nodes for the rented pair and prepares a job user on each (`distbench@fda68533:src/distbench/runner.py:4479-4490`).
Each job takes `pair-busy.lock` first, so grades, timings, canaries and noise runs never overlap (`distbench@fda68533:src/distbench/runner.py:4340-4351`).
`bin/pair-runner` wraps `serve`, passes SIGHUP, SIGINT and SIGTERM through, and on exit sends "PAIR RUNNER EXITED <code>" to the alert command, up to 30 tries (`distbench@fda68533:bin/pair-runner:2-11`).
The orchestrator plans and runs agent sessions from a matrix config with a backend, a seed and a ledger (`distbench@fda68533:src/distbench/orchestrator.py:1-7`).
Each session is one docker container running the Pi agent through `agent/launch.sh` (`distbench@fda68533:src/distbench/orchestrator.py:1375-1383`, `distbench@fda68533:agent/launch.sh:2-4`).
The orchestrator refuses to run without a frozen PREREG line in the ledger, and refuses capped arms without a `prereg-caps` line (`distbench@fda68533:src/distbench/orchestrator.py:1685-1694`).
The rented pair is created and torn down by `hyperstack.sh` (`distbench@fda68533:experiments/F03-node-scripts/hyperstack.sh:2-8`).
Its window mode starts tmux sessions for `pair-runner` and `pair-ping`, waits for a ping HTTP 200, and holds the pair until the block plan is done (`distbench@fda68533:experiments/F22-live-pair-checks/smoke/smoke.sh:78-86`).
Writes are crash-safe: atomic replace and fsynced one-line appends (`distbench@fda68533:src/distbench/durable.py:1-2`).

### Stop

A block-plan command that reaches its deadline gets SIGTERM, then SIGKILL after a grace (`distbench@fda68533:src/distbench/runner.py:5048-5054`).
A session's wall-clock limit is session time minus queue waits (`distbench@fda68533:src/distbench/orchestrator.py:1558-1566`); at the limit Pi gets `docker kill --signal TERM` (`distbench@fda68533:src/distbench/orchestrator.py:1576`), and removal is `docker pause` then `rm -f` (`distbench@fda68533:src/distbench/orchestrator.py:1244-1247`).
PREREG fixes the session at 4 hours and names the stop reasons: submit, no_submit, wall_clock, context_limit, cap and error (`distbench@fda68533:docs/research/2026-10-12-fresh-design/PREREG.md:78-85`).
F16 proved the SIGTERM path and that pause-before-remove keeps an in-flight write whole (`distbench@fda68533:experiments/F16-wallclock-stop/wallclock_stop.py:1-3`, `distbench@fda68533:experiments/F16-wallclock-stop/pause_trial.sh:2-7`).
Turn caps per model come from the matrix (`distbench@fda68533:src/distbench/orchestrator.py:287-298`) and reach the agent as `DISTBENCH_ARM_CAP` (`distbench@fda68533:agent/extension/index.ts:73`).
An idle watchdog rewrites `pair-status.json` each poll and raises idle, done or unlogged alerts, but never acts on the pair (`distbench@fda68533:src/distbench/runner.py:4381-4388`).
`bin/pair-alert` posts to a Slack webhook (`distbench@fda68533:bin/pair-alert:2-7`); Slack replaced Pushover when its free trial ended (`distbench@fda68533:docs/design/APPROVALS.md:576`).
`bin/pair-ping` pings healthchecks.io as a dead man's switch while the status file is fresh (`distbench@fda68533:bin/pair-ping:2-12`).
Before every step the pair driver checks the stop file, the deadline, the spend cap and a balance reserve, and teardown proves the nodes are gone (`distbench@fda68533:experiments/F03-node-scripts/hyperstack.sh:22-31`).
`budget.py` has lease admission (`distbench@fda68533:src/distbench/budget.py:112-140`), but nothing in `src/` or `bin/` imports it; the $500 pool no longer bounds the plan (`distbench@fda68533:docs/research/2026-10-12-fresh-design/PLAN.md:501-502`).

### Preregistration

One study-wide `PREREG.md` is frozen by commit SHA and file SHA-256 in `experiments/run-ledger.jsonl` (`distbench@fda68533:docs/research/2026-10-12-fresh-design/PREREG.md:7-10`).
`bin/check_prereg.py` enforces the freeze (`distbench@fda68533:bin/check_prereg.py:2`), and `bin/check` runs it (`distbench@fda68533:bin/check:160`).
The seed is fixed at 20261013 (`distbench@fda68533:docs/research/2026-10-12-fresh-design/PREREG.md:269`).

## 2. Grader: how a result is judged

The grader turns one frozen submission or turn snapshot into one run record; it is trusted code, and candidate code runs only as child processes in throwaway node copies (`distbench@fda68533:src/distbench/grader.py:1-4`).
It exits 0 when grading finished, 3 on a grader error with no record, and 4 on a cleaning error (`distbench@fda68533:src/distbench/grader.py:62-75`).
A result climbs four levels: build, run, correct and distributed (`distbench@fda68533:src/distbench/grader.py:85-89`).
Distributed means each node got at least half its fair share of CPU, network bytes and GPU time (`distbench@fda68533:src/distbench/grader.py:122-128`).
The oracle verdict is the last JSON `correct` line plus exit 0 (`distbench@fda68533:src/distbench/grader.py:697-709`).
Expected outputs come from `make_expected.py` (`distbench@fda68533:src/distbench/expected.py:1-27`), and the oracle guard requires the oracle to reject less-work, relabelled, extrapolated and replayed outputs (`distbench@fda68533:.agents/skills/verify-distbench/features/oracle-guard.md:3-5`).
Grader controls: a broken variant must grade `correct=False` and an idle-rank variant `distributed=False` (`distbench@fda68533:.agents/skills/verify-distbench/features/grader.md:55-56`).
`rejudge` re-runs `correct` offline from content-addressed oracle inputs after a sha256 check (`distbench@fda68533:src/distbench/rejudge.py:1-8`), but has not been run on live data (`distbench@fda68533:.agents/skills/verify-distbench/features/rejudge.md:6`).
`regrade.jsonl` is the queue for grader exit 3 (`distbench@fda68533:docs/tickets/F18-unlimited-wave.md:39`), and `metrics.py` counts only the last grade and keeps unknown as unknown (`distbench@fda68533:src/distbench/metrics.py:1-8`).
`invariance.py` checks that every model in a cell got the same prompt, tools, thinking level and task hash (`distbench@fda68533:src/distbench/invariance.py:1-7`).

## 3. Records: where results, decisions and handoffs live

### Results

`experiments/` holds one folder per run or ticket, and pre-12-October work is read-only under `archive/discovery-v1/` (`distbench@fda68533:experiments/README.md:3-4`).
The shared run ledger `experiments/run-ledger.jsonl` holds one JSON object per line with an `event` key; session lines carry model, arm, stop reason, PREREG SHA and orchestrator commit (`distbench@fda68533:experiments/run-ledger.jsonl:1-2`).
Graded records go in per-wave `runs.jsonl`, one per session (`distbench@fda68533:docs/tickets/F18-unlimited-wave.md:37`).
`ledger.py` defines a separate append-only assignment, session and attempt ledger with one writer, the supervisor (`distbench@fda68533:src/distbench/ledger.py:1-5`).
`records.py` holds the immutable `RunRecord` with SHA-256 bindings (`distbench@fda68533:src/distbench/records.py:40-73`).
Results from the rented host are copied into the repo by hand at two points of a wave (`distbench@fda68533:experiments/F18-unlimited-wave/go.md:138`).
Bulk outputs stay out of git in recovery-snapshot tarballs (`distbench@fda68533:.gitignore:69-70`).

### Decisions

`docs/design/DECISIONS.md` is a table of Id, Decision, Status, Current choice, and Reason and evidence (`distbench@fda68533:docs/design/DECISIONS.md:9`).
`docs/design/APPROVALS.md` holds Samyak's own words, authorizations and closed rulings (`distbench@fda68533:docs/design/ORIENTATION.md:18`), in 2611 lines of dated blocks (`distbench@fda68533:docs/design/APPROVALS.md:2600`).
DistBench forbids a `CONTEXT.md`, a `docs/adr/` or a second decision log; a decision is a DECISIONS row with its approval in APPROVALS (`distbench@fda68533:docs/agents/domain.md:4`, `distbench@fda68533:docs/agents/domain.md:16`).
`.loam/sync-rulings.md` keeps one line per template-sync call (`distbench@fda68533:.loam/sync-rulings.md:3`).

### Handoffs and session state

`docs/design/SESSION-STATE.md` owns the next action in its first paragraph (`distbench@fda68533:docs/design/SESSION-STATE.md:4`); that paragraph is dated 20 October (`distbench@fda68533:docs/design/SESSION-STATE.md:7`), older than the 25 October APPROVALS blocks.
`docs/design/ORIENTATION.md` is the entry point with a where-things-live table (`distbench@fda68533:docs/design/ORIENTATION.md:7-24`).
The mid-task handoff is a gitignored root `HANDOFF.md` with seven headings, defined in on-demand `docs/WORKERS.md` (`distbench@fda68533:docs/WORKERS.md:46-64`).
`/catchup` reads the handoff and calls it stale when its hash is no longer HEAD (`distbench@fda68533:.agents/skills/catchup/SKILL.md:19-20`).
Session reports go to `docs/tickets/reports/` from a template that labels each claim Verified or Assumption (`distbench@fda68533:docs/tickets/reports/TEMPLATE.md:26`).
`bin/check_tickets.py` enforces both ticket formats (`distbench@fda68533:bin/check_tickets.py:7-48`).

## 4. Paper and figure pipeline: how numbers become tables, figures and text

`distbench.metrics` computes the PLAN section 4 metrics per arm and model (`distbench@fda68533:src/distbench/metrics.py:1-8`).
`distbench.analysis` reads run records and telemetry and writes `analysis.json`, `tables.md`, `pareto.svg` and first-passage SVGs (`distbench@fda68533:src/distbench/analysis.py:1-13`), with a sign-flip test and a seeded bootstrap in the standard library only (`distbench@fda68533:src/distbench/analysis.py:15-18`).
matplotlib is avoided on purpose (`distbench@fda68533:docs/tickets/F21-analysis-and-figures.md:57-58`).
`distbench.research` writes the per-research-question `research.json` and `research.md` and reuses the analysis table code (`distbench@fda68533:src/distbench/research.py:23-26`, `distbench@fda68533:src/distbench/research.py:37-38`).
Both are proven only against frozen synthetic fixtures (`distbench@fda68533:docs/tickets/F21-analysis-and-figures.md:63-67`); both feature files say "Not run" on live data (`distbench@fda68533:.agents/skills/verify-distbench/features/analysis.md:6`, `distbench@fda68533:.agents/skills/verify-distbench/features/research.md:6`).
The one figure verifier, `check_outputs.py`, checks that every cell appears in `tables.md` and as an SVG title and that each SVG parses, and runs only as an F21 done-check (`distbench@fda68533:docs/tickets/checks/F21/check_outputs.py:6-8`).
There is no paper draft: `paper/` is empty, and `papers/` holds related-work PDFs (`distbench@fda68533:docs/tickets/F47-paper-placeholders.md:18`).
Ticket F47 plans `paper/main.tex` with `bin/paper_values.py` writing `\dbvalue{key}{value}` from the two JSON outputs and `[pending]` for a missing value (`distbench@fda68533:docs/tickets/F47-paper-placeholders.md:5`), so that no number is typed by hand (`distbench@fda68533:docs/tickets/F47-paper-placeholders.md:14`); it is `ready-for-agent`, not built (`distbench@fda68533:docs/tickets/F47-paper-placeholders.md:3`).
Today the one figure script with prose holds hand-typed data arrays (`distbench@fda68533:docs/research/2026-10-12-serial-to-cluster/make_figures.py:626-628`) and splices SVG into an HTML report (`distbench@fda68533:docs/research/2026-10-12-serial-to-cluster/make_figures.py:3-5`).
No citation check exists: a grep for bibtex, `.bib` and citation checks across `src`, `bin`, `docs`, `tests` and `.agents` found nothing.

## 5. The six BACKLOG items against DistBench practice

1. Research-lane bundle: none found for the vendored skills or paper verifiers (DistBench's skills are catchup, fable-prompting, factory-watch, formal-orchestrator, hypothesis-tree, verify-distbench); the run folder and `run.json` already exist (`distbench@fda68533:.agents/skills/verify-distbench/SKILL.md:79`), the figure verifier exists in part (`distbench@fda68533:docs/tickets/checks/F21/check_outputs.py:6-8`), and no-hand-typed-numbers is planned in F47 (`distbench@fda68533:docs/tickets/F47-paper-placeholders.md:14`); note that `cultivation/parked/research-lane/` holds only `research-assets/` (a results-protection hook, two rules, six seed-doc templates), not the skills, `run.json` or verifiers the item names.
2. Experiment contract: partly done by the study-wide frozen PREREG with its ledger hash and `bin/check_prereg.py` for question, seeds and protocol hash (`distbench@fda68533:docs/research/2026-10-12-fresh-design/PREREG.md:7-10`), by each ticket's done-checks block run by `bin/done-checks` for done-when (`distbench@fda68533:bin/done-checks:2-9`), and by `experiments/budget.json` for budget (`distbench@fda68533:experiments/budget.json:1-11`); no per-experiment `CONTRACT.md` was found (searched the tree for CONTRACT; only interface `CONTRACTS.md` files match).
3. Headless conveyor: done with a different agent and alert channel: the orchestrator runs Pi in docker in a tmux session on the eval host (`distbench@fda68533:experiments/F18-unlimited-wave/go.md:113`), alerts go to Slack plus a healthchecks.io dead man (`distbench@fda68533:bin/pair-alert:2-7`, `distbench@fda68533:bin/pair-ping:2-12`), and results sync back by hand (`distbench@fda68533:experiments/F18-unlimited-wave/go.md:138`); no `claude -p` conveyor found (grep of `bin`, `src`, `agent`, `docs/factory`, `experiments/F22-live-pair-checks`).
4. Ideation chain: none found as a skill; it was done by hand: three independent reports from one brief merged with a support count per question (`distbench@fda68533:docs/research/2026-10-15-reorient/notes/rq-merged.md:4`), a competitor check that read three papers in full (`distbench@fda68533:docs/research/2026-10-15-reorient/notes/competitors.md:3`), and PLAN section 1 fixing the claim and questions (`distbench@fda68533:docs/research/2026-10-12-fresh-design/PLAN.md:37`); retrieval was not mandatory, and `hypothesis-tree` tracks debugging hypotheses, not ideas (`distbench@fda68533:.agents/skills/hypothesis-tree/SKILL.md:10`).
5. Reading room: none found for a `read` skill, a `RESOURCES.md` or an `adopt-skill`; readings live in per-study `notes/` folders whose `BRIEF.md` sets Verified/Inferred labels (`distbench@fda68533:docs/research/2026-10-12-feedback-signals/notes/BRIEF.md:16-17`), `papers/` has 31 PDFs and no index, and the second-repetition rule exists for checks, not skills (`distbench@fda68533:docs/WORKERS.md:74-76`).
6. Decision ledger and handoff prose: done: APPROVALS keeps closed rulings and DECISIONS keeps choices (`distbench@fda68533:docs/agents/domain.md:16`), and on-demand `docs/WORKERS.md` already has the seven-field handoff (`distbench@fda68533:docs/WORKERS.md:46-64`) and worktree isolation (`distbench@fda68533:docs/WORKERS.md:7-10`); loop and inline-mermaid guidance were not found in WORKERS (the only mermaid mention is `distbench@fda68533:docs/tickets/reports/TEMPLATE.md:15`), and APPROVALS is 2611 lines loaded from ORIENTATION's read table, so it is not a lean on-demand ledger.

## Gaps in this study

The scouts read the docstrings and key functions of `runner.py`, `orchestrator.py`, `grader.py`, `hyperstack.sh` and `smoke.sh`, not every line.
The PDFs in `papers/` were listed, not read.
Files that `rq-merged.md` names (`rq-brief.md`, `paper-gaps.md`, `proof/verify2.py`, `rulings.md`) are not in the tree at fda68533.
The analysis feature file cites `analysis.py:644-665` for where outputs are written; that code is now at lines 731-753, so that DistBench citation is stale.
