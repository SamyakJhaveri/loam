# loam memory layer — design, evidence, implementation, testing

Status: v0 design for the loam seed. Written 2026-09-03. Every claim below is tied to a source in §8.

---

## 0. The objective function (corrected)

Proposed:  `(effectiveness × cost) >> complexity`

That multiplies by cost, so a system that burns more tokens scores higher. Corrected form:

```
maximize   E = recall_useful × application_correct × (1 − stale_applied_rate)
subject to C_write + C_read + C_maintain  ≤ budget       (tokens, seconds, human minutes)
           complexity                     ≤ 1 shell script per lifecycle event
```

Three things the evidence forces into this form:

1. **Write-path cost dominates and is usually unreported.** MemDelta measured Mem0 at 1,000+ LLM calls and ~120 min per ~50-session history vs. ~60 s and $0.01 for verbatim retrieval, for no accuracy gain on matched instances. Memory operational cost can consume >80% of total agent execution time.
2. **Effectiveness is three separate numbers, not one.** Capture (was it saved), retrieval (was it surfaced), application (was it used correctly). MEMPROBE: evidence is often stored in memory yet cannot be reached through normal retrieval. RaMem: retrieved memories lose the context needed to judge applicability ("context collapse").
3. **Reliability is a first-class term.** Retrieval-heavy stores over-answer; curated/sparse stores abstain better (Ping, both benchmarks). For research-to-production code a confidently-applied stale memory is the expensive failure.

Complexity is a *constraint*, not a term in the score. Raise the ceiling only when a measured failure demands it.

---

## 1. What the controlled evidence actually says (ranked by strength)

| # | Finding | Strength | Source |
|---|---|---|---|
| 1 | **Raw episodic retention beats LLM-consolidated memory.** Continuous LLM rewriting of a memory bank rises, then degrades below no-memory; episodic-only control matches or beats every consolidator tested. GPT-5.4 loses 54% of ARC-AGI problems it previously solved when consolidating from ground truth. | Strong (5 benchmarks + controlled env) | Faulty Memories, arXiv 2605.12978 |
| 2 | **Verbatim RAG ≈ Mem0 at 1/50 the write cost; LLM "self-memory" scratchpad (42%) < basic retrieval (47%).** | Strong (paired, McNemar, n=500) | MemDelta, arXiv 2606.29914 |
| 3 | **Embedding choice (+6.2pp) is as large as claimed architectural gains.** Swapping MiniLM→cloud embeddings flipped the Mem0-vs-RAG verdict. | Strong | MemDelta |
| 4 | **Never dump full history into Claude.** Sonnet refused 63% of full-context queries with the answer present in 115K tokens; RAG beat full-context by +31pp on Sonnet, while Gemini gained +14pp from full context. Model family reverses the conclusion. | Strong | MemDelta §4.2 |
| 5 | **Write-side loss exceeds retrieval-side loss** on LongMemEval for 4/6 baselines; the key decision is what to retain at write time. | Moderate | WhenLoss, arXiv 2605.24579 |
| 6 | **Structured store beats files by 28.7pp on long haystacks; files win where memory is small, human-owned, secondary — and files win abstention.** Consolidation pass: null. Hybrid ≈ flat vector index on LoCoMo, +15 on LongMemEval-M. | Strong, single author, code public | Ping-Lin Chang, pinglin.tw + a40-labs/memory |
| 7 | **Frontier actors gain ~0 task success from experience banks.** claude-sonnet-5: +1.4pp ALFWorld (p=0.5), +0.6 SR WebShop (p=0.8). Weak actors gain ~4pp. | Moderate (2 tasks, 2 actors) | Ping-Lin Chang, agentic section |
| 8 | **Cheap trajectory notes are the highest-ROI step.** Raw-slice RAG 42.8% → + notes 51.0% at 0.1→0.2 s. Agentic search reaches 74.9% at 108 s. | Strong (public benchmark) | LongMemEval-V2, arXiv 2605.12493 |
| 9 | **Simpler harness + better model beats elaborate orchestration.** AgentRunbook-C V2 (shell + file-edit only): 75.17% @ 49 s vs V1 73.61% @ 102 s (Luna, xhigh). Its second trick: a per-question consolidated *retrieval strategy note*. | Moderate | LME-V2 research update, Aug 2026 |
| 10 | **Curated skills: +16.2pp avg (+4.5pp in SWE). One-shot self-generated skills: no benefit on average.** Execution feedback is essential for skill improvement. | Strong (87 tasks, 18 configs) | SkillsBench 2602.12670; SkillLearnBench 2604.20087 |
| 11 | **A structural codebase index is the only intervention with a measured resolve-rate gain on a frontier model** (Opus 4.7, SWE-PolyBench Verified + SWE-bench Pro, 3 seeds, lower cost per solve). | Strong | "Code Isn't Memory", arXiv 2606.22417 |
| 12 | **Recurrence-triggered consolidation cuts memory-construction tokens up to 87% while improving accuracy.** | Moderate (LoCoMo only) | RecMem, ACL 2026 Findings |
| 13 | **ReasoningBank: +4.6pp SWE-Bench-Verified, ~3 fewer steps/task — on Gemini-2.5-Flash.** Success+failure lessons > success-only. | Moderate (weak actor) | Google Research, ICLR 2026 |
| 14 | **Vendor numbers do not survive reproduction.** Mem0's 94.4 LongMemEval → 73.8 under a third-party harness; LoCoMo numbers for one system span 25 points depending on scoring. | Strong | Mnemoverse Q3-2026 review; Ping-Lin Chang |
| 15 | **OpenAI's own harness team: "one big AGENTS.md" failed.** ~100-line AGENTS.md as a *map* with pointers to deeper sources of truth. Anthropic: CLAUDE.md < 200 lines; /doctor trims derivable content. | Authoritative | openai.com/index/harness-engineering; code.claude.com/docs/en/memory |

