export const meta = {
  name: 'exemplar-advisor',
  description: 'Exemplar-driven writing suggestions for every section of a paper: readers of published exemplar papers, section advisors, fact checkers, one coordinator. Suggestions only; no paper file is edited.',
  phases: [
    { title: 'Read', detail: 'readers, each reads its share of the exemplar papers and our paper in full' },
    { title: 'Understand', detail: 'advisors, each over its share of our sections' },
    { title: 'Check', detail: 'checkers verify the facts each advisor lists' },
    { title: 'Coordinate', detail: '1 coordinator over the whole paper' },
  ],
}

// ---- Constants and inputs (args, a JSON object)
// Agent count: readers + advisors + checkers + 1 coordinator, by default 4 + 2 + 2 + 1 = 9, plus at most one
// retry per reader. Raise readers, advisors or checkers above the defaults only with the owner's go.
//   papers        required: [{ id, title }], exemplar ids from the manifest (codex.manifest) with their titles;
//                 dealt to the readers in the order given, so order them to even out the reading length
//   sections      required: [{ key, name, lines }], our sections in paper order, abstract first: key is the
//                 file stem under sections_dir, name the heading as printed in the built text, lines
//                 (optional) its rough line range there
//   readers 4, advisors 2, checkers 2: the agent counts
//   root          default '.': the project root, the lead's working directory
//   corpus        default 'paper/exemplars' (codex.corpus_dir in paper-tools.toml), one <id>.txt per paper
//   ours          default 'paper/build/main.txt' (build.text): pdftotext of our built PDF
//   sections_dir  default 'paper/sections' (paper.sections_dir)
//   contract      default 'paper/tools/contract.md': venue and length rules (section 2), house rules (section 3)
//   rules         default []: files the advisors and the coordinator read first, such as the owner's writing
//                 rulings and the moves the project already adopted from exemplars
//   earlier       default []: earlier whole-paper reads saved from `codex_seat whole`, each with a jsonl block
//   codetruth     default '': a code-truth report of the paper saved from `codex_seat codetruth`
//   sources       default: the sources of truth the project's AGENTS.md or CLAUDE.md names; where a checker
//                 looks for the paper's numbers and rules
const A = args || {}
const ROOT = A.root || '.'
const at = p => (p.startsWith('/') ? p : `${ROOT}/${p}`)
const PAPERS = A.papers || []
const SECTIONS = A.sections || []
const READERS = A.readers || 4
const ADVISORS = A.advisors || 2
const CHECKERS = A.checkers || 2
const CORPUS = at(A.corpus || 'paper/exemplars')
const OURS = at(A.ours || 'paper/build/main.txt')
const SECTIONS_DIR = at(A.sections_dir || 'paper/sections')
const CONTRACT = at(A.contract || 'paper/tools/contract.md')
const RULES = (A.rules || []).map(at)
const EARLIER = (A.earlier || []).map(at)
const CODETRUTH = A.codetruth ? at(A.codetruth) : ''
const SOURCES = A.sources || "the sources of truth that the project's AGENTS.md or CLAUDE.md names"
// Agent types. `scout` and `escalate` are user-level types, not part of this plugin: the project or the user
// must define them (scout: a read-only search and extraction agent; escalate: the strongest model, for judgment).
const READER_TYPE = 'scout'
const ADVISOR_TYPE = 'escalate'
const CHECKER_TYPE = 'scout'
const COORDINATOR_TYPE = 'escalate'

if (!PAPERS.length || !SECTIONS.length) {
  throw new Error('exemplar-advisor: args.papers and args.sections are required (see the comment at the top)')
}

// n groups, dealt in turn; never an empty group
const deal = (items, n) => Array.from({ length: Math.min(n, items.length) }, (_, i) => items.filter((_, j) => j % n === i))
const GROUPS = deal(PAPERS, READERS)
const ADVISOR_GROUPS = deal(SECTIONS, ADVISORS)
const KEYS = SECTIONS.map(s => s.key)
const DIMS = ['structure', 'flow', 'readability', 'language', 'interpretation', 'presentation', 'engineering']
const KINDS = ['rewrite', 'move', 'cut', 'split', 'merge', 'add-structure', 'display', 'caption']
const SECTION_LIST = SECTIONS.map(s => `${s.key} (${s.name})`).join(', ')

