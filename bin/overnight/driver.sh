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
P=~/.local/state/loam-driver   # the driver's own: it holds the grader window, which the call reads and cannot write
LOCK=~/.local/state/loam-factory/next.lock
cd ~/loam || exit 1
# The call's sandbox (settings.json allowWrite) opens only paths that exist when each of its commands starts.
mkdir -p "$O" ~/.local/state/loam/worktrees && mkdir -p -m 700 "$P" \
  && touch "$O/log.md" "$O/followups.md" ~/.local/state/loam/alerts.jsonl
stamp() { date -u +%FT%TZ; }
# REAP runs its argv as its one child. It is a child subreaper (prctl PR_SET_CHILD_SUBREAPER, 36, by syscall number:
# 157 on x86_64, 167 on aarch64), as in bin/factory call_start, so every process the child leaves, in any session, is
# reparented to it. When the child exits or REAP gets TERM, INT or HUP, it TERMs every process left (and its own group,
# under WRAP), KILLs them 5 s later, and exits with the child's status; with $sole set, 120 instead when any process the
# child started was still there, or ended within the same 0.1 s poll, when the child exited.
REAP='$nr = {x86_64 => 157, aarch64 => 167}->{(POSIX::uname())[4]} or die "no prctl number for this CPU\n";
  syscall($nr, 36, 1, 0, 0, 0) == 0 or die "prctl PR_SET_CHILD_SUBREAPER: $!\n";
  defined($kid = fork) or die "fork: $!\n";
  unless ($kid) { exec { $ARGV[0] } @ARGV; print STDERR "exec $ARGV[0]: $!\n"; POSIX::_exit(127) }
  $SIG{$_} = sub { $sig = 1 } for qw(TERM INT HUP);
  sub kids { my @k; for (glob "/proc/[0-9]*/stat") { open(my $h, "<", $_) or next; my $s = <$h> // next;
      my ($p, $z, $pp, $pg) = $s =~ /^(\d+) .*\) (\S) (\d+) (\d+)/s or next;
      push @k, $p if $p != $$ && $z ne "Z" && ($pp == $$ || $pg == $$) } @k }
  for (;;) {
    $o = 0; while (($p = waitpid(-1, WNOHANG)) > 0) { if ($p == $kid) { $st = $? } else { $o = 1 } }
    if (defined $st || $sig) { $end //= time + 5; @p = kids(); $left ||= $o || @p; last unless @p;
      if (time < $end) { kill "TERM", grep { !$seen{$_}++ } @p } elsif (time < $end + 5) { kill "KILL", @p } else { last } }
    sleep 0.1 }
  $left ||= waitpid(-1, WNOHANG) > 0;
  exit($sole && $left && !$sig ? 120 : !defined $st ? 137 : $st & 127 ? 128 + ($st & 127) : $st >> 8)'
