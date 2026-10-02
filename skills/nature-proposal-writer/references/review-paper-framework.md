# Review Paper Framework Design — Gap-Driven Approach

Use this reference to design a review or survey paper from a research topic. It covers pre-writing framework design; use `compose-mode.md` after the framework is approved and evidence has been assembled.

## Contents

- [Phase 1: Literature landscape](#phase-1-literature-landscape)
- [Phase 2: Gap identification](#phase-2-gap-identification)
- [Phase 3: Targeted gap filling](#phase-3-targeted-gap-filling)
- [Phase 4: Coverage assessment](#phase-4-coverage-assessment)
- [Phase 5: Causal-chain narrative](#phase-5-causal-chain-narrative)
- [Phase 6: Section contracts](#phase-6-section-contracts)
- [Phase 7: Default structure](#phase-7-default-structure)
- [Phase 8: Figure strategy](#phase-8-figure-strategy)
- [Phase 9: Chinese review style](#phase-9-chinese-review-style)
- [Phase 10: Table-as-figure substitution](#phase-10-table-as-figure-substitution)
- [Pitfalls](#pitfalls)

## Phase 1: Literature landscape

Search multiple independent source classes:

| Source class | Purpose |
|---|---|
| User-provided corpus and project notes | Recover prior decisions, terminology, and curated references |
| Reference manager or institutional library | Find stored papers and verified metadata |
| Scholarly databases and publisher search | Expand beyond the local collection |
| Full text | Verify methods, evidence, limitations, figures, and exact claims |

When available, route broad discovery and citation verification through `nature-academic-search`, and lawful full-text retrieval through `nature-downloader`. Run independent source searches in parallel when permitted, then deduplicate by DOI, title, and study identity.

Record every included source with a stable identifier and the specific review question it supports. Do not treat search-result snippets as evidence.

## Phase 2: Gap identification

Enumerate gaps only after the first landscape pass. Each gap must be:

1. a specific question the review can address;
2. mapped to existing and missing evidence;
3. scored for importance to the review narrative;
4. classified as a knowledge, measurement, comparison, or translation gap.

Example:

```text
Gap 1: Which quantitative criterion separates stable from unstable operation?
Gap 2: Which variables explain disagreement between short- and long-duration studies?
Gap 3: Are reported mechanism classes mutually exclusive or interacting?
Gap 4: Which laboratory measurements predict application-scale performance?
```

## Phase 3: Targeted gap filling

For every gap, design searches using exact mechanisms, measurements, conditions, competing terminology, and key authors. Search backward through references and forward through citing papers for the most important studies.

If a gap remains after a documented search, label it as a candidate field-level gap and report the search boundary. Absence of retrieval is not, by itself, proof that no literature exists.

## Phase 4: Coverage assessment

Count and classify the literature before fixing the section architecture. Report coverage by:

- mechanism or theme;
- evidence type and method;
- operating condition or population;
- publication period;
- primary study versus review;
- directly relevant versus contextual.

There is no universal minimum reference count. A broad review generally needs more coverage than a narrowly framed critical review. Use the target venue and the nearest high-quality reviews as comparators, but judge readiness from coverage of the argument and major counterevidence rather than raw count.

## Phase 5: Causal-chain narrative

Do not organize the paper by research group or citation order. Prefer mechanism, dependency, or decision level.

Build a chain such as:

```text
Boundary conditions → underlying process → measurable state
→ failure or outcome → intervention → application consequence
```

Every major section should map to one link or one well-defined comparison across links. Missing links become explicit gaps rather than silent transitions.

## Phase 6: Section contracts

For each section define:

- **Purpose**: the question the section answers;
- **Inputs**: the evidence and prior sections it depends on;
- **Allowed claims**: claims supported within this section;
- **Forbidden claims**: claims reserved for another section or unsupported by current evidence;
- **Key references**: the small set of indispensable sources;
- **Validation**: checks that demonstrate synthesis rather than literature stacking.

## Phase 7: Default structure

Adapt this mechanism-led template to the field and venue:

| Section | Role |
|---|---|
| 1. Introduction | Problem framing, contribution, and scope boundary |
| 2. Boundary conditions | Environment, system assumptions, terminology, and evidence limits |
| 3. Formation or operating mechanism | How the target state emerges |
| 4. Outcome or failure classes | Systematic classification with criteria and competing explanations |
| 5. Controlling factors | Variables that connect conditions to outcomes |
| 6. Measurement and methodology | How evidence quality and comparability are established |
| 7. Implications and outlook | Translation, prioritized gaps, and research roadmap |

Retain a standalone methods section when readers need it to judge whether results across studies are comparable.

## Phase 8: Figure strategy

Route submission-grade scientific figures through `nature-figure` when available. Match the production method to the evidence type:

| Figure type | Preferred source or method |
|---|---|
| Conceptual structure or mechanism | Author-created schematic with cited evidence and explicit synthesis label |
| Quantitative chart | Replotted source data or validated analysis; never invented values |
| Comparison matrix | Table or precisely constructed vector graphic |
| Empirical image | Lawfully reused or adapted published evidence with attribution and permission checks |

Rules:

- Do not generate data-like charts from prose.
- Label multi-source conceptual figures as conceptual synthesis and cite supporting sources.
- Keep captions and citations editable rather than baking them into raster images.
- Inspect every figure for scientific, typographic, and citation accuracy.
- Place a figure near the paragraph where it is first interpreted.

## Phase 9: Chinese review style

Load `references/chinese-review-writing-style.md`. In particular:

- keep one analytical point per paragraph;
- replace filler transitions with explicit logical relations;
- report numbers, conditions, and uncertainty instead of unsupported intensifiers;
- distinguish reported fact, author interpretation, and hypothesis;
- use scientific section titles rather than metaphors or journalistic phrasing.

## Phase 10: Table-as-figure substitution

Use a table when a conceptual diagram becomes too dense, decorative, or ambiguous. Tables are often better for causal-chain comparisons, theory contrasts, evidence matrices, and processes that require source attribution in every row.

Decision rule:

- spatial structure or compact mechanism → schematic;
- quantitative relationship → validated chart;
- multi-attribute comparison or citation-dense process → table;
- no traceable evidence → omit the visual or label it explicitly as a hypothesis.

## Pitfalls

1. Organizing by author, laboratory, or material without a cross-cutting analytical structure.
2. Treating a search miss as proof of a field-level gap.
3. Fixing the outline before understanding the literature landscape.
4. Using raw reference counts as a substitute for coverage quality.
5. Creating categories that overlap without stating their boundaries.
6. Adding figures that imply empirical support where none exists.
7. Hiding methodological incomparability inside a narrative synthesis.
8. Writing an outlook that says only “more research is needed” rather than prioritizing dependencies and decisions.

After the framework passes review, use `compose-mode.md` for section drafting, `review-critique-methodology.md` for critical-depth QA, and `professor-dispatch.md` for targeted specialist review.
