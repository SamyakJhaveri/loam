#!/usr/bin/env python3
"""Grade what a worker round's method left behind, not whether the worker read it (docs/factory/LOOP.md, Method evidence).

Usage:
  method_evidence.py --run <run dir> --round N --repo <git repo> [--base SHA] [--head SHA]

Prints one line, `PASS method-evidence: <why>` (exit 0) or `FAIL method-evidence: <why>` (exit 1); input it cannot
use (no such sha, no decisions.md) prints a FAIL line too and exits 2. The supervisor runs its frozen copy after the
ticket's checks (round_checks); it also runs by hand on an old run directory.

The round is base..head: base is --base, else <run>/round-N.start.sha, else base.sha for round 1, else
round-(N-1).graded.sha; head is --head, else round-N.graded.sha. A round with no change, a docs-only change (every
path .md, .txt or .rst, or under docs/) or a trivial one (at most 5 changed lines outside docs and no added file
outside docs) passes with no method. Any other round declares its method in <run>/worker/decisions.md:
  method: <skill> | test: <command>
  method: <skill> | proof: <command> | exit <code>
(a leading `- ` or `* ` allowed); an older `pstack: <skill> | ...` line declares <skill> too, its other fields unread.
A line belongs to round N when it follows the `Round N` header the supervisor writes; a decisions.md with no header
gives a line to the first round K >= 2 whose round-K.jsonl tool_use inputs hold its first 40 characters, else round 1.

Each declaration is graded once per distinct command. Test route (a `test:` command, a method in TEST_METHODS, or a
round that changed a non-test source file with no `proof:`): its own command, else the round's first `test:` command,
else `python3 -m pytest -q -p no:cacheprovider` on the round's changed test_*.py and *_test.py files, must exit 0 in a
detached worktree at head, then, with every changed non-test file put back to base (an added one deleted), exit
non-zero and not 5, 126 or 127. A round whose code changes are all test files has nothing to put back, so its test only
has to pass at head. Proof route: the `proof:` command at head must exit with the declared code. A declaration with no
command that owes no test is covered by the round's other declarations; a round with nothing to run fails. Each run gets METHOD_EVIDENCE_TIMEOUT_SEC seconds (900), in a session of its
own whose process group, and on Linux every orphan it leaves, gets KILL when it ends. python3 stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

NAME = "method-evidence"
TEST_METHODS = {"tdd", "principle-fix-root-causes", "principle-attack-the-premise",
                "principle-test-behavior-not-implementation"}
TRIVIAL_LINES = 5
NOT_A_FAIL = {5: "no tests ran", 126: "not executable", 127: "command not found"}
DOC_SUFFIXES = (".md", ".txt", ".rst")
TEST_FILE = re.compile(r"test_.*\.py|.*_test\.py")
HEADER = re.compile(r"Round (\d+)")
METHOD = re.compile(r"(?:[-*] )?method:\s*([^|]+?)\s*\|\s*(.*)")
PSTACK = re.compile(r"(?:[-*] )?pstack:\s*([^|]+?)\s*\|")
PROOF = re.compile(r"proof:\s*(.+?)\s*\|\s*exit\s+(-?\d+)\s*")
TIMEOUT = float(os.environ.get("METHOD_EVIDENCE_TIMEOUT_SEC", "900"))
CURRENT: subprocess.Popen | None = None
SUBREAPER = False


class Unusable(Exception):
    """Input the checker cannot grade: exit 2."""


def git(repo: str | Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if r.returncode:
        raise Unusable(f"git {' '.join(args)} failed: {r.stderr.strip()}")
    return r.stdout


def is_doc(path: str) -> bool:
    return path.endswith(DOC_SUFFIXES) or path.startswith("docs/")


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


def tool_inputs(jsonl: Path) -> list[str]:
    """Every string inside the tool_use inputs of a stream-json transcript."""
    out: list[str] = []

    def walk(v: object) -> None:
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    try:
        lines = jsonl.read_text(errors="replace").splitlines()
    except OSError:
        return out
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        content = (ev.get("message") or {}).get("content") if isinstance(ev, dict) else None
        for c in content if isinstance(content, list) else []:
            if isinstance(c, dict) and c.get("type") == "tool_use":
                walk(c.get("input"))
    return out


def round_lines(run: Path, n: int, text: str) -> list[str]:
    """The decisions.md lines that belong to round n."""
    lines = text.splitlines()
    if any(HEADER.fullmatch(x) for x in lines):
        cur, mine = 1, []
        for x in lines:
            m = HEADER.fullmatch(x)
            if m:
                cur = int(m.group(1))
            elif cur == n:
                mine.append(x)
        return mine
    # No header (a run before the supervisor wrote them): a line is the first later round's whose transcript wrote it.
    # Every round with a transcript is searched, so a line a later round wrote is never given to round 1.
    later = sorted((int(m.group(1)), p) for p in run.glob("round-*.jsonl")
                   if (m := re.fullmatch(r"round-(\d+)\.jsonl", p.name)) and int(m.group(1)) >= 2)
    inputs = {k: tool_inputs(p) for k, p in later}
    mine = []
    for x in lines:
        key = x[:40]
        owner = next((k for k, _ in later if key.strip() and any(key in s for s in inputs[k])), 1)
        if owner == n:
            mine.append(x)
    return mine


def declarations(lines: list[str]) -> list[tuple[str, str | None, str | None, int | None]]:
    """(skill, 'test'|'proof'|None, command, declared exit) per method or pstack line."""
    out = []
    for x in lines:
        x = x.strip()
        m = METHOD.fullmatch(x)
        if m:
            skill, rest = m.group(1), m.group(2).strip()
            p = PROOF.fullmatch(rest)
            if rest.startswith("test:") and rest[5:].strip():
                out.append((skill, "test", rest[5:].strip(), None))
            elif p:
                out.append((skill, "proof", p.group(1), int(p.group(2))))
            else:
                out.append((skill, None, None, None))
            continue
        m = PSTACK.match(x)
        if m:
            out.append((m.group(1), None, None, None))
    return out


def kill_group(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def subreaper() -> bool:
    """On Linux, make this process the child subreaper of its descendants (prctl PR_SET_CHILD_SUBREAPER), so a test's
    child that starts a session of its own is orphaned to the checker, not to init, and killed with the run."""
    if not sys.platform.startswith("linux"):
        return False
    import ctypes
    return ctypes.CDLL(None, use_errno=True).prctl(36, 1, 0, 0, 0) == 0


def kill_orphans() -> None:
    """KILL every descendant left after a run's group KILL (as subreaper they are the run's orphans), for 5 s at most."""
    end = time.monotonic() + 5
    while time.monotonic() < end:
        kids: dict[int, list[int]] = {}
        for stat in Path("/proc").glob("[0-9]*/stat"):
            try:
                s = stat.read_bytes()
            except OSError:
                continue
            kids.setdefault(int(s[s.rindex(b")") + 2:].split()[1]), []).append(int(stat.parent.name))
        mine, todo = [], list(kids.get(os.getpid(), []))
        while todo:
            pid = todo.pop()
            mine.append(pid)
            todo.extend(kids.get(pid, []))
        if not mine:
            return
        for pid in mine:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        for pid in kids.get(os.getpid(), []):
            try:
                os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
        time.sleep(0.05)


def run(cmd: str, wt: Path) -> tuple[int | None, str]:
    """(exit code, or None on a timeout; the output's last non-empty line) of `bash -c cmd` in wt."""
    global CURRENT
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with open(os.devnull, "rb") as stdin, tempfile.TemporaryFile() as log:
        p = subprocess.Popen(["bash", "-c", cmd], cwd=wt, env=env, stdin=stdin, stdout=log, stderr=subprocess.STDOUT,
                             start_new_session=True)
        CURRENT = p
        try:
            rc: int | None = p.wait(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            rc = None
        finally:
            kill_group(p.pid)
            p.wait()
            if SUBREAPER:
                kill_orphans()
            CURRENT = None
        log.seek(0)
        tail = [x.strip() for x in log.read().decode("utf-8", "replace").splitlines() if x.strip()]
    return rc, (tail[-1][:200] if tail else "no output")


def shown(rc: int | None) -> str:
    return f"timed out after {TIMEOUT:g} s" if rc is None else f"exit {rc}"


def grade_test(cmd: str, wt: Path, base: str, restore: list[tuple[str, str]]) -> tuple[bool, str]:
    rc, tail = run(cmd, wt)
    if rc != 0:
        return False, f"test `{cmd}` must pass at head but {shown(rc)} ({tail})"
    if not restore:
        return True, f"test `{cmd}` exit 0 at head; the round changed only test files, so no base run"
    added = [p for st, p in restore if st == "A"]
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
    decs = declarations(round_lines(run_dir, n, text))
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
        if kind == "test" or skill in TEST_METHODS or (source and kind != "proof"):
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


def stop(signum: int, _frame: object) -> None:
    """A TERM, INT or HUP kills the run in progress; the temporary worktree goes on the way out."""
    if CURRENT is not None:
        kill_group(CURRENT.pid)
    raise SystemExit(128 + signum)


if __name__ == "__main__":
    for sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
        signal.signal(sig, stop)
    SUBREAPER = subreaper()
    sys.exit(main(sys.argv[1:]))
