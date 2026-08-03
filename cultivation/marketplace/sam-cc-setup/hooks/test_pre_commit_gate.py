#!/usr/bin/env python3
"""Test the pre-commit-gate.sh command-detection stage.

Feeds hook-protocol JSON on stdin and checks whether the hook gates (exit 2,
because no .validation_passed sentinel exists) or lets the command through
(exit 0).  Exit 2 == GATE, exit 0 == PASS.
"""
import json, os, subprocess, sys

# Derived, not hardcoded: the hook always sits next to this test file (plugin
# hooks/ dir or a project's .claude/hooks/), and the sentinel lives at the git
# toplevel of whatever repo the test is run from — same resolution the hook uses.
HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pre-commit-gate.sh")
PROJECT_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip() or os.getcwd()
SENTINEL = os.path.join(PROJECT_ROOT, ".validation_passed")

# The whole suite reads "did the hook block?" as a proxy for "did it detect a
# commit?", which only holds while no validation sentinel exists — with one
# present the hook allows every commit and all 26 must-gate cases silently
# invert into false passes. That is not hypothetical: a concurrent /validate
# run produced exactly this, 15/38 with every must-gate case reporting PASS.
# Refuse to run rather than report a meaningless number.
if os.path.exists(SENTINEL):
    sys.exit(
        f"REFUSING TO RUN: {SENTINEL} exists.\n"
        "With a valid sentinel the hook allows every commit, so every "
        "must-gate case would report a false PASS.\n"
        "Remove it and re-run: rm .validation_passed"
    )

