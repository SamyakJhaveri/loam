# Loop / factory videos: transcript report

Six YouTube URLs requested. Five transcripts retrieved via `yt-dlp` auto-captions.
One video has no captions and is reported from title and description only.

Raw artifacts on disk:

- Cleaned plain text: `clean_<VIDEOID>.txt`
- Original captions: `subs/<VIDEOID>.en.vtt`

---

## Video 1 - "Every Level Of Claude Code Loop Engineering Explained"

**a. Title and channel.**
"Every Level Of Claude Code Loop Engineering Explained", channel AI LABS.
https://www.youtube.com/watch?v=PLyRe6Zk--8
Transcript: RETRIEVED (5,371 words).

**b. The loop shape, step by step.**

Definition given first. "An agent loop is when you remove yourself from this process,
and that verification part goes to the agent as well."
The parts named are: something that starts the loop, the loop itself, and a
verification check at the end of each pass that decides whether the agent is done.

Level 1, the single loop, run on a landing page:

1. `grill-me` skill interrogates the user until the requirement is clear.
2. It writes a spec file into `features/<name>/`, next to an empty `verification/`
   folder that fills up as the loop runs.
3. The spec is written *as a goal*, so `/goal` can execute it directly.
4. The user names the skills to use (`GSAP` for animation, `optimized` to claw back
   page speed) and supplies an image reference.
5. `/goal` runs. The agent builds, then scores itself against the checklist that
   lives in the same file, repeatedly, until the condition is met.
6. A `goal-writer` skill was then built so the whole setup does not have to be
   repeated per feature. It creates the feature folders with specs already written
   as goals.

Level 2, the software factory loop:

1. Features are planned collectively, not one at a time.
2. `new-feature` skill creates a folder per feature holding `spec.md` plus
   verification material.
3. `functional-ui` skill creates a `mocks/` folder holding a fully clickable HTML
   prototype of the app, and a per-feature HTML mock showing only what that feature
   changes. Only one mock exists per folder; the skill will not recreate it.
4. `feature-batch` skill writes `Q.md`, a single table listing every feature with a
   status column (to do / building / done).
5. `/goal` is pointed at `Q.md` with the stop condition: no row left in "to do" or
   "building".
6. The main agent picks a row. It does not build. It creates a git branch and hands
   the task to a build sub-agent.
7. When the sub-agent finishes, the main agent hands the branch to an adversarial
   review agent, a different agent with a fresh context window.
8. A finding sends the work back to the build agent. This repeats until the feature
   ticks off.
9. The agent opens a pull request with screenshots attached. The human merges. Merging
   to main is what pushes the feature to the deployed Vercel app.

Level 3, removing the laptop:

1. The app runs through Paseo, which runs Claude Code on your own machine and gives a
   phone window into it. It also drives a connected Mac mini.
2. All skills and slash commands, `/goal` included, work there.
3. A `mobile-preview` skill deploys the HTML mocks to free Vercel links so the
   prototype is clickable from the phone, not just viewable as images.

Infrastructure prerequisite, set up once: GitHub for the repo, Supabase for the
database, Vercel for deployment. The human only creates accounts and pastes three CLI
login commands. "Your agent can't click around on a website the way you do. So, the
CLI is an app for the agent to use the platform."

**c. What verifies the work, and who writes that verification.**

The human writes it. Three verifiers, all authored before the loop starts:

1. **The spec file is the checklist.** "What it wrote was both things at once. It's
   the spec for building the page, and it's the verification checklist that gets run
   against that page."
2. **The clickable HTML prototype is the second bar.** "This prototype becomes a way
   for the agent which is working in a loop to verify if the thing that it built is
   correct or not."
3. **The adversarial review agent** re-checks the branch in a fresh context.

Screenshots come from a specific tool named in the user's global `CLAUDE.md`, chosen
because "that tool takes the screenshots way faster than opening a full browser every
single time."

Final human gate: the pull request, with screenshots attached as proof. The user can
also ask Claude to switch to the branch locally and test it before merging.

Explicit statement of who owns the check: "that verification check needs to be decided
by you."

**d. Keep it simple, get out of the model's way, do not over-check.**

- On not looping the first build: "An MVP is quick to build anyway, but to put a loop
  on it, you'd have to decide what done looks like before the agent even starts. And
  at that point, you don't really know where the product is going yet. So, working
  that out ends up taking you longer than just building the first version yourself."
