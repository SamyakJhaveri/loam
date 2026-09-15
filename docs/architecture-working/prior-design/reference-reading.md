# Original-reference reading and design-use record

Verified: this record combines the supplied outputs references with the repository docs/research/INDEX.md. Independent readers inspected originals and relevant implementation, then cross-critiqued the design. An inventoried or downloaded URL is not counted as read. Each report below gives exact scope, actual access limits, source findings, adaptation/rejection decisions, dependencies and proposed acceptance checks.

Verified: the supplied ledger contains 84 source entries. The URL inventory has 116 distinct normalized HTTP(S) targets, including 23 historical Loam revision/path targets. Fragment duplicates are retained in occurrence metadata rather than counted as independent evidence. The local X11 PDF is recorded separately from URL targets. These are coverage counts, not full-reading counts.

Verified: a separate reader compared every literal direct URL in docs/research/INDEX.md, outputs/source-register.md and outputs/loop-engineering/source-links.md against the inventory and found none missing. All referenced historical Git objects were available locally. Their changed-file diffs against current main were read. This does not mean every historical file was reread in full. Informal names and linked article bibliographies were not recursively expanded.

Examined repository: clean main `d627bb2755ad49865f798bcb095800ddd2ad1ced`. Source-level implementation findings are not fresh runtime tests. No upstream program was executed.

## Source entries

