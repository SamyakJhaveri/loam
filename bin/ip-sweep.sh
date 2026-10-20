#!/usr/bin/env bash
# ip-sweep.sh - repeatable IP gate before any public push.
#
# This gate is tracked in the public Loam repo but is not rendered into projects.
# The blocklist itself lives in a gitignored term file (see IP_TERMS_FILE), never
# in this tracked script.
#
# Checks:
#   (1) no foreign-IP terms in tracked text files   - hard FAIL
#   (2) no git-LFS objects                           - WARN; FAIL under STRICT
#   (3) public author/committer identities only        - WARN; FAIL under STRICT
#
# The private dev archive has legitimately dirty authors/LFS, so (2) and (3) are
# WARN by default. Set IP_SWEEP_STRICT=1 (release.sh does, and any public run
# should) to make them hard failures - a real exit-code gate, not a note.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

STRICT="${IP_SWEEP_STRICT:-0}"
# IP_SWEEP_IDENTITY_ONLY=1 runs only check (3), as a hard FAIL. It needs no term file, so
# bin/check runs it on every PR, before a non-noreply identity reaches the public main.
IDENTITY_ONLY="${IP_SWEEP_IDENTITY_ONLY:-0}"
[[ "$IDENTITY_ONLY" = 1 ]] && STRICT=1
FAIL=0

# Authors must use a complete GitHub noreply address. Committers may additionally
# be GitHub's exact web-merge identity; checking both fields preserves the public
# history identity boundary without rejecting GitHub's merge commits.
#
# Grandfathered baseline (Samyak's ruling, 2026-08-29): four sync-factory commits
# merged publicly via PR #1 (last: 7868345...) carry a pre-noreply identity and are
# accepted as already public. The identity check inspects only commits AFTER the
# baseline; if the baseline SHA is absent (fresh shallow clone), fall back to full
# history so the gate fails closed rather than silently narrowing.
#
# Second baseline (Samyak's ruling, 2026-09-07): the 36 Lean v3 loop commits merged
# publicly via PRs #27 to #32 (last: ef7e9be) were made on jhaveris with the
# pre-noreply identity and are accepted as already public; that clone now commits
# as noreply. The first baseline above stays for the record.
#
# Third baseline (Samyak's ruling, 2026-10-18): 25 commits dated 2026-09-11 to
# 2026-09-18, already on the public main, carry the uci.edu identity (24 as author and
# committer, 76b8527 as committer only). They are accepted by exact SHA, not by range,
# so no later commit can slip in.
IDENTITY_ACCEPTED="
8f0655bdd446c5cbf1ab2b6a6a68bee0b2c9197c
8488af8b5afecde3782d3feec269d21be5d02011
60efc16ab4dc833eb2273516423d373e2b9f54fa
27cbcff5c4269eb32c4ed45d9912036ec532074e
06ce3e84f547464fc6ce6126908469de8022461c
7c4cfaf7e2a77b173f26ed1056c16fd023a8cc22
0f24cf202806c9292cf38af389f9f4e6db93fd65
d99e76411d0553a44b3ea09b02e5c049f9824a9e
f410b509b912fa42bfad8371aade7ae6656ffdfe
4949a5a5b939269051617d67a128d3871c9935cd
edf0ccd1568e7ebd84bc27c92cd2c542e5c16f3a
161e99749d960a8be3761143657540c87887370d
90aafd9be08b9fa3fa42ec55d00028d5756dcf45
1dd2b32a71c660ac857e59d7a9036450c5bffdfc
58763412a7ae633b4c55594a299b39f6cb9e2e0a
b5335e43ffdc1f1c38c3cc524f50707067490b6e
a809d4c556beb383fc0347fc9c24416c8f91b699
14af8938265bae28a4837ba2f245500df2dc5954
5bbfc598ccc0c619e4f88016aed63cdeb53183c5
4e8ee8ae1b6adf370e97405fa8a638818005be41
ef241270125e1c5aa6dd89577b7000fae3749887
e4c6f474094340dd9829740d9004a0a36e1c121b
0f35813a2275ec5ddb81853784b7ffbf734769e6
8200eef8a7ab1224b98d45e491e91ce528369a59
76b85275bf99a379b3ae7a49c0f30f7750f72617
"
IDENTITY_BASELINE="ef7e9be19bd50caf1407a9ada1db5ae7c6df8864"
IDENTITY_RANGE="HEAD"
git cat-file -e "$IDENTITY_BASELINE" 2>/dev/null && IDENTITY_RANGE="${IDENTITY_BASELINE}..HEAD"
NOREPLY_AUTHOR_RE='^[^@[:space:]]+@users\.noreply\.github\.com$'
NOREPLY_COMMITTER_RE='^([^@[:space:]]+@users\.noreply\.github\.com|noreply@github\.com)$'
# One email per commit whose full SHA is not accepted. awk compares whole SHAs, and an empty list exempts nothing.
# The list goes through ENVIRON: macOS awk rejects a newline in an `awk -v` value.
identities() {
  git log --format="%H $1" $IDENTITY_RANGE |
    ACCEPTED="$IDENTITY_ACCEPTED" awk 'BEGIN { n = split(ENVIRON["ACCEPTED"], s); for (i = 1; i <= n; i++) ok[s[i]] = 1 } !($1 in ok) { print $2 }'
}
# Read first, filter second: a failed git log or awk fails the check instead of reading as "no bad
# identities" (the `|| true` below only absorbs grep's no-match exit).
AUTHORS=$(identities '%ae') || { echo "FAIL: could not read commit author identities."; FAIL=1; }
COMMITTERS=$(identities '%ce') || { echo "FAIL: could not read commit committer identities."; FAIL=1; }
BAD_AUTHORS=$(sort -u <<<"$AUTHORS" | grep -vE "$NOREPLY_AUTHOR_RE" || true)
if [ -n "$BAD_AUTHORS" ]; then
  echo "WARN: non-noreply author identities (must be clean in the public repo):"
  echo "$BAD_AUTHORS"
  [[ "$STRICT" = 1 ]] && FAIL=1
