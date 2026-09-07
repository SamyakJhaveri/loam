# seed-skills marketplace

Install-on-demand plugin bundles for Loam-adjacent projects.
Nothing here ships to bootstrapped projects by default; installs are explicit.
Slimmed 2026-08-29 in the rebuild.
Slimmed again in v3.0.0: `sam-cc-setup` keeps 3 skills and ships no hooks; everything else moved to `cultivation/parked/` (design law 7, burden of proof is on keeping).

## Install

```bash
claude plugin marketplace add /path/to/loam/cultivation/marketplace
/plugin install sam-cc-setup
```

## Bundles

| Bundle | Contents | Notes |
|--------|----------|-------|
| `sam-cc-setup` | `plan-review` (blind merged plan review, with the `plan-reviewer` agent), `codex-review` (cross-model second opinion), `surprise-me` (ranked, evidence-backed ideas) | The Loam-owned setup plugin. No hooks, no workflows |
| `web-frontend-*`, `deer-flow-public` | External skills, SHA-pinned via `git-subdir` | Ship `defaultEnabled:false`; enable to trial. Licenses per entry in `marketplace.json`; a `LICENSE.upstream` file in a vendored bundle is authoritative |

Parked in v3.0.0 (moved to `cultivation/parked/`, not installed): 23 `sam-cc-setup` skills, 5 unused agents, the plugin `hooks/` directory, the `plan-review-fanout` workflow, the upstream MIT notice that covered the parked design skills, and the whole `impeccable` plugin.
Removed 2026-08-29: `meta-improvement`, `helpers`, `business-process`, `planning-with-files`, `ui-ux-pro-max`, `understand-anything`.
