#!/usr/bin/env bash
# agent-sync prune - list hub files whose project source is gone and offer deletion.
#
# The additive scan never deletes, so a file retired in the project lingers in the
# hub forever. This mode closes that gap, interactively and manifest-guarded:
#   - Only paths listed in the project's portability-manifest.tsv AND carrying a
#     'travels' verdict are candidates (L1: matching the scan fold-in's gate).
#     Hub-only curated files (README, bootstrap templates, generalized forks) and
#     any stays/rework/unclassified row are never offered.
#   - A candidate is offered only when its project source no longer exists.
#   - Each offer is y/N (default N); deletion uses git rm inside the hub so the
#     removal is staged.
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

offered=0 deleted=0 withheld=0
# The manifest is read on fd 3, NOT stdin: the y/N answer is read from stdin below
# (option b), so the outer loop must not hold stdin open on the manifest file.
# shellcheck disable=SC2034  # kind/requires are read to keep the TSV columns aligned; only verdict/reason are printed
while IFS=$'\t' read -r path kind verdict reason requires <&3; do
  [ "$path" = "path" ] && continue      # header
  [ -z "$path" ] && continue
  hub_path="$HUB_PLUGIN/$path"
  src_path="$PROJECT_ROOT/.claude/$path"
  [ -e "$hub_path" ] || continue        # nothing in hub to prune
  [ -e "$src_path" ] && continue        # project source still exists
  # L1: gate on the manifest verdict exactly as the scan fold-in does
  # (consider_prune's travels-only check). A stays/rework/unclassified row is a
  # curated hub-only generalization, or one kept on purpose; never offer it.
  if [ "$verdict" != travels ]; then
    withheld=$((withheld+1))
    echo "  prune withheld (manifest verdict '${verdict:-unclassified}', not travels): $path" >&2
    continue
  fi
  offered=$((offered+1))
  echo ""
  echo "Hub file with no project source: sam-cc-setup/$path"
  echo "  manifest verdict: $verdict ($reason)"
  # L1: a directory row's `git rm -r` would delete hub-only curated files inside it
  # that this prompt never named. Enumerate every tracked hub file under the
  # directory so the y/N covers exactly what will be removed.
  if [ -d "$hub_path" ]; then
    echo "  NOTE: this is a DIRECTORY; git rm -r would delete ALL of these tracked hub files:"
    while IFS= read -r f; do
      echo "    - ${f#cultivation/marketplace/sam-cc-setup/}"
    done < <(git -C "$HUB_REPO" ls-files -- ":(literal)cultivation/marketplace/sam-cc-setup/$path")
  fi
  printf "  Delete from hub? [y/N] "
  # (b, advisor ruling 2026-08-25): read the answer from stdin like
  # agent-sync-scan.sh's prompts do, so this standalone tool is testable (L5). At a
  # terminal stdin IS the tty, so a human is still prompted and answers normally.
  # The safety delta: a NON-tty stdin (a pipe/redirect) now answers deletion prompts
  # instead of the terminal. Acceptable because it matches scan.sh's posture, the
  # travels-only gate + the directory listing above + the default-N below bound what
  # can ever be deleted, and EOF still means "kept".
  read -r ans || ans=""
  case "$ans" in
    [yY]|[yY][eE][sS])
      # H1 / L1: :(literal) so a glob metachar in a manifest path (a[1].md) cannot
      # wildmatch and delete an unrelated hub file the y/N prompt never named.
      git -C "$HUB_REPO" rm -r --quiet -- ":(literal)cultivation/marketplace/sam-cc-setup/$path"
      deleted=$((deleted+1))
      echo "  deleted (staged in hub; commit in $HUB_REPO)"
      ;;
    *) echo "  kept" ;;
  esac
done 3< "$MANIFEST_TSV"

echo ""
echo "prune: $offered orphan(s) offered, $deleted deleted, $withheld withheld (verdict not travels)."
[ "$deleted" -gt 0 ] && echo "Commit the hub: git -C $HUB_REPO commit -m 'prune: remove retired project sources'"
exit 0