fi
BAD_COMMITTERS=$(sort -u <<<"$COMMITTERS" | grep -vE "$NOREPLY_COMMITTER_RE" || true)
if [ -n "$BAD_COMMITTERS" ]; then
  echo "WARN: non-noreply committer identities (must be clean in the public repo):"
  echo "$BAD_COMMITTERS"
  [[ "$STRICT" = 1 ]] && FAIL=1
fi

if [[ "$IDENTITY_ONLY" = 1 ]]; then
  [ "$FAIL" -eq 0 ] && echo "ip-sweep: PASS (identity only)"
  exit "$FAIL"
fi

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
# concepts.yaml) are deliberately NOT excluded - if ever tracked they must be
# scanned. Terms under these paths are expected private history, not a leak.
EXCLUDE='^docs/(plans|adr)/|^_archive/|^docs/diagrams/loam-hero-.*\.(png|qa\.yaml)$'
# Content check: validate the assembled ERE before scanning. A malformed term
# must fail closed instead of being mistaken for a clean no-match result.
if [[ -n "$TERMS" ]]; then
  if grep -E "$TERMS" </dev/null >/dev/null 2>&1; then
    :
  else
    REGEX_RC=$?
    if [[ "$REGEX_RC" -gt 1 ]]; then
      echo "FAIL: invalid extended regex in $IP_TERMS_FILE; content sweep aborted."
      FAIL=1
    fi
  fi

  HITS=""
  if [[ "$FAIL" -eq 0 ]]; then
    while IFS=$'\t' read -r -d '' META FILE_PATH; do
      [[ "$META" =~ ^([0-9]{6})[[:space:]]([0-9a-f]{40})[[:space:]][0-3]$ ]] || continue
      MODE="${BASH_REMATCH[1]}"
      OID="${BASH_REMATCH[2]}"
      [[ "$MODE" == 160000 ]] && continue
      [[ "$FILE_PATH" =~ $EXCLUDE ]] && continue
      if [[ "$MODE" == 120000 ]]; then
        MATCH_CMD=(grep -niE "$TERMS")
      else
        MATCH_CMD=(grep -niIE "$TERMS")
      fi
      if git cat-file blob "$OID" | "${MATCH_CMD[@]}" >/dev/null; then
        HITS+="$FILE_PATH"$'\n'
      fi
    done < <(git ls-files -z --stage)
  fi
  if [[ -n "$HITS" ]]; then
    echo "FAIL: foreign-IP terms found in tracked files:"; echo "$HITS"; FAIL=1
  fi
else
  echo "WARN: no term file at $IP_TERMS_FILE - content sweep SKIPPED (copy bin/.ip-terms.example to bin/.ip-terms and fill in the blocklist)."
  [[ "$STRICT" = 1 ]] && { echo "FAIL: strict mode requires a term file."; FAIL=1; }
fi

if command -v git-lfs >/dev/null 2>&1 && [ -n "$(git lfs ls-files 2>/dev/null)" ]; then
  echo "WARN: git-LFS objects tracked (must be empty in the public repo):"
  git lfs ls-files | sed 5q || true  # sed 5q avoids head's SIGPIPE under pipefail
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
    echo "WARN: $EXAMPLE_FILE has non-placeholder line(s) - real terms belong ONLY in the gitignored bin/.ip-terms:"
    echo "$STRAY"
    [[ "$STRICT" = 1 ]] && FAIL=1
  fi
fi

if [ "$FAIL" -eq 0 ]; then
  [ "$STRICT" = 1 ] && echo "ip-sweep: PASS (strict)" || echo "ip-sweep: PASS (warn-only for authors/LFS; set IP_SWEEP_STRICT=1 to gate them)"
fi
exit "$FAIL"
