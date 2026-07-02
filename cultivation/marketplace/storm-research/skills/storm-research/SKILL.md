---
name: storm-research
description: >
  Stanford STORM — LLM research pipeline for Wikipedia-quality articles with citations.
  Multi-perspective research, Co-STORM collaborative mode. Python package, no native Claude Code integration.
auto-activate: false
---

# storm-research

Stanford's STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective question asking) — an LLM-powered research pipeline that produces Wikipedia-quality articles with citations.

**Upstream:** https://github.com/stanford-oval/storm

## Install

```bash
pip install knowledge-storm
```

## Usage with Claude

STORM has native Claude support via its `ClaudeModel` class:

```python
from knowledge_storm import STORMWikiRunnerArguments, STORMWikiRunner
from knowledge_storm.lm import ClaudeModel

claude_model = ClaudeModel(
    model="<your-model>",  # e.g. claude-sonnet-4-6
    max_tokens=4096
)

runner_args = STORMWikiRunnerArguments(
    output_dir="./output"
)

runner = STORMWikiRunner(runner_args, claude_model, claude_model)
runner.run(
    topic="Your Research Topic",
    do_research=True,
    do_generate_outline=True,
    do_generate_article=True,
    do_polish_article=True
)
```

## API Keys Required

1. **ANTHROPIC_API_KEY** — for Claude models
2. **Search engine key** — one of: Bing, You.com, Serper, Brave, or Tavily

## Co-STORM Mode

Co-STORM enables collaborative research where you and the LLM investigate together through multi-perspective questioning. Start a Co-STORM session to iteratively refine research direction.

## How It Complements Loam

- **`/researcher`** — quick web research, single-pass
- **STORM** — systematic multi-perspective literature review with citations

Use `/researcher` for fast lookups. Use STORM when you need a structured article with proper citations.

## Requirements

- Python 3.x
- dspy, litellm, streamlit
- Two API keys minimum (LLM + search engine)

## Notes

- MIT license, Stanford-backed
- Development pace has slowed — may be less actively maintained
- No MCP server or Claude Code skill integration — requires Python invocation
- Best-in-class research quality for systematic reviews
