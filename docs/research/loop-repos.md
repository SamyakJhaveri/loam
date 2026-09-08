# Loop and factory repos: what to steal

Research index for the nine outside repos read while designing the Loam agentic software factory.

## Five loop frameworks (2026-09-06)

Carried over verbatim from `.superpowers/lean-v3/research/loop-repos-fit.md`, which resolves SamyakJhaveri/loam#19.
That note read each repo's README, LICENSE, entry point, and loop code from a shallow clone, primary sources only.
Activity counts came from `gh api repos/<owner>/<name>` on 2026-09-06.

### Recommendation

Adopt none of the five as a dependency.
Use plain Claude Code `/goal` plus a shell supervisor and borrow three specific mechanisms.

Two of the five, loopy and loop-engineering, contain no code that ever invokes an agent, so they cannot drive anything.
agent-apprenticeship is a two-shot grading pipeline for training data whose judge is locked to an OpenAI-shaped API, so it cannot host Fable 5.1.
loopx explicitly rejects `/goal` because `/goal` judges completion from the transcript, and its only real enforcement path is the exact `PreToolUse` matcher-and-substring-denylist hook Loam forbids, on top of a 163 MB checkout and a hard Node 22.6 requirement.
LongHorizon-Harness is the closest technical fit but sets `bypassPermissions` for every role, replacing Claude Code's native permission layer with a launch-time deny-list its own docstring admits is not a sandbox, decides completion by regex over bilingual prose, has no token or dollar cap, and can end an unattended run early when the manager routes `Next: ask` with no human channel attached.

The supervisor to write instead is small: a bash `while` loop per ticket that runs `claude -p` with `--model` and `--effort` for the worker, runs the ticket's done checks as real commands and reads their exit codes, then invokes a second fresh-context `claude -p` as the Fable 5.1 judge, appending one JSON line per round to a per-ticket run directory.
Borrow three things.
Per-role model, agent, and effort resolution from LongHorizon-Harness's `_resolve_role_model` in `cli.py`.
The ledger circuit breaker from loop-engineering's `tools/loop-context/src/context-manager.ts`, including its normalized `errorSignature()` trigram comparison to detect a stuck loop.
The lock-guarded daily spend ledger from loop-engineering's `daily-spend.ts`, which gives the dollar cap that none of the runnable candidates provide.
That is perhaps two hundred lines of shell and one small state file.

### Fit table

Needs are the Lean v3 execution-ticket loop: completion from a ticket's done checks, Claude Opus 5 at low or medium effort as worker with Claude Fable 5.1 as a fresh-context judge, headless Ubuntu for days, one loop per ticket, clear logs, and no tool-matcher hook or free-text safety parsing.

