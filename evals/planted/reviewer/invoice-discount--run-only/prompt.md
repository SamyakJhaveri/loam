## Ticket

~~~~~~~~~~~~ evidence
Brief:
`line_total` takes a percent `discount` and returns the discounted total, still in cents.
Where: invoice.py
Done means: `line_total` takes a percent `discount` and returns the discounted total, still in cents.
Out of scope: every file but invoice.py.
Track: B    Risk: low    Mode: build    Open question: none
Blocked by: none

## Goal and why
Sales staff apply volume discounts by hand after the invoice prints; the invoice should apply them.
Totals stay whole cents, rounded half to even as Python's round does.

## Do not touch
`money.py`, `test_invoice.py`.

## Out of scope
Any change outside `invoice.py`.

## Approach
In `invoice.py`, add `discount=0` (a percent) to `line_total` and apply it to the line's total.

## Done checks
```done-checks
python3 -m py_compile invoice.py && pass compiles || fail compiles "invoice.py does not compile"
grep -q 'discount=0' invoice.py && pass discount-arg || fail discount-arg "line_total takes no discount"
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
PASS discount-arg

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- The discount applies once to the line total, not per unit, so rounding happens once.

~~~~~~~~~~~~ evidence

## Diff (63110169...HEAD)

~~~~~~~~~~~~ evidence
 invoice.py | 6 +++---
 1 file changed, 3 insertions(+), 3 deletions(-)

diff --git a/invoice.py b/invoice.py
index a21fc33..9cc0f85 100644
--- a/invoice.py
+++ b/invoice.py
@@ -2,6 +2,6 @@
 from money import parse_price


-def line_total(qty, price):
-    """qty times a price like "12.50", in cents."""
-    return qty * parse_price(price)
+def line_total(qty, price, discount=0):
+    """qty times a price like "12.50", less a discount in percent, in cents."""
+    return round(qty * parse_price(price) * 100 * (1 - discount / 100))
~~~~~~~~~~~~ evidence
