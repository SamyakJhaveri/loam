# Concurrent checkout hook ownership plan

## Decision

`seed/.claude/hooks/concurrent-checkout-guard.sh` is the canonical implementation.
Every Loam-rendered project receives this copy.

`cultivation/marketplace/sam-cc-setup/hooks/concurrent-checkout-guard.sh` is a distribution mirror.
It lets projects that do not use the Loam seed install the same guard through the plugin.

The mirror stays byte-identical to the canonical file.
The rendered harness contract enforces this rule.

## Task list

1. Define the mirror contract in a regression test.
   Check: `python3 -m unittest bin.tests.test_rendered_harness_contract.RenderedHarnessContractTest.test_concurrent_checkout_distribution_mirror_must_match_canonical -v` fails before the verifier changes and reports `distribution-mirrors`.
2. Add one source-level mirror check to the shared verifier.
   Check: the focused regression test passes, and `cmp seed/.claude/hooks/concurrent-checkout-guard.sh cultivation/marketplace/sam-cc-setup/hooks/concurrent-checkout-guard.sh` exits `0`.
3. Document the narrow mirror exception and the edit workflow.
   Check: `rg -n 'canonical|distribution mirror|byte-identical' docs/ASSET-LAYERS.md cultivation/marketplace/sam-cc-setup/README.md` finds both ownership routes.
4. Run the complete release gate.
   Check: `bin/verify-template.sh` ends with `verify-template: PASSED`, and `git diff --check a4305fe..HEAD` exits `0`.

## Change boundary

Do not change hook behavior.
Do not remove either distribution path.
Do not add a sync script.
