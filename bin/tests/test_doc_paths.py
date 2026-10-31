"""bin/doc_paths.py on temp repos: the done-checks' planted dead path and dead link, and a baseline
with one live and one stale line. The real tree has no relative link and no stale line, so only
these cases keep link detection and the stale rule from silently matching nothing."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "bin/doc_paths.py"


def run(files: dict[str, str]) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        p = subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)], capture_output=True, text=True)
        return p.returncode, p.stdout


class DocPathsTest(unittest.TestCase):
    def test_flags_planted_dead_path_and_link(self) -> None:
        rc, out = run({
            "docs/a.md": "See `bin/missing-tool.sh` and `docs/a.md`.\n",
            "docs/b.md": "Read [gone](gone.md), [here](a.md) and [web](https://example.com/x.md).\n",
            "seed/docs/c.md.jinja": "Run `bin/also-missing.py`.\n",
            "docs/archive/old.md": "Old `bin/missing-tool.sh` and [gone](gone.md).\n",
        })
        self.assertEqual(rc, 1)
        fails = sorted(line.split(": ", 2)[1] for line in out.splitlines())
        self.assertEqual(fails, ["docs/a.md:1", "docs/b.md:1", "seed/docs/c.md.jinja:1"], out)
        self.assertIn("docs/b.md:1: gone.md ", out)

    def test_baseline_accepts_a_hit_and_refuses_a_stale_line(self) -> None:
        rc, out = run({
            "docs/a.md": "See `bin/missing-tool.sh`.\n",
            "bin/doc_paths_baseline.txt": "docs/a.md bin/missing-tool.sh\ndocs/a.md bin/nothing-here.sh\n",
        })
        self.assertEqual(rc, 1)
        self.assertEqual(out.splitlines(), [
            "FAIL: bin/doc_paths_baseline.txt:2: docs/a.md bin/nothing-here.sh no longer hits; delete the line"])


if __name__ == "__main__":
    unittest.main()
