# seed-skills

Marketplace-candidate skills. **Not shipped to projects bootstrapped from this template** — `_exclude` in `copier.yml` keeps them out of `copier copy`.

These are skills that were removed from the default `.claude/skills/` set during the v2.0 single-tree rework. They're kept here for two reasons:

1. **Reference.** If a future project needs one, copy it back into `.claude/skills/` or install it as a plugin.
2. **Future plugin marketplace.** Phase-4 of the rework wires these as installable plugins via `.claude-plugin/marketplace.json`, then projects can `/plugin install <name>` on demand instead of carrying every skill at bootstrap.

## Why these skills were cut from default

The cut was driven by `.claude/rules/known-issues.md`: with 60+ skills competing for auto-invocation, false positives waste tokens and confuse sessions. The 18 core skills are the daily-driver loop plus the framework's own features (`template-sync`, `create-skill`). The 14 cut here are specialized, meta-meta, or duplicate functionality already in core.

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

## How to bring one back

```bash
# In a project bootstrapped from this template:
cp -R /path/to/project_seed_framework/seed-skills/<skill-name> .claude/skills/

# In the template itself (will then ship to future bootstraps):
git mv seed-skills/<skill-name> .claude/skills/<skill-name>
```

## Future plugin-marketplace structure (planned)

```
seed-skills/
├── .claude-plugin/
│   └── marketplace.json          # registers each pack as installable plugin
├── meta-improvement/             # bundle: reflect, dream variants, self-healing
│   └── .claude-plugin/plugin.json
├── team-deliberation/            # bundle: agent-team, council, session-critique
│   └── .claude-plugin/plugin.json
├── ...
```

Then `/plugin marketplace add path/to/seed-skills` followed by `/plugin install meta-improvement` etc.
