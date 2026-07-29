# MiniMax Image Generation for Manuscript Schematics

Use this reference only when the user explicitly asks to generate a paper schematic, graphical abstract, mechanism diagram, or concept illustration through the MiniMax image_generation API.

Do not use this route for quantitative plots, data panels, heatmaps, microscopy plates, blots, or figure assembly unless the user explicitly wants an AI-generated draft illustration. Keep data-driven figures in the Python or R route.

## Source

MiniMax exposes text-to-image generation at:

- generation: `POST /v1/image_generation`
- global endpoint: `https://api.minimax.io/v1/image_generation`
- China endpoint: `https://api.minimaxi.com/v1/image_generation`
- models: `image-01` (default) and `image-01-live`

Authentication uses a bearer token read from `MINIMAX_API_KEY`. Pick the endpoint that matches your account with `--region global` (api.minimax.io) or `--region cn` (api.minimaxi.com).

## Request fields

`model` and `prompt` are required. The prompt supports up to 1500 characters. Supported optional fields:

- `aspect_ratio`: one of `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9` (default `1:1`).
- `width` / `height`: pixels in `[512, 2048]`, each divisible by 8, and set together. Effective for `image-01`. When both `width`/`height` and `aspect_ratio` are supplied, `aspect_ratio` takes priority.
- `response_format`: `url` (default) or `base64`.
- `seed`: fixed integer seed for reproducible images.
- `n`: number of images per request, range `[1, 9]`.
- `prompt_optimizer`: boolean; let the service rewrite the prompt automatically.

## Response fields

- `data.image_urls`: array of image links when `response_format=url`. Links expire 24 hours after generation.
- `data.image_base64`: array of base64-encoded images when `response_format=base64`.
- `metadata.success_count` / `metadata.failed_count`: images generated versus blocked for content safety.
- `base_resp.status_code`: `0` on success; non-zero values (for example `1026` sensitive content, `1002` rate limited, `1004`/`2049` authentication) carry `base_resp.status_msg`.

## Safety and scientific integrity

- Treat generated images as draft visual concepts, not evidence.
- Do not invent quantitative values, p-values, spectra, microscopy findings, institution logos, author photos, journal marks, or unsupported mechanisms.
- Prefer short labels and simple shapes. AI image models can misspell text; final publication labels should usually be redrawn in Illustrator, Inkscape, PowerPoint, or a Python/R vector workflow.
- If the schematic could be interpreted as a data panel, explicitly mark it as conceptual.
- Do not send confidential manuscript content to the API without user permission.

## Prompt contract

Before calling the API, collect or infer:

1. article title or central claim
2. key biological/material/computational entities
3. cause-effect mechanism or workflow stages
4. desired layout, such as left-to-right pipeline, circular mechanism, split before/after, or graphical abstract
5. target aspect ratio and response format
6. any labels that must appear, keeping them short
7. things that must be excluded

Write a compact prompt with:

- visual role: "Nature-style graphical abstract" or "clean scientific mechanism schematic"
- composition: panel flow, hierarchy, and focal element
- style: flat vector-like, restrained palette, high contrast, white or transparent background
- scientific constraints: no fabricated numbers, no extra organs/cells/materials, no logos
- output constraints: minimal text, editable downstream, journal-safe

## Script usage

Use the bundled script for reproducible calls:

```bash
export MINIMAX_API_KEY="..."
python skills/nature-figure/scripts/generate_minimax_schematic.py \
  --title "Paper title" \
  --abstract-file abstract.txt \
  --panel-map "left: problem; center: proposed mechanism; right: validated outcome" \
  --outdir outputs/schematic \
  --basename graphical_abstract \
  --aspect-ratio 16:9 \
  --model image-01
```

Dry-run without network or API key:

```bash
python skills/nature-figure/scripts/generate_minimax_schematic.py \
  --title "Self-healing cementitious sensor" \
  --abstract "A composite sensor couples chloride ingress with recoverable piezoresistive response." \
  --panel-map "left: marine exposure; center: ion transport and microcrack healing; right: signal recovery curve" \
  --dry-run
```

Use a fully custom prompt and the China endpoint:

```bash
python skills/nature-figure/scripts/generate_minimax_schematic.py \
  --prompt-file schematic_prompt.md \
  --raw \
  --region cn \
  --outdir outputs/schematic
```

Request explicit pixel dimensions and base64 output:

```bash
python skills/nature-figure/scripts/generate_minimax_schematic.py \
  --prompt-file schematic_prompt.md \
  --raw \
  --width 1280 --height 720 \
  --response-format base64
```

The script saves generated files plus `request_metadata.json` in the output directory. The metadata records the endpoint, region, request payload, trace id, and the `success_count` / `failed_count` reported by the API.

## Recommended defaults

- `model`: `image-01`
- `aspect_ratio`: `16:9` for graphical abstracts, `4:3` for mechanism figures, `1:1` for cover-like concepts
- `response_format`: `url` for review drafts; use `base64` when you need the bytes inline
- `n`: `1`, raise only when comparing drafts

## Follow-up QA

After generation:

1. inspect the image visually
2. check whether labels are legible and spelled correctly
3. list any scientific hallucinations or unsupported visual claims
4. recommend which labels or arrows should be redrawn as vector objects
5. keep the generated image and metadata together for provenance
