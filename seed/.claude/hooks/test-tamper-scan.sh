#!/usr/bin/env bash
# test-tamper-scan.sh - PreToolUse hook on Bash; fires only on a `git commit`.
# Anti-reward-hacking guard on a commit's test half. BAITBENCH (arXiv 2608.30724)
# measured 20.8 to 76.1 percent test-cheating by model, so a commit that skips,
# mocks, loosens, or hard-codes a test is worth catching first. This scan is a
# script - no model call - so it costs no tokens and cannot be argued out of a
# finding. It flags ADDED lines in staged test files that add a skip/xfail, add a
# mock/patch, loosen a numeric tolerance, or assert a literal a non-test file's
# new `return` now hands back. Escape hatch: justify under a `Test-changes:` line
# in the commit message. Exit codes (hook protocol): 0 = allow, 2 = BLOCK (stderr).

set -uo pipefail
PAYLOAD="$(cat)"
# Extract command (line 1..) and cwd (line 0) in one pass. Malformed JSON -> empty.
EXTRACT="$(printf '%s' "$PAYLOAD" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    assert isinstance(d, dict)
except Exception:
    sys.exit(0)
ti = d.get("tool_input") or {}
cmd = ti.get("command", "") if isinstance(ti, dict) else ""
sys.stdout.write((d.get("cwd") or "") + "\n" + (cmd or ""))
' 2>/dev/null)" || EXTRACT=""
CWD="$(printf '%s' "$EXTRACT" | head -n1)"
CMD="$(printf '%s' "$EXTRACT" | tail -n +2)"
# Fire only on a real `git commit`: git, optional global options (-C dir,
# -c k=v), then the commit subcommand. `git grep commit` must not fire.
printf '%s' "$CMD" | grep -qE '\bgit\s+(-\S+\s+(\S+\s+)?)*commit\b' || exit 0
# Escape hatch: the justification lives in the commit message text.
printf '%s' "$CMD" | grep -qF 'Test-changes:' && exit 0
# Root = cwd field, fallback git toplevel, else pass.
if [ -n "$CWD" ] && [ -d "$CWD" ]; then
    ROOT="$CWD"
else
    ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
fi
[ -n "$ROOT" ] || exit 0
cd "$ROOT" 2>/dev/null || exit 0
# The command may stage before it commits (`git add ... && git commit`, or
# `commit -a`), and this hook runs first. Replay that staging into a copy of
# the index and diff against the copy: `add -A` for an explicit add (a
# superset; an over-block is recoverable), `add -u` for -a/--all (tracked
# changes only, which is exactly what -a commits). A plain commit reads the
# real index.
STAGE=""
if printf '%s' "$CMD" | grep -qE '\bgit\s+add\b'; then
    STAGE="-A"
elif printf '%s' "$CMD" | grep -qE '\bcommit\b[^&|;]*\s(--all|-[a-zA-Z]*a[a-zA-Z]*)\b'; then
    STAGE="-u"
fi
if [ -n "$STAGE" ]; then
    TMPI="$(mktemp)" || exit 0
    IDX="$(git rev-parse --git-path index)"
    # No index file yet (nothing ever staged): the copy starts empty.
    if [ -f "$IDX" ]; then
        cp -- "$IDX" "$TMPI" 2>/dev/null || { rm -f "$TMPI"; exit 0; }
    else
        rm -f "$TMPI"
    fi
    GIT_INDEX_FILE="$TMPI" git add "$STAGE" >/dev/null 2>&1
    DIFF="$(GIT_INDEX_FILE="$TMPI" git diff --cached -U0 --no-color 2>/dev/null)"
    rm -f "$TMPI"
else
    DIFF="$(git diff --cached -U0 --no-color 2>/dev/null)" || exit 0
fi
# Script via -c so the diff stays on stdin (a heredoc would take stdin instead).
printf '%s' "$DIFF" | python3 -c "$(cat <<'PY'
import sys, re
diff = sys.stdin.read()
TEST_NAME = re.compile(r'(^|/)(test_[^/]*\.py|[^/]*_test\.py|conftest\.py)$')
JS_TEST = re.compile(r'\.(test|spec)\.[jt]sx?$')

def is_test(p):
    segs = p.split('/')[:-1]
    return bool(TEST_NAME.search(p) or JS_TEST.search(p)) or 'tests' in segs or 'test' in segs

