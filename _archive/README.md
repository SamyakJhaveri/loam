# _archive/

Human-only reference material. Not loaded into Claude Code context.

Wisdom from these docs has already been implemented as active rules, skills,
and agents under `seed/.claude/`. Kept here for occasional manual lookup, not
for re-reading by Claude.

Subfolders:
- `claude-code-mastery/` — operational playbook + mastery reference
- `claude-folder-setup/` — folder-setup PDF
- `better-use-of-graphify/` — deprecated graphify research (superseded by
  CodeGraphContext + Semble)

If you find yourself wanting to point Claude at one of these, instead extract
the relevant rule into `seed/.claude/rules/` so it lives in the loaded surface.

Not the same as the `archive/` directory `copier.yml` creates in bootstrapped
projects — that one is empty working state for the project's user. This
`_archive/` is Loam-template-side static reference only.

Naming policy: subdirectories use kebab-case. File names preserve their
original published titles (so external references to e.g. "Claude Code
Operational Playbook" still resolve at a glance).
