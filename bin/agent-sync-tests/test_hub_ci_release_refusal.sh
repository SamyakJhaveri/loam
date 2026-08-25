#!/usr/bin/env bash
# test_hub_ci_release_refusal.sh
# release.sh must REFUSE to cut a release while hub-ci is red, at pre-flight -
# before it writes VERSION, commits, tags, or (critically) PUSHES. release.sh has
# two `git push` lines, so this test is built so a push can NEVER leave the box,
# even if the gate wiring regressed:
#
#   Guard 1 (fail-closed): the throwaway repo is created with `git init` and has
#   NO remote; we ASSERT `git remote` is empty immediately before invoking
#   release.sh and abort if anything is set.
#   Guard 2 (structural): a `git` shim is placed first on PATH that forwards every
#   subcommand to the real git EXCEPT `push`, which it records to a marker file
#   and exits 0. So an outbound push is structurally impossible here; the marker
#   instead becomes evidence of whether release.sh ever REACHED the push step.
#
# Against the WIRED release.sh with a red hub-ci, the gate fires at pre-flight:
# nonzero exit, hub-ci named, zero mutation, and the push marker is ABSENT
# (it never reached Step 4). Against an unwired release.sh the same harness would
# show the marker present and VERSION mutated - that is the RED, and it still
# cannot push because of the shim.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"   # bin/
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --- Guard 2: a git shim that neuters `push` --------------------------------
REALGIT="$(command -v git)"           # captured BEFORE the shim is on PATH
SHIMDIR="$TMP/shim"
MARKER="$TMP/push_attempted"
mkdir -p "$SHIMDIR"
cat > "$SHIMDIR/git" <<SHIM
#!/usr/bin/env bash
if [ "\$1" = "push" ]; then
  echo "PUSH BLOCKED BY SHIM: git \$*" >> "$MARKER"
  exit 0
fi
exec "$REALGIT" "\$@"
SHIM
chmod +x "$SHIMDIR/git"

# --- Build a hermetic release repo (no remote, ever) ------------------------
mkdir -p "$TMP/repo/bin"
cp "$REAL_BIN/release.sh" "$TMP/repo/bin/release.sh"
cp "$REAL_BIN/lib.sh"     "$TMP/repo/bin/lib.sh"
# Force the gate red. hub-ci runs before ip-sweep in release.sh, so this decides
# the outcome and ip-sweep never runs (none is shipped here).
printf '#!/usr/bin/env bash\necho "hub-ci: forced failure (drill)" >&2\nexit 1\n' > "$TMP/repo/bin/hub-ci.sh"
chmod +x "$TMP/repo/bin/"*.sh
echo "0.0.0" > "$TMP/repo/VERSION"

cd "$TMP/repo"
"$REALGIT" -c init.defaultBranch=main init -q
"$REALGIT" add -A
"$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init
"$REALGIT" branch -M main

# --- Guard 1: assert NO remote, fail-closed, right before release.sh --------
echo "--- git remote -v (must be empty) ---"; "$REALGIT" remote -v; echo "--- end remotes ---"
if [ -n "$("$REALGIT" remote)" ]; then
  echo "FAIL(SAFETY): a remote is configured on the throwaway repo; refusing to run release.sh"; exit 1
fi

# --- Snapshot the pre-state (must be byte-identical afterward) ---------------
head_before="$("$REALGIT" rev-parse HEAD)"
version_before="$(cat VERSION)"
tags_before="$("$REALGIT" tag -l)"

# --- Run the release drill under the shim: it MUST refuse -------------------
set +e
out="$(PATH="$SHIMDIR:$PATH" bash bin/release.sh 9.9.9 2>&1)"
rc=$?
set -e

if [ "$rc" -eq 0 ]; then
  echo "FAIL: release.sh exited 0 with a failing hub-ci (it should have refused)"; echo "$out"; exit 1
fi
if ! grep -qi 'hub-ci' <<<"$out"; then
  echo "FAIL: refusal message does not mention hub-ci"; echo "$out"; exit 1
fi

# --- The gate fired at pre-flight: it never reached the push step -----------
if [ -f "$MARKER" ]; then
  echo "FAIL: release.sh reached the push step (marker present) despite a red hub-ci"; cat "$MARKER"; exit 1
fi

# --- Assert ZERO mutation ----------------------------------------------------
if [ "$("$REALGIT" rev-parse HEAD)" != "$head_before" ]; then
  echo "FAIL: HEAD moved (a commit was made despite the refusal)"; exit 1
fi
if [ "$(cat VERSION)" != "$version_before" ]; then
  echo "FAIL: VERSION was rewritten despite the refusal ($(cat VERSION))"; exit 1
fi
if [ "$("$REALGIT" tag -l)" != "$tags_before" ]; then
  echo "FAIL: a tag was created despite the refusal"; "$REALGIT" tag -l; exit 1
fi
if [ -n "$("$REALGIT" status --porcelain)" ]; then
  echo "FAIL: working tree is dirty after the refusal (partial mutation)"; "$REALGIT" status --porcelain; exit 1
fi
if "$REALGIT" tag -l | grep -q 'v9.9.9'; then
  echo "FAIL: tag v9.9.9 exists"; exit 1
fi

echo "PASS test_hub_ci_release_refusal.sh"
