# Core principles

Build a Paper Card that helps a researcher reconstruct the paper's reasoning and inspect its evidential limits.

## Non-negotiable stance

- Treat the paper as a set of claims supported by specific evidence, not as prose to summarize.
- Preserve the difference between what the authors report, what the evidence directly supports, and what the Agent infers.
- Prefer exact numbers, conditions, and source pointers over evaluative adjectives.
- Explain why a method component exists and what evidence supports its contribution.
- State what a result does not establish.
- Leave unsupported fields incomplete rather than filling the template speculatively.
- Keep recurring terminology consistent using the shared Terminology Ledger.

## Scope

Produce only one Paper Card with Sections 01-16. Do not add:

- full-paper bilingual translation;
- formal reviewer reports;
- academic-English phrase collection;
- comprehension tests or self-quiz;
- public-article or social-media copy.

## Language

Match the language of the user's request unless the user specifies another output language. Localize section headings, table headings, and explanatory prose. Keep method names, dataset names, symbols, formulas, and established technical terms in their canonical forms.

## Required provenance classes

Separate content into:

- `[Paper]` - directly reported in the paper;
- `[External]` - verified from sources outside the paper;
- `[Analysis]` - reasoned interpretation from the available evidence;
- `[Hypothesis]` - proposed explanation or research direction requiring testing;
- `[User]` - a judgment or connection supplied by the user.

Do not write Agent-generated analysis in the user's voice. Use `Agent-derived candidate` where a section asks for the user's knowledge, connection, or idea and the user has not supplied one.

## Applicability

Keep the 16 headings stable, but adapt their contents to the paper type. A review may not have system modules or ablations; a theoretical paper may not have datasets; a clinical paper may not have a conventional component-removal study. Use `Not applicable` with a reason instead of forcing a methods-paper template onto every paper.

For hybrid papers, apply one primary analytical lens and at most one secondary lens. The primary lens governs the card's main argument; the secondary lens adds missing checks without duplicating the whole card.
