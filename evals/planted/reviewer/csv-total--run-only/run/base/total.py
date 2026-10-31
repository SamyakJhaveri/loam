"""Sum one column of a CSV file: python3 total.py <file> <column>."""
import sys

from rows import read_rows


def total(path, column):
    return sum(float(row[column]) for row in read_rows(path))


if __name__ == "__main__":
    print(total(sys.argv[1], sys.argv[2]))
