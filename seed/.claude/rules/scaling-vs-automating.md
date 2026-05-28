# Scaling vs. Automating

> Read when: creating new skills, deciding whether to automate a process, or evaluating
> whether a workflow step should become a hook/skill/agent.

## The distinction

Automation means a task runs without human involvement. Scaling means your capacity
increases without proportional increase in effort. These overlap but are not identical.
You can automate something that doesn't scale (an automated response that annoys people
faster). You can scale something without automating it (a well-documented process a new
team member can follow on day one).

The fix is different for each:
- **Automation problems** → deterministic tools, hooks, skills (Layer 1-2 of 60/30/10)
- **Scaling problems** → documentation, context files, stage contracts (make judgment transferable)

## The four-question diagnostic

For each step in your workflow, ask:

1. **Does this step require my specific judgment?**
   If yes → scales by documentation (make judgment criteria explicit), not automation.

2. **Would this step produce the same output regardless of who does it?**
   If yes → automate or delegate with minimal documentation.

3. **Does the quality of this step affect everything downstream?**
   If yes → this is a leverage point. Invest in quality, not speed.

4. **Am I the bottleneck on this step?**
   If yes → document well enough to delegate, or restructure the workflow.

**Rule of thumb**: If #1 and #3 are "yes," this is scaling work — document it,
don't automate it. If #2 is "yes" and #4 is "yes," this is automation work —
make it a skill or hook.

## Anti-pattern: premature skill creation

Before creating a new skill, run the diagnostic above. Common mistakes:
- Automating a task you don't yet understand well enough (Paul Graham: "do things that
  don't scale" until you understand the work deeply)
- Creating a skill for a one-off task (a skill's value comes from reuse frequency)
- Automating the judgment part instead of the throughput part

## Source

JVC `constraints/07-scaling-vs-automating.md` (Brooks's *Mythical Man-Month*, Toyota
Production System, Paul Graham's "Do Things That Don't Scale").
