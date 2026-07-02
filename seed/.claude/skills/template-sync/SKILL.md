---
name: template-sync
description: Sync Claude Code assets between this project and the project-template buffer. Use when promoting a generally-useful agent/skill/hook/rule from this project back to the template, when pulling a template-side update down into this project, or when checking what has diverged. Subcommands - status, diff, pull, promote, trial, sync-from-buffer. Refuses to operate without template-manifest.json. Promotion is always opt-in - never automatic.
auto-activate: false
---

# template-sync

**Purpose.** This skill is the cognition layer over `bin/template-sync.sh`. The script does mechanical file moves and git operations; this skill judges *whether* and *where* an asset belongs in the template, and asks you to confirm before mutating anything.

**Hard rule:** This skill runs only when you explicitly invoke it. There is no auto-promotion. No background hooks. No file watchers. The buffer-rotting failure mode is exactly what this skill exists to prevent.

## When to invoke

- "Promote this skill back to the template" — `template-sync promote`
- "What's different from the template?" — `template-sync status`
- "Pull the latest version of skill X from the template" — `template-sync pull`
- "Bring this project up to date with template main" — `template-sync sync-from-buffer`
- "Install this skill into my project" — `template-sync trial`
- "Try that skill from cultivation" — `template-sync trial /path/to/skill`
- "Grab the catchup skill from loam" — `template-sync trial catchup`

## Pre-flight (always)

1. Verify `template-manifest.json` exists at the project root. If missing, stop and tell the user this project wasn't bootstrapped via `init-project.sh` and the skill cannot operate.
2. Resolve the template clone location: prefer `$TEMPLATE_PATH`, then `template.path` from manifest, then `~/Desktop/project_template`. Confirm the directory exists.
3. Read `template-manifest.json` to know the project name and applied flavors — these inform layer suggestions.

## Subcommands

### `status`

Run `bin/template-sync.sh status` and present the table to the user. Group results by status (modified / local-only / template-only / unchanged). Don't dump unchanged unless asked.

### `diff <relpath>`

Run `bin/template-sync.sh diff <relpath>` and show the result. If the diff is large (>100 lines), summarise + offer to show in chunks.

### `pull <relpath>`

Before running:
- Run `diff` first.
- Confirm with the user: "About to overwrite local `<relpath>` with template version. Proceed?"

Then run `bin/template-sync.sh pull <relpath>`.

Supports both files and directories. For pulling an entire skill: `template-sync pull .claude/skills/<name>`.

### `promote <relpath>`  ← the key flow

This is the 10-step flow. **Never skip the questions.**

1. **Confirm intent.** "You want to promote `<relpath>` from this project to the template. Yes?"

2. **Read the file.** Use the Read tool to load the asset.

3. **Generality scan.** Look for and quote any of:
   - Project-specific names (the value of `project_name` in manifest, or any `~/Desktop/<other-project>/` path)
   - Hardcoded absolute paths under `/Users/...` or `/home/...` outside generic placeholders
   - Likely secrets: tokens, API keys, OAuth tokens, .env file contents (regex-style scan: `(?i)(api[_-]?key|secret|token|password|bearer)\s*[:=]\s*['"]?[A-Za-z0-9_\-]{16,}`)
   - References to a prior project's benchmarks, papers, or venues (e.g. Rodinia, HeCBench, XSBench, RSBench, mixbench, NeurIPS, SC26)
   - Machine-local assumptions: `/opt/nvidia/...`, `/home/samyak/...`, GPU model strings

   For each hit, quote the exact line and ask the user: "Found `<line>`. Should I (a) abort, (b) generalize this to a placeholder, or (c) promote anyway?"

4. **Suggest target layer.** Based on what the asset references, propose one of:
   - `generic` — domain-neutral, every project benefits
   - `flavor:research` — research projects (paper-writing, ML experiments, HPC/parallel work)
   - `flavor:software-eng` — building software products

   Explain the reasoning ("This skill mentions LaTeX and bibtex → suggests `flavor:research`"). Ask user to confirm or override.

5. **Confirm template repo is clean.** If `git -C <tpl> status --porcelain` shows uncommitted changes, refuse to proceed and tell the user to clean up the template repo first.

6. **Run the script.** `bin/template-sync.sh promote --layer <chosen-layer> <relpath>`. The script handles branch creation, commit, push, and printing the PR command.

7. **Hard rule never violated:** no commits or pushes to `main`. The script enforces this; you reinforce it in confirmation messages.

8. **After the script returns**, show the user:
   - The branch name created.
   - The PR command (verbatim).
   - A reminder that the asset will only land in the template once the PR is merged.

### `sync-from-buffer`

Run `bin/template-sync.sh sync-from-buffer`. For any reported "conflict (skipped)" lines, suggest the user run `template-sync diff <path>` to inspect, then `template-sync pull <path>` if they want to take the template version.

### `trial [--name NAME] [--force] <source-or-skill-name>`

Install a skill from any source into this project's `.claude/skills/`.

1. **Validate source.** If the argument contains no slashes, resolve it as a skill name from the template's `seed/.claude/skills/`. Otherwise treat as a literal path.

2. **Check source is valid.** The source must be a directory containing `SKILL.md`. If not, stop with an error.

3. **Check destination.** If `.claude/skills/<name>/` already exists and `--force` was not passed, refuse. Tell the user to use `--force`.

4. **Copy.** Run the script: `bin/template-sync.sh trial [--name NAME] [--force] <source>`.

5. **Confirm.** Show the user what was installed and how to remove it.

**Note on cultivation/ bundles:** Skills in `cultivation/marketplace/` are nested: `<bundle>/skills/<skill-name>/`. Point `trial` at the individual skill directory, not the bundle root. Example: `template-sync trial /path/to/loam/cultivation/marketplace/pocock-engineering/skills/tdd`

## Output style

- Brief. The user is making decisions; show them the relevant diffs and questions, not your reasoning.
- When in doubt, ask. Promoting the wrong asset to the wrong layer is the failure mode this skill prevents.
- Never promote silently. Every promotion produces a printed branch name + PR command in the chat.

## What this skill MUST NOT do

- Do not invoke promote as a side effect of any other skill (validate, fix-bug, feature-dev, session-critique, etc.).
- Do not register a post-commit / post-edit hook that triggers promote.
- Do not promote without the generality scan in step 3.
- Do not push to the template's `main` directly. Always via a `sync/...` branch + PR.
- Do not promote `.env`, `secrets/`, or any file matching the secret regex without an explicit user override.
- Do not modify or add provenance metadata files (.source.json or similar). Provenance is tracked via git commit messages only.
