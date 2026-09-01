#!/usr/bin/env bash
# vet-skill.sh - security-scan an external skill before it enters the repo.
#
# Wraps NVIDIA SkillSpector (https://github.com/nvidia/skillspector), a static
# scanner for AI-agent skills. Every external skill or bundle added to
# cultivation/marketplace/ must pass this gate first (see CONTRIBUTING.md).
#
# Usage:
#   bin/vet-skill.sh <path-to-skill-dir>
#   bin/vet-skill.sh <https://github.com/owner/repo>     # cloned read-only first
#   bin/vet-skill.sh <target> --json                     # machine-readable line
#   bin/vet-skill.sh <target> --safe [--out <dir>]       # strip scripts, re-scan
#
# --safe removes every executable/script the skill ships (.py .sh .js .ts .rb
# .pl, Makefile, *.mk, and scripts/ dirs), keeping only prose and document
# assets, then scans what remains. Use it for a skill whose value is its written
# guidance, not its code. With --out <dir>, the stripped tree is copied there on
# a non-REJECT verdict, ready to install. Stripping removes code-execution risk;
# it does NOT remove prompt-injection risk carried in the prose, so a --safe run
# can still return REVIEW or REJECT on the text alone - read those findings.
#
# Exit codes (map to SkillSpector severity, worst finding wins):
#   0  PASS    - severity NONE or LOW; safe to adopt
#   1  REVIEW  - severity MEDIUM; a human must read the findings and decide
#   2  REJECT  - severity HIGH or CRITICAL; do not adopt
#   3  no scanner - SkillSpector not installed (prints install + update hint)
#   4  scan error - the scan could not run or produced no verdict
#
# The scan is static (--no-llm): no API key, no network beyond the optional
# clone, deterministic. Records nothing; the caller records the verdict.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIB_PREFIX="vet-skill"
# shellcheck source=/dev/null
. "$ROOT/bin/lib.sh"

JSON_OUT=0
SAFE=0
OUT_DIR=""
TARGET=""
expect_out=0
for arg in "$@"; do
  if [ "$expect_out" -eq 1 ]; then OUT_DIR="$arg"; expect_out=0; continue; fi
  case "$arg" in
    --json) JSON_OUT=1 ;;
    --safe) SAFE=1 ;;
    --out) expect_out=1 ;;
    -*) die "unknown option: $arg" ;;
    *) TARGET="$arg" ;;
  esac
done
[ -n "$TARGET" ] || die "usage: vet-skill.sh <path-or-url> [--json] [--safe [--out <dir>]]"
[ "$expect_out" -eq 0 ] || die "--out needs a directory argument"

if ! command -v skillspector >/dev/null 2>&1; then
  echo "FAIL: SkillSpector not found." >&2
  echo "  Install:  uv tool install skillspector" >&2
  echo "  Update:   uv tool upgrade skillspector" >&2
  exit 3
fi

TMP="$(mktemp -d)"
trap 'python3 -c "import shutil,sys;shutil.rmtree(sys.argv[1],ignore_errors=True)" "$TMP"' EXIT

SCAN_PATH="$TARGET"
case "$TARGET" in
  http://*|https://*|git@*)
    info "cloning $TARGET (read-only, shallow)"
    if ! git clone -q --depth 1 "$TARGET" "$TMP/repo" 2>"$TMP/clone.err"; then
      echo "FAIL: could not clone $TARGET" >&2
      tail -3 "$TMP/clone.err" >&2 || true
      exit 4
    fi
    SCAN_PATH="$TMP/repo"
    ;;
esac

[ -e "$SCAN_PATH" ] || { echo "FAIL: no such path: $SCAN_PATH" >&2; exit 4; }

