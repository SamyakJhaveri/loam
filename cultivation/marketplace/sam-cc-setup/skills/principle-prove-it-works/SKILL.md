---
name: principle-prove-it-works
description: "Apply after completing a task, before declaring done. Verify against the real artifact (run the feature, read the actual value, inspect the diff), not a proxy, self-report, or 'it compiles.'"
disable-model-invocation: true
---

# Prove It Works

Owner copy of pstack 0.15.36's `principle-prove-it-works` (MIT, `LICENSE` beside this file), changed where noted in sam-cc-setup's UPGRADING.md; the router names it as `<S>/principle-prove-it-works`.

In Claude Code, read the Claude Code adapter, `<P>/docs/harness/claude-code.md` (`<P>` as the `sam-cc-setup:pstack` router gives it), once per session before you follow this skill. It maps the Cursor names in pstack skills to Claude Code.

Verify every task output by checking the real thing directly. Do not infer from proxies, self-reports, or "it compiles."

**Why:** Unverified work has unknown correctness. Indirect verification (file mtimes, output freshness, agent self-reports, cached screenshots) feels cheaper than direct observation. Acting on a wrong inference costs far more than checking the source.

Check the real thing, not a proxy:
- Check process liveness directly, not indirectly through derived state; a live process is not a working one, so when the question is whether work moves, check progress (the age of the last log line, how long a lock has been waited on), and never report a check that a written claim still matches as health
- Read the actual value, not a cached or derived representation
- When verification fails, suspect the observation method before suspecting the system

## Script the check when you can

The strongest proof is a deterministic script that re-runs the same comparison, not a one-time eyeball. Write the script, run it, and keep its output as an artifact a reviewer can re-run instead of trusting your word.

Keep the artifact visible for the human. Commit it only for large or complex work where the trail has to be auditable later, like a big port or migration (the **show-me-your-work** skill).
