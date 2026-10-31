"""How the leaderboard orders entries."""


def by_votes(entries):
    """The entries from fewest votes to most, ties by name A to Z."""
    return sorted(entries, key=lambda e: (e["votes"], e["name"]))
