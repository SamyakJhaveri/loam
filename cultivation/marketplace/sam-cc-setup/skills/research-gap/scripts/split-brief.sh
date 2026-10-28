#!/usr/bin/env bash
# Split a run's brief.md into one brief-<seat>.md per "## Seat <seat>" section, each holding
# everything above the first seat section (the shared part) plus that seat's section only, then
# remove brief.md so no seat can read another seat's seed. Refuses, keeping brief.md, when it has
# no "## Seat <seat>" heading, has another "## " section after the first one, or names one seat
# id twice; removes brief.md only after every seat file is written.
set -euo pipefail
run=${1:?usage: split-brief.sh <run folder>}
brief=$run/brief.md
if ! grep -q '^## Seat [^ ]' "$brief"; then
  echo "split-brief: no '## Seat <seat>' heading in $brief; kept it" >&2
  exit 1
fi
if awk '/^## Seat [^ ]/ { seat = 1; next } seat && /^## / { late = 1 } END { exit !late }' "$brief"; then
  echo "split-brief: a '## ' section follows the first '## Seat' heading in $brief; move shared sections above it; kept it" >&2
  exit 1
fi
dup=$(awk '/^## Seat [^ ]/ { print $3 }' "$brief" | sort | uniq -d | paste -sd " " -)
if [ -n "$dup" ]; then
  echo "split-brief: seat id used twice in $brief: $dup; give each seat its own id; kept it" >&2
  exit 1
fi
awk -v dir="$run" '
  /^## Seat [^ ]/ { if (out) close(out); out = dir "/brief-" $3 ".md"; printf "%s", shared > out; print > out; next }
  !out { shared = shared $0 "\n"; next }
  { print > out }
' "$brief"
rm "$brief"
ls "$run"/brief-*.md
