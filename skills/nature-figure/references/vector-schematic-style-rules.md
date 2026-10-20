# Vector Schematic Style Rules

Conventions for architecture, pipeline, and mechanism schematics drawn with the
[vector schematic workflow](vector-schematic-workflow.md). They bend only when
the figure's own story needs it; say so in the brief when a rule is bent.

## Contents

- [Type](#type)
- [Colour](#colour)
- [Lines and arrows](#lines-and-arrows)
- [Structure](#structure)
- [Legend and numbering](#legend-and-numbering)
- [Agent and tool diagrams](#agent-and-tool-diagrams)
- [Common failures](#common-failures)

## Type

- One family, at most three sizes, ordinary text 5 to 7 pt at final size for
  the flagship Nature journal; panel letters follow the journal rule. Nature
  asks for a sans-serif face; for another journal follow its own list (some,
  such as Elsevier's, also accept Times). Whatever the family, use it for every
  label, including mathematics and code names (a matching monospace).
- All text in one dark ink. Do not set labels or descriptions in grey; colour in
  text only where it carries a meaning the figure states (an error path, a
  highlighted component).
- Give each box its name and, where the reader needs it, one short line on its
  job. A figure of title-only boxes reads as empty and a box holding a paragraph
  reads as crowded; move the rest to the caption.
- Set several lines in a narrow box ragged or centred. Justify only when every
  box of that kind has the same text width and the line breaks leave the word
  spacing even; re-word rather than stretch a short line.
- Labels are the manuscript's own terms, spelled and capitalised as in the text.
- Text stays live. Do not outline it and do not use a glyph the embedded font
  lacks; draw an ellipsis or arrow as shapes if needed.
- Centre each label in its box, and size the box from the measured label width
  plus padding, not the other way round.

## Colour

- White canvas. At most two saturated fills, and exactly one accent that marks
  the paper's new component.
- Pale or grey fills for existing parts, white with a grey outline for external
  systems.
- Red only for errors, bottlenecks, or a highlighted path.
- Keep text contrast readable: dark text on pale fills, white text only on dark
  accents. Do not rely on colour alone; pair it with a label, shape, or line
  style so the figure survives greyscale printing and colour-vision differences.
- No rainbow categorical fills, gradients, 3D, or drop shadows.

## Lines and arrows

- Every directed edge has an arrowhead; the main path is the heaviest line.
- Solid means data or control that always flows. Dashed carries exactly one
  meaning per figure (for example feedback, or a logical group boundary), never
  two. If groups are dashed, make feedback dotted, or the reverse.
- Use orthogonal routes for structure and curves only for feedback.
- Where two unconnected lines must cross, break one of them for a short gap at
  the crossing; mark a real branch point with a small dot.
- No line passes through a label, and arrows do not end on a container
  boundary unless the whole group is the endpoint.
- Keep arrowheads and tails clear of tier dividers and container titles.

## Structure

- Nest at most three levels. A container is never filled darker than its
  children; outline-only containers are the safe default.
- Equal gaps in a row, and snap box edges to a common grid. Boxes that play the
  same role in different rows or containers share their width and their top and
  bottom edges.
- Repeat a container's internal order in every container of its kind (for
  example tools above, the functions that call them below).
- Place a container title in the headroom between the container's top edge and
  its first box, with no overlap.
- Show repetition with a `×N` mark or a stack of two offset boxes, not N copies.
- Pick one arrangement direction and keep the main path monotone along it.

## Legend and numbering

- Add a legend only when more than four fills, line styles, or icons carry
  meaning and the caption cannot explain them. Place it within one box-width of
  what it decodes.
- Use circled numbers at the upper-left of an edge for the main path, and make
  the numbers match the caption's walkthrough.

## Agent and tool diagrams

- Draw an LLM agent as what it is: a loop that iterates. Show its own cycle
  (reason, call a tool, read the result) with the agent at its centre, and step
  marks or a repeat sign so the reader sees many rounds, not one pass.
- Draw the tools as things the agent calls. Calls leave the cycle's tool-call
  station and results, refusals and returned designs come back to its
  observation station; group the tools by module and connect each module once.
- A retrieval step (a knowledge library, a search) is a tool call like the
  others, not a separate stage before the agent.
- Do not chain the agent and its tools as stages of a pipeline. A fixed order
  inside one tool call (check A, then B) may be drawn as a row inside that
  tool's container.
- Name the model the agent runs on when the paper compares models or harnesses.

## Common failures

| Failure | Fix |
|---|---|
| Too many boxes for the column | Merge, show once with `×N`, or split into two figures |
| Several things in the accent colour | Keep one accent: the new component |
| Dashed used for two meanings | Give one meaning a dotted line or a solid frame |
| Text below the journal floor | Reduce content, never the type |
| Arrow touching a title or crossing a label | Reroute or move the label |
| Decisions made silently | Record them as assumptions in the brief |
| The figure implies behaviour the system lacks | Check each component, edge and label against the code or methods |
| An agent drawn as one stage of a pipeline | Draw its loop; draw the tools as callees |
| Wide gaps in justified box text | Re-word, or set the box ragged |
| Grey labels, or boxes of one width in one row and another in the next | One dark ink; shared widths and edges |
