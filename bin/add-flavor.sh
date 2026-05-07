#!/usr/bin/env bash
# add-flavor.sh — layer an additional flavor onto an existing project.
#
# Usage:
#   bin/add-flavor.sh <flavor> [--project <path>] [--force]
#
# Reads template-manifest.json from the project root (default: cwd). Refuses to
# overlay an asset that has been locally modified unless --force is passed.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_ROOT="$(dirname "$SCRIPT_DIR")"

readonly VALID_FLAVORS=(research software-eng ml hpc)

die()  { printf 'add-flavor: %s\n' "$*" >&2; exit 1; }
info() { printf '\033[36m[add-flavor]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[ok]\033[0m %s\n' "$*"; }

is_valid_flavor() {
  local f="$1"
  for v in "${VALID_FLAVORS[@]}"; do
    [[ "$v" == "$f" ]] && return 0
  done
  return 1
}

# ----- Argument parsing -----------------------------------------------------
FLAVOR=""
PROJECT_DIR="$PWD"
FORCE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) [[ $# -ge 2 ]] || die "--project requires an argument"
               PROJECT_DIR="$2"; shift 2;;
    --force)   FORCE=1; shift;;
    -h|--help) sed -n '2,9p' "$0" | sed 's/^# *//'; exit 0;;
    -*)        die "unknown flag: $1";;
    *)         [[ -z "$FLAVOR" ]] || die "extra positional arg: $1"
               FLAVOR="$1"; shift;;
  esac
done

[[ -n "$FLAVOR" ]] || die "missing <flavor>. Run with --help for usage."
is_valid_flavor "$FLAVOR" || die "unknown flavor '$FLAVOR'. Valid: ${VALID_FLAVORS[*]}"

PROJECT_DIR="$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "$PROJECT_DIR")"
MANIFEST="$PROJECT_DIR/template-manifest.json"
FLAVOR_ROOT="$TEMPLATE_ROOT/flavors/$FLAVOR"

[[ -f "$MANIFEST" ]] || die "no template-manifest.json at $MANIFEST — was this project bootstrapped via init-project.sh?"
[[ -d "$FLAVOR_ROOT" ]] || die "flavor folder not found: $FLAVOR_ROOT"

# Already applied?
if python3 -c "import json,sys; m=json.load(open(sys.argv[1])); sys.exit(0 if sys.argv[2] in m.get('flavors',[]) else 1)" "$MANIFEST" "$FLAVOR"; then
  warn "flavor '$FLAVOR' already applied per manifest"
  [[ "$FORCE" -eq 1 ]] || die "use --force to re-apply"
fi

# ----- Conflict scan: would we overwrite locally-modified files? -----------
declare -a OVERWRITES=()
while IFS= read -r -d '' src; do
  rel="${src#"$FLAVOR_ROOT/"}"
  case "$rel" in
    agents/*|skills/*|hooks/*|rules/*) dst="$PROJECT_DIR/.claude/$rel";;
    seed-docs/*) dst="$PROJECT_DIR/$(basename "$rel" .tmpl)";;
    *) continue;;
  esac
  if [[ -f "$dst" ]]; then
    if ! cmp -s "$src" "$dst" 2>/dev/null; then
      OVERWRITES+=("$rel")
    fi
  fi
done < <(find "$FLAVOR_ROOT" -type f -print0)

if [[ ${#OVERWRITES[@]} -gt 0 && "$FORCE" -ne 1 ]]; then
  warn "the following project files differ from this flavor's version:"
  for f in "${OVERWRITES[@]}"; do printf '  %s\n' "$f" >&2; done
  die "refusing to overwrite. Re-run with --force, or manually reconcile."
fi

# ----- Apply the overlay ---------------------------------------------------
info "applying flavor: $FLAVOR"
for sub in agents skills hooks rules; do
  if [[ -d "$FLAVOR_ROOT/$sub" ]]; then
    mkdir -p "$PROJECT_DIR/.claude/$sub"
    cp -R "$FLAVOR_ROOT/$sub/." "$PROJECT_DIR/.claude/$sub/"
  fi
done

# Render seed-docs (with placeholder substitution from manifest)
if [[ -d "$FLAVOR_ROOT/seed-docs" ]]; then
  PROJECT_NAME=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("project_name",""))' "$MANIFEST")
  DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  YEAR=$(date -u +"%Y")
  CURRENT_FLAVORS_CSV=$(python3 -c 'import json,sys; print(",".join(json.load(open(sys.argv[1])).get("flavors",[])+[sys.argv[2]]))' "$MANIFEST" "$FLAVOR")

  while IFS= read -r -d '' tmpl; do
    final="$PROJECT_DIR/$(basename "$tmpl" .tmpl)"
    cp "$tmpl" "$final"
    python3 - "$final" "$PROJECT_NAME" "$DATE" "$YEAR" "$CURRENT_FLAVORS_CSV" <<'PY'
import sys, pathlib
p = pathlib.Path(sys.argv[1])
n, d, y, fcsv = sys.argv[2:6]
t = p.read_text()
t = t.replace("{{PROJECT_NAME}}", n).replace("{{DATE}}", d).replace("{{YEAR}}", y).replace("{{FLAVORS}}", fcsv)
p.write_text(t)
PY
  done < <(find "$FLAVOR_ROOT/seed-docs" -maxdepth 1 -type f -name '*.tmpl' -print0)

  while IFS= read -r -d '' f; do
    cp "$f" "$PROJECT_DIR/$(basename "$f")"
  done < <(find "$FLAVOR_ROOT/seed-docs" -maxdepth 1 -type f ! -name '*.tmpl' -print0)
fi

# ----- Update manifest -----------------------------------------------------
python3 - "$MANIFEST" "$FLAVOR" <<'PY'
import json, sys
path, flavor = sys.argv[1], sys.argv[2]
with open(path) as f:
    m = json.load(f)
flavors = m.setdefault("flavors", [])
if flavor not in flavors:
    flavors.append(flavor)
with open(path, "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
PY

ok "flavor '$FLAVOR' applied; manifest updated"
