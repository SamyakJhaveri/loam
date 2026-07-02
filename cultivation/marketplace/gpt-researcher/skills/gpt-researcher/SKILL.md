---
name: gpt-researcher
description: >
  Autonomous multi-source research agent with MCP server. Planner/executor architecture, 5 MCP tools.
  Requires 3 API keys (Tavily + Anthropic + embeddings). Research-flavor.
auto-activate: false
---

# gpt-researcher

Autonomous multi-source research agent with a planner/executor architecture. Gathers information from multiple sources in parallel.

**Upstream:** https://github.com/assafelovic/gpt-researcher
**MCP Server:** https://github.com/assafelovic/gptr-mcp

## MCP Server Setup

Add to your project's `.mcp.json`:

```json
{
  "gpt-researcher": {
    "type": "stdio",
    "command": "uvx",
    "args": ["gptr-mcp"],
    "env": {
      "TAVILY_API_KEY": "<your-key>",
      "ANTHROPIC_API_KEY": "<your-key>",
      "FAST_LLM": "anthropic:<your-fast-model>",
      "SMART_LLM": "anthropic:<your-smart-model>"
    }
  }
}
```

Replace `<your-fast-model>` and `<your-smart-model>` with your preferred Claude model IDs before use.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `deep_research` | Full multi-source research on a topic |
| `quick_search` | Fast single-source lookup |
| `write_report` | Generate structured report from research |
| `get_research_sources` | List sources used in research |
| `get_research_context` | Retrieve accumulated research context |

## API Keys Required

1. **TAVILY_API_KEY** — search engine (required)
2. **ANTHROPIC_API_KEY** — LLM provider (required)
3. **Embedding provider key** — for semantic search (required)

## How It Complements Loam

- **`/researcher`** — quick single-pass web research
- **GPT-Researcher** — autonomous multi-source deep research with structured reports

## Requirements

- Python 3.11+
- Three API keys minimum
- MCP server is from separate repo (`gptr-mcp`), early-stage

## Notes

- Apache-2.0 license
- Originally OpenAI-focused, but has native Anthropic provider support
- MCP server is early-stage (separate repo) — expect rough edges
- Per-invocation cost varies by research depth
