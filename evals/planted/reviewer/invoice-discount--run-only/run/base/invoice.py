"""Invoice lines."""
from decimal import Decimal


def line_total(qty, price):
    """qty times a price like "12.50", in cents."""
    return qty * int(Decimal(price) * 100)