**Net verdict for loam.** The system that is both most effective *and* cheapest to maintain is: verbatim raw traces (ground truth) + lexical/embedding retrieval + a small, human-curated schematic layer (gotchas, cards, skills) + an applicability gate. Every automatic LLM-rewrite layer is a known degradation vector (#1, #2, #6) and should be sandboxed behind git.

---

## 2. Where Claude Code and Codex already are (verified against docs / source)

| | Claude Code | Codex |
|---|---|---|
| Human instructions | `CLAUDE.md` (< 200 lines), `.claude/rules/*.md` with `paths:` frontmatter, `@import` (loads at launch, no context savings), `/doctor` trims | `AGENTS.md` (~100 lines as a map); memories are *not* for rules that must always apply |
| Agent-written memory | Auto memory: `MEMORY.md` index (first 200 lines / 25 KB loaded) + topic files, per git repo, machine-local; `autoMemoryDirectory` relocates it; skips debugging fixes and anything derivable from code | `[features] memories = true` (off by default); 2-phase async pipeline: Phase 1 per-rollout `raw_memory` + `rollout_summary`, Phase 2 global consolidation agent ranked by `usage_count`/`last_usage`; root at `~/.codex/memories/` kept as a git baseline; **user-scoped, not per-project** |
| Read path | Index in context; topic files on demand | `memory_summary → MEMORY.md search → 1–2 rollout summaries/skills → raw evidence` |
| Procedures | Skills, lazy-loaded | `skills/` produced by consolidation + versioned SKILL bundles |
| Hooks | `SessionStart` (additionalContext), `SessionEnd`, `Stop`, `PreCompact`, `PostToolUse`, `InstructionsLoaded`, … ; payload has `session_id`, `transcript_path`, `cwd` | `[features] hooks = true`; `<repo>/.codex/hooks.json` with the same event names |
| Transcript retention | Deleted after `cleanupPeriodDays` | Rollouts in state DB; summaries pruned by selection |
| Compaction | Re-reads project-root CLAUDE.md after `/compact`; nested files reload on touch | Compaction replaces history with a compressed representation |

Two facts that shape the design: (a) both native systems are *continuous LLM rewriters* (finding #1 applies to them); (b) Claude's auto memory deliberately excludes debugging fixes — the highest-value category for research→production work.

---

## 3. loam seed layout

```
loam/
├── AGENTS.md                      # ≤100 lines. A MAP. Pointers, not content.
├── CLAUDE.md                      # "@AGENTS.md" + ≤20 Claude-specific lines
├── .claude/
│   ├── settings.json              # hooks + autoMemoryDirectory + cleanupPeriodDays
│   ├── rules/
│   │   ├── memory.md              # the two memory rules (§5) — always loaded
│   │   └── hpc.md                 # paths: ["slurm/**","mpi/**","**/launch*.sh"]
│   └── skills/
│       └── _template/SKILL.md     # curated-only; see §5.3
├── .codex/
│   ├── hooks.json                 # same scripts as Claude
│   └── README.md                  # config.toml snippet the user pastes
├── docs/
│   ├── HOSTS.md                   # one block per machine: hostname, scheduler, modules, GPUs, quirks
│   ├── GOTCHAS.md                 # ≤60 lines, injected at SessionStart
│   ├── CARDS.md                   # append-only debugging cards (§5.2)
│   └── DECISIONS.md               # ADR-lite: one dated line per decision + why
└── bin/
    ├── mem-capture.sh             # SessionEnd / PreCompact / Stop
    ├── mem-recall.sh              # SessionStart
    ├── memsearch                  # rg wrapper (→ FTS5 later)
    └── mem-weekly.sh              # cron: commit + recurring-error report
```

Per-user store (outside the repo, git-tracked):

```
~/memstore/
├── claude/<repo>/     # Claude auto-memory, relocated
├── codex/             # symlink target for ~/.codex/memories
├── traces/<repo>/     # raw transcripts + INDEX.md   ← ground truth
└── reports/           # weekly.md, recurring-errors.md
```

Project-owned knowledge (`docs/*`) lives in the repo and propagates with the seed. Machine/session evidence (`~/memstore`) does not.

---

## 4. Implementation

### 4.1 `.claude/settings.json` (seed default)

```json
{
  "autoMemoryDirectory": "~/memstore/claude",
  "cleanupPeriodDays": 365,
  "hooks": {
    "SessionStart": [{"hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/bin/mem-recall.sh"}]}],
    "SessionEnd":   [{"hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/bin/mem-capture.sh"}]}],
    "PreCompact":   [{"hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/bin/mem-capture.sh"}]}],
    "Stop":         [{"hooks": [{"type": "command", "command": "$CLAUDE_PROJECT_DIR/bin/mem-capture.sh --throttle 600"}]}]
  }
}
```

### 4.2 `bin/mem-capture.sh`

```bash
#!/usr/bin/env bash
# Copies the raw transcript into ~/memstore/traces/<repo>/ and appends an INDEX line.
# Zero LLM calls. Idempotent (sha256 of transcript).
set -euo pipefail
IN=$(cat)                                   # hook JSON on stdin
TP=$(jq -r .transcript_path <<<"$IN"); SID=$(jq -r .session_id <<<"$IN"); CWD=$(jq -r .cwd <<<"$IN")
REPO=$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")
DST=~/memstore/traces/$REPO; mkdir -p "$DST"
if [[ "${1:-}" == "--throttle" ]]; then                       # Stop-hook throttling
  LAST="$DST/.last-$SID"; NOW=$(date +%s)
  [[ -f $LAST && $((NOW - $(cat "$LAST"))) -lt ${2:-600} ]] && exit 0; echo "$NOW" > "$LAST"
fi
SUM=$(sha256sum "$TP" | cut -c1-12)
OUT="$DST/$(date +%F)-${SID:0:8}.jsonl"
[[ -f "$OUT" && "$(sha256sum "$OUT" | cut -c1-12)" == "$SUM" ]] && exit 0
cp "$TP" "$OUT"
FIRST=$(jq -r 'select(.type=="user") | .message.content // .message | tostring' "$TP" 2>/dev/null | head -1 | cut -c1-90)
printf '%s | %s | %s@%s | %s | %s\n' "$(date +%F)" "${SID:0:8}" \
  "$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)" "$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)" \
  "$(hostname -s)" "$FIRST" >> "$DST/INDEX.md"
```

### 4.3 `bin/mem-recall.sh`

```bash
#!/usr/bin/env bash
# Emits ≤1K tokens of stable context: last 5 sessions, this host's block, GOTCHAS if short.
set -euo pipefail
IN=$(cat); CWD=$(jq -r .cwd <<<"$IN")
REPO=$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")
H=$(hostname -s)
CTX="## Recent sessions ($REPO)\n$(tail -5 ~/memstore/traces/$REPO/INDEX.md 2>/dev/null)\n"
CTX+="\n## This host ($H)\n$(awk -v h="$H" '$0 ~ "^## "h {p=1;next} /^## /{p=0} p' "$CWD/docs/HOSTS.md" 2>/dev/null)\n"
G="$CWD/docs/GOTCHAS.md"; [[ -f $G && $(wc -l <"$G") -le 60 ]] && CTX+="\n## Gotchas\n$(cat "$G")\n"
CTX+="\nRule: before acting on any recalled memory, check git log -1, hostname, toolchain versions; label APPLICABLE/STALE/UNVERIFIED."
jq -n --arg c "$(printf "$CTX")" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
```

### 4.4 `bin/memsearch`

```bash
#!/usr/bin/env bash
# v0: ripgrep. v1 (only if v0 misses paraphrases): sqlite FTS5 + embeddings (see §6).
rg -n -C2 --glob '!.git' --max-count 20 "$@" ~/memstore/traces "$(git rev-parse --show-toplevel 2>/dev/null)/docs" | head -80
```

### 4.5 Codex

`~/.codex/config.toml` (documented in `.codex/README.md`, not committed):

```toml
[features]
memories = true
hooks = true
no_memories_if_mcp_or_web_search = true
```

`mv ~/.codex/memories ~/memstore/codex && ln -s ~/memstore/codex ~/.codex/memories`

`.codex/hooks.json` mirrors `.claude/settings.json` hooks, pointing at the same `bin/` scripts (Codex hooks use the same event names and JSON shape).

### 4.6 `AGENTS.md` skeleton (the map)

```
# <project> — agent map (≤100 lines)
## What this is        (2 lines)
## Where truth lives   docs/DECISIONS.md · docs/HOSTS.md · docs/GOTCHAS.md · docs/CARDS.md
## Build / test        exact commands
## Memory rules        see .claude/rules/memory.md (Claude) / below (Codex):
  - Before debugging any error: run `bin/memsearch "<error string>"` first.
  - After a non-obvious fix: ask, then append one card to docs/CARDS.md.
  - Never rewrite existing cards or gotchas mid-task.
  - Recalled memories are evidence, not truth: verify against current repo/host.
## Skills              list with one-line triggers
```

`CLAUDE.md` = `@AGENTS.md` + `## Claude Code` section (plan mode for `launch/**`, etc.).

---

## 5. Operating rules

### 5.1 Two memory rules (`.claude/rules/memory.md`, always loaded)
1. **Search before debug.** `memsearch` on the error string / symbol before reading source. (Codex read-path discipline: 4–6 targeted searches, never scan.)
2. **Card after fix, with consent.** Format:
   ```
   ### YYYY-MM-DD <symptom, one line>
   CAUSE: … | FIX: … | ENV: host, CUDA, torch, commit | VERIFIED-ON: host@commit
   ```
   Append-only. Never edit prior cards (finding #1: rewrites compound errors).

### 5.2 Promotion ladder (human-gated, recurrence-triggered — RecMem's trigger, done by you)
```
raw trace ──(non-obvious fix)──▶ CARD ──(seen ≥2×)──▶ GOTCHA line ──(procedure worked ≥2×)──▶ SKILL
```
Nothing is promoted by an LLM. Weekly report (§7) surfaces candidates; you promote.

### 5.3 Skills: curated only
Write from a trajectory that worked twice. Include exact commands, expected output, and known failure signatures. Do not ask the model to generate skills one-shot (SkillsBench: no benefit). Keep the SKILL.md body under ~150 lines; put scripts alongside.

### 5.4 Applicability gate
Injected at SessionStart (§4.3) and repeated in AGENTS.md. Every recalled item must be labelled before use. This is the reliability term of the objective function; it is also the cheapest defense against the over-answering failure mode of retrieval-heavy memory.

### 5.5 Native memories: enabled, sandboxed
Keep Claude auto-memory and Codex memories on. Both are cheap, and Codex's usage counters are useful telemetry. Treat their `MEMORY.md` outputs as a cache: git-tracked in `~/memstore`, reviewed weekly, reverted when wrong. Never copy from them into `docs/` without reading the underlying trace.

---

## 6. Complexity ladder (advance only on a named failure)

| Level | Add | Trigger to advance |
|---|---|---|
| 0 | Native memories + AGENTS.md map + skills + docs/* | — |
| 1 | Raw trace capture + INDEX + SessionStart manifest | none — always do this |
| 2 | `memsearch` = ripgrep | none |
| 3 | SQLite FTS5 + local embeddings (bge-m3 or similar), RRF fusion, top-k 10 | `rg` misses a lesson you *know* is in traces because wording differs (≥3 occurrences in a month). Embedding choice matters more than architecture — test two. |
| 4 | Per-session index card auto-generated by a cheap model (Luna/Haiku-class), *only* for sessions with test fail→pass, a user correction, or a commit | recurring-errors report shows ≥5 repeat errors/month that never got a card |
| 5 | Retrieval strategy note (AgentRunbook-C V2 pattern): `docs/RETRIEVAL.md` the agent appends to after a successful memsearch | memsearch usage is high but hit-rate is low |
| 6 | Structural code index (Serena / LSP plugin) | localization is the visible bottleneck — this is the one step with a measured resolve gain on a frontier model; consider earlier |
| 7 | Agentic iterative retrieval over traces | single-pass retrieval leaves known evidence unfound |
| ✗ | Knowledge graph, LLM consolidation, RL memory policy | not until 3–7 have demonstrably plateaued |

---

## 7. Testing and verification (no eval suite; acceptance checks + signals)

### 7.1 Seed acceptance checklist (run once per new repo)
- [ ] `/context` lists `CLAUDE.md`, `.claude/rules/memory.md` under Memory files
- [ ] `InstructionsLoaded` hook log shows `hpc.md` loads only when a matching path is read
- [ ] Start a session, end it: `~/memstore/traces/<repo>/INDEX.md` gained one line; transcript file exists
- [ ] `/compact` in a long session → a second capture file appears
- [ ] New session: transcript shows the injected "Recent sessions / This host / Gotchas" block, ≤1K tokens (`/context`)
- [ ] `bin/memsearch NCCL` returns hits from traces
- [ ] Codex: `/memories` shows enabled; after ≥2 idle threads, `~/memstore/codex/rollout_summaries/` non-empty
- [ ] `git -C ~/memstore status` clean after `mem-weekly.sh`

### 7.2 Weekly signals (`bin/mem-weekly.sh`, cron Sunday)
```bash
#!/usr/bin/env bash
set -euo pipefail; cd ~/memstore
git add -A; git commit -qm "weekly $(date +%F)" || true
mkdir -p reports
rg -o --no-filename -e 'Error: .{0,60}' -e 'RuntimeError.{0,60}' -e 'NCCL.{0,40}' -e 'srun: error.{0,60}' traces \
  | sort | uniq -c | sort -rn | head -20 > reports/recurring-errors.md
{ echo "## $(date +%F)"; git diff --stat HEAD~1 -- claude/ codex/; } >> reports/weekly.md
sqlite3 ~/.codex/state*.sqlite "select count(*), sum(usage_count>0) from stage1_outputs" 2>/dev/null >> reports/weekly.md || true
```
Read `recurring-errors.md`: count ≥2 → promote to card/gotcha. Same error in two sessions = a capture failure, the only true quality metric you need.

### 7.3 Monthly signals
- `ccusage` input tokens on ≥3rd session/week per repo, before vs. after (re-exploration cost).
- Codex `usage_count` distribution: if ~90% of memories are never cited after a month, the write side is noise → tighten, don't add.
- `rg -c 'STALE' traces/` : gate firing rate. Zero means the gate isn't being applied; very high means memory is rotting.

### 7.4 If you ever compare two memory configurations
Follow MemDelta: change one variable, same model, same prompts, same embedding, report write-path cost, paired test. Anything else is confounded (embedding swap alone = +6.2pp).

---

## 8. Sources

Research
- Faulty Memories — Zhang et al., "Useful Memories Become Faulty When Continuously Updated by LLMs", arXiv 2605.12978, https://arxiv.org/abs/2605.12978 · site https://dylanzsz.github.io/faulty-memory/
- MemDelta — Wang, "Controlled Baselines and Hidden Confounds in Agent Memory Evaluation", arXiv 2606.29914, https://arxiv.org/abs/2606.29914
- WhenLoss — arXiv 2605.24579, https://arxiv.org/abs/2605.24579
- LongMemEval-V2 — Wu et al., arXiv 2605.12493, https://arxiv.org/abs/2605.12493 · site https://xiaowu0162.github.io/longmemeval-v2/ · AgentRunbook-C V2 https://xiaowu0162.github.io/longmemeval-v2/agentrunbook-c-v2/ · code https://github.com/xiaowu0162/LongMemEval-V2
- RecMem — Dai et al., ACL 2026 Findings, arXiv 2605.16045, https://github.com/CaiusDai/RecMem
- ReasoningBank — Ouyang et al., ICLR 2026, arXiv 2509.25140, https://research.google/blog/reasoningbank-enabling-agents-to-learn-from-experience/
- MemTrace — Long et al., arXiv 2606.17328; MEMPROBE — arXiv 2606.24595; RaMem — arXiv 2606.22844; MemConflict — arXiv 2605.20926
- SkillsBench — arXiv 2602.12670; SkillLearnBench — arXiv 2604.20087; procedural-memory survey — arXiv 2606.23127
- "Code Isn't Memory" — arXiv 2606.22417, https://arxiv.org/abs/2606.22417
- MemCoder — arXiv 2603.13258; SWE-MeM — arXiv 2606.28434 (RL route, future)
- MemHarness — arXiv 2607.28272, https://github.com/KnowledgeXLab/MemHarness (RL route, future)

Independent comparisons / practitioner writeups
- Ping-Lin Chang, "The Shapes of Agent Memory", Aug 2026, https://pinglin.tw/blog/the-shapes-of-agent-memory/ · data https://github.com/a40-labs/memory
- Mnemoverse, "Mem0 vs Zep vs Letta vs Cognee vs Supermemory (Q3 2026)", https://mnemoverse.com/docs/library/ai-memory-solutions-2026-q3
- Letta, "Is a Filesystem All You Need?", https://www.letta.com/blog/benchmarking-ai-agent-memory/
- Mastra, "Yes, you can use RAG for agent memory" (vendor), https://mastra.ai/research/use-rag-for-agent-memory

Vendor docs / authoritative
- Claude Code memory: https://code.claude.com/docs/en/memory · hooks: https://code.claude.com/docs/en/hooks · skills: https://code.claude.com/docs/en/skills
- Anthropic, "Effective context engineering for AI agents": https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- OpenAI, "Harness engineering": https://openai.com/index/harness-engineering/
- Codex memories: https://developers.openai.com/codex/memories.md · source: https://github.com/openai/codex/blob/main/codex-rs/memories/README.md · read path template: https://github.com/openai/codex/blob/main/codex-rs/ext/memories/templates/memories/read_path.md
- GPT-5.6 family: https://openai.com/index/gpt-5-6/

Tools (if you'd rather not maintain the scripts)
- claude-mem-lite (SQLite FTS5, filter-then-summarize): https://github.com/sdsrss/claude-mem-lite
- codenamev/claude_memory (episodic log + corroboration gate): https://github.com/codenamev/claude_memory
- codexmem (Codex SQLite+FTS5+hooks): https://pypi.org/project/codexmem/
- thedotmack/claude-mem (multi-harness, heavier): https://github.com/thedotmack/claude-mem
- Basic Memory (Markdown, MCP, cross-tool): https://docs.basicmemory.com/
