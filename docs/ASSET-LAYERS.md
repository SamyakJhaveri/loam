# Asset layers

Since the 2026-08 rebuild, every agent asset belongs to exactly one of three layers.
One directive, one canonical home.
A duplicate across layers is a bug unless it is an explicit distribution mirror with a verifier-enforced equality contract.

| Layer | Lives in | Reaches a project | Context cost |
|-------|----------|-------------------|--------------|
| Always-on seed harness | `seed/` (shared guidance and skill, Claude hooks and settings, Codex hook policy and rules) | Rendered by Copier at bootstrap; updated by `copier update` on new tags | Paid in every session; priced highest |
| Plugin layer | `cultivation/marketplace/sam-cc-setup/` (agents + optional skills + the plan-review workflow) | Installed as a plugin; updates in place | Skill descriptions only, until invoked |
| Marketplace bundles | `cultivation/marketplace/<name>/` | Install-on-demand | Zero until enabled |

Rules of thumb:

- A new asset starts in the project that needed it. It moves UP a layer only when a second project needs it (the plugin trigger from the official docs).
- Anything that must hold every time is a hook in the seed, not prose anywhere.
- The shared skill location for both harnesses is `seed/.agents/skills/` (Codex reads it directly; Claude Code reads it through a checked-in symlink in `.claude/skills/`).
- The canonical concurrent-checkout guard is `seed/.claude/hooks/concurrent-checkout-guard.sh`. The `sam-cc-setup` plugin carries a byte-identical distribution mirror for projects that do not use the Loam seed. `bin/rendered_harness_contract.py` rejects drift or a missing copy.
- `cultivation/wip/` stages work that has no placement verdict yet.
