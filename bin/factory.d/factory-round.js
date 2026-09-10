// factory-round.js - the F12 fan-out workflow for one `size: large` ticket's round 1:
// one Fable-checked plan, two to four Opus builders on disjoint files, one Opus
// integrator that reruns every check and commits. Run by the worker via the Workflow
// tool; every agent is pinned to the worker model by CLAUDE_CODE_SUBAGENT_MODEL.
//
// globsOverlap and normalizeOwnsGlob below are ported from Leonxlnx/unlazy
// (scripts/lib/gates.mjs), MIT License, Copyright (c) 2026 Leonxlnx. One edit: node's
// path.isAbsolute(raw) is inlined as raw.startsWith("/"), since a workflow script has
// no Node API access.
//
// The outcome is handed back through <run>/tasks/result.json, not this script's return
// value: `node --input-type=module --check` (the `script` done-check) rejects a
// top-level return in an ES module, and the script cannot write files itself. An absent
// result.json means the worker implements the round solo.

export const meta = {
  name: 'factory-round',
  description: 'Plan, build in parallel, integrate one factory ticket',
  phases: [{ title: 'Plan' }, { title: 'Build' }, { title: 'Integrate' }],
}

// ---- globsOverlap, ported from Leonxlnx/unlazy scripts/lib/gates.mjs (MIT) ----
// Prove disjointness only when literal path segments disagree. Everything else
// conflicts, including mid-segment pairs such as a* and ab*.
function normalizeOwnsGlob(value) {
  const raw = String(value || '').trim().replace(/\\/g, '/').replace(/^\.\//, '')
  if (!raw) return { error: 'OWNS path is blank' }
  if (raw.startsWith('/') || /^[A-Za-z]:\//.test(raw) || raw.startsWith('//')) {
    return { error: 'OWNS path must be relative: ' + value }
  }
  const parts = raw.split('/')
  if (raw.includes('\0') || parts.some((part) => part === '..')) {
    return { error: 'OWNS path cannot contain traversal: ' + value }
  }
  const normalized = parts.filter((part) => part !== '' && part !== '.').join('/')
  if (!normalized || normalized === '.') return { error: 'OWNS path cannot claim an implicit root' }
  return { value: normalized }
}

function globsOverlap(left, right) {
  const a = normalizeOwnsGlob(left)
  const b = normalizeOwnsGlob(right)
  if (a.error || b.error) return true
  const as = a.value.split('/')
  const bs = b.value.split('/')
  const count = Math.min(as.length, bs.length)
  for (let index = 0; index < count; index++) {
    const av = as[index]
    const bv = bs[index]
    if (/[*?[{]/.test(av) || /[*?[{]/.test(bv)) return true
    if (av !== bv) return false
  }
  // An exact prefix may denote a directory ownership claim, so it can overlap every
  // descendant. Treat common-prefix length differences as conflicts.
  if (as.length !== bs.length) return true
  return true
}

// The first pair of owned globs across two tasks that could match one path, or null.
function firstOverlap(tasks) {
  for (let i = 0; i < tasks.length; i++) {
    for (let j = i + 1; j < tasks.length; j++) {
      for (const a of tasks[i].owns || []) {
        for (const b of tasks[j].owns || []) {
          if (globsOverlap(a, b)) {
            return `task ${i + 1} glob "${a}" overlaps task ${j + 1} glob "${b}"`
          }
        }
      }
    }
  }
  return null
}

// ---- prompts ----
const PLAN_PROMPT = (ticket, run) => `You are the planner for one factory ticket. Read the ticket file at ${ticket}.

Decide whether the ticket's round-one work splits into two to four independent tasks that separate agents can build in parallel while sharing one working tree.

Rules:
- Each task is at least ten minutes of real implementation work.
- Each task owns a disjoint set of repo-relative file globs. No two tasks may own globs that could match the same path.
- Return at most four tasks; four is the review ceiling.
- If you cannot find at least two such tasks, set solo to true with a one-line reason and stop. Do not force a split.
- If you set solo to true, also append one line "PLAN solo: <reason>" to ${run}/worker/decisions.md.

For each task return:
- objective: one sentence naming what the task delivers.
- owns: the repo-relative file globs this task alone edits.
- tools: the tools and skills this task may use, as a short phrase.
- check: one line in the done-checks form, "A && pass NAME || fail NAME \\"why\\"", that proves the task using pass and fail from lib.sh.

Also return goal: the ticket's "## Goal and why" section verbatim, so each builder has the ticket's intent without reading the whole ticket.

Return JSON matching the schema: { solo, reason, goal, tasks }.`

const BUILD_PROMPT = (task, goal, run) => `You are one builder in a parallel round. You share the working tree with other builders, so you edit ONLY the files your task owns, and you never run git add or git commit; the integrator commits.

The ticket's goal and why:
${goal}

Your task:
${JSON.stringify(task, null, 2)}

Do:
1. Implement the objective by editing only files matching your owned globs: ${(task.owns || []).join(', ')}.
2. From the worktree root, source ${run}/frozen/lib.sh, then run your check line: ${task.check}
3. Write your artifact to ${task.artifact}: what you changed, the files you touched, and the exact output your check line printed.

Edit nothing outside your owned globs. Do not commit. Your final text is ignored; the artifact at ${task.artifact} is your hand-back.`

const INTEGRATE_PROMPT = (tasks, run) => `You are the integrator for one factory ticket. The builders have edited the shared working tree and each wrote an artifact. Accept work only when its check passes, then commit; the working tree must be clean when you finish.

Tasks, each with its owned globs, its check line, and its artifact path:
${JSON.stringify(tasks, null, 2)}

Do, from the worktree root, sourcing ${run}/frozen/lib.sh first:
1. For each task: read its artifact. If the artifact file is missing, the task is unmet. Otherwise rerun the task's check line yourself; if it prints FAIL, the task is unmet - do not trust the builder's reported output.
2. For an unmet task you can fix by editing only that task's owned globs, fix it and rerun the check. If you cannot make it pass, append a line "ABANDON <objective> <reason>" to ${run}/worker/decisions.md, restore that task's owned files to HEAD so no partial edit is left, and count the task abandoned.
3. Run the ticket's full done-checks block: ${run}/frozen/checks.sh from the worktree root. Capture its output.
4. Commit the accepted work with git, one commit per task or a single commit whose message names each task. Never push and never open a PR. Then run git status --porcelain and make it empty: git restore or git checkout any file still changed by an unmet or abandoned task.

Finally, write ${run}/tasks/result.json with exactly this JSON, and return the same object:
{"solo": false, "unmet": [<objectives you could not make pass>], "abandoned": [<objectives you abandoned>], "checks": "<the done-checks output>"}`

// ---- schemas ----
const PLAN = {
  type: 'object',
  properties: {
    solo: { type: 'boolean' },
    reason: { type: 'string' },
    goal: { type: 'string' },
    tasks: {
      type: 'array',
      maxItems: 4,
      items: {
        type: 'object',
        properties: {
          objective: { type: 'string' },
          owns: { type: 'array', items: { type: 'string' } },
          tools: { type: 'string' },
          check: { type: 'string' },
        },
        required: ['objective', 'owns', 'check'],
      },
    },
  },
  required: ['solo'],
}

const RESULT = {
  type: 'object',
  properties: {
    solo: { type: 'boolean' },
    unmet: { type: 'array', items: { type: 'string' } },
    abandoned: { type: 'array', items: { type: 'string' } },
    checks: { type: 'string' },
  },
  required: ['solo', 'checks'],
}

// ---- the round ----
// A terminal solo branch just ends: the worker reads no result.json and implements
// the round itself. Only a fully integrated round writes result.json.
async function main() {
  const run = args.run
  const ticket = args.ticket
  const usable = (p) => p && p.solo !== true && Array.isArray(p.tasks) && p.tasks.length >= 2 && p.tasks.length <= 4

  phase('Plan')
  let plan = await agent(PLAN_PROMPT(ticket, run), { effort: 'high', schema: PLAN, label: 'Plan', phase: 'Plan' })
  if (!usable(plan)) {
    log(`solo: planner returned ${plan && plan.solo ? `solo (${plan.reason || 'no reason'})` : 'no usable split'}`)
    return
  }

  let conflict = firstOverlap(plan.tasks)
  if (conflict) {
    log(`overlapping owned globs (${conflict}); asking the planner once more`)
    plan = await agent(
      `${PLAN_PROMPT(ticket, run)}\n\nYour previous split had overlapping owned globs: ${conflict}. Return tasks whose owned globs cannot match a common path, or set solo to true with a reason.`,
      { effort: 'high', schema: PLAN, label: 'Plan (retry)', phase: 'Plan' },
    )
    if (!usable(plan)) {
      log(`solo: planner returned ${plan && plan.solo ? `solo (${plan.reason || 'no reason'})` : 'no usable split'} on retry`)
      return
    }
    conflict = firstOverlap(plan.tasks)
    if (conflict) {
      log(`solo: owned globs still overlap after one retry (${conflict})`)
      return
    }
  }

  const tasks = plan.tasks.map((t, i) => ({
    n: i + 1,
    objective: t.objective,
    owns: t.owns,
    tools: t.tools,
    check: t.check,
    artifact: `${run}/tasks/${i + 1}.md`,
  }))

  phase('Build')
  const built = await parallel(
    tasks.map((task) => () =>
      agent(BUILD_PROMPT(task, plan.goal || '', run), { effort: 'xhigh', label: task.objective, phase: 'Build' }),
    ),
  )
  log(`${built.filter(Boolean).length}/${tasks.length} builders returned`)

  phase('Integrate')
  await agent(INTEGRATE_PROMPT(tasks, run), { effort: 'xhigh', schema: RESULT, label: 'Integrate', phase: 'Integrate' })
}

await main()
