"""Every factory write to GitHub passes through scrub, so a token in check output or model text never reaches
the public repo: notify's issue comment, file_issues' issue titles and bodies, and the PR title and body on
create and on the PATCH update.

`bin/factory` is sourced (FACTORY_SOURCED=1) and the real functions run on a fake run directory over a
throwaway worktree whose origin is a local bare repository. A fake `gh` first on PATH records its arguments,
and the body it reads from `--body-file`. HOME is a temp dir, so notify finds no Pushover config. No network.
"""

from __future__ import annotations

import gzip
import json
import os
import pathlib
import re
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
INHERITED = ("FACTORY_ROOT", "FACTORY_GH", "LOAM_FACTORY_TOOLCHAIN", "LOAM_FACTORY_COPIER", "REPO", "RUN", "LOG")
TICKET = "## Goal and why\n\nMake the widget work.\n\n## Merge checklist\n\n- read the diff\n"

FAKE_GH = """#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
sent = {"args": args, "body": ""}
if "--body-file" in args:
    path = args[args.index("--body-file") + 1]
    sent["body"] = sys.stdin.read() if path == "-" else open(path).read()
with open(os.environ["FAKE_GH_LOG"], "a") as f:
    f.write(json.dumps(sent) + "\\n")
if args[:2] == ["pr", "view"]:
    if not os.environ.get("FAKE_GH_PR"):
        sys.exit(1)
    print(os.environ["FAKE_GH_PR"])
elif args[:2] == ["pr", "create"]:
    print("https://github.com/acme/widget/pull/9")
"""


def fake(tag: str, n: int) -> str:
    """A token-shaped value, distinct per tag, that is not a real key."""
    return (tag + "X0" * n)[:n]


# Text the factory might publish -> the part of it that must not reach GitHub. Built at runtime, so this
# file holds no token-shaped literal.
SECRETS = {
    **{f"GH_TOKEN=gh{c}_{fake('gh' + c, 36)}": fake("gh" + c, 36) for c in "pousr"},
    "github_pat_" + fake("pat", 60): fake("pat", 60),
    "Authorization: token " + fake("auth", 20): fake("auth", 20),
    "curl -H 'Bearer " + fake("bearer", 40) + "'": fake("bearer", 40),
    "ANTHROPIC_API_KEY=sk-ant-api03-" + fake("ant", 40): fake("ant", 40),
    "key sk-proj-" + fake("oai", 40): fake("oai", 40),
    "xoxb-" + fake("slackb", 30): fake("slackb", 30),
    "xoxs-" + fake("slacks", 30): fake("slacks", 30),
    "AKIA" + fake("AWS", 16): "AKIA" + fake("AWS", 16),
    "-----BEGIN RSA PRIVATE KEY-----\n" + fake("pem", 64) + "\n-----END RSA PRIVATE KEY-----": fake("pem", 64),
    "-----BEGIN PGP PRIVATE KEY BLOCK-----\nVersion: GnuPG v2\n\n" + fake("pgp", 64) + "\n-----END PGP PRIVATE KEY BLOCK-----":
        fake("pgp", 64),
    "git push https://bot:" + fake("pw", 12) + "@example.com/acme/widget.git": fake("pw", 12),
    "PUSHOVER_TOKEN=" + fake("push", 30): fake("push", 30),
    "password: " + fake("pass", 16): fake("pass", 16),
    "eyJ" + ".".join(fake(t, 20) for t in ("hdr", "claims", "sig")): fake("claims", 20),
    "glpat-" + fake("gl", 20): fake("gl", 20),
    "AIza" + fake("goog", 35): fake("goog", 35),
    "npm_" + fake("npm", 36): fake("npm", 36),
    "dop_v1_" + "a1b2c3d4" * 8: "a1b2c3d4" * 8,
}
PLANTED = "\n".join(SECRETS)
# A key with no END line loses its header lines and body. It is planted only where no END marker follows it,
# since the scrub would take it on to that marker (the known over-span) and hide the headings checked here.
OPEN_KEY = ("-----BEGIN RSA PRIVATE KEY-----\nProc-Type: 4,ENCRYPTED\nDEK-Info: AES-256-CBC," + fake("iv", 16)
            + "\n\n" + fake("head", 64) + "\n" + fake("open", 40))
SECRETS[OPEN_KEY] = fake("open", 40)
# Prose that names a BEGIN marker loses the marker and the word run after it, and nothing more.
PROSE = "The scrub matches -----BEGIN RSA PRIVATE KEY----- markers, and this clause stays."
CUT = "-----BEGIN RSA PRIVATE KEY----- markers"


def indented(text: str, pad: str) -> str:
    """Every line of text with pad in front, as a key pasted into a code block or a YAML value is."""
    return pad + text.replace("\n", "\n" + pad)


