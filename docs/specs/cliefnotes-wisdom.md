# Clief Notes distilled wisdom

Working input for the Loam rebuild ledger.
Distilled from the Clief Notes lesson audit: 111 pages, 1,270 raw claims, normalized to 928 records.
This document reports what the SOURCE claims, not what Loam should do. No recommendations of my own are added.

Ledger: `soil/loam-rebuild-checkpoint/normalized-claims.jsonl` (one record per normalized claim; every raw_id appears in exactly one record).
The source corpus was machine-local during extraction. Lesson paths below are relative to that audited corpus.

## How to read a line

`Practice statement. [norm_id] n=<raw claims merged> <grade> - <representative source path>`

Source paths are relative to the Clief Notes root with the `html/courses/` prefix stripped.

`n=` is the number of raw claims that collapsed into the normalized record. High `n` means the source repeats the claim across lessons; it does NOT mean the claim is better evidenced.

Evidence grades map the ledger's free-text `evidence_in_source` onto the schema's five-rung ladder. Where a normalized record merges claims of different grades, the strongest is shown.

| Grade shown | Means |
|---|---|
| `demo` | something was demonstrated, run, or inspected in-page (worked example, executed check, inspected repository) |
| `linked` | evidence exists outside the page and was linked but not inspected, or an external standard is cited (OpenSSF, CISA, SBOM) |
| `community` | a community or third-party anecdote, case study, or implementation relayed by the author |
| `experience` | the author's own reported build, client, or production experience |
| `assert` | author recommendation, convention, rule, framework, or heuristic stated without support |

Blunt caveat: 594 of 928 normalized records (64 percent) grade `assert`. Only 118 (13 percent) reach `demo`. Treat almost everything below as a hypothesis the source asserts, not a finding the source proved.

## Coverage map

| Theme | Normalized | Raw claims |
|---|---|---|
| Folder structure / context routing | 247 | 341 |
| Plan and verification workflow | 265 | 340 |
| Automation and loops | 68 | 119 |
| Prompting | 69 | 93 |
| Agents and subagents | 66 | 80 |
| CLAUDE.md-style rules | 62 | 78 |
| Model and effort selection | 33 | 56 |
| Skills | 44 | 53 |
| Memory | 34 | 42 |
| Other (security, code craft, setup, business) | 34 | 62 |
| Hooks | 6 | 6 |

Hooks is the thinnest theme in the corpus: six raw claims, one of which is a Vue import-ordering rule misfiled by topic. The source has essentially nothing to say about hooks.

---

## 1. Folder structure and context routing

The largest and most repeated body of claims. The source's central thesis is that the filesystem is the architecture.

### Core architecture

- Load only the context the current task or stage needs; never load the whole workspace by default, even when the model has a large context window. `N-0023` n=9 linked - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Let the filesystem carry the architecture: treat the folder system as the workflow application and the agent's interface. `N-0148` n=7 experience - `08-davids-corner/01-04-this-ones-goldenvibe-coding-rules.html`
- Separate planning, source code, documentation, and operations into their own workspaces in a software project. `N-0043` n=9 assert - `02-the-foundation/04-02-32-customizing-for-your-use-case.html`
- Put a routing table in CLAUDE.md that maps each task type to the files or workspaces to read, the ones to skip, and any skills it needs. `N-0029` n=5 demo - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Keep each fact and each core rule in exactly one authoritative location; let that canonical copy override secondary guides when they disagree. `N-0058` n=5 demo - `02-the-foundation/05-05-45-where-this-goes.html`
- Design context as an explicit layered hierarchy (model defaults, global instructions, working context, retrieved material, persistent memory) so each agent receives only relevant material. `N-0022` n=3 linked - `02-the-foundation/03-03-23-how-a-1953-word-game-explains-ai-memory.html`
- Use Markdown as the format for project instruction, context, stage, and workflow files, with plain text as the fallback. `N-0007` n=6 assert - `02-the-foundation/02-02-12-your-first-folder.html`
- Treat the folder architecture and its durable artifacts as the project's source of truth and part of its definition. `N-0094` n=2 assert - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Treat disagreement between duplicated rule copies as a bug. `N-0106` n=1 demo - `05-the-vault/03-02-comp-9-the-editor.html`

### Per-area context files

- Give each workspace its own context file describing its purpose, process, organization, and relevant tools. `N-0030` n=2 demo - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Make project facts, audience, prior work, constraints, and examples of good output the majority of a context file, and keep generic behavioral instruction to about one fifth of it. `N-0048` n=2 experience - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Keep stable configuration (voice, format, business rules, domain, templates, skill assets) in dedicated reference areas, separate from run-specific stage work. `N-0101` n=3 linked - `05-the-vault/01-03-the-vault-toolkit.html`
- Separate voice and tone, format patterns, and hard constraints into different files. `N-0096` n=1 linked - `05-the-vault/01-03-the-vault-toolkit.html`
- Trim oversized context and method files (roughly 150 lines and up) by tightening structure and sharpening scoping. `N-0180` n=3 assert - `08-davids-corner/03-04-my-ai-workflow-evolution.html`
- Delete instructions, context, and template sections that no longer serve a clear purpose. `N-0133` n=2 assert - `08-davids-corner/03-04-my-ai-workflow-evolution.html`
- Add a last-updated marker when it will help maintainers notice stale context. `N-0049` n=1 community - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`

### Sizing and growth

- Start a workspace with the three core files - CLAUDE.md, CONTEXT.md, REFERENCES.md - before building anything larger. `N-0006` n=3 assert - `02-the-foundation/02-02-12-your-first-folder.html`
- Start with two to four workspaces matching your major work modes and add more only after use proves the need. `N-0046` n=3 community - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Create separate workspaces for different kinds of work (distinct mental modes), not merely for stages of the same mode. `N-0027` n=2 assert - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Keep an uncertain work area as a subfolder until repeated use justifies a separate workspace. `N-0047` n=1 assert - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Introduce subfolders when a single directory grows beyond roughly eight to ten files. `N-0050` n=1 assert - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Group files first by kind of work, then by stage or type within that work area. `N-0051` n=1 assert - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Give each directory one clear purpose, and make directory depth match conceptual depth. `N-0205` / `N-0206` n=1 assert - `08-davids-corner/04-03-advanced-coding-best-practices.html`
- Keep each repository file responsible for one job. `N-0113` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Use a self-documenting, self-describing nested folder tree instead of one flat directory of unnamed files. `N-0073` n=2 linked - `05-the-vault/01-03-the-vault-toolkit.html`
- Define predictable file and folder naming conventions per artifact type and version, and use them as lightweight metadata before adding a database. `N-0031` n=2 assert - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`

