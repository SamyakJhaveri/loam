# Handoff: Loam audit execution, sessions 2 to 6

> Written 2026-09-03 by the Fable 5.1 audit session for a fresh session with no context.
> Lead model for the next sessions: Claude Fable 5. Workers: Claude Opus 4.8 at xhigh effort, never Fable, never Haiku, Sonnet only for mechanical reads.
> Run each session as a dynamic workflow (the Workflow tool) with the lead deciding between phases.
> Samyak sleeps while this runs. Do not ask him questions that the files below already answer.

## Session-start prompt (paste this into the fresh session)

```text
Read docs/HANDOFF-2026-09-03-audit-sessions.md and run the next unfinished session in its
"Sessions" list, then stop. You are the Fable 5 lead. Workers are Opus 4.8 at xhigh via the
Workflow tool (model "claude-opus-4-8[1m]", effort "xhigh"); never spawn Fable subagents.
Seed behavior, hooks, and copier.yml go on a branch named in the session; docs go direct to main.
bin/verify-template.sh must print "verify-template: PASSED" and uvx pytest -q bin/tests must
be green before you commit (system python3 has no pytest; uvx does). Commit on the branch; do not push and do not open a PR.
Each session block also owns the items tagged for it in the Gap review and Research additions
sections. Update the "Execution log" at the bottom of the handoff when you finish. Please
remove all mannered prose.
```

## Objective and aim

Loam is the Copier template that ships Samyak's Claude Code and Codex harness into every project.
The aim: every project seeded from Loam gives him a research partner that can think, brainstorm,
code, test, and run experiments unattended until a written "done" check passes, with time and
token efficiency, using Fable 5.x as lead and Opus 4.8 as workers.

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
- Workers at xhigh everywhere. Lead is Fable 5 (or 5.1 when he says so).
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
  Fable 5.1. Opus 4.8 executes. The harness sessions in this handoff still run on Fable 5 as he
  asked. Ship this split as prose in the research-lane README, not as a model pin.
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
   the memory index treats Opus 4.8 as the frontier. Propose a diff; Samyak applies it.

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
  Key deltas vs Fable 5: fewer progress updates; may issue one tool call per turn in coding loops;
  denser prose; less formatting; may end early or ask permission; over-delivers extras and tests;
  rewrites whole files; at xhigh/max drafts long deliverables twice. Claude Code already injects
  the autonomy block and the batching nudge, so never duplicate those in CLAUDE.md.
- Opus 4.8 workers are literal: spell out scope, front-load the whole task in one prompt, never
  write "only report high-severity" (they drop real findings), name when to fan out.
- Worker prompts must forbid: git commit/add/checkout/stash, whole-file rewrites, edits outside
  the named files, em dashes. Workers never commit; the lead commits.
- Parallel workers may edit disjoint files in one checkout; the concurrent-checkout-guard only
  fires on git index writes.
- Workflow scripts: `agent(prompt, {model: "claude-opus-4-8[1m]", effort: "xhigh", label})`.
  `Date.now()` throws inside scripts. Worker reports over ~4000 characters get truncated in
  transit; ask for the rest in chunks under 3500 characters, or use a schema.
- Verification before every commit: `uvx pytest -q bin/tests` (system python3 has no pytest; uvx
  also catches the ruff-on-PATH case), `bin/verify-template.sh`, `bin/harness-smoke.sh`. Each of
  the first two takes about five minutes; run them in the background.

## Sessions

Each session: create the branch, run one workflow (implement workers on disjoint files, then one
verifier worker), read the diff yourself, fix what the verifier flags, run the four checks, commit
on the branch, append to the Execution log, stop.

### Session 2: prompts to Fable 5.1 (plugin edits, direct to main allowed; seed edit needs branch `fix/audit-s2-prompts`)

Also do every item tagged "session 2" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 2a and 2b on the same branch and log both.

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
   In `agent-team/SKILL.md:32` change "Every teammate runs Opus" to "Every teammate runs Opus 4.8 (`claude-opus-4-8[1m]`)".
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

Verify: `grep -rn "Fable 5[^.]" cultivation/marketplace/sam-cc-setup | grep -v "5\.1"` returns only historical citations; four checks green.

### Session 3: review consolidation (plugin, direct; weight gate rebaseline touches bin, branch `fix/audit-s3-reviews`)

Also do every item tagged "session 3" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 3a and 3b on the same branch and log both.

