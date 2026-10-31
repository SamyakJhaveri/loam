"""Line counts for the size report."""
from fileio import read


def count_lines(path):
    return len(read(path).splitlines())
