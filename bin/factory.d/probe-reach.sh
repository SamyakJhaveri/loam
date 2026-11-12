#!/usr/bin/env bash
# bin/factory.d/probe-reach.sh <clone> - one paid call of the factory worker command, to show what a fresh headless
# worker reaches: the sam-cc-setup copy it loads, the pstack router rows in that copy, and the owner skills audit and
# surprise-me read by path beside the router. Like probe-native.sh it sources this checkout's bin/factory, freezes the
# worker shell with freeze_shell and builds the command with worker_cmd, so a wrong flag or plugin path cannot pass.
# The clone needs a GitHub origin URL (use_target reads the target from it; nothing is fetched); it is not changed.
# Prints one line per check and last `reach: OK` or `reach: FAIL`, exiting 0 only on OK. PROBE_BUDGET_USD caps the call (0.3).
set -uo pipefail
[ $# -eq 1 ] && [ -d "$1" ] || { echo "usage: $0 <checkout of the target>" >&2; exit 2; }
clone=$(cd "$1" && pwd)
root=$(cd "$(dirname "$0")/../.." && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/probe-reach.XXXXXX")
export FACTORY_SOURCED=1 FACTORY_ROOT="$root" FACTORY_RUNS_ROOT="$work/runs"
# shellcheck source=bin/factory
. "$root/bin/factory"
die() { echo "probe-reach: $*" >&2; exit 2; }
use_target "$clone" || die "$clone is not a checkout with a GitHub origin URL"
RUN="$work/run"; WORKTREE="$clone"; LOG="$RUN/factory.log"; DECISIONS="$RUN/worker/decisions.md"
mkdir -p "$RUN/frozen" "$RUN/worker" "$RUN/tasks" && touch "$LOG"
freeze_shell
cp "$root/bin/factory.d/unattended.md" "$RUN/frozen/unattended.md"
printf 'exit 0\n' > "$RUN/frozen/checks.sh"
MAX_TURNS=6; ROUND_BUDGET_USD="${PROBE_BUDGET_USD:-0.3}"
worker_cmd
router=$(router_file) || die "no router under $(run_plugin_dir)"
skills=${router%/pstack/SKILL.md}
status=0
for row in surprise-me architect audit reflect correct automate-me; do
  if grep -qE "(\| $row \(|\`<S>/$row\`)" "$router"; then echo "router row $row ok"; else echo "router row $row MISSING in $router"; status=1; fi
done

cat > "$work/prompt.md" <<EOF
This is a probe of what you can read. Use the Read tool on each of these three files, in this order, then reply with
the single word done.
$router
$skills/audit/SKILL.md
$skills/surprise-me/SKILL.md
EOF
out="$work/out.jsonl"
echo "probe-reach: running the worker command in $clone (budget $ROUND_BUDGET_USD usd); stream in $out" >&2
( cd "$clone" && "${WORKER_CMD[@]}" < "$work/prompt.md" > "$out" 2> "$work/stderr" ) \
  || echo "probe-reach: the call exited non-zero; see $work/stderr" >&2

# A file counts as read only when a Read call of that path returned its own `name:` frontmatter line.
for f in "$router" "$skills/audit/SKILL.md" "$skills/surprise-me/SKILL.md"; do
  want=$(grep -m1 '^name:' "$f")
  if jq -es --arg p "$f" --arg w "$want" '
      ([.[] | select(.type == "assistant") | .message.content[]? | select(.type == "tool_use" and .name == "Read" and .input.file_path == $p) | .id]) as $ids
      | any(.[] | select(.type == "user") | .message.content[]? | select(.type == "tool_result" and (.tool_use_id as $t | $ids | index($t)));
            (.content | if type == "array" then map(.text? // "") | join("") else tostring end) | contains($w))' "$out" > /dev/null; then
    echo "read $f ok"
  else
    echo "read $f MISSING"; status=1
  fi
done
init=$(jq -cs '[.[] | select(.type == "system" and .subtype == "init")][0] // {}' "$out")
plugin=$(jq -r '[.plugins[]? | select(.name == "sam-cc-setup") | "\(.path) \(.version)"] | join(",") | if . == "" then "none" else . end' <<< "$init")
echo "loaded sam-cc-setup: $plugin; claude $(jq -r '.claude_code_version // "?"' <<< "$init"); permissionMode=$(jq -r '.permissionMode // "?"' <<< "$init")"
[ "${plugin% *}" = "$PLUGIN_SRC" ] || { echo "plugin path is not $PLUGIN_SRC"; status=1; }
echo "cost: $(jq -rs '[.[] | select(.type == "result") | .total_cost_usd] | last // "no result event"' "$out") usd"
[ "$status" -eq 0 ] && echo "reach: OK" || echo "reach: FAIL"
exit "$status"
