# Original-source review: research, memory, and supervisor mechanisms

Verified: Original-source reading supports a local evidence and inquiry layer around Loam's native workers. It does not establish that any reviewed research framework is a suitable replacement for the factory supervisor. This note separates source observations from proposed Loam behavior. Sources and implementation scopes are recorded below. Nothing was installed or run from these sources.

## Scope and access

Verified: The assignment is S57–S61, S66–S73, and X08–X10 from the original `source-ledger.json`. GitHub web/API access was inconsistent, including an anonymous API rate-limit rejection. Raw GitHub file reads worked. Repository inspection covered the README material and named implementation or skill files, not every file. Branch URLs are moving references; no source revision has been approved or vendored. The Medium originals S69 and S73 were blocked on fresh access. Prior review descriptions are not substituted for reading them.

Verified: Loam currently renders `seed/` (`copier.yml:2`). The existing native Codex worker call is at `bin/factory:815`; its ledger model label explicitly does not establish the effective model (`bin/factory:383`). Claude model and effort arguments are explicit at `bin/factory:843`. These are existing implementation observations, not verification that new native adapter capabilities exist.

Assumption: The agreed target is a complete independent factory in every seed, with shared skills in `seed/.agents/skills/`, local pinned rubrics, and a small supervisor around native execution. Codex uses Astra as driver and only Astra/Sol/Terra; Claude uses Fable 5.1 as driver and only Fable 5.1/Opus 4.8. The user controls effort. No source's cheaper model, automatic effort adjustment, scheduled loop, or account requirement overrides this target.

## Source-by-source record

### S57: GPT Researcher

