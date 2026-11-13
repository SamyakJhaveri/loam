# Design goal: Loam's factory builds distbench the way Samyak's sessions work

## Goal
Make Loam's software factory (bin/factory and its helpers in /Users/samyakjhaveri/loam, run on jhaveris through ~/.local/bin/factory-isc against ~/distbench-isc) able to build distbench tickets the way Samyak's attended sessions worked 8-11 Nov 2026, unattended, and able to improve itself.

Samyak, 11 Nov, verbatim: "everything needs to be transferred to the software factory so the software factory can do the actual work ... Just get rid of the sandbox or update the sandbox settings." and "make sure that the software factory is primed up and is able to work like the way we work in the past few days ... the reviews how we review stuff the audit skill, the surprise me skill, the new workflow instructions, the new rules instructions, the new cloud code MD, the new skills, the P-Stack, the use of P stack and automatic invocation of P stack, and the ability to run unattended and get reviews and also the ability to schedule the work correctly in order to run as many things simultaneously as possible in order to test and verify them, in order to combine them ... not just the code and craft, but the behavior is as intended as per the design ... and also the iterative improvement ... so that the software factory itself can write tickets to be able to improve and fix it or to make it more elegant and to review that code and work."

## Inputs (read all)
Evidence folder /Users/samyakjhaveri/.local/state/distbench/evidence/2026-11-12-factory/:
- inventory-distbench.tsv (D01-D50), inventory-global.tsv (G01-G55), inventory-jhaveris.tsv (J01-J24): the checklist of behaviours, each with source file:line and how a run would show it.
- factory-today.md: what the factory does now, with file:line, and the four confirmed blockers.
- runs-w24-w34-w35.md: three finished distbench factory runs round by round (router read in few rounds; bin/check refused by the worker sandbox in every round; the supervisor's unsandboxed check is the only gate).
Code: Loam at /Users/samyakjhaveri/loam (main 5e7fc15f; same commit on jhaveris ~/loam). distbench at /Users/samyakjhaveri/distbench (main 582df455).

## Must cover
(a) Sandbox, per Samyak's ruling: run factory workers on jhaveris unsandboxed, or with settings allowing local binding, AF_UNIX and the real gate (distbench bin/check) inside the worker's round. Say exactly what protection is lost and what still guards (git worktree isolation, credentials the worker can read, deny list, network).
(b) pstack auto-invocation with proof: the worker calls the sam-cc-setup:pstack router before non-trivial work; its decision log names the method and the SKILL.md path read; the judge fails a claim of a method without a matching read in the transcript.
(c) Models: workers Opus 5.5 high; reviews Fable 5.2 high blind plus Codex read-only; an Opus verifier reproduces each finding before a fix; the audit and surprise-me skills run at the points docs/WORKERS.md names. Never Haiku, never effort max.
(d) Behaviour proof, not just code: verify-distbench for runner, command, package, grader or orchestrator changes; proof on the real target; the six proof steps in implementation-plan.md section 5 (git -C /Users/samyakjhaveri/distbench show origin/redesign-1030:docs/research/2026-11-05-replan/implementation-plan.md).
(e) Scheduling for throughput: as many runs at once as jhaveris allows (24G slice, gate-0/gate-1 slots, gpu and mpi locks, at most 3 heavy suites), runs combined through bin/integrate groups. A worker now running bin/check in-round adds gate load: say how that is bounded.
(f) Unattended operation: wake-up loop, hand-off at 450K tokens, dead-session watch, NEEDS-SAMYAK for owner-only calls.
(g) Self-improvement: the factory writes tickets against itself (Loam) and distbench from its own failures and reviews, and those tickets go through the same review route before any build.
(h) The measurement after batch 2: factory against attended helpers on serious review findings, reruns, cost and time.

## Principles (fixed)
- One source of truth (pstack /correct at the highest level): the factory loads distbench's own instruction files, skills and settings, and Samyak's own plugin skills, or a view generated from them, never hand-synced copies. Delete copies that exist (factory-today.md and inventory-global.tsv list stale ones). Checks over text.
- A rerunnable parity check (being built separately: it reads a run folder and its transcripts and prints PASS/FAIL per behaviour) is the acceptance gate. Say which checklist rows your design makes observable in a run folder, and where.

## Fences (fixed)
- Do not edit anything; this is design only. jhaveris is read-only for you (bare `ssh jhaveris '<cmd>'`); tmux sessions distbench-lead, ticket-review, night-watch and any f-* are live: never touch them.
- Edits to .claude/settings*.json or anything under ~/.claude are protected: they become one script Samyak runs. Merges to main need Samyak. Spend over 10 USD needs his yes.
- The branch origin/redesign-1030 is owned by another session: read it, never plan edits to it.

## Output
Write your design to the file your brief names, at most 1800 words: one section per item (a)-(h), each with the mechanism, the exact files to change per repo (Loam, distbench, Samyak-run script), and the observable a run folder or transcript will show; then the build units in order (one commit each, disjoint files per unit so separate workers can build them in parallel), each with its done check (a command and its expected output); then what you would not do and why; then risks. Cite file:line for every claim about current code.
