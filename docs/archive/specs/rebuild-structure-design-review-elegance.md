# Elegance review - rebuild-structure-design.md

> Blind frame-breaking review, 2026-08-29.
> Reviewed artifact: `docs/specs/rebuild-structure-design.md`.
> Criteria: `docs/specs/rebuild-research/research-context-rules.md` (cited [CTX Pn]).
> Facts checked against `docs/specs/rebuild-research/research-cc-docs.md` [CC], `research-codex-docs.md` [CDX], and the working tree.
> The author's rationale was withheld from me; every finding below is derived from the document, the criteria, and the repository.

## Summary

The document is disciplined about the layers it looked at and under-priced on the layers it did not.
It agonizes over two ~50-line rule files while waving `KEEP` at a file that injects five MCP servers into every seeded project, and it spends real machinery (a new directory, a copier task, an idempotency guard, a CI assertion, and an open assumption) on shipping exactly one skill.

Three collapses account for most of the available deletion:

1. The two prose files do not need to be two sources of truth. Claude Code's documented `@AGENTS.md` import [CC §"AGENTS.md"] removes the "the two must agree" clause the design writes into itself.
2. `seed/.claude/rules/` can go to zero files, not one.
3. `seed/.codex/hooks/` and `hooks.json` should be deleted, not renamed. Renaming activates a hooks file whose commands mostly do not exist.

Net effect if all findings are taken: the seed loses one whole prose file's worth of duplicated content, one directory (`rules/`), one directory (`.codex/hooks/`), one JSON file, three MCP servers, one copier task, one absorbed lint script, and three plugin agents. Nothing in D-1..D-6 or [R-1..R-7] is reversed.

---

## E1 - Two prose files, one source of truth (largest collapse)

**Finding.** The design keeps `CLAUDE.md.jinja` and `AGENTS.md.jinja` as parallel homes and then writes the maintenance burden into the contract itself:

> "Where both harnesses need the same directive, AGENTS.md.jinja is the Codex home and CLAUDE.md.jinja the Claude home; the two must agree."

That sentence is the exact failure [CTX P4] names: "DELETE any asset that restates, softens, or contradicts a directive already present in another layer; one directive, one home." A rule that two files must agree is not one home; it is two homes plus an unenforced invariant, and nothing in the design checks the invariant (`verify-template.sh` does not compare them).

**The simpler shape.** [CC §"AGENTS.md"] records the documented bridge:

> "Claude Code reads `CLAUDE.md`, **not** `AGENTS.md`. The documented bridges are a `@AGENTS.md` import or a symlink (`ln -s AGENTS.md CLAUDE.md`)."

So the shared prose is written once in `AGENTS.md.jinja`, and `CLAUDE.md.jinja` opens with a single `@AGENTS.md` line followed only by Claude-only content (hooks, plugin skills, the routing table). Codex reads `AGENTS.md` directly and unconditionally - [CDX §4] calls it "the only artifact that works unconditionally, in every Codex surface". Claude Code resolves the import when it reads `CLAUDE.md`, including on the post-compact re-read, so D-6's durability argument is unaffected.

**Consistency with D-6.** D-6 fixes that the gotchas "fold INTO `CLAUDE.md.jinja`". An import is a fold-in at the level that matters (the content lands in the injected CLAUDE.md context), but the wording is the author's to interpret. If D-6 is read strictly as "the literal gotcha text lives in the CLAUDE.md.jinja file", then keep the gotchas there and apply the import in the other direction is not available (Codex cannot read CLAUDE.md unless `.codex/config.toml` is trusted, per [CDX §2.1] fallback filenames, and [CDX §2.2] makes that layer inert until trust). In that case the minimum change is: delete the "the two must agree" clause and state instead which directives are Codex-only, so no directive has two homes at all.

**Recommendation.** Prefer the import. At minimum, no directive may appear in both files.

## E2 - The AGENTS.md rewrite is far too gentle

