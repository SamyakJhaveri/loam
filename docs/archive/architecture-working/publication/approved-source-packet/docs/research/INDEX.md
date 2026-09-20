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
| `advisor-and-managed-agents.md` | the Claude Code advisor page, the seven cookbook notebooks Samyak named on 2026-09-09, one local advisor probe | `--advisor fable` on the worker call (F11), the specialist shape for the large-ticket workflow (F12), nothing from PTC or tool search |
| `primary-2026-09-08/` | the same sources read from their live pages, repos, and captions on 2026-09-08, with the fact-check corrections to the notes above | one fresh judge, human-decided checks, no loop inside a loop, remove one component per run and read the ledger (#38) |

The three 2026-09-06 notes were copied from gitignored files under `.superpowers/lean-v3/research/`, deleted 2026-09-11 (archive: loam-lean-v3-archive-2026-09-11.tar.gz on both machines); the video transcripts live on under `.superpowers/transcripts/`.
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

### Advisor and Managed Agents

| URL | kind | given on | context | note file |
|---|---|---|---|---|
| https://code.claude.com/docs/en/advisor | docs | 2026-09-09 | The native advisor tool, read when Samyak asked why Fable never steers the worker | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/managed-agents-cma-consult-an-advisor | cookbook | 2026-09-09 | "include these too, but only if they are relevant"; notebook `managed_agents/CMA_consult_an_advisor.ipynb` | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/managed-agents-cma-coordinate-specialist-team | cookbook | 2026-09-09 | Same ask; notebook `managed_agents/CMA_coordinate_specialist_team.ipynb` | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/managed-agents-cma-verify-with-outcome-grader | cookbook | 2026-09-09 | Same ask; notebook `managed_agents/CMA_verify_with_outcome_grader.ipynb` | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows | cookbook | 2026-09-09 | Same ask; notebook `claude_agent_sdk/08_Dynamic_workflows.ipynb` | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/patterns-agents-async-multi-agent-orchestration | cookbook | 2026-09-09 | Same ask; notebook `patterns/agents/async_multi_agent_orchestration.ipynb` | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/tool-use-programmatic-tool-calling-ptc | cookbook | 2026-09-09 | Same ask; notebook `tool_use/programmatic_tool_calling_ptc.ipynb` | advisor-and-managed-agents.md |
| https://platform.claude.com/cookbook/tool-use-tool-search-with-embeddings | cookbook | 2026-09-09 | Same ask; notebook `tool_use/tool_search_with_embeddings.ipynb` | advisor-and-managed-agents.md |
| https://github.com/anthropics/claude-cookbooks | repo | 2026-09-09 | The tree the seven notebooks live in, listed for the cookbook survey table | advisor-and-managed-agents.md |

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

## Where each resource lives in Loam today

Verified against `main` 8305c9a on 2026-09-11 by reading the files named.
"Code" means text or logic taken from the source and adapted; "shape" means the design was copied and the code written here; "read" means it changed a decision but no artifact points at it; "unused" means it is on the list and nothing uses it yet.

| Resource | Use | Where in Loam |
|---|---|---|
| Claude Code advisor doc | code | `--advisor fable` on the worker call, the env guard, the ledger fields `advisor_calls` and `advisor_usd` (`bin/factory`, F11); of its three consult moments the worker contract names the first, F24 adds the recurring-failure one, and the consult-before-done one is rejected on cost |
| Managed Agents consult-an-advisor cookbook | code | the consultation policy paragraph in `bin/factory.d/_common.md` is the cookbook worker prompt with Loam's decisions named |
| Managed Agents coordinate-specialist-team cookbook | shape | one objective, one owned input set, one JSON hand-back per task in `bin/factory.d/factory-round.js` (F12) |
| Leonxlnx/unlazy (`scripts/lib/gates.mjs`, MIT) | code | `globsOverlap` and `normalizeOwnsGlob` ported with attribution into `factory-round.js`; the parent re-verifies every check (the integrator reruns each task's check); ABANDON with a reason as the only non-fix exit (`_common.md`, `LOOP.md`) |
| disler/super-simple-software-factory (README essay, no code) | shape | `verdict_consistent` in `bin/factory` with its fixture gate in `bin/check` (F13); the four-line brief form in `CONTRACT.md`, moving to the `/brief` skill (F5); "a known command is code" as the rule that every done check is a shell line the supervisor runs |
| Anthropic, harness design and effective harnesses | shape | harness design: fresh-context judge and reviewer on a different model from the worker, frozen prompts, the worker never grades itself (`LOOP.md`, `ARCHITECTURE.md` design rules); effective harnesses: the feature list that starts `passes: false` is the done-checks block that must print FAIL on base (round 0) |
| Anthropic, multi-agent research system | read | the fan-out caps at four tasks and ships behind a flag with a ledger line because "most coding tasks involve fewer truly parallelizable tasks" and multi-agent costs about 15x (F12 Goal) |
| AI-native SDLC playbook | shape | the review ceiling is how many streams one person can review properly (the playbook suggests two or three to start; the fan-out cap of four is Loam's own number, inside multi-agent research's three to five); tracks by blast radius in `CONTRACT.md` |
| AI LABS, Every Level video | shape | the level-two loop is the factory's shape: queue row, build agent on a branch, adversarial reviewer with fresh context, human merge |
| AI LABS, gauntlet loop video | shape | the answer key "where every line comes back as either a pass or a fail" is the done-checks block; the fixed grader prompt the planner cannot write is the frozen judge and reviewer files |
| AI LABS, Unlazy walkthrough | shape | pending evidence counts as unmet; the owned-files rule for parallel builders; the integrator reruns checks instead of trusting reports (F12) |
| bradautomates/claude-video (`watch` skill) | read | used once for the 2026-09-06 transcript read; the 2026-09-09 transcripts came from youtube-transcript-api on the runner instead |
| Reddit threads on the playbook and on building fast | read | "plan with verification loops before any goal run" and "if it is not an enforced gate, humans stop looking" are why the done-checks block, not prose, is the completion condition |
| Lance Martin, `/claude-api prompt-audit` | code | run on every new prompt paragraph before a ticket is published (F11 and F12 prompts, 2026-09-10); the claude-api skill is installed from anthropics/skills |
| Fable 5.1 prompting guide | code | the `fable-prompting` skill in `seed/.agents/skills/` and the session-brief hook (`seed/.claude/hooks/`) |
| Claude Code hooks doc | code | `seed/.claude/hooks/` payload fields; the Stop hook in `bin/factory.d/worker-settings.json` |
| mattpocock/skills | code | installed as the `mattpocock-skills` plugin; four of the six names a worker may invoke in `bin/factory.d/skills.txt` |
| Codex plugin (openai-codex) | code | `bin/factory.d/review-output.schema.json` is the plugin's schema, byte-identical; the Codex worker and review calls (F4, F17) |
| AMAP-ML/LongHorizon-Harness | shape | per-role model and effort resolution is the roles block in `bin/factory` |
| cobusgreyling/loop-engineering | shape | stuck detection is the `stuck` exit (same failing set twice); the daily spend ledger is `ledger-daily.jsonl` |
| anthropics/cwc-long-running-agents | shape | the fresh-context evaluator with no write tools is the grader call with `--tools Read,Grep,Glob`; Apache-2.0; about eleven rules taken into `anthropic-engineering.md`, no code copied; its two `matcher: "*"` hooks rejected |
| huangruiteng/loopx, ray-r-ren/agent-apprenticeship, Forward-Future/loopy, Spielewoy/autoprompt-skill, chenxiachan/thoughtdag | read | evaluated in `loop-repos.md`, re-read at the code level 2026-09-11 (autoprompt's `autoprompt-gate.js` included); nothing taken, each rejection with its reason there |
| PTC and tool-search cookbooks | read | API betas with no CLI form; the Bash tool and native ToolSearch are the equivalents, so nothing was built |
| Dynamic workflows and async orchestration cookbooks | read | the Workflow tool and `parallel()` are the CLI forms used by F12 |
| nvidia/skillspector | unused | named as the vetting gate for every external skill; never installed; the 2026-09-01 skill clusters are still unvetted |
| stop-slop, humanizer, academic-humanizer | code | installed as user skills under `~/.claude/skills/`; they run on outward prose, not on the factory |
| The academic research skill clusters (Imbad0202, FAROS, paperjury, gpt-researcher, DeepResearch, and the rest) | unused | on the vet-first list; none installed, none used by the factory |
| VoltAgent, ZacheryGlass, vercel-labs agent-skills | read | the 2026-08-29 planning-agent sweep behind the merged plan-reviewer; archived under `docs/archive/specs/rebuild-research/` |
| The web-frontend bundles (anthropics, vercel) and deer-flow-public | code | installed from the `seed-skills` marketplace; design and research work outside the factory loop |
| The four diagram tools of 2026-05 (excalidraw, draw.io, PaperBanana, gitdiagram) | read | adopted then as bundles; `cultivation/marketplace/` on `main` ships only `sam-cc-setup` today, so they are not part of the shipped template |

What this table says: the factory's mechanisms come from three places, the Anthropic pages and cookbooks (the advisor, the grader split, the specialist shape), the unlazy repo (the only fan-out code worth porting), and the two AI LABS loop videos (the done-checks answer key and the human merge).
The rest of the loop-repo list was read and set aside on purpose.
The unused rows are the vetting gate and the research skill clusters, which wait on the gate.

## Older research, linked not copied

- `docs/archive/specs/rebuild-research/research-cc-docs.md` - full Claude Code docs sweep from 2026-08-28, every claim sourced to a doc URL.
- `docs/archive/specs/rebuild-research/refagents-sweep.md` and the three `refagents-*.md` files - the 2026-08-29 planning-agent sweep covering the agent repos above.
- `docs/archive/specs/rebuild-research/research-codex-docs.md` and `research-context-rules.md` - Codex docs and context-rule research.

## Standing asks not yet mechanized

- The Fable prompting guide must be live, not memorized; Samyak has asked three times for a mechanism that removes the reminder.
- Prompt shaping is a pipeline stage: raw request, brief for Fable, plan, grill or wayfinder, then the loop; `docs/factory/` is the design for it.
- Vet every external asset before installing, with skillspector as the gate; the 2026-09-01 skill clusters above are still unvetted.
