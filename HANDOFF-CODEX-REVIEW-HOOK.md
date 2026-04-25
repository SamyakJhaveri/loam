# HANDOFF: Pre-Commit Codex Review Reminder Hook

**Date:** 2026-04-24
**Author:** Claude Code session (exploration + adversarial plan review + design refinement)
**Status:** Ready to implement — all design decisions finalized, all edge cases addressed
**Audience:** Written for undergraduate software engineering clarity. Follow every step in order. Do not skip ahead.

---

## What Is This? (Plain English)

This project (ParBench) already has a strict commit workflow:

```
do work → run /session-critique → run /validate → git commit
```

We want to add a **Codex review step** between `/session-critique` and `/validate`. Codex is OpenAI's code agent (think of it as GPT-5.4 reviewing your code). It gives a second opinion from a completely different AI, catching things Claude might miss.

The new workflow:

```
do work → /session-critique → Codex review → /validate → git commit
```

### What You're Building

A **pre-commit reminder hook** — a small bash script that runs automatically when Claude tries to `git commit`. It checks whether a Codex review was done. If not, it shows a friendly reminder. It **never blocks** the commit (that's the validation gate's job) — it just nudges.

### How It Knows If You Did the Review

We use a **sentinel file** — a tiny marker file called `.codex_review_done` in the project root. Think of it like a "receipt":

- When you run a Codex review, a `.codex_review_done` file gets created (like getting a receipt after paying)
- When the hook runs, it checks: "Does this receipt exist? Is it less than 30 minutes old?"
- If yes → stays silent (you already did the review)
- If no → shows a reminder message

This is the exact same pattern the project already uses for validation (`.validation_passed`). We're copying a proven design, not inventing something new.

---

## What's Already Done (Investigation & Design)

| Item | Status | Details |
|------|--------|---------|
| Codex CLI verification | DONE | v0.122.0 installed at `/home/samyak/.npm-global/bin/codex`, OpenAI API key set |
| Codex plugin verification | DONE | `codex@openai-codex` v1.0.4 installed as user-scoped Claude Code plugin |
| Hook architecture exploration | DONE | All 12 existing hooks examined, JSON protocol documented, ordering analyzed |
| Adversarial plan review | DONE | `plan-reviewer` agent found 8 issues (2 CRITICAL, 5 IMPORTANT, 3 MINOR) — all addressed |
| Design decision: sentinel vs state-file | FINALIZED | Sentinel file wins — simpler, proven pattern, no coupling to Codex internals |
| Design decision: hook ordering | FINALIZED | Place AFTER `pre-commit-gate.sh` so reminder only fires when validation passed |
| Design decision: never block | FINALIZED | Advisory only (exit 0 always). Reminder, not a gate. |

### What Worked

- **Sentinel file pattern**: The project already uses `.validation_passed` + `sentinel-cleanup.sh` for the same concept. Copying this proven pattern eliminates design risk.
- **Adversarial review**: The `plan-reviewer` agent caught that the original plan tried to parse Codex's internal `state.json` — a file whose schema is undocumented and whose `jobs` array was empty (no review had ever been recorded). That approach would have produced code against a phantom specification.
- **Hook ordering analysis**: Placing the hook AFTER `pre-commit-gate.sh` means it only fires when the commit would otherwise succeed. No confusing "run Codex review" followed by "BLOCKED: run /validate first."

### What Didn't Work (Don't Repeat These)

- **Parsing Codex state files**: The original design tried to detect prior reviews by reading `~/.claude/plugins/data/codex-openai-codex/state/parbench_sam-*/state.json`. This was rejected because: (1) the `jobs` array was empty — no schema to code against; (2) the path contains a project-specific hash that could change; (3) it couples to Codex plugin internals that could change at any version bump.
- **Enabling the stop-review-gate**: The Codex plugin has a built-in `stopReviewGate` that auto-reviews before every Claude stop. The user explicitly rejected this — too aggressive. They want a reminder at commit time, not a gate at every turn.
- **Placing the hook BEFORE `pre-commit-gate.sh`**: This would show "run Codex review" even when `/validate` hasn't been run yet — confusing because the user can't commit anyway.
- **Using `set -euo pipefail`**: All existing hooks use this, but for an advisory hook that must NEVER block (exit 0 always), any internal failure under `set -e` would cause an accidental non-zero exit. The fix: use `trap 'exit 0' ERR` instead.