**Finding.** The design drops three things from `AGENTS.md.jinja`: the `/validate` sentinel, the model-selection table, and conflicting directives. Reading the actual 150-line file, that leaves the large majority intact - and the large majority is restated general competence, which is the single most explicit delete criterion in the corpus.

Concretely, what survives the design's three cuts:

| Surviving section | Sample content | Criterion that fires |
|---|---|---|
| §1 Think Before Coding | "State your assumptions explicitly. If uncertain, ask." | [CTX P11] criterion 1: the model does this unprompted |
| §1 Simplicity First | "No abstractions for single-use code." | [CTX P3]: hard-codes a judgement the model makes from context |
| §1 Surgical Changes | "Match existing style, even if you'd do it differently." | [CTX P3]: this is verbatim the example S1 gives of a rule that was deleted and replaced with one judgement line |
| §2 Security Practices | "NEVER concatenate user input into SQL..." | [CTX P11]: general competence, not project-specific |
| §2 Scalability Practices | the symptom/first-try/then-try table | [CTX P11] + [CTX P24]: no repeated failure named |
| §3 constraints 2, 4, 5 | L0 budget, handoff format, layer triage | [CTX P24]: all reference retired machinery |
| §3 constraint 8 | "The pipeline gate (`/validate`) must pass" | already flagged; retired |

[CTX P2] is the governing number here: Anthropic removed over 80% of its own system prompt with no measurable loss. This file is the closest analogue in the template and the design proposes roughly a 20% cut.

**Recommendation.** Rewrite `AGENTS.md.jinja` down to two things: (a) project conventions the seeded project fills in, and (b) the handful of constraints that are genuinely project-specific and not general competence. My read is that survives at well under 40 lines. Everything in §1, the security block, and the scalability block should be deleted outright, not trimmed.

## E3 - `seed/.claude/rules/` should go to zero files

**Finding.** The design keeps `rules/architecture.md` with this justification:

> "It is a fill-in skeleton for the seeded project's own architecture; that job cannot fold into CLAUDE.md without bloating it."

I read the file. All 51 lines are headings, HTML comments, and the literal token `TBD`. There is not one line of information in it; it is an empty form. The design's cost argument is sound (`paths:` scoping makes it free until `src/**` is read) but the cost argument is not the relevant test. [CTX P10]'s test is "would removing this cause Claude to make mistakes?" - removing an empty form cannot. [CTX P24]'s test is "name the concrete repeated failure that caused it to exist" - shipping a blank template names none.

There is a second, worse property: a path-scoped empty form loads at the exact moment Claude reads source code, and injects a document whose every field says `TBD`. That is noise arriving at the highest-attention moment, which is what [CTX P25] warns about ("it can also add noise that makes Claude less effective").

**The simpler shape.** Delete it. If the seeded project later needs an architecture rule, the trigger for writing one is real work, not bootstrap ([CTX P24]: "Build the asset at the moment its trigger fires, not before"). With `reassess-context-md-anatomy.md` and `reassess-rewrite-known-issues.md` already going, this deletes the entire `seed/.claude/rules/` directory, which is a cleaner statement of the design's own layering than "one skeleton survives".

**Cost of being wrong:** near zero and fully reversible - the file is one `git show 317b961^:` away, and a project that wants it writes a better one for itself.

## E4 - `.codex/hooks.json` should be deleted, not renamed

**Finding, and this one is a correctness defect the design's four-defect list misses.** `seed/.codex/reassess-hooks.json` wires five hooks referencing five scripts:

- `.codex/hooks/pre-tool-policy.py` - does not exist
- `.codex/hooks/post-tool-policy.py` - does not exist
- `.codex/hooks/post-compact-recovery.sh` - exists
- `.codex/hooks/session-start.sh` - does not exist
- `.codex/hooks/stop-verify-gate.sh` - does not exist

