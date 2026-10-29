---
name: codex-review
disable-model-invocation: true
description: "Second-opinion review of the current diff via the Codex CLI, read-only. Use when you want an independent fresh-context review before merging. Manual only. NOT for replacing your project's own diff-review or validation gate; Codex never edits - findings are advisory and Claude applies any fixes."
argument-hint: "[optional diff scope, e.g. main...HEAD or HEAD~3; defaults to the default branch ...HEAD]"
---

# Codex Second-Opinion Review

Run the current diff past the **Codex CLI** as an independent fresh-context reviewer and
triage its findings. Codex runs in a **read-only** sandbox and
**never edits the checkout** - it only reports. Claude saves a transcript under
`.claude/codex-reviews/` (gitignore it) and applies any fixes.

**Trigger:** user types `/codex-review [scope]`. Manual-only (`disable-model-invocation:
true`).

## Single-writer rule (mandatory)

Codex must never write to a checkout Claude is using (one checkout = one writer; two
writers race on the same working tree). The read-only sandbox enforces this - do
NOT relax `--sandbox read-only` to `workspace-write` (the repo config default is
workspace-write, which would violate this rule). Findings come back as text; Claude edits.

## Workflow

### Step 1 - Scope the diff

```bash
# Default scope is <default-branch>...HEAD; resolve the default branch instead of
# assuming `main` (repos on master/trunk would otherwise fail here).
DEFAULT_BRANCH=$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
SCOPE="${ARGUMENTS:-${DEFAULT_BRANCH:-main}...HEAD}"   # $ARGUMENTS if provided, else the branch diff
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

# Codex cuts long command output short, so Step 2 has it read this diff one path at a time.
# The cap bounds the whole diff, not each read.
MAX_DIFF_BYTES=200000
DIFF_BYTES=$(git --no-pager diff "$SCOPE" | wc -c | tr -d '[:space:]')
if [ "$DIFF_BYTES" -gt "$MAX_DIFF_BYTES" ]; then
  echo "Diff is ${DIFF_BYTES} bytes; narrow the scope before /codex-review."
  exit 2
fi

git --no-pager diff "$SCOPE" --stat    # confirm there is something to review
git --no-pager diff "$SCOPE" | git hash-object --stdin
```

If the diff is empty, stop and report "nothing to review for `<scope>`".

### Step 2 - Run Codex (read-only, one bare command)

First write one paragraph of intent: what the change is meant to do, from the user's request and
the commit messages in scope (`git log --format='%s%n%b' "$LEFT..${RIGHT:-HEAD}"`). State only
the intended behavior, never why it was built this way: the reviewer stays blind to the author's
reasoning, as in `plan-review`. If the intent is unclear, ask the user before running Codex.

Codex reads the diff itself; nothing is piped in. It lists the changed paths, then runs one
`git diff` per path, because Codex cuts long command output short and a whole-diff read can
come back cut. Keep the sandbox read-only. Choose the model and effort for this diff: `high` on
the configured model by default, `xhigh` or a stronger model for a large or risky diff, `medium`
for a few trivial lines; never `max` or `ultra`. Drop `-m` to keep the configured model, and
check a model ID against the provider's model list before passing it. `-o` saves the durable
final report. Pick its path:

```bash
mkdir -p .claude/codex-reviews
echo ".claude/codex-reviews/$(date +%F)-$(git rev-parse --abbrev-ref HEAD | tr / -).md"
```

Then run Codex as its own Bash call that starts with `codex exec`, with `<model>`, `<effort>`,
`<out>`, `<scope>`, and `<intent>` written in literally. A sandbox exclusion such as `codex exec *` matches only that bare
command. Behind a pipe, an assignment, `&&`, or any redirect, even `< /dev/null`, Claude Code runs
Codex inside its sandbox, where Codex can fail to reach its API or to start its own sandbox. Leave
no `<` anywhere in the command, prompt included: then Claude Code gives the call an empty stdin;
with one, it leaves stdin open and Codex waits on it forever.
Write `<intent>` as plain prose without quotes, backticks, `$`, `\`, or `<`.

```bash
codex exec --sandbox read-only -m "<model>" -c "model_reasoning_effort=<effort>" -o "<out>" \
  "You are a second-opinion code reviewer. The change is meant to do this: <intent> \
Review whether the diff achieves that intent well; do not question the intent itself. \
List the changed paths with git --no-pager diff --numstat <scope>, then read each path's \
diff with its own git --no-pager diff <scope> -- followed by that path, since one long output \
gets cut short. Read files in the current repository read-only for context. \
Respond in at most 60 lines: first line a single \
verdict - SHIP, FIX FIRST, or REWORK - then findings grouped under Critical / High / \
Medium / Low, each with file:line and a one-line fix. Omit empty groups. \
Be terse; no preamble."
```

### Step 3 - Triage back into the session

- Read the verdict block from `<out>` (Codex prints nothing inline with `-o`).
- Judge each finding yourself; Codex's verdict and severity are input, not the decision. Check
  it against the code first: a hypothetical input is a finding only if a real caller can pass it.
- Put every finding in exactly one bucket, with a one-line reason:
  - **Act on:** a real correctness, security, or maintainability problem for the stated intent;
    it would block a real PR. Fix it in this session.
  - **Consider:** legitimate, but not clearly worth its cost now. Show it to the user with the
    tradeoff.
  - **Noted:** valid but not actionable now (premature, low impact, context-dependent).
  - **Dismissed:** wrong, a nit, a preference with no concrete problem, or missing context
    Codex could not see. Look harder at a security or correctness finding before dismissing it.
- If every finding is a nit or a preference, say the change is probably fine.
- Report the four buckets in that order.
- For every Act on or Consider finding you do not fix in this session, file an issue in the
  project's tracker once the user agrees, by the tracker rules its `AGENTS.md` names (in Loam,
  `gh issue create`); with no tracker, list them in the reply.
  Close the issue from the commit that later fixes it.
- Record the diff fingerprint in `<out>`. Reuse this report while the fingerprint and
  criteria are unchanged. Review again only after material changes or for a named risk.

## What NOT to do

- Don't run Codex with a writable sandbox (`workspace-write` / `danger-full-access`) - read-only only.
- Don't let Codex apply fixes - it reviews, Claude edits (single-writer).
- Not a pipeline gate: `/codex-review` complements your project's own review and validation gates, it does not replace them.
