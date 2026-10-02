# Figure checklist

Run every item on each figure and its caption in the built PDF (`build.pdf` in `paper/tools/paper-tools.toml`).
Answer each item yes or no.
Answer n/a only when the item names a figure type (plot, bar chart, line chart, scatter plot, heatmap, diagram, TikZ fragment, raster image) that the figure is not.
Each "no" is a finding: record the figure label, the source file and line, and the item number.
Each item ends with its source: `repo@commit path:lines`, `contract` (the venue's rules in `paper/tools/contract.md` section 2), `plugin` (a file of this plugin), or `project` (a file the project keeps).
Short names: `PB` = paperbanana@87e01fd, `ARS` = academic-research-skills@e79085d, `CCW` = claude-code-my-workflow@ae72617 (full references at the end).

Commands the items refer to, run from the project root, with `PDF=$(paper-tool paper_config build.pdf)`:
- Font sizes: the document class sets them; for example, IEEEtran at 10 pt sets `\footnotesize` to 8 pt, `\scriptsize` to 7 pt and `\tiny` to 5 pt (IEEEtran.cls in TeX Live 2022, lines 658-660).
- Greyscale render of page N: `pdftoppm -gray -r 150 -f N -l N -png "$PDF" "$TMPDIR/pageN"`.
- Raster resolution: `pdfimages -list "$PDF"` (columns x-ppi and y-ppi).
- Figure uses in the body text: `grep -n 'ref{fig:' paper/sections/*.tex` (the folder `paper.sections_dir` names).
- TikZ rules: `paper-tool check_tikz_prevention FILE.tex ...` on every TikZ source, for example `paper/figures/*.tex` (the folder `paper.figures_dir` names).

## Legibility at print size

1. Every text element in the printed figure is at least 8 pt; with no scaling applied, the fragment's font keys are `\footnotesize` or larger. [PB data/guidelines/ieee/plot_style_guide.md:11-15,101; PB data/guidelines/ieee/methodology_style_guide.md:14-16]
2. The figure is drawn at its printed width: no `\resizebox`, `\scalebox` or graphic `width=` shrinks a figure that contains text. [PB data/guidelines/ieee/plot_style_guide.md:101; PB data/guidelines/ieee/methodology_style_guide.md:103-104]
3. No text overlaps a line, arrow, shape, hatching, grid line or other text. [PB prompts/evaluation/readability.txt:26; PB prompts/plot/critic.txt:19]
4. Every arrow can be followed from start to end, with no loop and no crossing that another routing would avoid. [PB prompts/evaluation/readability.txt:27]
5. Labels with the same role (box text, tick labels, legend entries) share one font size. [PB prompts/evaluation/readability.txt:28]
6. No light text sits on a light fill and no dark text on a dark fill. [PB prompts/evaluation/readability.txt:29]
7. The figure contains no caption text, figure title, duplicated label or watermark; panel labels (a), (b) are allowed. [PB prompts/evaluation/readability.txt:20-25; PB prompts/plot/critic.txt:16; PB prompts/diagram/critic.txt:16]
8. The figure fills a compact rectangle: no legend or panel sticks out of the main block, and no corner is left mostly empty. [PB prompts/evaluation/readability.txt:30-34]
9. The figure background is white. [PB prompts/evaluation/readability.txt:35; PB data/guidelines/ieee/methodology_style_guide.md:45-46]
10. Every raster image is above 300 ppi at printed size (above 600 ppi for black-and-white line art), and line art is vector (PDF or TikZ). [PB data/guidelines/ieee/plot_style_guide.md:18-20]
11. A TikZ fragment passes `check_tikz_prevention.py`: it has no bare `scale=` (P3), and every `\draw` edge label has `above`, `below`, `left` or `right` (P4). [CCW scripts/check-tikz-prevention.py:8-11; plugin: scripts/check_tikz_prevention.py]

## Encoding and colour

12. Rendered in greyscale, the figure still shows every category, series and status as distinct. [PB data/guidelines/ieee/plot_style_guide.md:28-31,39-40; PB data/guidelines/ieee/methodology_style_guide.md:39-41; contract]
13. No encoding uses colour alone: each colour-coded category also differs by line style, marker, hatching, position or a text label. [PB data/guidelines/ieee/plot_style_guide.md:98-99; PB data/guidelines/ieee/methodology_style_guide.md:110-111; contract]
14. No two categories differ only by a red-green hue contrast. [contract]
15. A plot uses at most 5 categorical colours and a diagram at most 4. [PB data/guidelines/ieee/plot_style_guide.md:41-42; PB data/guidelines/ieee/methodology_style_guide.md:58-59]
16. A heatmap uses a greyscale or viridis colour scale, and each cell carries its value or status letter. [PB data/guidelines/ieee/plot_style_guide.md:43,86-88]
17. Every bar has a thin black outline and carries hatching or a direct label. [PB data/guidelines/ieee/plot_style_guide.md:44-45,77-80]
18. In a line chart, each series differs from every other in both line style and marker. [PB data/guidelines/ieee/plot_style_guide.md:71-75]
19. In a scatter plot, groups differ by marker shape or by open versus filled markers. [PB data/guidelines/ieee/plot_style_guide.md:82-84]
20. The legend shows each series' line style or marker, not only a colour swatch. [PB data/guidelines/ieee/plot_style_guide.md:61-62]
21. A colour or line style means the same thing in every figure of the paper, for example one colour per result status. [PB data/guidelines/ieee/plot_style_guide.md:102]
22. Diagram blocks are white or light grey with dark borders, and any colour only adds to a difference that a label or shape already shows. [PB data/guidelines/ieee/methodology_style_guide.md:43-49,55-56]

## Caption fidelity trace

Scope: this group checks captions and claims against their recorded sources; it does not judge whether an experiment was designed or run well. [ARS academic-pipeline/agents/integrity_verification_agent.md:318]

23. The figure has a trace entry with six fields: figure label, source data file, transformation, caption claims, body sentences that use the figure, and known limitations (an empty limitations list is allowed; a missing field fails). [ARS academic-pipeline/agents/integrity_verification_agent.md:233-241]
24. The source data is a real file in the project, and the transformation is a script path or a claims-file `json_path`; "computed by hand" or "see paper" fails. [ARS academic-pipeline/agents/integrity_verification_agent.md:243-247]
25. Every number in the caption and every number drawn in the figure has a source in the trace: a `claim_id` in the project's claims file, a `\pending{Pn}` id, or a file and line for a design constant (for example a plan or a config file). [ARS academic-pipeline/agents/integrity_verification_agent.md:243-247; project: the claims file and the placeholder registry]
26. Each traced number equals its source value at the printed precision, and so do its interval and n where the claims entry has `ci_lower`, `ci_upper` and `n`. [ARS academic-pipeline/agents/integrity_verification_agent.md:368-383; project: the claims file]
27. Each interpretive statement in the caption (a comparison, a trend, "most", "all") follows from the traced data; not being contradicted is not enough. [ARS academic-pipeline/agents/integrity_verification_agent.md:249-255]
28. Each compound caption statement is split into single claims, and every one of them passes; one unsupported part fails the caption. [ARS academic-pipeline/agents/integrity_verification_agent.md:256-262]
29. Every body sentence listed in the trace cites the figure and claims no more than the figure shows. [ARS academic-pipeline/agents/integrity_verification_agent.md:264-267]
30. Every body sentence that uses the figure as evidence for a data claim is listed in the trace; a bare pointer such as "see Fig. 2" is exempt. [ARS academic-pipeline/agents/integrity_verification_agent.md:268-279]
31. Every known limitation in the trace (excluded cases, pending values, one configuration, one input) is stated in the caption, the Discussion or a limitations passage. [ARS academic-pipeline/agents/integrity_verification_agent.md:281-285]
32. No caption or figure claim rests on a run that did not execute, or on a pending value presented as final. [ARS academic-pipeline/agents/integrity_verification_agent.md:361-366]
33. No caption or figure claim is stronger than its claims entry supports; "overstated" or "not supported" fails, and "insufficient detail" is recorded as a note, never passed silently. [ARS academic-pipeline/agents/integrity_verification_agent.md:375-378]
34. No caption or figure claim asserts an effect that a null or negative result reported in the paper contradicts. [ARS academic-pipeline/agents/integrity_verification_agent.md:369-374]
35. Every pending value in a figure or caption is set with `\pending` or `\pendingcell` (red), and its id has a row in the project's placeholder registry. [project: the macro file that defines `\pending`; the placeholder registry]

## Faithfulness to data

36. Every data point in the source appears in the plot, and none is invented, omitted or misrepresented. [PB prompts/plot/critic.txt:13]
37. Axis scales, tick values and every plotted value agree with the source data. [PB prompts/plot/critic.txt:15]
38. For each figure a script draws from data, the project's figure check reports no mismatch between the figure and its source data. [project: the figure check script, when there is one]
39. For the same figures, a dry run of the script that writes them would change nothing. [project: the figure generator]
40. Numbers are read from the live part of a figure source, not from a commented prior revision. [project: the figure sources]
41. A comment that mirrors data inside a figure source (for example values written beside the table that draws them) equals that data. [project: the figure sources]
42. In a heatmap, each cell's fill colour and its letter give the same status. [project: the figure sources]
43. Every box, arrow and label in a diagram has a direct basis in the method text or its plan file, with no invented module, entity or connection. [PB prompts/evaluation/faithfulness.txt:13,21; PB prompts/diagram/critic.txt:13]
44. The diagram's flow matches the described method, with no reversed data direction, no skipped step and no missing required connection. [PB prompts/evaluation/faithfulness.txt:22]
45. The diagram shows only what its caption says it shows. [PB prompts/evaluation/faithfulness.txt:23]
46. No garbled text, fake notation, broken LaTeX, hex colour code or dimension appears as text in the figure. [PB prompts/evaluation/faithfulness.txt:24; PB prompts/diagram/critic.txt:14]
47. Every example inside a diagram (a sample output, a code line, a formula) is correct. [PB prompts/diagram/critic.txt:15]
48. Every label, legend entry and annotation is spelled correctly and clear, and a name that also appears in the body text is spelled the same way. [PB prompts/plot/critic.txt:14; PB prompts/diagram/critic.txt:14]

## The venue's figure rules, from the contract

Take the venue's figure rules from `paper/tools/contract.md` section 2.
Items 49 to 52 name what to look up there; the values in parentheses are IEEE's, from the PB guides, as an example.
Items 53 to 62 come from the same guides and hold for most venues; drop one only when the contract's rules say otherwise.

49. The caption sits where the venue's rules put it and starts with the venue's label (IEEE: below the figure, "Fig. N."). [contract; PB data/guidelines/ieee/plot_style_guide.md:11-13,63]
50. The figure float is placed where the venue's rules allow (IEEE: at the top or bottom of a column, `[t]` or `[b]`, not mid-column). [contract; PB data/guidelines/ieee/plot_style_guide.md:21-22]
51. The figure is no wider than the venue's column or page width (IEEE: 3.5 in for `figure`, 7.16 in for `figure*`), and the build log (`build.log` in the config) has no `Overfull \hbox` at the figure's source lines. [contract; PB data/guidelines/ieee/plot_style_guide.md:5-8]
52. Figure text uses the body font family of the venue's template (IEEE: Times). [contract; PB data/guidelines/ieee/plot_style_guide.md:14-15,58-60; PB data/guidelines/ieee/methodology_style_guide.md:85-87]
53. Every axis label is a word or phrase with units in parentheses, such as "Success rate (%)"; no axis is labelled with units alone or with an unexplained symbol. [PB data/guidelines/ieee/plot_style_guide.md:14-17,52-54,100]
54. A multi-panel figure labels its panels (a), (b), (c) at the top left of each panel. [PB data/guidelines/ieee/plot_style_guide.md:64-65,104]
55. The figure has no 3D effect, shadow or gradient. [PB data/guidelines/ieee/plot_style_guide.md:103; PB data/guidelines/ieee/methodology_style_guide.md:116]
56. A plot has light grey dotted or dashed grid lines, a full box frame and inward ticks. [PB data/guidelines/ieee/plot_style_guide.md:49-51]
57. Diagram connectors are straight or right-angled, not curved. [PB data/guidelines/ieee/methodology_style_guide.md:80-81]
58. Diagram blocks align to a grid, and related blocks share dimensions. [PB data/guidelines/ieee/methodology_style_guide.md:98,115]
59. A pipeline diagram runs left to right, and a layered diagram top to bottom. [PB data/guidelines/ieee/methodology_style_guide.md:96-97]
60. Every arrow carries a label on or beside it, unless the two boxes it joins already make its meaning plain. [PB data/guidelines/ieee/methodology_style_guide.md:88,114]
61. The figure and its caption can be understood without the body text. [PB data/guidelines/ieee/methodology_style_guide.md:101-102]
62. Fonts, line widths and palette match the other figures in the paper. [PB data/guidelines/ieee/plot_style_guide.md:102]

## Sources

- PB: https://github.com/llmsresearch/paperbanana at 87e01fd8aba2b3bc55abbe9b8826ff73f5696797, MIT license (Copyright (c) 2025 PaperBanana Contributors).
  Files read whole: `data/guidelines/ieee/plot_style_guide.md`, `data/guidelines/ieee/methodology_style_guide.md`, `prompts/plot/critic.txt`, `prompts/diagram/critic.txt`, `prompts/evaluation/faithfulness.txt`, `prompts/evaluation/readability.txt`.
  The items cite the lines actually used.
- ARS: https://github.com/imbad0202/academic-research-skills at e79085d0d38609984ef8cfe0faf2d254aac9e0a9, `academic-pipeline/agents/integrity_verification_agent.md` lines 226-312 (C3, caption fidelity) and 314-400 (C4, claim alignment).
  Licensed CC BY-NC 4.0 (Copyright (c) 2026 Cheng-I Wu, https://creativecommons.org/licenses/by-nc/4.0/).
  Changed: items 23-35 restate C3 and C4 as yes-or-no items for this paper, with this repository's claims file and placeholder register in place of the Figure Package trace and the experiment passport; no text is copied.
- CCW: https://github.com/pedrohcgs/claude-code-my-workflow at ae726177e23426b665e0a1eef5fb5bd83bd5b831, MIT license; `scripts/check-tikz-prevention.py`, copied to this plugin's `scripts/check_tikz_prevention.py` with the changes listed in its header.
- contract: the venue's rules in `paper/tools/contract.md` section 2, quoted there from the call for papers (for example a rule that figures be readable by color-blind readers).
- project: the project's own files that the items name (the claims file, the placeholder registry, the figure sources and the scripts that draw them).
