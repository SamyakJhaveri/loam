// codebase-review-fanout — generalized multi-lens CODE review (read-only).
// STATUS: un-exercised end-to-end as of 2026-06-22 (syntax-checked only). It reuses the
// proven plan-review-fanout verify/converge engine, re-pointed at code-review lenses.
// Treat the first real run as a shakedown; refine the lens prompts if a lens under/over-fires.
//
// Scope comes from args:
//   /codebase-review-fanout                         -> reviews current branch diff vs origin/main + uncommitted
//   /codebase-review-fanout {"targets":["a.py","b/"]}        -> reviews those files/dirs
//   /codebase-review-fanout {"diff":"origin/main...HEAD"}    -> reviews that git range
//   /codebase-review-fanout {"description":"...", "context":"triage bar / focus"}
// The workflow is READ-ONLY: it returns a triaged report; the calling session runs the fixes.

export const meta = {
  name: 'codebase-review-fanout',
  description: 'Multi-lens code review as a fan-out (correctness, security, performance, style, architecture, tech-debt, test-adequacy), adversarially verify BLOCK/HIGH findings, converge to a triaged report + atomic-PR slicing. READ-ONLY. Scope via args. Un-exercised end-to-end as of 2026-06-22.',
  whenToUse: 'Pre-merge / pre-pilot code review of a diff or a set of target files. Read-only finding pass that feeds a human-in-loop fix loop — never commits.',
  phases: [
    { title: 'Review', detail: '7 parallel lenses: correctness, security, performance, style, architecture, tech-debt, test-adequacy' },
    { title: 'Verify', detail: 'adversarial refutation of every BLOCK/HIGH finding (2 skeptics each)' },
    { title: 'Converge', detail: 'dedup + triage (fix-now / advisory / dismissed) + recommended atomic PRs' },
  ],
}

const SCOPE =
  (typeof args === "string" && args.trim()) ? { description: args.trim() }
  : (args && typeof args === "object") ? args
  : {}

let scopeText
if (Array.isArray(SCOPE.targets) && SCOPE.targets.length) {
  scopeText = "Review these specific files / areas:\n- " + SCOPE.targets.join("\n- ")
} else if (typeof SCOPE.diff === "string" && SCOPE.diff.trim()) {
  scopeText = "Review the changes in this git range: git diff " + SCOPE.diff.trim() + "  (review every changed file; read full files for context, not just the hunks)."
} else if (typeof SCOPE.description === "string" && SCOPE.description.trim()) {
  scopeText = SCOPE.description.trim()
} else {
  scopeText = "Review the current branch's changes: run `git diff origin/main...HEAD --stat` and `git status --porcelain`; review every changed/untracked file plus uncommitted edits, reading full files for context."
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
        required: ["id", "severity", "title", "file", "evidence", "why", "fix"],
        properties: {
          id: { type: "string" },
          severity: { type: "string", enum: ["BLOCK", "HIGH", "MED", "LOW"] },
          title: { type: "string" },
          file: { type: "string", description: "file:line" },
          evidence: { type: "string", description: "the offending snippet, quoted, that you actually read" },
          why: { type: "string", description: "why it is a problem" },
          fix: { type: "string", description: "the concrete change to make" },
        },
      },
    },
    summary: { type: "string" },
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

const REPORT = {
  type: "object",
  required: ["verdict", "verdict_rationale", "report_md", "fix_now_count", "advisory_count", "deferred_decisions"],
  properties: {
    verdict: { type: "string", enum: ["SHIP", "FIX_FIRST", "BLOCK"] },
    verdict_rationale: { type: "string" },
    report_md: { type: "string", description: "the COMPLETE triaged review report, markdown" },
    fix_now_count: { type: "integer" },
    advisory_count: { type: "integer" },
    deferred_decisions: { type: "array", items: { type: "string" } },
  },
}

const PREAMBLE = "CODE REVIEW SCOPE:\n" + scopeText + "\n\n" +
"FIRST: establish exactly what is in scope. Run the relevant commands (git diff --stat, git status --porcelain, grep) and Read every in-scope file IN FULL before reviewing. Never review code you have not opened.\n\n" +
"BINDING RULES:\n" +
"- READ-ONLY. Do NOT edit/commit/push. Your findings feed a human-in-loop fix loop.\n" +
"- Ground every finding in code you actually read: cite file:line and quote the offending snippet. Vague findings are discarded.\n" +
"- This repo: tests run with `pytest`. Verify topology/coverage with git/grep, never from memory.\n" +
"- SEVERITY BAR: BLOCK = correctness/security bug reachable on the real execution path; HIGH = likely bug or real risk; MED = maintainability/should-fix; LOW = nit. Default maintainability/style/architecture/tech-debt to MED or LOW unless you can show a concrete correctness/security impact.\n" +
"- If a prior triage/decision doc in the repo already dispositioned an item, note it and do not re-escalate without NEW evidence.\n" +
(typeof SCOPE.context === "string" && SCOPE.context.trim() ? "- CALLER CONTEXT / TRIAGE BAR: " + SCOPE.context.trim() + "\n" : "")

