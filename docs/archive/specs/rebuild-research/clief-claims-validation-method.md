# Clief claims: validation method and evidence map

> **Prior research only. Fresh verification required.** This matrix is a handoff
> artifact from an earlier research pass. It is not an accepted Loam decision.
> Claude must verify every claim, source, product mechanic, date, and proposed
> experiment afresh against current primary evidence before using it in a plan.
> Where fresh evidence conflicts with this file, report the conflict and follow
> the fresh evidence.

**Checked:** 2026-08-31 PDT
**Input:** `docs/specs/cliefnotes-wisdom.md`
**Purpose:** Decide which Clief claim families describe a real product feature, which have a credible mechanism, and which have measured outcome support.

## Bottom line

The Clief corpus is strongest when it says to select relevant repository context, plan interdependent edits, execute checks, preserve durable handoffs, and parallelize only independent work. These ideas have direct product support and some empirical support.

The corpus is much weaker when it turns those ideas into universal layout rules. The searched primary sources do not establish a causal benefit for a thirty-to-fifty-line root file, a specific folder count, a specific file-count threshold, or a fixed agent count. They also do not show that hooks improve code quality merely because hooks exist.

The practical rule for Loam is therefore:

1. Treat official documentation as evidence that a mechanism exists.
2. Treat architecture articles as plausible implementation guidance.
3. Treat comparative studies as outcome evidence only for the task and setup they tested.
4. Treat exact Clief heuristics as hypotheses until Loam measures them.

## Evidence classes

| Class | Question answered | What qualifies | What does not qualify |
|---|---|---|---|
| **F: feature existence** | Can the current product do this? | Current official documentation or source code | A tutorial, anecdote, or old screenshot |
| **M: mechanism plausibility** | Is there a credible reason this could help? | Product architecture, a directly relevant experiment, or a peer-reviewed adjacent result | “It feels cleaner” |
| **O: measured outcome** | Did it improve an observable result? | A comparison with a baseline, fixed task, and explicit metric | A successful demo with no comparator |

An **O** result does not automatically transfer to Loam. The result must still match the model, repository scale, task type, tools, and cost constraints.

## Research method

I mapped the headings and record identifiers in `cliefnotes-wisdom.md` to six requested surfaces: repository instructions, context selection, planning, verification, hooks, and multi-agent coding. I then checked current official Claude Code and Codex documentation. I also checked first-party Anthropic and OpenAI engineering reports and peer-reviewed proceedings from ACL, EMNLP, FSE, ICML, NeurIPS, and TACL.

Secondary blogs were excluded. Vendor posts are labeled as first-party reports. They are useful evidence about the vendor's own system, but they are not independent replications. A scoped search found no controlled study that isolates the effect of `CLAUDE.md` or `AGENTS.md` length, nested instruction placement, or coding-agent hooks on repository task success. This is a search result, not proof that no such study exists.

## Claim-family map

### 1. Folder structure and context routing

**Clief families:** `N-0023`, `N-0029`, `N-0058`, `N-0148`, `N-0155` to `N-0157`, and related folder-sizing claims.

