# `nature-exam-thumbnail` Skill

[中文说明](README.md)

Batch-generate and ship learning-platform exam thumbnails: read rows missing thumbnails from a database, fetch unique source images, render consistent WebP covers, upload to R2/S3, write back to the database, and verify.

## What To Use It For

- A freshly imported batch of exams (e.g. dozens of telc B1/B2 sets) has no cover images.
- Re-running generation after fixing duplicate or 404 thumbnails.
- Giving a learning platform's list page a consistent cover style.

## Typical Requests

- "49 telc exams have no thumbnails; generate them and update the database."
- "Some thumbnails are duplicated; regenerate a unique set."
- "Switch image sources and regenerate all exam covers."

## What You Need To Provide

- Database access (find the `exams` table and rows with empty `photo_url`).
- R2/S3 object storage config (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET_NAME`, `R2_PUBLIC_URL`).
- Optional: Pexels API key; falls back to curated URLs.
- Optional: the allowed emoji list (a built-in list is used by default).

## Outputs

- One `thumbnails/exams/{exam_id}.webp` (1280×720 WebP) per exam.
- Public URL list and an audit JSON of `{id, url, source_photo, emoji}`.
- `exams.photo_url` updated; zero missing thumbnails; no duplicates.

## Boundaries

- No creative design; copy comes from the user.
- Existing `photo_url` values are not overwritten except when fixing duplicates/404s.
- Nothing is claimed done before an upload succeeds.

## Related Skills

- `nature-figure`: publication-grade scientific figures, not product covers.