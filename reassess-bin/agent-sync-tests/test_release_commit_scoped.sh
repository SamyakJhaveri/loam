#!/usr/bin/env bash
# test_release_commit_scoped.sh  (Codex C2)
# release.sh's commit must never publish anything but VERSION. `git commit -m`
# with no pathspec commits the whole INDEX, and the gates (hub-ci, ip-sweep) run
# AFTER the clean-tree pre-flight, so a gate side-effect or a concurrent process
# can stage content that the unscoped commit then publishes to a public remote.
# Fix: re-verify a clean index immediately before the VERSION write (refuse on
# drift) AND commit `-- VERSION`. This test drives the recheck: a hub-ci stub
# that stages an extra file must make release.sh REFUSE with zero mutation.
#
# Safety (A5, both guards): mktemp repo with NO remote, asserted empty; a git
# push-shim so no push can leave the box; forced by construction never to reach a
# real push.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"

mkdir -p "$TMP/shim"; MARKER="$TMP/push_attempted"
cat > "$TMP/shim/git" <<SHIM
#!/usr/bin/env bash
if [ "\$1" = "push" ]; then echo "PUSH BLOCKED: git \$*" >> "$MARKER"; exit 0; fi
exec "$REALGIT" "\$@"
SHIM
chmod +x "$TMP/shim/git"

mkdir -p "$TMP/repo/bin"
cp "$REAL_BIN/release.sh" "$TMP/repo/bin/release.sh"
cp "$REAL_BIN/lib.sh"     "$TMP/repo/bin/lib.sh"
# hub-ci stub: exits 0 (GREEN) but STAGES an extra file as a side effect - stands
# in for a gate side-effect or a concurrent process staging content mid-release.
cat > "$TMP/repo/bin/hub-ci.sh" <<'HUBCI'
#!/usr/bin/env bash
echo "sneaky staged content" > "$PWD/LEAK.txt"
git add "$PWD/LEAK.txt"
exit 0
HUBCI
chmod +x "$TMP/repo/bin/"*.sh
echo "1.1.0" > "$TMP/repo/VERSION"

cd "$TMP/repo"
"$REALGIT" -c init.defaultBranch=main init -q
"$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init
"$REALGIT" branch -M main

echo "--- remote (must be empty) ---"; "$REALGIT" remote -v
[ -z "$("$REALGIT" remote)" ] || { echo "FAIL(SAFETY): a remote is set"; exit 1; }

head_before="$("$REALGIT" rev-parse HEAD)"
tags_before="$("$REALGIT" tag -l)"

set +e
out="$(PATH="$TMP/shim:$PATH" bash bin/release.sh 9.9.9 2>&1)"
rc=$?
set -e

# The release must REFUSE (the index went dirty during the gates).
if [ "$rc" -eq 0 ]; then echo "FAIL: release.sh exited 0 despite a staged file appearing during the gates"; echo "$out"; exit 1; fi
# Never reached push.
if [ -f "$MARKER" ]; then echo "FAIL: release.sh reached the push step"; cat "$MARKER"; exit 1; fi
# Zero mutation, and crucially the staged LEAK.txt was NOT committed/published.
if [ "$("$REALGIT" rev-parse HEAD)" != "$head_before" ]; then
  echo "FAIL: HEAD moved - a release commit was made"; "$REALGIT" show --name-only --format= HEAD; exit 1
fi
if "$REALGIT" log --all --name-only --format= | grep -q 'LEAK.txt'; then
  echo "FAIL: LEAK.txt was committed (unscoped release commit published staged content)"; exit 1
fi
if [ "$("$REALGIT" tag -l)" != "$tags_before" ]; then echo "FAIL: a tag was created"; exit 1; fi

echo "PASS test_release_commit_scoped.sh"
