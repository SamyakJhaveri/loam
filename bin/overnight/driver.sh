#!/usr/bin/env bash
# Overnight driver (jhaveris): one fresh headless Opus call per Loam factory PR, as protocol.md says.
# Start: tmux new -d -s loam-night "bash -lc ~/loam/bin/overnight/driver.sh" ; stop: tmux kill-session -t loam-night,
# which ends the running call too: the driver's hangup, interrupt, terminate and exit traps end the call's session.
# The driver, its protocol and settings live in this directory and change only through a PR (#476); a call's
# settings deny it any write here. Run state stays in O, outside the checkout bin/factory next pulls.
# Speed-up (30 Oct 2026, Samyak's go): a free gh poll every 60 s starts a paid call only when a factory PR has no
# outcome line; a call is ended 120 s after it writes its outcome line, since a finished `claude -p` can hang on a
# pending wakeup; a merge launches the next ticket at once, under the lock the cron line takes.
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd) || exit 1
O=~/.local/state/loam/overnight
LOCK=~/.local/state/loam-factory/next.lock
cd ~/loam || exit 1
mkdir -p "$O" && touch "$O/log.md" "$O/followups.md"
stamp() { date -u +%FT%TZ; }
# The call runs in a session of its own (run below), so a closed terminal does not reach it: end_call TERMs its group,
# then KILLs it 10 s later. The pid is kept in O/call.pid while the call runs, so a driver that died without its traps
# leaves a record the next driver uses to end that call before it starts its own, and two calls never review one PR.
call=""
end_call() { local c=$1 i
  case $c in '' | *[!0-9]* | 0 | 1) return 0 ;; esac
  kill -TERM -- -"$c" 2> /dev/null || kill -TERM "$c" 2> /dev/null || return 0
  for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 -- -"$c" 2> /dev/null || kill -0 "$c" 2> /dev/null || return 0; sleep 1; done
  kill -KILL -- -"$c" 2> /dev/null || kill -KILL "$c" 2> /dev/null
}
trap 'end_call "$call"; rm -f "$O/call.pid"' EXIT
trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
# A call left by a driver that died: ended only while that pid still leads its own group and runs a driver call
# (the watchdog's pattern), so a reused pid is never touched.
if c=$(cat "$O/call.pid" 2> /dev/null) && [ "$(ps -o pgid= -p "$c" 2> /dev/null | tr -d ' ')" = "$c" ] \
  && ps -ww -o args= -p "$c" 2> /dev/null | grep -q 'claude -p .*overnight/protocol.md'; then
  echo "$(stamp) ended call $c left by an earlier driver" >> "$O/driver.log"; end_call "$c"
