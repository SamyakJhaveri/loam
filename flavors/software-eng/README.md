# Flavor: software-eng

Adds scaffolding for building software products: design records, architecture documentation.

## Adds to `.claude/`

### Rules
- `rules/python.md`          — Python style, testing, naming (loads on `*.py`)
- `rules/tech-stack.md`      — Python 3.12+, pip, pyproject.toml (loads on Python/build files)
- `rules/architecture.md`    — Layered architecture template (loads on `src/**`, `lib/**`, `scripts/**`)
- `rules/frontend-design.md` — Frontend/UI design standards (loads on `frontend/**`, `*.html`, `*.css`, `*.js`)

## Seeds at project root

- `DESIGN.md`       — top-level design choices and decision records
- `ARCHITECTURE.md` — static structure: components, boundaries, data flow

## When to pick

- Building a SaaS product, internal tool, library, or service.
- Greenfield software work where design records and architecture docs matter.

## When NOT to pick

- Pure research with no product surface — pick `research` instead.
- Paper-only work — pick `paper-writing` instead.

## Stacks well with

- `ml` (ML-powered product feature)
