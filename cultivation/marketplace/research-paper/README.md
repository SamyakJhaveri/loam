# research-paper

A Claude Code plugin for writing and reviewing a LaTeX research paper before submission.
It ships review agents whose findings must quote the paper and pass a quote gate, an adjudicator that verifies them, two citation agents, deterministic gate scripts (citations, page and abstract limits, anonymity, acronyms, consistency, figures, claim drift), a section rewrite loop tested on a blind reader, and two review-round workflows.
Each project configures it once, in `paper/tools/`, so no venue, field or path is written into the plugin.

Why it is built this way: `docs/how-the-toolchain-works.md`.

## Setup

1. Add the marketplace once per machine: `claude plugin marketplace add /path/to/loam/cultivation/marketplace`.
2. Enable the plugin for one project; it installs disabled.
   Add `"enabledPlugins": {"research-paper@seed-skills": true}` to the project's `.claude/settings.json` (or enable it with `/plugin`), then start a new session or run `/reload-plugins`.
   Check: the Agent tool lists `research-paper:reviewer-methods` and the nine other agents below.
3. Copy the templates into the project: `mkdir -p paper/tools && cp <plugin>/templates/* paper/tools/`, where `<plugin>` is this folder.
4. Fill in every `FILL IN` block of `paper/tools/contract.md` (venue, review criteria, anonymity, the project's own review rules, reviewer persona), then edit `paper/tools/paper-tools.toml` (paths, build command, limits, macros, term files, and the `[codex]` keys if you use the experimental parts).
   Both templates hold synthetic examples ("ExampleSys", "Example Conference 2030"); replace every one.
5. Check the config: `paper-tool paper_config` prints the resolved config as JSON, and `paper-tool paper_config build.pdf` prints one value.
   It exits 2 and names the problem on an unknown key, a wrong value type or an unreadable file.

`paper-tool` is `bin/paper-tool`.
While the plugin is enabled it is on the `PATH` of Claude's Bash tool; in your own shell, run it by its path or link it onto your `PATH` (it follows symlinks).
`paper-tool` with no argument lists the scripts; `paper-tool <name> [args]` runs `scripts/<name>.py`.
Agents call the same scripts as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py`.

The scripts take the project root from `PAPER_TOOLS_ROOT` if set, else the git top level of the working directory, else the working directory.
They read `PAPER_TOOLS_CONFIG` if set, else `<root>/paper/tools/paper-tools.toml` if it exists, else the defaults alone.
A command-line flag always wins over the config.

## What a project must provide

- A git repository that holds the paper; `section_gate` compares a section with a base commit.
- LaTeX sources: a main file, one `.tex` file per section in a sections folder, an abstract file, a `.bib` file, and a preamble that defines the title macro (`paper.*` keys).
- A build command that writes the PDF and its log (`build.command`, `build.pdf`, `build.log`), and the text dump the seats read, made with `pdftotext <build.pdf> <build.text>`.
- `paper/tools/contract.md` and `paper/tools/paper-tools.toml`, filled in.
- Term files in `paper/tools/`: `banned_terms.txt` (regexes `section_gate` refuses), `acronym_allow.txt` (acronyms a reader of the venue knows), and for a double-anonymous venue `anonymity_terms.txt` (affiliations, labs, hosts, paths, URLs, titles, the system name; author names come from `CITATION.cff`).
  `anonymity_terms.txt` names real people: keep the filled copy in a private repository only.
  Optional: `anonymity_baseline.txt` and `acronym_baseline.txt`, known hits each with the decision that keeps it; with a baseline, a check fails only on a new hit.
- Optional inputs: a `CITATION.cff` whose authors `anonymity_scan` also searches for; literature notes and the paper's own names for `lit_index` and `citation-finder` (`literature.*`); for the adjudicator, a file of decisions already made (`DECISIONS`), known-issue lists (`KEYS`) and the previous round's adjudicated findings (`PRIOR`).
- The placeholder macros below, if the draft holds numbers not yet computed.

Layout assumptions in the scripts: `paper_limits` and `section_gate` find the end of the body at a "REFERENCES" or "BIBLIOGRAPHY" heading in the PDF text, and `section_gate` finds section headings in the IEEE roman-numeral form ("I. INTRODUCTION").
A paper with other heading forms needs those patterns changed.

## Requirements

- Python 3.11 or later; the scripts use only the standard library (`tomllib` needs 3.11).
- `pdftotext` from poppler; `paper_limits` and `anonymity_scan` also use `pdfinfo` and `pdfimages` from the same package.
- A LaTeX build command that writes the PDF, set in `build.command` (default `latexmk -pdf -cd -interaction=nonstopmode -outdir=build paper/main.tex`).
- Network for `cite_check`: `api.crossref.org` and `export.arxiv.org` only.
  `research-paper:claim-ref-alignment` and `research-paper:citation-finder` also fetch from `arxiv.org`, `api.openalex.org`, `api.semanticscholar.org`, `doi.org` and publisher pages; they send identifiers, URLs, cited titles and topic keywords, never the paper's text.
- Optional: the claude.ai Consensus connector (`mcp__claude_ai_Consensus__search`) for `citation-finder`; without it the agent falls back to a web search by title.
- Two user-level agent types that the workflows start; they are not part of this plugin, so define them in `~/.claude/agents/`:
  - `worker`: an execution agent on Opus 5.5 at effort `xhigh`; the full workflow runs its per-seat quote gate on it at effort `low`.
  - `escalate`: a critic on Fable 5.1 at effort `high`; it runs the blind `critic` and `taste` seats and the completeness critic.
- `pytest`, only to run the tests.

## Run order

All commands run from the project root.
Build first: run `build.command`, then `pdftotext <build.pdf> <build.text>` for the text the seats read.
Do not use `-layout`: two-column layout text makes the quote gate reject real quotes (`validate_findings.py` note D1).

While drafting each section:
1. Follow `docs/writing-rules.md`, and for a rewrite the loop in `docs/section-loop.md` (the `section-from-exemplars` skill runs the same loop).
2. After each revision or placeholder fill, run the token check on the before and after copy with an `--authorize` file: `git show HEAD:<file> > "$TMPDIR/before.tex"`, then `paper-tool check_revision_token_conservation pair --source "$TMPDIR/before.tex" --revision <file> --authorize <tsv>`.
   Every changed number, key, fill and strength word needs a row naming a confirmed finding, an author decision, or a `claims:` source.
   Apply `docs/CLAIM_DRIFT_GUARD.md` to each changed sentence; its commands are in that file.
3. Run the `research-paper:citation-finder` agent on the changed sentences.
4. `paper-tool style_lint <file>.tex` on each changed file (the plugin's only em dash check, for the character and for LaTeX's three hyphens); `paper-tool section_gate <file>` runs it with the other section checks.

Before each full review:
1. Cite check: `paper-tool cite_check` (network: `api.crossref.org`, `export.arxiv.org`).
   Exit 1 lists each defect by key and check; a network error counts as a defect, so rerun it rather than waive it.
2. Limits: `paper-tool paper_limits`.
   Exit 1 over `limits.max_pages` body pages, on an appendix heading when `limits.appendix_allowed` is false, or over `limits.max_abstract_words`.
3. Anonymity: `paper-tool anonymity_scan` (it uses `terms.anonymity_baseline` when that file exists).
   Exit 1 on any new hit; notes (third-person self-citations, the system name, raster figures) do not fail.
4. Consistency and acronyms: `paper-tool check_consistency --fail-on-findings` (default files: the abstract and the `paper.sections` files, checked together for cross-section variants) and `paper-tool check_acronyms --scopes body,abstract_en --fail-on-findings` (default input `paper.main_tex`, with the allow list and baseline from the config).
5. Figures: `paper-tool check_tikz_prevention <figures>/*.tex` on the TikZ sources, then `docs/FIGURE_CHECKLIST.md` on each figure.
   Findings go to a note for the author.
6. Review pipeline, at effort `high`: the four seats (`research-paper:reviewer-methods`, `research-paper:reviewer-domain`, `research-paper:reviewer-generalist`, `research-paper:reviewer-devils-advocate`), `research-paper:lean-critic-forensic`, `research-paper:claim-ref-alignment` and `research-paper:citation-finder` (both with `MAIN`, `BIB` and `SECTIONS`; both take any not given from the config), each with `PAPER`, `ROOT` and its own `OUT` (contract section 1).
   Add a blind critic through the `escalate` agent type, lens `critic`, writing `critic.findings.json` beside the other seats' files.
   Then `research-paper:adjudicate-review` with `FINDINGS_DIR` holding the outputs, and `DECISIONS`, `KEYS` and `PRIOR` when the project has them.
   The adjudicator reads only `PAPER`, so it cannot re-check a citation finding's fetched source; those stay as the claim-ref seat reported them.
   Route the result: confirmed text fixes to the writer, items that need new analysis to new tasks, held items to the author one decision at a time.
   The workflows below run this step; `docs/review-round.md` describes them.
7. `research-paper:reader-first-intro` on the abstract, introduction and contribution list.
8. `research-paper:blind-reader` on one extracted section, before the rewrite as a control and after each fix; its scores must not fall below the control's.
   `paper-tool section_gate <file> --no-build` writes the extract and prints its path.
9. Humanizer audit of the changed prose, report only, no rewrite (any humanizer skill you use; this plugin ships none).
10. Rigor pass: check every number and claim against its source before the text leaves the project.

## What ships

### Agents (`agents/`, addressed as `research-paper:<name>`)

| Agent | Model, effort | What it does |
|---|---|---|
| `reviewer-methods` | Opus 5.5, high | A program committee seat that reads hardest for how each result was established: baselines, sampling and nondeterminism, hardware and toolchain, statistics, reproducibility. |
| `reviewer-domain` | Opus 5.5, high | A domain expert seat that reads hardest for novelty, positioning and fair treatment of prior work; searches the web with topic keywords only. |
| `reviewer-generalist` | Opus 5.5, high | A seat from outside the subfield that reads for whether the claims hold, what is quietly assumed, and whether a non-specialist can follow. |
| `reviewer-devils-advocate` | Opus 5.5, high | Finds the most vulnerable claims, the logic gaps and the strongest counter-argument; only challenges, never scores. |
| `lean-critic-forensic` | Opus 5.5, high | A consistency critic (placeholder wiring, dangling labels, contradictions between sections, dead promises, terminology drift) plus a six-layer audit of the paper's own numbers. |
| `claim-ref-alignment` | Opus 5.5, high | Fetches each cited source by its identifier and labels every citing sentence supported, partly supported, not supported or not checked. |
| `citation-finder` | Opus 5.5, high | Lists factual sentences with no `\cite`, searches the saved literature (`lit_index`), then Consensus and a title search, and proposes keys and BibTeX; never edits the paper. |
| `adjudicate-review` | Opus 5.5, high | Validates the seat files, merges duplicates, verifies each finding against `PAPER` (confirmed, refuted, downgraded, held), checks each suggested fix, and tiers the survivors (must-fix, should-fix, optional). |
| `reader-first-intro` | Opus 5.5, high | Reviews the abstract, introduction and contribution list for contribution attribution, the reader's argument map, and plain meaning before internal names. |
| `blind-reader` | Fable 5.1, high | A reader with no project context reads one extracted section once, restates it, and reports terms used before they are defined, the hardest sentences, and three scores. |

### Scripts (`scripts/`, run as `paper-tool <name>`)

- `paper_config`: loads `paper/tools/paper-tools.toml`, fills the defaults, and prints the resolved config or one key.
- `validate_findings`: the quote gate; checks findings against `finding_schema.json` (beside it), fills ids (`--fill-ids`), and confirms each quote at its line (`--check-quotes --require-quotes`).
- `section_gate`: one command for the mechanical checks on a rewritten section against a base commit (no number, `\cite` or `\ref` lost, no banned term, style lint, build, page limits, where the references start, the section's pages) and the extract for `blind-reader`.
- `skim_extract`: the four extracts a skimming reader sees (title and abstract; last introduction paragraph and the displays; first introduction paragraph and first and last discussion paragraphs; the first sentence of every paragraph), one per pass of the skim-reader test (`docs/section-loop.md` section 4).
- `lit_index`: an index of the `.bib` file and the literature notes, with search; flags the paper's own names as self-citations.
- `cite_check`: bib fields, duplicate keys, cited keys against the bib, a DOI or URL per entry, full author lists, arXiv-only entries, and Crossref and arXiv resolution with title and year compared; fails closed.
- `paper_limits`: body pages with references excluded, appendix headings, and abstract words.
- `anonymity_scan`: names, affiliations, hosts, paths, URLs, titles and self-revealing phrases in the PDF text, the PDF metadata and the figure files.
- `check_acronyms`: acronyms used undefined, defined after first use, or defined twice, in LaTeX input.
- `check_consistency`: term, numeric precision and unit spelling variants across files.
- `check_tikz_prevention`: a read-only check of two TikZ rules (scaled coordinates without scaled text; an edge label with no placement).
- `check_revision_token_conservation`: numbers, `\cite` keys and `\ref` targets kept between two versions of a section, with placeholder fills listed.
- `style_lint`: deterministic style checks for research prose; `--list` shows the rules.

### Docs (`docs/`)

- `writing-rules.md`: the paper-writing rules, grouped (before drafting, per section, numbers and claims, citations, review rounds, anonymity), each with its reason.
- `section-loop.md`: the loop for rewriting any section: blind read first, exemplar papers read in full, edit to the findings, `section_gate`, blind read again.
- `review-round.md`: running a review round with the two workflows: what to prepare, the seats, the quote gate, the adjudicator, agent counts, inputs and outputs.
- `CLAIM_DRIFT_GUARD.md`: the claim-strength ladder for each revised sentence, and the token-check commands with the `--authorize` file.
- `FIGURE_CHECKLIST.md`: yes-or-no items for each figure and caption.
- `subagent-prompt-guide.md`: sourced rules for writing subagent prompts, model and effort per role, and a prompt skeleton.
- `how-the-toolchain-works.md`: why every finding passes a quote gate, the flow from seats to gate to adjudicator, and the design decisions.

### Templates (`templates/`, copied to `paper/tools/`)

- `contract.md`: the review contract every seat reads first (inputs, venue, rules, evidence, severity, output, stop condition, persona), with `FILL IN` blocks.
- `paper-tools.toml`: every config key with a one-line comment and synthetic values.
- `banned_terms.txt`: the format of the banned-regex list, for the project's own rulings.
- `anonymity_terms.txt`: the format of the anonymity terms file, with synthetic entries to replace.
- `acronym_allow.txt`: the format of the acronym allow list, with a few neutral examples.
- `next-session-prompt.md`: the five headings of a handoff prompt for the next session.
- `exemplar_manifest.tsv`: the exemplar list `codex_seat` reads, with one synthetic entry; for the experimental parts, copy it to `codex.manifest` (default `paper/exemplars/manifest.tsv`), not to `paper/tools/`.

### Workflows (`workflows/`, run as `/research-paper:<name>` with the `name` in each file's `meta` block)

- `attack_round_full.js` (`attack-round-full`): a full review round: ten review seats in parallel, a quote gate per seat with one repair, the adjudicator, then a completeness critic.
- `attack_round_seats.js` (`attack-round-seats`): the ten review seats only; the lead then runs the quote gate and the adjudicator by hand.

Both take their inputs as a JSON `args` object (`paper`, `out`, `keys`, `decisions`, `prior`, all optional) and name every agent type in a constant block at the top.
The full round needs the user-level `worker` and `escalate` agent types, the seats-only round `escalate`.
State the agent count before launching: 22 to 38 agents for the full round, 10 for the seats-only round.
`exemplar_advisor.js` is experimental (below).

### Skill (`skills/`)

- `section-from-exemplars`: the section rewrite loop as a model-invoked skill, for a request to write, rewrite or tighten a section, abstract or introduction.

## Placeholder convention

A number not yet computed is written `\tofill{Tn}` in the text and `\tofillcell{Tn}` in a table cell, where `Tn` is a placeholder id such as `T23`; the built text prints it as `[TOFILL Tn]`.
The project defines the two macros, for example `\newcommand{\tofill}[1]{[TOFILL #1]}`.
The seats do not report a pending number as missing, and `check_revision_token_conservation` records a placeholder replaced by a number as a fill, not a loss.
Before submission, `grep -c '\[TOFILL ' <build.text>` must print 0.

## Experimental

Three parts are experimental: a cross-model seat runner (`scripts/codex_seat.py`), its prompt files (`prompts/`), and an exemplar-advisor workflow (`workflows/exemplar_advisor.js`, which also uses the user-level `scout` and `escalate` agent types; `scripts/build_suggestions.py` turns its journal into a suggestions file for each section).
They are covered only by offline tests of `codex_seat.py` (`tests/test_codex_seat.py`, with no call to Codex, a model or the network), and they need the Codex plugin for Claude Code.
They read four `[codex]` keys of `paper-tools.toml`:
- `codex.corpus_dir` (default `paper/exemplars`): the exemplar papers as `pdftotext` output, one `<id>.txt` per paper.
- `codex.manifest` (default `paper/exemplars/manifest.tsv`): the exemplar list, tab-separated id, title and URL (`templates/exemplar_manifest.tsv`).
- `codex.companion` (default `""`): the path of `codex-companion.mjs`; `""` finds the newest installed Codex plugin.
- `codex.model`: the Codex model `codex_seat` runs when `--model` is not given; `paper-tool paper_config codex.model` prints the default.

## Tests

The tests are a manual gate, not run by Loam's CI: Loam's `bin/check` lints these Python files with ruff but does not run the tests.
Run them from this folder; each command exits 0 when every case passes:

```
python3 -m pytest tests -q -p no:cacheprovider
bash tests/run_selftest.sh
```

## Licences

This plugin is a mix of licences.
Files with no upstream notice are under the Loam repository's MIT licence (`LICENSE` at the repository root).
The files below carry third-party material under the terms their own notices state, and each notice is kept in its file exactly as written.
The CC BY-NC 4.0 material is licensed for non-commercial use only.
Material from an upstream with no licence file is adapted with credit and not relicensed.

| File | Upstream source (commit) | Licence, as the file states it |
|---|---|---|
| `scripts/check_acronyms.py` | `imbad0202/academic-research-skills` (e79085d), `scripts/check_acronyms.py` | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu, non-commercial research use only |
| `scripts/check_consistency.py` | `yuan1z0825/nature-skills` (8488081), `skills/nature-shared/scripts/check_consistency.py` | Apache License 2.0; no NOTICE file and no named copyright holder upstream |
| `scripts/check_tikz_prevention.py` | `pedrohcgs/claude-code-my-workflow` (ae72617), `scripts/check-tikz-prevention.py` | MIT, Copyright (c) 2026 Pedro H. C. Sant'Anna; licence text in the file |
| `scripts/check_revision_token_conservation.py` | `imbad0202/academic-research-skills` (e79085d), `scripts/check_revision_token_conservation.py` without its patch mode | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu, non-commercial research use only |
| `scripts/cite_check.py` | [A] `K-Dense-AI/scientific-agent-skills` (065b734), `skills/citation-management/scripts/`, logic read and rewritten; [B] `imbad0202/academic-research-skills` (e79085d), `scripts/retraction_status.py` lines 152-229, the retraction verdict rule | [A] MIT, Copyright (c) 2025 K-Dense Inc.; licence text in the file. [B] CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu |
| `scripts/validate_findings.py` | `pedrohcgs/claude-code-my-workflow` (ae72617), `scripts/validate-findings.py` | MIT, Copyright (c) 2026 Pedro H. C. Sant'Anna; licence text in the file |
| `scripts/finding_schema.json` | `pedrohcgs/claude-code-my-workflow` (ae72617), `.claude/references/finding-schema.json` | MIT, Pedro H. C. Sant'Anna |
| `scripts/anonymity_scan.py` | `sohan-shingade/paper-reviewer` (6a5c484), `scripts/extract_pdf.sh` lines 38 and 44; idea only, no text copied | no licence upstream |
| `docs/CLAIM_DRIFT_GUARD.md` | `imbad0202/academic-research-skills` (e79085d), `shared/references/claim_strength_ladder.md` lines 19-58 and the guard block of `evals/heldout/revision_claim_drift/runs/2026-08-07/RUN_PLAN.md` lines 72-95 | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu, non-commercial research use only |
| `docs/FIGURE_CHECKLIST.md` | `llmsresearch/paperbanana` (87e01fd); `imbad0202/academic-research-skills` (e79085d), `academic-pipeline/agents/integrity_verification_agent.md`, items restated with no text copied; `pedrohcgs/claude-code-my-workflow` (ae72617), the TikZ check | paperbanana: MIT, Copyright (c) 2025 PaperBanana Contributors. academic-research-skills: CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu. claude-code-my-workflow: MIT |
| `docs/writing-rules.md`, section-by-section rules | `Orchestra-Research/AI-Research-SKILLs` (773a529); `yuan1z0825/nature-skills` (8488081); `Master-cai/Research-Paper-Writing-Skills` (77e7c2c); rules restated, short labels only copied | AI-Research-SKILLs: MIT, Copyright (c) 2025 Claude AI Research Skills Contributors. nature-skills: Apache License 2.0, no named copyright holder. Research-Paper-Writing-Skills: MIT, Copyright (c) 2026 Master-cai |
| `tests/test_check_revision_token_conservation.py` | `imbad0202/academic-research-skills` (e79085d), `scripts/test_check_revision_token_conservation.py` without its patch-mode tests | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu, non-commercial research use only |
| `tests/test_check_consistency.py` | `yuan1z0825/nature-skills` (8488081), `skills/nature-shared/tests/test_check_consistency.py` lines 1-59 | Apache License 2.0 |
| `agents/adjudicate-review.md` | `pedrohcgs/claude-code-my-workflow` (ae72617), the `adjudicate-review` skill, two reference files and lines 56 and 70 of the `seven-pass-review` skill; `sohan-shingade/paper-reviewer` (6a5c484), `.claude/agents/handling-editor.md` lines 35-100, the merge and conflict rules; `yuan1z0825/nature-skills` (8488081), `forensic-consistency-audit.md`, the isolation rule | claude-code-my-workflow: MIT, Copyright (c) 2026 Pedro H. C. Sant'Anna. paper-reviewer: no licence file, adapted with credit, not relicensed. nature-skills: Apache License 2.0 |
| `agents/blind-reader.md` | none | the repository licence |
| `agents/citation-finder.md` | `imbad0202/academic-research-skills` (e79085d), `academic-pipeline/agents/claim_ref_alignment_audit_agent.md` lines 321-328, the uncited-assertion rule, carried from `claim-ref-alignment` | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu; non-commercial use only for those parts |
| `agents/claim-ref-alignment.md` | `imbad0202/academic-research-skills` (e79085d), `academic-pipeline/agents/claim_ref_alignment_audit_agent.md` and `academic-pipeline/agents/integrity_verification_agent.md` | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu |
| `agents/lean-critic-forensic.md` | the `lean-critic` agent of this marketplace's `sam-cc-setup` plugin (v0.9.4); `yuan1z0825/nature-skills` (8488081), `forensic-consistency-audit.md` and `technical-concern-taxonomy.md` | lean-critic: MIT License. nature-skills: Apache License 2.0 |
| `agents/reader-first-intro.md` | `ysyecust/write-reader-first-papers` (b184250), `skills/write-reader-first-papers/SKILL.md` and `references/style-rules.md` | MIT License |
| `agents/reviewer-devils-advocate.md` | `imbad0202/academic-research-skills` (e79085d), `academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md`; checks F2 to F4 from `academic-pipeline/references/ai_research_failure_modes.md` | CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu; non-commercial use only |
| `agents/reviewer-domain.md` | `sohan-shingade/paper-reviewer` (6a5c484), `.claude/agents/reviewer-domain.md` and the reviewer form prompts | no licence file, adapted with credit, not relicensed |
| `agents/reviewer-generalist.md` | `sohan-shingade/paper-reviewer` (6a5c484), `.claude/agents/reviewer-generalist.md` and the reviewer form prompts | no licence file, adapted with credit, not relicensed |
| `agents/reviewer-methods.md` | `sohan-shingade/paper-reviewer` (6a5c484), `.claude/agents/reviewer-methods.md` and the reviewer form prompts; `Orchestra-Research/AI-Research-SKILLs` (773a529), the named checks; `imbad0202/academic-research-skills` (e79085d), check F1 | paper-reviewer: no licence file, adapted with credit, not relicensed. AI-Research-SKILLs: MIT License. academic-research-skills: CC BY-NC 4.0, Copyright (c) 2026 Cheng-I Wu |
