export const meta = {
  name: 'attack-round-full',
  description: 'Full review round on the built paper text: 10 review seats in parallel, a quote gate per seat with one repair, the adjudicator, then a completeness critic (22 to 38 agents)',
  phases: [
    { title: 'Seats', detail: '10 blind review seats on the built paper text' },
    { title: 'Gate', detail: 'validate_findings --check-quotes --require-quotes per seat; on failure one repair by a fresh agent of the seat type, then one re-check' },
    { title: 'Adjudicate', detail: 'adjudicate-review over the seats that passed the gate, with DECISIONS, KEYS and PRIOR when given' },
    { title: 'Completeness', detail: 'blind critic: what is still uncovered once the confirmed findings are fixed' },
  ],
}

// Agents launched: 10 seats, 10 quote-gate checks, up to 8 repairs each followed by one
// re-check (0 to 16), 1 adjudicator and 1 completeness critic: 22 at least, 38 at most.
// State this count before launch; docs/review-round.md has the same table.

// ===== Constant block: every input and every agent type name =====
// Paths are relative to the project root, which is the session's working directory.
// Inputs come from the Workflow args object; a key left out takes its default.
const A = args && typeof args === 'object' && !Array.isArray(args) ? args : {}
const PAPER = A.paper || 'paper/build/main.txt' // built paper text: pdftotext of the built PDF, no -layout
const ROUND = A.out || 'paper/review/round-1' // output folder of this round
const KEYS = [].concat(A.keys || []).join(' ') // optional: known-issue key file(s), JSON
const DECISIONS = [].concat(A.decisions || []).join(', ') // optional: file(s) of decisions already made
const PRIOR = A.prior || '' // optional: the prior round's adjudicated.findings.json
const ROOT = 'the project root, your starting working directory (run pwd in your first Bash call and use the absolute path it prints)'
const CONTRACT = 'paper/tools/contract.md'
const VALIDATE = 'paper-tool validate_findings'
const MAX_REPAIRS = 8 // repairs across all seats; one per seat at most

const TYPE = {
  reviewerMethods: 'research-paper:reviewer-methods',
  reviewerDomain: 'research-paper:reviewer-domain',
  reviewerGeneralist: 'research-paper:reviewer-generalist',
  devilsAdvocate: 'research-paper:reviewer-devils-advocate',
  leanCritic: 'research-paper:lean-critic-forensic',
  claimRef: 'research-paper:claim-ref-alignment',
  readerFirstIntro: 'research-paper:reader-first-intro',
  citationFinder: 'research-paper:citation-finder',
  adjudicator: 'research-paper:adjudicate-review',
  // User-level agent types, not shipped by the plugin: the project must define both.
  worker: 'worker', // an execution agent; runs the quote gate at low effort
  escalate: 'escalate', // a critic on the strongest model; runs the critic, taste and completeness seats
}
// ===== End of constant block =====

if (args !== undefined && A !== args) log('args is not an object; every input takes its default')
log(`PAPER ${PAPER}; output ${ROUND}; KEYS ${KEYS || 'none'}; DECISIONS ${DECISIONS || 'none'}; PRIOR ${PRIOR || 'none'}`)

const VALIDATE_NOTE = `Run the validator as ${VALIDATE} wherever your instructions say python3 <V> or python3 VALIDATOR.`

const SCORES = (key) => `Besides your other outputs, write OUT/${key}.scores.md: score each review criterion and each aspect that ${CONTRACT} section 2 quotes from the call for papers, from 1 (fatal) to 5 (strong), in one table ordered weakest first; each row has the score, one quoted span of PAPER with its line number, and one sentence on what would raise it. End with two lines: "Strongest story:" (the strongest story the results support) and "First attack:" (the claim a reviewer would attack first). Never use the em dash character in anything you write.`

const BASE = (key, extra) => `Run your review procedure on this draft.
PAPER = ${PAPER}
ROOT = ${ROOT}
OUT = ${ROUND}/seats/${key} under ROOT
${extra || ''}
Use an absolute path for OUT. Create OUT if it does not exist. ${VALIDATE_NOTE}
${SCORES(key)}
Return the output paths, the recommendation line and your three weakest scores.`

