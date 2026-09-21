# Memory design v2, 2026-09-21: five layers, stored where their update rule says

Status: design of record. Picks R1 to R8 approved 2026-09-21 with two changes: Graphify is out of the navigation trial (the graph grows fast and misses edges), and implementation is for later sessions; the plan is `docs/plans/2026-09-21-memory-v2/` (local).
Supersedes the ordering in `memory-crossref-2026-09-21.md` and adds the navigation layer.
Inputs: the Codex memo of 2026-09-20 (`memory-crossref-2026-09-21.md`), the storage criticisms of 2026-09-21, and two Codex briefs from `~/Downloads` (`LOAM-MEMORY-DESIGN.md`, 409 lines, and `codex-loam-agent-memory-brief.md`, 386 lines) naming 37 repositories and 14 papers.
Method: every repository at or above 100 stars was cloned and read from source by an Opus 4.8 worker; every paper claim was checked against the paper; Fable judged.
Rule from Samyak: repositories under 100 stars are out.
Review page with picks: https://claude.ai/artifact/74r3ST5YTYLXmuPHqghaMw

## What the evidence settled

- For a frontier model the measured lever is navigation, not experience.
  A structural repository index with Opus 4.7 held fixed lifted resolve 41.9% to 50.4%, localization 44% to 85%, cut 8 turns, and cost less per solve ("Code Isn't Memory", arXiv 2606.22417).
  A semantic file-retrieval surface cut Claude Code tokens 66% at flat accuracy (Supermemory xAFS, vendor).
- Experience banks move a frontier actor by about zero (Ping Lin, claude-sonnet-5).
  Every positive experience-bank result is on Gemini 2.5, Sonnet 4, Haiku 4.5, or DeepSeek.
- Memory a model rewrites decays (Faulty Memories, GPT-5.4 100% to 54% on solved problems).
- A rules file from accepted corrections showed 0% recurrence of ruled-against errors in a deployment.
- The best model acts correctly on a stale memory 55% of the time; when memory fails, the evidence was retrievable ten times more often than missing (MemTrace).
  Use, not retrieval, is the bottleneck.
- Sizes measured on this Mac: 123 Loam transcripts are 150 MB, mean 1.2 MB, 71% envelope metadata, gzip 4x.
  Full content gzipped is about 150 MB a year.
- The runner already holds 80 MB of Claude sessions and 137 MB of Codex sessions and no store.

## The five layers

| Layer | Stored | Synced how | Loaded at start | Ticket |
|---|---|---|---|---|
| 1 Rules | repo, committed: AGENTS.md, gotchas, corrections | git | AGENTS.md (about 200 tokens) | exists |
| 2 Navigation artifacts | repo, committed: `graph.json`, `GRAPH_REPORT.md` or `MAP.md`; indexes rebuilt per machine | git for artifacts; indexes never synced | nothing; opened on demand | NAV-01 |
| 3 Experience | per-user store: traces gzipped a year, INDEX.md and notes forever, handoff.md, reports; keyed by repo remote name | bare git remote on jhaveris, scrubbed before commit | manifest under 1,000 tokens | MEM-01 to MEM-05 |
| 4 Research records | repo, committed markdown with a schema: decisions, experiments, handoffs, claims; index rebuilt per machine | git | fenced brief, capped 10,000 chars | REC-01 |
| 5 Transparency | the manifest and the labels | n/a | loaded, not loaded, how to reach; four-status labels | MEM-04 |

### Layer 1, rules

Already Loam's practice: AGENTS.md as a map, corrections become hooks or rules.
Borrow SuperClaude's error log: one JSONL line per error with a normalized signature (digits to N), looked up by word overlap at zero tokens on a hit, stdlib only (`pm_agent/reflexion.py`).
Re-keyed on correction text, it is the matcher for the weekly recurring-errors report.
SuperClaude's token-savings document is unvalidated estimates; do not cite its numbers.

### Layer 2, navigation

Your folder-and-file index, built from source by a parser, never by a model.
Two trial arms, one at a time, five factory tickets each against five interleaved without, judged on the ledger the factory already writes (turns, tokens, cost, grader verdicts, turns to first correct file); the frozen protocol is `docs/plans/2026-09-21-memory-v2/nav-01-protocol.md`:

- B. The official Claude Code language-server plugin: first-party, go-to-definition, references, symbols, call hierarchy, diagnostics after edits, 11 languages, no daemon.
  Claude only; Codex has no equivalent and open feature requests.
