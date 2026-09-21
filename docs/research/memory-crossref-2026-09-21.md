# Memory cross-reference, 2026-09-21: the Codex memo against the accepted design, MEM-01, and current source

Samyak pasted a Codex-written memory-system design on 2026-09-20 and asked for it to be cross-referenced and implemented.
Four Opus 4.8 workers read primary sources at `main` `fad17cb`.
Fable judged.
The review page with the picks is https://claude.ai/artifact/Y8tZwgh8GcSgWb5HqQhuuB.

## Verdict in four lines

The memo is sound and mostly already built into Loam's plan.
It is a second draft of the same research thread that produced `memory-design-2026-09-03.md`, and that design is ticketed as MEM-01 (#154).
Ten of its thirteen research claims match their sources to the decimal; nothing is fabricated.
It never cites the three strongest counter-results in the 2026-09-03 design, so two of its ten levels are cut and one mechanism is replaced.

## What was read

| Worker | Read | Result |
|---|---|---|
| Loam survey | seed, hooks, skills, factory, `bin/`, issues #152 to #154, transcripts on the Mac | Loam ships no memory. MEM-01 is the level 1 and 2 layer, Claude-only. 123 Claude transcripts (578 MB) and 1,945 Codex rollouts already exist as raw evidence. |
| Claude Code docs | 12 claims against code.claude.com and two Anthropic engineering posts | 9 verified, 3 partly. SessionEnd and Stop deliver `transcript_path`. Transcripts are deleted after 30 days by default. |
| Codex source | 10 claims against openai/codex at `a866315` | All 10 verified. Codex hooks use Claude's event names and stdin JSON shape. |
| Research | 13 claims via Consensus, Exa, arXiv, project pages | 10 verified, 1 partly, 2 corrected. |

## Research claims

| Claim | Verdict | Note |
|---|---|---|
| LongMemEval-V2 table (42.8 raw, 51.0 raw + notes, 74.9 AgentRunbook-C) | verified | Every cell matches the project page. arXiv 2605.12493. |
| AgentRunbook-C V2 numbers with GPT-5.6 Luna | partly | The system exists (`agentrunbook_c_v2.py`). The numbers appear nowhere public. The "leaner harness" wording fits a different project, ThinHarness. Not load-bearing for Loam. |
| RecMem, up to 87% write-cost cut | verified | ACL 2026 Findings, arXiv 2605.16045. |
| ReasoningBank, +4.6 pts SWE-Bench Verified | verified | ICLR 2026. Measured on Gemini 2.5 Flash, a weak actor. |
| MemTrace, evidence retrievable 10x more often than missing | verified | arXiv 2606.17328. |
| Mastra topK sweep and Observational Memory 84.23 | verified | Vendor numbers. |
| Letta usage vs generation split; Context Repository | verified | Vendor private benchmark. |
| Supermemory token and tool-call numbers | verified | Benchmark is xAFS, system is SMFS. |
| "Ping" and the MemHarness 76.4 vs 70.1 ablation | verified | Ping Lin, pinglin.tw, a40-labs/memory. |
| Mem0 semantic + keyword + entity; Graphiti; Memory-R1 | verified | |
| GPT-5.6 Luna, Sol, Terra exist | verified | The memo doubted its own names. They are real (openai.com/index/gpt-5-6). |
| Anthropic "context rot" phrase | partly | "Smallest possible set of high-signal tokens" is verbatim. "Context rot" is the concept, not the phrase. |

Eight strong papers the memo did not cite, from Consensus: Reflexion (2303.11366), the Zhang 2024 memory survey (2404.13501), Memp (2508.06433), Evo-Memory (2510.06133), Xiong on experience-following (2505.16067), EvolveR (2510.14496), A-Mem (2502.12110), and the OpenDataBox twelve-system evaluation (2606.24775).

## The memo against the design Loam already has

| Memo level | 2026-09-03 design | MEM-01 (#154) | What the evidence says |
|---|---|---|---|
| 1 Native baseline | Level 0 | kept as is | Agree. CLAUDE.md under 200 lines, skills lazy, auto memory on. |
| 2 Immutable evidence archive | Level 1 | `mem-capture.sh` on SessionEnd, PreCompact, Stop | Agree. Zero model calls. Needed because Claude deletes transcripts after 30 days. |
| 3 SQLite + BM25 + embeddings | Level 2 ripgrep, then Level 3 on a named miss | `memsearch` = ripgrep | Ripgrep first. MemDelta: the embedding choice alone moved the verdict by 6.2 points, so embeddings are an experiment, not a default. The sandbox also blocks pip. |
| 4 Trajectory notes | Level 4, cheap model, gated on 5 repeat errors a month | out of scope (no model call) | The highest-return step, verified. The memo's cheap-model writer breaks the model law. See MEM-03. |
| 5 Recurrence-triggered consolidation | human-gated promotion ladder | weekly recurring-errors report | Agree on the trigger. Disagree on who runs it: a model rewriting a bank rises then falls below no-memory (Faulty Memories, arXiv 2605.12978). A human promotes. |
| 6 Lessons become skills | sections 5.2 and 5.3, curated only | not yet | Agree. One-shot self-generated skills give no benefit on average (SkillsBench). |
| 7 Applicability gate | section 5.4 | APPLICABLE / STALE / UNVERIFIED rule in `mem-recall.sh` | Agree. Already in. |
| 8 Temporal fields | cards carry ENV and VERIFIED-ON | not yet | Take one line: SUPERSEDES on a note. Never edit old notes. |
| 9 Agentic retrieval | Level 7 | not yet | Agree. Only when single-pass search leaves known evidence unfound. |
| 10 Graph, RL, learned policy | never until 3 to 7 plateau | not yet | Agree. |
| Background LLM consolidation every 10 to 30 sessions | rejected | rejected | Cut. This is the rewriting step finding 1 measures as harmful. Both harnesses do it natively; keep those sandboxed in git as a cache. |
| SamMemEval: 100 questions, 5 models, 7 configs | weekly signals, no eval suite | weekly report | Right idea, wrong size. Take the four-way split (capture, retrieval, application, outcome) as three counts in the weekly report. |

## Where the memo is weaker

1. Missing counter-evidence.
   It cites none of Faulty Memories (rewritten memory decays), MemDelta (verbatim retrieval matches Mem0 at one fiftieth the write cost), or Ping's result that claude-sonnet-5 gains +1.4 points from an experience bank at p = 0.5.
   Those three are the reason Loam measures before it builds.
2. Model choice.
   It writes notes with a Luna or Haiku-class model.
   The law is Opus or Fable only.
   The fix is cheaper than a model call: the session that did the work writes its own note (MEM-03).
3. Embeddings from day one.
   Needs a model or an API key, needs pip, and the embedding choice is as large as the architecture effect.
   Ripgrep first; a paraphrase miss you know is there three times in a month is the named failure for FTS5 plus two embeddings tested side by side.
4. Eval size.
   The seven-configuration, five-model matrix is a research programme.
   Loam's rule is that a piece earns its keep by one measured signal: the same error in two sessions is a capture or recall failure.
5. One unsourced table.
   The AgentRunbook-C V2 numbers.

## What the memo adds that is worth taking

- Cross-harness with one script.
  Verified in Codex source: SessionEnd, Stop, SessionStart, and Compact carry the same stdin JSON fields (`session_id`, `transcript_path`, `cwd`).
  MEM-01 excluded Codex only because `features.hooks = false` in the seed.
  That becomes MEM-02.
- Trajectory notes as the first real gain, written by the session's own model, append-only, only when a trigger fires.
  That becomes MEM-03.
- Measure four things, not one.
  Three grep counts in the weekly report cover capture, retrieval, and application.
  Folded into MEM-02 because MEM-01 was mid-run with a frozen prompt when the pick landed.
- Temporal supersession.
  One SUPERSEDES line on a note keeps the append-only rule and still lets a stale note lose.
- "Current repository state beats memory" is already the applicability gate.

## The plan

Three tickets, one store.

- MEM-01 (#154): capture, recall, memsearch, weekly report.
  Zero model calls, Claude-only, about 120 lines of shell.
  Running in the factory since 2026-09-21T04:51Z.
  Gate to the next level: the first weekly report.
  Same error string in two sessions with no note is the named failure.
- MEM-02 (#161): Codex capture through the same script.
  `hooks = true` in `seed/.codex/config.toml`, a repo hooks file that registers the MEM-01 scripts on the same events, the Codex rollout line shape handled in `mem-capture.sh` for the INDEX line, the three counts in `mem-weekly.sh`, the orphan `.pyc` deleted.
  Blocked by MEM-01 merged.
  Why `hooks = false` was set is not recorded; git history shows only the file move (`1f312fe`).
- MEM-03 (#162): self-written trajectory note behind a Stop-hook gate.
  A Stop hook exits 0 unless `stop_hook_active` is false, no note exists for the session, no ask marker exists, and the transcript shows a trigger (a `git commit` tool call, a failing check followed by a passing one, or a user correction).
  Then it prints the note template to stderr and exits 2, once.
  The session writes the note with the Write tool to `$STORE/notes/<repo>/<date>-<sid8>.md`.
  The factory already uses this exit-2 Stop pattern for done checks.
  Blocked by MEM-01's first weekly report showing a repeat error with no note.
  If the report is clean for a month, do not build it.

Not taken: SQLite, FTS5, embeddings, and rank fusion (wait for a named ripgrep miss, then test two embeddings); background LLM consolidation; SamMemEval at full size; Mem0, Letta, Graphiti, Zep, Memory-R1, MemHarness; rewriting MEM-01 to fold in MEM-02 and MEM-03.

## Picks, approved 2026-09-21

- P1 Run MEM-01 as written. Already running; the base line already read `fad17cb`.
- P2 Three grep counts in `mem-weekly.sh`. Folded into MEM-02.
- P3 File MEM-02 (#161), blocked by MEM-01.
- P4 File MEM-03 (#162), blocked by MEM-01's first weekly report.
- P5 This document, and the ordering note in `docs/architecture-working/tickets/README.md`.
- P6 Codex native memories in Samyak's own config: skipped.

## Risks

- The Stop capture in MEM-01 may miss the last turn: the transcript is written asynchronously. SessionEnd catches it.
- Why Codex hooks are off in the seed is not recorded. MEM-02's done check covers the behavior, not the reason.
- Finding 7 of the 2026-09-03 design predicts the whole layer may show near zero gain for a Fable or Opus worker. That is the point of measuring first.
- No worker ran any pipeline. Every claim is read from source at the commits named above.
