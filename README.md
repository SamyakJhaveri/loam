# Loam

**Bootstrap a project with a tested Claude Code and Codex harness.**

![Loam](docs/assets/hero-identity.jpg)

Loam is a [Copier](https://copier.readthedocs.io/) template. It renders shared agent guidance, Claude Code hooks and settings, and Codex policy into a new or existing project. A release gate verifies the complete rendered harness before a Loam release ships.

```bash
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
```

The result is a small harness with explicit routes and enforceable local policy.

![Bootstrap demo](docs/assets/bootstrap.gif)

## Why this exists

A large always-loaded instruction file makes every session carry material it may not need. Copying the same setup by hand across projects also creates drift.

Loam fixes both:

- **One shared prose home.** Codex reads `AGENTS.md` directly. Claude Code imports it from `CLAUDE.md` and adds only Claude-specific guidance.
- **Tag-based updates.** `copier update` pulls released template changes into an existing project. Reusable optional assets move back into the plugin marketplace by a reviewed manual promotion.
- **Rendered policy.** Claude hooks enforce checkout and turn-end checks. A Codex hook rejects recognized force pushes. Codex execution rules add defense in depth.
- **One public release gate.** `bin/verify-template.sh` renders a project and checks the complete generated harness before release.

## What you get

- `AGENTS.md` and `CLAUDE.md` with fill-in project guidance.
- `.claude/` settings and hook scripts.
- A shared `/catchup` skill under `.agents/skills/`.
- `.codex/` configuration, hook policy, and execution rules.
- Optional agents and skills from `cultivation/marketplace/`.

## Quick start

```bash
# Bootstrap a new project
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update --trust
```

## Scope, honestly

Loam supports Claude Code and Codex through different native mechanisms. Both read the shared skill source and project guidance. Claude Code uses `.claude/settings.json` for its hooks. Codex uses `.codex/hooks.json` and execution rules. Optional plugin skills and agents are Claude Code assets unless their own documentation says otherwise.

## Project structure

```
loam/
├── seed/                    # Copier subdirectory — everything rendered to projects
│   ├── .agents/skills/      # Skills shared by Claude Code and Codex
│   ├── .claude/             # Claude Code hooks and settings
│   ├── .codex/              # Codex hook policy and execution rules
│   └── *.jinja              # Template files (CLAUDE.md, AGENTS.md, README.md, …)
├── cultivation/marketplace/ # Optional plugin bundles
├── soil/                    # Local-only knowledge base (gitignored)
├── bin/                     # Verification and release tooling
├── docs/                    # Template documentation
└── copier.yml               # Template config
```

## Verification

Run `bin/verify-template.sh` when changing Loam. It renders the template, checks the Rendered Harness Contract, and runs native Claude or Codex checks when those tools are installed.

## Documentation

- `docs/BOOTSTRAP.md` — First-session setup guide
- `docs/COPIER.md` — Template configuration details
- `docs/SYNC.md` — Forward updates and reverse promotion
- `docs/ASSET-LAYERS.md` — Asset organization

## Roadmap

- **Marketplace polish** — one-command install for every bundle via the plugin marketplace
- **Policy coverage** — extend native harness checks when a repeated failure earns a new guardrail

## Requirements

- [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier` needs no install)
- Python 3.11 or newer for the Rendered Harness Contract checker
- Optional: [Claude Code](https://code.claude.com/docs) and Codex CLIs for native supplemental checks

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changelog lives in
[GitHub Releases](https://github.com/SamyakJhaveri/loam/releases).

## License

MIT. See [LICENSE](LICENSE). A vendored marketplace bundle may carry its own `LICENSE.upstream`; that file is authoritative for the vendored content.
