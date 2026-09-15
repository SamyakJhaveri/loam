# Mac and jhaveris: validation record

Scope: correct the environment design to the user's actual machines and inspect relevant tool availability. Runtime implementation remains deferred.

## Evidence

Verified: local HEAD/main/origin/main and live remote main match `d627bb2755ad49865f798bcb095800ddd2ad1ced`. The preceding asset-environment checkpoint matched before edits; `Two-host baseline preservation: PASSED` was printed. Before-edit copies are in `/private/tmp/loam-two-host-before/`. Historical checkpoints, prior design and inactive asset intake remain preserved.

Verified: the user explicitly named this Mac and `jhaveris` Linux, allowed SSH access and expressed willingness to install needed libraries/software or change package versions. Current records now make both machines required targets. The old environment-choice questionnaire is superseded, not another pending user decision.

Verified: `ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=yes jhaveris` reached Linux through the existing SSH setup. The first command chain ended with exit 1 because native commands were not found on its PATH; the successful connection is separately shown by Linux/architecture output. A subsequent Python inventory records individual command exit statuses rather than treating the final shell status as every command's result.

Verified: the Linux non-interactive environment did not resolve user Node/Codex/Claude. npm failed with exit 127 and a missing-Node message. Targeted user installation paths revealed Node and native CLIs. A child environment with the discovered Node/local bin directories made the absolute Node/npm/Codex/Claude version commands each exit 0. This proves version-command resolution, not account login or factory readiness. No shell configuration edit was made.

Verified: [two-host-inventory.json](two-host-inventory.json) records OS, architecture, native/tool versions, compiler availability and Linux sandbox prerequisites. No credentials, project data, private native settings or environment files were read. The Mac diskutil probe failed; a follow-up `df` and matching mount line identify the home filesystem as APFS. Linux findmnt reports ext4. These observations do not establish crash/locking conformance.

Verified: the [official Node release page](https://nodejs.org/en/about/previous-releases) identifies v24.21.0 as current latest LTS and distinguishes the installed v26 Current/v25 end-of-life lines. The proposal uses that LTS patch as a compatibility candidate and requires a fresh check at setup. No Node runtime was installed, downgraded or certified for the factory.

## Scope correction and checks

The current environment record, native profile, first-run design, runtime overview, complete slice, asset plan, decision delta, README and handoff now require this Mac and jhaveris. Every seeded factory must satisfy its declared capabilities on both. The recommended authority/store/host grouping stays local to one machine. Automatic cross-machine takeover and shared live SQLite were not inferred from the user's host-scope instruction.

The document checker compares preserved historical/intake bytes, local links, required host wording, current navigation and tracked-source scope. Native version observations are not runtime tests. The prior full repository suite remains recorded in first-run validation; it was not repeated for this prose-only change.

Verified: `python3 /private/tmp/loam-two-host-check.py` printed `Two-host design checks: PASSED`, exit 0. Fresh-context review found no substantive scope/authority/PATH contradiction. It requested retaining the raw Mac mount evidence and removing one stale open-host-matrix phrase. The inventory now contains the successful matching mount output/status, and the first-run limit names compatibility results on the accepted hosts. The follow-up command printed `Mac filesystem evidence retained: PASSED`.

The second self-attack checked whether both-host support had been weakened into Mac-only proof with later Linux work. The current complete slice and ENV-01 require both machines. Host scope is settled; exact compatibility results remain open.

## Self-attack and requirement mapping

- Breaking input: a non-interactive SSH shell lacks Node despite an installed native CLI. This was reproduced and resolved for version commands using explicit paths. The planned installation fixture now covers that case.
- Unchecked paths: native authentication, actual provider work, process containment, storage/lock/crash recovery and package compatibility. All remain implementation/probe work; no readiness claim is based on a version command alone.
- Change without runtime tests: only documentation and host-observation metadata. Runtime, seed, shell configuration and packages are unchanged by the requested design work.
- Claim audit: the failed diskutil and npm calls are retained as failures. The filesystem and PATH conclusions use successful follow-up evidence. Package flexibility is accepted from the user's message; it does not become an implicit instruction to start the deferred runtime implementation.

| User instruction | Result |
|---|---|
| Simplify the environment discussion | Superseded E1/E2/E3 questionnaire; no broad VM/multi-platform product requirement |
| Support this Mac and jhaveris for Loam and seeded factories | Required host scope in current records, ENV-01 and the complete proof |
| Permit upgrades/downgrades/new dependencies | Recorded as setup flexibility; use qualified stable versions and explicit executable resolution |
| Access Linux through the shortcut or ssh | Direct SSH connection and bounded read-only host/tool inspection completed |
| Preserve existing design and runtime deferral | Curated profile/assets and ownership/recovery requirements retained; no implementation or package changes |
| End with clear input and next step | No further environment input is needed; next work is concrete setup/update and ordered implementation tickets |

## Limits

Not done: package changes, runtime implementation, actual factory/native model runs, host protection or recovery probes. No such work was necessary to establish the host scope or explain the observed PATH issue. Exact setup pins and commands remain to be qualified on both machines. The raw inventory captures the present environment, not a supported-runtime promise.
