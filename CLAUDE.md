# CLAUDE.md — Loam

This repo IS a Copier template AND a Claude Code project. The `.claude/` symlink points to `seed/.claude/`, so the shipped harness activates here too.

**REBUILT 2026-08-29** (design: `docs/specs/rebuild-structure-design.md`). The reassess/rewrite epoch is over; no prefixed files remain.

User preferences:
- Challenge assumptions or offer corrections anytime
- Point out flaws in proposed questions or solutions
- Offer solutions to flaws

## How to use

```bash
# Bootstrap a new project (resolves the last release TAG, not main)
uvx copier copy --trust gh:samyakjhaveri/loam ./my-project

# Pull template updates into an existing project
cd my-project && uvx copier update --trust
```

## Layout

| Path | Purpose |
|------|---------|
| `seed/`                  | Copier `_subdirectory` — everything rendered to projects |
| `seed/.agents/skills/`   | Skills shared by both harnesses (Claude Code reads via symlink) |
| `seed/.codex/`           | Codex config + execution rules (trust-gated in projects) |
| `.claude → seed/.claude` | Symlink for local dev experience |
| `cultivation/marketplace/` | Plugin layer: sam-cc-setup (agents+skills), sam-superpowers, impeccable, bundles |
| `cultivation/wip/`       | Staging with no verdict yet (gitignored) |
| `bin/`                   | verify-template.sh, release.sh, ip-sweep set, lib.sh |
| `docs/`                  | Template documentation |
| `docs/specs/`            | Design specs + rebuild records |
| `copier.yml`             | Copier config: `_subdirectory: "seed"`, `_preserve_symlinks`, `_tasks` |
| `VERSION`                | Semver for releases |

## Gotchas (this repo)

- Copier resolves git TAGS, not HEAD. Never tag until `bin/verify-template.sh` passes; use `bin/release.sh <version>`, which gates on it.
- `claude plugin validate` refuses a symlinked `.claude` and does not follow symlinks — always name the REAL dirs (`seed/.claude`, `seed/.agents/skills`), as verify-template does.
- Verification greps: case-insensitive and repo-wide (`grep -rni`), or they false-pass.
- Count skills by `find … -name SKILL.md`, not directory listings.
- Hook events/matchers are exact strings; a wrong name fails silently (a `PostToolUse`+`Compact` hook sat inert for months).
- `auto-activate` is not a real skill field; manual-only = `disable-model-invocation: true`.
- Quote YAML description strings containing colons.

## Rules when editing this template

- Don't add project-specific content; everything here is generic.
- **Hybrid branch policy:** direct-to-main for docs, content, and small fixes; branch + PR for `seed/` behavior changes, hooks, `copier.yml`, and releases.
- One directive, one home (see `docs/ASSET-LAYERS.md`). Skills for any project go in the sam-cc-setup plugin, not the seed, unless they must ship to every project.

## Reference docs (read on demand)

| File | Read when |
|------|-----------|
| `docs/ASSET-LAYERS.md` | Deciding where a new asset lives |
| `docs/SYNC.md` | Anything about distribution or promotion |
| `docs/BOOTSTRAP.md`, `docs/COPIER.md` | Bootstrap/update mechanics |
| `docs/specs/rebuild-structure-design.md` | Why the tree is shaped this way |
| `docs/specs/rebuild-research/` | The research grounding the rebuild (context rules, harness docs, reference agents) |
