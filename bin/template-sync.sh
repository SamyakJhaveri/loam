#!/usr/bin/env bash
# template-sync.sh — plumbing for syncing assets between a project and project-template.
#
# This script does mechanical file movement and git operations only. Generality
# judgments and secret-scanning are the responsibility of the template-sync
# skill (the cognition layer); this script is the pipes.
#
# Usage:
#   template-sync.sh status                                          # classify diffs
#   template-sync.sh diff <relpath>                                  # show file-level diff
#   template-sync.sh pull <relpath>                                  # copy from template into project
#   template-sync.sh promote --layer <generic|flavor:NAME> <relpath> # promote project -> template branch
#   template-sync.sh sync-from-buffer                                # bulk pull updates from template main
#
# Environment:
#   TEMPLATE_PATH    overrides the template clone location
#                    (default: ~/Desktop/project_template, or value from manifest)

set -euo pipefail

PROJECT_DIR="$PWD"
MANIFEST="$PROJECT_DIR/template-manifest.json"

die()  { printf 'template-sync: %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m[sync]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[ok]\033[0m   %s\n' "$*"; }

require_manifest() {
  [[ -f "$MANIFEST" ]] || die "no template-manifest.json at $MANIFEST. Are you in a project bootstrapped via init-project.sh?"
}

resolve_template_path() {
  if [[ -n "${TEMPLATE_PATH:-}" ]]; then
    echo "$TEMPLATE_PATH"; return
  fi
  if [[ -f "$MANIFEST" ]]; then
    local p
    p=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("template",{}).get("path",""))' "$MANIFEST")
    [[ -n "$p" && -d "$p" ]] && { echo "$p"; return; }
  fi
  echo "$HOME/Desktop/project_template"
}

project_name() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("project_name","unknown"))' "$MANIFEST"
}

# Map (layer, relpath-relative-to-project-root) → template-relpath.
# Project relpath is e.g. ".claude/skills/handoff/SKILL.md".
template_path_for() {
  local layer="$1" relpath="$2"
  case "$layer" in
    generic)
      [[ "$relpath" == .claude/* ]] || die "generic layer expects path under .claude/, got: $relpath"
      echo "$relpath";;
    flavor:*)
      local flavor="${layer#flavor:}"
      local stripped="${relpath#.claude/}"
      echo "flavors/$flavor/$stripped";;
    *) die "unknown layer: $layer";;
  esac
}

# ----- Subcommand: status ---------------------------------------------------
cmd_status() {
  require_manifest
  local tpl; tpl="$(resolve_template_path)"
  [[ -d "$tpl" ]] || die "template not found at $tpl"

  printf 'Comparing %s/.claude  ↔  %s/.claude\n\n' "$PROJECT_DIR" "$tpl"
  printf '%-12s  %s\n' "STATUS" "PATH"
  printf '%-12s  %s\n' "------" "----"

  # Files in project's .claude/
  while IFS= read -r -d '' f; do
    rel=".claude/${f#"$PROJECT_DIR/.claude/"}"
    tpl_path="$tpl/$rel"
    if [[ -f "$tpl_path" ]]; then
      if cmp -s "$f" "$tpl_path"; then
        printf '%-12s  %s\n' "unchanged" "$rel"
      else
        printf '%-12s  %s\n' "modified" "$rel"
      fi
    else
      printf '%-12s  %s\n' "local-only" "$rel"
    fi
  done < <(find "$PROJECT_DIR/.claude" -type f -print0 2>/dev/null)

  # Files in template's .claude/ not in project
  while IFS= read -r -d '' f; do
    rel=".claude/${f#"$tpl/.claude/"}"
    [[ -f "$PROJECT_DIR/$rel" ]] || printf '%-12s  %s\n' "template-only" "$rel"
  done < <(find "$tpl/.claude" -type f -print0 2>/dev/null)
}

# ----- Subcommand: diff -----------------------------------------------------
cmd_diff() {
  local relpath="${1:-}"
  [[ -n "$relpath" ]] || die "usage: template-sync.sh diff <relpath>"
  require_manifest
  local tpl; tpl="$(resolve_template_path)"
  diff -u "$tpl/$relpath" "$PROJECT_DIR/$relpath" || true
}

# ----- Subcommand: pull -----------------------------------------------------
cmd_pull() {
  local relpath="${1:-}"
  [[ -n "$relpath" ]] || die "usage: template-sync.sh pull <relpath>"
  require_manifest
  local tpl; tpl="$(resolve_template_path)"
  local src="$tpl/$relpath" dst="$PROJECT_DIR/$relpath"
  [[ -f "$src" ]] || die "no such file in template: $relpath"
  if [[ -f "$dst" ]] && ! cmp -s "$src" "$dst"; then
    warn "local file $relpath differs from template; overwriting"
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  ok "pulled $relpath"
}

# ----- Subcommand: promote --------------------------------------------------
cmd_promote() {
  local layer="" relpath=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --layer) [[ $# -ge 2 ]] || die "--layer requires arg"
               layer="$2"; shift 2;;
      -*)      die "unknown promote flag: $1";;
      *)       [[ -z "$relpath" ]] || die "extra positional: $1"
               relpath="$1"; shift;;
    esac
  done
  [[ -n "$layer" ]] || die "promote requires --layer <generic|flavor:NAME>"
  [[ -n "$relpath" ]] || die "promote requires <relpath>"

  require_manifest
  local tpl; tpl="$(resolve_template_path)"
  [[ -d "$tpl" ]] || die "template not found at $tpl"

  local src="$PROJECT_DIR/$relpath"
  [[ -f "$src" ]] || die "project file does not exist: $relpath"

  local tpl_relpath
  tpl_relpath="$(template_path_for "$layer" "$relpath")"
  local dst="$tpl/$tpl_relpath"

  # Verify template clean before mutating it
  if [[ -n "$(git -C "$tpl" status --porcelain 2>/dev/null)" ]]; then
    die "template repo at $tpl has uncommitted changes; aborting"
  fi

  local pname; pname="$(project_name)"
  local asset_slug; asset_slug="$(printf '%s' "$relpath" | tr '/.' '--' | sed 's/--*/-/g; s/^-//; s/-$//')"
  local ts; ts="$(date -u +"%Y-%m-%d-%H%M")"
  local branch="sync/$pname/$asset_slug/$ts"

  info "template:  $tpl"
  info "src:       $relpath"
  info "dst:       $tpl_relpath  (layer=$layer)"
  info "branch:    $branch"

  # Branch + copy + commit
  git -C "$tpl" fetch origin main --quiet || warn "fetch origin failed (offline?); proceeding with local main"
  local base; base="$(git -C "$tpl" rev-parse --verify origin/main 2>/dev/null || git -C "$tpl" rev-parse --verify main)"
  git -C "$tpl" checkout -q -b "$branch" "$base"
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  git -C "$tpl" add -- "$tpl_relpath"
  if git -C "$tpl" diff --cached --quiet; then
    warn "no changes vs $base after copy; nothing to commit"
    git -C "$tpl" checkout -q main
    git -C "$tpl" branch -D "$branch" >/dev/null
    return 0
  fi
  GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-template-sync}" \
  GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-template-sync@local}" \
  GIT_COMMITTER_NAME="${GIT_COMMITTER_NAME:-template-sync}" \
  GIT_COMMITTER_EMAIL="${GIT_COMMITTER_EMAIL:-template-sync@local}" \
    git -C "$tpl" -c commit.gpgsign=false commit -q \
      -m "promote($layer): $tpl_relpath from $pname"

  # Push branch
  if git -C "$tpl" remote get-url origin >/dev/null 2>&1; then
    info "pushing branch to origin"
    if git -C "$tpl" push -u origin "$branch"; then
      ok "branch pushed"
    else
      warn "push failed; the branch is local in $tpl. Push manually when ready."
    fi
  else
    warn "no origin remote on template repo; branch is local-only at $tpl"
  fi

  # Restore main (don't leave the template on the sync branch)
  git -C "$tpl" checkout -q main

  # Print PR command
  local repo
  repo=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("template",{}).get("repo","<owner>/project-template"))' "$MANIFEST")
  cat <<EOF

