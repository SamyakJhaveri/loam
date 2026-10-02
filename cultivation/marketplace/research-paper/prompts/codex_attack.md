<!-- FILL IN, then delete this comment:
Replace <SUGGESTIONS> (the suggestions/ folder build_suggestions.py wrote), <PAPER> (build.text in paper-tools.toml), <SECTIONS_DIR> (paper.sections_dir) and <CODETRUTH> (a saved code-truth report, or delete that line).
Run it read-only from the project root as a bare command, in the background: node <codex-companion.mjs> task --model <codex.model> --effort xhigh --cwd <project root> --prompt-file <the filled copy>.
Save the report with `paper-tool codex_seat save <task output> <OUT>/attack/<model>.md`; build_suggestions.py reads it from there.
-->
You are auditing a list of proposed wording changes to a research paper before its authors choose among them.
Your job is to break the list: find every proposal that would make the paper wrong, less exact, or longer.

Your working directory is the root of the project whose system the paper describes.
You are read-only: change no file.
Use shell reads and searches (`rg`, `sed -n`, `ls`) as much as you need.
Do not search the web.
Judge against the code and result files the project's config (its `AGENTS.md` or `CLAUDE.md`) or this message names as sources of truth; never judge a claim from a file they mark as superseded.

## Files

- The proposals: every file in `<SUGGESTIONS>`, one per section of the paper.
  Each entry has an id of the form `<section key>-<rank>` (for example `design-02`), an action (KEEP, REVISE or DROP), "Ours" (the paper's current text) and "Proposal" (the replacement text or an instruction).
  Read every entry of every file in full.
  Audit every entry whose action is KEEP or REVISE; ignore DROP entries.
- The paper as a reader sees it: `<PAPER>`; its source: `<SECTIONS_DIR>/*.tex`.
- A code-truth audit of the paper: `<CODETRUTH>`. The proposals may have been written without it.

## What to test for each KEEP or REVISE entry

1. `fact-changed`: compared with "Ours", the Proposal adds, drops or changes a number, a citation, a caveat, a condition or a claim. A proposal may legitimately correct a sentence the code contradicts; then test the corrected statement under 2.
2. `code-contradicted`: the Proposal states what the system does, or a count, in a way the code or the result files contradict or make imprecise. Read the implementing code for every such statement. A Proposal that repeats, unchanged, a statement the code-truth audit found `contradicts` or `imprecise` is a finding: cite that finding and say what the proposal would need.
3. `length-added`: count the words of "Ours" and of the Proposal's replacement text. Report an entry whose replacement is longer than the text it replaces, with both counts, and an entry whose stated word change is off by more than 3.
4. `house-rule`: the Proposal breaks a house rule of the project's review contract (`paper/tools/contract.md`, section 3).
5. `conflict`: two KEEP or REVISE entries that cannot both be applied (they rewrite the same text differently, or one cuts what another rewrites), or that would word the same number or rule differently in two sections.

## Report

Markdown, in this order:

0. READ. The files you read, and for each suggestions file the number of KEEP, REVISE and DROP entries you counted.
1. FINDINGS. One fenced block tagged `jsonl`, one JSON object per problem, with keys:
   - `id`: the entry id (for a conflict, both ids).
   - `problem`: fact-changed, code-contradicted, length-added, house-rule or conflict.
   - `evidence`: for code, `path:line` and a verbatim snippet of at most three lines; for facts and length, the two texts' differing words or the two word counts.
   - `fix`: the smallest change to the Proposal that removes the problem, or "drop".
   - `severity`: 1 (the paper would state something false, or a reviewer rebuilding the system would get it wrong), 2 (misleading or inexact), 3 (length or wording).
2. CLEAN. The count of audited entries with no finding, and their ids.
3. Risks: one line naming what you could not check.

Rules: every code verdict cites code you actually read, with `path:line`; no verdict from a file name, a docstring or a comment alone when the code body is available.
Never propose a number you did not read in code or in a results file.
