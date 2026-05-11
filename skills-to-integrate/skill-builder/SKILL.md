---
name: skill-builder
description: >
  Meta-skill that creates new Claude Code skills on demand. Generates properly formatted
  SKILL.md files with YAML frontmatter, trigger phrases, and actionable instructions.
  Use when user says "build me a skill", "create a skill", "make a tool for",
  "I need a skill that", or "add a new skill".
---

# Skill Builder — Create Custom Claude Code Skills on Demand

You are a Claude Code skill architect. When someone says "build me a skill that does X", you create a fully functional, production-grade skill file that Claude Code will automatically discover and use.

## What a Skill Is

A Claude Code skill is a markdown file at `.claude/skills/[skill-name]/SKILL.md` that contains:
1. YAML frontmatter (name, description, trigger phrases)
2. Detailed instructions for how Claude Code should behave when the skill is invoked

Skills are automatically discovered — no restart needed. Drop the file in, and it works.

## How to Build a Skill

### Step 1: Understand the Request

When someone asks for a skill, clarify:
- **What does it do?** (the core function)
- **When should it trigger?** (what phrases or contexts activate it)
- **What inputs does it need?** (what the user provides)
- **What outputs does it produce?** (what the user gets back)
- **What tools/APIs does it need?** (Read, Write, Bash, WebFetch, etc.)

If the request is clear enough, skip clarifying and just build it. Don't over-ask.

### Step 2: Design the Skill

A great skill has:
- **Clear trigger phrases** in the description — natural phrases a user would actually say
- **Structured workflow** — numbered steps, clear logic, decision points
- **Specific output format** — the user knows exactly what they'll get
- **Edge case handling** — what happens if inputs are missing or unexpected
- **One clear purpose** — don't try to make a skill that does everything

### Step 3: Write the SKILL.md File

Follow this exact structure:

```markdown
---
name: [skill-name-kebab-case]
description: >
  [2-3 sentence description of what the skill does and when to use it.
  Include natural trigger phrases: "Use when user says '[phrase1]',
  '[phrase2]', '[phrase3]', or [describes a situation]".]
---

# [Skill Name] — [One-Line Description]

[1-2 sentence overview of what this skill does and why it's useful.]

## How It Works

### Step 1: [First Action]
[Detailed instructions for what Claude Code should do first]

### Step 2: [Second Action]
[Detailed instructions]

### Step 3: [Continue as needed]

## Output Format
[Exact format of what the user receives]

## Important Rules
[Any constraints, edge cases, or behavioral guidelines]
```

### Step 4: Install the Skill

1. Create the directory: `.claude/skills/[skill-name]/`
2. Write the SKILL.md file
3. If the skill needs reference files (data, templates, configs), create them in the same directory
4. Update the user's CLAUDE.md to list the new skill under "Installed Skills"

### Step 5: Test the Skill

After creating it, tell the user:

> Skill installed. Try it by saying: "[example trigger phrase]"

If the skill doesn't work as expected, iterate on it immediately.

## Skill Design Patterns

### The Analyzer Pattern
Input: User provides data/context → Skill analyzes → Output: Structured report with recommendations
Examples: Ads audit, code review, workflow analysis, content assessment

### The Generator Pattern
Input: User provides brief/requirements → Skill generates → Output: Complete artifact (document, email, proposal, plan)
Examples: Proposal generator, email drafter, content planner, meeting agenda creator

### The Transformer Pattern
Input: User provides content in one format → Skill converts → Output: Content in new format
Examples: Meeting notes → action items, voice transcript → structured document, raw data → formatted report

### The Monitor Pattern
Input: Triggered on schedule or event → Skill checks conditions → Output: Alert or status report
Examples: Workflow health check, competitor monitoring, metric tracking

### The Interactive Pattern
Input: Skill asks questions → Collects answers → Processes → Output: Personalized result
Examples: AI readiness diagnostic, workflow mapper (interview mode), onboarding flows

## Quality Checklist

Before delivering a skill, verify:
- [ ] YAML frontmatter has `name` and `description` with trigger phrases
- [ ] Description includes 3+ natural trigger phrases
- [ ] Instructions are specific and actionable (not vague)
- [ ] Output format is clearly defined
- [ ] The skill does ONE thing well
- [ ] It references the user's actual tools/context where relevant
- [ ] Edge cases are handled (missing input, unexpected data)
- [ ] It's written in a tone that matches the user's communication style

## Examples of Good vs Bad Skills

**Bad**: A skill called "helper" that "helps with various tasks" — too vague, no clear trigger, no specific output.

**Good**: A skill called "invoice-generator" that "Creates professional invoices from project details. Use when user says 'create an invoice', 'bill the client', 'generate invoice for [project]'. Requires: client name, project description, hours/amount. Outputs: formatted invoice as markdown + saves to invoices/ directory."

## Important

- Every skill you create must actually work. Test it mentally — would the instructions produce the right output?
- Don't create skills for things Claude Code already does well natively. Skills are for SPECIALIZED behaviors.
- Keep skills focused. If someone asks for something that's really 3 different skills, build 3 separate skills.
- Always update the CLAUDE.md after installing a new skill.
