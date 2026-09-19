# Asset layers

Since the 2026-08 rebuild, every agent asset belongs to exactly one of three layers.
One directive, one canonical home.
A duplicate across layers is a bug unless it is an explicit distribution mirror with a verifier-enforced equality contract.

| Layer | Lives in | Reaches a project | Context cost |
|-------|----------|-------------------|--------------|
| Always-on seed harness | `seed/` (shared guidance and skills, Claude settings and the two hooks, Codex config and rules) | Rendered by Copier at bootstrap; updated by `copier update` on new tags | Paid in every session; priced highest |
| Plugin layer | `cultivation/marketplace/sam-cc-setup/` (agents + optional skills + the plan-review workflow) | Installed as a plugin; updates in place | Skill descriptions only, until invoked |
| Marketplace bundles | `cultivation/marketplace/<name>/` | Install-on-demand | Zero until enabled |

Rules of thumb:

- A new asset starts in the project that needed it. It moves UP a layer only when a second project needs it (the plugin trigger from the official docs).
- Anything that must hold every time is a hook in the seed, not prose anywhere.
- The shared skill location for both harnesses is `seed/.agents/skills/` (Codex reads it directly; Claude Code reads it through a checked-in symlink in `.claude/skills/`).
- A seed skill may be pure reference material when the owner requires it in every generated project; keep its description near 40 tokens, because the listing is paid in every session.
- The seed ships two SessionStart-class hooks and no tool-matcher hooks. Command policy is native: `.claude/settings.json` deny rules and `.codex/rules/loam.rules`. See `seed/docs/HARNESS.md`.
- `cultivation/parked/` holds assets removed from the shipped plugin. Nothing installs from it.
