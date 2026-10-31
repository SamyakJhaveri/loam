"""bin/transfer-coverage on temp manifests and targets: the ticket's done-check fixtures, a missing row whose
ticket file the target lacks, malformed manifests, and the shipped T1, T4 and T14 presence tests on planted
negatives (each once read a string anywhere, so a comment or an allow entry passed) and on passing fixtures."""

from __future__ import annotations

import pathlib
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin/transfer-coverage"
MANIFEST = ROOT / "bin/transfer-manifest.tsv"
HEADER = "# id\tkind\tdisposition\tcapability\tloam_source\tticket\tpresent"
T1 = "T1\tseed\tcarry\thook a\tabc\tF1\ttest -f \"$TARGET/.claude/hooks/a.sh\""
T2 = "T2\tplugin\tcarry\tplugin p\tdef\tF2\tgrep -q p \"$TARGET/plug/list\""
T3 = "T3\tuser-config\tdecline\tuser rule\tghi\t-\ttest -f \"$TARGET/absent\""
T4 = "T4\trunner\tcarry\trunner r\tjkl\t-\ttrue"
FLAGS = "seed/.agents/skills/catchup/red-flags.sh"
CHECK_LINES = ("python3 bin/shell_lint.py --root \"$ROOT\"\n"
               "step \"no em dash in Loam-owned text\"\npython3 bin/doc_paths.py --root \"$ROOT\"\n")


def real_row(tid: str) -> str:
    """The shipped manifest row for tid, so these tests run the test text that ships."""
    return next(line for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.split("\t")[0] == tid)


def seed_text(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class TransferCoverage(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = pathlib.Path(self.enterContext(tempfile.TemporaryDirectory()))

    def target(self, files: dict[str, str]) -> pathlib.Path:
        t = pathlib.Path(tempfile.mkdtemp(dir=self.tmp))
        for rel, text in files.items():
            (t / rel).parent.mkdir(parents=True, exist_ok=True)
            (t / rel).write_text(text, encoding="utf-8")
        return t

    def cover(self, rows: list[str], target: pathlib.Path, header: bool = True) -> tuple[int, list[str]]:
        m = pathlib.Path(tempfile.mkdtemp(dir=self.tmp)) / "m.tsv"
        m.write_text("\n".join(([HEADER] if header else []) + rows) + "\n", encoding="utf-8")
        p = subprocess.run([str(SCRIPT), "--manifest", str(m), "--target", str(target)],
                           capture_output=True, text=True)
        return p.returncode, (p.stdout + p.stderr).splitlines()

    def state(self, tid: str, files: dict[str, str]) -> str:
        rc, out = self.cover([real_row(tid)], self.target(files))
        if rc == 0 and f"ok {tid} " in "\n".join(out):
            return "present"
        if rc == 1 and any(line.startswith(f"MISSING {tid} ") for line in out):
            return "absent"
        return f"rc {rc}: {out}"

    def complete(self) -> pathlib.Path:
        return self.target({".claude/hooks/a.sh": "", "plug/list": "p\n"})

    @staticmethod
    def tagged(out: list[str], tag: str) -> list[str]:
        return [line for line in out if line.startswith(tag + " ")]

    def test_complete_covered_target_passes(self) -> None:
        rc, out = self.cover([T1, T2, T3], self.complete())
        self.assertEqual(rc, 0, out)
        self.assertIn("missing: 0", out)
        self.assertEqual(self.tagged(out, "MISSING") + self.tagged(out, "UNCOVERED"), [])

    def test_present_ticketless_row_is_uncovered(self) -> None:
        rc, out = self.cover([T1, T2, T3, T4], self.complete())
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.tagged(out, "UNCOVERED"), ["UNCOVERED T4 runner r"])
        self.assertEqual(self.tagged(out, "MISSING"), [])

    def test_removed_capability_is_missing_alone(self) -> None:
        t = self.complete()
        (t / "plug/list").unlink()
        rc, out = self.cover([T1, T2, T3], t)
        self.assertEqual(rc, 1, out)
        self.assertEqual(self.tagged(out, "MISSING"), ["MISSING T2 plugin p"])

    def test_missing_row_needs_its_ticket_file_in_the_target(self) -> None:
        t = self.target({".claude/hooks/a.sh": ""})
        rc, out = self.cover([T1, T2], t)
        self.assertEqual((rc, self.tagged(out, "UNCOVERED")), (1, ["UNCOVERED T2 plugin p"]), out)
        (t / "docs/tickets").mkdir(parents=True)
        (t / "docs/tickets/F2-x.md").write_text("", encoding="utf-8")
        rc, out = self.cover([T1, T2], t)
        self.assertEqual((rc, self.tagged(out, "UNCOVERED")), (1, []), out)
        self.assertIn("uncovered: 0", out)

    def test_short_row_and_comment_only_manifest_exit_2(self) -> None:
        self.assertEqual(self.cover(["T9\tseed\tcarry\tshort"], self.complete())[0], 2)
        self.assertEqual(self.cover(["# only a comment"], self.complete())[0], 2)
        self.assertEqual(self.cover([], self.complete(), header=False)[0], 2)

    def test_t1_reads_the_deny_list_and_a_forbidden_codex_rule(self) -> None:
        allow = ('{"permissions": {"allow": ["Read(~/.ssh/**)", "Bash(ssh-keygen:*)"], "deny": []}}\n')
        rules = seed_text("seed/.codex/rules/loam.rules")
        self.assertEqual(self.state("T1", {".claude/settings.json": allow, ".codex/rules/loam.rules": rules}),
                         "absent")
        allowed = 'prefix_rule(pattern = ["ssh-keygen"], decision = "allow")\n'
        settings = seed_text("seed/.claude/settings.json")
        self.assertEqual(self.state("T1", {".claude/settings.json": settings, ".codex/rules/loam.rules": allowed}),
                         "absent")
        self.assertEqual(self.state("T1", {".claude/settings.json": settings, ".codex/rules/loam.rules": rules}),
                         "present")

    def test_t4_reads_code_not_comments(self) -> None:
        rel = ".agents/skills/catchup/red-flags.sh"
        comments = "# Work in only one copy\n# --not --remotes\n# git worktree list --porcelain\n"
        self.assertEqual(self.state("T4", {rel: comments}), "absent")
        self.assertEqual(self.state("T4", {rel: seed_text(FLAGS)}), "present")

    def test_t14_needs_the_helpers_and_a_live_call(self) -> None:
        helpers = {"bin/shell_lint.py": "", "bin/doc_paths.py": ""}
        self.assertEqual(self.state("T14", {"bin/check": CHECK_LINES}), "absent")
        commented = "".join("# " + line + "\n" for line in CHECK_LINES.splitlines())
        self.assertEqual(self.state("T14", {"bin/check": commented, **helpers}), "absent")
        self.assertEqual(self.state("T14", {"bin/check": CHECK_LINES, **helpers}), "present")


if __name__ == "__main__":
    unittest.main()
