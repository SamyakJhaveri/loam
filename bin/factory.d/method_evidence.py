#!/usr/bin/env python3
"""Grade what a worker round's method left behind, not whether the worker read it (docs/factory/LOOP.md, Method evidence).

Usage:
  method_evidence.py --run <run dir> --round N --repo <git repo> [--base SHA] [--head SHA]

Prints one line, `PASS method-evidence: <why>` (exit 0) or `FAIL method-evidence: <why>` (exit 1); input it cannot
use (no such sha, no decisions.md) prints a FAIL line too and exits 2. The supervisor runs its frozen copy after the
ticket's checks (round_checks); it also runs by hand on an old run directory.

The round is base..head: base is --base, else <run>/round-N.start.sha, else base.sha for round 1, else
round-(N-1).graded.sha; head is --head, else round-N.graded.sha. A round with no change, a docs-only change (every
path .md or .rst) or a trivial one (at most 5 changed lines outside docs and no added file
outside docs) passes with no method. Any other round declares its method in <run>/worker/decisions.md:
  method: <skill> | test: <command>
  method: <skill> | proof: <command> | exit <code>
(a list mark and backticks around the line or the command ignored); an older `pstack: <skill> | ...` line declares <skill> too, its other
fields unread. A line belongs to round N when it follows the `Round N` header the supervisor writes; with no header
(a run from before them) every line is round 1's. Round N also reads the lines of each earlier round with its start sha.

Each declaration is graded once per distinct command. Test route (a `test:` command, a method in TEST_METHODS, or a
round that changed a non-test source file, unless a method in PROOF_METHODS names a `proof:`): its own command, else the round's first `test:` command,
else `python3 -m pytest -q -p no:cacheprovider` on the round's changed test_*.py and *_test.py files, must exit 0 in a
detached worktree at head, then, with every changed non-test file put back to base (an added one deleted), exit
non-zero and not 5, 126 or 127; an added file the command names stays, as the test. A round whose code changes are all test files has nothing to put back, so its test only
has to pass at head. Proof route: the `proof:` command at head must exit with the declared code. A declaration with no
command that owes no test is covered by the round's other declarations; a round with nothing to run fails. Each run gets
METHOD_EVIDENCE_TIMEOUT_SEC seconds (900) through mutation_sweep.py's run, frozen beside it. python3 stdlib only.
"""
from __future__ import annotations

import argparse
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

# python3 -I leaves the script's folder off the path; appended, so no file beside it can stand in for a stdlib module.
sys.dont_write_bytecode = True
sys.path.append(str(Path(__file__).resolve().parent))
import mutation_sweep as ms  # noqa: E402 - its run, stop and subreaper, frozen beside this file

NAME = "method-evidence"
TEST_METHODS = {"tdd", "principle-fix-root-causes", "principle-attack-the-premise",
                "principle-test-behavior-not-implementation"}
# The methods for work that need not change behavior (a refactor, a measured number): only they may grade a source
# change by a proof; any other method owes a test that fails before the change.
PROOF_METHODS = {"principle-laziness-protocol", "principle-subtract-before-you-add", "principle-explain-the-number",
                 "benchmark-checklist"}
TRIVIAL_LINES = 5
NOT_A_FAIL = {5: "no tests ran", 126: "not executable", 127: "command not found"}
DOC_SUFFIXES = (".md", ".rst")
TEST_FILE = re.compile(r"test_.*\.py|.*_test\.py")
HEADER = re.compile(r"Round (\d+)")
METHOD = re.compile(r"method:\**\s*([^|]+?)\s*\|\s*(.*)")
PSTACK = re.compile(r"pstack:\s*([^|]+?)\s*\|")
PROOF = re.compile(r"proof:\s*(.+?)\s*\|\s*exit\s+(-?\d+)\.?\s*")
TIMEOUT = float(os.environ.get("METHOD_EVIDENCE_TIMEOUT_SEC", "900"))


class Unusable(Exception):
    """Input the checker cannot grade: exit 2."""


