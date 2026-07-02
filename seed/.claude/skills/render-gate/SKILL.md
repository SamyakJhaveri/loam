---
name: render-gate
auto-activate: false
description: >
  TDD rendering gate for Copier template development. Writes E2E assertions first,
  then iteratively fixes the template until all flavors render cleanly. Never commits
  on a red suite. Use when editing Copier template files (copier.yml, .jinja files,
  flavor overlays). NOT for non-template projects, runtime code changes, or
  general testing (use /validate).
---

# Render Gate: TDD Template Rendering

A test-driven development loop for Copier template work. The agent writes rendering
assertions first, then iterates until every flavor passes.

## When to Use

- Editing `copier.yml`, `*.jinja` files, or flavor overlays
- Adding a new Copier question or choice
- Modifying the `_subdirectory`, `_tasks`, or `_templates_suffix` config
- After any change that could affect how the template renders

## When NOT to Use

- Non-template projects → use `/validate`
- Runtime code changes that don't affect template rendering
- Documentation-only edits

## Procedure

### Step 1: Establish the test baseline

Check if `bin/verify-template.sh` exists and what it covers:

```bash
[ -x bin/verify-template.sh ] && echo "verify-template.sh exists" || echo "no verify script"
cat bin/verify-template.sh 2>/dev/null | head -30
```

### Step 2: Write or extend E2E assertions

If `bin/verify-template.sh` exists, use it as the base. If it doesn't cover the
current change, extend it. The assertions must verify:

1. **Every flavor renders** — each combination of Copier choices produces output
2. **Answers file is valid** — `.copier-answers.yml` exists and contains expected keys
3. **Choices mappings are correct** — conditional includes/excludes match the choices
4. **YAML scalars are well-formed** — no unquoted colons, no broken folded scalars
5. **Jinja syntax is valid** — no unclosed tags, no undefined variables

Render from **committed git state** (not working tree) to match Copier's behavior:

```bash
TMPDIR=$(mktemp -d)
uvx copier copy --trust --vcs-ref HEAD --defaults . "$TMPDIR/test-default" 2>&1
echo "Exit code: $?"
ls -la "$TMPDIR/test-default/"
```

### Step 3: Run the full suite and record failures

```bash
bin/verify-template.sh 2>&1
echo "Exit code: $?"
```

### Step 4: Iterative fix loop

For each failure:
1. Read the error output
2. Identify the root cause in the template source
3. Fix the template file
4. Re-run the **full suite** (not just the failing test)
5. Report: what failed, what you fixed, current pass/fail status

**Hard rule:** Never commit while any test is failing. The loop continues until
exit code 0.

### Step 5: Final verification

After all tests pass:

```bash
bin/verify-template.sh 2>&1
echo "Final exit code: $?"
```

Only proceed to commit if exit code is 0. Report the full pass summary.

## Common Failure Patterns

| Symptom | Likely Cause |
|---------|-------------|
| `copier copy` fails with "not a git repo" | Need `--vcs-ref HEAD`; template must be committed |
| YAML parse error in rendered output | Unquoted colon in a Jinja variable or description field |
| Missing file in rendered output | Conditional include/exclude doesn't match the flavor choices |
| `.copier-answers.yml` missing keys | New question added to `copier.yml` without a default |
| Jinja `UndefinedError` | Variable name mismatch between `copier.yml` and template |
