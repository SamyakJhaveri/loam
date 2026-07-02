# Visual Overview

Loam is both a Copier template and a Claude Code project: the assets it ships to new
projects are the same assets it runs on itself. This document is a guided tour of the
repo through seven Mermaid diagrams — its dual identity, its layout, the bootstrap and
sync lifecycles, the L0/L1/L2 context-routing model, the 60/30/10 layer triage, and the
session workflow with its Pipeline Gate.

## 1. What is Loam? (dual identity)

Loam ships `seed/` to new projects via Copier, and a `.claude` symlink points back at
`seed/.claude` so the repo runs on the very config it distributes (it dogfoods itself).

```mermaid
flowchart LR
  subgraph LOAM["loam repo"]
    seed["seed/ (deliverables)"]
    cfg[".claude &rarr; seed/.claude"]
  end
  seed -->|"copier copy --trust"| P1["project A"]
  seed -->|"copier copy --trust"| P2["project B"]
  seed -->|"copier copy --trust"| P3["project ..."]
  cfg -. "symlink: repo dogfoods<br/>its own config" .-> LOAM
```

_Source:_ `CLAUDE.md:3` (dual-identity statement); `.claude` symlink target confirmed via `ls -l` (`.claude -> seed/.claude`).

## 2. Repository map

The top-level entries and their one-line purposes, distilled from the Layout table.

```mermaid
flowchart TD
  root["loam repo"]
  root --> seed["seed/<br/>Copier _subdirectory, all deliverables"]
  root --> cult["cultivation/<br/>wip / marketplace / retired skill staging"]
  root --> soil["soil/<br/>local-only knowledge base (gitignored)"]
  root --> docs["docs/<br/>plans / specs"]
  root --> bin["bin/<br/>scripts"]
  root --> arch["_archive/<br/>human-only reference"]
  root --> copier["copier.yml<br/>config"]
  root --> ver["VERSION<br/>semver"]
```

_Source:_ `CLAUDE.md:22-39` (Layout table).

## 3. Bootstrap lifecycle

Running `uvx copier copy --trust` asks three questions, renders `seed/` only, then runs
post-generation `_tasks` in order to leave a ready project. `--trust` is required.

```mermaid
flowchart TD
  start["uvx copier copy --trust"]
  start --> q["3 questions:<br/>project_name / is_research / github_repo"]
  q --> render["render seed/ only<br/>(_subdirectory)"]
  render --> t1["task 1: apply research overlay<br/>if is_research"]
  t1 --> t2["task 2: rm _research +<br/>helper scripts"]
  t2 --> t3["task 3: mkdir working dirs<br/>with .gitkeep"]
  t3 --> t4["task 4: git init + initial commit<br/>(only if no .git)"]
  t4 --> t5["task 5: run _gh_setup.sh<br/>if github_repo set"]
  t5 --> t6["task 6: rm _gh_setup.sh"]
  t6 --> ready["ready project"]
```

_Source:_ `copier.yml:21-37` (questions), `copier.yml:38-65` (task order); `docs/BOOTSTRAP.md:32-50`; `seed/.claude/rules/known-issues.md` (`--trust` gotcha).

## 4. Bidirectional sync + cultivation

Two distinct mechanisms move assets, plus a manual staging step. DOWN pulls template
updates via Copier; UP promotes a project asset back as a branch + PR (never to `main`).

```mermaid
flowchart LR
  tmpl["template seed/"]
  proj["project .claude/"]
  tmpl -->|"DOWN: copier update --trust<br/>(tag-based, three-way merge)"| proj
  proj -->|"UP: template-sync promote<br/>--layer generic or flavor:research<br/>(branch + PR)"| tmpl
  wip["cultivation/wip/"]
  wip -.->|"manual staging (human move)"| skills["seed/.claude/skills/"]
```

_Source:_ `docs/SYNC.md:5-49` (both flows, PR-based promotion, tag-based update); `CLAUDE.md:31` (cultivation staging).

## 5. Context routing (L0/L1/L2)

Three stacked routing layers, each answering one question with its own load timing and
token budget — a map (L0), area routing (L1), and a per-task contract (L2).

```mermaid
flowchart TD
  L0["L0: CLAUDE.md<br/>Where am I?<br/>always loaded &middot; ~800 tok"]
  L1["L1: subdir/CONTEXT.md<br/>Where do I go inside this area?<br/>on entry &middot; ~300 tok"]
  L2["L2: stage contract<br/>What do I do for this task?<br/>per task &middot; 200-500 tok"]
  L0 --> L1
  L1 --> L2
```

_Source:_ `seed/.claude/rules/L0-budget.md` (L0/L1/L2 table — questions, timing, budgets); `context-md-anatomy.md` (L1); `stage-contract.md` (L2).

## 6. 60/30/10 layer triage

Most work should route to deterministic tools or rule-based systems; only a small slice
needs the probabilistic reasoning of an LLM. The decision tree picks the layer.

```mermaid
pie title Where work should be routed
  "Deterministic" : 60
  "Rule-based" : 30
  "Probabilistic" : 10
```

```mermaid
flowchart TD
  q1{"Deterministic transform<br/>of the input?"}
  q1 -->|"yes"| L1["Layer 1<br/>function / tool"]
  q1 -->|"no"| q2{"Existing skill / hook / MCP<br/>handles this?"}
  q2 -->|"yes"| L2["Layer 2<br/>wire it up"]
  q2 -->|"no"| q3{"Cross-source synthesis<br/>or judgment?"}
  q3 -->|"yes"| L3["Layer 3<br/>wrap in stage contract"]
```

_Source:_ `seed/.claude/rules/layer-triage.md` (60/30/10 numbers; three-question routing).

## 7. Session workflow + Pipeline Gate

The 6-stage session workflow ends at Verify, where `/validate` runs as a three-wave
Pipeline Gate. Only after all three waves pass is the commit unblocked.

```mermaid
flowchart TD
  orient["1. Orient"] --> explore["2. Explore"]
  explore --> plan["3. Plan"]
  plan --> impl["4. Implement"]
  impl --> record["5. Record"]
  record --> verify["6. Verify"]

  impl --> validate
  impl -.->|"optional, manual"| crit["/session-critique"]

  subgraph validate["/validate (Pipeline Gate)"]
    w1["Wave 1 Deterministic<br/>ruff / mypy / git diff --check / bash -n"]
    w2["Wave 2 Rule-based<br/>pytest / validators"]
    w1 --> w2
  end

  validate -->|"FAIL"| fix["fix loop (max 3)"]
  fix --> validate
  validate -->|"PASS (waves_passed &gt;= 2)"| sentinel[".validation_passed sentinel"]
  sentinel --> commit["/commit"]
  commit --> pr["/pr"]
```

_Source:_ `seed/.claude/rules/workflow.md` (6 stages, ordering); `validation-loop.md` (wave contents, fix loop max 3, `waves_passed` field); `seed/.claude/hooks/pre-commit-gate.sh:82-88` (`waves_passed >= 2` gate). Deep adversarial review (`/session-critique`) is manual and not part of the gate.
