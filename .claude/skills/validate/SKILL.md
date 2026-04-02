# Post-Session Validation Loop

**Trigger:** When user types `/validate`, `/validate quick`, or `/validate fix`

Runs a wave-based multi-agent validation loop after implementation work, before committing.
Enforces the project's quality bar (CLAUDE.md Quality Standards).

## Arguments

- (none) or `full` → full 4-wave validation (recommended, ~3 min)
- `quick` → Wave 1 only: fast checks (schema, diff, security, ~30s)
- `fix` → re-run failed waves only (after implementing fixes)

## Prerequisites

Before running `/validate`:
1. All implementation work for the session is complete (files saved)
2. Files are NOT yet committed (git diff HEAD shows your changes)
3. Activate venv: `source {{PROJECT_ROOT}}/env_parbench/bin/activate`

## Workflow

### Step 0: Snapshot (before any wave)

Capture baseline metrics for regression-checker context:
```bash
source {{PROJECT_ROOT}}/env_parbench/bin/activate
cd {{PROJECT_ROOT}}
echo "=== PRE-VALIDATION SNAPSHOT ==="
echo "Changed files: $(git diff --name-only HEAD | wc -l)"
git diff --name-only HEAD
echo "Spec count: $(ls specs/*.json | wc -l)"
echo "Unit tests: $(python3 -m pytest c_augmentation/test_transforms.py --collect-only -q 2>/dev/null | tail -1 || echo 'N/A')"
```

Pass this snapshot as context to regression-checker.

---

### WAVE 1: Fast Checks (~30s)

**Launch 3 agents IN PARALLEL** (single message, multiple Agent tool calls):

1. **verify-app** — schema validation + unit tests + spec integrity + manifest cross-check
   - Expects ~135 known errors (120 HeCBench + 15 phantom). Anything beyond = real failure.

2. **diff-reviewer** — git diff analysis
   - Checks for partial implementations, accidental changes, removed tests, manifest violations

3. **security-scanner** — security patterns in changed files
   - Checks for secrets, command injection, unsafe shell scripts

**Wave 1 Gate:** If ANY agent returns FAIL → skip Wave 2+, go to Fix Loop.

Report Wave 1 results concisely:
```
WAVE 1: PASS/FAIL (3/3 or X/3)
  verify-app:       PASS/FAIL
  diff-reviewer:    PASS/FAIL
  security-scanner: PASS/FAIL
```

---

### WAVE 2: Deep Analysis (~60s)

**Skip if `/validate quick` was requested.**

**Launch 2-3 agents IN PARALLEL:**

4. **test-synthesizer** — writes + runs temp test programs for changed Python/specs/hooks
   - Tests Python imports, spec JSON validity, shell syntax, agent frontmatter

5. **regression-checker** — before/after metrics comparison
   - Verifies: Rodinia=60, XSBench≥4, tests=15, schema errors~135, manifest non-decreasing

6. **spec-auditor** (CONDITIONAL — only if `git diff --name-only HEAD | grep -q '^specs/'`)
   - Full spec audit: slug regex, category enum, manifest entry, source dir, schema

**Wave 2 Gate:** If ANY blocking agent returns FAIL → go to Fix Loop.

---

### WAVE 3: Cross-Checks (~45s)

**Launch 2 agents IN PARALLEL:**

7. **consistency-checker** — docs vs code cross-check
   - Verifies CLAUDE.md agent/skill/rules tables match actual files
   - Checks KNOWN_FAIL specs excluded from eval-batcher eligibility

8. **code-simplifier** — code quality advisory
   - Finds duplication, dead code, over-engineering
   - **Advisory only (WARN, not FAIL)** — does not block commit

**Wave 3 Gate:** Only consistency-checker FAIL blocks. code-simplifier issues are advisory.

---

### WAVE 4: Self-Review (~30s)

**Launch 1 agent (sequential, Opus):**

9. **self-critic** — adversarial self-review
   - Rationalization patterns, incomplete work, unverified claims, quality bar violations
   - Applies obra/superpowers verification-before-completion principle
   - **FAIL blocks commit**

