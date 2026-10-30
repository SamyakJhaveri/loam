"""bin/shell_lint.py on temp repos: the done-checks' planted files, b086ef1's pre-fix file, tokenizer cases."""

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
# Lines that must not count, then lines that must (from line 18 on).
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
                         [f"cases.sh:{n}" for n in (18, 19, 20, 21, 23, 25, *range(26, 35))])

    def test_clean_tree_passes(self) -> None:
        res = lint({"ok.sh": "#!/bin/sh\nset -o pipefail\nout=$(echo hi); grep -q hi <<<\"$out\"\n"})
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertEqual(res.stdout, "")


if __name__ == "__main__":
    unittest.main()