| Need | loopx | LongHorizon-Harness | agent-apprenticeship | loop-engineering | loopy |
|---|---|---|---|---|---|
| Completion from a ticket's done checks | Partial. Deterministic gate, but keyed to quota slots and evidence records, not to a ticket body. Rejects `/goal` by design. | Partial. Three-field auditor verdict, but every field regex-scraped from prose, and done checks must be restated as prompts. | No. Fixed two-shot pipeline with a rubric, not a done-check condition. | Partial. Circuit breaker is deterministic, but the pass or fail verdict is unparsed free text. | No. Model self-declares an outcome in prose. |
| Opus 5 worker plus Fable 5.1 judge | No. Does not assign models. Roles are capabilities, models come from the harness. | Yes, best in set. Per-role `agent`, `model`, `reasoning_effort`, passed as `--model` and `--effort`. | Partial. Worker is a CLI, judge is forced to an OpenAI-shaped API model. | No. Every agent is `model: inherit`. | No. No model plumbing at all. |
| Headless Ubuntu for days | Yes for the control plane, but it ticks nothing itself and needs Node 22.6. | Mostly. `--no-dashboard` works, but a `Next: ask` route with no human channel stops the run. | Partial. Non-interactive, resumable batches, but the loop is two attempts deep. | Scaffolding only. You supply the driver. | No. Interactive, pauses for approvals. |
| One loop per ticket | Yes. Goals are first-class with a per-goal registry. | Yes. One run per invocation with its own state directory. | Yes. One run per prompt. | Yes by convention, no enforcement. | No concept of a run. |
| Clear logs | Yes. JSONL event and run logs under `~/.codex/loopx`. | Yes, best in set. Ten-plus JSONL and JSON files per run plus per-role trajectories. | Yes. Progress events, per-iteration folders, batch checkpoints. | Partial. Run log, state file, metrics aggregation. | No. Nothing written by default. |
| No tool-matcher hook, no free-text safety parsing | Fails on the hardening path. `PreToolUse` with `matcher: "*"` plus a substring destructive-Bash denylist. Optional, off by default. | No hook, but sets `bypassPermissions` for every role and calls its own deny-list not a sandbox. | No hook, but passes `bypassPermissions` and classifies failures by stderr string matching. | Passes. No hooks, path globs plus git worktrees, does not bypass permissions. | No hook, but all safety is model-interpreted prose. |
| Install weight | Heavy. 163 MB, 3,700 files, hard Node 22.6 requirement. | Light. Five Python deps, Python 3.10+. | Light. Three Python deps. | Medium. Node only, sixteen npm packages. | Near zero. |
| Maintained | Very active, last commit 2026-09-07. | Active but quiet since 2026-08-20. | Quiet since 2026-07-06. | Active, last commit 2026-09-06. | Quiet since 2026-07-07. |
| License | Apache-2.0 | MIT | MIT | MIT | MIT |

### Per-repo disqualifier

#### huangruiteng/loopx

A deterministic, no-LLM control plane that ticks nothing itself; Claude Code's own `/loop` drives it over a generated `.claude/loop.md`.
Its adapter README rejects `/goal` because `/goal` judges completion from the transcript, a direct conflict with the Lean v3 design.
Its hardening path, `loopx/claude_goal_mode/hooks/hooks.json`, is a `PreToolUse` hook with `matcher: "*"` whose `decide` function substring-matches a `DESTRUCTIVE` denylist against Bash commands, the two things Loam rules out.
Off by default, installed only with `install.py --harden`.
Apache-2.0, 163 MB, 3,700 files, hard Node 22.6 requirement.

#### AMAP-ML/LongHorizon-Harness

The closest fit: eight roles each take independent `agent`, `model`, and `reasoning_effort`, resolved through `_resolve_role_model` in `cli.py` and passed as `--model` and `--effort`.
Disqualified because `adapters/claude_permissions.py` sets `permission_mode="bypassPermissions"` for every role and replaces the native permission layer with a launch-time tool deny-list its own docstring says is not a sandbox.
Completion is regex over bilingual prose (`parse_role_manager_next_step`, `_AUDIT_HEADER_RE`), there is no token or dollar cap, and `_human_gate` stops an unattended run on `Next: ask`.
README benchmark numbers (WeaveBench 51.8 to 80.7, Terminal-Bench 2.1 69.7 to 77.2) were not verified.

#### ray-r-ren/agent-apprenticeship

A training-data pipeline, not a long-horizon driver: the sequence is a hardcoded two-shot, baseline attempt then one revision, with `max_improvement_loops` unused and `retry_limit` a dead parameter.
Mentor roles go through `openai_structured.py`, and per-role model overrides apply only when the provider is openai, so the judge can never be a second CLI agent and Fable 5.1 does not fit.
It also passes `--permission-mode bypassPermissions` to Claude.
Quiet since 2026-07-06.

#### cobusgreyling/loop-engineering

A pattern library plus npm CLIs; no code anywhere spawns claude, codex, or an API client, and the only driver is a cron GitHub Action calling deterministic Node scripts.
Every shipped agent file sets `model: inherit`, so worker and judge are the same model, a hard fail against the Opus 5 worker plus Fable 5.1 judge requirement.
Its safety posture is the cleanest of the five (path globs in `gate.yaml`, ephemeral worktrees, no hooks, no bypass), and its `context-manager.ts` breaker (defaults: 10 iterations, stagnation 3, frustration 3, no-progress 5, similarity 0.85) and `daily-spend.ts` are the two pieces worth borrowing.

