# OCR and Text Hints Contract

## Credential and configuration

The cloud backend requires one Baidu AI Studio Access Token named
`PADDLE_OCR_TOKEN`. It is not the traditional Baidu `API Key + Secret Key` pair.
Apply at <https://aistudio.baidu.com/account/accessToken> and configure it with:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py config \
  --paddle-ocr-token "<BAIDU_AI_STUDIO_ACCESS_TOKEN>"
```

The process environment has priority over the active `config.yaml`, resolved as
override directory, project-level Skill root, then legacy user-level location.
Never print, commit, or copy the token into a run.

## Fixed network client behavior

- Endpoint: `https://paddleocr.aistudio-app.com/api/v2/ocr/jobs`
- Default model: `PaddleOCR-VL-1.6`
- Authorization: `Authorization: bearer <token>`
- Submit: multipart file plus `model` and the existing `optionalPayload` flags.
- Poll: `GET <endpoint>/<jobId>` until `done`; fail on `failed` or timeout.
- Result: download the service JSONL URL and collect every page's
  `prunedResult` from `layoutParsingResults`.

Do not change response interpretation or add another OCR normalizer. Missing pages,
non-200 submission, failed jobs, timeout, malformed/empty results, download errors,
and network exceptions are OCR failures.

Use the original PDF as one multi-page job when it is available. For a single image,
multiple images, PPT/PPTX pages, or a PDF run whose original file is unavailable,
submit each normalized `source.png` directly as its own job, in page order. Never
convert normalized images into a temporary PDF for OCR. Rescale service coordinates
to each actual source image before local measurement.

## Text filtering and local measurement

Keep only `text`, `paragraph_title`, and `vision_footnote` layout blocks. Preserve
recognized text as advisory content, then remeasure every block against the local
source ink. Produce source-pixel `box_px`, glyph height, line count, CJK/Latin font
size candidates, and a stable size group. Trust direct source reading for final
characters because recognition may be imperfect.

## Backend priority and fallback

1. If a token is available, attempt the network job first.
2. On any cloud failure, generate each page with local `builtin-ink`.
3. Even after successful cloud OCR, if a page has at most 2 OCR lines while the
   local detector finds at least 6, use the local result for that page.
4. Local fallback measures geometry and font scale but cannot recognize characters.
5. A page-level hint failure is reported and skipped; reconstruction may regenerate
   it with `page hints` or proceed by reading the source.

Do not change these thresholds or priorities during reconstruction.

## Artifacts and regeneration

`prepare` writes `text_hints.json` and `text_hints.png` beside every normalized page.
Regenerate without creating a second run:

```bash
python <image2ppt-root>/cli/image2ppt/cli.py run hints <run-dir>
```

Use `page hints <page-dir>` only for one-page local ink regeneration. Hints are
advisory page inputs, not lifecycle state and not a substitute for manifest text.
