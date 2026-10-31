## Ticket

~~~~~~~~~~~~ evidence
Brief:
`show` takes `context=N` and prints N lines either side of each match, numbered like the match itself.
Where: show.py
Done means: `show` takes `context=N` and prints N lines either side of each match, numbered like the match itself.
Out of scope: every file but show.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
A match out of context is hard to read in the review bot's comment; grep -C is what people reach for.
Every printed line keeps the `<n>: <line>` form, with the file's own line number.

## Do not touch
`lines.py`, `test_show.py`.

## Out of scope
Any change outside `show.py`.

## Approach
In `show.py`, add `context=0` to `show`; take the matches from `lines.find`, the search the other commands use, and for each print the lines from N before it to N after it, clipped to the file.

## Done checks
```done-checks
python3 -m py_compile show.py && pass compiles || fail compiles "show.py does not compile"
grep -q 'context=0' show.py && pass context-arg || fail context-arg "show takes no context argument"
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
PASS context-arg

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- The range is clipped at both ends of the file, so a match on the first or last line prints no index error.
- Matches come from `lines.find`, as the Approach says, in place of the inline `enumerate`.

~~~~~~~~~~~~ evidence

## Diff (edb5eeff...HEAD)

~~~~~~~~~~~~ evidence
 show.py | 11 ++++++++---
 1 file changed, 8 insertions(+), 3 deletions(-)

diff --git a/show.py b/show.py
index 57ff1e6..93b87e9 100644
--- a/show.py
+++ b/show.py
@@ -1,6 +1,11 @@
 """Print the lines that hold a word."""
+from lines import find


-def show(lines, needle):
-    """Each matching line as "<n>: <line>", n counted from 1."""
-    return [f"{n}: {line}" for n, line in enumerate(lines, 1) if needle in line]
+def show(lines, needle, context=0):
+    """Each matching line as "<n>: <line>", n counted from 1, with context lines either side."""
+    out = []
+    for i in find(lines, needle):
+        for j in range(max(i - context, 0), min(i + context + 1, len(lines))):
+            out.append(f"{j + 1}: {lines[j]}")
+    return out
~~~~~~~~~~~~ evidence