### Staged pipelines

- Use numbered stage folders to encode workflow order instead of orchestration code when the sequence is simple. `N-0155` n=3 assert - `08-davids-corner/01-06-the-golden-rules.html`
- Make each stage's output directory the next stage's input. `N-0157` n=2 assert - `08-davids-corner/01-06-the-golden-rules.html`
- Define stage contracts with explicit inputs, process steps, and completion criteria, and standardize their structure. `N-0097` n=3 linked - `05-the-vault/01-03-the-vault-toolkit.html`
- Put an explicit Inputs table in every stage contract that names required files and sections. `N-0289` n=1 assert - `08-davids-corner/01-06-the-golden-rules.html`
- Break work into narrow sequential stages. `N-0156` n=1 assert - `08-davids-corner/01-06-the-golden-rules.html`

### Templates and starters

- Rename the starter's workspaces and rewrite their context to match the actual work, while preserving the map / rooms / tools layering. `N-0032` n=9 assert - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Replace every bracketed template placeholder with actual project information. `N-0132` n=2 assert - `05-the-vault/06-07-production-claudemd-examples.html`
- Run the starter's self-audit and let it reshape the starter folder instead of treating the template as finished. `N-0124` n=2 assert - `05-the-vault/04-05-afternoon-tea-6-second-brain-chat.html`
- Duplicate a repeatable client-template folder for each engagement, writing a new context file and adding one routing entry. `N-0042` n=3 assert - `02-the-foundation/04-02-32-customizing-for-your-use-case.html`
- Annotate reusable architecture files with their context layer, purpose, and expected variation points. `N-0100` n=1 linked - `05-the-vault/01-03-the-vault-toolkit.html`

---

## 2. CLAUDE.md-style rules

The source treats CLAUDE.md as a router, then immediately loads it with content mandates. See the contradictions section.

- Place a concise CLAUDE.md at the project root and use it mainly as the project's map and router, not as a detail store. `N-0252` n=6 community - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Keep CLAUDE.md short - roughly one screen, thirty to fifty lines - and route to detailed files. `N-0249` n=3 assert - `02-the-foundation/02-02-12-your-first-folder.html`
- Keep only always-needed instructions global; move area- or stage-specific detail into local context files. `N-0251` n=3 assert - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Write CLAUDE.md as the agent's job description - day-one onboarding for a smart new project member. `N-0260` n=2 assert - `08-davids-corner/03-03-do-you-have-a-soul.html`
- Summarize the project's purpose in two or three sentences in CLAUDE.md. `N-0255` n=1 assert - `02-the-foundation/05-04-44-making-claude-understand-your-project.html`
- Record the actual technology stack (languages, frameworks, databases, tools) in CLAUDE.md. `N-0256` n=2 assert - `02-the-foundation/05-04-44-making-claude-understand-your-project.html`
- Record the verified development, test, and build commands in CLAUDE.md. `N-0257` n=2 assert - `02-the-foundation/05-04-44-making-claude-understand-your-project.html`
- Record code, naming, file-layout, and architectural conventions in CLAUDE.md. `N-0258` n=3 experience - `02-the-foundation/05-04-44-making-claude-understand-your-project.html`
- Record an avoid-list in CLAUDE.md naming the libraries, patterns, and files the agent must not use or modify. `N-0259` n=2 assert - `02-the-foundation/05-04-44-making-claude-understand-your-project.html`
- Reference constraint files from the project's CLAUDE.md rather than inlining them. `N-0273` n=1 assert - `05-the-vault/01-03-the-vault-toolkit.html`
- Require the agent to ask before creating files outside the designated drafts area. `N-0253` n=1 assert - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Encode client confidentiality boundaries in the root instructions of a multi-client project. `N-0286` n=2 assert - `05-the-vault/06-07-production-claudemd-examples.html`
- Audit borrowed CLAUDE.md files, role files, and agent prompts for embedded beliefs before adopting them. `N-0306` n=1 assert - `08-davids-corner/07-05-worldview-engineering.html`
- Read the root CLAUDE.md before changing the template. `N-0281` n=1 assert - `05-the-vault/06-02-workspace-blueprint-full-template.html`
- Enforce editorial rules with offline checkers that inspect the editor's output. `N-0275` n=1 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Name disguised requests for prohibited output in the rules before users discover them. `N-0276` n=1 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Design output schemas with no field that can carry prohibited content. `N-0277` n=1 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Keep domain rules in one swappable file. `N-0105` n=1 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Encode who the system serves, what it refuses, preconditions for action, required proof, and forbidden tradeoffs. `N-0302` n=1 assert - `08-davids-corner/07-04-a-system-worth-amplifying.html`
- Mine a corpus of real conversations for repeated operating rules; write the actual learned rules, not framework names or slogans. `N-0301` n=1 experience - `08-davids-corner/07-04-a-system-worth-amplifying.html`

---

## 3. Skills

