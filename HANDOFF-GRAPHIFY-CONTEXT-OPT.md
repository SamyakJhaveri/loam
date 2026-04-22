# HANDOFF: Graphify Setup + Context/Token Optimization Plan

**Written:** 2026-04-21 | **Author:** Claude Opus session | **For:** Fresh session continuation

---

## Goal

Reduce Claude Code's context consumption and token usage on ParBench while boosting precision and accuracy. Graphify (a local knowledge graph built from tree-sitter ASTs) was installed as the primary tool. The next session should:

1. Teach Samyak how to use graphify day-to-day
2. Ensure Claude Code uses graphify automatically going forward
3. Execute a context/token optimization plan across the project

---

## Current State (what's already done)

### Graphify Installation
- **Package:** `graphifyy==0.4.25` installed in `env_parbench` venv
- **Graph built:** 2,226 nodes, 4,092 edges, 70 communities from 192 source files
- **Output:** `graphify-out/graph.json` (2.5 MB), `graph.html` (interactive viz), `GRAPH_REPORT.md`
- **`.graphifyignore`** excludes: `env_parbench/`, `HeCBench-master/`, `rodinia/`, `.git/`, `.planning/`, `results/`, `.claude/`, `__pycache__/`
- **Claude Code integration:** `graphify claude install` completed:
  - `CLAUDE.md` has `## graphify` section (lines 170-178) with 4 rules
  - `.claude/settings.json` has PreToolUse hook on `Glob|Grep` that reminds Claude about the graph
  - `.gitignore` has `graphify-out/cache/`

### God Nodes (most-connected abstractions — the project's core)
1. `Status` (92 edges) — harness/models.py
2. `RunResult` (58 edges) — harness result model
3. `MetricResult` (45 edges) — metric tracking
4. `ChangeNames` (39 edges) — c_augmentation transform
5. `ChangeFunctionNames` (37 edges) — c_augmentation transform
6. `PointerArithmeticToArrayIndex` (33 edges) — c_augmentation transform
7. `resolve_paths()` (32 edges) — path resolution utility
8. `SwapCondition` (31 edges) — c_augmentation transform
9. `verify_run()` (31 edges) — harness verifier
10. `main()` (30 edges) — entry points

### Memory Consolidation (dream)
Also completed this session:
- 31 → 28 memory files (3 merges, 1 rename)
- Fixed stale PHASE-3-BLOCKER (Phase 3 is running: 181+ Qwen results)
- Deleted `protect-cuda-omp-results.sh` hook (guarded wrong path)
- Updated protection memories to reflect hook deletion

---

## What Worked

- `graphify update .` builds the graph in ~15 seconds with `.graphifyignore` scoping to 192 project files
- The PreToolUse hook on Glob|Grep fires automatically, reminding Claude to check the graph
- Tree-sitter AST extraction is 100% local — zero API cost, zero data leaves machine
- MIT license, Python-native, fits naturally alongside ParBench's existing toolchain

## What Didn't Work

- `graphify build` is not a valid CLI command — use `graphify update .` instead
- Without `.graphifyignore`, graphify tried to parse 6,973 files (including venv + HeCBench) and hit `maximum recursion depth exceeded`
- The MCP server integration was NOT set up (stdio-based `graphify.serve`) — only the hook+CLAUDE.md integration was installed. MCP would give Claude direct `query_graph`, `get_node`, `get_neighbors` tools but requires additional setup

---

## How Graphify Works (teach Samyak)

### CLI Commands (run in project root with venv active)
```bash
# Rebuild graph after code changes (AST only, no LLM, ~15s)
graphify update .

# Ask a question — BFS traversal of the graph
graphify query "how does the harness verify results?"

# Find shortest path between two concepts
graphify path "verify_run()" "Status"

# Explain a node and its neighbors
graphify explain "RunResult"

# Open interactive visualization in browser
open graphify-out/graph.html

# Read the full graph report
cat graphify-out/GRAPH_REPORT.md
```

### How Claude Code Uses It Automatically
1. **PreToolUse hook** on every `Glob|Grep` call: Claude sees a reminder that the graph exists
2. **CLAUDE.md rules** (4 rules in `## graphify` section):
   - Read GRAPH_REPORT.md before answering architecture questions
   - Use `graphify query/path/explain` instead of grep for cross-module questions
   - Run `graphify update .` after modifying code files
3. **The graph replaces broad exploration:** Instead of spawning Explore agents or reading 10+ files, Claude reads the 2.5 MB graph.json or queries it via CLI — getting the same structural info in ~100 tokens instead of ~5,000

