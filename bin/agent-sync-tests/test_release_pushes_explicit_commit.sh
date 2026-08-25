#!/usr/bin/env bash
# test_release_pushes_explicit_commit.sh  (Codex round 5, R5-H2)
# The release tag and push must target the EXACT validated commit object, not a
# mutable branch name. The old `tag -a "v$VERSION"` (tags HEAD) and
# `git push origin HEAD` resolve HEAD at run time, so a concurrent commit could
# change the tag target or the pushed commit. release.sh must capture the release
# commit's object id and tag/push THAT id explicitly.
#
# Safety (A5, both guards): mktemp repo, NO remote asserted empty, git push shim.
# The shim records the push args AND blocks the real push; the release runs to a
# shimmed completion (no refusal) so we can inspect what it WOULD push.
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
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/repo/bin/hub-ci.sh"   # GREEN -> healthy release
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

# The release commit object id, and what actually got pushed.
RELEASE_COMMIT="$("$REALGIT" rev-parse HEAD)"
pushed="$(cat "$PUSHLOG")"

# R5-H2: the push must carry the EXPLICIT release-commit OID to main, not "HEAD".
if grep -qwE 'HEAD' <<<"$pushed"; then
  echo "FAIL: push used the mutable 'HEAD' ref instead of the explicit commit object"; echo "pushed: $pushed"; exit 1
fi
if ! grep -qF "${RELEASE_COMMIT}:refs/heads/main" <<<"$pushed"; then
  echo "FAIL: push did not carry the explicit release-commit OID to refs/heads/main"; echo "pushed: $pushed"; echo "want ${RELEASE_COMMIT}:refs/heads/main"; exit 1
fi
# The annotated tag must point at that same explicit commit.
if [ "$("$REALGIT" rev-parse "v9.9.9^{commit}")" != "$RELEASE_COMMIT" ]; then
  echo "FAIL: tag v9.9.9 does not point at the release commit object"; exit 1
fi

echo "PASS test_release_pushes_explicit_commit.sh"
