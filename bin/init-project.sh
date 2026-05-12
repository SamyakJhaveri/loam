#!/usr/bin/env bash
# init-project.sh — bootstrap a new project from project-template.
#
# Usage:
#   bin/init-project.sh <project-path> [--flavor <name>]... [--github <owner/repo>] [--name <project-name>]
#
# The project is created with its own clean git history. No git remote is set
# unless --github is provided. The template is remembered via template-manifest.json
# at the project root (NOT via a git remote).

set -euo pipefail

# ----- Resolve template root from script location ---------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"

readonly VALID_FLAVORS=(research software-eng)
readonly TEMPLATE_REPO_DEFAULT="samyakjhaveri/project-template"

# ----- Helpers --------------------------------------------------------------
die() { printf 'init-project: %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m[init]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[ok]\033[0m   %s\n' "$*"; }

is_valid_flavor() {
  local f="$1"
  for v in "${VALID_FLAVORS[@]}"; do
    [[ "$v" == "$f" ]] && return 0
  done
  return 1
}

# Substitute {{PROJECT_NAME}}, {{DATE}}, {{YEAR}}, {{FLAVORS}} in a single file in place.
render_in_place() {
  local file="$1"
  python3 - "$file" "$PROJECT_NAME" "$DATE" "$YEAR" "$FLAVORS_CSV" <<'PY'
import sys, pathlib
path = pathlib.Path(sys.argv[1])
project_name, date, year, flavors_csv = sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
text = path.read_text()
text = (text
        .replace("{{PROJECT_NAME}}", project_name)
        .replace("{{DATE}}", date)
        .replace("{{YEAR}}", year)
        .replace("{{FLAVORS}}", flavors_csv))
path.write_text(text)
PY
}

# Render every *.tmpl in <src> into <dst-dir>, stripping the .tmpl suffix.
render_tmpl_dir_into() {
  local src="$1" dst="$2"
  [[ -d "$src" ]] || return 0
  while IFS= read -r -d '' tmpl; do
    local final_name
    final_name="$(basename "$tmpl" .tmpl)"
    cp "$tmpl" "$dst/$final_name"
    render_in_place "$dst/$final_name"
  done < <(find "$src" -maxdepth 1 -type f -name '*.tmpl' -print0)
}

# Copy non-.tmpl files from <src> directly into <dst-dir>.
copy_plain_files_into() {
  local src="$1" dst="$2"
  [[ -d "$src" ]] || return 0
  while IFS= read -r -d '' f; do
    cp "$f" "$dst/$(basename "$f")"
  done < <(find "$src" -maxdepth 1 -type f ! -name '*.tmpl' -print0)
}

