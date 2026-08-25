#!/usr/bin/env bash
# test_release_recheck_complete.sh  (Codex round 4, R4-H2)
# The pre-mutation recheck must be COMPLETE. release.sh captures no HEAD before the
# gates, so a concurrent CLEAN commit during the gates is invisible to its
# branch/status/tag recheck, and a gate that sets assume-unchanged mid-run is
# invisible too - either way release.sh would publish content hub-ci never
# validated. The recheck must require the identical HEAD and re-run the ls-files -v
# guard.
#   leg A: a hub-ci stub makes a concurrent clean commit -> HEAD moved -> refuse.
#   leg B: a hub-ci stub sets --assume-unchanged on a tracked file -> refuse.
#
# Safety (A5, both guards): mktemp repos, NO remote asserted empty, git push shim.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"

# $1 = leg name ; $2 = hub-ci stub body. Builds a fresh repo, runs release.sh
# under the push shim, and asserts it refuses with zero publish.
run_leg() {
  local leg="$1" stub="$2"
  local root="$TMP/$leg" marker="$TMP/push_$leg" t0 rc out
  mkdir -p "$root/bin" "$root/shim"
  cat > "$root/shim/git" <<SHIM
#!/usr/bin/env bash
if [ "\$1" = "push" ]; then echo "PUSH BLOCKED: git \$*" >> "$marker"; exit 0; fi
exec "$REALGIT" "\$@"
SHIM
  chmod +x "$root/shim/git"
  cp "$REAL_BIN/release.sh" "$root/bin/release.sh"
  cp "$REAL_BIN/lib.sh"     "$root/bin/lib.sh"
  printf '%s\n' "$stub" > "$root/bin/hub-ci.sh"
  chmod +x "$root/bin/"*.sh
  echo "1.1.0" > "$root/VERSION"
  echo "tracked v1" > "$root/data.txt"
  ( cd "$root" && "$REALGIT" -c init.defaultBranch=main init -q \
    && "$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init \
    && "$REALGIT" branch -M main )
  [ -z "$("$REALGIT" -C "$root" remote)" ] || { echo "FAIL(SAFETY) $leg: a remote is set"; exit 1; }
  t0="$("$REALGIT" -C "$root" tag -l)"
  set +e
  out="$(cd "$root" && PATH="$root/shim:$PATH" bash bin/release.sh 9.9.9 2>&1)"
  rc=$?
  set -e
  if [ "$rc" -eq 0 ]; then echo "FAIL $leg: release.sh exited 0 despite the concurrent change during the gates"; echo "$out"; exit 1; fi
  if [ -f "$marker" ]; then echo "FAIL $leg: release.sh reached the push step"; cat "$marker"; exit 1; fi
  if [ "$("$REALGIT" -C "$root" tag -l)" != "$t0" ]; then echo "FAIL $leg: a tag was created"; exit 1; fi
  # release.sh must not have added its own release commit on top of the drift.
  if "$REALGIT" -C "$root" log --format='%s' | grep -q '^release: v9.9.9$'; then
    echo "FAIL $leg: a release commit was made despite the drift"; exit 1
  fi
  echo "  leg $leg: refused as expected"
}

# leg A: concurrent clean commit during the gate (invisible to status/branch/tag).
run_leg A "$(printf '#!/usr/bin/env bash\ngit -c user.email=g@g -c user.name=g commit -q --allow-empty -m "concurrent clean commit" >/dev/null 2>&1\nexit 0\n')"

# leg B: gate sets assume-unchanged on a tracked file (hidden from status).
run_leg B "$(printf '#!/usr/bin/env bash\ngit update-index --assume-unchanged data.txt >/dev/null 2>&1\nexit 0\n')"

echo "PASS test_release_recheck_complete.sh"
