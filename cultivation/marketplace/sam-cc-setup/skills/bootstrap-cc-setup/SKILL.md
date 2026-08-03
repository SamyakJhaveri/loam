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
It contains the model-notes section only - the Fable 5 / Opus 5 guides invert on
subagent use and self-verification, and following the wrong one is costly both ways.
**No anti-pattern list is written**: a 2026-08-02 audit cut twelve anti-patterns to
three, and all three survivors were incidents local to the source repo. A new repo
starts with zero and earns its own.

### 4. Prove the gate works here

Run the shipped detector test suite from the plugin, in this repo:

```bash
rm -f "$ROOT/.validation_passed"   # suite refuses to run if a sentinel exists
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/test_pre_commit_gate.py"
```

Every case must pass (the suite prints `N/N passed` and exits 0). If it fails,
report the failing cases and stop - do not leave a half-proven gate.

### 5. (Optional, on request) Vendor the hooks into the repo

Default is NOT to do this: the plugin's own hooks already gate commits wherever the
plugin is enabled. Vendor only if the user wants enforcement that travels with the
repo via git to collaborators who do not have the plugin:

```bash
mkdir -p "$ROOT/.claude/hooks"
cp "${CLAUDE_PLUGIN_ROOT}"/hooks/{pre-commit-gate.sh,gate_detect.py,test_pre_commit_gate.py,sentinel-cleanup.sh,concurrent-checkout-guard.sh} "$ROOT/.claude/hooks/"
```

Then add the three hook entries to `$ROOT/.claude/settings.json` (PreToolUse Bash →
pre-commit-gate.sh; PreToolUse Bash|Edit|Write → concurrent-checkout-guard.sh;
PostToolUse Edit|Write → sentinel-cleanup.sh), using
`$CLAUDE_PROJECT_DIR/.claude/hooks/...` paths. Warn that with both plugin and vendored
hooks enabled the gate fires twice (harmless - same verdict - but noisy).

### 6. Report

Print exactly what was written, what was skipped and why, the test result, and:

```
Undo: rm CLAUDE.md .claude/rules/workflow.md   # plus .claude/hooks/* if vendored
```

Also remind: add `.validation_passed` to `.gitignore`.
