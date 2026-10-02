# Evidence and provenance rules

## Labels

Use the smallest applicable label:

| Label | Meaning | Required support |
|---|---|---|
| `[Paper]` | The paper explicitly reports or claims this | Page/section/figure/table/equation/block pointer |
| `[External]` | A source outside the paper supports this | Direct citation or URL |
| `[Analysis]` | The Agent infers this from identified evidence | Reasoning plus relevant source pointers |
| `[Hypothesis]` | A testable but unverified explanation or idea | Proposed test and possible falsifier |
| `[User]` | The user supplied this judgment or connection | User statement or linked user knowledge |

## Source-pointer format

Prefer:

```text
[Paper: PDF p. 3 (printed p. 24959), Fig. 2]
[Paper: PDF p. 6, Table 2]
[Paper: Eq. 6]
[Paper: S041-S044]
```

For PDFs in page-grounded mode, always write `PDF p. N` for the file page index. Store printed page labels in the source bundle and optionally declare their range once in the card header; do not require them in every pointer. Use only pointers available in the source. Never invent line numbers. For HTML without pages, use section and figure/table IDs. For abstract-only material, use `[Paper: Abstract]` and do not infer unseen methods or results.

## Locator modes

### Page-grounded

Use when the bundled preparation script validates PDF page indices:

```text
[Paper: PDF p. 3, Figure 2]
[Paper: PDF p. 7, Table 4]
```

Printed page labels may be stored in the source bundle or declared once in the card header. Do not repeat them in every pointer unless the user asks.

### Structure-grounded

Use when page indices are unreliable but document structure is reliable:

```text
[Paper: Methodology, Symbolic Parsing]
[Paper: Figure 2]
[Paper: Table 4]
[Paper: Equation 3]
```

Do not include any page number.

### Source-limited

Use when only limited source material is reliable:

```text
[Paper: Abstract]
[Paper: Metadata]
[Paper: User-provided excerpt]
```

Do not infer unseen methods, experiments, figures, tables, equations, or limitations.

## Claim strength

Use verbs that match evidence:

- `reports`, `observes`, `is associated with`;
- `supports`, `is consistent with`;
- `suggests`, `does not distinguish`;
- `demonstrates necessity` only with a valid intervention or ablation;
- `demonstrates sufficiency` only with evidence that establishes sufficiency;
- `causes` only when the design supports causal inference.

## Paper framing versus verification

Prefix an unverified field history with:

```text
[Paper-framed; external verification not performed]
```

Do not call a method first, novel, state of the art, or unprecedented solely because the authors do.

## Contradictions

When prose, tables, figures, or supplements disagree:

1. record both values and their locations;
2. do not silently choose one;
3. mark the affected conclusion uncertain;
4. state what would resolve the discrepancy.
