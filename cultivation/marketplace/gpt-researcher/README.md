# gpt-researcher

Autonomous multi-source research agent with MCP server integration. Planner/executor architecture, parallel source gathering.

**Upstream:** https://github.com/assafelovic/gpt-researcher
**MCP Server:** https://github.com/assafelovic/gptr-mcp

## MCP Server Setup

See SKILL.md for MCP server configuration and API key requirements.

## API Keys Required

1. `TAVILY_API_KEY` — search engine
2. `ANTHROPIC_API_KEY` — LLM provider
3. Embedding provider key

## Notes

- Apache-2.0 license
- MCP server is early-stage (separate repo) — expect rough edges
- Per-invocation cost varies by research depth
- Research-flavor tool
