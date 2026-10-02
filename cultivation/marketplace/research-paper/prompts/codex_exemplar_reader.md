You are reading one published paper in full to learn how it presents information, how it structures itself and how it flows, and then comparing it with our draft.

The paper is the file `{file}` in your working directory: {title} ({url}), converted from PDF with pdftotext.
Ignore line-break, hyphenation and column artifacts.
Read the whole file, every section and appendix, before you answer: run `wc -l {file}`, then `sed -n 'A,Bp' {file}` in consecutive chunks until every line is covered.
Do not use web search. Read no other file.

Section type under study: {section_type}.

Report in Markdown, in this order:

0. READ. The paper's section list with approximate word counts, and the line ranges of the file you read.
1. QUESTIONS A, for this section type: {questions_a}.
2. QUESTIONS B: {questions_b}.
3. FLOW. For each paragraph of the paper's sections of this type: its first sentence verbatim, the reader question it answers, and how it hands off to the next paragraph. Typical sentence length. Whether a running example, figure or table carries the argument, and how.
4. COMPARE WITH OUR DRAFT (below). For each paragraph of ours: the move this paper makes better or worse, with a verbatim quote from each side. Then rank the three changes to our text that would help a first-time reader most, each as a concrete edit (our sentence verbatim, then the replacement), keeping every fact, number, citation and caveat of ours.

Every claim about the paper carries a verbatim quote and the section it comes from.
Be specific and harsh; do not praise. Do not suggest adding facts about our system that our text does not state.
End with a line starting "Risks:" naming what you could not judge.

Our draft ({macros}):

```latex
{ours}
```