const HOUSE = `Rules for every proposal:
- Follow the house rules in the project's review contract, ${CONTRACT} (section 3)${RULES.length ? `, and the owner's rules in ${RULES.join(', ')}` : ''}.
- Never add a fact, number, mechanism or result our text does not state, and never change a number. If our text is unclear about a fact, suggest that the authors state it; do not guess it.
- Length: the venue's length rules (contract section 2) bind. A proposal should be no longer than the text it replaces. If a proposal is longer, say by how many words.
- A move suits our paper only if it fits the venue's page limit.`

const READ_SCHEMA = {
  type: 'object',
  required: ['read', 'moves', 'suggestions', 'risks'],
  properties: {
    read: { type: 'array', items: { type: 'object', required: ['file', 'total_lines', 'ranges_read'], properties: {
      file: { type: 'string' }, total_lines: { type: 'integer' }, ranges_read: { type: 'string' } } } },
    moves: { type: 'array', items: { type: 'object', required: ['paper', 'our_section', 'dimension', 'what', 'quote', 'where', 'verdict'], properties: {
      paper: { type: 'string' }, our_section: { type: 'string', enum: KEYS }, dimension: { type: 'string', enum: DIMS },
      what: { type: 'string' }, quote: { type: 'string' }, where: { type: 'string' },
      verdict: { type: 'string', enum: ['copy', 'avoid', 'does-not-fit-page-limit'] } } } },
    suggestions: { type: 'array', items: { type: 'object',
      required: ['section', 'dimension', 'kind', 'ours', 'proposal', 'exemplar_paper', 'exemplar_quote', 'exemplar_where', 'why', 'facts_kept', 'length_effect', 'priority'],
      properties: {
        section: { type: 'string', enum: KEYS }, dimension: { type: 'string', enum: DIMS }, kind: { type: 'string', enum: KINDS },
        ours: { type: 'string' }, proposal: { type: 'string' }, exemplar_paper: { type: 'string' }, exemplar_quote: { type: 'string' },
        exemplar_where: { type: 'string' }, why: { type: 'string' }, facts_kept: { type: 'boolean' },
        length_effect: { type: 'string', enum: ['shorter', 'same', 'longer'] }, priority: { type: 'integer', enum: [1, 2, 3] } } } },
    risks: { type: 'string' },
  },
}

