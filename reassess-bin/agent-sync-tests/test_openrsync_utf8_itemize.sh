#!/usr/bin/env bash
# test_openrsync_utf8_itemize.sh
# H4 (group 7): macOS openrsync escapes bytes 0x80-0x9F as \#ooo mid-UTF-8, so an
# itemize line for a non-ASCII filename is invalid UTF-8; under a UTF-8 locale
# bash [[ =~ ]] fails both categorize regexes and the file is dropped with NO
# warning - silently unsyncable on the Mac. The scan must parse the stream
# byte-wise (LC_ALL=C) and SURFACE the file (a visible warning), never drop it
# silently. openrsync-specific: GNU rsync emits valid UTF-8 and does not manifest
# H4, so this test SKIPs there.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"

if ! rsync --version 2>&1 | grep -qi openrsync; then
  echo "SKIP: H4 is openrsync-specific (GNU rsync emits valid UTF-8; no silent drop)"
  exit 0
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
CJK="日本-notes.md"

# Hub: a committed placeholder + identity.
mkdir -p "$HUB_SETUP"
echo "placeholder" > "$HUB_SETUP/.keep"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)

# Project: MANIFEST-LESS, a single CJK-named file (so a silent drop yields a bare
# "No changes" with the file invisible).
mkdir -p "$TMP/proj/.claude"
printf 'body\n' > "$TMP/proj/.claude/$CJK"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"

# Defer anything offered; we only inspect what the scan SURFACED.
set +e
out=$(printf 'd\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: scan exit $rc"; echo "$out"; exit 1; fi

# Fixture sanity (passes in BOTH states): the scan ran past the no-changes gate to
# the enumeration line, so the CJK itemize line WAS presented to the categorize
# loop. This rules out a warning-absent that is really a broken fixture / early
# no-op. (The CJK file itemizes as a non-empty CHANGES, so "No changes" is never
# taken; the count is 0 in both states - dropped pre-fix, candidate_ok-rejected
# post-fix - so only the warning below is the RED->GREEN flip.)
# NOTE: grep the output byte-wise (LC_ALL=C). The warning line legitimately
# contains invalid UTF-8 (openrsync's raw 0x80-0x9F bytes + \#ooo escapes), and a
# UTF-8-locale grep silently fails to match an ASCII substring that sits AFTER
# those bytes on the line - the very H4 class this group fixes (verified: default
# `grep -F notes.md` NOMATCH, `LC_ALL=C grep -F notes.md` MATCH).
if ! echo "$out" | LC_ALL=C grep -qF "new files to ask about"; then
  echo "FAIL: scan did not reach enumeration (fixture/engine problem, not H4)"; echo "$out"; exit 1
fi

# Assertion 1 (RED): the CJK file must be SURFACED, not silently dropped. Post-fix
# it is parsed byte-wise and candidate_ok rejects its \#ooo-escaped name with a
# visible warning; pre-fix the line matches neither regex under the UTF-8 locale
# and is dropped BEFORE candidate_ok, so no such warning appears (the scan just
# reports "0 new files").
if ! echo "$out" | LC_ALL=C grep -qF "ignoring unsafe candidate path"; then
  echo "FAIL: the non-ASCII file was silently dropped (no warning; not surfaced)"
  echo "--- scan output ---"; echo "$out"
  exit 1
fi

# Assertion 2 (RED): the surfaced warning names the file (its ASCII suffix
# survives the escaping). Pre-fix the file is invisible, so "notes.md" appears
# nowhere in the output.
if ! echo "$out" | LC_ALL=C grep -qF "notes.md"; then
  echo "FAIL: the surfaced warning does not name the dropped file (notes.md)"
  echo "$out"; exit 1
fi

echo "PASS: test_openrsync_utf8_itemize"
