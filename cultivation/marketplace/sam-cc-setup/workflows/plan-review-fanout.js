export const meta = {
  name: 'plan-review-fanout',
  description: 'Adversarial plan review as a grounded fan-out (canonical plan-reviewer checklist + elegance gate), adversarially verify BLOCK findings, converge to APPROVE / APPROVE_WITH_CHANGES / REJECT plus a verbatim revised handoff plan. Pass the plan path as args.',
  whenToUse: 'Reviewing a plan written in a prior session before execution. Parallel, grounded upgrade of the single-agent /plan-review skill. Invoke: /plan-review-fanout <path-to-plan.md> (the calling session writes the returned revised plan to disk).',
  phases: [
    { title: 'Ground', detail: '3 git/Bash agents verify the plan factual/code/reframe claims against the live repo' },
    { title: 'Review', detail: '5 plan-reviewer lenses: repo-rules, over-engineering, missing-decisions, completeness, ordering' },
    { title: 'Elegance', detail: 'step back + web-search for a fundamentally simpler approach' },
    { title: 'Verify', detail: 'adversarial refutation of every BLOCK finding (2 skeptics each)' },
    { title: 'Converge', detail: 'synthesize verdict + verbatim revised handoff plan' },
  ],
}

// ---- plan path comes from args: /plan-review-fanout <path>  (string) or args:{path} ----
const PLAN_PATH =
  (typeof args === "string" && args.trim()) ? args.trim()
  : (args && typeof args === "object" && typeof args.path === "string" && args.path.trim()) ? args.path.trim()
  : null
if (!PLAN_PATH) {
  throw new Error("plan-review-fanout requires the plan path. Invoke: /plan-review-fanout <path-to-plan.md> (or pass args:{path:\"...\"}).")
}

const FINDINGS = {
  type: "object",
  required: ["dimension", "verdict", "findings", "summary"],
  properties: {
    dimension: { type: "string" },
    verdict: { type: "string", enum: ["PASS", "FAIL", "MIXED"] },
    findings: {
      type: "array",
      items: {
        type: "object",
        required: ["id", "severity", "title", "plan_claim", "reality", "evidence", "recommendation"],
        properties: {
          id: { type: "string" },
          severity: { type: "string", enum: ["BLOCK", "HIGH", "MED", "LOW"] },
          title: { type: "string" },
          plan_claim: { type: "string", description: "what the plan asserts" },
          reality: { type: "string", description: "what the repo/files actually show" },
          evidence: { type: "string", description: "file:line or exact command+output that grounds this" },
          recommendation: { type: "string" },
        },
      },
    },
    summary: { type: "string" },
  },
}

const ELEGANCE = {
  type: "object",
  required: ["solving_right_problem", "drift_assessment", "alternatives", "recommendation"],
  properties: {
    solving_right_problem: { type: "string" },
    drift_assessment: { type: "string" },
    alternatives: {
      type: "array",
      items: {
        type: "object",
        required: ["name", "what", "why_better_or_worse", "tradeoffs", "replaces", "verdict"],
        properties: {
          name: { type: "string" },
          what: { type: "string" },
          why_better_or_worse: { type: "string" },
          tradeoffs: { type: "string" },
          replaces: { type: "string" },
          verdict: { type: "string", enum: ["ADOPT", "PARTIAL", "REJECT"] },
        },
      },
    },
    web_sources: { type: "array", items: { type: "string" } },
    recommendation: { type: "string" },
  },
}

const VERDICT = {
  type: "object",
  required: ["finding_id", "real", "confidence", "reasoning"],
  properties: {
    finding_id: { type: "string" },
    real: { type: "boolean", description: "true ONLY if the finding survives your refutation attempt" },
    confidence: { type: "string", enum: ["high", "medium", "low"] },
    reasoning: { type: "string" },
    correction: { type: "string", description: "if partly-right-but-overstated, the corrected version" },
  },
}

