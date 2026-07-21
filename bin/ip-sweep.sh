#!/usr/bin/env bash
# ip-sweep.sh — repeatable IP gate before any public push.
#
# PRIVATE-DEV TOOLING: this script is NOT shipped to the public repo — a tracked
# blocklist would leak the very names it scrubs. The blocklist itself lives in a
# gitignored term file (see IP_TERMS_FILE), never in this tracked script.
#
# Checks:
#   (1) no foreign-IP terms in tracked text files   — hard FAIL
#   (2) no git-LFS objects                           — WARN; FAIL under STRICT
#   (3) commit authors are the GitHub noreply only   — WARN; FAIL under STRICT
#
# The private dev archive has legitimately dirty authors/LFS, so (2) and (3) are
# WARN by default. Set IP_SWEEP_STRICT=1 (release.sh does, and any public run
# should) to make them hard failures — a real exit-code gate, not a note.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

STRICT="${IP_SWEEP_STRICT:-0}"

# Blocklist lives OUTSIDE this tracked script (gitignored) so the scrubbed names
# never ship in a file that could become public. Format: comment lines (#...) are
# ignored; the rest is joined into one extended-regex alternation.
IP_TERMS_FILE="${IP_TERMS_FILE:-bin/.ip-terms}"
# `|| true` so a present-but-empty/comment-only file yields TERMS="" and flows into
# the empty-TERMS WARN branch below, instead of aborting here under set -e/pipefail
# (the greps exit 1 when they match nothing).
TERMS="$(grep -vE '^[[:space:]]*#' "$IP_TERMS_FILE" 2>/dev/null | grep -vE '^[[:space:]]*$' | paste -sd '|' - || true)"

# Exclude private-archive-only paths + the binary hero-art renders (loam-hero-*,
# which grep -I skips as binary anyway): session plans, ADRs, human-only reference
# material. Public text docs (POST-RELEASE-BACKLOG, design-philosophy.md,
# concepts.yaml) are deliberately NOT excluded — if ever tracked they must be
# scanned. Terms under these paths are expected private history, not a leak.
EXCLUDE='^docs/(plans|adr)/|^_archive/|^cultivation/wip/|^docs/diagrams/loam-hero-'
FAIL=0

# Content check: decide on the OUTPUT (matching filenames), not on xargs' exit
# code — a multi-batch xargs can return non-zero from a later empty batch and mask
# a real match found in an earlier one.
if [[ -n "$TERMS" ]]; then
  HITS="$(git ls-files | grep -vE "$EXCLUDE" | xargs grep -lniIE "$TERMS" 2>/dev/null || true)"
  if [[ -n "$HITS" ]]; then
    echo "FAIL: foreign-IP terms found in tracked files:"; echo "$HITS"; FAIL=1
  fi
else
  echo "WARN: no term file at $IP_TERMS_FILE — content sweep SKIPPED (copy bin/.ip-terms.example to bin/.ip-terms and fill in the blocklist)."
  [[ "$STRICT" = 1 ]] && { echo "FAIL: strict mode requires a term file."; FAIL=1; }
fi

if command -v git-lfs >/dev/null 2>&1 && [ -n "$(git lfs ls-files 2>/dev/null)" ]; then
  echo "WARN: git-LFS objects tracked (must be empty in the public repo):"
  git lfs ls-files | sed 5q || true  # sed 5q avoids head's SIGPIPE under pipefail
  [[ "$STRICT" = 1 ]] && FAIL=1
fi

# Inspect the AUTHOR (%ae) only. An IP leak can only ride in on the author identity;
# the committer (%ce) on a GitHub web "Merge pull request" is GitHub's own server
# identity (noreply@github.com), never a leak. Unioning %ce here only minted false
# positives that hard-failed release under strict. (Matches this script's header:
# "commit authors are the GitHub noreply only".)
BAD_AUTHORS=$(git log --format='%ae' | sort -u | grep -v 'users.noreply.github.com' || true)
if [ -n "$BAD_AUTHORS" ]; then
  echo "WARN: non-noreply commit identities (must be clean in the public repo):"
  echo "$BAD_AUTHORS"
  [[ "$STRICT" = 1 ]] && FAIL=1
fi

# Footgun guard: bin/.ip-terms (gitignored, the REAL blocklist) and
# bin/.ip-terms.example (tracked, placeholders) are look-alikes. Editing the wrong
# one either leaks real terms into the tracked example or silently no-ops. Flag any
# non-comment, non-placeholder line that has crept into the tracked example.
# Keep PLACEHOLDERS in sync with the terms shipped in bin/.ip-terms.example.
EXAMPLE_FILE="bin/.ip-terms.example"
if [[ -f "$EXAMPLE_FILE" ]]; then
  PLACEHOLDERS='^(example-project-name|another vendored term|\\bacronym\\b)$'
  STRAY="$(grep -vE '^[[:space:]]*#' "$EXAMPLE_FILE" | grep -vE '^[[:space:]]*$' | grep -vE "$PLACEHOLDERS" || true)"
  if [ -n "$STRAY" ]; then
    echo "WARN: $EXAMPLE_FILE has non-placeholder line(s) — real terms belong ONLY in the gitignored bin/.ip-terms:"
    echo "$STRAY"
    [[ "$STRICT" = 1 ]] && FAIL=1
  fi
fi

if [ "$FAIL" -eq 0 ]; then
  [ "$STRICT" = 1 ] && echo "ip-sweep: PASS (strict)" || echo "ip-sweep: PASS (warn-only for authors/LFS; set IP_SWEEP_STRICT=1 to gate them)"
fi
exit "$FAIL"