- Package repeated workflows, instructions, standards, and processes as reusable skills instead of re-pasting the same context into every prompt. `N-0310` n=4 assert - `08-davids-corner/03-06-have-you-figured-out-the-code.html`
- Represent skills as on-demand tooling rather than always-loaded context. `N-0311` n=1 assert - `02-the-foundation/03-03-23-how-a-1953-word-game-explains-ai-memory.html`
- Wire each skill or tool only into the workspaces that need it, rather than loading them globally. `N-0313` n=2 assert - `02-the-foundation/04-01-31-the-full-walkthrough-23-min-video.html`
- Add a skills column to the routing table only when the project actually routes skills. `N-0314` n=3 assert - `02-the-foundation/04-02-32-customizing-for-your-use-case.html`
- Wire skills into the workspace as a separate tools layer. `N-0335` n=1 assert - `05-the-vault/06-03-claude-skills-manual.html`
- Turn a manual checklist into a repeatable, portable harness - a skill folder holding SKILL.md, a deterministic script, and a rubric. `N-0340` n=2 assert - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`
- Prefer the scripted skill to the copy-paste evaluator prompt when scripts can run. `N-0347` n=1 assert - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`
- Use SKILL.md as a reusable manual for specialized workflows. `N-0349` n=1 assert - `08-davids-corner/03-03-do-you-have-a-soul.html`
- Have workspace-building skills ask diagnostic questions before generating a structure, then assemble the workspace from the answers. `N-0328` / `N-0329` n=1 linked - `05-the-vault/01-03-the-vault-toolkit.html`
- Study a specialized skill's prompts, examples, guidelines, and encoded domain principles before creating a new one. `N-0325` n=2 linked - `04-building-your-stack/01-04-14-repo-tour-open-source-references.html`
- Account for context-token cost when deciding whether and how to use a skill. `N-0330` n=1 assert - `05-the-vault/04-02-session-2---42526.html`
- Inspect downloaded skills for prompt-injection risk before installing or running them. `N-0331` n=1 assert - `05-the-vault/04-02-session-2---42526.html`
- Treat cloning a repository, installing a skill or plugin, pasting an action, or running a CLI as a trust decision. `N-0339` n=1 assert - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`
- For each tool-specific AI skill, identify and learn the transferable pattern underneath it. `N-0333` n=1 assert - `05-the-vault/05-02-lesson-13-the-system-underneath.html`
- Advance incrementally from copy-and-paste to skills and then to routed folders with an agent. `N-0332` n=1 assert - `05-the-vault/04-05-afternoon-tea-6-second-brain-chat.html`
- Package a multi-part workflow as a plugin when it must be shared, installed, improved, audited, or scaled. `N-0351` n=1 assert - `08-davids-corner/03-06-have-you-figured-out-the-code.html`
- Ask Claude to identify the right skill for the task currently being performed. `N-0337` n=1 assert - `05-the-vault/06-03-claude-skills-manual.html`

---

## 4. Hooks

The entire hook corpus. Six raw claims, no merges, no demonstrated evidence.

- Use a hook when a check or action must run automatically before or after a task. `N-0356` n=1 assert - `08-davids-corner/03-06-have-you-figured-out-the-code.html`
- Use terminal hooks to synchronize file-based task state across machines. `N-0359` n=1 community - `08-davids-corner/05-06-a-completely-markdown-based-task-management-system.html`
- Make the agent halt and report that approval is required while the approval file is empty. `N-0357` n=1 assert - `08-davids-corner/03-08-stop-automating-your-frustration-audit-it-first.html`
- Use explicit conversational keywords as triggers when connecting meetings to agent actions. `N-0354` n=1 assert - `02-the-foundation/01-01-01-where-all-of-this-leads.html`
- Use SOUL.md to define an agent's personality, values, and firm boundaries. `N-0355` n=1 assert - `08-davids-corner/03-03-do-you-have-a-soul.html`
- (Misfiled by topic keyword: `N-0358`, a Vue lifecycle-hook ordering rule. Not about harness hooks.)

Adjacent, filed under workflow but functionally hook-shaped:

- Implement critical guarantees as blocking code, calculators, or schema checks rather than prose-only instructions. `N-0563` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Use a self-tested blocking gate for a non-negotiable safety rule. `N-0565` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Back every named verifier gate with a negative fixture. `N-0580` n=2 demo - `05-the-vault/03-02-comp-9-the-editor.html`

---

## 5. Agents and subagents

- Give the agent explicit boundaries against requesting credentials, making financial requests, revealing private user data, making unsupported promises, and bypassing access controls. `N-0391` n=5 assert - `08-davids-corner/02-03-comprehensive-guide-to-clief-notes-ai.html`
- Route work through one agent first and master it before building a larger agent stack. `N-0360` n=3 demo - `08-davids-corner/07-03-the-5-levels-of-ai-mastery.html`
- Put a routing orchestrator above the specialists, combining the assistant and context folders needed for each job, instead of routing every request manually. `N-0361` n=3 experience - `08-davids-corner/07-03-the-5-levels-of-ai-mastery.html`
- Surround the builder with specialized agents for distinct roles - analysis, planning, implementation - to expand throughput beyond a one-agent workflow. `N-0393` n=2 experience - `08-davids-corner/03-05-building-companies-intelligence-layers.html`
- Give each specialist its own role, context, and job in a plain-text folder structure. `N-0238` n=1 experience - `08-davids-corner/07-03-the-5-levels-of-ai-mastery.html`
- Load the doctrine and rules layer before every agent, specialist, and session produces work. `N-0414` n=2 demo - `08-davids-corner/07-04-a-system-worth-amplifying.html`
- Give global coding rules to the orchestrating agent rather than duplicating them in each stage. `N-0381` n=1 assert - `08-davids-corner/01-04-this-ones-goldenvibe-coding-rules.html`
- Delegate independent repository study, workspace inspection, or component implementation to scoped sub-agents during a complex build. `N-0369` n=1 assert - `04-building-your-stack/01-03-13-designing-for-your-use-case.html`
- Give concurrent Claude Code sessions distinct work areas while sharing one root context. `N-0367` n=1 assert - `03-implementation-playbooks/04-02-32-github-and-folder-structure.html`
- Model most deployed agents as prompts sequenced by traditional orchestration code rather than as a single autonomous intelligence. `N-0363` n=1 assert - `02-the-foundation/03-07-27-from-nazi-psychology-to-ai-auditing.html`
- Use queues, concurrency controls, ordered dispatch, completion tracking, and retries around parallel model calls. `N-0364` n=1 experience - `02-the-foundation/03-07-27-from-nazi-psychology-to-ai-auditing.html`
- Parse probabilistic natural-language responses into deterministic structured values before scoring or analysis. `N-0365` n=1 assert - `02-the-foundation/03-07-27-from-nazi-psychology-to-ai-auditing.html`
- Let the agent run unmonitored when it has a clear specification and no expected decision point. `N-0373` n=2 assert - `04-building-your-stack/02-03-23-mobile-workflow-patterns.html`
- Check in when the task reaches a decision point the agent cannot resolve, or when an ambiguous instruction may need early correction. `N-0374` n=2 assert - `04-building-your-stack/02-03-23-mobile-workflow-patterns.html`
- Instruct the agent to state uncertainty explicitly and to say when material is absent rather than inventing it. `N-0290` n=1 assert - `08-davids-corner/02-03-comprehensive-guide-to-clief-notes-ai.html`
- Ask the agent for a bounded starting sequence, the exact first artifact, and a definition of done. `N-0384` / `N-0385` / `N-0386` n=1 assert - `08-davids-corner/02-03-comprehensive-guide-to-clief-notes-ai.html`
- Write an Agent Charter that defines what AI may and may not handle in the given context. `N-0379` n=1 assert - `06-the-archive/02-02-lesson-22-raise-the-bar.html`
- Define field-level or column-level boundaries for what an agent may write, propose, or never change. `N-0376` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Track official session references and working, blocked, or idle states for every coding agent. `N-0409` n=1 assert - `08-davids-corner/06-03-attn-keyboard-warriors-introducing-herdrdev.html`
- Use the multi-agent loop spawn, monitor, detach, resume, then hand off. `N-0410` n=1 assert - `08-davids-corner/06-03-attn-keyboard-warriors-introducing-herdrdev.html`
- Do not let the producing agent perform the final verification of its own output. `N-0705` n=1 assert - `08-davids-corner/07-04-a-system-worth-amplifying.html`
- Combine complementary reasoning styles so one agent gathers or generates and another evaluates. `N-0424` n=1 assert - `08-davids-corner/07-09-cognitive-architecture-for-ai-agents.html`
- Choose an agent's reasoning style from how it should approach the task, not only from the task label. `N-0422` n=1 assert - `08-davids-corner/07-09-cognitive-architecture-for-ai-agents.html`

---

## 6. Memory

- Externalize important state in durable workspace files and use them as the memory layer across agent sessions instead of relying on model memory. `N-0430` n=2 linked - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Record important decisions together with their reasons in durable project files, as architecture decision records for systems another person or agent must take over. `N-0432` n=4 linked - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Persist the actual work products - code, specifications, PRD, outputs - in the workspace. `N-0431` n=2 assert - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Use plain Markdown files and directories for agent memory, identity, and workflow instructions before adding a database or vector store. `N-0448` n=2 community - `08-davids-corner/03-03-do-you-have-a-soul.html`
- Record only session details that would be costly or frustrating to lose. `N-0433` n=1 assert - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Use session synchronization for short-term continuity and workspace files for cross-session continuity. `N-0434` n=1 assert - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Tag each fact with its source. `N-0436` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Let repository evidence override remembered information when the two conflict. `N-0437` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Populate designed memories, correction logs, archives, and pattern logs with real entries before claiming that the system learns. `N-0435` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Persist open tasks, recent activity, and project threads so an agent can restore context between sessions. `N-0453` n=1 community - `08-davids-corner/05-02-helping-your-ai-remember-tasks-between-sessions.html`
- Keep doctrine memory in human-readable folders when future operators must inspect what the system protected. `N-0455` n=1 experience - `08-davids-corner/07-04-a-system-worth-amplifying.html`
- Put costly lessons and corrections into agent context instead of relying on generic principles. `N-0421` n=1 community - `08-davids-corner/07-07-the-mirror-and-the-window.html`
- Write down a correction mechanism that makes the human the training loop, then run it for a meaningful period and commit its trace. `N-0569` (demo) / `N-0438` / `N-0439` n=1 - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Capture one recurring conversation before expanding the system. `N-0440` n=1 assert - `05-the-vault/04-05-afternoon-tea-6-second-brain-chat.html`

---

## 7. Plan and verification workflow

The second-largest theme, and the one with the highest share of demonstrated evidence.

### Plan before build

- Front-load conversational brainstorming to surface assumptions and blind spots before asking for a finished artifact. `N-0483` n=2 community - `08-davids-corner/05-03-i-run-four-phases-before-any-ai-builds-anything.html`
- Generate a product requirements document before any implementation code. `N-0508` n=2 demo - `03-implementation-playbooks/04-01-31-build-and-deploy-a-website.html`
- Read, review, and edit the generated PRD before allowing the build to begin. `N-0509` n=3 assert - `03-implementation-playbooks/04-01-31-build-and-deploy-a-website.html`
- Make the PRD record the source repositories and their stacks, the retained and removed features, the desired layout, and phased ordered implementation steps. `N-0519` n=2 assert - `04-building-your-stack/01-01-11-starting-the-build-process.html`
- Audit a proposed PRD in a separate model session for over-complexity, omissions, and simplification opportunities. `N-0521` n=1 assert - `04-building-your-stack/01-02-12-how-i-use-claude-code-in-the-build-process.html`
- Use plan mode for a complex build and inspect the plan before approving execution. `N-0524` n=1 demo - `04-building-your-stack/01-03-13-designing-for-your-use-case.html`
- Write the clarified plan and its context into one Markdown handoff document for the build phase. `N-0689` n=2 community - `08-davids-corner/05-03-i-run-four-phases-before-any-ai-builds-anything.html`
- Plan in one session and hand the handoff file to a fresh session for implementation. `N-0719` n=2 experience - `09-the-legends/02-08-dont-let-being-new-stop-you.html`
- Define clear specifications and scenario-based validations before asking an AI system to generate code. `N-0665` n=2 linked - `08-davids-corner/03-04-my-ai-workflow-evolution.html`
- Focus design effort on the fragile handoff or irregular middle of the workflow. `N-0718` n=1 experience - `09-the-legends/02-08-dont-let-being-new-stop-you.html`

### Session continuity

- At session start, have the agent read the project map, PRD, and progress file, inspect what has actually been built, and summarize current state and next work. `N-0543` n=5 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- At session end, update the progress file with what was actually accomplished and the next step. `N-0546` n=3 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Structure the progress file around current status, completed, in-progress, blocked, next work, decisions made, and open questions. `N-0545` n=2 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Keep the PRD in the workspace and explicitly reload it at each session boundary to reorient the agent and force scope decisions. `N-0520` n=4 experience - `04-building-your-stack/01-01-11-starting-the-build-process.html`
- Start a fresh session rather than pushing through a nearly full or degraded context window. `N-0525` n=2 experience - `04-building-your-stack/01-03-13-designing-for-your-use-case.html`
- Verify the progress record against the actual code and files before continuing. `N-0550` n=1 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Verify that the agent's orientation summary matches the user's understanding before continuing. `N-0549` n=1 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Continue from a specific verified next task rather than a vague instruction to resume. `N-0551` n=1 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- After an unexpected session end, do not assume the last agent task completed - inspect the actual files to see whether the promised work exists. `N-0552` n=2 assert - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Update status documents to the observed state rather than the expected state. `N-0554` n=1 assert - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- When the implementation drifts, point the agent back to the PRD and require adjustment. `N-0526` n=1 experience - `04-building-your-stack/01-03-13-designing-for-your-use-case.html`

### Verification and gates

- Execute every shipped self-test and checker during review rather than accepting its existence as proof. `N-0572` n=2 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Independently reproduce every checkable claim, including README claims, during review. `N-0562` n=2 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Use named verification gates for quoted text, commit identifiers, and file paths. `N-0595` n=3 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Back every named verifier gate with a negative fixture. `N-0580` n=2 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Verify that a checker accepts every output form mandated by its own rules. `N-0601` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Test checks against violations in different paragraph positions and formats. `N-0600` n=1 assert - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Make underdetermined cases reach the explicit underdetermined path in tests. `N-0603` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- State system claims precisely enough to falsify, and keep the runs that falsify them. `N-0593` / `N-0576` n=1-3 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Publish the run that disproves a claim, patch the rules from the failure, and rerun. `N-0576` n=3 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Declare the evaluation method before testing begins and preserve evaluation inputs byte for byte. `N-0574` / `N-0575` n=1 demo - `05-the-vault/03-02-comp-9-the-editor.html`
- Commit predictions to git before each evaluation run. `N-0594` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Maintain an OPEN-DEFECTS file that records known holes before external review. `N-0596` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Write a judge guide whose purpose is to falsify the build. `N-0597` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Require human review even after a green automated gate. `N-0598` n=1 demo - `05-the-vault/03-03-comp-10-the-diagnostician.html`
- Insert a human review gate between stages, and whenever a stage output would be expensive to undo. `N-0634` n=2 assert - `08-davids-corner/01-06-the-golden-rules.html`
- Allow humans to edit artifacts at stage boundaries and continue without restarting the workflow. `N-0633` n=1 assert - `08-davids-corner/01-06-the-golden-rules.html`
- Limit README claims to behavior a stranger can verify from a fresh clone. `N-0570` n=1 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Verify that context is earning its place by running the same task with and without the folder context or CLAUDE.md and comparing the outputs. `N-0464` n=3 assert - `02-the-foundation/02-02-12-your-first-folder.html`
- Read every generated file and inspect the workflow for gaps; describe each gap to the agent, let it draft the repair, then check the repair. `N-0720` / `N-0721` n=1 experience - `09-the-legends/02-08-dont-let-being-new-stop-you.html`
- Use a read, think, write, check, adjust loop and repeat it until the workflow holds. `N-0480` n=2 experience - `02-the-foundation/05-02-42-claude-code-in-practice.html`

### Scope discipline

- Begin with the minimum viable instruction set and workspace structure, then revise it from observed use. `N-0477` n=6 community - `02-the-foundation/04-03-33-common-mistakes-and-how-to-fix-them.html`
- Choose the simplest interface level that solves the workflow problem before building a custom front end. `N-0266` n=1 assert - `04-building-your-stack/01-01-11-starting-the-build-process.html`
- Fix the single largest leak in the workflow before optimizing smaller ones. `N-0615` n=1 assert - `05-the-vault/05-01-lesson-12-the-partnership-nlp-logix.html`
- Prototype the cheapest measurable fix before investing in the expensive solution. `N-0769` n=1 assert - `05-the-vault/06-01-the-prompt-library.html`
- Solve the workflow for one user, then validate it for ten, and only then scale it. `N-0278` n=1 assert - `05-the-vault/04-02-session-2---42526.html`
- Delay software construction until the manual solution's scale limits show what the software must do. `N-0770` n=1 assert - `05-the-vault/06-01-the-prompt-library.html`
- Run a removal test by substituting a different technology for AI and checking whether the system still works. `N-0612` n=1 community - `05-the-vault/05-01-lesson-12-the-partnership-nlp-logix.html`
- Classify each problem or task as AI, traditional code, human judgment, or not worth building, and sequence the layers when a task needs more than one. `N-0473` n=4 experience - `06-the-archive/02-01-lesson-21-the-mindset-before-the-method.html`
- Classify each bottleneck as missing infrastructure, missing orchestration, or missing AI capability before proposing a tool. `N-0616` n=2 experience - `05-the-vault/05-02-lesson-13-the-system-underneath.html`
- Preserve existing databases, storage, routing, and approval chains that already work. `N-0279` n=1 assert - `05-the-vault/05-02-lesson-13-the-system-underneath.html`

### Learning from other repos

- Study and read existing reference repositories before implementing a custom tool. `N-0517` n=4 experience - `04-building-your-stack/01-01-11-starting-the-build-process.html`
- Borrow the useful parts and drop the features the target workflow does not need, rather than importing a whole project or hunting for one perfect off-the-shelf solution. `N-0518` n=4 assert - `04-building-your-stack/01-01-11-starting-the-build-process.html`
- Select reference repositories relevant to the system being built instead of cloning every example. `N-0268` n=1 assert - `04-building-your-stack/01-04-14-repo-tour-open-source-references.html`
- Treat reference architectures as material to inspect and adapt, not as theoretical claims or templates to paste unchanged. `N-0103` n=1 linked - `05-the-vault/01-03-the-vault-toolkit.html`

---

## 8. Prompting

- Invest in structured context, constraints, and stage contracts rather than in engineering one perfect prompt or collecting isolated prompt tips. `N-0732` n=5 assert - `05-the-vault/01-03-the-vault-toolkit.html`
- Structure task prompts with typed slots - identity, task, context, constraints, output format - and treat those slots as error-handling structure around generation. `N-0733` n=2 assert - `02-the-foundation/03-02-22-one-line-of-python-triggers-12k-lines-of-code.html`
- Keep persistent identity, project context, and standing rules in files, while putting the current task and current constraints in each prompt. `N-0730` n=1 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Supply the goal, background, project, audience, decisions, data, and constraints the model cannot know on its own. `N-0725` n=2 community - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Start by describing the outcome and the problem rather than naming only the artifact you want produced. `N-0736` n=2 community - `02-the-foundation/05-03-43-claude-desktop-as-a-thinking-partner.html`
- Specify the required shape of the result - table, list, code block, CSV, JSON - matched to the downstream consumer. `N-0728` n=3 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- State unwanted language, styles, tools, length, structure, and other prohibited outcomes as explicit constraints. `N-0727` n=2 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Require the model to surface alignment questions before it writes any code. `N-0744` n=2 demo - `03-implementation-playbooks/04-01-31-build-and-deploy-a-website.html`
- Ask the model to confirm its understanding of the context or spec before it proposes or implements a solution. `N-0747` n=2 demo - `08-davids-corner/04-01-leaked-ten-prompts-from-experts.html`
- Ask the model to state its assumptions, flag uncertainties, and assign confidence before its final answer. `N-0776` n=3 community - `08-davids-corner/04-01-leaked-ten-prompts-from-experts.html`
- Ask the model to show a step-by-step reasoning process before its final recommendation. `N-0780` n=1 community - `08-davids-corner/04-01-leaked-ten-prompts-from-experts.html`
- Tell the model what has already been tried. `N-0813` n=1 community - `08-davids-corner/04-01-leaked-ten-prompts-from-experts.html`
- Ask for one clear thing per prompt when a project is larger than one prompt can handle, and review between prompt-sized steps. `N-0731` n=1 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Write stage-specific contracts instead of one monolithic prompt. `N-0774` n=1 assert - `08-davids-corner/01-06-the-golden-rules.html`
- Do not combine research and writing in the same stage. `N-0773` n=1 assert - `08-davids-corner/01-06-the-golden-rules.html`
- When output is generic or off target, add the missing context and improve input clarity before changing models. `N-0726` n=2 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Treat the first model response as a draft and push back by asking what is wrong, missing, or opposed. `N-0486` n=2 assert - `02-the-foundation/05-03-43-claude-desktop-as-a-thinking-partner.html`
- Have the model ask discovery questions one at a time and wait for the user's answer before mapping the workflow. `N-0763` n=2 assert - `05-the-vault/05-01-lesson-12-the-partnership-nlp-logix.html`
- Organize a prompt library by the session or problem each prompt solves, and encode a specific decision framework inside each reusable prompt. `N-0766` / `N-0765` n=1 assert - `05-the-vault/06-01-the-prompt-library.html`
- Fill prompt placeholders with specific operational facts rather than broad role descriptions. `N-0767` n=1 assert - `05-the-vault/06-01-the-prompt-library.html`
- Break long documents or datasets into structured sections, supply the table of contents first, feed sections in order, and wait until all sections are supplied before requesting whole-source analysis. `N-0015` to `N-0019` n=1 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Preserve spreadsheet and table inputs in their structured form instead of converting them to prose. `N-0020` n=1 assert - `02-the-foundation/02-03-13-how-to-structure-any-prompt.html`
- Use a prompt for a temporary or one-time task; package anything repeated. `N-0778` n=1 assert - `08-davids-corner/03-06-have-you-figured-out-the-code.html`

---

## 9. Model and effort selection

- Use deterministic traditional code for everything that does not need language-model synthesis, and reserve model calls for genuinely semantic tasks such as summarization, extraction, generation, and comparison against a standard. `N-0796` n=7 experience - `02-the-foundation/03-01-21-video-text-guide-series-overview.html`
- Compute exact results - counts, sums, dates, scores, rankings, stable textual patterns - with deterministic scripts and verifiers, and let the model only apply semantic labels and presentation. `N-0801` n=7 demo - `05-the-vault/03-01-comp-8-the-wildcard.html`
- Use the 60/30/10 split as a design heuristic: most of an AI tool is traditional integration code, a smaller part is rule-based routing and security, and about one tenth is model processing. `N-0795` n=4 linked - `02-the-foundation/03-01-21-video-text-guide-series-overview.html`
- Use explicit rule-based logic for decisions that need constraints but not open-ended synthesis. `N-0425` n=1 assert - `06-the-archive/03-03-lesson-33-the-real-cost-of-knowledge.html`
- Build AI systems so the model is a component and the surrounding architecture is the product. `N-0797` n=1 assert - `02-the-foundation/03-01-21-video-text-guide-series-overview.html`
- Keep model intelligence behind replaceable hooks rather than embedding one provider throughout the orchestration code. `N-0362` n=1 assert - `02-the-foundation/03-05-25-openclaw-has-350k-stars.html`
- Prefer the conversational interface for planning, ideas, questions, and drafts, and Claude Code in an editor for building and editing files inside a project. `N-0802` n=3 experience - `02-the-foundation/05-02-42-claude-code-in-practice.html`
- Reserve frontier models for architecture and hard multi-step reasoning. `N-0247` n=1 assert - `09-the-legends/02-09-tokens-deepseek-managing-context.html`
- Use a small local model for repetitive high-volume reformatting, summarization, drafting, classification, renaming, and first-pass extraction. `N-0822` n=1 assert - `09-the-legends/02-09-tokens-deepseek-managing-context.html`
- Use a more autonomous model for multi-step research, tool use, and self-correcting code workflows. `N-0406` n=1 assert - `08-davids-corner/06-01-gpt-55-what-actually-changed.html`
- Do not pay for an autonomy-focused model upgrade when the workflow is only single-turn drafting or summarization. `N-0818` n=1 assert - `08-davids-corner/06-01-gpt-55-what-actually-changed.html`
- Compare candidate models on the same task the workflow actually performs, including tool behavior, failure points, token use, and cost. `N-0819` n=2 linked - `09-the-legends/02-09-tokens-deepseek-managing-context.html`
- Treat model benchmarks as directional signals rather than guarantees for a specific workflow. `N-0816` n=1 linked - `08-davids-corner/06-01-gpt-55-what-actually-changed.html`
- Calculate model cost from the workload's actual token use rather than assuming an efficiency claim will save money. `N-0817` n=1 assert - `08-davids-corner/06-01-gpt-55-what-actually-changed.html`
- Maintain a compatible local or alternative model path for production work when usage limits, cost, privacy, or offline needs matter. `N-0803` n=2 experience - `03-implementation-playbooks/02-01-claude-design-folder-structure-as-a-design-system.html`
- Diagnose unexpected spend before switching models; find the highest-spend days first, then inspect the largest sessions. `N-0821` / `N-0722` / `N-0823` n=1 assert - `09-the-legends/02-09-tokens-deepseek-managing-context.html`
- Measure token usage per stage and refine context selection from it. `N-0636` n=1 community - `08-davids-corner/01-06-the-golden-rules.html`
- Treat every retrieved document as potentially executable instruction because model context does not enforce a code-data boundary. `N-0798` n=1 assert - `02-the-foundation/03-03-23-how-a-1953-word-game-explains-ai-memory.html`

---

## 10. Automation and loops

- Automate the repetitive, mechanical load - transcription, glue work, templated writing, routine analysis - and keep human attention on judgment, ambiguity, strategy, and taste. `N-0828` n=7 community - `08-davids-corner/03-02-flip-the-script---its-all-about-the.html`
- Map and audit the manual workflow, decomposed into individual tasks, before deciding what to automate or building end-to-end automation. `N-0827` n=4 community - `06-the-archive/02-03-lesson-23-more-human.html`
- Decide explicitly which parts of a workflow to automate and which to protect for human work. `N-0877` n=2 experience - `06-the-archive/02-03-lesson-23-more-human.html`
- Score each candidate workflow for impact and for failure risk on a one-to-five scale. `N-0885` n=2 assert - `08-davids-corner/03-08-stop-automating-your-frustration-audit-it-first.html`
- Raise a workflow's risk assessment when its output binds the business, reaches a customer, feeds other systems, or could damage trust with partners or regulators. `N-0886` n=4 assert - `08-davids-corner/03-08-stop-automating-your-frustration-audit-it-first.html`
- Reserve end-to-end automation with minimal human touch for high-impact, low-risk workflows. `N-0887` n=1 assert - `08-davids-corner/03-08-stop-automating-your-frustration-audit-it-first.html`
- Use the consequence of failure as the main test for whether an action stays manual, needs approval, or can be automated. `N-0848` n=1 assert - `03-implementation-playbooks/03-04-24-inbox-and-scheduling-on-autopilot.html`
- Begin automation of a risky surface with read-only summarization before allowing actions. `N-0843` n=1 assert - `03-implementation-playbooks/03-04-24-inbox-and-scheduling-on-autopilot.html`
- Automate only low-consequence actions without per-action review; allow routine actions with review; keep consequential actions manual. `N-0847` / `N-0846` / `N-0263` n=1 assert - `03-implementation-playbooks/03-04-24-inbox-and-scheduling-on-autopilot.html`
- Prefer copy-and-paste handoffs to premature automation. `N-0875` n=1 community - `05-the-vault/04-01-session-1--4182026.html`
- Distinguish automation from scaling. `N-0874` n=1 linked - `05-the-vault/01-03-the-vault-toolkit.html`
- Prioritize automation for tasks performed daily or weekly. `N-0837` n=1 assert - `03-implementation-playbooks/03-03-23-teach-claude-your-workflow.html`
- Prefer automation for workflows with roughly three to fifteen consistent steps; keep variable, judgment-heavy, unstable, or credential-sensitive workflows manual, or split them. `N-0838` / `N-0839` n=1 assert - `03-implementation-playbooks/03-03-23-teach-claude-your-workflow.html`
- Schedule a recorded shortcut only after it has run reliably in manual runs and is low-risk. `N-0835` n=2 assert - `03-implementation-playbooks/03-03-23-teach-claude-your-workflow.html`
- Break a long recorded task into several short shortcuts. `N-0503` n=1 assert - `03-implementation-playbooks/03-03-23-teach-claude-your-workflow.html`
- Add a dead-man's-switch safeguard to automation that can modify live data. `N-0892` n=1 community - `08-davids-corner/05-09-allans-mini-series-parts-12.html`
- Redesign the automation approach when token limits reveal an expensive loop instead of only buying more capacity. `N-0891` n=1 community - `08-davids-corner/05-09-allans-mini-series-parts-12.html`
- Learn and test the manual deployment path with a basic index file before relying on automated deployment. `N-0850` n=2 assert - `03-implementation-playbooks/04-01-31-build-and-deploy-a-website.html`
- Enable ask-before-acting mode for sensitive automated work. `N-0831` n=2 assert - `03-implementation-playbooks/03-01-21-setting-up-claude-in-chrome-5-min.html`
- Run CodeQL, Semgrep, or equivalent language-aware static analysis in CI. `N-0881` n=1 linked - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`
- Pin GitHub Actions to full commit SHAs rather than floating tags. `N-0882` n=2 linked - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`
- Enable automated dependency updates (Dependabot, Renovate). `N-0880` n=2 linked - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`