- On not looping cheap work: "Putting a loop around a landing page would be more work
  than the page itself." The landing page qualified only because it was motion-heavy
  and "that's the part you can't really check by looking at it once."
- The stated trigger for looping at all: "This is actually a really good way to check
  if something needs to be looped is if it requires a lot of back and forth with the
  agent."
- On what stays human: "In an agent loop, the piece that you keep is the piece that
  was always going to be yours. That's the piece that decides whether you turn the
  agent off or you need it to work more. You can't really hand this off."
- On why loops only work now: "Models couldn't really run for this long. And now, with
  the new models that are coming out, they can basically work without you for hours."
- On skills being unremarkable: "A skill is really just written instructions sitting in
  a file. So there isn't anything in here that you can't actually make on your own."
- On skill composition, kept minimal: "If we don't want a feature to become a goal, if
  we just want to work on the feature without a loop, we don't use goal writer."
- On what an automated check will never catch: the mascot blink. "That one mistake is
  the one thing the verification was never going to catch because a screenshot only
  ever catches a single moment, and the gap between one blink and the next is too
  short for two screenshots to catch." Fixed with one human correction prompt.

**e. Separate verifier, fresh context, deterministic gate.**

- The central rule, stated as a rule: "The agent that does the work should never verify
  it. The verification should always go to another agent with a fresh context window."
- The reviewer's stance is adversarial by construction: "This means that the agent
  always needs to believe that there is some error in the work done. This is how it's
  useful in capturing bugs."
- Sub-agents are isolated by design: the main agent "hands the task to a sub-agent."
- Blast radius is contained deterministically: "the main agent makes a copy of the
  folder called a branch and the agent works on that," so a bad build cannot ruin the app.
- The stop condition is a table state, not a judgement: the goal "was only going to
  stop when no row was in to do or building."
- A naming correction about the gate mechanism: `/loop` "runs a prompt on a timer, so
  every 5 minutes or every hour it fires again, whether anything changed or not,"
  whereas `/goal` "is the one that keeps working until the thing you asked for is
  actually done." Loop engineering means `/goal`.
- How `/goal` decides: "At the end of every turn, a smaller model reads through the
  conversation and decides whether the agent needs to work on this again or if the
  condition is met or not."

**f. Numbers.**

| Item | Value |
|---|---|
| Landing page loop runtime | 38 minutes |
| Errors surviving that loop | 1 (mascot blink) |
| Correction prompts to fix it | 1 |
| Factory run, two features | still running at ~3 hours when filmed |
| Features in the batch | 2 (services page, session reviews) |
| Cost | not stated |

---

## Video 2 - "This Claude Skill Just Fixed Loop Engineering"

**a. Title and channel.**
"This Claude Skill Just Fixed Loop Engineering", channel AI LABS.
Published 2026-08-14. https://www.youtube.com/watch?v=D_uojDHkbw4
Transcript: RETRIEVED (3,331 words).

**b. The loop shape, step by step.**

The gauntlet loop, originated by Matt Schumer, who posted a first-person shooter Claude
built from one prompt with no existing assets. The whole method is a three-line prompt.

1. **Line one, what and how good.** Names the thing to build and the quality bar.
   Schumer's asked for a first-person shooter at the level of the most recent Call of
   Duty, spelling out that it had to be perfect "in literally everything from the
   textures to the physics."
2. **Line two, how to split.** Tells the main agent to break the goal into parts itself
   and hand each part to its own sub-agent, each working in its own memory without
   seeing the others.
3. **Line three, the bar the critic uses.** Names the comparison product and tells the
   critic when it may stop.
4. The keyword "ultra code" (caption spelling, almost certainly a Claude Code keyword)
   turns this into a dynamic workflow that runs a fleet of sub-agents at once rather
   than a few.
5. The resulting shape is called a graph, specifically a diamond: "one task at the top
   splitting out into several sub-agents running side by side, and then narrowing back
   down into a single agent that pulls everything they found into one answer."
6. Every builder sub-agent is paired with a critic sub-agent inside its own loop.

The fix, applied to an HR system with no product to copy:

1. Run the trimmed Wayfinder skill (Matt Pocock's planning skill, rewritten by the
   channel) as an explicit command, since "this is one of those skills the agent won't
   start on its own."
