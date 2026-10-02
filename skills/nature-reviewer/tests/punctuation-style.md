# Punctuation-style behavior fixture

## Synthetic input

The manuscript supports one Major Concern and two Minor Comments. The review needs several explanatory transitions, parenthetical qualifications, and stable concern IDs.

## Expected behavior

- Write reviewer prose and post-review synthesis without relying on em dashes, en dashes, or colons as sentence connectors.
- Use a new sentence, comma, semicolon, parentheses, or a short label followed by a new line according to the grammatical relationship.
- Keep stable IDs such as `R1-M1` and established hyphenated terms such as `pre-submission`.
- Preserve punctuation in source-faithful titles, quotations, formulas, identifiers, URLs, times, and required machine-readable syntax when changing it would make the source or format inaccurate.
- Format concern headings without dash or colon punctuation, for example `R1-M1 [experimental-design]`.
- Format structured fields as bold labels followed by content, for example `**Severity** Major`.

## Forbidden behavior

- Do not repeatedly join clauses with dash punctuation or colons.
- Do not place a colon after every heading, label, or introductory phrase by habit.
- Do not replace punctuation mechanically when it belongs to a stable ID, compound term, formula, identifier, URL, time, title, faithful quotation, or required machine-readable syntax.
- Do not make sentences longer or less readable merely to avoid a punctuation mark.

## Pass/fail checklist

- [ ] No avoidable em-dash, en-dash, or colon punctuation appears in generated prose.
- [ ] Structured labels do not require trailing colons.
- [ ] Concern IDs and necessary hyphens remain correct.
- [ ] Replacement punctuation preserves the original logical relationship.
- [ ] Source-faithful and machine-readable material remains accurate.