### Remote and unattended operation

A large sub-body (roughly 60 raw claims across pages A-P032 to A-P035). Mostly product mechanics for Claude Code Remote Control rather than harness design. The transferable claims:

- Use remote access to monitor long-running builds (roughly thirty minutes or more) without staying at the desk. `N-0853` n=4 demo - `04-building-your-stack/02-01-21-why-remote-access.html`
- Use remote or mobile access only for short approvals, decisions, clarifications, and course corrections. `N-0854` n=4 demo - `04-building-your-stack/02-01-21-why-remote-access.html`
- Skip remote control for short tasks, or when you will return to the desk within minutes. `N-0857` n=5 assert - `04-building-your-stack/02-01-21-why-remote-access.html`
- Keep execution on the project machine and use remote access only as a mobility layer over that configured local workspace. `N-0855` n=2 assert - `04-building-your-stack/02-01-21-why-remote-access.html`
- Update the durable progress file before stepping away from a session that might terminate, and at major milestones during it. `N-0547` n=4 demo - `04-building-your-stack/02-04-24-session-persistence-across-devices.html`
- Configure and verify power settings so an unattended workstation does not terminate the local agent process. `N-0859` n=3 demo - `04-building-your-stack/02-01-21-why-remote-access.html`

---

## 11. Other

