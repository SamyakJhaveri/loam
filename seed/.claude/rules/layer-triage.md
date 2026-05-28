# Layer triage — the 60/30/10 diagnostic

> Read when: scoping a new task, evaluating an existing skill, or proposing a new automation. Use as a triage filter before any task routes work to an LLM.

## The framework

JVC's central thesis (`constraints/06-layer-triage.md:52-70`, repeated in `the_full_toolkit/README.md:46`):

> Roughly 60% of the problems people throw at AI are better solved by traditional tools, databases, or established writing principles. Another 30% are handled well by rule-based systems, existing skills, or purpose-built software. Only about 10% genuinely benefit from the probabilistic reasoning that a language model provides.

The numbers are not literal frequencies. Treat them as a budget heuristic: when designing a task that routes work to an LLM, the LLM-handled portion should rarely exceed ~15% of the total work; if it does, the design is likely over-assigning to the wrong layer.

## The three layers

| Layer | What it is | Examples |
|---|---|---|
| Deterministic (60%) | Functions, scripts, lookups, SQL, validators, parsers, formatters. Always produces the same output from the same input. | `ruff check`, `pytest`, schema validators, `git diff`, sorting algorithms, regex extraction. |
| Rule-based (30%) | Pre-written decision trees, configured workflows, skills with explicit triggers, MCPs that route to deterministic backends. | Most slash commands, `/validate`, `pre-commit-gate.sh`, lint configurations, the `Pipeline Gate` pattern. |
| Probabilistic (10%) | Open-ended reasoning, synthesis across heterogeneous sources, novel-problem decomposition. | `feature-dev` plan-mode, `multi-review` analysis, code-review judgment calls, research synthesis. |

## How to triage a proposed task

Answer in order. The first "yes" routes the task:

1. **Is the output a deterministic transformation of the input?** → Layer 1. Write a function or use an existing tool. Do not invoke an LLM.
2. **Does an existing skill, hook, or MCP already handle this exact pattern?** → Layer 2. Wire it up; don't author new LLM scaffolding.
3. **Does the task require synthesis across sources that have no shared schema, or judgment that depends on context the rules cannot encode?** → Layer 3. The LLM portion is justified. Wrap it in a stage contract (`stage-contract.md`) with a Must-NOT list and a verifiable Done.

## Engineering-research adaptations

The framework was authored for consulting / content workflows. Translation:

| JVC framing | Engineering / research equivalent |
|---|---|
| "Pricing logic is deterministic" | Build pipelines, dependency resolution, code formatting, type checking, test running — all deterministic. |
| "Brand voice is rule-based" | Style guides, lint rules, API contracts, schema validation, test gates. |
| "Final writing review is probabilistic" | Code review, hypothesis evaluation, debugging a flaky bug, paper drafting, experimental design. |

## Anti-patterns the triage catches

- **LLM where a regex would do.** Asking the model to extract a field from JSON output. → Layer 1: `jq`.
- **LLM where a config would do.** "Choose the right model for this task." → Layer 2: a routing rule with explicit conditions, not a meta-skill that prompts the model to choose.
- **LLM where a test would do.** Verifying that the implementation matches the spec. → Layer 1: `pytest`. The model can author the test; the gate is deterministic.
- **LLM where a skill would do.** Re-explaining the project's conventions every session. → Layer 2: put it in `.claude/rules/` and let path-scoped loading do the work.

## When the AI portion legitimately exceeds 15%

Three patterns:

1. **Greenfield design** — no prior rule-base exists yet; the LLM is helping construct what will become Layer 2. Acceptable for the first iteration, but the Output should *be* the Layer 2 artifact (a rule, a skill, a contract).
2. **Cross-domain synthesis** — combining heterogeneous sources (paper + code + experiment data). No deterministic pipeline covers all three; the LLM is the bridge.
3. **One-off exploration** — a research question with low repetition value. Not worth investing in rules. Use the LLM, capture the result, move on.

If a task fits none of these and still has >15% LLM portion, redesign before automating it.

## Self-audit

Periodically audit your project's `.claude/` setup against the 60/30/10 framework.
Run this diagnostic:

1. **Inventory**: List every rule, skill, agent, and hook in `.claude/`.
2. **Classify**: For each, assign to deterministic (60%), rule-based (30%),
   or probabilistic (10%) based on what the asset actually does.
3. **Flag**: Identify items where an LLM is used but a deterministic tool could
   do the job (the "LLM where a regex would do" anti-pattern above).
4. **Report**: Show the current ratio and specific recommendations.

If the probabilistic portion exceeds ~15%, look for items to move to Layer 1 or 2.

Source: JVC Vault Course 4.2 ("The Build — VigilOre"), Exercise 2 — "Find the AI that shouldn't be AI."

## Source

JVC `constraints/06-layer-triage.md` (the canonical framework); `the_full_toolkit/README.md:46` (the 60/30/10 origin statement); case studies in `jvc_vault_3.2.md` (VigilOre) and `jvc_vault_3.3.md` (NLP Logix) for worked examples of the diagnostic in practice.
