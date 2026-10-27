# What the evidence says about the six research-lane decisions, 2026-10-27

Audit of the owner's 2026-10-27 research-lane rulings (`docs/RULES.md`, rows "Research lane, ...") against published research and practitioner guidance.
The DistBench side is in `distbench-research-practice-2026-10.md`.
This note changes no ruling; it records evidence and the design limits it implies for the two build-later units, #361 and #362.

## How it was gathered

A deep-research workflow ran 106 agents: 5 search angles, about 15 fetched sources, and a 3-vote adversarial check per claim (2 of 3 refutes kill a claim).
16 claims survived and 9 were refuted.
All 16 survivors come from arXiv papers or one vendor report; most are single preprints, and almost all tested 2024 to mid-2025 models, none Opus 5.x or Fable.
The lead re-read two abstracts (2602.11988, 2506.20803) on arXiv and the Boris Cherny tips file (`~/.claude/skills/boris/SKILL.md`, version 8.13.0) directly; an Opus verifier read the HindSight paper (2603.15164).
The workflow did not weigh the Anthropic posts, the Boris tips, or the notes in this folder; the Boris lines below were read by the lead.

## Lean skills and guidance (the cross-cutting rule)

Supported, with one sharpening: lean means "only what the agent cannot infer, and no overlapping skills", not just fewer lines.
- Repository context files "do not generally improve task success rates" and add "over 20%" inference cost; "repository overviews ... are not helpful", while the files "are useful for specifying non-standard coding practices" (Gloaguen et al., arXiv 2602.11988; Python issue-fixing tasks).
- Look-alike skills cut skill-selection accuracy (one competitor per skill: 7-30% drop; two: 17-63%), more than skill count does (Li, arXiv 2601.04748; toy skills, GPT-4o only).
- Accuracy falls as instruction count and context length grow (IFScale, arXiv 2507.11538: 68% at 500 instructions; Chroma "Context Rot" report), but at the dozens of instructions Loam carries the size of the effect is unmeasured; a claim that strong models lose little there was refuted.
- Practitioner guidance agrees: move steps into skills that load when needed (Boris tip 112, `boris/SKILL.md:1877`), keep skills "lightweight guides" (tip 114, `:1906`), and Boris found 38 skills unused in 2,345 sessions (tip 106).
- Counter-evidence: a Claude Code team tip says "If you do something more than once a day, turn it into a skill or command" (`boris/SKILL.md:308`), against the closed second-repetition rule. The overlap result reconciles them: a repeated task earns a skill only when no existing skill already covers it.

## Per decision

| Decision | Evidence | Verdict |
|---|---|---|
| Experiment contract closed for now | no surviving claim | untested |
| Conveyor closed | no surviving claim | untested |
| Ideation skills built later (#361) | 2506.20803, 2409.04109, 2604.18005, 2507.08350, 2502.14297, 2506.22026, 2603.15164 | supported only with the limits below |
| Reading log built later (#362); no adopt-skill; no second-repetition rule | 2601.04748; indirect support from 2502.14297 and 2409.04109 | supported; reading log only loosely |
| Decision ledger closed | 2602.11988 | supported |
| Bundle deleted; paper tooling built in DistBench first | 2502.14297 | number flow supported; "DistBench first" untested |

## Limits the evidence puts on #361 (ideation and research gaps)

1. End in a validation step, not a ranked list: after real execution, LLM ideas lost "significantly more" score than expert ideas on every metric, with "a flip in rankings" (Si, Hashimoto, Yang, arXiv 2506.20803).
2. An LLM judge is not the final call: the best LLM idea evaluator reached 53.3% balanced accuracy against 56.1% human agreement, chance being 50% (Si, Yang, Hashimoto, arXiv 2409.04109).
3. Diverge with independent proposers, not one shared brainstorm: 4000 seed ideas per topic gave about 200 unique ones (2409.04109), and dense shared-context debate speeds convergence (Chen et al., arXiv 2604.18005); structured critique loops gain diversity up to about 3 critics and 3 rounds (Ueda et al., arXiv 2507.08350).
4. Gap checks need several searches and a reranking step, and must report what was searched: AI Scientist papers had a median of five citations (Beel et al., arXiv 2502.14297), and gap detection fell from 89.66% to 13.79% without facet reranking (Shahid et al., arXiv 2506.22026; 58 items).
5. The backlog's "2.5x" is HindSight (Bo Jiang, arXiv 2603.15164): retrieval-augmented ideas scored 0.297 vs 0.119 on matched later papers' impact (p<0.001), an LLM judge saw no difference (p=0.584), and that score correlated negatively with LLM-judged novelty (rho=-0.29); 200 ideas, one judge model. It measures matched-paper impact, not the ideas' own impact.

DistBench's by-hand method already fits limits 3 and 4 in part: three independent reports from one brief, merged with a support count, then three competitor papers read in full (`distbench-research-practice-2026-10.md` section 5, item 4).

## Limits on #362 (reading log) and the paper tooling

- AI-written manuscripts held "hallucinated numerical results" and placeholder text like "Conclusions Here" (2502.14297): numbers should flow mechanically from analysis output, and the paper build also needs a placeholder and empty-section lint.
- A quote check is cheap: a 32-line read-only script matched 31 of 42 Verified quotes in DistBench's notes against the PDFs on the first pass; of the 11 misses, 7 were a PDF filed under a hash name, 3 were the checker's punctuation handling, and 1 was a dropped "and" in the note (surprise-me run, 2026-10-27, scratch only). A verifier script fits the lean rule better than label rules written into a skill.
- The three competitor papers read in full are not in DistBench's `papers/`.

## Open questions

- Does trimming Loam's always-loaded files to non-inferable rules (for example the Layout table in `AGENTS.md`) change task success or cost on Loam's own factory tickets?
- Do Loam's shipped and marketplace skills overlap in their descriptions, and does Claude pick the wrong one in practice?
- What does practitioner guidance say about experiment contracts, conveyors and paper-number pipelines? No claim survived on these.
- Do Opus 5.5 and Fable close the ideation-execution gap or the idea-judging gap? Every result above predates them.