const L_CORRECT = PREAMBLE + "\nYOUR LENS — CORRECTNESS & BUGS (highest priority). Hunt for logic errors, off-by-one, wrong conditionals/operators, unhandled edge cases, error-swallowing / silent failures, incorrect error handling, resource leaks, concurrency/race issues, and CONTRACT MISMATCHES between a caller and callee (argument order, types, return shape, a constructed CLI/command string vs the tool it actually invokes). For changed code, check the diff did not regress a previously-correct path. Report each with file:line, the quoted snippet, why it is wrong, and the fix."

const L_SEC = PREAMBLE + "\nYOUR LENS — SECURITY. Look for: command/SQL/path injection, path traversal, unsafe subprocess (shell=True, unsanitized args), secrets/credentials in code or logs, unsafe deserialization (pickle / yaml.load / eval), SSRF, missing authorization, TOCTOU. For a research harness, scrutinize subprocess construction and any untrusted file path that reaches the filesystem. Report each with file:line, the exploit path, and the mitigation. If you find none in scope, say so explicitly."

const L_PERF = PREAMBLE + "\nYOUR LENS — PERFORMANCE. Look for: accidental O(n^2) or worse, work inside loops that could be hoisted, N+1 file/IO/subprocess calls, repeated re-parsing of the same data, unbounded memory growth, missing streaming for large files. Only flag perf issues that matter at the code's REAL input scale. Report each with file:line, the cost, and the cheaper approach."

const L_STYLE = PREAMBLE + "\nYOUR LENS — STYLE / MAINTAINABILITY / CONVENTIONS. Read .claude/rules/*.md (esp. python.md) and CLAUDE.md first. Flag deviations from repo conventions (naming, structure, layering), unclear names, dead or misleading comments and comment-rot (comments that no longer match the code), unhelpful error messages, and readability problems. Keep these MED/LOW unless they hide a bug. Report file:line + the change."

const L_ARCH = PREAMBLE + "\nYOUR LENS — ARCHITECTURE (read-only finding pass). Look for: duplicated logic across files (the SAME helper re-implemented), oversized modules/functions doing several jobs, tight coupling, leaky abstractions, helpers that should be hoisted into a shared package, and code that is hard to unit-test because of its shape. For each duplication, name ALL files that carry the copy and whether they can silently drift. Recommend the MINIMAL consolidation — and explicitly warn if extracting a shared helper would itself be over-engineering. MED/advisory by default."

const L_DEBT = PREAMBLE + "\nYOUR LENS — TECH DEBT (read-only finding pass). Look for: dead code (unused functions/vars/imports/branches), magic numbers/strings that should be named constants (especially ones re-declared across multiple files), duplicated literals, stale TODO/FIXME, and config/constant drift. Report file:line + the cleanup. MED/LOW by default."

const L_TEST = PREAMBLE + "\nYOUR LENS — TEST ADEQUACY. For every new or changed behavior in scope, check whether a test actually exercises it: grep tests/ for the symbol, READ the test, and judge whether its assertion PINS the behavior or merely smoke-tests it. Flag: untested new code paths, mocked seams where the real contract is never asserted (e.g. a subprocess executor whose command string is never checked against the real CLI it must match), missing edge-case / failure-mode tests, and tests that would still pass if the code were wrong. Report the file:line of the gap and the specific test that should exist."

log("Code-review fan-out (7 lenses) on scope: " + scopeText.slice(0, 120))
// Single-source specs: each lens's label lives ONCE and drives both the agent
// call and the failed-lens report (a dropped lens is UN-REVIEWED, not clean —
// computed from `raw` BEFORE .filter(Boolean) strips the index→label mapping).
const findSpecs = [
  { label: "review:correctness",   prompt: L_CORRECT, phase: "Review", schema: FINDINGS, effort: "high" },
  { label: "review:security",      prompt: L_SEC,     phase: "Review", schema: FINDINGS, effort: "high" },
  { label: "review:performance",   prompt: L_PERF,    phase: "Review", schema: FINDINGS, effort: "high" },
  { label: "review:style",         prompt: L_STYLE,   phase: "Review", schema: FINDINGS, effort: "high" },
  { label: "review:architecture",  prompt: L_ARCH,    phase: "Review", schema: FINDINGS, effort: "high" },
  { label: "review:techdebt",      prompt: L_DEBT,    phase: "Review", schema: FINDINGS, effort: "high" },
  { label: "review:test-adequacy", prompt: L_TEST,    phase: "Review", schema: FINDINGS, effort: "high" },
]
const LENS_LABELS = findSpecs.map(s => s.label)
const raw = await parallel(findSpecs.map(s => () => { const { prompt, ...opts } = s; return agent(prompt, opts) }))
const failedLenses = LENS_LABELS.filter((_, i) => !raw[i])
if (failedLenses.length) log("FAILED LENSES (returned nothing): " + failedLenses.join(", "))
const all = raw.filter(Boolean)

const allFindings = all.flatMap(r => (r.findings || []).map(f => ({ ...f, dimension: r.dimension })))
const dimVerdicts = all.map(r => ({ dimension: r.dimension, verdict: r.verdict, summary: r.summary }))
log("Collected " + allFindings.length + " findings across " + all.length + " lenses")