const REVIEW = {
  type: "object",
  required: ["verdict", "verdict_rationale", "findings_breakdown_md", "final_plan_md", "deferred_decisions"],
  properties: {
    verdict: { type: "string", enum: ["APPROVE", "APPROVE_WITH_CHANGES", "REJECT"] },
    verdict_rationale: { type: "string" },
    findings_breakdown_md: { type: "string" },
    final_plan_md: { type: "string", description: "the COMPLETE revised plan, verbatim, self-contained for a fresh session" },
    deferred_decisions: { type: "array", items: { type: "string" } },
  },
}

const PREAMBLE = "PLAN UNDER REVIEW: " + PLAN_PATH + "\n" +
"FIRST ACTION: Read that file in full. It was authored in a PRIOR session - treat the file as the authoritative plan content. Where the canonical reviewer prompt says 'the plan I just created in this session', substitute 'the plan in that file'.\n\n" +
"<investigate_before_answering> Never critique anything you have not opened. Never assume a file's contents - read it. If the plan references a pattern/convention/file, verify it exists before accepting the plan's claim about it. </investigate_before_answering>\n\n" +
"ESTABLISH LIVE TOPOLOGY YOURSELF (do NOT trust the plan's stated state): run git log origin/main --oneline -5 ; git rev-list --left-right --count HEAD...origin/main ; gh pr list --state open ; git worktree list ; git status --porcelain . The local checkout may be BEHIND origin - read MERGED state with git show origin/main:PATH and read merged PRs with gh pr view N.\n\n" +
"BINDING RULES for THIS review:\n" +
"- This is READ-ONLY. Do not edit/commit/push, do not run paid models.\n" +
"- Verify every factual claim against git/gh/files - NEVER trust prose or memory.\n" +
"- Run tests with the project's configured test command (check CLAUDE.md, CI config, or the test runner's own config).\n" +
"- Cite evidence as file:line or the exact command + a short output snippet. Vague findings will be discarded.\n"

// ---- Grounding lenses (default workflow agent: full tools incl. Bash/git) ----
const G1 = PREAMBLE + "\nYOUR LENS - CODEBASE GROUNDING #1: the plan's FACTUAL / ground-truth claims.\n" +
"For every concrete repo-state claim the plan makes - a commit SHA, a branch/PR number and its content, an open-PR or worktree count, a row/file count, a 'X is DONE / merged / unstarted' assertion, any 'current state' or 'ground truth' table - confirm or correct it against live git/gh and the filesystem. Read merged state with git show origin/main:PATH and gh pr view N when local is behind.\n" +
"Report each fact as accurate / stale / wrong, with the exact command + output that proves it."

const G2 = PREAMBLE + "\nYOUR LENS - CODEBASE GROUNDING #2: the plan's CODE claims (file existence, LOC, duplication, test coverage, constants).\n" +
"For every code claim the plan makes - a file exists at PATH, a file is ~N LOC, a function/symbol exists, code is duplicated across files, something is or is not unit-tested, a constant/threshold/config has value X - OPEN the file (locally or via git show origin/main:PATH) and verify. Search tests/ to confirm coverage claims by actually grepping for the symbol under test.\n" +
"Report REAL line counts and grep hits. Mark each claim accurate / overstated / wrong. Flag any file:line citation that does NOT resolve in the tree the plan will actually execute against (if the plan says to sync first, verify against origin/main, not the stale local checkout)."

const G3 = PREAMBLE + "\nYOUR LENS - CODEBASE GROUNDING #3: the plan's RATIONALE / reframe + reused-artifact + remaining-work claims.\n" +
"Verify the plan's narrative claims that are not bare facts: (1) any 'the prior theory was wrong, the real cause/approach is X' reframe - read the merged code/PR that supposedly proves it and confirm or correct; (2) any 'these artifacts already exist and are reusable' claim - open each and confirm it actually contains what the plan says; (3) any 'X is unstarted / still remains / is a stub' claim - check the filesystem.\n" +
"Report each as accurate / stale / wrong with evidence."

