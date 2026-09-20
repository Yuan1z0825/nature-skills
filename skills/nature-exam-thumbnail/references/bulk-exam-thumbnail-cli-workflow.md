# Bulk Exam Thumbnail CLI Workflow

## Contents

- [Current CLI Contract](#current-cli-contract)
- [Visual Requirements Learned](#visual-requirements-learned)
- [Bulk Generation Rules](#bulk-generation-rules)
- [Known Good Bulk Run Shape](#known-good-bulk-run-shape)
- [Pitfalls](#pitfalls)

Session-derived workflow for generating WebP thumbnails for all platform exams
with a standalone thumbnail CLI.

## Current CLI Contract

- Run from the standalone thumbnail CLI directory (older notes may mention a
  different path; confirm before using).
- Required output destination is remote R2 object `--path`, not a local
  `--output` file.
- The CLI uploads WebP directly and prints the public URL first, then source
  Pexels URL.
- R2 env: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
  `R2_BUCKET_NAME`, `R2_PUBLIC_URL` (copied from the backend `.env`).
- Pexels key is read from `PEXELS_API_KEY` in the CLI `.env` or passed with
  `--pexels-api-key`.
- Use filenames based on exam id: `thumbnails/exams/{exam_id}.webp`.

Example one-off command:

```bash
python -m thumbnail_cli.main \
  --keyword "european old town architecture" \
  --emoji "🇩🇪" \
  --text "Practice German reading questions without feeling overwhelmed" \
  --exam-type reading \
  --level B1 \
  --quality 88 \
  --path thumbnails/exams/{exam_id}.webp
```

## Visual Requirements Learned

- Prefer Pexels scenery, architecture, Germany, or Europe keywords; avoid
  people/student imagery unless requested.
- Text overlay: left aligned, vertically centered only, not horizontally centered.
- Inline white rectangular backgrounds behind text lines; no rounded corners
  and no shadow.
- Emoji is separate, no background; render via Twemoji PNG if font emoji fails.
- Main text uses bundled bold Open Sans and should be legible but not oversized
  (about 10% smaller than the first version).
- Top-right type/level tags match FE semantics: `text-color bg-color/10`,
  pre-blended to a very light background. Exam type is `reading` or
  `listening` (also accept typo alias `listing`) with an icon.
- WebP quality around 88 with strong encoder effort is a good balance
  (about 145 KB vs ~328 KB JPG).

## Bulk Generation Rules

1. Query exams from backend DB using the project venv and asyncpg/SQLAlchemy.
2. Use `exams.photo_url` as the thumbnail field to update.
3. Ensure no duplicate source images:
   - Fetch a larger Pexels result set/pages once using architecture/scenery
     keywords.
   - Track and persist used Pexels photo URLs or IDs.
   - Pass a unique `--photo-index` only if the CLI's current Pexels result
     ordering is stable enough; for robust bulk runs, extend the CLI to accept
     an explicit `--source-url` or implement the bulk loop inside Python using
     the same render/upload functions.
4. Random emoji must come only from the user-provided emoji file/list. If the
   file is not present, stop and ask for it instead of inventing an emoji pool.
5. Update DB only after a thumbnail URL is successfully uploaded.
6. After direct DB updates, invalidate detail-cache keys (e.g.
   `exam_bank:exam:<exam_id>`) when possible.
7. Verify:
   - `count(*)` exams equals number updated.
   - `photo_url` is non-empty for all target exams.
   - no duplicate `photo_url` values.
   - public URLs return image content (HEAD/GET content-type starts with
     `image/`).

## Known Good Bulk Run Shape

In a successful 74-exam run, the safest path was:

1. Export exams to `exams.json` from the backend using the project venv and
   `postgresql+asyncpg://`.
2. Run a bulk script inside the thumbnail CLI directory that imports
   render/upload helpers from `thumbnail_cli.main` instead of shelling out many
   times.
3. Fetch unique Pexels photos up front across scenery/architecture keywords
   such as `european old town architecture`, `germany architecture old town`,
   `german village architecture`, `bavaria old town`, `european street
   architecture`, `germany landscape castle`, `berlin architecture city`,
   `munich old town architecture`, `europe cityscape architecture`, and
   `cobblestone street europe`.
4. Shuffle the unique source URLs, render each exam with a random emoji from
   the user list, and upload to `thumbnails/exams/{exam_id}.webp`.
5. Persist `bulk_thumbnail_results.json` with `{id, url, source_photo, emoji}`
   for audit/retry before updating DB.
6. Verify `len(ids) == len(source_photo) == len(url) == exam_count`; then
   update `exams.photo_url` with the R2 URLs and re-query the updated count.
7. Probe a few public URLs with HEAD and require `200`,
   `content-type: image/webp`, and plausible content length.

For Python 3.9 compatibility in the standalone thumbnail project, avoid
`str | None` in helper scripts or add `from __future__ import annotations`.

## Pitfalls

- The backend folder name may be misspelled (e.g. `german-leanring-be`);
  prefer `/Volumes/Data/blauberry/blauberry/german-leanring-be` and confirm
  before using older paths.
- Do not overwrite all thumbnails until the user-provided emoji file/list is
  available if they explicitly require that source.
- Pexels source URL uniqueness and R2 output URL uniqueness are different
  checks; verify both when the user says no duplicate images.
- If the batch generated thumbnails but DB update happens via direct SQL,
  remember the existing cache rule: invalidate detail-cache keys when Redis is
  available, or report that cache invalidation was not performed.
- The telc 49-exam run used one unified script: query missing rows -> generate
  -> upload -> update DB -> verify in a single process, running through the
  backend venv Python (system Python 3.9 lacks `datetime.UTC`).