2. Wayfinder interrogates. It asked who the app is for, what is in and out of scope,
   what done looks like, and what could go wrong in production.
3. It writes two files into a `.wayfinder/` folder: **the map** (every decision, its
   reasoning, and what the finished thing looks like) and **the answer key** (nothing
   but pass/fail checks).
4. Take Schumer's exact gauntlet prompt, hand it to Claude, and ask it to rewrite it
   for your app. "The one thing you change is what it measures against. Instead of a
   game, you tell it the source of truth is the .wayfinder folder."
5. Run it. It planned what to build first, then the tools to install, then foundation
   work, "so the agents had something solid to build on." Then it launched many agents
   at once, each on a different part.

**c. What verifies the work, and who writes that verification.**

In the original gauntlet loop, the main agent writes the critics' instructions, and
the video treats that as defect number one. The critic compares the built artifact to
Call of Duty **blindly**: "Blind here just means it isn't told which one Claude made,
so it doesn't know which one is the product and which one is the game Claude
designed."

In the fix, the human writes it, indirectly, through the interview. The answer key
replaces the shipped product as the bar: "just like how Call of Duty worked as a bar
for the game, a spec becomes the same bar and becomes a way to verify what marks the
thing you want to build as done."

The critic never builds. "The critic's only job is to check the work, and if it isn't
good enough, it sends it back to the builder agent to correct until it is."

**d. Keep it simple, get out of the model's way, do not over-check.**

- On the prompt: "the prompt behind all of that is nowhere near as complex as you'd
  expect", "the whole method is a prompt that's only three lines long", "it's simple
  enough that you can write the same three lines for whatever you're making."
- On not doing the decomposition yourself: "The agent has to split the work up by
  itself so that this hassle doesn't come on you."
- On cutting the tool down, the clearest simplicity statement in the set: "Wayfinder is
  really extensive in how it plans, because it's built to carry you all the way through
  to a finished spec. That wasn't what we needed. We only wanted the part that gets you
  to clarity so that we'd come out of it with a complete plan and nothing else."
- The result of that cut: "What we ended up with is a much simpler version, one that
  only writes two files, the map and the answer key, instead of the separate tickets
  the original produces."
- Dependencies were cut too: "The Wayfinder skill doesn't work by itself. It calls
  other skills from Matt Pocock as well. But, in our version we've also reduced that.
  You just need these three skills."
- On why the loop is worth running at all, quoting Karpathy (caption spelling
  "Andre Karpathy"): work this high quality "was never worth producing before when it
  took... A model doesn't have that limit."
- Counter-pressure, the one anti-simplicity line: "We told it there was no close enough
  and no shortcuts."

**e. Separate verifier, fresh context, deterministic gate.**

- The founding argument for an external bar: "He could have told the agent to make the
  game good, but good is something it decides for itself and an agent that decides its
  own standard passes its own work."
- Fresh context, stated concretely: the critic "never builds anything itself, and it
  starts with no memory of what came before. So, it doesn't know who made the work or
  how many times this part has already been sent back. It just has to be brutal and
  critically honest in grading the thing."
- Defect one, the agent authoring its own checks: "the main agent is completely
  responsible for checking. It manages on its own how it spins up the critics and
  writes their instructions. So basically, you don't have control on the agents nor how
  the judgment prompt is being passed to the critics."
- The channel's standing position: "checking is something you should set more
  concretely rather than letting the agent verify on its own."
- Defect two, the bar itself: "The quality bar in that prompt is an existing product...
  when you're building something new, there's no existing app to set that bar by. The
  critic makes up a standard and starts passing work by it. And when you realize that
  its assumed direction isn't what you want, you've wasted a lot of time and tokens."
- Generalized: "having nothing to compare the work to is the normal case, not the
  exception... the gauntlet loop works when there's something close enough to copy, and
  it breaks the moment there isn't."
- The two-part fix, stated as such: "The first is verification, where you plan the
  checks properly instead of letting the agent invent them... The second is giving the
  loop concrete requirements so that it doesn't drift from what you want."
- The fog, on silent assumption: "The agent never tells you when it's in the fog. It
  fills the gap with its own assumption and carries on planning as though the thing was
  settled. So, what you get back is a plan that looks finished with invented parts in
  the middle of it."
