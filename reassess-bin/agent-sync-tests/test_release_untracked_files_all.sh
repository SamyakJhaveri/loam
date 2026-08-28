#!/usr/bin/env bash
# test_release_untracked_files_all.sh  (Codex round 4, R4-H1)
# release.sh's clean-tree checks use `git status --porcelain`, which HONORS a
# repo-level `status.showUntrackedFiles=no`. With that config, an untracked
# non-ignored file is invisible to the check: it can influence the worktree-based
# hub-ci gate, stay out of the tag, and still reach the public push. release.sh
# must force `--untracked-files=all` (reuses bin/agent-sync-scan.sh M3, 5b7a1a5).
#
# Safety (A5, both guards): mktemp repo, NO remote asserted empty, git push shim.
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
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/repo/bin/hub-ci.sh"   # GREEN, so only the clean check can stop it
chmod +x "$TMP/repo/bin/"*.sh
echo "1.1.0" > "$TMP/repo/VERSION"
cd "$TMP/repo"
"$REALGIT" -c init.defaultBranch=main init -q
"$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init
"$REALGIT" branch -M main

# The blinding config + an untracked non-ignored file it hides.
"$REALGIT" config status.showUntrackedFiles no
echo "untracked content not in any tag" > "$TMP/repo/LEAK.txt"
# Sanity: bare status is blinded (the hole); -uall would see it.
[ -z "$("$REALGIT" status --porcelain)" ] || { echo "FIXTURE-BUG: bare status should be blinded by the config"; exit 1; }
[ -n "$("$REALGIT" status --porcelain --untracked-files=all)" ] || { echo "FIXTURE-BUG: -uall should see LEAK.txt"; exit 1; }

[ -z "$("$REALGIT" remote)" ] || { echo "FAIL(SAFETY): a remote is set"; exit 1; }
h0="$("$REALGIT" rev-parse HEAD)"; t0="$("$REALGIT" tag -l)"

set +e
out="$(PATH="$TMP/shim:$PATH" bash bin/release.sh 9.9.9 2>&1)"
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: release.sh exited 0 with an untracked file hidden by status.showUntrackedFiles=no"; echo "$out"; exit 1; fi
if [ -f "$MARKER" ]; then echo "FAIL: release.sh reached the push step"; cat "$MARKER"; exit 1; fi
if [ "$("$REALGIT" rev-parse HEAD)" != "$h0" ]; then echo "FAIL: HEAD moved"; exit 1; fi
if [ "$("$REALGIT" tag -l)" != "$t0" ]; then echo "FAIL: a tag was created"; exit 1; fi

echo "PASS test_release_untracked_files_all.sh"
