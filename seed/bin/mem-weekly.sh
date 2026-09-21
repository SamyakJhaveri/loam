#!/usr/bin/env bash
# mem-weekly.sh - weekly maintenance for the memory store (run from cron).
#
# Deletes traces older than a year, commits the store as a git baseline, then
# regenerates the recurring-errors and counts reports from the captured traces.
# Zero model calls. The cron line is documented in seed/docs/HARNESS.md; this
# ticket does not install it.
#
# The error-signature normalizer (first 100 chars, digits -> N) is ported from
# SuperClaude src/superclaude/pm_agent/reflexion.py (_create_error_signature, MIT);
# see the memory-v2 plan's "Borrowed code" note. Commit hash not pinned here.
#
# Store root: $LOAM_MEMSTORE, default ~/memstore.
# Usage: mem-weekly.sh

set -uo pipefail

STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
mkdir -p "$STORE" || exit 0
cd "$STORE" || exit 0
mkdir -p reports

# Retention: drop trace files older than 365 days by mtime, before the reports
# read them. Never INDEX.md, never anything under notes/ or reports/. Each
# deletion is logged so a forgotten transcript leaves an audit line.
if [ -d traces ]; then
  find traces -type f -mtime +365 ! -name 'INDEX.md' -print 2>/dev/null | while IFS= read -r old; do
    printf '%s deleted %s\n' "$(date +%F)" "$old" >> reports/retention.log
    rm -f -- "$old" 2>/dev/null || true
  done
fi

# The baseline holds reports and native-memory caches only. Traces stay out of git so
# that deleting a trace file forgets it (HARNESS.md, Accepted risks); a git history of
# transcripts would keep a pasted secret after the file is gone.
[ -d .git ] || git init -q 2>/dev/null
printf 'traces/\n.throttle/\n' > .gitignore
git add -A 2>/dev/null \
  && git -c user.name=memstore -c user.email=memstore@localhost \
       commit -qm "weekly $(date +%F)" 2>/dev/null || true

# Recurring errors: extract error lines from every trace (gzipped and plain),
# normalize each to a signature (first 100 chars, digits -> N) so runs that differ
# only in a port or pid collapse into one recurrence, and count the top 20.
python3 - <<'PY' > reports/recurring-errors.md
import collections, glob, gzip, re

ERR = re.compile(r'(?:Error: |RuntimeError|Traceback)[^"\\\n]{0,60}')
DIGITS = re.compile(r'\d')
counts = collections.Counter()
for fp in glob.glob('traces/*/*.jsonl') + glob.glob('traces/*/*.jsonl.gz'):
    opener = gzip.open if fp.endswith('.gz') else open
    try:
        with opener(fp, 'rt', encoding='utf-8', errors='replace') as fh:
            for line in fh:
                for match in ERR.findall(line):
                    counts[DIGITS.sub('N', match[:100])] += 1
    except Exception:
        continue
for sig, n in counts.most_common(20):
    print('%2d %s' % (n, sig))
PY

# Capture, retrieval, and application counts, so the weekly report says whether the
# memory layer is used, not only which errors recur. All three read gzipped traces.
# The recall manifest (mem-recall.sh) itself names memsearch and every trust word,
# so its lines are skipped first - otherwise every session would score one
# retrieval and one application from the injected manifest, not from real use.
# Application requires the label form the manifest asks for (a "label" word near a
# trust word), not the bare word, which occurs in ordinary prose ("not supported").
read -r capture retrieval application < <(python3 - <<'PY'
import glob, gzip, re

files = glob.glob('traces/*/*.jsonl') + glob.glob('traces/*/*.jsonl.gz')
RET = re.compile('memsearch')
APP = re.compile(r'\blabel\w*\b[^\n]{0,40}\b(supported|contradicts|near-match|insufficient)\b', re.I)
# Markers unique to the recall manifest (mem-recall.sh); a line carrying one is the
# injected manifest, not the agent's own use, so it is not counted.
MANIFEST = re.compile('Not loaded:|Label every recalled item')
retrieval = application = 0
for fp in files:
    opener = gzip.open if fp.endswith('.gz') else open
    try:
        with opener(fp, 'rt', encoding='utf-8', errors='replace') as fh:
            for line in fh:
                if MANIFEST.search(line):
                    continue
                if RET.search(line):
                    retrieval += 1
                if APP.search(line):
                    application += 1
    except Exception:
        continue
print(len(files), retrieval, application)
PY
)

sessions="n/a"
CLAUDE_PROJECTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
CODEX_SESSIONS="${CODEX_HOME:-$HOME/.codex}/sessions"
if [ -d "$CLAUDE_PROJECTS" ] || [ -d "$CODEX_SESSIONS" ]; then
  claude_n=0; codex_n=0
  [ -d "$CLAUDE_PROJECTS" ] && claude_n=$(ls "$CLAUDE_PROJECTS"/*/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
  [ -d "$CODEX_SESSIONS" ] && codex_n=$(find "$CODEX_SESSIONS" -type f -name 'rollout-*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
  sessions=$((claude_n + codex_n))
fi
{
  printf 'capture %s traces, %s sessions seen\n' "${capture:-0}" "$sessions"
  printf 'retrieval %s\n' "${retrieval:-0}"
  printf 'application %s\n' "${application:-0}"
} > reports/counts.md
exit 0
