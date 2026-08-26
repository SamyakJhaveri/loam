---
name: unknowns
description: "Surface what you do not know before prompting, log deviations during implementation, and verify understanding after. Use before starting in an unfamiliar area, when you cannot describe what you want, when a long-horizon task came back wrong, when a plan needs stress-testing, and before merging a change you have not fully read. Emits HTML artifacts that carry the prompt and the output together. NOT for small changes where a one-line answer or a diff already resolves the unknown - running every technique on those is over-production."
---

# Finding your unknowns

Source: Thariq Shihipar, *A Field Guide to Fable: Finding Your Unknowns* (2026-07-03), and
the artifact set at thariqs.github.io/html-effectiveness/unknowns/.

The premise: **the map is not the territory.** Your prompts, skills and CLAUDE.md are the
map; the codebase and its real constraints are the territory. The gap between them is your
*unknowns*, and clarifying them is now the bottleneck:

> "Fable is the first model where I find the quality of the work is bottlenecked by my
> ability to clarify its unknowns."
> "Reducing and planning for your unknowns is *the skill* of agentic coding."

## The precondition - do this first or the rest underperforms

> "The most important part of this process is to give Claude context about your starting
> point. For example, tell it where you are in your thought process; disclose your
> experience with the problem and codebase; and let it work with you like a thought partner."

## The two-sided failure - read before deciding how much to specify

> "If you are too specific, Claude will follow your instructions even when a pivot may be
> more appropriate. If you are too vague, Claude will often make choices and assumptions
> based on industry best practices that may not be a fit for your task."

Both directions fail. This is why "write more rules" and "delete all the rules" are equally
wrong as blanket policies, here and in `.claude/rules/`.

And when a long task comes back wrong, there are **two** remedies, not one:

> "When a long-horizon task comes back wrong, it's likely you need to spend more time
> defining your unknowns **or creating an implementation plan that allows for Claude to
> improvise through them**."

## The four unknowns

|  | you know it | you do not |
|---|---|---|
| **you know you do** | known knowns | known unknowns |
| **you do not** | unknown knowns ("I'll know it when I see it") | **unknown unknowns** |

Most techniques below exist to convert the bottom-right cell into anything else.

---

## Before implementation

### 1. Blindspot pass

**Use the literal words.** Thariq: *"I like to use the literal words 'blindspot pass' and
'unknown unknowns'."* The phrasing is load-bearing; paraphrase and you lose the behaviour.

> I'm working on adding a new auth provider but I know nothing about the auth modules in
> this codebase. Can you do a blindspot pass to help me figure out my relevant unknown
> unknowns and help me prompt you better.

> I don't know what color grading is but I need to grade this video. Can you teach me to
> understand my unknown unknowns about color grading, so that I can prompt better?

Note the second shape: **teach-me**, not give-me-options. In the worked example, asking for
variations to pick from *failed first* - "I realized that I didn't know what 'good' looked
like" - and was replaced by asking to be taught the vocabulary.

### 2. Brainstorms and prototypes - for unknown knowns

> I want a dashboard for this data but I have no visual taste and don't know what's
> possible. Make me an HTML page with 4 wildly different design directions so I can react
> to them.

> Before wiring anything up, make a single HTML file mocking the new editor toolbar with
> fake data. I want to react to the layout before you touch the real app.

> Here's my rough problem: users churn after onboarding. Search the codebase and brainstorm
> 10 places we could intervene, from cheapest to most ambitious. I'll tell you which ones
> resonate.

### 3. Interviews

> Interview me one question at a time about anything ambiguous, prioritize questions where
> my answer would change the architecture.

Order by **architectural blast radius**, not by document order.

### 4. References - source code beats everything

> "the absolute best reference is *source code*"

> This Rust crate in vendor/rate-limiter implements the exact backoff behavior I want. Read
> it and reimplement the same semantics in our TypeScript API client.

Before porting, have it prove comprehension: a semantics map of matched excerpts, gotcha
notes and edge-case tables. Do not accept a port whose reference reading was never shown.

### 5. Implementation plans - ordered by likelihood of change

> Write an implementation plan in HTML, but lead with the decisions I'm most likely to tweak
> with: data model changes, new type interfaces, and anything user-facing. Bury the
> mechanical refactoring at the bottom, I trust you on that part.

---

## During implementation

> Keep an implementation-notes.md file. If you hit an edge case that forces you to deviate
> from the plan, pick the conservative option, log it under 'Deviations', and keep going.

The file is **temporary** and belongs to one build. Implementation itself starts in a **new
session**, with the plan and prototype artifacts passed in as attachments.

**Why this matters.** A common failure is not fabrication but silent loss: when work is
promoted from a scratch file to a committed artifact, a number or one of two control results
can be dropped in transit, and only the favourable half survives. A self-critic pass catches
that after the fact; a Deviations log is the mechanism that catches it at the moment of the
drop instead.

See `IMPLEMENTATION-NOTES.md` in this skill for the format.

---

## After implementation

### Pitches

> Package the prototype, the spec, and the implementation notes into a single doc I can drop
> in Slack to get buy-in. Lead with the demo GIF.

### Quizzes - the merge gate

> I want to make sure I understand everything that's happened in this change. Give me a HTML
> report on the changes for me to read and understand with context, intuition, what was
> done, etc. and a quiz at the bottom on the changes that I must pass.

The bar is stricter than it sounds: **"I only merge after I pass the quiz perfectly."**
Wrong answers should point back to the exact section that was skimmed.

---

## Output as HTML artifacts, not Markdown

The techniques that ask you to **choose between options, absorb structure, or prove you
understood something** produce an **artifact**, carrying *the prompt at the top and the
output below it*, so it is self-documenting and re-runnable. That is the brainstorm, the
interview, the implementation plan, the reference map and the quiz.

A blindspot pass is usually just prose - building a page to deliver a list of things you did
not know is the over-production this skill warns about elsewhere. See `ARTIFACT-FORMAT.md`,
"When NOT to use one".

The reusable pattern is not the styling. It is that **the artifact ends by writing the
user's reply for them** - steal/skip chips, resonate checkboxes, a self-filling reply
template. The output of reacting is a pasteable message, not a decision the user then has to
compose. See `ARTIFACT-FORMAT.md`.

Markdown cannot express the parts that matter: a 2x2 rendered as layout, filter pills with
live counts, a card grid where the filename is the affordance, or a quiz that gates a merge.

## Do not run every technique every time

> "I don't use every technique each time, but it's a useful collection of techniques to have."

Pick by which unknown you are actually stuck on. Running all eight on a small change is the
over-specification failure in a different costume.
