---
paths:
  - ".claude/skills/**"
  - ".claude/hooks/**"
---

# Scaling vs. Automating

> Read when: creating new skills, deciding whether to automate a process, or evaluating
> whether a workflow step should become a hook/skill/agent.

## The distinction

Two different problems wear the same disguise. *Automating* a step means taking your
hands off it — it runs without you in the loop. *Scaling* means getting more output
without paying proportionally more effort for it. The two are orthogonal, not synonyms: a
step can be fully automated and still refuse to scale (a bot that mass-produces replies
nobody asked for just makes noise faster), and a step can scale beautifully with zero
automation (a checklist precise enough that a new teammate hits your quality bar on day
one). Reaching for automation when the real gap is scale — or the reverse — is exactly
why "I automated it and it got worse" happens.

Match the fix to the gap:
- **Can't take your hands off it** (automation gap) → deterministic tools, hooks, skills (Layer 1-2 of 60/30/10).
- **Effort climbs with every extra unit of output** (scaling gap) → write the judgment down: documentation, context files, stage contracts that let someone else repeat your decisions.

## The four-question diagnostic

Walk each step of the workflow through these; the answers route the step:

1. **Is the value here your judgment, or your throughput?**
   Judgment → the lever is documentation (make the criteria explicit), not a script.

2. **Would any competent person reach the same result from the same inputs?**
   Yes → it's mechanical; hand it to a tool or a lightly-documented delegate.

3. **Does a mistake here contaminate everything after it?**
   Yes → it's a leverage point; spend on getting it right, not on getting it fast.

4. **Is forward progress gated on you personally?**
   Yes → either write it down well enough that someone else can own it, or reshape the workflow so it no longer routes through you.

**Reading the answers**: judgment-heavy and high-leverage (1 and 3) is *scaling* work —
capture it in writing, don't script it. Mechanical and stuck-on-you (2 and 4) is
*automation* work — make it a skill or a hook.

## Anti-pattern: premature skill creation

Before you build a skill, run the diagnostic. The recurring mistakes:
- Encoding a task you don't yet understand well enough — do it by hand until its shape is
  obvious, *then* automate (understand the work before you mechanize it).
- Building a skill for something you'll do once — a skill earns its cost through repetition.
- Automating the judgment and leaving the drudgery, when it should be the other way around.

## Attribution

The automation-vs-scaling split and the "understand the work before you mechanize it"
principle are long-standing ideas in software and operations. Fred Brooks's *The Mythical
Man-Month* is the canonical text on why adding people to a late project makes it later;
lean manufacturing (Taiichi Ohno's system at Toyota) draws the efficiency-versus-effectiveness
line; and "do things that don't scale" is Paul Graham's phrasing. This file is an original
synthesis of those public ideas, applied to template work.