# (command, should_gate, why)
CASES = [
    # --- real invocations: MUST gate -------------------------------------
    ("git commit -m 'x'",                              True,  "plain"),
    ("git commit",                                     True,  "bare"),
    ("cd /tmp && git commit -m 'x'",                   True,  "v1 bypass: compound"),
    ("git -c user.email=a@b.com commit -m 'x'",        True,  "v1 bypass: -c config"),
    ("/usr/bin/git commit -m 'x'",                     True,  "v1 bypass: absolute path"),
    ("echo hi; git commit -m z",                       True,  "after semicolon"),
    ("git add . && git commit -m 'x' && git push",     True,  "mid-chain"),
    ("GIT_AUTHOR_NAME=x git commit -m y",              True,  "env assignment prefix"),
    ("git --no-pager commit -m x",                     True,  "long option"),
    ("false || git commit -m x",                       True,  "after ||"),
    ("git commit -m x > /tmp/log 2>&1",                True,  "with redirection"),
    ("echo $(git commit -m x)",                        True,  "command substitution"),
    # --- wrapper bypasses found by security-scanner 2026-08-02 -----------
    ("env FOO=bar git commit -m x",                    True,  "v3 bypass: env wrapper"),
    ("env A=1 B=2 git commit -m x",                    True,  "v3 bypass: env, two vars"),
    ("nice git commit -m x",                           True,  "v3 bypass: nice"),
    ("command git commit -m x",                        True,  "v3 bypass: command builtin"),
    ("sudo git commit -m x",                           True,  "v3 bypass: sudo"),
    ("timeout 30 git commit -m x",                     True,  "v3 bypass: timeout + duration"),
    ('sh -c "git commit -m x"',                        True,  "v3 bypass: sh -c"),
    ('bash -c "git commit -m x"',                      True,  "v3 bypass: bash -c"),
    ('bash -c "cd /tmp && git commit -m x"',           True,  "v3 bypass: sh -c compound"),
    ("find . -name x -exec git commit -m y ;",         True,  "v3 bypass: find -exec"),
    ("xargs git commit -m x",                          True,  "v3 bypass: xargs"),
    # --- v4 bypasses found by adversarial re-scan 2026-08-02 -------------
    ('eval "git commit -m x"',                         True,  "v4 bypass: eval"),
    ("eval git commit -m x",                           True,  "v4 bypass: eval, unquoted"),
    ("git \\\ncommit -m x",                            True,  "v4 bypass: line continuation"),
    ("git \\\n  commit -m x",                          True,  "v4 bypass: continuation + indent"),
    ("git add . && \\\n  git commit -m x",             True,  "v4 bypass: continuation mid-chain"),
    ("git commit -m x &",                              True,  "backgrounded"),
    # --- v5 bypasses found by Codex Sol review 2026-08-02 ----------------
    ('env bash -c "git commit -m x"',                  True,  "v5 bypass: wrapper + interpreter"),
    ('nice sh -c "git commit -m x"',                   True,  "v5 bypass: nice + sh -c"),
    ('sudo bash -c "git commit"',                      True,  "v5 bypass: sudo + bash -c"),
    ('env A=1 bash -c "cd /tmp && git commit -m x"',   True,  "v5 bypass: env+var+bash -c+compound"),
    ('timeout 30 sh -c "git commit"',                  True,  "v5 bypass: timeout + sh -c"),
    ('env nice bash -c "git commit -m x"',             True,  "wrapper + wrapper + interpreter"),
    ('echo hi | xargs sh -c "git commit -m x"',        True,  "pipe into xargs sh -c"),
    # --- v6: comment/continuation total-bypass, security re-scan 2026-08-02 --
    # A comment line ending in a backslash used to merge with the NEXT line;
    # shlex then swallowed the merged line as one comment, tokens = [], and
    # every detector was blind at once. Two-line paste, no special shell state.
    ("# note \\\ngit commit -m x",                     True,  "v6 bypass: comment line + continuation"),
    ("#see x \\\ngit commit",                          True,  "v6 bypass: comment, no space"),
    ("echo x # \\\ngit commit -m y",                   True,  "v6 bypass: trailing comment + continuation"),
    ("  # indented \\\n  git commit -m z",             True,  "v6 bypass: indented comment"),
    # --- v7: piped interpreter, found by test-synthesis 2026-08-02 --------
    ("printf 'git commit\\n' | bash",                  True,  "v7 bypass: script piped to bash"),
    ("echo 'git commit' | sh",                         True,  "v7 bypass: script piped to sh"),
    ("cat f | env bash",                               False, "piped to bash but no commit text"),

    # --- not invocations: MUST NOT gate ----------------------------------
    ("git commit-graph write",                         False, "different subcommand"),
    ("git commit-tree abc",                            False, "different subcommand"),
    ("echo 'git commit'",                              False, "quoted mention"),
    ('echo "a; git commit"',                           False, "v2 FALSE POSITIVE: sep in quotes"),
    ("git log --grep=commit",                          False, "option value"),
    ("git log --oneline | grep commit",                False, "grep for the word"),
    ("python3 -c \"x = 'a && git commit -m y'\"",       False, "v2 FALSE POSITIVE: inside -c script"),
    ("grep -rn 'git commit' .claude/hooks/",           False, "searching for the phrase"),
    ("git status --short",                             False, "unrelated git"),
    ("ls -la",                                         False, "unrelated"),
    ("git commitmsg",                                  False, "prefix only, no boundary"),
    ("git config --get commit.template",               False, "dotted config key"),
    ("git log --oneline | grep commit",                False, "git and commit in DIFFERENT segments"),
    ('echo "sh -c \\"git commit\\""',                   False, "nested quotes, still just an echo"),
    ("cat .claude/hooks/gate_detect.py",               False, "reading the detector itself"),
    ("git commit-tree $(git write-tree) -m x -p HEAD", False, "v4 FALSE POSITIVE: commit-tree + substitution"),
    ("git commit-graph write --reachable",             False, "commit-graph, not commit"),
    ("# git commit -m x",                              False, "pure comment, nothing executes"),
    ("echo hi  # git commit later",                    False, "trailing comment only"),
    ('echo "a#b"',                                     False, "hash inside quotes, must not unbalance"),
    ('git log -1 --format="%s #42"',                   False, "hash inside a quoted format string"),
    # --- v7: multi-line commands. A newline is a REAL separator; unrelated
    # lines must not be welded into one segment. This was gating ordinary
    # two-line Bash-tool commands. Found by the security re-scan 2026-08-02.
    ("git status\ngrep commit CHANGELOG.md",           False, "v7 FP: unrelated lines, no operator"),
    ("git log --oneline\necho notes\ngrep -rn commit README.md",
                                                       False, "v7 FP: three unrelated lines"),
    ('x="value \\\n# not a comment, inside quotes"\necho done',
                                                       False, "v7 FP: quote spanning a continuation"),
    ("git add .\ngit commit -m x",                     True,  "multi-line, second line IS a commit"),
    ('msg="line one\nline two"\ngit status',           False, "genuine multi-line string, no commit"),

    # --- documented permanent gaps: indirection hides the word 'git' -----
    # These are ACCEPTED, not bugs. See gate_detect.py's docstring. They are
    # asserted here so that a future change closing them fails loudly and the
    # tradeoff gets re-decided deliberately rather than by accident.
    ("G=git; $G commit -m x",                          False, "ACCEPTED GAP: variable indirection"),
    ("alias g='git'; g commit -m x",                   False, "ACCEPTED GAP: alias indirection"),
    ("printf commit | xargs -I{} git {}",              False, "ACCEPTED GAP: xargs placeholder"),
]

def run(cmd):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    p = subprocess.run([HOOK], input=payload, capture_output=True, text=True)
    return p.returncode

fails = 0
print(f"{'RESULT':7} {'EXPECT':7} {'GOT':7}  COMMAND")
print("-" * 78)
for cmd, should_gate, why in CASES:
    rc = run(cmd)
    got = "GATE" if rc == 2 else ("PASS" if rc == 0 else f"ERR{rc}")
    exp = "GATE" if should_gate else "PASS"
    ok = got == exp
    if not ok:
        fails += 1
    print(f"{'ok' if ok else 'FAIL':7} {exp:7} {got:7}  {cmd[:44]:44} ({why})")

print("-" * 78)
print(f"{len(CASES) - fails}/{len(CASES)} passed")
sys.exit(1 if fails else 0)