const mustFix = allFindings.filter(f => f.severity === "BLOCK" || f.severity === "HIGH")
const toVerify = mustFix.slice(0, 16)
if (mustFix.length > toVerify.length) log("Capping adversarial verify at 16 of " + mustFix.length + " BLOCK/HIGH findings")

const verifyPrompt = (f) => PREAMBLE + "\nYOU ARE AN ADVERSARIAL VERIFIER. A code-review finding is below. Try HARD to REFUTE it — show the code is actually correct, the concern does not apply on the real path, or it is already handled/tested elsewhere. Open the real files and run git/grep. Default to real=false (refuted) if the evidence is ambiguous.\n\n" +
  "FINDING:\n- id: " + f.id + "\n- severity: " + f.severity + "\n- dimension: " + f.dimension + "\n- title: " + f.title + "\n- file: " + f.file + "\n- evidence: " + f.evidence + "\n- why (reviewer asserts): " + f.why + "\n- fix: " + f.fix + "\n\n" +
  "Return real=true ONLY if the finding SURVIVES your refutation (it genuinely identifies a real problem). If partly-right-but-overstated, set real per its core and give the corrected version in 'correction'. Ground your reasoning in code you read (file:line or command output)."

let verified = []
if (toVerify.length > 0) {
  log("Adversarially verifying " + toVerify.length + " BLOCK/HIGH findings (2 skeptics each)")
  verified = (await parallel(toVerify.map(f => () =>
    parallel([
      () => agent(verifyPrompt(f), { label: "verify-A:" + f.id, phase: "Verify", schema: VERDICT, effort: "high" }),
      () => agent(verifyPrompt(f), { label: "verify-B:" + f.id, phase: "Verify", schema: VERDICT, effort: "high" }),
    ]).then(vs => {
      const v = vs.filter(Boolean)
      return { finding: f, verdicts: v, survived: v.some(x => x.real) }
    })
  ))).filter(Boolean)
}

const convergePrompt = PREAMBLE +
  (failedLenses.length
    ? "\nFAILED LENSES — these dimensions returned NOTHING and are UN-REVIEWED, not clean: " + failedLenses.join(", ") + ". State this explicitly in the verdict; do not treat an un-run lens as a pass.\n"
    : "") +
  "\nYOU ARE THE CONVERGING CODE REVIEWER. Synthesize the multi-lens review below into ONE triaged, actionable report. READ-ONLY: recommend fixes, do not apply them.\n\n" +
  "=== PER-LENS VERDICTS ===\n" + JSON.stringify(dimVerdicts, null, 1) + "\n\n" +
  "=== ALL FINDINGS ===\n" + JSON.stringify(allFindings, null, 1) + "\n\n" +
  "=== ADVERSARIAL VERIFICATION of BLOCK/HIGH findings (survived=true means it withstood a refutation attempt) ===\n" + JSON.stringify(verified.map(v => ({ id: v.finding.id, title: v.finding.title, severity: v.finding.severity, file: v.finding.file, survived: v.survived, verdicts: v.verdicts })), null, 1) + "\n\n" +
  "PRODUCE (REPORT schema):\n" +
  "1. verdict: SHIP (no fix-now) / FIX_FIRST (fix-now items exist) / BLOCK (a correctness/security BLOCK on the real path).\n" +
  "2. verdict_rationale: 2-4 sentences.\n" +
  "3. report_md: COMPLETE markdown (no summarization), with these sections:\n" +
  "   - FIX-NOW (survived verification AND correctness/security on the real path) — grouped by severity, each with file:line, the quoted problem, and the concrete fix.\n" +
  "   - ADVISORY (maintainability / architecture / tech-debt / style — defer to a post-merge or v2/v3 pass) — concise list.\n" +
  "   - CONSIDERED & DISMISSED (BLOCK/HIGH findings with survived=false) — each with why the refutation held.\n" +
  "   - RECOMMENDED ATOMIC PRs — one per cohesive concern (the repo's pre-commit gate discourages bundled compound commits). For each: name, the concern, the finding ids it closes, the files it touches, and the test that should accompany it (TDD).\n" +
  "   - DEFERRED DECISIONS — choices that are the user's call.\n" +
  "   Dedup findings that multiple lenses raised. Be honest, transparent, critical.\n" +
  "4. fix_now_count, advisory_count: integer counts.\n" +
  "5. deferred_decisions: the list for the user.\n"

log("Converging into a triaged code-review report")
const report = await agent(convergePrompt, { label: "converge:code-review", phase: "Converge", schema: REPORT, effort: "high" })

return {
  scope: scopeText,
  verdict: report && report.verdict,
  counts: {
    findings_total: allFindings.length,
    block_high: mustFix.length,
    verified: verified.length,
    survived: verified.filter(v => v.survived).length,
    fix_now: report && report.fix_now_count,
    advisory: report && report.advisory_count,
  },
  failed_lenses: failedLenses,
  report,
  dimVerdicts,
}
