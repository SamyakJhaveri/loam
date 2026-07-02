---
name: code-review-graph
description: GraphRAG-powered code review with blast-radius analysis via Tree-sitter AST. MCP server. Recommended for 500+ file codebases.
auto-activate: false
---

# code-review-graph

GraphRAG-powered code review that uses Tree-sitter AST analysis to scope blast radius for diffs and detect architectural hotspots. 24-language support.

**Upstream:** https://github.com/tirth8205/code-review-graph

## Install

```bash
pip install code-review-graph
```

## MCP Server Setup

Add to your project's `.mcp.json`:

```json
{
  "code-review-graph": {
    "type": "stdio",
    "command": "uvx",
    "args": ["code-review-graph", "--stdio"],
    "env": {}
  }
}
```

The MCP server exposes tools for graph-based code analysis.

## How It Complements Loam

- **code-review-graph** decides WHICH code to look at (blast-radius scoping)
- **`/multi-review`** decides WHAT to say about it (quality analysis)

Use code-review-graph first to identify affected files, then feed those into `/multi-review` for focused critique.

## Requirements

- Python 3.10+
- Tree-sitter (auto-installed)
- Optional: sentence-transformers, igraph

## Notes

- MIT license, actively maintained
- No benefit below ~200 files — graph overhead exceeds savings
- Windows has known deadlock issues
- Still Beta with many open issues