def subs(path: pathlib.Path) -> list[str]:
    """The re.compile(...) calls, flags included, in a file's `SUBS = [` block."""
    block = path.read_text().split("SUBS = [", 1)[1].split("\n]", 1)[0]
    return re.findall(r're\.compile\(r"(?:[^"\\]|\\.)*"(?:, re\.[A-Z]+)?\)', block)


def git(*args: str, cwd: pathlib.Path) -> str:
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=cwd,
                          capture_output=True, text=True, check=True).stdout.strip()


class PublishScrubTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        top = pathlib.Path(tmp.name)
        origin = top / "origin.git"
        git("init", "-q", "--bare", str(origin), cwd=top)
        self.wt = top / "wt"
        self.wt.mkdir()
        git("init", "-q", "-b", "main", cwd=self.wt)
        git("remote", "add", "origin", str(origin), cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.wt)
        base = git("rev-parse", "HEAD", cwd=self.wt)
        git("checkout", "-q", "-b", "factory/7", cwd=self.wt)
        git("commit", "-q", "--allow-empty", "-m", "ticket 7: the fix", cwd=self.wt)
        self.graded = git("rev-parse", "HEAD", cwd=self.wt)
        self.home = top / "home"
        self.home.mkdir()
        bindir = top / "bin"
        bindir.mkdir()
        (bindir / "gh").write_text(FAKE_GH)
        (bindir / "gh").chmod(0o755)
        self.path = f"{bindir}{os.pathsep}{os.environ['PATH']}"
        self.gh_log = top / "gh-calls.jsonl"
        self.run_dir = top / "run"
        (self.run_dir / "frozen").mkdir(parents=True)
        (self.run_dir / "frozen" / "issue.md").write_text("# Widget works " + "AKIA" + fake("TITLE", 16) + "\n")
        (self.run_dir / "base.sha").write_text(base + "\n")
        (self.run_dir / "started").write_text("0\n")
        (self.run_dir / "ledger.jsonl").write_text("")
        (self.run_dir / "decisions.md").write_text(f"- kept it small\n{PLANTED}\n{OPEN_KEY}\n")
        (self.run_dir / "round-0.checks").write_text("FAIL widget\n")
        (self.run_dir / "round-2.checks").write_text("PASS widget\n")
        (self.run_dir / "round-2.measure").write_text(f"MEASURE speed {PLANTED} (baseline 3)\n")
        backlog = [f"Rotate these: {PLANTED}", "y" * 70 + " " + "gh" + "p_" + fake("cut", 36)]
        (self.run_dir / "round-2.judge.json").write_text(
            json.dumps({"verdict": "pass", "rows": {"widget": "pass"}, "backlog": backlog}))
        (self.run_dir / "round-2.review.json").write_text(json.dumps(
            {"verdict": "fix", "findings": [{"severity": "high", "file": "a.sh", "line": 1,
                                             "defect": f"leaks {PLANTED}", "fix": "drop it"}]}))

    def run_factory(self, script: str, pr: str = "") -> list[dict]:
        """Source bin/factory, run `script` for issue 7 at round 2, and return the fake gh's calls."""
        setup = (
            f"RUN='{self.run_dir}'; WORKTREE='{self.wt}'; BRANCH=factory/7; ISSUE=7; KEY=7; IS_FILE=0\n"
            f"ROUND=2; GRADED_SHA={self.graded}; LEDGER=\"$RUN/ledger.jsonl\"; DECISIONS=\"$RUN/decisions.md\"\n"
            "BODY=\"$TICKET\"\n"
        )
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        proc = subprocess.run(["bash", "-c", f". bin/factory\n{setup}{script}"], cwd=ROOT,
                              env={**env, "FACTORY_SOURCED": "1", "FACTORY_ROOT": str(ROOT), "REPO": "acme/widget",
                                   "TICKET": TICKET, "HOME": str(self.home), "PATH": self.path,
                                   "FAKE_GH_LOG": str(self.gh_log), "FAKE_GH_PR": pr,
                                   "LOG": str(self.run_dir / "factory.log")},
                              stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return [json.loads(x) for x in self.gh_log.read_text().splitlines()] if self.gh_log.exists() else []

    def assert_scrubbed(self, call: dict, planted: bool = True) -> None:
        sent = "\n".join(call["args"] + [call["body"]])
        for text, secret in SECRETS.items():
            self.assertNotIn(secret, sent, f"gh {' '.join(call['args'][:2])} published {text!r}")
        self.assertNotIn(fake("TITLE", 16), sent)
        self.assertNotIn(fake("cut", 36)[:5], sent)   # a token is scrubbed before a title cuts it
        if planted:
            self.assertIn("[redacted]", sent)

    def calls(self, calls: list[dict], *kind: str) -> list[dict]:
        found = [c for c in calls if c["args"][:len(kind)] == list(kind)]
        self.assertTrue(found, f"no gh {' '.join(kind)} call")
        return found

    def test_notify_issue_comment_is_scrubbed(self) -> None:
        # main_loop's notify after an even failing round posts up to ten FAIL lines with their reasons.
        calls = self.run_factory('notify "7 checks failing after round 2" "FAIL widget: $(cat "$DECISIONS")"\n')
        for call in self.calls(calls, "issue", "comment"):
            self.assert_scrubbed(call)

    def test_pr_create_and_filed_issues_are_scrubbed(self) -> None:
        calls = self.run_factory("open_pr\n")
        self.assertIn("## Rows measured", self.calls(calls, "pr", "create")[0]["body"])
        self.assertEqual(len(self.calls(calls, "issue", "create")), 3)   # two backlog lines, one blocking finding
        for call in self.calls(calls, "pr", "create") + self.calls(calls, "issue", "create"):
            self.assert_scrubbed(call)
        self.assert_scrubbed(self.calls(calls, "issue", "comment")[0], planted=False)   # finish's notify

    def test_pr_patch_update_is_scrubbed(self) -> None:
        calls = self.run_factory("open_pr\n", pr="9")
        patch = self.calls(calls, "api", "-X", "PATCH")
        self.assertIn("## Decisions", patch[0]["args"][-1])
        self.assert_scrubbed(patch[0])


class ScrubRulesTests(unittest.TestCase):
    def test_scrub_holds_every_mem_capture_rule(self) -> None:
        # The public GitHub path must redact at least what the private memory store does.
        memory = subs(ROOT / "seed/.claude/hooks/mem-capture.sh")
        self.assertTrue(memory)
        factory = subs(ROOT / "bin/factory")
        self.assertEqual([rule for rule in memory if rule not in factory], [])

    def test_factory_scrub_stops_a_key_with_no_end_line(self) -> None:
        text = f"{PROSE}\n## Next\n{OPEN_KEY}\n\n## Indented\n{indented(OPEN_KEY, '    ')}\n\n## Metrics\nrounds: 2\n"
        env = {k: v for k, v in os.environ.items() if k not in INHERITED}
        out = subprocess.run(["bash", "-c", ". bin/factory; scrub"], cwd=ROOT, env={**env, "FACTORY_SOURCED": "1"},
                             input=text, capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, PROSE.replace(CUT, "[redacted]") + "\n## Next\n[redacted]\n\n## Indented\n    [redacted]"
                         "\n\n## Metrics\nrounds: 2\n")

    def test_mem_capture_scrubs_private_key_blocks(self) -> None:
        # The memory store gets the key samples, one per transcript line as Claude writes it, so each line
        # break in a key is the two characters \n inside a JSON string. Every line must stay valid JSON.
        # The open key also comes inside a JSON string in a message (\\n in the trace, depth 2 and 3),
        # indented with tabs (\t), and indented with spaces, headers included.
        closed = [text for text in SECRETS if "PRIVATE KEY" in text and text != OPEN_KEY]
        nested = [json.dumps({"cmd": OPEN_KEY}), json.dumps(json.dumps({"cmd": OPEN_KEY}))]
        texts = closed + [PROSE, OPEN_KEY, *nested, indented(OPEN_KEY, "\t"), indented(OPEN_KEY, "    "),
                          "a later message stays"]
        with tempfile.TemporaryDirectory() as tmp:
            top = pathlib.Path(tmp)
            transcript = top / "t.jsonl"
            transcript.write_text("".join(json.dumps({"type": "user", "message": {"content": t}}) + "\n" for t in texts))
            env = {k: v for k, v in os.environ.items() if k != "LOAM_MEMSTORE_REMOTE"}
            subprocess.run(["bash", str(ROOT / "seed/.claude/hooks/mem-capture.sh")], cwd=top, check=True,
                           input=json.dumps({"transcript_path": str(transcript), "session_id": "scrub1", "cwd": tmp}),
                           env={**env, "LOAM_MEMSTORE": str(top / "store")}, capture_output=True, text=True)
            trace = gzip.decompress(next(top.glob("store/traces/*/*-scrub1.jsonl.gz")).read_bytes()).decode()
        stored = [json.loads(line)["message"]["content"] for line in trace.splitlines()]
        tag = "[REDACTED:private_key]"
        nested_tag = [json.dumps({"cmd": tag}), json.dumps(json.dumps({"cmd": tag}))]   # still parses as JSON
        self.assertEqual(stored, [tag] * len(closed) + [PROSE.replace(CUT, tag), tag, *nested_tag, "\t" + tag,
                                                        "    " + tag, "a later message stays"])


if __name__ == "__main__":
    unittest.main()
