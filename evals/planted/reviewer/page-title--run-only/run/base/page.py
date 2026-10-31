"""A page's title for the index."""


def title(text):
    """The first non-blank line after the header."""
    body = text.split("\n\n", 1)[1] if "\n\n" in text else text
    return next((line for line in body.splitlines() if line.strip()), "")
