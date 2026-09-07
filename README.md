# Loam

**Bootstrap a project with a tested Claude Code and Codex harness.**

![Loam](docs/assets/hero-identity.jpg)

Loam is a [Copier](https://copier.readthedocs.io/) template. It renders shared agent guidance, Claude Code settings, and Codex policy into a new or existing project. One check, `bin/check`, gates every change.

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
- **Native policy, no text parsing.** Claude Code deny rules and `.codex/rules/loam.rules` block the destructive command families in both harnesses, and a repository ruleset guards the default branch. Two SessionStart-class hooks remain, so a tool call pays no hook latency.
- **One check.** `bin/check` runs lint, shell syntax, tests, plugin validation, and a render smoke. The agent and CI run the same script.

## What you get

- `AGENTS.md` and `CLAUDE.md` with fill-in project guidance.
- `.claude/` settings, deny rules, and two SessionStart-class hooks.
- A shared `/catchup` skill under `.agents/skills/`.
- A shared `/fable-prompting` skill under `.agents/skills/`: which Fable 5.1 guide sections a prompt can act on.
- `.codex/` configuration and execution rules.
- `bin/check` and a CI workflow that runs it.
- `docs/HARNESS.md` and `docs/WORKERS.md`, read on demand.
- Optional agents and skills from `cultivation/marketplace/`.

## Quick start

```bash
# Bootstrap a new project
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update --trust
```

## Scope, honestly

Loam supports Claude Code and Codex through different native mechanisms. Both read the shared skill source and project guidance. Claude Code uses `.claude/settings.json` for permissions, the sandbox, and hooks. Codex uses `.codex/config.toml` and execution rules. Optional plugin skills and agents are Claude Code assets unless their own documentation says otherwise.

## Project structure

```
loam/
├── seed/                    # Copier subdirectory: everything rendered to projects
│   ├── .agents/skills/      # Skills shared by Claude Code and Codex
│   ├── .claude/             # Claude Code settings, deny rules, two hooks
│   ├── .codex/              # Codex config and execution rules
│   └── *.jinja              # Template files (CLAUDE.md, AGENTS.md, README.md, ...)
├── cultivation/marketplace/ # Optional plugin bundles
├── soil/                    # Local-only knowledge base (gitignored)
├── bin/                     # Check and release tooling
├── docs/                    # Template documentation
└── copier.yml               # Template config
```

## Verification

Run `bin/check` when changing Loam. It lints, checks shell syntax and whitespace, runs the tests including a render smoke, and validates the shipped plugins.

## Documentation

- `docs/BOOTSTRAP.md` - First-session setup guide
- `docs/COPIER.md` - Template configuration details
- `docs/SYNC.md` - Forward updates, reverse promotion, and attach mode
- `docs/ASSET-LAYERS.md` - Asset organization
- `seed/docs/HARNESS.md` - What the shipped harness guards, and the accepted risks

## Roadmap

- **Marketplace polish** - one-command install for every bundle via the plugin marketplace
- **Policy coverage** - extend the native deny lists when a repeated failure earns a new guardrail

## Requirements

- [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier` needs no install)
- Python 3.11 or newer, with `pytest` and `ruff`, to run `bin/check`
- [Claude Code](https://code.claude.com/docs) and Codex CLIs: `bin/check` fails without them (set `LOAM_ALLOW_MISSING_AGENT_CLIS=1` for a reduced local run)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changelog lives in
[GitHub Releases](https://github.com/SamyakJhaveri/loam/releases).

## License

MIT. See [LICENSE](LICENSE). A vendored marketplace bundle may carry its own `LICENSE.upstream`; that file is authoritative for the vendored content.
