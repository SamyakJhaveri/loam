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
In `board.py`, add `top=None` to `board`, order the entries with `rank.by_votes`, the ordering the rest of the site uses, and cut the list to `top`.

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
- The inline sort key gave way to `rank.by_votes`, as the Approach says, so the board and the site share one ordering.

~~~~~~~~~~~~ evidence

## Diff (f818d5c4...HEAD)

~~~~~~~~~~~~ evidence
 board.py | 7 ++++---
 1 file changed, 4 insertions(+), 3 deletions(-)

diff --git a/board.py b/board.py
index a44e6ee..199fc69 100644
--- a/board.py
+++ b/board.py
@@ -1,6 +1,7 @@
 """The leaderboard."""
+from rank import by_votes


-def board(entries):
-    """Names, most votes first, ties by name."""
-    return [e["name"] for e in sorted(entries, key=lambda e: (-e["votes"], e["name"]))]
+def board(entries, top=None):
+    """Names, most votes first, ties by name; with top, only the first top of them."""
+    return [e["name"] for e in by_votes(entries)][:top]
~~~~~~~~~~~~ evidence
