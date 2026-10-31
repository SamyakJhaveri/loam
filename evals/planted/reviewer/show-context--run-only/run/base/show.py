"""Print the lines that hold a word."""


def show(lines, needle):
    """Each matching line as "<n>: <line>", n counted from 1."""
    return [f"{n}: {line}" for n, line in enumerate(lines, 1) if needle in line]
