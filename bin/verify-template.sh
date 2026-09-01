#!/usr/bin/env bash
# verify-template.sh - public release gate for the Loam template.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

echo "== stage 1: contract unit tests =="
if python3 -m unittest discover -s bin/tests \
    -p 'test_*.py' -v; then
  echo "contract unit tests: OK"
else
  echo "FAIL: rendered harness contract unit tests failed."
  FAIL=1
fi

echo "== stage 2: Copier scratch render from HEAD =="
COPIER=()
if command -v copier >/dev/null 2>&1; then
  COPIER=(copier)
elif command -v uvx >/dev/null 2>&1; then
  COPIER=(uvx copier)
else
  echo "FAIL: neither copier nor uvx found; cannot render."
  FAIL=1
fi

if [ "${#COPIER[@]}" -ne 0 ]; then
  if "${COPIER[@]}" copy --trust --defaults --vcs-ref=HEAD \
      --data project_name=verifyproj --data github_repo= \
      "$ROOT" "$TMP/render" >"$TMP/render.log" 2>&1; then
    echo "Copier scratch render: OK"
  else
    echo "FAIL: Copier scratch render failed. Log tail:"
    tail -20 "$TMP/render.log" || true
    FAIL=1
  fi
fi

echo "== stage 3: rendered harness contract =="
if [ -d "$TMP/render" ]; then
  if python3 bin/rendered_harness_contract.py \
      --source-root "$ROOT" --rendered-root "$TMP/render"; then
    echo "rendered harness contract: OK"
  else
    echo "FAIL: rendered harness contract failed."
    FAIL=1
  fi
else
  echo "FAIL: rendered harness contract could not run without a scratch render."
  FAIL=1
fi

echo "== stage 4: Claude native validation =="
if command -v claude >/dev/null 2>&1; then
  if claude plugin validate seed/.claude >"$TMP/claude.log" 2>&1; then
    echo "validate seed/.claude: OK"
  else
    echo "FAIL: claude plugin validate seed/.claude:"
    tail -10 "$TMP/claude.log" || true
    FAIL=1
  fi

  for TARGET in seed/.agents/skills cultivation/marketplace; do
    if claude plugin validate --strict "$TARGET" >"$TMP/claude.log" 2>&1; then
      echo "validate --strict $TARGET: OK"
    else
      echo "FAIL: claude plugin validate --strict $TARGET:"
      tail -10 "$TMP/claude.log" || true
      FAIL=1
    fi
  done

  if python3 bin/rendered_harness_contract.py --source-root "$ROOT" \
      --list-local-plugin-roots >"$TMP/local-plugin-roots"; then
    while IFS= read -r PLUGIN_ROOT; do
      [ -n "$PLUGIN_ROOT" ] || continue
      if claude plugin validate --strict "$PLUGIN_ROOT" \
          >"$TMP/claude.log" 2>&1; then
        echo "validate --strict $PLUGIN_ROOT: OK"
      else
        echo "FAIL: claude plugin validate --strict $PLUGIN_ROOT:"
        tail -10 "$TMP/claude.log" || true
        FAIL=1
      fi

      for COMPONENT in agents skills commands; do
        COMPONENT_ROOT="$PLUGIN_ROOT/$COMPONENT"
        [ -d "$COMPONENT_ROOT" ] || continue
        if claude plugin validate --strict "$COMPONENT_ROOT" \
            >"$TMP/claude.log" 2>&1; then
          echo "validate --strict $COMPONENT_ROOT: OK"
        else
          echo "FAIL: claude plugin validate --strict $COMPONENT_ROOT:"
          tail -10 "$TMP/claude.log" || true
          FAIL=1
        fi
      done

      HOOKS_JSON="$PLUGIN_ROOT/hooks/hooks.json"
      if [ -e "$HOOKS_JSON" ]; then
        if python3 -m json.tool "$HOOKS_JSON" >/dev/null 2>&1; then
          echo "parse $HOOKS_JSON: OK"
        else
          echo "FAIL: $HOOKS_JSON is not valid JSON."
          FAIL=1
        fi
      fi
    done <"$TMP/local-plugin-roots"
  else
    echo "FAIL: could not discover local marketplace plugins."
    FAIL=1
  fi
elif [ "${LOAM_ALLOW_MISSING_AGENT_CLIS:-0}" = "1" ]; then
  echo "SKIPPED: claude CLI not found; native Claude validation did not run."
else
  echo "FAIL: claude CLI not found; install it or set LOAM_ALLOW_MISSING_AGENT_CLIS=1."
  FAIL=1
fi

run_codex_probe() {
  local expected="$1"
  local label="$2"
  shift 2
  if codex execpolicy check --rules seed/.codex/rules/default.rules -- "$@" \
      >"$TMP/codex.json" 2>"$TMP/codex.log"; then
    local decision
    if decision="$(python3 -c '
import json
import sys

value = json.load(sys.stdin)
decision = value.get("decision") if isinstance(value, dict) else None
if not isinstance(decision, str):
    raise SystemExit(1)
print(decision)
' <"$TMP/codex.json")"; then
      if [ "$decision" = "$expected" ]; then
        echo "Codex probe $label: OK ($decision)"
      else
        echo "FAIL: Codex probe $label returned $decision; expected $expected."
        FAIL=1
      fi
    else
      echo "FAIL: Codex probe $label returned invalid decision JSON."
      FAIL=1
    fi
  else
    echo "FAIL: Codex probe $label could not run:"
    tail -10 "$TMP/codex.log" || true
    FAIL=1
  fi
}

echo "== stage 5: Codex native policy probes =="
if command -v codex >/dev/null 2>&1; then
  run_codex_probe prompt normal-push git push origin main
  run_codex_probe forbidden force-push git push --force origin main
  run_codex_probe forbidden force-with-lease git push --force-with-lease origin main
elif [ "${LOAM_ALLOW_MISSING_AGENT_CLIS:-0}" = "1" ]; then
  echo "SKIPPED: codex CLI not found; native Codex policy probes did not run."
else
  echo "FAIL: codex CLI not found; install it or set LOAM_ALLOW_MISSING_AGENT_CLIS=1."
  FAIL=1
fi

echo "== stage 6: skill frontmatter names =="
if find seed cultivation/marketplace -name SKILL.md \
    -not -path '*/node_modules/*' >"$TMP/skill-paths" 2>"$TMP/find.log"; then
  while IFS= read -r SKILL; do
    if awk '/^---$/{n++} n==1 && /^name:/{found=1} END{exit !found}' "$SKILL"; then
      continue
    fi
    echo "FAIL: $SKILL frontmatter has no name: field."
    FAIL=1
  done <"$TMP/skill-paths"
else
  echo "FAIL: could not discover SKILL.md files."
  tail -10 "$TMP/find.log" || true
  FAIL=1
fi

echo
if [ "$FAIL" -ne 0 ]; then
  echo "verify-template: FAILED"
  exit 1
fi
echo "verify-template: PASSED"