const CONFIG_PATHS = 'MAIN, BIB and SECTIONS = the paths that paper-tool paper_config prints for paper.main_tex, paper.bib and paper.sections_dir (one key per call).'
const SCHEMA_FILE = 'finding_schema.json in the scripts folder that paper-tool prints when run with no argument'

const CRITIC = `You are a blind whole-paper critic for a submission to the venue that ${CONTRACT} section 2 names. Your seat name is "critic" and every finding has lens "critic".
Read, whole and in this order: ${CONTRACT} (the review rules every seat obeys; follow it, including its evidence rule, severity bands, output files and the two validator commands of its section 6), ${SCHEMA_FILE}, then PAPER. Read no other project file.
PAPER = ${PAPER}
ROOT = ${ROOT}
OUT = ${ROUND}/seats/critic under ROOT
Your lens: judge the paper as the venue's program committee will, on the review criteria and the aspects that ${CONTRACT} section 2 quotes from the call for papers. For each criterion and aspect, find where a reviewer looks for it and whether the paper answers it there. Report every defect at its true severity, each with a verbatim quote of 12 or more characters and its line.
Write OUT/critic.findings.json and OUT/critic.review.md as the contract says, run both validator commands of contract section 6 with ${VALIDATE} in place of python3 <V>, and fix any quote the validator rejects by copying the exact span from PAPER.
${SCORES('critic')}
Return the output paths, the recommendation line and your three weakest scores.`

const TASTE = `You are a blind critic of taste, narrative and machine-sounding prose for a submission to the venue that ${CONTRACT} section 2 names. Your seat name is "taste" and every finding has lens "critic".
Read, whole and in this order: ${CONTRACT} (the review rules every seat obeys; follow its evidence rule, severity bands, finding fields and the two validator commands of its section 6), ${SCHEMA_FILE}, then PAPER. Read no other project file.
PAPER = ${PAPER}
ROOT = ${ROOT}
OUT = ${ROUND}/seats/taste under ROOT
Measure PAPER on six moves that well-written papers in its field make, and report each place it falls short, with a verbatim quote of 12 or more characters and its line: (1) argument chain: every paragraph's first sentence, read in order, tells one story from the gap to the answer; (2) gap-to-answer mapping: each gap named in the introduction has one answer in the design and one result that tests it, named with the same words; (3) headings and captions as claims, not topics: for each topic heading, propose the claim heading in the finding's fix; (4) Fig. 1: does it show a result or a worked failure, or only the pipeline; (5) numbers carried in the sentence that makes the claim, with denominators; (6) machine-sounding prose: stock connectives, not-X-but-Y reflexes, signposting, triplets for rhythm, empty emphasis, hedges about the authors' effort, and parentheticals that break a sentence. In each finding's rule field, name the move it fails by its number and name (for example "(1) argument chain" or "(6) machine-sounding prose: signposting"). Suggested fixes keep every number, citation and cross-reference.
Write OUT/taste.findings.json and OUT/taste.review.md as the contract says, run both validator commands of contract section 6 with ${VALIDATE} in place of python3 <V>, and fix any quote the validator rejects by copying the exact span from PAPER.
${SCORES('taste')}
Return the output paths, the recommendation line and your three weakest scores.`

const SEATS = [
  { key: 'reviewer-methods', type: TYPE.reviewerMethods },
  { key: 'reviewer-domain', type: TYPE.reviewerDomain },
  { key: 'reviewer-generalist', type: TYPE.reviewerGeneralist },
  { key: 'reviewer-devils-advocate', type: TYPE.devilsAdvocate },
  { key: 'lean-critic-forensic', type: TYPE.leanCritic },
  { key: 'claim-ref-alignment', type: TYPE.claimRef, extra: CONFIG_PATHS },
  { key: 'reader-first-intro', type: TYPE.readerFirstIntro },
  { key: 'citation-finder', type: TYPE.citationFinder, extra: CONFIG_PATHS + '\nNo ONLY: check every build file.' },
  { key: 'critic', type: TYPE.escalate, prompt: CRITIC },
  { key: 'taste', type: TYPE.escalate, prompt: TASTE },
]

