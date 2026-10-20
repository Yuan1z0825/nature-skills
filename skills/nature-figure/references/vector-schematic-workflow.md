# Vector Schematic Workflow

Use this reference when the user wants a **hand-built, editable vector schematic**
for a manuscript: a system or method architecture, a pipeline overview, an
agent or model block diagram, or a mechanism or process flow. This is the
deterministic, non-image-model counterpart of the AI route in
[ai-graphical-abstract-workflow.md](ai-graphical-abstract-workflow.md). It does
not plot data, so it skips the Python/R backend gate.

Do not use it for quantitative panels. Do not invent components, flows, or
numbers the author did not supply.

## Contents

- [Why a vector schematic](#why-a-vector-schematic)
- [1. Write a brief and get it confirmed](#1-write-a-brief-and-get-it-confirmed)
- [2. Fix the canvas from the journal](#2-fix-the-canvas-from-the-journal)
- [3. Pick the arrangement](#3-pick-the-arrangement)
- [4. Draw the SVG](#4-draw-the-svg)
- [5. Check, look, fix](#5-check-look-fix)
- [6. Deliver](#6-deliver)
- [Optional companion and credit](#optional-companion-and-credit)

## Why a vector schematic

A figure drawn as SVG keeps live text and shapes, so authors and production
editors can change a label without regenerating an image. It also makes the
final-size checks below computable instead of a matter of eyeballing a bitmap.

## 1. Write a brief and get it confirmed

Before drawing, write a short brief in the user's language and have the user
confirm it. Infer first and ask second: ask only what changes the structure and
cannot be read from the material, at most three points in one message, each
phrased as your guess plus the alternative.

The brief states:

1. What the figure is: the system, the scope (whole system, one subsystem, one
   path), where it sits in the paper, single or double column.
2. Every component with its exact label, one clause on its job, its container,
   and a tag: **new** (the paper's contribution), existing, or external.
3. The main path as numbered steps ("from, to, what moves"), then secondary
   flows, and which of them are control, feedback, or optional.
4. The one point the figure argues, and where the eye should start.
5. Layout and style intent, including whether a legend and step numbers are used.
6. Three to five assumptions to confirm, each with its source.
7. A caption draft that walks the numbered steps.

Keep component labels identical to the manuscript's own terms. Never add a box
or arrow that the brief does not contain.

Check the brief against the implementation, not only the manuscript draft: for
every component and edge, find the code, configuration or methods text that
does it, and note under which condition it runs (for example which ablation
arm has the tool). A label such as "used for every design" or an arrow from one
tool to another is a claim; drop it or rephrase it when the source does not
support it, and tell the user.

## 2. Fix the canvas from the journal

Read the target journal's figure rules first. For the flagship Nature journal
use [nature-article-requirements.md](nature-article-requirements.md): 89 mm
(about 252 pt) single column, 183 mm (about 519 pt) double column, text between
5 pt and 7 pt at final size, a sans-serif face (Arial or Helvetica preferred),
live editable text, no outlined text.

Draw at final size: set `width`/`height` with units and a matching `viewBox`,
so one drawing unit is one point and every size in the file is a print size.

## 3. Pick the arrangement

Choose by the structure of the content, not by taste:

| Content | Arrangement |
|---|---|
| Stages in order | left-to-right or top-down pipeline |
| Tiers or planes (control, execution, resources) | stacked layers, one container per tier |
| A hub and its workers | central node with fan-out |
| Cycle or feedback | loop with one dashed return edge |
| An agent that calls tools | the agent's own loop at the hub; tool modules as callees around it ([style rules](vector-schematic-style-rules.md#agent-and-tool-diagrams)) |
| Alternatives or before/after | side-by-side panels with identical structure |

Budget: about 13 labelled boxes for a single column, about 20 for a double
column. If the brief is heavier, merge boxes, show a repeated unit once with a
`×N` mark, or move detail to a second figure. Never shrink text below the
journal floor to fit more.

## 4. Draw the SVG

- One group per component with a stable `id` (`n:orchestrator`, `e:submit`,
  `c:control-plane`) wrapping its shape and its `<text>`, so later edits map
  back to the brief.
- Text stays `<text>`. No gradients, filters, drop shadows, scripts, or
  external references; embed any bitmap as a data URI.
- Apply [vector-schematic-style-rules.md](vector-schematic-style-rules.md) for
  colour, line, arrowhead, container, and legend conventions.
- Size each box from the measured label width plus padding rather than guessing.

## 5. Check, look, fix

1. Run the audit on the SVG:
   `python skills/nature-figure/scripts/audit_svg_schematic.py figure.svg`.
   It checks final-size text, canvas width, off-canvas content, and forbidden
   constructs. A non-zero exit blocks delivery.
2. Render the SVG to PNG at final size and look at it. The audit cannot see
   overlaps between boxes, crossing arrows, or a label that touches a line.
3. Walk the brief: every component and flow is present, the main path reads in
   order, the new component is the visual accent, and the numbered steps match
   the caption.
4. Fix, then repeat from step 1 until the audit passes and every remaining
   warning is deliberate. Do this after every revision, not only before
   delivery: render the changed figure at final size, crop the region you
   edited, and look for overlaps, clipped text, loose lines and arrows that
   end on the wrong box before reporting the revision as done.

## 6. Deliver

Hand over the SVG, a PDF exported from it, a PNG preview, the caption draft,
the assumption list from the brief, and one line on how to edit (element ids
match the brief). Embed or outline nothing silently: say which fonts the SVG
uses. Treat the figure as a draft until the author has reviewed the science.

## Optional companion and credit

The structure of this workflow (brief gate, final-size drawing, check loop)
follows the approach of the MIT-licensed FigGenie skill
(<https://github.com/Sleepy-Avacado/FigGenie>), which additionally ships a
layout and exemplar library, a browser-based linter, and PowerPoint export for
systems-conference papers. It is an independent project with its own corpus
and licences; install it separately if you want those features. This
repository does not redistribute its figures, parts, or fonts.
