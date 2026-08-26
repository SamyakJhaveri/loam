#!/usr/bin/env bash
# test_hub_ci_release_repo_binding.sh  (Codex H3)
# release.sh runs its pre-flight git commands (branch/status/tag) and its
# mutations (commit/tag/push) against the CALLER's cwd, while the hub-ci gate is
# resolved from the script's own path. So an absolute-path invocation from a
# DIFFERENT repo would validate one repo but tag/push the other. release.sh must
# operate on ITS OWN repository, not the caller's cwd.
#
# Design (never reaches push - both A5 guards present anyway):
#   repoA = the script's repo: branch main, clean, wired release.sh, hub-ci
#           FORCED RED so release.sh dies at the gate (never mutates, never pushes).
#   repoB = the caller's cwd: on a NON-main branch.
#   Run `cd repoB && bash repoA/bin/release.sh 9.9.9`.
#   Correct binding -> release.sh operates on repoA (main), reaches the hub-ci
#   gate, and refuses with "hub-ci failed". The cwd-relative bug -> release.sh
#   reads repoB's branch and dies "must be created from main" instead, never
#   reaching repoA's gate. So: the refusal MENTIONS hub-ci iff the binding is right.
# Safety: fail-closed empty-remote assert on BOTH repos + a git push-shim.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REAL_BIN="$(dirname "$SCRIPT_DIR")"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
REALGIT="$(command -v git)"          # captured BEFORE the shim is on PATH

# --- git push shim: forward all but push (record + exit 0), never recurse ----
mkdir -p "$TMP/shim"; MARKER="$TMP/push_attempted"
cat > "$TMP/shim/git" <<SHIM
#!/usr/bin/env bash
if [ "\$1" = "push" ]; then echo "PUSH BLOCKED: git \$*" >> "$MARKER"; exit 0; fi
exec "$REALGIT" "\$@"
SHIM
chmod +x "$TMP/shim/git"

# --- repoA: the script's repo (main, wired release.sh, forced-red hub-ci) ----
mkdir -p "$TMP/repoA/bin"
cp "$REAL_BIN/release.sh" "$TMP/repoA/bin/release.sh"
cp "$REAL_BIN/lib.sh"     "$TMP/repoA/bin/lib.sh"
printf '#!/usr/bin/env bash\necho "hub-ci: forced red (binding test)" >&2\nexit 1\n' > "$TMP/repoA/bin/hub-ci.sh"
chmod +x "$TMP/repoA/bin/"*.sh
echo "1.1.0" > "$TMP/repoA/VERSION"
( cd "$TMP/repoA" && "$REALGIT" -c init.defaultBranch=main init -q \
  && "$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init \
  && "$REALGIT" branch -M main )

# --- repoB: the caller's cwd, on a NON-main branch --------------------------
mkdir -p "$TMP/repoB"
( cd "$TMP/repoB" && "$REALGIT" -c init.defaultBranch=main init -q \
  && echo x > f && "$REALGIT" add -A && "$REALGIT" -c user.email=t@t -c user.name=t commit -q -m init \
  && "$REALGIT" checkout -q -b feature )

# --- Guard 1: assert NEITHER repo has a remote (fail-closed) -----------------
for r in repoA repoB; do
  echo "--- $r remotes ---"; "$REALGIT" -C "$TMP/$r" remote -v
  if [ -n "$("$REALGIT" -C "$TMP/$r" remote)" ]; then echo "FAIL(SAFETY): $r has a remote"; exit 1; fi
done

headA_before="$("$REALGIT" -C "$TMP/repoA" rev-parse HEAD)"
headB_before="$("$REALGIT" -C "$TMP/repoB" rev-parse HEAD)"

# --- Run from repoB, invoking repoA's release.sh by absolute path -----------
cd "$TMP/repoB"
set +e
out="$(PATH="$TMP/shim:$PATH" bash "$TMP/repoA/bin/release.sh" 9.9.9 2>&1)"
rc=$?
set -e

if [ "$rc" -eq 0 ]; then echo "FAIL: release.sh exited 0 (should have refused at the gate)"; echo "$out"; exit 1; fi
# The binding is correct iff release.sh reached repoA's hub-ci gate.
if ! grep -qi 'hub-ci' <<<"$out"; then
  echo "FAIL: refusal did not come from the hub-ci gate - release.sh acted on the caller cwd, not its own repo"; echo "$out"; exit 1
fi
# Never reached push, and no repo mutated.
if [ -f "$MARKER" ]; then echo "FAIL: release.sh reached the push step"; cat "$MARKER"; exit 1; fi
if [ "$("$REALGIT" -C "$TMP/repoA" rev-parse HEAD)" != "$headA_before" ]; then echo "FAIL: repoA mutated"; exit 1; fi
if [ "$("$REALGIT" -C "$TMP/repoB" rev-parse HEAD)" != "$headB_before" ]; then echo "FAIL: repoB (caller) mutated"; exit 1; fi
if "$REALGIT" -C "$TMP/repoA" tag -l | grep -q 'v9.9.9'; then echo "FAIL: repoA gained tag v9.9.9"; exit 1; fi
if "$REALGIT" -C "$TMP/repoB" tag -l | grep -q 'v9.9.9'; then echo "FAIL: repoB gained tag v9.9.9"; exit 1; fi

echo "PASS test_hub_ci_release_repo_binding.sh"
