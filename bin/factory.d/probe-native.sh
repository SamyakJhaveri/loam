#!/usr/bin/env bash
# bin/factory.d/probe-native.sh <clone> - one paid call of the native worker shell on a scratch clone of another target
# (docs/research/2026-11-12-distbench-priming/design-pick.md, unit U3). It sources this checkout's bin/factory, writes the frozen
# worker settings with freeze_shell, builds the worker command with worker_cmd, and runs that command in the clone,
# so a wrong flag or settings file cannot pass. The model runs six Bash calls (an AF_UNIX bind in a multi-line
# python3 -c, a systemd-run scope in distbench-build.slice, docker ps, mpirun, a git commit in the clone, and a kill loop over every process group outside its own shell) and the
# probe reads the real init event and tool results. It prints one line per command, the count of permission_denied
# events, the cost, and last
#   permissionMode=auto plugin=<this checkout>/cultivation/marketplace/sam-cc-setup verify-distbench=yes BIND_OK
# exiting 0 only when all of those hold and no call was denied. The clone needs a GitHub origin URL (use_target reads
# the target from it; nothing is fetched) and is changed by one empty commit. MAX_TURNS (8) bounds the call.
# The pstack gate fails open here, since the probe freezes no pstack-gate.py (the hook says so on stderr).
set -uo pipefail
[ $# -eq 1 ] && [ -d "$1" ] || { echo "usage: $0 <scratch clone of the target>" >&2; exit 2; }
clone=$(cd "$1" && pwd)
root=$(cd "$(dirname "$0")/../.." && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/probe-native.XXXXXX")
export FACTORY_SOURCED=1 FACTORY_ROOT="$root" FACTORY_RUNS_ROOT="$work/runs"
# shellcheck source=bin/factory
. "$root/bin/factory"
die() { echo "probe-native: $*" >&2; exit 2; }
use_target "$clone" || die "$clone is not a checkout with a GitHub origin URL"
target_is_loam && die "$clone is Loam itself, whose worker keeps the sandboxed shell"
user_token_free || die "$(user_settings) has CLAUDE_CODE_OAUTH_TOKEN in its env; bin/factory would refuse this launch"
RUN="$work/run"; WORKTREE="$clone"; LOG="$RUN/factory.log"; DECISIONS="$RUN/worker/decisions.md"
mkdir -p "$RUN/frozen" "$RUN/worker" "$RUN/tasks" && touch "$LOG"
freeze_shell
cp "$root/bin/factory.d/unattended.md" "$RUN/frozen/unattended.md"
printf 'exit 0\n' > "$RUN/frozen/checks.sh"   # the Stop hook's checks: nothing to gate in a probe
MAX_TURNS=8
worker_cmd

# Command 6 is R543's kill loop (distbench): the worker's shell must be in another PID namespace than this probe, and
# SIGKILL to every process group outside the shell's own ancestry must end its inner sentinel and leave this one alive.
setsid tail -f /dev/null > /dev/null 2>&1 < /dev/null &
host=$!
call=
trap 'kill "$host" 2> /dev/null' EXIT
trap '[ -z "$call" ] || { kill "$call" 2> /dev/null; wait "$call"; }; exit 130' INT
trap '[ -z "$call" ] || { kill "$call" 2> /dev/null; wait "$call"; }; exit 143' TERM
hostns=$(readlink /proc/self/ns/pid)
cat > "$work/prompt.md" <<EOF
This is a probe of your shell. Run each of these six commands in its own Bash call, in this order, exactly as written,
whatever an earlier one printed. Then reply with the single word done.

1.
python3 -c '
import os, socket, tempfile
p = os.path.join(tempfile.mkdtemp(), "s")
socket.socket(socket.AF_UNIX).bind(p)
print("BIND_OK")'

2.
systemd-run --user --scope -q --slice=distbench-build.slice true && echo SYSTEMD_OK

3.
docker ps > /dev/null && echo DOCKER_OK

4.
mpirun -n 1 true 2> /dev/null && echo MPI_OK

5.
git -C $clone -c user.name=probe -c user.email=probe@example.invalid commit -q --allow-empty -m probe-native && echo COMMIT_OK

6.
setsid -w tail -f /dev/null & inner=\$!; python3 -c '
import os, signal
if os.readlink("/proc/self/ns/pid") == "$hostns":
    raise SystemExit("NOT_CONTAINED")
mine, p = set(), os.getpid()
while p > 0:
    mine.add(os.getpgid(p))
    p = int(open(f"/proc/{p}/stat").read().rsplit(")", 1)[1].split()[1])
for d in os.listdir("/proc"):
    if d.isdigit():
        try:
            g = os.getpgid(int(d))
        except OSError:
            continue
        if g not in mine:
            try:
                os.killpg(g, signal.SIGKILL)
            except OSError:
                pass' && { wait \$inner; [ \$? = 137 ] && echo CONTAINED_OK; }; kill \$inner 2> /dev/null
EOF

out="$work/out.jsonl"
echo "probe-native: running the worker command in $clone; stream in $out" >&2
# In the background, so an INT or TERM trap runs at once and ends the call (bash defers traps until a foreground child ends).
( cd "$clone" && exec "${WORKER_CMD[@]}" < "$work/prompt.md" > "$out" 2> "$work/stderr" ) &
call=$!
wait "$call" || echo "probe-native: the call exited non-zero; see $work/stderr" >&2
call=

# Each Bash call's command and the text of its tool result, joined by tool_use id.
results=$(jq -rs '
  ([.[] | select(.type == "assistant") | .message.content[]? | select(.type == "tool_use") | {(.id): (.input.command // "")}] | add // {}) as $cmd
  | [.[] | select(.type == "user") | .message.content[]? | select(.type == "tool_result")
     | {cmd: $cmd[.tool_use_id], text: (.content | if type == "array" then map(.text? // "") | join("") else tostring end)}]' "$out")
status=0
for m in BIND_OK SYSTEMD_OK DOCKER_OK MPI_OK COMMIT_OK CONTAINED_OK; do
  # The marker counts only in a tool result whose command prints it, never in the model's own text.
  if jq -e --arg m "$m" 'any(.[]; (.cmd | contains($m)) and (.text | split("\n") | any(. == $m)))' <<< "$results" > /dev/null; then
    echo "$m ok"
  else
    echo "$m MISSING: $(jq -r --arg m "$m" '[.[] | select(.cmd | contains($m)) | .text][0] // "no such call" | gsub("\n"; " ") | .[0:300]' <<< "$results")"
    status=1
  fi
done
if kill -0 "$host" 2> /dev/null; then echo "host sentinel $host alive"; else echo "host sentinel $host KILLED"; status=1; fi
denied=$(jq -s '[.[] | select(.type == "system" and .subtype == "permission_denied")] | length' "$out")
jq -rs '.[] | select(.type == "system" and .subtype == "permission_denied") | "denied: \(.tool_name // "?") \(.decision_reason_type // "?"): \(.tool_input.command // .tool_input // "" | tostring | .[0:200])"' "$out"
echo "permission_denied events: $denied; result permission_denials: $(jq -s '[.[] | select(.type == "result") | .permission_denials // [] | length] | add // 0' "$out")"
echo "cost: $(jq -rs '[.[] | select(.type == "result") | .total_cost_usd] | last // "no result event"' "$out") usd, turns $(jq -rs '[.[] | select(.type == "result") | .num_turns] | last // 0' "$out")"
[ "$denied" -eq 0 ] || status=1

init=$(jq -cs '[.[] | select(.type == "system" and .subtype == "init")][0] // {}' "$out")
mode=$(jq -r '.permissionMode // "none"' <<< "$init")
plugin=$(jq -r '[.plugins[]? | select(.name == "sam-cc-setup") | .path] | join(",") | if . == "" then "none" else . end' <<< "$init")
vd=$(jq -r 'if (.skills // []) | index("verify-distbench") then "yes" else "no" end' <<< "$init")
bind=BIND_FAIL; jq -e 'any(.[]; .cmd | contains("BIND_OK")) and any(.[]; .text | split("\n") | any(. == "BIND_OK"))' <<< "$results" > /dev/null && bind=BIND_OK
{ [ "$mode" = auto ] && [ "$plugin" = "$PLUGIN_SRC" ] && [ "$vd" = yes ] && [ "$bind" = BIND_OK ]; } || status=1
echo "permissionMode=$mode plugin=$plugin verify-distbench=$vd $bind"
exit "$status"
