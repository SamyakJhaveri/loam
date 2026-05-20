# Memory architecture (engineering + research)

Three complementary memory layers plus two adjacent tools. Each layer answers a different question; they do not overlap.

## The layers

| Layer | Tool | What it stores | Question it answers |
|-------|------|----------------|---------------------|
| L1 — Static knowledge | Built-in (CLAUDE.md + `.claude/rules/` + Anthropic native memory tool) | Project conventions, coding standards, known issues, durable cross-session facts | What are our rules? |
| L2 — Structured facts | [Knowledge-Graph Memory MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/memory) (Anthropic reference server, JSONL-backed Entities/Relations/Observations) | Explicit claims, decisions, observed behaviors, named entities | What do we know about X, and how does it connect to Y? |
| L3 — Codebase map | [Graphify](https://github.com/safishamsi/graphify) | Module relationships, dependency graphs, AST-derived structure | How is the code organized; what depends on what? |

Adjacent (not memory, but related):

| Tool | Role |
|------|------|
| [Superpowers](https://github.com/obra/superpowers) | Process scaffolding (TDD discipline, brainstorming, journaling). The journal it produces becomes L1/L2 input over time. |
| [CodeBurn](https://github.com/anthropic-experimental/codeburn) | Cost / token observability. Not a memory layer. |

## Layer 1 — built-in (always on)

Three sub-channels, all configured by default:

- `CLAUDE.md` at project root — the L0 entry, ~800-token budget. See `.claude/rules/L0-budget.md`.
- `.claude/rules/*.md` — path-scoped rules that load only when matching files are touched (the L3 of ICM routing).
- **Anthropic native memory tool** — built into Claude Code v2.1.59+. The model can create / read / update / delete files in a session-persistent memory directory under `~/.claude/projects/<key>/memory/`. No installation required.

Claude Code's built-in memory tool writes durable user-preference and project-fact entries to this directory automatically during sessions.

## Layer 2 — Knowledge-Graph Memory MCP

Ships enabled in `.mcp.json` of every project bootstrapped from this template. The MCP server runs locally via `npx @modelcontextprotocol/server-memory` and stores entities + relations + observations in a JSONL file under `.claude-memory/knowledge-graph.json`.

When to use vs L1 native memory:
- **L1 native memory** is for free-form text the model writes naturally during sessions (preferences, gotchas, recent decisions in prose).
- **L2 Knowledge-Graph MCP** is for structured facts you want to query: "what entities relate to X?" "what observations contradict claim Y?" Use when the project accumulates a body of named entities (modules, experiments, papers, people) with explicit relationships.

Both can coexist. Native memory is the default workspace; the KG server is a queryable index of structured claims.

### Setup

Zero setup if `npx` is available — `.mcp.json` invokes it on session start. To verify:

```bash
npx -y @modelcontextprotocol/server-memory --help
```

The first run will pull the package; subsequent runs are cached.

Storage: `.claude-memory/knowledge-graph.json` (gitignored by default; rebuild from session evidence if lost).

## Layer 3 — Graphify (codebase map)

AST-derived knowledge graph of the codebase across 29 languages (Tree-sitter). Identifies "god nodes" (modules everything depends on), generates an interactive HTML graph, and runs as an MCP server so the model can query the structure directly.

### Setup

```bash
uv tool install graphifyy   # or: pip install graphifyy
graphify .                  # build the graph; produces graphify-out/
graphify claude install     # register as MCP server (optional; .mcp.json already wires it)
```

Storage:
- `graphify-out/graph.json` — the queryable graph
- `graphify-out/graph.html` — interactive visualization
- `graphify-out/GRAPH_REPORT.md` — human-readable summary

The graph is derived from source; rebuild with `graphify .` after significant refactors. `graphify-out/` is gitignored.

## Adjacent — Superpowers (process scaffolding)

Not a memory layer. Installed as a Claude Code plugin:

```bash
/plugin marketplace add obra/superpowers
/plugin install superpowers
```

Provides the brainstorming, journaling, and TDD-discipline skills that Jesse Vincent's Superpowers framework uses. Worth installing for the journaling skill alone — the entries it writes feed Layer 1 native memory over time.

## Adjacent — CodeBurn (cost observability)

Terminal dashboard for token / cost spend across 19 AI coding tools (Claude Code, Cursor, Copilot, etc.). Reads local session data; no proxy, no API keys. MIT.

Not memory — included here because the user runs it alongside the memory stack to track the cost of leaving multiple MCPs active.

### Quick start (no install)

```bash
npx codeburn       # opens the dashboard; persists nothing to the repo
```

## What to .gitignore

Already in the template's `.gitignore.jinja`:

- `.claude-memory/` — Knowledge-Graph MCP storage (machine-local, ungitable across machines without conflict)
- `graphify-out/` — derived; rebuild from source
- `~/.claude/projects/<key>/memory/` — actually outside the repo, no gitignore needed

## Skills that wire into the memory layers

| Skill | Wires to | When |
|-------|----------|------|
| `dream` | L1 native memory (consolidation pass) | Manual `/dream`; also notified at SessionStart if ≥24h since last consolidation |
| `researcher` | L2 KG MCP + L1 native | Research projects — captures hypotheses, claims, citations as structured entities |

## Memsearch — explicitly NOT in this stack

Memsearch was in earlier iterations. Removed in v2.0 of the framework — the user prefers the lighter L1+L2+L3 set, and Memsearch's Markdown-first session journal duplicates what the `dream` skill produces against the native memory tool.

## claude-mem — explicitly REJECTED

Two unresolved issues (documented in v2.0's SESSION-P-HANDOFF.md, removed in v3.0) and ongoing community reports:
1. The HTTP server binds to `0.0.0.0` — exposed on shared/networked machines.
2. Issue #618 (open): context injection volume exhausts Claude Code session limits in <10 messages on medium projects.

Revisit if upstream resolves both.
