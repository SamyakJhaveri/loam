"""Print the lines that hold a word."""
from lines import find


def show(lines, needle):
    """Each matching line as "<n>: <line>"."""
    return [f"{n}: {lines[n - 1]}" for n in find(lines, needle)]
