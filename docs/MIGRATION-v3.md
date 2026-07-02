# Migration Guide: v2.0 → v3.0

> **Historical — pre-1.0 internal lineage only.** The public `loam` repo starts at **v1.0.0**;
> a project bootstrapped from public loam has nothing to migrate. This guide is retained only
> for the pre-public internal template lineage (v2.x/v3.x).

v3.0 changes `_subdirectory` from `"."` to `"seed"`. This is a structural change that breaks `copier update`.

## Why `copier update` won't work

Copier tracks which files it rendered from the template. When `_subdirectory` changes, Copier sees all old-root files as deleted and all `seed/` files as new. The result is a broken merge with file conflicts on every delivered file.

## Migration Steps

### 1. Back up project-local customizations

    cp CLAUDE.md CLAUDE.md.backup
    cp AGENTS.md AGENTS.md.backup 2>/dev/null
    cp -R .claude/rules/ .rules-backup/
    cp -R .claude/skills/ .skills-backup/ 2>/dev/null

### 2. Re-bootstrap from v3.0 template

    cd ..
    uvx copier copy --trust gh:samyakjhaveri/loam ./my-project-v3

### 3. Restore customizations

    cd my-project-v3
    cp ../my-project/.rules-backup/*.md .claude/rules/
    cp -R ../my-project/.skills-backup/* .claude/skills/ 2>/dev/null

### 4. Copy project code

    cp -R ../my-project/src ./
    cp -R ../my-project/tests ./

### 5. Verify

Open in Claude Code. Run `/catchup` — should show all core skills and the correct framework version.

## What changed in v3.0

| Component | v2.0 | v3.0 |
|-----------|------|------|
| Core Skills | 24 | 17 (-29%) |
| Agents | 11 | 6 (-45%) |
| Hooks | 12 | 8 (-33%) |
| Templates | 14 | 7 (-50%) |
| Copier exclusions | 36 | ~9 (-78%) |
| Architecture | Single-tree (root) | Seed subdirectory |