Open PR:
  gh pr create \\
    --repo $repo \\
    --base main \\
    --head $branch \\
    --title "promote($layer): $(basename "$tpl_relpath") from $pname" \\
    --body  "Promotes $tpl_relpath from $pname."

EOF
}

# ----- Subcommand: sync-from-buffer ----------------------------------------
cmd_sync_from_buffer() {
  require_manifest
  local tpl; tpl="$(resolve_template_path)"
  [[ -d "$tpl" ]] || die "template not found at $tpl"
  info "fetching template main"
  (cd "$tpl" && git fetch origin main --quiet 2>/dev/null) || warn "fetch failed (offline?)"
  info "scanning for template-side updates not yet in this project"
  local updated=0
  while IFS= read -r -d '' f; do
    rel=".claude/${f#"$tpl/.claude/"}"
    if [[ ! -f "$PROJECT_DIR/$rel" ]]; then
      mkdir -p "$PROJECT_DIR/$(dirname "$rel")"
      cp "$f" "$PROJECT_DIR/$rel"
      printf '  pulled (new):       %s\n' "$rel"
      updated=$((updated+1))
    elif ! cmp -s "$f" "$PROJECT_DIR/$rel"; then
      printf '  conflict (skipped): %s — local differs; resolve manually with: template-sync diff %s\n' "$rel" "$rel"
    fi
  done < <(find "$tpl/.claude" -type f -print0 2>/dev/null)
  ok "sync-from-buffer complete; $updated file(s) pulled"
}

# ----- Dispatch -------------------------------------------------------------
sub="${1:-}"; shift || true
case "$sub" in
  status)            cmd_status "$@";;
  diff)              cmd_diff "$@";;
  pull)              cmd_pull "$@";;
  promote)           cmd_promote "$@";;
  sync-from-buffer)  cmd_sync_from_buffer "$@";;
  ""|-h|--help)
    sed -n '2,16p' "$0" | sed 's/^# *//'
    exit 0;;
  *) die "unknown subcommand: $sub";;
esac