### Dependency and repository security (22 normalized records, page B-P069)

The best-sourced block in the corpus: most claims cite OpenSSF, CISA KEV, EPSS, SSVC, SBOM, or Sigstore.

- Do not select or trust a dependency on stars, a polished README, or recent activity alone; base trust on inspectable evidence and give popularity little weight in the score. `N-0901` n=3 linked - `08-davids-corner/02-02-git-repo-security-why-it-matters-and.html`
- Match the depth of a repository or dependency review to the stakes. `N-0904` n=3 assert - same page
- Run OpenSSF Scorecard on a candidate repository and read its per-check remediation, not only the aggregate score. `N-0906` n=2 linked - same page
- Verify a clear open-source license, and assess maintenance by checking recent activity. `N-0903` / `N-0902` n=2 linked - same page
- Check whether releases are signed and verify signatures with Sigstore or cosign; prefer artifacts with signed build provenance. `N-0907` n=2 linked - same page
- Prefer dependencies that publish an SBOM, and generate one for the system you ship. `N-0908` / `N-0910` n=1-2 linked - same page
- Trace every security rule to a primary standard, and reject rubric changes that cannot map to a cited standard. `N-0909` n=2 assert - same page
- Put unavailable security signals in an explicit uncertainty bucket with a note instead of automatically failing the project. `N-0917` n=2 assert - same page
- Apply hard score caps when a critical control is missing rather than relying only on weighted averages. `N-0918` n=2 assert - same page
- Add human review for installation scripts, novel malware indicators, and maintainer social-engineering risk. `N-0921` n=3 assert - same page
- Re-run repository and dependency checks on a regular cadence (quarterly default for shipped systems). `N-0905` n=2 assert - same page
- Require every security claim in a generated report to trace to a collected signal. `N-0645` n=1 assert - same page

