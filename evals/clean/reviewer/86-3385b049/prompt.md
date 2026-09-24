## Ticket

~~~~~~~~~~~~ evidence
Brief:
Add bin/factory next on a ten-minute runner timer so the next unblocked ready-for-agent ticket launches after each merge with no operator command.
Where: bin/factory (next, cmd_status), bin/factory.d/ (the timer unit), docs/factory/LOOP.md (Commands; Status and the manager)
Done means: after a merge the next run's ledger start line is within ten minutes with zero operator commands and removing the ready-for-agent label parks the ticket (merge checklist, #38); FACTORY_STOP at the runs root pauses the timer; `bin/factory status` has a `clean` column per D09 Option A.
Out of scope: MAX_PARALLEL above 1; any grader change.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: #56 and #43, both closed (#43 closed 2026-09-11 with Option A; F20 and F15 were the two clean runs, read by hand)

## Goal and why
`bin/factory next` on a ten-minute runner timer, as specified in `LOOP.md` Commands and Status and the manager (`ROADMAP.md` F9).
After this lands the operator action count after a PR opens is one: the merge.
The timer fast-forwards the runner's main checkout on its own (ff-only, only with a clean tree and no live run), which today only the manager session does; without it every loop-improving merge after F9 would never reach the runner's supervisor, since `freeze` copies `bin/factory` from that checkout. Samyak may strike the pull sentence and the `next-pulls` check, which makes the zero-operator-commands claim false for loop tickets.
The ticket also carries the `clean` column D09 asked for (Option A, 2026-09-11): clean means the run reached `pr-opened` with zero grader-fail rounds and no other exit on the way; a hand fix after `pr-opened` does not change it. Read from the run directory, that is: `status` is `pr-opened`, the only `EXIT` line in `factory.log` is `pr-opened`, and every `round-<k>.fixes` for k at least 1 is empty (a grader that fails or blocks queues fixes there). Against the 2026-09-11 runs this reads F20 (#81) and F15 (`runs/76/0ebf222a`) as clean and F19, F18, and F21 (`ticket-defect` on the way) as not, which is the reading Samyak gave.

## Do not touch
The standing list. Except: bin/factory (`next`, `cmd_status`, `usage`), bin/factory.d/ (this ticket adds the timer unit), docs/factory/LOOP.md (Commands; Status and the manager).

## Out of scope
- `MAX_PARALLEL` above 1
- any grader prompt or schema change
- notification changes

## Approach
`next` reads the runs root from `FACTORY_RUNS_ROOT` (default `~/.local/state/loam-factory/runs`) and, in this order: if `FACTORY_STOP` exists there, prints `paused` and exits 0; if the count of run directories whose `status` reads `running` or `waiting-limit` is at least `MAX_PARALLEL` (`FACTORY_MAX_PARALLEL` in the environment, default 1), prints `nothing to launch` and exits 0; then fast-forwards the checkout it runs from (`git fetch -q origin && git merge --ff-only origin/main`) when `git status --porcelain` is empty, else logs `refused pull: dirty checkout` and continues; then lists open `ready-for-agent` issues with no assignee through `gh api` and keeps those whose `issue_dependencies_summary.blocked_by` is 0, lowest issue number first. `--dry-run` prints `would launch #N`, `nothing to launch`, or `paused` and never launches or pulls, so a check can run it from inside a worktree. Otherwise it launches `bin/factory run <N>` in a detached tmux session named `loam-<N>`, output appended to `<runs root>/<N>.tmux.log` (the launch shape the manager records use). The timer: `next --install` writes a crontab line `*/10 * * * * bash -lc 'cd ~/Desktop/loam && bin/factory next'` from a template under `bin/factory.d/`; a systemd user timer with `OnUnitActiveSec=10min`, `OnActiveSec=1min`, `ExecStart=/bin/bash -lc '...'`, and `loginctl enable-linger` is the alternative (a user unit gets no login environment and stops with the last ssh session unless lingering is on); the check accepts either. No check runs the timer; the merge checklist observes it once (#38).

The `clean` column: `cmd_status` prints it after `first-failing-grader` as `yes`, `no`, or `-` (a run not at `pr-opened`), computed as the Goal defines; `docs/factory/LOOP.md` (Status and the manager) names the column and its three values in one sentence, and the `MAX_PARALLEL` sentence under Commands reads "raise it after two clean single runs, as `status` reports them".

Runs on jhaveris under `bin/factory run` (`LOOP.md` Commands), launched with `bin/runner 'bin/factory run <this issue>'` until the F9 timer exists; the merge is the one human action.

## Done checks
```done-checks
out=$(bin/factory next --help 2>&1); grep -q "usage: bin/factory next" <<<"$out" && pass next-exists || fail next-exists "bin/factory next prints no usage line"
grep -rEq '(OnUnitActiveSec=10min|\*/10 \* \* \* \*)' bin/factory.d/ 2>/dev/null && pass timer-ten-minutes || fail timer-ten-minutes "no timer definition under bin/factory.d/ with a ten-minute interval"
grep -Eq '^[^#]*ready-for-agent' bin/factory 2>/dev/null && grep -Eq '^[^#]*issue_dependencies_summary' bin/factory && pass frontier-query || fail frontier-query "next does not read the label and native blockers"
d=$(mktemp -d); touch "$d/FACTORY_STOP"; out=$(FACTORY_RUNS_ROOT="$d" bin/factory next --dry-run 2>&1); grep -q paused <<<"$out" && pass stop-pauses || fail stop-pauses "FACTORY_STOP at the runs root does not pause next"
out=$(FACTORY_RUNS_ROOT="$(mktemp -d)" bin/factory next --dry-run 2>&1); grep -Eq 'would launch|nothing to launch' <<<"$out" && pass next-dry-run || fail next-dry-run "next --dry-run does not report"
d=$(mktemp -d); mkdir -p "$d/9/x"; echo running > "$d/9/x/status"; out=$(FACTORY_RUNS_ROOT="$d" FACTORY_MAX_PARALLEL=1 bin/factory next --dry-run 2>&1); rm -r "$d"; grep -q 'nothing to launch' <<<"$out" && pass slot-full || fail slot-full "next launches past MAX_PARALLEL with a live run present"
grep -Eq '^[^#]*merge --ff-only origin/main' bin/factory && pass next-pulls || fail next-pulls "next does not fast-forward the checkout before launching"
d=$(mktemp -d "${TMPDIR:-/tmp}/f9s.XXXXXX"); for r in a/r1 b/r2 c/r3; do mkdir -p "$d/$r"; echo pr-opened > "$d/$r/status"; date -u +%s > "$d/$r/started"; : > "$d/$r/ledger.jsonl"; : > "$d/$r/round-1.checks"; : > "$d/$r/round-1.fixes"; done; echo 'x EXIT pr-opened (0): ok' > "$d/a/r1/factory.log"; printf 'x EXIT no-change (2): y\nx EXIT pr-opened (0): ok\n' > "$d/b/r2/factory.log"; echo 'x EXIT pr-opened (0): ok' > "$d/c/r3/factory.log"; echo '- fix' > "$d/c/r3/round-1.fixes"; out=$(FACTORY_RUNS_ROOT="$d" bin/factory status 2>/dev/null); rm -r "$d"; head -1 <<<"$out" | grep -qw clean && grep -E '^a ' <<<"$out" | grep -qw yes && grep -E '^b ' <<<"$out" | grep -qw no && grep -E '^c ' <<<"$out" | grep -qw no && pass clean-column || fail clean-column "status has no clean column, or misreads a clean run (a), a run with an earlier exit (b), or a run with queued fixes (c)"
grep -q 'a `clean` column' docs/factory/LOOP.md && pass loop-md-clean || fail loop-md-clean "LOOP.md does not name the clean column"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }   # under the Stop hook bin/check (minutes per stop) is left to the supervisor, which runs it once on green
```

## Merge checklist
- after this PR merges, `bin/runner 'git log -1 --format=%h'` shows the merged sha within ten minutes with no pull by hand, and the next run's ledger start line lands within ten minutes with zero operator commands; then remove `ready-for-agent` from the only frontier issue and confirm `bin/runner 'bin/factory next --dry-run'` prints `nothing to launch` (#38)
- `bin/runner 'crontab -l'` shows the line, or `bin/runner 'loginctl show-user $USER -p Linger'` prints `yes`
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: yes
effort: xhigh
size: large
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 60 turns

## Decisions
docs/factory/LOOP.md (Commands, Status and the manager), docs/factory/ROADMAP.md; decision ticket #43 (closed 2026-09-11, Option A) in .superpowers/factory/tickets/D09-clean-run.md and the record in .superpowers/factory/sessions/manager-2026-09-11-codex.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS next-exists
PASS timer-ten-minutes
PASS frontier-query
PASS stop-pauses
PASS next-dry-run
PASS slot-full
PASS next-pulls
PASS clean-column
PASS loop-md-clean
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Timer template path pinned: bin/factory.d/next.crontab holds the crontab line `*/10 * * * * bash -lc 'cd ~/Desktop/loam && bin/factory next'`; `next --install` reads that exact file (crontab only, systemd skipped per Approach's "the check accepts either").
Launch shape: `tmux new-session -d -s loam-<N>` running `bin/factory run <N>` with output appended to $RUNS_ROOT/<N>.tmux.log, guarded by `tmux has-session`; matches the Approach.
next order per Approach: FACTORY_STOP -> paused; live-run count (status running|waiting-limit) >= MAX_PARALLEL -> nothing to launch; ff-only pull of the run checkout (skipped under --dry-run, and only when the tree is clean, else log `refused pull: dirty checkout`); then the gh api frontier query.
Frontier query: gh api repos/<REPO>/issues?labels=ready-for-agent&state=open&assignee=none, keep .pull_request==null and .issue_dependencies_summary.blocked_by==0, lowest number first.
Departure from Approach (relaunch guard): next skips any issue that already has a run dir at status pr-opened. open_pr (bin/factory:1014) never removes the label or assigns the issue, so between pr-opened and merge the timer would relaunch the same ticket every 10 min into the same run dir, and main_loop (bin/factory:1076) makes a fresh paid worker call on resume. The guard keeps the Goal's "one action after a PR opens: the merge". A merged ticket is closed (Closes #N), so it drops out of the query anyway; the guard covers only the pr-opened-awaiting-merge window.
LOOP.md section note: the MAX_PARALLEL sentence the Approach calls "under Commands" is actually under "Parallel runs" (docs/factory/LOOP.md:169). exempt.txt covers the whole file, so editing it there is in scope; the "a `clean` column" sentence goes in "Status and the manager".
PLAN solo: next, cmd_status, and usage all live in bin/factory (one path), so the natural next-vs-clean split is structurally impossible under disjoint globs; the only disjoint carve-offs (timer template, LOOP.md) are under ten minutes and describe interfaces the code task fixes.
Implemented the round solo (no tasks/result.json). Commit 41181e1. All ten done-checks PASS (frozen checks.sh from the worktree root, LOAM_HOOK=1) and bin/check is green; worktree clean. unmet: none. abandoned: none.
Verified beyond the checks: the relaunch guard prints "nothing to launch" for an issue at pr-opened and the slot check does the same for a running one; --install is idempotent (three installs leave one cron line).
Frontier jq: dropped my earlier `// 0` fallback; the filter is now plain `.issue_dependencies_summary.blocked_by == 0` per the Approach. Fail-safe: if the field is ever absent the query launches nothing (visible at the merge-checklist sha check) rather than launching a blocked ticket. The live API shape could not be verified from the worktree (gh api is denied here), so it is a merge-checklist observation on the runner.
--install fix: installs only the cron line (grep -v '^#'), so the template comments do not accumulate on reinstall.
Guard scope is only pr-opened. A run ending stuck/no-change/ticket-defect/stopped-* leaves the issue labeled and unassigned, so once the timer is installed the timer relaunches it each tick, resuming at the last round for one paid worker call until MAX_ROUNDS or TICKET_BUDGET_USD, then exits stopped-cap. Bounded by the caps and parked by removing the label (LOOP.md); a broader guard would wrongly suppress the desirable stopped-environment retry. Ticket-level design, flagged for the diff reader.
refused pull goes through log() with LOG=/dev/null, i.e. stderr only (under cron: mail or nothing). A stray untracked file on the runner blocks every pull silently; the merge-checklist sha check is the only detector.
--- round 2 (codex-review blocking findings) ---
Finding 1 (gh swallow): the frontier query no longer hides gh failure. Empty `gh repo view`, or a nonzero `gh api`, prints `frontier query failed: <cause>` to stderr and returns 1 (cron mails it); only a successful, empty query still falls through to `nothing to launch` exit 0. `local repo ready num` stays on its own line so `if ! ready=$(...)` keeps the real exit code (a `local ready=$(...)` would mask it and reintroduce the swallow). Verified with failing gh shims: repo-view-fail and api-fail both give the message and exit 1; an empty-but-successful shim gives `nothing to launch` exit 0; the real child gh still prints `would launch #87`.
Finding 2 (ff-only swallow): the pull block is now an if/elif chain that logs `refused pull: git fetch origin failed` or `refused pull: not fast-forward` on the respective failure, alongside the existing `refused pull: dirty checkout`. A refused pull never aborts the launch (the run proceeds on the stale checkout with the cause on record), preserving the old `|| true` behaviour but with the cause visible.
Finding 3 (high, RUNS_ROOT missing): `mkdir -p "$RUNS_ROOT"` runs before `tmux new-session`, so a fresh install's `>> $RUNS_ROOT/<N>.tmux.log` redirection no longer fails before the run starts. `launched #N` now prints only when `tmux new-session` succeeds; on failure it prints `launch failed: ...` to stderr and returns 1.
FACTORY_MAX_PARALLEL: cmd_next now reads it (`max="${FACTORY_MAX_PARALLEL:-$MAX_PARALLEL}"`, default 1) for the slot count, matching the Approach and cmd_run's apply_caps. Not "MAX_PARALLEL above 1" (out of scope); that is raising the cap and multi-run orchestration, unchanged.
Comment rewrite: the stale "A gh failure ... yields no candidate, not an error" comment at the frontier step was corrected to describe the return-1-on-failure behaviour.
Round 2 result: all ten done-checks PASS from the worktree root (LOAM_HOOK unset, so bin/check ran and is green); worktree otherwise clean. unmet: none. abandoned: none. LOOP.md untouched this round: its Commands table does not enumerate next's output strings, so there is no `frontier query failed` line to add.

~~~~~~~~~~~~ evidence

## Diff (eed83d17...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                | 151 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++---------
 bin/factory.d/next.crontab |   6 ++++++
 docs/factory/LOOP.md       |   3 ++-
 3 files changed, 150 insertions(+), 10 deletions(-)

diff --git a/bin/factory b/bin/factory
index 1ed5e67..c947550 100755
--- a/bin/factory
+++ b/bin/factory
@@ -1,10 +1,11 @@
 #!/usr/bin/env bash
-# bin/factory - factory tooling. Subcommands: lint, eval, run, status, stop.
+# bin/factory - factory tooling. Subcommands: lint, eval, run, status, stop, next.
 #   bin/factory lint <file|issue>   statically checks a ticket body against docs/factory/CONTRACT.md.
 #   bin/factory eval <grader>       replays the frozen evals/ cases through the production grader call.
 #   bin/factory run <issue|file>    the supervisor: one ticket to a pull request (docs/factory/LOOP.md).
 #   bin/factory status              run states, spend, denials, worktrees, PRs, preconditions.
 #   bin/factory stop <issue>        writes FACTORY_STOP into the run dir; the run halts before its next call.
+#   bin/factory next [--install]    the F9 frontier timer's step: launch the next unblocked ready-for-agent ticket.
 # Lint never executes a check; it reads the body and shells out only to `bash -n` and `gh`.
 set -uo pipefail

@@ -1169,10 +1170,122 @@ cmd_stop() { # <issue|stem>
   [ "$n" -gt 0 ] || { echo "factory stop: no run directory under $RUNS_ROOT/$1" >&2; return 1; }
 }

+# The F9 frontier timer's one step: launch the next unblocked ready-for-agent ticket, or say why not.
+# --dry-run reports without launching or pulling, so a check can run it from inside a worktree.
+# --install writes the ten-minute runner timer from bin/factory.d/next.crontab.
+cmd_next() { # [--dry-run|--install]
+  local dry=0 do_install=0 a
+  for a in "$@"; do
+    case "$a" in
+      --dry-run) dry=1 ;;
+      --install) do_install=1 ;;
+      *)         usage next ;;
+    esac
+  done
+
+  if [ "$do_install" = 1 ]; then
+    local tmpl="$ROOT/bin/factory.d/next.crontab"
+    [ -f "$tmpl" ] || { echo "factory next --install: no template at $tmpl" >&2; return 1; }
+    command -v crontab > /dev/null 2>&1 || { echo "factory next --install: crontab not found" >&2; return 1; }
+    # Install the cron line only (the comments would accumulate on reinstall); grep -vF strips the
+    # prior copy so the result is idempotent.
+    ( crontab -l 2> /dev/null | grep -vF 'bin/factory next'; grep -v '^#' "$tmpl" ) | crontab -
+    echo "installed: $(grep -v '^#' "$tmpl" | grep -m1 .)"
+    return 0
+  fi
+
+  # 1. FACTORY_STOP at the runs root pauses the timer.
+  if [ -f "$RUNS_ROOT/FACTORY_STOP" ]; then
+    echo paused
+    return 0
+  fi
+
+  # 2. A run whose status is running or waiting-limit holds a slot (assert_parallel's rule).
+  #    FACTORY_MAX_PARALLEL bounds the count, as it does in cmd_run through apply_caps; default 1.
+  local d st n=0 max="${FACTORY_MAX_PARALLEL:-$MAX_PARALLEL}"
+  for d in "$RUNS_ROOT"/*/*/; do
+    [ -f "$d/status" ] || continue
+    st=$(cat "$d/status")
+    [ "$st" = running ] || [ "$st" = waiting-limit ] || continue
+    n=$((n + 1))
+  done
+  if [ "$n" -ge "$max" ]; then
+    echo "nothing to launch"
+    return 0
+  fi
+
+  # 3. Fast-forward the checkout next runs from, so a merged loop change reaches the supervisor
+  #    (freeze copies bin/factory from here) before the launch. Never under --dry-run, and only
+  #    with a clean tree, since a dirty tree would abort the --ff-only merge mid-launch.
+  #    A refused pull is logged (log writes to stderr, which cron mails) and never aborts the launch:
+  #    the run proceeds on the stale checkout, with the cause on record.
+  if [ "$dry" = 0 ]; then
+    if [ -n "$(git -C "$ROOT" status --porcelain 2> /dev/null)" ]; then
+      log "refused pull: dirty checkout"
+    elif ! git -C "$ROOT" fetch -q origin 2> /dev/null; then
+      log "refused pull: git fetch origin failed"
+    elif ! git -C "$ROOT" merge --ff-only origin/main > /dev/null 2>&1; then
+      log "refused pull: not fast-forward"
+    fi
+  fi
+
+  # 4. The frontier: open, ready-for-agent, unassigned issues with no open native blocker, lowest
+  #    number first. A gh failure (offline, unauthenticated, off cron's PATH, empty repo) prints
+  #    `frontier query failed` and returns 1, so cron mails it rather than the timer stalling silent;
+  #    only a successful, empty query falls through to `nothing to launch`.
+  local repo ready num
+  repo=$(gh repo view --json nameWithOwner -q .nameWithOwner 2> /dev/null)
+  if [ -z "$repo" ]; then
+    echo "frontier query failed: gh repo view" >&2
+    return 1
+  fi
+  if ! ready=$(gh api "repos/$repo/issues?labels=ready-for-agent&state=open&assignee=none&per_page=100" \
+    --jq 'sort_by(.number)[] | select(.pull_request == null) | select(.issue_dependencies_summary.blocked_by == 0) | .number' 2> /dev/null); then
+    echo "frontier query failed: gh api issues" >&2
+    return 1
+  fi
+
+  # A ticket whose PR is open but unmerged keeps its label and stays unassigned (open_pr does
+  # neither), so skip any issue with a run dir already at pr-opened, or the timer would relaunch it.
+  local pick="" rd skip
+  for num in $ready; do
+    skip=0
+    for rd in "$RUNS_ROOT/$num"/*/; do
+      [ -f "$rd/status" ] || continue
+      [ "$(cat "$rd/status")" = pr-opened ] && { skip=1; break; }
+    done
+    [ "$skip" = 0 ] && { pick="$num"; break; }
+  done
+
+  if [ -z "$pick" ]; then
+    echo "nothing to launch"
+    return 0
+  fi
+  if [ "$dry" = 1 ]; then
+    echo "would launch #$pick"
+    return 0
+  fi
+
+  # Launch bin/factory run <N> detached in one tmux session per issue, output appended to the runs root.
+  if tmux has-session -t "loam-$pick" 2> /dev/null; then
+    echo "nothing to launch"
+    return 0
+  fi
+  # cmd_run creates the run dir, but the detached shell opens the tmux log first; on a fresh install
+  # RUNS_ROOT does not exist yet, so the redirection would fail before the run ever starts.
+  mkdir -p "$RUNS_ROOT"
+  if tmux new-session -d -s "loam-$pick" "cd '$ROOT' && bin/factory run $pick >> '$RUNS_ROOT/$pick.tmux.log' 2>&1"; then
+    echo "launched #$pick"
+  else
+    echo "launch failed: tmux new-session -s loam-$pick" >&2
+    return 1
+  fi
+}
+
 cmd_status() {
-  local d led st rounds spend wall den grader notes
-  printf '%-14s %-9s %-20s %6s %8s %6s %8s %-22s %s\n' \
-    ticket sha8 status rounds spend wall denials first-failing-grader notes
+  local d led st rounds spend wall den grader clean notes
+  printf '%-14s %-9s %-20s %6s %8s %6s %8s %-22s %-5s %s\n' \
+    ticket sha8 status rounds spend wall denials first-failing-grader clean notes
   for d in "$RUNS_ROOT"/*/*/; do
     [ -f "$d/status" ] || continue
     led="$d/ledger.jsonl"
@@ -1182,11 +1295,12 @@ cmd_status() {
     wall=$(( ( $(date -u +%s) - $(cat "$d/started" 2> /dev/null || date -u +%s) ) / 60 ))
     den=$(jq -s '[.[].denials // 0] | add // 0' "$led" 2> /dev/null || echo 0)
     grader=$(grader_first_fail "$d")
+    clean=$(run_clean "$d")
     notes=""
     [ -f "$d/notify.failed" ] && notes="notify.failed"
     [ -f "$d/FACTORY_STOP" ] && notes="$notes FACTORY_STOP"
-    printf '%-14s %-9s %-20s %6s %8s %5sm %8s %-22s %s\n' \
-      "$(basename "$(dirname "$d")")" "$(basename "$d")" "$st" "$rounds" "$spend" "$wall" "$den" "${grader:--}" "$notes"
+    printf '%-14s %-9s %-20s %6s %8s %5sm %8s %-22s %-5s %s\n' \
+      "$(basename "$(dirname "$d")")" "$(basename "$d")" "$st" "$rounds" "$spend" "$wall" "$den" "${grader:--}" "$clean" "$notes"
   done
   printf '\n== worktrees and PRs\n'
   git -C "$MAIN_CHECKOUT" worktree list 2> /dev/null | sed 's/^/  /'
@@ -1207,6 +1321,23 @@ grader_first_fail() { # run dir -> the first grader item that failed in the last
   printf '%s' "$r"
 }

+# run_clean: yes|no|- for the status clean column (D09 Option A). A run is clean when it reached
+# pr-opened with zero grader-fail rounds and no other exit on the way; a hand fix after pr-opened
+# does not change it. From the run dir: status is pr-opened, the only EXIT line in factory.log is
+# pr-opened, and every round-<k>.fixes for k>=1 is empty (a grader that fails or blocks queues fixes
+# there). `-` marks a run not yet at pr-opened.
+run_clean() { # run dir -> yes|no|-
+  local d="$1" f
+  [ "$(cat "$d/status" 2> /dev/null)" = pr-opened ] || { printf -- '-'; return; }
+  grep -h ' EXIT ' "$d/factory.log" 2> /dev/null | grep -vq ' EXIT pr-opened ' && { printf 'no'; return; }
+  for f in "$d"/round-*.fixes; do
+    [ -e "$f" ] || continue
+    case "$f" in */round-0.fixes) continue ;; esac
+    [ -s "$f" ] && { printf 'no'; return; }
+  done
+  printf 'yes'
+}
+
 precondition_lines() { # LOOP.md, Preconditions
   local t
   for t in claude gh git jq python3 uv tmux timeout socat node; do
@@ -1279,16 +1410,17 @@ precondition_lines() { # LOOP.md, Preconditions
     || echo "  INFO no pushover.env; notifications comment on the ticket"
 }

-usage() { # [cmd...] - one line per named command, all five when none is named
+usage() { # [cmd...] - one line per named command, all six when none is named
   local c
-  for c in ${@:-lint eval run status stop}; do
+  for c in ${@:-lint eval run status stop next}; do
     case "$c" in
       lint)   echo "usage: bin/factory lint <file|issue>" ;;
       eval)   echo "usage: bin/factory eval <grader> [--evals-dir D] [--graders-dir D] [--model M]" ;;
       run)    echo "usage: bin/factory run <issue|ticket-file>" ;;
       status) echo "usage: bin/factory status" ;;
       stop)   echo "usage: bin/factory stop <issue|ticket-stem>" ;;
