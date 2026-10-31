# The four switched-off user skills: proposal (#375)

U8 (28 Oct 2026) switched off `rigor`, `research-writing`, `team-voice` and `adhd` on both hosts with `skillOverrides` "off" in `~/.claude/settings.json`.
The files stay on jhaveris under `~/.claude/skills/<name>/`; the Mac never had them.
This page proposes one of four options per skill, with evidence; Samyak picks.

The options:

- rewrite: replace the skill with a short new version whose purpose and trigger Samyak sets.
- plugin: move it into the sam-cc-setup plugin (`cultivation/marketplace/sam-cc-setup/skills/`), so it reaches both hosts.
- typed-only: keep the file on jhaveris and set `skillOverrides` to "user-invocable-only", like `experiment-loop` and `new-model-workflow`; `/name` works, and Claude never loads it on its own.
- delete: remove the folder, or move it to `~/.claude/skills-archive/` (as was done for `fable-mode`), which keeps it recoverable at no load cost.

The test is the lean-skill rule (PLAN item 2k): few skills, no auto-skill rules, a typed-only skill costs nothing until invoked.
All four descriptions let Claude load the skill on its own when switched on, so every option except delete must also drop that.
The sam-cc-setup plugin lives in this public repo, so anything moved into it is published.

## How the evidence was gathered

Every skill file was read on jhaveris on 31 Oct 2026.
Uses were counted two ways.
Skill calls: `"skill":"<name>"` across all 1412 transcripts in `~/.claude/projects/` found 0 for each of the four.
Those transcripts reach back only to 2026-10-06, after the skills went quiet, so automatic loads in July and August cannot be counted.
Typed requests: `~/.claude/history.jsonl` (every prompt typed on jhaveris, 2026-03-28 to 2026-10-29) was searched for each name.
That second source goes beyond the ticket's Approach; it is the only record that reaches back to July and August.
Only prompts that asked Claude to use a skill count as uses; plain-English "rigor" and a 2026-08-02 prompt asking for an explanation of the skills do not.
Every typed use came from one paper project on jhaveris during one rebuttal.
Prompts are cited by date, not quoted or named by project, because they name co-authors and reviewers and this repo is public.

| Skill | Typed uses | First | Last |
|---|---|---|---|
| team-voice | 4 | 2026-07-28 | 2026-08-03 |
| research-writing | 3 | 2026-08-02 | 2026-08-03 |
| rigor | 2 | 2026-08-02 | 2026-08-02 |
| adhd | 0 | - | - |

Team-voice depends on research-writing: it runs `research-writing/style_lint.py --house` and points at `research-writing/exemplars.md` for its corpus.
Pick these two together; deleting or moving research-writing alone breaks team-voice.
The pointers also run the other way: research-writing's `SKILL.md` tells Claude to load team-voice for the group's writing, and `exemplars.md` points to it for house rules, so deleting team-voice needs those two lines removed (`style_lint.py` names it only in a comment).