### Code craft (page C-P082)

Largely language-specific style rules with no evidence beyond author convention. Structural claims already appear under Folders. Representative:

- Never swallow an error silently - when catching, either handle it meaningfully or log it. `N-0926` n=2 assert
- Keep the application entry point minimal and delegate immediately. `N-0927` n=2 assert
- Give every source file a header with description, status, issues, and todo sections; clean it whenever working in the file. `N-0208` / `N-0209` n=1 assert
- Use file-header todos only as temporary breadcrumbs, and move a real task into the project plan. `N-0683` / `N-0684` n=1 assert
- Use inline comments to explain non-obvious reasons, not to restate the code. `N-0212` n=1 assert
- Delete unused or commented-out code instead of retaining it. `N-0682` n=1 assert

### Setup

- Install the long-term-support release of Node.js before installing Claude Code. `N-0895` n=2 assert
- Three ways to attach to a running remote session: scan the terminal QR code, open the session URL, or pick the session from the app list. `N-0897` / `N-0898` / `N-0899` n=1 demo

---

## Contradictions and tensions

Flagged where two source claims push in opposite directions. Conditions in the ledger sometimes reconcile them; where they do not, the source simply disagrees with itself.

1. **CLAUDE.md must be short vs CLAUDE.md must contain everything.**
   `N-0249` caps it at thirty to fifty lines and `N-0252` calls it a router, not a detail store.
   Against that: `N-0256` stack, `N-0257` commands, `N-0258` conventions, `N-0259` avoid-list, `N-0029` routing table, `N-0248` identity and behavior rules, `N-0255` purpose, `N-0284` workspace descriptions, `N-0285` operating rules, `N-0071` file locations, folder layout, deployment target and constraints, `N-0028` naming and placement rules.
   These cannot all fit in fifty lines. The source never resolves this.

