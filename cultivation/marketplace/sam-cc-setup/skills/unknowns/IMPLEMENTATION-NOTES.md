# implementation-notes.md — the Deviations log

Temporary, one per build, deleted or archived when the work merges. Not a design doc and
not a status report: it is a record of every point where reality differed from the plan.

## The instruction that produces it

> Keep an implementation-notes.md file. If you hit an edge case that forces you to deviate
> from the plan, pick the conservative option, log it under 'Deviations', and keep going.

Three parts, and all three matter:

1. **Pick the conservative option.** Not the one that makes the number look better.
2. **Log it.** The entry is the deliverable, not the deviation.
3. **Keep going** - for deviations that are reversible and inside the stated scope. The log
   is what makes not-stopping safe, and it only covers that much. **Stop and ask** when the
   conservative option would still change a published number, alter an architecture or an
   interface, touch anything under the artifact freeze, or cost more to undo than to confirm.
   A Deviations entry is not consent.

## Format

```markdown
# Implementation notes — <what is being built>
Plan: <path to the plan or prototype this implements>
Started: <date>

## Deviations

### D1 — <one line: what the plan said vs what was done>
**Plan said:** <verbatim from the plan>
**Reality:** <what was actually found — file:line, command output, the measurement>
**Chose:** <the conservative option>
**Rejected:** <the other option, and why it was less conservative>
**Costs:** <what this deviation makes worse, or "none identified">
**Needs a decision from the owner?** yes / no

### D2 — ...

## Open questions
- <anything that could not be resolved conservatively>
```

## The rule that exists because of a real incident

**Every measurement taken during the build goes in, not only the ones that support the
result.** On 2026-07-30 a dwt2d evidence card was promoted from a scratch card to the
committed repo card, and only the favourable of two control figures survived the promotion.
A self-critic pass caught it afterwards. Nothing was fabricated — a number was simply
dropped in transit, which is the more common failure and the harder one to see.

So: if you ran two controls, both go in the log. If a number moved when you re-ran it, both
values go in the log with the reason. A Deviations log that contains only the deviations you
were comfortable with is worse than none, because it looks like diligence.



## When to promote an entry out of the log

An entry graduates when it is no longer about this build:

- It contradicts a documented fact → fix the doc and cite the log entry.
- It will recur → it is a lint rule, a CI step, or a test, per the automation lever. Do not
  leave a recurring class in a temporary file.
- It changes a published number → it goes to the owner before anything ships.
