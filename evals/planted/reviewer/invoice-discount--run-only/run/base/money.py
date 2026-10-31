"""Prices as the price list writes them."""
from decimal import Decimal


def parse_price(text):
    """A price like "12.50" as a whole number of cents."""
    return int(Decimal(text) * 100)
