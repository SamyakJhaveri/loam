# 🏦 The Vault Toolkit - The Vault

> Source: [🏦The Vault Toolkit - The Vault](https://www.skool.com/cliefnotes/classroom/7634b927?md=6694488c69ee463ab1367c9379cfdc2e)

---

---

### What This Is (Download at bottom)

The Vault Toolkit is a constraint library, reference architecture gallery, and skill starter collection. It is not a prompt pack. It is not a template you paste and pray.

It is a set of tools organized around problems you have already run into. Every file follows the same structure: the principle that solves the problem (most of which are decades old), the existing tools or skills that handle part of it, and the architectural thinking that makes the fix permanent.

Every constraint file includes tuning questions. Answer them before you use the file. The constraint adapts to your workflow, not the other way around.

---

### What Is Inside

**8 Constraint Files**

Each one addresses a specific frustration. Each one has three layers: the traditional solution that predates AI, the existing tool or skill that handles part of the problem, and the deeper architectural principle that makes the fix stick.

1. AI Keeps Writing Like AI References Orwell's six rules (1946), the Hemingway Editor, Grammarly, the blader/humanizer skill and its forks. Then goes deeper into why AI writing sounds generic (it is a probability problem, not a prompting problem) and introduces the three-file voice architecture: voice/tone, format patterns, and constraints as separate files.
2. Output Drifts From What I Asked Covers Bloom's Taxonomy for instruction clarity, structured output formats, and the ICM stage contract with explicit Inputs/Process/Outputs. Explains why drift happens (the model fills gaps in your instructions with its best guess) and how to close the gaps.
3. My Context Window Is a Mess References Parnas (1972) on separation of concerns, the Unix philosophy, and the Liu et al. research on context degradation. Breaks down the five-layer context hierarchy (L0 through L4) and gives practical rules for token budgeting and context hygiene.
4. I Cannot Get Consistent Results Across Sessions Covers Architecture Decision Records from software engineering, the [CLAUDE.md](http://CLAUDE.md) as persistent state, and the update discipline. Explains why the workspace is the memory and how to externalize state so the model does not have to carry it.
5. My Voice File Is Not Working References the AP Stylebook and Chicago Manual for how professional style guides separate direction from rules. Introduces the three-file voice architecture in full detail with examples of good and bad voice entries. Explains why describing your voice TO the model produces generic output and what to do instead.
6. I Do Not Know What Layer This Problem Belongs On The 60/30/10 framework. 60% traditional tools, 30% rule-based logic, 10% AI. Includes the three-question diagnostic for routing any task to the right layer. References Herbert Simon on bounded rationality and covers spreadsheets, Zapier, n8n, and purpose-built software as alternatives to throwing everything at a model.
7. My Workflow Works But Does Not Scale Covers Brooks (The Mythical Man-Month), the Toyota Production System, and Paul Graham on doing things that do not scale. Distinguishes automation from scaling. Includes the scaling audit for each step in your workflow.
8. I Built Something But Cannot Hand It Off References Architecture Decision Records, README conventions, and naming as documentation. Covers self-documenting folder structure, the handoff checklist, and how a well-built workspace can be handed off by handing someone the folder.

**3 Annotated Reference Architectures**

Real downloadable folders you can open, explore, and study. Every file is annotated with what layer it sits on (L0 through L4), why it exists, and what would change if your workflow were different.

Content Production: Three-stage pipeline (Research, Script, Production) with config files for voice, format patterns, and constraints. Includes stage contracts with explicit inputs, process steps, and "done looks like" criteria.

Small Business Operations: Three-stage pipeline (Intake, Process, Deliver) with config files for business rules, quality standards, and client context. Designed for service businesses, freelancers, and small teams handling recurring work.

Client Delivery: Four-stage engagement pipeline (Discovery, Build, Review, Handoff) with config files for client brief, engagement terms, and scope agreement. Designed for consultants and agencies running multi-stage projects.

Each architecture includes template config files with annotations explaining what to write and why.

**3 Skill Starters**

Skills that ask before they build. Each one opens with diagnostic questions about your specific workflow, then assembles a customized workspace based on your answers.

Content Production Builder: 5 diagnostic questions, then assembles your content workspace. Business Operations Builder: 6 diagnostic questions, then assembles your operations workspace. Client Delivery Builder: 6 diagnostic questions, then assembles your engagement workspace.

---

### How to Use This

**If you work in Claude Code, Cursor, or VS Code:** Drop constraint files into your workspace. Reference them from your [CLAUDE.md](http://CLAUDE.md). Load selectively based on the stage of work you are in. Do not load all of them at once.

**If you work in Claude Projects:** Add constraint files as knowledge sources. Use one or two at a time, matched to the task.

**If you work in Claude Desktop, ChatGPT, Copilot, or any other chat interface:** Copy the constraint content into your conversation when you need it. These are portable. The principles work regardless of which model or tool you are using.

**If you are non-technical:** Start with Constraint 06 (Layer Triage). It will help you figure out which problems actually need AI and which ones need a spreadsheet. Then move to whichever constraint matches your most frequent frustration.

---

### A Note on What This Is Not

This is not a prompt library. If you want 50 copy-paste prompts, this is the wrong resource.

This is the thinking behind the prompts. It is the architecture that makes prompts unnecessary. A good workspace with good constraints and good stage contracts produces good output without you needing to engineer a perfect prompt every time.

The constraint files reference real tools and skills by name with links. The architecture files are real folders you can download and explore. The skill starters build real workspaces through conversation. Nothing here is theoretical.

---

The Vault Toolkit will be updated as new tools, skills, and constraints are developed. What you download today gets better over time.

![Full Toolkit](/Users/samyakjhaveri/Downloads/jvc_vault_course/assets/full_toolkit.zip)