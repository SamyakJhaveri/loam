# Research index

Every resource found in the on-disk transcripts since 2026-08-26, where its reading lives, and what the factory took from it.
The design that rests on this evidence is in `../factory/ARCHITECTURE.md`.

## Notes

| Note | Covers | What the factory took |
|---|---|---|
| `anthropic-engineering.md` | nine sources: eight Anthropic engineering articles and the SDLC playbook | default-FAIL contracts, fresh-context graders on a different model, one unit per session, prompt changes as production changes, remove one harness piece per model upgrade |
| `loop-repos.md` | nine repos: five loop frameworks (2026-09-06) and four pattern repos (2026-09-07); cwc-long-running-agents is in anthropic-engineering.md | adopt no framework; the four-line brief, gates before implementation, ABANDON with reason, verdict consistency, a known command is code |
| `community.md` | three Reddit threads, six videos, the playbook critiques, the surprise-me panel tables | spec over parallelism, independent expectations, tracks by size, risk as a dimension, the four slop tells |
| `harness-primitives.md` | Claude Code 2.1.258 and Codex 0.153.4 flags, hooks, workflows, plugin tooling | json-schema verdicts, read-only grader calls, shell driver over in-session loops, ultracode inert under print, plugin eval unsuitable for grader replay |
| `anthropic-loop-engineering.md` | the mis-titled loop-engineering PDF and the AI LABS levels video (2026-09-06) | supervisor owns everything mechanical; models write and judge only |
| `video-loop-engineering.md` | the AI LABS skill video (2026-09-06) | answer key per ticket, fixed judge prompt, hard caps |
| `sandbox-and-codex-keys.md` | sandbox and permission keys from primary docs (2026-09-06) | the deny-only role settings |
| `primary-2026-09-08/` | the same sources read from their live pages, repos, and captions on 2026-09-08, with the fact-check corrections to the notes above | one fresh judge, human-decided checks, no loop inside a loop, remove one component per run and read the ledger (#38) |

The three 2026-09-06 notes are copies of gitignored files under `.superpowers/lean-v3/research/`; F1 deletes the originals.
Transcripts for the five videos given on 2026-09-07 were unobtainable on that day; `primary-2026-09-08/videos.md` has them, pulled with yt-dlp auto-captions.

## Resources given, by theme

Scope: on-disk transcripts start 2026-08-26, so earlier sessions are not recoverable; only resources Samyak gave are listed, and links an agent found by search are excluded.

### Loop engineering

| URL | kind | given on | context | note file |
|---|---|---|---|---|
| https://github.com/huangruiteng/loopx | repo | 2026-09-06 | One of five loop repos to compare: pick the simplest, most direct fit | loop-repos.md |
| https://github.com/AMAP-ML/LongHorizon-Harness | repo | 2026-09-06 | Same five-repo fit evaluation | loop-repos.md |
| https://github.com/ray-r-ren/agent-apprenticeship | repo | 2026-09-06 | Same five-repo fit evaluation | loop-repos.md |
| https://github.com/cobusgreyling/loop-engineering | repo | 2026-09-06 | Same five-repo fit evaluation | loop-repos.md |
| https://github.com/Forward-Future/loopy | repo | 2026-09-06 | Same five-repo fit evaluation | loop-repos.md |
| https://github.com/Leonxlnx/unlazy | repo | 2026-09-07 | Named as a loop-engineering input | loop-repos.md |
| https://github.com/Spielewoy/autoprompt-skill | repo | 2026-09-07 | Named as "autoprompt skill"; fits the reprompt-for-Fable stage | loop-repos.md |
| https://github.com/chenxiachan/thoughtdag | repo | 2026-09-07 | Named as "thoughtdag"; fits the graph-engineering goal | loop-repos.md |
| https://github.com/anthropics/cwc-long-running-agents | repo | 2026-09-07 | Anthropic long-running-agent reference; read as source 9 of the Anthropic set | anthropic-engineering.md |
| https://github.com/disler/super-simple-software-factory | repo | 2026-09-07 | Named as "Super Simple Software Factory" | loop-repos.md |

### Anthropic and official guidance

| URL | kind | given on | context | note file |
|---|---|---|---|---|
| https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | article | 2026-09-07 | Core of the loop-engineering reading list | anthropic-engineering.md |
| https://www.anthropic.com/engineering/harness-design-long-running-apps | article | 2026-09-07 | Same reading list | anthropic-engineering.md |
| https://www.anthropic.com/engineering/managed-agents | article | 2026-09-07 | Same reading list | anthropic-engineering.md |
| https://www.anthropic.com/engineering/multi-agent-research-system | article | 2026-09-07 | Same reading list, multi-agent orchestration | anthropic-engineering.md |
| https://www.anthropic.com/engineering/building-effective-agents | article | 2026-09-07 | Same reading list | anthropic-engineering.md |
| https://www.anthropic.com/engineering/AI-resistant-technical-evaluations | article | 2026-09-07 | Same reading list; feeds the judge design | anthropic-engineering.md |
| https://www.anthropic.com/engineering/april-23-postmortem | article | 2026-09-07 | Same reading list, failure modes | anthropic-engineering.md |
| https://claude.com/blog/the-ai-native-sdlc-playbook | article | 2026-09-07 | The SDLC framing Samyak wants Loam to implement | anthropic-engineering.md |
| local: `~/Desktop/Hardware, Software and AI Agent Harness Setup/Guides/loop engineering form anthropoic.pdf` | pdf | 2026-09-06 | Titled as an Anthropic playbook; it is a reformatting of Addy Osmani's guide, so nothing in it is cited to Anthropic | anthropic-loop-engineering.md |
| https://www.anthropic.com/claude-fable-and-mythos-5-1 | article | 2026-09-01 | Answered "this model" when asked which model to research | anthropic-engineering.md |

### Community

| URL | kind | given on | context | note file |
|---|---|---|---|---|
| https://www.youtube.com/watch?v=D_uojDHkbw4 | video | 2026-09-06 | "This Claude Skill Just Fixed Loop Engineering", AI LABS; watch and fold into the loop design | community.md |
| https://github.com/bradautomates/claude-video | repo | 2026-09-06 | The skill named for watching that video | community.md |
| https://www.youtube.com/watch?v=PLyRe6Zk--8 | video | 2026-09-07 | "Every Level Of Claude Code Loop Engineering Explained", AI LABS; transcript read 2026-09-06, outline 2026-09-07 | community.md, anthropic-loop-engineering.md |
| https://www.youtube.com/watch?v=c47uqR7XB_c | video | 2026-09-07 | "GitHub's #1 Trending Author's New Claude Skill Is Insane", AI LABS, the Unlazy walkthrough; outline only | community.md |
| https://www.youtube.com/watch?v=Uvl-tRga98g | video | 2026-09-07 | "Designing with Claude: From prompt to production", Anthropic; no captions, nothing extractable | community.md |
| https://www.youtube.com/watch?v=VMvZuhcDdnw | video | 2026-09-07 | "Build $10,000 Websites using Claude Code", Metics Media; design tutorial, low relevance | community.md |
| https://www.youtube.com/watch?v=Ysr7oNDajJI | video | 2026-09-07 | "Insane Claude Design Skills", AI LABS; seven design skills compared, medium relevance | community.md |
| https://www.reddit.com/r/ClaudeCode/comments/1w97lh4/how_are_you_building_so_fast/ | reddit | 2026-09-07 | Loop engineering reading list | community.md |
| https://www.reddit.com/r/ClaudeCode/comments/1w71zqx/has_anyone_actually_tried_anthropics_ainative/ | reddit | 2026-09-07 | Reception of the AI-native SDLC playbook | community.md |
| https://www.reddit.com/r/ClaudeAI/comments/1vzl6kk/anthropic_published_an_ainative_sdlc_playbook_the/ | reddit | 2026-09-07 | Reception of the AI-native SDLC playbook | community.md |
| r/ClaudeCode threads 1w5o5zz, 1w5fed8, 1w59n28, 1w5tnlk, 1w4qs4p, 1vojj88 | reddit | 2026-09-03 | Fable 5.1 field reports gathered for the project design and prompt audit | community.md |
| https://www.reddit.com/r/claude/comments/1w4mrqs/used_fable_51_all_day_heres_whats_actually/ | reddit | 2026-09-03 | Same audit brief | community.md |
| https://www.reddit.com/r/ClaudeAI/wiki/survivalguideweekly/ | reddit | 2026-09-03 | Same audit brief | community.md |
| https://news.ycombinator.com/item?id=49525809 | other | 2026-09-03 | Same audit brief | community.md |
| https://x.com/RLanceMartin/status/2095170001175199771 | other | 2026-09-06 | "See this as well", sent beside the claude-api skill | community.md |

### Skills and agents to vet

| URL | kind | given on | context | note file |
|---|---|---|---|---|
| https://github.com/nvidia/skillspector | repo | 2026-09-01 | Vet every external skill with it, and keep it updated | not yet read |
| https://github.com/anthropics/skills/tree/main/skills/claude-api | repo | 2026-09-06 | "There is this"; became the claude-api skill upstream sync | not yet read |
| https://github.com/VoltAgent/awesome-claude-code-subagents | repo | 2026-08-29 | Hunt for plan-review and architecture agents | archive: docs/archive/specs/rebuild-research/ |
| https://github.com/ZacheryGlass/.claude | repo | 2026-08-29 | Same hunt | archive: docs/archive/specs/rebuild-research/ |
| https://github.com/vercel-labs/agent-skills | repo | 2026-08-29 | Same hunt | archive: docs/archive/specs/rebuild-research/ |
| https://github.com/hardikpandya/stop-slop | repo | 2026-09-01 | Anti-AI-writing skill to keep; drop the rest of that cluster | not yet read |
| https://github.com/AIScientists-Dev/academic-humanizer | repo | 2026-09-01 | Same anti-slop keep list | not yet read |
| https://github.com/blader/humanizer | repo | 2026-09-01 | Same anti-slop keep list | not yet read |
| https://github.com/Imbad0202/academic-research-skills | repo | 2026-09-01 | Research-skill cluster to keep, install by workflow, vet first | not yet read |
| https://github.com/Imbad0202/academic-research-skills-codex | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/OpenNSWM-Lab/FAROS | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/lishix520/academic-paper-skills | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/Spark-To-Paper-Skills/paperjury | repo | 2026-09-01 | Same cluster; a jury skill worth reading for the judge stage | not yet read |
| https://github.com/Master-cai/Research-Paper-Writing-Skills | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/assafelovic/gpt-researcher | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/hzwer/WritingAIPaper | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/Orchestra-Research/AI-Research-SKILLs | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/dzhng/deep-research | repo | 2026-09-01 | Same cluster | not yet read |
| https://github.com/Alibaba-NLP/DeepResearch | repo | 2026-09-01 | Same cluster; install by dynamic workflow, not inline | not yet read |

### Prompting guide and docs

| URL | kind | given on | context | note file |
|---|---|---|---|---|
| https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 | docs | 2026-09-03 | "Use this prompting guide as a gospel"; wanted live access from every Fable session | harness-primitives.md |
| https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#writing-density | docs | 2026-09-04 | Density section; cited when asking for the mechanism that became the session-brief hook | harness-primitives.md |
| https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#prefer-targeted-edits-over-whole-file-rewrites | docs | 2026-09-06 | "How do we bake these in so I do not have to keep reminding you?" | harness-primitives.md |
| https://code.claude.com/docs/en/hooks | docs | 2026-09-05 | Named as the authority for SessionStart and PostModelSwitch payload fields | harness-primitives.md |

## Older research, linked not copied

- `docs/archive/specs/rebuild-research/research-cc-docs.md` - full Claude Code docs sweep from 2026-08-28, every claim sourced to a doc URL.
- `docs/archive/specs/rebuild-research/refagents-sweep.md` and the three `refagents-*.md` files - the 2026-08-29 planning-agent sweep covering the agent repos above.
- `docs/archive/specs/rebuild-research/research-codex-docs.md` and `research-context-rules.md` - Codex docs and context-rule research.

## Standing asks not yet mechanized

- The Fable prompting guide must be live, not memorized; Samyak has asked three times for a mechanism that removes the reminder.
- Prompt shaping is a pipeline stage: raw request, brief for Fable, plan, grill or wayfinder, then the loop; `docs/factory/` is the design for it.
- Vet every external asset before installing, with skillspector as the gate; the 2026-09-01 skill clusters above are still unvetted.
