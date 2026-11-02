#!/usr/bin/env bash
# Overnight watchdog (jhaveris cron, every 10 minutes): restart a dead driver and alert, at most once per 30 minutes;
# alert once when a driver call runs over 3 hours. A STOP file in O stands it down, so a deliberate stop stays stopped:
#   touch ~/.local/state/loam/overnight/STOP && tmux kill-session -t loam-night
# It restarts the repo's driver (#476): cron runs ~/loam/bin/overnight/watchdog.sh, and state stays in O.
set -u
O=~/.local/state/loam/overnight
DRIVER=~/loam/bin/overnight/driver.sh
[ -f "$O/STOP" ] && exit 0
alert() { ~/loam/bin/alert --level fail --source overnight-watchdog --project loam "$1"; }
if ! tmux has-session -t loam-night 2> /dev/null; then
  if [ -n "$(find "$O/restarted" -mmin -30 2> /dev/null)" ]; then
    [ -f "$O/gave-up" ] || { touch "$O/gave-up"; alert "The overnight driver died again within 30 minutes of a restart; the watchdog stopped restarting it. See $O/driver.log."; }
  else
    rm -f "$O/gave-up"; touch "$O/restarted"
    tmux new -d -s loam-night "bash -lc $DRIVER"
    alert "The overnight driver had stopped; the watchdog restarted it. See $O/driver.log."
  fi
fi
pid=$(pgrep -of "claude -p .*overnight/protocol.md")
if [ -n "$pid" ] && [ "$(ps -o etimes= -p "$pid" | tr -d ' ')" -gt 10800 ] && [ ! -f "$O/stuck-$pid" ]; then
  touch "$O/stuck-$pid"
  alert "An overnight driver call (pid $pid) has run over 3 hours and may be stuck. See $O/driver.log."
fi
