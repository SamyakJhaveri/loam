#!/usr/bin/env bash
# Self-test for ../scripts/validate_findings.py (the quote gate).
# Usage: run_selftest.sh [ROOT]
# ROOT (default: this directory) holds paper_fixture.txt, a synthetic pdftotext-style dump in
# which the small-caps name ExampleSys is split as "E XAMPLE S YS", and paper_fixture.tex, a
# .tex file with a % comment. paper_fixture.toml is the config the gate reads through
# PAPER_TOOLS_CONFIG; it lists ExampleSys in paper.smallcaps_names.
# Fixtures: findings_abc.json (A real quote, B invented quote, C no quote with a normal locus),
# findings_a.json (A only), findings_absence.json (D absence: locus, no quote),
# findings_tex_comment.json (E quote only in a % comment), findings_smallcaps.json
# (F "ExampleSys" against "E XAMPLE S YS", with the config and without it),
# findings_wrong_line.json (G A's quote, line 1), findings_critic.json (H lens critic) and
# findings_bad_lens.json (I valid except for a lens outside the enum).
# Exit 0 when every step gives its expected exit code, 1 otherwise.
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
V="$HERE/../scripts/validate_findings.py"
ROOT="${1:-$HERE}"
if [ ! -f "$ROOT/paper_fixture.txt" ]; then
  echo "run_selftest: $ROOT/paper_fixture.txt not found" >&2
  exit 1
fi
TMP="$(mktemp -d "${TMPDIR:-/tmp}/vf_selftest.XXXXXX")" || exit 1
trap 'rm -rf "$TMP"' EXIT
cd "$ROOT" || exit 1
# Without these, the config would be looked up from the git repository holding this folder.
export PAPER_TOOLS_ROOT="$ROOT" PAPER_TOOLS_CONFIG="$HERE/paper_fixture.toml"

fails=0
expect() {  # expect WANT GOT LABEL
  if [ "$1" = "$2" ]; then
    echo "PASS  exit $2  $3"
  else
    echo "FAIL  exit $2, expected $1  $3"
    fails=$((fails + 1))
  fi
}

echo '[]' | python3 "$V" >/dev/null
expect 0 $? "empty array validates"

python3 "$V" --fill-ids "$HERE/findings_abc.json" >"$TMP/abc.json"
expect 0 $? "--fill-ids on A, B, C"

python3 "$V" --check-quotes --require-quotes "$TMP/abc.json" --root "$ROOT" >"$TMP/abc.out"
expect 1 $? "--check-quotes --require-quotes on A, B, C"
if grep -q 'findings\[1\]' "$TMP/abc.out" && grep -q 'findings\[2\]' "$TMP/abc.out" &&
  ! grep -q 'findings\[0\]' "$TMP/abc.out"; then
  echo "PASS  output names B and C, not A"
else
  echo "FAIL  output should name findings[1] (B) and findings[2] (C) only:"
  cat "$TMP/abc.out"
  fails=$((fails + 1))
fi

python3 "$V" --fill-ids "$HERE/findings_a.json" >"$TMP/a.json"
expect 0 $? "--fill-ids on A"

python3 "$V" --check-quotes --require-quotes "$TMP/a.json" --root "$ROOT" >/dev/null
expect 0 $? "--check-quotes --require-quotes on A only"

gate() {  # gate WANT FIXTURE LABEL: --fill-ids, then --check-quotes --require-quotes
  python3 "$V" --fill-ids "$HERE/$2" >"$TMP/g.json"
  expect 0 $? "--fill-ids on $2"
  python3 "$V" --check-quotes --require-quotes "$TMP/g.json" --root "$ROOT" >/dev/null
  expect "$1" $? "--check-quotes --require-quotes: $3"
}
gate 0 findings_absence.json "D absence: locus with no quote passes"
gate 1 findings_tex_comment.json "E quote only in a .tex % comment fails (P3)"
gate 0 findings_smallcaps.json "F ExampleSys matches E XAMPLE S YS (P4, paper.smallcaps_names)"
env -u PAPER_TOOLS_CONFIG PAPER_TOOLS_ROOT="$TMP" \
  python3 "$V" --check-quotes --require-quotes "$TMP/g.json" --root "$ROOT" >/dev/null
expect 1 $? "--check-quotes --require-quotes: F fails with no paper.smallcaps_names (P4)"
gate 1 findings_wrong_line.json "G real quote 7 lines from its line fails (P9)"
gate 0 findings_critic.json "H lens critic passes"

python3 "$V" "$HERE/findings_bad_lens.json" >"$TMP/bad_lens.out"
expect 1 $? "I lens outside the enum fails"
if grep -q 'findings\[0\]\.lens:' "$TMP/bad_lens.out" && ! grep -qv -e '^validate-findings:' -e 'findings\[0\]\.lens:' "$TMP/bad_lens.out"; then
  echo "PASS  output names only the lens of I"
else
  echo "FAIL  output should name findings[0].lens only:"
  cat "$TMP/bad_lens.out"
  fails=$((fails + 1))
fi

[ "$fails" -eq 0 ] && echo "run_selftest: all steps passed" && exit 0
echo "run_selftest: $fails step(s) failed"
exit 1