1. Delete `cultivation/marketplace/sam-cc-setup/skills/critique-swarm/` and every reference to it (grep -rni critique-swarm across the repo, including README, UPGRADING.md, ship, auto-phase, session-critique, docs). Update skill counts in `UPGRADING.md` (count by `find -name SKILL.md`).
2. `cultivation/marketplace/sam-cc-setup/workflows/plan-review-fanout.js`: add `model: "claude-opus-4-8[1m]"` to every agent call (lines 162-199 and the verify/converge calls); change the verifier fan-out to run only for BLOCK findings, not HIGH.
3. `skills/auto-phase/SKILL.md` steps 2c-2d: run session-critique once at the end of the plan, or per stage only when the stage touched `seed/`, hooks, or `copier.yml`.
4. Merge the three "does it run" checks: keep `agents/build-validator.md` as the single command-running gate; fold the unique checks from `skills/validate/SKILL.md` Wave 1 and `verify-app` into it; make `validate` a thin caller of build-validator; guard ruff/mypy on the presence of `pyproject.toml`.
5. `skills/ship/SKILL.md` stage 4: skip push and PR when `git diff --name-only main` is docs-only (paths under docs/ or *.md outside seed/ and cultivation/).
6. `disable-model-invocation: true` test: add it to `skills/ship/SKILL.md` only, restart, run `/ship critique-only`. If it runs, add it to auto-phase, gen-spec, codex-review, codex-plan-review. If not, record the failure in the Execution log and leave descriptions as they are.
7. `bin/skill_listing_weight.py`: also sum `agents/*.md` descriptions and each `workflows/*.js` `meta.description`; rebaseline the budget once and record the new number in `bin/verify-template.sh` stage 8.

Verify: `python3 bin/skill_listing_weight.py` prints the new total; four checks green.

### Session 4: new hooks (branch `fix/audit-s4-hooks`)

Also do every item tagged "session 4" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 4a and 4b on the same branch and log both.

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

1. `seed/.agents/skills/catchup/SKILL.md`: add a gather step that reads `.copier-answers.yml` `_commit`, runs `git ls-remote --tags gh:samyakjhaveri/loam` (or reads `VERSION` when offline), and prints a red flag when `_commit` is not the latest tag or not a tag at all.
2. `copier.yml`: add question `project_kind` (choices: python, typescript, research, mixed, other). Gate `pyproject.toml.jinja` and the `pyright-lsp` plugin line on python or research or mixed. Update `bin/rendered_harness_contract.py` and tests for both branches.
3. Parity bill of materials: copy `~/Desktop/distbench/agent-parity.toml` and `~/Desktop/distbench/scripts/agent_parity/parity.py` (plus `adapters/`) into `bin/agent_parity/`. Read them first and strip distbench-specific entries. Author `seed/agent-parity.toml` listing every seed skill, agent, and hook with a Codex mirror or `unsupported: reason`. Wire `python3 bin/agent_parity/parity.py check` as verify-template stage 9.
4. Validate-sentinel trio: copy `~/Desktop/distbench/.claude/hooks/run-validate-waves.sh`, `sentinel-cleanup.sh`, `pre-commit-gate.sh` into `seed/.claude/hooks/`, generalize (no distbench paths, ruff/mypy guarded on pyproject), wire sentinel-cleanup as PostToolUse Edit|Write, pre-commit-gate as PreToolUse Bash on `git commit`. The sentinel file is `.validation_passed`, gitignored. Contract inventory and tests as in session 4.
5. Attach mode: `bin/loam-attach.sh <dir>`: copies `seed/.claude/settings.json`, `seed/.claude/hooks/`, the `.gitignore` hook lines, and writes a `.claude/settings.local.json` that enables the sam-cc-setup plugin from `cultivation/marketplace`; refuses if `<dir>/.claude/settings.json` exists unless `--force`. Test on `~/Desktop/teach-parbench` (no git repo there; the script must handle that) and show a hook firing.
6. distbench: do NOT edit it. Add `docs/plans/2026-09-03-distbench-archive-note.md` stating it is archived at commit 410c07e, its Loam pin is v3.6.2 (dead), and which inventions were promoted in this session.
7. Root `AGENTS.md:44-49` duplicates `seed/AGENTS.md.jinja` gotchas: add a mirror check next to `_check_distribution_mirrors` in the contract, or delete the root copies. Fix the `bin/harness-smoke.sh:39-45` comment vs behavior mismatch (make a dirty seed exit 1).

Verify: `python3 bin/agent_parity/parity.py check` green; four checks green; attach test output pasted.

### Session 6: research and autonomy layer (branch `fix/audit-s6-research`)

Also do every item tagged "session 6" in the Gap review and Research additions sections above. If the combined scope exceeds one workflow run, split into 6a and 6b on the same branch and log both.