- Fog resolution is action, not guessing: "When Wayfinder hits fog, it doesn't guess.
  It sends the agent off to go and clear the fog, and that can be done through either
  researching or building something rough to look at and react to, or a real-world job
  like signing up for a service so you can judge it."
- Deterministic gate: the answer key "is nothing but checks, where every line comes back
  as either a pass or a fail."

**f. Numbers.**

| Item | Value |
|---|---|
| Gauntlet prompt length | 3 lines |
| Wayfinder interview | 34 questions |
| Files Wayfinder emits (trimmed) | 2 (map, answer key) |
| Skills required (trimmed) | 3 |
| HR system build time | 1 hour 33 minutes |
| Session limit consumed | ~40% of a max plan |
| Equivalent API cost | ~$116 |
| Outcome | every wanted feature working, "though it did have some issues" |

---

## Video 3 - "GitHub's #1 Trending Author's New Claude Skill Is Insane"

**a. Title and channel.**
"GitHub's #1 Trending Author's New Claude Skill Is Insane", channel AI LABS.
https://www.youtube.com/watch?v=c47uqR7XB_c
Transcript: RETRIEVED (2,942 words).
Subject: the `unlazy` skill, by the author of the design-taste skill.

**b. The loop shape, step by step.**

1. You invoke the skill with a **tree depth** number and the task. "If you say five,
   the task gets broken down five times over and no further." No number means it picks
   the smallest depth that fits.
2. The skill splits the task into sub-tasks, then splits each of those again, and so on
   to the given depth. "That's why it's called a tree."
3. Leaf tasks are handed to their own sub-agents.
4. Depth three or under is **solo mode**, the default. "Everything stays in one session,
   and the same agent works through all of it."
5. Depth four and up is **orchestrated mode**, which writes things down: a `plan.md`
   holding the whole breakdown, and a separate checklist file for every task in it.
   `plan.md` also records which task touches which file "so that if two agents are
   working at the same time, they don't overwrite each other's work."
6. It lays foundation work first, then hands tasks out.
7. In orchestrated mode, each task goes to a fresh agent that receives only the plan
   and its own gates file.
8. When that agent reports done, the main agent re-runs that task's checks itself
   before writing a completion line into `plan.md` and issuing the next task.

The channel found a defect and patched it. As shipped, the skill "hands out one task,
waits for it to complete, and only then hands out the next one," despite both Claude
Code and Codex being able to run agents in parallel. They rewrote the skill to fan out.

**c. What verifies the work, and who writes that verification.**

A ledger, written to disk before any work starts, called the **gates file**. Each entry
is a gate: a checkbox with an outcome next to it, one thing that must be true. Under
each outcome sit three lines:

1. The command that proves the outcome.
2. The exact words that command must return.
3. The evidence line, which starts as `pending`.

The skill ships a **checker**. "When you run it, it goes down that file and runs every
one of those commands itself. If the answer that comes back has the words the gate was
expecting, it ticks the box, and it replaces that pending line with the bit of the
answer that decided it."

The evidence line is the whole point: "A tick box with pending still under it, it means
the agent ticked that box itself, which is just the agent telling you it's done all over
again. So, it counts as unmet, and the skill treats that as worse than an empty box,
because an empty box is at least honest about where the work actually got to."

There is an explicit honest-failure path. "Sometimes a task turns out to be impossible.
So, instead of the agent dropping it and saying nothing, it writes a line giving up on
that gate by name with the reason, and that goes into the report you get at the end."

Framing: "it doesn't tell you the agent is done, it proves it."

**d. Keep it simple, get out of the model's way, do not over-check.**

- The key lesson, on why instructions fail and files work: the previous version "tried
  to fix laziness by telling the agent to be thorough. But, an instruction is the first
  thing to get lost in a long session, which is the exact problem it was trying to fix.
  So, this version stopped asking and started putting it in a file before any work
  begins."
- Against over-decomposition, with a concrete floor: "those tasks can't be too small,
  either. The rule the skill gives is that each one should be worth at least 10 minutes
  of real work, because it has to be a proper piece of the job that an agent can pick up
  and finish on its own."
- Self-correcting depth, so the user cannot over-tune it: "if you set that number too
  high, and the tasks come out smaller than the 10 minutes of work, the skill lowers the
  split task to the default number, which is three." And: "you don't have to worry about
  selecting the wrong option because if you picked higher than needed, it will
  automatically lower the depth for you."
