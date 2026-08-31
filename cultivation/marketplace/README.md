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
| `sam-cc-setup` | `brainstorming` -> `writing-plans`, merged plan review, technology selection, validation, Codex cross-model review, and bootstrap support | The Loam-owned setup plugin. Upstream-derived design skills retain their MIT notice in `sam-cc-setup/THIRD_PARTY_LICENSES/obra-superpowers.txt` |
| `impeccable` | UI polish workflow | Vendored; kept per rebuild ledger ruling |
| `web-frontend-*`, `deer-flow-public` | External skills, SHA-pinned via `git-subdir` | Ship `defaultEnabled:false`; enable to trial. Licenses per entry in `marketplace.json`; a `LICENSE.upstream` file in a vendored bundle is authoritative |

Removed 2026-08-29 (zero or near-zero survivors under the rebuild criteria): `meta-improvement`, `helpers` (surprise-me rehomed into sam-cc-setup), `business-process`, `planning-with-files`, `ui-ux-pro-max`, `understand-anything`.
Earlier removals (ledger): `pocock-engineering`, `team-deliberation`, `code-review-graph`, and the research bundles.