---

## Skills to Load at Session Start

Before doing ANY implementation work, invoke these skills. They guide HOW you work:

```
Skill("test-driven-development")                      — Gated TDD: 3 mandatory human checkpoints (INTENT → RED → GREEN)
Skill("andrej-karpathy-skills:karpathy-guidelines")    — Think before coding, surgical changes, verify before claiming done
Skill("update-config")                                 — Guidance for editing settings.json safely
```

### TDD Gates for This Task

The `/test-driven-development` skill requires 3 mandatory checkpoints. Here's how they apply:

| Gate | What to Present to User | When |
|------|------------------------|------|
| **INTENT** | "I will build: advisory pre-commit hook that checks `.codex_review_done` sentinel and outputs a reminder via `additionalContext` JSON. 5 files: 1 new, 4 edits." | Before writing any code |
| **RED** | Write test script with 3 test cases (see Step 1 verification below). Run it. All 3 should FAIL because the hook doesn't exist yet. Show the failures. | Before implementing the hook |
| **GREEN** | Implement the hook (Step 1). Run the same 3 tests. All should PASS. Show the passes. | After tests are written |

---

## Working Directory

**All commands assume:**
```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
```

Run these two lines FIRST, before any other command.

---

## Step-by-Step Implementation

### Step 1: Create `.claude/hooks/codex-review-reminder.sh`

**File to create:** `/home/samyak/Desktop/parbench_sam/.claude/hooks/codex-review-reminder.sh`

This is the main deliverable. It's a Bash script that Claude Code calls automatically before every Bash command. Here's exactly what it should do:

#### Input/Output Protocol

**Input:** Claude Code passes the command as an environment variable `$CLAUDE_TOOL_INPUT`. It also sends JSON on stdin: `{"tool_input": {"command": "git commit -m ..."}}`. We use `$CLAUDE_TOOL_INPUT` (simpler — same pattern as `bash-audit-log.sh` at `.claude/hooks/bash-audit-log.sh:18`).

**Output (when reminder is needed):** Print this exact JSON to stdout:
```json
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Codex review reminder: You have not run a Codex review in this session. Before committing, consider running:\n\n  /codex:rescue review the uncommitted changes for correctness and regressions\n\nAfter the review completes, write the sentinel: touch .codex_review_done\nTo skip this reminder, touch .codex_review_done manually."}}
```

**Output (when no reminder needed):** Nothing. Just exit 0 silently.

**Exit code:** Always 0. Never 2 (never blocks).

#### Exact Algorithm (Pseudocode)

```
1. trap 'exit 0' ERR           ← safety net: any failure → exit 0 (never block)
2. cat > /dev/null              ← consume stdin to prevent SIGPIPE
3. if $CLAUDE_TOOL_INPUT does NOT contain "git commit" → exit 0 (not our concern)
4. PROJECT_ROOT = git rev-parse --show-toplevel
5. SENTINEL = $PROJECT_ROOT/.codex_review_done
6. if SENTINEL does not exist → print reminder JSON → exit 0
7. if SENTINEL age > 1800 seconds (30 min) → print reminder JSON → exit 0
8. exit 0 silently (sentinel is fresh → review was done recently)
```

#### Reference Files to Copy Patterns From

- **Command detection pattern**: `.claude/hooks/bash-audit-log.sh` line 18 — uses `$CLAUDE_TOOL_INPUT`
- **Stdin consumption**: `.claude/hooks/bash-audit-log.sh` line 17 — `cat > /dev/null`
- **Git commit matching**: `.claude/hooks/pre-commit-gate.sh` line 47 — `grep -qE '^\s*git\s+commit'`
- **PROJECT_ROOT discovery**: `.claude/hooks/pre-commit-gate.sh` line 22 — `git rev-parse --show-toplevel`
- **Sentinel age check (Linux)**: `.claude/hooks/pre-commit-gate.sh` line 69 — `stat -c %Y`
- **Sentinel age check (macOS)**: `.claude/hooks/pre-commit-gate.sh` line 72 — `stat -f %m`
- **OS detection**: `.claude/hooks/pre-commit-gate.sh` lines 26-30 — `uname` check
- **hookSpecificOutput JSON**: `.claude/settings.json` line 89 — the Glob/Grep graphify hook

