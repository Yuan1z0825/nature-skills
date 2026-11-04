# Reformat a manuscript against a reference paper

Use this workflow for an unformatted manuscript A and a formatted DOCX paper B.
The host identifies semantic roles; the helper reads actual paragraph formatting;
the existing `md-to-word` engine exports the normalized manuscript.
Resolve the helper relative to this skill directory, not the manuscript directory.
If B instead contains written formatting instructions, read
[format-requirements](format-requirements.md). Its own text appearance does not
define the requested manuscript style. For a PDF or image reference, read or
recognize the pages first; the DOCX-only helper cannot inspect those files.

## 1. Inspect both documents

```bash
python scripts/reference_layout.py inspect reference.docx -o reference-samples.json
python scripts/reference_layout.py inspect manuscript.docx -o manuscript-samples.json
```

For Markdown or PDF manuscripts, read their structure directly. Read the reference
samples and inspect the document pages. Identify title, author, abstract heading,
abstract body, keywords, heading levels, body, captions and references by meaning
and position. A short bold paragraph alone does not establish a heading.
Identify these roles independently in A and B; their wording and order can differ.
Do not match paragraphs by index between documents.

## 2. Select reference samples and extract requirements

Choose a representative paragraph and run for each role used by A. Check other
instances of that role in B for agreement. Avoid an emphasized word when selecting
body typography. Record deliberate exceptions separately, such as the first body
paragraph, and do not average different roles into one rule.

Write `roles.json` using engine style names from `md-to-word --contract`:

```json
{
  "Title": {"paragraph": 0, "run": 0},
  "Heading 1": {"paragraph": 4, "run": 0},
  "Body Text": {"paragraph": 5, "run": 0},
  "First Paragraph": {"paragraph": 5, "run": 0},
  "Normal": {"paragraph": 5, "run": 0}
}
```

Indices are zero-based IDs from `inspect`; the example numbers are illustrative.
The helper combines the selected run and paragraph's direct formatting with their
style inheritance, including custom styles. It reuses the engine's requirements
vocabulary and keeps source-sample comments and unresolved extraction notes.

```bash
python scripts/reference_layout.py build reference.docx --map roles.json -o format.txt
```

Review the resulting rules against the reference samples. Make a compact coverage
table: source role, reference paragraph/run, applied properties, unresolved items.
Cover every role used by A, including the engine's required base styles. If B has
no example, label the rule as an explicit user requirement or a named preset
default; do not describe it as extracted. Resolve extraction notes from the actual
reference or its supplied specification. Remove reference-specific authors,
running text and other content from the requirements; preserve A's content.
Multiple-section layouts and engine-unsupported properties remain specific gaps.

## 3. Export and check the result

Normalize A to the existing Markdown contract, assigning the identified roles.
Compare text, numbers, equations, images, tables, notes and citations with A;
resolve conversion losses before delivery. Do not copy B's manuscript content.

```bash
md-to-word manuscript.md -r format.txt -o formatted.docx --json
```

Check the engine result, then compare the output's role styles with the sampled
reference properties and the coverage table. An unrepresented role or omitted
property is a gap even when export passes. Use available Word or LibreOffice to
render the output, and inspect headings, captions, equations, table breaks and
page boundaries. Fix observed defects and recheck the affected pages. Different
manuscript lengths do not require identical page breaks.

Deliver the DOCX, requirements and concise coverage/check results. Distinguish
verified properties, unresolved reference rules and pages not visually checked.