function readerPrompt(group) {
  const one = group.length === 1
  const files = group.map(p => `- ${CORPUS}/${p.id}.txt : ${p.title} (paper id "${p.id}")`).join('\n')
  return `You are an experienced program committee member for the venue and field that the project's review contract describes; read ${CONTRACT} (sections 2, 3 and 8) first.
Your job: read ${one ? 'one published paper' : `${group.length} published papers`} in full, learn how ${one ? 'it presents its' : 'they present their'} work, compare our paper against ${one ? 'it' : 'them'}, and suggest concrete writing fixes for every section of our paper.
You suggest; you never edit any file. The authors decide which suggestions to take.

Files (pdftotext output; ignore line-break, hyphenation and column artifacts; a sentence near a figure or table can be split across lines):
${files}
- ${OURS} : our paper, a submission to that venue.

Read every file completely before you judge anything: get each line count (wc -l), then read each file with the Read tool in consecutive chunks until every line is covered. Read no other file besides the contract${RULES.length ? ' and the rule files named below' : ''}, and do not search the web. In "read", report the line count and the ranges you actually read; they must cover every line.

Our paper has ${SECTIONS.length} sections, with these keys: ${SECTION_LIST}.

Seven dimensions:
1. structure: section order, what each section is for, where the reader learns the problem, the design, the results and the limits.
2. flow: how each paragraph opens, how paragraphs and sections hand off, where a term or number is used before it is explained.
3. readability: sentence length and load, one idea per sentence, concrete before abstract, examples.
4. language: claim strength matched to evidence, hedges, how the paper names its own limits, register.
5. interpretation: what each result is said to mean, baselines and denominators, uncertainty, rival explanations, what the paper says not to conclude.
6. presentation: tables and figures, what each caption claims, how prose points to a display, how numbers are rounded and grouped.
7. engineering: how the system is described so a reader could rebuild it (inputs, steps, decision rules, thresholds and why).

Questions to answer while reading each published paper:
- Method: subsection titles and the reader question each answers; how mechanisms are introduced (purpose first or rule first); how thresholds are justified; where caveats sit and their share.
- Results and discussion: how the first results paragraph opens; how the headline number is anchored (baseline, denominator, unit, interval); captions as claim or label and how prose points to a table; where robustness and limitations sit; how the discussion opens and closes.
- Abstract, introduction and related work: the first three sentences; where the gap and the contribution are stated; how contributions are listed and tied to sections; how prior work is grouped and what each group is said to lack; how numbers are used in the abstract.

What to return:
- "moves": the published papers' moves, each tied to the one section of OURS it would apply to. For each published paper, cover each of our ${SECTIONS.length} sections that the paper has a counterpart for, and cover each of the seven dimensions at least once. Each move has a verbatim "quote" from the published paper and "where" (its section). "verdict" says whether to copy it, avoid it, or that it does not fit the venue's page limit.
- "suggestions": between 14 and 28 concrete suggestions for our paper in total, with at least one for each of our ${SECTIONS.length} sections unless the papers truly offer nothing for it (say so in "risks"). Keys:
  - section: the key of our section.
  - dimension, kind (rewrite = replace a sentence; move = relocate text; cut = remove repetition; split; merge; add-structure = a list or a signpost; display = a table or figure change; caption).
  - ours: the exact sentence or phrase from our paper that the suggestion acts on, verbatim, complete, so the authors can find it. Rejoin a sentence that pdftotext split across lines.
  - proposal: the replacement text for a rewrite, or a precise instruction for the other kinds.
  - exemplar_paper: the paper id; exemplar_quote: the verbatim span from that paper that shows the move; exemplar_where: its section.
  - why: one sentence on what a first-time reader gains.
  - facts_kept: true only if the proposal keeps every number, citation, caveat and claim of "ours" and adds no fact; otherwise false, and say in "why" which fact changes.
  - length_effect: shorter, same or longer than the text it replaces.
  - priority: 1 (a reviewer would notice), 2 (clear gain), 3 (polish).
- "risks": one or two lines naming what you could not judge.

${HOUSE}
- Prefer one strong suggestion per problem over several variants. Be specific and harsh; do not praise. Quotes must be verbatim: a made-up or paraphrased quote makes the suggestion useless.`
}

function advisorSchema(keys) {
  const section = { type: 'object', required: ['section', 'diagnosis', 'suggestions', 'checks', 'dropped', 'conflicts'],
    properties: {
      section: { type: 'string', enum: keys },
      diagnosis: { type: 'string' },
      suggestions: { type: 'array', items: { type: 'object',
        required: ['id', 'rank', 'priority', 'dimension', 'kind', 'ours', 'proposal', 'why', 'exemplars', 'readers_agreeing', 'facts_kept', 'length_effect', 'words_delta', 'skim_pass', 'check_ids'],
        properties: {
          id: { type: 'string' }, rank: { type: 'integer' }, priority: { type: 'integer', enum: [1, 2, 3] },
          dimension: { type: 'string', enum: DIMS }, kind: { type: 'string', enum: KINDS },
          ours: { type: 'string' }, proposal: { type: 'string' }, why: { type: 'string' },
          exemplars: { type: 'array', items: { type: 'object', required: ['paper', 'quote', 'where'], properties: {
            paper: { type: 'string' }, quote: { type: 'string' }, where: { type: 'string' } } } },
          readers_agreeing: { type: 'integer' }, facts_kept: { type: 'boolean' },
          length_effect: { type: 'string', enum: ['shorter', 'same', 'longer'] }, words_delta: { type: 'integer' },
          skim_pass: { type: 'string' }, check_ids: { type: 'array', items: { type: 'string' } } } } },
      checks: { type: 'array', items: { type: 'object', required: ['id', 'claim', 'sentence', 'where_to_look'], properties: {
        id: { type: 'string' }, claim: { type: 'string' }, sentence: { type: 'string' }, where_to_look: { type: 'string' } } } },
      dropped: { type: 'array', items: { type: 'object', required: ['ours', 'reason'], properties: {
        ours: { type: 'string' }, reason: { type: 'string' } } } },
      conflicts: { type: 'array', items: { type: 'object', required: ['issue', 'resolution'], properties: {
        issue: { type: 'string' }, resolution: { type: 'string' } } } },
    } }
  return { type: 'object', required: ['sections'], properties: { sections: { type: 'array', items: section } } }
}

