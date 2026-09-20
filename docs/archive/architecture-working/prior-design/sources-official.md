# Official source reading and design contributions

Verified: the assigned original pages were read through the web tool in this session, rather than treating the prior ledger or repository notes as the sources. The scope table below names exactly what was read. This is a design report, not a runtime validation.

Critical point: preserving the user's model and effort choices while retaining native agent capabilities. A policy that only watches explicit model-switch hooks cannot establish that every provider turn respected those choices.

## Scope and provenance

All article reads below cover the accessible prose, examples, captions, and text tables. Images, interactive charts, videos, referenced system cards, and linked experiments were not independently inspected or reproduced. None of the assigned article bodies was unavailable. The initial direct Python HTTP request to S11 returned 403; the original official page was then fully accessible through the web tool. A preliminary parser attempt failed because BeautifulSoup was not installed. Nothing was installed.

| ID | Exact original URL | Access and read scope in this session |
|---|---|---|
| S11 | https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents | Full accessible article body, environment management, feature-list JSON, testing, getting-up-to-speed transcript, failure table, future work, acknowledgments, footnote. Web lines 13–117. |
| S12 | https://www.anthropic.com/engineering/harness-design-long-running-apps | Full accessible article, frontend experiment, full-stack architecture, both application narratives and tables, simplification failures, removal of sprint construct, limitations, appendix sample plan. Web lines 13–222. |
| S13 | https://www.anthropic.com/engineering/managed-agents | Full accessible article through conclusion and acknowledgments, including the session/harness/sandbox interfaces, credential boundary, context storage, and multi-environment discussion. Web lines 13–72. |
| S14 | https://www.anthropic.com/engineering/multi-agent-research-system | Full accessible article and appendix, including benefits/limits, delegation, tools, evaluation, deployment/recovery, asynchronous caveats, memory and filesystem handoff. Web lines 13–106. |
| S15 | https://www.anthropic.com/engineering/building-effective-agents | Full accessible article, all workflow patterns and both appendices. Includes the current notice that tooling has changed and points to Managed Agents. Web lines 13–178. |
| S16 | https://www.anthropic.com/engineering/AI-resistant-technical-evaluations | Full accessible article: evaluation goals, all redesign attempts, model interventions, benchmark table, open challenge. Web lines 13–120. |
| S17 | https://www.anthropic.com/engineering/april-23-postmortem | Full accessible article: effort default change, cache/prior-thinking defect, verbosity instruction regression, detection failures and remediation. Web lines 13–81. |
| S18 | https://claude.com/blog/the-ai-native-sdlc-playbook | Full accessible substantive body, all lifecycle stages, code/config examples, legacy system authority sidebar, metrics, maintenance/scans/Claude Tag sections, closing and resources. Read overlapping windows covering web lines 135–1016. Navigation and repeated footer are not article content. |
| S19 | https://www.anthropic.com/claude-fable-and-mythos-5-1 | Full accessible product article including all partner quotations, science, safeguards, anti-distillation changes, trusted access, EU section, availability, footnotes and further-reading list. Web lines 17–372. Product claims remain provider claims. |
| S62 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1 | Complete substantive guide, all sections and visible Python batching example, web lines 38–289. Other language tabs and linked API reference pages were not separately read. |
| S63 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#writing-density | Exact writing-density section read in S62, web lines 192–202. Same document, not independent evidence. |
| S64 | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1#prefer-targeted-edits-over-whole-file-rewrites | Exact targeted-edits section read in S62, web lines 267–270. Same document, not independent evidence. |
| S65 | https://code.claude.com/docs/en/hooks | Relevant complete reference sections, not whole reference: common input, exit codes, timeout, per-event decisions, HTTP/JSON, context injection (800–1077); SubagentStop, TaskCreated/Completed, Stop/StopFailure, TeammateIdle (2230–2542); WorktreeRemove, PreCompact/PostCompact, Pre/PostModelSwitch, SessionEnd (2811–3128); supported hook types and prompt-hook default (3248–3294). Also read surrounding ConfigChange and directory-event text. |

## Source-derived mechanisms and counterpoints

### S11: Explicit acceptance and recoverable work

