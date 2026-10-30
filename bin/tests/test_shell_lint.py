"""bin/shell_lint.py on temp repos: the done-checks' planted files, b086ef1's and c29ef01's pre-fix files,
tokenizer cases, and the bash 4 and GNU-only forms."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "bin/shell_lint.py"

BAD = "#!/usr/bin/env bash\nset -o pipefail\necho hi | grep -q hi && echo yes\necho hi | grep -vq x || echo no\n"
NO_PIPEFAIL = "#!/usr/bin/env bash\necho hi | grep -q hi && echo yes\n"
# Lines that must not count, then lines that must (lines 18 to 34), then substitutions from line 35,
# then heredocs inside a substitution, case words and grep continuations from line 50.
CASES = """#!/usr/bin/env bash
set -euo pipefail
fail a "lacks | grep -q"  # a quoted pipe is one word
true || grep -q x f
echo hi | grep -c x
cat <<'EOF'
echo hi | grep -q x
EOF
printf 'query\\nquery\\n' | grep -equery
cat f | grep -fqfile
n=$((n+1)); cat <<EOF
echo hi | grep -q x
EOF
printf '%s\\n' "Example:
cmd | grep -q needle
"
echo hi # | grep -q x
echo "${#x}" | grep -Eq y
x=$'a\\'' ; echo hi | grep -q z
echo hi |& LC_ALL=C grep --quiet y
echo hi |
  grep -q y
echo hi | \\
  grep -xq y
echo $((1 << 2)) | grep -q 4
supported="$(yes needle | grep -q needle && echo yes || echo no)"
x="$(cmd | grep -q x)"
if [ -n "$(cmd | grep -q x)" ]; then
x="$(a "$(b)" | grep -q x)"
x="`cmd | grep -q x`"
yes '# heading' | grep -e '# heading' -q
yes '# heading' | grep -q '# heading'
echo "# x" | grep -q x
printf '## Merge checklist\\n' | grep -q x
out="$(printf '%s\\n' "cmd | grep -q needle")"
out="$(cat <<'EOF'
cmd | grep -q needle
EOF
)"
out="$(printf '%s\\n' 'Example:
cmd | grep -q needle
')"
out="$(yes needle |
  grep -q needle)"
out="$(yes needle | \\
  grep -q needle)"
out="$(case check in
  check) yes needle | grep -q needle ;;
esac)"
out="$(cat <<'EOF'
It's ready.
EOF
)"
yes needle | grep -q needle
out="$(cat <<'EOF'
1) Run "cmd | grep -q needle".
EOF
)"
out="$(case " $* " in
  *) yes needle | grep -q needle ;;
esac)"
out="$(case "$(printf x)" in
  x) yes needle | grep -q needle ;;
esac)"
yes needle | grep \\
  -q needle
out="$(yes needle | grep \\
  -q needle)"
out="$(cat <<'EOF'
It's
EOF
yes needle | grep -q needle
)"
"""

# The done-checks' planted files for #280, verbatim.
GNU_BAD = ('#!/usr/bin/env bash\nmapfile -t a < f\nreadarray -t b < f\nls | xargs -r echo\nstat -c %Y f\n'
           'grep -P "x" f\ntimeout 5 sleep 1\n')
GNU_GOOD = ('#!/usr/bin/env bash\n# mapfile is bash 4, so read in a loop\nm=$(stat -c %Y f 2>/dev/null || stat -f %m f)\n'
            'command -v timeout >/dev/null && timeout 5 true\n')
# Forms that must count (lines 2 to 9; a continued stat counts on its first line), then words that must not (from line 10).
GNU_CASES = """#!/usr/bin/env bash
x="$(stat -c %Y f)"
find . -print0 | xargs -0 -r rm
env LC_ALL=C grep -Pq x f
if true; then readarray -t a < f; fi
stat \\
  --format=%Y f
y="$(cat f |
  grep --perl-regexp x)"
cat <<'EOF'
mapfile -t a < f
EOF
echo "mapfile -t a < f" 'grep -P x'
x="$(stat -c %Y f 2>/dev/null || stat -f %m f)"
for c in $(pgrep -P 1); do :; done
for t in timeout mapfile; do :; done
grep -eP x f
ls | xargs -I {} echo -r {}
"""
GUARDED = """#!/usr/bin/env bash
t="$(command -v timeout)"
timeout 5 true
"""


def lint(files: dict[str, str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        for name, text in files.items():
            (root / name).write_text(text, encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "-A"], cwd=root, check=True)
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(root)],
                              capture_output=True, text=True)


class ShellLintTest(unittest.TestCase):
    def test_flags_planted_pipes_only_under_pipefail(self) -> None:
        res = lint({"bad.sh": BAD, "nopipefail.sh": NO_PIPEFAIL})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual([line.split(": ")[1] for line in res.stdout.splitlines()], ["bad.sh:3", "bad.sh:4"])
        self.assertIn("capture the output first", res.stdout)

    def test_flags_b086ef1_pre_fix(self) -> None:
        old = subprocess.run(["git", "-C", str(ROOT), "show", "b086ef1^:seed/_gh_setup.sh"],
                             capture_output=True, text=True, check=True).stdout
        res = lint({"gh_setup.sh": old})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertIn("gh_setup.sh:65:", res.stdout)

    def test_tokenizer_cases(self) -> None:
        res = lint({"cases.sh": CASES})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual([line.split(": ")[1] for line in res.stdout.splitlines()],
                         [f"cases.sh:{n}" for n in (18, 19, 20, 21, 23, 25, *range(26, 35), 43, 45, 48,
                                                    54, 60, 63, 65, 67, 72)])

    def test_flags_planted_gnu_forms(self) -> None:
        res = lint({"bad.sh": GNU_BAD, "good.sh": GNU_GOOD})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual([line.split(": ")[1] for line in res.stdout.splitlines()], [f"bad.sh:{n}" for n in range(2, 8)])
        for form in ("while IFS= read -r", "drop it", "stat -f %m", "grep -E", "command -v timeout"):
            self.assertIn(form, res.stdout)

    def test_gnu_cases(self) -> None:
        res = lint({"cases.sh": GNU_CASES, "guarded.sh": GUARDED})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual([line.split(": ")[1] for line in res.stdout.splitlines()],
                         [f"cases.sh:{n}" for n in (2, 3, 4, 5, 6, 9)])

    def test_flags_c29ef01_pre_fix(self) -> None:
        old = subprocess.run(["git", "-C", str(ROOT), "show", "c29ef01^:seed/bin/memsearch"],
                             capture_output=True, text=True, check=True).stdout
        res = lint({"memsearch": old})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual([line.split(": ")[1] for line in res.stdout.splitlines()], ["memsearch:55"])

    def test_guarded_factory_passes(self) -> None:
        # bin/factory runs timeout behind command -v timeout (#426), so the file passes.
        res = lint({"factory": (ROOT / "bin/factory").read_text(encoding="utf-8")})
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_open_quote_fails_closed(self) -> None:
        res = lint({"open.sh": "#!/usr/bin/env bash\necho 'oops\nset -o pipefail\nyes | grep -q x\n"})
        self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
        self.assertEqual([line.split(": ")[1] for line in res.stdout.splitlines()], ["open.sh:2"])
        self.assertIn("could not find the end of the quote, substitution or heredoc", res.stdout)

    def test_clean_tree_passes(self) -> None:
        res = lint({"ok.sh": "#!/bin/sh\nset -o pipefail\nout=$(echo hi); grep -q hi <<<\"$out\"\n"})
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(res.stdout, "")


if __name__ == "__main__":
    unittest.main()