- **F:** Claude Code loads root and ancestor `CLAUDE.md` files at launch. It loads descendant files when it reads files in those directories. Path-scoped rules also load on matching reads. Its documentation says imported files still enter context and recommends concise, specific instructions. [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
- **F:** Codex reads an instruction chain from the repository root to the working directory. It concatenates one selected instruction file per level and applies a configurable combined byte limit. [Codex `AGENTS.md` documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- **M:** Long-context models do not use every position equally well. TACL experiments found that answer use can degrade when relevant evidence is placed in the middle of a long context. [Liu et al., TACL 2024](https://aclanthology.org/2024.tacl-1.9/)
- **M/O:** Repository-specific retrieval is useful for code. RepoCoder's iterative retrieval-and-generation method improved its in-file baseline by more than ten percent across its reported repository-level completion settings. This supports selective context retrieval, not a specific folder tree. [Zhang et al., EMNLP 2023](https://aclanthology.org/2023.emnlp-main.151/)
- **O, first-party observational:** OpenAI reports that its Codex-built internal product moved from a large `AGENTS.md` to a short map plus structured repository documentation, execution plans, linters, and documentation checks. The report describes substantial delivery, but it is a single uncontrolled case. It does not isolate the router's effect. [OpenAI harness engineering report](https://openai.com/index/harness-engineering/)

**Judgment:** The claims to route and progressively disclose context are credible. The exact Clief thresholds for lines, files per directory, and number of workspaces remain unsupported heuristics.

### 2. `CLAUDE.md`-style rules

**Clief families:** `N-0249`, `N-0251`, `N-0252`, `N-0255` to `N-0260`, and `N-0273` to `N-0277`.

- **F:** Claude Code documents `CLAUDE.md` as persistent context, not hard enforcement. It recommends keeping always-needed facts there and moving multi-step or path-specific material to skills or scoped rules. [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
- **F:** Codex documents nested `AGENTS.md` files, closer-directory precedence, and direct commands to inspect loaded instructions. [Codex `AGENTS.md` documentation](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- **M:** Concise routing can reduce irrelevant context and stale duplication. The mechanism is consistent with long-context and retrieval evidence above.
- **O:** No searched controlled study compares a short router, a monolithic instruction file, and no instruction file on the same repository tasks.

**Judgment:** “Root file as map” is a good hypothesis and matches current vendor guidance. “Thirty to fifty lines” is not a validated optimum. Loam should test instruction adherence and task success, not optimize a line count by itself.

### 3. Skills

**Clief families:** `N-0310`, `N-0311`, `N-0313`, `N-0330`, `N-0340`, and `N-0347`.

- **F:** Claude Code skills have an always-visible discovery layer and a body that loads when the skill is used. The product supports direct invocation, model invocation, supporting files, and isolated subagent execution. [Claude Code skills documentation](https://code.claude.com/docs/en/skills)
- **M:** Moving a repeated procedure out of always-loaded instructions can save context while retaining reusable behavior. That follows from the documented load mechanism. It does not prove better outputs.
- **O:** The searched sources do not provide a controlled coding study showing that packaging the same procedure as a skill outperforms putting it in the task prompt.

**Judgment:** Skills are a real on-demand mechanism. Their value depends on correct discovery, invocation, and adherence. Those must be tested separately.

### 4. Hooks

**Clief families:** the six hook records under section 4, plus enforcement claims such as `N-0275`.

- **F:** Claude Code hooks can run before and after tool use and at session, prompt, compaction, subagent, and stop events. A `PreToolUse` hook can allow, deny, ask, or rewrite a tool request before execution. [Claude Code hooks reference](https://code.claude.com/docs/en/hooks)
- **F:** Codex hooks expose lifecycle events including session start, tool use, permission requests, compaction, subagent start or stop, and turn stop. Synchronous pre-tool hooks can block or rewrite supported calls. [Codex hooks documentation](https://learn.chatgpt.com/docs/hooks)
- **M:** A client-side blocking hook can enforce a machine-checkable policy more reliably than natural-language guidance because the hook runs outside the model's choice. Claude Code makes the same distinction between context and enforcement. [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
- **O:** No searched comparative study shows that adding hooks improves end-to-end coding quality. A hook can also fail silently through a wrong event, matcher, path normalization, output shape, or timeout.

**Judgment:** Hooks have strong mechanism evidence for enforcement and observability. They have no automatic outcome credit. Each hook needs positive, negative, and bypass fixtures.

### 5. Agents and subagents

**Clief families:** `N-0360`, `N-0361`, `N-0373`, `N-0374`, `N-0393`, `N-0410`, `N-0424`, and `N-0705`.

- **F:** Claude Code subagents use isolated contexts and return results to the caller. Agent teams use independent contexts, direct messaging, and a shared task list. Agent teams remain experimental and the official documentation warns about coordination cost, token cost, dependent tasks, same-file edits, and session limits. [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) and [agent teams](https://code.claude.com/docs/en/agent-teams)
- **F:** Codex can spawn specialized agents in parallel, return summaries, and configure agent roles. Its documentation also warns that parallel writes can cause conflicts and that subagent workflows consume more tokens. [Codex subagents documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents)
- **O, first-party:** Anthropic reports that its research multi-agent system outperformed a single-agent system on an internal breadth-first research evaluation. It also reports much higher token use and says coding tasks often have fewer independent branches. This is evidence for conditional parallelism, not for multi-agent coding in general. [Anthropic multi-agent research report](https://www.anthropic.com/engineering/multi-agent-research-system)
- **O, first-party case:** Anthropic reports that a parallel agent team built a compiler and describes tests, isolated checkouts, task locks, and continuous integration as key controls. The project is a stress test without a matched single-agent baseline. [Anthropic compiler report](https://www.anthropic.com/engineering/building-c-compiler)
- **O, peer-reviewed but limited transfer:** ChatDev reports benefits from role-based multi-agent communication on its software-generation evaluation. Its tasks and waterfall-style greenfield setup differ from maintenance work in an existing repository. [Qian et al., ACL 2024](https://aclanthology.org/2024.acl-long.810/)

**Judgment:** Parallel agents are supported when tasks are independent, read-heavy, or use distinct files. The evidence does not support “more agents is better,” nor the claim that the producing agent must never verify its own work. Independent review is a testable risk control, not a universal law.

### 6. Memory and session continuity

**Clief families:** `N-0430` to `N-0439`, `N-0453`, `N-0455`, and the session-boundary records under section 7.

- **F:** Claude Code has repository-scoped auto memory and persistent `CLAUDE.md` instructions. It documents what loads at session start and how subagent memory differs. [Claude Code memory documentation](https://code.claude.com/docs/en/memory)
- **M/O, first-party case:** Anthropic's long-running coding harness used an initializer, incremental tasks, and durable artifacts to bridge sessions. The report says compaction alone did not produce the target long-horizon behavior in its setup. It is a first-party experiment on full-stack application work, not a general controlled result. [Anthropic long-running harness report](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- **M/O, first-party case:** A later Anthropic harness used planner, generator, and evaluator roles plus structured artifacts. The report also notes that a newer model changed which context-reset mechanism was useful. This is evidence that harness value is model-dependent. [Anthropic 2026 harness report](https://www.anthropic.com/engineering/harness-design-long-running-apps)

**Judgment:** Durable state is a plausible continuity mechanism. Loam must test recovery from correct, missing, and stale handoffs. A memory file that is confidently wrong can be worse than no memory file.

### 7. Plan and verification workflow

**Clief families:** `N-0483`, `N-0508`, `N-0520` to `N-0526`, `N-0543` to `N-0554`, and `N-0562` to `N-0603`.

- **F:** Claude Code plan mode reads and proposes without editing until approval. Its official workflows also recommend delegating large exploration when raw reads would fill the main context. [Claude Code common workflows](https://code.claude.com/docs/en/common-workflows)
- **M/O:** CodePlan treats repository-wide change as an incremental planning problem. In its repository evaluation, the planned system passed validity checks on five of six repositories while baselines with similar contextual information passed none. The tested tasks were package migration and temporal edits, so the result does not validate every PRD or plan template. [Microsoft Research CodePlan report](https://www.microsoft.com/en-us/research/publication/codeplan-repository-level-coding-using-llms-and-planning/) and [FSE publication record](https://www.microsoft.com/en-us/research/project/967350/publications/)
- **M/O:** SWE-agent found that an agent-oriented interface for repository navigation, editing, and program execution materially changed coding-agent performance on SWE-bench and HumanEvalFix. This supports improving the feedback interface around the model. It does not isolate any one Loam rule. [Yang et al., NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/5a7c947568c1b1328ccc5230172e1e7c-Abstract-Conference.html)
- **M/O:** Reflexion improved coding and other tasks by feeding explicit task feedback into later trials. Its HumanEval result supports iterative feedback, but function-level synthesis is much smaller than repository maintenance. [Shinn et al., NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b44b878bb782e6954cd888628510e90-Abstract-Conference.html)
- **M/O:** Repo-level compiler feedback can guide retrieval and repair of project-specific context. CoCoGen reports this on project-level code generation. [Bi et al., Findings of ACL 2024](https://aclanthology.org/2024.findings-acl.138/)
- **M, first-party practice:** Anthropic recommends evaluating agent outcomes with multiple trials and a mix of code-based, model-based, and human graders. It distinguishes the transcript from the actual end state and recommends inspecting both. [Anthropic agent-evals report](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

**Judgment:** Planning and execution feedback have the strongest transferred evidence in the Clief corpus. The evidence supports plans for interdependent change, not a PRD before every edit. Verification should target end state and hidden negative fixtures, not the agent's verbal claim that it checked.

### 8. Prompting

**Clief families:** `N-0725` to `N-0736`, `N-0744`, `N-0747`, `N-0773` to `N-0780`, and `N-0813`.

- **M, first-party:** Anthropic describes context engineering as selecting and maintaining the tokens needed across an agent loop. It recommends treating context as finite and curating it as the trajectory grows. [Anthropic context-engineering report](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- **O, adjacent:** ICML experiments show that irrelevant context can distract language models. The tasks were reasoning problems, not coding repositories. [Shi et al., ICML 2023](https://proceedings.mlr.press/v202/shi23a.html)
- **O:** No searched source establishes one universal prompt schema for repository coding. The Clief requirements to expose constraints and output shape are testable. The instruction to request hidden step-by-step reasoning is not required by current product mechanisms and should not be treated as an evidence-backed coding control.

**Judgment:** Specific task context and observable acceptance criteria are credible. Prompt templates should be evaluated by task results, not by their rhetorical completeness.

### 9. Model and effort selection

**Clief families:** `N-0795` to `N-0803`, `N-0816` to `N-0823`, and `N-0636`.

- **M:** The multi-agent and long-running harness reports show that model changes can alter which scaffolding helps. [Anthropic multi-agent research report](https://www.anthropic.com/engineering/multi-agent-research-system) and [Anthropic 2026 harness report](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- **O:** The searched sources do not validate the Clief sixty-thirty-ten split or a permanent frontier-versus-small-model assignment. Model and cost claims are time-sensitive.

**Judgment:** Keep the harness fixed and evaluate candidate model and effort settings on Loam tasks. Record success, tokens, tool calls, latency, and cost. Do not infer model value from a public benchmark alone.

### 10. Automation and loops

**Clief families:** `N-0827`, `N-0828`, `N-0835` to `N-0848`, `N-0850`, `N-0874` to `N-0892`.

- **M/O, first-party case:** OpenAI reports that mechanical repository checks, review, testing, and recovery increased the autonomy of its internal Codex workflow. The report is observational and bundles many changes. [OpenAI harness engineering report](https://openai.com/index/harness-engineering/)
- **M/O, first-party case:** Anthropic's compiler project used a continuous loop, isolated workspaces, test suites, task locks, and continuous integration. The report also warns that the verifier must be high quality or agents optimize the wrong target. [Anthropic compiler report](https://www.anthropic.com/engineering/building-c-compiler)
- **O:** No searched source validates the Clief three-to-fifteen-step automation band or a universal frequency threshold.

**Judgment:** Automate deterministic checks after they pass positive and negative fixtures. Keep high-consequence actions approval-gated. Measure false blocks and false permits.

### 11. Other: security, code craft, and setup

Most claims in this family are standards, local conventions, or product mechanics rather than agent-harness hypotheses. Validate security controls against their owning standards and test implementations with fixtures. Validate style rules with repository outcomes such as defect rate, review findings, and maintenance cost. Recheck setup commands against current product documentation before each release.

## Loam experiment protocol

Use a clean fixture repository for each trial. Pin the repository commit, model, effort, tool set, permissions, and task prompt. Randomize condition order. Run repeated trials because agent output varies. Grade the final repository state before reading the transcript. Then inspect the transcript to explain failures.

Use these common measures:

| Measure | Observable definition |
|---|---|
| Task success | Hidden fail-to-pass tests pass and existing pass-to-pass tests remain green |
| Instruction adherence | Required actions completed divided by checkable required actions |
| False-green rate | Trials claiming success while a hidden check fails |
| Context precision | Relevant files read divided by all files read |
| Context recall | Required evidence files read divided by all required evidence files |
| Scope drift | Files changed outside the gold task scope |
| Efficiency | Input and output tokens, tool calls, wall time, and cost |
| Human burden | Review minutes, interventions, and unresolved questions |
| Parallel overhead | Merge conflicts, duplicate work, coordination messages, and idle time |

### Test 1: root router and selective context

**Hypothesis:** A short root router plus task-scoped documents improves adherence and context precision without lowering task success.

| Arm | Setup |
|---|---|
| A | Short root map. Detailed rules live in the relevant nested file or skill. |
| B | The same facts are in one monolithic root file. |
| C | No project instructions beyond build and test commands. |
| Negative control | Same token count as A, but the added text is irrelevant to the task. |

Use maintenance tasks that require a known cross-file convention and tasks that do not require it. Record loaded instruction sources separately from file reads. Compare task success, checkable rule adherence, context precision and recall, tokens, and scope drift.

**Falsifier:** Reject the router claim if A does not improve adherence or efficiency over B and C, or if it lowers hidden-test success.

### Test 2: planning and durable handoff

**Hypothesis:** A reviewed plan helps on interdependent changes, while a durable handoff helps a fresh session resume accurately.

| Arm | Setup |
|---|---|
| A | Read-only plan, human or scripted plan check, then implementation. |
| B | Direct implementation with the same task and context budget. |
| Negative control | Plan contains one deliberately wrong dependency or stale next step. |

Run both a local one-file task and a repository-wide migration task. For continuity, stop after a fixed milestone and resume in a fresh session with the correct handoff, no handoff, or stale handoff. Measure defects caught before editing, hidden-test success, rework, unnecessary files changed, orientation accuracy, and time.

**Falsifier:** Limit mandatory plans to high-dependency work if planning does not help local tasks. Reject trust in handoffs if stale handoffs are followed more often than repository evidence.

### Test 3: verification gates and hooks

**Hypothesis:** A deterministic gate lowers false-green results, and a blocking hook enforces a narrow policy more reliably than prose alone.

| Arm | Setup |
|---|---|
| A | Natural-language instruction to test and verify. |
| B | The same instruction plus a deterministic post-change gate. |
| C | The same gate triggered through the hook under test. |
| Negative controls | A known failing fixture, a near-match event name, a nonmatching path, malformed hook output, and a bypass-form command. |

First run each new regression test against the unfixed fixture and require failure. Then run it against the fix and require success. For hooks, log every expected event and assert exact allow or deny behavior. Measure verifier sensitivity, specificity, false-green rate, missed hook events, false blocks, bypasses, latency, and hidden-test success.

**Falsifier:** Do not ship a hook that misses any safety-critical positive fixture or blocks legitimate negative fixtures above the agreed tolerance.

### Test 4: single agent, reviewer subagent, and parallel team

**Hypothesis:** Parallel agents help independent exploration and review, but not tightly coupled same-file implementation.

| Arm | Setup |
|---|---|
| A | One agent completes the task and self-checks. |
| B | One producer plus an independent reviewer with a bounded review brief. |
| C | Parallel agents own disjoint read-heavy or file-disjoint subtasks. |
| Negative control | Parallel agents receive dependent tasks that edit the same file. |

Match model and total token budget where possible. Run a bug triage task, a multi-area review, and a coupled implementation task. Measure true defect recall, false positives, hidden-test success, wall time, tokens, duplicate work, merge conflicts, coordination messages, and human interventions.

**Falsifier:** Keep a single agent when parallelism does not improve quality or time after token and coordination cost. Use an independent reviewer only when it catches defects the producer's own checks miss often enough to justify the added cost.

### Test 5: on-demand skill and memory value

**Hypothesis:** On-demand procedures reduce always-loaded context without reducing adherence, and correct memory helps only when repository evidence can override stale state.

| Arm | Setup |
|---|---|
| A | Procedure is always loaded in the root instructions. |
| B | Procedure is in an on-demand skill with a precise trigger. |
| C | Procedure is supplied directly in the task prompt. |
| Negative controls | Similar task that must not trigger the skill; stale memory that conflicts with code. |

Measure skill trigger precision and recall, procedure adherence, context tokens, task success, and whether the agent resolves memory-versus-code conflicts in favor of inspected repository evidence.

**Falsifier:** Keep a procedure always loaded if the skill misses required invocations or adds more recovery cost than context it saves. Disable or narrow memory if stale state causes uncorrected task errors.

## Decision rules for the rebuild

1. **Adopt now:** Documented feature plus a deterministic local conformance test. Examples are instruction discovery and hook event contracts.
2. **Pilot:** Plausible mechanism with transferred outcome evidence. Examples are selective context, durable handoffs, and independent reviewer agents.
3. **Do not canonize yet:** Exact numeric heuristics or workflow universals with no direct comparison.
4. **Retire:** A rule whose negative control performs the same or better on task success and total cost.
5. **Re-test after model or product changes:** Any harness component whose value depends on context behavior, planning, self-evaluation, or tool use.

## Source quality and limits

The peer-reviewed studies establish that context selection, planning, interface design, and execution feedback can change outcomes. They do not test Loam's exact files or current frontier coding agents. The vendor reports are more current and operationally close to Loam, but they bundle model, prompt, tool, and process changes. The proposed Loam trials are therefore the final evidence gate.