`seed/.codex/hooks/` contains exactly one file. The design's instruction "RENAME `reassess-hooks.json` -> `hooks.json`, Codex discovers `hooks.json` only [CDX defect 1]" therefore takes a file that is currently inert *because of its name* and makes it live with four out of five commands pointing at nothing. The rename is the change that turns a latent defect into a shipped one. Defect 3 in the design's own table is "dangling refs in config.toml"; this is the same defect class, four times over, in the file being activated.

**Second finding: the one surviving hook is not worth keeping either.** The design keeps `post-compact-recovery.sh` on the grounds that "PostCompact is a documented Codex event and Codex documents no native re-injection". True, but look at what the script emits after the rest of the rebuild lands:

- project root and branch - two git commands the agent can run itself, so [CTX P18] fires ("DELETE any tool, script, or MCP server that wraps something the agent can already invoke directly")
- a count of entries in `.claude/rules/known-issues.md` - that file does not exist today and will not exist after the rebuild, since the known-issues rule is deleted and its content folds into the prose. Dead branch.
- file counts in `results/`, `tests/`, `src/` - `results/` is created by the dir-creation `_tasks` step the design is deleting, so that branch goes dead too.

After the rebuild it prints the git root and the branch name. That is not context recovery; it is two lines of noise on every compaction, and hook output is the one way a hook stops being free ([CTX P16]: "A hook that returns chatty output is paying context rent").

**Recommendation.** Delete `seed/.codex/hooks/` and `reassess-hooks.json` outright. `seed/.codex/` becomes `config.toml` + `rules/default.rules`, which is a layer whose every file is real. If the author wants a Codex hooks layer later, [CTX P24] says build it when a hook is actually written.

## E5 - `.mcp.json.jinja` is the biggest unpriced asset in the seed

**Finding.** The target tree records `.mcp.json.jinja  KEEP` with no criterion and no discussion. It ships five MCP servers to every seeded project: `codegraphcontext`, `semble`, `memory`, `drawio`, `sequential-thinking`. Per [CTX P25], MCP "loads tool names at start with schemas deferred" - this is an always-on cost, and the design's own rule 5 says "the always-on layer is priced highest". A five-server tool listing is very plausibly larger than every rule file the document argues about combined.

Two of the five have named native supersessions in the fact sources:

- `memory` (`@modelcontextprotocol/server-memory`) - [CC §"Auto memory"] records that the hand-rolled memory format "is now the *native* format and the harness enforces the index budget itself". [CTX P8]: "DELETE hand-maintained memory scaffolding whose only job is to persist facts the auto-memory layer now captures."
- `sequential-thinking` - a reasoning scratchpad shipped to a Claude 5-generation harness. [CTX P18]: wraps something the model already does.

The other three (`codegraphcontext`, `semble`, `drawio`) are defensible for Samyak's own work but fail [CTX P24] as *template* defaults: nothing names the repeated failure that makes a generic bootstrapped project need a code-graph server, a semantic-search server, and a diagram editor on day one.

**Recommendation.** Delete `memory` and `sequential-thinking` now, on cited grounds. Record an explicit keep-or-cut verdict for the other three rather than a bare `KEEP`; my recommendation is to cut all three and let a project add what it needs, which deletes `.mcp.json.jinja` entirely.

**Knock-on.** `settings.json` currently allows `mcp__sequential-thinking` and asks on `mcp__drawio`. Both permission entries follow whatever this verdict is; leaving them behind would be a new dangling reference of exactly the kind defect 3 catalogues.

## E6 - `verify-template.sh`: check 1 validates zero skills, check 3 lints one file

**Finding A (defect).** Check 1 runs `claude plugin validate` on `seed/.claude`. [CC §"claude plugin validate"] states the tool "does **not** follow symlinks inside the named directory". The seed's only skill is `seed/.claude/skills/catchup`, which under D-5 is a symlink - and per the design it is not even checked into the template. So check 1 validates the seed's hooks and settings and precisely zero skills. The real skill lives at `seed/.agents/skills/catchup/`, which nothing in the design validates.

**Fix:** name `seed/.agents/skills` as an additional validate target.