2. **CLAUDE.md line budget disagrees with itself.**
   Inside merged record `N-0249`, one page says forty to fifty lines and another says thirty to fifty. Both conditions are preserved in the ledger.

3. **Never load the whole workspace vs point Claude at the whole folder.**
   `N-0023` (n=9) says never load the whole workspace by default.
   `N-0056` says for synthesis tasks, point Claude Code at the full folder and ask it to process all relevant files in one task.
   Conditional on task type, but stated without cross-reference.

4. **Plain Markdown memory vs relational graph memory.**
   `N-0448` says use Markdown files and directories before a database or vector store.
   `N-0183` says use relational knowledge graphs rather than only flat vector retrieval for complex long-running knowledge work, and `N-0449` recommends a specific graph stack (Hermes plus Cognee).
   The conditions differ (small personal assistant vs complex long-running work) but the pages do not acknowledge each other.

5. **One agent first vs a specialist stack.**
   `N-0360` (n=3, demonstrated) says route work through one agent and master it before building a stack.
   `N-0393` and `N-0361` describe surrounding a builder with specialists under a routing orchestrator.
   Presented as a maturity ladder in one page and as the target architecture in another.

6. **Let it run unmonitored vs monitor it remotely.**
   `N-0373` says let the agent run without monitoring when it has a clear spec and no decision point.
   `N-0853` and `N-0856` build a whole workflow around remote monitoring of long builds.
   Both appear within the same page cluster (A-P032 to A-P034).