-      *)      echo "usage: bin/factory <lint|eval|run|status|stop>" ;;
+      next)   echo "usage: bin/factory next [--dry-run|--install]" ;;
+      *)      echo "usage: bin/factory <lint|eval|run|status|stop|next>" ;;
     esac
   done >&2
   exit 2
@@ -1322,5 +1454,6 @@ case "$CMD" in
           cmd_status ;;
   stop)   [ $# -eq 1 ] || usage stop
           cmd_stop "$1" ;;
+  next)   cmd_next "$@" ;;
   *)      usage ;;
 esac
diff --git a/bin/factory.d/next.crontab b/bin/factory.d/next.crontab
new file mode 100644
index 0000000..a2b4e63
--- /dev/null
+++ b/bin/factory.d/next.crontab
@@ -0,0 +1,6 @@
+# bin/factory.d/next.crontab - the F9 ten-minute frontier timer.
+# `bin/factory next --install` appends this line to the runner's crontab (idempotently).
+# A user crontab entry runs without a login shell, so `bash -lc` loads the profile that puts
+# claude, gh, and tmux on PATH. The alternative is a systemd user timer with
+# OnUnitActiveSec=10min plus `loginctl enable-linger`; the merge checklist accepts either.
+*/10 * * * * bash -lc 'cd ~/Desktop/loam && bin/factory next'
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 6ed4bb6..4e5fff0 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -166,7 +166,7 @@ The worker runs with `--setting-sources user`, which loads `~/.claude/skills/` a
 Each run has its own worktree, branch, and run directory, so unblocked tickets may run at the same time.
 Two tickets may run together only when neither names a path the other's Goal creates or rewrites; the stage-2 grader pass checks this over a breakdown, and native blocking edges hold the rest apart.
 The daily ledger is written under a lock.
-`bin/factory next` launches up to `MAX_PARALLEL` runs (default 1; raise it after two clean single runs).
+`bin/factory next` launches up to `MAX_PARALLEL` runs (default 1; raise it after two clean single runs, as `status` reports them).

 ## Notify

@@ -177,6 +177,7 @@ Events: run started, `pr-opened` with the URL, every other exit, checks failing
 ## Status and the manager

 `bin/factory status` renders, per run: status, rounds, spend, wall time, first failing grader, permission denials per round (from the worker stream-json), `notify.failed`, and a worktree and PR readiness table.
+It also shows a `clean` column (D09 Option A): `yes` when the run reached `pr-opened` with zero grader-fail rounds and no other exit on the way, `no` when it reached `pr-opened` some other way (an earlier exit, or a round that queued fixes), and `-` for a run not yet at `pr-opened`.
 It also checks the preconditions below.
 The manager is a Fable session that runs `status`, merges, and writes one learn line when the same first-failing grader appears in two consecutive runs.
 After F9, `bin/factory next` on a ten-minute runner timer launches the next frontier ticket after each merge; removing the `ready-for-agent` label parks a ticket, and `FACTORY_STOP` at the runs root pauses the timer.
~~~~~~~~~~~~ evidence
