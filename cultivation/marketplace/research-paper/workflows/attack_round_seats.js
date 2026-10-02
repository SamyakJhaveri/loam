export const meta = {
  name: 'attack-round-seats',
  description: 'Seats-only review round on the built paper text: 10 review seats write findings, and all but the devil\'s advocate write scores; the lead then runs the quote gate and the adjudicator by hand (10 agents)',
  phases: [
    { title: 'Seats', detail: '10 blind review seats on the built paper text' },
  ],
}

// Agents launched: 10 seats, nothing else. State this count before launch.
// After it the lead runs the quote gate and the adjudicator by hand (docs/review-round.md);
// the workflow returns those steps with this round's paths filled in.

// ===== Constant block: every input and every agent type name =====
// Paths are relative to the project root, which is the session's working directory.
// Inputs come from the Workflow args object; a key left out takes its default.
const A = args && typeof args === 'object' && !Array.isArray(args) ? args : {}
const PAPER = A.paper || 'paper/build/main.txt' // built paper text: pdftotext of the built PDF, no -layout
const ROUND = A.out || 'paper/review/round-1' // output folder of this round
const KEYS = [].concat(A.keys || []).join(' ') // optional: known-issue key file(s), JSON; for the lead's adjudicator step
const DECISIONS = [].concat(A.decisions || []).join(', ') // optional: decisions already made; for the lead's adjudicator step
const PRIOR = A.prior || '' // optional: the prior round's adjudicated.findings.json; for the lead's adjudicator step
const ROOT = 'the project root, your starting working directory (run pwd in your first Bash call and use the absolute path it prints)'
const CONTRACT = 'paper/tools/contract.md'
const VALIDATE = 'paper-tool validate_findings'

const TYPE = {
  reviewerMethods: 'research-paper:reviewer-methods',
  reviewerDomain: 'research-paper:reviewer-domain',
  reviewerGeneralist: 'research-paper:reviewer-generalist',
  devilsAdvocate: 'research-paper:reviewer-devils-advocate',
  leanCritic: 'research-paper:lean-critic-forensic',
  claimRef: 'research-paper:claim-ref-alignment',
  readerFirstIntro: 'research-paper:reader-first-intro',
  citationFinder: 'research-paper:citation-finder',
  adjudicator: 'research-paper:adjudicate-review', // not launched here; named in the returned steps
  // User-level agent type, not shipped by the plugin: the project must define it.
  escalate: 'escalate', // a critic on the strongest model; runs the critic and taste seats
}
// ===== End of constant block =====

if (args !== undefined && A !== args) log('args is not an object; every input takes its default')
log(`PAPER ${PAPER}; output ${ROUND}`)

const VALIDATE_NOTE = `Run the validator as ${VALIDATE} wherever your instructions say python3 <V> or python3 VALIDATOR.`

const NO_EM_DASH = 'Never use the em dash character in anything you write.'

const SCORES = (key) => `This round adds one output file to the two of contract section 6, an exception to any rule that limits you to those two. Write OUT/${key}.scores.md: score each review criterion and each aspect that ${CONTRACT} section 2 quotes from the call for papers, from 1 (fatal) to 5 (strong), in one table ordered weakest first; each row has the score, one quoted span of PAPER with its line number, and one sentence on what would raise it. End with two lines: "Strongest story:" (the strongest story the results support) and "First attack:" (the claim a reviewer would attack first). ${NO_EM_DASH}`

// The devil's advocate only challenges and never scores (its agent file), so it writes no scores file.
const UNSCORED = 'reviewer-devils-advocate'

const BASE = (key, extra) => `Run your review procedure on this draft.
PAPER = ${PAPER}
ROOT = ${ROOT}
OUT = ${ROUND}/seats/${key} under ROOT
${extra || ''}
Use an absolute path for OUT. Create OUT if it does not exist. ${VALIDATE_NOTE}
${key === UNSCORED ? NO_EM_DASH : SCORES(key)}
Return the output paths${key === UNSCORED ? ' and the recommendation line.' : ', the recommendation line and your three weakest scores.'}`

const CONFIG_PATHS = 'MAIN, BIB and SECTIONS = the paths that paper-tool paper_config prints for paper.main_tex, paper.bib and paper.sections_dir (one key per call).'
const SKIP_UNCITED = '\nSkip step 6 (uncited assertions): citation-finder covers them in this round. In review.md write "skipped (citation-finder covers them)" under Uncited assertions and in place of their count in the Summary.'
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
  { key: 'claim-ref-alignment', type: TYPE.claimRef, extra: CONFIG_PATHS + SKIP_UNCITED },
  { key: 'reader-first-intro', type: TYPE.readerFirstIntro },
  { key: 'citation-finder', type: TYPE.citationFinder, extra: CONFIG_PATHS + '\nNo ONLY: check every build file.' },
  { key: 'critic', type: TYPE.escalate, prompt: CRITIC },
  { key: 'taste', type: TYPE.escalate, prompt: TASTE },
]

phase('Seats')
const results = await pipeline(
  SEATS,
  (s) => agent(s.prompt || BASE(s.key, s.extra), { label: `seat ${s.key}`, phase: 'Seats', agentType: s.type }),
  (seatOut, s) => ({ seat: s.key, done: seatOut !== null && seatOut !== undefined, summary: String(seatOut || '').slice(0, 1200) }),
)

const missing = SEATS.map((s) => s.key).filter((k) => !results.some((r) => r && r.seat === k && r.done))
log(`seats finished: ${results.filter((r) => r && r.done).length}/${SEATS.length}; no output from: ${missing.join(', ') || 'none'}`)

const next = [
  `Quote gate, from the project root, for each seat: ${VALIDATE} ${ROUND}/seats/<seat>/<seat>.findings.json, then ${VALIDATE} --check-quotes --require-quotes ${ROUND}/seats/<seat>/<seat>.findings.json --root .; copy the .findings.json, .review.md and .scores.md (every seat but ${UNSCORED} writes one) of each seat that passes both into ${ROUND}/findings/.`,
  `Adjudicator (${TYPE.adjudicator}): FINDINGS_DIR = ${ROUND}/findings, PAPER = ${PAPER}, ROOT = the project root, OUT = ${ROUND}/adjudicated${DECISIONS ? `, DECISIONS = ${DECISIONS}` : ''}${KEYS ? `, KEYS = ${KEYS}` : ''}${PRIOR ? `, PRIOR = ${PRIOR}` : ''}.`,
]

return { seats: results, missing, next }
