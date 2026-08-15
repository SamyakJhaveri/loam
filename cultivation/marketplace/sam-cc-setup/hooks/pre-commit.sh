#!/usr/bin/env bash
# Native git pre-commit hook: fast deterministic checks only (<10s).
# Installed per-clone by /bootstrap-cc-setup: ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
# Heavier validation stays in /validate, run on demand.

set -uo pipefail
fail=0

# Whitespace errors and conflict markers in the staged diff
if ! git diff --cached --check; then
    echo "pre-commit: whitespace/conflict-marker check failed" >&2
    fail=1
fi

# Syntax-check staged shell scripts
for f in $(git diff --cached --name-only --diff-filter=ACM | grep '\.sh$'); do
    if ! bash -n "$f"; then
        echo "pre-commit: bash syntax error in $f" >&2
        fail=1
    fi
done

# Syntax-check staged python files
for f in $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$'); do
    if ! python3 -m py_compile "$f" 2>&1; then
        echo "pre-commit: python syntax error in $f" >&2
        fail=1
    fi
done

# Project-specific fast checks, when present
if [ -x "bin/precommit-checks.sh" ]; then
    if ! bin/precommit-checks.sh; then
        echo "pre-commit: bin/precommit-checks.sh failed" >&2
        fail=1
    fi
fi

exit $fail
