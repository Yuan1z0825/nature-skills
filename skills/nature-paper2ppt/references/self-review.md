# Self-review and verification

## Contents

- [The loop](#the-loop)
- [Self-review checklist](#self-review-checklist)
- [Severity rules](#severity-rules)
- [Programmatic checks when using python-pptx](#programmatic-checks-when-using-python-pptx)
- [Rendered preview policy](#rendered-preview-policy)
- [Step 9 — final verification](#step-9-final-verification)


Open this reference for step 8 (self-review/corrective revision loop) and step 9 (final verification).

## The loop

After creating the first PPTX draft, run at least one explicit self-review pass before declaring the deck final. Treat this as a defect-finding step, not a confirmation step.

1. Inspect the generated PPTX and extracted assets.
2. Write a short defect list with severity (`high`, `medium`, `low`) and slide numbers.
3. Correct every high-severity issue and every medium-severity issue that can be fixed without expanding the task substantially.
4. Regenerate the PPTX after edits.
5. Re-run verification and update `output/qa_report.md` with what was checked, what was fixed, and what remains.

## Self-review checklist

Check content and structure:

- slide order follows the paper's argument, not merely the paper section order,
- each slide has one dominant claim,
- slide titles are conclusion-style where possible,
- no invented numbers, mechanisms, datasets, claims, or unsupported implications,
- result slides include source labels and do not remove original scientific labels,
- speaker notes exist when planned and are useful for oral explanation.

Check visual and layout quality:

- no cropped-off figure titles, axes, legends, panel labels, or important annotations,
- no source figure is squeezed so far that the evidence becomes unreadable,
- dense figures are split or cropped rather than placed as tiny full-figure screenshots,
- text boxes, figures, captions, source labels, and takeaway bands do not overlap,
- no text visually exceeds or is likely to exceed its text box; text overflow is a delivery-blocking defect,
- all shapes stay inside slide bounds,
- text density is reasonable; move excess explanation into speaker notes or split the slide,
- layout rhythm feels intentional rather than generated from one repeated card/rail template,
- no slide uses equal cards or metric chips merely to fill space,
- cards, metrics, and captions have consistent spacing and alignment,
- font choices are Office-safe; avoid relying on a font that is unavailable in the environment for text fitting.

## Severity rules

Use `high` for defects that can mislead the audience or make the deck look broken:

- clipped scientific evidence such as axes, legends, panel labels, table rows, figure titles, or method labels,
- unreadable main evidence on a key result slide,
- overlapping text/figures, text cut off by its box, or text extending beyond a visible boundary,
- wrong slide order or missing central evidence,
- fabricated or unsupported quantitative statements.

Use `medium` for defects that reduce professionalism or comprehension:

- overly dense slides,
- rigid AI-looking layouts, especially repeated equal cards, repeated right-side rails, or decorative metric rows,
- weak crop margins,
- figure captions detached from the visual,
- excessive repeated layouts,
- missing or unhelpful speaker notes,
- ambiguous source attribution.

Use `low` for cosmetic issues that do not affect comprehension:

- minor alignment imperfections,
- palette or typography refinements,
- optional split of a readable but dense figure.

## Programmatic checks when using python-pptx

When generating with python-pptx, perform a lightweight audit in code after the first draft and again after revision. Run the bundled audit script whenever a real PPTX exists:

```bash
python skills/nature-paper2ppt/scripts/audit_pptx_quality.py \
  output/final_presentation_cn.pptx \
  --report output/pptx_audit.md \
  --fail-on high
```

If the script reports high-severity findings, treat the deck as not ready. Fix the deck, regenerate, and run the script again. Copy the final audit summary into `output/qa_report.md`.

The script checks common structural and language issues directly from PPTX XML:

- shapes outside the slide canvas,
- suspicious image crop settings,
- main evidence images that are too small for presentation use,
- repeated near-miss alignment between objects,
- text-heavy shapes likely to overflow,
- AI-template phrases such as `一句话总结`, `最有价值的后续方向`, and `不是……而是……`,
- slide count, media count, and notes count.

Also perform these checks in code or manually when the generation stack allows it:

- reopen the PPTX with `Presentation(output_path)`,
- count slides and embedded media,
- count non-empty notes slides if notes were planned,
- check every shape's left/top/right/bottom stays within the slide canvas,
- flag text-heavy slides by character count and number of text boxes,
- flag any text box whose estimated text length is too large for its width/height, especially mixed Chinese-English strings,
- flag long unbroken tokens or labels that may overflow narrow boxes,
- count repeated layout patterns and flag decks that reuse the same composition too often,
- flag images whose displayed size is too small for their role,
- scan for placeholder text such as `lorem`, `xxxx`, or accidental unreplaced labels.

These checks cannot prove visual perfection, but they reliably catch many failures and should trigger a manual/self-review pass.

## Rendered preview policy

Render slide previews when a reliable headless renderer is readily available. If rendered previews are available, inspect them for: missing images; distorted or low-resolution figures; unreadable panels; text overflow; overlapping captions, bullets, and figures; excessive bullet density; wrong slide order; missing source labels; missing or unhelpful speaker notes.

If rendered preview reveals defects, revise and regenerate the PPTX. Do not deliver a deck with obvious visual defects merely because the package validates.

If no reliable renderer is available, still complete the self-review loop using: crop/contact-sheet inspection for selected assets; `audit_pptx_quality.py`; slide-by-slide text and shape inspection; and a clear note in `output/qa_report.md` that rendered preview was unavailable.

## Step 9 — final verification

After revision, perform lightweight verification: reopen the PPTX with the generation library when possible; check slide count; check embedded media count; check speaker notes presence when notes were planned; run `audit_pptx_quality.py`; check obvious shape bounds if tooling supports it; create or inspect a contact sheet from selected extracted assets when figures were cropped.

Do not stop at "PPTX opens" if the self-review found high-severity issues. Correct them first, then verify again. Document any remaining limitation in `output/qa_report.md`.