#### Forward-Future/loopy

Not a framework: a Cloudflare Worker hosting a catalog of prompt playbooks plus a 301-line Markdown skill.
There is no entry point, no runtime, no structured completion signal, no retries, no caps, no logging by default, and no model plumbing.
`run.md` tells the model to ask the user for its run boundary, which an unattended loop cannot do.
All safety is model-interpreted prose.

## Four pattern repos (2026-09-07)

These four were read for mechanisms, not as candidate dependencies.

### Leonxlnx/unlazy

An anti-laziness skill: acceptance gates are written before implementation, then a Node checker executes and re-executes them.
MIT, 3,150 stars, 207 forks, last push 2026-09-03.

The state is a markdown ledger, one `GATES.md` solo or `.unlazy/<scope>/` with a per-leaf ledger when orchestrated.
A gate is four lines:

```
- [ ] G1: <observable outcome measured directly from the artifact>
  CHECK: node scripts/verify-outcome.mjs
  EXPECT: outcome verification passed
  EVIDENCE: pending
```

The done rule and the honesty rule are the mechanism:

> Count a runnable gate as met only when its process exits zero, its `EXPECT:` matches combined output, and its automatic evidence carries the current versioned definition digest.
> Do not silently remove an impossible gate. Add `ABANDON: <id> <non-empty reason>` and surface it as a required handoff.
> Remember that the checker proves only the declared command oracle. It cannot infer whether an English gate title describes what the command actually measures.
> Exercise a negative check against a known positive control before trusting absence.
> Measure figures independently; do not copy a supplied number into `EXPECT:` as its own proof.

Verification runs in four layers: leaf self-check, parent re-verify which re-executes the oracle, branch integration, and an optional structural backstop.
Layer one is labelled self-certification, and `--status` explicitly does not count as re-execution.

Steal:
- `CHECK:` and `EXPECT:` gates authored before implementation, because our verify stage currently reads prose acceptance criteria.
- `ABANDON:` with a mandatory reason that exits non-zero, because three of four Loam loops stalled on exactly the silent-scope-shrink failure this prevents.
- Parent re-verification, because our loop trusts worker reports today.
- The gate-honesty checklist as a plan-reviewer rubric, because a gate that cannot fail is worse than no gate.
- `gate-lint`, because catching a vacuous oracle at authoring time is cheaper than certifying it at report time.
- Append-only `status.log` instead of regenerating a plan file, which is a direct token saving.

Reject:
- The Depth Tree `tree N` arithmetic, which the repo itself retracts as unreproducible design history.
- The lease, claim, and dispatch-wave concurrency machinery, which is coordination weight a single-repo template does not need.
- The Stop hook, which collides with our existing stop-verify-gate and embeds machine-specific absolute paths.
- The `Tier: judgment|mechanical` field, which admits it is non-binding and duplicates model routing we already fixed by policy.

Maps to: ticket (one ledger per ticket with an `OWNS:` glob set), verify (the checker and the four layers), judge (abandonment surfacing and the final re-measure-every-number audit).

### Spielewoy/autoprompt-skill

An explicit-invocation orchestration skill running 24 named personas across nine coding agents.
MIT, 1,014 stars, 68 forks, pushed 2026-09-07.

Governance is three files and a named ban on more:

> New-run governance is exactly: `PROMPTS.txt`, append-only `=== PROMPT N ===` blocks; `ROADMAP.md`, canonical executable roadmap; `GATELOG.md`, append-only transitions, verdicts, artifact hashes, and resume frontier.
> Do not create new-run governance-only `BRIEF.md`, `PLAN.md`, `AGENTS.md`, `COVERAGE.md`, `BACKLOG.md`, `ANCHOR.md`, `bucketlist.md`, `intake.md`, `scope-map.md`, or per-angle scope files.

Briefs carry a pointer, not the mission text:

> MISSION POINTER: read the exact prompt ledger before acting; stop if its hash or byte length differs.
> path=<PROMPTS.txt> hash=sha256:<64 hex> bytes=<UTF-8 byte length> nonce=<RUN-NONCE>

The judge is default-FAIL and re-derives from the original text:

