# Writing a section from exemplar papers

A loop any session can run on any section of a paper.
It has three parts: a reader with no context says what the current text fails to carry, exemplar papers read in full supply the moves, and one command checks everything a script can check.
The `section-from-exemplars` skill is the short form of this page.

## 1. The loop

Each step ends on a condition; move on only when it holds.

1. **Read first.** Extract the section as it stands (`paper-tool section_gate <file> --no-build` prints the extract path) and run the `research-paper:blind-reader` agent on it with the add-on for its section type (section 3).
   Done when you hold its restatement, its scores, and its list of terms and numbers it could not trace.
   This control read is the diagnosis and the baseline.
2. **Exemplars.** If the project has a move table for this section type (saved by an earlier run of this step), use it.
   If it has none, read the papers (section 2), one read-only agent per paper, and save the table in the project before writing.
   Done when every paper on the list is reported read in full with the URL fetched, or named as unreachable.
3. **Edit to the findings.** Start from the text on disk.
   Change what the reader could not restate, apply the moves, and keep every fact, number, `\cite` and caveat of the previous version.
   Verify any number you add against its results file before it enters the text.
   Done when each control finding is fixed in the text or listed as the owner's to decide.
4. **Gate.** `paper-tool section_gate paper/sections/<file>.tex`.
   Done at exit 0, with the references no later on the page than they were at the base commit (the `slack` line).
5. **Blind read again.** Run `research-paper:blind-reader` on the new extract, fix what it could not restate, rerun the gate, and read once more.
   Done when the restatement is complete and correct and no score is below the control's.
   A one-point move between two reads is noise; a change in what the reader restates is the evidence.
6. **Show the owner.** The changes as before and after lines, the page range from the gate, the restatements, and every finding left for the owner.
   Commit only on the owner's go.

One section, one file, one commit.
Open owner decisions stay as they are in the text and go to the owner as decisions.

## 2. Reading the papers

"Refer to a paper" means fetch and read the paper.
Pick the exemplars in three rings: the papers this paper cites (the field's register and its reviewers' expectations); strong papers of the same kind outside the field; two recent accepted papers at the target venue.

One reader per paper, a read-only agent at high effort.
A read-only agent's final report reaches the lead cut at about 4,000 characters, and at 16,000 for all reports that arrive together, so the brief asks for two parts and the lead collects part 2 by `SendMessage`, three or four agents per turn.
Messages an agent sends to the lead with its own `SendMessage` tool are not cut, so the faster brief asks for the report as three such messages of under 3,000 characters each and a one-line final report.

> Read ONE paper in full, every section, not the abstract: TITLE (VENUE; arXiv ID or DOI).
> Fetch the PDF or HTML; say which URL fetched.
> If a fetch returns a summary, fetch again for verbatim text.
> Confirm you read the whole paper by giving its section list with approximate word counts.
> Report with verbatim quotes (section named) for every claim, in two parts of under 3,300 characters each.
> Part 1 now: QUESTIONS A.
> I will ask for part 2: QUESTIONS B, then Read: URLs and Risks:.
> Do not message the lead; your final report is your only output.

Questions by section type:

| Section type | Part 1 | Part 2 |
|---|---|---|
| Method | subsection titles and the reader question each answers; how three mechanisms are introduced (purpose first or rule first); how thresholds are justified | where caveats sit and their share; three verbatim paragraphs with sentence length and run-in labels; what to copy and avoid |
| Results, discussion | how the first results paragraph opens; how the headline number is anchored (baseline, denominator, unit, interval); captions as claim or label and how prose points to a table | where robustness sits and its share; where limitations sit and their share, two quotes; how the discussion opens and closes; what to copy and avoid |
| Abstract, introduction, related work | the first three sentences; where the gap and the contribution are stated; how contributions are listed and tied to sections | how prior work is grouped and what each group is said to lack; how numbers are used in the abstract; what to copy and avoid |

List what was read by title and URL in the report to the owner.

## 3. The blind reader

The `research-paper:blind-reader` agent reads one extract once and returns a restatement, the terms left open, the hardest sentences with rewrites, flow and errors, and three scores.
Give it the extract path, the venue and field, the macro-to-text map (`paper.macros` in `paper/tools/paper-tools.toml`) and the add-on for the section type, nothing else:

