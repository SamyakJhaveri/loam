// Source-unit extraction for the curated catalog (plan NATIVE-05 D7). Byte-exact and
// newline-preserving:
//  1. Split the raw bytes into lines at every 0x0a byte. Each line keeps its "\n". A final
//     unterminated line is a line too. A file with no 0x0a byte is one line. Lines are
//     numbered from 1. Digests always cover raw bytes; comparisons strip only a trailing
//     "\r\n" or "\n" and ignore a single leading U+FEFF on line 1.
//  2. Markdown-shaped files (.md, .md.jinja, or .txt beneath the intake sources directory)
//     receive structural units:
//     - frontmatter: line 1 compares equal to "---" and a later line compares equal to
//       "---"; the unit spans line 1 through the first such closing line. An unclosed block
//       is not frontmatter.
//     - Fenced code: outside a fence, /^ {0,3}(`{3,}|~{3,})/ opens a fence with that
//       character and run length; it closes only on a line of the same character with a run
//       at least as long followed by whitespace only. An unclosed fence runs to the end.
//     - HTML comments: outside a fence, /^ {0,3}<!--/ without "-->" enters comment state,
//       which ends on the first line containing "-->". Nothing inside opens a fence or a heading;
//       the active comment is closed before a new fence is recognized.
//     - heading: outside fences and comments, an ATX line /^ {0,3}#{1,6}([ \t]|$)/ starts a
//       unit spanning through the line before the next heading, or the last line.
//     - body: when headings exist, the lines after the frontmatter and before the first
//       heading, trimmed of leading and trailing blank lines; omitted when empty.
//     - paragraph: when a Markdown file has no headings, each run of non-blank lines after
//       the frontmatter; a fenced block counts as non-blank throughout.
//     - A Markdown file with at least one line but no unit receives one body unit.
//  3. Every other file receives one body unit spanning line 1 through the last line.
//  4. A unit's digest is SHA-256 over the concatenated raw bytes of its lines. IDs are
//     positional (`${entryId}:u${index}`), scoped to the parent file digest, and never
//     depend on heading text. Verification re-extracts and requires deep equality.
import { createHash } from 'node:crypto';
export const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
export function splitLines(bytes) {
    const lines = [];
    let start = 0;
    for (let i = 0; i < bytes.length; i++) {
        if (bytes[i] === 0x0a) {
            lines.push(bytes.subarray(start, i + 1));
            start = i + 1;
        }
    }
    if (start < bytes.length)
        lines.push(bytes.subarray(start));
    return lines;
}
export const isMarkdownPath = (path) => /\.md(\.jinja)?$/.test(path) || (/\.txt$/.test(path) && path.startsWith('docs/architecture-working/asset-intake/sources/'));
function compare(line, first) {
    let value = Buffer.from(line).toString('utf8').replace(/\r?\n$/, '');
    if (first && value.charCodeAt(0) === 0xfeff)
        value = value.slice(1);
    return value;
}
export function extractSourceUnits(entryId, path, bytes) {
    const lines = splitLines(bytes);
    const spans = [];
    if (!lines.length)
        return [];
    const texts = lines.map((line, i) => compare(line, i === 0));
    const blank = (i) => texts[i].trim() === '';
    if (!isMarkdownPath(path)) {
        spans.push({ role: 'body', start: 1, end: lines.length });
    }
    else {
        let index = 0;
        if (texts[0] === '---') {
            const close = texts.findIndex((value, i) => i > 0 && value === '---');
            if (close > 0) {
                spans.push({ role: 'frontmatter', start: 1, end: close + 1 });
                index = close + 1;
            }
        }
        const headings = [];
        const fencedLine = new Array(lines.length).fill(false);
        let fence = null;
        let comment = false;
        for (let i = index; i < lines.length; i++) {
            const value = texts[i];
            if (fence) {
                fencedLine[i] = true;
                const close = /^ {0,3}(`{3,}|~{3,})\s*$/.exec(value);
                if (close && close[1][0] === fence.char && close[1].length >= fence.length)
                    fence = null;
                continue;
            }
            // An active HTML comment is terminated before a new fence is recognized: a fence marker inside
            // an open comment is comment text, not a fence, so its closing `-->` and any later heading stay
            // visible. Checking the fence-open first would swallow the comment's close line into a fence.
            if (comment) {
                if (value.includes('-->'))
                    comment = false;
                continue;
            }
            const open = /^ {0,3}(`{3,}|~{3,})/.exec(value);
            if (open) {
                fence = { char: open[1][0], length: open[1].length };
                fencedLine[i] = true;
                continue;
            }
            if (/^ {0,3}<!--/.test(value) && !value.includes('-->')) {
                comment = true;
                continue;
            }
            if (/^ {0,3}#{1,6}([ \t]|$)/.test(value))
                headings.push(i);
        }
        if (headings.length) {
            let start = index;
            let end = headings[0] - 1;
            while (start <= end && blank(start))
                start++;
            while (end >= start && blank(end))
                end--;
            if (start <= end)
                spans.push({ role: 'body', start: start + 1, end: end + 1 });
            for (let h = 0; h < headings.length; h++) {
                const last = h + 1 < headings.length ? headings[h + 1] - 1 : lines.length - 1;
                spans.push({ role: 'heading', start: headings[h] + 1, end: last + 1 });
            }
        }
        else {
            let open = -1;
            for (let i = index; i <= lines.length; i++) {
                const gap = i === lines.length || (blank(i) && !fencedLine[i]);
                if (!gap && open < 0)
                    open = i;
                if (gap && open >= 0) {
                    spans.push({ role: 'paragraph', start: open + 1, end: i });
                    open = -1;
                }
            }
        }
        if (!spans.length)
            spans.push({ role: 'body', start: 1, end: lines.length });
    }
    return spans.map((span, i) => ({
        id: `${entryId}:u${i + 1}`, role: span.role, start: span.start, end: span.end,
        sha256: sha256(Buffer.concat(lines.slice(span.start - 1, span.end))),
    }));
}
// Throws when the recorded units are not exactly what the raw bytes produce.
export function verifySourceUnits(entryId, path, bytes, parentSha256, units) {
    if (sha256(bytes) !== parentSha256)
        throw new Error(`Source digest mismatch: ${entryId}`);
    const actual = extractSourceUnits(entryId, path, bytes);
    if (JSON.stringify(actual) !== JSON.stringify(units))
        throw new Error(`Source unit mismatch: ${entryId}`);
}
//# sourceMappingURL=units.js.map