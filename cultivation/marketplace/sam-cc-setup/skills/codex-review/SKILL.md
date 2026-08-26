---
name: codex-review
description: "Second-opinion review of the current diff via the Codex CLI, read-only. Use when you want an independent adversarial review of a diff from a different model before merging. Manual only. NOT for replacing your project's own diff-review or validation gate; Codex never edits - findings are advisory and Claude applies any fixes."
argument-hint: "[optional diff scope, e.g. main...HEAD or HEAD~3; defaults to main...HEAD]"
---

# Codex Second-Opinion Review

Run the current diff past the **Codex CLI** as an independent reviewer (a different model,
fresh context) and triage its findings. Codex runs in a pinned **read-only** sandbox and
**never edits the checkout** - it only reports. Claude saves a transcript under
`.claude/codex-reviews/` (gitignore it) and applies any fixes.

**Trigger:** user types `/codex-review [scope]`. It deliberately does NOT carry
`disable-model-invocation: true`: that flag currently also blocks the `/codex-review` slash
command itself (anthropics/claude-code#26251, dup #38969), so the "Manual only" scoping in the
description is what keeps it from auto-firing.

## Single-writer rule (mandatory)

Codex must never write to a checkout Claude is using (one checkout = one writer; two
writers race on the same working tree). The read-only sandbox enforces this - do
NOT relax `--sandbox read-only` to `workspace-write` (the repo config default is
workspace-write, which would violate this rule). Findings come back as text; Claude edits.

## Workflow

### Step 1 - Scope the diff

```bash
SCOPE="${ARGUMENTS:-main...HEAD}"      # $ARGUMENTS if provided, else the branch diff
BRANCH=$(git rev-parse --abbrev-ref HEAD)
set -o pipefail

# Custom scopes must be one Git revision or revision range, never options/pathspecs.
case "$SCOPE" in
  ""|-*)
    echo "Invalid scope: use a revision/range like main...HEAD or HEAD~3, not a git option."
    exit 2
    ;;
  *[!A-Za-z0-9._/@{}~^+-]*)
    echo "Invalid scope: spaces, pathspecs, and shell metacharacters are not allowed."
    exit 2
    ;;
esac

LEFT="$SCOPE"
RIGHT=""
if [[ "$SCOPE" == *...* ]]; then
  LEFT="${SCOPE%%...*}"
  RIGHT="${SCOPE#*...}"
elif [[ "$SCOPE" == *..* ]]; then
  LEFT="${SCOPE%%..*}"
  RIGHT="${SCOPE#*..}"
fi

if [ -z "$LEFT" ] || { [[ "$SCOPE" == *..* ]] && [ -z "$RIGHT" ]; }; then
  echo "Invalid scope: revision ranges must include both endpoints."
  exit 2
fi

for REV in "$LEFT" "$RIGHT"; do
  [ -z "$REV" ] && continue
  git rev-parse --verify --quiet "$REV^{commit}" >/dev/null || {
    echo "Invalid scope: '$REV' is not a commit-like revision."
    exit 2
  }
done

git --no-pager diff --quiet "$SCOPE"
DIFF_STATUS=$?
if [ "$DIFF_STATUS" -eq 0 ]; then
  echo "nothing to review for '$SCOPE'"
  exit 0
elif [ "$DIFF_STATUS" -ne 1 ]; then
  echo "git diff failed for scope '$SCOPE'"
  exit "$DIFF_STATUS"
fi

MAX_DIFF_BYTES=200000
DIFF_BYTES=$(git --no-pager diff "$SCOPE" | wc -c | tr -d '[:space:]')
if [ "$DIFF_BYTES" -gt "$MAX_DIFF_BYTES" ]; then
  echo "Diff is ${DIFF_BYTES} bytes; narrow the scope before /codex-review."
  exit 2
fi

git --no-pager diff "$SCOPE" --stat    # confirm there is something to review
```

If the diff is empty, stop and report "nothing to review for `<scope>`".

### Step 2 - Run Codex (read-only, diff piped via stdin)

Pipe the diff on **stdin** (Codex appends it as a `<stdin>` block) so a large diff never
hits the shell argument-length limit. The Codex sandbox stays read-only, and the effort floor
(`model_reasoning_effort=high`) is pinned explicitly because this is a reasoning-heavy review
(don't rely on the ambient default). `-o` writes **only the final agent message** to `$OUT`;
nothing is echoed to the terminal - streamed reasoning goes to stderr and is dropped - so read
the verdict from `$OUT` in Step 3.

**Model policy:** default to the frontier Codex model (`gpt-5.6-sol`) at `high`, or step up to
a deeper-reasoning tier at `xhigh` when you want the stronger pass. The deeper pass is
materially slower - run it in the background rather than blocking on a foreground timeout.
Valid `model_reasoning_effort` values: `none, low, medium, high, xhigh, max`. Confirm the
current Codex model ids against your provider before pinning one.

```bash
mkdir -p .claude/codex-reviews
SAFE_BRANCH="${BRANCH//\//-}"
OUT=".claude/codex-reviews/$(date +%F)-${SAFE_BRANCH}.md"

git --no-pager diff "$SCOPE" | codex exec --sandbox read-only \
  -c model="gpt-5.6-sol" -c model_reasoning_effort=high -o "$OUT" \
  "You are a second-opinion code reviewer. Review the diff in the <stdin> block against \
the current repository (you may read files read-only for context). Respond in <=60 lines: \
first line a single verdict - SHIP, FIX FIRST, or REWORK - then findings grouped under \
Critical / High / Medium / Low, each with file:line and a one-line fix. Omit empty groups. \
Be terse; no preamble."
```

### Step 3 - Triage back into the session

- Read the verdict block from `$OUT` (Codex prints nothing inline with `-o`).
- Treat findings as **advisory**: Claude decides which to act on, then applies fixes in the
  Claude checkout. Codex does not edit.
- For a FIX FIRST / REWORK verdict, fold the confirmed Critical/High findings into the work
  before shipping; note Medium/Low as follow-ups.

## What NOT to do

- Don't run Codex with a writable sandbox (`workspace-write` / `danger-full-access`) - read-only only.
- Don't let Codex apply fixes - it reviews, Claude edits (single-writer).
- Not a pipeline gate: `/codex-review` complements your project's own review and validation gates, it does not replace them.
