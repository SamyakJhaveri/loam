## Ticket

~~~~~~~~~~~~ evidence
Brief:
A page's title comes from its `Title:` header when the page has a header, and from its first body line otherwise.
Where: page.py
Done means: A page's title comes from its `Title:` header when the page has a header, and from its first body line otherwise.
Out of scope: every file but page.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
Pages whose first body line is an image get an empty or wrong title in the index; authors already write a `Title:` header on those pages.

## Do not touch
`meta.py`, `test_page.py`.

## Out of scope
Any change outside `page.py`.

## Approach
In `page.py`, read the header with `meta.parse_header` and return its title when there is a header; keep the first-line rule for a page with none.

## Done checks
```done-checks
python3 -m py_compile page.py && pass compiles || fail compiles "page.py does not compile"
grep -q 'parse_header(text)' page.py && pass reads-header || fail reads-header "page.py does not read the header"
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
PASS reads-header

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- A page with no header keeps the first-line rule, as the Approach says.

~~~~~~~~~~~~ evidence

## Diff (34ea79ce...HEAD)

~~~~~~~~~~~~ evidence
 page.py | 9 ++++++---
 1 file changed, 6 insertions(+), 3 deletions(-)

diff --git a/page.py b/page.py
index 4feb05f..f04fb4e 100644
--- a/page.py
+++ b/page.py
@@ -1,7 +1,10 @@
 """A page's title for the index."""
+from meta import parse_header


 def title(text):
-    """The first non-blank line after the header."""
-    body = text.split("\n\n", 1)[1] if "\n\n" in text else text
-    return next((line for line in body.splitlines() if line.strip()), "")
+    """The Title header when the page has a header, else the first non-blank line."""
+    header = parse_header(text)
+    if header:
+        return header["Title"]
+    return next((line for line in text.splitlines() if line.strip()), "")
~~~~~~~~~~~~ evidence
