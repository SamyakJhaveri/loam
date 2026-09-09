# Ten agent-loop repositories, read from source

All ten repositories were fetched at `main` HEAD on 2026-09-08.
Every quote below comes from a file downloaded via `curl` against `raw.githubusercontent.com`, not from a summary.

Method note.
WebFetch's summarizer refused to return `AMAP-ML/LongHorizon-Harness` verbatim and paraphrased four other READMEs rather than quoting them.
I switched to direct `curl` plus the GitHub trees API for file discovery.
Three files hit a truncated read on first attempt (`unlazy/SKILL.md`, `autoprompt/agents/claude/SKILL.md`, `autoprompt-gate.js`) and succeeded on retry.

---

## 1. cobusgreyling/loop-engineering

**a. Loop shape.**
A scheduler (GitHub Actions cron, or the agent's own scheduler) invokes a CLI agent with a pattern's skills.
Between calls, deterministic scripts run: `scripts/github-triage.mjs` writes `STATE.md` from open PRs and issues, `loop-gate check` reads `gate.yaml`, the budget skill checks spend.
It never converges; it repeats on cadence.
Per item it stops at 3 attempts and escalates.
Global stops are the `loop-pause-all` label and the 80%-of-daily-cap switch to report-only.

**b. What verifies.**
A separate `loop-verifier` skill, plus a deterministic path gate.
The verifier runs tests itself and defaults to REJECT.
`loop-gate` exits 2 to escalate, 0 to proceed, matching the `loop-context --check` convention.
The human writes `gate.yaml` and `loop-constraints.md` before the run; the verifier skill ships with the repo.

**c. Size and state.**
No single loop script.
The thin-loop workflow is 87 lines, `gate.yaml` is 26 lines, the verifier skill is 48 lines.
State files: `STATE.md`, `LOOP.md`, `loop-budget.md`, `loop-run-log.md`, `loop-constraints.md`, `loop-ledger.json`.

**d. Simplicity and anti-over-checking quotes.**
From the README:

- "This is a **pattern library for operating agents around a codebase**. It is not a "rewrite the module" button."
- "Week one is **report-only**."
- "Companions exist for later: ... Do not add them until a loop has actually run."
- "Loop engineering amplifies judgment. Token costs can explode. Unattended loops make unattended mistakes. Read what the loop ships."

**e. Separate-verifier and frozen-gate quotes.**

- README: "Roll out **L1 report → L2 assisted → L3 unattended** only after the verifier has been right for a week."
- README: "Loop Ready now **weights recent runs harder than files on disk**. A 30-day-old `STATE.md` is not L3."
- `docs/loop-design-checklist.md`: "**Implementer** and **verifier** are separate (agent, model, or instructions)"
- `docs/loop-design-checklist.md`: "Implementer **cannot** mark its own work "done""
- `docs/loop-design-checklist.md`: "Verifier runs **tests** in isolation (worktree) before approving"
- `docs/loop-design-checklist.md`: "`/goal` or equivalent uses a **fresh model** for stop condition (if applicable)"
- Red flag list: "Verifier is the same agent session as implementer"
- `skills/loop-verifier/SKILL.md`: "Do not trust implementer's claim that tests passed — run them."
- `skills/loop-verifier/SKILL.md`: "Default stance: REJECT until proven otherwise."

**f. Wrong or gamed check.**
The verifier checklist has an explicit no-cheating item: "No disabled tests, skipped assertions, or commented-out checks."
Anti-pattern 8 forbids fixing flakes with code, requiring classify then quarantine.
Safety says "Do not disable tests to make CI green" and "Do not increase timeouts blindly without root-cause note."
Incident response is "Tighten verifier or shrink scope before restart."
`loop-swarm` requires byte-identical patch consensus across separate sandboxed runs before accepting edits.

**g. Numbers.**
8 patterns with cadence and cost bands.
3 attempts per item.
Human gate above 10 changed files.
80% budget threshold.
48-hour first response on PRs.

---

## 2. disler/super-simple-software-factory

**a. Loop shape.**
A Python ADW script owns sequencing.
`run.phase(PhaseParams(name, kind, owner, description))` is the one primitive, used for three kinds: `engineer` (human), `agent` (`ph.call(AgentCall(output_type=..., gates=[...]))`), and `code` (a deterministic step like commit or test).
Agents return a typed JSON envelope.
Between calls, code parses the envelope, runs gates, persists `envelope.json`, and injects it into the next prompt.
The run ends at `run.finish(accepted=...)`, which sets the session status and exit code together.
Retries do not restart: a parse failure or gate violation re-prompts the same live session as a correction.

**b. What verifies.**
Gates, which are Python callables checking the envelope's own declarations after the fact: `artifacts_exist`, `files_non_empty`, `json_parses`, `diff_matches_claims`, `verdict_consistent`, and `tests_pass(command)` which shells out and requires exit 0.
Separately, `permissions.py` diffs the repo before and after every agent call and rolls back unauthorized writes.
A `reviewer` agent covers taste.
The human writes the real commands into `quality.py` and the gate functions into `gates.py`; no model authors its own gate.

**c. Size and state.**
ADW scripts run 1.7KB to 10KB, described in the README as "40 to 180 lines on purpose".
`runner.py` is 143 lines, `gates.py` is 109.
State: a WAL SQLite trace database with seven tables (`sessions`, `phases`, `events`, `envelopes`, `gate_results`, `agent_sessions`, `processes`), plus `envelope.json`, `raw_output.jsonl`, `agent_map.json`, and `context_handoff/` per session.

**d. Simplicity quotes.**

- "**Is this overkill for a one-off feature?** Yes. Prompt an agent and move on."
- "### Agents are great. You do not always need one."
- "So when the invocation is already known, write it down. `bun test` is not a judgement call. Neither is `ruff check`."
- "An agent rediscovering your test runner burns a context window to learn what a subprocess already knows, and it charges you for the privilege every single run. Worse, it puts a passing test suite into a context window, which buys you nothing at all."
- "There is no DSL here. No framework to learn."
- "They are left out so the core stays small enough to read in one sitting, which is the only reason you would trust it enough to change it."

**e. Separate-verifier and deterministic-gate quotes.**

- "Deterministic Python owns the graph. Coding agents are bounded nodes inside it."
- "code owns sequencing, retries, and acceptance, and the agent owns only the work inside one bounded phase"
- "Gates verify claims, never predictions."
- "**Success must be earned.** Every phase defaults to `fail`."
- "Give the reviewer no ability to write code at all."
- "so "this agent changes nothing" is enforced in code, after every call, by comparing the repo before and after."
- "Determinism is wired into every step. Agents must return a specific structure, every time."

**f. Wrong or gamed check.**
The README's failure table names it directly: "The test phase reports green on a fresh install ... `quality.py` ships placeholder commands that exit 0 ... Until you wire this, your test phase is theater."
And "Gates pass, output is bad | Gates check what a predicate can check, not plan quality or code taste | Run the `reviewer`, or read it yourself."
The `verdict_consistent` gate refutes a reviewer that approves while listing blocking items, without reading the diff.

**g. Numbers.**
No success rates.
Twelve starter workflows.
Five starter agents.
The payoff framing is "run one hundred and run one thousand, not on run one."

---

## 3. Leonxlnx/unlazy

**a. Loop shape.**
Not an outer process loop.
It is a skill plus a Node checker.
The agent writes `GATES.md` before implementing, works the leaf in four passes, then runs `gate-check.mjs`.
An optional Claude Code Stop hook blocks session exit while gates are unmet.
The hook's own progress guard releases after six consecutive blocks with no semantic progress, so it cannot wedge.
In orchestrated mode a driver fans out leaves in launch waves and re-verifies each returned leaf.

**b. What verifies.**
`gate-check.mjs` executes the declared `CHECK:` shell command.
A gate passes only when the process exits 0 and `EXPECT:` matches combined output, and its evidence carries the current SHA-256 digest of the parsed `CHECK:`, `EXPECT:`, and raw `CWD:`.
The agent writes the gates before doing the work.
The human must approve each exact command with `--approve` before it can ever execute.
The parent re-runs returned leaves with `--reverify`.

**c. Size and state.**
`scripts/gate-check.mjs` is 960 lines, `scripts/lib/gates.mjs` is 953.
Also `dispatch-check.mjs`, `gate-lint.mjs`, `install-hooks.mjs`, `stop-hook.mjs`, `lib/check-supervisor.mjs`, `lib/dispatch.mjs`, `lib/process-tree.mjs`, `lib/regex-worker.mjs`.
State: `GATES.md`, `.unlazy/<scope>/PLAN.md`, `gates/leaf-*.md` and `node-*.md`, `dispatch.json`, `status.log`, approval records under `~/.unlazy/approved`, and `.unlazy-hook-state.json`.

**d. Simplicity quotes.**
The README carries none.
`SKILL.md` and `references/token-economy.md` do:

- "Do not create gates for a trivial edit or factual reply. Use this discipline when the cost of quiet incompleteness justifies the ledger."
- "Do not orchestrate a task that one focused session can implement and verify cleanly."
- "Keep check execution sequential by default."
- "Keep `SKILL.md` limited to the core workflow. Load method, gate, orchestration, and parallel references only when the selected mode needs them."
- "Append events to `status.log`. Do not repeatedly regenerate a large plan when one line records the event."

**e. Separate-verifier and frozen-check quotes.**

- README: "A runnable gate passes only when its process exits `0` and `EXPECT:` matches combined output."
- README: "Parent re-verification should use the same declared shell and required toolchain. A shell or PATH mismatch is a failed verification to resolve, not successful evidence."
- README: "`--status` and Stop detect definition drift without resolving a shell or executing a check, but old evidence is not re-execution; parent verification uses `--reverify`."
- `SKILL.md`: "Verification runs in four layers: leaf self-check, parent `--reverify`, branch integration, and the optional Stop hook (a structural backstop that does not itself execute checks). Only the parent and branch layers are independent of the leaf."
- `SKILL.md`: "Re-run each returned leaf's runnable gates with `--reverify`; do not mistake `--status` for re-execution."
- `token-economy.md`: "Do not save time by skipping approval, negative controls, parent re-verification, or integration gates. Those checks exist because a fast false completion costs more than a direct failure."

**f. Wrong or gamed check.**
This repo treats it as the central problem.
README: "The checker can prove only the command oracle you declare. It cannot infer that an English title and arbitrary shell code mean the same thing."
Its authoring rules require a success-only marker printed after all assertions, a negative check tested against a known positive control, and measuring supplied figures rather than copying them into `EXPECT:`.
`gate-lint.mjs` catches "mechanically weak ledger patterns" at authoring time.
It also states its own limit: "This unkeyed binding detects structural drift, not ledger tampering: anyone who can edit a ledger can forge canonical-looking evidence."
An impossible gate must be abandoned explicitly, which exits 1 with `HANDOFF REQUIRED` and cannot promote a parent to complete.

**g. Numbers.**
It retracted its own benchmark: "Earlier README versions also cited a six-run internal comparison. The raw artifacts needed to reproduce those exact ratios and counts are not in this repository."
Cited external figures: SlopCodeBench's best agent passed "14.8% of checkpoints"; METR's "196.5 day overall P50 doubling-time fit".
`--jobs` accepts 1 through 64.
Output cap 1 MiB.
Six-block progress guard.

---

## 4. Spielewoy/autoprompt-skill

**a. Loop shape.**
A five-level agent hierarchy under gates G1 through G8.
L0 conductor dispatches only L1 coordinators, which dispatch an optional L2 manager or L3 executors directly, which may spawn L4 terminal leaves.
Scope produces one `ROADMAP.md`, approved by an independent reviewer and a blind fresh verifier running concurrently.
Approved lanes dispatch straight to implementation.
Unattended, `supervisor.sh` relaunches an interrupted child until a fresh DONE sentinel appears or a bounded poison or scope guard escalates.

**b. What verifies.**
Four distinct checkers, all default-FAIL.
`ap-fresh-verifier` blind-checks the roadmap.
`ap-reviewer` reviews implementation.
`ap-verifier` runs runtime verification.
`ap-juror` holds one of three sign-off seats where every criterion starts FAILED and flips only on opened, quoted evidence.
Underneath sits strict TDD and a 95% changed-line coverage floor.
The roadmap author writes the acceptance criteria and verification commands into `ROADMAP.md`; the human supplies only the mission.

**c. Size and state.**
`workflow/supervisor.sh` is 1272 lines, `workflow/autoprompt-gate.js` is 4937 lines.
State: `PROMPTS.txt` (append-only prompt ledger), `ROADMAP.md`, `GATELOG.md` (append-only transitions and resume frontier), and `track.md`.
These live at a governance root outside the target repository and must never appear in its diff.

**d. Simplicity quotes.**
None.
The README's nearest statement is a cost disclosure: "**Expected trade-off:** about 3x the time and 2x the tokens."

**e. Separate-verifier quotes.**

- README: "The layers separate coordination, management, execution, and independent judgment. That separation keeps one agent from planning, approving, and verifying its own work."
- `SKILL.md`: "No agent reviews or verifies work it authored."
- `SKILL.md`: "Preserve blind review: reviewer and fresh verifier receive the mission, candidate roadmap, real repository, and raw evidence only."
- `GATES.md`: "Reviewer independence is load-bearing: send the mission pointer, candidate artifact, real repository, and raw evidence, never another reviewer's verdict or reasoning."
- `GATES.md`: "Concurrent blind assurance agents share no verdict channel: neither reads ledger rows carrying the other's verdict before reporting its own."
- `GATES.md`: "Author-independent verification is mandatory at every scope: the independent-verification floor never collapses with fan-out width - even a bounded lane with zero fan-out ends in independent review and verification."
- `ap-juror.md`: "Uncertain means FAIL."

**f. Wrong or gamed check.**
`GATES.md`: "Verification must exercise the actual graded oracle target: the verifier names and runs the real fail-to-pass or oracle tests against the candidate diff; running only pre-patch suites or roadmap-conformance checks is NOT-VERIFIED, never a PASS."
And "Dismissing a red test as documenting buggy behavior requires independent adjudication by an agent that did not author the change; the author never dismisses a red test alone."
A juror FAIL naming a P0 or P1 blocker is explicitly not arbitrable into PASS.

**g. Numbers.**
Terminal-Bench 2.1 with OpenCode 1.18.7: 60/89 solved (67.42%) baseline versus 73/89 (82.02%) with Autoprompt, +14.61 points, 29 failures down to 16, described as 45% fewer.
Roughly 3x time and 2x tokens, and the README admits "Timing and token logs were not retained, so these are planning estimates based on user experience reports, not measured benchmark results."
Bounded scope is 3 agents and 2 rounds; multi-surface is exactly 5 agents and 3 rounds; `tokensaver` caps six live subagents; coverage floor 95%.

---

## 5. chenxiachan/thoughtdag

**a. Loop shape.**
There is no automated agent loop.
ThoughtDAG is a desktop app, a CLI, read-only MCP tools, and a DeepSeek Harness plugin.
The user edits a directed acyclic graph; the edges into a node are exactly the context the model receives for that node.
The model runs one turn per question node.
The README's own closing line is "The graph is acyclic. You are the loop."

**b. What verifies.**
Nothing verifies agent work.
The only measurement is a benchmark whose answers are "scored by exact match" against gold files.
The stated design principle is the opposite of autonomy: "the human in the loop, the model on the wires" and "No autonomous agent redraws your graph."

**c. Size and state.**
No loop script.
State is canvas files (`*.thoughtdag.json`), a local index of Claude Code, Codex, DeepSeek Harness, and Pi sessions, automatic folder backup, and Markdown export.

**d. Simplicity and anti-over-checking quotes.**
None.
The nearest relevant line is "**Give agents less irrelevant history. Reduce context-driven hallucinations and wasted tokens. Improve answer accuracy.**"

**e. Separate-verifier and fresh-context quotes.**
None about verification.
The context-hygiene claim is adjacent and worth recording:

- "A wrong statement flows into the replies that come after it and undermines the truthfulness of every later conclusion."
- "deleting the message that introduced the error is often not enough, because the follow-up replies still carry it"
- "Managing context, not just accumulating it, decides what a model gets right."

**f. Wrong or gamed check.**
Not applicable.
The remedy for a bad answer is cutting the edge that fed it and re-asking.

**g. Numbers.**
Context Intervention Benchmark Pilot v2: 9 models, 1,485 test runs, $0 in free tiers, scored by exact match.
It disclaims ranking models or explaining mechanism.
60+ features listed.

---

## 6. Forward-Future/loopy

**a. Loop shape.**
A published loop is a prompt bundled with a verification rule and a stop rule.
Loopy executes it in bounded passes: observe fresh state, choose one reversible in-scope action, run the loop's acceptance check under recorded conditions, record action and evidence, decide whether another pass is justified.
It stops at success, clean no-op, blocked, approval required, exhausted, or no measurable progress.
Nothing runs between calls except the acceptance check itself.

**b. What verifies.**
The loop's own acceptance check, authored before the run by the human or produced by Loopy's craft interview with the user.
`references/run.md` is explicit: "Do not replace a missing check with confidence or self-approval."
It also refuses to invent a budget: a finite run boundary must be supplied by the loop or the user, and "If it is missing, ask the user rather than inventing one."

**c. Size and state.**
No loop script.
`skills/loopy/SKILL.md` is 302 lines plus five reference files (`audit.md`, `debrief.md`, `discover.md`, `publish.md`, `run.md`).
State is deliberately minimal: an optional project `LOOPS.md` written only when asked, and a receipt returned in the conversation.
"Loopy does not create persistent run files unless you request them or the project already has an established convention."

**d. Simplicity quotes.**

- README: "Loops are not permission for an agent to run forever. The best ones are deliberately bounded."
- README: "Debrief completed runs and recommend the smallest evidence-backed improvement."
- README: "A good loop answers four simple questions"
- `references/audit.md`: "Do not assign a numerical score. Do not flag the absence of an arbitrary time, iteration, cost, or retry budget when a clear no-progress stop is sufficient."
- `references/audit.md`: "Do not invent missing tools, metrics, owners, schedules, permissions, or system details."
- `references/audit.md`: "Make the smallest change that closes each material weakness."
- `references/audit.md`: "If the loop is already sound, say so and leave it unchanged."

**e. Separate-verifier and reproducibility quotes.**

- `references/audit.md` flags as a defect: "vague, self-graded, or irreproducible verification" and "optimizing and accepting against the same evidence when that can overfit"
- `references/run.md`: "Its receipt preserves the exact loop definition or an immutable reference plus the acceptance conditions, so a later debrief can reproduce what ran."
- README: "**Verify** defines the evidence that proves the work succeeded."

**f. Wrong or gamed check.**
The Loop Doctor path exists for exactly this: audit a loop, name material weaknesses, repair only those.
Runtime rules: "Never classify an error as success" and "If the loop is not executable with the available tools or evidence, stop as blocked instead of simulating success."
Loop text and `LOOPS.md` are treated as untrusted data that cannot grant new authority.

**g. Numbers.**
Nine paths.
At least two distinct thread occurrences before work counts as repeated.
Up to three published loops recommended per find.
Up to three material findings per audit.
No success rates or costs.

---

## 7. huangruiteng/loopx

**a. Loop shape.**
LoopX is a control plane, not a runner.
The agent harness (Codex, Claude Code, Cursor, DeepSeek Harness, or a custom runner) executes one bounded turn.
Around it, LoopX decides whether that turn should happen.
The core tick is five CLI calls: `loopx quota should-run`, `loopx todo claim`, `loopx todo update`, `loopx refresh-state`, `loopx quota spend-slot`.
The documented state machine branches on human judgment first, then a safe fallback, then a bounded agent slice, then writes evidence and a handoff, and quota decides the next tick.

**b. What verifies.**
Evidence and validation recorded into LoopX state, plus per-host verification rules.
The KunlunCode row says "LoopX writes completion and quota only after strict verification."
The auto-research demo ships a "deterministic CPU evaluator, and dev/held-out commands" in the repository.
Final ownership is human: "Dangerous permissions, publishing, production writes, and final ownership stay with the human."

**c. Size and state.**
No single loop script; 3,834 files.
State: `.loopx/registry.json`, projected goal state, todos, gates, evidence, quota, compact run history, claims, leases, handoffs, plus `.codex/goals/` and `.local/`, all gitignored.

**d. Simplicity quotes.**

- "The core tick is deliberately small:"
- "> Keep the loop moving. Keep the judgment human."
- "It is not another agent framework or a provider-specific orchestration runtime."

**e. Separate-verifier and deterministic-gate quotes.**

- "The public task, editable and protected files, deterministic CPU evaluator, and dev/held-out commands all live in this repository."
- "Review protected changes through typed preview, explicit confirmation, and receipts while LoopX state—not the browser—remains authoritative."
- "May the loop continue? | Quota, capabilities, safe fallback, scheduler hints, and stop conditions."

**f. Wrong or gamed check.**
The most useful finding in the whole set is here, and it cuts against more verification:
"Five execution modes on 15 matched tasks compare self-verification, scores, and cost. More self-verification did not consistently yield higher scores."
The repo then bounds its own claim: "SWE-Marathon has one trial per task and mode; DeepSWE uses selected cases and post-hoc analysis. Neither establishes a general performance gain."

**g. Numbers.**
Two showcase arcs at 200+ hours of elapsed loop lifetime, explicitly wall-clock and not continuous compute.
SWE-Marathon: 5 modes, 15 matched tasks, one trial each.
Independent user reports: one run over 13 hours, one 4-day unattended run, 7 merged PRs, a 1B+ token scale that remains a user report.
The demo workspace has 3 scenarios, 4 roles, 18 tasks, 2 decisions, 2 watches.

---

## 8. anthropics/cwc-long-running-agents

**a. Loop shape.**
Two options, both explicit.
The built-in one is `/goal`, where "After every turn a separate fast model checks the condition and keeps the session going until it's met."
The custom one is a six-line bash loop in the README:

```bash
while grep -q '"passes": false' test-results.json; do
  claude -p "Read PROGRESS.md and build the next unfinished feature per CLAUDE.md."
  VERDICT=$(claude --agent evaluator -p "Review the most recent commit against its spec.")
  [ "$(echo "$VERDICT" | head -1)" = "PASS" ] || echo "$VERDICT" > NEXT_FINDINGS.md
done
```

Each pass is a fresh `claude` process.
It exits when the contract file has nothing failing, a cycle makes no changes, or a budget is hit.
`touch AGENT_STOP` stops it early.

**b. What verifies.**
Three layers.
A `PreToolUse` hook denies any write to `test-results.json` unless an evidence file was opened with the Read tool first, then consumes that evidence so the next write needs fresh proof.
A fresh-context evaluator subagent with no Write or Edit tools returns PASS or NEEDS_WORK.
A Stop hook commits work.
Critically, the human writes the checks before the run: "Every feature is a row in a `test-results.json` file you create in your project."

**c. Size and state.**
Everything is tiny.
`verify-gate.sh` is 30 lines, `track-read.sh` is 12, `commit-on-stop.sh` is 18, `evaluator.md` is 26, `CLAUDE.md` is 28.
The loop is 6 lines of bash.
State: `test-results.json`, `PROGRESS.md`, `.claude/.evidence-reads`, `screenshots/`, git history, `NEXT_FINDINGS.md`, `AGENT_STOP`, `STEER.md`.

**d. Simplicity quotes.**

- "**These are example ingredients, not a turnkey harness.**"
- "**Read and cherry-pick.** Each primitive is one standalone file with no dependency on the others."
- "One line, no contract file or hooks."
- "(The shipped hook is intentionally simple; see the comments in `verify-gate.sh` for the gaps a production version would close.)"
- "This is the layer most sensitive to model capability; newer models drift less and self-scope better, so re-evaluate how much of `CLAUDE.md` you still need after each model release"
- "**Re-simplify on model upgrades** | After each model release, comment out harness pieces one at a time and see what's still load-bearing"

**e. Separate-verifier and default-FAIL quotes.**

- "**Default-FAIL contract.** Every criterion starts `false`; the agent can't mark it passing without opening evidence first."
- "**Fresh-context evaluator.** A separate agent with no Write/Edit tools grades the work from a context window that never saw the build."
- "The builder shouldn't grade its own work."
- "Agents will mark a feature "passing" after a unit test or a curl when the UI is visibly broken. Asking nicely in the prompt doesn't reliably stop this. The harness makes "done" structural."
- "Each pass is a fresh context."
- `evaluator.md`: "Plausibility is not correctness."
- `evaluator.md`: "You did not see how it was built and you should not trust the builder's own assessment."

**f. Wrong or gamed check.**
It documents its own gate's holes in the script comments:
"this only hooks Write/Edit (Bash sed/jq can rewrite the file unchecked); the path match is basename-only and case-sensitive; and any evidence read unlocks any result row, not the corresponding one."
The README offers the fix for a self-graded contract: "have your wrapper write the contract on `PASS` instead if you want "all true" to mean "independently confirmed.""
The going-further table adds a browser-verified evaluator, to "Let the evaluator open the running app itself instead of trusting the builder's screenshots."

**g. Numbers.**
None.
No rounds, cost, or success rate is claimed anywhere.

---

## 9. AMAP-ML/LongHorizon-Harness

**a. Loop shape.**
Three roles per round: Manager plans the next bounded step from the original goal and verified state, Executor runs it with a fresh context in a GUI or CLI, Auditor independently inspects the real environment.
Verified results are checkpointed; rejected ones stay as evidence and feed the next round.
The loop is `while round_index < gate.round_budget`, default 30 rounds.
Per-episode timeouts are 600s manager, 1800s executor, 600s auditor.
It also stops on blocked, on an explicit ask-the-human, and on operator stop.

**b. What verifies.**
The Auditor, a separate model role with read-only permissions and its own backend and model.
It is a model, not a test suite, but it inspects the actual workspace rather than the Executor's report.
Its prompt says harness records do not count: "Harness prompts, trajectories, and role output logs are execution records, not proof that the task succeeded."
Separately, `dashboard/rules.py` raises a human review gate after 3 consecutive failing rounds.
The Manager writes the per-round task contract; the auditor instructions ship in `role_prompts.py`.

**c. Size and state.**
`manager.py` is 2,480 lines, `supervisor/service.py` is 2,468, `auditor_agent.py` is 860, `role_prompts.py` is 763, `dashboard/gate.py` is 187, `rules.py` is 83.
State per run under `./.lh-harness/runs/<run-id>/`: `task_state.txt`, `task_contract.txt`, `manager_plan.txt`, `harness_feedback.txt`, auditor reports, an event stream, role trajectories, workspace artifacts, and `logs/report.json`.

**d. Simplicity quotes.**
None.
The README argues the opposite direction throughout.

**e. Separate-verifier and fresh-context quotes.**

- "Only results that pass independent verification become trusted task state. A rejected result remains evidence, not progress."
- "**Auditor** | Independently inspects the actual files, interfaces, logs, and tests instead of trusting the Executor's claim"
- "**Executor** | Starts with a fresh context and completes one clearly defined step in a desktop app or the CLI"
- "The model determines what an agent can do in one round. LongHorizon-Harness engineers the loop around it"
- "`eval/` provides frozen reproduction suites for three benchmarks"
- `role_prompts.py`: "Related auditor reports (background, never a substitute for direct read-only audit)"

**f. Wrong or gamed check.**
The manager cannot declare done on its own.
From `manager.py`: "Completion is not accepted unless it is grounded in a previous clean auditor report. The synthetic audit gets fed back into the next manager turn as a repair signal."
A DONE without a clean audit is recorded as `invalid_completion` and the round continues.
A timed-out episode keeps its partial trajectory and lets the next Manager round inspect the real workspace, and "The timeout remains an agent execution timeout; it is not treated as proof of a provider network failure."

**g. Numbers.**
Default 30 rounds.
Human-review trigger at 3 consecutive failed rounds.
WeaveBench (114 tasks): PassRate 51.8 to 80.7, +28.9; Overall 0.702 to 0.835.
OSWorld 2.0 (108 tasks): binary 2.8 to 8.3, a 3.0x gain; partial 21.5 to 35.2.
Terminal-Bench 2.1: 69.7 to 77.2, +7.5, with 24% fewer tokens.
All rows use Qwen 3.7-Plus as backbone and Claude Code as execution backend.

---

## 10. ray-r-ren/agent-apprenticeship

**a. Loop shape.**
`run_task` in `loop.py` is a fixed pipeline, not an open loop.
Task intake produces a spec, a model generates a rubric, the apprentice agent runs a baseline attempt, then grader, verifier, and evaluator run in sequence, the evaluator writes a revision plan, and the apprentice runs one revised attempt scored the same way.
The higher-scoring attempt is selected and training signals are written.
It stops at `max_iterations` (`AA_MAX_ITERATIONS`), on a mentor decision to finish, or immediately on an apprentice operational error.
The shipped code path caps `actual_iterations` at 2.

**b. What verifies.**
Three separate model roles plus one deterministic guardrail.
The grader scores against the pre-generated rubric.
The verifier checks whether the grader's evidence is grounded in the actual outputs and artifact previews.
The evaluator writes the feedback and revision plan.
`deterministic_verify` is a structural check only: artifact refs present, score within bounds, no hidden-reference leak.
The rubric is written before the attempt, by a model, from the task spec.

**c. Size and state.**
`loop.py` is 210 lines, `grader.py` 196, `evaluator.py` 181, `loop_review.py` 687, `verifier.py` 62.
State per task package: `attempts/{baseline,revised}/actual_outputs.json` and `agent_trace.json`, `grading/*`, `feedback/*`, `loops/iterations/NNN/`, `signals/*.jsonl`, and `package_manifest.json` carrying `loop_stop_reason`, `actual_iterations`, and `selected_attempt_id`.

**d. Simplicity quotes.**
None in the README.

**e. Separate-verifier quotes.**
The verifier's own prompt, in `verifier.py`, is the clearest statement in the repo:
"Do not treat Apprentice Agent self-assessment or self evaluation as outcome evidence. Do not use deterministic fallback judgement; structural guardrails are package-integrity checks only and are not verifier judgments."
The README frames the same split as "are evaluated by mentor agents or humans in the loop."

**f. Wrong or gamed check.**
A `hidden_reference_leaked` flag propagates from grader to verifier, and `apply_score_reliability` adjusts the grade using the verifier result rather than trusting the raw score.
When `evaluation_mode` is `llm_required` or `llm_fail_closed` is set, a failed verifier call raises instead of silently degrading to the structural guardrail, and the guardrail records `verification_status='not_run'` so a fallback cannot masquerade as a verdict.

**g. Numbers.**
Seed dataset v0.2: 500+ curated tasks, 495 reusable lessons, 1000+ execution traces, 1000+ work episodes, 505 full experience compilations, 39k+ structured records.
Max loop depth is configurable, with `AA_MAX_ITERATIONS=3` shown as the example.
No success rate or cost.

---

## UNREACHABLE

None.
All ten repositories were fetched successfully.

---

## Risks

All ten repos were read at `main` HEAD on 2026-09-08 with no commit pinning, so line counts and quotes drift as the repos move.
For the three largest repos (loopx at 3,834 files, LongHorizon-Harness at 1,462, autoprompt at 747) I read the README plus targeted loop and verifier files, not the full tree, so a loop mechanism living somewhere I did not open would be missed.
The benchmark claims quoted from autoprompt, LongHorizon-Harness, thoughtdag, and loopx are the authors' own self-reported numbers; I did not attempt to reproduce any of them.