const GATE_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    file: { type: 'string' },
    findings: { type: 'integer' },
    rejected: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, message: { type: 'string' } }, required: ['id', 'message'] } },
    commands: { type: 'array', items: { type: 'object', properties: { command: { type: 'string' }, exit_code: { type: 'integer' } }, required: ['command', 'exit_code'] } },
    copied: { type: 'array', items: { type: 'string' } },
  },
  required: ['pass', 'file', 'rejected', 'commands', 'copied'],
}

const gatePrompt = (s) => `You are the independent quote gate for review seat "${s.key}". Do not edit any file in ${ROUND}/seats/${s.key}.
ROOT = ${ROOT}. Every path below is relative to ROOT; run every command from ROOT.
1. List ${ROUND}/seats/${s.key}. The findings file is the one file there whose name ends in .findings.json (if there is none, return pass=false with a rejected item id "missing").
2. Run each as its own Bash call and record the exit code:
   ${VALIDATE} <that file>
   ${VALIDATE} --check-quotes --require-quotes <that file> --root <ROOT>
3. Count the findings (a JSON array). For each finding the validator rejects, record its id and the validator's message.
4. If both commands exit 0: mkdir -p ${ROUND}/findings, then copy (cp) every file in ${ROUND}/seats/${s.key} whose name ends with .findings.json, .review.md or .scores.md into ${ROUND}/findings, keeping names; list what you copied. If either command exits non-zero, copy nothing.
Return the structured result.`

const repairPrompt = (s, g) => `You are seat "${s.key}" of this review round. Earlier you (or another instance of your seat) wrote ${g.file} for PAPER = ${PAPER}, ROOT = ${ROOT}. An independent quote gate ran the contract's validator (${VALIDATE}) and rejected these findings: ${JSON.stringify(g.rejected).slice(0, 6000)}.
Read ${CONTRACT} section 4 and section 6, then fix only these findings: open PAPER at or near the line given, copy the exact span of 12 or more characters that supports the finding, and correct its evidence and line. If PAPER has no text that supports a finding, remove that finding and add a line "Removed at the gate: <id>, <reason>" to the review.md in the same directory. Change no other finding. Then run both validator commands of contract section 6 on the file, with ${VALIDATE} in place of python3 <V>, and stop when both exit 0. Never use the em dash character.`

phase('Seats')
let repairsUsed = 0
const results = await pipeline(
  SEATS,
  (s) => agent(s.prompt || BASE(s.key, s.extra), { label: `seat ${s.key}`, phase: 'Seats', agentType: s.type }),
  async (seatOut, s) => {
    let g = await agent(gatePrompt(s), { label: `gate ${s.key}`, phase: 'Gate', agentType: TYPE.worker, effort: 'low', schema: GATE_SCHEMA })
    let repaired = false
    if (g && !g.pass && g.file && !(g.rejected || []).some((r) => r.id === 'missing')) {
      if (repairsUsed < MAX_REPAIRS) {
        repairsUsed++
        repaired = true
        log(`${s.key}: gate rejected ${(g.rejected || []).length} finding(s); one repair (repairs used ${repairsUsed}/${MAX_REPAIRS})`)
        await agent(repairPrompt(s, g), { label: `repair ${s.key}`, phase: 'Gate', agentType: s.type })
        g = await agent(gatePrompt(s), { label: `gate ${s.key} #2`, phase: 'Gate', agentType: TYPE.worker, effort: 'low', schema: GATE_SCHEMA })
      } else {
        log(`${s.key}: gate failed and all ${MAX_REPAIRS} repairs are used; no repair`)
      }
    }
    if (!g || !g.pass) log(`${s.key}: NOT in the findings folder (${repaired ? 'after its one repair' : 'not repaired'}); left for the lead`)
    return { seat: s.key, summary: String(seatOut || '').slice(0, 1500), gate: g, repaired }
  },
)

