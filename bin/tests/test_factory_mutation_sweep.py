"""The mutation sweep after a judge pass (#618; docs/factory/LOOP.md, Mutation sweep).

SweepTests drives bin/factory.d/mutation_sweep.py on scratch repositories whose one commit after an empty base adds
the files under test: each operator in both languages, the lines that give no edit (comments, strings, here-documents,
test files, tests and fixtures directories), an edit that does not parse, an edit that never ends, a same-size edit, a
red unedited run, the order, and a bad base. FactoryRunTests runs `bin/factory -C <target> run` on a file ticket with
a scripted `claude` whose worker copies the files of its round into the worktree and whose graders pass, so only the
sweep can fail a round: survivors reach the next worker round once, a relaunch keeps that one block, and a failed
helper stops the run. Every subprocess gets an explicit environment: a scratch HOME and TMPDIR and a git identity.
"""

from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[2]
HELPER = ROOT / "bin/factory.d/mutation_sweep.py"
PASSING = "def test_nothing():\n    pass\n"

CALC = """def over(n, limit):
    # n > limit means over
    if n > limit:
        return True
    note = "n == limit is not over"
    return False


def same(a, b):
    return a == b
"""
GATE = """#!/usr/bin/env bash
# [ "$1" = 5 ] would be wrong here
if [ "$1" -gt 3 ]; then echo big; else echo small; fi
cat > /dev/null <<END
[ 1 -eq 1 ] && exit 0
END
"""
WEAK = """import pathlib, subprocess
from calc import over, same


def gate(n):
    return subprocess.run(["bash", str(pathlib.Path(__file__).parent / "gate.sh"), str(n)], capture_output=True, text=True).stdout


def test_over():
    assert over(5, 1)
    assert gate(5) == "big\\n"
"""
STRONG = WEAK.replace("    assert over(5, 1)\n", "    assert over(5, 1) is True\n    assert over(1, 5) is False\n"
                      "    assert over(3, 3) is False\n    assert same(1, 1) is True\n    assert same(1, 2) is False\n"
                      ).replace('    assert gate(5) == "big\\n"\n', '    assert gate(5) == "big\\n"\n    assert gate(1) == "small\\n"\n')
WEAK_RECORDS = ["calc.py:10:drop:survived", "calc.py:10:flip:survived", "calc.py:3:flip:killed",
                "calc.py:3:force-true:survived", "calc.py:4:drop:killed", "calc.py:6:drop:survived",
                "gate.sh:3:flip:killed", "gate.sh:3:force-true:survived"]
ALL_KILLED = sorted(r.rsplit(":", 1)[0] + ":killed" for r in WEAK_RECORDS)
SURVIVORS = ["calc.py:3 mutation survived (force-true)", "calc.py:6 mutation survived (drop)",
             "calc.py:10 mutation survived (flip)", "calc.py:10 mutation survived (drop)",
             "gate.sh:3 mutation survived (force-true)"]


