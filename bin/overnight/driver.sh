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
# The protocol's one read of DistBench (Grader window), run here because the call's settings deny it gh on DistBench:
# grader-window.txt holds the read's UTC time, gh's exit status (124 on a timeout) and one open DistBench grader-fix
# PR number per line. Written through a fresh mktemp file (never a fixed name the call could link elsewhere) and
# moved with mv -T over the name itself, so a call never reads half of it and no planted link redirects the write.
to=(); command -v timeout > /dev/null && to=(timeout 60)
grader_window() { local at out rc tmp
  at=$(stamp)
  out=$(${to[@]+"${to[@]}"} gh pr list -R SamyakJhaveri/distbench --state open --limit 100 --json number,title,files --jq '.[] | select((.title | test("grader|regrade"; "i")) or any(.files[].path; test("(^|/)grader\\.py$|regrade"; "i"))) | .number' 2>> "$O/driver.log")
  rc=$?
  [ "$rc" -eq 0 ] || echo "$(stamp) grader-window read failed: exit $rc" >> "$O/driver.log"
  tmp=$(mktemp "$O/grader-window.XXXXXX") || { rm -f "$O/grader-window.txt"; return; }   # no stale clear window
  { echo "read_at $at"; echo "exit $rc"; [ -z "$out" ] || printf '%s\n' "$out"; } > "$tmp" \
    && mv -fT "$tmp" "$O/grader-window.txt"
}
# Watch a call with kill -0, since an adopted call is not our child; a zombie has ended (kill -0 still finds it while
# an ancestor that took the orphan has not reaped it, as the factory's mutation sweep does). Refresh the grader
# window until an outcome appears past line $2, after the call's merge gate. Then allow 8 more 15 s polls before
# ending a hung call.
watch() { local pid=$1 before=$2 polls=-1
  while kill -0 "$pid" 2> /dev/null && ! ps -o stat= -p "$pid" 2> /dev/null | grep -q '^Z'; do
    sleep 15
    [ "$polls" -lt 0 ] && tail -n +"$((before + 1))" "$O/log.md" | grep -q '^outcome issue ' \
      && polls=0
    [ "$polls" -lt 0 ] && grader_window
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
# run as holding the slot while ~/loam-<issue> exists (cmd_next in bin/factory: "a pr-opened run whose ticket
# worktree still exists"), and the call's sandbox cannot remove
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
  FACTORY_DAILY_BUDGET_USD=1000000 FACTORY_GRADER_BUDGET_USD=1000000 FACTORY_MAX_PARALLEL=2 flock -n -o "$LOCK" bin/factory next \
    >> ~/.local/state/loam-factory/next.log 2>&1
}
# JSON output (31 Oct): the call's reply text still goes to driver.log, its cost to costs.tsv; a call ended after
# its outcome line may never print its JSON, so its cost is logged as unknown. On a usage-limit reply the driver
# switches only through `bin/claude-account switch <account the call ran on>` (#600), the host-wide switch under the
# factory's lock and cooldown, so a switch another caller made since the call started is kept, never undone: exit 0
# (switched, or already switched by another caller) retries at once, exit 3 (another switch under 300 s ago) keeps the
# normal pacing. A call with no recorded account switches nothing.
account() { local out=$1 from=${2-} cost
  jq -r '.result // empty' "$out" >> "$O/driver.log" 2> /dev/null
  cost=$(jq -r '.total_cost_usd // empty' "$out" 2> /dev/null)
  echo "$(stamp) call $(basename "$out" .json) cost_usd=${cost:-unknown} turns=$(jq -r '.num_turns // "?"' "$out" 2> /dev/null)" >> "$O/driver.log"
  printf '%s\t%s\t%s\n' "$(stamp)" "${cost:-unknown}" "$(basename "$out" .json)" >> "$O/costs.tsv"
  if jq -e '.is_error == true' "$out" > /dev/null 2>&1 && jq -r '.result // ""' "$out" | grep -qiE '(hit|reached) your .*limit'; then
    if [ -z "$from" ]; then
      echo "$(stamp) usage limit on a call with no recorded account: switched nothing" >> "$O/driver.log"; return
    fi
    ~/loam/bin/claude-account switch "$from" 2>> "$O/driver.log"
    case $? in
      0) echo "$(stamp) usage limit on account $from: active account now $(active_account); retrying" >> "$O/driver.log"; limited=1 ;;
      3) echo "$(stamp) usage limit on account $from: another caller switched under 300 s ago; switched nothing" >> "$O/driver.log" ;;
      *) echo "$(stamp) usage limit and no other account to switch to" >> "$O/driver.log" ;;
    esac
  fi
}
# The active account name `bin/claude-account status` prints; empty when it names none.
active_account() { local a
  a=$(~/loam/bin/claude-account status 2> /dev/null) || a=""
  a=${a#active: }; a=${a%%;*}
  [ "$a" = none ] || printf '%s\n' "$a"
}
# One call under WRAP. O/call.pid holds "pid before out account" while it runs (account: the one active just before
# the call starts; left out when none is): a stopped driver leaves the call to finish, and the next driver adopts it
# with the same rules (below), so a restart neither kills a review, nor starts a second call on the same PR, nor
# judges the call's usage limit by the account active now.
run() { local pid out acct
  mkdir -p "$O/calls"; out="$O/calls/$(date -u +%Y%m%dT%H%M%SZ).json"; limited=0
  grader_window
  acct=$(active_account)
  env CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_SONNET_MODEL=claude-opus-5-5 \
    perl -MPOSIX -MTime::HiRes=time,sleep -e "$WRAP" \
    claude -p --model claude-opus-5-5 --effort high --permission-mode bypassPermissions --settings "$D/settings.json" --max-turns 400 --output-format json "$1" \
    < /dev/null > "$out" 2>> "$O/driver.log" &
  pid=$!; echo "$pid $before $out${acct:+ $acct}" > "$O/call.pid"
  watch "$pid" "$before"
  wait "$pid" 2> /dev/null; rm -f "$O/call.pid"
  account "$out" "$acct"
}
# After a PR call, its own or adopted: free a merged PR's slot at once, then pace. A call that wrote nothing, or found
# nothing to do, waits 10 minutes, so a PR the protocol will not pick cannot start a paid call every minute.
after_call() {
  freed=0; reap
  [ "$freed" = 1 ] && launch_next
  if [ "$limited" = 1 ]; then sleep 5
  elif [ "$(wc -l < "$O/log.md")" = "$before" ] || tail -n 1 "$O/log.md" | grep -q '^idle'; then sleep 600; else sleep 60; fi
}
reported=""; limited=0
# A call left by an earlier driver is adopted only while its pid still leads its own group and runs a driver call
# (the watchdog's pattern), so a reused pid is never touched; the loop starts no call of its own until it ends, and
# paces after it as after its own. Only a record with at least "pid before out" is adopted: without its log line count
# an outcome written before the restart is unseen. A record from a driver before #615 has no account, so that call's
# usage limit switches nothing.
if read -r c b f a < "$O/call.pid" 2> /dev/null && [ -n "$f" ] && [ "$(ps -o pgid= -p "$c" 2> /dev/null | tr -d ' ')" = "$c" ] \
  && ps -ww -o args= -p "$c" 2> /dev/null | grep -q 'claude -p .*overnight/protocol.md'; then
  echo "$(stamp) adopted call $c left by an earlier driver" >> "$O/driver.log"
  limited=0; before=$b; watch "$c" "$b"; [ -f "$f" ] && account "$f" "$a"
  after_call
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
  after_call
done
