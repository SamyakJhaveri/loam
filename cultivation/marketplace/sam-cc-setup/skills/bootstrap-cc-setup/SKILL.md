---
name: bootstrap-cc-setup
description: "Write the always-loaded rules layer that a plugin cannot ship into the current repo: a CLAUDE.md skeleton (purpose + gotchas only) and a generic workflow.md rule (model notes only). Optionally vendors the pre-commit gate hooks into .claude/hooks/ for git-tracked, collaborator-visible enforcement. Run once per new repo after installing the sam-cc-setup plugin. NOT for repos rendered by the Loam Copier template (they already have this layer)."
---

# bootstrap-cc-setup

Plugins cannot inject always-loaded context (`CLAUDE.md`, `.claude/rules/*.md`).
This skill writes that layer. Everything else in sam-cc-setup (skills, agents, the
gate hooks) already works the moment the plugin is enabled - do not copy it.

## Invariants

1. **Never overwrite silently.** If a target file exists, show a diff of what would
   change and ask before touching it.
2. **Report everything written, with the undo command, at the end.**

## Steps

### 1. Detect what is already there

```bash
ROOT="$(git rev-parse --show-toplevel)" || { echo "Not a git repo - run git init first"; exit 1; }
ls -la "$ROOT/CLAUDE.md" "$ROOT/.claude/rules/workflow.md" 2>/dev/null
```

If the repo looks Loam-rendered (`.copier-answers.yml` present), stop and say so -
this skill would fight the template.

### 2. Write `CLAUDE.md` (skeleton)

Copy `templates/CLAUDE-skeleton.md` from this skill's directory to `$ROOT/CLAUDE.md`,
filling `{{PROJECT_NAME}}` from the directory name. The skeleton is purpose + gotchas
only - explicitly NOT a directory tour; the codebase is the README. Do not pad it.
If a CLAUDE.md exists, offer to append only the "Pipeline gate" section instead.

### 3. Write `.claude/rules/workflow.md` (model notes only)

Copy `templates/workflow-model-notes.md` to `$ROOT/.claude/rules/workflow.md`.
It contains the model-notes section only - the Fable 5.1 / Opus 4.8 guides differ on
instruction detail and subagent use, and following the wrong one is costly both ways.
**No anti-pattern list is written**: a 2026-08-02 audit cut twelve anti-patterns to
three, and all three survivors were incidents local to the source repo. A new repo
starts with zero and earns its own.

### 4. Install the native pre-commit hook

Commit enforcement here is a plain git pre-commit hook, not a sentinel or
PreToolUse gate: this repo was bootstrapped, not rendered from Loam, so the native
hook runs inside git, where no compound command can outrun it. A project rendered
from Loam uses the sentinel trio instead: `.validation_passed` is written by
`.claude/hooks/run-validate-waves.sh`, removed by `sentinel-cleanup.sh` on the
next edit, and required by `pre-commit-gate.sh` on `git commit`.

```bash
mkdir -p "$ROOT/scripts"
cp "${CLAUDE_PLUGIN_ROOT}/hooks/pre-commit.sh" "$ROOT/scripts/pre-commit.sh"
chmod +x "$ROOT/scripts/pre-commit.sh"
ln -sf ../../scripts/pre-commit.sh "$ROOT/.git/hooks/pre-commit"
```

Prove it works: make a scratch commit with a deliberate conflict marker in a staged
file and confirm the commit fails, then clean up. The hook is per-clone; tell the
user each new clone needs the `ln -sf` line once.

### 5. Report

Print exactly what was written, what was skipped and why, the hook-proof result, and:

```
Undo: rm CLAUDE.md .claude/rules/workflow.md scripts/pre-commit.sh .git/hooks/pre-commit
```
