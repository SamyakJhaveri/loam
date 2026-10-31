"""When a retry loop gives up."""


def should_stop(elapsed_s, limit):
    """True once elapsed_s seconds pass the limit, given like "30s"."""
    return elapsed_s > int(limit.rstrip("s"))
