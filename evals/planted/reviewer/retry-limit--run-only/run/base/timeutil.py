"""Durations as the config files write them."""
import re

UNITS = {"ms": 1, "s": 1000, "m": 60000}


def parse_duration(text):
    """A duration like "250ms", "30s", or "1m", in milliseconds."""
    m = re.fullmatch(r"(\d+)(ms|s|m)", text.strip())
    if not m:
        raise ValueError(f"not a duration: {text!r}")
    return int(m.group(1)) * UNITS[m.group(2)]
