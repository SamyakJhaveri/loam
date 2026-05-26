# Unified Skill Movement via template-sync — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `template-sync` the single tool for moving skills between projects, adding a `trial` subcommand and upgrading `pull`/`promote` to handle skill directories (not just single files).

**Architecture:** Extend the existing `bin/template-sync.sh` (294 lines) with three changes: (1) new `trial` subcommand (~20 lines) that copies any skill directory into a project with smart path resolution, (2) upgrade `pull` to handle directories, (3) upgrade `promote` to handle directories. Then update the template-sync SKILL.md (the cognitive wrapper) to document the new capabilities. No new files, no JSON provenance, no doc rewrites — mechanism only.

**Tech Stack:** Bash (shell script), Markdown (SKILL.md update)

---

## Context for Fresh Session

**What is this repo?** `/Users/samyakjhaveri/Desktop/loam` is a Copier template that bootstraps new projects with Claude Code infrastructure (skills, rules, hooks, folder structure). The `.claude/` symlink points to `seed/.claude/`.

**What is template-sync?** A tool (shell script + Claude Code skill) for syncing assets between projects and this template. The shell script (`bin/template-sync.sh`) does mechanical file operations; the skill (`seed/.claude/skills/template-sync/SKILL.md`) adds judgment (generality scanning, confirmation prompts).

