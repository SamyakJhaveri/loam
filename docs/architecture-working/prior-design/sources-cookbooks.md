# Original-source review: S34 through S42

Verified: all assigned notebook markdown and code cells were read from original repository files at commit `a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5`. GitHub commits API supplied this revision; raw files were fetched at that revision. The native advisor documentation was fetched live. No notebook, downloaded program, model worker, install, automation, or repository runtime was executed. This report is analysis for the parent integration owner.

Critical point: mistaking a service API or demonstrator for an enforced native factory capability. The two independent checks were original source/code inspection and comparison with official native/API documentation or stored notebook traces. Host capability tests below are proposed, not run.

Repository provenance: [Claude Cookbooks pinned tree](https://github.com/anthropics/claude-cookbooks/tree/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5). Verified: `LICENSE` is MIT, copyright Anthropic. Preserve the copyright and permission notice in copied substantial code. The README describes copyable recipes. This is permission to reuse source, not a quality certification. The full repository was not audited.

Read scope: notebook cells include setup, all implementation, terminal handling, and cleanup where present. Stored output was also inspected for the Workflow-generated JavaScript, tool-search demonstrations, advisor usage, grader rejection sequence, and async orchestration traces. PTC output traces were selectively read; their visualization truncates some generated execution code. No benchmark results were reproduced. `managed_agents/utilities.py` and `tool_use/utils/team_expense_api.py` were read as original helper source. Display-only `utils.visualize` was not audited.

## Coverage and decisions

### S34: native advisor documentation

URL: https://code.claude.com/docs/en/advisor
Status: full substantive live documentation read. Host execution unverified.

Verified: this is a native Claude Code interface to a server-side advisor. Fable 5.1 main accepts Fable 5.1 advisor; Opus is rejected. Native subagents inherit the advisor subject to their own model pairing. Timing is model-decided, with no setting to force or cap consultations. The advisor rereads the full conversation without its own prompt-cache reuse. Disabling flags can leave an accepted launch flag ineffective. Feature availability is host/account dependent.

Adapt: use an optional, explicitly reported Fable advisor for Claude-side work when the user enables it. Keep model identity explicit and within the user's model policy. Opus 4.8 workers can consult Fable, but an Opus advisor cannot review the Fable driver through this feature. A separate fresh reviewer is a distinct design.

Reject: mandatory advisor on every round; describing advisor access as proof a consultation happened; importing this feature as a Codex capability.

Proposed target: each generated project's native Claude capability profile and consultation instructions. Proposed probe: check active model/advisor identity and a bounded consultation receipt, including disabled, unsupported, and redacted cases. Run only with user-authorized model execution later.

### S35: consult an advisor

Original URL: https://platform.claude.com/cookbook/managed-agents-cma-consult-an-advisor
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/managed_agents/CMA_consult_an_advisor.ipynb
Status: complete notebook source; selected stored outputs; helper source read.

Verified: the reusable pieces are the costly-decision consultation prompt, `advice_text` redaction branch, thread usage attribution, and avoiding double-counting advisor spend already present in session totals. Managed Agents consultation is a short-lived advisor thread; identifying its `agent.type` is stronger than matching a name. Only the primary consults in this service example. That differs from S34 native subagent inheritance.

Adapt the consultation policy and evidence receipt. Reject Agents/Environments/Sessions plumbing, sandbox mount paths, unrestricted networking, cloud budget values, and native parsing based on these cloud event names. The cleanup helper distinguishes an idle event from server state settling; its timeout returns without proving idle, so it is a demonstration rather than a durable cleanup contract.

Proposed target: native driver result normalization and optional consultation record. Probe: fixture events for text/redacted advice, unavailable advisor, and aggregate usage containing advisor usage already. Verify consulted identity and occurrence independently of readable advice. The historical prompt in `_common.md` already adapts the decision policy, so preserve the useful rule without copying another controller.

### S36: coordinate a specialist team

Original URL: https://platform.claude.com/cookbook/managed-agents-cma-coordinate-specialist-team
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/managed_agents/CMA_coordinate_specialist_team.ipynb
Status: complete notebook prose/code; no stored outputs in this notebook.

Verified: `make_agent` builds separate role prompts/toolsets; coordinator sequencing expresses research-to-case-selection dependencies while pricing can run independently. JSON handbacks are requested through `send_to_parent` in prompts. The case picker and pricer receive the broad `agent_toolset_20260401`, despite prose implying narrow file access. File isolation and strict output validation are not demonstrated by those prompts.

Adapt: bounded objective, explicit inputs, dependencies, role tools, and validated handback. In software tasks add owned paths, evidence references, failure state, and a snapshot identity. Keep output validation in the integration owner.

Reject: using specialist names as evidence of skill; assuming role prompts enforce filesystem access; calling any `session.status_idle` a completed deliverable. The original helper explains idle can also mean a tool needs a response. The proposal extraction reads the first matching write, so it is not a reliable final-artifact reader after revisions.

Proposed target: portable task handoff schema in every seed, with native Claude/Codex adapters. Probe: forbidden-path access, malformed handback, missing evidence, and dependency arrival out of order. Current `factory-round.js` already adapts the task shape, but ownership prompts are not isolation.

### S37: verify with outcome grader

Original URL: https://platform.claude.com/cookbook/managed-agents-cma-verify-with-outcome-grader
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/managed_agents/CMA_verify_with_outcome_grader.ipynb
Status: complete source; stored rubric and rejection/acceptance trace read; no independent source fact-check of the example brief.

Verified: `user.define_outcome` gives description to the writer and rubric to a fresh service grader. The notebook states grader uses the same model and tools as writer, not necessarily a different model or a read-only role. Terminal outcomes distinguish satisfied, capped, failed, and interrupted. Its strongest reusable asset is a rubric demanding evidence for every criterion, citation support rather than mere existence, and a no-fire list to avoid scope creep.

Adapt: separate artifact quality from execution success, fresh grading context, frozen reviewer criteria, structured failed criteria, and bounded revisions. Strengthen access to read-only where feasible. A missing or failed grader cannot count as satisfied.

Reject: assuming a rubric alone guarantees actual checks, treating a live URL as claim support, and importing the service outcome loop as a native API. Its brief reconstruction from tool-call arguments is not proof of successful final filesystem state.

Proposed target: software and research evaluator contracts in each generated factory. Probe: wrong document type with correct domain, fabricated quote, missing artifact, cap/interruption, and a fully correct control artifact. Current historical judgment machinery is prior art, not proof of equivalent controls.

### S38: dynamic workflows

Original URL: https://platform.claude.com/cookbook/claude-agent-sdk-08-dynamic-workflows
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/claude_agent_sdk/08_Dynamic_workflows.ipynb
Status: complete markdown/code plus complete generated JavaScript stored in output cell 15.

Verified: the notebook explicitly identifies Workflow as a Claude Code feature, driven through Agent SDK. The useful code is `agent` with schemas, `pipeline` per-item stages, `parallel` barriers, explicit phase metadata, and the SDK logger retaining the latest result across launch and completion turns. The notebook restricts resume to the same session. Scraping script paths/task IDs with regex is explicitly described as unstable demo convenience.

Verified correctness gaps in the generated script: extraction lacks a complete unique claim-ID check; null verifier results are removed by `results.filter(Boolean)`; missing skeptic results preserve a confirmation; skeptic schema lacks an unverifiable option. A malformed or incomplete pipeline can therefore generate a plausible report. The final report is model-written with no deterministic reconciliation against expected IDs.

Adapt orchestration primitives and evidence shapes. Reject these fail-open branches and a fresh report agent for formatting that deterministic code can do. Native feature identity is documented; compatibility with the installed host and Loam's existing script remains unverified.

Proposed target: Claude native workflow adapter and common completion contract; equivalent Codex primitives require their own evidence. Probe duplicate/missing IDs, null verifier, unavailable skeptic, same-session resume, fresh-session replay, and edits with cached results. Complete project-level recovery must use durable records beyond Workflow's same-session resume.

### S39: async multi-agent orchestration

Original URL: https://platform.claude.com/cookbook/patterns-agents-async-multi-agent-orchestration
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/patterns/agents/async_multi_agent_orchestration.ipynb
Status: complete source and stored introduction/sleep demo traces.

Verified: reusable code shapes are `Hub.post/drain`, inbox delivery appended to a tool result, async task creation, explicit status, and `finally` cancellation followed by gathering child tasks. This is Messages API client orchestration. It demonstrates mechanics with introductions and sleeping, not software or scientific competence.

Verified gaps: the array `maxItems` bounds one spawn request, not cumulative live helpers. The implementation has no global admission control, durable state, parent-death recovery, filesystem ownership, or independent completion evidence. A max-turns exit is labeled done and returned as text. Inbox delivery only reaches tool-result boundaries; a final answer can exit before draining pending messages.

Adapt lifecycle ideas and event-driven waiting when a native host lacks them. Reject installing this as another loop around existing native agents.

Proposed target: common task statuses and native adapter contract, including completed, failed, cancelled, capped, and blocked. Probe repeated spawn requests, completion before last message, helper crash, parent cancellation, and missing task reports. Enforce the user's selected parallel limit outside agent prompts. Do not treat `parallel()` barriers as equivalent to asynchronous messaging and cancellation.

### S40: programmatic tool calling

Original URL: https://platform.claude.com/cookbook/tool-use-programmatic-tool-calling-ptc
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/tool_use/programmatic_tool_calling_ptc.ipynb
Status: complete source; original expense API helper read; selected stored traces and comparison read. Display output truncates portions of generated execution code, so no complete generated-program audit is claimed.

Verified: `allowed_callers`, code-execution tool, container reuse, and caller-type handling separate model-visible results from execution-only raw data. Native shell batching can achieve aggregation and filtering, but lacks this exact API/container contract. Both notebook loops use shared mutable conversation state and have no turn cap. Counts derived from assistant messages omit the final response, which is never appended; the separately incremented API counter is the relevant counter. Stored examples are not a reproducible production benchmark.

Adapt: compute deterministic operations in code, batch independent reads, filter large outputs before model context, preserve raw evidence separately, and return compact provenance-bearing summaries.

Reject: extra API runtime in every seed merely to obtain batching; unconditional token/latency promises; copying model/API settings outside the user's selected native family.

Proposed target: domain tools and evidence collection instructions usable through either native host. Probe identical totals and source coverage between raw and compact output, error propagation, timeout, and bounded record processing. Arithmetic correctness must survive filtering, not merely produce shorter context.

### S41: tool search with embeddings

Original URL: https://platform.claude.com/cookbook/tool-use-tool-search-with-embeddings
Pinned source: https://github.com/anthropics/claude-cookbooks/blob/a97b9a2dc300635f0c26b5e05d0b54bbe0279ee5/tool_use/tool_search_with_embeddings.ipynb
Status: complete source and stored tool-search/demo outputs read.

Verified: useful components are `tool_to_text`, ranked tool lookup, and `tool_reference` return blocks. However, the conversation sends all tools without `defer_loading`. Both stored examples directly invoke domain tools without discovery. Current official documentation says non-deferred definitions enter context immediately. The notebook therefore does not demonstrate its claimed deferred-loading savings. Evidence: source cells 5/19/21/23 and [official deferred-loading contract](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool).

Verified: it uses dot products while relying on a generic normalization-default claim; current [SentenceTransformer reference](https://sbert.net/docs/package_reference/sentence_transformer/model.html) defaults `normalize_embeddings` to false. Whether the selected model internally normalizes was not checked. `top_k` is declared number, lacks bounds, and goes directly into slicing. The mock fallback calls unknown tools successful.

Adapt catalog descriptions and on-demand discovery, with permission-filtered catalogs. Reject this implementation as an installation-ready asset and reject its savings percentage as Loam evidence.

Proposed target: each project's capability/skill catalog, using native discovery first. Probe unavailable/disallowed tools, unknown names, empty matches, numeric bounds, and measured definition tokens. Validate retrieval quality before adding an embedding dependency.

### S42: repository overview

URL: https://github.com/anthropics/claude-cookbooks
Status: full README and LICENSE; recursive tree inventory; assigned notebook source and named helpers only. No whole-repository audit.

Verified: this is a recipe collection with multiple execution substrates. MIT source can be adapted with notices. Do not install the repository as a mandatory runtime dependency or imply its catalogue has been vetted.

Adopt a pinned provenance entry for any adapted code; adapt patterns into the correct native extension point. Reject wholesale copying, model IDs carried over from demo defaults, and dependency installation inferred from a notebook setup cell.

Proposed target: source/provenance manifest shipped with any reused asset. Probe each cited file at the pinned revision and ensure copied substantial portions carry attribution; maintain separate host/version compatibility evidence. Factory inclusion in every seed is a user requirement, so useful contracts must render with the project rather than depending on this machine's notebooks or private setup.

## E-WORKFLOWS: current native workflow contract

URL: https://code.claude.com/docs/en/workflows
Status: full substantive live documentation read, including implementation example, permissions, model substitution, limits, and replay. No installed-host probe.

Verified: this confirms S38's native feature identity. Stopped, blocked, or unrecoverable agent calls can return null. Replay follows agent start order; a failed agent invalidates later results, including completed siblings. Same-session saved results can survive CLI exit and session resumption; a fresh session starts anew. Native workflow size guidelines are advice, not hard caps. Organization model policy can substitute a requested model.

Version qualification: documentation places human-origin keyword restrictions at v2.1.210, workflow-authoring at v2.1.248, and the medium default size guideline at v2.1.219. These describe documented behavior, not a measured installed version. The keyword in a print-mode prompt is not an orchestration guarantee.

Adapt: explicit native launch, project-saved workflow, null-to-unmet conversion, requested-versus-effective model receipts, and replay-safe operations. Reject classifying a filtered-null report as complete or a size guideline as budget enforcement.

Proposed target: generated Claude workflow profile and recovery tests. Probe substitution outside the allowed family, failed middle-stage replay, missing saved results, and stop-before-relaunch. Load the native authoring reference before future workflow implementation.

## Historic Loam lessons and necessary corrections

Verified: `docs/research/advisor-and-managed-agents.md` and `docs/research/INDEX.md` were read as historical notes, alongside `bin/factory.d/factory-round.js` and `_common.md`. These source files show what Loam previously adapted. Their old local probe results were not reproduced.

- Preserve the costly-decision consultation rule and independent rechecking of builder evidence. The notes' claims that PTC equals Bash, embedding search equals native ToolSearch, and asynchronous messaging equals `parallel()` should become narrower statements about overlapping benefits.
- S38 is native Workflow according to the original notebook. Still verify host contracts before using the current `factory-round.js`; its artifact-file handbacks differ from the notebook's advice to return findings to the script, and it compensates for a Node parser rejecting top-level return. A Node syntax check does not prove Workflow runtime semantics.
- The existing workflow hardcodes high/xhigh effort and `_common.md` pins Agent calls to Opus. Those are incompatible with treating the user's effort and family selections as the controlling policy across all roles. Propose explicit resolved model/effort records, with Astra driver restricted to Astra/Sol/Terra and Fable driver restricted to Fable 5.1/Opus 4.8. This is the user's requirement, not a claim that these notebooks implement Codex routing.
- Existing planner ownership is a convention plus overlap checking. The integrator is told to restore files and make the working tree clean. Do not port that instruction without a snapshot and ownership-safe integration policy, since cleanup could erase unrelated edits.
- A complete factory in every seed needs portable contracts and project state, per-project setup checks, and native adapters. Cookbook API keys, cloud sessions, host user directories, and current private setup must not be hidden prerequisites. Lack of optional Workflow/advisor support should have an explicit native solo path where semantics permit, without falsely claiming requested parallel or advisor behavior happened.

## Self-attack and residual limits

What input breaks the borrowed designs? Missing results, malformed task IDs, invalid search limits, parent termination, stale resume state, and idle events requiring action. Each is mapped above to a proposed negative probe rather than papered over as success.

Which path was not checked? Installed host execution, native Codex analogues, cloud service behavior, library dependency internals, and the unassigned cookbook catalogue. These remain unverified.

What changed without a test? Only this research report and read-only temporary acquisition files. No runtime implementation was changed, so no passing implementation-test claim is made.

Which draft claim lacked evidence? Broad runtime equivalence and performance claims were removed; actual compatibility and outcome improvement remain to be measured. The source flaws above are verified by inspection, not reproduced failures.