- Simple mode is the default: three or under stays in one session with one agent. The
  heavier machinery only switches on at four and up.
- Sizing advice: "If you want to work on a feature rather than a whole app in one go?
  Two or three would be enough for you."
- The reason splitting helps at all is attention: "When the work is broken up like this,
  each task has one clear goal, and the agent working on it isn't carrying the rest of
  the job around with it."
- The over-checking cost is shown, not argued: run as shipped, serial hand-offs burned
  3 to 4 hours to produce a login page.

**e. Separate verifier, fresh context, deterministic gate.**

- The summary claim: "Unlazy is a whole system rather than a single check at the end,
  and at no point in it does the agent get to decide whether the work is done."
- Fresh context per task: orchestrated mode "hands one task to a fresh agent, which only
  gets the plan and its own gates file, nothing about the rest of the job."
- The verifier does not trust the worker: "when that agent comes back saying it's
  finished, the main one doesn't take its word for it and runs that task's checks against
  itself, and only then does it write a line into the plan file and hand out the next task."
- Deterministic gate, precisely defined: a command, an expected exact output, and captured
  evidence. Nothing is judged by prose.
- Critique of three weaker gates, each named:
  - Ralph loop: "that finish line is just a bit of text the agent writes while it's
    working. But, a [tree] of tasks can't be judged by a finish line. There's no single
    word that tells you a feature is actually built properly."
  - `/goal`: "uses a smaller model that reads through the conversation to decide whether
    the work is finished. So, it's judging by what the conversation says instead of the
    work itself, and it can drift from what you actually needed."
  - Their own prior loops: "those checks were real, but it was the agent itself that
    graded them. So, it was still the agent deciding whether it was done."
  - All three share a failure curve: "they can all work really well when your context
    window is fresh. But once you're deep in the real work, they start to falter. And
    that's exactly the point where you need them to hold."
- Why laziness happens, mechanically: models carry the whole message pile forward, "and
  as you send more and more messages, that pile keeps growing, and there's a lot more for
  the model to pay attention to at one time."
- The two laziness modes named: reporting done when it is not, and silently shrinking the
  job. "You ask for something that has five parts to it, and one of those parts is
  difficult. It builds the four easy ones and skips the hard one. And the summary you get
  at the end never mentions anything's missing."
- The severity ranking, useful for grader design: "A model that stops early with clearly
  unfinished work is acceptable, but when it stops early and tells you it finished
  everything, that's where it becomes a problem."
- Installation detail relevant to harness layout: the skill lives in `.agents/`, and
  `.claude/` is a symlink shortcut to it, "so that Claude code can also recognize it and
  use it without having duplicates in the same project."

**f. Numbers.**

| Item | Value |
|---|---|
| Minimum task size | 10 minutes of real work |
| Default depth | 3 |
| Solo mode threshold | depth <= 3 |
| Orchestrated mode threshold | depth >= 4 |
| Depth used in the demo | 5 |
| Unpatched run | 3 to 4 hours, produced only a login page |
| Patched run | ~2 hours, 10 agents in parallel, working first version |
| Cost | not stated |

Also mentioned: pairing with a model-router skill so "the simple mechanical work goes to
a cheaper model and the hard parts go to the strong one."

---

## Video 4 - "Build $10,000 Websites using Claude Code (Ultimate Guide)"

**a. Title and channel.**
"Build $10,000 Websites using Claude Code (Ultimate Guide)". Channel not recoverable from
the caption data; not an AI LABS video by voice and format.
https://www.youtube.com/watch?v=VMvZuhcDdnw
Transcript: RETRIEVED (4,628 words).

**b. The loop shape, step by step.**

Not a loop video. It is a human-in-the-loop design tutorial with no autonomous run.

