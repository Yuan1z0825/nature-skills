# OpenRouter Image Generation for Manuscript Schematics

## Contents

- [Source](#source)
- [Safety and scientific integrity](#safety-and-scientific-integrity)
- [Prompt contract](#prompt-contract)
- [Script usage](#script-usage)
- [Recommended defaults](#recommended-defaults)
- [Follow-up QA](#follow-up-qa)


Use this reference only when the user explicitly asks to generate a paper schematic, graphical abstract, mechanism diagram, or concept illustration through OpenRouter / GPT Image 2 / an image-generation API.

Read `ai-graphical-abstract-workflow.md` first. Complete its journal-policy gate,
communication brief, scientific-review plan, and provenance plan before making a
real API call. If submission eligibility has not been verified, mark the result
as an internal design draft rather than a submission-ready asset.

Do not use this route for quantitative plots, data panels, heatmaps, microscopy plates, blots, or figure assembly unless the user explicitly wants an AI-generated draft illustration. Keep data-driven figures in the Python or R route.

## Source

OpenRouter's dedicated Images API uses:

- model discovery: `GET https://openrouter.ai/api/v1/images/models`
- generation: `POST https://openrouter.ai/api/v1/images`
- default model for this skill: `openai/gpt-image-2`

Authentication uses `OPENROUTER_API_KEY` as a bearer token.

## Safety and scientific integrity

- Treat generated images as draft visual concepts, not evidence.
- Do not treat a Nature Careers article as permission to submit generative-AI
  artwork. Verify the exact target journal's current official rules and keep
  internal usefulness separate from submission eligibility.
- Do not invent quantitative values, p-values, spectra, microscopy findings, institution logos, author photos, journal marks, or unsupported mechanisms.
- Prefer short labels and simple shapes. AI image models can misspell text; final publication labels should usually be redrawn in Illustrator, Inkscape, PowerPoint, or a Python/R vector workflow.
- If the schematic could be interpreted as a data panel, explicitly mark it as conceptual.
- Do not send confidential manuscript content to OpenRouter without user permission.

## Prompt contract

Before calling the API, collect or infer:

1. article title or central claim
2. key biological/material/computational entities
3. cause-effect mechanism or workflow stages
4. desired layout, such as left-to-right pipeline, circular mechanism, split before/after, or graphical abstract
5. target aspect ratio and output format
6. any labels that must appear, keeping them short
7. things that must be excluded
8. target journal, policy URL, access date, and intended AI-use disclosure

Write a compact prompt with:

- visual role: "Nature-style graphical abstract" or "clean scientific mechanism schematic"
- composition: panel flow, hierarchy, and focal element
- style: flat vector-like, restrained palette, high contrast, white or transparent background
- scientific constraints: no fabricated numbers, no extra organs/cells/materials, no logos
- output constraints: minimal text, editable downstream, journal-safe

## Script usage

Use the bundled script for reproducible calls:

```bash
export OPENROUTER_API_KEY="sk-or-..."
python skills/nature-figure/scripts/generate_openrouter_schematic.py \
  --title "Paper title" \
  --abstract-file abstract.txt \
  --panel-map "left: problem; center: proposed mechanism; right: validated outcome" \
  --outdir outputs/schematic \
  --basename graphical_abstract \
  --aspect-ratio 16:9 \
  --resolution 2K \
  --quality high
```

Dry-run without network or API key:

```bash
python skills/nature-figure/scripts/generate_openrouter_schematic.py \
  --title "Self-healing cementitious sensor" \
  --abstract "A composite sensor couples chloride ingress with recoverable piezoresistive response." \
  --panel-map "left: marine exposure; center: ion transport and microcrack healing; right: signal recovery curve" \
  --dry-run
```

Use a fully custom prompt:

```bash
python skills/nature-figure/scripts/generate_openrouter_schematic.py \
  --prompt-file schematic_prompt.md \
  --raw \
  --outdir outputs/schematic
```

Use one or more reference images:

```bash
python skills/nature-figure/scripts/generate_openrouter_schematic.py \
  --prompt-file schematic_prompt.md \
  --reference-image draft_layout.png \
  --reference-image https://example.com/style-reference.png
```

The script saves generated files plus `request_metadata.json` in the output directory.

Use another OpenAI-compatible images endpoint (`--api-url`, or `SCHEMATIC_IMAGE_API_URL`) when the user already pays for a gateway instead of OpenRouter. The response shape (`data[].b64_json` or `data[].url`) is the same, so nothing else changes; the endpoint actually called is recorded in `request_metadata.json`. Example with OrcaRouter:

```bash
export ORCAROUTER_API_KEY="sk-orca-..."
python skills/nature-figure/scripts/generate_openrouter_schematic.py \
  --api-url https://api.orcarouter.ai/v1/images/generations \
  --api-key-env ORCAROUTER_API_KEY \
  --model openai/gpt-image-2 \
  --title "Paper title" \
  --outdir outputs/schematic
```

## Recommended defaults

- `model`: `openai/gpt-image-2`
- `aspect_ratio`: `16:9` for graphical abstracts, `4:3` for mechanism figures, `1:1` for cover-like concepts
- `resolution`: `2K` for review drafts; use higher only when needed
- `quality`: `high`
- `output_format`: `png`
- `background`: `opaque` unless the user asks for transparent

## Follow-up QA

After generation:

1. inspect the image visually
2. check whether labels are legible and spelled correctly
3. list any scientific hallucinations or unsupported visual claims
4. recommend which labels or arrows should be redrawn as vector objects
5. keep the generated image and metadata together for provenance
6. report separate verdicts for internal design use and submission eligibility
