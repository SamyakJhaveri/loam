---
name: session-critique
description: >
  Use when a completed multi-file change needs decision-aware independent review,
  especially for security, trust boundaries, architecture, or cross-cutting behavior.
  Manual only. NOT for routine focused checks, deterministic validation, or work
  that is still changing.
disable-model-invocation: true
---

# Session Critique

Review one fixed diff against the user's decisions and repository rules. Keep the
review independent from implementation. Save its evidence so another turn does not
repeat the same review.

## When to use

- The change crosses subsystems or changes architecture.
- The change affects security, permissions, data integrity, or another trust boundary.
- The user asks for an independent review.

For routine or single-area work, use focused self-review plus `/validate`.

## Model and team policy

Inspect the live spawn tool before selecting a model or effort. Use a stronger available
review profile for the aggregate reviewer. Do not copy a model ID from prose. Add a
specialist only for a concrete risk that the aggregate reviewer cannot cover. Mechanical
evidence gathering uses the default or cheaper available profile.

## Phase 1: Freeze the review input

The integration owner records:

```text
base revision
changed paths, including untracked paths
diff fingerprint
validation receipt fingerprint, or "none"
numbered session decisions
```

The reviewer uses this fixed diff. It checks the fingerprint before and after review.
If the source changes, it stops and reports that its input became stale. It does not
silently switch to the new diff.

## Phase 2: Independent review

Spawn one read-only aggregate reviewer. Give it only the fixed input, repository rules,
and acceptance criteria. Do not include the implementer's rationale or earlier verdicts.
The reviewer checks:

1. Correctness and decision adherence.
2. Security and trust-boundary failures.
3. Unchecked callers, interfaces, and cross-file contradictions.
4. Scope drift, excess machinery, and missing error paths.
5. Claims not supported by the fixed diff or durable validation receipt.

The reviewer does not rerun an unchanged full suite. It may run a focused check only for
a named unresolved risk that existing evidence does not cover. It reports the command,
exit code, and why the extra run was needed.

## Phase 3: Durable findings

Write the report under `.superpowers/reviews/` with the diff fingerprint in the filename.
Keep it bounded. Point to source sections and log paths instead of pasting whole files or
logs.

```markdown
# Independent review: <fingerprint>

## Verdict
PASS | FIX | BLOCKED

## Fixed input
- Base: <revision>
- Diff fingerprint: <fingerprint>
- Validation receipt: <fingerprint or none>

## Findings
| Severity | Evidence | Consequence | Smallest repair |
|----------|----------|-------------|-----------------|

## Coverage and deferred checks
- Checked: ...
- Deferred: ... because ...
```

Every finding is either confirmed with evidence or marked uncertain with the exact check
that would settle it. An unrun check is never a pass.

## Phase 4: Repair and re-review

The user approves any repair that changes scope or a prior decision. A targeted owner
implements each accepted repair and runs its focused regression check. The validation
owner runs new validation because the content fingerprint changed.

Reuse the durable review when the diff fingerprint is unchanged. Run a second independent
review only when a material repair changes behavior across the reviewed boundary, or when
the first report names a concrete unresolved risk. Record why the second review was needed.

## Completion

The critique is complete when the report has a verdict, every blocking finding has a
recorded disposition, the fixed-input fingerprint still matches, and deferred checks are
visible. `/validate` remains the one deterministic full-gate owner. Critique does not run
that gate again.

## Red flags

- Review input changes while reviewers are running.
- Several generic reviewers inspect the same diff.
- A reviewer repeats the full suite without a named evidence gap.
- Findings exist only in chat or a transcript.
- A repair changes the fingerprint but old evidence is called current.