**What's the problem?** Users seed projects from Loam, develop/discover useful skills, and want to move them between projects. Current friction:
- `pull` and `promote` are file-level only — skills are directories
- No way to install a skill from an arbitrary source (another project, open source repo, loam's cultivation/ staging area)
- The only option is manual `cp -r` with no guidance

**What's the solution?** One new subcommand (`trial`) + directory support for existing subcommands. Total: ~50 lines of shell.

**Key design decisions (already made):**
- `trial` with a bare name (no slashes) resolves from the template's `seed/.claude/skills/`
- `trial` with a path uses that path directly
- No `.source.json` provenance file — git commit messages are the audit trail
- No documentation rewrites in this session — mechanism first, docs later after dogfooding
- Skills in `cultivation/marketplace/` have a nested structure: `<bundle>/skills/<skill-name>/SKILL.md`. The unit of installation is the individual skill directory, not the bundle.

**File map:**

| File | Action | Lines affected |
|------|--------|----------------|
| `bin/template-sync.sh` | Modify | Add `cmd_trial` (~20 lines), modify `cmd_pull` (lines 134-148), modify `cmd_promote` (lines 151-243), update dispatch (line 283) |
| `seed/.claude/skills/template-sync/SKILL.md` | Modify | Add `trial` subcommand section, update `pull` section, minor framing updates |

---

## Stage Contract

**Inputs:**
- `bin/template-sync.sh` (existing, 294 lines)
- `seed/.claude/skills/template-sync/SKILL.md` (existing, 96 lines)

**Process:**
1. Add `cmd_trial` to shell script
2. Upgrade `cmd_pull` for directory support
3. Upgrade `cmd_promote` for directory support
4. Update dispatch table
5. Update SKILL.md with `trial` documentation
6. Verify all three flows end-to-end

**Output:** Git commit with the two modified files.

**Must NOT include:**
- No `.source.json` or any new JSON provenance files
- No changes to `docs/SYNC.md`, `docs/ASSET-LAYERS.md`, or `CLAUDE.md`
- No renaming of `cultivation/marketplace/` directory
- No changes to `copier.yml` or bootstrap flow
- No `--bundle` mode (individual skills only)
- No git URL support (local paths only)
- No changes to `sync-from-buffer` or `update` subcommands

**Done looks like:** Running `bin/template-sync.sh trial /Users/samyakjhaveri/Desktop/loam/cultivation/marketplace/pocock-engineering/skills/tdd` from a project directory copies the `tdd/` skill into `.claude/skills/tdd/` with SKILL.md intact. Running `bin/template-sync.sh trial catchup` resolves from template and copies. Running `bin/template-sync.sh pull .claude/skills/catchup` copies the full directory. Running `bin/template-sync.sh promote --layer generic .claude/skills/my-skill` handles all files in the directory.

---

### Task 1: Add `cmd_trial` subcommand to shell script

**Files:**
- Modify: `bin/template-sync.sh` (insert after line 148, before `cmd_promote`)

- [ ] **Step 1: Add the `cmd_trial` function**

Insert this function after `cmd_pull` (after line 148) and before `cmd_promote` (line 151):

```bash
# ----- Subcommand: trial ----------------------------------------------------
cmd_trial() {
  local src="" name="" force=false
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --name)  [[ $# -ge 2 ]] || die "--name requires arg"; name="$2"; shift 2;;
      --force) force=true; shift;;
      -*)      die "unknown trial flag: $1";;
      *)       [[ -z "$src" ]] || die "extra positional: $1"; src="$1"; shift;;
    esac
  done
  [[ -n "$src" ]] || die "usage: template-sync.sh trial [--name NAME] [--force] <source-path-or-skill-name>"

  # Bare name (no slashes) → resolve from template's seed/.claude/skills/
  if [[ "$src" != */* ]]; then
    local tpl; tpl="$(resolve_template_path)"
    [[ -d "$tpl" ]] || die "template not found at $tpl"
    src="$tpl/seed/.claude/skills/$src"
  fi

  [[ -d "$src" ]] || die "source is not a directory: $src"
  [[ -f "$src/SKILL.md" ]] || die "no SKILL.md found in $src — not a valid skill directory"

  [[ -z "$name" ]] && name="$(basename "$src")"
  local dst=".claude/skills/$name"

  if [[ -d "$dst" ]]; then
    if [[ "$force" == true ]]; then
      warn "overwriting existing skill at $dst"
      rm -rf "$dst"
    else
      die "skill already exists at $dst (use --force to overwrite)"
    fi
  fi

  [[ -d ".claude/skills" ]] || die "no .claude/skills/ directory found — is this a Claude Code project?"

  mkdir -p "$dst"
  cp -r "$src/." "$dst/"
  ok "installed skill '$name' from $src"
  info "to remove: rm -rf $dst"
}
```

- [ ] **Step 2: Add `trial` to the dispatch table**

In the dispatch section (around line 283), add the `trial` case:

```bash
case "$sub" in
  status)            cmd_status "$@";;
  diff)              cmd_diff "$@";;
  pull)              cmd_pull "$@";;
  promote)           cmd_promote "$@";;
  sync-from-buffer)  cmd_sync_from_buffer "$@";;
  update)            cmd_update "$@";;
  trial)             cmd_trial "$@";;
  ""|-h|--help)
    sed -n '2,16p' "$0" | sed 's/^# *//'
    exit 0;;
  *) die "unknown subcommand: $sub";;
esac
```

- [ ] **Step 3: Update the usage comment at the top of the script**

Add the trial usage line to the header comment (after line 11):

```bash
#   template-sync.sh trial [--name NAME] [--force] <source-or-name>   # install skill from any path
```

- [ ] **Step 4: Verify trial with a path**

```bash
cd /Users/samyakjhaveri/Desktop/loam
bin/template-sync.sh trial /Users/samyakjhaveri/Desktop/loam/cultivation/marketplace/pocock-engineering/skills/tdd
```

Expected: `[ok] installed skill 'tdd' from /Users/samyakjhaveri/Desktop/loam/cultivation/marketplace/pocock-engineering/skills/tdd`

Then verify: `ls .claude/skills/tdd/SKILL.md` should exist.

Clean up: `rm -rf .claude/skills/tdd`

- [ ] **Step 5: Verify trial with a bare name**

```bash
bin/template-sync.sh trial catchup
```

Expected: `template-sync: skill already exists at .claude/skills/catchup` (catchup is already in seed/.claude/skills/ via symlink).

- [ ] **Step 6: Verify trial refuses invalid source**

```bash
bin/template-sync.sh trial /tmp/nonexistent
```

Expected: `template-sync: source is not a directory: /tmp/nonexistent`

```bash
mkdir -p /tmp/fake-skill && bin/template-sync.sh trial /tmp/fake-skill; rm -rf /tmp/fake-skill
```

Expected: `template-sync: no SKILL.md found in /tmp/fake-skill — not a valid skill directory`

---

### Task 2: Upgrade `cmd_pull` for directory support

**Files:**
- Modify: `bin/template-sync.sh` (lines 134-148)

- [ ] **Step 1: Replace `cmd_pull` with directory-aware version**

Replace lines 134-148 with:

```bash
# ----- Subcommand: pull -----------------------------------------------------
cmd_pull() {
  local relpath="${1:-}"
  [[ -n "$relpath" ]] || die "usage: template-sync.sh pull <relpath>"
  require_manifest
  local tpl; tpl="$(resolve_template_path)"
  local tpl_root; tpl_root="$(resolve_template_claude_root "$tpl")"
  local src="$tpl_root/$relpath" dst="$PROJECT_DIR/$relpath"

  if [[ -d "$src" ]]; then
    if [[ -d "$dst" ]]; then
      warn "local directory $relpath exists; overwriting"
      rm -rf "$dst"
    fi
    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
    ok "pulled directory $relpath"
  elif [[ -f "$src" ]]; then
    if [[ -f "$dst" ]] && ! cmp -s "$src" "$dst"; then
      warn "local file $relpath differs from template; overwriting"
    fi
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    ok "pulled $relpath"
  else
    die "no such file or directory in template: $relpath"
  fi
}
```

- [ ] **Step 2: Verify directory pull works**

```bash
cd /Users/samyakjhaveri/Desktop/loam
TEMPLATE_PATH=/Users/samyakjhaveri/Desktop/loam bin/template-sync.sh pull .claude/skills/catchup 2>&1 | head -5
```

Expected: Pull output or overwrite warning (source and destination are the same via symlink). Key check: no "no such file" error.

---

### Task 3: Upgrade `cmd_promote` for directory support

**Files:**
- Modify: `bin/template-sync.sh` (lines 151-243)

- [ ] **Step 1: Modify `cmd_promote` to handle directories**

**Change 1:** Replace the file existence check (around line 169):

```bash
# OLD:
  [[ -f "$src" ]] || die "project file does not exist: $relpath"

# NEW:
  [[ -f "$src" || -d "$src" ]] || die "project path does not exist: $relpath"
```

**Change 2:** Replace the single-file copy+add section (around lines 196-197):

```bash
# OLD:
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  git -C "$tpl" add -- "$tpl_relpath"

# NEW:
  if [[ -d "$src" ]]; then
    mkdir -p "$dst"
    cp -r "$src/." "$dst/"
    git -C "$tpl" add -- "$tpl_relpath"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
    git -C "$tpl" add -- "$tpl_relpath"
  fi
```

- [ ] **Step 2: Verify no syntax errors**

```bash
bash -n bin/template-sync.sh
```

Expected: No output (clean parse).

- [ ] **Step 3: Verify --help still works**

```bash
bin/template-sync.sh --help
```

Expected: Shows usage text including the new trial line.

---

### Task 4: Update template-sync SKILL.md

**Files:**
- Modify: `seed/.claude/skills/template-sync/SKILL.md`

- [ ] **Step 1: Add `trial` to "When to invoke" section**

After the existing bullet list (around line 18), add:

```markdown
- "Install this skill into my project" — `template-sync trial`
- "Try that skill from cultivation" — `template-sync trial /path/to/skill`
- "Grab the catchup skill from loam" — `template-sync trial catchup`
```

- [ ] **Step 2: Add `trial` subcommand section**

Insert after the `### `sync-from-buffer`` section (after line 81), before "## Output style":

```markdown
### `trial [--name NAME] [--force] <source-or-skill-name>`

Install a skill from any source into this project's `.claude/skills/`.

1. **Validate source.** If the argument contains no slashes, resolve it as a skill name from the template's `seed/.claude/skills/`. Otherwise treat as a literal path.

2. **Check source is valid.** The source must be a directory containing `SKILL.md`. If not, stop with an error.

3. **Check destination.** If `.claude/skills/<name>/` already exists and `--force` was not passed, refuse. Tell the user to use `--force`.

4. **Copy.** Run the script: `bin/template-sync.sh trial [--name NAME] [--force] <source>`.

5. **Confirm.** Show the user what was installed and how to remove it.

**Note on cultivation/ bundles:** Skills in `cultivation/marketplace/` are nested: `<bundle>/skills/<skill-name>/`. Point `trial` at the individual skill directory, not the bundle root. Example: `template-sync trial /path/to/loam/cultivation/marketplace/pocock-engineering/skills/tdd`
```

- [ ] **Step 3: Update the `pull` section**

Add after "Then run `bin/template-sync.sh pull <relpath>`.":

```markdown

Supports both files and directories. For pulling an entire skill: `template-sync pull .claude/skills/<name>`.
```

- [ ] **Step 4: Add provenance rule to "What this skill MUST NOT do"**

Add one more bullet:

```markdown
- Do not modify or add provenance metadata files (.source.json or similar). Provenance is tracked via git commit messages only.
```

- [ ] **Step 5: Verify SKILL.md frontmatter is intact**

```bash
head -5 seed/.claude/skills/template-sync/SKILL.md
```

Confirm `---` delimiters are intact.

---

### Task 5: Final verification and commit

- [ ] **Step 1: Run the template verifier**

```bash
bin/verify-template.sh
```

Expected: `ALL OK`.

- [ ] **Step 2: Verify shell script parses cleanly**

```bash
bash -n bin/template-sync.sh
```

Expected: No output.

- [ ] **Step 3: Run a full trial flow end-to-end**

```bash
cd /Users/samyakjhaveri/Desktop/loam
bin/template-sync.sh trial /Users/samyakjhaveri/Desktop/loam/cultivation/marketplace/pocock-engineering/skills/tdd
ls .claude/skills/tdd/SKILL.md
rm -rf .claude/skills/tdd
```

- [ ] **Step 4: Run /validate (Pipeline Gate)**

Use the `/validate` skill before committing. Required by `seed/.claude/rules/session-guardrails.md`.

- [ ] **Step 5: Commit**

```bash
git add bin/template-sync.sh seed/.claude/skills/template-sync/SKILL.md
git commit -m "feat(template-sync): add trial subcommand + directory support for pull/promote

Adds template-sync trial for installing skills from any source path.
Upgrades pull and promote to handle skill directories (not just files).
Bare name resolution: 'trial catchup' resolves from template's seed/.

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Summary

| What | Why | Lines |
|------|-----|-------|
| `cmd_trial` function | Install skills from any path with smart name resolution | ~35 |
| `cmd_pull` upgrade | Skills are directories, pull should handle them | ~10 net |
| `cmd_promote` upgrade | Symmetry — install a directory, promote a directory | ~5 net |
| SKILL.md `trial` docs | Cognitive wrapper for the new subcommand | ~25 |

Total: ~75 lines added/modified across 2 files. No new files created.

## Out of Scope (do NOT implement)

- No `.source.json` or provenance files
- No changes to `docs/SYNC.md`, `docs/ASSET-LAYERS.md`, or `CLAUDE.md`
- No renaming of `cultivation/marketplace/`
- No changes to `copier.yml` or bootstrap flow
- No `--bundle` mode
- No git URL support
- No changes to `sync-from-buffer` or `update` subcommands
