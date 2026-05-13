# 3-Layer Memory Architecture

Claude Code projects benefit from three complementary memory layers that cover different aspects of project knowledge.

## The Three Layers

| Layer | Tool | What it stores | How it helps |
|-------|------|----------------|-------------|
| **1. Static knowledge** | Built-in (CLAUDE.md + `.claude/rules/` + auto memory) | Project conventions, coding standards, known issues | "Always use pytest, never mock the database" |
| **2. Session memory** | [Memsearch](https://github.com/zilliztech/memsearch) | Temporal decisions, what was worked on each day | "Last Tuesday we decided to switch from REST to GraphQL" |
| **3. Codebase map** | [Graphify](https://github.com/safishamsi/graphify) | Module relationships, dependency graphs, hub detection | "The auth module connects to 15 other modules (god node)" |

### Why three layers?

They don't overlap — each answers different questions:
- Layer 1: "What are our rules?" (static, curated by humans)
- Layer 2: "What happened recently?" (temporal, auto-captured per session)
- Layer 3: "How is the code structured?" (structural, derived from AST)

## Layer 1: Built-in Memory (already configured)

No setup needed. Claude Code automatically uses:
- `CLAUDE.md` at project root — top-level rules and conventions
- `.claude/rules/*.md` — path-scoped rules (load only when matching files are touched)
- `~/.claude/projects/<key>/memory/` — auto memory (cross-session facts, max 200 lines loaded)

## Layer 2: Memsearch (session memory)

Automatically captures what you work on each session and enables semantic recall.

### How it works
1. After each Claude response, a Haiku model summarizes the conversation turn
2. Summary is appended to `.memsearch/memory/YYYY-MM-DD.md` (human-readable Markdown)
3. At session start, recent memories are injected as context
4. Semantic search via ONNX embeddings + Milvus Lite (100% local, no API key)

### Setup
```bash
# Install the plugin (one-time, in Claude Code):
/plugin marketplace add zilliztech/memsearch
```

### Storage
- Memories: `.memsearch/memory/*.md` (Markdown, human-readable and editable)
- Vector DB: `.memsearch/milvus.db` (local Milvus Lite file)
- Config: `.memsearch.toml` (at project root)

### Cost
Free for embeddings (ONNX runs locally). Summarization uses Haiku via your Claude CLI subscription.

## Layer 3: Graphify (codebase knowledge graph)

Parses your codebase using Tree-sitter and builds a knowledge graph showing how modules connect.

### How it works
1. Parses source files across 29 languages using Tree-sitter ASTs
2. Builds a NetworkX knowledge graph of modules, functions, and dependencies
3. Identifies "god nodes" (modules everything depends on)
4. Outputs `graphify-out/graph.json` + interactive `graphify-out/graph.html`
5. Runs as an MCP server so Claude can query the graph directly

### Setup
```bash
# Install graphify
uv tool install graphifyy  # or: pip install graphifyy

# Build the knowledge graph
graphify .

# (Optional) Install as Claude Code MCP server for direct querying
graphify claude install
```

### Storage
- Graph: `graphify-out/graph.json`
- Visualization: `graphify-out/graph.html`
- Report: `graphify-out/GRAPH_REPORT.md`

### Cost
Free for AST parsing. Optional API key for semantic analysis of docs/images.

## Bonus: CodeBurn (AI cost observability)

Not a memory layer, but useful for tracking AI token spending:
```bash
npx codeburn  # Terminal dashboard — no install needed
```
Reads local session data from 19 tools (Claude Code, Cursor, Copilot, etc.). No proxy, no API keys. MIT license.

## What goes in `.gitignore`

Both `.memsearch/` and `graphify-out/` are in `.gitignore` by default:
- `.memsearch/` — machine-local session memory, not shared
- `graphify-out/` — derived from source, rebuild with `graphify .`

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Memsearch not capturing | Check plugin is installed: `/plugin list` |
| Memsearch memories stale | Delete old entries in `.memsearch/memory/` |
| Graphify graph outdated | Re-run `graphify .` to rebuild |
| Graphify MCP not responding | Check `.mcp.json` has the graphify server config |
