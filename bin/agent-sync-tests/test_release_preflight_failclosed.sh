#!/usr/bin/env bash
# test_release_preflight_failclosed.sh  (Codex H6)
# release.sh's pre-flight must FAIL CLOSED. `[[ -z "$(git status --porcelain)" ]]`
# reads a FAILED git status as a clean tree (empty output), and
# `git tag -l | grep -q .` reads a failed git tag as "tag absent" - either way it
# proceeds to mutate and push. A git error must REFUSE the release, not green-light
# it. Two legs: git status fails, git tag fails.
#
# Safety (A5, both guards): mktemp repo, NO remote asserted empty, git push-shim.
# The shim also injects the targeted git failure (status/tag exits nonzero) while
# forwarding everything else to the real git.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"

mkdir -p "$TMP/repo/bin"
cp "$REAL_BIN/release.sh" "$TMP/repo/bin/release.sh"
cp "$REAL_BIN/lib.sh"     "$TMP/repo/bin/lib.sh"
# hub-ci stub is GREEN, so ONLY the pre-flight git error can stop the release.
printf '#!/usr/bin/env bash\nexit 0\n' > "$TMP/repo/bin/hub-ci.sh"
chmod +x "$TMP/repo/bin/"*.sh
echo "1.1.0" > "$TMP/repo/VERSION"
cd "$TMP/repo"
"$REALGIT" -c init.defaultBranch=main init -q
"$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init
"$REALGIT" branch -M main
[ -z "$("$REALGIT" remote)" ] || { echo "FAIL(SAFETY): a remote is set"; exit 1; }

# $1 = the git subcommand to force-fail (status|tag)
make_shim() {
  local fail_cmd="$1"
  local dir="$TMP/shim_$fail_cmd"
  mkdir -p "$dir"
  cat > "$dir/git" <<SHIM
#!/usr/bin/env bash
if [ "\$1" = "push" ]; then echo "PUSH BLOCKED: git \$*" >> "$TMP/push_$fail_cmd"; exit 0; fi
if [ "\$1" = "$fail_cmd" ]; then exit 3; fi
exec "$REALGIT" "\$@"
SHIM
  chmod +x "$dir/git"
  echo "$dir"
}

run_leg() { # $1 = status|tag
  local fail_cmd="$1" shimdir h0 t0 rc out
  shimdir="$(make_shim "$fail_cmd")"
  h0="$("$REALGIT" rev-parse HEAD)"; t0="$("$REALGIT" tag -l)"
  set +e; out="$(PATH="$shimdir:$PATH" bash bin/release.sh 9.9.9 2>&1)"; rc=$?; set -e
  if [ "$rc" -eq 0 ]; then echo "FAIL leg[$fail_cmd]: release exited 0 though git $fail_cmd errored (fail-open)"; echo "$out"; return 1; fi
  if [ -f "$TMP/push_$fail_cmd" ]; then echo "FAIL leg[$fail_cmd]: reached push"; return 1; fi
  if [ "$("$REALGIT" rev-parse HEAD)" != "$h0" ]; then echo "FAIL leg[$fail_cmd]: HEAD moved"; return 1; fi
  if [ "$("$REALGIT" tag -l)" != "$t0" ]; then echo "FAIL leg[$fail_cmd]: tag created"; return 1; fi
  return 0
}

run_leg status || exit 1
run_leg tag || exit 1

echo "PASS test_release_preflight_failclosed.sh"