# Each call runs under WRAP: REAP in a session of its own (its pid leads the group end_call signals), so a closed
# terminal does not reach it, and a tool shell in a session of its own (#434) is reparented to it once claude exits.
WRAP='POSIX::setsid() == $$ or die "setsid: $!\n";'"$REAP"
# end_call TERMs the wrapper's group, then KILLs it 10 s later.
end_call() { local c=$1 i
  case $c in '' | *[!0-9]* | 0 | 1) return 0 ;; esac
  kill -TERM -- -"$c" 2> /dev/null || kill -TERM "$c" 2> /dev/null || return 0
  for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 -- -"$c" 2> /dev/null || kill -0 "$c" 2> /dev/null || return 0; sleep 1; done
  kill -KILL -- -"$c" 2> /dev/null || kill -KILL "$c" 2> /dev/null
}
# The protocol's one read of DistBench (Grader window), run here because the call's settings deny it gh on DistBench:
# grader-window.txt holds the read's UTC time, gh's exit status (124 on a timeout, 120 if a process gh started was
# still there when gh exited) and, only after exit 0, one open DistBench grader-fix PR number per line. It lives in P,
# which the call can read but not write, so the call cannot forge or swap it; written to a temp file there and renamed
# into place, so a call never reads half of it (a failed rename removes the window).
# gh runs under REAP with $sole set. REAP stays in the driver's process group, as timeout --foreground does (plain
# timeout makes a group of its own), so killing the driver's group ends the read too. gh's stdout is shared with every
# process gh starts, so what one writes after gh exits is not gh's answer: REAP ends them all, and a read gh may have
# been outlived by fails (120; a process that ended within REAP's 0.1 s poll of gh's exit counts too, so it fails
# safe). With nothing left holding gh's stdout once REAP exits, the read is a plain $(...), with no file the call
# could replace; timeout's KILL (-k 15) comes after REAP's own TERM and KILL (10 s).
to=(); command -v timeout > /dev/null && to=(timeout --foreground -k 15 60)
grader_window() { local at out rc
  at=$(stamp)
  out=$(${to[@]+"${to[@]}"} perl -MPOSIX -MTime::HiRes=time,sleep -e '$sole = 1;' -e "$REAP" gh pr list -R SamyakJhaveri/distbench --state open --limit 100 --json number,title,files --jq '.[] | select((.title | test("grader|regrade"; "i")) or any(.files[].path; test("(^|/)grader\\.py$|regrade"; "i"))) | .number' 2>> "$O/driver.log")
  rc=$?
  [ "$rc" -eq 0 ] || { echo "$(stamp) grader-window read failed: exit $rc" >> "$O/driver.log"; out=; }   # not an answer
  { echo "read_at $at"; echo "exit $rc"; [ -z "$out" ] || printf '%s\n' "$out"; } | perl -MFile::Temp=tempfile -e '
    ($h, $t) = tempfile("grader-window.XXXXXX", DIR => $ARGV[0]); print $h <STDIN>; close $h or die "close: $!\n";
    rename($t, "$ARGV[0]/grader-window.txt") or do { unlink $t; die "rename: $!\n" }' "$P" 2>> "$O/driver.log" \
    || rm -f "$P/grader-window.txt"   # no stale clear window
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
# 0 when an open PR from a factory/<issue> branch has no outcome line for its issue yet. Only PRs Samyak opened from
# this repo's own branches count: Loam is public and gh gives a fork's branch without its owner, so a stranger's
# factory/<n> PR would otherwise start a call (and its outcome line could free the real PR's slot).
pending() { local list n
  list=$(gh pr list --repo SamyakJhaveri/loam --state open --limit 200 --json headRefName,isCrossRepository,author \
    --jq '.[] | select(.isCrossRepository == false and .author.login == "SamyakJhaveri") | .headRefName
      | select(test("^factory/[0-9]+$")) | ltrimstr("factory/")' 2>> "$O/driver.log") \
    || { echo "$(stamp) gh pr list failed" >> "$O/driver.log"; return 1; }
  for n in $list; do grep -Eq "^outcome issue $n: (merged|left open)" "$O/log.md" || return 0; done
  [ -s "$O/revisit.txt" ] && return 0   # a PR Samyak answered (protocol: Revisits)
  return 1
}
# The cron line's command; flock -n skips when cron's next holds the lock, -o keeps the launched run from holding it.
launch_next() {
  echo "$(stamp) slot freed: next" >> "$O/driver.log"
  FACTORY_MAX_PARALLEL=2 flock -n -o "$LOCK" bin/factory next \
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
# One call under WRAP, through claude-account exec, which execs claude with the token of the account recorded below in
# its env (one read of `active` gives both, so a switch in between cannot record a for a call on b; the settings files
# hold no token) and keeps the pid; the wrapper's args still hold `claude -p ... overnight/protocol.md`,
# which the adopt check below and watchdog.sh match. O/call.pid holds "pid before out account" while it runs (account:
# the one active just before the call starts; left out when none is): a stopped driver leaves the call to finish, and
# the next driver adopts it with the same rules (below), so a restart neither kills a review, nor starts a second call
# on the same PR, nor judges the call's usage limit by the account active now.
# CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 (#679): headless claude otherwise stops the lead's background agents 10 min
# after its last turn; 0 waits for them.
run() { local pid out acct
  mkdir -p "$O/calls"; out="$O/calls/$(date -u +%Y%m%dT%H%M%SZ).json"; limited=0
  grader_window
  acct=$(active_account)
  env CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0 CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_HAIKU_MODEL=claude-opus-5-5 ANTHROPIC_DEFAULT_SONNET_MODEL=claude-opus-5-5 \
    perl -MPOSIX -MTime::HiRes=time,sleep -e "$WRAP" "$HOME/loam/bin/claude-account" exec --as "$acct" \
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
