---
name: research-gap
disable-model-invocation: true
description: "Pick research questions or check a research gap, ending in one cheap validation: blind proposer seats, a merge with support counts, logged paper searches, and the closest papers read into a quote-checked reading log. Use for research questions, a gap, novelty or 'first to' claim, prior work for one claim, or logging a paper. Manual only."
argument-hint: "[the research question, or the one claim to check]"
---

# Research gap

A research gap is a hypothesis until a search built to destroy it fails.
This procedure turns a question into candidate research questions, checks each gap against the literature, and ends in one executed check.
`${CLAUDE_SKILL_DIR}` below is this skill's folder; Claude Code fills it in when the skill is invoked, and if you read this file by path it is the folder holding it.
Subagents and seats do not see it: give them the resolved path.
The scripts in `scripts/` need Python 3 and poppler's `pdftotext`, nothing else.
The evidence behind each step is in Loam's `docs/research/research-lane-evidence-2026-10.md`.

## Modes and their cost

| Mode | Seats | Gap checks | Cost |
|---|---|---|---|
| Full | four: assets, reframe, codex, analogist | every shortlisted gap claim | Trial, 27-28 Oct 2026: two full runs together took about 30 Claude runs plus 3 Codex runs (one a review), most Claude runs at 150K to 300K tokens, over one night; more than an hour of it was gap workers waiting on Semantic Scholar's rate limit. |
| Small | two: assets (Opus) and codex | the owner's ideas only | Estimate, not yet run: about 6 Claude runs and 1 Codex run. |

Before step 1 the lead gives the owner both costs and asks which mode; an unattended run uses the mode its brief names.

## Entry points

- Picking research questions: steps 1 to 6, in the chosen mode.
- Checking one gap, novelty or "first to" sentence: write it as the only idea in `merged.md`, marked owner, and start at step 3.
- Surveying prior work for one claim (the academic-research workflow): write the claim as the only idea in `merged.md`, marked owner, and run steps 3 and 4 only; the result is its `gap.md`.
- Logging one paper read in full, outside any run: no run folder and none of steps 1 to 6.
  1. Store the PDF in `<repo>/papers/` and write its note in `<repo>/docs/research/readings/notes/`, both named and written as `READINGS.md` beside this file says.
  2. Log it: `python3 ${CLAUDE_SKILL_DIR}/scripts/readings-index.py add --paper <arXiv:id or doi:doi> --note <note path from the repo root> --depth full --reader <reader> --date <YYYY-MM-DD>` (`add` comes first; that folder carries no date, so give one).
  3. Check it: `python3 ${CLAUDE_SKILL_DIR}/scripts/quotecheck.py <note path>`; on a SPLIT or MISS fix the quote from the PDF, trim it, or relabel the line Inferred, and run it again until it exits 0.
  4. Rebuild the index: `python3 ${CLAUDE_SKILL_DIR}/scripts/readings-index.py`.

  Done when: the check exits 0 with a nonzero checked count, and `<repo>/docs/research/readings/INDEX.md` has a row for the paper and that note at depth full.

## Where the owner is needed

- Before step 1: which mode.
- Step 5: every decision the facts cannot settle.
- Step 6: a pilot that spends money or rented hardware.

An unattended run writes what it has and stops at the first of these; it never guesses the owner's answer.

## Run folder

A run writes under `<repo>/docs/research/<YYYY-MM-DD>-<slug>/` (below, `<run>`), with these fixed names, so a reviewer can audit or rerun any step:

| File | Step | Holds |
|---|---|---|
| `brief.md`, then `brief-<seat>.md` | 1 | The brief from `brief-template.md` beside this file, split by `scripts/split-brief.sh` into one file per seat: the shared part plus that seat's section only |
| `seeds/<seat>/` | 1 | That seat's seed files (PDFs, data excerpts), copied into the seat's own folder at launch |
| `owner-ideas.md` | 1 | The owner's own ideas, written before any proposal is read |
| `seats.tsv` | 1 | seat, lens, model and effort, seeds, launch command, output file, returned (`pending`, `yes`, or `no: <why>`) |
| `proposals/<seat>.md` | 1 | One file per seat; a Claude seat also leaves `proposals/<seat>.json` with its usage |
| `merged.md` | 2 | From `merged-template.md` beside this file |
| `gap/<idea>/` | 3, 4 | `searches.tsv`, `aliases.tsv`, `rerank.tsv`, `scripts/` and `gap.md` (facets, the paper-by-facet table, gap status, what the claim may and must not say) |
| `notes/<paper>.md` | 4 | One reading note per paper, in the form `READINGS.md` beside this file sets |
| `quotecheck-<reader>.out` | 4 | Each reader's check of its own notes |
| `quotecheck.sh`, `quotecheck.out` | 4 | The run's one check over every `gap.md` and every note they use |
| `decisions.md` | 5 | Each decision put to the owner, its recommended answer, the owner's answer |
| `validation.md`, `validation/` | 6 | Criteria, command, exit code, output, result |

Besides its folder, a run writes only PDFs to `<repo>/papers/` and readings to the shared reading log, `<repo>/docs/research/readings/`, so later runs reuse them.
The project's results and data are read-only for a run.
`scripts/readings-index.py` writes only its own `INDEX.md` and `log.jsonl` there; link that index from a hand-curated `docs/research/INDEX.md`, which the script never touches.

## Steps

### 1. Diverge with blind seats

Run surprise-me's Panel mode (`${CLAUDE_SKILL_DIR}/../surprise-me/SKILL.md`, section "Scale modes"; it is user-invoked, so read the file) with these changes.
Each lens is its own seat on a different model, with different seeds:

| Seat | Lens | Model and effort | Seeds |
|---|---|---|---|
| assets | dormant-assets hunter (Panel mode's step 2) | Opus, xhigh | the project's data paths, opened to the seat with `--add-dir` |
| reframe | reframing hunter | Fable, high; read the `fable-prompting` skill (`.agents/skills/fable-prompting/SKILL.md` in a rendered project) before writing this seat's section | the target venue's call for papers or reviewer guide, plus one paper that venue published on a neighbouring problem |
| codex | adversary | Codex, xhigh | the closest known competitor's PDF |
| analogist | analogist (Panel mode's step-3 analogy move) | Opus, xhigh | one paper from an adjacent field |

The small mode runs assets and codex only.

- Write `<run>/brief.md` from `brief-template.md`, with every seat section last, then run `bash ${CLAUDE_SKILL_DIR}/scripts/split-brief.sh <run>`; it refuses, keeping `brief.md`, on a wrong layout or a seat id used twice.
  Each seat reads only its `brief-<seat>.md` and never sees another seat's seeds.
  Each seat returns ideas, not a ranked table.
- Put each seat's seed files in `<run>/seeds/<seat>/`; its section names them by file name.
- The owner's ideas stay out of every brief; write them to `owner-ideas.md` before any proposal is read.
- Write a `seats.tsv` row per seat, with the exact launch command and returned `pending`, before launch; set returned to `yes` or `no: <why>` when the seat ends.

Each seat runs headless in the lead's background from its own empty folder outside any repository (below, `<dir>`), for example `~/.local/state/research-gap/<date>-<slug>/<seat>/`, with absolute paths throughout.
Make it and copy the seat's seeds in, if it has any: `mkdir -p <dir> && cp <run>/seeds/<seat>/* <dir>/`; `git -C <dir> rev-parse` must fail there.
A Claude seat, Opus here; the Fable seat takes `--model claude-fable-5-1 --effort high`, and the assets seat adds one `--add-dir <path>` per data folder:

```bash
env -C <dir> claude -p --safe-mode --model opus --effort xhigh --tools "Read,Grep,Glob,Bash,WebSearch,WebFetch" --allowedTools "Read,Grep,Glob,WebSearch,WebFetch,Bash(pdftotext *)" --output-format json < <run>/brief-<seat>.md > <run>/proposals/<seat>.json
jq -r .result <run>/proposals/<seat>.json > <run>/proposals/<seat>.md
```

`--safe-mode` loads no CLAUDE.md, rules, auto-memory, hooks, MCP servers, plugin or user skills, or custom agents, and the brief arrives on stdin and the proposal leaves on stdout, so the seat never opens the run folder.
Probed on Claude Code 2.1.312 for Opus 5.5 and Fable 5.1, 28 Oct 2026: a context canary, the session's own init list and a tool run.
`--bare` is blind too but cannot sign in with a subscription, and a worker or escalate subagent inherits the lead's CLAUDE.md and memory, so neither serves as a seat.

The Codex seat reads its brief from its own folder, so its prompt names no path in the run folder: first `cp <run>/brief-codex.md <dir>/`.
Its launch is one bare command, with no pipe, redirect, `cd`, `;` or `<`, and its prompt one line that points at the file (long inline prompts have hung):

```bash
codex exec -s read-only --skip-git-repo-check -C "<dir>" -c model_reasoning_effort=xhigh -o "<run>/proposals/codex.md" "Read brief-codex.md in this folder and follow it as seat codex."
```

The empty folder keeps the repository's AGENTS.md out; Codex still reads the owner's global `~/.codex/AGENTS.md`, so keep project conclusions out of that file.
`-o` is read by the launcher, not the model, and saves only the final message, which is why the brief asks every seat to make its whole document that message.
Record the model from Codex's config (or `-m`) in `seats.tsv`.

Why separate seats: one model resampled stops producing new ideas (about 200 unique from 4000 seeds per topic, 2409.04109), and shared-context debate converges early (2604.18005).
Done when: `seats.tsv` has a row per seat written before launch, every seat has a proposal file or is marked `no: <why>`, and no row still says `pending`.

### 2. Merge with support counts

A fresh Opus `worker` at effort xhigh reads only `proposals/`, `owner-ideas.md`, `seats.tsv` (for N) and `${CLAUDE_SKILL_DIR}/merged-template.md`, and writes `merged.md` in that template's form; it reads no earlier merge or owner notes, which carry the owner's conclusions.

- Each merged idea gets an id (M1, M2, ...), plain words, and support k/N: k seats proposed it as one of their `###` ideas, of N that returned.
  "+k cite" means k more seats raise the same gap inside an idea mapped to another id, by quoting the same passage or reporting the same evidence; name them.
  Name any seat that argues against it.
- An owner idea carries the mark "owner".
  If the brief states it (usually the question itself), every seat was briefed on it and none can support it independently: write its support as "owner; briefed" and list as cites the seats whose ideas take up a part of it.
  An owner idea kept out of the briefs gets k/N like any other, and 0/N is a real count.
- A map from every seat idea to one merged id; an idea that spans two names the second as "other half" and counts as a cite there.
- A table of numbers two seats state differently, with each seat's definition, left unresolved.
- Where the seats disagree, and why.
- The shortlist: every owner idea, every idea with support 2 or more, and at most three single-seat ideas with the cheapest kill, each with one line of reason.
  Cheapest means first in this order: (1) a read or analysis of data already collected, with no hardware time and no money; (2) hardware time with no model spend; (3) runs already planned; (4) a new arm, new runs that spend money.
  Split it in two: claims that would be new against prior work go to step 3, each with 3 to 5 facets and the papers seats named as closest; questions about the project's own data skip step 3 and go to step 6 as candidate checks, since no paper can settle them.
  In the small mode only the owner's ideas go to step 3.

Support counts independent proposers; it is not a score, since models can share a blind spot.
Done when: the map covers every `###` idea in every proposal file, and every gap claim on the shortlist has facets.

### 3. Check each gap (the academic-research workflow)

One `worker` per shortlisted gap claim; each writes only its own `gap/<idea>/`, so they run in parallel.
Each keeps every helper script and scratch file in `gap/<idea>/scripts/`, never in a shared scratch folder: in the trial, parallel workers overwrote each other's helpers there.

1. Write 3 to 5 facets in `gap.md`: the parts a prior paper must all match to close the gap (for example setting, method, measurement, scale, claim).
2. Seed by name first: the papers the seats named as closest, and the readings index (`<repo>/docs/research/readings/INDEX.md`, built by `scripts/readings-index.py`) for papers already read.
   Look each seed up in Semantic Scholar by id or title, or in OpenAlex when Semantic Scholar refuses, to get the id its citation crawl needs; log the lookup as a seed row, then crawl its citations both ways.
   Why, with DistBench as the example: on 10 October 2026, 14 topic searches and a Consensus research thread missed the project's three closest competitors, which a search by name found at rank 1, and the thread declared a gap that did not exist.
3. Then topic and kill queries: at least 10 per idea, at least 2 per index, and at least half phrased as the paper that would make the gap false.
   - Consensus: the `search` tool, for peer-reviewed papers and indexed preprints.
     It returns no paper ids, so key each hit by its normalized title and map it to an arXiv id or DOI in `aliases.tsv`.
   - Semantic Scholar: its unauthenticated limit is shared by every caller on the machine; in the trial single calls answered 429 for over an hour, while one batch call answered at once.
     So look up seeds and crawl citations in one batch call: `curl -s -X POST "https://api.semanticscholar.org/graph/v1/paper/batch?fields=title,year,externalIds,abstract,citations.title,citations.year,citations.externalIds,references.title,references.year,references.externalIds" -H "Content-Type: application/json" -d '{"ids":["arXiv:<id>","DOI:<doi>"]}'`.
     Run single searches (`https://api.semanticscholar.org/graph/v1/paper/search?query=<q>&fields=title,year,externalIds&limit=10`) from one worker at a time; after one failed retry, log the query as a failed row and use OpenAlex instead (`https://api.openalex.org/works?search=<q>`, citations by `filter=cites:<work id>`).
   - Exa: `web_search_exa`, for workshop papers, project pages and repositories.
   - arXiv: `curl -s "https://export.arxiv.org/api/query?search_query=all:%22<two or three words>%22&max_results=10"`, for the newest preprints.
     Encode a phrase's quotes as `%22` and its spaces as `+`, and keep a query to two or three terms: long AND queries return nothing.
     Its feed lags by days, so an empty answer never proves absence; check an id at `https://arxiv.org/abs/<id>`.
   - Citation crawls of papers from the last few months return almost nothing, since the indexes lag; log them, but lean on kill queries for recent work.
   - Append each query and its top 10 hits to `searches.tsv` as it runs: qid, index, kind (seed, topic, kill, citations), query as sent, rank, paper id, title, year; a query with no hits, or one that failed, gets one row with rank 0 and the reason.
   - A research agent's "no prior work" (Consensus `create_thread`, Exa `agent_run`, the `deep-research` workflow) adds hits to the pool; it is never the verdict.
4. Rerank: pool all hits, dedupe by arXiv id or DOI through `aliases.tsv` (one row per alias: the id as logged, the canonical id; for Consensus title keys, publisher DOIs of preprints and mirror pages), mark each facet matched, partial or none from title and abstract, and sort by matches, then partials.
   Write `rerank.tsv`: paper id, title, facets matched, facets partial, the qids that found it, read (yes or no).
   The top 3 to 5, plus any paper two seats named, go to step 4 as the read list in `gap.md`.

Why: gap detection fell from 89.66% to 13.79% without facet reranking (2506.22026), AI Scientist papers had a median of five citations (2502.14297), and retrieval-grounded ideas scored 0.297 against 0.119 on matched later papers' impact (2603.15164).
Done when: `searches.tsv` holds the seed and citation rows plus at least 10 topic and kill queries, at least 2 in each of the four indexes (OpenAlex stands in for Semantic Scholar when its failed rows are logged) and half of them kill queries, every pooled hit is in `rerank.tsv`, and `gap.md` holds the read list.

### 4. Read the closest papers in full

Dedupe the read list across ideas: one paper is read once and serves every idea that lists it.
Give each reader, a `worker`, 2 or 3 related papers (one reader per paper cost too much in the trial), plus every `gap.md` whose read list holds one of them: its note answers every facet of every such gap.
Each reader:

1. Stores each PDF in `<repo>/papers/`, named as `READINGS.md` says.
2. Reads the main text and appendices and writes one note per paper in `<run>/notes/`, by the rules in `READINGS.md` (give the reader its resolved path): each facet answered YES, PARTLY, NO or NOT FOUND (searched the full text, found nothing), with a page-located Verified quote, a fact from the authors' code or pages written as "repo:" with no V mark, and the parts it did not read.
   A quote is Verified only when read in the stored PDF this session.
3. Logs each paper: `python3 ${CLAUDE_SKILL_DIR}/scripts/readings-index.py add --paper <arXiv:id or doi:doi> --note <note path from the repo root> --depth full --reader <reader>` (`add` comes first).
4. Checks its own notes and saves the output: `python3 ${CLAUDE_SKILL_DIR}/scripts/quotecheck.py <its notes> > <run>/quotecheck-<reader>.out`.
   On a SPLIT or MISS it fixes the quote from the PDF, trims it, or relabels the line Inferred, and runs the check again until it exits 0.

Then complete each `gap.md`:

- The paper-by-facet table: one row per paper read, with its arXiv id or DOI in the row's first cell, and one column per facet.
  Each cell holds the verdict and the note's V-marked quote with its page, or its "repo:" fact, or NOT FOUND.
  The quote checker ties a quote to the paper ids on its own line, so a row holds one paper and the table is never turned the other way.
  A cell never says "not in the note": send the reader back.
- The gap status: open, narrowed to the named unmatched facets, or closed by the named paper.
- "The claim may say" and "The claim must not say": facts only, each with its paper and page.

Then the run's one check: write `<run>/quotecheck.sh`, which runs `quotecheck.py` over every `gap/*/gap.md` plus every note they use, with one `--papers <dir>` per PDF folder, and saves the command, its exit code and the output as `quotecheck.out`.
The per-reader outputs are working files; `quotecheck.out` is the run's record.
The checker exits 1 on any SPLIT or MISS, a missing PDF included, and 2 when no Verified quote cites a paper: a zero count proves nothing, so check the paths.
A note from an earlier run that fails here is fixed in place by this run's lead, from the PDF or by relabelling the line Inferred, and the fix is named at the top of `quotecheck.out`; never copy a note to get around a miss.
Last, rebuild the index: `python3 ${CLAUDE_SKILL_DIR}/scripts/readings-index.py`; with no note paths it reads every `docs/research/**/notes/**/*.md`, so name notes kept elsewhere.
It merges a reading logged by DOI into the row its notes cite by arXiv id, and refuses to replace an `INDEX.md` it did not write.
Done when: `quotecheck.out` shows exit 0 with a nonzero checked count over every `gap.md`, and every shortlisted gap claim has a full table, a gap status, and both the may-say and must-not-say lists.

### 5. The owner decides

The lead puts each open decision to the owner as a plain walk-through: what the decision is, how it came up, the facts from the `gap.md` files that bear on it, the options with what each costs and changes, and a recommended answer.
Only decisions the facts cannot settle go to the owner; the lead makes the routine ones and says so.
The decisions are: for each owner idea, the claim wording that survives its competitors; and which idea and which check go to step 6, with the result that would kill the idea.
Record each decision, the recommendation and the owner's answer in `decisions.md`.
If the owner is away, write the decisions and recommendations to `decisions.md` and stop: the run waits here for the owner.
Done when: the owner has named the idea and the check for step 6.

### 6. End in a cheap validation

Pick the cheapest check that can kill the chosen idea, in this order:

1. An executed check over data already collected, such as a read-only script over the project's results.
2. A pilot: the smallest run that can show the effect.
   Anything that spends money or rented hardware waits for the owner's go.
3. A grounded side-by-side, only when neither can run: the idea against its closest competitor, facet by facet, each cell a quote that `quotecheck.py` passes.

Write the success and kill criteria in `validation.md` before running.
Then add the command, its exit code, its output under `validation/`, and the criterion the result met.
The run's outcome is that result, and the owner makes the call from it.
Why not a ranked list or an LLM verdict: after execution, LLM ideas lost more score than expert ideas and the rankings flipped (2506.20803); the best LLM idea judge reached 53.3% balanced accuracy against 56.1% human agreement (2409.04109); and an LLM judge saw no difference (p=0.584) where matched later papers did (2603.15164).
Done when: `validation.md` holds the criteria, the command, its exit code and the result.
