# Upstream Pocock Skills Replacement + Tool/Plugin Adoption

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace 7 adapted Pocock marketplace skills with upstream originals (keeping only DOMAIN.md rename + auto-activate frontmatter), adopt 2 new upstream skills, pull 4 high-impact reference files, restore cross-skill references — then adopt 9 external tools/plugins into the Loam ecosystem.

**Architecture:** Two independent workstreams executed sequentially. Workstream 1 (Pocock skills) is file replacement with targeted adaptation. Workstream 2 (tool adoption) creates new marketplace bundles, wires MCP servers, and documents external plugins. Run `/compact` between workstreams.

**Tech Stack:** Copier template (Jinja2), Claude Code plugin/skill format, MCP server config (`.mcp.json.jinja`)

---

## Pre-Flight

Before starting any task, verify the workspace:

```bash
cd /Users/samyakjhaveri/Desktop/loam
git status  # should be on main, clean working tree
ls cultivation/marketplace/pocock-engineering/skills/  # 7 skill dirs
cat cultivation/marketplace/pocock-engineering/.claude-plugin/plugin.json
```

---

## WORKSTREAM 1: Pocock Skills Upstream Replacement

### Design Decisions (already made)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| CONTEXT.md vs DOMAIN.md | **Keep DOMAIN.md rename** | Loam uses CONTEXT.md for ICM L1 routing (different purpose) |
| Reference files | **Pull 4 high-impact only**: AGENT-BRIEF.md, LOGIC.md, UI.md, DEEPENING.md | Balance upstream faithfulness vs. file count |
| New skills | **Adopt both** to-prd and zoom-out | to-prd complements gen-spec; zoom-out fills micro-skill gap |
| Cross-references | **Restore** | All skills ship together in the bundle |
| SKILL.md replacement | **Replace all 7** with upstream originals | Only apply: DOMAIN.md rename, `auto-activate: false` frontmatter, restore cross-refs using `/skill-name` format |

### Adaptation Rules (apply to EVERY upstream file)

When replacing or adding a file, apply these and ONLY these changes to the upstream original:

1. **DOMAIN.md rename**: Replace ALL occurrences of `CONTEXT.md` with `DOMAIN.md`, `CONTEXT-FORMAT.md` with `DOMAIN-FORMAT.md`, `CONTEXT-MAP.md` with `DOMAIN-MAP.md`
2. **Frontmatter**: Add `auto-activate: false` after the description line
3. **Remove setup refs**: Remove any mention of `/setup-matt-pocock-skills` (not adopted)
4. **Restore cross-refs**: Keep references to other Pocock skills (e.g., `/grill-with-docs`, `/improve-codebase-architecture`) — they all ship together
5. **DO NOT**: Rewrite structure, add phases, add NOT-for clauses, add Loam workflow integration, condense prose, or make any other changes

---

### Task 1: Fetch All Upstream Skill Files

**Files:** No local files modified yet — this is a fetch-and-stage step.

The upstream repository is `mattpocock/skills`. All engineering skills live at:
`https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/<skill>/<file>`

- [ ] **Step 1: Fetch all 7 adopted SKILL.md files from upstream**

```bash
cd /Users/samyakjhaveri/Desktop/loam
mkdir -p /tmp/pocock-upstream

# Fetch all 7 adopted skills
for skill in triage to-issues grill-with-docs improve-codebase-architecture tdd prototype diagnose; do
  mkdir -p /tmp/pocock-upstream/$skill
  curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/$skill/SKILL.md" \
    -o /tmp/pocock-upstream/$skill/SKILL.md
  echo "Fetched $skill/SKILL.md ($(wc -l < /tmp/pocock-upstream/$skill/SKILL.md) lines)"
done
```

Expected: 7 SKILL.md files downloaded, each 50-140 lines.

- [ ] **Step 2: Fetch 4 high-impact reference files**

```bash
# triage/AGENT-BRIEF.md
curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/triage/AGENT-BRIEF.md" \
  -o /tmp/pocock-upstream/triage/AGENT-BRIEF.md

# prototype/LOGIC.md and UI.md
curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/prototype/LOGIC.md" \
  -o /tmp/pocock-upstream/prototype/LOGIC.md
curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/prototype/UI.md" \
  -o /tmp/pocock-upstream/prototype/UI.md

# improve-codebase-architecture/DEEPENING.md
curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/improve-codebase-architecture/DEEPENING.md" \
  -o /tmp/pocock-upstream/improve-codebase-architecture/DEEPENING.md

# Verify all fetched
for f in triage/AGENT-BRIEF.md prototype/LOGIC.md prototype/UI.md improve-codebase-architecture/DEEPENING.md; do
  echo "$f: $(wc -l < /tmp/pocock-upstream/$f) lines"
done
```

Expected: 4 reference files downloaded (~100-120 lines each).

- [ ] **Step 3: Fetch existing reference files that may have upstream updates**

```bash
# grill-with-docs reference files (upstream uses CONTEXT-FORMAT.md, we have DOMAIN-FORMAT.md)
curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/grill-with-docs/CONTEXT-FORMAT.md" \
  -o /tmp/pocock-upstream/grill-with-docs/CONTEXT-FORMAT.md
curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/grill-with-docs/ADR-FORMAT.md" \
  -o /tmp/pocock-upstream/grill-with-docs/ADR-FORMAT.md

# improve-codebase-architecture reference files
for f in LANGUAGE.md HTML-REPORT.md INTERFACE-DESIGN.md; do
  curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/improve-codebase-architecture/$f" \
    -o /tmp/pocock-upstream/improve-codebase-architecture/$f
done

echo "All existing reference files fetched"
```

- [ ] **Step 4: Fetch 2 new skills (to-prd, zoom-out)**

```bash
for skill in to-prd zoom-out; do
  mkdir -p /tmp/pocock-upstream/$skill
  curl -sL "https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/$skill/SKILL.md" \
    -o /tmp/pocock-upstream/$skill/SKILL.md
  echo "Fetched $skill/SKILL.md ($(wc -l < /tmp/pocock-upstream/$skill/SKILL.md) lines)"
done
```

- [ ] **Step 5: Verify all fetches — no empty/404 files**

```bash
echo "=== File inventory ==="
find /tmp/pocock-upstream -type f | sort | while read f; do
  lines=$(wc -l < "$f")
  if [ "$lines" -eq 0 ]; then
    echo "EMPTY (possible 404): $f"
  else
    echo "OK ($lines lines): $f"
  fi
done
```

Expected: All files show "OK" with non-zero line counts. If any show EMPTY, the upstream path may have changed — check `https://github.com/mattpocock/skills/tree/main/skills/engineering` for the current structure and adjust the URL accordingly.

