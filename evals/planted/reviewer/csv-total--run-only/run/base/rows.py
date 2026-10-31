"""Read a CSV file into a list of dicts, one per row."""
import csv


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))
