"""How the leaderboard orders entries."""


def sort_key(entry):
    """Ascending order on this key puts the most votes first, then names A to Z."""
    return (-entry["votes"], entry["name"])