function advisorPrompt(secs, material) {
  const one = secs.length === 1
  const list = secs.map(s => `"${s.name}" (key "${s.key}"${s.lines ? `, about lines ${s.lines} of the built text` : ''})`).join('; ')
  return `You are the advisor for ${one ? 'one section' : `${secs.length} sections`} of our paper: ${list}.
${GROUPS.length} readers each read some of ${PAPERS.length} published exemplar papers in full plus our paper, and returned the exemplar papers' moves and concrete suggestions. Your job is to understand that material for your ${one ? 'section' : 'sections'} and return, for each, one ranked list of suggestions the owner can choose from. You suggest only: edit no file.

Read first, in full:
- our section ${one ? 'source' : 'sources'}: ${secs.map(s => `${SECTIONS_DIR}/${s.key}.tex`).join(', ')}
- our whole paper as a reader sees it: ${OURS} (pdftotext interleaves columns near floats)
- the project's review contract ${CONTRACT}: the venue and its length rules (section 2), the house rules (section 3)
${RULES.length ? `- the owner's rules that bind every suggestion: ${RULES.join(', ')}\n` : ''}${EARLIER.length ? `- second opinions: earlier whole-paper reads, ${EARLIER.join(', ')} (each has a fenced jsonl block of suggestions; take the ones for your sections)\n` : ''}${CODETRUTH ? `- a code-truth audit of the paper's engineering sentences: ${CODETRUTH} (take the findings for your sections; a proposal must never restate a sentence that audit found wrong, and a suggestion that fixes one of its findings is welcome, with its code location)\n` : ''}
Then, for each of your sections, return one entry of "sections":
1. Find each reader suggestion's "ours" text in the section. Drop a suggestion whose "ours" you cannot find in our section, whose proposal adds or changes a fact, or that breaks a house rule or an owner rule; list it under "dropped" with the reason.
2. Merge suggestions that act on the same sentence or make the same move; count the readers who agree ("readers_agreeing"). Settle conflicts between readers and record each under "conflicts".
3. Write the final proposal text yourself, in the paper's register (plain, specific, no primer-style sentences). ${HOUSE}
4. Apply the skim-reader rule: a reader makes five passes (title and abstract; the last introduction paragraph with figures and captions; the first introduction paragraph with the first and last discussion paragraphs; the first sentence of every paragraph; deep reading only by choice). Check that this section serves the passes that touch it, add suggestions where it does not, and name in "skim_pass" which pass each suggestion helps ("none" if only deep reading).
5. Rank: rank 1 is the suggestion a reviewer would most notice. Return at most 25 suggestions per section; put the rest under "dropped" with reason "below the cut". Ids are "<key>-01", "<key>-02", in rank order (for example "${secs[0].key}-01").
6. "words_delta" is the proposal's word count minus the replaced text's (0 for kinds with no text change).
7. "checks": every fact that a proposal states or relies on and that must be verified against code or results before the owner uses it (a number, a rule, a threshold, what the code does). One entry per fact: id "<key>-c01", the claim, the sentence it sits in, and where to look (${SOURCES}). Put the ids in the suggestion's "check_ids". A pure rewording that keeps every fact needs no check.
8. "diagnosis": at most 150 words on how this section reads against the exemplars across the seven dimensions (structure, flow, readability, language, interpretation, presentation, engineering).

Every "ours" must be verbatim from our section and every exemplar quote verbatim from a reader's material; when in doubt about an exemplar quote, check it in ${CORPUS}/<paper id>.txt.

Reader material for your sections, by section key (JSON):
${JSON.stringify(material)}`
}

const CHECK_SCHEMA = {
  type: 'object', required: ['results'],
  properties: { results: { type: 'array', items: { type: 'object', required: ['id', 'verdict', 'evidence', 'corrected_text'], properties: {
    id: { type: 'string' }, verdict: { type: 'string', enum: ['supported', 'partly', 'contradicted', 'not-found'] },
    evidence: { type: 'string' }, corrected_text: { type: 'string' } } } } },
}

