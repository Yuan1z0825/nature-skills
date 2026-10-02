# Equation handling

## Contents

- [Goal](#goal)
- [Portable Markdown math](#portable-markdown-math)
- [Display-equation block](#display-equation-block)
- [Confidence ladder and visual fallback](#confidence-ladder-and-visual-fallback)
- [Equation index](#equation-index)
- [公式索引](#公式索引)
- [Source-map contract](#source-map-contract)
- [Compatibility fallback](#compatibility-fallback)


Load this reference whenever the source contains equations, mathematical expressions, chemical formulae, custom LaTeX macros, or image-only formulae.

## Goal

The reader must show a usable equation, not a line of raw LaTeX that forces the user back into the PDF. Preserve source fidelity and make uncertainty visible.

## Portable Markdown math

Use syntax supported by GitHub-flavoured Markdown renderers with MathJax:

- inline math: `$E = mc^2$`
- display math: put opening and closing `$$` on their own lines
- fenced `math` blocks are acceptable only when dollar signs inside the expression make `$$...$$` ambiguous

Do not put formulas in ordinary backticks or generic code fences. Do not leave commands such as `\frac`, `\sum`, `\alpha`, or `\begin{aligned}` in prose outside a math block.

Keep the publisher's printed equation number outside the math delimiters so the renderer cannot swallow or reposition it.

## Bilingual formula preservation

Do not translate mathematical content. Preserve formulas, symbols, indices, operators, Greek letters, and units exactly as they appear in the verified source. Translate only prose that introduces, defines, or interprets them.

For a display equation, emit one shared `E...` block. Do not repeat or rewrite the equation under `**中文:**`:

```markdown
**Original:** The peak intensity is

<a id="E001"></a>
**Source:** p.6 E001

$$
I_0=\frac{4E_0}{\pi w_0^2\tau}\sqrt{\frac{\ln(2)}{\pi}}
$$

**中文:** 峰值强度由上方原式给出。其中 $I_0$ 为峰值强度，$E_0$ 为脉冲能量，$w_0$ 为焦斑半径，$\tau$ 为脉宽。
```

Forbidden forms include `(I_0)`, `(E_0=...)`, `(tau)`, `(Delta T)`, translated variable names, Unicode approximations that change the source notation, and bare LaTeX outside math delimiters. Ordinary parentheses remain valid for prose labels such as `Fig. 2(a)`; they must not be used as a substitute for `$...$`.

## Display-equation block

Assign every display equation a stable `E...` ID in reading order:

```markdown
<a id="E001"></a>
**Source:** p.4 E001 · Eq. (3)

$$
\mathcal{L}(\theta) = \sum_{i=1}^{n} \log p(y_i \mid x_i, \theta)
$$

**中文说明：** 该式定义了训练目标；符号和变量名称保持原样。
```

Translate or explain surrounding prose, but do not translate variable names or alter mathematical meaning. If the source has no printed equation number, omit `Eq. (...)`; never invent one.

## Confidence ladder and visual fallback

Use the highest trustworthy representation:

1. **High confidence:** publisher MathML/LaTeX or source TeX verified against the rendered page. Emit the rendered math block.
2. **Medium confidence:** reconstructed from a selectable PDF and visually checked. Emit the math block and record `confidence: "medium"`.
3. **Low confidence or image-only:** crop the original equation into `assets/equations/E001.png` (or `.svg`), show the crop first, and add best-effort LaTeX only when it is useful. Label it `低置信度转写 / Low-confidence transcription`.

Example fallback:

```markdown
<a id="E001"></a>
**Source:** p.4 E001 · Eq. (3) · low confidence

![Original equation E001](assets/equations/E001.png)

**低置信度转写（请以原图为准）：**

$$
\widetilde{f}(x) \approx \sum_k a_k \phi_k(x)
$$
```

Never infer an unreadable symbol from context. When a useful transcription cannot be produced, keep the crop and write `LaTeX transcription unavailable` rather than emitting invented math.

## Equation index

When the reader contains three or more display equations, add a compact index near the page/section index:

```markdown
## 公式索引

- [E001 · Eq. (1)](#E001) — p.3，损失函数
- [E002 · Eq. (2)](#E002) — p.4，更新规则
```

The label may add a short reader-facing description, but it must not replace the source equation number.

## Source-map contract

Each display equation must have a matching `blocks` entry of `type: "equation"`:

```json
{
  "id": "E001",
  "page": 4,
  "type": "equation",
  "order": 17,
  "equation_number": "3",
  "latex": "\\mathcal{L}(\\theta) = \\sum_{i=1}^{n} ...",
  "bbox": [88, 214, 513, 286],
  "confidence": "high",
  "image_path": null
}
```

For a visual fallback, set `image_path` to the relative crop path and retain `latex` only if a best-effort transcription is shown. `page`, `confidence`, and at least one of `latex` or `image_path` are required.

## Compatibility fallback

Markdown remains the primary artifact. If the user's target viewer does not support math or they report seeing raw LaTeX, generate `reader.html` as an additional artifact with KaTeX or MathJax and keep the same `E...` anchors. Do not silently replace `paper.md`.

Before delivery, run:

```bash
python scripts/validate_reader_math.py paper.md --source-map source_map.json
```
