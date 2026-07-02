# code-review-graph

GraphRAG-powered code review via Tree-sitter AST analysis. Scopes blast radius for diffs and detects architectural hotspots. 24-language support.

**Upstream:** https://github.com/tirth8205/code-review-graph

## Install

```bash
pip install code-review-graph
```

## MCP Server Setup

See SKILL.md for MCP server configuration.

## Requirements

- Python 3.10+
- Recommended for 500+ file codebases (graph overhead exceeds savings below ~200 files)

## Notes

- MIT license, actively maintained
- Complements `/multi-review`: code-review-graph scopes WHICH code to review, `/multi-review` decides WHAT to say
- Windows has known deadlock issues