const passed = results.filter((r) => r && r.gate && r.gate.pass).map((r) => r.seat)
const failed = SEATS.map((s) => s.key).filter((k) => !passed.includes(k))
log(`gate passed: ${passed.length}/${SEATS.length}; not passed: ${failed.join(', ') || 'none'}`)

const priorBlock = PRIOR
  ? `PRIOR = ${PRIOR}, with adjudication.md in the same folder: the previous review round, on an earlier draft (its line numbers refer to that round's paper text, not PAPER). The draft was revised since. Add a section "Prior findings" to adjudication.md: for every PRIOR must-fix and should-fix finding, one row with its id, its claim in a few words, and status closed (quote PAPER showing it), still open (quote PAPER), or open by decision (name the DECISIONS entry). A new finding that repeats a still-open prior one keeps the prior id in its note.`
  : 'No PRIOR is named.'

phase('Adjudicate')
const adj = await agent(`Run your adjudication procedure.
FINDINGS_DIR = ${ROUND}/findings under ROOT
PAPER = ${PAPER}
ROOT = ${ROOT}
OUT = ${ROUND}/adjudicated under ROOT
${DECISIONS ? `DECISIONS = ${DECISIONS}` : 'No DECISIONS is named.'}
${KEYS ? `KEYS = ${KEYS}` : 'No KEYS is named.'}
${priorBlock}
Seats whose files passed the quote gate and are in FINDINGS_DIR: ${passed.join(', ') || 'none'}. Seats not in FINDINGS_DIR (failed the gate): ${failed.join(', ') || 'none'}.
The seats "critic" and "taste" are blind critics on the strongest model, with lens "critic"; "taste" judges narrative, taste and machine-sounding prose on six writing moves.
FINDINGS_DIR also holds a <seat>.scores.md per seat: each scores the review criteria and aspects of ${CONTRACT} section 2 from 1 to 5. Add a section "Scores" to adjudication.md: one table, one row per criterion and aspect, one column per seat plus the median, rows ordered weakest median first${PRIOR ? ", and one column with the median from PRIOR's adjudication.md for comparison" : ''}; then list each seat's "Strongest story" and "First attack" lines.
For each confirmed or downgraded finding, say whether its fix is text only (the writer can apply it) or needs new analysis or a decision by the authors.
${VALIDATE_NOTE}
Never use the em dash character. Return the two output paths and one line of counts per verdict and per tier${PRIOR ? ', plus the prior closed and still open counts' : ''}.`,
  { label: 'adjudicator', phase: 'Adjudicate', agentType: TYPE.adjudicator })

phase('Completeness')
const comp = await agent(`You are a blind completeness critic for a submission to the venue that ${CONTRACT} section 2 describes.
ROOT = ${ROOT}. Every path below is relative to ROOT.
Read only these, whole: section 2 of ${CONTRACT} (the venue, its format, and the review criteria and aspects quoted from its call for papers), ${PAPER} (pdftotext of the built PDF; multi-column text may be interleaved) and ${ROUND}/adjudicated/adjudicated.findings.json (the review findings that will be fixed, with verdicts and tiers). Read no other project file. Edit nothing except your output file.
Answer one question: after the confirmed findings are fixed, which criterion, aspect, reviewer question or promised item is still uncovered or weakly covered? For each: quote the paper with its line number, say why it stays uncovered, and say in one sentence what text would close it (new experiments only if text cannot). Also list each criterion and aspect with the paragraph that answers it (first words and line), weakest first.
Write Markdown to ${ROUND}/completeness/completeness.md. Never use the em dash character. Return the three weakest items and the counts.`,
  { label: 'completeness critic', phase: 'Completeness', agentType: TYPE.escalate })

return { passed, failed, repairsUsed, gates: results.map((r) => r && ({ seat: r.seat, pass: r.gate && r.gate.pass, findings: r.gate && r.gate.findings, rejected: r.gate && (r.gate.rejected || []).length, repaired: r.repaired })), adjudicator: String(adj || '').slice(0, 3000), completeness: String(comp || '').slice(0, 3000) }
