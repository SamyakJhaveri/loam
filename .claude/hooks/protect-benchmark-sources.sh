#!/usr/bin/env bash
# protect-benchmark-sources.sh
#
# PreToolUse hook — blocks Edit/Write on benchmark source code files.
#
# ALLOWED (fix build/run infrastructure):
#   - Makefile, *.mk  (even inside benchmark source dirs)
#   - specs/*.json
#
# BLOCKED (original benchmark program code):
#   - *.cu *.cpp *.c *.cl *.h *.cuh *.cc *.cxx inside benchmark source trees
#   - Claude Code Operational Playbook.md (unconditionally)
#
# Receives full hook event JSON on stdin:
#   { "tool_name": "Edit", "tool_input": { "file_path": "...", ... } }
# Exits 2 to block, 0 to allow.

INPUT=$(cat)

FILE_PATH=$(python3 -c "
import sys, json
try:
    d = json.loads(sys.stdin.read())
    ti = d.get('tool_input', d)
    print(ti.get('file_path', ''))
except Exception:
    print('')
" <<< "$INPUT" 2>/dev/null)

# No file path — nothing to check, allow
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# ── Unconditional block ──────────────────────────────────────────────────────

if echo "$FILE_PATH" | grep -qF "Claude Code Operational Playbook"; then
    echo "BLOCKED: Claude Code Operational Playbook.md is read-only." >&2
    exit 2
fi

# ── Makefiles are always allowed (even inside benchmark dirs) ────────────────

BASENAME=$(basename "$FILE_PATH")
if echo "$BASENAME" | grep -qiE '^(GNUmakefile|Makefile|makefile)$|\.mk$|\.make$'; then
    exit 0
fi

# ── Benchmark source code directories ───────────────────────────────────────
# Matches any file inside a known benchmark source tree.

BENCHMARK_DIRS_RE='/(rodinia|rodinia-src|HeCBench-master|hecbench|xsbench-src)/'

SOURCE_EXTS_RE='\.(cu|cpp|cxx|cc|c|cl|h|hpp|hh|cuh|f|f90|f77|f03)$'

if echo "$FILE_PATH" | grep -qE "$BENCHMARK_DIRS_RE" && \
   echo "$FILE_PATH" | grep -qiE "$SOURCE_EXTS_RE"; then
    echo "BLOCKED: Benchmark source code is read-only: $(basename "$FILE_PATH")" >&2
    echo "  Path: $FILE_PATH" >&2
    echo "  Fix the spec JSON or Makefile instead, or classify as KNOWN_FAIL." >&2
    exit 2
fi

exit 0