def git(repo: str | Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode:
        raise Unusable(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def is_doc(path: str) -> bool:
    return path.endswith(DOC_SUFFIXES)


def is_test(path: str) -> bool:
    """A test-side file: a test_*.py or *_test.py, a conftest.py, or anything under a tests, test or fixtures folder."""
    p = Path(path)
    return bool(TEST_FILE.fullmatch(p.name)) or p.name == "conftest.py" or bool(
        {"tests", "test", "fixtures"} & set(p.parts[:-1]))


def read_sha(path: Path) -> str | None:
    try:
        return path.read_text().strip() or None
    except OSError:
        return None


def round_range(run: Path, n: int, base: str | None, head: str | None) -> tuple[str, str]:
    """(base, head) by the order the module docstring gives."""
    if base is None:
        base = read_sha(run / f"round-{n}.start.sha")
    if base is None:
        base = read_sha(run / ("base.sha" if n == 1 else f"round-{n - 1}.graded.sha"))
    if head is None:
        head = read_sha(run / f"round-{n}.graded.sha")
    if base is None or head is None:
        raise Unusable(f"no {'base' if base is None else 'head'} sha for round {n} in {run}; pass --base/--head")
    return base, head


def changes(repo: str, base: str, head: str) -> list[tuple[str, str, int | None]]:
    """(status A/M/D/T, path, lines added plus deleted or None for a binary file) per changed path, no renames."""
    status = {}
    out = git(repo, "diff", "--name-status", "-z", "--no-renames", base, head).split("\0")
    for st, path in zip(out[0::2], out[1::2]):
        status[path] = st[:1]
    rows = []
    for line in git(repo, "diff", "--numstat", "-z", "--no-renames", base, head).split("\0"):
        if not line:
            continue
        a, d, path = line.split("\t", 2)
        rows.append((status.get(path, "M"), path, None if a == "-" else int(a) + int(d)))
    return rows


def round_lines(n: int, text: str) -> list[str]:
    """The decisions.md lines that belong to round n: those after its `Round n` header, or all of them for round 1."""
    cur, mine = 1, []
    for x in text.splitlines():
        m = HEADER.fullmatch(x)
        if m:
            cur = int(m.group(1))
        elif cur == n:
            mine.append(x)
    return mine


def declarations(lines: list[str]) -> list[tuple[str, str | None, str | None, int | None]]:
    """(skill, 'test'|'proof'|None, command, declared exit) per method or pstack line."""
    out = []
    for x in lines:
        x = re.sub(r"^[-*]\s+", "", x.strip()).strip("`")   # a list mark, and backticks around the whole line
        m = METHOD.search(x)
        if m:
            skill, rest = m.group(1).strip("*` ").split(":")[-1], m.group(2).strip()   # pstack:tdd is tdd
            p = PROOF.fullmatch(rest)
            if rest.startswith("test:") and rest[5:].strip(" `"):
                out.append((skill, "test", rest[5:].strip(" `"), None))
            elif p:
                out.append((skill, "proof", p.group(1).strip("`"), int(p.group(2))))
            else:
                out.append((skill, None, None, None))
            continue
        m = PSTACK.match(x)
        if m:
            out.append((m.group(1), None, None, None))
    return out


def run(cmd: str, wt: Path) -> tuple[int | None, str]:
    """(exit code, or None on a timeout; the output's last non-empty line) of `bash -c cmd` in wt."""
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    rc, _, tail = ms.run(["bash", "-c", cmd], wt, env, TIMEOUT)
    lines = [x.strip() for x in tail.splitlines() if x.strip()]
    return rc, (lines[-1][:200] if lines else "no output")


def shown(rc: int | None) -> str:
    return f"timed out after {TIMEOUT:g} s" if rc is None else f"exit {rc}"


def grade_test(cmd: str, wt: Path, base: str, restore: list[tuple[str, str]]) -> tuple[bool, str]:
    rc, tail = run(cmd, wt)
    if rc != 0:
        return False, f"test `{cmd}` must pass at head but {shown(rc)} ({tail})"
    if not restore:
        return True, f"test `{cmd}` exit 0 at head; the round changed only test files, so no base run"
    try:
        named = {os.path.normpath(t) for t in shlex.split(cmd)}
    except ValueError:
        named = set(cmd.split())
    added = [p for st, p in restore if st == "A" and p not in named]
    for p in added:
        (wt / p).unlink(missing_ok=True)
    back = [p for st, p in restore if st != "A"]
    if back:
        git(wt, "checkout", base, "--", *back)
    rc0, tail0 = run(cmd, wt)
    what = f"{len(restore)} changed non-test file(s) put back to base"
    if rc0 == 0:
        return False, (f"test `{cmd}` exit 0 at head and exit 0 with {what}: it does not fail before the change; "
                       "name a test that does")
    if rc0 is None or rc0 in NOT_A_FAIL:
        why = "timed out" if rc0 is None else NOT_A_FAIL[rc0]
        return False, f"test `{cmd}` exit 0 at head but {shown(rc0)} ({why}) with {what}, which is not a failing test ({tail0})"
    return True, f"test `{cmd}` exit 0 at head, exit {rc0} with {what}"


def grade(run_dir: Path, n: int, repo: str, base: str, head: str) -> tuple[bool, str]:
    rows = changes(repo, base, head)
    span = f"{base[:8]}..{head[:8]}"
    if not rows:
        return True, f"round {n} changed nothing ({span}), so no method is owed"
    code = [r for r in rows if not is_doc(r[1])]
    if not code:
        return True, f"round {n} changed docs only ({len(rows)} file(s), {span}), so no method is owed"
    size = sum(r[2] for r in code) if all(r[2] is not None for r in code) else None
    if size is not None and size <= TRIVIAL_LINES and not any(r[0] == "A" for r in code):
        return True, f"round {n} is trivial: {size} changed line(s) outside docs and no added file ({span}), so no method is owed"
    dec_file = run_dir / "worker" / "decisions.md"
    try:
        text = dec_file.read_text(errors="replace")
    except OSError as e:
        raise Unusable(f"cannot read {dec_file}: {e}") from e
    # A round that kept an earlier round's start (its method evidence did not pass) is graded with that round's lines too.
    shared = [k for k in range(1, n) if read_sha(run_dir / f"round-{k}.start.sha") == base]
    decs = declarations([x for k in [*shared, n] for x in round_lines(k, text)])
    names = ", ".join(r[1] for r in code[:8]) + (f" and {len(code) - 8} more" if len(code) > 8 else "")
    if not decs:
        return False, (f"round {n} changed {names} ({span}) but declared no method in decisions.md; write "
                       "`method: <skill> | test: <command>` or `method: <skill> | proof: <command> | exit <code>`")
    source = [r for r in code if not is_test(r[1])]
    tests = [r[1] for r in rows if TEST_FILE.fullmatch(Path(r[1]).name) and r[0] != "D"]
    named = [cmd for _, kind, cmd, _ in decs if kind == "test"]
    fallback = named[0] if named else (
        "python3 -m pytest -q -p no:cacheprovider " + " ".join(tests) if tests else None)
    jobs: dict[tuple, str] = {}  # (route, command, declared exit) -> the skills that declared it
    for skill, kind, cmd, want in decs:
        if kind == "test" or skill in TEST_METHODS or (source and not (kind == "proof" and skill in PROOF_METHODS)):
            key = ("test", cmd if kind == "test" else fallback, None)
        elif kind == "proof":
            key = ("proof", cmd, want)
        else:
            continue  # no command and no test owed: another declaration's command grades the round
        jobs[key] = f"{jobs[key]},{skill}" if key in jobs else skill
    if not jobs:
        return False, (f"round {n} declared {', '.join(d[0] for d in decs)} with no command; name one: "
                       "`method: <skill> | test: <command>` or `method: <skill> | proof: <command> | exit <code>`")
    for (route, cmd, _), skills in jobs.items():
        if cmd is None:
            return False, (f"round {n} declared {skills}, which owes a test, but named no test: command and changed "
                           "no test_*.py or *_test.py file to run; name a test: command")
    restore = [(r[0], r[1]) for r in rows if not is_test(r[1])]
    whys = []
    tmp = Path(tempfile.mkdtemp(prefix="method-evidence."))
    wt = tmp / "wt"
    try:
        for (route, cmd, want), skills in jobs.items():
            git(repo, "worktree", "add", "--detach", str(wt), head)
            try:
                if route == "test":
                    ok, why = grade_test(cmd, wt, base, restore if source else [])
                else:
                    rc, tail = run(cmd, wt)
                    ok = rc == want
                    why = (f"proof `{cmd}` {shown(rc)} at head, as declared" if ok else
                           f"proof `{cmd}` declared exit {want} but {shown(rc)} at head ({tail})")
            finally:
                subprocess.run(["git", "-C", repo, "worktree", "remove", "--force", str(wt)], capture_output=True)
                subprocess.run(["git", "-C", repo, "worktree", "prune"], capture_output=True)
            if not ok:
                return False, f"round {n} ({span}), {skills}: {why}"
            whys.append(f"{skills}: {why}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return True, f"round {n} ({span}), " + "; ".join(whys)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", required=True, type=Path)
    ap.add_argument("--round", required=True, type=int)
    ap.add_argument("--repo", required=True)
    ap.add_argument("--base")
    ap.add_argument("--head")
    a = ap.parse_args(argv)
    try:
        base, head = round_range(a.run, a.round, a.base, a.head)
        base, head = (git(a.repo, "rev-parse", "--verify", f"{s}^{{commit}}").strip() for s in (base, head))
        ok, why = grade(a.run, a.round, a.repo, base, head)
    except Unusable as e:
        print(f"FAIL {NAME}: cannot grade round {a.round}: {e}")
        return 2
    print(f"{'PASS' if ok else 'FAIL'} {NAME}: {why}")
    return 0 if ok else 1


if __name__ == "__main__":
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, ms.stop)
    ms.SUBREAPER = ms.subreaper()
    sys.exit(main(sys.argv[1:]))
