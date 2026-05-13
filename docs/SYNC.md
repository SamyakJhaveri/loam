# Syncing assets between a project and the template

The buffer pattern: when you build a generally-useful agent/skill/hook/rule in a project, you can promote it back to the template, where future projects will pick it up at bootstrap time.

## The two flows

```
                    copier update (primary)
project/.claude/  ◀────────────────────  template (git tags)
                  ────────────────────▶
                    template-sync promote (manual, PR-based)
```

For shell-bootstrapped projects (no Copier), the downstream flow uses `pull` / `sync-from-buffer` instead:

```
                       promote (explicit)
   project/.claude/  ────────────────────▶  template/.claude/  or  flavors/<name>/
                     ◀────────────────────
                       pull / sync-from-buffer
```

## Hard rule

**Promotion is opt-in only.** No background hooks. No file watchers. No side-effects from other skills. The `template-sync` skill runs only when you explicitly invoke it.

Auto-deciding what deserves promotion is exactly how a buffer rots into a dump folder. We avoid that by making the human always sign off.

## How to promote

Inside Claude Code, in a project bootstrapped via Copier or `init-project.sh`:

```
template-sync promote <relpath>
```

The skill walks the 10-step flow:

1. Validates `template-manifest.json` or `.copier-answers.yml` exists.
2. Locates the template (`$TEMPLATE_PATH` → manifest → `~/Desktop/project_template`).
3. Verifies the template's working tree is clean.
4. Scans the asset for project-specific names, hardcoded paths, secrets, and legacy references.
5. Prompts you to confirm the target layer (`generic` / `flavor:<name>`).
6. Creates a branch `sync/<project>/<asset-slug>/<timestamp>` in the template repo.
7. Copies the asset.
8. Commits with a structured message.
9. Pushes the branch to GitHub.
10. Prints the `gh pr create` command.

The asset only lands in the template once you (or a reviewer) merge the PR.

## How to pull

```
template-sync pull <relpath>     # pull a single file
template-sync sync-from-buffer   # pull all template-side updates not in this project
```

`pull` overwrites local. If the local file differs, you're warned.
`sync-from-buffer` skips locally-modified files (reports them as conflicts) and lets you resolve manually.

## How to inspect

```
template-sync status       # classify each .claude/ file as unchanged / modified / local-only / template-only
template-sync diff <path>  # unified diff vs template
```

## What the skill checks (the safety net)

When promoting, the skill scans for:

- The project's own name from `template-manifest.json`
- Absolute paths under `/Users/...` or `/home/...`
- Secret-like strings (API keys, tokens, passwords, OAuth bearers)
- Legacy artefact names (ParBench, Rodinia, etc.)
- Machine-local toolchain paths

For each hit, it stops and asks: abort / generalise / promote anyway. You decide.

## What the skill MUST NOT do

- Promote as a side effect of any other skill (validate, fix-bug, etc.).
- Push to template `main` directly.
- Promote `.env`, `secrets/`, or matching files without explicit override.
- Run from a project without `template-manifest.json` or `.copier-answers.yml`.

## After a PR is merged into template main

For Copier-bootstrapped projects:

```bash
cd my-project
uvx copier update           # interactive, shows diffs for conflicts
uvx copier update --defaults # non-interactive, accepts defaults
```

For shell-bootstrapped projects:

```
template-sync sync-from-buffer
```
