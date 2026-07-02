# Loam

**Bootstrap any project with a production-grade AI-agent setup — and keep every project in sync from one template.**

![Loam](docs/assets/hero-identity.jpg)

Loam is a [Copier](https://copier.readthedocs.io/) template that gives a new (or existing) project a complete, battle-tested Claude Code configuration: curated skills, enforcement hooks, layered context routing, and a validation gate that blocks bad commits. When the template improves, every project pulls the update with one command — and skills you build in a project can be promoted back.

```bash
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project
```

That's the whole bootstrap. Sixty seconds later you have a project where the agent knows where it is, what to load, and what it's not allowed to skip.

![Bootstrap demo](docs/assets/bootstrap.gif)

## Why this exists

A 2,000-line CLAUDE.md doesn't make an agent smarter — it makes every session pay a token tax for context it mostly ignores. And when you work across several projects, every improvement to your agent setup has to be hand-copied into each repo, where it silently drifts.

Loam fixes both:

- **Layered context routing with token budgets** — an ~800-token `CLAUDE.md` map (L0), per-directory `CONTEXT.md` routers (L1), per-task stage contracts (L2), and path-scoped rules that load only when matching files are touched. The agent loads what the task needs, not everything you ever wrote.
- **Template propagation, both directions** — `copier update` pulls template improvements into every project (three-way merge, tag-based). `template-sync promote` sends a battle-tested skill from a project back to the template as a PR.
- **An enforced pipeline gate** — `/validate` runs deterministic + rule-based check waves before any commit; a pre-commit hook blocks commits until it passes. Not a convention — a gate.

## What you get

- **27 core skills** — feature-dev, fix-bug, validate, ship, commit, pr, multi-review, session-critique, catchup, handoff, researcher, agent-team, and more
- **10 hooks** — pre-commit validation gate, turn-end verify gate, session-start brief, sentinel cleanup, audit logging, plan-location routing
- **16 rules** — 6-stage session workflow, known-issues gotcha log, token-budget guidance, path-scoped language rules
- **6 agents** — plan-reviewer (adversarial review + elegance gate), self-critic, verification-lead, explorer, diff-reviewer, security-scanner
- **Research flavor** (optional, `-d is_research=true`) — 18 additional skills: paper-write, cite-check, eval-run, experiment, hypothesis-tree, rebuttal, and more
- **Skill marketplace** — optional bundles under `cultivation/marketplace/`, installable on demand

## Quick start

```bash
# Bootstrap a new project
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# With the research flavor
uvx copier copy --trust -d is_research=true gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update --trust
```

**📊 [Visual Overview](docs/VISUAL-OVERVIEW.md)** — diagrams of Loam's architecture, lifecycle, and workflow.

## Scope, honestly

Loam is **Claude-Code-first**. Skills follow the [agentskills.io](https://agentskills.io/specification) SKILL.md standard (a portable, tool-agnostic format), and a rendered `AGENTS.md` bridges Codex and other AGENTS.md-aware agents to the same conventions — but hooks, the validation gate, and slash-command workflows are Claude Code features today. If you live in Claude Code, this is built for you; if not, you get the context architecture and the skill *definitions* as conventions — not skill execution or the enforcement gate.

## Project structure

```
loam/
├── seed/                    # Copier subdirectory — everything rendered to projects
│   ├── .claude/             # Skills, agents, hooks, rules, settings
│   ├── _research/           # Research flavor overlay (optional)
│   └── *.jinja              # Template files (CLAUDE.md, AGENTS.md, README.md, …)
├── cultivation/             # Skill lifecycle: marketplace bundles, retired skills
├── soil/                    # Local-only knowledge base (gitignored)
├── bin/                     # verify-template.sh, template-sync.sh, release.sh
├── docs/                    # Template documentation
└── copier.yml               # Template config
```

## The workflow it ships

```
Implement → /validate (pipeline gate) → /commit → /pr
```

Six-stage session workflow (orient → explore → plan → implement → record → verify), surgical exploration rules, plan-review sub-workflow with an adversarial reviewer agent, and a 60/30/10 triage that routes work to deterministic tools before rules before model reasoning. See [docs/VISUAL-OVERVIEW.md](docs/VISUAL-OVERVIEW.md).

## Documentation

- `docs/BOOTSTRAP.md` — First-session setup guide
- `docs/MEMORY.md` — Memory stack architecture
- `docs/COPIER.md` — Template configuration details
- `docs/FLAVORS.md` — Flavor system documentation
- `docs/SYNC.md` — Template sync workflow (update + promote)
- `docs/ASSET-LAYERS.md` — Asset organization

## Roadmap

- **Multi-harness parity** — tested Codex / OpenCode support beyond the AGENTS.md bridge
- **Marketplace polish** — one-command install for every bundle via the plugin marketplace
- **Research-overlay update hardening** — first-class `copier update` support for the flavor overlay

## Requirements

- [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`uvx copier` needs no install)
- [Claude Code](https://code.claude.com/docs) CLI

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Changelog lives in [GitHub Releases](../../releases).

## License

MIT — see [LICENSE](LICENSE). Vendored marketplace bundles retain their upstream license as a `LICENSE.upstream` file (Apache-2.0, MIT, or — for `academic-research` — CC BY-NC 4.0, which is NonCommercial); bundles authored for Loam fall under the repo MIT. See [`cultivation/marketplace/README.md`](cultivation/marketplace/README.md#licensing--attribution) for per-bundle provenance.
