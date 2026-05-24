---
name: academic-research
description: >
  4-skill academic pipeline: deep research (13-agent), academic paper (LaTeX), peer review (7-agent),
  pipeline orchestrator (10-stage). CC BY-NC 4.0 — non-commercial use only.
auto-activate: false
---

# academic-research

Comprehensive academic research pipeline with 4 skills, 10 slash commands, and 3 agents.

**Upstream:** https://github.com/imbad0202/academic-research-skills

## LICENSE WARNING

**CC BY-NC 4.0 — Non-commercial use only.** Users in commercial settings cannot use this plugin. Academic and personal research use only.

## Install

> Install commands are from upstream documentation and may change. Check the [upstream repo](https://github.com/imbad0202/academic-research-skills) for current instructions.

```bash
# Via Claude Code plugin marketplace
/plugin marketplace add Imbad0202/academic-research-skills

# Or clone and symlink
git clone https://github.com/imbad0202/academic-research-skills.git
```

Requires Claude Code v3.7.0+.

## Skills

| Skill | Agents | What it does |
|-------|--------|-------------|
| **deep-research** | 13-agent team | PRISMA-supported systematic review |
| **academic-paper** | 12-agent pipeline | Full paper writing with LaTeX/DOCX output |
| **academic-paper-reviewer** | 7-agent panel | Multi-perspective peer review with 0-100 rubrics |
| **academic-pipeline** | 10-stage orchestrator | End-to-end pipeline with integrity gates |

## Slash Commands

`/ars-research`, `/ars-paper`, `/ars-review`, `/ars-pipeline`, `/ars-search`, `/ars-cite`, `/ars-outline`, `/ars-revise`, `/ars-export`, `/ars-status`

## Optional Dependencies

- **Pandoc** — document conversion
- **Tectonic** — LaTeX compilation
- **Semantic Scholar API key** — enhanced paper search
- **OpenAlex API** — open access metadata
- **Crossref API** — DOI resolution

## Notes

- Very active development, frequent releases
- Most comprehensive academic research tool evaluated
- Integrity gates and temporal verification built in
- Claim audit with L3 faithfulness locators
