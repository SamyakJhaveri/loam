#!/usr/bin/env python3
"""Deterministic style checks for outward-facing research text.

Catches mechanically what is mechanical, so the human pass can spend itself on
what is not. Every rule here traces to a defect that actually shipped: its
message names the failure it prevents (see --list).

Usage:
    python3 style_lint.py FILE [FILE ...]        # core rules
    python3 style_lint.py --house FILE           # + plain-text submission rules
    python3 style_lint.py --advisory FILE        # + low-precision prompts
    python3 style_lint.py --list                 # show all rules and their groups
    python3 style_lint.py --only ID,ID FILE      # run a subset (enables their groups)
    python3 style_lint.py --test                 # self-test on fixtures

A line containing `lint-ok` anywhere is skipped by every rule, so a document that
quotes bad prose on purpose (a style guide, a retrospective) stays lintable. The
suppression is per line by design; there is no way to switch a whole file off.

Exit status: 0 clean, 1 violations found, 2 usage error.
Stdlib only. No config file, no dependencies.
"""

import argparse
import re
import sys

# --------------------------------------------------------------------------
# Rules. Each is (id, group, compiled regex, message).
# group "core"  -> always on: defects no research prose wants.
# group "house" -> opt-in: tightenings for reviewer responses and rebuttals,
#                  where the published corpus does NOT support a blanket ban.
# --------------------------------------------------------------------------

# Passive constructions whose hidden agent is us, describing our own action.
# Genuine state descriptions (is frozen, is bounded, is running) are excluded by
# listing only verbs that name something a person did.
# Split deliberately. The core set is verbs performed on a document or a claim,
# where an agentless passive is almost always us hiding. The advisory set is
# ordinary mechanism verbs ("the halo region is updated at every timestep"),
# where the passive is usually correct and a flag is a prompt, not a defect.
OUR_ACTIONS = "corrected|fixed|resolved|audited|recomputed|re-run|rerun|retracted"
OUR_ACTIONS_ADVISORY = (
    "marked|updated|verified|characterized|characterised|implemented|"
    "removed|excluded|documented|added|delivered|labeled|labelled"
)

# Shared by both branches of adjective-near-count so they cannot drift apart.
SOFT_ADJ = "low|negligible|minimal|small|tiny|modest"
COUNT_NOUN = r"false positives?|error rate|failure rate|mismatch(?:es)?|defects?"

