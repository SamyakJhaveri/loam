"""The header block at the top of a page."""


def parse_header(text):
    """The `Key: value` lines before the first blank line, as a dict with the keys lowercased."""
    header = {}
    for line in text.splitlines():
        if not line.strip():
            break
        key, sep, value = line.partition(":")
        if sep:
            header[key.strip().lower()] = value.strip()
    return header
