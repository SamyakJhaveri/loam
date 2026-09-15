# TypeScript versus Python: a decision Samyak can inspect

Status: completed comparison followed by explicit user acceptance of TypeScript. The user welcomes learning the language and does not want unfamiliarity to constrain the design. The comparative reasoning below is retained as decision history; conditional language-selection recommendations are superseded by this acceptance. Implementation validation and runtime authorization remain separate. Read this alongside [runtime and layout](engine-runtime-and-layout.md). It corrects the earlier comparison's underweighting of a direct Python implementation.

Critical point: every generated project inherits the factory's installation and maintenance obligations.

## The recommendation, without a sales claim

Recommendation: retain TypeScript as the preferred candidate for a small factory package, with direct Python as a serious alternative. Choose on native capability fit, recovery, packaging and owner readability. Do not choose on a claim of lower token bills or faster research: neither has been measured. Existing lifecycle, authority, memory and distribution decisions are independent of the language choice.

Verified: local main remains `d627bb2755ad49865f798bcb095800ddd2ad1ced`. The header and implementation of `bin/factory` show a Bash controller. The current comparison is therefore a new implementation decision, not a migration from an established Python engine. Git status before this discussion showed only the untracked architecture working directory.

## What TypeScript would mean in daily work

Verified: TypeScript adds a static checker to JavaScript. Static means it examines code before execution. Its type annotations describe expected values and are erased when compiling to JavaScript. Node executes the resulting program outside the browser. It does not require a website or frontend framework. [TypeScript introduction](https://www.typescriptlang.org/docs/handbook/typescript-from-scratch.html).

Illustration: Loam originally distinguishes a running task from a finished task. Later we add a task waiting for a lead decision. With an explicit union of those states and an exhaustive handler, the checker can identify handlers that have not accounted for the new state. The relevant TypeScript mechanism is documented as discriminated unions and exhaustiveness checking. This is a development check, not a guarantee that every state transition is correct. [Narrowing and exhaustiveness](https://www.typescriptlang.org/docs/handbook/2/narrowing.html).

Recommendation: make the message vocabulary readable: work started, input pending, native turn ended, check recorded and lead decision received. Keep important distinctions explicit. TypeScript cannot establish whether an experiment supports a hypothesis or whether a receipt is authentic. External messages still need runtime validation, authority checks and evidence review. Python supports annotations and static checkers too; a fair comparison uses checked Python, not loosely typed scripts. [Python typing](https://docs.python.org/3/library/typing.html).

Recommendation: ordinary use should require understanding the research task and the factory's visible decisions. Project customization should normally be configuration, Markdown methods and declared extension commands. Maintaining the engine does require learning JavaScript behavior, asynchronous operations, modules and TypeScript types. Agent assistance does not remove Samyak's need to inspect consequential behavior. Build understanding through a walkthrough of a real ticket and a small module when implementation is authorized, rather than a separate web-development curriculum.

## SWOT for this project

The following is engineering judgment informed by the linked capability evidence, not an empirical ranking.

| SWOT | TypeScript factory | Direct Python factory |
|---|---|---|
| Strengths | Explicit message/state contracts; useful compiler feedback across modules; direct fit with the audited Claude TS interface; Node supports concurrent I/O. | Direct official Claude SDK; standard SQLite facilities and Unix locking; no TypeScript-to-JavaScript release build; potentially easier personal inspection if Python is familiar. |
| Weaknesses | New language and runtime concepts for Samyak; release compilation and source/output verification; package/runtime maintenance; selected SQLite and lock mechanisms need proof. | Dependency and interpreter isolation still needed; disciplined static checks and runtime validation remain necessary; required native controls may differ from TS. |
| Opportunities | Make agent-produced engine changes mechanically reviewable; keep shared contracts consistent; later use an OpenCode TS client if its capabilities fit. | Use built-in operational facilities to simplify the initial host implementation; integrate Python extensions naturally while retaining a separate factory environment. |
| Threats | Complex type machinery, dependency sprawl or hidden setup costs; false confidence from a passing compiler; shared TS shapes becoming an accidental requirement for external workers. | Treating research environments as factory environments; using private SDK internals to bridge gaps; mistaking Unix behavior for portable recovery. |

## Native integration: a correction to the previous argument

Verified: Anthropic explicitly supports its native Agent SDK in both Python and TypeScript. Python is not inherently a reduced reasoning loop or a requirement for an extra TS bridge. The Python reference documents persistent streaming, interruption, hooks, tools, permission/model controls and task stopping. That establishes substantial capability, not complete equivalence for Loam's precise evidence and recovery contract. [SDK overview](https://code.claude.com/docs/en/agent-sdk/overview), [Python reference](https://code.claude.com/docs/en/agent-sdk/python).

Verified: the preserved [Claude interface evidence](prior-design/native-claude-evidence.md) records pinned TypeScript declarations for initialization, interruption receipts, task controls and a process-spawn seam. These were source observations, not live conformance tests. Independent current Python inspection did not find equivalents for every TypeScript control, including runtime flag application and dynamic MCP server replacement. Absence from those searched public surfaces is a bounded finding, not proof that a capability is impossible. Do not make optional dynamic controls decisive unless an accepted workflow needs them. Public-interface equivalence still needs a focused comparison.

Verified: official Codex documentation supplies both TS and Python SDKs and describes app-server for richer clients. The preserved [Codex audit](prior-design/cookbook-codex-audit.md) explains the concrete approval/event-routing reasons for a narrow direct protocol client at its recorded source pin. Those are client behavior concerns, not a Python-language limitation. Choosing TypeScript does not automatically make its high-level Codex SDK the right adapter. [Codex SDK documentation](https://learn.chatgpt.com/docs/codex-sdk).

Verified: Python's SQLite documentation includes URI `mode=rw`, which refuses to create a missing database. Its Unix `fcntl.flock()` offers a direct candidate for lifetime file locking. These address open implementation questions in the Node design. They do not establish database identity, prevent malicious file replacement, prove crash recovery or supply Windows support. Python's SQLite module availability and actual linked SQLite version must also be verified in supported installations. [SQLite interface](https://docs.python.org/3/library/sqlite3.html), [Unix locking](https://docs.python.org/3/library/fcntl.html).

Likely: Python could offer simpler packaging for these specific operational mechanisms. This is a stronger argument than familiarity alone. Node's selected built-in SQLite binding remains marked Release Candidate in its version-branch documentation; an alternative binding or host helper has its own distribution cost. [Node SQLite source](https://raw.githubusercontent.com/nodejs/node/v24.x/doc/api/sqlite.md).

Recommendation: reject the circular argument that TS is best merely because an earlier proposal selected a TS bridge. Retain TS on its independently useful contract tooling and inspected native interface, conditional on the packaging/ownership gates. Upgrade direct Python from a vaguely narrower fallback to a contender against the same operational obligations. A Python core plus TS bridge is warranted only if a necessary interface gap justifies maintaining both.

## Cost, tokens and performance are different questions

Verified: model token counting applies to material submitted to the model, including messages and tool definitions. Prompt caching concerns repeated eligible prompt content. Those mechanisms do not assign a language discount to a controller. Subscription usage and API charges are different accounting surfaces; record actual native usage and billing context without converting one into the other by assumption. [Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting), [Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching).

Likely: ordinary research inference cost will be governed more by native work, supplied context and repeated attempts than by the factory implementation language. Local compiler checks and local protocol messages are not model calls; they consume model context only if their content is supplied to a model. When agents develop the factory, TS annotations can increase source text while useful compiler feedback can avoid repair work. Net savings are unknown. No evidence establishes which language the permitted models implement more reliably for this project.

Recommendation: optimize cost per accepted useful outcome, accounting for failed attempts and human review. Do not minimize source characters at the expense of readable contracts. Keep the full factory installed, but load its source and detailed internals into agent context only when relevant. Ordinary project work should not automatically ingest the engine, compiled mirrors, dependency tree and full event archive. Required instructions, current constraints and necessary evidence must still be delivered. This follows the repository's existing [asset-layer context distinction](../ASSET-LAYERS.md).

Verified: Node's documentation explains its suitability for I/O, meaning waiting for external processes, networks and storage. Python's asyncio also supports concurrent I/O and subprocesses. Both require keeping blocking operations off their event-reading path. [Node event loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop), [Python asyncio](https://docs.python.org/3/library/asyncio.html).

Assumption: native model/tool/experiment time will dominate typical Loam task elapsed time. To confirm: measure controller overhead separately from native and research execution. No throughput, memory, startup, energy or token benchmark was run. Choosing TS does not accelerate a Python experiment, compiled solver or remote model. Compute-heavy research remains in project-selected tools and isolated jobs.

## File structure and future providers

Recommendation: choose directory organization separately from implementation language. Markdown remains suitable for human methods and decisions; configuration remains declarative; SQLite/artifacts keep their accepted roles. A coherent module layout is possible with either `.ts` or `.py`. Neither a folder tree nor Markdown alone supplies durable transactions, process ownership or validated recovery.

Verified: OpenCode provides a JS/TS SDK and an HTTP server described by OpenAPI with streamed events. TS offers a convenient client option; the protocol permits other languages. Optional integration still needs a behavior audit before claiming equivalent steering, evidence or native capability. [OpenCode SDK](https://opencode.ai/docs/sdk/), [OpenCode server](https://opencode.ai/docs/server/).

Assumption: the user's term “PyAgent” refers to a future agent product, but its identity is not established. Obtain its exact repository or documentation when prioritizing that adapter. No implementation choice depends on guessing it now.

Recommendation: preserve versioned language-neutral boundary records and capability checks. Python research extensions should be possible through a declared command and validated result contract without importing the factory's private TS modules. These commands obey the existing execution, evidence and authority rules; this adds no general plugin framework or new first-slice provider.

## Historical decision conditions considered before acceptance

Recommendation: before authorizing the full implementation, compare the required Claude controls and the smallest ownership/storage/install proof. Do not build duplicate complete factories just to choose a language. If Python satisfies required native controls and materially simplifies trustworthy installation/recovery, prefer it. If TS meets those obligations cleanly and keeps the engine understandable, retain it. A required feature available only through unsupported Python internals strengthens the TS case; optional feature convenience alone does not settle it.

Proposed later evaluation, not run: replay the same recorded native events through small candidate mechanisms, including a pending approval while other events arrive, a busy database, missing registered storage, supervisor death and competing ownership. Require equivalent authority and recovery outcomes before comparing local latency, peak memory, setup burden and dependency artifacts. Do not compare a correct slower implementation against an incorrect fast one as if both were viable.

Proposed later maintenance comparison: give the same model and user-selected effort equivalent bounded changes in each implementation, with matched requirements, native versions, tool access, context policy and acceptance checks. Use fresh matched workspaces; account for run-order/learning and multiple tasks. Record success, total tokens including failed repairs, elapsed time and human review effort. A tiny sample or source-token count alone cannot establish a general language advantage. These are comparison specifications, not authorized model jobs or executable acceptance scripts.

## Outside challenge, scope and verification

Verified: filename and content searches of the available local skill roots found no installed “surprise me” skill. The brainstorming skill and independent Python/economics critiques supplied the requested outside perspective. No claim is made to have used the missing skill.

Recommendation: the surprising design constraint is how little of the factory a researcher should have to understand or load into context for ordinary work, while still being able to inspect every consequential decision. The full factory must ship; its entire implementation need not occupy every session. This is an operating-model benefit that must hold in either language.

Self-attack: type checking cannot authenticate evidence, optional SDK differences must not masquerade as required features, and built-in Unix locks do not prove portable recovery. The comparison explicitly retains those boundaries. Language economics and owner learning effort remain unmeasured. Runtime implementation, dependencies, paid model probes and release actions remain deferred.

Verified: independent cross-critique identified a residual hybrid-only language argument in the older runtime story. That paragraph now explicitly states that both direct Python and TypeScript can share core/adapter definitions in one language. The bounded review found no other concrete comparison, savings or authority gaps. Documentation checks reported `Language comparison document checks: PASSED`; these validate links, preservation and edit scope, not the proposed runtime.
