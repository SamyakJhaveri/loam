"""File reads shared by the reports."""


def read(path):
    """A file's raw bytes; the reports decode only what they print."""
    with open(path, "rb") as fh:
        return fh.read()