#### Critical: `trap 'exit 0' ERR` Instead of `set -euo pipefail`

Every other hook in this project uses `set -euo pipefail`. You might be tempted to do the same. **Don't.** Here's why:

- `set -e` means "exit immediately if any command fails"
- This hook does filesystem operations (stat, grep) that CAN fail (missing file, weird permissions)
- If they fail under `set -e`, the script exits with a non-zero code
- A non-zero exit from a PreToolUse hook **blocks the tool** — exactly what we don't want
- `trap 'exit 0' ERR` is the safety net: if anything goes wrong, we exit 0 (allow the commit)

#### Verification (Run These 3 Tests)

```bash
# Test 1: Non-commit command → should exit 0 with no stdout output
OUTPUT=$(echo '{"tool_input":{"command":"ls -la"}}' | CLAUDE_TOOL_INPUT="ls -la" bash .claude/hooks/codex-review-reminder.sh 2>/dev/null)
EXIT=$?
[ "$EXIT" -eq 0 ] && [ -z "$OUTPUT" ] && echo "TEST 1 PASS: non-commit passthrough" || echo "TEST 1 FAIL: exit=$EXIT output='$OUTPUT'"

# Test 2: Commit command with NO sentinel → should print reminder JSON
rm -f .codex_review_done
OUTPUT=$(echo '{"tool_input":{"command":"git commit -m test"}}' | CLAUDE_TOOL_INPUT="git commit -m test" bash .claude/hooks/codex-review-reminder.sh 2>/dev/null)
EXIT=$?
[ "$EXIT" -eq 0 ] && echo "$OUTPUT" | grep -q "Codex review reminder" && echo "TEST 2 PASS: reminder shown" || echo "TEST 2 FAIL: exit=$EXIT output='$OUTPUT'"

# Test 3: Commit command WITH fresh sentinel → should exit 0 with no output
touch .codex_review_done
OUTPUT=$(echo '{"tool_input":{"command":"git commit -m test"}}' | CLAUDE_TOOL_INPUT="git commit -m test" bash .claude/hooks/codex-review-reminder.sh 2>/dev/null)
EXIT=$?
[ "$EXIT" -eq 0 ] && [ -z "$OUTPUT" ] && echo "TEST 3 PASS: sentinel suppresses reminder" || echo "TEST 3 FAIL: exit=$EXIT output='$OUTPUT'"
rm -f .codex_review_done
```

**GATE:** All 3 tests must PASS. Do NOT proceed to Step 2 until they do.

---

### Step 2: Register the Hook in `.claude/settings.json`

**File to edit:** `/home/samyak/Desktop/parbench_sam/.claude/settings.json`

**Back up first:**
```bash
cp .claude/settings.json .claude/settings.json.bak-codex-hook
```

**What to do:** Insert a new hook entry into the `hooks.PreToolUse[0].hooks` array (the Bash matcher group at lines 46-67).

**Where to insert:** At **array index 2** — AFTER `pre-commit-gate.sh` (index 1) and BEFORE `bash-audit-log.sh` (currently index 2).

**Why this exact position:**
- Index 0: `rm -rf` blocker (inline command)
- Index 1: `pre-commit-gate.sh` — **blocks** commit if validation hasn't run (exit 2)
- **Index 2: NEW — `codex-review-reminder.sh`** — reminds about Codex review (exit 0 always)
- Index 3: `bash-audit-log.sh` — logs the command
- Index 4: `protect-eval-results.sh` — protects result files

**The entry to insert:**
```json
{
  "type": "command",
  "command": ".claude/hooks/codex-review-reminder.sh",
  "timeout": 5
}
```

**Why timeout 5:** This hook does only simple file checks (stat, grep). 5 seconds is generous. Same timeout as `bash-audit-log.sh` (another advisory hook).