> Re-derive EVERY ask from the ORIGINAL MISSION text ALONE. Each ask starts NOT-DONE, flips to DONE only on opened, quoted evidence.
> The ONLY non-fix exit is an evidenced WONTFIX-with-reason closure for a genuine non-defect, not a silent backlog or a severity downgrade.
> E2E: scope=<pass|gap> prompt=<pass|gap> flaws=<n> ran=<one phrase of the actual end-to-end exercise>

The `prompt` axis exists to catch a scope drawn too small, which no scope-relative check can find.
Blind assurance agents share no verdict channel, and no agent verifies work it authored.

Steal:
- The `E2E:` machine line, especially the `prompt` axis, because our judge currently grades against the plan and cannot see what the plan omitted.
- Default-FAIL rows that flip only on quoted evidence, because a judge that starts from approval finds less.
- The hash-and-byte-length pointer brief, because it cuts tokens and makes brief drift detectable rather than silent.
- The governance whitelist paired with a blacklist, because that is anti-bloat enforced by the harness rather than by prose.
- `WONTFIX-with-reason` as the only non-fix exit, which is the same rule unlazy reached independently.
- Frontier-tail resume, one line read to restart, because our manager state is a prose log today.

Reject:
- The 24-persona hierarchy, which is governance weight for a solo author and repeats identical boilerplate in every file.
- The opus, sonnet, and haiku alias-filling scheme, which conflicts with the Opus-and-Fable-only rule.
- The 260KB gate script and 89KB PowerShell supervisor, which we could not maintain.
- The hard 95 percent changed-line coverage floor, which does not fit a template whose product is markdown and shell.

Maps to: brief (`PROMPTS.txt`), plan (one canonical roadmap), loop (spawn-all-then-collect under a live ceiling), judge (the tri-axis default-FAIL verdict).

### chenxiachan/thoughtdag

An editable context graph for LLM conversations, desktop app plus CLI, not a factory.
MIT, 364 stars, 35 forks, pushed 2026-09-07.

Its one rule and its research are the parts that matter:

> Wires are the context. What the model sees is exactly what wires into the node. Editing the graph edits the model's memory.
> A wrong statement flows into the replies that come after it and undermines the truthfulness of every later conclusion.
> Deleting the message that introduced the error is often not enough, because the follow-up replies still carry it.

That finding comes from a self-published pilot across nine models and 1,485 runs scored by exact match.
A read-only MCP server indexes local Claude Code, Codex, DeepSeek Harness, and Pi sessions and exposes `why_check`, `why_file`, `find`, and `recall_turn`.

Steal:
- The context-pollution result as a design constraint, because it is the strongest available argument for a fresh context per round and for a judge that re-derives from the brief rather than from an inherited summary.
- The cross-agent session index as an optional tool, because "which past conversation touched this file, and why" is a real gap across Loam's multi-session work.
- Staleness and replay in dependency order with a token estimate shown first, as a model for re-running downstream tickets after an upstream one changes.

Reject:
- The canvas, Session Atlas, PDF reader, and Electron app, which are a human-in-the-loop product with no autonomous loop to borrow.
- The localhost import bridge, which works around a desktop app we will not install.

Maps to: brief and loop hygiene only, as a constraint rather than a component.

### disler/super-simple-software-factory

A skill that stamps deterministic Python workflow scripts into a repo, with agents as bounded nodes inside them.
MIT, 811 stars, 211 forks, last push 2026-08-04.

The thesis is that code owns the graph:

> Deterministic Python owns the graph; coding agents are bounded nodes inside it. Agent proposes, code disposes.
> A known command is code, not an agent. If you can write the invocation down, it belongs in a `kind="code"` phase.
> A failing block does not fail its phase: the runner did its job, the code is what failed.
> Success must be earned, every phase defaults to fail.
> Phases passing is not the same as the run being accepted.

The brief cookbook is the strongest prose in any of the nine:

> The intent is theirs. The precision is yours.
> If you catch yourself improving the idea rather than the sentence, stop.
> <the ask, one imperative sentence, their words where they were specific>
> Where: <files or dirs you verified>
> Done means: <the observable result>
> Out of scope: <what you were tempted to add, named so nobody adds it>

