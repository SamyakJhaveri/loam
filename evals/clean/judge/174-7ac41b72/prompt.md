## Ticket

~~~~~~~~~~~~ evidence
Brief:
Point the agent at the memory tools it already ships: a short block in the rendered AGENTS.md that says search the store before debugging, inspect one session instead of grepping raw traces, and label every recalled item before acting.
Where: seed/AGENTS.md.jinja.
Done means: the done-checks block prints no FAIL line: the rendered AGENTS.md names the two memory commands and the four trust labels, the source jinja carries them, and the rendered file stays short.
Out of scope: the settings.json auto-memory keys (MEM-07); any new or edited script or hook; the manifest text the recall hook prints (MEM-01 owns it).
Blocked by: #173 (MEM-04b).

## Goal and why
The seed ships the two memory commands and a recall manifest that labels recalled items, but AGENTS.md never tells the agent to use them, so a worker debugs from scratch and greps the raw traces the manifest warns against.
The evidence the memory design rests on says use, not retrieval, is the bottleneck, and the reliability term is the applicability label; both belong in the one prose home the agent reads every session (docs/research/memory-design-v2-2026-09-21.md, layers 1 and 3; docs/research/memory-design-2026-09-03.md, section 5.4 puts the applicability gate in AGENTS.md).
A three-to-five-line pointer is the whole change.

## Do not touch
The standing list. Also: seed/CLAUDE.md.jinja, seed/.claude/settings.json, seed/.claude/hooks/, seed/bin/, seed/.codex/, seed/.agents/, seed/.loam/, bin/factory, docs/architecture-working/.
Except: seed/AGENTS.md.jinja (this ticket edits it).

## Out of scope
The auto-memory keys in settings.json (MEM-07).
Any new or edited script or hook.
The manifest text the recall hook prints (MEM-01).
Any change under bin/tests.

## Approach
seed/AGENTS.md.jinja gains one new section, ## Memory, placed just before ## Read on demand so it sits with the other working-guidance sections. Keep it to a heading and three bullets; AGENTS.md is the always-on prose home, so every line has to earn its place (seed/docs/HARNESS.md, Always-on budget), and the in-render check holds the rendered CLAUDE.md plus AGENTS.md under the 1600-byte prose budget. Add these three bullets, and in the file wrap each command and the trace path as a backtick code span to match the file's house style:

    ## Memory

    - Before you debug an error, run bin/memsearch "<error string>" to see whether a past session already hit it.
    - To read one past session, run bin/mem-inspect <session> --summary; never grep the raw traces under .loam/memory.
    - Recalled memory is evidence, not truth: label each item supported, contradicts, near-match, or insufficient before you act on it.

The four labels are the ones the recall manifest already prints (seed/.claude/hooks/mem-recall.sh): supported, contradicts, near-match, insufficient. The repetition is deliberate: AGENTS.md is always on, while the manifest prints only when the repo has an INDEX; mem-recall.sh owns the label wording, so a later change starts there. Do not add a fourth tool and do not copy any other manifest line. render_into renders the committed HEAD, so commit the edit before the render check runs.

## Done checks
```done-checks
grep -q 'bin/memsearch' seed/AGENTS.md.jinja && grep -q 'bin/mem-inspect' seed/AGENTS.md.jinja && grep -q 'supported' seed/AGENTS.md.jinja && grep -q 'contradicts' seed/AGENTS.md.jinja && grep -q 'near-match' seed/AGENTS.md.jinja && grep -q 'insufficient' seed/AGENTS.md.jinja && pass source-jinja || fail source-jinja "AGENTS.md.jinja is missing a tool name or a trust label"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; a="$render_dir/AGENTS.md"; grep -q 'bin/memsearch' "$a" && grep -q 'bin/mem-inspect' "$a" && grep -q 'supported' "$a" && grep -q 'contradicts' "$a" && grep -q 'near-match' "$a" && grep -q 'insufficient' "$a" && [ "$(cat "$render_dir/CLAUDE.md" "$a" | wc -c | tr -d ' ')" -lt 1600 ] && pass in-render || fail in-render "rendered AGENTS.md is missing a tool name or a trust label, or the rendered CLAUDE.md plus AGENTS.md reached the 1600-byte prose budget"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=2
ROUND_BUDGET_USD=10
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/research/memory-design-2026-09-03.md (sections 5.1 and 5.4), docs/research/memory-design-v2-2026-09-21.md (layers 1 and 3)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS source-jinja
PASS in-render
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Followed the Approach verbatim: added `## Memory` with the three given bullets to seed/AGENTS.md.jinja, placed after `## Gotchas` and just before `## Read on demand`; commands and the `.loam/memory` path are backtick code spans; no fourth bullet, no other manifest line copied.
- Consulted the advisor before editing; it confirmed the verbatim text and the placement and said to commit before the render check (render_into renders HEAD). No change of plan resulted.
- Left the seed/docs/HARNESS.md "1125" table row alone: it is a v3.0.0 historical measurement, not a live assertion, and HARNESS.md is outside this ticket's edit scope.
- Committed dc3ef26f; done-checks from the worktree root printed PASS source-jinja, PASS in-render (rendered CLAUDE.md + AGENTS.md = 1500 bytes), PASS check-green (bin/check ran for real, LOAM_HOOK unset); no FAIL line.

~~~~~~~~~~~~ evidence

## Diff (6348dce8...HEAD)

~~~~~~~~~~~~ evidence
 seed/AGENTS.md.jinja | 6 ++++++
 1 file changed, 6 insertions(+)

diff --git a/seed/AGENTS.md.jinja b/seed/AGENTS.md.jinja
index 8f84114b..992e4717 100644
--- a/seed/AGENTS.md.jinja
+++ b/seed/AGENTS.md.jinja
@@ -17,6 +17,12 @@
 - Copier resolves git TAGS, not HEAD; run `copier update --trust`.
 - In YAML frontmatter, quote description strings containing colons.

+## Memory
+
+- Before you debug an error, run `bin/memsearch "<error string>"` to see whether a past session already hit it.
+- To read one past session, run `bin/mem-inspect <session> --summary`; never grep the raw traces under `.loam/memory`.
+- Recalled memory is evidence, not truth: label each item supported, contradicts, near-match, or insufficient before you act on it.
+
 ## Read on demand

 - `docs/HARNESS.md` - what the harness guards, what it does not, the accepted risks. Read it before editing a hook, `.claude/settings.json`, or `.codex/`.
~~~~~~~~~~~~ evidence