# Parse the unified diff (-U0) into files -> hunks, tracking new-file line numbers.
files, cur, hunk, new_no = [], None, None, 0
for ln in diff.split('\n'):
    if ln.startswith('diff --git '):
        cur, hunk = None, None
    elif hunk is None and ln.startswith('+++ '):
        p = ln[4:].strip()
        p = p[2:] if p.startswith('b/') else p
        if p == '/dev/null':
            cur = None
        else:
            cur = {'path': p, 'test': is_test(p), 'hunks': []}
            files.append(cur)
    elif ln.startswith('@@'):
        m = re.search(r'\+(\d+)', ln)
        new_no = int(m.group(1)) if m else 0
        hunk = {'add': [], 'rem': []}
        if cur is not None:
            cur['hunks'].append(hunk)
    elif cur is None or hunk is None:
        continue  # header/context line outside any hunk (`--- a/`, `index`, ...)
    elif ln.startswith('+'):
        hunk['add'].append((new_no, ln[1:])); new_no += 1
    elif ln.startswith('-'):
        hunk['rem'].append(ln[1:])

if not any(f['test'] for f in files):  # no staged test files: pass without scanning.
    sys.exit(0)
# New return literals from staged non-test files: literal text -> impl path.
RET = re.compile(r'^\s*return\s+(.+?)\s*(#.*)?$')
returns = {}
for f in (x for x in files if not x['test']):
    for h in f['hunks']:
        for _, txt in h['add']:
            m = RET.match(txt)
            if m: returns.setdefault(m.group(1).strip(), f['path'])

NUM = r'-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?'
LIT = r'(?:%s|"[^"]*"|\'[^\']*\'|True|False|None)' % NUM
SKIP = re.compile(r'\b(skip|skipif|xfail)\b')
MOCK = re.compile(r'\b(mock|patch|MagicMock|monkeypatch|sinon)\b|jest\.mock|vi\.mock')
TOL = re.compile(r'(rel|abs|atol|rtol|delta|tolerance|places)\s*=\s*([0-9.eE+-]+)')
ASSERTS = (re.compile(r'assert\b.*?==\s*(' + LIT + r')\s*(#.*)?$'),
           re.compile(r'assertEqual\s*\(\s*.*,\s*(' + LIT + r')\s*\)\s*(#.*)?$'),
           re.compile(r'\.(?:toBe|toEqual)\s*\(\s*(' + LIT + r')\s*\)'))

def fnum(s):
    try:
        return float(s)
    except ValueError:
        return None

def strip_comment(s):
    """Drop a trailing Python '#' or JS '//' comment, respecting quotes, so
    prose like `data[1:]  # skip the header row` is not read as a skip."""
    q, i, n = None, 0, len(s)
    while i < n:
        c = s[i]
        if q:
            if c == '\\':
                i += 2
                continue
            if c == q:
                q = None
        elif c in ('"', "'"):
            q = c
        elif c == '#':
            return s[:i]
        elif c == '/' and s[i + 1:i + 2] == '/':
            return s[:i]
        i += 1
    return s

def strip_strings(s):
    """Blank the contents of quoted string literals so prose in a docstring
    or a message (`"we patch the config"`) is not read as a mock or skip."""
    out, q, i, n = [], None, 0, len(s)
    while i < n:
        c = s[i]
        if q:
            if c == '\\':
                i += 2
                continue
            if c == q:
                q = None
                out.append(c)
        else:
            if c in ('"', "'"):
                q = c
            out.append(c)
        i += 1
    return ''.join(out)

# Literals too common to mean anything: a test asserting 0 or True is not
# mirroring an implementation's new return value.
TRIVIAL = {'0', '1', '-1', '0.0', '1.0', 'True', 'False', 'None', '""', "''"}

findings = []
for f in (x for x in files if x['test']):
    for h in f['hunks']:
        for no, txt in h['add']:
            trimmed = txt.strip()[:120]
            code = strip_strings(strip_comment(txt))
            if SKIP.search(code):
                findings.append((f['path'], no, 'new skip/xfail', trimmed))
            if MOCK.search(code):
                findings.append((f['path'], no, 'new mock/patch', trimmed))
            for kw, num in TOL.findall(txt):
                an = fnum(num)
                if an is None: continue
                for r in h['rem']:
                    mm = re.search(re.escape(kw) + r'\s*=\s*([0-9.eE+-]+)', r)
                    on = fnum(mm.group(1)) if mm else None
                    if on is None: continue
                    if (an < on) if kw == 'places' else (an > on):
                        findings.append((f['path'], no, 'loosened tolerance %s -> %s' % (mm.group(1), num), trimmed)); break
            lit = None
            for rx in ASSERTS:
                m = rx.search(txt)
                if m: lit = m.group(1).strip(); break
            if lit in returns and lit not in TRIVIAL:
                findings.append((f['path'], no, 'expected literal %s equals a new return value in %s' % (lit, returns[lit]), trimmed))

if not findings:
    sys.exit(0)
out = ['Test integrity scan: %d flagged line(s) in staged tests:' % len(findings)]
for path, no, reason, trimmed in findings:
    out.append('  %s:%d: %s: %s' % (path, no, reason, trimmed))
out.append("Justify each under a 'Test-changes:' line in the commit message, then retry.")
sys.stderr.write('\n'.join(out) + '\n')
sys.exit(2)
PY
)"
exit $?
