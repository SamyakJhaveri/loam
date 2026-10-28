# Shared brief: <the question in one line>

<!-- Copy to <run>/brief.md and fill every <...>. Keep the owner's own ideas and conclusions, the run folder's path and every other seat's seeds out of the shared part. Everything above the first "## Seat" heading is shared: every seat's file gets it. End the file with one "## Seat <seat id>" section per seat, each id used once, with no other "## " section after them ("### " subsections inside a seat section are fine). Then run the skill's scripts/split-brief.sh <run>, so each seat gets the shared part and its own section only. Delete this comment before splitting. -->

## The question (from the study owner)

<One paragraph: what the owner wants to find out, in the owner's words.>

## The setting (facts, not hypotheses)

- <What the project measures and how, in plain words.>
- <Data already collected, with absolute paths a seat may read.>
- <Constraints: budget, deadline, venue, what cannot change.>

## Rules

- Use only the sources this brief names, the files in your working folder, and the web.
- Do not read memory files, CLAUDE.md or AGENTS.md files, or any repository file this brief does not name: stay blind to the owner's existing conclusions and to the other seats.
- For every claim give the source and a locator (page or section, URL), and quote numbers exactly.
- Mark each claim Verified (you read it in the source this session) or Inferred.
- Note confounds, small samples, single-model results and claims made without an ablation.
- Read and propose only; run no experiments.

## Output

One Markdown document with 3 to 8 ideas, one `###` section each, holding these five fields:

- **Plain words.** The question in one or two sentences an undergraduate can follow.
- **Gap.** The strongest quote showing the gap, with its locator and Verified or Inferred.
- **Closest work.** The nearest paper you know and what it already does.
- **Data and cost.** What data would answer it, and its cost: FREE (already collected), SMALL (one analysis or one logged field) or NEW ARM (new runs).
- **Kill result.** The finding that would show the idea wrong or already done.

Write no file.
Make the whole document your final message, with nothing before or after it: the launcher saves only that message as your proposal.

## Seat <seat id>

Seat: <seat id>.
Lens: <dormant-assets hunter | reframing hunter | adversary | analogist>.
<Paste this lens's definition from surprise-me's Panel mode; for the analogist also paste its step 3, the analogy move; for the dormant-assets hunter its step 2.>
Model and effort: <for example Opus 5.5 at xhigh, Fable 5.1 at high, or Codex with the model from its config at xhigh>.
Seed papers: <ids and URLs, different for every seat>.
Seed files in your working folder: <file names copied from <run>/seeds/<seat id>/, or none>.
<Dormant-assets hunter only: the data paths you may read, each one an absolute path the launcher opens with --add-dir.>
<Reframing hunter only: the target venue or audience whose problem the story is told as, with its call for papers or reviewer guide.>
<Fable seat only: add the five "###" subsections of the fable-prompting skill's plan rubric (Goal and why, Constraints, Done check per task, Session conduct, Target model and effort).>
