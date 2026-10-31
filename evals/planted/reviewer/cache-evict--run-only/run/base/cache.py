"""Read the cache."""
from store import key_path


def get(root, key):
    """A key's data, or None when the cache has no such key."""
    try:
        with open(key_path(root, key), encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return None
