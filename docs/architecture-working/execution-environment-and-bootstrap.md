# Execution on Mac and Linux

Status: accepted platform scope is Mac and Linux, initially this Mac and the Linux machine reached through `ssh jhaveris`, with replacement machines later. The latest requirement explicitly includes Mac-led remote native agents and GPU experiments. This supersedes the previous E1/E2/E3 questionnaire and the earlier assumption that entering Linux through SSH was sufficient. A VM product and automatic cross-machine takeover are outside the requirement. Runtime implementation remains deferred.

## Settled direction

Verified: the user permits installing libraries/tools and upgrading or downgrading packages to supported stable versions on either machine. SSH inspection of `jhaveris` is explicitly authorized. This is flexibility to make the chosen setup work, not a requirement to preserve today's accidental package versions.

Recommendation: one TypeScript factory, built and checked for macOS arm64 and this Ubuntu x86_64 host. Keep only narrow operating-system differences in locking, process control, filesystem permissions and native launch setup. Both machines are required targets for the first complete proof; Linux is no longer a later optional extension.

Recommendation: keep each project's supervisor and authoritative SQLite store together on its owning machine. For the user's Mac-led workflow, local tools operate on the Mac and an SSH transport reaches a persistent Linux execution runner. Its local job ledger and artifact spool preserve execution facts; they do not acquire task acceptance authority. Do not share a live SQLite database across machines or infer ownership from an SSH connection. [Maintenance and remote work](maintenance-and-remote-work.md) and the [remote execution contract](remote-execution-contract.md) specify this extension. Remote dispatch is required; a general cluster scheduler and automatic owner failover are not.

## Actual machine evidence

Verified: the [host inventory](two-host-inventory.json) records individual commands and statuses. Direct `ssh jhaveris` worked using the existing host-key trust and non-interactive authentication.

| Item | This Mac | jhaveris |
|---|---|---|
| Operating system | macOS 26.6.2, arm64 | Ubuntu 24.04.4 LTS, x86_64 |
| Node found | v26.7.0 | v25.9.0 under the user's nvm directory |
| npm after explicit executable resolution | 11.19.0 | 11.12.1 |
| Codex | 0.154.0 | 0.153.4 after child-process PATH resolution |
| Claude Code | 2.1.266 | 2.1.269 |
| Native build tools | Apple clang and make available | GCC and make available |
| Linux sandbox prerequisites | Host-specific Mac mechanism | bubblewrap 0.9.0 and socat 1.8.0.0 available |

Verified: the initial non-interactive Linux PATH did not find Node, Codex or Claude. `/usr/local/bin/npm --version` failed with exit 127 because Node was unavailable through PATH. Explicitly including the already discovered user Node and local executable directories made Node, npm, Codex and Claude version checks each exit 0. No login shell configuration or package installation was needed for that check. Therefore the immediate setup issue is executable resolution, not evidence that those tools are absent.

Verified: `findmnt` reports the Linux home on ext4. The Mac `diskutil` probe failed; `df` resolved its home to `/System/Volumes/Data` and the corresponding mount reports APFS. Filesystem identity is evidence for selecting local storage tests, not proof of lock/crash durability.

## Concrete package and setup plan

Recommendation: qualify the same exact supported Node LTS patch for the factory on both machines, in an isolated factory toolchain. LTS means long-term support. This avoids changing unrelated research projects just to run Loam. Refresh the candidate when setup begins; record executable identity and the package lock with each admitted runtime.