RULES = [
    (
        # LaTeX writes an em dash as ---, which is ASCII and so escapes the
        # non-ascii rule. A house rule against the em dash covers paper sources too.
        "latex-emdash",
        "core",
        re.compile(r"(?<!-)---(?!-)"),
        "LaTeX em dash (---). Use a plain dash or rewrite the sentence.",
    ),
    # ---- voice and framing ------------------------------------------------
    (
        "disposition",
        "core",
        re.compile(
            r"\bwe (want to be|think that was|think it|would rather|feel that|"
            r"believe it deserves)\b|\brather than a defen[cs]e\b|"
            r"\bwe want to be straight\b|\bwe would rather show\b",
            re.I,
        ),
        "Disposition framing: the subject is the authors' attitude, not the finding. "
        "Delete the clause and keep the action or the number.",
    ),
    (
        "meta-commentary",
        "core",
        # Sentence-anchored, not line-anchored: rebuttal text is unwrapped prose,
        # so ^ with re.M would miss every mid-paragraph instance.
        re.compile(
            r"(?:^|(?<=[.!?]\s))(This (response|reply|document|paper|section) "
            r"(shows|demonstrates|argues)"
            r"|One point runs through"
            r"|All numbers below"
            r"|For the record"
            r"|One (methods )?note for the record)",
            re.I | re.M,
        ),
        "Sentence about the document itself. Outward text makes claims about the "
        "world, not about its own structure or epistemics.",
    ),
    (
        "self-congratulation",
        "core",
        re.compile(
            r"\bwe (state|disclose|show) (it |this )?(ourselves|rather than assert)\b"
            r"|\bwhich is itself worth stating\b",
            re.I,
        ),
        "Narrating your own disclosure awards yourself credit for it. Keep the "
        "disclosure; delete the narration.",
    ),
    (
        "passive-our-action",
        "core",
        # "is fixed BY the thread count" states its agent and is not about us;
        # "is fixed" with no agent is the defect.
        re.compile(
            r"\b(is|are|was|were|has been|have been|will be)\s+(" + OUR_ACTIONS + r")\b(?!\s+by\b)",
            re.I,
        ),
        "Passive report of our own action. Use first person with a tense that says "
        "whether it is done: 'We have corrected X', not 'X is corrected'.",
    ),
    (
        "passive-mechanism-verb",
        "advisory",
        re.compile(
            r"\b(is|are|was|were|has been|have been|will be)\s+("
            + OUR_ACTIONS_ADVISORY
            + r")\b(?!\s+by\b)",
            re.I,
        ),
        "Agentless passive. Often correct for a mechanism ('the halo region is "
        "updated each timestep'); a defect when the hidden agent is us.",
    ),
    (
        "hedged-diligence",
        "core",
        re.compile(
            r"\bwe did our best\b|\bdue to time constraints\b|\bas far as we could\b"
            r"|\bwe tried to ensure\b|\bto the extent possible\b",
            re.I,
        ),
        "Hedge on your own diligence. Hedge the world, never your effort. "
        "State what you did and did not cover instead.",
    ),
    (
        "should-work",
        "core",
        re.compile(r"\b(should|ought to|probably) (work|pass|be fine|be correct)\b", re.I),
        "Modal about your own change. Run it, or write what is not verified and why.",
    ),
    # ---- commitments ------------------------------------------------------
    (
        "vague-timing",
        "core",
        # Match the commitment, not one phrasing: any reference to the period
        # itself fires, whatever preposition introduces it.
        re.compile(
            r"\b(discussion|response|rebuttal|review)\s+(period|window|phase|round)\b"
            r"|\bin the coming (weeks|days|months)\b"
            r"|\b(in due course|as soon as possible)\b"
            r"|\bshortly\b(?!\s+(after|before|thereafter|afterwards))"
            r"|\bwe will .{0,40}\bsoon\b",
            re.I,
        ),
        "Unfalsifiable timing. Give a calendar date and the delivery channel.",
    ),
    (
        "deferred-correction",
        "core",
        re.compile(
            r"\bwill be (corrected|fixed|reported|addressed) (for|at|in) (the )?camera[- ]ready\b",
            re.I,
        ),
        "Deferring an already-computed correction reads as concealment. Put the "
        "corrected value in this document, or give a date.",
    ),
    # ---- numbers ----------------------------------------------------------
    (
        "adjective-near-count",
        "core",
        re.compile(
            r"\b(" + SOFT_ADJ + r")\b[^.]{0,60}?\b(" + COUNT_NOUN + r")"
            r"|\b(" + COUNT_NOUN + r")[^.]{0,60}?\b(" + SOFT_ADJ + r")\b",
            re.I,
        ),
        "Evaluative adjective next to an unfinished measurement. Raw counts only, "
        "with the denominator.",
    ),
    (
        "bare-numerator",
        "core",
        re.compile(
            r"\b\d{1,4}\s+(false positives?|errors?|mismatches?|failures?|defects?)\b",
            re.I,
        ),
        "Count without its denominator. Write 'N of M' or 'N/M'; a defect count "
        "always carries its population.",
        # Suppressed when the same sentence contains a denominator - see check().
    ),
    (
        "unscoped-superlative",
        "core",
        re.compile(
            r"\b(hardest|easiest|largest|smallest|best|worst|strongest|weakest)\b"
            r"[^.\n]{0,60}?\d+(\.\d+)?\s*(%|/\s*\d)",
            re.I,
        ),
        "Ranking superlative in a results sentence. Re-derive it against the current "
        "data cut before shipping - superlatives survive silently across cuts and go "
        "false. Prefer a named comparison ('substantially harder than the pooled rest').",
    ),
    (
        "false-equivalence",
        "core",
        # Not a bare "equivalent", which is often a defined term ("an equivalent
        # test suite"), and not a bare "no difference", which is a legitimate
        # finding when it has evidence behind it.
        re.compile(
            r"(?<![-\w])(statistically\s+)?(inseparable|indistinguishable)\b"
            r"|(?<![-\w])statistically\s+(equivalent|the same)\b",
            re.I,
        ),
        "Overlapping intervals do not establish equivalence. Say 'near-tied' or "
        "state the test that supports the claim.",
    ),
    # ---- reference and precision ------------------------------------------
    (
        "bare-this",
        "advisory",
        re.compile(r"(?:^|(?<=[.!?]\s))(This|These|That|It) (is|are|was|were|leads|shows|means)\b"),
        "Nonreferential 'this'. Put a noun after it: 'This reaction is fast'.",
    ),
    (
        "various-reasons",
        "core",
        re.compile(r"\bfor various reasons\b|\b(,|\s)etc\.", re.I),
        "Name the reasons. Name the items.",
    ),
    (
        # House, not core: a paper section legitimately contains a micro sign, a
        # section mark, and accented author names. Only plain-text submission
        # boxes require pure ASCII.
        "non-ascii",
        "house",
        re.compile(r"[^\x00-\x7F]"),
        "Non-ASCII character. Em dashes, en dashes and smart quotes break plain-text "
        "submission boxes and byte-vs-character counts.",
    ),
    # ---- house rules (opt-in) ---------------------------------------------
    (
        "house-connectives",
        "house",
        re.compile(r"\b(Moreover|Furthermore)\b|\bIt is worth noting\b|\bimportantly\b", re.I),
        "House rule for reviewer responses. Note: published papers use these "
        "connectives freely, so this is a document-class tightening, not a "
        "property of good prose.",
    ),
    (
        "house-provenance-furniture",
        "house",
        re.compile(r"\((proven|verified|confirmed) by command\)", re.I),
        "Provenance format contract leaking into prose. Move the command to a "
        "companion table with a `command` column.",
    ),
    # ---- ported from the avoid-ai-writing skill ---------------------------
    # Only the rows that are real tells in research prose. `robust` and
    # `comprehensive` are deliberately excluded: published papers use both
    # freely. `leverage`, `underscores`, `pivotal` and `meticulous` are also
    # excluded until a word-frequency count over saved paper texts settles
    # them - default to not banning an unverified term rather than guessing.
    (
        "sycophantic-tone",
        "house",
        # The "!" is load-bearing: it is what separates the chatbot tic
        # ("Excellent point!") from the courteous academic phrasing research
        # prose actually uses ("we thank the reviewer for this excellent
        # point"). Dropping the exclamation would false-positive on that.
        re.compile(
            r"\b(Great question|Excellent point|You're absolutely right|"
            r"That's a really insightful observation)!",
            re.I,
        ),
        "Chatbot validation tic. Answer the point directly; the reader does "
        "not need to be told the question was good.",
    ),
    (
        "cutoff-disclaimer",
        "house",
        re.compile(
            r"\bas of my last update\b"
            r"|\bi don't have access to real[- ]time data\b"
            r"|\bwhile specific details are limited based on available information\b",
            re.I,
        ),
        "Model-limitation leaking into prose. Look the fact up, or state "
        "plainly what is not known and why - never publish a hedge that "
        "admits the writer didn't check.",
    ),
    (
        "significance-inflation",
        "house",
        re.compile(
            r"\bpivotal moment\b|\bwatershed moment\b"
            r"|\bmarking a\b[^.\n]{0,40}\bmoment\b",
            re.I,
        ),
        "Inflates a routine event into a historic one. State what happened "
        "and let the reader judge significance.",
    ),
    (
        "acknowledgment-loop",
        "house",
        re.compile(r"\bto answer your question\b|\byou're asking about\b", re.I),
        "Restates the prompt before answering. The reviewer knows what they asked - just answer.",
    ),
    (
        "tier1-jargon",
        "house",
        re.compile(
            r"\bdelve\b|\bgame-chang(?:er|ing)\b|\btestament to\b"
            r"|\bcutting-edge\b|\bseamless(?:ly)?\b",
            re.I,
        ),
        "AI-tell vocabulary research prose does not use. Say what specifically "
        "changed instead (e.g. 'seamless' -> describe what has no friction).",
    ),
    (
        "hollow-intensifier",
        "advisory",
        # Adverb forms only, not bare "genuine": a phrase such as "a genuine
        # speedup" is legitimate, and bare "genuine" would false-positive on it.
        re.compile(r"\bgenuinely\b|\btruly\b|\bquite frankly\b|\bto be honest\b", re.I),
        "Padding intensifier. State the fact directly without the filler.",
    ),
]