1. Experiment contract. Template `seed/experiments/README.md` (starts empty, explains the contract) and `cultivation/marketplace/research-lane/templates/CONTRACT.md` with fields: question, done-when (a shell command that exits 0), budget (turns, dollars, hours), seeds, protocol hash. Hook `seed/.claude/hooks/experiment-contract-gate.sh`: Stop hook that, when `experiments/*/CONTRACT.md` exists and `EXPERIMENT_ACTIVE=<name>` is set, runs the done-when command and blocks turn end on non-zero with the command output. Commit gate: refuse `git commit` that stages `results/*.jsonl` without a sibling `manifest.json` carrying seed, git SHA, hostname, GPU, container digest, command line. Dry run: a contract with done-when `test -f results/demo.jsonl` must end a `/goal` loop by itself within 5 turns.
2. Research bundle `cultivation/marketplace/research-lane/`: move the six templates from `cultivation/wip/research-assets/seed-docs/` (they render EMPTY, one heading and one sentence each), and vendor the skills `rigor`, `experiment-loop`, `hypothesis-tree`, `research-writing`, `ml-paper-writing` from `~/.claude/skills/` after `bin/vet-skill.sh` passes on each. Add `cite-resolve` hook: PreToolUse on Edit|Write of `*.bib`/`*.tex`, a new cite key must exist in `refs/resolved.json`; ship `bin/cite-resolve.sh` wrapping a DOI or arXiv lookup (CrossRef or arXiv API, no model). Add a `.claude/loop.md` template: "Continue the current experiment sweep. Run the next unrun configuration in protocol.md, append the result row, commit. If every configuration has a row, say 'sweep complete' and stop."
3. Ideation chain: new skill `cultivation/marketplace/sam-cc-setup/skills/ideate/SKILL.md` with five steps (frame with one-question-at-a-time interview, diverge via adhd with named directions and ordinary role frames, react with one disposable artifact, ground with the external-anchor gate, plan on one survivor). Fold `unknowns` into step 1, `grilling` references into step 4, `surprise-me` into step 2; leave those skills in place but mark them as parts of `ideate`. Add the grounding gate text: "Before ranking, each surviving idea needs one external anchor: a real citation, a command that would test it, or a cost or time estimate with its basis. Ideas with no anchor are cut, not ranked low. Do not score novelty."
4. Reading room: skill `read` that takes a paper URL or PDF, a repo path, or a plan file and writes a one-page reading with every claim labeled Verified, Likely, or Relayed, plus appends to `RESOURCES.md` with status adopted, candidate, rejected, or reference. Test on arXiv 2603.15164.
5. One CLAUDE.md line for loops in `seed/AGENTS.md.jinja`: "Loops: use /goal for a verifiable end state in one session, a Routine for laptop-closed schedules, a saved dynamic workflow for fixed protocols, and always name the terminating check in the condition itself."
6. Weekly harness watch: write `docs/routines/harness-watch.md` with the prompt for a Monday Routine that reads code.claude.com/docs/en/whats-new and diffs CHANGELOG.md, then opens a PR with new features, adopt/ignore/watch verdicts, exact diffs for adopts, falsified assertions, and a staleness list. Samyak creates the Routine himself with `/schedule`.
7. Memory staleness: SessionStart hook line `find ~/.claude/projects/*/memory -name '*.md' -mtime +60 | head -5` printed as "stale memory candidates".

After session 6, the harness-evals idea (skill-creator benchmark on 8 to 12 real prompts, with and without each research skill) is the next session.

## Execution log

- 2026-09-03 session 1 DONE on branch `fix/audit-s1-stop-the-bleeding`, pushed, PR #5 open (https://github.com/SamyakJhaveri/loam/pull/5).
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
  Open follow-ups: two agents still use the bare `model: sonnet` alias by design; the
  test-synthesizer sample validator only accepts short aliases; stop-verify-gate still probes
  ruff with `--version` (unify with the ruff-after-edit pattern in session 4).
  Codex round 1 (gpt-5.6-sol, high, read-only): FIX FIRST with three High on the stop gate and
  one Medium on the sample validator; all four applied in a second commit: unborn branch is
  gated against git's empty tree instead of skipped; files mutated through Bash commands that
  name a dirty path count as session edits; `git diff --check` is scoped to the session set;
  the sample validator accepts pinned `claude-*` ids. Transcript in
  `.claude/codex-reviews/2026-09-03-fix-audit-s1-stop-the-bleeding.md` (gitignored). Round cap
  reached; no second round.
  NEXT SESSION: if `main` does not yet contain this branch, create the session 2 branch FROM
  `fix/audit-s1-stop-the-bleeding` (stacked), or fast-forward main first if Samyak has approved
  the merge. Never rebase or force-push.
