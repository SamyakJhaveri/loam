#!/usr/bin/env bash
# harness-hygiene.sh - SessionStart: flag dead references in agent docs.
# 23% of 356 repos carried stale path references in their agent docs (arXiv 2606.09090);
# this prints only the dead ones so they get fixed. Scans, if present, the project's
# CLAUDE.md, AGENTS.md, STATE.md, and HANDOFF.md.
#
# Scan scope: inline `code spans` get the full path/file/command rules. Fenced
# ```code blocks``` are path-checked only, and only on the FIRST whitespace-
# separated token of each line: that token is the command or script the line
# claims exists, while later tokens are arguments and are usually placeholders
# (--config configs/base.yml). Fence tokens are never command-checked, because
# fence lines carry arguments and output and a command check there would be
# noisy. Absolute and "~" paths inside a fence are skipped as machine-specific
# examples; inline spans still check them. The extension rule and the colon rule
# (gh:owner/repo and other scheme-like tokens) apply as before. A single-token
# backticked word is also deliberately not command-checked: those are usually
# names (skills, flags, concepts), so leaving them out keeps the scan precise.
#
# Triggered by: SessionStart (startup|resume|clear)
# Exit codes:
#   0 = always (advisory only; stdout is added to the session context)

set -uo pipefail

PAYLOAD="$(cat)"

python3 - "$PAYLOAD" <<'PY'
import sys, json, os, re, subprocess

try:
    payload = json.loads(sys.argv[1])
except Exception:
    payload = {}

root = ""
if isinstance(payload, dict):
    c = payload.get("cwd")
    if isinstance(c, str) and c:
        root = c
if not root or not os.path.isdir(root):
    try:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                              capture_output=True, text=True).stdout.strip()
    except Exception:
        root = ""
if not root or not os.path.isdir(root):
    sys.exit(0)

SCANNED = ["CLAUDE.md", "AGENTS.md", "STATE.md", "HANDOFF.md"]
scanned_set = set(SCANNED)

# git ls-files once; cache tracked basenames for the bare-filename fallback.
tracked_basenames = set()
try:
    r = subprocess.run(["git", "-C", root, "ls-files"],
                       capture_output=True, text=True)
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            if line:
                tracked_basenames.add(os.path.basename(line))
except Exception:
    pass

SPAN = re.compile(r"`([^`\n]+)`")
BADCHARS = set("*{}$<>|()")
CMD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.+-]*$")
# A slashless word is path-checked only when it ends in a file extension we
# recognise. Everything else with a dot (asyncio.gather, this.state,
# docs.example.com, v2.0.0) is a dotted name, not a path, and is left alone.
FILE_RE = re.compile(
    r"^[\w.+-]+\.(md|py|sh|json|jsonl|yml|yaml|toml|txt|js|ts|tsx|jsx|cfg|ini"
    r"|lock|rules|css|html|rst|csv|sql|tex|bib|ipynb|env|log)$"
)
VERSION_RE = re.compile(r"^v?\d+(\.\d+)+$")

cmd_cache = {}
def cmd_missing(word):
    if word not in cmd_cache:
        try:
            rc = subprocess.run(
                ["bash", "-c", 'command -v -- "$1" >/dev/null 2>&1', "_", word]
            ).returncode
        except Exception:
            rc = 0  # can't check -> don't flag
        cmd_cache[word] = (rc != 0)
    return cmd_cache[word]

def is_url(w):
    return "://" in w or w.startswith("www.")

def resolve(word):
    w = word.rstrip("/") or "/"
    if w.startswith("~"):
        return os.path.expanduser(w)
    if os.path.isabs(w):
        return w
    return os.path.join(root, w)

def fence_path_reason(word):
    # Fenced-block path rule (path-checks only, no command checks). A token is a
    # path when it holds a "/", passes rule a, has no ":" (so gh:owner/repo and
    # other scheme-like tokens are left alone), and its basename looks like a
    # file (a recognised extension). Placeholders such as ./my-project have no
    # extension and are not flagged. Absolute and "~" paths are skipped too:
    # inside a fence they are machine-specific examples, not repo references.
    if "/" not in word or ":" in word:
        return None
    if any(ch in word for ch in BADCHARS):
        return None
    if word[0] in "-@#":
        return None
    if word.startswith("/") or word.startswith("~"):
        return None
    if is_url(word) or word in scanned_set:
        return None
    base = os.path.basename(word.rstrip("/"))
    if not FILE_RE.match(base) or VERSION_RE.match(base):
        return None
    if not os.path.exists(resolve(word)):
        return "missing path"
    return None

dead = []   # (file, word, reason)
seen = set()

for name in SCANNED:
    fp = os.path.join(root, name)
    if not os.path.isfile(fp):
        continue
    try:
        text = open(fp, encoding="utf-8", errors="ignore").read()
    except Exception:
        continue
    for m in SPAN.finditer(text):
        span = m.group(1)
        toks = span.split()
        if not toks:
            continue
        raw = toks[0]
        word = raw.rstrip(",.:;)")
        if not word:
            continue
        # rule a: skip non-references.
        if any(ch in word for ch in BADCHARS):
            continue
        if word[0] in "-@#":
            continue
        if word in scanned_set:
            continue
        if word.startswith("/") and word.count("/") == 1:
            continue
        if is_url(word):
            continue
        reason = None
        if "/" in word:
            # rule b: a slash makes it a path; check it.
            if not os.path.exists(resolve(word)):
                reason = "missing path"
        elif "." in word:
            # rule b (bare filename): a known extension and not a version.
            # The uppercase-stem carve-out is the one deliberate heuristic:
            # it keeps capitalized product names (`Node.js`, `React.js`) out
            # of the path check unless the repo really tracks such a file.
            stem = word.rsplit(".", 1)[0]
            if (FILE_RE.match(word)
                    and not VERSION_RE.match(word)
                    and (not any(c.isupper() for c in stem)
                         or word in tracked_basenames)):
                if (not os.path.exists(resolve(word))
                        and word not in tracked_basenames):
                    reason = "missing path"
        elif len(toks) >= 2 and CMD_RE.match(word):
            # rule c: command check; skip config-key labels ending in ':'.
            if not raw.rstrip(",;)").endswith(":") and cmd_missing(word):
                reason = "command not found"
        if reason:
            key = (name, word)
            if key not in seen:
                seen.add(key)
                dead.append((name, word, reason))

    # Fenced code blocks: path-checks only, first token only (see header). A
    # line starting with three backticks toggles the fence; inside, skip blank
    # and comment lines.
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        word = stripped.split()[0].rstrip(",.:;)")
        if not word:
            continue
        reason = fence_path_reason(word)
        if reason:
            key = (name, word)
            if key not in seen:
                seen.add(key)
                dead.append((name, word, reason))

if not dead:
    sys.exit(0)

n = len(dead)
out = ["Harness hygiene: %d stale reference(s) in agent docs" % n]
for name, word, reason in dead[:25]:
    out.append("  %s: %s (%s)" % (name, word, reason))
if n > 25:
    out.append("  ... and %d more" % (n - 25))
print("\n".join(out))
PY
exit 0