# A 4-digit year is not a population: "4 failures in 2026" must still fire.
DENOMINATOR = re.compile(r"/\s*\d|\b(of|out of|in|from|among|the)\s+(?!\d{4}\b)\d")
# Split on sentence enders AND on line/list boundaries, so a bullet list of bare
# counts is not treated as one long sentence.
SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n\s*(?:[-*+]|\d+\.)\s+|\n{2,}|\n(?=\|)")


def sentences_with_offsets(text):
    """Yield (sentence, absolute_start_offset)."""
    pos = 0
    for part in SENTENCE_SPLIT.split(text):
        idx = text.find(part, pos)
        if idx < 0:
            idx = pos
        yield part, idx
        pos = idx + len(part)


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def squash(s):
    """Collapse whitespace so a hard-wrapped match prints on one line."""
    return " ".join(s.split())


def check(text, groups, only=None):
    """Return a list of (line, rule_id, matched_text, message)."""
    findings = []
    for rule in RULES:
        rid, group, pattern, message = rule
        if group not in groups:
            continue
        if only and rid not in only:
            continue

        if rid == "bare-numerator":
            # Sentence-scoped, with two suppressions. The bare count is only a
            # defect when it stands alone as a claim: a denominator anywhere in the
            # sentence, and a parenthesised label breakdown ("(12 Confirmed, 2 False
            # positive, 5 Indeterminate)") whose total precedes it, both carry the
            # population by construction. Every match is reported - two orphaned
            # counts in one sentence is a worse defect than one, not an exemption.
            for sent, start in sentences_with_offsets(text):
                if DENOMINATOR.search(sent):
                    continue
                for m in pattern.finditer(sent):
                    inside_parens = sent.rfind("(", 0, m.start()) > sent.rfind(")", 0, m.start())
                    if inside_parens:
                        continue
                    line = line_of(text, start + m.start())
                    if text.splitlines()[line - 1].lstrip().startswith("|"):
                        continue
                    findings.append((line, rid, squash(m.group(0)), message))
            continue

        for m in pattern.finditer(text):
            snippet = squash(m.group(0))
            if rid == "non-ascii":
                snippet = "U+%04X %r" % (ord(m.group(0)[0]), m.group(0)[0])
            findings.append((line_of(text, m.start()), rid, snippet, message))

    # Line-level suppression. A document that *quotes* bad prose - a style guide, a
    # retrospective, this file's own fixtures - would otherwise be unlintable. Mark
    # the line with `lint-ok` (in an HTML comment, a code span, whatever the format
    # allows) and every rule skips it. Deliberately line-scoped, not file-scoped:
    # you cannot switch the linter off for a whole document.
    suppressed = {i for i, ln in enumerate(text.splitlines(), 1) if "lint-ok" in ln}
    if suppressed:
        findings = [f for f in findings if f[0] not in suppressed]

    findings.sort(key=lambda f: (f[0], f[1]))
    return findings