def scratch_env(top: pathlib.Path) -> dict[str, str]:
    (top / "h").mkdir(exist_ok=True)
    return {"HOME": str(top / "h"), "TMPDIR": str(top), "PATH": os.environ["PATH"], "LANG": "C.UTF-8",
            "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}


def git(cwd: pathlib.Path, env: dict[str, str], *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout.strip()


def records(result: dict) -> list[str]:
    return sorted(f"{m['path']}:{m['line']}:{m['operator']}:{m['result']}" for m in result["mutants"])


class SweepTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        self.env = scratch_env(self.top)
        self.wt = self.top / "r"

    def commit(self, files: dict[str, str]) -> str:
        """The base sha (an empty first commit) after committing files on top of it."""
        if not self.wt.exists():
            self.wt.mkdir()
            git(self.wt, self.env, "init", "-q", "-b", "main")
            git(self.wt, self.env, "commit", "-q", "--allow-empty", "-m", "base")
        for name, text in files.items():
            (self.wt / name).parent.mkdir(parents=True, exist_ok=True)
            (self.wt / name).write_text(text)
        git(self.wt, self.env, "add", "-A")
        git(self.wt, self.env, "commit", "-q", "-m", "work")
        return git(self.wt, self.env, "rev-list", "--max-parents=0", "HEAD")

    def sweep(self, files: dict[str, str], first_timeout: str = "600") -> dict:
        base = self.commit(files)
        out = self.top / "out.json"
        out.unlink(missing_ok=True)
        r = subprocess.run(["python3", "-I", str(HELPER), str(self.wt), base, str(out), first_timeout], env=self.env,
                           capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(out.read_text())

    def edits(self, files: dict[str, str]) -> list[tuple[int, str, str]]:
        """(line, operator, edited line) of each edit, after a sweep whose test passes whatever the code does."""
        result = self.sweep({**files, "test_ok.py": PASSING})
        self.assertEqual((result["reason"], result["tests"]), (None, ["test_ok.py"]))
        self.assertEqual({m["result"] for m in result["mutants"]}, {"survived"})
        return sorted((m["line"], m["operator"], m["after"]) for m in result["mutants"])

    def test_python_comparisons_conditions_and_statements(self) -> None:
        self.assertEqual(self.edits({"a.py": "def f(a, b):\n    if a == b:\n        return 1\n    while a != b:\n"
                                             "        break\n    assert a < b\n"}),
                         [(2, "flip", "if a != b:"), (2, "force-true", "if (a == b) or True:"), (3, "drop", "pass"),
                          (4, "flip", "while a == b:"), (4, "force-true", "while (a != b) or True:"),
                          (5, "drop", "pass"), (6, "drop", "pass"), (6, "flip", "assert a >= b")])

    def test_python_orderings_elif_continue_and_raise(self) -> None:
        self.assertEqual(self.edits({"b.py": "def g(a, b, xs):\n    for x in xs:\n        if x >= a:\n"
                                             "            continue\n        elif x > b:\n"
                                             "            raise ValueError(x)\n    return a <= b\n"}),
                         [(3, "flip", "if x < a:"), (3, "force-true", "if (x >= a) or True:"), (4, "drop", "pass"),
                          (5, "flip", "elif x <= b:"), (5, "force-true", "elif (x > b) or True:"), (6, "drop", "pass"),
                          (7, "drop", "pass"), (7, "flip", "return a > b")])

    def test_python_membership_identity_and_a_statement_over_two_lines(self) -> None:
        # A for clause's `in` is no comparison; the comprehension's filter is. The two-line return drops whole.
        self.assertEqual(self.edits({"c.py": "def h(a, xs):\n    y = a in xs\n    z = a not in xs\n"
                                             "    w = a is None\n    v = a is not None\n"
                                             "    u = [x for x in xs if x in a]\n    return (\n        y, z, w, v, u)\n"}),
                         [(2, "flip", "y = a not in xs"), (3, "flip", "z = a in xs"), (4, "flip", "w = a is not None"),
                          (5, "flip", "v = a is None"), (6, "flip", "u = [x for x in xs if x not in a]"),
                          (7, "drop", "pass")])

    def test_bash_tests_headers_and_leading_tests(self) -> None:
        self.assertEqual(self.edits({"a.sh": '#!/usr/bin/env bash\nf() {\n  if [ "$1" -eq 1 ]; then echo one; fi\n'
                                             '  while [ "$2" -lt 5 ]; do break; done\n  [ "$1" = a ] && exit 4\n'
                                             '  [[ $1 != b ]] || return 5\n}\n'}),
                         [(3, "flip", 'if [ "$1" -ne 1 ]; then echo one; fi'),
                          (3, "force-true", 'if [ "$1" -eq 1 ] || true; then echo one; fi'),
                          (4, "flip", 'while [ "$2" -ge 5 ]; do break; done'),
                          (4, "force-true", 'while [ "$2" -lt 5 ] || true; do break; done'),
                          (5, "flip", '[ "$1" != a ] && exit 4'), (5, "force-true", '[ "$1" = a ] || true && exit 4'),
                          (6, "flip", "[[ $1 = b ]] || return 5"), (6, "force-true", "[[ $1 != b ]] || true || return 5")])

    def test_bash_elif_and_dropped_statements(self) -> None:
        # No .sh suffix: the #!/bin/sh line makes it bash.
        self.assertEqual(self.edits({"bin/g": '#!/bin/sh\ng() {\n  if [ "$1" -ne 1 ]; then\n    return 2\n'
                                              '  elif [ "$1" -gt 2 ]; then\n    continue\n  fi\n  exit 0\n}\n'}),
                         [(3, "flip", 'if [ "$1" -eq 1 ]; then'), (3, "force-true", 'if [ "$1" -ne 1 ] || true; then'),
                          (4, "drop", ":"), (5, "flip", 'elif [ "$1" -le 2 ]; then'),
                          (5, "force-true", 'elif [ "$1" -gt 2 ] || true; then'), (6, "drop", ":"), (8, "drop", ":")])

    def test_bash_remaining_comparisons_and_break(self) -> None:
        self.assertEqual(self.edits({"c.sh": 'for i in 1 2; do\n  [ "$i" -ge 3 ] && break\n'
                                             '  [ "$i" -le 3 ] || continue\n  [[ $i == 3 ]] && echo\n  break\ndone\n'}),
                         [(2, "flip", '[ "$i" -lt 3 ] && break'), (2, "force-true", '[ "$i" -ge 3 ] || true && break'),
                          (3, "flip", '[ "$i" -gt 3 ] || continue'),
                          (3, "force-true", '[ "$i" -le 3 ] || true || continue'),
                          (4, "flip", "[[ $i != 3 ]] && echo"), (4, "force-true", "[[ $i == 3 ]] || true && echo"),
                          (5, "drop", ":")])

    def test_comments_strings_and_here_documents_give_no_edit(self) -> None:
        py = ('# if a == b: return 1\ndef k(a, b):\n    """while a != b:\n    return a < b\n    """\n'
              '    s = "a == b"\n    t = f"{a}: x is y"\n')
        sh = ('#!/usr/bin/env bash\n# [ "$1" -eq 1 ] && exit 1\necho \'[ "$1" -eq 1 ] && exit 1\'\n'
              'echo "[ \\"$1\\" = x ] || return 2"\njq -n \'if 1 == 2 then 0 else 1 end\'\n'
              'x="multi\n[ 1 -eq 1 ] && exit 0\nline"\ncat <<EOF\n[ 1 -eq 1 ] && exit 0\nEOF\n'
              "cat <<-'END'\n\texit 3\n\tEND\ngrep x <<< \"a\"\necho $(( 1 << 2 ))\n")
        result = self.sweep({"k.py": py, "s.sh": sh, "test_ok.py": PASSING})
        self.assertEqual((result["mutants"], result["reason"]),
                         ([], "no added bash or Python code line outside tests and fixtures gives an edit"))

    def test_python_edits_that_cannot_change_behavior_are_skipped(self) -> None:
        # A function's last `return` or `return None`, a last `return 0` of a function whose every call is the
        # argument of sys.exit or SystemExit, and the main guard's force-true give no edit; an earlier return, a
        # last `return 0` whose value is used, a return of False, and the guard's flip do.
        self.assertEqual(self.edits({"m.py": 'import sys\n\n\ndef main():\n    if sys.argv:\n        return 1\n'
                                             '    print()\n    return 0\n\n\ndef f():\n    return\n\n\n'
                                             'def g(x):\n    return None\n\n\ndef u():\n    return 0\n\n\n'
                                             'def k():\n    return False\n\n\nif __name__ == "__main__":\n'
                                             '    sys.exit(main())\nif __name__ == "__main__":\n'
                                             '    raise SystemExit(main())\ny = u() + 1\n'}),
                         [(5, "force-true", "if (sys.argv) or True:"), (6, "drop", "pass"), (20, "drop", "pass"),
                          (24, "drop", "pass"), (27, "flip", 'if __name__ != "__main__":'),
                          (29, "flip", 'if __name__ != "__main__":'), (30, "drop", "pass")])

    def test_bash_edits_that_cannot_change_behavior_are_skipped(self) -> None:
        # The file's last `exit 0` gives no edit; an exit in a function or before other code does.
        self.assertEqual(self.edits({"m.sh": '#!/usr/bin/env bash\nf() {\n  exit 0\n}\n[ "$1" = a ] && exit 0\n'
                                             'exit 0\n# end\n'}),
                         [(3, "drop", ":"), (5, "flip", '[ "$1" != a ] && exit 0'),
                          (5, "force-true", '[ "$1" = a ] || true && exit 0')])

    def test_a_quoted_here_document_word_is_read_as_the_shell_reads_it(self) -> None:
        # In single quotes a backslash is literal, so `AB` does not end the first body; in double quotes a space is
        # part of the word, so `C D` ends the second. Only the exit after it is code.
        self.assertEqual(self.edits({"q.sh": "#!/usr/bin/env bash\ncat <<'A\\B'\n[ 1 -eq 1 ] && exit 0\nAB\nexit 1\n"
                                             'A\\B\ncat <<"C D"\nexit 2\nC D\nexit 3\n'}),
                         [(10, "drop", ":")])

    def test_test_files_tests_and_fixtures_give_no_edit(self) -> None:
        code = "def f(a, b):\n    return a == b\n"
        result = self.sweep({"tests/helper.py": code, "x/fixtures/f.py": code, "test_ok.py": PASSING + code,
                             "ok_test.py": PASSING + code})
        self.assertEqual((result["tests"], result["mutants"]), (["ok_test.py", "test_ok.py"], []))

    def test_no_committed_test_runs_no_edit(self) -> None:
        result = self.sweep({"a.py": "def f(a, b):\n    return a == b\n"})
        self.assertEqual((result["tests"], result["mutants"], result["reason"], result["baseline_sec"]),
                         ([], [], "no committed test in the diff", None))

    def test_a_bash_drop_takes_its_redirections(self) -> None:
        # The & or | of a redirection does not end the dropped words; the && after it does.
        self.assertEqual(self.edits({"r.sh": "f() {\n  return 1 >&2\n}\ng() {\n  exit 2 2>&1 && echo\n"
                                             "  exit 3 &> /dev/null\n  exit 4 >| /dev/null\n}\n"}),
                         [(2, "drop", ":"), (5, "drop", ": && echo"), (6, "drop", ":"), (7, "drop", ":")])

    def test_an_edit_that_does_not_parse_is_discarded(self) -> None:
        # Dropping the return leaves `:; echo 3)`, which bash -n rejects; the exit's drop parses and runs.
        self.assertEqual(self.edits({"d.sh": "f() {\n  return $(true; echo 3)\n}\nexit 1\n"}), [(4, "drop", ":")])

    def test_red_unedited_tests_run_no_edit(self) -> None:
        result = self.sweep({"a.py": "def f(a, b):\n    return a == b\n", "test_red.py": "def test_red():\n    assert 0\n"})
        self.assertEqual((result["mutants"], result["reason"]), ([], "the committed tests fail unedited (pytest exit 1)"))
        self.assertIsNotNone(result["baseline_sec"])

    def loops_left(self, name: str = "loop.sh") -> list[tuple[int, str]]:
        ps = subprocess.run(["ps", "-eo", "pid=,args="], capture_output=True, text=True, check=True).stdout
        return [(int(pid), a) for pid, a in (ln.split(None, 1) for ln in ps.splitlines() if " " in ln.strip())
                if str(self.wt / name) in a]

    def hang(self, popen_args: str) -> None:
        loop = '#!/usr/bin/env bash\ni=0\nwhile [ "$i" -lt "$1" ]; do i=$((i + 1)); done\necho "$i"\n'
        test = ("import pathlib, subprocess\n\n\ndef test_count():\n"
                "    out = subprocess.run(['bash', str(pathlib.Path(__file__).parent / 'loop.sh'), '3'],"
                f" capture_output=True, text=True{popen_args}).stdout\n    assert out == '3\\n'\n")
        self.addCleanup(lambda: [os.kill(pid, 9) for pid, _ in self.loops_left()])
        result = self.sweep({"loop.sh": loop, "loop_test.py": test})
        self.assertEqual(records(result), ["loop.sh:3:flip:killed", "loop.sh:3:force-true:killed"])
        self.assertEqual(result["timeout_sec"], round(2 * result["baseline_sec"] + 10, 2))
        hung = [m for m in result["mutants"] if m["timed_out"]]
        self.assertEqual([m["operator"] for m in hung], ["force-true"])
        self.assertGreaterEqual(hung[0]["seconds"], result["timeout_sec"])
        self.assertLessEqual(hung[0]["seconds"], result["timeout_sec"] + 5)
        left = []
        for _ in range(20):  # KILL is asynchronous; allow it 2 s to land
            left = self.loops_left()
            if not left:
                break
            time.sleep(0.1)
        self.assertEqual(left, [])

    @unittest.skipUnless(sys.platform.startswith("linux"), "the sweep reads /proc on Linux only")
    def test_a_process_whose_name_is_not_utf8_does_not_stop_the_sweep(self) -> None:
        # The orphan search after each run reads every process's /proc/<pid>/stat, whose name may be any bytes.
        named = subprocess.Popen(["python3", "-c", "import ctypes, sys, time\n"
                                  "ctypes.CDLL(None).prctl(15, b'bad-\\xff-name', 0, 0, 0)\nprint(flush=True)\n"
                                  "time.sleep(300)\n"], stdout=subprocess.PIPE)
        self.addCleanup(named.wait)
        self.addCleanup(named.kill)
        named.stdout.readline()
        self.assertEqual(pathlib.Path(f"/proc/{named.pid}/comm").read_bytes(), b"bad-\xff-name\n")
        result = self.sweep({"a.py": "def f(a, b):\n    return a == b\n", "test_ok.py": PASSING})
        self.assertEqual(records(result), ["a.py:2:drop:survived", "a.py:2:flip:survived"])

    @unittest.skipUnless(sys.platform.startswith("linux"), "the sweep is a child subreaper on Linux only")
    def test_a_deep_chain_of_orphans_is_killed_whole(self) -> None:
        # The test leaves a chain of 200 bash processes, each waiting on the next, in a session of its own; killing
        # one level at a time would outlast the 5 s the sweep allows itself.
        chain = ('#!/usr/bin/env bash\nif [ "$1" -gt 0 ]; then bash "$0" $(($1 - 1)); echo; else\n'
                 '  touch "$(dirname "$0")/leaf"; while :; do sleep 1; done; fi\n')
        test = ("import pathlib, subprocess, time\n\n\ndef test_chain():\n    d = pathlib.Path(__file__).parent\n"
                "    (d / 'fixtures/leaf').unlink(missing_ok=True)\n"
                "    subprocess.Popen(['bash', str(d / 'fixtures/chain.sh'), '200'], start_new_session=True)\n"
                "    while not (d / 'fixtures/leaf').exists():\n        time.sleep(0.05)\n")
        name = "fixtures/chain.sh"

        def kill_left() -> None:
            for _ in range(10):
                for pid, _a in self.loops_left(name):
                    os.kill(pid, 9)
                time.sleep(0.1)

        self.addCleanup(kill_left)
        result = self.sweep({"fixtures/chain.sh": chain, "chain_test.py": test, "a.py": "x = 1 == 2\n"})
        self.assertEqual(records(result), ["a.py:1:flip:survived"])
        left = []
        for _ in range(20):
            left = self.loops_left(name)
            if not left:
                break
            time.sleep(0.1)
        self.assertEqual(len(left), 0)

    def test_an_edit_that_hangs_is_killed_with_its_whole_group(self) -> None:
        # The force-true edit makes the while loop endless in a bash child of the test, which pytest's own death would
        # leave spinning; the group KILL at twice the unedited run plus 10 s must take it too.
        self.hang("")

    @unittest.skipUnless(sys.platform.startswith("linux"), "the sweep is a child subreaper on Linux only")
    def test_an_edit_that_hangs_in_a_session_of_its_own_is_killed(self) -> None:
        # The bash child starts its own session, out of the group the run's KILL reaches; the sweep, as the child
        # subreaper, gets it as an orphan when pytest dies and must KILL it too.
        self.hang(", start_new_session=True")

    def test_a_same_size_edit_reads_no_cached_bytecode(self) -> None:
        # The flip keeps the file's size. Its write keeps the source's mtime, as a write in the same second would, so
        # the edit would import the bytecode the unedited run cached, and survive, if any run wrote bytecode.
        base = self.commit({"calc.py": "same = lambda a, b: a == b\n",
                            "test_calc.py": "from calc import same\n\n\ndef test_same():\n    assert same(1, 1)\n"})
        spec = importlib.util.spec_from_file_location("mutation_sweep", HELPER)
        sweep = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sweep)
        write = sweep.write

        def same_second(path: pathlib.Path, text: str) -> None:
            st = path.stat()
            write(path, text)
            os.utime(path, ns=(st.st_atime_ns, st.st_mtime_ns))

        out = self.top / "out.json"
        with mock.patch.object(sweep, "write", same_second), mock.patch.dict(os.environ, self.env, clear=True):
            self.assertEqual(sweep.main([str(self.wt), base, str(out), "600"]), 0)
        self.assertEqual(records(json.loads(out.read_text())), ["calc.py:1:flip:killed"])

    def test_an_unchanged_line_gets_the_same_edits_wherever_it_moves(self) -> None:
        # Eleven edits, of which the first 8 by sha256 run; three lines added above move every line down.
        code = ('#!/bin/sh\nif [ "$1" -ne 1 ]; then\n  echo no\nelif [ "$1" -gt 2 ]; then\n  return 2\nfi\n'
                '[ "$1" -ge 3 ] && echo ge\n[ "$1" -le 3 ] || echo le\n[ "$1" == 3 ] && echo eq\nexit 0\n')
        first = self.sweep({"o.sh": code, "test_ok.py": PASSING})
        moved = self.sweep({"o.sh": "#!/bin/sh\n\n# moved\n" + code.split("\n", 1)[1]})
        self.assertEqual(len(first["mutants"]), 8)
        self.assertEqual([(m["line"] + 2, m["operator"], m["before"]) for m in first["mutants"]],
                         [(m["line"], m["operator"], m["before"]) for m in moved["mutants"]])

    def test_lines_added_apart_keep_their_numbers_under_an_inter_hunk_context(self) -> None:
        # A diff.interHunkContext would merge the two one-line hunks, and the context lines between them would not
        # be counted, so the second added line would be numbered 2.
        self.commit({"test_ok.py": PASSING, "a.sh": "x=1\ny=2\nz=3\nw=4\n"})
        base = git(self.wt, self.env, "rev-parse", "HEAD")
        git(self.wt, self.env, "config", "diff.interHunkContext", "5")
        self.commit({"a.sh": "[ 1 -eq 1 ] && x=1\ny=2\nz=3\n[ 1 -eq 1 ] && w=4\n", "test_ok.py": PASSING + "\n"})
        out = self.top / "out.json"
        r = subprocess.run(["python3", "-I", str(HELPER), str(self.wt), base, str(out), "600"], env=self.env,
                           capture_output=True, text=True, timeout=300, check=False)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted({m["line"] for m in json.loads(out.read_text())["mutants"]}), [1, 4])

    def test_a_bad_base_exits_non_zero_and_writes_nothing(self) -> None:
        self.commit({"a.py": "x = 1\n"})
        out = self.top / "out.json"
        r = subprocess.run(["python3", "-I", str(HELPER), str(self.wt), "0" * 40, str(out), "600"], env=self.env,
                           capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual((r.returncode, out.exists()), (2, False), r.stderr)


# The scripted claude: the version probe; a worker that copies $d/round-<n>/ into its worktree, or writes note.txt
# when the test gave that round no files, and commits; a judge that passes every row and a reviewer with no finding.
# With $d/stop-once, the first reviewer call drops FACTORY_STOP in the run dir, as an operator's stop after the sweep.
CLAUDE = r"""#!/bin/sh
[ "$1" = --version ] && { echo "2.1.300 (Claude Code)"; exit 0; }
[ "$1" = -p ] || exit 1
d=$(dirname "$0")/..
case "$*" in
  *json-schema*rows*) cat > /dev/null; cat "$d/judge.json"; exit 0 ;;
  *json-schema*)
    cat > /dev/null
    if [ -e "$d/stop-once" ]; then
      rm -f "$d/stop-once"
      for r in "$d"/h/.local/state/loam-factory/runs/o__r/mprobe/*/; do : > "$r/FACTORY_STOP"; done
    fi
    cat "$d/review.json"; exit 0 ;;
esac
n=$(( $(cat "$d/rounds" 2> /dev/null || echo 0) + 1 )); echo "$n" > "$d/rounds"
cat > "$d/prompt-$n.txt"
if [ -d "$d/round-$n" ]; then cp -R "$d/round-$n/." .; else echo "$n" > note.txt; fi
git add -A > /dev/null 2>&1; git commit -qm "round $n" > /dev/null 2>&1
cat "$d/worker.json"
"""
ENVELOPE = {"type": "result", "subtype": "success", "is_error": False, "total_cost_usd": 0, "num_turns": 1}
JUDGE = {"verdict": "pass", "rows": {"correct": "pass", "verified": "pass", "honest": "pass"}, "fixes": [],
         "backlog": [], "evidence": {}}
TICKET = """# mutation probe
Brief: x
Blocked by: none

## Goal and why
g

## Do not touch
The standing list.

## Out of scope
o

## Done checks
```done-checks
```

## Worker
worker: claude
codex-review: no
effort: low
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 5 turns

## Decisions
none
"""


class FactoryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.top = pathlib.Path(tmp.name)
        env = scratch_env(self.top)
        self.co = self.top / "co"
        origin = self.top / "github.com/o/r.git"
        origin.mkdir(parents=True)
        git(origin, env, "init", "-q", "--bare")
        (self.co / "bin").mkdir(parents=True)
        (self.co / "docs/factory").mkdir(parents=True)
        (self.co / "bin/check").write_text("#!/bin/sh\nexit 0\n")
        (self.co / "bin/check").chmod(0o755)
        (self.co / "docs/factory/STANDING.md").write_text("## Standing do-not-touch list\n\n- bin/check\n")
        git(self.co, env, "init", "-q", "-b", "main")
        git(self.co, env, "remote", "add", "origin", str(origin))
        git(self.co, env, "add", "-A")
        git(self.co, env, "commit", "-qm", "base")
        git(self.co, env, "push", "-q", "-u", "origin", "main")
        stubs = self.top / "bin"
        stubs.mkdir()
        (stubs / "claude").write_text(CLAUDE)
        (stubs / "claude").chmod(0o755)
        for name, reply in (("judge", json.dumps(JUDGE)), ("review", '{"verdict":"merge","findings":[]}'),
                            ("worker", "CLAIM: done")):
            (self.top / f"{name}.json").write_text(json.dumps({**ENVELOPE, "result": reply}) + "\n")
        self.ticket = self.top / "mprobe.md"
        self.ticket.write_text(TICKET)
        # bin/tests/fixtures/systemd holds #578's stand-ins once it lands, as the ticket's done checks put it on PATH.
        env["PATH"] = f"{stubs}:{ROOT / 'bin/tests/fixtures/systemd'}:{env['PATH']}"
        self.env = env

    def round_files(self, n: int, test: str | None) -> None:
        d = self.top / f"round-{n}"
        d.mkdir()
        (d / "calc.py").write_text(CALC)
        (d / "gate.sh").write_text(GATE)
        if test is not None:
            (d / "test_calc.py").write_text(test)

    def launch(self) -> int:
        r = subprocess.run([str(ROOT / "bin/factory"), "-C", str(self.co), "run", str(self.ticket)], cwd=ROOT,
                           env=self.env, capture_output=True, text=True, timeout=300, check=False)
        with (self.top / "run.out").open("a") as f:
            f.write(r.stdout + r.stderr)
        return r.returncode

    def run_dir(self) -> pathlib.Path:
        (run,) = (self.top / "h/.local/state/loam-factory/runs/o__r/mprobe").glob("*/")
        return run

    def worker_rounds(self) -> int:
        return int((self.top / "rounds").read_text())

    def sweep_records(self, n: int) -> list[str]:
        return records(json.loads((self.run_dir() / f"round-{n}.mutation.json").read_text()))

    def body(self) -> str:
        return (self.run_dir() / "pr-body.md").read_text()

    def findings(self, n: int) -> list[str]:
        """The blocking-finding lines of worker round n's prompt."""
        prompt = (self.top / f"prompt-{n}.txt").read_text()
        return [ln for ln in prompt.split("Blocking findings, verbatim:", 1)[1].splitlines() if ln.startswith("- ")]

    def assert_survivors_found_once(self, n: int) -> None:
        lines = self.findings(n)
        self.assertEqual(len(lines), 5, lines)
        for survivor in SURVIVORS:
            self.assertEqual(sum(ln.startswith(f"- {survivor}: ") for ln in lines), 1, (survivor, lines))
        self.assertIn("- calc.py:3 mutation survived (force-true): `if (n > limit) or True:` in place of "
                      "`if n > limit:`, and test_calc.py still pass. Fix: add or tighten a committed test that fails "
                      "on this edit (if a test the diff does not touch already does, or the edit cannot change "
                      "behavior, say so in decisions.md).", lines)

    def assert_draft_on_survivors(self) -> None:
        self.assertNotIn("mutation survived", (self.run_dir() / "round-2.fixes").read_text())
        first = self.body().splitlines()[0]
        self.assertTrue(first.startswith("Draft: the judge passed, but 5 blocking "), first)
        self.assertIn("The first is mutation [survived] ", first)
        self.assertNotIn("grader-round cap", first)

    def test_survivors_reach_the_next_worker_round_then_a_ready_pr(self) -> None:
        self.round_files(1, WEAK)
        self.round_files(2, STRONG)
        self.assertEqual(self.launch(), 0)
        self.assertEqual(self.worker_rounds(), 2)
        self.assertEqual(self.sweep_records(1), WEAK_RECORDS)
        self.assert_survivors_found_once(2)
        self.assertEqual(self.sweep_records(2), ALL_KILLED)
        self.assertIn("\n## Mutation sweep\n\n8 of 8 mutants killed by test_calc.py; 0 survived\n", self.body())
        self.assertFalse(self.body().startswith("Draft:"))
        self.assertEqual(len(git(self.co, self.env, "worktree", "list").splitlines()), 1)

    def test_the_sweep_blocks_once_then_drafts_the_pr_on_its_survivors(self) -> None:
        self.round_files(1, WEAK)
        self.assertEqual(self.launch(), 0)
        self.assertEqual(self.worker_rounds(), 2)
        self.assertEqual(self.sweep_records(2), WEAK_RECORDS)
        self.assert_draft_on_survivors()
        self.assertIn("\n3 of 8 mutants killed by test_calc.py; 5 survived\n- survived: ", self.body())

    def stopped_after_the_block(self) -> None:
        (self.top / "stop-once").touch()
        self.round_files(1, WEAK)
        self.launch()
        self.assertEqual((self.run_dir() / "status").read_text().strip(), "stopped")
        self.assertEqual(self.worker_rounds(), 1)
        (self.run_dir() / "FACTORY_STOP").unlink()

    def test_a_relaunch_after_the_block_resumes_into_a_worker_round(self) -> None:
        self.stopped_after_the_block()
        self.round_files(2, STRONG)
        self.assertEqual(self.launch(), 0)
        self.assertEqual(self.worker_rounds(), 2)
        self.assert_survivors_found_once(2)
        self.assertIn("\n8 of 8 mutants killed by test_calc.py; 0 survived\n", self.body())
        self.assertFalse(self.body().startswith("Draft:"))

    def test_a_relaunch_after_the_block_does_not_block_again(self) -> None:
        self.stopped_after_the_block()
        self.assertEqual(self.launch(), 0)
        self.assertEqual(self.worker_rounds(), 2)
        self.assert_draft_on_survivors()

    def test_a_failed_helper_stops_the_run(self) -> None:
        python = shutil.which("python3", path=self.env["PATH"])
        stub = self.top / "bin/python3"
        stub.write_text(f'#!/bin/sh\ncase "$*" in *mutation_sweep.py*) exit 3 ;; esac\nexec {python} "$@"\n')
        stub.chmod(0o755)
        self.round_files(1, WEAK)
        self.launch()
        self.assertEqual((self.run_dir() / "status").read_text().strip(), "stopped-environment")
        self.assertFalse((self.run_dir() / "pr-body.md").exists())
        self.assertEqual(len(git(self.co, self.env, "worktree", "list").splitlines()), 1)

    def test_strong_tests_open_a_ready_pr_after_one_round(self) -> None:
        self.round_files(1, STRONG)
        self.assertEqual(self.launch(), 0)
        self.assertEqual(self.worker_rounds(), 1)
        self.assertIn("\n8 of 8 mutants killed by test_calc.py; 0 survived\n", self.body())
        self.assertFalse(self.body().startswith("Draft:"))

    def test_no_committed_test_opens_a_ready_pr_after_one_round(self) -> None:
        self.round_files(1, None)
        self.assertEqual(self.launch(), 0)
        self.assertEqual(self.worker_rounds(), 1)
        self.assertIn("\n## Mutation sweep\n\nnot run: no committed test in the diff\n", self.body())
        self.assertFalse(self.body().startswith("Draft:"))
        self.assertIn("mutation sweep: not run: no committed test in the diff",
                      (self.run_dir() / "factory.log").read_text())
