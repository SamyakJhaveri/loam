# Loam

A Copier template that bootstraps Claude Code projects with battle-tested skills, hooks, agents, and a structured memory stack. Built for researchers and software engineers working on advanced projects.

## What you get

When you run `copier copy`, Loam generates a project with:

- **21 skills** — feature-dev, fix-bug, commit, validate, ship, multi-review, session-critique, and more
- **7 hooks** — pre-commit validation gate, post-edit test runner, session-start context, audit logging, result immutability, sentinel cleanup, compact recovery
- **Structured memory** — 3-layer routing stack (CLAUDE.md → CONTEXT.md → stage contracts) + MCP tools (CodeGraphContext, Semble, Knowledge Graph)
- **Research flavor** (optional) — paper-write, cite-check, eval-run, experiment, hypothesis-tree, and 18 research-specific skills total

## Quick start

```bash
# Bootstrap a new project
uvx copier copy gh:samyakjhaveri/loam ./my-project

# With the research flavor
uvx copier copy -d is_research=true gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update
```

## Project structure

```
loam/
├── seed/                    # Copier subdirectory — everything rendered to projects
│   ├── .claude/             # Skills, agents, hooks, rules, settings
│   │   ├── skills/          # 21 core skills
│   │   ├── agents/          # Specialized subagents
│   │   ├── hooks/           # Pre-commit gate, post-edit tests, etc.
│   │   └── rules/           # Workflow, guardrails, known issues
│   ├── _research/           # Research flavor overlay (optional)
│   │   ├── skills/          # 18 research-specific skills
│   │   └── rules/           # Research consistency, memory rules
│   └── *.jinja              # Template files (CLAUDE.md, README.md, etc.)
├── cultivation/             # Skill lifecycle management
│   ├── marketplace/         # Cut skills — installable bundles
│   ├── retired/             # Dissolved skills (reference material)
│   └── wip/                 # Skills in development
├── soil/                    # Knowledge base (JVC, foundation, playbooks)
├── bin/                     # verify-template.sh, template-sync.sh, etc.
├── docs/                    # Template documentation
└── copier.yml               # Template config
```

## Skill inventory

### Core skills (shipped to every project)

| Skill | Purpose |
|-------|---------|
| `/feature-dev` | Feature development: explore → plan → implement → verify |
| `/fix-bug` | Bug fix: reproduce → diagnose → plan → fix → verify |
| `/validate` | Pipeline gate — 3-wave checks before commit |
| `/ship` | Full pipeline: critique → validate → commit → PR |
| `/commit` | Conventional commit with staging |
| `/pr` | Push and open GitHub PR |
| `/multi-review` | 4-reviewer parallel code review |
| `/session-critique` | Adversarial self-review before commit |
| `/catchup` | 30-second session bootstrap briefing |
| `/handoff` | Structured handoff for agent continuity |
| `/gen-spec` | Guided specification wizard |
| `/researcher` | Deep research with web search and synthesis |
| `/agent-team` | Coordinated multi-agent teams |
| `/critique-swarm` | 4-agent adversarial critique |
| `/auto-phase` | Autonomous multi-phase execution |
| `/dream` | Memory consolidation |
| `/techdebt` | Codebase tech debt scan |
| `/scaffold-context` | Author CONTEXT.md routing files |
| `/create-skill` | Create new skills |
| `/template-sync` | Sync assets with template buffer |
| `/render-gate` | TDD for Copier template files |

### Research-only skills (when `is_research=true`)

paper-write, cite-check, eval-run, experiment, hypothesis-tree, interpret-results, augment-test, auto-paper-improvement-loop, paper-review-sim, paper-claim-audit, rebuttal, citation-audit, overnight-eval, post-eval, cuda-omp-translator, hpc-code-reviewer, grill-research, eval-grader

## Documentation

- `docs/BOOTSTRAP.md` — First-session setup guide
- `docs/MEMORY.md` — Memory stack architecture
- `docs/COPIER.md` — Template configuration details
- `docs/FLAVORS.md` — Flavor system documentation
- `docs/SYNC.md` — Template sync workflow
- `docs/ASSET-LAYERS.md` — Asset organization

## Requirements

- [Copier](https://copier.readthedocs.io/) >= 9.4.0 (`pip install copier` or `uvx copier`)
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

## Contributing

Issues and pull requests are welcome.

## License

MIT — see [LICENSE](LICENSE).
