# Technical Disclosure

Use this mode for Chinese patent mining and technical disclosure drafts
(`技术交底书`), especially when the user asks for patent points, disclosure
materials for a patent attorney, prior-art comparison, or a Markdown/DOCX
disclosure rather than a full formal application package.

Load and follow these references in order:

1. `references/disclosure/intake.md` for minimal boundary questions;
2. `references/disclosure/project_scan.md` before scanning projects, code,
   `.docx`, or `.pptx` materials;
3. `references/disclosure/patent_points_analyzer.md` to form candidate
   patent points and select the best disclosure direction;
4. `references/disclosure/prior_art_search.md` before writing prior-art
   discussion;
5. `references/disclosure/disclosure_preview.md` unless the user explicitly
   skips preview;
6. `references/disclosure/disclosure_builder.md` and
   `references/disclosure/template_reference.md` for the final disclosure;
7. `references/disclosure/disclosure_self_check.md` for internal QA before
   delivery.

Use scripts under `scripts/disclosure/` for Office conversion, CNIPA
published-patent search, Mermaid rendering, Markdown-to-DOCX conversion,
formula rendering, and revision logs. Read `references/disclosure/tooling.md`
when command details or dependency setup are needed.

Deliver final technical disclosures as both `.md` and `.docx` using the
case-name plus timestamp naming rule from `disclosure_builder.md`. Do not put
self-check tables, source IDs, skill metadata, or repository notes into the
delivered disclosure body.
