# Output contract

Default deliverable:

```text
paper-card.md
```

Required working artifacts in page-grounded mode:

```text
source_bundle.json
audit-report.json
```

In fallback modes, `source_bundle.json` may be unavailable, but `audit-report.json` remains required when the bundled auditor can run. These are machine-readable support artifacts, not additional Paper Card sections.

For normalized source-map input, `pages` contains only blocks with verified positive page locators. Blocks with missing or invalid locators remain in `unlocated_blocks`; `locator_summary` reports the counts and reliability. A `null` page in structural evidence means unknown location and must never be rendered as page 1.

The file must contain:

- title and evidence-status header;
- input scope and paper-type classification;
- Sections 01-16 in order;
- source pointers for substantive paper-derived claims;
- provenance labels for external facts, analysis, hypotheses, and user-supplied judgments;
- explicit `Not applicable` or `Not assessable` markers where needed.

Do not create Sections 17 or 18.

## Evidence-status header

Include:

```markdown
> Source coverage: Full paper / Partial paper / Abstract only / Metadata only
> Extraction confidence: High / Mixed / Low
> Locator mode: page-grounded / structure-grounded / source-limited
> Primary analytical lens: ...
> Secondary analytical lens: None / ...
> Context verification: Paper-only / Targeted external check / Externally verified
> Card completeness: Complete relative to supplied source / Partial
```

`Complete relative to supplied source` does not imply that field history, novelty, or knowledge connections were independently verified.

Locator rules:

- `page-grounded`: use `[Paper: PDF p. N, Figure/Table/Equation/Section]`.
- `structure-grounded`: use `[Paper: Figure N]`, `[Paper: Table N]`, `[Paper: Equation N]`, or `[Paper: Section title]`; never include page numbers.
- `source-limited`: use `[Paper: Abstract]`, `[Paper: Metadata]`, or `[Paper: User-provided excerpt]`; mark unseen sections not assessable.

## Quality gates

Block final delivery when:

- a major reported number cannot be traced to the source;
- a main figure or table has not been inventoried;
- the card claims full coverage from partial input;
- author-stated limitations and Agent criticism are mixed;
- a research idea is described as novel without prior-art verification;
- irrelevant template content was invented to fill a section.

If a blocker cannot be resolved, downgrade the card to `Partial` and identify the exact gap.

Run the bundled auditor before final delivery. In fallback modes, run it without `--bundle` and expect an inventory-unavailable warning. A nonzero exit caused by audit errors blocks delivery. Audit success does not prove scientific correctness; manually review claims, evidence strength, and analytical conclusions.