10. **plan-reviewer** (CONDITIONAL — only if Fix Loop was triggered in any previous wave)
    - Adversarial review of the fix plan (Opus)

---

### Fix Loop (triggered when any wave FAILs)

When a wave FAIL is detected:

1. **Collect** all FAIL verdicts from the current wave (wait for all parallel agents to finish)
2. **Enter plan mode** with a targeted fix plan:
   ```
   Issues found in Wave N:
   - [Agent]: [specific problem at file:line]
   - [Agent]: [specific problem at file:line]

   Proposed fixes:
   1. [minimal fix for issue 1]
   2. [minimal fix for issue 2]
   ```
3. **Wait for user approval** — do not implement before approval
4. **Implement fixes** — targeted only, no scope creep, no unrequested improvements
5. **Re-validate** with `/validate fix`:
   - Re-run the failed wave and all downstream waves
   - Skip waves that already passed (no need to re-run verify-app if only Wave 3 failed)

**Maximum iterations:** 3. After 3 failed fix attempts on the same issue → STOP and escalate:
```
ESCALATION: Issue in [agent] not resolved after 3 attempts.
Problem: [description]
Options:
  a) Manual investigation required
  b) Defer this issue (document in known-issues.md)
  c) Override validation for this commit (add reason to commit message)
```

---

### Completion: Write Sentinel

After ALL waves pass (or after Wave 1 for `/validate quick`):

**IMPORTANT — set WAVES_RUN before running this block:**
- `/validate` or `/validate full` → `WAVES_RUN=4` (commits unblocked)
- `/validate quick` → `WAVES_RUN=1` (commits still blocked by pre-commit gate)
- `/validate fix` → `WAVES_RUN=4` (all remaining waves re-ran)

```bash
cd {{PROJECT_ROOT}}

# Set this based on which command variant was run (see note above):
if [ "${VALIDATE_MODE:-full}" = "quick" ]; then
  WAVES_RUN=1
else
  WAVES_RUN=4
fi

cat > .validation_passed << EOF
timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
git_hash=$(git rev-parse HEAD 2>/dev/null || echo "none")
changed_files=$(git diff --name-only HEAD | wc -l | tr -d ' ')
waves_passed=${WAVES_RUN}
validated_by=validate-skill
EOF

echo ".validation_passed written — git commit is now unblocked"
```

**Then report the full validation summary:**

```
=== POST-SESSION VALIDATION: PASS ===

WAVE 1: PASS (3/3) ~Xs
  verify-app:       PASS (schema: 135 expected, tests: 15/15, manifest: OK)
  diff-reviewer:    PASS (N files, 0 regressions, 0 partial impls)
  security-scanner: PASS (0 issues found)

WAVE 2: PASS (3/3) ~Xs
  test-synthesizer:   PASS (N tests run, N passed)
  regression-checker: PASS (all metrics stable)
  spec-auditor:       PASS/SKIP

WAVE 3: PASS (2/2) ~Xs
  consistency-checker: PASS
  code-simplifier:     WARN (N advisory suggestions — see details)

WAVE 4: PASS (1/1) ~Xs
  self-critic:         PASS (no rationalization patterns)

OVERALL: PASS
Sentinel: .validation_passed written
git commit: UNBLOCKED

Advisory items from code-simplifier:
  [list suggestions with file:line if any]
```

---

## Context Management Protocol

**Critical: all agent output stays in subagent context. Only summaries return.**

Each agent is instructed to return max 50 lines. The aggregated report above (~50 lines)
is all that enters the main conversation context. This is the subagent isolation pattern:
heavy validation work runs in isolated 200K-token windows, the main session stays lean.

Do NOT read agent output files into main context. Do NOT paste raw test output here.
Let each agent do its work and return only its structured verdict.

## Override (emergency, docs-only changes)

If validation is genuinely not applicable (e.g., updating a comment in a single .md file):
1. User explicitly says "skip validation for this commit"
2. Document reason in commit message: `[skip-validate: reason]`
3. This must be RARE — the self-critic will flag overuse as a quality concern
