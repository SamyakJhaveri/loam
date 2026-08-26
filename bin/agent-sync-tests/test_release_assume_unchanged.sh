#!/usr/bin/env bash
# test_release_assume_unchanged.sh  (Codex round 3, FIX 2)
# release.sh's clean-tree check is `git status --porcelain`, which is BLIND to a
# tracked file marked --assume-unchanged (lowercase ls-files -v tag) or
# skip-worktree. hub-ci then validates the diverged WORKTREE bytes while the tag
# would publish the COMMITTED bytes. release.sh must refuse when any tracked path
# carries a non-`H` ls-files -v tag (whole-repo: the tag ships the whole tree).
#
# Safety (A5, both guards): mktemp repo, NO remote asserted empty, git push shim.
# Never reaches a real push.
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
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/repo/bin/hub-ci.sh"   # GREEN, so only the guard can stop it
chmod +x "$TMP/repo/bin/"*.sh
echo "1.1.0" > "$TMP/repo/VERSION"
echo "v1 committed" > "$TMP/repo/data.txt"
cd "$TMP/repo"
"$REALGIT" -c init.defaultBranch=main init -q
"$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init
"$REALGIT" branch -M main

# Diverge a tracked file in the worktree, then hide it with --assume-unchanged.
echo "v2 divergent worktree bytes" > data.txt
"$REALGIT" update-index --assume-unchanged data.txt
# Sanity: the divergence is hidden from status (the hole) and tagged lowercase.
[ -z "$("$REALGIT" status --porcelain)" ] || { echo "FIXTURE-BUG: assume-unchanged should hide the change from status"; exit 1; }
"$REALGIT" ls-files -v | grep -q '^[a-z] ' || { echo "FIXTURE-BUG: expected a lowercase ls-files -v tag"; exit 1; }

[ -z "$("$REALGIT" remote)" ] || { echo "FAIL(SAFETY): a remote is set"; exit 1; }
h0="$("$REALGIT" rev-parse HEAD)"; t0="$("$REALGIT" tag -l)"

set +e
out="$(PATH="$TMP/shim:$PATH" bash bin/release.sh 9.9.9 2>&1)"
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: release.sh exited 0 with an assume-unchanged tracked file (status-blind)"; echo "$out"; exit 1; fi
if [ -f "$MARKER" ]; then echo "FAIL: release.sh reached the push step"; cat "$MARKER"; exit 1; fi
if [ "$("$REALGIT" rev-parse HEAD)" != "$h0" ]; then echo "FAIL: HEAD moved"; exit 1; fi
if [ "$("$REALGIT" tag -l)" != "$t0" ]; then echo "FAIL: a tag was created"; exit 1; fi
# The refusal must name the assume-unchanged condition (not some unrelated die).
if ! grep -qiE 'assume-unchanged|skip-worktree' <<<"$out"; then
  echo "FAIL: refusal did not cite the assume-unchanged/skip-worktree condition"; echo "$out"; exit 1
fi

echo "PASS test_release_assume_unchanged.sh"