# ----- Argument parsing -----------------------------------------------------
PROJECT_PATH=""
declare -a FLAVORS=()
GITHUB_REPO=""
PROJECT_NAME=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --flavor)
      [[ $# -ge 2 ]] || die "--flavor requires an argument"
      is_valid_flavor "$2" || die "unknown flavor '$2'. Valid: ${VALID_FLAVORS[*]}"
      FLAVORS+=("$2"); shift 2;;
    --github)
      [[ $# -ge 2 ]] || die "--github requires an argument (owner/repo)"
      GITHUB_REPO="$2"; shift 2;;
    --name)
      [[ $# -ge 2 ]] || die "--name requires an argument"
      PROJECT_NAME="$2"; shift 2;;
    -h|--help)
      sed -n '2,12p' "$0" | sed 's/^# *//'; exit 0;;
    -*)
      die "unknown flag: $1";;
    *)
      [[ -z "$PROJECT_PATH" ]] || die "extra positional arg: $1"
      PROJECT_PATH="$1"; shift;;
  esac
done

[[ -n "$PROJECT_PATH" ]] || die "missing <project-path>. Run with --help for usage."

PROJECT_PATH="$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "$PROJECT_PATH")"
[[ -n "$PROJECT_NAME" ]] || PROJECT_NAME="$(basename "$PROJECT_PATH")"

# ----- Pre-flight checks ----------------------------------------------------
if [[ -e "$PROJECT_PATH" ]]; then
  if [[ -d "$PROJECT_PATH" ]]; then
    if [[ -n "$(ls -A "$PROJECT_PATH" 2>/dev/null || true)" ]]; then
      die "project path '$PROJECT_PATH' exists and is non-empty"
    fi
  else
    die "project path '$PROJECT_PATH' exists and is not a directory"
  fi
fi

[[ -d "$TEMPLATE_ROOT/.claude" ]] || die "template root '$TEMPLATE_ROOT' has no .claude/ — wrong location?"

command -v git >/dev/null || die "git not found on PATH"
command -v python3 >/dev/null || die "python3 not found on PATH"

TEMPLATE_SHA="$(git -C "$TEMPLATE_ROOT" rev-parse --short HEAD 2>/dev/null || echo "unknown")"
DATE="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
YEAR="$(date -u +"%Y")"
# ${FLAVORS[@]} with nounset safe for bash 3.2 (macOS default)
# Same fix applied on the for-loop at line ~170: ${FLAVORS[@]+"${FLAVORS[@]}"}
if [[ ${#FLAVORS[@]} -eq 0 ]]; then FLAVORS_CSV=""; else FLAVORS_CSV="$(IFS=,; echo "${FLAVORS[*]}")"; fi

info "template:      $TEMPLATE_ROOT @ $TEMPLATE_SHA"
info "project path:  $PROJECT_PATH"
info "project name:  $PROJECT_NAME"
info "flavors:       ${FLAVORS_CSV:-<none>}"

# ----- Build the project ----------------------------------------------------
mkdir -p "$PROJECT_PATH"

# 1. Generic .claude/ core
info "copying generic core (.claude/)"
mkdir -p "$PROJECT_PATH/.claude"
cp -R "$TEMPLATE_ROOT/.claude/." "$PROJECT_PATH/.claude/"
rm -rf "$PROJECT_PATH/.claude/worktrees" 2>/dev/null || true
# Remove transient/machine-local files that shouldn't propagate
rm -f "$PROJECT_PATH/.claude/.local-paths" \
      "$PROJECT_PATH/.claude/.venv-name" \
      "$PROJECT_PATH/.claude/.DS_Store" \
      "$PROJECT_PATH/.claude/audit.log" \
      "$PROJECT_PATH/.claude/settings.json.bak-codex-hook" \
      "$PROJECT_PATH/.claude/settings.local.json" \
      2>/dev/null || true

# 2. seed-folders (empty dirs with .gitkeep)
if [[ -d "$TEMPLATE_ROOT/seed-folders" ]]; then
  info "materialising seed-folders/"
  while IFS= read -r -d '' subdir; do
    rel="${subdir#"$TEMPLATE_ROOT/seed-folders/"}"
    mkdir -p "$PROJECT_PATH/$rel"
    [[ -f "$PROJECT_PATH/$rel/.gitkeep" ]] || touch "$PROJECT_PATH/$rel/.gitkeep"
  done < <(find "$TEMPLATE_ROOT/seed-folders" -mindepth 1 -type d -print0)
fi

# 3. seed-docs (rendered into project root)
info "rendering seed-docs/"
render_tmpl_dir_into "$TEMPLATE_ROOT/seed-docs" "$PROJECT_PATH"
copy_plain_files_into "$TEMPLATE_ROOT/seed-docs" "$PROJECT_PATH"

# 4. seed-config (rendered into project root)
info "rendering seed-config/"
render_tmpl_dir_into "$TEMPLATE_ROOT/seed-config" "$PROJECT_PATH"
copy_plain_files_into "$TEMPLATE_ROOT/seed-config" "$PROJECT_PATH"

# 5. Flavors (overlay each in order)
for flavor in ${FLAVORS[@]+"${FLAVORS[@]}"}; do
  flavor_root="$TEMPLATE_ROOT/flavors/$flavor"
  [[ -d "$flavor_root" ]] || die "flavor '$flavor' has no folder at $flavor_root"
  info "applying flavor: $flavor"
  for sub in agents skills hooks rules; do
    if [[ -d "$flavor_root/$sub" ]]; then
      mkdir -p "$PROJECT_PATH/.claude/$sub"
      cp -R "$flavor_root/$sub/." "$PROJECT_PATH/.claude/$sub/"
    fi
  done
  render_tmpl_dir_into "$flavor_root/seed-docs" "$PROJECT_PATH"
  copy_plain_files_into "$flavor_root/seed-docs" "$PROJECT_PATH"
done

# 6. Write template-manifest.json (template repo is hard-coded; --github is for the PROJECT's own remote)
info "writing template-manifest.json"
python3 - "$PROJECT_PATH/template-manifest.json" \
  "$TEMPLATE_REPO_DEFAULT" "$TEMPLATE_SHA" "$TEMPLATE_ROOT" \
  "$PROJECT_NAME" "$DATE" "$FLAVORS_CSV" <<'PY'
import json, sys
out_path, repo, sha, tpath, name, date, flavors_csv = sys.argv[1:8]
flavors = [f for f in flavors_csv.split(",") if f]
manifest = {
    "schema_version": 1,
    "template": {"repo": repo, "commit": sha, "path": tpath},
    "flavors": flavors,
    "project_name": name,
    "created_at": date,
    "asset_overrides": {},
}
with open(out_path, "w") as f:
    json.dump(manifest, f, indent=2)
    f.write("\n")
PY

# 7. git init + first commit
info "initializing git repo"
git -C "$PROJECT_PATH" init -q -b main 2>/dev/null || git -C "$PROJECT_PATH" init -q
git -C "$PROJECT_PATH" add .
GIT_AUTHOR_NAME="${GIT_AUTHOR_NAME:-$PROJECT_NAME}" \
GIT_AUTHOR_EMAIL="${GIT_AUTHOR_EMAIL:-$PROJECT_NAME@local}" \
GIT_COMMITTER_NAME="${GIT_COMMITTER_NAME:-$PROJECT_NAME}" \
GIT_COMMITTER_EMAIL="${GIT_COMMITTER_EMAIL:-$PROJECT_NAME@local}" \
  git -C "$PROJECT_PATH" -c commit.gpgsign=false commit -q \
    -m "Initial commit from project-template @ $TEMPLATE_SHA${FLAVORS_CSV:+ (flavors: $FLAVORS_CSV)}"

# 8. Optional GitHub remote for the new PROJECT (separate from the template repo)
if [[ -n "$GITHUB_REPO" ]]; then
  if command -v gh >/dev/null; then
    info "creating GitHub repo $GITHUB_REPO and setting it as origin"
    if (cd "$PROJECT_PATH" && gh repo create "$GITHUB_REPO" --private --source=. --remote=origin --push); then
      ok "remote origin set to $GITHUB_REPO"
    else
      warn "gh repo create failed; project is initialized locally without remote"
    fi
  else
    warn "gh CLI not found; skipping GitHub repo creation. Add origin manually."
  fi
fi

# 9. Banner
ok "project created at $PROJECT_PATH"
cat <<EOF

Next steps:
  cd $PROJECT_PATH
$(if [[ -z "$GITHUB_REPO" ]]; then
  printf '  # Create a GitHub repo for THIS project, then:\n'
  printf '  git remote add origin git@github.com:<owner>/%s.git\n' "$PROJECT_NAME"
  printf '  git push -u origin main\n'
fi)

The template is remembered via template-manifest.json — there is NO git remote
pointing at project-template. To promote a project asset back to the template,
invoke the template-sync skill from inside Claude Code:
  template-sync promote <asset-path>

EOF
