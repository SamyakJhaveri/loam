"""Find lines in a list of lines."""


def find(lines, needle):
    """The line numbers, counted from 1 as an editor does, of the lines holding needle."""
    return [n for n, line in enumerate(lines, 1) if needle in line]
