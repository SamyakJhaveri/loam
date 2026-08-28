#!/usr/bin/env bash
# test_release_atomic_publish.sh  (Codex round 5, R5-H3)
# The commit and the tag must be published in ONE atomic push. The old code ran
# `git push origin HEAD` then `git push origin "v$VERSION"` as two separate
# pushes, so the branch push could succeed and the tag push then fail, leaving a
# PARTIAL public release. release.sh must use a single `git push --atomic`
# carrying both refs.
#
# Safety (A5, both guards): mktemp repo, NO remote asserted empty, git push shim
# records args and blocks the real push; the release runs to a shimmed completion.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"

mkdir -p "$TMP/shim"; PUSHLOG="$TMP/push_args"
cat > "$TMP/shim/git" <<SHIM
#!/usr/bin/env bash
if [ "\$1" = "push" ]; then printf '%s\n' "\$*" >> "$PUSHLOG"; exit 0; fi
exec "$REALGIT" "\$@"
SHIM
chmod +x "$TMP/shim/git"

mkdir -p "$TMP/repo/bin"
cp "$REAL_BIN/release.sh" "$TMP/repo/bin/release.sh"
cp "$REAL_BIN/lib.sh"     "$TMP/repo/bin/lib.sh"
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/repo/bin/hub-ci.sh"
chmod +x "$TMP/repo/bin/"*.sh
echo "1.1.0" > "$TMP/repo/VERSION"
cd "$TMP/repo"
"$REALGIT" -c init.defaultBranch=main init -q
"$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init
"$REALGIT" branch -M main
[ -z "$("$REALGIT" remote)" ] || { echo "FAIL(SAFETY): a remote is set"; exit 1; }

set +e
out="$(PATH="$TMP/shim:$PATH" bash bin/release.sh 9.9.9 2>&1)"
rc=$?
set -e
if [ "$rc" -ne 0 ]; then echo "FAIL: healthy release did not complete (rc=$rc)"; echo "$out"; exit 1; fi
[ -f "$PUSHLOG" ] || { echo "FAIL: release never reached the push step"; echo "$out"; exit 1; }

# R5-H3: exactly ONE push invocation.
n="$(wc -l < "$PUSHLOG" | tr -d ' ')"
if [ "$n" -ne 1 ]; then echo "FAIL: expected exactly 1 (atomic) push, got $n"; echo "--- pushes ---"; cat "$PUSHLOG"; exit 1; fi
pushed="$(cat "$PUSHLOG")"
# It must use --atomic and carry BOTH the commit refspec and the tag together.
grep -qw -- '--atomic' <<<"$pushed" || { echo "FAIL: the single push is not --atomic"; echo "pushed: $pushed"; exit 1; }
grep -qF 'refs/heads/main' <<<"$pushed" || { echo "FAIL: the push does not carry the main refspec"; echo "pushed: $pushed"; exit 1; }
grep -qE 'refs/tags/v9\.9\.9|(^| )v9\.9\.9( |$)' <<<"$pushed" || { echo "FAIL: the push does not carry the tag"; echo "pushed: $pushed"; exit 1; }

echo "PASS test_release_atomic_publish.sh"
