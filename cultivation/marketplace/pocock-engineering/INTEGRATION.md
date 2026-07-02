# Loam Integration Notes

How these skills interact with Loam's workflow. Read this once when installing the bundle — the individual SKILL.md files are upstream-faithful and don't reference Loam-specific tooling.

## Pipeline Gate

After any skill produces code changes, run `/validate` before committing:

```
/tdd cycles → all green → /validate → /commit
/diagnose fix → /validate → /commit
/prototype → adopt decision → implement → /validate → /commit
```

## Skill relationships

| Pocock skill | Loam counterpart | Relationship |
|---|---|---|
| `/tdd` | `superpowers:test-driven-development` | Coexist — Pocock emphasizes anti-horizontal-slice discipline; superpowers is more procedural |
| `/to-issues` | `/gen-spec` | Sequential — run `/gen-spec` first to produce the spec, then `/to-issues` to decompose into tickets |
| `/to-prd` | `/gen-spec` | Complementary — gen-spec is interactive; to-prd synthesizes from existing context without interviewing |
| `/grill-with-docs` | `/gen-spec` | Different purpose — grill challenges a plan against the domain model; gen-spec generates a spec from scratch |
| `/improve-codebase-architecture` | `/techdebt` | Complementary — techdebt is a broad sweep; improve-codebase-architecture is deep Ousterhout-style analysis |
| `/diagnose` | `superpowers:systematic-debugging` | Coexist — similar philosophy (reproduce first), Pocock is more structured (6 phases) |
| `/triage` | GitHub Issues | Triage reads `.claude/rules/known-issues.md` for prior context when evaluating bugs |

## DOMAIN.md convention

These skills use `DOMAIN.md` for the project's domain glossary (ubiquitous language). This is NOT the same as Loam's `CONTEXT.md` (L1 context-routing files). The two serve different purposes:

- `DOMAIN.md` — domain glossary: terms, definitions, relationships (managed by `/grill-with-docs`)
- `CONTEXT.md` — routing file: what to load, what to skip, process steps (managed by `/scaffold-context`)

Never write domain terms into `CONTEXT.md`. Never write routing logic into `DOMAIN.md`.