**Why AFTER `pre-commit-gate.sh`:** When `pre-commit-gate.sh` blocks (exit 2), Claude Code short-circuits — subsequent hooks don't fire. So the Codex reminder only appears when validation HAS passed. This prevents the confusing scenario of "run Codex review" followed immediately by "BLOCKED: run /validate first."

**Verification:**
```bash
# JSON is still valid
python3 -c "import json; json.load(open('.claude/settings.json'))" && echo "JSON valid" || echo "JSON BROKEN — restore from .claude/settings.json.bak-codex-hook"

# Correct number of hooks and correct position
python3 -c "
import json
d = json.load(open('.claude/settings.json'))
hooks = d['hooks']['PreToolUse'][0]['hooks']
print(f'{len(hooks)} Bash PreToolUse hooks registered')
assert len(hooks) == 5, f'Expected 5, got {len(hooks)}'
assert 'codex-review-reminder' in hooks[2]['command'], f'Wrong position: index 2 is {hooks[2][\"command\"]}'
print('OK: codex-review-reminder.sh at index 2 (after pre-commit-gate, before audit-log)')
"
```

**GATE:** JSON must be valid AND hook must be at index 2. If JSON is broken, restore:
```bash
cp .claude/settings.json.bak-codex-hook .claude/settings.json
```

---

### Step 3: Extend Sentinel Cleanup

**File to edit:** `/home/samyak/Desktop/parbench_sam/.claude/hooks/sentinel-cleanup.sh`

**What this file currently does (lines 20-30):** When any Edit/Write tool fires, it deletes `.validation_passed` so you must re-validate before the next commit.

**What to add:** The same cleanup for `.codex_review_done`. If you edit a file after doing a Codex review, the review sentinel is invalidated — you'll get the reminder again.

**Where to add:** After line 28 (after the existing `.validation_passed` cleanup block), before the final `exit 0`.

**Code to add:**
```bash
CODEX_SENTINEL="$PROJECT_ROOT/.codex_review_done"
if [ -f "$CODEX_SENTINEL" ]; then
    rm -f "$CODEX_SENTINEL"
    echo "sentinel-cleanup: .codex_review_done deleted (file edited after Codex review)" >&2
fi
```

**Verification:**
```bash
# Create both sentinels, then trigger cleanup
touch .validation_passed .codex_review_done
echo '{}' | bash .claude/hooks/sentinel-cleanup.sh
[ ! -f .validation_passed ] && echo "PASS: validation sentinel cleaned" || echo "FAIL"
[ ! -f .codex_review_done ] && echo "PASS: codex sentinel cleaned" || echo "FAIL"
```

**GATE:** Both sentinels must be cleaned.

---

### Step 4: Add `.codex_review_done` to `.gitignore`

**File to edit:** `/home/samyak/Desktop/parbench_sam/.gitignore`

**Find this existing line:**
```
.validation_passed
```

**Add directly after it:**
```
.codex_review_done
```

**Why:** The sentinel is a local runtime artifact (like `.validation_passed`). It should never be committed.

**Verification:**
```bash
grep -n 'codex_review_done' .gitignore && echo "OK" || echo "FAIL: not in gitignore"
```

---

### Step 5: Document in CLAUDE.md

**File to edit:** `/home/samyak/Desktop/parbench_sam/CLAUDE.md`

**Where:** In the "Quality" section, after the existing `/validate` bullet point.

**Line to add:**
```markdown
- After `/session-critique`, run `/codex:rescue review the uncommitted changes` for a GPT-5.4 second opinion. This writes `.codex_review_done` sentinel. The pre-commit hook reminds you if you skip this step.
```

**Verification:**
```bash
grep -c 'codex_review_done' CLAUDE.md  # Should print: 1
```

---

### Step 6: Make the Hook Executable

```bash
chmod +x .claude/hooks/codex-review-reminder.sh
ls -la .claude/hooks/codex-review-reminder.sh
# Expected: -rwxrwxr-x permissions
```

---

### Step 7: End-to-End Integration Test

This verifies the full workflow works as intended:

```bash
echo "=== E2E Test: Codex Review Reminder Hook ==="

# Clean state
rm -f .codex_review_done .validation_passed

# Test A: No sentinels → pre-commit-gate blocks first, codex reminder never fires
echo "--- Test A: commit with no sentinels ---"
echo '{"tool_input":{"command":"git commit -m test"}}' | CLAUDE_TOOL_INPUT="git commit -m test" bash .claude/hooks/pre-commit-gate.sh 2>&1; echo "pre-commit-gate exit: $?"
# Expected: BLOCKED by pre-commit-gate (exit 2)

# Test B: Validation sentinel exists, no codex sentinel → codex reminder fires
echo "--- Test B: validation passed, no codex review ---"
echo "waves_passed=3" > .validation_passed
echo '{"tool_input":{"command":"git commit -m test"}}' | CLAUDE_TOOL_INPUT="git commit -m test" bash .claude/hooks/codex-review-reminder.sh 2>/dev/null
echo "codex-reminder exit: $?"
# Expected: stdout contains "Codex review reminder", exit 0

# Test C: Both sentinels exist → no reminder
echo "--- Test C: both sentinels present ---"
touch .codex_review_done
OUTPUT=$(echo '{"tool_input":{"command":"git commit -m test"}}' | CLAUDE_TOOL_INPUT="git commit -m test" bash .claude/hooks/codex-review-reminder.sh 2>/dev/null)
echo "codex-reminder exit: $?"
[ -z "$OUTPUT" ] && echo "PASS: no reminder (both sentinels present)" || echo "FAIL: unexpected output"

# Test D: Edit a file → sentinel-cleanup removes both
echo "--- Test D: sentinel cleanup after edit ---"
echo '{}' | bash .claude/hooks/sentinel-cleanup.sh 2>/dev/null
[ ! -f .codex_review_done ] && echo "PASS: codex sentinel cleaned" || echo "FAIL: codex sentinel still exists"
[ ! -f .validation_passed ] && echo "PASS: validation sentinel cleaned" || echo "FAIL: validation sentinel still exists"

# Cleanup
rm -f .codex_review_done .validation_passed
echo "=== E2E tests complete ==="
```

**GATE:** All tests (A through D) must show expected behavior. Do NOT claim the task is done until this passes.

---

## Files Summary

| # | File (Absolute Path) | Action | Purpose |
|---|------|--------|---------|
| 1 | `/home/samyak/Desktop/parbench_sam/.claude/hooks/codex-review-reminder.sh` | **Create** | Advisory pre-commit hook — the main deliverable |
| 2 | `/home/samyak/Desktop/parbench_sam/.claude/settings.json` | **Edit** line ~56 | Register hook at array index 2 in Bash PreToolUse hooks |
| 3 | `/home/samyak/Desktop/parbench_sam/.claude/hooks/sentinel-cleanup.sh` | **Edit** line ~28 | Add `.codex_review_done` cleanup alongside `.validation_passed` |
| 4 | `/home/samyak/Desktop/parbench_sam/.gitignore` | **Edit** | Add `.codex_review_done` after `.validation_passed` |
| 5 | `/home/samyak/Desktop/parbench_sam/CLAUDE.md` | **Edit** Quality section | Document the Codex review workflow step |

## Source Files (Read-Only Reference — Do NOT Modify)

| File | Why You Need It |
|------|----------------|
| `.claude/hooks/pre-commit-gate.sh` | Copy the sentinel age-check pattern (lines 22, 26-30, 47, 68-89) |
| `.claude/hooks/bash-audit-log.sh` | Copy the `$CLAUDE_TOOL_INPUT` + `cat > /dev/null` pattern (lines 17-18) |
| `.claude/hooks/sentinel-cleanup.sh` | Understand the cleanup hook you'll extend (lines 20-30) |
| `.claude/settings.json` lines 42-93 | Understand hook registration structure and current array |
| `.gitignore` | Find the `.validation_passed` line to add after |

---

## What NOT To Do