// ---- Checklist lenses (plan-reviewer agent: Read/Glob/Grep/WebSearch) ----
const R1 = PREAMBLE + "\nYOUR LENS - REPOSITORY RULES (canonical checklist item 2).\n" +
"Read .claude/rules/*.md and CLAUDE.md. Then check TWO things separately:\n" +
"(a) Does the plan CONFORM to these rules - workflow ordering (implement -> the project's validation gate -> commit -> independent review); ask-before-broad-sweeps; never-cite-from-memory; immutable data directories; atomic commits; plan-vs-execute; the validation gate's mechanics?\n" +
"(b) If the plan inlines a 'binding repo rules' section, are those restatements ACCURATE? Cross-check each restated rule against the actual rule file it claims to restate, including any commit gate, sandbox artifact, and commit/merge mechanics.\n" +
"For each violation or inaccurate restatement, cite the specific rule file:line and the corrective action."

const R2 = PREAMBLE + "\nYOUR LENS - OVER-ENGINEERING / SCOPE (canonical checklist item 3). Prefer the smallest change that completely satisfies the reviewed plan.\n" +
"For each task/phase ask: is this the simplest change that achieves the plan's stated goal, or is it gold-plating - unnecessary abstractions, premature generalization, new files that could be avoided, flexibility nobody asked for, broad sweeps where a targeted change suffices? If the plan bundles a genuinely-critical task together with deferrable nice-to-haves, say so and recommend narrowing to the critical core. If the plan re-litigates work a prior triage/decision doc in the repo already deferred, flag it (cite the doc).\n" +
"Flag every instance of scope that exceeds the plan's own stated objective."

const R3 = PREAMBLE + "\nYOUR LENS - MISSING DECISIONS (canonical checklist item 4).\n" +
"List design choices the plan makes SILENTLY that should be the user's call: cost/spend, irreversible or outward-facing actions, data deletion, scope cuts, ordering that commits the user to large work, settings/config changes, anything the repo flags as user-gated. If the plan already has a user-gate / open-decisions section, verify it is COMPLETE and check for NEW silent choices it omits.\n" +
"For each, state the implicit choice the plan made and recommend surfacing it to the user."

const R4 = PREAMBLE + "\nYOUR LENS - COMPLETENESS (canonical checklist item 5). Judge at the RIGHT altitude (a meta-plan need not pre-specify fixes it has not found yet, but it must make its targets and gates concrete).\n" +
"For each task/phase, check it has: (a) the exact files to create/modify (or concrete targets), (b) the concrete action, and (c) a verification command or checkable gate. Are work TARGETS concrete (file:line)? Are GATES checkable? Is the whole-effort done-criteria verifiable?\n" +
"Flag any task missing files, action, or verification; note where appropriate abstraction is fine."

const R5 = PREAMBLE + "\nYOUR LENS - ORDERING & DEPENDENCIES (canonical checklist item 6).\n" +
"Check sequencing: are prerequisites done before dependents (e.g., a sync/setup step before anything that reads the synced state)? Are the repo's known ordering hazards correctly encoded (any validation-gate-before-commit rule and what invalidates the gate; switching off the PR branch before gh pr merge --delete-branch; atomic commits against a fail-closed gate)? Are parallel lanes genuinely file-disjoint? Can each phase be verified independently before the next, or are there circular deps?\n" +
"Flag circular dependencies, steps that cannot be tested in isolation, and any ordering hazard the plan omits."

const E1 = PREAMBLE + "\n<elegance_gate> MANDATORY. Do not treat as a formality.\n" +
"Step back from the plan ENTIRELY and look at the underlying problem it is trying to solve. Ask: (1) Is the plan solving the RIGHT problem, or has it drifted into solving a side-effect / into 'do all these steps' as the goal? (2) Is there a fundamentally different, leaner approach - a built-in feature, an existing library or pattern, a much smaller change - that would make most of the plan unnecessary? (3) Would an experienced engineer say 'why not just do X instead'?\n" +
"SEARCH THE WEB for how others have solved this class of problem (established patterns, official docs, open-source projects). Cite sources.\n" +
"Produce concrete alternatives with verdicts (ADOPT / PARTIAL / REJECT). If the current approach is genuinely best, say so and explain why the alternatives you considered are worse. </elegance_gate>"

