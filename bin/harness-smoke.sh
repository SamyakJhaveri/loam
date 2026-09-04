#!/usr/bin/env bash
# harness-smoke.sh - render the seed and prove the harness works and guides well.
#
# Four stages, one verdict. Tests the seed you are about to ship (the working
# tree), not the last release tag. Reuses the contract checker and the listing
# scorer; only the live stage is new machinery.
#
#   1 render   - copier renders the seed into a scratch project
#   2 contract - bin/rendered_harness_contract.py against the render
#   3 weight   - bin/skill_listing_weight.py (Score B: always-loaded tokens)
#   4 live     - (--live only) a real headless `claude -p` turn in the rendered
#                project proves the hooks actually DISPATCH, not just that they
#                pass when called directly (which the unit fixtures already show)
#
# Fast lane (default): stages 1-3, deterministic, no model calls.
# Live lane (--live):  adds stage 4. Needs the `claude` CLI; makes model calls.
#
# Exit 0 = PASS, 1 = FAIL. Appends one line to bin/harness-smoke.log.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LIVE=0
for arg in "$@"; do
  case "$arg" in
    --live) LIVE=1 ;;
    *) echo "usage: harness-smoke.sh [--live]" >&2; exit 2 ;;
  esac
done

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAIL=0
RENDER="$TMP/render"

echo "== stage 1: render the working-tree seed =="
# The rig must test what is about to ship. `copier ... --vcs-ref=HEAD` renders
# committed state, so a dirty seed/ would be rendered stale. Fail fast and say
# so, rather than silently scoring the wrong tree.
if [ -n "$(git status --porcelain seed/ copier.yml 2>/dev/null)" ]; then
  echo "NOTE: seed/ or copier.yml has uncommitted changes; the render reflects HEAD, not the working tree."
  echo "      Commit seed changes before trusting the scores below."
fi
COPIER=()
if command -v copier >/dev/null 2>&1; then COPIER=(copier)
elif command -v uvx >/dev/null 2>&1; then COPIER=(uvx copier)
else echo "FAIL: neither copier nor uvx found."; exit 1
fi
if "${COPIER[@]}" copy --trust --defaults --vcs-ref=HEAD \
    --data project_name=smokeproj --data github_repo= \
    "$ROOT" "$RENDER" >"$TMP/render.log" 2>&1; then
  echo "render: OK"
else
  echo "FAIL: render failed. Log tail:"; tail -20 "$TMP/render.log"; exit 1
fi

echo "== stage 2: rendered harness contract =="
if python3 bin/rendered_harness_contract.py --source-root "$ROOT" \
    --rendered-root "$RENDER" >"$TMP/contract.log" 2>&1; then
  echo "contract: OK"
else
  echo "FAIL: contract violations:"; tail -20 "$TMP/contract.log"; FAIL=1
fi

echo "== stage 3: skill-listing token weight (Score B) =="
WEIGHT_JSON="$(python3 bin/skill_listing_weight.py --root "$ROOT" --json)"
SEED_TOKENS="$(printf '%s' "$WEIGHT_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("seed",{}).get("listing_tokens",0))')"
PLUGIN_TOKENS="$(printf '%s' "$WEIGHT_JSON" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("sam-cc-setup",{}).get("listing_tokens",0))')"
echo "score.B seed_listing_tokens=$SEED_TOKENS plugin_listing_tokens=$PLUGIN_TOKENS"

HOOK_FIRE="skipped"
if [ "$LIVE" -eq 1 ]; then
  echo "== stage 4: live hook-dispatch proof =="
  if ! command -v claude >/dev/null 2>&1; then
    echo "FAIL: --live needs the claude CLI, which is not on PATH."; FAIL=1
  else
    # A real headless turn that must run a Bash command. If the PostToolUse Bash
    # audit hook dispatches, .claude/audit.log gains a line. That is end-to-end
    # proof the hook fires in a session, not just in a unit test.
    ( cd "$RENDER" && git init -q 2>/dev/null; git add -A 2>/dev/null; \
      git -c user.email=smoke@local -c user.name=smoke commit -qm init 2>/dev/null; true )
    : >"$RENDER/.claude/audit.log" 2>/dev/null || true
    ( cd "$RENDER" && claude -p "Run exactly this shell command and nothing else: echo harness-smoke-probe" \
        --allowedTools Bash >"$TMP/live.log" 2>&1 ) || true
    if grep -q "harness-smoke-probe" "$RENDER/.claude/audit.log" 2>/dev/null; then
      echo "hook-dispatch: OK (PostToolUse/Bash logged the probe command)"
      HOOK_FIRE="pass"
    else
      echo "FAIL: the Bash audit hook did not log the probe; hooks may not be dispatching."
      echo "      live session log tail:"; tail -8 "$TMP/live.log" 2>/dev/null || true
      HOOK_FIRE="fail"; FAIL=1
    fi
  fi
fi

STAMP="$(git rev-parse --short HEAD 2>/dev/null || echo nohead)"
VERDICT="PASS"; [ "$FAIL" -ne 0 ] && VERDICT="FAIL"
echo "commit=$STAMP verdict=$VERDICT seed_tokens=$SEED_TOKENS plugin_tokens=$PLUGIN_TOKENS hook_fire=$HOOK_FIRE live=$LIVE" >> bin/harness-smoke.log

echo
echo "harness-smoke: $VERDICT"
[ "$FAIL" -ne 0 ] && exit 1
exit 0
