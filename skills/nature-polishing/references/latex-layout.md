# LaTeX layout & float typesetting for Nature-style manuscripts

## Contents

- [0. Diagnosis workflow (do this first)](#0-diagnosis-workflow-do-this-first)
- [1. The "loose / 松散" float page — top-align the glue](#1-the-loose-松散-float-page-top-align-the-glue)
- [2. Wide-and-short figures can never fill a portrait page — fix at the source](#2-wide-and-short-figures-can-never-fill-a-portrait-page-fix-at-the-source)
- [3. Do NOT rotate to landscape (Nature house style)](#3-do-not-rotate-to-landscape-nature-house-style)
- [4. Float backlog → stranded section headings](#4-float-backlog-stranded-section-headings)
- [5. [H] and placeins — sharp edges](#5-h-and-placeins-sharp-edges)
- [6. Multi-panel main-text figures — stack, don't cram](#6-multi-panel-main-text-figures-stack-dont-cram)
- [7. Page-count is not the metric — fullness is](#7-page-count-is-not-the-metric-fullness-is)
- [8. Quick checklist](#8-quick-checklist)


Deep reference for **typesetting/layout** requests (排版): loose pages, stranded
headings, figures that don't fill the page, "Float too large", page-splitting
figures, Supplementary Information that looks sparse. This is about *placement*,
not prose. Load it when the user asks to fix layout, spacing, figure placement,
page breaks, or "make it less empty / more compact / more beautiful".

Golden rule: **change → compile → render to image → look → iterate.** Never judge
layout from the `.tex` alone. Measure, don't guess.

---

## 0. Diagnosis workflow (do this first)

1. Compile and read the log for the three signals that matter:
   - `Float too large for page by Xpt` — a float (often figure+caption) exceeds the text height.
   - `Overfull \vbox` — content ran past the bottom margin (often `[H]` placement).
   - `Reference ... undefined` / `Citation ... undefined` — re-run needed (and for `xr-hyper`, compile the SI first, then the main file twice).
2. Render pages to PNG and *look*. With pymupdf:
   `fitz.open(pdf)[i].get_pixmap(dpi=90).save(...)`. Build a **contact sheet**
   (all pages as a grid) to spot whitespace, stranded headings, and split floats at a glance.
3. Measure figure aspect ratios from the source PDFs (`pypdf` mediabox, or pymupdf):
   `aspect = width/height`. Then `displayed_height_pt ≈ textwidth_pt / aspect`.
   For a 1-in-margin `article` on US Letter, `\textwidth ≈ 468 pt`, usable
   `\textheight ≈ 620–650 pt`. Budget every page against that height.

---

## 1. The "loose / 松散" float page — top-align the glue

**Symptom:** a page holding only floats (two tables, or a figure) has a big band of
whitespace in the middle / above, content seemingly centered with gaps.

**Cause:** LaTeX's float-page glue is rubber and spreads floats to fill the page:
`\@fptop = 0pt plus 1fil`, `\@fpsep = 8pt plus 2fil`, `\@fpbot = 0pt plus 1fil`.

**Fix:** top-align floats so they pack from the top and slack collects at the bottom
(reads as an intentional page tail, not "loose"):

```latex
\makeatletter
\setlength{\@fptop}{0pt}            % no stretch at top → floats start at top
\setlength{\@fpsep}{14pt}           % fixed gap between stacked floats
\setlength{\@fpbot}{0pt plus 1fil}  % all slack to the bottom
\makeatother
% Let a page hold more float and less forced text:
\renewcommand{\topfraction}{0.95}
\renewcommand{\bottomfraction}{0.95}
\renewcommand{\textfraction}{0.06}
\renewcommand{\floatpagefraction}{0.80}
\setlength{\textfloatsep}{16pt plus 3pt minus 3pt}
\setlength{\floatsep}{14pt plus 3pt minus 3pt}
```

This single change fixed the spread-apart table pages in practice (a two-table page
went from a centered gap to a tight top-aligned block). Apply it in the SI preamble.

---

## 2. Wide-and-short figures can never fill a portrait page — fix at the source

**Symptom:** a figure (e.g. a 1×N strip of per-dataset bars) sits at full width but is
short (aspect 3:1–4:1), leaving ~40–50% of the page empty; it also tends to strand the
next heading (see §4).

**Why LaTeX can't fix it:** the figure is width-bound at `\textwidth`. A 3.3:1 figure
at 468 pt wide is only ~140 pt tall. You cannot make it taller without making it wider
than the text, and stretching (`height=...` without keeping aspect) distorts it.

**Correct fix — regenerate the figure with a taller aspect** (target ~**1.9:1–2.2:1**)
so two stacked panels + caption fill the portrait page. In matplotlib this is just the
`figsize` height, e.g. `figsize=(17, 4.1)` → `figsize=(17, 6.8)`. Then:

- **Verify faithfulness before trusting regeneration:** re-run at the *original* size
  first and pixel-diff against the shipped PDF. Only if identical do you trust that
  changing the height won't drift fonts/colors/style.
- **Only touch the SI branch.** Main-text and SI versions are often produced by
  different functions (`plot_avg_bar` vs `plot_grouped_bar`); change only the one the
  SI uses, or you'll silently alter approved main-text figures.
- **Font-size caveat:** the on-page text size is set by the *display width* (figure
  scaled to `\textwidth`). Making a figure *taller* does **not** enlarge tick/label
  fonts — it only adds vertical extent (taller bars, more breathing room). To enlarge
  labels you must *narrow* the figure (more scale-up to `\textwidth`) or bump the
  in-plot font, not add height.
- **Mind the caption budget.** A 5–6 line caption is ~80 pt. Size the figure so
  `heading + intro + 2 panels + subcaptions + caption ≤ usable height`. A long-caption
  figure (e.g. a timeline) often needs to be ~0.5 in shorter than a short-caption one.

---

## 3. Do NOT rotate to landscape (Nature house style)

Nature / Nature Communications discourage rotated/landscape figures that force the
reader to turn the page. **Prefer a taller redraw (§2) over `\rotatebox` /
`sidewaysfigure`.** Landscape is *tolerated* in SI for genuinely un-squarable figures,
but try the redraw first. If the user defers ("do what Nature does"), choose upright.

---

## 4. Float backlog → stranded section headings

**Symptom (very common in figure-heavy SI):** two or more section headings pile at the
top of a page above a huge empty gap; their figures appear pages later.

**Cause:** big floats can't be placed, so they defer; meanwhile body text and the next
`\section` keep flowing and stack up. The headings out-run their figures.

**Fix — bind each figure section into a "heading + figure" unit:**

1. Make the figure short enough to *share a page* with its heading + intro
   (`heading + intro + figure ≤ usable height`; see §2 caption budget).
2. Start the section on a fresh page: `\clearpage` immediately before the `\section`.
   This guarantees full height is available.
3. Pin the figure with `[H]` (needs `\usepackage{float}`) right after the heading/intro
   so it cannot float away:

```latex
\clearpage
\section{Per-dataset context scaling}
Figure~\ref{fig:scaling} shows ...        % short intro
\begin{figure}[H]                         % H = exactly here, no floating
  ...two stacked panels...
  \caption{...}\label{fig:scaling}
\end{figure}
```

Result: a fresh page with heading + intro + figure + caption that fills the page, with
no stranded heading.

**Also pin the *preceding* section's trailing figure.** A `\clearpage` before a heading
flushes the page early — if the previous section ended with a big floating figure whose
intro text is still on the page, you strand that text instead. Give that trailing figure
`[H]` too (and size it to fit with its intro), so the page before the `\clearpage` is
also full. (In practice: a timeline figure had to be shrunk ~10% so its intro paragraph
+ figure + long caption fit one page.)

---

## 5. `[H]` and `placeins` — sharp edges

- **`[H]`** (float package) does not float. If the figure doesn't fit in the remaining
  space it either page-breaks *before* itself (stranding preceding text) or overflows
  (`Overfull \vbox`). Safe only when you guarantee room — hence pair it with `\clearpage`
  and size-to-fit. Great for the heading+figure unit; risky mid-page.
- **`\usepackage[section]{placeins}`** puts a `\FloatBarrier` at every `\section`, keeping
  a section's floats inside it. Useful against backlog — **but** it flushes the previous
  float and can strand the *current* heading alone on a page if that section's figure is
  too tall to share. It fixed a two-heading pile-up yet produced one-heading-per-empty-page
  until figures were also shortened. Use it *with* §2/§4 sizing, not as a standalone cure.
- **Don't blanket-`\clearpage` every section.** Section-boundary clearpages create
  near-empty pages when a section is short. Use `\clearpage` surgically (figure sections,
  §4), not everywhere. (Removing 8 blanket clearpages once took an SI 23→21 pages with
  even density.)

---

## 6. Multi-panel main-text figures — stack, don't cram

- A 2×2 grid shrinks panels; for **wide** panels prefer a **single-column vertical stack**
  (`a` over `b` over `c` over `d`), each near full width, on a dedicated float page `[p]`.
  Reads larger and matches a 2-panel `a/b` stacked figure elsewhere.
- Tune inter-panel space with `\vspace` between `subfigure`s (e.g. `0.3em–0.8em`).
- If you see `Float too large for page by X pt` and X is small (<5 pt), shave the
  smallest thing first: reduce inter-panel `\vspace`, or panel width by ~2%, before
  touching the figure itself.

```latex
\begin{figure}[p]\centering
  \begin{subfigure}{0.66\textwidth}\includegraphics[width=\textwidth]{a}\caption{}\end{subfigure}
  \vspace{0.3em}
  \begin{subfigure}{0.66\textwidth}\includegraphics[width=\textwidth]{b}\caption{}\end{subfigure}
  ...
  \caption{...}\label{...}
\end{figure}
```

---

## 7. Page-count is not the metric — *fullness* is

Tightening loose pages can *reduce* count; enlarging short figures to fill pages can
*increase* it. Both are correct. A 20-page SI where every page is full beats a 19-page SI
with half-empty figure pages. Optimize for even density and no stranded headings, not for
the smallest page count.

---

## 8. Quick checklist

- [ ] Top-aligned float glue in the preamble (§1).
- [ ] Wide-short figures regenerated to ~2:1, SI branch only, faithfulness pixel-checked (§2).
- [ ] Upright, not landscape (§3).
- [ ] Each figure section: `\clearpage` + `[H]` heading-figure unit; trailing figure of the
      previous section also `[H]` and sized to fit (§4).
- [ ] No blanket section clearpages; no stranded headings (§5).
- [ ] Compile clean: no "Float too large", no "Overfull \vbox", no undefined refs.
- [ ] Contact-sheet the final PDF and eyeball every page (§0).
