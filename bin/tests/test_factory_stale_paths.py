"""bin/factory.d/stale_paths.py on planted streams: a failed Read is listed when the ticket names the same
file in any spelling (relative, `./`, absolute, `~/`, or through the `.claude -> seed/.claude` symlink
every Loam worktree has), and not when the ticket names a longer path, the file exists, or no Read failed."""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[2] / "bin/factory.d/stale_paths.py"


def stream(*reads: tuple[str, bool], bad_input: bool = False) -> str:
    uses = [{"type": "tool_use", "id": f"t{i}", "name": "Read", "input": {"file_path": p}} for i, (p, _) in enumerate(reads)]
    if bad_input:
        uses.append({"type": "tool_use", "id": "tx", "name": "Read", "input": "docs/gone.md"})
    results = [{"type": "tool_result", "tool_use_id": f"t{i}", "is_error": failed, "content": "x"}
               for i, (_, failed) in enumerate(reads)]
    return "".join(json.dumps(e) + "\n" for e in (
        {"type": "assistant", "message": {"content": uses}}, {"type": "user", "message": {"content": results}}))


class StalePaths(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = pathlib.Path(tmp.name, "home")
        self.wt = pathlib.Path(tmp.name, "wt")
        (self.wt / "seed/.claude/rules").mkdir(parents=True)
        (self.wt / "docs").mkdir()
        (self.wt / "docs/here.md").write_text("x")
        (self.wt / ".claude").symlink_to("seed/.claude")
        self.home.mkdir()

    def scan(self, ticket: str, *reads: tuple[str, bool], bad_input: bool = False) -> list[str]:
        (self.wt / "s.jsonl").write_text(stream(*reads, bad_input=bad_input))
        (self.wt / "t.md").write_text(ticket)
        p = subprocess.run([sys.executable, "-I", str(SCRIPT), "s.jsonl", "t.md", "AGENTS.md"], cwd=self.wt,
                           capture_output=True, text=True, env={**os.environ, "HOME": str(self.home)})
        self.assertEqual(p.returncode, 0, p.stderr)
        return p.stdout.splitlines()

    def test_named_spellings_are_listed(self) -> None:
        gone = f"{self.wt}/docs/gone.md"
        for ticket in ("Read `docs/gone.md` first.", "Read ./docs/gone.md.", f"Read {gone}.",
                       "See [gone](./docs/gone.md), then docs/gone.md:12."):
            with self.subTest(ticket=ticket):
                self.assertEqual(self.scan(ticket, (gone, True), (f"{self.wt}/docs/here.md", False)), ["docs/gone.md"])

    def test_symlinked_dir_either_spelling(self) -> None:
        self.assertEqual(self.scan("Read `.claude/rules/x.md`.", (f"{self.wt}/.claude/rules/x.md", True)),
                         [".claude/rules/x.md"])
        self.assertEqual(self.scan("Read `seed/.claude/rules/x.md`.", (f"{self.wt}/.claude/rules/x.md", True)),
                         [".claude/rules/x.md"])
        self.assertEqual(self.scan("Read `.claude/rules/x.md`.", (f"{self.wt}/seed/.claude/rules/x.md", True)),
                         ["seed/.claude/rules/x.md"])

    def test_worktree_reached_through_a_symlink(self) -> None:
        # As macOS /var -> /private/var: the Read spells the worktree through a link, cwd is the real path.
        link = self.home / "wt-link"
        link.symlink_to(self.wt)
        self.assertEqual(self.scan("Read `.claude/rules/x.md`.", (f"{link}/.claude/rules/x.md", True)),
                         [".claude/rules/x.md"])

    def test_names_with_spaces_and_punctuation(self) -> None:
        for name in ("docs/old guide.md", "docs/[slug].md", "docs/@scope/gone.md", "docs/$name.md"):
            with self.subTest(name=name):
                self.assertEqual(self.scan(f"Read `{name}`.", (f"{self.wt}/{name}", True)), [name])

    def test_parent_component_and_two_spellings(self) -> None:
        # .claude/.. is seed/, not the worktree root, and one missing file read two ways is listed once.
        self.assertEqual(self.scan("Read `seed/docs/here.md`.", (f"{self.wt}/.claude/../docs/here.md", True)),
                         ["seed/docs/here.md"])
        self.assertEqual(self.scan("Read `seed/.claude/rules/x.md`.", (f"{self.wt}/.claude/rules/x.md", True),
                                   (f"{self.wt}/seed/.claude/rules/x.md", True)), [".claude/rules/x.md"])

    def test_home_path_outside_worktree(self) -> None:
        self.assertEqual(self.scan("Read `~/notes/x.md`.", (f"{self.home}/notes/x.md", True)), [f"{self.home}/notes/x.md"])
        # Outside the worktree the Read's own spelling is kept, not the resolved one (macOS /var).
        (self.home / "link").symlink_to(self.home / "notes", target_is_directory=True)
        self.assertEqual(self.scan("Read `~/link/x.md`.", (f"{self.home}/link/x.md", True)), [f"{self.home}/link/x.md"])

    def test_not_listed(self) -> None:
        gone = f"{self.wt}/docs/gone.md"
        for ticket in ("Read docs/gone.md.bak.", "Read docs/gone.md~ first.", "Read x/docs/gone.md.", "Nothing named."):
            with self.subTest(ticket=ticket):
                self.assertEqual(self.scan(ticket, (gone, True)), [])
        self.assertEqual(self.scan("Read docs/gone.md.", (gone, False)), [], "a Read that did not fail")
        self.assertEqual(self.scan("Read docs/here.md.", (f"{self.wt}/docs/here.md", True)), [], "the file exists now")

    def test_malformed_read_input_is_skipped(self) -> None:
        self.assertEqual(self.scan("Read docs/gone.md.", (f"{self.wt}/docs/gone.md", True), bad_input=True),
                         ["docs/gone.md"])


if __name__ == "__main__":
    unittest.main()