log("Fan-out: 3 grounding (git/Bash) + 5 checklist lenses + 1 elegance gate on " + PLAN_PATH)
// Single-source specs: each lens's label lives ONCE and drives both the agent
// call and the failed-lens report, so labels can never desync from the thunk
// order (the off-by-3 class of bug: 3 grounding thunks prefix the 5 review
// lenses + elegance, so a hardcoded 5-label array over all[0..4] would mislabel
// grounding failures and never check completeness/ordering/elegance).
// Do NOT set agentType on these. The merged plan-reviewer agent declares
// `tools: Read, Glob, Grep, Bash, WebSearch` - an explicit allowlist that
// excludes StructuredOutput, so a lens run under it cannot emit its schema.
// The default workflow agent has the full toolset and the prompts already
// carry each lens.
const findSpecs = [
  { label: "ground:facts",             prompt: G1, phase: "Ground",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "ground:code+LOC+dup",      prompt: G2, phase: "Ground",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "ground:reframe+artifacts", prompt: G3, phase: "Ground",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "review:repo-rules",        prompt: R1, phase: "Review",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "review:over-engineering",  prompt: R2, phase: "Review",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "review:missing-decisions", prompt: R3, phase: "Review",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "review:completeness",      prompt: R4, phase: "Review",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "review:ordering-deps",     prompt: R5, phase: "Review",   schema: FINDINGS, effort: "high", model: "claude-opus-4-8[1m]" },
  { label: "elegance:step-back+web",   prompt: E1, phase: "Elegance", schema: ELEGANCE, effort: "high", model: "claude-opus-4-8[1m]" },
]
const LENS_LABELS = findSpecs.map(s => s.label)
const all = await parallel(findSpecs.map(s => () => { const { prompt, ...opts } = s; return agent(prompt, opts) }))
const failedLenses = LENS_LABELS.filter((_, i) => !all[i])
if (failedLenses.length) log("FAILED LENSES (returned nothing): " + failedLenses.join(", "))
const elegance = all[all.length - 1] || { recommendation: "(elegance agent failed)", alternatives: [] }
const findingResults = all.slice(0, -1).filter(Boolean)

const allFindings = findingResults.flatMap(r =>
  (r.findings || []).map(f => ({ ...f, dimension: r.dimension }))
)
const dimVerdicts = findingResults.map(r => ({ dimension: r.dimension, verdict: r.verdict, summary: r.summary }))
log("Collected " + allFindings.length + " findings across " + findingResults.length + " lenses")

const blockers = allFindings.filter(f => f.severity === "BLOCK")
const toVerify = blockers.slice(0, 14)
if (blockers.length > toVerify.length) log("Capping adversarial verify at 14 of " + blockers.length + " BLOCK findings")

const verifyPrompt = (f) => PREAMBLE + "\nYOU ARE AN ADVERSARIAL VERIFIER. A plan-review finding is below. Try HARD to REFUTE it - show the plan is actually CORRECT and the finding is wrong or overstated. Open the real files / run git to check. Default to real=false (refuted) if the evidence is ambiguous.\n\n" +
  "FINDING:\n- id: " + f.id + "\n- severity: " + f.severity + "\n- dimension: " + f.dimension + "\n- title: " + f.title + "\n- plan_claim: " + f.plan_claim + "\n- reality (finder asserts): " + f.reality + "\n- evidence (finder): " + f.evidence + "\n- recommendation: " + f.recommendation + "\n\n" +
  "Return real=true ONLY if the finding SURVIVES your refutation (it genuinely identifies a real problem in the plan). If partly-right-but-overstated, set real per its core and give the corrected version in 'correction'. Ground your reasoning in repo evidence (file:line or command output)."