function checkerPrompt(checks) {
  return `Verify facts for our paper. You are read-only; edit nothing; do not search the web.
The project root is ${ROOT}. The paper's numbers and rules come from ${SOURCES}; never judge a claim from a file those sources mark as superseded.
The paper text is ${OURS}; each check names its section, whose source is ${SECTIONS_DIR}/<section>.tex.

For each check below, find the code or results file that decides it and read enough of the code body or data to know. Return one result per check id:
- verdict: supported (the code or results file says exactly this), partly (true in spirit, a detail differs), contradicted, or not-found (say where you looked).
- evidence: path:line and a verbatim snippet of at most three lines. No verdict from a file name, a docstring or a comment alone when the code body is available.
- corrected_text: empty when supported; otherwise one sentence stating what the code or data shows.

Checks (JSON):
${JSON.stringify(checks)}`
}

const COORD_SCHEMA = {
  type: 'object',
  required: ['sections', 'cross_section', 'skim_passes', 'page_budget', 'top'],
  properties: {
    sections: { type: 'array', items: { type: 'object', required: ['section', 'final'], properties: {
      section: { type: 'string', enum: KEYS },
      final: { type: 'array', items: { type: 'object', required: ['id', 'rank', 'action', 'proposal', 'reason'], properties: {
        id: { type: 'string' }, rank: { type: 'integer' }, action: { type: 'string', enum: ['keep', 'revise', 'drop'] },
        proposal: { type: 'string' }, reason: { type: 'string' } } } } } } },
    cross_section: { type: 'array', items: { type: 'object', required: ['issue', 'sections', 'recommendation'], properties: {
      issue: { type: 'string' }, sections: { type: 'string' }, recommendation: { type: 'string' } } } },
    skim_passes: { type: 'array', items: { type: 'object', required: ['pass', 'verdict', 'fix_ids'], properties: {
      pass: { type: 'string' }, verdict: { type: 'string' }, fix_ids: { type: 'string' } } } },
    page_budget: { type: 'string' },
    top: { type: 'array', items: { type: 'string' } },
  },
}

