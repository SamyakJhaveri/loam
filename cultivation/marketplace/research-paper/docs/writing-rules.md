# Paper-writing rules

Rules for writing any research paper with this plugin.
Each rule is followed by the reason for it.
The section-by-section rules restate published writing guides and carry a source tag; the sources are listed at the end.
"The author" below is the person who owns the paper and its decisions; "the writer" is whoever drafts, human or agent.
Commands and agents are described in `../README.md`.

## Before drafting

1. Attack the current draft on the venue's review criteria before drafting anything, and get a narrative strategy approved first: the one-sentence claim, the contributions mapped to the criteria, what each section must prove, what is cut, and the open decisions.
   The paper is judged on those criteria, so the story has to be chosen against them before the prose is written.
2. Review only a draft written after the latest results and decisions; if the text predates them, draft first and review after.
   A review of a stale draft grades text that is about to change, so most findings land on dead text.
3. When a written procedure's order of steps no longer fits the current state, flag the mismatch before following it.
   Following the order literally can spend a whole review round on the wrong text.
4. Read every exemplar paper in full, from its own PDF or source, one read-only agent per paper; never use an excerpt, a summary, an abstract or memory of the paper.
   A summary keeps neither the wording nor the layout that advice on register and structure is drawn from, so such advice cannot be traced to the paper.
5. Pick exemplars in three rings: papers this paper cites, strong papers of the same kind outside the field, and two recent accepted papers at the target venue.
   List each paper read by title and source, and say "not read" plainly for any paper not opened, so the advice can be traced to real papers.
6. Revise the existing draft in place, starting from the author's text on disk, not from a blank page.
   A rewrite from scratch loses the author's structure and register.
7. Never answer an open author decision yourself: draft only the parts no open decision touches, leave a `% OWNER:` comment that names the decision, and put it to the author as one question (fact, options, risk, recommendation).
   A guessed answer becomes text the author has to find and undo.

## Per section

### The loop

1. Rewrite a section only through the loop in `section-loop.md` (or the `section-from-exemplars` skill): blind read of the current text, exemplar moves, edit to the findings, `paper-tool section_gate`, blind read again.
   The first blind read, the control, finds most of what the later reads find before a word changes, so the rewrite gets smaller.
2. Give `research-paper:blind-reader` the extracted section, the venue and field, and the macro map; nothing else: no rules, no history, no repository access.
   The missing context is the point; it reads the way a first-time reader does.
3. A section is done when the blind reader's restatement is complete and correct and no score is below the control's.
   Scores from one reader are noisy; a change in what the reader can restate is the evidence.
4. Re-read every line a reader or reviewer quotes before acting on it.
   Some "never defined" findings are defined in text the reader did not see, and a reported number mismatch is worth checking against the data.
5. Keep every number, `\cite` and caveat of the previous version through a rewrite, and verify any number you add against its results file before it enters the text.
   A rewrite for readability must not change what the paper claims.
6. One section, one file, one commit; no draft or alternative copies beside the section file.
   Git history is the backup, and a second copy drifts from the first.

### Structure for the skimming reader

7. Put the strongest findings where a skimming reader looks: the title and abstract; the last introduction paragraph and every figure with its caption; the first introduction paragraph and the first and last discussion paragraphs; the first sentence of every paragraph.
   Most readers, and many reviewers, stop after these places, so a finding that sits only mid-paragraph is not received.
8. In results and discussion, the first sentence of each paragraph states a finding and the rest gives its context and qualification.
   Read alone, the first sentences should rebuild the argument.
9. Test the structure with `paper-tool skim_extract` and the skim-reader test of `section-loop.md` section 4: one fresh read-only agent per pass, given only that pass's files, then compare each restatement with the message the paper must deliver.
10. A run-in paragraph header names what the paragraph holds, as a phrase, never a full sentence; do not add new labels or split paragraphs as a fix.
    A header that says nothing invites the reader to skip, and each extra label is one more thing to track.

### Register

11. "Easier to read" means fewer bookkeeping numbers and less internal process, not simpler sentences: keep the technical vocabulary and the sentence shape, and never explain a term the field already knows.
    Short explanatory sentences talk down to an expert reader and lose the precision that the field's terms carry.
12. Commit the author's version before replacing a whole section.
    The author can then compare and restore it.
13. Present tense for what the system is, past tense for what was run; a result "shows", never "proves".
    The tense tells the reader which statements are design and which are measurement, and no finite experiment proves a general claim.

### Section by section

Abstract:
14. The abstract carries numbers only for the most important findings; supporting counts and the "how" go to the introduction and the body.
    An abstract that reads as a chain of counts loses its argument.
