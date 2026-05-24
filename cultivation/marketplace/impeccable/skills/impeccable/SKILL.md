---
name: impeccable
description: >
  Design polish with 27 deterministic anti-pattern rules + 12-rule LLM critique. By Paul Bakaus (jQuery UI creator).
  Commands: polish, audit, critique, typeset, animate, colorize, layout, delight. Apache-2.0.
auto-activate: false
---

# impeccable

Hybrid design polish tool — 27 deterministic anti-pattern rules (Layer 1) plus 12-rule LLM critique (Layer 3). Created by Paul Bakaus (jQuery UI creator, former Google Chrome DevTools/AMP DevRel).

**Source:** https://www.claudepluginhub.com/plugins/pbakaus-impeccable

## Install

> Install commands are from upstream documentation and may change. Check the [Plugin Hub page](https://www.claudepluginhub.com/plugins/pbakaus-impeccable) for current instructions.

```bash
# CLI detection mode
npx impeccable detect

# Full install
npm install -g impeccable
```

Also available as a browser extension.

## Modes

| Mode | When to use |
|------|------------|
| **Brand** | Design IS the product (marketing sites, portfolios) |
| **Product** | Design SERVES the product (SaaS, tools, dashboards) |

## Commands

`polish`, `audit`, `critique`, `typeset`, `animate`, `colorize`, `layout`, `delight`

## Why It's Strong

The 27 deterministic rules align with Loam's 60/30/10 layer triage — most design checks are Layer 1 (deterministic), not Layer 3 (LLM). The tool runs the deterministic rules first, then uses LLM critique only where judgment is needed.

Also detects AI-generated design fingerprints.

## Known Issues

- Live mode can disconnect
- Component selection finicky on deeply nested DOM
- `adapt` command can break layouts
- Monorepo file targeting has edge cases

## Requirements

- Node.js (pnpm or Bun)
- Puppeteer for CLI mode
- No API keys needed for deterministic rules

## Notes

- Apache-2.0 license, actively maintained
- Strongest design tool evaluated
- Frontend-focused — no value for backend-only projects