function coordPrompt(advised) {
  return `You are the coordinator for exemplar-driven writing suggestions on our paper. Section advisors each returned a ranked list of suggestions for their sections, and checkers verified the facts those suggestions rely on. Your job is the whole paper: produce the final ranked list per section that the owner chooses from. You suggest only: edit no file.

Read first, in full: our paper ${OURS}; the section sources in ${SECTIONS_DIR}; the project's review contract ${CONTRACT}${RULES.length ? `; the owner's rules ${RULES.join(', ')}` : ''}${CODETRUTH ? `; and the code-truth audit ${CODETRUTH}` : ''}.

Then:
1. For every advisor suggestion, decide keep, revise or drop, and give the reason in one sentence. Drop or revise a suggestion whose check came back contradicted or partly (use the checker's corrected text), that conflicts with a suggestion in another section, that repeats one in another section, or that breaks a house rule or an owner rule. For revise, give the full final proposal text; for keep, repeat the advisor's proposal unchanged; for drop, leave proposal empty.
2. Consistency across sections: a term, a number or a claim worded one way in one section's proposals and another way elsewhere; a move applied in one section that leaves a neighbour inconsistent. List each under "cross_section".
3. Page budget: the venue's length rules (contract section 2) bind. Sum the kept and revised suggestions' word changes per section and say in "page_budget" whether taking them all is length-neutral, and which ones add length.
4. The five skim passes (title and abstract; the last introduction paragraph with figures and captions; the first introduction paragraph with the first and last discussion paragraphs; the first sentence of every paragraph; deep reading by choice): for each pass, say whether the paper with the kept suggestions serves it, and name the suggestion ids that fix it.
5. Re-rank within each section (rank 1 = most worth the owner's time) and give "top": the 15 suggestion ids across the paper that matter most, in order.

${HOUSE}

Advisor output and checker verdicts, by section (JSON):
${JSON.stringify(advised)}`
}

// ---- Read
phase('Read')
const reads = await parallel(GROUPS.map(g => async () => {
  const ids = g.map(p => p.id).join('+')
  const opts = { label: 'read:' + ids, phase: 'Read', schema: READ_SCHEMA, agentType: READER_TYPE }
  let r = await agent(readerPrompt(g), opts)
  if (!r) {
    log('reader ' + ids + ' returned nothing; retrying once')
    r = await agent(readerPrompt(g) + '\n\n(Second attempt: the first run returned nothing.)', { ...opts, label: 'read-retry:' + ids })
  }
  return r ? { group: g.map(p => p.id), ...r } : null
}))
const okReads = reads.filter(Boolean)
const missing = GROUPS.filter((g, i) => !reads[i]).map(g => g.map(p => p.id).join('+'))
if (missing.length) log('NOT READ (no result after retry): ' + missing.join(', '))
log(`readers done: ${okReads.length}/${GROUPS.length}; suggestions ${okReads.reduce((n, r) => n + r.suggestions.length, 0)}; moves ${okReads.reduce((n, r) => n + r.moves.length, 0)}`)

// ---- Understand: each advisor takes its share of the sections
phase('Understand')
const advisors = await parallel(ADVISOR_GROUPS.map(secs => () => {
  const material = Object.fromEntries(secs.map(sec => [sec.key, {
    suggestions: okReads.flatMap(r => r.suggestions.filter(s => s.section === sec.key)),
    moves: okReads.flatMap(r => r.moves.filter(m => m.our_section === sec.key)),
  }]))
  for (const sec of secs) log(`${sec.key}: ${material[sec.key].suggestions.length} reader suggestions, ${material[sec.key].moves.length} moves to its advisor`)
  const keys = secs.map(s => s.key)
  return agent(advisorPrompt(secs, material), { label: 'advise:' + keys.join('+'), phase: 'Understand', schema: advisorSchema(keys), agentType: ADVISOR_TYPE })
}))
const advice = advisors.filter(Boolean).flatMap(a => a.sections)
const noAdv = KEYS.filter(k => !advice.some(a => a.section === k))
if (noAdv.length) log('NO ADVISOR RESULT: ' + noAdv.join(', '))

// ---- Check: the checks of every section, pooled and split into CHECKERS contiguous chunks
phase('Check')
const checks = advice.flatMap(a => a.checks.map(c => ({ ...c, section: a.section })))
const size = Math.max(1, Math.ceil(checks.length / CHECKERS))
const chunks = []
for (let i = 0; i < checks.length; i += size) chunks.push(checks.slice(i, i + size))
const res = await parallel(chunks.map((c, i) => () =>
  agent(checkerPrompt(c), { label: `check:${i + 1}`, phase: 'Check', schema: CHECK_SCHEMA, agentType: CHECKER_TYPE })))
const notRun = new Set(chunks.filter((c, i) => !res[i]).flatMap(c => c.map(x => x.id)))
if (notRun.size) log('checks not run: ' + [...notRun].join(', '))
const verdicts = res.filter(Boolean).flatMap(r => r.results)
const advised = advice.map(a => {
  const ids = new Set(a.checks.map(c => c.id))
  return { section: a.section, advisor: a, check_results: verdicts.filter(v => ids.has(v.id)), checks_not_run: [...ids].filter(id => notRun.has(id)) }
})

// ---- Coordinate
phase('Coordinate')
const coord = await agent(coordPrompt(advised), { label: 'coordinate', phase: 'Coordinate', schema: COORD_SCHEMA, agentType: COORDINATOR_TYPE })

return {
  readers_ok: okReads.length, readers_missing: missing,
  reader_suggestions: okReads.reduce((n, r) => n + r.suggestions.length, 0),
  sections: advised.map(a => ({ section: a.section, suggestions: a.advisor.suggestions.length, dropped: a.advisor.dropped.length,
    checks: a.advisor.checks.length, check_verdicts: a.check_results.reduce((m, r) => { m[r.verdict] = (m[r.verdict] || 0) + 1; return m }, {}), checks_not_run: a.checks_not_run.length })),
  advisors_missing: noAdv,
  coordinator: coord ? { top: coord.top, page_budget: coord.page_budget, cross_section: coord.cross_section.length,
    actions: coord.sections.map(s => ({ section: s.section, keep: s.final.filter(f => f.action === 'keep').length, revise: s.final.filter(f => f.action === 'revise').length, drop: s.final.filter(f => f.action === 'drop').length })) } : null,
}