- C. Semble (MIT, 6,116 stars): local BM25 plus static Model2Vec embeddings over tree-sitter chunks, global path-hashed cache, reindex under a second, two MCP tools or `semble search "<q>" <path> --format json` from the factory worker with no schema cost.

Not in the trial: Graphify (Samyak's call: the graph grows fast and misses edges; its git-hook rebuild fixed the May staleness but not that), Serena (see below), CodeNib (84 stars), code-review-graph (30 tool schemas and a synchronous per-tool-call update hook; borrow its blast-radius query later as a CLI), jCodeMunch (free for academic use, license bars shipping it; personal install only), aider's repo map (ran on the seed in 3 s, ranked only the TypeScript runtime, missed every bash hook and the symlinked skills).
Why Serena was rejected, since it is the obvious symbol tool: it front-loads a 12.5 KB instruction manual plus a Claude-Code-specific override that forbids the built-in Read and Edit tools, about 3k tokens of prose and 3k to 4k of tool schemas every session before any code is read; its docs concede Claude Code drifts off its tools in long sessions and recommend alpha reminder hooks; it writes `.serena/` memories inside the repo and does not gitignore them; its source is GPL-3.0-or-later, fine to run, not fine to vendor.
The official Claude Code plugin gives the same symbol operations first-party with a per-plugin context cost shown in `/plugin`.
One honest gap: Codex has no language-server support, so Serena in `no-memories` mode is the only symbol tool a Codex session could use; if NAV-01 arm B wins and Codex sessions need the same, Serena becomes a Codex-only follow-up, measured the same way.
Fallback if neither arm supplies a committed structural map: LocAgent's stdlib-ast graph builder (about 150 lines, Python only, 0.2 s on 25 files) and Agentless's libcst skeleton generator (about 120 lines).

### Layer 3, experience

MEM-01 as running, plus:

- Key the store by the repository remote name, not the directory name, or the factory's worktrees (`loam-154`, `loam-hang`) each start empty.
- Scrub secrets at capture, before the first commit: agentmemory's 15 key patterns (`src/functions/privacy.ts`) or Hindsight's 45 (`test_memory_defense.py`) in python3 `re`.
- Gzip traces; ripgrep reads them with `-z`; delete traces older than a year; INDEX.md and notes never.
- A gitignored `.loam/memory` symlink in the repo pointing at the store's repo folder, so agents and you navigate by path.
- Sync: the store is a git repository with a bare remote on jhaveris (`~/memstore.git`) over the ssh `bin/runner` already uses; capture commits, recall pulls with a short timeout, offline stays silent; append-only files merge cleanly.
- Notes (MEM-03) use the LongMemEval-V2 two-note format behind the 42.8 to 51.0 result (`memory_modules/support.py:16`): a procedure note (the reliable workflow, 4 to 8 bullets) and a hint note (durable facts, 6 to 12 bullets), each `{title, description, content}`, which is Loam's memory frontmatter shape.
  Its rules carry over: never write a fact the run did not show, prefer exact strings, never pretend a failed run succeeded.
  Written by the session's own model, once, behind the Stop-hook gate, append-only; refine by a new note with SUPERSEDES, never overwrite (Hindsight's rule).
- Retrieval uses the AgentRunbook-C pattern from the same repo: a fixed layout, a committed concise index (INDEX.md), a small stdlib inspect CLI (`memsearch --session <id> --span a:b --match <re>`, modeled on `scripts/inspect_trajectory.py`, 355 lines stdlib), and a runbook line in the manifest: use the CLI, do not grep the raw trace.
  A retrieval-strategy note the agent may edit after a query, with the discipline "most queries should not add a row".
- Labels: every recalled item carries one of four statuses from that harness's `LEARNED_RETRIEVAL_STRATEGY_SKELETON.md`: supported, contradicts the premise, near match only, insufficient.
  These replace APPLICABLE, STALE, UNVERIFIED.
