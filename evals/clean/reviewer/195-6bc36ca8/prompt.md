## Ticket

~~~~~~~~~~~~ evidence
Brief:
Make `bin/factory next` park a ticket only when a run of its current body exited on a parking status, so a body edit relaunches it, and pass the two toolchain variables into the tmux launch.
Where: bin/factory, bin/tests/test_factory_next_parking.py, docs/factory/LOOP.md.
Done means: `park_status <issue> <body>` reads only the run dir keyed by that body; cmd_next uses it with the body from its existing frontier query; the tmux launch carries LOAM_FACTORY_TOOLCHAIN and LOAM_FACTORY_COPIER.
Out of scope: the parallel cap; the pr-opened case; the grader-round cap; any change to how cmd_run computes the key.
Blocked by: none

## Goal and why
On 2026-09-22 #182 and #183 had their bodies fixed after an abandon, yet `bin/factory next` kept printing "parked: last run exited abandon; edit the body or remove ready-for-agent", because the loop at bin/factory:1420 reads the newest run dir under any body key; both needed hand launches in tmux.
Run dirs are already keyed by the body (bin/factory:1260, `printf '%s' "$BODY" | sha256_of | cut -c1-8`), so the fix is to read the dir for the current key.
Second gap from the post-merge critique of PR #191: `cmd_next` checks the toolchain env in its own shell, but `tmux new-session` gives the run the tmux server's environment, so a server started without ~/.profile makes `run` exit 4 before it writes a run dir, and cron prints "launched" every ten minutes.

## Do not touch
The standing list. Also: bin/check, bin/factory.d/, seed/, docs/factory/CONTRACT.md, bin/tests/test_factory_budget_stop.py.
Except: bin/factory, docs/factory/LOOP.md (this ticket edits them), bin/tests/test_factory_next_parking.py (this ticket creates it).

