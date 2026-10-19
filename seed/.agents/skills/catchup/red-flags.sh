#!/usr/bin/env bash
# red-flags.sh - catchup's fixed red-flag checks, one line per flag that fires.
#
# Usage: red-flags.sh   (run inside the repo)
#   Prints one `FLAG:` line per red flag, then a `Handoff:` line naming the
#   handoff note to read (or none) and a `Loam pin:` verdict line. Zero model
#   calls; exit 0 in a repo, 2 outside one.

set -uo pipefail

git rev-parse --git-dir >/dev/null 2>&1 || { echo "red-flags: not a git repository" >&2; exit 2; }
ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT" || exit 2

# Git state.
PORCELAIN="$(git status --porcelain 2>/dev/null)"
[ -n "$PORCELAIN" ] && echo "FLAG: uncommitted changes in $(printf '%s\n' "$PORCELAIN" | wc -l | tr -d ' ') paths"
git symbolic-ref -q HEAD >/dev/null || echo "FLAG: detached HEAD at $(git rev-parse --short HEAD 2>/dev/null)"
[ -e "$(git rev-parse --git-path MERGE_HEAD)" ] && echo "FLAG: merge in progress"
{ [ -d "$(git rev-parse --git-path rebase-merge)" ] || [ -d "$(git rev-parse --git-path rebase-apply)" ]; } \
  && echo "FLAG: rebase in progress"

# Active tmux sessions may be running long jobs.
SESSIONS="$(tmux list-sessions -F '#S' 2>/dev/null | tr '\n' ' ')"
[ -n "$SESSIONS" ] && echo "FLAG: tmux sessions active (may be running long jobs): ${SESSIONS% }"

# The handoff note (docs/WORKERS.md owns its path and format): the live note,
# else the newest one the SessionStart recall archived. The repo key is the one
# mem-recall uses: the origin remote's name, else the toplevel directory's.
URL="$(git remote get-url origin 2>/dev/null)"; URL="${URL%/}"; URL="${URL%.git}"
KEY="$(basename "${URL:-$ROOT}")"
MEM="$ROOT/.loam/memory"; [ -d "$MEM" ] || MEM="${LOAM_MEMSTORE:-$HOME/memstore}"
HANDOFF="$MEM/handoff/$KEY.md"
# shellcheck disable=SC2012 # archive names are <date>-<sid8>.md, no odd characters
[ -f "$HANDOFF" ] || HANDOFF="$(ls -t "$MEM/handoff/$KEY/archive/"*.md 2>/dev/null | head -1)"

# Staleness: status words that contradict git, or a "Written at" hash that is
# not HEAD; STATE.md also when it was modified before the last commit. Words
# match whole words only, so "uncommitted" never counts as "committed".
HEAD_SHA="$(git rev-parse HEAD 2>/dev/null)"
AHEAD="$(git rev-list --count '@{upstream}..HEAD' 2>/dev/null || echo 0)"
says() { grep -i -n -o -E ".{0,40}\\b($2)\\b.{0,40}" "$1" 2>/dev/null | head -1 | sed 's/:/: /'; }
stale() {
  local f="$1" hit written
  if [ -z "$PORCELAIN" ]; then
    hit="$(says "$f" 'uncommitted|dirty')"
    [ -n "$hit" ] && echo "FLAG: STALE $f: says uncommitted or dirty, but git status --porcelain is empty (line $hit)"
  else
    hit="$(says "$f" 'clean|committed')"
    [ -n "$hit" ] && echo "FLAG: STALE $f: says clean or committed, but git status --porcelain is not empty (line $hit)"
  fi
  if [ "$AHEAD" -gt 0 ]; then
    hit="$(says "$f" 'pushed')"
    [ -n "$hit" ] && echo "FLAG: STALE $f: says pushed, but the branch is $AHEAD commits ahead of its upstream (line $hit)"
  fi
  # The hash sits on or under a line that starts with the "Written at" label, and
  # is a full object name or a short one naming a commit, so a hash quoted in
  # prose, an epoch number, or a word like "defaced" is never taken for it.
  written="$(grep -i -E -A3 '^[-#*[:space:]]*([0-9]+\.)?[*[:space:]]*written at' "$f" 2>/dev/null \
    | grep -o -E '\b[0-9a-f]{7,64}\b' | while read -r w; do
        if [ "${#w}" -ge 40 ] || git cat-file -e "$w^{commit}" 2>/dev/null; then echo "$w"; break; fi
      done)"
  if [ -n "$written" ]; then
    case "$HEAD_SHA" in
      "$written"*) ;;
      *) echo "FLAG: STALE $f: Written at $written is not HEAD $(git rev-parse --short HEAD)" ;;
    esac
  fi
}
if [ -n "$HANDOFF" ]; then
  HANDOFF="${HANDOFF#"$ROOT"/}"
  stale "$HANDOFF"
