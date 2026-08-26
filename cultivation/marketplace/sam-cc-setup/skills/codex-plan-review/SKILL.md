---
name: codex-plan-review
description: "Second-opinion adversarial review of a PLAN file via the Codex CLI, read-only. Use when a plan needs an independent cross-model review before execution. Manual only. NOT for replacing your project's own plan-review gate; Codex never edits - findings are advisory and Claude folds them into the plan."
argument-hint: "<path-to-plan.md>"
---

# Codex Plan Review (cross-model)

Run a **plan file** past the **Codex CLI** as an independent adversarial reviewer (a different
model, fresh context) and fold its findings into the plan. Codex runs in a pinned **read-only**
sandbox and **never edits the checkout** - it only reports. Claude saves a transcript
under `.claude/codex-reviews/` (gitignore it) and applies any accepted changes to the plan itself.

This is the plan-file sibling of `/codex-review` (which reviews diffs). The cross-model angle is
the point: a same-model reviewer cannot remove identity-based self-preference, so a *different*
model reviewing the plan is the irreplaceable defense before execution.

**Trigger:** user types `/codex-plan-review <path-to-plan.md>`. Like `/codex-review`, it
deliberately does NOT carry `disable-model-invocation: true`: that flag currently also blocks
the slash command itself (anthropics/claude-code#26251, dup #38969), so the "Manual only" scoping
in the description is what keeps it from auto-firing.

## Single-writer rule (mandatory)

Codex must never write to a checkout Claude is using (one checkout = one writer; two
writers race on the same working tree). The read-only sandbox enforces this - do
NOT relax `--sandbox read-only` to `workspace-write` (the repo config default is
workspace-write, which would violate this rule). Findings come back as text; **Claude** folds the
accepted ones into the plan file. Never let Codex update the plan.

## Workflow

### Step 1 - Resolve and validate the plan path

```bash
PLAN="$ARGUMENTS"      # the plan file to review; no default - a path is required

# The path must be a readable .md file with no options/metacharacters (mirror
# /codex-review's validation stance, adapted from a git revision to a file path).
case "$PLAN" in
  ""|-*)
    echo "Usage: /codex-plan-review <path-to-plan.md> (a readable .md file in the repo)."
    exit 2
    ;;
  *..*)
    echo "Invalid path: parent-directory traversal is not allowed."
    exit 2
    ;;
  *[!A-Za-z0-9._/-]*)
    echo "Invalid path: spaces, options, and shell metacharacters are not allowed."
    exit 2
    ;;
  *.md) ;;
  *)
    echo "Invalid: the plan must be a .md file."
    exit 2
    ;;
esac

if [ ! -f "$PLAN" ] || [ ! -r "$PLAN" ]; then
  echo "No readable file at '$PLAN'."
  exit 2
fi

# Reject an oversized plan: Codex auto-injects AGENTS.md (32 KiB cap) and the plan
# rides on stdin, so keep the review prompt lean.
MAX_PLAN_BYTES=150000
PLAN_BYTES=$(wc -c < "$PLAN" | tr -d '[:space:]')
if [ "$PLAN_BYTES" -gt "$MAX_PLAN_BYTES" ]; then
  echo "Plan is ${PLAN_BYTES} bytes (>150 KB); trim or split it before /codex-plan-review."
  exit 2
fi
```

### Step 2 - Run Codex (read-only, plan piped via stdin)

Pipe the plan on **stdin** (Codex appends it as a `<stdin>` block) so a large plan never hits the
shell argument-length limit. The Codex sandbox stays read-only; the effort floor
(`model_reasoning_effort=high`) applies because this is a reasoning-heavy review. `-o` writes only
the final agent message to `$OUT` (streamed reasoning on stderr is dropped). Codex has no built-in
timeout - run this **via the Bash tool with an extended timeout** (up to the 600 s tool max); don't
prefix a shell `timeout`, which isn't present on macOS (`codex-review` runs the same way).

**Model policy:** default to the frontier Codex model (`gpt-5.6-sol`) at `high`, or step up to
a deeper-reasoning tier at `xhigh` when you want the stronger pass. The deeper pass is
materially slower - run it in the background rather than blocking on a foreground timeout.
Valid `model_reasoning_effort` values: `none, low, medium, high, xhigh, max`. Confirm the
current Codex model ids against your provider before pinning one.

```bash
PLAN="$ARGUMENTS"   # set explicitly - mirrors codex-review's SCOPE="${ARGUMENTS:-...}" pattern
mkdir -p .claude/codex-reviews
OUT=".claude/codex-reviews/$(date +%F)-plan-$(basename "$PLAN" .md).md"
cat "$PLAN" | codex exec --sandbox read-only \
  -c model="gpt-5.6-sol" -c model_reasoning_effort=high -o "$OUT" \
  "You are an adversarial plan reviewer. Review the plan in the <stdin> block against the \
current repository (read files read-only for context). Check: (1) every task names real files \
and a verification command; (2) unstated assumptions and missing edge cases; (3) ordering/ \
dependency hazards; (4) ELEGANCE GATE, mandatory and frame-breaking: step back from the plan, \
ask if a different architecture, built-in feature, existing library, or existing repo machinery \
makes most of the plan unnecessary ('why not just do X instead?'); reuse-before-new is a repo \
law; a counter-proposal must name what it replaces and its tradeoffs; (5) conformance to \
.claude/rules/. \
First line: verdict APPROVE / APPROVE_WITH_CHANGES / REJECT. Then findings grouped \
Critical/High/Medium/Low, each with plan-section ref and a one-line concrete fix. Report gaps \
that affect correctness or the stated requirements, not style preferences. <=60 lines."
```

### Step 3 - Fold findings back into the plan (single-writer)

- Read the verdict block (saved at `$OUT`).
- Treat findings as **advisory**: Claude decides which to accept, then edits the **plan file
  itself** - Codex does not edit anything.
- Fold accepted Critical/High findings into the plan; note Medium/Low as follow-ups.
- **Dismiss a finding only with a reproducing check**, never an argument: record the check
  that shows the finding is a false positive.

## What NOT to do

- Don't run Codex with a writable sandbox (`workspace-write` / `danger-full-access`) - read-only only.
- Don't let Codex edit the plan - it reviews, Claude folds (single-writer).
- Not a pipeline gate: `/codex-plan-review` complements your project's own plan-review gates, it does not replace them.