| ID | Original | This-session scope/status | Detailed reading and design use |
|---|---|---|---|
| S01 | [Original](https://github.com/huangruiteng/loopx) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S02 | [Original](https://github.com/AMAP-ML/LongHorizon-Harness) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S03 | [Original](https://github.com/ray-r-ren/agent-apprenticeship) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S04 | [Original](https://github.com/cobusgreyling/loop-engineering) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S05 | [Original](https://github.com/Forward-Future/loopy) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S06 | [Original](https://github.com/Leonxlnx/unlazy) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S07 | [Original](https://github.com/Spielewoy/autoprompt-skill) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S08 | [Original](https://github.com/chenxiachan/thoughtdag) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S09 | [Original](https://github.com/anthropics/cwc-long-running-agents) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S10 | [Original](https://github.com/disler/super-simple-software-factory) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| S11 | [Original](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S12 | [Original](https://www.anthropic.com/engineering/harness-design-long-running-apps) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S13 | [Original](https://www.anthropic.com/engineering/managed-agents) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S14 | [Original](https://www.anthropic.com/engineering/multi-agent-research-system) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S15 | [Original](https://www.anthropic.com/engineering/building-effective-agents) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S16 | [Original](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S17 | [Original](https://www.anthropic.com/engineering/april-23-postmortem) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S18 | [Original](https://claude.com/blog/the-ai-native-sdlc-playbook) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S19 | [Original](https://www.anthropic.com/claude-fable-and-mythos-5-1) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S20 | [Original](https://www.youtube.com/watch?v=D_uojDHkbw4) | Complete cached transcript read; original video not watched | [sources-community.md](sources-community.md) |
| S21 | [Original](https://github.com/bradautomates/claude-video) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S22 | [Original](https://www.youtube.com/watch?v=PLyRe6Zk--8) | Complete cached transcript read; original video not watched | [sources-community.md](sources-community.md) |
| S23 | [Original](https://www.youtube.com/watch?v=c47uqR7XB_c) | Complete cached transcript read; original video not watched | [sources-community.md](sources-community.md) |
| S24 | [Original](https://www.youtube.com/watch?v=Uvl-tRga98g) | Original body blocked; not read this pass | [sources-community.md](sources-community.md) |
| S25 | [Original](https://www.youtube.com/watch?v=VMvZuhcDdnw) | Cached caption excerpts only; no complete transcript or video read | [sources-community.md](sources-community.md) |
| S26 | [Original](https://www.youtube.com/watch?v=Ysr7oNDajJI) | Cached caption excerpts only; no complete transcript or video read | [sources-community.md](sources-community.md) |
| S27 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w97lh4/how_are_you_building_so_fast/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S28 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w71zqx/has_anyone_actually_tried_anthropics_ainative/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S29 | [Original](https://www.reddit.com/r/ClaudeAI/comments/1vzl6kk/anthropic_published_an_ainative_sdlc_playbook_the/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S30 | [Original](https://www.reddit.com/r/claude/comments/1w4mrqs/used_fable_51_all_day_heres_whats_actually/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S31 | [Original](https://www.reddit.com/r/ClaudeAI/wiki/survivalguideweekly/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S32 | [Original](https://news.ycombinator.com/item?id=49525809) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| S33 | [Original](https://x.com/RLanceMartin/status/2095170001175199771) | Original body blocked; not read this pass | [sources-community.md](sources-community.md) |
| S34 | [Original](https://code.claude.com/docs/en/advisor) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S35 | [Original](https://platform.claude.com/cookbook/managed-agents-cma-consult-an-advisor) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S36 | [Original](https://platform.claude.com/cookbook/managed-agents-cma-coordinate-specialist-team) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S37 | [Original](https://platform.claude.com/cookbook/managed-agents-cma-verify-with-outcome-grader) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S38 | [Original](https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S39 | [Original](https://platform.claude.com/cookbook/patterns-agents-async-multi-agent-orchestration) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S40 | [Original](https://platform.claude.com/cookbook/tool-use-programmatic-tool-calling-ptc) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S41 | [Original](https://platform.claude.com/cookbook/tool-use-tool-search-with-embeddings) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S42 | [Original](https://github.com/anthropics/claude-cookbooks) | Original content inspected; full/selected scope specified in report | [sources-cookbooks.md](sources-cookbooks.md) |
| S43 | [Original](https://github.com/nvidia/skillspector) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S44 | [Original](https://github.com/anthropics/skills/tree/main/skills/claude-api) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S45 | [Original](https://github.com/VoltAgent/awesome-claude-code-subagents) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S46 | [Original](https://github.com/ZacheryGlass/.claude) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S47 | [Original](https://github.com/vercel-labs/agent-skills) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S48 | [Original](https://github.com/hardikpandya/stop-slop) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S49 | [Original](https://github.com/AIScientists-Dev/academic-humanizer) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S50 | [Original](https://github.com/blader/humanizer) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S51 | [Original](https://github.com/Imbad0202/academic-research-skills) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S52 | [Original](https://github.com/Imbad0202/academic-research-skills-codex) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S53 | [Original](https://github.com/OpenNSWM-Lab/FAROS) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S54 | [Original](https://github.com/lishix520/academic-paper-skills) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S55 | [Original](https://github.com/Spark-To-Paper-Skills/paperjury) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S56 | [Original](https://github.com/Master-cai/Research-Paper-Writing-Skills) | Original content inspected; full/selected scope specified in report | [sources-skills.md](sources-skills.md) |
| S57 | [Original](https://github.com/assafelovic/gpt-researcher) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S58 | [Original](https://github.com/hzwer/WritingAIPaper) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S59 | [Original](https://github.com/Orchestra-Research/AI-Research-SKILLs) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S60 | [Original](https://github.com/dzhng/deep-research) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S61 | [Original](https://github.com/Alibaba-NLP/DeepResearch) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S62 | [Original](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S63 | [Original](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#writing-density) | Relevant fragment of S62 read; same document | [sources-official.md](sources-official.md) |
| S64 | [Original](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#prefer-targeted-edits-over-whole-file-rewrites) | Relevant fragment of S62 read; same document | [sources-official.md](sources-official.md) |
| S65 | [Original](https://code.claude.com/docs/en/hooks) | Original content inspected; full/selected scope specified in report | [sources-official.md](sources-official.md) |
| S66 | [Original](https://addyosmani.com/blog/agent-harness-engineering/) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S67 | [Original](https://lilianweng.github.io/posts/2026-07-04-harness/) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S68 | [Original](https://github.com/DenisSergeevitch/agents-best-practices) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S69 | [Original](https://medium.com/@tort_mario/ai-agent-best-practices-production-ready-harness-engineering-2026-guide-c1236d713fac) | Original body blocked; not read this pass | [sources-research-memory.md](sources-research-memory.md) |
| S70 | [Original](https://iaee.substack.com/p/agent-harnesses-with-claude-intuitively) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S71 | [Original](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S72 | [Original](https://martinfowler.com/articles/harness-engineering.html) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| S73 | [Original](https://medium.com/data-science-collective/the-complete-guide-to-agent-harnesses-with-code-6fa11cecd004) | Original body blocked; not read this pass | [sources-research-memory.md](sources-research-memory.md) |
| X01 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w5o5zz/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| X02 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w5fed8/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| X03 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w59n28/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| X04 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w5tnlk/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| X05 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1w4qs4p/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| X06 | [Original](https://www.reddit.com/r/ClaudeCode/comments/1vojj88/) | Original content inspected; full/selected scope specified in report | [sources-community.md](sources-community.md) |
| X07 | [Original](https://github.com/paoloap-py/agent-harness-guide) | Original content inspected; full/selected scope specified in report | [sources-loop-repos.md](sources-loop-repos.md) |
| X08 | [Original](https://arxiv.org/html/2601.03315) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| X09 | [Original](https://arxiv.org/html/2605.26340) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| X10 | [Original](https://arxiv.org/html/2502.10517) | Original content inspected; full/selected scope specified in report | [sources-research-memory.md](sources-research-memory.md) |
| X11 | Local loop-engineering PDF | Complete extracted local PDF text read; visual layout not inspected | [sources-supplemental.md](sources-supplemental.md) |

## Supplemental URLs

| Original | Read-status home |
|---|---|
| [Original](https://www.makingsoftware.com) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://learn.chatgpt.com/docs/non-interactive-mode) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://learn.chatgpt.com/docs/agent-configuration/subagents) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://learn.chatgpt.com/docs/app-server) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://code.claude.com/docs/en/headless) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://code.claude.com/docs/en/agent-teams) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://code.claude.com/docs/en/workflows) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://openai.com/index/harness-engineering) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://code.claude.com/docs/en/goal) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://chatgpt.com/share/6aa49cf5-af98-83e8-b393-997152fa28fd) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://developers.openai.com/api/docs/guides/latest-model) | [sources-supplemental.md](sources-supplemental.md) |
| [Original](https://github.com/DenisSergeevitch/agents-best-practices/blob/main/SKILL.md) | [sources-supplemental.md](sources-supplemental.md) |

## Design changes and reuse

Read [source-informed-design.md](source-informed-design.md) for concrete source-to-design choices. Read [loop-design.md](loop-design.md) for native adapters, stage transitions, replay, checks, stop/steering, discovery and the export example. Read [memory-design.md](memory-design.md) for records, authority, capture, retrieval, correction and evaluated factory improvement. The accepted directions remain in [decisions.md](decisions.md).

Verified: current Loam completion and resume branches were reread during integration. The source register is historical: current baseline checks use a detached base worktree, and the workflow header no longer claims an independent checked plan. These differences are preserved in current-evidence.md. Old no-code/provider-incompatibility claims for S10/S02/S03 are corrected in the new design record, without rewriting the historical report.

Recommendation: original code/prose can be copied selectively when the chosen file and dependency closure have been read, the revision pinned, the terms resolved and required notices included in the seed. Current source reports distinguish pinned reviews from moving-branch reads that still need a pin before copying. No complete external framework is selected as the runtime.

## Access and scope limits

- Original bodies S24, S33, S69 and S73 remain blocked. Making Software returns HTTP 403. The shared ChatGPT memory conversation exposes a title but no body, and no browser surface is available. No content-based recommendation relies on these unread bodies.
- S25/S26 have only cached excerpts. Complete cached transcripts for S20/S22/S23 are text reads, not watched videos; no frame or audio inspection is claimed.
- Repository reads are selected implementation audits, not full repositories or transitive dependency audits. Relevant article prose was read where available; source charts and experimental results were not independently reproduced. Individual reports identify remaining sections, helpers and linked papers not inspected.
- The local loop guide is a secondary HuaShu synthesis, not established Anthropic authorship. Its extracted text was read; filename attribution and its dated native commands are not authority.
- Not done: permanent writing to the original review folder. This session can read it but its write policy permits only the repository and temporary roots, with no escalation. Updated records are staged here in /private/tmp/loam-architecture-design, separate from the original report.
- Not done: runtime implementation, live native probes, dependency installation, automation activation, commits, pushes or deployment. The user explicitly deferred runtime implementation. Proposed test commands and source-inspection findings are not passing-runtime claims.

## Verification and self-attack

The coverage check asserts every ledger ID maps to an existing report with an explicit source entry. A separate URL audit checks input inventory coverage. Artifact checks verify local document links, required design clauses and unchanged repository status. These checks validate the research/design records, not native-host enforcement or memory quality.

Self-attack: blocked originals could inherit credibility from old summaries, so status is explicit. A source-reported benchmark or demo can overstate applicability, so no Loam performance claim is inferred. A constructed context packet could be mistaken for source reading, so intended delivery, observed inclusion and inspection are distinct. A model violation could merely be logged, so the proposed loop now prohibits continuation and requires reconciliation/readmission.

## Expanded cookbook-native design audit

The user subsequently added the Claude cookbook catalog and repository plus the OpenAI cookbook repository and Codex topic. This expanded audit has independent reports: [Claude SDK/catalog](cookbook-claude-sdk-audit.md), [Claude patterns/Managed Agents](cookbook-claude-patterns-audit.md), [Codex](cookbook-codex-audit.md), [long-horizon originals](cookbook-long-horizon-audit.md), and [INDEX coverage and targeted gaps](cookbook-index-coverage.md). Their machine inventories distinguish source reading from metadata triage, selected dependency scope, images not inspected and explicit domain deferrals. The source-to-implementation decisions are in cookbook-practice-registry.md. This is expanded bounded evidence, not a full read of every repository or transitive bibliography.