15. Each claim in the abstract names the property achieved and the measurement that shows it [AIRS-WP:226-227].
    A claim with neither is a slogan.
16. The abstract names the gaps and the answers in the same words as the introduction's contribution list [AIRS-WP:53-55], so the reader can match them.
17. A coined term in the abstract comes with a one-clause mechanism, or a plain phrase replaces it [RPW-I:376-380].
    An undefined coinage stops a first-time reader.

Introduction:
18. State the gaps of prior work, each with the evidence that shows it, before the paragraph that presents this paper's answers; no design detail comes before the gaps [AIRS-WP:7-18,223-224].
    The reader needs the problem before a solution can matter.
19. The prior-work paragraphs form one chain: the general difficulty, then each group of prior work with its limitation and the technical reason for it, ending on the limitation that is exactly this paper's gap [RPW-I:184-201].
20. Each contribution names the gap it answers, its concrete mechanism and the section that holds it; nothing enters the contribution list without a gap [AIRS-WP:38-44,220-221; RPW-I:372-380].
    A contribution with no gap reads as a feature list.
21. A reader can point to the paragraph that answers each review aspect the call for papers names, such as motivation, the limits of the state of the art, and the contributions.
    Reviewers score those aspects and look for them.

Related work:
22. Each paragraph that names prior work says how this paper differs from it; no paragraph only lists papers [AIRS-SB:335].
    With four or more close prior systems, add a comparison table with one row per system and one column per gap [AIRS-SB:336-346].
23. Marks in tables and figures read in greyscale: text or distinct symbols, never colour alone.
    Many readers print in greyscale or cannot tell colours apart, and some venues require accessible figures.

Design:
24. Each design subsection opens by naming the gap it answers, and each major design decision names one alternative and why it was rejected [AIRS-WP:20-24,229-230].
    When a table is shorter than the prose, the alternatives go in one table with the columns Decision, Choice, Alternative, Why not [AIRS-SB:211-221].
25. Cut provenance and implementation detail that does not advance the central claim [NS:46], but keep any detail needed to reproduce a result or judge its integrity, even when the page limit binds [NS:170-172].
26. Beside each metric or acceptance rule, one sentence says what meeting it shows and what it leaves open.
    Without it a reader takes the metric to mean more than it measures.

Evaluation:
27. Before drafting, keep a result-allocation table outside the paper: each result, its job in this paper (core finding, necessary support, qualification, robustness, heterogeneity, provenance detail, alternative inference, edge case) and its place, main text or cut [NS:35-52].
    A result is placed by its job in the argument, not by the name of its analysis.
28. Order the results by the shortest evidence chain: the central observation, the decisive comparison, the main uncertainty, the boundary that changes the conclusion [NS:54-65].
    The order in which the analyses were run is not an argument.
29. A robustness result that leaves the conclusion unchanged gets at most one sentence [NS:44,47]; a qualification that changes how a claim reads sits beside that claim [NS:43,48].
30. Tables carry one message each, with the caption above, stating the claim first and then setting and notation; booktabs rules only, no vertical or double rules; headers give metric direction and units; one precision per column; only best or target cells are highlighted, by bold or a symbol [RPW-E:63-88].
31. Every rate carries its denominator.
    A rate without its n cannot be judged.

Discussion and conclusion:
32. Limitations get their own labelled paragraph, naming each conclusion that rests on an assumption; evidence that contradicts or changes a conclusion stays in the body and is never cut for space [NS:173-175].
33. A sentence whose main job is to answer an expected objection goes to the rebuttal notes, unless the objection bears on the central inference [NS:78-86].
34. The conclusion adds no new result, repeats no sentence of the abstract or introduction without adding a boundary or an interpretation, and names the gaps with the introduction's labels [NS:141-148; AIRS-WP:7-18,32].

Before a section goes to review:
35. Run the necessity test on each changed paragraph: if the reader would still understand the central claim and have its evidence without it, delete it, or move it to the rebuttal notes when a reviewer may ask; when one sentence of it matters, keep that sentence [NS:117-129].
36. Each added sentence has a named job, and the sentence that already did that job is replaced or merged [NS:67-76].
    Otherwise every revision makes the paper longer and more repetitive.

## Numbers and claims

1. Every sentence states what the current code and results do: check it against the code or results file it describes, not against an earlier draft.
   A smoother sentence that says more than the code does is the first thing a reviewer attacks.
2. When a nicer wording and a true wording differ, write the true one, and do not offer the author a choice between them.
   When a reviewer's suggested rewrite would state something the code does not do, keep the true statement and fix its clarity another way.
