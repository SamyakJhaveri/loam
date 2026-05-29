# Session Prompts — One per session, copy-paste into fresh Claude Code

> Each prompt is self-contained. Paste one into a new Claude Code session.
> Order: D → H → I → J → K → T1 → T2 → P (parbench comparison)

---

## Session D — Move project-shaped rules to flavor packs

```
Read these two files first, in order:
  1. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health.md
  2. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md

Execute Session D from the plan. The user's STOP gate decision is:
  → Approach 2 (move to flavor packs) — most semantically honest.

Context: project-shaped rules (python.md, architecture.md, tech-stack.md,
frontend-design.md) currently live in .claude/rules/ and propagate to ALL
bootstrapped projects via cp -R in init-project.sh. Move them to the
appropriate flavor packs under flavors/<name>/.claude/rules/. The flavor
overlay loop at init-project.sh:173-178 already handles this — no script
change should be needed.

Use /karpathy-guidelines before each edit. Use superpowers:brainstorming
to design the placement. Run plan-reviewer agent before implementing.
Verify with bin/verify-template.sh. Follow §5 universal protocol.

Also read the mastery doc at:
  _archive/claude-code-mastery/claude-code-mastery-reference.docx
Section 7b ("Progressive Disclosure via .claude/rules/") — apply any
insights about path-scoped rule design to the moved rules.
```

---

## Session H — Triage skills-to-integrate/ (agent team)

```
Read these two files first, in order:
  1. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health.md
  2. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md

Execute Session H from the plan. 16 skills sit in skills-to-integrate/.
The user's STOP gate decision is:
  → Approach 1 (agent team, 4 teammates, advisor pattern).

Back up skills-to-integrate/ to ~/Backups/ FIRST. Spawn the agent team
as described in the plan. Each teammate gets 4 skills. The team produces
a decision table — DO NOT execute moves/deletes until the user reviews
and approves each row.

Verdicts per skill: KEEP-GENERIC (.claude/skills/), KEEP-FLAVOR-<name>
(flavors/<name>/skills/), DELETE-DUPLICATE, DELETE-EMPTY, or ESCALATE.

After user approves, execute in micro-batches (4 skills per commit).
Verify with bin/verify-template.sh after each batch. Follow §5 protocol.

Also read mastery doc section 8a ("Taxonomy of Claude Code Primitives")
and 8c ("Annotated Skill Catalog") — use these criteria to judge whether
each skill is generic, flavor-scoped, or redundant.
```

---

## Session I — Skill description-budget audit

```
Read these two files first, in order:
  1. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health.md
  2. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md

Execute Session I from the plan. After Sessions G and H, there may be
15-20+ skills competing in the auto-invocation match space. Audit each
skill's description: field for overlap, vagueness, and missing negative
triggers ("NOT for...").

Check these overlap candidates specifically:
  - grill-research vs plan-reviewer agent [RESOLVED: kept both, narrowed grill-research description]
  - reflect vs CLAUDE.md self-update loop [RESOLVED: reflect deleted in Session I]
  - session-critique vs review + validate [RESOLVED: kept both as-is; review renamed to multi-review]
  - dream vs reflect [RESOLVED: kept dream as-is; reflect deleted]

For each overlap: ASK the user — keep both (narrow descriptions), fold
A into B, or delete A. Edit SKILL.md description fields to be more
conditional ("Use ONLY when X and not Y"). Follow §5 protocol.

Also read mastery doc section 8b ("Complete Skill Frontmatter Reference")
for best practices on description fields and auto-invocation triggers.
```

---

## Session J — P2 judgment calls

```
Read these two files first, in order:
  1. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health.md
  2. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md

Execute Session J from the plan. Four P2 items, each needs a user decision:

  P2-2: Is the dream skill earning its keep? Check usage frequency.
  P2-3: Add validation-gate mention to seed-docs/CLAUDE.md.tmpl?
  P2-4: Should seed-config/pyproject.toml.tmpl move to flavors/software-eng/?
  P2-5: Read README.md — does it overlap with CLAUDE.md?

ASK the user for each item before acting. Each item gets its own commit.
Follow §5 protocol. Verify with bin/verify-template.sh.

Also read mastery doc section 7a ("What Goes In and What Doesn't") for
CLAUDE.md content guidelines, and section 11 ("Verification & Autonomous
Debugging") for insights on the validation-gate pattern worth documenting.
```

