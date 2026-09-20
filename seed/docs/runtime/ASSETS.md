# Curated asset catalog

## What the catalog is

`.loam/runtime/assets/curated-catalog.json` is a conservation record. It lists every
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
| `available` | Delivery is qualified: every required body and support digest matches its recipient bytes, every prerequisite resolves, and no blocker remains. Still not activated. |
| `not-selected`, `local-only`, `declared-unread`, `rejected` | Informational dispositions. No delivered target, activation or wrapper claim. |

Every actual method in this revision is pending. `catchup`, `fable-prompting` and
`hypothesis-tree` are present in the seed but unqualified. Existing seed policy and hooks are recorded as
already distributed; the catalog neither enabled nor disabled them. Pocock same-name
methods do not replace Loam baseline methods; an assessed merge names its baseline
successor without claiming the merge is implemented. The `pocock:to-tickets` entry records
the campaign's supersession of its generic publish workflow.

## Activation authority

`activation.activated` is `false` for every entry. Qualification never activates a method. The
validator proves the catalog consistent with itself, reading only catalog fields: no entry is ever
`available`, every edge resolves to a real entry, target or prerequisite, every wrapper resolves,
each target's declared section keys equal the union of the map sections aimed at it, and the
reverse index is the recomputed inverse of the edges. It does not compare the catalog to a second
copy of itself. A target's delivery state and expected digest are proven by bytes, not by any frozen
record: `checkRecipientDelivery` reads each present target body from the recipient tree and requires
its exact expected digest, in Loam and in every render. Source bytes and source units are re-verified
against the working tree by the Loam-only provenance gate, and recipient integrity rests on the
release manifest, the admission seal and doctor.
`resolveEntry` is a lower-level helper: it binds one candidate entry to a trusted expected
contract and returns `activatable: true` only when that contract is qualified and every
required body, support file and prerequisite resolves; it certifies nothing on its own.

## Wrappers and projections

`nativeWrappers` freezes the planned provider payload files under
`assets/native/claude/commands/`, `assets/native/claude/agents/`,
`assets/native/claude/workflows/` and `assets/native/codex/`. Every row is
`planned-metadata-only`; no wrapper file exists yet. A wrapper carries invocation metadata
only; the shared method body lives under `.agents/skills/`. Each wrapper resolves within the
catalog: it wraps a real entry, names a real method target, and its payload path sits under its
provider's own native directory. `projectionMechanism` is one sentence describing how a projection
reaches a provider. The Claude wrappers describe a future distribution mirror of invocation-only
metadata whose byte equality and native discovery are verified by the owning adapter
ticket. The Codex wrappers describe the existing shared-skill discovery plus the
invocation reference the method's future Codex branch reads at the factory package path
and the payload path.

## Dependencies and prerequisites

Each dependency edge has a stable ID, a source unit, a typed relationship and a
disposition. A retained required edge names the exact target or prerequisite that
satisfies it. File prerequisites name a recipient path and expected digest. Command and
service prerequisites are recorded by name and are never executed by catalog checks; an
unverified command blocks availability. The five private session records cannot satisfy
any edge or prerequisite, carry no source units, and expose no capability claims.

## Qualify the catalog

```bash
node .loam/runtime/launcher.mjs qualify catalog
```

The command runs the fixed `curated-catalog` population
(`dist/tests/assets/catalog.test.js`) and prints the exact case names and count. It checks
schema validity, edge and wrapper resolution, activation honesty, the delivery digests proven by
recipient bytes, the selected-dependency mappings and the Pocock collection, all from the catalog's
own fields. It needs no compiler, network or source projects. Source provenance against
the Loam repository tree runs only in Loam (`bin/factory-catalog-provenance.mjs`), because a
rendered project has neither `cultivation/` nor the intake inventories; that gate re-hashes the
source bodies, re-extracts the source units, and anchors the recorded ticket digest to the archived
ticket in the tree. Neither command
delivers a method or makes the full installation group pass; that group stays
unavailable until its remaining populations exist.