| Section type | RESTATE | Score (b) |
|---|---|---|
| Method | what the system is and how it works | could you re-implement it from this text |
| Results | what was found and on what evidence | could you state exactly which number supports each claim |
| Discussion | what the results mean, what a positive result does and does not establish, what each limitation costs | could you state what each limitation leaves unmeasured and what would fix it |
| Abstract, introduction | the problem, the gap, what was built, the headline result | could you list the contributions and the evidence for each |
| Related work | how the prior work is grouped, what each group is said to lack, what this paper does that the others do not | could you state, for each prior work named, what it does and what this paper adds over it |
| Corpus, curation | what the corpus is, where it comes from, how it was selected, what being in it does and does not establish | could you rebuild the selection and reconcile every count with the others |
| Experimental setup | which systems were run, how each result was produced and judged, on what platform, how results are counted and compared | could you re-run the experiment and recompute the metrics |

Ask for one message under 3,800 characters with RESTATE and VERDICT first.
Re-read every quoted line before acting: a term it calls undefined may be defined in a section it did not see, and a contradiction it reports between two numbers is worth checking against the data.

## 4. The skim-reader test

Sections 1 to 3 test one section on a reader who reads all of it.
This test asks what a reader takes away who reads only the places most readers read.
The reading order is that of "How I read a scientific paper in 20 minutes" (predirections.substack.com/p/how-i-read-a-scientific-paper-in) and Brian McGill's "The 5 pivotal paragraphs in a paper" (dynamicecology.wordpress.com, 2016-02-24):

1. The title and the abstract: what is the question and why care, in one sentence, or the reader stops.
2. The last paragraph of the introduction, then every figure and table with its caption, not the results text.
3. The first paragraph of the introduction, then the first and the last paragraph of the discussion.
4. The first sentence of every paragraph.

What each place must do:

| Place | Its job |
|---|---|
| Abstract | the problem, what was built, the main findings each with its number, what they mean; a finding the paper opens on has a count |
| Last introduction paragraph | what the paper set out to do; here the contribution list |
| Caption | its first sentence states the finding the display shows |
| First introduction paragraph | the big open question |
| First discussion paragraph | the main findings in one place, one sentence each, no caveats |
| Last discussion paragraph | what the findings mean beyond this paper |
| First sentence of a paragraph | the paragraph's point, readable without the paragraph before it; a run-in header stays a phrase |

The run:

1. Fix the message the paper must leave, in one sentence, with the owner.
2. `paper-tool skim_extract <dir>/control` writes `pass1.txt` to `pass4.txt` from the working tree.
3. One fresh `research-paper:blind-reader` per pass, four in one turn, each told to ignore its standard output format, to use nothing but the files named, and to reply in one message under 3,300 characters:
   - pass 1 reads `pass1.txt`: the question in one sentence; a restatement with every number retained; the one finding it would repeat; stop or continue; the two sentences that carried most and the two that cost most; what it would cite the paper for.
   - pass 2 reads `pass1.txt` and `pass2.txt`: the objectives; for each display the finding it shows, whether the caption states it or only labels the display, and whether caption and display alone give it; the main result from the displays; which parts of the abstract's story have no display; numbers it could not rebuild.
   - pass 3 reads `pass1.txt` to `pass3.txt`: the whole story in six sentences; each sentence of the first discussion paragraph as finding, caveat or method detail; whether the last paragraph says what the findings mean; conflicts between the pivotal paragraphs and the displays; what it would cite the paper for.
   - pass 4 reads `pass4.txt` only: the argument rebuilt from first sentences; per section how many state a point and how many only set up; the eight weakest; first sentences that depend on the paragraph before.
4. Edit to the findings under the loop of section 1 (gate, page, every number kept or its cut named to the owner).
5. Extract again into `<dir>/after` and run four new readers.
   Done when each reader's "what I would cite it for" is the message of step 1.
   The change in that sentence is the evidence; counts of point and setup sentences from one reader are noisy.

Traps: a blind reader can see the project's memory index, so tell it to ignore it; a finding-first caption or a longer first sentence costs a line the page may not have.
