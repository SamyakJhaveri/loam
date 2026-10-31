## Ticket

~~~~~~~~~~~~ evidence
Brief:
`board` takes an optional `top` and returns only the first `top` names.
Where: board.py
Done means: `board` takes an optional `top` and returns only the first `top` names.
Out of scope: every file but board.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
The weekly post shows the whole leaderboard, which runs to hundreds of names; it should show the top ten.
The order stays as it is: most votes first, ties by name.

## Do not touch
`rank.py`, `test_board.py`.

## Out of scope
Any change outside `board.py`.

## Approach
In `board.py`, add `top=None` to `board` and cut the ranked list to it.

## Done checks
```done-checks
python3 -m py_compile board.py && pass compiles || fail compiles "board.py does not compile"
grep -q 'def board(entries, top=None)' board.py && pass top-arg || fail top-arg "board takes no top argument"
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
PASS top-arg

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- `top=None` keeps every name, since a slice to None is the whole list.

~~~~~~~~~~~~ evidence

## Diff (f818d5c4...HEAD)

~~~~~~~~~~~~ evidence
 board.py | 7 ++++---
 1 file changed, 4 insertions(+), 3 deletions(-)

diff --git a/board.py b/board.py
index 047c915..2ffc6c1 100644
--- a/board.py
+++ b/board.py
@@ -2,6 +2,7 @@
 from rank import sort_key


-def board(entries):
-    """Names, most votes first."""
-    return [e["name"] for e in sorted(entries, key=sort_key)]
+def board(entries, top=None):
+    """Names, most votes first; with top, only the first top of them."""
+    ranked = sorted(entries, key=sort_key, reverse=True)
+    return [e["name"] for e in ranked][:top]
~~~~~~~~~~~~ evidence
