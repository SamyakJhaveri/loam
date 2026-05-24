---
name: nature-skills
description: >
  9 Nature-journal skills: figures, polishing, writing, citations, data availability,
  paper reading, reviewer responses, paper-to-PPT, academic search (MCP). MIT license.
auto-activate: false
---

# nature-skills

9 skills optimized for Nature-journal-family (CNS: Cell/Nature/Science) academic publishing.

**Upstream:** https://github.com/yuan1z0825/nature-skills

## Install

> Install commands are from upstream documentation and may change. Check the [upstream repo](https://github.com/yuan1z0825/nature-skills) for current instructions.

```bash
# Via Claude Code plugin marketplace
/plugin marketplace add yuan1z0825/nature-skills

# Or clone and symlink
git clone https://github.com/yuan1z0825/nature-skills.git
```

## Skills

| Skill | Status | What it does |
|-------|--------|-------------|
| **nature-figure** | Stable | Publication-quality figures (Matplotlib, SVG) |
| **nature-polishing** | Stable | Prose refinement for journal standards |
| **nature-writing** | Draft | Full manuscript drafting |
| **nature-citation** | Beta | CNS-family citation formatting |
| **nature-data** | Draft | FAIR metadata and data availability statements |
| **nature-reader** | Beta | Bilingual paper reading and conversion |
| **nature-response** | Beta | Reviewer response letter generation |
| **nature-paper2ppt** | Beta | Paper-to-PPTX deck conversion |
| **nature-academic-search** | Beta | Multi-source academic search (has MCP server) |

## MCP Server (Academic Search)

The `nature-academic-search` skill includes an MCP server for multi-source academic search:

```bash
bash install.sh your-email@example.com
```

## Optional Dependencies

- Python
- NCBI API key (for PubMed access)

## Notes

- MIT license
- Nature-journal-specific — best for researchers targeting CNS family journals
- Many skills still Beta/Draft — expect rough edges
- MCP server for academic search adds value beyond the skills alone
