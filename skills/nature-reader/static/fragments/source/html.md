# Source: publisher or preprint HTML

The source is an HTML page (publisher site, preprint server, or similar).

- Extract the article body; strip site navigation, cookie banners, related-article rails, reference-manager widgets, and advertisements.
- Keep the section structure and paragraph order from the article markup.
- Figures and tables are usually separate image/HTML elements — capture each figure image and its caption, and place per `references/figure-extraction.md`. Reconstruct HTML tables faithfully rather than screenshotting them when the markup is clean.
- Preserve inline math (MathML/LaTeX/images), superscript citation markers, and links to the reference list. Prefer accessible MathML or publisher-provided LaTeX over OCR, normalize it to `$...$` or `$$...$$`, and retain image formulae as equation crops when no trustworthy machine-readable form exists.
- Respect the copyright caution: for paywalled or all-rights-reserved pages, keep chat output short and point to the local artifact. Reproduce full bilingual text only for clearly lawful open-access content.
- If the page is JavaScript-rendered and content is missing, note what could not be retrieved instead of inventing it.