fi
if [ -f STATE.md ]; then
  LAST_COMMIT="$(git log -1 --format=%ct 2>/dev/null)"
  MTIME="$(stat -c %Y STATE.md 2>/dev/null || stat -f %m STATE.md)"
  [ -n "$LAST_COMMIT" ] && [ "$MTIME" -lt "$LAST_COMMIT" ] \
    && echo "FLAG: STALE STATE.md: modified before the last commit"
  stale STATE.md
fi

# Loam pin: only for a project seeded from Loam. A pin must be a vX.Y.Z release
# tag and the newest one. ls-remote gets 5 s of wall clock: git's low-speed
# settings do not bound a stalled connect, and stock macOS has no `timeout`.
# set -m puts git in its own process group, so the kill also reaches its
# remote-https helpers. The gh: shorthand is Copier-only and fails in git.
ANSWERS=.copier-answers.yml
answer() { sed -n "s/^$1:[[:space:]]*//p" "$ANSWERS" | tr -d "\"'" | head -1; }
newest() { grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' | sort -t. -k1.2,1n -k2,2n -k3,3n | tail -1; }
tags() {
  local pid n=0
  set -m
  git ls-remote --tags https://github.com/samyakjhaveri/loam 2>/dev/null &
  pid=$!
  set +m
  while kill -0 "$pid" 2>/dev/null && [ "$n" -lt 50 ]; do sleep 0.1; n=$((n + 1)); done
  kill -KILL -- "-$pid" 2>/dev/null
  wait "$pid" 2>/dev/null
}
pin() {
  [ -f "$ANSWERS" ] || { PIN="not a Loam project"; return; }
  local commit latest src
  commit="$(answer _commit)"
  if ! printf '%s\n' "$commit" | grep -Eq '^v[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "FLAG: Loam pin $commit is not a release tag"
    PIN="$commit (not a release tag)"; return
  fi
  latest="$(tags | grep -v '\^{}$' | sed 's#.*refs/tags/##' | newest)"
  if [ -z "$latest" ]; then
    # Offline: fall back to VERSION in a reachable local template checkout.
    src="$(answer _src_path)"
    if [ -n "$src" ] && [ -f "$src/VERSION" ] && [ -f "$src/copier.yml" ]; then
      latest="v$(tr -d '[:space:]' < "$src/VERSION" | sed 's/^v//')"
    else
      PIN="$commit (pin check skipped: offline)"; return
    fi
  fi
  if [ "$commit" = "$latest" ]; then
    PIN="$commit (latest)"
  elif [ "$(printf '%s\n%s\n' "$commit" "$latest" | newest)" = "$commit" ]; then
    echo "FLAG: Loam pin $commit is newer than the newest release $latest"
    PIN="$commit (newer than the newest release)"
  else
    echo "FLAG: Loam pin $commit is not the latest release $latest; run uvx copier update --trust"
    PIN="$commit (not the latest)"
  fi
}
pin

echo "Handoff: ${HANDOFF:-none}"
echo "Loam pin: $PIN"
exit 0
