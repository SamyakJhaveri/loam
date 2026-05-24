# storm-research

Stanford STORM — LLM research pipeline for Wikipedia-quality articles with citations. Multi-perspective research, Co-STORM collaborative mode.

**Upstream:** https://github.com/stanford-oval/storm

## Install

```bash
pip install knowledge-storm
```

## API Keys Required

1. `ANTHROPIC_API_KEY` — Claude models (native `ClaudeModel` class)
2. Search engine key — Bing, You.com, Serper, Brave, or Tavily

## How It Complements Loam

- `/researcher` — quick single-pass web research
- STORM — systematic multi-perspective literature review with citations

## Notes

- MIT license, Stanford-backed
- Development pace has slowed — may be less actively maintained
- No MCP server or Claude Code integration — requires Python invocation
- Research-flavor tool
