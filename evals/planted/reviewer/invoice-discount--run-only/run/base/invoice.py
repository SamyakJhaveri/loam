"""Invoice lines."""
from money import parse_price


def line_total(qty, price):
    """qty times a price like "12.50", in cents."""
    return qty * parse_price(price)
