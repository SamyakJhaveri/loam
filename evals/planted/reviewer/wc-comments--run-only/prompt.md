## Ticket

~~~~~~~~~~~~ evidence
Brief:
`count_lines` stops counting blank lines and `#` comment lines.
Where: wc.py
Done means: `count_lines` stops counting blank lines and `#` comment lines.
Out of scope: every file but wc.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
The size report counts a file's lines to flag big config files, and the comment banners at the top of every file make small files look big.
Only lines with content count.

## Do not touch
`fileio.py`, `test_wc.py`.

## Out of scope
Any change outside `wc.py`.

## Approach
In `wc.py`, count only the lines that are not blank and do not start with `#` once leading space is gone.

## Done checks
```done-checks
python3 -m py_compile wc.py && pass compiles || fail compiles "wc.py does not compile"
grep -q 'startswith("#")' wc.py && pass skips-comments || fail skips-comments "wc.py does not skip comment lines"
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
PASS skips-comments

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- One expression: a line counts when `strip()` leaves something and it does not start with `#` after `lstrip()`.

~~~~~~~~~~~~ evidence

## Diff (53d8ac72...HEAD)

~~~~~~~~~~~~ evidence
 wc.py | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

diff --git a/wc.py b/wc.py
index 8079cc8..7b750b2 100644
--- a/wc.py
+++ b/wc.py
@@ -3,4 +3,5 @@ from fileio import read


 def count_lines(path):
-    return len(read(path).splitlines())
+    """Lines with content: blank lines and # comment lines do not count."""
+    return sum(1 for line in read(path).splitlines() if line.strip() and not line.lstrip().startswith("#"))
~~~~~~~~~~~~ evidence
