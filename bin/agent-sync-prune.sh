#!/usr/bin/env bash
# agent-sync prune - list hub files whose project source is gone and offer deletion.
#
# The additive scan never deletes, so a file retired in the project lingers in the
# hub forever. This mode closes that gap, interactively and manifest-guarded:
#   - Only paths listed in the project's portability-manifest.tsv are candidates.
#     Hub-only curated files (README, bootstrap templates, generalized forks) are
#     absent from the manifest and are never offered.
#   - A candidate is offered only when its project source no longer exists.
#   - Each offer is y/N; deletion uses git rm inside the hub so the removal is staged.
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: run from inside the project's git repo." >&2
  exit 1
}
HUB_REPO="${SAM_CC_HUB_REPO:-$HOME/Desktop/loam}"
HUB_PLUGIN="$HUB_REPO/cultivation/marketplace/sam-cc-setup"
MANIFEST_TSV="$PROJECT_ROOT/.claude/reference/portability-manifest.tsv"

[ -d "$HUB_REPO/.git" ] || { echo "Error: hub repo not found at $HUB_REPO." >&2; exit 1; }
[ -f "$MANIFEST_TSV" ] || { echo "Error: $MANIFEST_TSV missing - the manifest is the authority; refusing to prune without it." >&2; exit 1; }

offered=0 deleted=0
while IFS=$'\t' read -r path kind verdict reason requires; do
  [ "$path" = "path" ] && continue      # header
  [ -z "$path" ] && continue
  hub_path="$HUB_PLUGIN/$path"
  src_path="$PROJECT_ROOT/.claude/$path"
  [ -e "$hub_path" ] || continue        # nothing in hub to prune
  [ -e "$src_path" ] && continue        # project source still exists
  offered=$((offered+1))
  echo ""
  echo "Hub file with no project source: sam-cc-setup/$path"
  echo "  manifest verdict: $verdict ($reason)"
  printf "  Delete from hub? [y/N] "
  read -r ans </dev/tty || ans=""
  case "$ans" in
    [yY]|[yY][eE][sS])
      git -C "$HUB_REPO" rm -r --quiet "cultivation/marketplace/sam-cc-setup/$path"
      deleted=$((deleted+1))
      echo "  deleted (staged in hub; commit in $HUB_REPO)"
      ;;
    *) echo "  kept" ;;
  esac
done < "$MANIFEST_TSV"

echo ""
echo "prune: $offered orphan(s) found, $deleted deleted."
[ "$deleted" -gt 0 ] && echo "Commit the hub: git -C $HUB_REPO commit -m 'prune: remove retired project sources'"
exit 0