A 2026-08-05 setup-audit memory note (`project_claude5_setup_rework.md`, in the paper project's memory) called the rigor/research-writing/team-voice trio "correctly factored - never restructure it".
U8 is newer and is Samyak's own call; it found the trio unused and team-voice not giving the writing Samyak needed.

## rigor

What it does: a verification and reporting checklist (8.5 KB): never state an unmeasured number, label claims Verified/Likely/Assumption, a self-attack pass, a completeness mapping, ten "fake competence" patterns, and a final gate.
When it triggers: its description says to load it "AUTOMATICALLY" for any text leaving the project and any published number, and on "be rigorous" or "this is going out".
Origin: sections 4 to 7, 10 and the final gate of `~/.claude/FABLE-BRAIN.md` (the file says it was written by Claude Fable 5 on 2026-07-11), moved into this skill on 2026-08-01 during the Claude 5 setup overhaul (memory note `setup-overhaul-2026-08-01.md`); that original text now survives only in `~/.claude-backup-2026-08-01/`.
Last used: 2026-08-02, typed as `/rigor` in two prompts that day; 0 Skill calls in the 6-31 Oct transcripts.

Options:

- rewrite: possible, but the parts worth keeping already live elsewhere (see Evidence).
- plugin: it could ship typed-only (`disable-model-invocation: true`, as every sam-cc-setup skill does), but that publishes a checklist whose short form the global `CLAUDE.md` already loads, for a skill not called since 2026-08-02.
- typed-only: harmless, but nothing calls it and its short form already loads from the global `CLAUDE.md`.
- delete: loses nothing that is not kept elsewhere; the full original text is in the 2026-08-01 backup.

Recommend: delete.
Its core rules already load in short form from the global `CLAUDE.md`, typed pstack skills cover the rest, and its automatic trigger is the kind of auto-skill rule the lean-skill rule forbids.
Evidence: the global `~/.claude/CLAUDE.md` already carries the short form ("Reproduce a bug the way a user hits it ... show proof", "When you cannot check something: I don't know X", "End a report with Risks:"); pstack's typed-only `principle-prove-it-works` (called in 30 of the 1412 October transcripts, the most-called skill there) and `principle-explain-the-number` cover verification and numbers when invoked; the factory's done-checks and judge enforce evidence on every ticket; the last typed use was 2026-08-02 and it was never named again in three months; the source text survives in `~/.claude-backup-2026-08-01/FABLE-BRAIN.md`, so deleting is recoverable.

## research-writing

What it does: a craft guide for research text read by outsiders (15.6 KB `SKILL.md`): name the reader first, answer in sentence one, put the number in the claim's sentence, a defect-and-repair table for sentences, an "honesty apparatus", and a send checklist; plus `exemplars.md` (44 KB of verbatim passages from published papers) and `style_lint.py` (598 lines, stdlib-only, with `--test` fixtures).
When it triggers: its description asks Claude to load it for any paper section, abstract, rebuttal, OpenReview comment, report or co-author status message, and when a draft is called dense or a character limit forces cuts.
Origin: written about 2026-07-27 in the paper project during the rebuttal (file times: `SKILL.md` 2026-07-27, `style_lint.py` 2026-08-08).
Last used: 2026-08-03, typed as `/research-writing` in a prompt about the rebuttal responses; also typed twice on 2026-08-02; 0 Skill calls in the 6-31 Oct transcripts.

Options:

- rewrite: worth doing only once Samyak states what writing is needed; the 2026-08-03 prompt found an earlier batch of drafts far too long and asked for a short rewrite in the style of this skill and team-voice, and whether that batch was written with them is not recorded.
- plugin: the plugin is in this public repo, so moving it would publish 44 KB of passages copied from other people's papers; the `SKILL.md` prose of both skills hardcodes `~/.claude/skills/research-writing/` paths, and team-voice would have to follow it.
- typed-only: keeps the linter, the exemplars and team-voice's dependency intact at no cost until typed.
- delete: throws away the one tested tool here (`style_lint.py`) while paper work continues.

Recommend: typed-only.
Research writing is still a live need, and a typed-only skill costs nothing until Samyak types `/research-writing`.
Evidence: it was typed three times in two days (2026-08-02 to 2026-08-03); a second paper project on jhaveris was active in October history (timing runs), so outward writing is likely again; it holds the only executable, tested asset of the four (`style_lint.py --test`); team-voice depends on its files; "user-invocable-only" removes its automatic trigger, as already done for `experiment-loop` and `new-model-workflow`; pstack's `technical-writing` and `unslop` cover docs and AI tells, not paper or rebuttal craft, so they do not replace it; plugin is ruled out while the exemplars stay in it, because the plugin is public.

## team-voice

What it does: the house style of one research group (10.6 KB): who the co-authors are, ten writing habits measured from the group's published papers, rebuttal-only rules, standing instructions from named senior co-authors, and a send checklist.
When it triggers: its description lets Claude load it, alongside research-writing, for any paper section, rebuttal, OpenReview comment, audit report, reviewer email or co-author note published under that group's names.
Origin: written about 2026-07-27 with research-writing, from the group's papers and the co-authors' corrections during the rebuttal (its rebuttal rules cite 2026-07-27).
Last used: 2026-08-03, typed as `/team-voice` in the same prompt as research-writing; first typed 2026-07-28, four typed uses in all; 0 Skill calls in the 6-31 Oct transcripts.

Options:

- rewrite: only with a new statement from Samyak of the voice wanted; U8 judged the current one did not give the writing needed.
- plugin: wrong home: the plugin is public and holds repo-independent tooling, and this file names one group's members and institutions and holds one rebuttal's rules.
- typed-only: keeps a file U8 judged unhelpful, at no runtime cost.
- delete: the group's published-text evidence survives in `research-writing/exemplars.md`; only the rules distilled from it go.

Recommend: delete.
U8 judged that it did not give the writing needed, and half of it serves one finished rebuttal; the summer record is mixed rather than against it (see Evidence), so this pick rests on U8.
Evidence: it is the most-typed of the four (4 uses), but every use fell in one week of one rebuttal, and the last one, on 2026-08-03, asked for a short rewrite of an earlier batch in the style of it and research-writing; that batch came from a 2026-08-02 session told to use both, but whether Claude loaded them is not recorded, and a later prompt blamed the model rather than the skills; U8 (28 Oct) recorded that team-voice "did not give the writing Samyak needed"; its "Rebuttal and response house rules" section says those rules were adopted after a 2026-07-27 rebuttal and must not be carried into papers; the paper corpus and its word counts live in `research-writing/exemplars.md` (sections 1 to 15), so deleting team-voice keeps the evidence; this delete needs the two pointers to team-voice in research-writing removed (see the dependency note above), and the 2026-08-01 backup holds the same body text; if Samyak wants the co-authors' standing instructions kept, the cheaper home is a few lines in the paper repo's own `CLAUDE.md`, not a user skill.

## adhd

What it does: parallel brainstorming: five isolated subagents each answer under a different "cognitive frame", then one agent scores, one clusters, and three deepen the survivors (about 10 Agent calls and 5 to 10 times the cost of one answer, by its own Cost section).
When it triggers: on `/adhd`, and its description also asks Claude to load it on brainstorm or ideate intents and on open-ended design, architecture, naming, API or fuzzy-debugging decisions.
Origin: a third-party MIT skill from github.com/UditAkhourii/adhd, installed with npx on 2026-08-01 during the Claude 5 setup overhaul (memory note `setup-overhaul-2026-08-01.md`); npx first dropped it into a repo as a symlink, which was fixed on 2026-08-02.
The same day Samyak also installed `i-have-adhd`, a separate always-on terseness plugin; it is no longer installed, and the U8 record does not say whether the misbehaviour it noted came from this skill or from that plugin.
Last used: no use found; `/adhd` was never typed in `history.jsonl` (the 2026-08-01 prompt asked to install it, and 2026-08-02 prompts listed it and objected to its being disabled), and it was never loaded in the surviving transcripts (it was loadable on 2026-08-09 and 6-28 Oct); no record covers 2026-08-10 to 2026-10-05, so automatic use then is unknown.

Options:

- rewrite: unneeded; skills Samyak already has cover the same job (see Evidence).
- plugin: would publish and spread to both hosts a third-party skill with no recorded use.
- typed-only: keeps a skill that U8 recorded as misbehaving and that was never typed.
- delete: loses nothing; the upstream repo remains if it is ever wanted.

Recommend: delete.
No use of it is recorded, U8 recorded it as misbehaving, and other skills already cover parallel ideation.
Evidence: on 2026-08-02 Samyak objected when an audit switched it off, because it was new and was meant to be used once the setup was fixed; yet in the three months since `/adhd` was never typed in `history.jsonl` and never loaded in the surviving transcripts; U8 recorded that it misbehaved; its closing section points to a `SOURCE-SPEC.md` that is not in `~/.claude/skills/adhd/` (the npx package shipped only `SKILL.md`), a broken reference though the loop itself is complete; its automatic trigger on any open-ended design question is the auto-skill rule the lean-skill rule forbids, and at about 10 agents per run it is the costliest way to misfire; pstack's `arena` (N parallel candidates, graft the best) and `principle-exhaust-the-design-space`, and the plugin's `surprise-me`, already cover divergent ideas.