---

### Task 2: Replace 7 Adopted SKILL.md Files

For each skill, read the upstream file from `/tmp/pocock-upstream/`, apply the 5 adaptation rules, and write to the local marketplace path.

**Files to modify (all under `cultivation/marketplace/pocock-engineering/skills/`):**
- `triage/SKILL.md` (replace)
- `to-issues/SKILL.md` (replace)
- `grill-with-docs/SKILL.md` (replace)
- `improve-codebase-architecture/SKILL.md` (replace)
- `tdd/SKILL.md` (replace)
- `prototype/SKILL.md` (replace)
- `diagnose/SKILL.md` (replace)

- [ ] **Step 1: Replace triage/SKILL.md**

Read `/tmp/pocock-upstream/triage/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Remove any `/setup-matt-pocock-skills` references
3. Keep `/grill-with-docs` cross-reference (it ships in the bundle)
4. Replace `CONTEXT.md` → `DOMAIN.md` if present
5. Write to `cultivation/marketplace/pocock-engineering/skills/triage/SKILL.md`

- [ ] **Step 2: Replace to-issues/SKILL.md**

Read `/tmp/pocock-upstream/to-issues/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Remove any `/setup-matt-pocock-skills` references
3. Replace `CONTEXT.md` → `DOMAIN.md`, `CONTEXT-FORMAT.md` → `DOMAIN-FORMAT.md`
4. Keep cross-references to other Pocock skills
5. Write to `cultivation/marketplace/pocock-engineering/skills/to-issues/SKILL.md`

- [ ] **Step 3: Replace grill-with-docs/SKILL.md**

Read `/tmp/pocock-upstream/grill-with-docs/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Replace ALL `CONTEXT.md` → `DOMAIN.md`, `CONTEXT-FORMAT.md` → `DOMAIN-FORMAT.md`, `CONTEXT-MAP.md` → `DOMAIN-MAP.md`
3. Remove any `/setup-matt-pocock-skills` references
4. Write to `cultivation/marketplace/pocock-engineering/skills/grill-with-docs/SKILL.md`

- [ ] **Step 4: Replace improve-codebase-architecture/SKILL.md**

Read `/tmp/pocock-upstream/improve-codebase-architecture/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Replace `CONTEXT.md` → `DOMAIN.md`, `CONTEXT-FORMAT.md` → `DOMAIN-FORMAT.md`
3. Keep `/grill-with-docs` cross-reference
4. Write to `cultivation/marketplace/pocock-engineering/skills/improve-codebase-architecture/SKILL.md`

- [ ] **Step 5: Replace tdd/SKILL.md**

