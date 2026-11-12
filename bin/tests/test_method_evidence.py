"""bin/factory.d/method_evidence.py grades what a round's method left behind (docs/factory/LOOP.md, Method evidence).

Each test builds a scratch git repository with a base commit whose add() is wrong and a head commit for the round, a
run directory with base.sha, round-N.graded.sha and worker/decisions.md, and runs the checker as the supervisor does.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CHECKER = ROOT / "bin/factory.d/method_evidence.py"
PY = sys.executable
BUGGY = "def add(a, b):\n    return a - b\n"
FIXED = "def add(a, b):\n    return a + b\n"
TEST_ADD = "from calc import add\n\n\ndef test_add():\n    assert add(2, 3) == 5\n"
PYTEST = f"{PY} -m pytest -q -p no:cacheprovider test_calc.py"
# More than 5 changed lines, so the round is not trivial, and add() still as wrong as at base.
FEATURE = BUGGY + "".join(f"\n\ndef f{i}():\n    return {i}\n" for i in range(3))


def git(repo: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout.strip()


def commit(repo: pathlib.Path, files: dict[str, str]) -> str:
    for name, text in files.items():
        (repo / name).parent.mkdir(parents=True, exist_ok=True)
        (repo / name).write_text(text)
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "step")
    return git(repo, "rev-parse", "HEAD")


def setup(tmp: pathlib.Path, head_files: dict[str, str], decisions: str) -> tuple[pathlib.Path, pathlib.Path]:
    repo, run = tmp / "repo", tmp / "run"
    repo.mkdir()
    git(repo, "init", "-q")
    base = commit(repo, {"calc.py": BUGGY, "README.md": "calc\n"})
    head = commit(repo, head_files)
    (run / "worker").mkdir(parents=True)
    (run / "base.sha").write_text(base + "\n")
    (run / "round-1.graded.sha").write_text(head + "\n")
    (run / "worker/decisions.md").write_text(decisions)
    return repo, run


def check(repo: pathlib.Path, run: pathlib.Path, n: int = 1, **extra: str) -> tuple[int, str]:
    args = [PY, "-I", str(CHECKER), "--run", str(run), "--round", str(n), "--repo", str(repo)]
    for k, v in extra.items():
        args += [f"--{k}", v]
    # The derived test command runs `python3`; put the interpreter running these tests first on PATH.
    env = {**os.environ, "PATH": f"{pathlib.Path(PY).parent}:{os.environ['PATH']}"}
    r = subprocess.run(args, capture_output=True, text=True, env=env)
    assert r.stdout.count("\n") == 1, r.stdout + r.stderr
    return r.returncode, r.stdout.strip()


def test_docs_only_round_passes_with_no_declaration(tmp_path):
    repo, run = setup(tmp_path, {"README.md": "calc, documented\n" * 20, "docs/use.md": "how\n"}, "")
    rc, out = check(repo, run)
    assert (rc, out.split(":")[0]) == (0, "PASS method-evidence") and "docs only" in out


def test_code_round_with_no_declaration_fails_naming_the_files(tmp_path):
    repo, run = setup(tmp_path, {"calc.py": FEATURE, "extra.py": "X = 1\n"}, "- Approach: added f0..f2.\n")
    rc, out = check(repo, run)
    assert rc == 1 and out.startswith("FAIL method-evidence:") and "calc.py" in out and "extra.py" in out


def test_trivial_round_passes_and_a_six_line_one_does_not(tmp_path):
    repo, run = setup(tmp_path, {"calc.py": FIXED}, "")
    rc, out = check(repo, run)
    assert rc == 0 and "trivial" in out
    head = commit(repo, {"calc.py": FIXED + "\n\ndef g():\n    return 1\n\n\n"})
    rc, out = check(repo, run, base=git(repo, "rev-parse", "HEAD~1"), head=head)
    assert rc == 1 and "declared no method" in out


def test_tdd_test_that_fails_at_base_and_passes_at_head_passes(tmp_path):
    repo, run = setup(tmp_path, {"calc.py": FIXED, "test_calc.py": TEST_ADD},
                      f"Round 1\n- method: tdd | test: {PYTEST}\n")
    rc, out = check(repo, run)
    assert rc == 0 and out.startswith("PASS method-evidence:") and "exit 0 at head, exit 1 with" in out, out
    assert not [w for w in git(repo, "worktree", "list").splitlines() if "method-evidence" in w]


def test_old_pstack_line_derives_the_test_from_the_changed_test_files(tmp_path):
    # An old record: no Round header, a pstack: line, no command; the round's test_calc.py is the derived test.
    repo, run = setup(tmp_path, {"calc.py": FIXED, "test_calc.py": TEST_ADD},
                      "- pstack: tdd | /x/tdd/SKILL.md | abc | write the failing test first | test first\n")
    rc, out = check(repo, run)
    assert rc == 0 and "-m pytest -q -p no:cacheprovider test_calc.py` exit 0 at head, exit 1" in out, out


def test_a_test_that_passes_at_base_too_fails(tmp_path):
    passing = "from calc import add\n\n\ndef test_add():\n    assert add(3, 0) == 3\n"
    repo, run = setup(tmp_path, {"calc.py": FEATURE, "test_calc.py": passing}, f"Round 1\nmethod: tdd | test: {PYTEST}\n")
    rc, out = check(repo, run)
    assert rc == 1 and "does not fail before the change" in out, out


def test_a_test_command_that_is_not_found_at_base_is_no_failing_test(tmp_path):
    # Exit 127 at base is a missing command, not a red test: here the test is a script the round adds.
    repo, run = setup(tmp_path, {"calc.py": FIXED, "check.sh": f"{PY} -c 'import calc; assert calc.add(2, 3) == 5'\n"},
                      "Round 1\nmethod: principle-fix-root-causes | test: bash check.sh\n")
    rc, out = check(repo, run)
    assert rc == 1 and "exit 127" in out, out


def test_proof_route_matches_the_declared_exit_code(tmp_path):
    proof = f"{PY} -c 'import calc, sys; sys.exit(calc.add(2, 3))'"
    repo, run = setup(tmp_path, {"calc.py": FIXED + "\n\ndef h():\n    return 2\n\n\ndef k():\n    return 3\n"},
                      f"Round 1\nmethod: principle-prove-it-works | proof: {proof} | exit 5\n")
    rc, out = check(repo, run)
    assert rc == 0 and "exit 5 at head, as declared" in out, out
    (run / "worker/decisions.md").write_text(f"Round 1\nmethod: principle-prove-it-works | proof: {proof} | exit 0\n")
    rc, out = check(repo, run)
    assert rc == 1 and "declared exit 0 but exit 5" in out, out


def test_a_round_one_declaration_does_not_satisfy_round_two(tmp_path):
    repo, run = setup(tmp_path, {"calc.py": FIXED, "test_calc.py": TEST_ADD}, "")
    r1 = git(repo, "rev-parse", "HEAD")
    r2 = commit(repo, {"calc.py": FIXED + "".join(f"\n\ndef f{i}():\n    return {i}\n" for i in range(3))})
    (run / "round-2.graded.sha").write_text(r2 + "\n")
    (run / "worker/decisions.md").write_text(f"Round 1\nmethod: tdd | test: {PYTEST}\nRound 2\n- Round 2: added f0..f2.\n")
    rc, out = check(repo, run, n=2)
    assert rc == 1 and "round 2 changed calc.py" in out and r1[:8] in out, out


def test_with_no_header_a_line_a_later_transcript_wrote_is_that_rounds(tmp_path):
    # W41's shape: no Round headers. The line is in round 2's Write input, so it is round 2's, not round 1's.
    line = f"- method: tdd | test: {PYTEST}"
    repo, run = setup(tmp_path, {"calc.py": FIXED, "test_calc.py": TEST_ADD}, line + "\n")
    event = {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Write", "input": {"file_path": "decisions.md", "content": line + "\n"}}]}}
    (run / "round-2.jsonl").write_text(json.dumps(event) + "\n")
    rc, out = check(repo, run)
    assert rc == 1 and "declared no method" in out, out
    (run / "round-2.jsonl").write_text("")
    rc, out = check(repo, run)
    assert rc == 0, out
