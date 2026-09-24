## Ticket

~~~~~~~~~~~~ evidence
Brief:
Count a run directory that carries `launched` but no `status` file as holding a slot, in both `bin/factory next` and the run's own `assert_parallel`, so two launches within round 0 cannot both pass MAX_PARALLEL.
Where: bin/factory, docs/factory/LOOP.md.
Done means: a run directory with `launched` and no `status` counts as live in both counts; a directory with neither, or with a terminal status, does not; bin/check passes.
Out of scope: a lock around count-and-launch; the one-second window between `tmux new-session` and the run's own mkdir; a status column for a launching run.
Blocked by: #182 (both tickets edit bin/factory).

## Goal and why
On 2026-09-21 two runs launched eight seconds apart (#156) and two more 68 seconds apart (#167) with MAX_PARALLEL=1, because both counts read only a `status` file and a run in round 0 has not written one yet (bin/factory:598 and 1319); round 0 takes about 90 seconds.
cmd_run writes `launched` at line 1229 before it calls assert_parallel, so the marker already exists; the counts ignore it.

## Do not touch
The standing list. Also: bin/check, bin/factory.d/, seed/, docs/factory/CONTRACT.md.
Except: bin/factory, docs/factory/LOOP.md (this ticket edits them).

## Out of scope
A lock file at the runs root.
Writing `status: running` before round 0.
Any change to how pr-opened runs are counted.
The `bin/factory status` table.

## Approach
1. Add `holds_slot DIR` in bin/factory next to assert_parallel (line 596): returns 0 when `DIR/status` reads `running` or `waiting-limit`, or when `DIR/launched` exists and `DIR/status` does not; returns 1 otherwise.
2. assert_parallel and cmd_next's slot loop (line 1319) each call it in place of their status test; cmd_next keeps its pr-opened clause unchanged and assert_parallel keeps its own-key exclusion.
3. A run that ends through `finish` always writes a status, so only a hard-killed round-0 run leaves `launched` alone; that holds the slot until the operator removes the directory, the same as a hard-killed running run today. Say so in the MAX_PARALLEL comment above assert_parallel and, where docs/factory/LOOP.md describes the parallel cap, in this sentence: "A run directory with `launched` and no `status` file holds a slot until its run writes one or the operator removes it."

## Done checks
```done-checks
r=$(mktemp -d); mkdir -p "$r/l" "$r/e" "$r/t"; date +%s > "$r/l/launched"; date +%s > "$r/t/launched"; echo abandon > "$r/t/status"; ( FACTORY_SOURCED=1 . bin/factory; holds_slot "$r/l" && ! holds_slot "$r/e" && ! holds_slot "$r/t" ) >/dev/null 2>&1 && pass holds-slot || fail holds-slot "holds_slot missing, or it miscounts launched-only, empty, or terminal directories"
r=$(mktemp -d); mkdir -p "$r/998/aaaaaaaa" "$r/other/bbbbbbbb"; date +%s > "$r/998/aaaaaaaa/launched"; ( FACTORY_SOURCED=1 . bin/factory; RUNS_ROOT="$r"; KEY=other; RUN="$r/other/bbbbbbbb"; LOG="$RUN/factory.log"; MAX_PARALLEL=1; IS_FILE=1; assert_parallel ) >/dev/null 2>&1; rc=$?; [ "$rc" -eq 4 ] && pass assert-parallel-sees-launching || fail assert-parallel-sees-launching "assert_parallel let a second run start beside a launched-only run (exit $rc, expected 4 stopped-environment)"
sed -n '/^cmd_next()/,/^}/p' bin/factory | grep -q 'holds_slot' && sed -n '/^assert_parallel()/,/^}/p' bin/factory | grep -q 'holds_slot' && pass wired-into-both-counts || fail wired-into-both-counts "cmd_next or assert_parallel does not call holds_slot"
grep -q 'holds a slot' docs/factory/LOOP.md && pass loop-doc || fail loop-doc "LOOP.md does not say a launched run with no status holds a slot"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: no
effort: high
MAX_ROUNDS=2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
#156, #167, docs/factory/LOOP.md (MAX_PARALLEL)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS holds-slot
PASS assert-parallel-sees-launching
PASS wired-into-both-counts
PASS loop-doc
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- holds_slot branches on whether `status` exists: with a status, only running or waiting-limit count; without one, `launched` decides (Approach step 1, as written).
- cmd_next reads status with `cat ... || true` so a launched-only directory reaches holds_slot; the pr-opened clause is unchanged.
- LOOP.md parallel-cap paragraph gains the ticket's sentence plus one line naming running and waiting-limit, so the new sentence has its context.
- Verified the assert-parallel-sees-launching check fails against HEAD's bin/factory (rc 0) and passes after the change (rc 4).

~~~~~~~~~~~~ evidence

## Diff (051221ec...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory          | 30 ++++++++++++++++++++----------
 docs/factory/LOOP.md |  2 ++
 2 files changed, 22 insertions(+), 10 deletions(-)

diff --git a/bin/factory b/bin/factory
index ffeaf32b..fa7f97f3 100755
--- a/bin/factory
+++ b/bin/factory
@@ -592,14 +592,25 @@ assert_caps() { # before every model call; the daily cap is "the next call could
 stop_requested() { [ -f "$RUN/FACTORY_STOP" ] || [ -f "$RUNS_ROOT/FACTORY_STOP" ]; }

 # MAX_PARALLEL counts the other tickets already holding a slot: a run is live while its
-# status reads running or waiting-limit.
+# status reads running or waiting-limit, or while it has written `launched` and no status yet
+# (round 0, #156 #167). A run that ends through finish always writes a status, so only a
+# hard-killed round-0 run leaves `launched` alone; it holds the slot until the operator removes
+# its directory, as a hard-killed running run does.
+holds_slot() { # <run dir>
+  local st
+  if [ -f "$1/status" ]; then
+    st=$(cat "$1/status")
+    [ "$st" = running ] || [ "$st" = waiting-limit ]
+  else
+    [ -f "$1/launched" ]
+  fi
+}
+
 assert_parallel() {
-  local d n=0 st
+  local d n=0
   for d in "$RUNS_ROOT"/*/*/; do
-    [ -f "$d/status" ] || continue
     [ "$(basename "$(dirname "$d")")" = "$KEY" ] && continue
-    st=$(cat "$d/status")
-    [ "$st" = running ] || [ "$st" = waiting-limit ] || continue
+    holds_slot "$d" || continue
     n=$((n + 1))
   done
   [ "$n" -lt "$MAX_PARALLEL" ] \
@@ -1346,19 +1357,18 @@ cmd_next() { # [--dry-run|--install]
     return 1
   fi

-  # 2. A run whose status is running or waiting-limit holds a slot (assert_parallel's rule), and so
-  #    does a pr-opened run whose ticket worktree still exists: the merge ritual removes the worktree,
+  # 2. A run holds a slot when holds_slot says so (assert_parallel's rule: running, waiting-limit,
+  #    or launched with no status yet), and so does a pr-opened run whose ticket worktree still exists: the merge ritual removes the worktree,
   #    so until then the PR awaits merge and the next ticket waits (LOOP.md: after each merge).
   #    FACTORY_MAX_PARALLEL bounds the count, as it does in cmd_run through apply_caps; default 1.
   local d st n=0 max="${FACTORY_MAX_PARALLEL:-$MAX_PARALLEL}"
   for d in "$RUNS_ROOT"/*/*/; do
-    [ -f "$d/status" ] || continue
-    st=$(cat "$d/status")
+    st=$(cat "$d/status" 2> /dev/null || true)
     if [ "$st" = pr-opened ]; then
       [ -d "$MAIN_CHECKOUT-$(basename "$(dirname "$d")")" ] && n=$((n + 1))
       continue
     fi
-    [ "$st" = running ] || [ "$st" = waiting-limit ] || continue
+    holds_slot "$d" || continue
     n=$((n + 1))
   done
   if [ "$n" -ge "$max" ]; then
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 6b5abac3..edbeae3f 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -162,6 +162,8 @@ Each run has its own worktree, branch, and run directory, so unblocked tickets m
 Two tickets may run together only when neither names a path the other's Goal creates or rewrites; the stage-2 grader pass checks this over a breakdown, and native blocking edges hold the rest apart.
 The daily ledger is written under a lock.
 `bin/factory next` launches up to `MAX_PARALLEL` runs (default 1; raise it after two clean single runs, as `status` reports them).
+A run holds a slot while its status reads `running` or `waiting-limit`.
+A run directory with `launched` and no `status` file holds a slot until its run writes one or the operator removes it.

 ## Notify

~~~~~~~~~~~~ evidence