def report(path, findings):
    if not findings:
        print("%s: clean" % path)
        return
    print("%s: %d violation(s)" % (path, len(findings)))
    seen_msg = set()
    for line, rid, snippet, message in findings:
        print("  %s:%d  [%s]  %s" % (path, line, rid, snippet))
        if rid not in seen_msg:
            print("      -> %s" % message)
            seen_msg.add(rid)


# --------------------------------------------------------------------------
# Self-test: one violating and one clean fixture per rule.
# --------------------------------------------------------------------------

FIXTURES = [
    # (rule_id, dirty, clean)
    (
        "latex-emdash",
        "The cache---which we profiled---evicts the oldest entry.",
        "The cache, which we profiled, evicts the oldest entry.",
    ),
    (
        "disposition",
        "We have not run a fourth workload, and we want to be straight about why.",
        "We have not run a fourth workload.",
    ),
    (
        "meta-commentary",
        "One point runs through all three items: every change makes the estimate more cautious.",
        "We completed the check the reviewers asked for: a rerun of all 120 trials.",
    ),
    (
        "self-congratulation",
        "One caveat we state ourselves: the label appears once in a derived table.",
        "One caveat: the label appears once in a derived table.",
    ),
    (
        "passive-our-action",
        "The timing table is corrected in this version.",
        "We have corrected the timing table in this version.",
    ),
    (
        "passive-mechanism-verb",
        "The outlier run is marked as excluded.",
        "We marked the outlier run as excluded.",
    ),
    (
        "hedged-diligence",
        "We did our best to cover the remaining cases.",
        "We covered 18 of the 60 cases; the rest are untested.",
    ),
    (
        "should-work",
        "The patched allocator should work on the multi-socket path.",
        "The patched allocator passes 5 of 5 multi-socket tests.",
    ),
    (
        "vague-timing",
        "We will complete the analysis during the discussion period.",
        "We will complete the analysis by March 3 and post it in this thread.",
    ),
    (
        "deferred-correction",
        "The rounding defect will be corrected for camera-ready.",
        "We correct the rounding defect here: under the corrected rule, one result changes.",
    ),
    (
        "adjective-near-count",
        "The false positive rate is low across the checked samples.",
        "We found 2 false positives in 30 checked samples and quote no rate.",
    ),
    (
        "bare-numerator",
        "The manual check found 2 false positives.",
        "The manual check found 2 false positives in 30 samples.",
    ),
    (
        "unscoped-superlative",
        "The sparse suite stays hardest, at 41.0% against the pooled rest.",
        "The sparse suite is substantially harder than the pooled rest, 41.0% against 68.5%.",
    ),
    (
        "false-equivalence",
        "The two top configurations are statistically inseparable.",
        "Both builds run an equivalent test suite; the top two configurations are near-tied.",
    ),
    (
        "bare-this",
        "This is a fast path under the new allocator.",
        "This path is fast under the new allocator.",
    ),
    (
        "various-reasons",
        "We excluded four inputs for various reasons.",
        "We excluded four inputs: two for missing files, two for a timeout.",
    ),
    (
        "non-ascii",
        "The change \u2014 which we found late \u2014 moves one result.",
        "The change, which we found late, moves one result.",
    ),
    (
        "house-connectives",
        "Moreover, the rerun reproduces every recorded result.",
        "The rerun also reproduces every recorded result.",
    ),
    (
        "house-provenance-furniture",
        "No trial uses either input file (verified by command).",
        "No trial uses either input file, so no timing changes.",
    ),
    (
        "sycophantic-tone",
        "Great question! We will post the fix by March 3, 2030 in this thread.",
        "We thank the reviewer for this excellent point; we will post the fix by "
        "March 3, 2030 in this thread.",
    ),
    (
        "cutoff-disclaimer",
        "As of my last update, the skip list held nine inputs.",
        "As of 2030-01-15, the skip list holds ten inputs.",
    ),
    (
        "significance-inflation",
        "This release marks a pivotal moment in the evolution of the scheduler.",
        "This release changes three defaults in the scheduler.",
    ),
    (
        "acknowledgment-loop",
        "To answer your question, the gap comes from a stale cached log.",
        "The gap comes from a stale cached log.",
    ),
    (
        "tier1-jargon",
        "This cutting-edge, seamless pipeline is a testament to careful engineering; "
        "we won't delve into implementation details here.",
        "This pipeline runs without manual steps; we describe the implementation in section 4.",
    ),
    (
        "hollow-intensifier",
        "The fix is genuinely, truly the right call here, to be honest.",
        "The fix removes the race condition in queue.c:88.",
    ),
]


