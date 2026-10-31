"""Where cache keys live on disk, and the writer."""
import os


def key_path(root, key):
    """A key's file: a two-letter fan-out directory, then the key."""
    return os.path.join(root, key[:2], key)


def put(root, key, data):
    path = key_path(root, key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(data)
