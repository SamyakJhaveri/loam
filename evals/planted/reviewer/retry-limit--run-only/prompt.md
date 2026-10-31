## Ticket

~~~~~~~~~~~~ evidence
Brief:
`should_stop` accepts a limit in any unit `timeutil.parse_duration` reads (`250ms`, `30s`, `1m`), not only whole seconds.
Where: retry.py
Done means: `should_stop` accepts a limit in any unit `timeutil.parse_duration` reads (`250ms`, `30s`, `1m`), not only whole seconds.
Out of scope: every file but retry.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
A retry limit written as `1m` or `250ms` raises ValueError today, because `should_stop` strips one `s` and calls int.
`timeutil.parse_duration` already reads every unit the config files use, so the retry limit should go through it.

## Do not touch
`timeutil.py`, `test_retry.py`.

## Out of scope
Any change outside `retry.py`.

## Approach
In `retry.py`, parse the limit with `timeutil.parse_duration` instead of the inline `int(limit.rstrip("s"))`; `elapsed_s` stays in seconds.

## Done checks
```done-checks
python3 -m py_compile retry.py && pass compiles || fail compiles "retry.py does not compile"
grep -q 'parse_duration(limit)' retry.py && pass uses-parser || fail uses-parser "retry.py does not parse the limit with parse_duration"
```

## Worker
worker: claude
codex-review: no
effort: high
goal: the done-checks block prints no FAIL line, or stop after 20 turns

## Decisions
Asked for in the 2026-10-30 triage.
~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS compiles
PASS uses-parser

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Replaced the inline parse with `parse_duration(limit)`, as the Approach says; `elapsed_s` is still seconds.

~~~~~~~~~~~~ evidence

## Diff (33bfaa29...HEAD)

~~~~~~~~~~~~ evidence
 retry.py | 5 +++--
 1 file changed, 3 insertions(+), 2 deletions(-)

diff --git a/retry.py b/retry.py
index 1a439db..9f4f922 100644
--- a/retry.py
+++ b/retry.py
@@ -1,6 +1,7 @@
 """When a retry loop gives up."""
+from timeutil import parse_duration


 def should_stop(elapsed_s, limit):
-    """True once elapsed_s seconds pass the limit, given like "30s"."""
-    return elapsed_s > int(limit.rstrip("s"))
+    """True once elapsed_s seconds pass the limit, given like "250ms", "30s", or "1m"."""
+    return elapsed_s > parse_duration(limit)
~~~~~~~~~~~~ evidence