Verified: the article addresses premature completion with a comprehensive failing feature list, incremental implementation, environment startup, and real end-to-end tests. Its initializer and coder differ in initial prompt, not necessarily in tools or system prompt. This supports a complete seed factory with recoverable state and checkable acceptance. Its web-app demonstration does not prove scientific research capability. The prompt prohibition on editing acceptance tests is an advisory mechanism, not an enforced security boundary. [Original](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

### S12: Calibrated evaluator and adaptable granularity

Verified: the evaluator improves after human calibration, still misses bugs, and sometimes later visual iterations are worse. Removing many harness pieces together failed; removing them individually exposed their contribution. The later design removes resets and sprint structure while retaining planning and useful evaluation. Thus preserve ambitious outcome coverage, artifact snapshots, and a calibrated independent evaluator; do not mandate resets or microtickets merely because older models needed them. Best-so-far artifact retention is a sensible design inference from non-monotonic output quality. [Original](https://www.anthropic.com/engineering/harness-design-long-running-apps)

### S13: Durable events, replaceable execution

Verified: the session is durable storage independent of both execution environment and reasoning harness. Context selection is replaceable and can revisit stored events. Sandbox loss becomes an explicit tool error; harness loss resumes from the external log. Credential isolation belongs outside generated-code execution. For Loam, checkpoint metadata should reference original evidence and native session identity, so a compact summary is an index, not the only surviving record. These are interfaces to adapt around native hosts, not a reason to recreate their inference loop or require a hosted service. [Original](https://www.anthropic.com/engineering/managed-agents)

### S14: Research teams need adaptive coverage

Verified: the lead iteratively decomposes, evaluates findings, and expands research. Delegation needs objective, output, tool/source guidance, and boundaries. The article evaluates outcomes and source/citation quality, recognizes source-selection bias, and recommends persistent worker artifacts. Its warning concerns dependency-heavy parallel work, not a ban on coding teams. Its synchronous limitation is a historical implementation limitation. Loam should support open-ended research with source coverage and contradictions, direct artifact references, and native asynchronous coordination when available. The internal results do not establish a Loam success rate or justify model/effort substitutions. [Original](https://www.anthropic.com/engineering/multi-agent-research-system)

### S15: Compose agency with deterministic contracts

Verified: this is a conditional taxonomy, not a rule that only execution may be agentic. Dynamic orchestration explicitly includes coding and search; autonomous agents suit unpredictable paths. Deterministic gates are useful when intermediate conditions are clear. Tool descriptions, examples, and structurally unambiguous arguments are central. Loam can offer discovery, planning, execution and evaluation roles while keeping authorization, evidence validation and state transitions in code. Its smaller-model routing example is not applicable to the user's allowed-model policy. [Original](https://www.anthropic.com/engineering/building-effective-agents)

### S16: Evaluate both familiar work and unknowns

Verified: the hiring test stopped separating candidates as models improved. A claimed performance limit fell after targeted steering; a supposedly hard replacement was solved with different inference settings. The eventual novel puzzles traded realism for discrimination. Loam should retain realistic project outcomes and add diagnostic unfamiliar problems, without confusing those purposes. An agent saying a task is impossible needs evidence and a recorded attempt to falsify the premise. This source does not authorize changing the user's effort to obtain a better score. [Original](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)

### S17: Configuration is part of the experiment

Verified: effort defaults, repeated removal of prior reasoning, and a verbosity instruction produced distinct regressions. Internal environments and narrow evaluations obscured them. Loam should record actual host/model/effort, instruction and tool versions, context events, and worker outcomes, then evaluate changes in the same host mode users run. A compact final report is compatible with sustained reasoning; suppressing all intermediate explanation can affect task performance. Never silently lower effort to reduce latency. [Original](https://www.anthropic.com/engineering/april-23-postmortem)

### S18: Complete lifecycle with one record of authority

Verified: the playbook covers intent through maintenance, uses versioned artifacts, distinguishes advisory skills from enforcement, and names one authoritative home for each artifact. It explicitly allows adaptive adoption and includes headless confidence gates. Its release-hook example matches command substrings and tests an environment variable. Inference: that example can miss wrapper commands and cannot authenticate an approval by itself. Loam should ship the complete lifecycle surface while activating external triggers or production actions only under user authorization. Source-linked lessons should reconnect incidents to future work. [Original](https://claude.com/blog/the-ai-native-sdlc-playbook)

### S19: Ambition with evidence boundaries

Verified: the launch reports research, root-cause analysis and long-horizon work, but mixes provider measurements and partner testimony. Its scientific examples include tools and external validation. It discloses residual approval-bypass behavior and limited evaluation visibility into long contexts and multi-agent work. Some benchmark tasks used fallback models; results are therefore not a universal proof for one fixed model. Loam should enable ambitious research and experimentation while recording actual execution and independent checks. Neither a blanket capability ceiling nor automatic addition of Mythos or Opus 5 follows. [Original](https://www.anthropic.com/claude-fable-and-mythos-5-1)

### S62/S63/S64: Preserve scope, history and native concurrency

Verified: the guide supports append-only conversation history, complete task delivery, exact preservation of user constraints during compaction, independent tool batching, asynchronous lead work, visual crop/zoom, explicit source quotation, and targeted edits. It describes prompt nudges as observable-behavior remedies. It does not establish that every Claude Code version already injects every remedy. Effort recommendations are evaluation advice, not authority to override Samyak. S63 supports plain literal writing; S64 supports targeted changes when results are preserved. [Complete guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1)

### S65: Hook semantics constrain guarantees

Verified: ordinary PreToolUse command/HTTP/MCP timeout errors fail open; SDK callback timeouts differ. Stop is absent on interrupt/API failure and has a continuation cap. PostCompact cannot modify or block compaction. PreModelSwitch misses automatic fallback and resume; PostModelSwitch cannot block and misses one-turn fallback-chain substitutions. Prompt hooks default to Haiku. Effective effort appears in applicable hook inputs. Therefore hooks provide useful observation and selected gates, but cannot alone prove allowed-model execution or durable completion. [Reference](https://code.claude.com/docs/en/hooks)

## Changes to Loam's existing interpretation

Verified: read `docs/research/anthropic-engineering.md`, `docs/research/harness-primitives.md`, `docs/factory/ARCHITECTURE.md`, `docs/ASSET-LAYERS.md`, `seed/.agents/skills/fable-prompting/SKILL.md`, and focused `bin/factory` call sites in this session.

| Existing interpretation | Required design repair |
|---|---|
| Engineering synthesis treats one work unit per session, reset context, and never self-grade as universal source rules. | Keep self-checking during implementation, independent final assessment where required, and explicit acceptance. Choose native continuation or reset according to measured recovery/quality needs. Preserve the whole requested deliverable regardless of scheduling granularity. |
| Building-effective-agents notes say to confine agency to execution. | Permit agent-led discovery, research, planning, task decomposition and replanning. Enforce the accepted objective and authorization at boundaries. |
| Harness-primitives says `--bare` is the CI default and ends with a universal shell/workflow combination. | Replace universal defaults with tested host profiles. Preserve native skills, plugins, tools, memory, workflows and team facilities for the tasks that need them. Make each deliberate restriction visible in the capability manifest. |
| Harness-primitives globally says to skip teams based on its headless findings. | Separate interactive-team availability from unattended-worker availability. Do not delete an interactive capability because another host surface cannot support it. Current team documentation is covered in E-TEAMS below; runtime verification remains outstanding. |
| Factory architecture requires Fable graders even for the Codex worker and hardcodes role effort choices. | Introduce provider-contained role resolution: Claude driver Fable 5.1, only Fable 5.1/Opus 4.8; Codex driver Astra, only Astra/Sol/Terra. Keep the user's selected effort unchanged. Existing architecture is historical, not authority over the current request. |
| Fable skill says H rows mean prompt text changes nothing, and native injection is universal. | Record the host/version evidence for actual native coverage. Apply a remedy only when the symptom persists and the host has not supplied it. Remove instructions that autonomously change effort. |
| Asset-layer prose says anything that must always hold is a hook. | Distinguish advisory instructions, native permissions, supervisor state checks, and external authorization. A hook with fail-open semantics cannot be the sole invariant enforcement. |
| Grader invocation uses Read/Grep/Glob only; worker invocation restricts MCP configuration. | Make the grade contract explicit: evidence-only audit or independent live execution. Add a native verifier with authorized runtime/browser/scientific tools when live reproduction is required; freeze its resulting evidence for the audit. Do not claim the read-only audit itself reproduced behavior. |

## Proposed acceptance scenarios

These are implementation requirements inferred from the evidence and the user's scope. They were not executed here.

- **Model policy survives all roles.** Start each provider profile, delegate, invoke an evaluator or advisor, resume, and simulate fallback. Validate explicit launch, worker, advisor, evaluator and teammate selections against the permitted set. Record requested, resolved and observed model/effort separately, with observation provenance and unknown values. Reject known disallowed configurations and substitutions. Where the host cannot prevent or expose a hidden substitution, mark strict compliance unverified and do not certify or continue a run that requires that guarantee. This is a design acceptance condition, not a claim that hooks can supply complete observability.
- **Complete seed factory.** Generate a fresh project and exercise discovery, planning, execution, evaluation, recovery, delivery preparation and learning using local fixtures. Each stage is present without attaching a personal plugin. External scheduling, messaging, installs and publishing remain inactive until explicitly authorized.
- **Native capability retention.** A generated Claude project can use its permitted native skills, tools, plugins, memory, teams and workflows. The Codex profile can use its own native equivalents. An unsupported surface is reported specifically; it does not disable the capability everywhere or trigger a cross-provider fallback.
- **Recovery without invented history.** Terminate the worker during a tool operation. Restart the supervisor. It inspects the real repository/job state, retains the accepted request and pending work, marks the action's completion unknown until reconciled, and resumes without duplicating the side effect. Evidence links still resolve after compaction.
- **No false completion while waiting.** A lead has pending research workers or a long experiment. Returning a turn, a hook failure, or a context reset cannot mark the whole task accepted. The supervisor distinguishes waiting, blocked, failed, canceled, and verified complete from observable evidence.
- **Independent verification reaches the product.** Provide an application with a working API but disconnected UI action. The runtime verifier reproduces the broken user flow. The audit rejects a passing build as insufficient. For a scientific result, an executable experiment and its outputs accompany the claim; polished prose alone cannot pass.
- **Research follows a surprising result.** Begin with a hypothesis contradicted by an original source or experiment. The research lead preserves the contradiction, revises the next investigation within the accepted goal, and records why. The final report maps each claim to source/experiment evidence and labels unavailable material.
- **Memory can be corrected.** Store an observed result with source identity, exact scope, run/config identity, and confidence. New evidence contradicts it. Mark the old interpretation superseded, retain the original observation, and retrieve both when explaining the revision. Do not overwrite history with a new confident summary.
- **Evaluator calibration and artifact selection.** A seeded evaluation suite includes a superficial attractive failure and an ugly functional pass. Reviewers distinguish required correctness from taste, report reproducible findings, and retain the best accepted artifact even if a later revision degrades it.
- **Changes improve capability rather than merely shortening runs.** Evaluate a proposed harness removal on representative and frontier tasks under identical user-selected model/effort. Compare requirement coverage, correctness, evidence, recovery and human corrections. Keep complexity that improves the requested outcome.

## Supplemental native documentation

| ID | Original URL | Exact access/read scope |
|---|---|---|
| E-GOAL | https://code.claude.com/docs/en/goal | Full substantive page through requirements and see-also, web lines 68–250: usage, condition, status, resume, non-interactive behavior, evaluation, all failure modes, background waiting, evaluation model and requirements. |
| E-TEAMS | https://code.claude.com/docs/en/agent-teams | Full substantive page through next steps, web lines 107–577: enabling, controls, model/effort resolution, plan approval, tasks, architecture, role-definition fields, permissions, messaging, examples, best practices, troubleshooting and limitations. |

**E-GOAL, Verified:** Native goals resume and work non-interactively. Their evaluator reads transcript evidence without tools. `ANTHROPIC_DEFAULT_HAIKU_MODEL` changes that evaluator, but also the Haiku alias and background functions such as summarization. Background work defers evaluation; interactive idle retry/check-in behavior differs from headless turn-end check-ins. Resume resets accounting baselines. A goal judged impossible or cleared by an unrecoverable error is not accepted work. **Design inference:** preserve native goals when model-policy support is verified, retain supervisor-level lifetime accounting, and distinguish a goal verdict from independently checked acceptance. Test background completion, error clearing, no-progress pause, and resume accounting. [Original](https://code.claude.com/docs/en/goal)

**E-TEAMS, Verified:** Interactive teammates support direct messaging and shared tasks; headless named helpers remain subagents. Effort inherits from the lead. Model selection consults spawn instructions, role definition, configured subagent model, then lead; the force setting bypasses the first choices. An allowlist can substitute models. Native teammate plan approvals happen automatically without lead review. Role `skills` preloads are ignored; in-process teammates ignore role `mcpServers`; role bodies are appended in-process but replace the default system prompt in split panes. Tasks persist while in-process teammates do not resume. **Design inference:** preserve teams with explicit host profiles, rehydrate replacements from durable artifacts, and verify effective tools/context. Do not treat native plan approval as an independent Loam review gate or globally force a single model when distinct allowed roles are intended. Acceptance: an enabled interactive team exchanges contrary findings with retained project skills; headless operation reports its actual subagent shape; restart restores task evidence without pretending old teammates survived. [Original](https://code.claude.com/docs/en/agent-teams)

## Risks and self-attack

Verified: no model jobs, demonstrations, paid evaluations, installations, automation, commits, pushes or repository edits were performed. The only authored output is this report. Runtime enforcement and documented team behavior require implementation-time validation.

Self-attack: a hidden provider fallback breaks a hook-only policy; the design explicitly flags that gap. Read-only graders cannot independently run an app; the design separates runtime verification from evidence audit. Native host prompt injection claims in the seed skill lack evidence from the official guide; they remain unverified rather than being repeated as facts. Full prose access does not imply visual chart inspection, system-card review or experiment replication. All assigned source IDs have an explicit scope above; S63/S64 are duplicate fragments, not extra independent sources.