Gates verify the envelope's claims rather than judging the work, and one of them, `verdict_consistent`, refutes a reviewer against itself: an approval that ships blocking items, or a rejection naming no problem, fails without reading the diff.
A parse failure re-prompts the same session with context intact rather than restarting cold.

Steal:
- The four-line brief and the intent-versus-precision rule, which is the highest-value item across all nine repos for our missing brief stage.
- `verdict_consistent`, because nothing currently polices our two judges for self-contradiction.
- "A known command is code, not an agent", because our loop likely spends model turns on work that is already a shell script.
- Verbatim unparsed failure output as the fixer's spec, with no summarizing layer between the error and the fix.
- Phases defaulting to fail plus one call that decides exit code, status, and banner together, which kills the green-banner-over-red-suite bug.
- The lazy-load routing table and its argument that volunteered state is guessed state, spent before you know the task.

Reject:
- The Vue visualizer, roughly 120KB of frontend for a dashboard we do not need.
- The SQLite trace database, at least initially, since the session directory is the record and JSONL plus a status log is enough.
- The Pi and gemini-3.6-flash default roster, which is off-policy here.
- Its in-house Python style rules, which belong to that codebase.

Maps to: brief (near verbatim), ticket (a phase with a real description and declared gates), loop (a bounded fix cycle), verify (code phases plus claim-checking gates), judge (a review envelope policed by a consistency gate).

## Comparison

| Repo | State model | Done criterion | Verification | Anti-laziness | Complexity |
|---|---|---|---|---|---|
| unlazy | Markdown ledgers plus an append-only status log | Every runnable gate exits 0, matches EXPECT, carries a current digest, and nothing is abandoned | Four layers, with the parent re-executing the oracle | ABANDON with a reason exits 1; four passes per leaf; a lint that rejects gates which cannot fail | 4 |
| autoprompt | Three files outside the target repo; resume reads only the gatelog tail | Zero open findings at any severity, usable, coverage floor, a real end-to-end run, zero live subagents | Strict TDD, then concurrent blind review and runtime verification | Default-FAIL judge re-deriving from the mission text; the prompt axis catches a too-small scope | 5 |
| thoughtdag | Canvas graph, human-driven, no loop | None, the human decides | None; instead pilot data on context pollution | Not its problem; it prevents contamination rather than laziness | 2 |
| sssf | Session directory per run plus a typed envelope per agent | Every phase defaults to fail; envelope parses, gates green, one call sets exit code and banner | Deterministic code phases plus gates that check the envelope's claims | Bounded fix loop on verbatim failure; known commands are code; vacuous descriptions rejected | 3 |

## Two convergences

unlazy and autoprompt independently reached the same rule: a requirement leaves the ledger only through a named, reasoned, non-successful exit, never by quiet deletion.
autoprompt and thoughtdag independently reached a second: re-derive requirements from the original text rather than from an inherited summary, and thoughtdag supplies the benchmark evidence for why.

## Fetch method

The four 2026-09-07 repos were read through the GitHub contents API, not a clone.
`raw.githubusercontent.com` is blocked by this sandbox's proxy, returning curl exit 28 and HTTP 000.
The working call is `curl -L "https://api.github.com/repos/OWNER/REPO/contents/PATH" -H "Accept: application/vnd.github.raw"`.
Repository metadata and file trees came from `https://api.github.com/repos/OWNER/REPO` and its `git/trees/main?recursive=1` endpoint.

## Risks

None of the nine repos was executed, so every behavior claim is read from source or documentation rather than observed.
For the four pattern repos I read the shipped prompt and script text, not the 260KB autoprompt gate script, the 207KB ledger checker, or unlazy's 39KB checker, so what those enforce is taken from their docs.
unlazy and autoprompt both make self-reported benchmark claims and both partially disclaim their own numbers.
thoughtdag's context-pollution result is a self-published pilot, not peer-reviewed.
Star counts, fork counts, and push dates were read on 2026-09-07 for the four pattern repos and on 2026-09-06 for the five loop frameworks.
