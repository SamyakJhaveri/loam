---
name: planning-with-files
description: Manus-style persistent markdown planning with task_plan.md, findings.md, progress.md. Hook-based re-injection after /compact.
auto-activate: false
---

# planning-with-files

Persistent markdown planning files that survive `/compact` via hook-based re-injection. Creates and maintains `task_plan.md`, `findings.md`, and `progress.md` for cross-session persistence.

**Upstream:** https://github.com/othmanadi/planning-with-files

## Install

> Install commands are from upstream documentation and may change. Check the [upstream repo](https://github.com/othmanadi/planning-with-files) for current instructions.

```bash
npx skills add planning-with-files
```

Or clone the repo and symlink into your project's `.claude/skills/`.

## What It Does

1. Creates structured planning files at project root
2. Hooks into Claude Code lifecycle to re-inject plan context after `/compact`
3. Maintains progress tracking across sessions

## Overlap Warning

This tool **heavily overlaps** with Loam's built-in planning infrastructure:

| planning-with-files | Loam equivalent |
|---|---|
| `task_plan.md` | Plan mode + `docs/plans/` |
| `findings.md` | Memory system + `.claude/rules/` |
| `progress.md` | `/handoff` skill |
| Hook re-injection | Always-loaded rules |

Install only if you prefer file-based planning over Loam's built-in approach. The two systems may conflict if used simultaneously.

## Requirements

- Node.js
- Bash or PowerShell

## Notes

- MIT license
- Novel piece is hook-based re-injection after `/compact`
- Near-zero independent reviews despite popularity
