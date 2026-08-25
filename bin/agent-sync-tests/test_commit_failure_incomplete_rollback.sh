#!/usr/bin/env bash
# test_commit_failure_incomplete_rollback.sh
# Codex round-2 High (scan.sh commit-failure path): CX-5's rollback ignored
# reset/checkout/unlink failures and always claimed "rolled back this run's staged
# changes". A failed restore must instead be VERIFIED (scoped porcelain status)
# and reported as INCOMPLETE with the residue and manual recovery steps.
# Injection: the rejecting pre-commit hook also flips the change's parent
# directory read-only, so the rollback's `checkout HEAD` cannot restore the file.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYNC_SH="$SCRIPT_DIR/../agent-sync-scan.sh"
TMP="$(mktemp -d)"
trap 'chmod -R u+rwx "$TMP" 2>/dev/null; rm -rf "$TMP"' EXIT

if [ "$(id -u)" -eq 0 ]; then
  echo "FAIL: this test must run as a non-root user (root bypasses the chmod-based injection)"
  exit 1
fi

HUB_SETUP="$TMP/hub/cultivation/marketplace/sam-cc-setup"
CHG="skills/x/exist.md"

mkdir -p "$HUB_SETUP/skills/x"
echo "keep" > "$HUB_SETUP/keep.md"
echo "hub version" > "$HUB_SETUP/$CHG"
(cd "$TMP/hub" && git init -q && \
  git config user.email t@t && git config user.name t && \
  git add -A && git commit -q -m init)
echo "session=3" > "$TMP/hub/.sync-state"
# The hook rejects the commit AND makes the parent dir read-only, so the
# subsequent checkout-HEAD restore of the change must fail.
HOOK="$TMP/hub/.git/hooks/pre-commit"
cat > "$HOOK" << EOF
#!/bin/sh
chmod 0555 "$HUB_SETUP/skills/x"
echo "pre-commit hook: rejecting" >&2
exit 1
EOF
chmod +x "$HOOK"

mkdir -p "$TMP/proj/.claude/skills/x" "$TMP/proj/.claude/reference"
echo "project version" > "$TMP/proj/.claude/$CHG"
printf 'skills/x\t-\ttravels\n' > "$TMP/proj/.claude/reference/portability-manifest.tsv"
(cd "$TMP/proj" && git init -q && \
  git -c user.email=t@t -c user.name=t add -A && \
  git -c user.email=t@t -c user.name=t commit -q -m init)

cd "$TMP/proj"
set +e
out=$(printf 'y\ny\n' | SAM_CC_HUB_REPO="$TMP/hub" bash "$SYNC_SH" 2>&1)
rc=$?
set -e
chmod -R u+rwx "$TMP/hub"

# 1: non-zero exit.
if [ "$rc" -eq 0 ]; then echo "FAIL: scan exited 0 despite commit failure + failed rollback"; echo "$out"; exit 1; fi
# 2 (RED flip): the INCOMPLETE branch fires - no false "rolled back" success claim.
if ! echo "$out" | grep -q "rollback is INCOMPLETE"; then
  echo "FAIL: incomplete rollback was not reported as INCOMPLETE"; echo "$out"; exit 1
fi
if echo "$out" | grep -q "rolled back this run's staged changes. Nothing was committed"; then
  echo "FAIL: the success claim was printed despite residue"; echo "$out"; exit 1
fi
# 3: the residue listing names the un-restored path.
if ! echo "$out" | grep -q "exist.md"; then
  echo "FAIL: residue listing does not name the un-restored path"; echo "$out"; exit 1
fi
# 4: manual recovery guidance present.
if ! echo "$out" | grep -q "Finish by hand"; then
  echo "FAIL: no manual recovery guidance"; echo "$out"; exit 1
fi
# 5: no synced: record was promoted.
if grep -Eq "^synced:.*[[:space:]]$CHG:" "$TMP/hub/.sync-state" 2>/dev/null; then
  echo "FAIL: a synced: record was promoted"; exit 1
fi

echo "PASS: test_commit_failure_incomplete_rollback"