**Finding B (collapse).** Check 3 absorbs `lint-skill-descriptions.sh` (4.1 KB of shell) to perform "description quality, required `name`, colon quoting" checks. After the rebuild, the seed ships one skill. A 4 KB semantic linter guarding one file is [CTX P23] in its purest form: "DELETE any layer of the harness for which no one can name the outcome it demonstrably improved." The marketplace bundles are a real target for it, but they are validated by check 1 already for parse errors, and the semantic gap ([CC]: `plugin validate` "does not flag a file whose frontmatter parses but has no `name`") is a one-line `grep` per skill, not an absorbed script.

**Finding C.** The design notes that CI has no `claude` CLI, so check 1 always SKIPs in CI. That means the only thing CI actually verifies is check 2 (the copier render) plus the lint. Stating that plainly is better than the current framing, which reads as if CI runs three checks.

**Recommendation.** `bin/verify-template.sh` = the copier scratch render (the one check that is genuinely custom and genuinely load-bearing) plus `claude plugin validate` over `seed/.claude`, `seed/.agents/skills`, and each marketplace bundle, skipped-with-a-visible-line when the CLI is absent. Drop the absorbed semantic lint; revisit it when the seed ships more than one skill. That deletes a script instead of relocating it.

## E7 - Replace the copier `_tasks` symlink step with a checked-in symlink

**Finding.** D-5 fixes that Claude Code reaches catchup through a symlink; it does not fix *how the symlink comes to exist*. The design chooses a guarded `_tasks` command, which costs: one copier task, an idempotency guard, an assertion in `verify-template.sh` check 2, and open assumption 3 ("The copier `_tasks` symlink is safe across `copier update`").

Copier has a documented setting for exactly this, `_preserve_symlinks: true`, which renders checked-in symlinks as symlinks instead of dereferencing them. If it behaves as documented, the symlink is checked into `seed/.claude/skills/catchup`, the task disappears, the guard disappears, the CI assertion becomes "the render produced a symlink" (or disappears), and assumption 3 is closed rather than carried.

**Honesty flag:** copier is not installed in this worktree, so I could not verify the setting's name or default from source. Verify before relying on it:

```
pip install copier && python3 -c "import copier.settings, inspect; print('preserve_symlinks' in inspect.getsource(copier))"
```

or simply add `_preserve_symlinks: true` to `copier.yml`, check the symlink in, and run check 2.

**Caveat that does not change the answer:** symlinks need Administrator or Developer Mode on Windows [CC §"AGENTS.md"]. That is true of the `_tasks` route as well, so it is not a reason to prefer the task.

## E8 - Plugin agents: 8 survivors is still two too many

**Finding.** Four of the eight survivors are "run some commands and report PASS/FAIL" agents. Two of them are worse than redundant:

- `verify-app` and `regression-checker` both key off `.claude/baselines.json`. The seed ships no such file and no way to produce one (I checked: `find seed -name "baselines*"` returns nothing). Both agents are self-documented to report `NO-BASELINE` when it is absent, so in every freshly seeded project they are two agent descriptions burning listing budget to say "I have nothing to compare against". [CTX P24] fires: neither can name the repeated failure in a *bootstrapped* project.
- Their descriptions also overlap each other heavily - both are "compare current state to `.claude/baselines.json`, report PASS/FAIL per check, most severe first". [CTX P14]: "DELETE the weaker of any two skills whose descriptions overlap; overlap degrades selection for both."

`build-validator` ("lint clean, imports, tests collect") is a third member of the same family, and `test-synthesizer` a fourth.

**Recommendation.** Cut `verify-app` and `regression-checker`. If the baseline workflow is genuinely used in Samyak's own repos, keep exactly one of them and ship a `baselines.json` alongside it, because an agent whose contract file never ships is a dangling reference with a model attached. That takes the survivor list to 6 (7 after step 2), and every survivor then names a real, distinct job.