def self_test():
    groups = {"core", "house", "advisory"}
    failures = 0
    for rid, dirty, clean in FIXTURES:
        got_dirty = [f[1] for f in check(dirty, groups, only={rid})]
        got_clean = [f[1] for f in check(clean, groups, only={rid})]
        if rid not in got_dirty:
            print("FAIL %-28s did not fire on its violating fixture" % rid)
            failures += 1
        if got_clean:
            print("FAIL %-28s fired on its clean fixture: %r" % (rid, clean))
            failures += 1

    covered = {f[0] for f in FIXTURES}
    for rule in RULES:
        if rule[0] not in covered:
            print("FAIL %-28s has no fixture" % rule[0])
            failures += 1

    # Line-level suppression: the same text fires, then does not, with the marker.
    for fixture in FIXTURES:
        rid, first = fixture[0], fixture[1].splitlines()[0]
        if check(first, groups, only={rid}) and not check(
            first + "  <!-- lint-ok -->", groups, only={rid}
        ):
            continue
        print("FAIL %-28s lint-ok suppression did not work" % rid)
        failures += 1

    total = len(RULES)
    if failures:
        print("\n%d check(s) failed across %d rules." % (failures, total))
        return 1
    print("%d rules, %d fixtures, 0 failures." % (total, len(FIXTURES) * 2))
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    p.add_argument("files", nargs="*", help="text files to lint")
    p.add_argument(
        "--house", action="store_true", help="also apply the strict reviewer-response house rules"
    )
    p.add_argument(
        "--advisory",
        action="store_true",
        help="also apply low-precision advisory rules (expect false positives)",
    )
    p.add_argument("--only", help="comma-separated rule ids to run")
    p.add_argument("--list", action="store_true", help="list rules and exit")
    p.add_argument("--test", action="store_true", help="run the self-test and exit")
    args = p.parse_args(argv)

    if args.test:
        return self_test()

    if args.list:
        for rid, group, _, message in RULES:
            print("%-28s %-6s %s" % (rid, group, message.split(".")[0] + "."))
        return 0

    if not args.files:
        p.print_usage(sys.stderr)
        print("error: no files given (or use --test / --list)", file=sys.stderr)
        return 2

    groups = {"core"}
    if args.house:
        groups.add("house")
    if args.advisory:
        groups.add("advisory")
    only = None
    if args.only:
        only = {r.strip() for r in args.only.split(",") if r.strip()}
        known = {r[0]: r[1] for r in RULES}
        unknown = only - set(known)
        if unknown:
            print("error: unknown rule id(s): %s" % ", ".join(sorted(unknown)), file=sys.stderr)
            print("       run --list to see all rule ids", file=sys.stderr)
            return 2
        # Naming a rule explicitly enables its group; otherwise --only on a
        # non-core rule would report clean and exit 0.
        groups |= {known[r] for r in only}

    total = 0
    for path in args.files:
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            if path.endswith(".tex"):
                # A whole-line LaTeX comment is not prose. Blank it and keep the
                # line numbers, so findings still point at the right line.
                text = "\n".join(
                    "" if ln.lstrip().startswith("%") else ln for ln in text.splitlines()
                )
        except OSError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 2
        findings = check(text, groups, only)
        total += len(findings)
        report(path, findings)

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
