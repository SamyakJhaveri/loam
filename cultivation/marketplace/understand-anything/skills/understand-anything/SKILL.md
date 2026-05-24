---
name: understand-anything
description: Multi-agent codebase analysis with interactive React knowledge graph dashboard. Best for onboarding and visual architecture exploration.
auto-activate: false
---

# understand-anything

Multi-agent codebase analysis pipeline that builds an interactive React knowledge graph dashboard. Useful for onboarding and visual architecture exploration.

**Upstream:** https://github.com/Lum1104/Understand-Anything

## Install

> Install commands are from upstream documentation and may change. Check the [upstream repo](https://github.com/Lum1104/Understand-Anything) for current instructions.

```bash
# Via Claude Code plugin marketplace
/plugin marketplace add Lum1104/Understand-Anything

# Or clone and symlink
git clone https://github.com/Lum1104/Understand-Anything.git
```

## Commands

| Command | Purpose |
|---------|---------|
| `/understand` | Full codebase analysis and knowledge graph build |
| `/understand-dashboard` | Launch interactive React dashboard |
| `/understand-chat` | Chat with the knowledge graph |
| `/understand-diff` | Analyze changes against existing graph |
| `/understand-domain` | Domain-specific analysis |

## Overlap Warning

Overlaps with **Semble + CodeGraphContext** in Loam's diagrams stack. Unique value is the interactive React dashboard for visual exploration.

## Cost Warning

LLM calls during initial codebase scan can be expensive. Claims 70x token reduction after initial build, but the build itself costs tokens.

## Requirements

- TypeScript/pnpm
- LLM API key (for analysis phase)

## Notes

- MIT license, actively maintained
- Best for onboarding — commit the knowledge graph for new team members
- Dashboard is the differentiator vs. other graph tools