**Also worth checking during execution:** the design's removal table cites native `/simplify` and `/security-review` as superseding `code-simplifier` and `security-scanner`. `consistency-checker` (256 lines) is kept on the grounds that docs-vs-code drift is "explicitly not bundled [CC §10]". That holds - [CC] lists domain rules and provenance tooling as genuinely custom - so I am not contesting it, but it is the longest agent in the set and deserves the [CTX P22] bounded-findings treatment the merged plan-reviewer is getting.

## E9 - `settings.json`: three unrecorded verdicts

The design records one edit (drop the compact hook) and one non-edit (`no skillOverrides`). Three things in the file have no verdict:

1. `"enabledPlugins": {"pyright-lsp": true, "clangd-lsp": true}` - every seeded project gets a C/C++ language server enabled. The current `CLAUDE.md.jinja` even ships a warning that clangd "reports **false** errors on C/C++ ... without a `compile_commands.json`". Shipping a plugin plus a paragraph explaining its false positives is [CTX P24]/[CTX P23]: cut `clangd-lsp` and the paragraph goes with it.
2. `"env": {"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"}` - an experimental flag pinned into every project. Either it is load-bearing (say why) or it is speculative (delete).
3. The `permissions.allow` list pre-approves `cat`, `ls`, `grep`, `head`, `tail`, `sed`, `echo`, `wc`, `mkdir`. Worth a line in the design saying whether that is deliberate policy or leftover, because it is the one part of the seed that changes what the agent may do without asking.

## E10 - Free win: the dead compact hook is itself a gotcha

The design deletes `post-compact-recovery.sh` on the grounds of native supersession [CTX P18]. The stronger fact is that it never ran. `settings.json` wires it as `PostToolUse` with `"matcher": "Compact"`, and [CC §"Hook events"] lists the real event names, which include `PreCompact` and `PostCompact` - `Compact` is not a `PostToolUse` matcher.

Two consequences:

- **Open assumption 2 can be closed, not carried.** The design asks whether native re-injection "fully covers the gotchas' durability need". Since the hook never fired, whatever coverage exists today is already coverage-without-the-hook. Deleting it has provably zero behavioral delta.
- **This belongs in the rewritten gotcha list.** It is the same species as the surviving "hooks receive JSON on stdin, not env vars" entry: a plausible-looking hook wiring that silently never executes. One line: *hook events are exact strings; a wrong event or matcher name fails silently, so verify against the documented event list.* The design's gotcha list has room and this one cost the repo a real, months-long inert hook.

## E11 - Coverage gaps in "a verdict for every asset that exists today"

The document opens with "It records a verdict for every asset that exists today". These exist in the tree with no verdict:

| Path | Note |
|---|---|
| `seed/_research/` (5 empty dirs: `.codex/agents`, `agents`, `hooks`, `rules`, `skills`) | overlay content is gone but the skeleton remains; [R-4] retired the flavor, so delete the dirs |
| `seed/.codex/agents/`, `seed/.codex/mcp/` | empty; `mcp/` is the dangling target of the `[mcp_servers.memory]` block being deleted as defect 3, so it goes with it |
| `seed/.claude/audit.log` | a committed log file inside the rendered seed; excluded by `copier.yml` `_exclude`, so it ships nowhere, but it should not be in the tree |
| `seed/.DS_Store` | same |
| `reassess-bin/__pycache__/` | untracked build artifact next to the scripts being repopulated |
| `reassess-bin/.ip-terms`, `.ip-terms.example` | the ledger keeps these with `ip-sweep.sh`; the design's `bin/` block lists only the four scripts, so the two data files need to move with them or `ip-sweep.sh` arrives broken |
| `cultivation/wip/research-assets/` | [R-4] parked the research assets here "for later use as normal optional assets"; no verdict, no deadline |

`.ip-terms` is the one that can actually break something - verify `ip-sweep.sh` finds its terms file at the new path during step 5.

## E12 - Frame-break, advisory: should `seed/.claude/` be a plugin?