Verified: Read the original [repository README](https://github.com/assafelovic/gpt-researcher), plus `gpt_researcher/skills/researcher.py` sections for planning, research-source routing, web-query fan-out, subquery processing, URL deduplication, source retrieval, and scraping. Other retriever implementations, report writers, MCP implementation, and deployment code were not audited. The README separates planning, source research, and report production. This supports a discover/read/synthesize contract, not proof of report accuracy.

Verified: In the [actual research conductor](https://raw.githubusercontent.com/assafelovic/gpt-researcher/master/gpt_researcher/skills/researcher.py), source records can retain URL and raw content. `_get_new_urls` marks a URL visited before fetching succeeds. `_process_sub_query` catches errors and returns empty text; `_get_context_by_web_search` can return an empty list on exceptions. Thus an empty research result does not itself distinguish no evidence from collection failure.

Assumption: Adapt source-aware collection and per-query goals. Require distinct attempted/fetched/read/failed states and durable error receipts. Reject adopting the full API-oriented research runtime as Loam's core. Probe a failed fetch followed by retry and ensure it cannot become “source read” or permanent deduplication suppression. License: [Apache-2.0](https://raw.githubusercontent.com/assafelovic/gpt-researcher/master/LICENSE), verified from the license file. No code selected for direct copying yet.

### S58: WritingAIPaper

Verified: Read the original [README handbook](https://github.com/hzwer/WritingAIPaper), including core contribution, paper structure, related work, defensibility, readability, checklist, and submission appendices. This is advice, explicitly described by its authors as not peer reviewed. It distinguishes insight, performance, and capability contributions, and warns that better metrics are not automatically new knowledge. No executable reuse candidate was identified from the material read.

Assumption: Adapt only a conditional research-writing checklist: identify the contribution, align the result with the claim, and show supporting evidence prominently. Keep it out of generic factory acceptance. Reject treating novelty, conference acceptance, or polished prose as success for ordinary research inquiries. Probe a well-supported negative result: it must be allowed to finish without an invented novelty claim or manuscript. No copying proposed; source license not established in this inspection.

### S59: AI Research Skills

Verified: Read README research/ARA catalog and changelog sections, and the full selected skill implementations: [autoresearch](https://raw.githubusercontent.com/Orchestra-Research/AI-Research-SKILLs/main/0-autoresearch-skill/SKILL.md), [ARA compiler](https://raw.githubusercontent.com/Orchestra-Research/AI-Research-SKILLs/main/22-agent-native-research-artifact/compiler/SKILL.md), [research manager](https://raw.githubusercontent.com/Orchestra-Research/AI-Research-SKILLs/main/22-agent-native-research-artifact/research-manager/SKILL.md), and [rigor reviewer](https://raw.githubusercontent.com/Orchestra-Research/AI-Research-SKILLs/main/22-agent-native-research-artifact/rigor-reviewer/SKILL.md). These are prose programs for native agents. Referenced schemas/checklists and the installer were not audited.

Verified: The compiler separates raw source evidence from derived subsets, explicit history from inferred reconstruction, and observations from interpretation. Its required minimum numbers of concepts, experiments, graph nodes, and code stubs can force irrelevant structure. The manager records provenance, decisions, dead ends, and pivots, but runs only as an epilogue and has count-based maturity promotion. The reviewer reads the artifact, spot-checks evidence, prohibits execution/external checking, and takes reported evidence at face value. Its grade is not independent reproduction.

Assumption: Reconsider the earlier broad rejection: selectively adapt the compiler's evidence rules, the manager's provenance/failed-approach fields, and the reviewer's claim-scoped findings into shared native skills and local rubrics. Reject mandatory ARA trees, fixed content quotas, automatic scheduling/commits, count-based authority promotion, and an academic grade as universal completion. Probe contradictory raw/derived tables, missing evidence, and a valid negative result. License: [MIT](https://raw.githubusercontent.com/Orchestra-Research/AI-Research-SKILLs/main/LICENSE), verified. Preserve the notice if substantial prose is adapted; pin selected files first.

### S60: dzhng/deep-research

Verified: Read the full original [README](https://github.com/dzhng/deep-research) and full [src/deep-research.ts](https://raw.githubusercontent.com/dzhng/deep-research/main/src/deep-research.ts). The code generates search queries with a research goal, extracts learnings and follow-up questions, and recursively explores them. The final result stores learning strings separately from visited URLs, then appends URLs to the report. There is no claim-to-passage relationship in that result type. Exceptions return empty learning/URL lists. A new concurrency limiter is created within each recursive call, so the implementation does not establish a single global recursion-tree concurrency bound.

Assumption: Adapt the compact query-goal/follow-up schema as a discovery worker output. Replace plain learning strings with claim candidates linked to exact fetched source records, and persist failed branches. Reject direct adoption as evidence storage or supervisor scheduling. Probe duplicate discoveries, branch failure, changed source content, and global in-flight limit across recursive work. License: [MIT](https://raw.githubusercontent.com/dzhng/deep-research/main/LICENSE), verified. This is a small code candidate after its provenance and error contracts are rewritten, not a drop-in dependency.

### S61: Alibaba DeepResearch

Verified: Read the full original [README](https://github.com/Alibaba-NLP/DeepResearch) and full [inference/react_agent.py](https://raw.githubusercontent.com/Alibaba-NLP/DeepResearch/main/inference/react_agent.py). The implementation uses a Qwen/OpenAI-compatible local model runtime, parses tool-call markers, retries model requests, and records a termination field with its final messages/prediction. The loop's messages are maintained in memory. At the context limit it requests a likely final answer. Search/visit/file/Python tool implementations and training/infrastructure were not audited.

Assumption: Adapt explicit termination reasons and preservation of the trace, but keep “context exhausted” distinct from a supported conclusion. Reject this model/runtime and its service dependencies as the core factory. It does not preserve the requested native driver boundary. Probe exhaustion during contradictory evidence collection: preserve partial work and unresolved status instead of fabricating a best answer. License: [Apache-2.0](https://raw.githubusercontent.com/Alibaba-NLP/DeepResearch/main/LICENSE), verified. No direct code reuse selected.

### S66: Addy Osmani, Agent Harness Engineering

Verified: Read the full substantive [article](https://addyosmani.com/blog/agent-harness-engineering/), including component inventory, native-harness reuse, context management, completion contracts, and evaluation. It is an engineering synthesis, not a controlled evaluation. Its useful framing is to connect an observed failure to a specific harness component and keep scaffolding revisable as models change.

Assumption: Adapt this as a change record: failure evidence, proposed mechanism, expected effect, regression probe, and removal condition. Reject automatic conversion of every mistake into permanent global instructions. Probe whether a proposed rule improves held-out cases without degrading already passing cases. No code or article prose copying proposed.

### S67: Lilian Weng, Harness Engineering for Self-Improvement

Verified: Read the substantive [article](https://lilianweng.github.io/posts/2026-07-04-harness/), including memory approaches, harness evolution, evaluation boundaries, negative results, and future challenges. The article discusses itemized memory updates and constrained harness edits while keeping evaluators and permissions outside the evolving surface. It distinguishes objectively evaluated optimization from research with weak or ambiguous evaluation. Its descriptions of ACE, MCE, and other memory methods are a synthesis; their underlying papers were not independently read in this assignment. X08 was read independently below.

Assumption: Adapt itemized proposed lessons with stable IDs and scoped applicability. Keep model/effort policy, authority, and acceptance criteria outside autonomous memory changes. Reject expected benchmark gains or automatic improvement claims. Probe source-grounded lessons against stale conditions and held-out tasks; compare against no retrieval and ordinary project notes. No direct prose/code copying proposed.

### S68: agents-best-practices

Verified: Read the full [README](https://github.com/DenisSergeevitch/agents-best-practices), core/advanced `SKILL.md` sections, and complete relevant [context-memory-compaction](https://raw.githubusercontent.com/DenisSergeevitch/agents-best-practices/main/references/context-memory-compaction.md) and [workflow-orchestration](https://raw.githubusercontent.com/DenisSergeevitch/agents-best-practices/main/references/workflow-orchestration.md) references. This is a Markdown-only reference skill, not an implemented runtime or evaluated security boundary. Other advanced references and provider adapters were not audited.

Verified: Its memory reference separates user assertions from derived suggestions, source references from summaries, and scope from retrieval convenience. Correction/deletion must invalidate dependent caches; stale extraction must not resurrect deleted memory. Workflow guidance binds work to versioned packets and uses durable child identities, cancellation, and tombstones. These mechanisms are more precise than merely saving a Markdown recap.

Assumption: Adapt the lifecycle invariants and packet fields into local schemas, fixtures, and selective guidance. Leave native compaction inside each native harness. Reject replacing native tools or introducing every governance feature described. Probe corrected facts, duplicate capture, late child output, and restored cancelled work. License: [MIT](https://raw.githubusercontent.com/DenisSergeevitch/agents-best-practices/main/LICENSE), verified. Selective checklist/schema adaptation is a reuse candidate; no tested implementation to vendor.

### S69: Mario Tort, Production-Ready Harness Engineering

Verified: Fresh access to the [original Medium URL](https://medium.com/@tort_mario/ai-agent-best-practices-production-ready-harness-engineering-2026-guide-c1236d713fac) was blocked: direct retrieval returned HTTP 403 and the web tool supplied a block page. The original article body was not read in this pass. The historical ledger's earlier access claim is not current evidence.

Assumption: Defer adopt/reject judgment until accessible original text is supplied or an authorized browser reads it. No code or mechanism is credited to this unread source. No license established.

### S70: Agent Harnesses with Claude, Intuitively and Exhaustively Explained

Verified: Read the original [article's](https://iaee.substack.com/p/agent-harnesses-with-claude-intuitively) conceptual exposition, structure/routing specification, metaskill explanation, maintenance discussion, conclusion, and selected relevant job-application/initialization transcripts. Long repeated terminal transcripts were not exhaustively audited. The linked metaskill implementation was not inspected, so its scripts are not approved reuse candidates. The source proposes a hierarchical index and progressive disclosure. Its own example acknowledges changing historical work locations while applying a current-location update.

Assumption: Adapt a small index linking authoritative project knowledge and task records. Reject another mandatory harness standard, broad automatic wiki rewrites, and treating navigation markers as sandbox boundaries. Probe a changed present preference that must not overwrite historical evidence. Author claims about native product capabilities were not verified and are not used to establish Loam's adapter design. No code/prose copying proposed; linked project licenses not established.

### S71: LangChain, The Anatomy of an Agent Harness

Verified: Read the full substantive [article](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness), covering model versus harness, context, tools, filesystem, compaction, and runtime control. It provides an engineering taxonomy. It does not demonstrate that Loam requires a new runtime or that a particular native product exposes a specific API.

Assumption: Use the taxonomy to allocate ownership: native harnesses retain internal context/tool execution; Loam owns task lifecycle, evidence validation, and integration decisions. Reject copying framework internals to reproduce native capabilities. Probe the smallest supported native invocation and result/cancellation interface before designing a large adapter. No implementation was linked and audited as a reuse candidate in this scope.

### S72: Martin Fowler site, Harness Engineering for Coding Agent Users

Verified: Read the full substantive [article](https://martinfowler.com/articles/harness-engineering.html), including guidance versus feedback, computational versus inferential checks, functional behavior, templates, and limitations. The article explicitly questions confidence in agent-generated tests and notes that approved fixtures only fit some contexts. It also identifies template versioning and contribution drift.

Assumption: Adapt stack-specific checks and explicit acceptance ownership within a generic shipped supervisor. Treat semantic review as additional evidence with coverage limits. Reject a universal testing recipe or confidence derived solely from worker-authored tests. Probe a candidate that edits its own tests to hide broken behavior; the owner's frozen acceptance must still fail. No code/prose copying proposed.

### S73: Complete Guide to Agent Harnesses with Code

Verified: Fresh access to the [original Medium URL](https://medium.com/data-science-collective/the-complete-guide-to-agent-harnesses-with-code-6fa11cecd004) returned HTTP 403/block content. The article body and its code were not read in this pass. The historical paywall-preview record is not a full-source reading.

Assumption: Defer a mechanism or code-reuse verdict until the original becomes accessible. No claims, code, or license are attributed to unseen text.

### X08: Why LLMs Aren't Scientists Yet

Verified: Read [the original paper](https://arxiv.org/html/2601.03315), main setup/method/results/failure analysis/limitations, and relevant appendix case discussions. Not every appendix passage or referenced repository was audited. This is a small qualitative study of human-selected research attempts, not a controlled comparison of harness interventions. It reports stale defaults, implementation drift under execution pressure, lost context, over-optimistic interpretation, domain-knowledge gaps, and weak problem selection. Its limitations preclude claiming a general model ceiling or measured benefit from a particular repair.

Assumption: Adapt the failure cases into probes: algorithm simplification must register a method revision; raw failed runs must remain visible even when the summary sounds successful; stale dependency assumptions need rechecking. Reject treating a generated manuscript or favorable narrative as inquiry completion. These findings motivate tests; they do not predict Loam performance. No paper prompts or code copied.

### X09: ScientistOne, Chain-of-Evidence

Verified: Read [the original paper](https://arxiv.org/html/2605.26340) sections on evidence, architecture, audits, experiments, generalization, limitations, and full implementation Appendix B. It binds claims to artifacts before drafting, checks evidence, critiques conclusions, then verifies composed text. Reported results favor its integrity checks, but baseline adaptations, narrow benchmark coverage, automated review proxies, and unmeasured false negatives limit transfer.

Verified: Appendix B's numeric checks normalize units near referenced log lines; citation checks judge abstract support; methodological checks use textual overlap with experimental logs. The independent reference audit establishes existence, not passage support. A method-code failure still survives the system's verification. These are aids, not proof of faithful implementation.

Assumption: Adapt claim-to-artifact binding and a final claim check, retaining provenance alongside the final deliverable. Probe a real citation supporting the wrong assertion, a method name present in logs but absent from code, and a score from the wrong run. Reject benchmark-derived confidence in Loam. No released implementation inspected or code-copy candidate identified.

### X10: KernelBench

Verified: Read [the original paper](https://arxiv.org/html/2502.10517) task/evaluator design, baseline and capability studies, discussion, and complete evaluation/orchestration Appendices B and H. It compares generated kernels against a reference, separates execution/correctness/performance feedback, and evaluates sampling versus iterative refinement. Feedback benefits depend on the model; additional examples can worsen overall success. Random checks on fixed task shapes are not formal equivalence. Hardware and baseline choice change results.

Assumption: Adapt precise feedback categories and an attempt state machine. For GPU research only, consider resource leases and disposable evaluation processes as a later domain adapter. Reject mandatory GPU machinery or numerical speedup metrics for every seed. Probe an evaluator crash separately from a wrong answer; neither can be promoted as a valid negative scientific result. Paper methods were read, but no KernelBench repository implementation/license was audited for copying. No benchmark performance transfers to Loam.

## Recommended local inquiry and memory design

Assumption: Keep the universally shipped inquiry contract compact: question, scope, proposed method, evidence requirements, observed evidence, conclusion, limitations, and next decision. Research can conclude supported, refuted, mixed, or inconclusive. The work outcome independently records completed, interrupted, failed collection, or blocked execution. A completed inquiry may honestly refute its hypothesis. An interrupted experiment cannot silently become a negative result. Convert an inquiry to an engineering ticket only when the intended behavior and acceptance are known.

Assumption: Preserve distinct stores with distinct authority:

| Store | Contents | Writer and authority | Applicability and invalidation |
|---|---|---|---|
| Raw evidence | Original source snapshots or references, command receipts, stdout/stderr, exit status, candidate tree, datasets/configuration, review output | Supervisor captures and identifies; worker output remains untrusted until validated | Content hashes and immutable attempt IDs; never silently rewrite to match a new summary |
| Inquiry and claim records | Question/method revisions, claim text, evidence edges, counterevidence, conclusion, unresolved gaps | Worker proposes; supervisor validates structure and binds exact evidence; semantic assessment records reviewer identity and limits | Bind to task revision, method and candidate. New evidence appends or supersedes a claim instead of retroactively changing its basis |
| Curated memory | Small lessons, assumptions, failed approaches, useful source pointers | Agent proposes. Promotion follows an explicit project policy or review; retrieval never grants permission | Include source, scope, environment/model/effort/rubric dependencies, confidence, validation status, last checked condition, supersedes/retracted state |
| Control state | Task/attempt lifecycle, current task revision, leases, cancellation, acceptance manifest, authorization, publication state | Deterministic supervisor is the only writer | Durable event sequence; worker prose cannot alter status or revive cancelled authority |

Assumption: Store operational events as they occur. A session epilogue may curate lessons but cannot be the only recovery record. Keep original observations distinct from explanation, and retain counterexamples. A failed approach applies only to its conditions; it is not a universal prohibition. Repeated copies of the same observation do not increase independent evidence. A user correction should update the current fact and invalidate dependent summaries without falsifying the historical record.

Assumption: Immutability means evidence cannot be silently rewritten. It is not a rule to retain private material forever. An authorized deletion must remove the affected memory payload and derived copies under the project retention policy, while a minimal non-content tombstone prevents an old extraction job from restoring it. Record deletion as an explicit event rather than presenting the missing material as evidence still available.

Assumption: Retrieval should return why an item applies and where it came from. A changed dependency, rubric, method, native runtime, or relevant model/effort setting makes a lesson a candidate for revalidation rather than current authority. Broad capability knowledge should not be keyed so narrowly that it becomes unusable; record which dependencies are actually material. Invalidated or uncertain lessons may appear as labeled background if useful, but cannot satisfy acceptance or authorize an action. Do not promote personal facts or private conversation content merely because a worker summarized them.

Assumption: Memory-driven improvement should produce a concrete proposal with the supporting failures, intended change, affected behavior, and a held-out probe. It may refine supplemental guidance. It must not change user-owned effort, allowed models, acceptance, permissions, or scheduling authorization. Evaluate usefulness against ordinary project notes and no-memory retrieval. Measure wrong reuse as well as successful recall. No reviewed source establishes that more memory is always beneficial.

## Supervisor boundary and risk-first probes

Verified: Current completion can infer success from absence of a `FAIL` line even when the checks command fails (`bin/factory:1135`), and malformed Codex review defaults to zero blockers (`bin/factory:1031`). The grader cap also reaches `open_pr` (`bin/factory:1151`). Resume is based partly on file existence (`bin/factory:1195`), and stop writes a marker (`bin/factory:1205`). These concrete paths make durable validation and cancellation more urgent than sophisticated memory search.

Assumption: Build the first probe around one clean generated project, a fake native adapter, an immutable candidate handoff, and a supervisor-owned acceptance manifest. Fake adapters avoid paid/native execution while validating state behavior. Protect control state and acceptance outside the worker's writable scope. A read-only file or frozen hash alone is not an operating-system isolation boundary when the same worker can change the containing directory or effective harness configuration. Evaluate the candidate in a supervisor-owned view if native sandbox controls cannot establish the boundary.

Assumption: Give repository/project, task, task revision, attempt, candidate tree, verifier invocation, and evidence record separate identities. Each restart or steering revision grants a fresh attempt authority token. Stop revokes authority immediately; terminating the actual process tree is a separate observation. Late output may be retained for diagnosis but cannot satisfy acceptance, update current state, publish, or mutate a reused worktree. Quarantine a worktree until old writers are confirmed gone. Memory cannot override these checks.

Assumption: Run proposed probes in this order before considering a broad native or research integration:

1. Checks exit nonzero with no `FAIL` text; malformed/empty review; omitted required check. Expected: explicit verification failure or unknown, never pass.
2. Worker changes acceptance fixtures, rubric, or its own expected result. Expected: owner-approved acceptance remains authoritative, and candidate acceptance changes require a distinct reviewed revision.
3. Supervisor crashes after launch, after result capture, and after check completion. Expected: exact persisted attempts survive, counters do not reset, and unfinished work is reconciled without inventing success or duplicating authority.
4. Stop during a live child process; late result arrives after a restart. Expected: cancellation and old-authority rejection persist across restore; old writers cannot touch the next candidate.
5. User steers the question/method during a run. Expected: old evidence keeps its original revision; the new conclusion cannot cite it as current without an explicit applicability assessment.
6. Research source fails or returns a real but irrelevant citation. Expected: failed collection differs from no evidence; existence differs from support.
7. A proposed lesson is stale, contradicted, corrected, deleted, or extracted twice. Expected: no silent authoritative reuse, stale-cache resurrection, or fabricated independent corroboration.
8. Native adapter preflight and controlled integration, once separately authorized. Expected: verify effective driver and all nested/reviewer/auxiliary models against the allowed profile, preserve user effort, and fail closed on unknown enforcement. Codex-only and Claude-only profiles must not require the other account.

## Reuse decision and limits

Assumption: Best near-term reuse is selective MIT skill prose/schema adaptation from S59 and S68, plus possibly S60's small query-goal/follow-up shape after error and provenance redesign. Keep local copies pinned with license notices and a source/change record. Prefer implementing the small supervisor contract directly over vendoring an unrelated research framework. S57's collector is a reference for an optional research adapter, not a core runtime dependency. S61's trained/API runtime is outside the native model boundary. Paper mechanisms are proposals to reproduce, not code imports.

Verified: No downloaded source was executed, no native worker or grader was launched, and no benchmark was reproduced. S69 and S73 remain unread originals in this pass. S70's linked metaskill implementation, S59's supporting schema references, underlying memory papers summarized by S67, and KernelBench's repository remain outside the inspected implementation scope. The supplemental ChatGPT memory share was reported by the parent as title-only; its body is not claimed as read here. X11 was read by the parent, not by this subagent.

Risks: The proposed memory and supervisor contracts have not been implemented or tested. Source branch URLs can change; exact pins and license notices need checking before copying. Source access gaps can change a reuse verdict, but they do not justify importing uninspected code. Native cancellation, descendant model enforcement, state-write isolation, and effective effort observability still need bounded adapter probes. The next engineering step is the generated-project fake-adapter completion and cancellation slice, before adding memory-driven refinement.
