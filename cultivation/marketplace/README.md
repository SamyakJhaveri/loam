# Marketplace Skills

Marketplace-candidate skills. **Not shipped to projects bootstrapped from this template** — `_exclude` in `copier.yml` keeps them out of `copier copy`.

These are skills that were removed from the default `.claude/skills/` set during the v2.0 single-tree rework. They're kept here as installable plugin bundles.

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
| `helpers` | decision-matrix, navigate, model-route, prompt-improver, frontend-design, grill-research | Situational utility skills for specialized one-off tasks |
| `business-process` | process-optimizer, sop-writer, workflow-mapper, weekly-review | Operational documentation and workflow analysis |
| `pocock-engineering` | triage, to-issues, to-prd, tdd, prototype, diagnose, grill-with-docs, improve-codebase-architecture, zoom-out | Engineering workflow skills from [mattpocock/skills](https://github.com/mattpocock/skills) — issue lifecycle, TDD, prototyping, architectural review, domain grilling, PRD generation |

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
