# Marketplace Skills

Marketplace-candidate skills. **Not shipped to projects bootstrapped from this template** — `_exclude` in `copier.yml` keeps them out of `copier copy`.

Includes skills removed from the default `.claude/skills/` set during the v2.0 single-tree rework, plus external tool and plugin adoptions bundled for easy installation. All kept here as installable plugin bundles.

## Install

```bash
# From a project bootstrapped from this template:
/plugin marketplace add /path/to/loam/cultivation/marketplace
/plugin install team-deliberation    # or: meta-improvement, helpers, business-process
```

## Bundles

| Bundle | Skills | Purpose |
|--------|--------|---------|
| `team-deliberation` | agent-team, council, session-critique | Multi-agent deliberation and adversarial critique |
| `meta-improvement` | self-healing | Autonomous error recovery and session self-correction |
| `helpers` | decision-matrix, navigate, model-route, prompt-improver, frontend-design, grill-research, align-prompt | Situational utility skills for specialized one-off tasks |
| `business-process` | process-optimizer, sop-writer, workflow-mapper, weekly-review | Operational documentation and workflow analysis |
| `pocock-engineering` | triage, to-issues, to-prd, tdd, prototype, diagnose, grill-with-docs, improve-codebase-architecture, zoom-out | Engineering workflow skills from [mattpocock/skills](https://github.com/mattpocock/skills) — issue lifecycle, TDD, prototyping, architectural review, domain grilling, PRD generation |
| `code-review-graph` | code-review-graph | GraphRAG-powered code review with blast-radius analysis. [Upstream](https://github.com/tirth8205/code-review-graph). MCP server, recommended for 500+ file codebases |
| `planning-with-files` | planning-with-files | Manus-style persistent markdown planning. [Upstream](https://github.com/othmanadi/planning-with-files). Overlaps with feature-dev + plan mode |
| `understand-anything` | understand-anything | Codebase knowledge graph with React dashboard. [Upstream](https://github.com/Lum1104/Understand-Anything). Overlaps with Semble + CodeGraphContext |
| `ui-ux-pro-max` | ui-ux-pro-max | Design system generator with curated palettes, fonts, and UI styles. [Plugin Hub](https://www.claudepluginhub.com/plugins/nextlevelbuilder-ui-ux-pro-max). Frontend-focused |
| `impeccable` | impeccable | Design polish with 27 deterministic anti-pattern rules + LLM critique. [Plugin Hub](https://www.claudepluginhub.com/plugins/pbakaus-impeccable). By Paul Bakaus. Apache-2.0 |
| `storm-research` | storm-research | Stanford STORM research pipeline for Wikipedia-quality articles. [Upstream](https://github.com/stanford-oval/storm). Python package, research-flavor |
| `gpt-researcher` | gpt-researcher | Autonomous multi-source research agent with MCP server. [Upstream](https://github.com/assafelovic/gpt-researcher). Research-flavor, 3 API keys required |
| `academic-research` | academic-research | 4-skill academic pipeline — research, paper writing, peer review, orchestrator. [Upstream](https://github.com/imbad0202/academic-research-skills). **CC BY-NC 4.0** |
| `nature-skills` | nature-skills | 9 Nature-journal skills — figures, polishing, citations, writing, data, search. [Upstream](https://github.com/yuan1z0825/nature-skills). MIT, research-flavor |

## Why these skills were cut from default

The cut was driven by `.claude/rules/known-issues.md`: with 60+ skills competing for auto-invocation, false positives waste tokens and confuse sessions. The 19 core skills are the daily-driver loop plus the framework's own features (`template-sync`, `create-skill`). The 14 here are specialized, meta-meta, or duplicate functionality already in core.

| Skill | Why cut |
|-------|---------|
| `agent-team` | Overlaps with `multi-review`, `session-critique` (multiple "spawn a team" skills) |
| `council` | Same — multi-agent deliberation, overlaps with `multi-review` |
| `session-critique` | Same — overlapping team pattern |
| `self-healing` | Vague meta-skill; overlaps with `reflect`, `dream`, `know-me` |
| `decision-matrix` | Knowledge-injection skill with no clear trigger boundary |
| `frontend-design` | Skill is specialized; the rule (`.claude/rules/frontend-design.md`) loads path-scoped when relevant |
| `grill-research` | Adversarial 4-wave skill; overlaps with `multi-review` for quality gates |
| `model-route` | Meta-meta (recommending a model for a task) |
| `navigate` | Meta-meta (recommending tools to Claude — Claude already does this) |
| `prompt-improver` | Niche; specific use case |
| `process-optimizer` | Business-consultant skill; not aligned with engineering/research workflow |
| `sop-writer` | Same — business-process focus |
| `workflow-mapper` | Same — business-process focus |
| `weekly-review` | Personal-productivity meta-skill; orthogonal to a starter template |
| `triage` | New adoption — evaluate before promoting to core |
| `to-issues` | New adoption — evaluate before promoting to core |
| `tdd` | New adoption — coexists with superpowers:test-driven-development |
| `prototype` | New adoption — specialized, disposable-code workflow |
| `diagnose` | New adoption — heavyweight diagnostic for hard bugs |
| `grill-with-docs` | New adoption — domain grilling, evaluate DOMAIN.md pattern first |
| `improve-codebase-architecture` | New adoption — heavy Ousterhout-based review with HTML reports |
| `to-prd` | New adoption — synthesizes conversation into PRD, complements gen-spec |
| `zoom-out` | New adoption — micro-skill (disable-model-invocation), contextual cue |

External tool bundles (code-review-graph through nature-skills) were adopted directly into the marketplace and were never part of the default skill set.
