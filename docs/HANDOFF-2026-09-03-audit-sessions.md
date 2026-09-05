# Handoff: Loam audit execution, sessions 2 to 6

> Written 2026-09-03 by the Fable 5.1 audit session for a fresh session with no context.
> Lead for the next sessions: Claude Fable 5.1 (`claude-fable-5-1`). Samyak selected 5.1 on 2026-09-03.
> Run any Fable model at `medium` or `high` effort only, never `xhigh` or `max` (Samyak's cap). The lead runs at `high`.
> The lead decides, commissions the work, coordinates the agents, assesses their output, and gives feedback; it does not write the code.
> Workers: Claude Opus 4.8 (`claude-opus-4-8[1m]`) at xhigh effort. Never Fable workers.
> Allowed models: Opus and Fable only, for everything, including mechanical subagents. Use only Opus, Fable, or a model Samyak names next.
> Run each session as an advisor-mode agent team or a dynamic workflow; the lead picks the shape. See "Operating model" below.
> A fresh Fable 5.1 session reviews the work at the end of each session. See "End-of-session review".
> Samyak sleeps while this runs. Do not ask him questions that the files below already answer.

## Session-start prompt (paste this into the fresh session)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. Read
docs/HANDOFF-2026-09-03-audit-sessions.md in full, then run the next unfinished session in its
"Sessions" list and stop. Read "Operating model" first; it defines your loop.
Run yourself at `high` effort, never above (Samyak's cap on Fable); Opus 4.8 workers run at `xhigh`.
Orchestrate with dynamic workflows and the ultracode quality patterns. In auto mode, set `/goal`
to this session's Goal line.
You decide, commission, coordinate, assess, and give feedback. You do not write the file edits.
Opus 4.8 workers (model "claude-opus-4-8[1m]", effort "xhigh") do the edits, spawned as an
advisor-mode agent team or a dynamic workflow, your choice per the Operating model. Never spawn
Fable workers. A worker cannot read your thinking blocks, so every brief must stand on its own.
Assess each worker's diff on four axes (correctness, Samyak's intent, taste, thoroughness) and
send it back with specific feedback when it falls short; cap at two feedback rounds per worker.
Seed behavior, hooks, and copier.yml go on the branch named in the session; docs go direct to main.
Before you commit, bin/verify-template.sh must print "verify-template: PASSED" and
uvx pytest -q bin/tests must be green (system python3 has no pytest; uvx does). You commit on the
branch; workers never commit; do not push and do not open a PR.
Each session block also owns the items tagged for it in the Gap review and Research additions
sections. Update the "Execution log" at the bottom of the handoff when you finish, then stop so the
End-of-session review can run in a fresh context. Please remove all mannered prose.
```

## Operating model: Fable 5.1 leads, Opus 4.8 executes

The lead for every remaining session is Claude Fable 5.1 (`claude-fable-5-1`).
Samyak selected 5.1 on 2026-09-03, replacing the earlier "run on Fable 5" note.
The lead does not write the code.
It reads intent, resolves open design choices, commissions the work, coordinates the workers, judges what they produce, sends it back for improvement, then verifies and commits.
Opus 4.8 workers (`claude-opus-4-8[1m]`, effort `xhigh`) do the file edits.

Effort split, per Samyak's cap on Fable models:

- The Fable 5.1 lead runs at `high` effort and never above. For any Fable model use `medium` or `high` only; `xhigh` and `max` are off-limits for Fable. `high` is also the guide's own default and it avoids the xhigh double-draft, so the cap costs nothing here.
- The Opus 4.8 workers run at `xhigh`. Dial a worker to `high` only when its whole job is writing one long file.
- "Ultracode" here means the orchestration and quality discipline, not a Fable effort bump. The lead orchestrates with a dynamic workflow for every substantive step and spends tokens on exhaustive, verified quality; token cost is not the constraint, correctness and taste are. The `xhigh` in ultracode belongs to the Opus workers, not the Fable lead.

Pick one execution shape per session:

1. Advisor-mode agent team. Use the `agent-team` skill with Fable 5.1 as the advisor and Opus 4.8 teammates. Best when the work needs live cross-talk between workers or the plan may change as they report.
2. Dynamic workflow. Use the Workflow tool: fan workers out over disjoint files, then a verifier stage. Best for a fixed fan-out-then-verify shape. It is deterministic, resumable, and keeps worker transcripts out of the lead's context. This is the default for an unattended overnight run.

Under ultracode, build the workflow for quality, not just speed:

- Adversarially verify each worker edit. Add a checker stage whose job is to prove the edit wrong or incomplete against the item it was given, not to rubber-stamp it.
- Run a completeness critic at the end. One agent asks what session item is unaddressed, what report recommendation is uncovered, and what check was not run; its answer is the next round of work.
- Never cap coverage silently. If you bound something (top-N, no retry, sampling), `log()` what you dropped so it does not read as full coverage.

Either shape, the lead runs this loop:

1. Frame. Read the session block plus every Gap review and Research addition item tagged to it. Resolve an open design choice from the repo. Samyak is asleep, so do not ask him a question the handoff already answers; record a genuine blocker in the Execution log and keep going on everything not blocked.
2. Commission. Write a self-contained brief per worker. An Opus 4.8 worker cannot read your Fable 5.1 thinking blocks, so the brief must stand alone: the exact files, the exact changes, the scope boundary, the forbidden actions, and the command the worker must run to check its own work. Ask for the result as data, not prose.
3. Coordinate. Keep working while workers run; do not idle waiting for each one (Fable 5.1 guide, "let the lead keep working"). Workers edit disjoint files, so one checkout is safe.
4. Assess. When a worker reports, read the actual diff, not just its summary. Judge the work on four axes:
   - Correctness and software-engineering best practice. It works, it is the right layer, it follows the repo's patterns, and the worker ran and pasted the check.
   - Samyak's intent and the stated scope. It delivers exactly what the session asked, no less and no more.
   - Taste. Minimal diff, no over-engineering, no abstraction the task did not need, reads like the surrounding code.
   - Thoroughness. The whole item, the edge cases, the verification actually run.
5. Iterate. Where the work falls short on any axis, send specific, actionable feedback that names the axis and the fix, and have the worker redo that part. Cap at two feedback rounds per worker; if it still will not converge, re-scope the item smaller, sharpen the brief, or spawn a fresh worker, and log why. Never write the edit yourself; that breaks the lead-does-not-code split.
6. Verify and commit. Run the four checks. You commit; workers never commit. Append to the Execution log and stop.

Do not paste the autonomy block or the tool-batching nudge into a worker brief.
Claude Code injects both as turn-scoped system messages, so a second copy is paid input for no change (Fable 5.1 guide; verified in the audit).

## Running a session under `/goal`

Each session has a checkable end state, so the lead runs it under `/goal` (Claude Code docs, `code.claude.com/docs/en/goal`).
`/goal <condition>` sets a completion condition and Claude keeps taking turns until a small fast model judges the condition met, judges it impossible, or an unrecoverable error clears it.
Setting the goal starts a turn at once, so no separate prompt is needed.
Each session block below carries its own `Goal:` line; the lead pastes that line as the `/goal` condition when it starts the session.

How to write and run it, from the docs:

1. The evaluator reads only the transcript. It never runs commands or reads files. So the condition must be provable by output the lead has already printed. Print the check; do not describe it.
2. A good condition names one measurable end state, the stated check that proves it (for example "`bin/verify-template.sh` printed verify-template: PASSED"), and the constraint that must not change ("no file outside this session's items is modified").
3. Always add a turn cap, "or stop after N turns", so a stuck loop returns control. The condition may be up to 4000 characters.
4. Run the session in auto mode so goal turns proceed unattended; in manual mode Claude still stops for any tool call the settings do not already allow.
5. `/goal` needs hooks. It is unavailable when `disableAllHooks` is true or `allowManagedHooksOnly` is set, and it tells you so rather than failing silently; never set either in the session.

How `/goal` composes with the workers and with ultracode:

- Workers are background work. While a subagent or a dynamic workflow is still running, Claude Code defers the goal evaluation to the end of the next turn with no background work running. So the evaluator never grades a half-finished session; it waits for the workers, then reads the diff and the checks in the transcript. This is the behavior we want.
- If the lead answers the evaluator several turns in a row with no tool use, Claude Code pauses the loop and returns control. That pause is the signal to commission the next worker, not to argue with the evaluator.
- `/goal` (when to stop) and ultracode (how to orchestrate and verify) are orthogonal, so a session runs under both at once.

## Objective and aim

Loam is the Copier template that ships Samyak's Claude Code and Codex harness into every project.
The aim: every project seeded from Loam gives him a research partner that can think, brainstorm,
code, test, and run experiments unattended until a written "done" check passes, with time and
token efficiency, using Fable 5.1 as lead and Opus 4.8 as workers.

The 2026-09-02 audit (14 Opus workers, Fable 5.1 lead) found:

1. No project uses the Loam seed today. distbench is pinned to a dead tag (v3.6.2). parbench and
   content_search_engine run plugin-only plus richer hand-built harnesses. Samyak chose to KEEP
   the three-layer model and REPAIR sync (not invert to plugin-first).
2. Every model-facing prompt targets Fable 5 or Opus 5. Rendered projects get zero Fable 5.1 steering.
3. Plugin agents used a bare `model: opus` alias (resolves to Opus 5). Fixed in session 1.
4. Two hooks had bugs (stop gate scoping and HEAD guard; ruff fallback). Fixed in session 1.
5. The review surface has six entry points; four is enough. Session 3.

Full evidence: `docs/plans/2026-09-02-harness-audit-synthesis.md` (worker reports, paste-ready
text, Samyak's answers, the approved idea table). Decision page:
https://claude.ai/code/artifact/fc407a45-857b-4186-8b93-6975bf06cbcb

## Samyak's decisions (binding)

- Keep three layers; repair forward sync. Archive distbench; promote its inventions.
- Promote first: parity bill of materials, validate-sentinel hook trio, experiment scaffolding
  that starts empty (never pre-filled stubs).
- Workers at xhigh everywhere. Lead is Fable 5.1 (Samyak selected 5.1 on 2026-09-03).
- The stop gate BLOCKS a final message that claims verification without command output.
- Killed for good: a knowledge graph of claims, more review skills, any always-on MCP server.
- Seed settings.json carries NO model key; the user's global default decides (session 1).
- Codex second opinions cap at ~2 rounds; findings are candidates to check, never verdicts.

## Samyak's answers on 2026-09-03 (binding, additive to everything above)

- Dogfood target for the research lane and the experiment contract: a NEW distbench, same research
  goal, fresh repo rendered from the updated seed. The old distbench stays archived.
- Walk-away runs execute on this Mac AND on a remote eval host (ssh plus tmux, like parbench's
  conveyor). The experiment contract needs a remote runner and a results sync step.
- Notifications: Pushover. Reuse parbench's pattern (`~/.parbench_pushover` credentials file,
  ntfy.sh as fallback). See `~/Desktop/parbench_sam/scripts/orchestration/run_conveyor.sh`.
- Codex is an EQUAL IMPLEMENTER, not a review probe. The parity bill of materials must give
  Codex every skill, hook, and agent with a mirror or an explicit unsupported reason.
- Fable 5.1 doubled Fable 5 on Terminal-Bench-Science. For research work inside seeded projects,
  the lead for hypothesis design, experiment analysis, chart reading, and paper reasoning is
  Fable 5.1. Opus 4.8 executes. The harness sessions in this handoff now run on Fable 5.1 as lead
  (Samyak's 2026-09-03 selection). Ship this split as prose in the research-lane README, not as a model pin.
- Everything below is IN ADDITION to sessions 2 to 6. Nothing replaces carved-out work.

## Gap review (lead's own re-read of the three requests, 2026-09-03)

These were asked for and were missing from the first draft. Each names the session that owns it.

1. Understanding his own thinking and the repo (session 5). Ship a decision ledger:
   `docs/decisions/RULINGS.md`, one dated line per ruling ("do now / defer / drop", verbatim
   words, agents may not re-argue), promoted from parbench's rulings walkthrough and the day
   planner's backlog-for-ruling. Ship a standing-constraints block: `.claude/rules/invariants.md`
   that every ticket prompt references instead of restating (parbench repeated one clause five
   times in one plan). Ship the CONTEXT.md scaffold with a Skip column (Task / Load these / Skip
   these with a reason), from parbench's six subdirectory files; the `scaffold-context` skill
   exists in the plugin, so wire it and add the Skip column.
2. Acquiring and creating skills (session 6). A skill-acquisition loop as one skill, `adopt-skill`:
   find (`find-skills`, skills.sh), vet (`bin/vet-skill.sh`), eval (skill-creator benchmark with
   and without), adopt into the marketplace with a `RESOURCES.md` line. Add the rule "write a
   skill at the second repetition, never the first" and promote distbench's
   `scaling-vs-automating.md` and `layer-triage.md` rules (deterministic vs rule vs LLM).
3. Parallel-agent safety (session 5). A lock-file convention for exclusive resources
   (`.locks/<resource>` with owner and timestamp, checked by a PreToolUse Bash hook when a
   command names the resource), and a worker brief-and-report protocol (`.superpowers/sdd/<task>/`
   brief.md plus report.md, from the day planner) so an interrupted agent's findings are never
   rebuilt from a wire log. Add a state-freshness gate: `catchup` flags STATE.md or HANDOFF.md
   whose mtime is older than the last commit, or whose status verbs contradict git.
4. Durable finding tracker (session 3). Codex review transcripts are gitignored; unfixed
   findings survive only as prose. Add `docs/findings/FINDINGS.md`, one row per open verified
   finding with path:line and a closing commit; `codex-review` appends to it.
5. Retrieval before ideation (session 6). The `ideate` skill's Diverge step must run one
   literature or code retrieval pass (Exa or arXiv search, or `grep` of the repo) before
   branching; retrieval-grounded ideas had 2.5x the real impact of ungrounded ones and the
   model cannot see the difference.
6. Benchmarking and AI engineering (session 6, research lane). Ship an `evals/` scaffold:
   `evalset.json` hash-pinned, a judge script with position swap and rubric dimensions, and a
   cost-per-task column (tokens, dollars, wall-clock) in every results table. Contamination
   note and a verification oracle field in the experiment contract.
7. Fast research coding (session 6). Promote parbench's headless conveyor as
   `bin/conveyor.sh`: tasks run via `claude -p` in tmux on the eval host, a Codex gate capped by
   `MAX_GATE_ROUNDS=2`, Pushover on halt, and the HEADLESS EXECUTION RULE line (never
   run_in_background, ScheduleWakeup, or tmux-and-wait inside a headless task).
8. Global config pass (user-gated, after session 6). `~/.claude/CLAUDE.md` and
   `~/.claude/FABLE-BRAIN.md` carry anti-formatting language the 5.1 guide says to remove, and
   the memory index treats Opus 4.8 as the frontier. Also propose the D1 declarative model split:
   set `ANTHROPIC_DEFAULT_MODEL` and `CLAUDE_CODE_SUBAGENT_MODEL_FORCE` in `~/.claude/settings.json`
   so the Fable-5.1-lead and Opus-4.8-worker split is config, not prose (Samyak decides which model
   is his global default). Propose a diff; Samyak applies it.

## Research additions (three Opus researchers, 2026-09-03; additive, each names its session)

Headline from the evidence: leverage is in what the agent must PROVE, not what it is TOLD.
Instruction-layer additions (repo overviews, routing tables, "write more tests") measured flat or
negative. Execution-gated checks measured real. Sources are in the synthesis file and below.

A. Correction to gap item 1. Repository overviews and Load/Skip routing tables do not raise task
   success and add over 20 percent inference cost (ETH Zurich, arXiv 2602.11988; configuration
   smells arXiv 2606.15828: context bloat in 42 percent of repos). Instructions ARE followed;
   overviews are not. So: keep `invariants.md` and the decision ledger (instructions), keep
   CONTEXT.md as an ON-DEMAND file a skill generates, never always-loaded, and do not claim a
   token saving for it until session 7 evals measure one. Keep the seed AGENTS.md short.

B. Session 4 (hooks), add:
   - Diff-scoped mutation score as the test-quality gate, not coverage. Coverage does not predict
     effectiveness for LLM-written suites (r near zero within a model, arXiv 2607.22880). Run
     `mutmut` or `cosmic-ray` on the files in the diff only, gate on surviving mutants this change
     introduced. Guard on pyproject.
   - Anti-reward-hacking scan of the test half of the diff: a script, no model call, flags new
     `skip`, `xfail`, `mock`, `patch`, loosened numeric tolerances, or an expected value equal to
     a constant the implementation now returns; the agent must justify each flagged line
     (BAITBENCH arXiv 2608.30724: cheating 20.8 to 76.1 percent by model). Rule: the failing test
     lands in its own commit before the implementation commit.
   - Harness hygiene at SessionStart: extract every path, file, and command named in CLAUDE.md,
     AGENTS.md, STATE.md, HANDOFF.md, test each for existence, print only the dead ones (23
     percent of 356 repos had stale references, arXiv 2606.09090). Plus a PreToolUse Skill hook
     appending skill name and timestamp to `.claude/skill-usage.log`; that log is the eval
     (Anthropic's own Claude Code team does this).
   - Command capture: PostToolUse on Bash appending command, exit code, timestamp to
     `logs/commands/` inside an active experiment folder (the bash-audit-log hook already does
     most of this; extend it with exit code and the experiment name).

C. Session 5 (sync and promotions), add:
   - Fixed-schema HANDOFF.md and the same schema for worker brief/report: goal, files touched,
     commands run with exit codes, what was tried and failed, open assumptions, next single
     action. Structured handoffs cut prompt tokens 42 to 63 percent on takeover (arXiv
     2606.02875). This is the direct answer to token burn. Replace the seed's four-line HANDOFF
     convention with this schema.
   - Worktree isolation for parallel workers: `claude --worktree <name>` creates
     `.claude/worktrees/<name>` and blocks edits to the main checkout; `-p` runs skip the trust
     dialog. Write it into the agent-team skill as the default for parallel implementers.

D. Session 6 (research lane), add:
   - Per-run folder layout enforced by one verifier script (from Glite ARF arXiv 2606.27416 and
     XScientist arXiv 2607.12301): `experiments/<name>/runs/<run_id>/{manifest.json, plan/,
     results/{metrics,costs,images}, logs/{commands,steps}}`; completed runs are immutable; fixes
     go in `corrections/`; an aggregator renders the canonical view. Manifest records model,
     effort, and harness version, because harness alone moved Terminal-Bench 2 from 69.7 to 77.0
     percent with the model fixed (arXiv 2605.23950).
   - Protocol validator (from Curie arXiv 2502.16069): the manifest must name every variable the
     sealed protocol declares (independent, dependent, constant); missing or hardcoded values fail.
   - Claims ledger with a build gate: `claims.tsv` (key, value, source_path, run_id, git_sha)
     renders to `claims.tex` macros; the paper cites numbers only through macros; a pre-commit
     grep fails on bare decimals in .tex outside macros. This is what Claude Science's reviewer
     flags as "untraceable numbers". About 60 lines of Python; no tool does the whole loop.
   - Figure faithfulness via `pytest-mpl`: every figure script regenerates from ledger data and
     diffs against a committed baseline with an RMS tolerance.
   - Citation gate: a script that pulls every DOI and arXiv id from the .bib, hits CrossRef and
     arXiv (keyless), and diffs title, authors, year, venue; fail on mismatch. Prefer this over any
     citation MCP server (the citecheck paper has no repo; Zotero MCPs do not export citations).
   - Self-review restricted to verifiable defects, no score: abstract number vs table, missing
     ablation named in intro, claim with no ledger key, hallucinated reference, broken cross-ref.
     AI reviewers show a "hivemind" effect and are gamed by rewriting (arXiv 2605.03202).
   - Rebuttal table: one row per reviewer concern with the quoted concern, the reviewer's stated
     score-change criterion, the ledger key or new experiment that answers it, and characters
     spent (NeurIPS 2026 caps 10,000 per review). CLAUDE.md line: never paste received reviews
     into a model outside the sanctioned experiment (NeurIPS 2026 integrity rule).
   - Evals scaffold: Inspect AI as the harness (plain Python tasks, local logs, no server);
     scorer wrapper that runs every pairwise judgment in both orders and averages, scores rubric
     dimensions separately, pins judge model id plus rubric version plus prompt hash in the run
     log, and uses a judge from a different family than the generator; cost per task as a result
     column (tokens, dollars from a checked-in price table, wall-clock) reported as an
     accuracy-versus-cost frontier. Verify Inspect's log schema records tokens before relying on it.
   - Benchmark admission checklist (Terminal-Bench arXiv 2601.11868): an oracle solution per
     task, completion decided only by deterministic tests on final state, an adversarial exploit
     agent run against your own tasks, a contributor checklist. Contamination control is seeded
     perturbation (rename symbols, permute shapes, vary seeds, compare to unperturbed), never a
     canary string.
   - Property-based tests as a skill on changed pure functions: three to five Hypothesis
     properties, run, paste the failing input; run alongside example tests (they catch different
     bugs; agentic PBT arXiv 2510.09907: 56 percent valid bug reports, 86 percent in the top 21).
   - Skill adoption step runs NVIDIA SkillSpector (`bin/vet-skill.sh` already wraps it).

F. Worktrees, notifications, arbitration (sessions 5 and 6; from code.claude.com/docs/en/worktrees and /hooks, read 2026-09-03):
   - `claude --worktree <name>` isolates at `.claude/worktrees/<name>`; `-p` runs never clean up
     their worktree (manual `git worktree remove`); set `worktree.baseRef: "head"` when an
     experiment must start from a dirty branch; `.worktreeinclude` copies gitignored files such as
     `.env`; a subagent can be pinned with `isolation: worktree`. Hook gotcha: `CLAUDE_PROJECT_DIR`
     stays at the launch root; the worktree path is the `cwd` field of the hook JSON. Every
     run-logging hook must read `cwd`.
   - Stop hook input carries `stop_reason` (`end_turn` or `max_tokens`). `max_tokens` is the
     overnight-stall signal. The Pushover notification hook (session 6) must send the stop_reason
     and the cwd. Pushover first, ntfy fallback, per Samyak.
   - Resource arbitration: build nothing beyond isolation. Twelve parallel tasks ran on one Mac
     with no lock at all when worktrees and separate databases were used (arXiv 2606.27416). If a
     GPU is contended on the eval host, the mechanism is one line: `flock /tmp/gpu0.lock <cmd>`
     (util-linux; not on stock macOS). Replace gap item 3's lock-file hook with this note.
   - "awesome-claude-code" style lists yielded no verifiable mechanism beyond a session logger,
     which the bash-audit-log hook already is. Do not cite star counts.

G. Session 6, run-folder contract (paste-ready, from XScientist and the harness-disclosure paper):
   CLAUDE.md line: "Experiments live in runs/<UTC-date>_<slug>/ with run.json, protocol.md, logs/,
   results/. A finished run is immutable: corrections go in runs/<id>/corrections/, never by
   editing results."
   `run.json` schema:
   ```json
   {"schema_version":"1","run_id":"2026-09-03_cuda-ocl-baseline","protocol_sha256":"","git_commit":"",
    "harness":{"tool":"claude-code","version":"","model":"","effort":""},
    "independent_vars":{},"dependent_vars":[],"constants":{},
    "status":"running|complete|failed","missing_artifacts":[]}
   ```
   The `harness` block is load-bearing (harness alone moved Terminal-Bench 2 by 7 points, arXiv
   2605.23950). `missing_artifacts` is the honesty field everyone omits. Verifier: ~30 lines that
   reject a run folder missing any of the four parts or any variable the protocol declares.
   Simpler scaffolds win on MLE-bench (AIDE beat OpenHands and MLAgentBench, arXiv 2410.07095), so
   the experiment contract stays a file convention plus a verifier, never a framework.

E. Do not do (evidence says skip): asking the agent to add tests mid-fix (test volume did not
   change outcomes across six models, arXiv 2602.07900); spec-driven development as a
   productivity claim (position paper only, arXiv 2609.00252; METR 2025 found experts 19 percent
   slower while believing 20 percent faster); reviewer-agent scores as verdicts; canary strings
   as contamination control; graph memory stores.

## Standing facts every session needs

- Fable 5.1 prompting guide (fetch it, do not recite):
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1
  The `/fable-prompting` seed skill is the filtered index over that guide: it says which sections a
  prompt can act on and which ones Claude Code already injects.
  The lead is now Fable 5.1, so these deltas describe the lead's own behavior, not just the workers'.
  Key deltas vs Fable 5: fewer user-facing progress updates; may issue one tool call per turn in
  coding loops; denser prose (the "mannered prose" line is the fix); less chat formatting; may end
  a turn early or ask permission on long async work; over-delivers extras and tests; rewrites whole
  files for small edits; at xhigh/max can draft a long deliverable twice. Claude Code already
  injects the autonomy block, the Delivering work block, the progress-updates line, and the
  batching nudge, so never duplicate those in a CLAUDE.md or a worker brief.
- Opus 4.8 workers are literal: spell out scope, front-load the whole task in one prompt, never
  write "only report high-severity" (they drop real findings), name when to fan out. A worker
  cannot read the lead's thinking blocks, so every brief must be self-contained.
- Worker prompts must forbid: git commit/add/checkout/stash, whole-file rewrites, edits outside
  the named files, em dashes. Workers never commit; the lead commits.
- Paste these guide guards into a worker brief when they apply (the guide's own wording):
  - Editing: "The number of tokens used to edit files is best minimized, all else being equal.
    Therefore, when it will not affect the end result, try to surgically edit a file rather than
    rewrite the entire thing."
  - Extras: "If, while working or testing, you find a pre-existing bug, a performance concern, or
    behavior the task doesn't mention, don't fix, optimize or extend it in this change unless the
    requested behavior cannot work without it; report it as a follow-up in your summary. Commit
    tests only where the task asks for them or this repository already keeps tests for this kind of
    change. This is about extras only: implement every behavior the task asks for, completely."
  - Prose: "Please remove all mannered prose."
  - Evidence: a sentence claiming something passes, builds, or was re-checked must be preceded in
    the same turn by the command and its output; else write "not verified" and name the command.
- Parallel workers may edit disjoint files in one checkout; the concurrent-checkout-guard only
  fires on git index writes.
- Workflow scripts: `agent(prompt, {model: "claude-opus-4-8[1m]", effort: "xhigh", label})`.
  `Date.now()` throws inside scripts. Worker reports over ~4000 characters get truncated in
  transit; ask for the rest in chunks under 3500 characters, or use a schema.
- Verification before every commit: `uvx pytest -q bin/tests` (system python3 has no pytest; uvx
  also catches the ruff-on-PATH case), `bin/verify-template.sh`, `bin/harness-smoke.sh`. Each of
  the first two takes about five minutes; run them in the background.

## Open decision for Samyak (does not block starting session 2)

Your 2026-09-03 answers name a NEW distbench dogfood render and an experiment-contract results-sync
step. No session 2 to 6 owns them. Confirm they are post-session-6 validation work, or assign them
to a session.

## Sessions

Each session: pick the execution shape, set `/goal`, commission workers on disjoint files, then a
verifier stage, read the diff yourself, send any fix back to a worker (never edit it yourself), run
the four checks, commit on the branch, append to the Execution log, stop.

Path rule: every bare `skills/...`, `agents/...`, and `workflows/...` path in the session blocks
lives under `cultivation/marketplace/sam-cc-setup/`. Resolve them there. Full copies also exist
under `soil/`; never edit or grep-match those, they are salvage decoys.

### Session 2: prompts to Fable 5.1 (plugin edits, direct to main allowed; seed edit needs branch `fix/audit-s2-prompts`)

Also do every item tagged "session 2" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 2a and 2b on the same branch and log both.

Goal (paste as the `/goal` condition, run in auto mode): every item tagged for session 2 is implemented, the plugin edits are committed to main and the seed `AGENTS.md.jinja` edit is committed on `fix/audit-s2-prompts`, and this session's transcript shows `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", `bin/harness-smoke.sh` printed PASS, and the session 2 Verify grep returned only historical citations. No file outside the session 2 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

Files and exact changes:

1. `cultivation/marketplace/sam-cc-setup/skills/align-prompt/SKILL.md`
   - Frontmatter lines 5 and 8: "Claude Fable 5" becomes "Claude Fable 5.1"; "a Fable 5 session" becomes "a Fable 5.1 session".
   - Dispatch table (lines 36-43) becomes:
     ```
     | First token | Route |
     |-------------|-------|
     | `fable`, `fable5.1`, `f51` | Prompt alignment, target Fable 5.1 |
     | `4.8` | Prompt alignment, target Opus 4.8 |
     | `fable-plan` | Plan mode, target Fable 5.1 (see below) |
     | anything else, or empty | Ask which of the two targets. Do not default. |
     ```
     Delete the `4.7` row and its refusal paragraph (lines 50-54).
   - Section 3 heading for Fable becomes ``**Claude Fable 5.1 (`claude-fable-5-1`)** - steer briefly and let it find the path.`` Keep the five existing bullets. Append this block after them:
     ```markdown
     Five deltas are new in 5.1. Fold the relevant ones into the prompt you emit:

     - **Targeted edits.** When the task edits files, append: "The number of tokens used to
       edit files is best minimized, all else being equal. Therefore, when it will not affect
       the end result, try to surgically edit a file rather than rewrite the entire thing."
     - **Scope of extras.** When the task is an open-ended implementation, append: "If, while
       working or testing, you find a pre-existing bug, a performance concern, or behavior the
       task doesn't mention, don't fix, optimize or extend it in this change unless the
       requested behavior cannot work without it; report it as a follow-up in your summary.
       Commit tests only where the task asks for them or this repository already keeps tests
       for this kind of change. This is about extras only: implement every behavior the task
       asks for, completely."
     - **Prose.** When the deliverable is written English, append: "Please remove all mannered
       prose."
     - **Long deliverables.** Recommend `high` effort, not `xhigh`, for a single long document
       or a complete code file: at `xhigh` and `max` the model can draft the deliverable once
       in thinking and again in the reply.
     - **Progress updates.** 5.1 writes fewer user-facing updates than 5. If the run is attended,
       say so in the prompt; never add a line suppressing narration.

     Do NOT add the autonomy block or the tool-batching nudge to a prompt destined for a Claude
     Code session. Claude Code already injects both as turn-scoped system messages, and a second
     copy is paid input tokens for no behavior change.
     ```
   - Reword the `reasoning_extraction` bullet (lines ~99-100) to: "Avoid asking it to echo, transcribe, or explain its internal reasoning as response text. This tripped a `reasoning_extraction` refusal on Fable 5; the 5.1 guide does not list it among the remaining safeguard triggers, so treat this as unconfirmed for 5.1 and cheap insurance rather than a hard rule."
   - Plan mode: "5" becomes "5.1" at lines 130, 131, 132, 139, 148, 156; output filename `<stem>-fable5.md` becomes `<stem>-fable51.md` at lines 26-27 and 154; confirmation line at 156 matches. Sketch labels at 162 and 167 become "Aligned (Fable 5.1)". Citation at line 176 becomes the 5.1 guide URL above.
   - Final step: append one line to the last step of `skills/writing-plans/SKILL.md`: "When the plan will be handed to a fresh session, run `/align-prompt fable-plan <path>` before writing the handoff."
2. `cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/templates/workflow-model-notes.md`: replace lines 1-13 and 23-29 with the text in the synthesis file under "Prompts chunk B1" (Fable 5.1 vs Opus 4.8 table: instruction detail, subagents; Fable 5.1-only bullets: targeted edits, extras stay out, fewer progress updates, long deliverables at high). Keep lines 15-21 and 31-34. Also fix `bootstrap-cc-setup/SKILL.md:40` which says "the Fable 5 / Opus 5 guides invert on".
3. `cultivation/marketplace/sam-cc-setup/skills/agent-team/teammate-prompt.md:14`: replace the bullet with:
   ```
   - When a reading is ambiguous, make the routine judgment call yourself, state the
     assumption in your milestone report, and keep going. Escalate to the lead only when
     two readings would lead to materially different work, or when the next step is
     destructive or outside your scope. A step you have decided on is something to run,
     not to announce.
   ```
   Delete the "think hard" lines at `advisor-prompt.md:26` and `teammate-prompt.md:20`.
   In `agent-team/SKILL.md` rewrite the whole Model policy block (lines 32-34) to: "Every teammate runs Opus 4.8 (`claude-opus-4-8[1m]`). Effort is the dial, not the model: xhigh for Opus execution workers, planners, and critics; a Fable advisor or lead runs at `medium` or `high` only, never higher. Use only Opus or Fable." Delete the line that permits Sonnet for a mechanical subagent (line 33); the Opus-or-Fable-only rule removes that carve-out. This also fixes the bare `Opus` alias and the old "medium to high for execution workers; xhigh for the advisor" split, which contradicts Samyak's xhigh-workers rule and the Fable effort cap. Verify: `grep -niE "sonnet|medium to high" cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md` returns nothing.
4. `seed/AGENTS.md.jinja` (branch): after `## Gotchas` add:
   ```markdown
   ## Editing discipline

   Prefer a surgical edit to a whole-file rewrite when the end result is the same.
   Keep the change to what the request needs. A pre-existing bug, a performance concern, or
   nearby cleanup you notice while working is a follow-up line in your summary, not a change
   in this diff. Commit tests only where the task asks for them or this repo already keeps
   tests for that kind of change.
   A verification claim must carry its evidence. A sentence asserting that something passes,
   builds, or was re-checked must be preceded in the same turn by the command and its output.
   If you did not run it, write "not verified" and name the command that would verify it.
   ```
   Delete gotcha lines 20-21 (case-insensitive grep; count skills by marker). Keep lines 19 and 22.
   `bin/rendered_harness_contract.py` may assert AGENTS.md content; update its expectations and tests.
5. `skills/critique-swarm/SKILL.md:51`: drop "verbose preambles" from agent 2's mandate (the skill is deleted in session 3, so skip this if session 3 runs first).
6. Never-Sonnet rule: re-pin `cultivation/marketplace/sam-cc-setup/agents/build-validator.md:5` and `.../agents/read-only.md:5` from `model: sonnet` to `model: claude-opus-4-8[1m]`. Session 1 kept these on Sonnet for cheap mechanical checks; Samyak's 2026-09-03 rule forbids Sonnet, so they move to Opus. Update the contract check if it asserts these agents' models. Verify: `grep -rniE "model:\s*sonnet" cultivation/marketplace/sam-cc-setup/agents` returns nothing.

Verify: `grep -rn "Fable 5[^.]" cultivation/marketplace/sam-cc-setup | grep -v "5\.1"` returns only historical citations; every `model:` line under `cultivation/marketplace/sam-cc-setup/agents` is an Opus or Fable id; four checks green.

### Session 3: review consolidation (plugin, direct; weight gate rebaseline touches bin, branch `fix/audit-s3-reviews`)

Also do every item tagged "session 3" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 3a and 3b on the same branch and log both.

Goal (paste as the `/goal` condition, run in auto mode): every item tagged for session 3 is implemented and committed (plugin edits direct to main where allowed, the weight-gate rebaseline on `fix/audit-s3-reviews`), and this session's transcript shows `python3 bin/skill_listing_weight.py` printed the new rebaselined total, `grep -rniI critique-swarm cultivation/marketplace/sam-cc-setup` returned nothing (the skill dir is deleted; the `cultivation/marketplace/UPGRADING.md` changelog keeps its historical line and is out of this scope), `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 3 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

1. Delete `cultivation/marketplace/sam-cc-setup/skills/critique-swarm/` and update its live references in the plugin only: `cultivation/marketplace/UPGRADING.md` (skill count, count by `find -name SKILL.md`, plus one changelog line noting the removal). A repo-wide `grep -rni critique-swarm` also matches dated records (the `docs/` handoffs and specs, this handoff, and copies under `soil/`); do NOT edit those, they are history, not live config. Within `cultivation/marketplace/sam-cc-setup` the only reference is the skill dir itself, so deleting it clears the scoped grep.
2. `cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js`: add `model: "claude-opus-4-8[1m]"` to every agent call (lines 162-199 and the verify/converge calls); change the verifier fan-out to run only for BLOCK findings, not HIGH. Also set `cultivation/marketplace/sam-cc-setup/agents/plan-reviewer.md:6` to `effort: high` (report repair; `high` suits an agent that emits a full revised plan, and session 1 left it at `xhigh`).
3. `skills/auto-phase/SKILL.md` steps 2c-2d: run session-critique once at the end of the plan, or per stage only when the stage touched `seed/`, hooks, or `copier.yml`.
4. Merge the three "does it run" checks: keep `agents/build-validator.md` as the single command-running gate; fold the unique checks from `skills/validate/SKILL.md` Wave 1 and `verify-app` into it; make `validate` a thin caller of build-validator; guard ruff/mypy on the presence of `pyproject.toml`.
5. `skills/ship/SKILL.md` stage 4: skip push and PR when `git diff --name-only main` is docs-only (paths under docs/ or *.md outside seed/ and cultivation/).
6. `disable-model-invocation: true` test: add it to `skills/ship/SKILL.md` only, restart, run `/ship critique-only`. If it runs, add it to auto-phase, gen-spec, codex-review, codex-plan-review. If not, record the failure in the Execution log and leave descriptions as they are.
7. `bin/skill_listing_weight.py`: also sum `agents/*.md` descriptions and each `workflows/*.js` `meta.description`; rebaseline the budget once and record the new number in `bin/verify-template.sh` stage 8.

Verify: `python3 bin/skill_listing_weight.py` prints the new total; four checks green.

### Session 4: new hooks (branch `fix/audit-s4-hooks`)

Also do every item tagged "session 4" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 4a and 4b on the same branch and log both.

Goal (paste as the `/goal` condition, run in auto mode): every item tagged for session 4 is implemented and committed on `fix/audit-s4-hooks`, each new hook is wired in `seed/.claude/settings.json`, added to `CLAUDE_HOOK_ROUTES` in the contract, and covered by a test, and this session's transcript shows each new hook run against a synthetic stdin envelope with the expected output, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 4 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

All under `seed/.claude/hooks/`, each wired in `seed/.claude/settings.json`, each added to `CLAUDE_HOOK_ROUTES` in `bin/rendered_harness_contract.py` and covered by a test in `bin/tests/test_seed_claude_hooks.py`.

1. `write-rewrite-guard.sh`, PreToolUse matcher `Write`, timeout 5. Advisory only. If `tool_input.file_path` exists and has 80 or more lines, print `{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"<path> already exists with <n> lines. Prefer Edit; use Write only if most of the file is changing."}}` and exit 0. Threshold from `REWRITE_GUARD_LINES`, default 80.
2. `post-compact-reinject.sh`, SessionStart matcher `compact`, timeout 5. Prints to stdout: "Post-compaction reminders: 1. Finish the whole task; do not stop early or ask permission for work already requested. 2. Keep changes to what the task asks; report pre-existing bugs as follow-ups. 3. Surgically edit files. 4. Batch independent tool calls. 5. Re-read HANDOFF.md if present and run the verify command it names before claiming anything."
3. Evidence-with-claim gate inside `stop-verify-gate.sh` (BLOCK, per Samyak). Read the last assistant message from `transcript_path`. If it matches, case-insensitive, any of `verified|all tests pass|tests pass|passes|confirmed|re-verified|PASSED`, require that the same turn contains a Bash tool_result whose output contains a matching success token (`PASSED`, `passed`, `OK`, `exit 0`, or the same phrase). If not, exit 2 with: "Final message claims verification without command output in this turn. Run the check and paste its output, or write 'not verified'." Skip when the message also contains "not verified". Keep the whole script under 160 lines; bash -n clean.
4. `bash-length-advisory.sh`, PreToolUse matcher `Bash`, timeout 5. Advisory: if the command is over 400 characters, additionalContext "Long command (<n> chars). Split it into steps so each result is readable." (Rejected: counting separators; 6 percent false positives on 4,271 real commands.)
5. `seed/.codex/hooks.json`: add a second matcher group `^apply_patch$` routing to `pre-tool-policy.py`, and extend the policy to deny patches touching `.env*`, sealed result namespaces, and generated outputs. `seed/.codex/rules/default.rules:43-54`: add `-f` and `--force-if-includes` so `git push -f` is forbidden, not prompt.
6. Add a gotcha line to `seed/CLAUDE.md.jinja`: "`/goal` is unavailable when `disableAllHooks` or `allowManagedHooksOnly` is set; never set either in a rendered project."

Verify: run each hook with a synthetic stdin envelope and show output; four checks green.

### Session 5: repair sync and promote inventions (branch `fix/audit-s5-sync`)

Also do every item tagged "session 5" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 5a and 5b on the same branch and log both.

Goal (paste as the `/goal` condition, run in auto mode): every item tagged for session 5 is implemented and committed on `fix/audit-s5-sync`, distbench itself is not edited, and this session's transcript shows `python3 bin/agent_parity/parity.py check` printed green, the attach-mode test output is pasted, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 5 items is changed; do not push or open a PR. Or stop after 35 turns and say what is left.

1. `seed/.agents/skills/catchup/SKILL.md`: add a gather step that reads `.copier-answers.yml` `_commit`, runs `git ls-remote --tags gh:samyakjhaveri/loam` (or reads `VERSION` when offline), and prints a red flag when `_commit` is not the latest tag or not a tag at all.
2. `copier.yml`: add question `project_kind` (choices: python, typescript, research, mixed, other). Gate `pyproject.toml.jinja` on python or research or mixed. The `pyright-lsp` line lives in `seed/.claude/settings.json`, which has no `.jinja` suffix and is copied verbatim, so first rename it to `seed/.claude/settings.json.jinja` (Copier strips the suffix) to make that one line conditional, and update every path reference to it in the contract and tests. Update `bin/rendered_harness_contract.py` and tests for both `project_kind` branches. Verify: render with `project_kind=typescript` and confirm no pyright-lsp line.
3. Parity bill of materials: copy `~/Desktop/distbench/agent-parity.toml` and `~/Desktop/distbench/scripts/agent_parity/parity.py` (plus `adapters/`) into `bin/agent_parity/`. Read them first and strip distbench-specific entries. Author `seed/agent-parity.toml` listing every seed skill, agent, and hook with a Codex mirror or `unsupported: reason`. Wire `python3 bin/agent_parity/parity.py check` as verify-template stage 9.
4. Validate-sentinel trio: copy `~/Desktop/distbench/.claude/hooks/run-validate-waves.sh`, `sentinel-cleanup.sh`, `pre-commit-gate.sh` into `seed/.claude/hooks/`, generalize (no distbench paths, ruff/mypy guarded on pyproject), wire sentinel-cleanup as PostToolUse Edit|Write, pre-commit-gate as PreToolUse Bash on `git commit`. The sentinel file is `.validation_passed`, gitignored. Contract inventory and tests as in session 4.
5. Attach mode: `bin/loam-attach.sh <dir>`: copies `seed/.claude/settings.json`, `seed/.claude/hooks/`, the `.gitignore` hook lines, and writes a `.claude/settings.local.json` that enables the sam-cc-setup plugin from `cultivation/marketplace`; refuses if `<dir>/.claude/settings.json` exists unless `--force`. Test on `~/Desktop/teach-parbench` (no git repo there; the script must handle that) and show a hook firing.
6. distbench: do NOT edit it. Add `docs/plans/2026-09-03-distbench-archive-note.md` stating it is archived at commit 410c07e, its Loam pin is v3.6.2 (dead), and which inventions were promoted in this session.
7. Root `AGENTS.md:63-64` (the case-insensitive-grep and count-by-marker gotchas) overlap `seed/AGENTS.md.jinja`: add a mirror check next to `_check_distribution_mirrors` in the contract, or delete the root copies. Note session 2 item 4 removes these two lines from the seed, so after that lands the overlap is root vs CLAUDE.md, not root vs seed. Fix the `bin/harness-smoke.sh:39-45` comment vs behavior mismatch (make a dirty seed exit 1).

Verify: `python3 bin/agent_parity/parity.py check` green; four checks green; attach test output pasted.

### Session 6: research and autonomy layer (branch `fix/audit-s6-research`)

Also do every item tagged "session 6" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 6a and 6b on the same branch and log both.

Goal (paste as the `/goal` condition, run in auto mode): every item tagged for session 6 is implemented and committed on `fix/audit-s6-research`, and this session's transcript shows the item-1 dry run (a contract with done-when `test -f results/demo.jsonl` ended a headless `/goal` loop within 5 turns), each new hook run against a synthetic envelope with the expected output, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 6 items is changed; do not push or open a PR. Or stop after 40 turns and say what is left.

Note on the item-1 dry run: only one goal is active per session, so run that inner `/goal` test as a headless `claude -p "/goal <condition>"` invocation, not as a second interactive goal inside this session. The docs confirm `claude -p "/goal ..."` runs the goal loop to completion in one invocation.

1. Experiment contract. Template `seed/experiments/README.md` (starts empty, explains the contract) and `cultivation/marketplace/research-lane/templates/CONTRACT.md` with fields: question, done-when (a shell command that exits 0), budget (turns, dollars, hours), seeds, protocol hash. Hook `seed/.claude/hooks/experiment-contract-gate.sh`: Stop hook that, when `experiments/*/CONTRACT.md` exists and `EXPERIMENT_ACTIVE=<name>` is set, runs the done-when command and blocks turn end on non-zero with the command output. Commit gate: refuse `git commit` that stages `results/*.jsonl` without a sibling `manifest.json` carrying seed, git SHA, hostname, GPU, container digest, command line. Dry run: a contract with done-when `test -f results/demo.jsonl` must end a `/goal` loop by itself within 5 turns.
2. Research bundle `cultivation/marketplace/research-lane/`: move the six templates from `cultivation/wip/research-assets/seed-docs/` (they render EMPTY, one heading and one sentence each), and vendor the skills `rigor`, `experiment-loop`, `research-writing`, `ml-paper-writing` from `~/.claude/skills/` after `bin/vet-skill.sh` passes on each (`hypothesis-tree` already ships in `cultivation/marketplace/sam-cc-setup/skills/`, so move or reference it from there, do not re-vendor from `~/.claude/skills/`, where it does not exist). Add `cite-resolve` hook: PreToolUse on Edit|Write of `*.bib`/`*.tex`, a new cite key must exist in `refs/resolved.json`; ship `bin/cite-resolve.sh` wrapping a DOI or arXiv lookup (CrossRef or arXiv API, no model). Add a `.claude/loop.md` template: "Continue the current experiment sweep. Run the next unrun configuration in protocol.md, append the result row, commit. If every configuration has a row, say 'sweep complete' and stop."
3. Ideation chain: new skill `cultivation/marketplace/sam-cc-setup/skills/ideate/SKILL.md` with five steps (frame with one-question-at-a-time interview, diverge with named directions and ordinary role frames, react with one disposable artifact, ground with the external-anchor gate, plan on one survivor). For Diverge, either vendor `adhd` from `~/.claude/skills/adhd` into the bundle after `bin/vet-skill.sh` passes, or inline its stratified-divergence step; do not reference `adhd` as a shipped skill, because it does not ship in the template. Fold `unknowns` into step 1 and `surprise-me` into step 2 (both ship in `sam-cc-setup/skills/`; leave them in place and mark them as parts of `ideate`). For step 4, either inline a grill prompt or reference the `mattpocock-skills:grilling` plugin skill; there is no `grilling` skill in `sam-cc-setup`. Add the grounding gate text: "Before ranking, each surviving idea needs one external anchor: a real citation, a command that would test it, or a cost or time estimate with its basis. Ideas with no anchor are cut, not ranked low. Do not score novelty."
4. Reading room: skill `read` that takes a paper URL or PDF, a repo path, or a plan file and writes a one-page reading with every claim labeled Verified, Likely, or Relayed, plus appends to `RESOURCES.md` with status adopted, candidate, rejected, or reference. Test on arXiv 2603.15164.
5. One CLAUDE.md line for loops in `seed/AGENTS.md.jinja`: "Loops: use /goal for a verifiable end state in one session, a Routine for laptop-closed schedules, a saved dynamic workflow for fixed protocols, and always name the terminating check in the condition itself."
6. Weekly harness watch: write `docs/routines/harness-watch.md` with the prompt for a Monday Routine that reads code.claude.com/docs/en/whats-new and diffs CHANGELOG.md, then opens a PR with new features, adopt/ignore/watch verdicts, exact diffs for adopts, falsified assertions, and a staleness list. Samyak creates the Routine himself with `/schedule`.
7. Memory staleness: SessionStart hook line `find ~/.claude/projects/*/memory -name '*.md' -mtime +60 | head -5` printed as "stale memory candidates".
8. D5 diagrams line (report decision D5, the one unshipped piece). Add one line to
   `seed/AGENTS.md.jinja`: "Diagrams in docs and PRs are inline mermaid; do not maintain drawio or
   excalidraw sources for internal design." One line, no other change.

After session 6, the harness-evals idea (skill-creator benchmark on 8 to 12 real prompts, with and without each research skill) is the next session.

## End-of-session review

After each session a fresh Claude Fable 5.1 session reviews the work with no memory of the implementation session.
The fresh context is the point: the reviewer sees the committed diff, not the reasoning that produced it, so it judges the result on its own terms.
This is a real review, not self-critique theater, because the diff is new input the reviewer never saw; it is the same reason the report keeps plan-review-fanout and drops score-only self-critique.

Run the reviewer at `high` effort. It is a Fable model, so `high` is the cap anyway, and a single written deliverable is best at `high` (guide's long-output note).
The reviewer reports; it does not edit code.
Paste this prompt into a fresh session:

```text
You are a Claude Fable 5.1 reviewer with no context from the session that did this work. Review
session <N> of the Loam harness audit. Read, in this order:
1. docs/HANDOFF-2026-09-03-audit-sessions.md: session <N>'s block, every Gap review and Research
   addition item tagged for it, and the report decisions it implements.
2. The committed diff: run `git log --oneline main..<session-branch>`, then
   `git diff main...<session-branch>`. For a docs-only session on main, diff the session's commits.
3. The session's Execution log entry.
Judge the work on four axes and cite file:line for each finding:
- Correctness and software-engineering best practice.
- Samyak's intent and the session's stated scope: every tagged item done, nothing out of scope.
- Taste: minimal diff, no over-engineering, reads like the surrounding code.
- Thoroughness: edge cases, and the four checks actually run with output in the commit or the log.
Confirm the diff matches the report recommendation for this session; flag any drift.
Run the four checks yourself: `uvx pytest -q bin/tests`, `bin/verify-template.sh`,
`bin/harness-smoke.sh`, and the session's Verify line. Paste the output; a claim without output is
"not verified".
End with a verdict: SHIP, FIX (list the exact fixes), or REWORK (say why). Write the review to
docs/reviews/2026-09-<dd>-session-<N>-review.md. Please remove all mannered prose.
```

If the verdict is FIX or REWORK, Samyak or a follow-up implementation session applies the fixes; the review file is the record.

## Execution log

- 2026-09-03 session 1 DONE on branch `fix/audit-s1-stop-the-bleeding`, merged to main as c7952db via PR #5 (CI verify passed). Session 2 branches from main.
  Changed: plugin agents pinned to `claude-opus-4-8[1m]` at xhigh (consistency-checker and
  test-synthesizer moved off Sonnet; build-validator and read-only stay Sonnet at high);
  techdebt skill pinned; seed settings.json lost its model key, cat and echo moved to ask, ruff
  hook got a 10 s timeout; local template lost its model key; contract now FAILS on any model
  key; ruff-after-edit falls back to the PATH binary only on "No module named ruff";
  stop-verify-gate gained a HEAD guard, stdout-only diff check, and session scoping via
  transcript_path; root .codex is now a symlink to seed/.codex (the old root config is saved at
  the session scratchpad, keys approval_policy=never, sandbox_mode=danger-full-access,
  model_reasoning_effort=high); HANDOFF-2026-09-01 corrected. Gate: uvx pytest 151 passed;
  verify-template PASSED; harness-smoke PASS.
  Open follow-ups: two agents (build-validator, read-only) still use `model: sonnet`; the
  never-Sonnet rule (2026-09-03) now moves them to Opus 4.8 in session 2 item 6. The
  test-synthesizer sample validator only accepts short aliases; stop-verify-gate still probes
  ruff with `--version` (unify with the ruff-after-edit pattern in session 4).
  Codex round 1 (gpt-5.6-sol, high, read-only): FIX FIRST with three High on the stop gate and
  one Medium on the sample validator; all four applied in a second commit: unborn branch is
  gated against git's empty tree instead of skipped; files mutated through Bash commands that
  name a dirty path count as session edits; `git diff --check` is scoped to the session set;
  the sample validator accepts pinned `claude-*` ids. Transcript in
  `.claude/codex-reviews/2026-09-03-fix-audit-s1-stop-the-bleeding.md` (gitignored). Round cap
  reached; no second round.
  NEXT SESSION: session 2, Claude Fable 5.1 lead, branch `fix/audit-s2-prompts` from `main`.
  Run it under `/goal` in auto mode with session 2's Goal condition; workers are Opus 4.8 at xhigh.
  When it commits, run the End-of-session review in a fresh Fable 5.1 session. Never rebase or force-push.
- 2026-09-03 session 2 DONE. Lead Claude Fable 5.1 at high; workers Claude Opus 4.8 (`claude-opus-4-8[1m]`) at xhigh via three dynamic workflows (five editors with one adversarial checker each and a completeness critic; one lead feedback round; one Codex-fix round).
  Commits: `eaf1aca` on `main` (plugin half, items 1, 2, 3, 5, 6); `c05229f` on `fix/audit-s2-prompts` (seed half, item 4); `d85a0da` on `fix/audit-s2-prompts` (three accepted Codex findings, plugin files).
  Shipped: fresh-context review returned SHIP (`docs/reviews/2026-09-03-session-2-review.md`); its two low nits closed in `997b002`; branch merged to main as `58983df` via PR #6 (CI verify passed). No Gap review or Research addition item is tagged for session 2, so the scope was the six listed items.
  Gate, run after every commit: `uvx pytest -q bin/tests` 153 passed; `bin/verify-template.sh` PASSED; `bin/harness-smoke.sh` PASS; the Verify grep `grep -rn "Fable 5[^.]" cultivation/marketplace/sam-cc-setup | grep -v "5\.1"` returns one line, a quotation from the Fable 5 guide at align-prompt/SKILL.md:97 kept on its original citation; every `model:` line under `agents/` is `claude-opus-4-8[1m]`; the agent-team Sonnet grep is empty.
  Decisions the lead made from the repo:
  (a) align-prompt quotes: four quoted phrases attributed to the Fable 5 guide do not appear in the 5.1 guide (worker and checker both fetched it), so they keep the `[prompting-claude-fable-5]` key; a new `[prompting-claude-fable-5-1]` key carries the API-parameter citation and the new 5.1 block. Retargeting a quote to a document it is not in would be a false citation.
  (b) The synthesis file's "Prompts chunk B1" is a one-line spec, not paste-ready text, so the model-notes worker wrote the Fable 5.1 vs Opus 4.8 table from both fetched guides; the two rows are instruction detail and subagents. The reasoning_extraction and context-countdown bullets were dropped from the template.
  (c) Never-Sonnet consistency inside the same skill: the Sonnet carve-out was also removed from `agent-team/teammate-prompt.md:36` and `agent-team/scenarios.md:8`, and the test-synthesizer sample validator no longer accepts `sonnet` or any `claude-*` id outside `claude-opus-*` and `claude-fable-*`. These go one step past item 3 and item 6 as written; the rule they enforce is binding.
  (d) build-validator and read-only keep `effort: high`; item 6 asked for the model re-pin only, and neither is an execution worker.
  (e) `/goal` was not set: the lead cannot invoke a slash command from inside the session. The lead ran the same loop by hand and stayed under the 30-turn cap.
  Codex round 1 (gpt-5.6-sol, high, read-only, scope `dfa9803..HEAD`): FIX FIRST, five High, two Medium. Accepted three: the `claude-*` validator hole, the two "advisor runs at higher effort" lines (false once Opus workers are at xhigh and a Fable advisor is capped at high), and the five scenario worker rows at `high` (moved to xhigh per the workers-at-xhigh rule). Rejected: "Every teammate runs Opus 4.8" vs the Fable advisor clause (the sentence is Samyak's mandated text and already says "Use only Opus or Fable"); a model pin on nested Explore subagents (the policy sentence governs them); keeping `fable5`/`f5` aliases (the handoff replaced the table); gating the writing-plans line by target model (the handoff mandated the line). Transcript in `.claude/codex-reviews/2026-09-03-fix-audit-s2-prompts.md` (gitignored). Round cap: one round used; no second round.
  Residuals for the reviewer: align-prompt/SKILL.md:145 "do not target Opus 5" is pre-existing and still true; `seed/AGENTS.md.jinja:1` has a pre-existing em dash in the title line, untouched; the writing-plans line sends every fresh-session plan through `fable-plan`, which matches the lead-is-Fable model but has no Opus 4.8 branch.
  NEXT SESSION: session 3, Claude Fable 5.1 lead, branch `fix/audit-s3-reviews` from `main` at `58983df` or later. Item 5 of session 2 already trimmed critique-swarm, which session 3 deletes. A worktree for it exists at `/private/tmp/loam-audit-s3-reviews` holding `main`; fast-forward it before branching.
- 2026-09-03 session 3 DONE. Lead Claude Fable 5.1 at high; workers Claude Opus 4.8 (`claude-opus-4-8[1m]`) at xhigh via six dynamic workflows (two editors with one adversarial checker each and a completeness critic in rounds 1 and 2, then four one-file fix workers). Worktree `/private/tmp/loam-audit-s3-reviews`, fast-forwarded to `74a2a58` before committing.
  Commits: `0ba0553` on `main` (items 1 to 6, gap item 4, plugin and docs); `87f802f` on `fix/audit-s3-reviews` (item 7, bin). Not pushed; no PR. No Research addition item is tagged for session 3.
  Gate, run on the final tree: `uvx pytest -q bin/tests` 155 passed (153 plus the two new weight tests; the run predates the last build-validator.md edit, which no test reads); `bin/verify-template.sh` PASSED; `bin/harness-smoke.sh` PASS; `python3 bin/skill_listing_weight.py` prints `sam-cc-setup [gated]: 2704 tokens (18 skills listed, 8 manual, 6 agents, 1 workflow)`; `grep -rniI critique-swarm cultivation/marketplace/sam-cc-setup` empty; `node --check` on plan-review-fanout.js clean; `grep -rniE '\bwave' cultivation/marketplace/sam-cc-setup` empty.
  Item 6 test: a copy of the ship skill with `disable-model-invocation: true` was loaded as a throwaway plugin (`claude -p --plugin-dir <copy> --max-turns 1 "/s3test:ship critique-only"`); the init message listed `s3test:ship` and the reply started stage 1, so the slash command runs with the flag. anthropics/claude-code#26251 and #38969 are CLOSED (2026-02-20). The flag is on ship, auto-phase, gen-spec, codex-review, codex-plan-review; the two codex skills' Trigger paragraphs no longer claim the flag blocks the command.
  Decisions the lead made from the repo:
  (a) Item 4: the global `~/.claude/agents/verify-app.md` (not in the plugin since 2026-08-29) was folded into build-validator as check 9, the smoke path with the BLOCKED guardrail; build-validator also runs the project test suite and `bin/validate.sh` so validate could become a thin caller with nothing lost except the informational TODO/FIXME grep, dropped on purpose. ruff and mypy are guarded on pyproject.toml.
  (b) Item 5: ship resolves the default branch like codex-review does instead of hardcoding `main`.
  (c) Item 7: the script sums name plus description for agents and workflows, the same basis as skills; the ratchet is the measured total rounded up to the next 50 (2704 to 2750).
  (d) No plugin version bump; the README release loop bumps it at release. UPGRADING.md gained an "Unreleased" entry instead.
  (e) Gap item 4: `docs/findings/FINDINGS.md` created with two open rows (stop-verify-gate ruff probe, owner session 4; writing-plans fable-plan line with no Opus 4.8 branch). codex-review Step 3 appends there.
  (f) Stage 7 (stale counts) failed on `docs/specs/seed-skill-promotion.md:13`, a live inventory line; changed 27 to 26. This is the one file outside the session 3 list.
  (g) `/goal` was not set: the lead cannot invoke a slash command from inside the session; the loop ran by hand.
  Codex round 1 (gpt-5.6-sol, high, read-only, on the uncommitted diff): FIX FIRST, two High, three Medium, one Low. Accepted two: piped `pytest | tail` masked the exit code (build-validator now captures to a file and reads the exit code), and the mypy fallback did not match its availability check. Rejected: the `.claude/baselines.json` verify-app contract (never shipped; README line 30), the two procedural findings (the log and the branch split are done at the end), and the TODO grep (decision a). Round cap reached; transcript at the session scratchpad.
  Residuals for the reviewer: pre-existing em dashes in `agents/test-synthesizer.md` (lines 100, 150-159) and `agents/code-architect.md` description, untouched; several `bin/tests/*.py` trip ruff I001 under ruff 0.16.6 (verify-template runs unittest, not ruff); the plugin version stays 0.7.0 while two sessions changed plugin content.
  Shipped: fresh-context review returned SHIP (`docs/reviews/2026-09-03-session-3-review.md`); its five Low findings are rows in `docs/findings/FINDINGS.md`; branch merged to main as `d56d008` via PR #7 (CI verify passed; the CI unit-test stage took 12 minutes against 3 minutes on PR #6 with only a 95-line test file added, so watch the next run before blaming the code).
  NEXT SESSION: session 4, Claude Fable 5.1 lead, branch `fix/audit-s4-hooks` from `main` at `d56d008` or later. The tracker `docs/findings/FINDINGS.md` has two rows owned by session 4 (stop-gate ruff probe; plan-review-fanout agents at xhigh).
- 2026-09-04 session 4 DONE. Lead Claude Fable 5.1 at high; workers Claude Opus 4.8 (`claude-opus-4-8[1m]`) at xhigh via two dynamic workflows (4a: four editors, one test writer, one adversarial checker each, a completeness critic; 4b: five editors, one test writer, one checker each, a critic), plus three one-worker feedback rounds. Split into 4a and 4b on the same branch as the ticket allows.
  Commits on `fix/audit-s4-hooks`: `5aee49a` (4a: items 1 to 6, FINDINGS row 1); `e8df75d` (4b: Research addition B, Research F cwd rule, FINDINGS row 3); `b49e744` (accepted Codex findings); and one docs commit after it for the tracker rows and this log. Not pushed; no PR.
  Gate, run on the final tree: `uvx pytest -q bin/tests` 217 passed; `bin/verify-template.sh` PASSED; `bin/harness-smoke.sh` PASS; every new hook was run against a synthetic stdin envelope in the session transcript with the expected output (advisory JSON, the claim block, the apply_patch denials, the hygiene list, the audit line with exit code, the tamper block, and a real cosmic-ray run that listed eight survivors on the changed line only and left the checkout and worktree list unchanged).
  Shipped hooks (all under `seed/.claude/hooks/`, wired in `settings.json`, in `CLAUDE_HOOK_ROUTES`, each with tests): write-rewrite-guard.sh, bash-length-advisory.sh, post-compact-reinject.sh, harness-hygiene.sh (SessionStart startup|resume|clear), skill-usage-log.sh (PreToolUse Skill), test-tamper-scan.sh and mutation-gate.sh (PreToolUse Bash, fire only on a `git commit` command), bash-audit-log.sh moved to PostToolUse plus PostToolUseFailure with exit code and experiment name; stop-verify-gate.sh gained the blocking evidence leg and the ruff-after-edit fallback. Codex: `hooks.json` routes `^apply_patch$` to `pre-tool-policy.py`, which denies patches to `.env*`, sealed results (a `results` segment under `runs` or `experiments`), and generated outputs; `default.rules` forbids `git push -f` and `--force-if-includes`.
  Decisions the lead made from the repo:
  (a) Command capture uses `EXPERIMENT_ACTIVE=<name>` (session 6's convention) and writes to `experiments/<name>/logs/commands/<UTC date>.log`; session 6 may re-point the path. The seed `.gitignore` ignores `logs/`, so these logs are local unless session 6 changes that.
  (b) The mutation gate uses cosmic-ray (8.7.0 verified on Python 3.12), because mutmut 3 has no diff scoping and cosmic-ray's `cr-filter-git` limits mutants to changed lines. cosmic-ray mutates source in place, so the gate runs inside a throwaway linked worktree overlaid with the staged index; the checkout is never touched. Opt-in by tool presence; `[tool.mutation-gate] test-command` and `timeout` in pyproject.toml; justify survivors under a `Mutants:` line.
  (c) Both commit gates fire on the regex `\bgit\s+(-\S+\s+(\S+\s+)?)*commit\b`, not the concurrent guard's broader pattern, so `git grep commit` and `git log --grep=commit` do not trigger them. The concurrent guard is unchanged.
  (d) The hygiene scan checks bare filenames only when they carry a known extension, are not a version string, and (the one heuristic) have no uppercase stem unless tracked, so `v2.0.0`, `asyncio.gather`, and `Node.js` are not reported. Config-key spans ending in a colon are skipped. Loam's own root prints nothing.
  (e) The tamper scan strips trailing comments before the skip and mock regexes and ignores the trivial literals 0, 1, -1, 0.0, 1.0, True, False, None, and empty strings in the expected-equals-new-return clause.
  (f) The evidence leg counts Bash, Agent, Task, and Workflow tool results as evidence (a lead that delegates verification reports the subagent's pasted output through those tools), requires a whole-word success token, and rejects a result that also carries `N failed`, `FAILED`, `FAIL`, or `Traceback`.
  (g) `/goal` was not set: the lead cannot invoke a slash command from inside the session; the loop ran by hand under the 30-turn cap.
  (h) `sam-cc-setup:codex-review` is manual-only since session 3, so the Codex round ran through the `codex:rescue` plugin skill (read-only, fresh thread); no `.claude/codex-reviews/` transcript was written.
  Codex round 1 (read-only, scope `4b4719b..HEAD`): FIX FIRST, two High, one Medium, four Low. Accepted three: the evidence token matched "2 failed, 5 passed"; delegated-agent results did not count as evidence; a run killed at the hook timeout leaked a worktree entry (now pruned at the next run). Rejected: narrowing the claim trigger (the word `passes` is in Samyak's item 3 text); relaxing the expected-equals-new-return clause (it is Research B verbatim and pairs with the new failing-test-first rule; Samyak's go/no-go); the trigger regex matching `git commit` inside a quoted string (any string match shares this; the guards bound the cost). Round cap: one round used; no second round.
  Residuals for the reviewer: the claim trigger word `passes` blocks a doc-only turn that uses it as a verb until the message says "not verified" or a check is pasted; the tamper scan's literal clause fires on `return 42` plus `assert f() == 42` in one commit, by design; the sealed-results and generated-outputs families match those segment names anywhere in a path; bash-audit-log writes one entry per command, and a multi-line command stays multi-line; harness-hygiene reports a backticked command that is not installed on the box (a true dead reference, but noisy for optional tools); `cr-filter-git` skips every mutant in a filename containing a space (upstream); the FORBIDDEN_RENDERED_PATHS entry `post-compact-recovery.sh` names an old hook and is unrelated to the new `post-compact-reinject.sh`.
  Review: the fresh-context review returned FIX (`docs/reviews/2026-09-04-session-4-review.md`; four Opus workers, then an ultracode workflow of 17 Opus 4.8 skeptics at xhigh). Two High: both commit gates read the index before `git add -A && git commit` or `git commit -a` staged anything; the mutation gate never scored a newly added file. Five Medium: the Bash tool_response has no `exit_code`, so the audit log read `exit=?` on every clean command; the claim trigger had no word boundaries ("unverified" blocked); no cosmic-ray baseline; the tamper scan flagged words inside strings and would have blocked two of this session's own commits; one bad transcript line disabled the claim leg. The nine fixes landed in `de9e107` with 13 new tests (230 passed, verify-template PASSED, harness-smoke PASS); the four Low residuals are rows in `docs/findings/FINDINGS.md`. Not pushed; no PR.
  NEXT: open the PR for `fix/audit-s4-hooks`; then session 5 (`fix/audit-s5-sync`) from `main` after the merge. Session 5 item 4 wires `pre-commit-gate.sh` on `git commit`; reuse decision (c)'s regex and the index-copy staging rule from `test-tamper-scan.sh`.
- 2026-09-04 session 4c DONE (residuals). Lead Claude Fable 5.1 at high; workers Claude Opus 4.8 (`claude-opus-4-8[1m]`) at xhigh via one dynamic workflow (three editors, one test worker, one adversarial checker each, a completeness critic) plus one feedback round.
  Commits `fdf88f5` and `9096eac` on `fix/audit-s4-hooks` close the four Low rows the fresh-context review left open (FINDINGS rows dated 2026-09-04) and the by-design notes worth acting on: one audit-log line per command with newlines escaped; fenced code blocks in agent docs path-checked on the first token per line, absolute paths skipped, single-token backticked words unchecked by design; the skill log's unused `name` fallback removed; the `--force-if-includes` rule justification corrected (the flag is a no-op without `--force-with-lease`); the mutation gate sweeps scratch worktrees named `mutation-gate.*` older than 30 minutes so a run killed at the hook timeout heals on the next run; both commit gates read the `Test-changes:` or `Mutants:` marker from a `-F` or `--file` message file; the contract probes all three apply_patch deny families; tests point `cwd` at a second repo, assert the cosmic-ray config, cover malformed JSON and zero survivors, share `_payload` and `_stage` through `HookFixtureCase`, and `TestTamperScanTests` is now `TamperScanTests`.
  Gate on `9096eac`: `uvx pytest -q bin/tests` 246 passed; `bin/verify-template.sh` PASSED; `bin/harness-smoke.sh` PASS; the hygiene scan, audit log, tamper-scan `-F` escape, and policy probes ran against synthetic envelopes in the session transcript.
  Decision: the fence scan checks only the first token of a fence line because later tokens are arguments and usually placeholders (`/path/to/dataset.csv`); a dead script path in argument position goes unreported, accepted for precision. Loam's own test commits need a `Test-changes:` line when a fixture literally contains skip or patch text; `fdf88f5` carries one.
  Codex round 2 (read-only, scope `668e436..HEAD`): SHIP, one Medium (a quoted `-F "msg.txt"` path kept its quote characters, so the justification file was never read and the commit was over-blocked; fixed in `9096eac` with a BSD-and-GNU-portable sed, since an `-E` backreference is inert on macOS sed) and one note (an orphaned cosmic-ray child that outlives a SIGKILLed hook could still be running when the 30-minute sweep removes its worktree; low impact, the parent is already dead). All four round-1 Low rows confirmed closed by direct execution. Round cap reached.
  NEXT: push `fix/audit-s4-hooks` and open its PR (seed behavior goes through a PR); after the merge, session 5 on `fix/audit-s5-sync` from `main`; session 5 item 4 (`pre-commit-gate.sh`) should reuse the commit regex and the index-copy staging rule from `test-tamper-scan.sh`.