if [ "$SAFE" -eq 1 ]; then
  STRIPPED="$TMP/stripped"
  cp -R "$SCAN_PATH" "$STRIPPED"
  # Remove everything that can execute; keep prose and document assets.
  find "$STRIPPED" \( \
      -name '*.py' -o -name '*.sh' -o -name '*.bash' -o -name '*.zsh' \
      -o -name '*.js' -o -name '*.mjs' -o -name '*.ts' -o -name '*.rb' \
      -o -name '*.pl' -o -name '*.php' -o -name 'Makefile' -o -name '*.mk' \
      -o -name '*.bat' -o -name '*.ps1' \
    \) -type f -delete 2>/dev/null || true
  find "$STRIPPED" -type d -name scripts -exec \
    python3 -c "import shutil,sys;[shutil.rmtree(p,ignore_errors=True) for p in sys.argv[1:]]" {} + 2>/dev/null || true
  find "$STRIPPED" -type d -empty -delete 2>/dev/null || true
  info "safe mode: stripped executables and scripts, scanning prose only"
  SCAN_PATH="$STRIPPED"
fi

REPORT="$TMP/report.json"
SKILLSPECTOR_LOG_LEVEL="${SKILLSPECTOR_LOG_LEVEL:-ERROR}" \
  skillspector scan "$SCAN_PATH" --recursive --no-llm \
    --format json --output "$REPORT" >"$TMP/scan.out" 2>"$TMP/scan.err" || true

if [ ! -s "$REPORT" ]; then
  echo "FAIL: SkillSpector produced no report for $TARGET" >&2
  tail -5 "$TMP/scan.err" >&2 || true
  exit 4
fi

# Parse the worst severity across every scanned skill in the report.
read -r VERDICT SEVERITY SCORE ISSUES <<EOF
$(python3 - "$REPORT" <<'PY'
import json, sys
data = json.load(open(sys.argv[1]))
# A report is one object (single skill) or a list (recursive, many skills).
records = data if isinstance(data, list) else [data]
rank = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
worst = 0
score = 0
issue_titles = []
for rec in records:
    ra = rec.get("risk_assessment", {}) if isinstance(rec, dict) else {}
    sev = str(ra.get("severity", "NONE")).upper()
    worst = max(worst, rank.get(sev, 0))
    try:
        score = max(score, int(ra.get("score", 0)))
    except (TypeError, ValueError):
        pass
    for issue in (rec.get("issues") or [])[:6]:
        t = issue.get("title") or issue.get("rule") or issue.get("id")
        if t:
            issue_titles.append(str(t).replace(" ", "_"))
severity = {v: k for k, v in rank.items()}[worst]
verdict = {0: "PASS", 1: "PASS", 2: "REVIEW", 3: "REJECT", 4: "REJECT"}[worst]
print(verdict, severity, score, ",".join(issue_titles[:4]) or "none")
PY
)
EOF

if [ "$JSON_OUT" -eq 1 ]; then
  printf '{"target":"%s","verdict":"%s","severity":"%s","score":%s,"top_issues":"%s","safe":%s}\n' \
    "$TARGET" "$VERDICT" "$SEVERITY" "${SCORE:-0}" "$ISSUES" "$SAFE"
fi

# --safe --out: hand the caller the stripped, non-rejected tree to install from.
if [ "$SAFE" -eq 1 ] && [ -n "$OUT_DIR" ] && [ "$VERDICT" != "REJECT" ]; then
  python3 -c "import shutil,sys;shutil.rmtree(sys.argv[1],ignore_errors=True)" "$OUT_DIR"
  cp -R "$STRIPPED" "$OUT_DIR"
  info "stripped skill written to $OUT_DIR"
fi

case "$VERDICT" in
  PASS)   ok   "PASS   $TARGET  (severity $SEVERITY, score ${SCORE:-0})";   exit 0 ;;
  REVIEW) warn "REVIEW $TARGET  (severity $SEVERITY, score ${SCORE:-0}) - a human must read: $ISSUES"; exit 1 ;;
  REJECT) echo "FAIL: REJECT $TARGET (severity $SEVERITY, score ${SCORE:-0}) - $ISSUES" >&2; exit 2 ;;
  *)      echo "FAIL: no verdict for $TARGET" >&2; exit 4 ;;
esac
