#!/usr/bin/env bash
# Overnight driver (jhaveris): one fresh headless Opus call per Loam factory PR, as protocol.md says.
# Start: tmux new -d -s loam-night "bash -lc ~/loam/bin/overnight/driver.sh" ; stop: tmux kill-session -t loam-night.
# A stopped driver leaves its call to finish, and the next driver adopts it (below); to end a call on purpose, touch STOP
# first, then pkill -TERM -s <pid in O/call.pid>.
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
# Each call runs under WRAP, a perl process in a session of its own (its pid leads the group end_call signals), so a
# closed terminal does not reach it. As in bin/factory call_start, it is a child subreaper (prctl PR_SET_CHILD_SUBREAPER,
# 36, by syscall number: 157 on x86_64, 167 on aarch64), so a tool shell in a session of its own (#434) is reparented
# to it once claude exits. It execs claude with its argv unchanged; when claude exits or the wrapper gets TERM, INT or
# HUP, it TERMs claude's group and every child, KILLs them 5 s later, and exits with claude's status.
WRAP='POSIX::setsid() == $$ or die "setsid: $!\n";
  $nr = {x86_64 => 157, aarch64 => 167}->{(POSIX::uname())[4]} or die "no prctl number for this CPU\n";
  syscall($nr, 36, 1, 0, 0, 0) == 0 or die "prctl PR_SET_CHILD_SUBREAPER: $!\n";
  defined($kid = fork) or die "fork: $!\n";
  unless ($kid) { exec { $ARGV[0] } @ARGV; print STDERR "exec $ARGV[0]: $!\n"; POSIX::_exit(127) }
  $SIG{$_} = sub { $sig = 1 } for qw(TERM INT HUP);
  sub kids { my @k; for (glob "/proc/[0-9]*/stat") { open(my $h, "<", $_) or next; my $s = <$h> // next;
      my ($p, $z, $pp, $pg) = $s =~ /^(\d+) .*\) (\S) (\d+) (\d+)/s or next;
      push @k, $p if $p != $$ && $z ne "Z" && ($pp == $$ || $pg == $$) } @k }
  for (;;) {
    while (($p = waitpid(-1, WNOHANG)) > 0) { $st = $? if $p == $kid }
    if (defined $st || $sig) { $end //= time + 5; @p = kids(); last unless @p;
      if (time < $end) { kill "TERM", grep { !$seen{$_}++ } @p } elsif (time < $end + 5) { kill "KILL", @p } else { last } }
    sleep 0.1 }
  exit(!defined $st ? 137 : $st & 127 ? 128 + ($st & 127) : $st >> 8)'
# end_call TERMs the wrapper's group, then KILLs it 10 s later.
end_call() { local c=$1 i
  case $c in '' | *[!0-9]* | 0 | 1) return 0 ;; esac
  kill -TERM -- -"$c" 2> /dev/null || kill -TERM "$c" 2> /dev/null || return 0
  for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 -- -"$c" 2> /dev/null || kill -0 "$c" 2> /dev/null || return 0; sleep 1; done
  kill -KILL -- -"$c" 2> /dev/null || kill -KILL "$c" 2> /dev/null
}
# Watch a call until it exits, polling every 15 s; end it 8 polls (120 s) after an outcome line appears in log.md past
# line $2, since a finished `claude -p` can hang on a pending wakeup. It polls kill -0, since an adopted call is not
# this driver's child.
watch() { local pid=$1 before=$2 polls=-1
  while kill -0 "$pid" 2> /dev/null; do
    sleep 15
    [ "$polls" -lt 0 ] && tail -n +"$((before + 1))" "$O/log.md" | grep -q '^outcome issue ' && polls=0
    [ "$polls" -ge 0 ] && polls=$((polls + 1))
    if [ "$polls" -gt 8 ]; then
      echo "$(stamp) ended call $pid 120 s after its outcome line" >> "$O/driver.log"
      end_call "$pid"
      break
    fi
  done
}
# Free Loam's slot after a PR's outcome line, or once the factory marked its PR closed (pr-closed, written by
# pr_closed_events, so a call ended between its merge and its outcome line strands nothing): next counts a pr-opened
# run as holding the slot while ~/loam-<issue> exists (bin/factory:2975-2993), and the call's sandbox cannot remove
# that worktree. Only a run still at pr-opened is touched.
reap() { local wt n d; for wt in "$HOME"/loam-[0-9]*; do
  [ -d "$wt" ] || continue; n=${wt##*-}; d=$(ls -dt ~/.local/state/loam-factory/runs/"$n"/*/ 2>/dev/null | head -1)
  [ -n "$d" ] && [ "$(cat "$d/status" 2>/dev/null)" = pr-opened ] \
    && { grep -Eq "^outcome issue $n: (merged|left open)" "$O/log.md" || [ -e "$d/pr-closed" ]; } \
    && git -C ~/loam worktree remove --force "$wt" && echo "$(stamp) removed $wt" >> "$O/driver.log" && freed=1
done; }
# 0 when an open PR from a factory/<issue> branch has no outcome line for its issue yet.
pending() { local list n
  list=$(gh pr list --repo SamyakJhaveri/loam --state open --limit 200 --json headRefName \
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
# JSON output (31 Oct): the call's reply text still goes to driver.log, its cost to costs.tsv; a call ended after
# its outcome line may never print its JSON, so its cost is logged as unknown. On a usage-limit reply the driver
# switches to the next stored account (bin/claude-account, as bin/factory limit_switch does) and the loop retries.
account() { local out=$1 cost to
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
# One call under WRAP. O/call.pid holds "pid before out" while it runs: a stopped driver leaves the call to finish,
# and the next driver adopts it with the same rules (below), so a restart neither kills a review nor starts a second
# call on the same PR.
run() { local pid out
  mkdir -p "$O/calls"; out="$O/calls/$(date -u +%Y%m%dT%H%M%SZ).json"; limited=0
  env CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_SONNET_MODEL=claude-opus-5-5 \
    perl -MPOSIX -MTime::HiRes=time,sleep -e "$WRAP" \
    claude -p --model claude-opus-5-5 --effort high --permission-mode bypassPermissions --settings "$D/settings.json" --max-turns 400 --output-format json "$1" \
    < /dev/null > "$out" 2>> "$O/driver.log" &
  pid=$!; echo "$pid $before $out" > "$O/call.pid"
  watch "$pid" "$before"
  wait "$pid" 2> /dev/null; rm -f "$O/call.pid"
  account "$out"
}
reported=""; limited=0
# A call left by an earlier driver is adopted only while its pid still leads its own group and runs a driver call
# (the watchdog's pattern), so a reused pid is never touched; the loop starts no call of its own until it ends. Only a
# full "pid before out" record is adopted: without its log line count an outcome written before the restart is unseen.
if read -r c b f < "$O/call.pid" 2> /dev/null && [ -n "$f" ] && [ "$(ps -o pgid= -p "$c" 2> /dev/null | tr -d ' ')" = "$c" ] \
  && ps -ww -o args= -p "$c" 2> /dev/null | grep -q 'claude -p .*overnight/protocol.md'; then
  echo "$(stamp) adopted call $c left by an earlier driver" >> "$O/driver.log"
  limited=0; watch "$c" "$b"; [ -f "$f" ] && account "$f"
fi
rm -f "$O/call.pid"
while :; do
  freed=0; reap
  [ "$freed" = 1 ] && launch_next
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