Not a change I am recommending for this rebuild, but the design does not consider it and it is the largest structural simplification available.

D-1 already concluded that the plugin marketplace is the one distribution channel and retired the file-sync engine on that basis. [CC §10] extends the same logic one step further than the design takes it, listing "Copier-based multi-repo distribution" as superseded by "Plugins + marketplaces with release channels and auto-update". Hooks, skills, and agents all ship inside a plugin.

If `seed/.claude/hooks/` and the one skill shipped as a plugin instead of Copier-rendered files, then: hooks update in place across every project instead of freezing at copy time; the catchup symlink problem disappears (plugin skills need no bridge); and `verify-template.sh` check 1 stops needing the "name the real directory, not the symlink" workaround, because there would be no symlinked `.claude` to work around.

What blocks a full move: `settings.json` (`model`, `permissions`, `env`) is not plugin-shippable, so a residual `seed/.claude/settings.json` remains, and the seed still owns the prose files, `pyproject`, and `.gitignore`. So this is a shrink, not an elimination, and it is a scope change beyond the reviewed document. Raising it so the author decides deliberately rather than by omission - and so the next rebuild does not re-derive it.

---

## What I checked and did not fault

- **D-1 (retire agent-sync).** Correct and well-grounded. The engine is ~120 KB of shell plus a test suite serving a loop nobody runs; [CTX P23] and [CC §10] both fire.
- **The `.codex/config.toml` defect list.** Verified against [CDX §2.4] and the file. `max_depth`, `max_threads`, the dangling `mcp_servers.memory`, and the `agent-team` comment are all real. My only addition is E4, which is the same defect class in the file next door.
- **The plan-reviewer merge [R-2] and the removals justified by native `/code-review`, `/simplify`, `/security-review`.** Cleanly grounded in [CC §8] and [CTX P22]; the "adversarial *plan* review has no bundled equivalent" carve-out is directly supported by [CC §10]'s genuinely-custom list.
- **`architecture.md`'s path-scoping cost argument.** The cost argument is correct; I fault the content, not the mechanism (E3).
- **Keeping `release.sh`, `ip-sweep.sh`, `check-own-synthesis.py`.** No native equivalent; [CC §10] agrees.
- **Deleting the dir-creation `_tasks` step.** Correct, and open assumption 4 is sound: copier tasks run on copy/update and do not remove existing directories.

## Priority order for the author

| # | Change | What it deletes |
|---|---|---|
| E4 | Delete `.codex/hooks/` + `hooks.json` instead of renaming | 1 dir, 1 JSON, 4 dangling refs, 1 shipped defect |
| E2 | Gut `AGENTS.md.jinja` to conventions + project-specific constraints | ~110 lines of general competence |
| E1 | One prose source of truth via `@AGENTS.md` | the "must agree" invariant |
| E5 | Price `.mcp.json.jinja`; cut `memory` + `sequential-thinking` at minimum | 2-5 always-on MCP servers |
| E6 | Two-check `verify-template.sh`; add `seed/.agents/skills` as a validate target | 1 absorbed lint script; fixes a check that validates nothing |
| E3 | Delete `rules/architecture.md` | 1 file, 1 directory |
| E8 | Cut `verify-app` + `regression-checker` | 2 agents with a contract file that never ships |
| E7 | `_preserve_symlinks` instead of a `_tasks` step | 1 copier task, 1 guard, 1 open assumption |
| E9 | Record verdicts on `enabledPlugins`, `env`, permissions | likely 1 plugin + 1 flag |
| E10 | Close open assumption 2; add the hook-event gotcha | 1 carried assumption |
| E11 | Cover the unrecorded assets | 8 stray paths; prevents an `ip-sweep.sh` break |

None of these require reversing D-1..D-6 or [R-1..R-7]. E1 is the only one that touches the wording of a session decision, and it has a fallback (delete the "must agree" clause) that does not.

## Verdict

APPROVE_WITH_CHANGES
