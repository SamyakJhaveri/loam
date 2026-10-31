"""bin/doc_paths.py on temp repos: the done-checks' planted dead path and dead link, the fence, link
and existence rules, and a baseline keyed on (doc, path). The real tree has no relative link and no
stale line, so only these cases keep link detection and the stale rule from silently matching nothing."""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "bin/doc_paths.py"


def run(files: dict[str, str], links: dict[str, str] | None = None, deleted: tuple[str, ...] = ()) -> tuple[int, str]:
    """Plant files and symlinks, git add them, remove the `deleted` ones from disk, and run the script."""
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for rel, text in files.items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(text, encoding="utf-8")
        for rel, target in (links or {}).items():
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            os.symlink(target, root / rel)
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        for rel in deleted:
            (root / rel).unlink()
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

    def test_passes_fenced_code_and_live_targets(self) -> None:
        rc, out = run({
            "docs/a.md": (
                "```\n`bin/fenced.sh`\n```\n"
                "  ```sh\n`bin/indented-fence.sh`\n  ```\n"
                "~~~\n`bin/tilde.sh`\n~~~\n"
                "Optional `.claude/rules/` and linked `.claude/skills/x/SKILL.md`.\n"
                "Links [s](b.md#part), [d](../bin), [t](t.md), [n](guide%20name.md), [p](guide(v2).md).\n"
                "Code `[c](gone.md)` is not a link.\n"),
            "docs/b.md": "", "docs/t.md.jinja": "", "docs/guide name.md": "", "docs/guide(v2).md": "",
            "bin/tool.sh": "", "seed/.agents/skills/x/SKILL.md": "",
        }, links={"seed/.claude/skills/x": "../../.agents/skills/x", ".claude": "seed/.claude"})
        self.assertEqual((rc, out), (0, ""))

    def test_flags_dead_targets_past_fences_and_on_disk(self) -> None:
        rc, out = run({
            "docs/a.md": "````md\n```\n`bin/in-long-fence.sh`\n````\nAfter `bin/after-fence.sh` and [sp](<a b.md>).\n",
            "docs/b.md": "See `bin/deleted.sh`.\n", "bin/deleted.sh": "",
        }, deleted=("bin/deleted.sh",))
        self.assertEqual(rc, 1)
        fails = [line.split(" is ", 1)[0] for line in out.splitlines()]
        self.assertEqual(fails, ["FAIL: docs/a.md:5: bin/after-fence.sh", "FAIL: docs/a.md:5: a b.md",
                                 "FAIL: docs/b.md:1: bin/deleted.sh"], out)

    def test_baseline_keys_on_doc_and_path_and_only_shrinks(self) -> None:
        rc, out = run({
            "docs/a.md": "See `bin/missing-tool.sh`.\n",
            "docs/c.md": "Also `bin/missing-tool.sh`.\n",
            "docs/other.md": "Nothing here.\n",
            "bin/doc_paths_baseline.txt": "docs/a.md bin/missing-tool.sh \ndocs/other.md bin/missing-tool.sh\n"
                                          "docs/a.md bin/nothing-here.sh\ndocs/a.md bin/missing-tool.sh\n",
        })
        self.assertEqual(rc, 1)
        self.assertEqual(out.splitlines(), [
            "FAIL: bin/doc_paths_baseline.txt:4: docs/a.md bin/missing-tool.sh duplicates line 1; delete the line",
            "FAIL: docs/c.md:1: bin/missing-tool.sh is not tracked by git (fix the path, or git add the file)",
            "FAIL: bin/doc_paths_baseline.txt:2: docs/other.md bin/missing-tool.sh no longer hits; delete the line",
            "FAIL: bin/doc_paths_baseline.txt:3: docs/a.md bin/nothing-here.sh no longer hits; delete the line"])


if __name__ == "__main__":
    unittest.main()
