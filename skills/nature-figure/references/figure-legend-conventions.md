# Figure & Table Legend Conventions (Nat Commun 2025 CS/AI corpus)

Use this file when **writing or auditing the legend text** of a figure or table.
It complements `nature-2026-observations.md`, which covers visual/layout
archetypes; this file covers the *words* of the caption. Distilled from a 2025
set of 20 open-access *Nature Communications* computer-science / AI papers
(legend conventions were consistent across all research articles). **Do not copy
source wording.**

## Legend structure — the fixed skeleton

1. **`Fig. N | ` + a bold noun-phrase overall title** that names the whole
   figure. Common openers: *Overview of …*, *Comparison of …*, *Performance of
   …*, or a finding phrase. No terminal full stop required on the title.
2. **`a / b / c …` panels, each described in present tense, telegraphic style**,
   often subject-less: *"a Comparison of the four EMS paradigms. b Distributions
   of WSIs and patches in the pre-training dataset."*
3. **Statistics written into the legend**: sample size `n=`, error type, and
   test — *"mean ± 95% CI (n = 1373) … one-way ANOVA with Tukey correction."*
4. **Data-availability boilerplate** at the end: *"Source data are provided as a
   Source Data file."*

## Tense

- Visual facts in **present** tense — *"are shown as cyan sticks"*, *"depicts"*.
- Methods/how-it-was-made in **past** tense — *"was performed"*, *"was adopted
  from"*.

## Self-containment rule

A legend must be readable away from the body text. Put colour/shape mappings,
sample size, and key numeric anchors (PDB id, RMSD, units) into the legend
itself — *"tRNA-Glu of E. coli (PDB: 2DER chain C). 76 nt, RMSD: 2.88 Å."*;
*"Grey boxes designate what is defined by the benchmark, and orange boxes
indicate what is unique to each solution."*

## Display-label capitalization

- Treat in-figure legend entries as display labels. Start ordinary descriptive labels with an uppercase letter, for example `Tuned XGBoost`, `Tuned RF`, `+ Semantic guidance`, and `+ Causal guidance`.
- Preserve canonical product/model spelling exactly, including internal capitals, hyphens, periods, and abbreviations such as `XGBoost`, `DeepSeek`, `GPT-5.2`, and `RF`.
- In prose legend sentences, use normal sentence grammar rather than forcing every term into display case.
- Do not apply `.title()` or equivalent automatic title-casing because it corrupts canonical names.

## Advanced: the claim-closing sentence

A legend's final sentence may advance an argument rather than only describe —
*"…indicating that these co-folding models are not predicting poses based on
physics but rather learning patterns in global structures."* Use sparingly, and
only when the panel actually supports the inference.

## Review/Perspective legends

When a figure aggregates others' published systems, each sub-panel gets a
one-line characterisation (often past tense, describing prior work) and the
legend carries an attribution line — *"adapted with permission from refs. 16,17
… by Springer Nature."* Include the permission/attribution string for any
adapted panel.

## Table captions

Same shape: **`Table N | ` + noun phrase**, with detailed specs pointed to
Methods — *"Table 1 | … Detailed specifications are provided in the Methods
section."* Benchmark/framework papers lean on tables (multi-metric results) more
than figures.

## Length and journal gate

- This file's corpus evidence is from Nature Communications and does not set a
  universal Nature Portfolio word limit.
- For the flagship journal Nature, load `nature-article-requirements.md` and
  keep each complete figure legend below 250 words.
- For Nature Communications or another subjournal, verify the current journal
  and article-type instructions before enforcing a numerical cap.
- Keep the `Fig. N |` title short and nominal; no numbers/results in the figure
  *title* line (numbers live in the panels and stats).

## 中文图注要点

- 结构铁律:`图 N | 加粗名词短语总题` → `a/b/c` 现在时电报式分面 → 统计(n、误差、检验)写进图注 → "Source data are provided as a Source Data file." 套语。
- 时态:视觉事实用现在时,制作方法用过去时。
- 自足:颜色/形状映射、样本量、关键数值(PDB/RMSD/单位)都写进图注,使其脱离正文可读。
- 图内图例按展示标签处理,普通描述首字母大写,同时保留 `XGBoost`、`DeepSeek`、`GPT-5.2`、`RF` 等规范拼写;正文仍按句法大小写,不要盲目自动 title case。
- 进阶:图注末句可给一句推断结论,但须确有面板支撑。
- 综述图注:聚合他人系统时逐子图一句话定性,并标注"adapted with permission from refs… by Springer Nature"授权。
