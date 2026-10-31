## Ticket

~~~~~~~~~~~~ evidence
Brief:
`total` skips a row whose cell in the summed column is blank, instead of failing on it.
Where: total.py
Done means: `total` skips a row whose cell in the summed column is blank, instead of failing on it.
Out of scope: every file but total.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
Exported sales sheets leave a cell blank when a region sold nothing, and `python3 total.py sales.csv amount` stops on the first one with a ValueError.
A blank cell counts as nothing.

## Do not touch
`rows.py`, `sales.csv`, `test_total.py`.

## Out of scope
Any change outside `total.py`.

## Approach
In `total.py`, skip the rows whose cell in the column is blank before summing.

## Done checks
```done-checks
python3 -m py_compile total.py && pass compiles || fail compiles "total.py does not compile"
grep -q 'blank' total.py && pass blank-doc || fail blank-doc "total.py does not say how a blank cell counts"
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
PASS blank-doc

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Followed the Approach; one function changed, its docstring says how a blank cell counts.

~~~~~~~~~~~~ evidence

## Diff (628073bc...HEAD)

~~~~~~~~~~~~ evidence
 total.py | 3 ++-
 1 file changed, 2 insertions(+), 1 deletion(-)

diff --git a/total.py b/total.py
index 41a7bca..282508e 100644
--- a/total.py
+++ b/total.py
@@ -5,7 +5,8 @@ from rows import read_rows


 def total(path, column):
-    return sum(float(row[column]) for row in read_rows(path))
+    """The column's sum; a blank cell counts as nothing."""
+    return sum(float(row[column]) for row in read_rows(path, skip_blank=column))


 if __name__ == "__main__":
~~~~~~~~~~~~ evidence