---

## Session K — Final handoff

```
Read these two files first, in order:
  1. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health.md
  2. /Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md

Execute Session K from the plan. Use the /handoff skill to rewrite
docs/audits/2026-05-11-template-health-handoff.md as a completion doc:

  1. Summary: which findings addressed (P0-X, P1-X, P2-X) + sessions done
  2. Outstanding: any skipped/deferred findings and why
  3. Verification: run bin/verify-template.sh, paste output
  4. Decision log: for each STOP gate, what the user decided
  5. Next audit: suggest re-audit date 3-6 months out
  6. Refer back to the plan at docs/audits/2026-05-11-template-health.md

Run bin/verify-template.sh — must show ALL OK. Follow §5 protocol.
```

---

## Session T1 — Test: bootstrap a real project (research flavor)

```
We're testing the project-template by bootstrapping a real project.

1. Run: bin/init-project.sh ~/Desktop/test-research-project --flavor research
2. cd into the new project
3. Open a Claude Code session in it
4. Try these workflows:
   - /catchup (should orient you)
   - /commit (should work on staged changes)
   - /karpathy-guidelines (should load principles)
   - Create a simple Python script, see if hooks fire
   - Check that .claude/rules/ only has generic rules (no python.md etc
     if Session D is done)
5. Report what worked, what broke, what's missing

This is a real-world smoke test. Note any rough edges for feedback to
the template. Clean up the test project when done:
  rm -rf ~/Desktop/test-research-project
```

---

## Session T2 — Test: bootstrap a software-eng project + stress test

```
We're stress-testing the project-template with the software-eng flavor.

1. Run: bin/init-project.sh ~/Desktop/test-swe-project --flavor software-eng
2. cd into the new project
3. Initialize a simple Node.js or Python project in it
4. Try these advanced workflows:
   - /validate (does the validation loop work?)
   - /pr (does it create a PR correctly?)
   - /session-critique (does the agent team spawn?)
   - Run bin/verify-template.sh from the TEMPLATE repo to confirm it
     still bootstraps correctly
5. Check settings.json — is the model pin present? Are hooks wired?
6. Try the plan-reviewer agent on a dummy plan
7. Report findings: what works, what's broken, what's confusing

Also read mastery doc sections 10 ("Hooks") and 11 ("Verification") —
compare what the mastery doc recommends vs what the template provides.
Note any gaps worth adding back to the template.

Clean up: rm -rf ~/Desktop/test-swe-project
```

---

## Session P — Compare parbench_sam and transplant

```
Compare the Claude Code setup between two repos:
  SOURCE: /Users/samyakjhaveri/Desktop/parbench_sam/
  TARGET: /Users/samyakjhaveri/Desktop/project_template/

Goal: identify skills, hooks, agents, rules, and settings in parbench_sam
that are GENERIC (should be transplanted to project_template) vs
PROJECT-SPECIFIC (should stay in parbench_sam only).

Steps:
1. Diff the directory structures:
   diff <(cd /Users/samyakjhaveri/Desktop/parbench_sam && find .claude/ -type f | sort) \
        <(cd /Users/samyakjhaveri/Desktop/project_template && find .claude/ -type f | sort)
2. For each file only in parbench_sam: read it, classify as generic or
   project-specific. Present a decision table to the user.
3. For each file in both: diff them, note meaningful differences.
4. Check parbench_sam's settings.json for hooks, permissions, statusLine
   config that should be transplanted.
5. Check parbench_sam's CLAUDE.md for patterns worth generalizing.

DO NOT copy anything without user approval. Present a decision table first.
For files classified as generic: propose where they go in project_template
(.claude/skills/, .claude/hooks/, a flavor pack, etc.).

Also check: does parbench_sam have a statusLine config? That's the
progress bar the user remembers seeing.
```