7. **Avoid single-file directories vs start with four near-empty folders.**
   `N-0207` says avoid a directory containing only one file unless it is expected to gain related files.
   `N-0123` says start a knowledge workspace with capture, workflows, reference, and output folders, each holding only its own CONTEXT.md.

8. **Line-count caps vs semantic splitting.**
   `N-0191` caps functions at about 100 lines and `N-0195` caps files at about 1,000.
   `N-0198` says split files at semantic boundaries rather than only to satisfy a line count.
   The same page states all three.

9. **Prompting is a supporting skill vs a detailed prompting curriculum.**
   `N-0732` (n=5) says invest in structured context and stage contracts rather than in perfecting prompts, and one contributing claim states prompting is a supporting skill, not the foundation.
   The corpus nonetheless carries 93 raw prompting claims including per-slot prompt anatomy (`N-0733`) and a ten-prompt expert list (`N-0776`, `N-0780`, `N-0813`).

10. **Stay with the default tools vs build a custom front end.**
    `N-0267` and `N-0266` say stay with VS Code and Claude Code until a concrete limitation justifies a custom front end.
    Pages A-P028 to A-P031 then walk through building one, including a repo tour of references to borrow from.

11. **Automate frequent work vs prefer copy-and-paste.**
    `N-0837` says prioritize automation for daily or weekly tasks.
    `N-0875` says prefer copy-and-paste handoffs to premature automation.
    Reconcilable through the risk-scoring records (`N-0885`, `N-0886`), but not reconciled in the source.

---

## Reliability notes for the rebuild

- 64 percent of normalized claims are unsupported assertions. The demonstrated 13 percent clusters almost entirely in three pages: `05-the-vault/03-01-comp-8-the-wildcard.html`, `03-02-comp-9-the-editor.html`, and `03-03-comp-10-the-diagnostician.html` - a competition-judging exercise. Those pages carry the verification, gate, and negative-fixture practices, which are therefore the best-evidenced material in the corpus.
- 34 raw claims cite a linked repository or asset that the audit explicitly did not inspect (`linked repository not inspected`, `description of linked asset not inspected`). Their grade of `linked` reflects that a link exists, not that anything was checked.
- Six numeric heuristics are recorded as unsupported: the 60/30/10 split, the thirty-to-fifty-line CLAUDE.md, the eight-to-ten-file subfolder threshold, the 150-line context-file threshold, the 100-line function and 1,000-line file caps, and the three-to-fifteen-step automation band.
- Claims about product mechanics (Remote Control flags, Chrome extension setup, subscription tiers, Codex `/status`) are time-sensitive and were not re-verified against current primary sources. That is step 4 of the checkpoint resume order and has not been done.
