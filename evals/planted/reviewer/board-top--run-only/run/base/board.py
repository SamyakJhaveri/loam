"""The leaderboard."""


def board(entries):
    """Names, most votes first, ties by name."""
    return [e["name"] for e in sorted(entries, key=lambda e: (-e["votes"], e["name"]))]