Verified: the official Node release page currently lists v24.21.0 as latest LTS, v26 as Current and v25 as end-of-life. Use v24.21.0 as today's compatibility candidate, not as an already tested factory pin. The user's installed Node versions need not determine the factory runtime. [Node release status](https://nodejs.org/en/about/previous-releases).

Recommendation: qualify explicit Codex/Claude versions on both hosts against the required native protocol/SDK behavior. Align versions where feasible, or record separately tested provider bindings. A larger version number is not compatibility proof. Resolve installed executable paths and construct the launch environment deliberately; never depend on an interactive `nvm` initialization, a personal alias or incidental PATH order. Retain supported native account login and selected models/effort. Version checks do not test login or model availability.

Recommendation: use the existing compilers and Linux prerequisites when they pass the relevant probes. Install, update or downgrade only concrete missing/incompatible dependencies. The user has already expressed willingness to do that. Do not ask them to choose generic library alternatives before a compatibility result identifies a real tradeoff. Proposed bindings such as SQLite/locking and any whole-process wrapper still need their targeted tests; being installed is not enough.

## Required protection and recovery work

Keep the accepted ownership boundary practical: the candidate cannot rewrite the supervisor, forge authoritative check/lead receipts or replace the state store. Keep installed control code and state separate from candidate-writable code. Retain the native-profile and recovery probes already specified; implement the simplest host mechanism that passes them on these machines. This is a correctness requirement, not another open deployment questionnaire.

Recommendation: retain the native platforms' supported controls and qualify whole-process restrictions where the accepted profile needs them. The same logical cases run on both hosts: missing registered store; concurrent owner; killed supervisor; surviving native/check child; replayed evidence; changed candidate/profile; rejected child adoption; undeclared configuration; lost tool access. Linux additionally needs its actual process/filesystem/locking behavior exercised, not inferred from Mac success. SSH disconnection must remain distinguishable from worker completion.

Native credentials, startup hooks, read-only admitted input discovery and actual root-lead attribution remain probe gates. No compatibility guarantee or containment result was established by this host inventory. A failure warrants a concrete repair or a specific user tradeoff, not silently weakened authority.

## Bootstrap and implementation-ticket changes

Recommendation: retain Copier source distribution and explicit setup from an independently admitted release or reviewed fork. Prepare the factory runtime for the selected host, verify the rendered payload and register its local state. Keep candidate-local manifests from authenticating themselves. Package changes belong in this controlled setup; ongoing native work does not silently update its own runtime.

Update ENV-01 from the previous proposal: it now qualifies both actual hosts, with no prerequisite E1/E2 choice. Proposed files remain `seed/.loam/factory/src/platform/native-boundary.ts`, `seed/.loam/factory/src/profiles/admitted-view.ts`, `seed/.loam/factory/tests/platform/native-boundary.test.ts` and `seed/docs/factory/SETUP.md`. Add the host/executable contract to `seed/.loam/factory/assets/runtime-manifest.json` and its installation fixtures. These are planned files, not new runtime code.

Acceptance obligations: the same released factory revision renders and completes the generated-project proof on each host, using its recorded native binaries and local store. Installation fixtures must include a non-interactive environment where user Node is absent from PATH but a valid configured runtime exists. Missing or incompatible executables produce precise setup failures. Run the installation, execution and complete-slice groups on both machines; real provider probes remain separate from fake-native fixtures. No such factory test has run yet.

The asset adoption tickets remain in scope. Their specialist dependencies can be installed when needed, and their methods must not assume the original benchmark/job-search directories exist on either host. Source snapshots remain inactive.

## Input needed and next work

No further platform choice is needed. Mac and Linux are accepted, initially qualified on this Mac and `jhaveris`; replacement machines need enrollment and readiness checks. Package flexibility is recorded.

The [maintenance/remote tickets](maintenance-remote-tickets.md) now cover compatibility, Linux service setup, native/GPU execution, controlled updates and replacement. Recommendation: explicit initial setup, fixed versions during active work and reviewed release adoption. The user selected the mixed offline default. The [job record and operator flow](remote-job-and-operator-flow.md) now specify launch, monitoring, recovery and update obligations. Queue-by-default with fail-fast is accepted. Treat jhaveris as the user's personal machine, with simple handling for overlapping work. Next consolidate the remaining bootstrap/setup/update tickets; routine scheduling details do not need further user decisions. Runtime implementation still begins only on the user's explicit instruction.
