"""The leaderboard."""
from rank import sort_key


def board(entries):
    """Names, most votes first."""
    return [e["name"] for e in sorted(entries, key=sort_key)]
