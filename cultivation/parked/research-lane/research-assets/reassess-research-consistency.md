# Research consistency rules

> Always loaded in research projects. Prevents the four highest-impact consistency failures.

## 1. Never cite numbers from memory

Do NOT use any number from memory, previous messages, or knowledge graph nodes.
For any statistic: compute from raw data files or ask the user for the source.
Say "Let me check the result files for this number" — never "Based on the results, the rate is approximately X%."

## 2. Claim-first paper writing

When writing any paper section:
1. Identify what claims the section needs
2. Find or compute evidence for each claim from raw data
3. Write prose referencing the evidence

Never write prose first and backfill numbers — that path leads to confirmation bias.

## 3. Code graph is structural, not authoritative

CodeGraphContext answers: "What connects X to Y in code structure?"
It does NOT answer: "Is X correct?" or "What value does X produce?" or "Is X the current approach?"
Never use graph node descriptions as paper text. Never navigate the graph to find statistics.

## 4. Explicit uncertainty over silent assumptions

When you cannot find a number or verify a claim, say so:
- "I can't find a result file for this statistic. Should I compute it, or can you point me to the source?"
- "The changelog doesn't mention when this metric was added. Can you confirm?"

Never fill gaps with plausible-sounding guesses. Asking takes seconds; guessing wrong costs hours of rework.

## 5. Scaffold routing for research directories

After bootstrapping a research project, run `/scaffold-context` on high-traffic
research directories (`results/`, `scripts/`, `submission_docs/`) to create
per-directory CONTEXT.md routing files. These directories ship without routing —
each project's content is different enough that pre-built CONTEXT.md files would
be too generic to meet the 25-line minimum in `context-md-anatomy.md`.
