You are checking that a research paper describes its software exactly as the code does it, not approximately.

Your working directory is the root of the project whose system the paper describes.
The paper's text, as a reader sees it, is `{paper}` (pdftotext of the built PDF).
Its LaTeX source is under `{sections_dir}`.
You are read-only: change no file.
Use shell reads and searches (`rg`, `sed -n`, `ls`) as much as you need.
Do not search the web.
Judge against the code and result files the project's config (its `AGENTS.md` or `CLAUDE.md`) or the task message names as sources of truth; never judge a claim from a file they mark as superseded.

## Task

1. Read in full the paper's sections that describe the system, how its inputs were built and the experimental setup, and every sentence elsewhere (abstract, introduction, results, discussion) that states what the system does: what it takes in, a processing stage or component, a decision rule or threshold, a tolerance, how many items or repetitions it covers, what it writes out and in which file format, a model or tool setting.
2. For each such sentence, find the code or configuration that implements it, and read enough of it to know what it really does.
3. Judge each sentence: `matches` (the code does exactly this), `imprecise` (true in spirit, but a reader rebuilding it from the sentence would build something different), `contradicts` (the code does something else), or `not-found` (you could not find the implementing code; say where you looked).

## Report

Markdown, in this order:

0. READ. The paper sections you read, and the code paths you read, as a list.
1. FINDINGS. One fenced block tagged `jsonl`, one JSON object per checked sentence that is not `matches`, with keys:
   - `section`: the paper section.
   - `ours`: the sentence, verbatim from `{paper}`.
   - `verdict`: imprecise, contradicts or not-found.
   - `code`: the implementing location(s) as `path:line`, and a verbatim snippet of at most three lines.
   - `what_code_does`: one or two plain sentences.
   - `proposal`: a replacement sentence that states what the code does, in the paper's register, with every number kept unless the code shows the number is wrong (then say so in `what_code_does`).
   - `severity`: 1 (a reviewer rebuilding the system would get it wrong, or the claim is false), 2 (misleading), 3 (wording).
2. MATCHES. A count of the sentences you checked that match, and three examples with `path:line`.
3. Risks: one line naming what you could not check.

## Rules

- Every verdict cites code you actually read, with `path:line`. No verdict from a file name, a docstring or a comment alone when the code body is available.
- Never propose a number you did not read in code or in a results file; give its `path:line`.
- Proposals follow the house rules of the project's review contract (`paper/tools/contract.md`, section 3).
