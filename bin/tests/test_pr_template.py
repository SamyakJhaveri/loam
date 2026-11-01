"""The PR template's Proof section asks a seed/ or copier.yml PR for verify-loam or a waiver (#293)."""

from __future__ import annotations

import pathlib
import unittest

TEMPLATE = pathlib.Path(__file__).resolve().parents[2] / ".github/pull_request_template.md"


class PrTemplate(unittest.TestCase):
    def test_proof_asks_for_verify_loam(self) -> None:
        proof = TEMPLATE.read_text().split("## Proof\n", 1)[1].split("\n## ", 1)[0]
        # Code spans keep the <placeholders> visible; bare, GitHub strips them as HTML tags.
        for form in (r"`verify-loam: <[^`<>]+>`", r"`verify-loam waived: <[^`<>]+>`"):
            self.assertRegex(proof, form)
        for needle in ("seed/", "copier.yml"):
            self.assertIn(needle, proof)

    def test_rest_kept(self) -> None:
        lines = TEMPLATE.read_text().splitlines()
        for line in ("## What and why", "## Proof", "Port: seed | runner | Loam-only (see docs/SYNC.md)"):
            self.assertIn(line, lines)


if __name__ == "__main__":
    unittest.main()
