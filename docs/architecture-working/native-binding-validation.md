# Native profile and lead binding: evidence and validation

Scope: design continuation after the user accepted the preceding first-run explanation. Native implementation and live provider probes remain deferred.

## Baseline and source scope

Verified: local `HEAD`, `main`, `origin/main` and live `git ls-remote origin refs/heads/main` match `d627bb2755ad49865f798bcb095800ddd2ad1ced`. Initial status contains only the untracked architecture directory. Python compared every preceding `resume-checkpoint.json` entry before editing and printed `Native binding baseline: PASSED; previous resume checkpoint preserved`. Before-edit copies are in `/private/tmp/loam-native-binding-before/`.

Verified: the preceding [first-run validation](first-run-validation.md) records the existing full repository check, including `31 passed in 8.95s` and `check: PASSED`. This continuation changes documentation only and does not rerun or claim a new full suite result. No runtime proof follows from that historical main check.

Verified: read the current handoff, decision record and first-run work/validation records, and relevant prior distribution/configuration/native evidence. Read current `bin/release.sh` and `docs/COPIER.md`. The release script uses `git tag -a`; it does not implement the proposed independently admitted factory bootstrap. This is a claim about that script, not an audit of every possible release-signing control.

Independent provider investigations used current official sources. The root separately read the native identity fields and key configuration limits. Downloaded declarations and generated schemas are temporary evidence, not installed dependencies. An attempted standalone `v2/Thread.json` read failed because the generated types are embedded; the root then found the model/effort/session descriptions in `v2/ThreadStartResponse.json`. No claim rests on the failed read. Large source outputs were inspected selectively, not treated as a complete implementation audit.

| Evidence | Observation | Limit |
|---|---|---|
| Local Codex help/version and offline schema generation | Investigator reported `codex-cli 0.154.0`; schema generation exited 0. Root read `DynamicToolCallParams.json` and embedded thread descriptions in `v2/ThreadStartResponse.json`. | No app-server or model launch. Experimental interface shape is not runtime behavior. Temporary directory: `/private/tmp/loam-codex-binding-schema/`. |
| [Codex dynamic tool flow](https://learn.chatgpt.com/docs/app-server#dynamic-tool-calls-experimental) | Native server-initiated request/reply route; thread/turn/call envelope supplies a proposed root decision boundary. | Exact routing, descendants and recovery replay need a probe. |
| [Codex environment](https://learn.chatgpt.com/docs/config-file/environment-variables), [skills](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills), [configuration](https://learn.chatgpt.com/docs/config-file/config-basic) | Native home is broader than settings; discovery has additional roots and host policy. | Home relocation alone does not establish isolation. |
| [Codex authentication](https://learn.chatgpt.com/docs/auth) | Native account and API-key routes differ. | Cross-home credential scoping, refresh, logout effects and connector access untested. |
| [Claude SDK package](https://registry.npmjs.org/@anthropic-ai/claude-agent-sdk/-/claude-agent-sdk-0.3.271.tgz) | Investigator inspected published `0.3.271` and verified registry SHA1/SHA512 integrity. Root read `BaseHookInput` and `SDKAssistantMessage` declarations in `/private/tmp/loam-claude-binding-sdk.d.ts`. | Registry integrity is not independent release authentication. No installation or Claude launch. |
| [Claude native feature configuration](https://code.claude.com/docs/en/agent-sdk/claude-code-features) | Selected setting sources omit some global inputs; account connectors and memory have separate behavior. | No proof of an immutable admitted view or complete capability parity. |
| SDK declarations for settings inspection, parent policy and model switches | Bounded settings inspection, restricted parent policy, separate automatic model-switch observations. | Declarative/API evidence only; no effective-policy or all-descendant enforcement claim. |

Verified: critical identity boundary checked by separate methods: native declarations/schema and independent provider analysis plus current official transport/configuration documentation. A fresh-context correctness review is the additional design check. These do not replace native probes.

## Validation and review

Verified: `python3 /private/tmp/loam-native-binding-doc-check.py design` printed `Native binding design checks: PASSED`, exit 0, before navigation changes. After living-record updates, its final mode printed `Native binding final checks: PASSED`, exit 0. It checks local Markdown links, trailing whitespace, required contract clauses, byte preservation of historical snapshots/checkpoints and the documentation-only Git scope. It does not execute a provider or prove the semantics of the design.

Verified: a fresh-context reviewer identified missing native withdrawal handling in Claude decision assembly. The root confirmed `supersedes` and `retracted_message_uuids` in the published declarations. The proposal now excludes withdrawn blocks, retains withdrawal history on replay, waits for a correlated successful terminal result and resolved replacement state, and stages a Claude decision tool until that gate. Late contradictions block affected use through correction handling. Actual model changes and external effects remain recorded even when answer blocks are withdrawn.

Verified: the document check passed after that repair. The reviewer's bounded reread confirmed the repair and found no further concrete contradiction in those clauses. The reviewer did not certify native ordering/finality, account isolation or model enforcement.

## Self-attack and completeness

- What input breaks this? A valid-looking adopt block can be withdrawn later. The repaired finality and replay rules exclude it. Unknown or inconsistent finality blocks the decision or affected use; a live probe remains necessary.
- Which path did I not check? Live native startup, child routing, automatic reruns, authentication/refresh and mutable discovery. They remain explicit gates. A schema/type declaration cannot establish these behaviors.
- What changed without a runtime test? All changes are design and living records. Temporary document checks validate preservation and links, not the future factory. No new suite result or compatibility result is claimed.
- Which claim lacks evidence? No verified isolation, complete native parity, selected dependency pin or model/effort guarantee is claimed. Expected option consequences are design tradeoffs. First-run acceptance follows the user's "looks good"; the newly presented profile option remains pending.

The second attack pass checked whether withdrawing answer blocks could also erase an actual unauthorized model change or external effect. The repaired clause explicitly retains those observations and barriers. No further concrete repair was identified; finality/order feasibility stays listed under Limits.

| User instruction | Result |
|---|---|
| Resume from the saved architecture and preserve changes | Handoff/current-record continuation, checkpoint comparison, before-edit copy, unchanged historical records |
| Verify current main | Matching local and live remote Git identities; preceding suite evidence remains separately dated by its own record |
| Continue with selected model/effort and settled TypeScript | No override or language reopening; native protocol observations are not new selected pins |
| Resume concrete first-run/ownership/storage/recovery design | Accepted direction retained; native profile, root attribution, replay and bootstrap dependency specified |
| Keep living records current | README, decision delta, first-run status and restart handoff updated; new specification, work/check record and validation saved |
| Defer runtime implementation | Documentation-only scope; no native calls, installations, login/config changes, commits or publication |
| Explain needed input, options, consequences and recommendation; permit combinations | Saved choice table and combined recommendation; durable response instruction in handoff and decision record |
| Name the next decision | Bootstrap and supported execution environment, then file-level implementation/probe tickets |

The previous pause and resume checkpoints remain unchanged history. The new `native-binding-checkpoint.json` records the current documentation snapshot; its hashes are preservation evidence, not proof of runtime correctness.

## Limits

Not done: runtime implementation, live model/provider probes, login, credential/configuration mutation, dependency installation, commits, pushes or publication. Exact dependency pins, stable native input enforcement, all required model/effort observations and replay behavior remain unverified. Bootstrap and supported execution environment are the next design decision after the user's profile choice.