let verified = []
if (toVerify.length > 0) {
  log("Adversarially verifying " + toVerify.length + " BLOCK findings (2 skeptics each)")
  verified = await parallel(toVerify.map(f => () =>
    parallel([
      () => agent(verifyPrompt(f), { label: "verify-A:" + f.id, phase: "Verify", schema: VERDICT, effort: "high", model: "claude-opus-4-8[1m]" }),
      () => agent(verifyPrompt(f), { label: "verify-B:" + f.id, phase: "Verify", schema: VERDICT, effort: "high", model: "claude-opus-4-8[1m]" }),
    ]).then(vs => {
      const v = vs.filter(Boolean)
      const survived = v.some(x => x.real)
      return { finding: f, verdicts: v, survived }
    })
  ))
  verified = verified.filter(Boolean)
}

const convergePrompt = PREAMBLE +
  (failedLenses.length
    ? "\nFAILED LENSES - these dimensions returned NOTHING and are UN-REVIEWED, not clean: " + failedLenses.join(", ") + ". State this explicitly in the verdict; do not treat an un-run lens as a pass.\n"
    : "") +
  "\nYOU ARE THE CONVERGING PLAN-REVIEWER. Synthesize the multi-agent review below into ONE adversarial verdict and ONE handoff-ready REVISED plan. Judge whether the plan is SAFE and SUFFICIENT to hand to a fresh session that will execute it autonomously.\n\n" +
  "Re-Read the plan file in full first: " + PLAN_PATH + "\n\n" +
  "=== PER-LENS VERDICTS ===\n" + JSON.stringify(dimVerdicts, null, 1) + "\n\n" +
  "=== ALL FINDINGS (grounding + checklist lenses) ===\n" + JSON.stringify(allFindings, null, 1) + "\n\n" +
  "=== ADVERSARIAL VERIFICATION of BLOCK findings (survived=true means it withstood a refutation attempt) ===\n" + JSON.stringify(verified.map(v => ({ id: v.finding.id, title: v.finding.title, severity: v.finding.severity, survived: v.survived, verdicts: v.verdicts })), null, 1) + "\n\n" +
  "=== ELEGANCE GATE ===\n" + JSON.stringify(elegance, null, 1) + "\n\n" +
  "PRODUCE (REVIEW schema):\n" +
  "1. verdict: APPROVE / APPROVE_WITH_CHANGES / REJECT.\n" +
  "2. verdict_rationale: 2-4 sentences.\n" +
  "3. findings_breakdown_md: COMPLETE markdown (no summarization). Cover: what was investigated; what you CHANGED from the original plan and why; the elegance alternatives (adopted/partial/rejected + why); decisions deferred to the user. Group by severity. Treat BLOCK findings with survived=false as 'Considered & dismissed' (state why the refutation held). HIGH findings were not adversarially verified; carry each into the revised plan as a must-fix unless the grounding lenses contradict it. Be honest, transparent, critical.\n" +
  "4. final_plan_md: the COMPLETE revised plan, VERBATIM and self-contained for a fresh session with zero context. PRESERVE the plan's section structure/headings. CORRECT every stale/wrong fact the grounding surfaced (real SHAs, real counts, real LOC, etc.). Keep any user-gate / open-decisions section INTACT. Fold in the elegance recommendation (if it narrows scope or re-orders, do so explicitly). Ensure every task states files + action + verification. Repo-relative paths only; no 'the file we discussed'. Inline the binding repo rules. Add a 'verify live topology yourself' note (with the commands) so the executor re-verifies rather than trusting the file.\n" +
  "5. deferred_decisions: the list of choices for the user.\n"

log("Converging into verdict + revised handoff plan")
const review = await agent(convergePrompt, { label: "converge:final-review", phase: "Converge", schema: REVIEW, effort: "high", model: "claude-opus-4-8[1m]" })

return {
  plan_path: PLAN_PATH,
  verdict: review && review.verdict,
  counts: {
    findings_total: allFindings.length,
    block: blockers.length,
    verified: verified.length,
    survived: verified.filter(v => v.survived).length,
  },
  failed_lenses: failedLenses,
  review,
  elegance,
  dimVerdicts,
}
