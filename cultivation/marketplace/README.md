# seed-skills marketplace

Install-on-demand plugin bundles for Loam-adjacent projects.
Nothing here ships to bootstrapped projects by default; installs are explicit.
Slimmed 2026-08-29 in the rebuild (audit: `docs/specs/rebuild-research/slim-audit-bundles.md`).

## Install

```bash
claude plugin marketplace add /path/to/loam/cultivation/marketplace
/plugin install sam-cc-setup
```

## Bundles

| Bundle | Contents | Notes |
|--------|----------|-------|
| `sam-cc-setup` | Merged blind plan-reviewer + 5 review agents, /plan-review, /tech-selection, /surprise-me, /validate, Codex cross-model review, /bootstrap-cc-setup | The plugin layer of the Loam design; see its README |
| `sam-superpowers` | brainstorming | The single skill kept from the obra/superpowers fork |
| `impeccable` | UI polish workflow | Vendored; kept per rebuild ledger ruling |
| `web-frontend-*`, `deer-flow-public` | External skills, SHA-pinned via `git-subdir` | Ship `defaultEnabled:false`; enable to trial. Licenses per entry in `marketplace.json`; a `LICENSE.upstream` file in a vendored bundle is authoritative |

Removed 2026-08-29 (zero or near-zero survivors under the rebuild criteria): `meta-improvement`, `helpers` (surprise-me rehomed into sam-cc-setup), `business-process`, `planning-with-files`, `ui-ux-pro-max`, `understand-anything`.
Earlier removals (ledger): `pocock-engineering`, `team-deliberation`, `code-review-graph`, and the research bundles.