| Don't | Why | Instead |
|-------|-----|---------|
| Parse Codex internal state files (`~/.claude/plugins/data/...`) | Schema is undocumented, `jobs` array is empty, path contains hash that could change | Use sentinel file `.codex_review_done` |
| Enable `stopReviewGate` in Codex config | User explicitly rejected — too aggressive | Keep advisory hook, not a gate |
| Use `set -euo pipefail` in the hook | Internal failures would cause non-zero exit → accidental blocking | Use `trap 'exit 0' ERR` |
| Place hook BEFORE `pre-commit-gate.sh` | Would show Codex reminder even when validation hasn't run | Place at index 2 (AFTER pre-commit-gate) |
| Block the commit (exit 2) | This is a reminder, not a gate | Always exit 0 |
| Skip the settings.json backup | Malformed JSON breaks ALL hooks globally | `cp .claude/settings.json .claude/settings.json.bak-codex-hook` first |
| "Improve" or add features beyond this spec | Scope creep — Karpathy guideline: surgical changes only | Implement exactly what's specified |

---

## Assumptions to Verify Empirically

The plan-reviewer flagged one assumption that should be verified during implementation:

> **Assumption:** Claude Code short-circuits subsequent PreToolUse hooks when an earlier hook exits with code 2 (block).

This is why we place the Codex reminder AFTER `pre-commit-gate.sh`. If this assumption is wrong (hooks keep running even after a block), the UX is slightly worse (reminder shows alongside the validation block message) but still functionally correct.

**How to test:** Remove `.validation_passed`, attempt `git commit`, and check whether the Codex reminder fires alongside the validation block message.

---

## Who Writes the Sentinel?

After running a Codex review, Claude should execute:
```bash
touch .codex_review_done
```

The hook's `additionalContext` message tells Claude to do this. It's a convention. The user can also manually skip the reminder by running `touch .codex_review_done` themselves.

---

## Glossary

| Term | Meaning |
|------|---------|
| **Hook** | A shell script that Claude Code runs automatically before/after tool invocations |
| **PreToolUse** | A hook that runs BEFORE a tool executes — can block (exit 2) or allow (exit 0) |
| **Sentinel file** | A marker file whose existence proves that a step was completed (like `.validation_passed`) |
| **Advisory hook** | A hook that provides information but never blocks (always exits 0) |
| **Gate hook** | A hook that CAN block (exit 2) — like `pre-commit-gate.sh` |
| **`additionalContext`** | A JSON field in hook output that injects a message into Claude's context |
| **`$CLAUDE_TOOL_INPUT`** | Environment variable containing the raw tool input (the bash command) |
| **Codex** | OpenAI's code agent CLI — runs GPT-5.4 to review/write code |
| **`/codex:rescue`** | Claude Code skill that delegates a task to Codex |

---

## Design Decisions (Why Things Are The Way They Are)

**Q: Why a sentinel file instead of parsing Codex's internal state?**
A: The Codex plugin's `state.json` file has a `jobs` array that is currently empty — no review has ever been recorded there. We'd be coding against an assumed schema that has never been observed. The sentinel file approach is proven (`.validation_passed` uses it), has no external dependencies, and takes ~5 lines of bash to implement.

**Q: Why place the hook AFTER `pre-commit-gate.sh`, not before?**
A: If validation hasn't been run, `pre-commit-gate.sh` blocks the commit (exit 2). There's no point showing "run Codex review" when you can't commit anyway. By placing our hook after the gate, the reminder only appears when the commit would otherwise succeed — the one moment it's actionable.

**Q: Why `trap 'exit 0' ERR` instead of `set -euo pipefail`?**
A: The other hooks use `set -euo pipefail` because they either (a) don't do risky operations (`bash-audit-log.sh` just appends to a file) or (b) intentionally block on failure (`pre-commit-gate.sh`). Our hook does filesystem operations (stat) that can fail, and it must NEVER block. The trap guarantees exit 0 regardless of what happens internally.

**Q: Why not make this a hard gate like `pre-commit-gate.sh`?**
A: The user explicitly chose advisory-only. The Codex review is optional best practice, not a required workflow step. Making it a gate would be annoying for quick fixes where a full Codex review isn't warranted.

**Q: Why timeout 5 seconds?**
A: The hook does only: (1) grep a string in an env var, (2) check if a file exists, (3) stat that file for age. This takes milliseconds. 5 seconds is the same timeout as `bash-audit-log.sh` (another lightweight advisory hook). The 10-second timeout on `pre-commit-gate.sh` is justified because it runs `git diff` + multiple stat calls.