fi
rm -f "$O/call.pid"
# Free Loam's slot after a PR's outcome line: next counts a pr-opened run as holding it while ~/loam-<issue> exists
# (bin/factory:1858-1861), and the call's sandbox cannot remove that worktree. Only a run still at pr-opened is touched.
reap() { local wt n d; for wt in "$HOME"/loam-[0-9]*; do
  [ -d "$wt" ] || continue; n=${wt##*-}; d=$(ls -dt ~/.local/state/loam-factory/runs/"$n"/*/ 2>/dev/null | head -1)
  [ -n "$d" ] && [ "$(cat "$d/status" 2>/dev/null)" = pr-opened ] && grep -Eq "^outcome issue $n: (merged|left open)" "$O/log.md" \
    && git -C ~/loam worktree remove --force "$wt" && echo "$(stamp) removed $wt" >> "$O/driver.log" && freed=1
done; }
# 0 when an open PR from a factory/<issue> branch has no outcome line for its issue yet.
pending() { local list n
  list=$(gh pr list --repo SamyakJhaveri/loam --state open --json headRefName \
    --jq '.[].headRefName | select(test("^factory/[0-9]+$")) | ltrimstr("factory/")' 2>> "$O/driver.log") \
    || { echo "$(stamp) gh pr list failed" >> "$O/driver.log"; return 1; }
  for n in $list; do grep -Eq "^outcome issue $n: (merged|left open)" "$O/log.md" || return 0; done
  [ -s "$O/revisit.txt" ] && return 0   # a PR Samyak answered (protocol: Revisits)
  return 1
}
# The cron line's command; flock -n skips when cron's next holds the lock, -o keeps the launched run from holding it.
launch_next() {
  echo "$(stamp) slot freed: next" >> "$O/driver.log"
  FACTORY_DAILY_BUDGET_USD=1000000 FACTORY_MAX_PARALLEL=2 flock -n -o "$LOCK" bin/factory next \
    >> ~/.local/state/loam-factory/next.log 2>&1
}
# One call in a session of its own, so its whole group can be ended once its outcome line is in log.md.
# JSON output (31 Oct): the call's reply text still goes to driver.log, its cost to costs.tsv; a call ended after
# its outcome line may never print its JSON, so its cost is logged as unknown. On a usage-limit reply the driver
# switches to the next stored account (bin/claude-account, as bin/factory limit_switch does) and the loop retries.
run() { local pid done_at="" out cost to
  mkdir -p "$O/calls"; out="$O/calls/$(date -u +%Y%m%dT%H%M%SZ).json"; limited=0
  setsid env CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_SONNET_MODEL=claude-opus-5-5 \
    claude -p --model claude-opus-5-5 --effort high --permission-mode bypassPermissions --settings "$D/settings.json" --max-turns 400 --output-format json "$1" \
    < /dev/null > "$out" 2>> "$O/driver.log" &
  pid=$!; call=$pid; echo "$pid" > "$O/call.pid"
  while kill -0 "$pid" 2> /dev/null; do
    sleep 15 & wait $!   # in the background, so a signal's trap runs at once
    [ -z "$done_at" ] && tail -n +"$((before + 1))" "$O/log.md" | grep -q '^outcome issue ' && done_at=$SECONDS
    if [ -n "$done_at" ] && [ $((SECONDS - done_at)) -ge 120 ]; then
      echo "$(stamp) ended call $pid 120 s after its outcome line" >> "$O/driver.log"
      end_call "$pid"
      break
    fi
  done
  wait "$pid" 2> /dev/null; call=""; rm -f "$O/call.pid"
  jq -r '.result // empty' "$out" >> "$O/driver.log" 2> /dev/null
  cost=$(jq -r '.total_cost_usd // empty' "$out" 2> /dev/null)
  echo "$(stamp) call $(basename "$out" .json) cost_usd=${cost:-unknown} turns=$(jq -r '.num_turns // "?"' "$out" 2> /dev/null)" >> "$O/driver.log"
  printf '%s\t%s\t%s\n' "$(stamp)" "${cost:-unknown}" "$(basename "$out" .json)" >> "$O/costs.tsv"
  if jq -e '.is_error == true' "$out" > /dev/null 2>&1 && jq -r '.result // ""' "$out" | grep -qiE '(hit|reached) your .*limit'; then
    if to=$(~/loam/bin/claude-account other 2> /dev/null) && ~/loam/bin/claude-account use "$to" 2> /dev/null; then
      echo "$(stamp) usage limit: switched account to $to" >> "$O/driver.log"; limited=1
    else
      echo "$(stamp) usage limit and no other account to switch to" >> "$O/driver.log"
    fi
  fi
}
reported=""; limited=0
while :; do
  today=$(TZ=America/Los_Angeles date +%F)
  if [ "$(TZ=America/Los_Angeles date +%H)" = 07 ] && [ "$reported" != "$today" ]; then
    before=$(wc -l < "$O/log.md")
    run "Read $D/protocol.md and write the Morning report it describes, then stop."; reported=$today
  fi
  pending || { sleep 60; continue; }
  # Build the next ticket while this PR is reviewed (Samyak, 31 Oct): MAX_PARALLEL=2 lets next launch one beside the
  # PR under review; with a second PR already open it launches nothing.
  launch_next
  before=$(wc -l < "$O/log.md")
  run "Read $D/protocol.md and process one pull request as it says."
  freed=0; reap
  [ "$freed" = 1 ] && launch_next
  # A call that wrote nothing, or found nothing to do, waits 10 minutes, so a PR the protocol will not pick
  # cannot start a paid call every minute.
  if [ "$limited" = 1 ]; then sleep 5
  elif [ "$(wc -l < "$O/log.md")" = "$before" ] || tail -n 1 "$O/log.md" | grep -q '^idle'; then sleep 600; else sleep 60; fi
done