1. Install Claude Code desktop, open a dedicated folder as the workspace.
2. Install two skills: `front-end-design` (by Anthropic, auto-invoked, "bans the most
   overused fonts on the internet and pushes Claude toward bold design direction") and
   `UI-UX-Pro-Max` (community, invoked explicitly).
3. Switch to auto mode so Claude "can work without stopping to ask for permission at
   every step."
4. Gather 3 to 5 reference screenshots.
5. Write one prompt: the skill call, the brief, and the closing line "ask me clarifying
   questions."
6. Claude asks 7 questions and offers 3 style directions to pick from.
7. Claude builds. The human then polishes section by section.
8. Deploy to Hostinger with a custom domain.

**c. What verifies the work, and who writes that verification.**

A human-authored checklist of eight criteria, written before the build by asking Claude
what separates a $10,000 site from a $200 one: point of view, typography, color,
hierarchy, imagery, motion, mobile, and the invisible quality items. These group into
taste, substance, and felt quality.

Verification is self-grading, in-session, with no separate agent and no fresh context.
"You set the bar high at the start, and now you check yourself against it. To do this,
paste that checklist into Claude and ask, 'Where does this site land against each of
these criteria?' Be honest."

The polish pass is also human-driven: "The pattern is to review every section, find the
ones that feel flat, ask Claude for one cursor interaction or piece of movement per
section. And tell Claude to make it more subtle until the section feels [right]."

**d. Keep it simple, get out of the model's way, do not over-check.**

- Auto mode is framed as getting out of the way: it "lets Claude work without stopping to
  ask for permission at every step."
- One line does the planning work: "The trick to making this work is this last line. Ask
  me clarifying questions. That's the line that makes Claude stop and think before it
  starts building."
- Front-loading the answers reduces later fighting: "This is the most important moment in
  the entire build. The answers you give here become the entire site. The more specific
  you are at this stage, the less you'll have to fight Claude later to make revisions."
- Simplicity is treated as a correct outcome, not a compromise. Claude refused to drop in
  a React component: "Our project is a simple static site, so Claude says no to dropping
  in the React component as is because it would change how our whole project works." The
  video endorses the refusal and uses it to pick a cheaper hosting plan: "If Claude kept
  your site simple, premium is fine."
- Restraint as a quality signal: "There are no rainbow palettes here. Restraint with color
  is what signals quality."
- Limits acknowledged honestly: imagery "is one pillar Claude can't fully solve on its own."

**e. Separate verifier, fresh context, deterministic gate.**

None. This is the counter-example in the set. The same session that built the site grades
the site, against a checklist that session helped write. No sub-agent, no fresh context,
no command-based gate.

**f. Numbers.**

| Item | Value |
|---|---|
| Checklist criteria | 8 |
| Clarifying questions asked | 7 |
| Style directions offered | 3 |
| Reference screenshots advised | 3 to 5 |
| Planning before first line of code | ~3 minutes |
| Build time | 4 to 5 minutes |
| Claude Pro plan | $20 / month |
| Hosting | ~$60 total |
| Setup time for one integration | under 5 minutes |

---

## Video 5 - "Insane Claude Design Skills You Need To Actually Build Beautiful Sites"

**a. Title and channel.**
"Insane Claude Design Skills You Need To Actually Build Beautiful Sites", channel AI LABS.
https://www.youtube.com/watch?v=Ysr7oNDajJI
Transcript: RETRIEVED (2,841 words).

**b. The loop shape, step by step.**

A survey of design skills, not a loop or factory. The recurring shape is build-then-score-
then-refine, driven by the human:

1. Install skills into Claude settings; they work in Claude Code, Claude Design, or Codex
   identically.
2. Run a build skill, which asks clarifying questions first, then builds.
3. Run a review or critique skill against the result. It returns a score and a list of
   findings.
4. Fix and re-run. "You can keep refining the design and running it again and again until
   it reaches a perfect score and matches the design you actually want."

**c. What verifies the work, and who writes that verification.**

Third-party review skills, each grounded in stated criteria rather than model taste:

- **The review skill** in Emil Kowalski's set. "It comprehensively reviews all aspects of
  the design, so we can iterate based on the score it gives." Connecting it to GitHub makes
  it a regression check: "it checks what the design looked like before and after the changes
  you made. If something worked before your last change and doesn't anymore, it flags that
  and will be able to tell you that it doesn't work anymore because of a certain change you
  made."
- **Screen critique**, which "takes a screen and reviews it across a lot of different
  angles, then tells you where that screen is going wrong and it's working from proper
  guidelines for judging design quality."
- **Perception laws**, "grounded in actual research in the named laws that designers really
  work from."
- Connard Lee's (caption spelling) web-design-engineer skill "contains a set of references
  covering multiple design-related areas. They cover how to judge a design, the ways designs
  usually go wrong, and style recipes for well-known sites like Apple and Linear."

**d. Keep it simple, get out of the model's way, do not over-check.**

- Against impressive-looking process: "Some have an intensive workflow that seems impressive
  and at the end of it they still generate a site that looks like every other one. Only a few
  of them actually deliver."
- Install only what you use: "You don't have to install all of it. You just install the skills
  that fit how you work. For our setup, we added two."
- One skill can be enough: the Elia landing-page skill, "and this time it's just a single
  skill built for landing pages. Everything it does sits in one file."
- Skills are captured practice, not novelty: "these skills are developed by people who have
  extensive experience in design and they've repackaged the workflow they tested and that
  worked for them into a reusable form."
- Why a skill is needed at all despite strong models: "no matter how powerful a model is,
  each model follows its own pattern when it designs and that pattern is easy to spot.
  That's why you need something to steer them away from that pattern."

**e. Separate verifier, fresh context, deterministic gate.**

- The strongest structural point, one concern per skill: "unlike the others where one skill
  handles every part of the site at once, this splits it into multiple skills so each area
  gets its own skill. All the elements that are part of the design, including typography,
  color, accessibility, and more, each get a separate skill instead of having one skill
  handle everything."
- Review is a distinct skill invocation from build, though not documented as a fresh context
  or a separate agent.
- Grounding against external references rather than model judgement, the same principle as
  video 2's comparison product: "good design never starts from thin air, just like how every
  design out there is inspired by something that came before it. It also grounds itself with
  the designs that have worked previously."
- No deterministic gate. The scores are model-produced.

**f. Numbers.**

| Item | Value |
|---|---|
| Skills in Emil Kowalski's set | 9 |
| Skills used from it | 2 |
| Skills in Connard Lee's Garden set | 5 |
| Skills in the Elia design skill | 1 |
| Rounds, cost, time, success rate | none stated |

---

## Video 6 - "Designing with Claude: From prompt to production"

**a. Title and channel.**
"Designing with Claude: From prompt to production", channel Claude (@claude).
https://www.youtube.com/watch?v=Uvl-tRga98g
Duration 1,680 seconds (28 minutes).

**Transcript: UNREACHABLE.** No captions of any language exist for this video. `yt-dlp`
returned "There are no subtitles for the requested languages" after successfully retrieving
format information, and the watch page contains no `captionTracks` entry. Reported here from
title and description only, per instruction.

**Description, verbatim and complete:**

> Claude Design lets you describe what you want in plain language and get production-quality
> outputs. Learn how a small team built a design tool that ships in your brand, from prompt
> to production.

b through f cannot be answered without the transcript.

---

## UNREACHABLE list

1. **https://www.youtube.com/watch?v=Uvl-tRga98g** - "Designing with Claude: From prompt to
   production", channel Claude. No captions exist. `yt-dlp` error text: `[info] There are no
   subtitles for the requested languages`. The page carries no `captionTracks` field. Title,
   channel, duration, and description were recovered and are reported above.

No other video was unreachable. All five remaining transcripts were retrieved in full.

### Method note

Direct WebFetch of the watch pages returned only titles, because YouTube serves a shell.
The `timedtext` API returned HTTP 200 with `content-length: 0`, since it now requires a
proof-of-origin token. `r.jina.ai` returned page shells and 401s under rate limiting.
Local `yt-dlp` succeeded on the first pass for four videos and on a retry for the fifth,
after an HTTP 429.

### Risks

- All five transcripts are YouTube auto-captions. Proper nouns are unreliable. "Andre
  Karpathy", "Connard Lee", "Superbase", "gold command", "Code X", and "email design
  engineering" are caption artifacts for Andrej Karpathy, a designer whose name I could
  not confirm, Supabase, the goal command, Codex, and Emil design engineering.
- "Ultra code" in video 2 is near-certainly a mistranscription of a Claude Code keyword.
  I did not verify which one.
- One sentence in video 3 is garbled in the source: "a a of tasks can't be judged by a
  finish line." I read the missing word as "tree" from context and marked it in brackets.
- Every runtime, cost, and success figure is the creator's own claim, filmed as a demo.
  None is independently verified, and none reports a failure rate or a repeated trial.
- Channel names for videos 1, 3, and 5 come from the oembed endpoint or self-identification
  in the audio. Video 4's channel was not recoverable from the data I collected.