3. State results as percentages with the systems named ("41.2% for SystemA and 37.5% for SystemB"), never as "about three in five".
   A vague fraction hides both the number and the system it belongs to.
4. No claim gets stronger without new evidence in the same edit: apply `CLAIM_DRIFT_GUARD.md` to each changed sentence, and run `paper-tool check_revision_token_conservation` after every revision and every placeholder fill.
   The check catches a lost number, citation or reference that a reader would miss.
5. A placeholder `\tofill{Tn}` stands for one quantity; no text gives it a stand-in value or "about N".
   A stand-in value survives into the submission more often than anyone expects.
6. When a claim appears in several places (abstract, introduction, contribution list), change all of them in the same edit or none.
   Otherwise the paper contradicts itself.
7. Measure page fit with a forced build and read where the references start; never estimate it from word counts.
   Line breaking and float placement decide where a page ends, and no word count models them; a cut can move a float and leave the page no shorter.
8. When an edit pushes the paper past its page limit, report the overflow as the build measured it and leave the choice of what to cut to the author; do not trim other text to make room.
   Text the writer trims on its own was text the author had decided to keep.

## Citations

1. A key enters the bibliography only after its DOI, arXiv id or URL was fetched in the session and the fetched title, authors and year match the entry.
   Some venues make an inaccurate or invented reference grounds for rejection.
2. Each `\cite` sits on the sentence whose claim it supports: `research-paper:claim-ref-alignment` labels every citing sentence, and any label below "supported" means move the citation, replace it, or weaken the sentence.
3. `research-paper:citation-finder` covers factual sentences that have no citation; it proposes keys and entries and never edits the paper.
4. `paper-tool cite_check` fails closed on a network error: rerun it, never waive it.
5. Only identifiers, URLs, cited titles and topic keywords leave the machine; never send the paper's sentences to an outside service.
   Manuscript text sent to a search service is out of the author's control.
6. AI-use disclosure follows the venue's rule exactly, for example a citation of the AI system in each section that holds AI-generated text; check the call for papers before adding or removing one.
   Venues differ, and an author may rule differently for each venue.

## Review rounds

1. The writer never reviews its own draft: review seats, the reader-first pass and blind readers run as separate agents.
   A model that checks text against reasons it wrote itself finds what it expects.
2. Nothing a review agent says counts until the quote gate has found its quote in the paper and the adjudicator has verified it (`how-the-toolchain-works.md`).
3. Add a blind critic on another model through the `escalate` agent type: it gets the built text and the venue's criteria, never the writer's reasoning, and it never edits the paper.
4. After drafting, run a humanizer audit on the changed prose, report only, and let the writer apply what fits.
   A voice pass never changes a number, `\cite` or `\ref`; run the token check after it.

## Anonymity (double-anonymous venues)

1. Copying sentences verbatim from public text, such as a thesis chapter or a workshop version, can make the submission findable by a text search; flag each such reuse to the author, whose call it is.
2. Self-citations are written in the third person, named by system with a numeric citation, and not clustered together.
   A self-citation in the first person names the authors.
3. The title, abstract and body name no URL, host, lab, cluster or repository of the authors; `paper-tool anonymity_scan` checks the PDF text, its metadata and the figure files.
4. The filled anonymity terms file lists real names: keep it in a private repository only.

## Sources

Rules without a tag are this plugin's own.
The tagged rules restate passages of three published guides as plain rules; only short labels are copied (the NS result classes, the AIRS table header).
Line numbers refer to each file at the commit named below; they were not re-checked against those files for this page.

- AIRS: https://github.com/Orchestra-Research/AI-Research-SKILLs at 773a52944ba4747a18bd4ae9ade53fff041adcbc, MIT license, Copyright (c) 2025 Claude AI Research Skills Contributors.
  AIRS-WP is `20-ml-paper-writing/systems-paper-writing/references/writing-patterns.md`; AIRS-SB is `20-ml-paper-writing/systems-paper-writing/references/section-blueprints.md`.
- NS: https://github.com/yuan1z0825/nature-skills at 84880815fb37317b3766bff2c2abba395b8993c3, Apache License 2.0 (no NOTICE file and no named copyright holder upstream).
  NS is `skills/nature-shared/core/main-text-discipline.md`; its "SI" and "supplementary information" become "cut", and its "response letter" becomes "rebuttal notes".
- RPW: https://github.com/Master-cai/Research-Paper-Writing-Skills at 77e7c2c1ba06f7d71844873147665437a03aac1b, MIT license, Copyright (c) 2026 Master-cai.
  RPW-I is `research-paper-writing/references/introduction.md`; RPW-E is `research-paper-writing/references/experiments.md`; its colour highlighting becomes bold or a symbol.
