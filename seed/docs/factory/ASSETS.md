# Curated asset catalog

## What the catalog is

`.loam/factory/assets/curated-catalog.json` is a conservation record. It lists every
curated Loam method and supporting file, the selected cross-project methods, the
acquired Matt Pocock skill collection, the optional remote bundles, and the cross-project
assets that were inventoried but not selected. Its shape is fixed by
`assets/curated-catalog.schema.json`. The catalog says where each method comes from,
where its shared body is planned to live, what it depends on, and whether that delivery
has been qualified. It does not install, move, activate or execute anything.

Source truth and delivery truth are recorded separately. A source identity is a
repository-relative path with the SHA-256 of its exact bytes, a checked distribution
symlink, a pinned remote declaration whose body was never read, or one of five private
session records carried as metadata only. A target is a recipient-relative path with an
owner, a kind, declared section keys and a delivery state. Adaptation changes bytes, so a
source digest never certifies a delivered body.

## Pending versus available

| Status | Meaning |
| --- | --- |
| `source-preserved` | The source identity is retained. Nothing is delivered or certified as executable. |
| `shipped-pending-adaptation` | The stated recipient body is present and its delivered digest matches, but repair or catalog qualification is pending. Not activatable. |
| `blocked-missing-support` | A required selected dependency is unresolved. The inclusion obligation remains. |
| `available` | The fixed obligations mark delivery qualified: every required body, support digest and prerequisite resolves and no blocker remains. Still not activated. |
| `not-selected`, `local-only`, `declared-unread`, `rejected` | Informational dispositions. No delivered target, activation or wrapper claim. |

Every actual method in this revision is pending. `catchup` and `fable-prompting` are
present in the seed but unqualified. Existing seed policy and hooks are recorded as
already distributed; the catalog neither enabled nor disabled them. Pocock same-name
methods do not replace Loam baseline methods; an assessed merge names its baseline
successor without claiming the merge is implemented. The `pocock:to-tickets` entry records
the campaign's supersession of its generic publish workflow.

## Activation authority

`activation.activated` is `false` for every entry. Qualification never activates a method.
Changing status, activation, blockers or prerequisites inside the catalog cannot promote a
pending entry, because the validator compares the catalog against obligations compiled into
the package (`src/assets/obligations.ts`), never against the catalog's own claims. Bodies
recorded as present are read from the recipient tree and must match their expected digest.
`resolveEntry` is a lower-level helper: it binds one candidate entry to a trusted expected
contract and returns `activatable: true` only when that contract is qualified and every
required body, support file and prerequisite resolves; it certifies nothing on its own.

## Wrappers and projections

`nativeWrappers` freezes the planned provider payload files under
`assets/native/claude/commands/`, `assets/native/claude/agents/`,
`assets/native/claude/workflows/` and `assets/native/codex/`. Every row is
`planned-metadata-only`; no wrapper file exists yet. A wrapper carries invocation metadata
only; the shared method body lives under `.agents/skills/`. `projectionMechanism` names
how a projection reaches a provider: `distribution-mirror` is a future Claude mirror of
invocation-only metadata whose byte equality and native discovery are verified by its
owning adapter ticket; `shared-skill-discovery` is the existing Codex shared-skill path
plus the invocation reference the method's Codex branch reads.

## Dependencies and prerequisites

Each dependency edge has a stable ID, a source unit, a typed relationship and a
disposition. A retained required edge names the exact target or prerequisite that
satisfies it. File prerequisites name a recipient path and expected digest. Command and
service prerequisites are recorded by name and are never executed by catalog checks; an
unverified command blocks availability. The five private session records cannot satisfy
any edge or prerequisite, carry no source units, and expose no capability claims.

## Qualify the catalog

```bash
node .loam/factory/launcher.mjs qualify catalog
```

The command runs the fixed `curated-catalog` population
(`dist/tests/assets/catalog.test.js`) and prints the exact case names and count. It checks
schema validity, the required memberships, exact targets and edges, activation honesty,
the selected-dependency mappings and the Pocock collection against the compiled
obligations. It needs no compiler, network or source projects. Source provenance against
the Loam repository tree runs only in Loam (`bin/factory-catalog-provenance.mjs`), because a
rendered project has neither `cultivation/` nor the intake inventories. Neither command
delivers a method or makes the full installation group pass; that group stays
unavailable until its remaining populations exist.