- A claim-once `handoff.md` in the store, injected once at the next start on either harness, then renamed (ai-memory's typed handoff, without the daemon).

Not adopted, with the reason: Engram (daemon, about 6k tokens per session, overwrites notes in place), claude-mem (a model call per tool use, daemon, cross-machine through their cloud), agentmemory (43k lines, daemon, opaque store), OpenViking (AGPL daemon, model calls per file), mcp-memory-service (opaque blobs, autonomous forgetting), mem0 (its Claude Code MCP is cloud only; its local keyword and entity retrieval is the one idea, for later).
Held in reserve: Hindsight (MIT), one self-hosted server both machines point at, fully local models possible, raw kept, observations refined not overwritten, superseded units invalidated not deleted, a 45-pattern secret scanner, knowledge pages read as plain markdown with no model call.
It puts a model and Postgres in the write path, so it waits for a named failure of the git sync.

### Layer 4, research records

The need is DistBench and papers: decisions, experiments, handoffs, and claims with evidence, status, conditions, and an explicit supersedes link (the brief's record schema).
Pilot basic-memory (AGPL-3.0, 4,011 stars) on DistBench as a personal install: markdown is the source of truth, a SQLite index rebuilds from the files by a watcher, hooks make no model calls, checkpoints are extractive, the session brief is capped at 10,000 characters and fenced as data not instructions, one front door `bm hook <event> --harness claude|codex|pi`, `write_note` refuses to overwrite by default.
It ships a Decision schema with `status: [open, accepted, superseded, rejected]` and a `supersedes` relation; experiment and claim schemas are two more schema files.
AGPL is inert for private use; the tool is never vendored into the seed.
After four weeks: the seed ships the three schema files, a gitignore line, and the hook registration, or the same frontmatter schema lives in plain files under `docs/agent/` with a check that validates it.
Paper corpus later, on evidence: LightRAG (MIT) keys incremental updates on content hash and returns file plus passage; GraphRAG keys on title and silently skips an edited draft, so it is out for evolving papers.

### Layer 5, transparency

The manifest names what it loaded, what exists but was not loaded, and the one command to reach it, under 1,200 tokens.
Every recalled item is labeled.
The weekly report counts capture, retrieval, and application.

## The brief's paper claims, checked

Nine of fourteen verified.
Four numbers are off: SWE-Pruner's Sonnet 4.5 success rose 70.6 to 72.0 (the brief says fell to 70.2); CodeNib's static-live agreement is 63.2%, not 39%; LoCoMo's F1 pair 43.3 and 30.9 appears nowhere (the range is 37.8 to 41.4 against 29.9 to 32.5); SWE-agent's 10.7-point gain is on the full set, 7.0 on Lite.
The Reddit post behind agent-native-cli could not be fetched.
No experiment used Opus 4.8, Fable 5.1, or GPT-5.6.

## Tickets

| Ticket | Layer | Contents | State |
|---|---|---|---|
| MEM-01 #154 | 3 | capture, recall, memsearch, weekly report | PR #163 open, CI green, awaiting merge |
| MEM-02 #161 | 3 | Codex capture, three counts; addendum: key by remote name | revised 2026-09-21, blocked by #154 |
| MEM-03 #162 | 3 | self-written note in the two-note format; corrections signature log | revised 2026-09-21, human-gated |
| MEM-04 #164 | 3, 5 | scrub, gzip and retention, symlink, inspect CLI, four-status manifest | filed 2026-09-21, blocked by #161 |
| MEM-05 #165 | 3 | bare remote on jhaveris, commit on capture, pull at start, claim-once handoff | filed 2026-09-21, blocked by #164 |
| NAV-00 #166 | 2 | FACTORY_NAV_ARM flag, arm-C prompt file, nav01-metrics.py in the factory | filed 2026-09-21, blocked by #165 |
| NAV-01 | 2 | pre-registered trial: language-server plugin, Semble CLI; five tickets each against five interleaved without | protocol frozen in docs/plans; runs after MEM-05 |
| REC-01 | 4 | basic-memory pilot on DistBench, four weeks | installed and seeded 2026-09-21; results in docs/research/rec-01-results.md |

Cut from the plan: a hand-written `docs/MAP.md` (NAV-01's winning arm replaces it, or AGENTS.md pointers stay), Graphify, the Serena trial, CodeNib.

## Risks

- Semble, CodeGraphContext, and code-review-graph were each adopted by Loam once in 2026 and cut in the rebuilds without a measurement; Graphify was cut on evidence (inferred edges, staleness).
  NAV-01 exists so it does not happen a third time.
- Semble publishes token-per-question reductions, not turns or cost per solve.
  The 8-turn result must be shown on Loam's own tickets.
- basic-memory's latest release number was not readable from a shallow clone.
- No tool was run except aider's map on a copy of the seed.