### When to Rebuild
- After editing Python/C/C++ source files: `graphify update .`
- After adding new specs or scripts: `graphify update .`
- NOT needed for: editing markdown, JSON specs, result files, planning docs (these aren't code)

---

## Next Steps: Context/Token Optimization Plan

### Phase 1: Maximize Graphify Value (COMPLETE as of 2026-04-21)

**1a. Set up MCP server** -- DONE (session 1)
- `mcp` 1.27.0 installed in env_parbench
- `.mcp.json` created with graphify stdio server (7 tools: query_graph, get_node, get_neighbors, get_community, god_nodes, graph_stats, shortest_path)
- Auto-allow permissions added to `.claude/settings.json`
- **Note:** MCP tools only appear after a full Claude Code CLI restart (not `/exit`)

**1b. Generate wiki** -- DONE (session 2)
- 108 articles written to `graphify-out/wiki/`
- Entry point: `graphify-out/wiki/index.md` (2226 nodes, 4092 edges, 98 communities)
- Generated directly from graph.json via `graphify.wiki.to_wiki()`
- CLAUDE.md rule at line 178 already references the wiki

**1c. Install git hooks for auto-rebuild** -- DONE (session 2)
- `.git/hooks/post-commit` — rebuilds graph after each commit (changed files only)
- `.git/hooks/post-checkout` — rebuilds graph on branch switch
- Installed via `graphify hook install`

### Phase 2: Reduce Exploration Overhead (this week)

**2a. Audit CLAUDE.md + .claude/rules/ for redundancy with graph**
- The graph now captures code structure that `.claude/rules/architecture.md` describes manually
- After verifying graph accuracy, slim down architecture.md to pointer-only: "See graphify-out/GRAPH_REPORT.md for live architecture"
- Saves ~150 lines of CLAUDE.md context loaded every session

**2b. Use graphify query before spawning agents**
- Current pattern: spawn Explore agent → reads 10+ files → returns summary
- New pattern: `graphify query "how does X work?"` → 100-token answer → read only the 1-2 files that matter
- Enforce via CLAUDE.md rule: "Before spawning an Explore agent, try `graphify query` first"

**2c. Compact CLAUDE.md further**
- Current: ~180 lines loaded every turn
- Move the skills table and agents table into separate `.claude/rules/` files (conditional load)
- Target: CLAUDE.md ≤ 100 lines (saves ~80 lines × every message = significant token savings)

### Phase 3: Session-Level Optimizations (ongoing)

**3a. Use `/compact` at 40% context** (already in workflow.md but needs enforcement)
**3b. Graphify-informed file reads:** Before `Read`, check if graphify already has the structure
**3c. Result caching in graphify memory:** Use `graphify save-result` to store Q&A pairs so repeated questions hit the cache

### Expected Impact
| Metric | Before | After (estimated) |
|--------|--------|-------------------|
| Files read per architecture question | 5-15 | 1-3 |
| Tokens per codebase exploration | ~5,000-20,000 | ~500-2,000 |
| Context consumed by CLAUDE.md | ~180 lines/turn | ~100 lines/turn |
| Explore agents per session | 2-5 | 0-2 |
| Graph rebuild cost | N/A | 0 tokens (local AST) |

### Phase 4: Verification — Measure Actual Token Savings (A/B test)

The "Expected Impact" table above is estimated. We need hard numbers. Run a controlled A/B comparison using two sessions performing the same task, one with graphify and one without.

**Tool: codeburn** (`codeburn@0.8.5`, installed globally via npm) — session-level token usage and context management analytics. Use it to capture per-session metrics for the comparison.

**Protocol:**

**Step 1: Pick a representative task**
Choose a task that involves codebase exploration + implementation. Good candidates:
- "Add a new spec for an existing HeCBench kernel" (touches specs/, harness/, manifest)
- "Trace how `verify_run()` handles numeric_comparison oracles" (cross-module question)
- "Explain how the augmentation pipeline transforms L0→L4" (architecture question)

**Step 2: Session A — WITHOUT graphify**
```bash
# Temporarily disable graphify integration:
# 1. Remove the Glob|Grep PreToolUse hook from .claude/settings.json
# 2. Remove the ## graphify section from CLAUDE.md
# 3. Start a fresh session with codeburn enabled
# 4. Perform the chosen task
# 5. Record: total tokens, tool calls, files read, agents spawned, time to completion
```

**Step 3: Session B — WITH graphify**
```bash
# Restore graphify integration (revert Step 2 changes)
# Start a fresh session with codeburn enabled
# Perform the SAME task
# Record the same metrics
```

**Step 4: Compare**

| Metric | Session A (no graphify) | Session B (with graphify) | Delta |
|--------|------------------------|--------------------------|-------|
| Total input tokens | — | — | — |
| Total output tokens | — | — | — |
| Tool calls (Read/Glob/Grep) | — | — | — |
| Files opened | — | — | — |
| Explore agents spawned | — | — | — |
| Time to task completion | — | — | — |
| Context compactions needed | — | — | — |
| Accuracy (task completed correctly?) | — | — | — |

**Step 5: Ongoing monitoring**
After the A/B test, keep codeburn enabled for 5 sessions to build a baseline of graphify-assisted token usage. Track:
- **Token burn rate** (tokens per minute of active work)
- **Exploration ratio** (% of tokens spent on codebase reads vs. actual implementation)
- **Compaction frequency** (fewer compactions = better context management)
- **Answer precision** (did Claude find the right file on the first try?)

**Where results go:** Save the comparison table and codeburn logs to `.planning/graphify-eval/` for reference. If graphify doesn't demonstrably save tokens, consider removing it (sunk cost = ~15s rebuild time + 2.5 MB graph file, minimal).

---

## Files Changed This Session

| File | Change |
|------|--------|
| `.claude/hooks/protect-cuda-omp-results.sh` | **DELETED** (guarded wrong path) |
| `.claude/settings.json` | Removed protect hook; graphify added Glob\|Grep PreToolUse hook |
| `CLAUDE.md` | Graphify section appended (lines 170-178) |
| `.graphifyignore` | **CREATED** — scopes graph to 192 project source files |
| `graphify-out/` | **CREATED** — graph.json, graph.html, GRAPH_REPORT.md, cache/ |
| `.gitignore` | Added `graphify-out/cache/` |
| 28 memory files | Dream consolidation: 3 merges, 2 date fixes, 2 hook-ref fixes, 1 rename |
| `MEMORY.md` | Rebuilt with semantic grouping (Permanent Feedback / Active State / References) |

---

## How to Start the Next Session

```
Read HANDOFF-GRAPHIFY-CONTEXT-OPT.md — continue from Phase 1a (MCP server setup).
Qwen Phase 3 canonical evals are running in background (181+ results as of 2026-04-21).
Do NOT touch results/evaluation/together-qwen-3.5-397b-a17b/.
```