Read `/tmp/pocock-upstream/tdd/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Replace `CONTEXT.md` → `DOMAIN.md` if present
3. Keep references to local reference files (tests.md, mocking.md, etc.) — even though we're not pulling them all, the references are harmless and signal what exists upstream
4. Write to `cultivation/marketplace/pocock-engineering/skills/tdd/SKILL.md`

- [ ] **Step 6: Replace prototype/SKILL.md**

Read `/tmp/pocock-upstream/prototype/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Keep references to LOGIC.md and UI.md (we're adding those)
3. Write to `cultivation/marketplace/pocock-engineering/skills/prototype/SKILL.md`

- [ ] **Step 7: Replace diagnose/SKILL.md**

Read `/tmp/pocock-upstream/diagnose/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Replace `CONTEXT.md` → `DOMAIN.md` if present
3. Keep `/improve-codebase-architecture` cross-reference (Phase 6 handoff)
4. Write to `cultivation/marketplace/pocock-engineering/skills/diagnose/SKILL.md`

- [ ] **Step 8: Verify all 7 replacements**

```bash
cd /Users/samyakjhaveri/Desktop/loam
for skill in triage to-issues grill-with-docs improve-codebase-architecture tdd prototype diagnose; do
  file="cultivation/marketplace/pocock-engineering/skills/$skill/SKILL.md"
  lines=$(wc -l < "$file")
  has_auto=$(grep -c "auto-activate: false" "$file")
  has_setup=$(grep -c "setup-matt-pocock-skills" "$file")
  has_context_md=$(grep -c "CONTEXT\.md" "$file")
  echo "$skill: ${lines}L, auto-activate=${has_auto}, setup-refs=${has_setup}, CONTEXT.md-refs=${has_context_md}"
done
```

Expected for each: `auto-activate=1`, `setup-refs=0`, `CONTEXT.md-refs=0`.

---

### Task 3: Add 4 High-Impact Reference Files

**Files to create:**
- `cultivation/marketplace/pocock-engineering/skills/triage/AGENT-BRIEF.md` (new)
- `cultivation/marketplace/pocock-engineering/skills/prototype/LOGIC.md` (new)
- `cultivation/marketplace/pocock-engineering/skills/prototype/UI.md` (new)
- `cultivation/marketplace/pocock-engineering/skills/improve-codebase-architecture/DEEPENING.md` (new)

- [ ] **Step 1: Copy AGENT-BRIEF.md to triage/**

Read `/tmp/pocock-upstream/triage/AGENT-BRIEF.md`. Apply DOMAIN.md rename if it contains CONTEXT.md references. Write to `cultivation/marketplace/pocock-engineering/skills/triage/AGENT-BRIEF.md`.

- [ ] **Step 2: Copy LOGIC.md and UI.md to prototype/**

Read `/tmp/pocock-upstream/prototype/LOGIC.md`. No CONTEXT.md references expected — copy as-is to `cultivation/marketplace/pocock-engineering/skills/prototype/LOGIC.md`.

Read `/tmp/pocock-upstream/prototype/UI.md`. Copy as-is to `cultivation/marketplace/pocock-engineering/skills/prototype/UI.md`.

- [ ] **Step 3: Copy DEEPENING.md to improve-codebase-architecture/**

Read `/tmp/pocock-upstream/improve-codebase-architecture/DEEPENING.md`. Apply DOMAIN.md rename if needed. Write to `cultivation/marketplace/pocock-engineering/skills/improve-codebase-architecture/DEEPENING.md`.

- [ ] **Step 4: Update existing reference files from upstream**

For these files that ALREADY exist locally, compare the upstream version against local. If upstream has meaningful changes, update the local version (applying DOMAIN.md rename):

- `grill-with-docs/DOMAIN-FORMAT.md` ← compare against upstream `CONTEXT-FORMAT.md`
- `grill-with-docs/ADR-FORMAT.md` ← compare against upstream `ADR-FORMAT.md`
- `improve-codebase-architecture/LANGUAGE.md` ← compare against upstream
- `improve-codebase-architecture/HTML-REPORT.md` ← compare against upstream
- `improve-codebase-architecture/INTERFACE-DESIGN.md` ← compare against upstream (add DEEPENING.md reference back)

For each: diff the upstream against local. If the upstream has new content (not just formatting), update the local file with the upstream content, applying the DOMAIN.md rename.

- [ ] **Step 5: Verify reference files**

```bash
cd /Users/samyakjhaveri/Desktop/loam
echo "=== New reference files ==="
for f in triage/AGENT-BRIEF.md prototype/LOGIC.md prototype/UI.md improve-codebase-architecture/DEEPENING.md; do
  path="cultivation/marketplace/pocock-engineering/skills/$f"
  if [ -f "$path" ]; then
    echo "OK: $f ($(wc -l < "$path") lines)"
  else
    echo "MISSING: $f"
  fi
done

echo "=== Existing reference files ==="
for f in grill-with-docs/DOMAIN-FORMAT.md grill-with-docs/ADR-FORMAT.md improve-codebase-architecture/LANGUAGE.md improve-codebase-architecture/HTML-REPORT.md improve-codebase-architecture/INTERFACE-DESIGN.md; do
  path="cultivation/marketplace/pocock-engineering/skills/$f"
  echo "$f: $(wc -l < "$path") lines"
done
```

Expected: All files present, non-zero lines.

---

### Task 4: Adopt to-prd and zoom-out

**Files to create:**
- `cultivation/marketplace/pocock-engineering/skills/to-prd/SKILL.md` (new directory + file)
- `cultivation/marketplace/pocock-engineering/skills/zoom-out/SKILL.md` (new directory + file)

- [ ] **Step 1: Create to-prd skill**

```bash
mkdir -p cultivation/marketplace/pocock-engineering/skills/to-prd
```

Read `/tmp/pocock-upstream/to-prd/SKILL.md`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Remove `/setup-matt-pocock-skills` references
3. Replace `CONTEXT.md` → `DOMAIN.md` if present
4. Keep cross-references to other Pocock skills (e.g., domain glossary)
5. Write to `cultivation/marketplace/pocock-engineering/skills/to-prd/SKILL.md`

- [ ] **Step 2: Create zoom-out skill**

```bash
mkdir -p cultivation/marketplace/pocock-engineering/skills/zoom-out
```

Read `/tmp/pocock-upstream/zoom-out/SKILL.md`. This is an 8-line micro-skill with `disable-model-invocation: true`. Apply adaptations:
1. Add `auto-activate: false` after description in frontmatter
2. Replace "domain glossary" with "domain glossary (DOMAIN.md)" if appropriate
3. Write to `cultivation/marketplace/pocock-engineering/skills/zoom-out/SKILL.md`

- [ ] **Step 3: Update plugin.json to include new skills**

Modify: `cultivation/marketplace/pocock-engineering/.claude-plugin/plugin.json`

Update the description to include the 2 new skills. The new description should be:

```json
{
  "name": "pocock-engineering",
  "version": "0.2.0",
  "description": "Engineering workflow skills from Matt Pocock's skills repo (triage, to-issues, to-prd, tdd, prototype, diagnose, grill-with-docs, improve-codebase-architecture, zoom-out). Covers issue lifecycle, TDD, prototyping, architectural review, domain grilling, and PRD generation. NOT for: daily development workflow — install individual skills as needed.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 4: Verify new skills**

```bash
cd /Users/samyakjhaveri/Desktop/loam
ls cultivation/marketplace/pocock-engineering/skills/to-prd/SKILL.md
ls cultivation/marketplace/pocock-engineering/skills/zoom-out/SKILL.md
grep "auto-activate: false" cultivation/marketplace/pocock-engineering/skills/to-prd/SKILL.md
grep "disable-model-invocation" cultivation/marketplace/pocock-engineering/skills/zoom-out/SKILL.md
grep "to-prd" cultivation/marketplace/pocock-engineering/.claude-plugin/plugin.json
```

Expected: Both files exist. to-prd has auto-activate. zoom-out has disable-model-invocation. plugin.json lists to-prd.

---

### Task 5: Update Marketplace README

**File to modify:** `cultivation/marketplace/README.md`

- [ ] **Step 1: Update pocock-engineering entry in the Bundles table**

Find the `pocock-engineering` row in the Bundles table. Update it to:

```markdown
| `pocock-engineering` | triage, to-issues, to-prd, tdd, prototype, diagnose, grill-with-docs, improve-codebase-architecture, zoom-out | Engineering workflow skills from [mattpocock/skills](https://github.com/mattpocock/skills) — issue lifecycle, TDD, prototyping, architectural review, domain grilling, PRD generation |
```

- [ ] **Step 2: Verify**

```bash
grep "to-prd" cultivation/marketplace/README.md
grep "zoom-out" cultivation/marketplace/README.md
```

---

### Task 6: Workstream 1 Verification

- [ ] **Step 1: Full file inventory**

```bash
cd /Users/samyakjhaveri/Desktop/loam
echo "=== Pocock Engineering Skills ==="
find cultivation/marketplace/pocock-engineering/skills -type f | sort
echo ""
echo "=== Expected: 9 skill dirs, each with SKILL.md, some with reference files ==="
echo "=== Total skill dirs: $(ls -d cultivation/marketplace/pocock-engineering/skills/*/ | wc -l) ==="
```

Expected: 9 skill directories (triage, to-issues, to-prd, tdd, prototype, diagnose, grill-with-docs, improve-codebase-architecture, zoom-out).

- [ ] **Step 2: Adaptation compliance check**

```bash
cd /Users/samyakjhaveri/Desktop/loam

echo "=== Checking auto-activate: false in all SKILL.md files ==="
for f in cultivation/marketplace/pocock-engineering/skills/*/SKILL.md; do
  skill=$(basename $(dirname "$f"))
  has_auto=$(grep -c "auto-activate: false" "$f")
  echo "$skill: auto-activate=$has_auto"
done

echo ""
echo "=== Checking NO setup-matt-pocock-skills references ==="
grep -r "setup-matt-pocock-skills" cultivation/marketplace/pocock-engineering/skills/ || echo "CLEAN: no setup refs"

echo ""
echo "=== Checking NO CONTEXT.md references (should all be DOMAIN.md) ==="
grep -rn "CONTEXT\.md" cultivation/marketplace/pocock-engineering/skills/ || echo "CLEAN: no CONTEXT.md refs"

echo ""
echo "=== Checking cross-refs exist ==="
grep -rn "grill-with-docs\|improve-codebase-architecture\|/diagnose\|/triage" cultivation/marketplace/pocock-engineering/skills/ | head -10
echo "(should see cross-skill references)"
```

Expected: All auto-activate=1 (except zoom-out which uses `disable-model-invocation: true`). Zero setup refs. Zero CONTEXT.md refs. Some cross-refs present.

- [ ] **Step 3: Run template verifier**

```bash
bin/verify-template.sh
```

Expected: ALL OK.

- [ ] **Step 4: Commit Workstream 1**

```bash
git add cultivation/marketplace/pocock-engineering/
git add cultivation/marketplace/README.md
git status
```

Use `/commit` skill with message: `feat(marketplace): replace pocock skills with upstream originals + adopt to-prd, zoom-out`

---

## `/compact` — Clear context before Workstream 2

Run `/compact "Focus on Workstream 2: tool and plugin adoption into cultivation/marketplace/"` to free context for the second workstream.

---

## WORKSTREAM 2: Tool and Plugin Adoption

### Integration Strategy by Tool Type

Each tool has a different integration path based on how it's built:

| Tool | Type | Integration Path |
|------|------|-----------------|
| code-review-graph | MCP server | Wire into `.mcp.json.jinja` as optional + marketplace docs |
| planning-with-files | Claude Code skill | Create marketplace bundle |
| Understand-Anything | Claude Code plugin | Create marketplace bundle |
| UI-UX Pro Max | Claude Code skill | Create marketplace bundle |
| Impeccable | Claude Code skill+CLI | Create marketplace bundle |
| STORM | Python package | Research-flavor docs + optional wrapper |
| GPT-Researcher | MCP server | Wire into `.mcp.json.jinja` (research flavor) + marketplace docs |
| academic-research-skills | Claude Code plugin | Create marketplace bundle |
| nature-skills | Claude Code plugin | Create marketplace bundle |

### How Marketplace Bundles Work in Loam

Each bundle lives at `cultivation/marketplace/<bundle-name>/` with:
```
<bundle-name>/
├── .claude-plugin/
│   └── plugin.json          # name, version, description, author
└── skills/
    └── <skill-name>/
        └── SKILL.md          # the skill definition
```

For tools that are external plugins (with their own install mechanisms), we create a lightweight bundle that:
1. Contains a SKILL.md that acts as a **wrapper/installer** pointing to the external tool
2. Documents how to install and use the external tool
3. Provides any Loam-specific configuration or integration notes

---

### Task 7: code-review-graph (MCP Server)

**Repo:** https://github.com/tirth8205/code-review-graph
**What:** Tree-sitter AST graph → blast-radius analysis for code review. 24-language support.
**Integration:** MCP server (28 tools). Python 3.10+.
**Stars:** 17.3k | **License:** MIT | **Last active:** May 16, 2026

**Files to create/modify:**
- Create: `cultivation/marketplace/code-review-graph/.claude-plugin/plugin.json`
- Create: `cultivation/marketplace/code-review-graph/skills/code-review-graph/SKILL.md`
- Create: `cultivation/marketplace/code-review-graph/README.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p cultivation/marketplace/code-review-graph/.claude-plugin
mkdir -p cultivation/marketplace/code-review-graph/skills/code-review-graph
```

- [ ] **Step 2: Create plugin.json**

Write `cultivation/marketplace/code-review-graph/.claude-plugin/plugin.json`:

```json
{
  "name": "code-review-graph",
  "version": "0.1.0",
  "description": "GraphRAG-powered code review via Tree-sitter AST analysis. Blast-radius scoping for diffs, architectural hotspot detection. Recommended for 500+ file codebases. Requires Python 3.10+. NOT for: small projects — graph overhead exceeds savings below ~200 files.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md**

Fetch the upstream README for accurate install/usage instructions:
```bash
curl -sL "https://raw.githubusercontent.com/tirth8205/code-review-graph/main/README.md" -o /tmp/code-review-graph-readme.md
```

Write `cultivation/marketplace/code-review-graph/skills/code-review-graph/SKILL.md` — a wrapper skill that documents how to install and use code-review-graph. Include:
- Frontmatter with `auto-activate: false`
- Install instructions (pip install, MCP server setup)
- How it complements Loam's `/multi-review` (blast-radius scoping → multi-review quality analysis)
- MCP server config snippet for `.mcp.json`

- [ ] **Step 4: Create README.md**

Write `cultivation/marketplace/code-review-graph/README.md` with:
- What it does (1-2 sentences)
- Install instructions
- How to wire into a project's `.mcp.json`
- Link to upstream repo
- Note: "Recommended for 500+ file codebases"

- [ ] **Step 5: Verify**

```bash
ls -la cultivation/marketplace/code-review-graph/
cat cultivation/marketplace/code-review-graph/.claude-plugin/plugin.json | python3 -m json.tool
```

---

### Task 8: planning-with-files (Claude Code Skill)

**Repo:** https://github.com/othmanadi/planning-with-files
**What:** Persistent markdown planning files (task_plan.md, findings.md, progress.md) with lifecycle hooks.
**Integration:** Claude Code skill/plugin via `npx skills add`.
**Stars:** 21.9k | **License:** MIT | **Last active:** May 22, 2026

**Files to create:**
- `cultivation/marketplace/planning-with-files/.claude-plugin/plugin.json`
- `cultivation/marketplace/planning-with-files/skills/planning-with-files/SKILL.md`
- `cultivation/marketplace/planning-with-files/README.md`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p cultivation/marketplace/planning-with-files/.claude-plugin
mkdir -p cultivation/marketplace/planning-with-files/skills/planning-with-files
```

- [ ] **Step 2: Fetch upstream and create plugin.json**

```bash
curl -sL "https://raw.githubusercontent.com/othmanadi/planning-with-files/main/README.md" -o /tmp/planning-with-files-readme.md
```

Write `cultivation/marketplace/planning-with-files/.claude-plugin/plugin.json`:

```json
{
  "name": "planning-with-files",
  "version": "0.1.0",
  "description": "Manus-style persistent markdown planning. Creates task_plan.md, findings.md, progress.md for cross-session persistence. Hook-based re-injection after /compact. NOTE: overlaps with Loam's feature-dev, plan mode, and handoff skills — install only if you prefer file-based planning over Loam's built-in approach.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md**

Write a wrapper SKILL.md that:
- Documents what planning-with-files does
- How to install from the upstream repo (`npx skills add planning-with-files` or manual clone)
- Notes overlap with Loam's existing planning infrastructure
- Has `auto-activate: false`

- [ ] **Step 4: Create README.md and verify**

Same pattern as Task 7. Include overlap warning with Loam's existing tools.

```bash
ls -la cultivation/marketplace/planning-with-files/
```

---

### Task 9: Understand-Anything (Claude Code Plugin)

**Repo:** https://github.com/Lum1104/Understand-Anything
**What:** Multi-agent codebase analysis → interactive React knowledge graph dashboard.
**Integration:** Claude Code plugin (marketplace). Commands: /understand, /understand-dashboard, /understand-chat, /understand-diff, /understand-domain.
**Stars:** 21.3k | **License:** MIT | **Last active:** May 23, 2026 (today)

**Files to create:**
- `cultivation/marketplace/understand-anything/.claude-plugin/plugin.json`
- `cultivation/marketplace/understand-anything/skills/understand-anything/SKILL.md`
- `cultivation/marketplace/understand-anything/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/understand-anything/.claude-plugin
mkdir -p cultivation/marketplace/understand-anything/skills/understand-anything
curl -sL "https://raw.githubusercontent.com/Lum1104/Understand-Anything/main/README.md" -o /tmp/understand-anything-readme.md
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "understand-anything",
  "version": "0.1.0",
  "description": "Multi-agent codebase analysis pipeline with interactive React knowledge graph dashboard. Commands: /understand, /understand-dashboard, /understand-chat, /understand-diff, /understand-domain. NOTE: overlaps with Semble + CodeGraphContext — best for onboarding and visual architecture exploration. LLM cost during initial scan.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md and README.md, verify**

Same pattern. Note overlap with Semble + CodeGraphContext. Document the `/understand-*` commands. `auto-activate: false`.

```bash
ls -la cultivation/marketplace/understand-anything/
```

---

### Task 10: UI-UX Pro Max (Claude Code Skill)

**Repo/Source:** https://www.claudepluginhub.com/plugins/nextlevelbuilder-ui-ux-pro-max
**What:** Design system generator with 161 color palettes, 57 font pairings, 67 UI styles, 161 product-type rules, 99 UX guidelines across 10 tech stacks.
**Integration:** Claude Code skill (installs to `.claude/skills/`). Also CLI: `npm install -g uipro-cli`.
**Stars:** 82k (verify — may be inflated) | **License:** MIT | **Last active:** April 2026

**Files to create:**
- `cultivation/marketplace/ui-ux-pro-max/.claude-plugin/plugin.json`
- `cultivation/marketplace/ui-ux-pro-max/skills/ui-ux-pro-max/SKILL.md`
- `cultivation/marketplace/ui-ux-pro-max/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/ui-ux-pro-max/.claude-plugin
mkdir -p cultivation/marketplace/ui-ux-pro-max/skills/ui-ux-pro-max
```

Fetch the Plugin Hub page for install instructions:
```bash
curl -sL "https://www.claudepluginhub.com/plugins/nextlevelbuilder-ui-ux-pro-max" -o /tmp/ui-ux-pro-max-page.html
```

Also try fetching from what appears to be the GitHub source (search for it):
```bash
# Try common GitHub locations
curl -sL "https://api.github.com/search/repositories?q=ui-ux-pro-max+claude" -o /tmp/ui-ux-search.json
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "ui-ux-pro-max",
  "version": "0.1.0",
  "description": "Design system generator with curated palettes, font pairings, UI styles, and UX guidelines. Installs via Claude Plugin Hub or npm (uipro-cli). Frontend-focused — install for web/mobile UI projects. NOT for: backend-only or CLI projects.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md and README.md, verify**

Document install methods (Plugin Hub marketplace add, npm global). Note: star count (82k) may be inflated — this is from Claude Plugin Hub, not a traditional GitHub project. `auto-activate: false`.

```bash
ls -la cultivation/marketplace/ui-ux-pro-max/
```

---

### Task 11: Impeccable (Claude Code Skill + CLI)

**Repo/Source:** https://www.claudepluginhub.com/plugins/pbakaus-impeccable
**What:** Hybrid design skill — 27 deterministic anti-pattern rules (CLI: `npx impeccable detect`) + 12-rule LLM critique. Created by Paul Bakaus (jQuery UI creator).
**Integration:** Claude Code skill + CLI + browser extension.
**Stars:** 29.7k | **License:** Apache-2.0 | **Last active:** May 22, 2026 (yesterday)

**Files to create:**
- `cultivation/marketplace/impeccable/.claude-plugin/plugin.json`
- `cultivation/marketplace/impeccable/skills/impeccable/SKILL.md`
- `cultivation/marketplace/impeccable/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/impeccable/.claude-plugin
mkdir -p cultivation/marketplace/impeccable/skills/impeccable
```

Search for the actual GitHub repo:
```bash
# Impeccable by Paul Bakaus — likely has a GitHub repo
curl -sL "https://api.github.com/search/repositories?q=impeccable+pbakaus" -o /tmp/impeccable-search.json
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "impeccable",
  "version": "0.1.0",
  "description": "Design polish with 27 deterministic anti-pattern rules + 12-rule LLM critique. By Paul Bakaus (jQuery UI creator). Commands: polish, audit, critique, typeset, animate, colorize, layout, delight. Detects AI-generated design fingerprints. Apache-2.0. NOT for: backend-only projects.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md and README.md, verify**

Document: CLI detection mode (`npx impeccable detect`), two modes (brand vs product), install methods. Note: strongest design tool evaluated — deterministic rules align with Loam's 60/30/10 layer triage. `auto-activate: false`.

```bash
ls -la cultivation/marketplace/impeccable/
```

---

### Task 12: STORM (Python Package — Research Tool)

**Repo:** https://github.com/stanford-oval/storm
**What:** Stanford's LLM-powered research pipeline — Wikipedia-quality articles with citations. Multi-perspective research, Co-STORM collaborative mode.
**Integration:** Python package (`pip install knowledge-storm`). No MCP server. No Claude Code skill.
**Stars:** 28.3k | **License:** MIT | **Last active:** Sept 2025 (8 months ago)
**Claude support:** YES — has `ClaudeModel` class in `knowledge_storm/lm.py`.

**Files to create:**
- `cultivation/marketplace/storm-research/.claude-plugin/plugin.json`
- `cultivation/marketplace/storm-research/skills/storm-research/SKILL.md`
- `cultivation/marketplace/storm-research/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/storm-research/.claude-plugin
mkdir -p cultivation/marketplace/storm-research/skills/storm-research
curl -sL "https://raw.githubusercontent.com/stanford-oval/storm/main/README.md" -o /tmp/storm-readme.md
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "storm-research",
  "version": "0.1.0",
  "description": "Stanford STORM — LLM research pipeline for Wikipedia-quality articles with citations. Multi-perspective research, Co-STORM collaborative mode. Requires Python + search engine API key. Research-flavor tool — complements /researcher with systematic literature review. NOT for: quick lookups (use /researcher) or non-research projects.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md**

This SKILL.md should be more detailed since STORM has no native Claude Code integration. Include:
- Install: `pip install knowledge-storm`
- Python API usage with Claude (`ClaudeModel` class)
- Required API keys (ANTHROPIC_API_KEY + search engine: Bing/You.com/Serper/Brave/Tavily)
- Example invocation
- Co-STORM collaborative mode instructions
- `auto-activate: false`

- [ ] **Step 4: Create README.md and verify**

```bash
ls -la cultivation/marketplace/storm-research/
```

---

### Task 13: GPT-Researcher (MCP Server)

**Repo:** https://github.com/assafelovic/gpt-researcher
**MCP Server:** https://github.com/assafelovic/gptr-mcp (separate repo, 346 stars, v0.0.1)
**What:** Autonomous multi-source research agent with planner/executor architecture.
**Integration:** MCP server (5 tools: deep_research, quick_search, write_report, get_research_sources, get_research_context). Also Claude Code skill via `npx skills add`.
**Stars:** 27.2k | **License:** Apache-2.0 | **Last active:** April 2026
**Claude support:** YES — native Anthropic provider (`FAST_LLM=anthropic:claude-*`)
**API keys needed:** Tavily (search) + Anthropic + embedding provider (3 keys minimum)

**Files to create:**
- `cultivation/marketplace/gpt-researcher/.claude-plugin/plugin.json`
- `cultivation/marketplace/gpt-researcher/skills/gpt-researcher/SKILL.md`
- `cultivation/marketplace/gpt-researcher/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/gpt-researcher/.claude-plugin
mkdir -p cultivation/marketplace/gpt-researcher/skills/gpt-researcher
curl -sL "https://raw.githubusercontent.com/assafelovic/gpt-researcher/master/README.md" -o /tmp/gpt-researcher-readme.md
curl -sL "https://raw.githubusercontent.com/assafelovic/gptr-mcp/main/README.md" -o /tmp/gptr-mcp-readme.md
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "gpt-researcher",
  "version": "0.1.0",
  "description": "Autonomous multi-source research agent with MCP server integration. Planner/executor architecture, parallel source gathering. Requires 3 API keys (Tavily + Anthropic + embeddings). MCP server is v0.0.1 — expect rough edges. Research-flavor tool. NOT for: quick searches (use /researcher) or non-research projects.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md with MCP config**

Include MCP server configuration snippet:
```json
{
  "gpt-researcher": {
    "type": "stdio",
    "command": "uvx",
    "args": ["gptr-mcp"],
    "env": {
      "TAVILY_API_KEY": "<your-key>",
      "ANTHROPIC_API_KEY": "<your-key>",
      "FAST_LLM": "anthropic:claude-sonnet-4-6",
      "SMART_LLM": "anthropic:claude-opus-4-6"
    }
  }
}
```

Document the 5 MCP tools: deep_research, quick_search, write_report, get_research_sources, get_research_context. Note: MCP server is from separate repo (`gptr-mcp`), v0.0.1. `auto-activate: false`.

- [ ] **Step 4: Create README.md and verify**

```bash
ls -la cultivation/marketplace/gpt-researcher/
```

---

### Task 14: academic-research-skills (Claude Code Plugin)

**Repo:** https://github.com/imbad0202/academic-research-skills
**What:** 4-skill academic pipeline — deep research (13-agent team), academic paper (12-agent pipeline with LaTeX), peer review (7-agent multi-perspective), pipeline orchestrator (10-stage).
**Integration:** Claude Code plugin (`/plugin marketplace add`). 10 slash commands (`/ars-*`), 3 agents.
**Stars:** 19.7k | **License:** CC BY-NC 4.0 | **Last active:** May 18, 2026 (v3.9.2)
**Dependencies:** Python, optional Pandoc + Tectonic (LaTeX). Optional API keys: Semantic Scholar, OpenAlex, Crossref.

**Files to create:**
- `cultivation/marketplace/academic-research/.claude-plugin/plugin.json`
- `cultivation/marketplace/academic-research/skills/academic-research/SKILL.md`
- `cultivation/marketplace/academic-research/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/academic-research/.claude-plugin
mkdir -p cultivation/marketplace/academic-research/skills/academic-research
curl -sL "https://raw.githubusercontent.com/imbad0202/academic-research-skills/main/README.md" -o /tmp/academic-research-readme.md
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "academic-research",
  "version": "0.1.0",
  "description": "Academic research pipeline — 4 skills: deep research (13-agent team, PRISMA support), academic paper (LaTeX/DOCX output), peer review (7-agent multi-perspective, 0-100 rubrics), pipeline orchestrator (10-stage with integrity gates). CC BY-NC 4.0 license. Research-flavor tool. NOT for: non-academic projects or commercial use (license restriction).",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

**IMPORTANT LICENSE NOTE:** CC BY-NC 4.0 means **non-commercial use only**. This MUST be clearly documented in the SKILL.md and README. Users in commercial settings cannot use this plugin.

- [ ] **Step 3: Create SKILL.md**

Include:
- Install: `/plugin marketplace add Imbad0202/academic-research-skills` or symlink install
- The 4 skills and what each does
- 10 `/ars-*` slash commands
- Optional dependencies (Pandoc, Tectonic, Semantic Scholar API key)
- **License warning: CC BY-NC 4.0 — non-commercial use only**
- `auto-activate: false`

- [ ] **Step 4: Create README.md and verify**

Include license warning prominently.

```bash
ls -la cultivation/marketplace/academic-research/
```

---

### Task 15: nature-skills (Claude Code Plugin)

**Repo:** https://github.com/yuan1z0825/nature-skills
**What:** 9 Nature-journal skills — figures (Matplotlib/SVG), prose polishing, writing, citations, data availability, paper reading, reviewer responses, paper-to-PPT, academic search (MCP).
**Integration:** Claude Code plugin. 9 skills auto-available after install.
**Stars:** 10.9k | **License:** MIT | **Last active:** Recent
**Dependencies:** Python, optional NCBI API key, optional MCP server for academic search.

**Files to create:**
- `cultivation/marketplace/nature-skills/.claude-plugin/plugin.json`
- `cultivation/marketplace/nature-skills/skills/nature-skills/SKILL.md`
- `cultivation/marketplace/nature-skills/README.md`

- [ ] **Step 1: Create structure and fetch upstream**

```bash
mkdir -p cultivation/marketplace/nature-skills/.claude-plugin
mkdir -p cultivation/marketplace/nature-skills/skills/nature-skills
curl -sL "https://raw.githubusercontent.com/yuan1z0825/nature-skills/main/README.md" -o /tmp/nature-skills-readme.md
```

- [ ] **Step 2: Create plugin.json**

```json
{
  "name": "nature-skills",
  "version": "0.1.0",
  "description": "9 Nature-journal skills: nature-figure (Matplotlib SVG), nature-polishing (prose refinement), nature-writing (manuscript drafting), nature-citation (CNS-family citations), nature-data (FAIR metadata), nature-reader (bilingual paper conversion), nature-response (reviewer response letters), nature-paper2ppt (PPTX decks), nature-academic-search (MCP multi-source). MIT license. Research-flavor tool. NOT for: non-academic projects.",
  "author": {
    "name": "Samyak Jhaveri",
    "email": "samyakjhaveri2799@gmail.com"
  }
}
```

- [ ] **Step 3: Create SKILL.md**

Include:
- Install: `/plugin marketplace add yuan1z0825/nature-skills` or symlink
- All 9 skills with status (Stable/Beta/Draft)
- MCP server for academic-search: `bash install.sh your-email@example.com`
- Optional NCBI API key for PubMed
- `auto-activate: false`

- [ ] **Step 4: Create README.md and verify**

```bash
ls -la cultivation/marketplace/nature-skills/
```

---

### Task 16: Update Marketplace README with All New Bundles

**File to modify:** `cultivation/marketplace/README.md`

- [ ] **Step 1: Add all new bundles to the Bundles table**

Add these rows to the Bundles table in `cultivation/marketplace/README.md`:

```markdown
| `code-review-graph` | code-review-graph | GraphRAG-powered code review with blast-radius analysis. [Upstream](https://github.com/tirth8205/code-review-graph). MCP server, recommended for 500+ file codebases |
| `planning-with-files` | planning-with-files | Manus-style persistent markdown planning. [Upstream](https://github.com/othmanadi/planning-with-files). Overlaps with feature-dev + plan mode |
| `understand-anything` | understand-anything | Codebase knowledge graph with React dashboard. [Upstream](https://github.com/Lum1104/Understand-Anything). Overlaps with Semble + CodeGraphContext |
| `ui-ux-pro-max` | ui-ux-pro-max | Design system generator with curated palettes, fonts, and UI styles. [Plugin Hub](https://www.claudepluginhub.com/plugins/nextlevelbuilder-ui-ux-pro-max). Frontend-focused |
| `impeccable` | impeccable | Design polish with 27 deterministic anti-pattern rules + LLM critique. [Plugin Hub](https://www.claudepluginhub.com/plugins/pbakaus-impeccable). By Paul Bakaus. Apache-2.0 |
| `storm-research` | storm-research | Stanford STORM research pipeline for Wikipedia-quality articles. [Upstream](https://github.com/stanford-oval/storm). Python package, research-flavor |
| `gpt-researcher` | gpt-researcher | Autonomous multi-source research agent with MCP server. [Upstream](https://github.com/assafelovic/gpt-researcher). Research-flavor, 3 API keys required |
| `academic-research` | academic-research | 4-skill academic pipeline — research, paper writing, peer review, orchestrator. [Upstream](https://github.com/imbad0202/academic-research-skills). **CC BY-NC 4.0** |
| `nature-skills` | nature-skills | 9 Nature-journal skills — figures, polishing, citations, writing, data, search. [Upstream](https://github.com/yuan1z0825/nature-skills). MIT, research-flavor |
```

- [ ] **Step 2: Verify README**

```bash
grep -c "cultivation/marketplace" cultivation/marketplace/README.md
# Should show all bundles listed
wc -l cultivation/marketplace/README.md
```

---

### Task 17: Update POST-RELEASE-BACKLOG.md

**File to modify:** `docs/POST-RELEASE-BACKLOG.md`

- [ ] **Step 1: Mark evaluated tools with decisions**

Update the P1 tools section to reflect adoption decisions:

| Tool | Status | Notes |
|------|--------|-------|
| code-review-graph | **Done** — marketplace bundle | MCP server, blast-radius analysis |
| planning-with-files | **Done** — marketplace bundle | Persistent markdown planning |
| claude-task-master | **Skipped** — MIT + Commons Clause license, native Tasks supersede | |
| Understand-Anything | **Done** — marketplace bundle | Knowledge graph dashboard |
| UI-UX Pro Max | **Done** — marketplace bundle | Design system generator |
| Impeccable | **Done** — marketplace bundle | Design polish, Paul Bakaus |

Add a new section for the additional tools adopted:

| Tool | Status | Notes |
|------|--------|-------|
| STORM | **Done** — marketplace bundle | Stanford research pipeline |
| GPT-Researcher | **Done** — marketplace bundle | MCP server, autonomous research |
| academic-research-skills | **Done** — marketplace bundle | 4-skill academic pipeline, CC BY-NC 4.0 |
| nature-skills | **Done** — marketplace bundle | 9 Nature-journal skills |

- [ ] **Step 2: Update Pocock skills section**

Mark the upstream replacement as done:

```markdown
### Skills — Upstream Replacement (completed 2026-05-23)
All 7 adopted skills replaced with upstream originals (DOMAIN.md rename + auto-activate only).
to-prd and zoom-out adopted. 4 high-impact reference files pulled.
Cross-skill references restored.
```

---

### Task 18: Workstream 2 Final Verification

- [ ] **Step 1: Full marketplace inventory**

```bash
cd /Users/samyakjhaveri/Desktop/loam
echo "=== Marketplace Bundles ==="
for d in cultivation/marketplace/*/; do
  bundle=$(basename "$d")
  if [ -f "$d/.claude-plugin/plugin.json" ]; then
    skills=$(find "$d/skills" -name "SKILL.md" 2>/dev/null | wc -l)
    echo "$bundle: ${skills} skill(s)"
  else
    echo "$bundle: (no plugin.json)"
  fi
done
```

Expected: 14 bundles total (5 existing + 9 new), each with at least 1 SKILL.md.

- [ ] **Step 2: Validate all plugin.json files**

```bash
for f in cultivation/marketplace/*/.claude-plugin/plugin.json; do
  bundle=$(echo "$f" | cut -d'/' -f3)
  if python3 -m json.tool "$f" > /dev/null 2>&1; then
    echo "OK: $bundle"
  else
    echo "INVALID JSON: $bundle"
  fi
done
```

Expected: All OK.

- [ ] **Step 3: Run template verifier**

```bash
bin/verify-template.sh
```

Expected: ALL OK.

- [ ] **Step 4: Commit Workstream 2**

```bash
git add cultivation/marketplace/
git add docs/POST-RELEASE-BACKLOG.md
git status
```

Use `/commit` skill with message: `feat(marketplace): add 9 tool/plugin bundles (code-review-graph, planning-with-files, understand-anything, ui-ux-pro-max, impeccable, storm-research, gpt-researcher, academic-research, nature-skills)`

---

## Research Findings Reference

This section contains the full evaluation data for each tool. The executing session should use this as reference when writing SKILL.md and README.md files — do not re-research.

### code-review-graph (C3)
- **Stars:** 17,254 | **Last release:** May 8, 2026 (v2.3.3) | **Commits (4 wk):** 75
- **Integration:** MCP server (28 tools), CLI, auto-config for Claude Code/Cursor/Copilot
- **Dependencies:** Python 3.10+, Tree-sitter. Optional: sentence-transformers, igraph
- **License:** MIT
- **Key insight:** "6.8x fewer tokens" is cherry-picked; honest average is 8.2x across 6 repos. No benefit below ~200 files. Windows has deadlock issues. Still Beta with 125 open issues.
- **Complements `/multi-review`:** code-review-graph decides WHICH code to look at; multi-review decides WHAT to say about it.

### planning-with-files (C4)
- **Stars:** 21,935 | **Last release:** May 22, 2026 (v2.40.1) | **Commits (4 wk):** 17
- **Integration:** Claude Code plugin/skill via `npx skills add`
- **Dependencies:** Node.js, Bash/PowerShell. Lightweight.
- **License:** MIT
- **Key insight:** Heavy overlap with Loam (feature-dev, plan mode, handoff, rules, memory). Only novel piece is hook-based re-injection after /compact. 22k stars but near-zero independent reviews. "$2B Manus AI" marketing is hype.
- **Overlap warning:** Duplicates 5+ existing Loam mechanisms. Install only for teams that prefer file-based planning.

### Understand-Anything (C6)
- **Stars:** 21,265 | **Last active:** Today (May 23, 2026)
- **Integration:** Claude Code plugin. Commands: /understand, /understand-dashboard, /understand-chat, /understand-diff, /understand-domain
- **Dependencies:** TypeScript/pnpm. LLM calls during analysis (token cost).
- **License:** MIT
- **Key insight:** Overlaps Semble + CodeGraphContext. Unique value is interactive React dashboard. Token cost during initial scan is the biggest concern. Best for onboarding — commit knowledge graph for new team members. Claims 70x token reduction after initial build.

### UI-UX Pro Max (C7a)
- **Stars:** 81,982 | **Last active:** April 2026
- **Integration:** Claude Code skill + CLI (`npm install -g uipro-cli`)
- **Dependencies:** Python 3.x (search script), Node.js/npm (CLI)
- **License:** MIT
- **Key insight:** 82k star count is anomalously high for a niche Claude Code skill — may not be organic. Contains 161 color palettes, 57 font pairings, 67 UI styles, 161 product-type rules, 99 UX guidelines, 25 chart types across 10 tech stacks. Source: Claude Plugin Hub.

### Impeccable (C7b)
- **Stars:** 29,742 | **Last active:** Yesterday (May 22, 2026, v3.1.1, 670 commits)
- **Integration:** Claude Code skill + CLI (`npx impeccable detect`) + browser extension
- **Dependencies:** Node.js (pnpm/Bun). Puppeteer for CLI. No API keys for deterministic rules.
- **License:** Apache-2.0
- **Author:** Paul Bakaus (creator of jQuery UI, former Google Chrome DevTools/AMP DevRel)
- **Key insight:** Strongest design tool evaluated. 27 deterministic anti-pattern rules (Layer 1!) + 12-rule LLM critique (Layer 3). Two modes: brand (design IS product) vs product (design SERVES product). Detects AI-generated design fingerprints. Rated 8.4/10 independently. Known issues: live mode disconnects, component selection finicky on deeply nested DOM, `adapt` can break layouts, monorepo file targeting.

### STORM (C8a)
- **Stars:** 28,254 | **Last active:** Sept 2025 (8 months ago)
- **Integration:** Python package only (`pip install knowledge-storm`). No MCP. No Claude Code skill.
- **Dependencies:** Python, dspy, litellm, streamlit. Two API keys minimum: LLM + search engine.
- **License:** MIT
- **Claude support:** YES — dedicated `ClaudeModel` class
- **Key insight:** Best-in-class research quality. Multi-perspective research, Co-STORM collaborative mode. Stanford-backed. But: no MCP/skill integration (requires custom wrapping), dual API key requirement, 8 months since last push.

### GPT-Researcher (C8b)
- **Stars:** 27,247 | **Last active:** April 2026
- **MCP server:** `gptr-mcp` (separate repo, 346 stars, v0.0.1, last push Nov 2025)
- **Integration:** MCP server (5 tools), Python package, Docker, web UI
- **Dependencies:** Python 3.11+, Tavily API key + LLM key + embedding provider (3 keys min)
- **License:** Apache-2.0
- **Claude support:** YES — native Anthropic provider env vars
- **Key insight:** Better integration than STORM (MCP exists) but MCP is immature (v0.0.1, Nov 2025). OpenAI-first tool. Per-invocation cost $0.10-$0.40.

### academic-research-skills
- **Stars:** 19,700 | **Last active:** May 18, 2026 (v3.9.2)
- **Integration:** Claude Code plugin (v3.7.0+). 10 `/ars-*` commands, 3 agents.
- **Skills:** deep-research (13-agent), academic-paper (12-agent, LaTeX), academic-paper-reviewer (7-agent), academic-pipeline (10-stage orchestrator)
- **Dependencies:** Python. Optional: Pandoc, Tectonic, Semantic Scholar/OpenAlex/Crossref APIs.
- **License:** **CC BY-NC 4.0 — NON-COMMERCIAL USE ONLY**
- **Key insight:** Most comprehensive academic research tool evaluated. Integrity gates, temporal verification, claim audit with L3 faithfulness locators. Very active (20+ releases in 2026). License is the main concern for commercial users.

### nature-skills
- **Stars:** 10,900 | **License:** MIT
- **Integration:** Claude Code plugin. 9 skills auto-available after install.
- **Skills (9):** nature-figure (Stable), nature-polishing (Stable), nature-writing (Draft), nature-citation (Beta), nature-data (Draft), nature-reader (Beta), nature-response (Beta), nature-paper2ppt (Beta), nature-academic-search (Beta, has MCP)
- **Dependencies:** Python. Optional: NCBI API key, MCP server for academic search.
- **Key insight:** Nature-journal-specific. Good for researchers targeting CNS (Cell/Nature/Science) family journals. MCP server for academic search adds value. Many skills still Beta/Draft.
