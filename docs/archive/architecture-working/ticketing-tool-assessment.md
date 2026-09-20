# Ticketing tool assessment and acquired package

## Verified source and acquisition

Primary sources inspected: <https://www.aihero.dev/skills-wayfinder> and <https://github.com/mattpocock/skills>, plus the acquired README, plugin manifest and Wayfinder, setup and to-tickets instructions.

The upstream repository at `3cca18b368ae95cdbdebbff572ccafa662551015` declares Claude plugin version `1.2.3`. Its released manifest selects 25 skills. The broader repository has 37 SKILL.md files, including in-progress and miscellaneous material not selected by the released plugin. All 25 released skills and their 74 supporting/source files were acquired using the Codex skill-installer helper and compared byte-for-byte with the pinned clone. See [provenance](tooling/mattpocock-skills/provenance.json). Upstream license and README are retained alongside the source bundle.

Upstream currently supplies a Claude Code plugin and editable skill installation for Codex; its README puts a native Codex plugin on the roadmap. No native Codex plugin installation is claimed here.

An attempted project-local active install into `.agents/skills` failed with `Operation not permitted` while creating `.agents`. No skill was installed there. The source bundle is staged at `docs/architecture-working/tooling/mattpocock-skills/` for explicit reading, outside automatic skill discovery. This preserves the package durably without bypassing the restricted discovery directory. No global configuration, seed asset, or source project was changed. Enabling automatic discovery remains unfinished. Reading the staged instructions is sufficient for this ticket-authoring session.

## Decision: use to-tickets now; use Wayfinder for genuine open decisions

Wayfinder creates a map of unresolved decisions. Its own article directs already-decided work through a specification and then to-tickets. Loam already has accepted decisions, detailed contracts and a consolidated implementation plan. Recreating them as open questions would add work without resolving uncertainty.

Use [to-tickets](tooling/mattpocock-skills/to-tickets/SKILL.md) to produce independently verifiable work increments and explicit dependency edges. Retain qualification questions about runtime pins, protection and native identity as bounded probe results. If a probe forces a consequential choice, record the evidence and bring that choice back to the user; a small Wayfinder map is useful only if multiple unresolved decisions emerge.

The repo already has `docs/agents/issue-tracker.md`, `triage-labels.md` and `domain.md`, with pointers in AGENTS.md. Setup is already configured; do not rerun its questionnaire or overwrite those files.

## Deliberate adaptations

- Current accepted architecture is the specification. Do not recreate it or reopen TypeScript, the host scope, the curated profile or routine scheduling.
- User-required source paths, exact reading packets and proposed commands stay in tickets despite upstream's usual preference to omit paths.
- All tickets remain planned, with runtime deferred. Do not apply upstream's default `ready-for-agent` label or assign a worker before execution is authorized.
- Produce complete individual draft issue bodies and a dependency map before asking for publication approval. The invoked skill explicitly says to iterate until the user approves the breakdown, and standing repository instructions require confirmation for outward-facing publication. Approval here would publish work items only, not begin runtime work.
- Use independent bounded source/core/native/remote drafts, integrate their dependencies, then obtain fresh correctness review. Helpers do not independently edit the shared packet or publish tickets.
- Upstream guidance is a method library. A justified departure records the relevant source, changed choice, reason and verification obligation. It cannot weaken accepted user requirements, authority boundaries or review gates.

## Existing tracker history

Read-only GitHub inspection found the open [Loam Factory wayfinder map](https://github.com/SamyakJhaveri/loam/issues/33), which describes the existing Bash factory and historical model rules, plus the separate [Lean v3 map](https://github.com/SamyakJhaveri/loam/issues/14) and [optional follow-up](https://github.com/SamyakJhaveri/loam/issues/26). The new generated-factory campaign needs its own parent. Link this history; do not close, relabel or reinterpret its existing work as the new implementation plan.