## Out of scope
The parallel cap loop and `holds_slot` (#184).
How cmd_run computes the key or names the run dir.
The pr-opened and stopped relaunch rules; they keep their current meaning, now per body key.
The runner crontab and ~/.local/bin scripts.

## Approach
1. Add `park_status() { # <issue> <body> -> the status of the run for this body, or none` near cmd_next. It computes the key exactly as cmd_run does (`printf '%s' "$2" | sha256_of | cut -c1-8`) and prints the contents of `$RUNS_ROOT/$1/<key>/status`, or `none` when that file is missing. It reads RUNS_ROOT at call time.
2. In cmd_next, the frontier query (bin/factory:1406) already returns `.body`; emit the number and the base64 of the body on one line (`"\(.number) \(.body | @base64)"`), decode each with `base64 -d` inside `$(...)` so trailing newlines strip exactly as `load_ticket`'s `$(gh issue view ...)` does, and replace the newest-dir loop (about lines 1418 to 1424) with `st_last=$(park_status "$num" "$body")`. Keep the case arms as they are. Update the comment above the loop: a run of an earlier body no longer parks the issue.
3. The tmux launch in cmd_next passes both variables: `tmux new-session -d -s "loam-$pick" -e "LOAM_FACTORY_TOOLCHAIN=$LOAM_FACTORY_TOOLCHAIN" -e "LOAM_FACTORY_COPIER=$LOAM_FACTORY_COPIER" "..."` (tmux 3.4 on the runner supports `-e`).
4. Create bin/tests/test_factory_next_parking.py on the pattern of bin/tests/test_factory_budget_stop.py (source bin/factory with FACTORY_SOURCED=1, a temp RUNS_ROOT): an old body's abandon does not park a new body; the same body's abandon parks it; a stopped-environment run of the same body relaunches.
5. docs/factory/LOOP.md, next to the line on parking (about line 180): one sentence saying a ticket is parked by a run of its current body, so editing the body relaunches it.
6. Commit before the checks run.

## Done checks
```done-checks
out=$( (FACTORY_SOURCED=1 . bin/factory; RUNS_ROOT=$(mktemp -d); mkdir -p "$RUNS_ROOT/7/aaaaaaaa"; echo abandon > "$RUNS_ROOT/7/aaaaaaaa/status"; echo 1 > "$RUNS_ROOT/7/aaaaaaaa/launched"; park_status 7 "a new body"; rm -rf "$RUNS_ROOT") 2>&1 ); [ "$out" = none ] && pass new-body-launches || fail new-body-launches "park_status is missing, or an earlier body's abandon still parks a new body: $out"
out=$( (FACTORY_SOURCED=1 . bin/factory; RUNS_ROOT=$(mktemp -d); k=$(printf '%s' "same body" | sha256_of | cut -c1-8); mkdir -p "$RUNS_ROOT/7/$k"; echo abandon > "$RUNS_ROOT/7/$k/status"; echo 1 > "$RUNS_ROOT/7/$k/launched"; park_status 7 "same body"; rm -rf "$RUNS_ROOT") 2>&1 ); [ "$out" = abandon ] && pass same-body-parks || fail same-body-parks "park_status does not report the abandon of a run of the same body: $out"
fn=$(sed -n '/^cmd_next()/,/^}/p' bin/factory); grep -q 'park_status' <<<"$fn" && grep -q '@base64' <<<"$fn" && pass next-uses-body-key || fail next-uses-body-key "cmd_next does not call park_status with the body from the frontier query"
fn=$(sed -n '/^cmd_next()/,/^}/p' bin/factory); launch=$(grep 'tmux new-session' <<<"$fn"); grep -q 'LOAM_FACTORY_TOOLCHAIN=' <<<"$launch" && grep -q 'LOAM_FACTORY_COPIER=' <<<"$launch" && pass launch-carries-env || fail launch-carries-env "the tmux launch in cmd_next does not pass both toolchain variables"
grep -qi 'current body' docs/factory/LOOP.md && pass loop-doc || fail loop-doc "LOOP.md does not say a ticket is parked by a run of its current body"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: no
effort: high
MAX_ROUNDS=2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/factory/LOOP.md (parking, line 180), #182, #183, PR #191

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS new-body-launches
PASS same-body-parks
PASS next-uses-body-key
PASS launch-carries-env
PASS loop-doc
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
park_status sits above cmd_next's header comment, not between the comment and cmd_next, so the comment stays on the function it documents.
The frontier jq uses `.body // ""` before @base64, since `null | @base64` encodes the word "null" and would key an empty body wrongly.
The loop reads the frontier with `while read ... done <<< "$ready"` (not a pipe), so `pick` survives the loop; a blank line from an empty query is skipped.
The test file also drives cmd_next --dry-run with gh, claude_logged_in, and assert_toolchain_env stubbed as shell functions, so the base64 wiring is tested, not only park_status; the tests fail on the pre-change bin/factory (3 of 4).
The tmux line keeps both -e flags on the one physical line the launch-carries-env check greps.
cmd_next takes the body from gh api (REST) and load_ticket from gh issue view (GraphQL); the fix assumes both return the same bytes, so a wrong park after this lands should be checked there first.

~~~~~~~~~~~~ evidence

## Diff (29535354...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                            | 36 ++++++++++++++++++++++--------------
 bin/tests/test_factory_next_parking.py | 88 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 docs/factory/LOOP.md                   |  1 +
 3 files changed, 111 insertions(+), 14 deletions(-)

diff --git a/bin/factory b/bin/factory
index f3a12258..88e0c8c6 100755
--- a/bin/factory
+++ b/bin/factory
@@ -1310,6 +1310,12 @@ cmd_stop() { # <issue|stem>
   [ "$n" -gt 0 ] || { echo "factory stop: no run directory under $RUNS_ROOT/$1" >&2; return 1; }
 }

+park_status() { # <issue> <body> -> the status of the run for this body, or none
+  local k
+  k=$(printf '%s' "$2" | sha256_of | cut -c1-8)   # the key cmd_run names the run dir by
+  cat "$RUNS_ROOT/$1/$k/status" 2> /dev/null || echo none
+}
+
 # The F9 frontier timer's one step: launch the next unblocked ready-for-agent ticket, or say why not.
 # --dry-run reports without launching or pulling, so a check can run it from inside a worktree.
 # --install writes the ten-minute runner timer from bin/factory.d/next.crontab.
@@ -1397,37 +1403,37 @@ cmd_next() { # [--dry-run|--install]
   #    number first. A gh failure (offline, unauthenticated, off cron's PATH, empty repo) prints
   #    `frontier query failed` and returns 1, so cron mails it rather than the timer stalling silent;
   #    only a successful, empty query falls through to `nothing to launch`.
-  local repo ready num
+  local repo ready num b64 body
   repo=$(gh repo view --json nameWithOwner -q .nameWithOwner 2> /dev/null)
   if [ -z "$repo" ]; then
     echo "frontier query failed: gh repo view" >&2
     return 1
   fi
   if ! ready=$(gh api "repos/$repo/issues?labels=ready-for-agent&state=open&assignee=none&per_page=100" \
-    --jq 'sort_by(.number)[] | select(.pull_request == null) | select(.issue_dependencies_summary.blocked_by == 0) | .number' 2> /dev/null); then
+    --jq 'sort_by(.number)[] | select(.pull_request == null) | select(.issue_dependencies_summary.blocked_by == 0) | "\(.number) \(.body // "" | @base64)"' 2> /dev/null); then
     echo "frontier query failed: gh api issues" >&2
     return 1
   fi

-  # An issue's newest run dir (by launch time) decides: no run dir launches; stopped-environment and
-  # stopped relaunch (the environment, not the ticket, ended them); every other exit parks the issue
+  # The run of the issue's current body decides (park_status): no such run launches; stopped-environment
+  # and stopped relaunch (the environment, not the ticket, ended them); every other exit parks the issue
   # until a human edits the body or removes the label, since the same body would fail the same way.
+  # A run of an earlier body no longer parks the issue, so an edited body launches on the next tick.
+  # The body travels as base64 so its newlines stay on one line; $(...) strips its trailing newlines
+  # the way load_ticket's $(gh issue view ...) does, so the key matches the one cmd_run computes.
   # A ticket at pr-opened is assigned at launch, so it is not in the frontier; if a human unassigns
   # it, its slot is already counted above while its worktree exists.
-  local pick="" rd newest st_last
-  for num in $ready; do
-    newest=""
-    for rd in "$RUNS_ROOT/$num"/*/; do
-      [ -f "$rd/status" ] || continue
-      [ -z "$newest" ] || [ "$(cat "$rd/launched" 2> /dev/null || echo 0)" -gt "$(cat "$newest/launched" 2> /dev/null || echo 0)" ] && newest="$rd"
-    done
-    st_last=$(cat "$newest/status" 2> /dev/null || echo none)
+  local pick="" st_last
+  while read -r num b64; do
+    [ -n "$num" ] || continue
+    body=$(printf '%s' "$b64" | base64 -d)
+    st_last=$(park_status "$num" "$body")
     case "$st_last" in
       none|stopped-environment|stopped) [ -n "$pick" ] || pick="$num" ;;
       pr-opened) ;;
       *) echo "parked #$num: last run exited $st_last; edit the body or remove ready-for-agent" >&2 ;;
     esac
-  done
+  done <<< "$ready"

   if [ -z "$pick" ]; then
     echo "nothing to launch"
@@ -1445,8 +1451,10 @@ cmd_next() { # [--dry-run|--install]
   fi
   # cmd_run creates the run dir, but the detached shell opens the tmux log first; on a fresh install
   # RUNS_ROOT does not exist yet, so the redirection would fail before the run ever starts.
+  # tmux gives the session the tmux server's environment, not this shell's, so the toolchain exports
+  # checked above travel with -e; a server started without them would make the run exit 4 unrecorded.
   mkdir -p "$RUNS_ROOT"
-  if tmux new-session -d -s "loam-$pick" "cd '$ROOT' && bin/factory run $pick >> '$RUNS_ROOT/$pick.tmux.log' 2>&1"; then
+  if tmux new-session -d -s "loam-$pick" -e "LOAM_FACTORY_TOOLCHAIN=$LOAM_FACTORY_TOOLCHAIN" -e "LOAM_FACTORY_COPIER=$LOAM_FACTORY_COPIER" "cd '$ROOT' && bin/factory run $pick >> '$RUNS_ROOT/$pick.tmux.log' 2>&1"; then
     echo "launched #$pick"
   else
     echo "launch failed: tmux new-session -s loam-$pick" >&2
diff --git a/bin/tests/test_factory_next_parking.py b/bin/tests/test_factory_next_parking.py
new file mode 100644
index 00000000..2d445561
--- /dev/null
+++ b/bin/tests/test_factory_next_parking.py
@@ -0,0 +1,88 @@
+"""`bin/factory next` parks a ticket only on a run of its current body, so a body edit relaunches it.
+
+`bin/factory` is sourced (FACTORY_SOURCED=1) with a temp runs root. park_status is called directly,
+and cmd_next --dry-run runs with gh, the login probe, and the toolchain gate stubbed as shell functions,
+so the frontier line carries the body the way the real query does. No network, no tmux, no `claude`.
+"""
+
+from __future__ import annotations
+
+import base64
+import hashlib
+import os
+import pathlib
+import subprocess
+import tempfile
+import unittest
+
+ROOT = pathlib.Path(__file__).resolve().parents[2]
+
+
+def sourced(script: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
+    """Run `script` in a bash that has sourced bin/factory from the repo root."""
+    return subprocess.run(
+        ["bash", "-c", f". bin/factory\n{script}"],
+        cwd=ROOT, env={**os.environ, "FACTORY_SOURCED": "1", **(env or {})},
+        capture_output=True, text=True, check=False,
+    )
+
+
+def key(body: str) -> str:
+    """The run-dir key cmd_run computes: the first 8 hex digits of the body's sha256."""
+    return hashlib.sha256(body.encode()).hexdigest()[:8]
+
+
+class ParkingTests(unittest.TestCase):
+    def setUp(self) -> None:
+        tmp = tempfile.TemporaryDirectory()
+        self.addCleanup(tmp.cleanup)
+        self.runs = pathlib.Path(tmp.name)
+
+    def run_dir(self, issue: int, body: str, status: str) -> None:
+        d = self.runs / str(issue) / key(body)
+        d.mkdir(parents=True)
+        (d / "status").write_text(status + "\n")
+        (d / "launched").write_text("1\n")
+
+    def park_status(self, issue: int, body: str) -> str:
+        proc = sourced(f'park_status {issue} "$BODY_ARG"', {"FACTORY_RUNS_ROOT": str(self.runs), "BODY_ARG": body})
+        self.assertEqual(proc.returncode, 0, proc.stderr)
+        return proc.stdout.strip()
+
+    def next_dry_run(self, issue: int, body: str) -> subprocess.CompletedProcess[str]:
+        line = f"{issue} {base64.b64encode(body.encode()).decode()}"
+        stubs = ("assert_toolchain_env() { :; }; claude_logged_in() { :; }; "
+                 f"gh() {{ case $1 in repo) echo o/r ;; api) echo '{line}' ;; esac; }}; cmd_next --dry-run")
+        return sourced(stubs, {"FACTORY_RUNS_ROOT": str(self.runs)})
+
+    def test_old_body_abandon_does_not_park_a_new_body(self) -> None:
+        self.run_dir(7, "the old body", "abandon")
+        self.assertEqual(self.park_status(7, "the new body\n\nwith a second paragraph"), "none")
+        proc = self.next_dry_run(7, "the new body\n\nwith a second paragraph")
+        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
+        self.assertNotIn("parked", proc.stderr)
+
+    def test_same_body_abandon_parks(self) -> None:
+        body = "same body\n\n- a list item"
+        self.run_dir(7, body, "abandon")
+        self.assertEqual(self.park_status(7, body), "abandon")
+        proc = self.next_dry_run(7, body)
+        self.assertEqual(proc.stdout.strip(), "nothing to launch", proc.stderr)
+        self.assertIn("parked #7: last run exited abandon", proc.stderr)
+
+    def test_same_body_stopped_environment_relaunches(self) -> None:
+        body = "same body"
+        self.run_dir(7, body, "stopped-environment")
+        self.assertEqual(self.park_status(7, body), "stopped-environment")
+        proc = self.next_dry_run(7, body)
+        self.assertEqual(proc.stdout.strip(), "would launch #7", proc.stderr)
+
+    def test_trailing_newlines_strip_as_load_ticket_does(self) -> None:
+        # gh returns the body raw; load_ticket's $(...) strips its trailing newlines before cmd_run keys it.
+        self.run_dir(7, "body", "abandon")
+        proc = self.next_dry_run(7, "body\n\n")
+        self.assertIn("parked #7: last run exited abandon", proc.stderr)
+
+
+if __name__ == "__main__":
+    unittest.main()
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 87032079..2e09d259 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -178,6 +178,7 @@ It also shows a `clean` column (D09 Option A): `yes` when the run reached `pr-op
 It also checks the preconditions below.
 The manager is a Fable session that runs `status`, merges, and writes one learn line when the same first-failing grader appears in two consecutive runs.
 After F9, `bin/factory next` on a ten-minute runner timer launches the next frontier ticket after each merge; removing the `ready-for-agent` label parks a ticket, and `FACTORY_STOP` at the runs root pauses the timer; a logged-out runner makes `next` print `login expired` on stderr and exit 1 without launching.
+A ticket is parked only by a run of its current body, so editing the body relaunches it on the next tick.

 ## Stop

~~~~~~~~~~~~ evidence
