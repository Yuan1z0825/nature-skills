# nature-skills
当算法构筑世界，当智能引领未来，顶尖的灵魂终将相遇。
TOP AI CREW 顶尖AI人才联盟正式招募！
这里汇聚经过严格筛选的行业强者，多元思维碰撞，前沿技术共生。
拒绝单打独斗，告别低效内耗，和一群同频的顶尖伙伴并肩前行，深耕AI领域，突破技术边界，一同站上行业前沿。
敢想、敢闯、敢创造，下一个AI传奇，由我们共同书写！

感谢大家持续关注 nature-skill。如果你有任何需求，欢迎提交 issue；如果我们认为该需求有意义且可行，也会尽量推进实现。我们同样欢迎 PR，但请务必按照 README 后面说明的格式提交，以便我们更高效地审核与合并。
<table>
  <tr>
    <td align="center">
      <b>TOP AI CREW 顶尖AI人才联盟</b><br>
      <img width="1672" height="2453" alt="232c0c2e87d7e52eb9cebff6dea41382" src="https://github.com/user-attachments/assets/078bd8df-9715-413a-b243-3d1519c5936d" />
    </td>
    <td align="center">
      <b>个人微信</b><br>
      <img width="400" alt="个人微信" src="https://github.com/user-attachments/assets/9e2931fb-748b-418e-97ab-0515d191633d" />
    </td>
  </tr>
</table>

Hello everyone, I'm Yizhe Yuan, a Ph.D. candidate at Shanghai Jiao Tong University. My work primarily focuses on Medical AI research and entrepreneurial initiatives, and I am currently planning to establish related ventures in Zhangjiang, Pudong (Shanghai).
If you have access to disease-specific pathology cohorts or large-scale pan-cancer cohorts (10,000+ patients), are building a startup in a related field, or are an investor interested in my work, feel free to connect with me via WeChat. Please include a brief note explaining the purpose of your contact request.
Thank you for your continued interest in nature-skill.
If you have any feature requests or suggestions, please feel free to submit an Issue. If we find the proposal meaningful and feasible, we will do our best to implement it. We also welcome Pull Requests (PRs). However, please follow the contribution format described later in this README to help us review and merge submissions more efficiently.

## 📢 课题组诚招“医学 + AI”实习生
<table border="0" cellpadding="10" cellspacing="0">
  <tr>
    <td width="34%" valign="top" align="center" style="border: none; background-color: #f9f9f9; padding: 20px; border-radius: 8px;">
      <span style="font-size: 14px; color: #666;">微信群聊</span><br>
      <img width="1080" height="1632" alt="feae2bf93421fbf99d21f20f2cf5562a" src="https://github.com/user-attachments/assets/388f4f6c-9f3e-4582-8136-e15676dff889" />
      <div style="margin-top:10px; font-size: 13px; color: #666;">答疑交流群！进群请立刻改备注</div>
    </td>
    <td width="66%" valign="top" style="border: none; line-height: 1.6;">
      还在寻找能够落地的 <strong>AI 前沿交叉赛道</strong>吗？我们课题组现向对“医学 + AI”充满热情的你发出邀请！<br><br>
      这里有充足的计算资源，以及深耕医疗大模型（LLM）、视觉预训练、Prompt Engineering 及自动化医疗 AI Agent 的科研团队。我们更看重你的<strong>自驱力、学习能力与科研产出追求</strong>。<br><br>
      项目信息文档链接：https://iigqjt2m4ia.feishu.cn/wiki/VIvDwHu18iTc6mk411xco8chnJb   密码：664#N926<br>
      如果你有相关代码基础或项目经验，渴望在顶级交叉学科中积累成果，请将简历发送至：<br>
      📧 <strong><a href="mailto:sjtu520aimedws@163.com" style="text-decoration: none; color: #0056b3;">sjtu520aimedws@163.com</a></strong><br>
      <small>（标题格式：姓名-专业-医学AI科研申请）</small><br><br>
      期待与你在 AI 赋能医疗的征途中，做出最扎实的科研工作！
    </td>
  </tr>
</table>

---

## Installation

`nature-skills` is a repository of reusable instruction bundles centred on `SKILL.md`.
Each `skills/nature-*` directory is one installable unit. Copy the whole folder, not
only `SKILL.md`, because many skills depend on `references/`, `static/`, assets,
scripts, or README context. The `skills/_shared/` directory is shared support
content used by several skills and should stay next to the `nature-*` folders
when you install skills manually.

### 1. Codex

**Codex plugin marketplace installation**

This repository includes Codex plugin packaging at `plugins/nature-skills/`, so
Codex users can install the complete Nature Skills bundle from the plugin
marketplace instead of copying each skill folder manually.

CLI installation:

```bash
codex plugin marketplace add https://github.com/Yuan1z0825/nature-skills --ref main
codex plugin add nature-skills@nature-skills
```

Codex Desktop users can add the same repository as a custom plugin marketplace:

- Marketplace source: `https://github.com/Yuan1z0825/nature-skills.git`
- Branch/ref: `main`
- Plugin: `nature-skills`

After installation, all `nature-*` skills are available through the plugin as a
complete bundle, together with the shared support directory used by the newer
router-style skills. If the skills do not appear immediately, refresh the plugin
page or start a new Codex session.

**Manual local-skill installation**

Codex can also use these folders directly as local skills.

**Clone the repo**

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
```

**Install one skill**

```bash
mkdir -p ~/.codex/skills
cp -R skills/_shared ~/.codex/skills/
cp -R skills/nature-reader ~/.codex/skills/
```

Copying `_shared` is harmless even for skills that do not use it, and it avoids
broken relative references for skills such as `nature-reader`, `nature-writing`,
`nature-polishing`, and `nature-paper2ppt`.

**Install all current skills**

```bash
mkdir -p ~/.codex/skills
cp -R skills/_shared ~/.codex/skills/
for d in skills/nature-*; do
  cp -R "$d" ~/.codex/skills/
done
```

**Update after pulling new changes**

```bash
git pull
cp -R skills/_shared ~/.codex/skills/
for d in skills/nature-*; do
  cp -R "$d" ~/.codex/skills/
done
```

**Finish**

- Restart Codex so newly added skills are picked up.
- Then ask naturally, for example: `Translate this paper into a full markdown reader.` or
  `Make this paper into a Chinese journal-club PPT.`

If you prefer not to use the terminal, copying the `skills/nature-*` folder(s) into
`~/.codex/skills/` manually works as well; also copy `skills/_shared/` once. For
a longer walkthrough, see [`install.md`](install.md).

### 2. Claude Code

**Claude Code plugin marketplace installation**

This repository also includes Claude Code plugin metadata at
`.claude-plugin/`, so Claude Code users can install the complete Nature Skills
bundle directly as a plugin instead of setting up wrappers first.

CLI installation:

```bash
claude plugin marketplace add Yuan1z0825/nature-skills
claude plugin install nature-skills@nature-skills
```

If the plugin does not appear immediately, refresh the plugin page or start a
new Claude Code session.

**Alternative: wrapper/subagent installation**

Claude Code can also use a thin subagent or slash-command wrapper that points
to a stable clone of this repository, so supporting files such as
`references/`, `static/`, assets, scripts, and `skills/_shared/` remain
available.

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

Create a user-level subagent wrapper:

```bash
mkdir -p ~/.claude/agents
cat > ~/.claude/agents/nature-reader.md <<'EOF'
---
name: nature-reader
description: Full-paper bilingual, figure-aware, source-grounded Markdown reader for journal or conference papers. Use proactively when the user asks to translate an entire paper or generate a complete markdown reader.
---

When invoked, first read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md`.
Treat that file as the governing workflow.
If the skill references supporting files, read only the specific files you need from
`~/ai-skills/nature-skills/skills/nature-reader/` and
`~/ai-skills/nature-skills/skills/_shared/`.
Do not replace the skill with a generic paper-summary response.
EOF
```

After that, start a new Claude Code session or open `/agents`, and invoke it
naturally or explicitly:

```text
Use the nature-reader subagent to turn this PDF into a full markdown reader.
```

If you prefer commands instead of subagents, create a project or user command under
`.claude/commands/` or `~/.claude/commands/` that tells Claude Code to read the
real `SKILL.md` from the cloned repository.

Official Claude Code docs:

- [Subagents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)
- [Slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands)

### 3. Other agents or manual use

If your agent supports reusable prompt files, system prompts, or agent profiles, the minimum
portable unit is the skill directory itself:

```text
skills/
├── _shared/              # keep this when a skill references ../_shared
└── nature-<topic>/
    ├── README.md
    ├── SKILL.md
    ├── manifest.yaml     # present for router-style skills
    ├── static/           # present for router-style skills
    └── references/...
```

In that case:

1. Copy the whole skill directory into your prompt library or project.
2. Preserve `SKILL.md`, `manifest.yaml`, `static/`, `references/`, scripts, assets,
   and any needed `skills/_shared/` files together.
3. Adapt the frontmatter and body to the target agent's native format if needed.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Yuan1z0825/nature-skills&type=Date&cache_bust=2026-06-07T16)](https://star-history.com/#Yuan1z0825/nature-skills&Date)


## Skill index

| Skill | Status | Purpose | Trigger keywords |
|-------|--------|---------|-----------------|
| [`nature-figure`](skills/nature-figure/README.md) | Stable | Nature/high-impact Python or R figure workflow with bundled figures4papers demos | "Nature figure", "publication plot", "scientific figure", "figures4papers" |
| [`nature-polishing`](skills/nature-polishing/README.md) | Stable | Academic prose polishing to *Nature* style | "Nature style", "polish", "academic writing" |
| [`nature-writing`](skills/nature-writing/README.md) | Draft | Nature-style manuscript section drafting and argument restructuring | "Nature writing", "write abstract", "write introduction", "manuscript draft" |
| [`nature-reviewer`](skills/nature-reviewer/README.md) | Draft | Nature-style reviewer assessment with 3 referee reports and a cross-review synthesis | "Nature reviewer", "pre-submission review", "reviewer report", "peer-review critique", "审稿人视角评估" |
| [`nature-citation`](skills/nature-citation/README.md) | Beta | Strict Nature / CNS-family citation retrieval with ENW, RIS, and Zotero RDF export | "Nature citation", "CNS citation", "text citation", "supporting references", "Zotero RDF" |
| [`nature-data`](skills/nature-data/README.md) | Draft | Nature Data Availability statements, repository plans, and FAIR checks | "Data Availability", "repository", "FAIR metadata", "data availability statement" |
| [`nature-reader`](skills/nature-reader/README.md) | Beta | Full-paper bilingual Markdown reader with source anchors and figure grounding | "nature reader", "full markdown", "paper md", "原文对照", "图文对应", "全文翻译" |
| [`nature-response`](skills/nature-response/README.md) | Beta | Point-by-point reviewer response letters with comment triage, action mapping, and risk checks | "response to reviewers", "rebuttal letter", "major revision", "审稿意见回复" |
| [`nature-paper2ppt`](skills/nature-paper2ppt/README.md) | Beta | Chinese PPTX decks from scientific papers | "paper PPT", "journal club", "paper to slides", "paper presentation" |
| [`nature-academic-search`](skills/nature-academic-search/README.md) | Beta | Multi-source literature search, citation verification, and reference management | "search papers", "find articles", "academic search", "literature search", "verify DOI" |

> **Adding a new skill?** Follow the [contribution guide](#adding-a-new-skill) at the bottom of this file.

---

## nature-figure

**What it does** — Generates multi-panel matplotlib figures that match *Nature* journal
visual standards: correct typography, semantic colour palette, editable SVG output,
and non-redundant panel information architecture.

**Example output gallery** — Five dense, simulated *Nature*-style result figures are
included in the [`nature-figure` gallery](skills/nature-figure/README.md#example-output-gallery):
material/mechanism, spatial imaging, in vivo efficacy, single-cell systems and
perturbation validation.

**Chart-type atlas** — The [`nature-figure` chart atlas](skills/nature-figure/README.md#chart-type-atlas)
classifies 10 supported chart families, including bar, line, heatmap, scatter/bubble,
radar/polar, distribution, forest/interval, area/stacked, image-plate and network/matrix
layouts.

| ![Material design and physical validation](skills/nature-figure/assets/gallery/fig1-material-mechanism-rich.png) | ![Spatial imaging and uptake](skills/nature-figure/assets/gallery/fig2-spatial-imaging-rich.png) | ![In vivo efficacy and tolerability](skills/nature-figure/assets/gallery/fig3-in-vivo-efficacy-rich.png) | ![Single-cell systems figure](skills/nature-figure/assets/gallery/fig4-single-cell-systems-rich.png) | ![Perturbation validation](skills/nature-figure/assets/gallery/fig5-validation-perturbation-rich.png) |
|---|---|---|---|---|

**Built from** — Production scripts from papers published in *Nature Machine Intelligence*
and top ML/bioinformatics venues ([figures4papers](https://github.com/ChenLiu-1996/figures4papers)).
The figures4papers demo scripts and preview assets are bundled inside
`skills/nature-figure/assets/figures4papers/`, with a routing guide at
`skills/nature-figure/references/demos.md`.

**Key rules enforced**

- Three mandatory rcParams must always appear first:
  ```python
  plt.rcParams['font.family'] = 'sans-serif'
  plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
  plt.rcParams['svg.fonttype'] = 'none'   # text stays as <text> nodes, not paths
  ```
- Primary output is always `.svg`; `.png` at 300 dpi is a secondary raster preview.
- Multi-panel figures follow a three-level information hierarchy: **overview → deviation → relationship**. No two panels may answer the same scientific question.

**Reference files**

```
skills/nature-figure/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
└── references/
    ├── api.md            PALETTE, helper signatures, validation rules
    ├── design-theory.md  Typography, layout, export policy, anti-redundancy rules
    ├── common-patterns.md Ultra-wide panels, legend axes, print-safe bars
    ├── tutorials.md      End-to-end walkthroughs (bars, trends, heatmaps)
    ├── chart-types.md    Radar, 3D sphere, scatter, fill_between, log-scale
    └── demos.md          Bundled figures4papers scripts and preview routing
```

**Supported chart types** — Stacked bar, grouped bar, horizontal ablation bar, trend/line,
sequential heatmap, diverging z-score heatmap, bubble scatter, radar/polar, 3D sphere
illustration, fill-between area, log-scale bar, GridSpec multi-panel.

---

## nature-polishing

**What it does** — Transforms academic draft text (including Chinese → English translation)
into prose matching *Nature* journal conventions: ≤ 30-word sentences, section-aware
tense and hedging, precise vocabulary, correct citation practice, and British English.

**Built from** — A graduate-level scientific English writing course, Academic Phrasebank,
and close reading of curated *Nature* and *Nature Communications* research articles
across materials, energy systems, construction decarbonization and machine learning.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Sentence length | Every sentence ≤ 30 words; count individually; last sentence most likely to fail |
| Hedging calibration | Match claim strength to evidence: *demonstrate* → *suggest* → *may reflect* |
| Section tense | Results = past tense + quantitative detail; Discussion = hedging + mechanism |
| Citation integrity | Cite only sources personally read and verified; four attribution types |
| Overclaim detection | Flag absolutes, unwarranted causation, scope expansion, unverified "first" claims |
| British English | signalling, colour, analyse, programme, modelling, behaviour |

**12-step polishing workflow**

Sentence split → Section ID → Hourglass check → Tense audit → Sentence edit →
Vocabulary upgrade → Template check → Citation audit → House style → Overclaim →
Proofreading → Plain-text output

**Reference files**

```
skills/nature-polishing/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
└── references/
    ├── latex-layout.md
    ├── published-article-patterns.md
    ├── phrasebank-playbook.md
    ├── section-moves.md
    ├── style-guardrails.md
    └── writing-strategy.md
```

---

## nature-writing

**What it does** — Drafts or rebuilds manuscript sections from author-provided
claims, results, figures, notes, or Chinese drafts. It is for argument construction:
abstracts, introductions, Results narratives, Discussions, Conclusions, titles and
full manuscript outlines, method sections, experiment sections and reviewer-facing
self-review.

**Built from** — Close reading of curated *Nature* and *Nature Communications*
articles, especially how published papers move from field-scale stakes to a narrow
gap, then to evidence, interpretation and bounded implication. It also integrates
open research-writing notes for paragraph flow, section logic and adversarial
paper review.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Evidence first | Do not invent data, mechanisms, references, statistics, novelty or limitations |
| Abstract | Context/problem → gap → approach → key result → implication → boundary |
| Introduction | Field scale → bottleneck → prior attempts → unresolved gap → present study |
| Method | Module motivation → module design → forward process → technical advantage |
| Results | Build an evidence ladder, not a chronological lab diary |
| Experiments | Tie claims to baselines, ablations, metrics, stress tests and readable tables |
| Discussion | Explain meaning, relation to prior work, constraints and future use |
| Review | Run claim-evidence and rejection-risk checks before submission |
| Chinese notes | Translate intent and argument, not clause order |

**Reference files**

```
skills/nature-writing/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
├── agents/
│   └── openai.yaml
└── references/
    ├── abstract.md
    ├── article-architecture.md
    ├── chinese-author-workflow.md
    ├── conclusion.md
    ├── experiments.md
    ├── introduction.md
    ├── method.md
    ├── paper-review.md
    ├── paragraph-flow.md
    ├── related-work.md
    └── examples/
```

---

## nature-reviewer

**What it does** — Simulates a Nature-style pre-submission reviewer assessment
from the referee perspective. It returns three reviewer reports plus a
cross-review synthesis, focusing on novelty, significance, technical soundness,
presentation, and likely editorial risk.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Reviewer role | Assess as external referees, not as an author rebuttal writer |
| Evidence grounding | Use only the manuscript/material supplied by the user and the local reviewer source basis |
| Multi-reviewer output | Produce three distinct reviewer reports plus a synthesis |
| Editorial relevance | Separate novelty, significance, technical confidence, presentation, and decision risk |
| Boundaries | Do not invent experiments, citations, journal policy, or manuscript content |

**Reference files**

```text
skills/nature-reviewer/
├── README.md
├── SKILL.md
└── references/
    ├── source-basis.md
    ├── reviewer-workflow.md
    ├── review-axes.md
    ├── report-structure.md
    ├── role-boundaries.md
    └── qa-checklist.md
```

---

## nature-citation

**What it does** — Converts manuscript text or standalone claims into strict Nature / CNS-family
citation candidates, then exports one reference-manager-ready file in `ENW`, `RIS`, or Zotero
`RDF`. It can also generate an HTML screening page for year filtering, citation selection, and
format-specific download.

**Built from** — Crossref metadata retrieval, DOI record export, and journal-family filtering logic
for Nature Portfolio, the AAAS Science family, and Cell Press.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Scope filtering | Restrict to Nature Portfolio, Science family, Cell Press, or flagship-only journals |
| Segmentation | Split long text into citable claim units with stable segment IDs |
| Search discipline | Translate Chinese claims into English scientific concepts; prefer precision over volume |
| Support grading | Distinguish strong, partial, background, limiting, and metadata-only support |
| Export integrity | Do not fabricate DOI, pages, volume, issue, or journal metadata |
| Download options | Support one-file export in `ENW`, `RIS`, or Zotero `RDF` |

**Reference files**

```text
skills/nature-citation/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
├── references/
│   ├── journal-scope.md
│   ├── ris-endnote.md
│   ├── script-usage.md
│   └── search-strategy.md
└── scripts/
    └── nature_citation.py
```

**Example workflow** — Segment a paragraph, search in-scope citations, review candidates in the
HTML browser, then download only the selected records as `ENW`, `RIS`, or Zotero `RDF`.

---

## nature-data

**What it does** — Prepares and audits Data Availability statements, repository plans,
dataset citations, and FAIR metadata checks for Nature-family and Springer Nature
submissions. It is bilingual-aware: Chinese author notes such as "data availability statement",
"request from corresponding author", "raw data", "restricted data", and "public database" are converted into precise
submission-ready English with Chinese action notes.

**Built from** — Springer Nature research data policy, Nature Portfolio reporting standards,
Scientific Data repository and citation practice, the FAIR Guiding Principles, and DataCite
metadata conventions.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Data Availability | Map every result-supporting dataset to a durable access route |
| Repository strategy | Prefer mandated or discipline-specific repositories with persistent identifiers |
| Restricted data | State the restriction reason, controller, review route, and access conditions |
| Dataset citations | Cite public datasets with DataCite-style creator, title, repository, year, and identifier metadata |
| FAIR metadata | Check identifiers, licence, README/data dictionary, provenance, version, and reuse conditions |
| Chinese alignment | Translate intent rather than literal wording; flag vague "reasonable request" phrasing |

**Reference files**

```
skills/nature-data/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
├── agents/
│   └── openai.yaml
└── references/
    ├── chinese-author-alignment.md
    ├── fair-metadata-checklist.md
    ├── policy-principles.md
    ├── repository-and-identifiers.md
    ├── source-basis.md
    └── statement-patterns.md
```

---

## nature-response

**What it does** — Drafts, audits, and revises point-by-point reviewer response
letters for Nature-family and high-impact journal manuscript revisions. It treats the
response letter as an editor-facing verification document: every reviewer concern is assigned
a stable ID, classified, mapped to an action, and tied to manuscript evidence, a revision
location, or an unresolved author-input flag.

**Built from** — Nature editorial process guidance, Nature-family revision-package
instructions, Springer Nature rebuttal advice, and transparent peer-review considerations.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Completeness | Every reviewer comment receives an ID and a response, cross-reference, or unresolved flag |
| Action mapping | Each reply maps to a concrete manuscript action such as `ACCEPT_TEXT`, `ACCEPT_ANALYSIS`, `SOFTEN_CLAIM`, or `AUTHOR_INPUT_NEEDED` |
| Traceability | Claimed changes must cite a section, page, line, figure, table, supplement, citation, or visible placeholder |
| Factuality | Do not invent experiments, analyses, citations, line numbers, figure panels, editor instructions, or manuscript changes |
| Tone | Use cooperative, evidence-forward language; disagree only with scientific or scope-based reasoning |
| Chinese alignment | Convert Chinese author notes into English response prose plus Chinese confirmation items when needed |

**Reference files**

```
skills/nature-response/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
├── references/
│   ├── action-mapping.md
│   ├── chinese-author-alignment.md
│   ├── comment-taxonomy.md
│   ├── difficult-cases.md
│   ├── intake-and-routing.md
│   ├── qa-checklist.md
│   ├── response-structure.md
│   ├── source-basis.md
│   └── tone-and-stance.md
├── tests/
    ├── conflicting-reviewers.md
    ├── defensive-draft-audit.md
    ├── evaluation-summary.md
    ├── impossible-experiment.md
    ├── major-revision-missing-evidence.md
    ├── minor-revision.md
    └── rubric.md
└── examples/
    ├── conflicting-reviewers.md
    ├── major-revision-with-missing-evidence.md
    └── minor-revision.md
```

---

## nature-paper2ppt

**What it does** — Turns a scientific paper, preprint, PDF, article text, abstract,
figure legends, or reading notes into a concise Chinese `.pptx` presentation for journal
club, group meeting, lab meeting, paper sharing, or thesis seminar.

The skill identifies the paper type and central argument, selects only figures and tables
that support the evidence chain, writes Chinese slide titles, bullets, captions, takeaways
and speaker notes, creates the actual PPTX deck, and runs lightweight package QA.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Narrative | Use the paper's scientific argument as the slide spine, not the manuscript section order |
| Paper type | Classify the paper before choosing claim-first, problem-to-solution, workflow-to-validation, or evidence-map logic |
| Figures | Use figures as evidence; crop or split dense panels rather than shrinking them into unreadable slots |
| Output | Build a real `.pptx` as the primary deliverable, with Chinese text and speaker notes |
| QA | Reopen or inspect the PPTX package, record slide count, embedded media, notes, and any rendering limits |
| Integrity | Do not fabricate results, methods, numbers, datasets, mechanisms, or figure details |

**Reference files**

```
skills/nature-paper2ppt/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
└── references/
    ├── design-and-layout.md
    ├── figure-assets.md
    └── self-review.md
```

---

## nature-academic-search

**What it does** — Provides a multi-source academic search and reference-management
workflow backed by a local MCP server. It searches PubMed, CrossRef and arXiv in
parallel, fetches records by DOI, PMID or arXiv ID, formats citations, looks up MeSH
terms, verifies bibliographic identifiers, and supports `.nbib`, `.ris`, `.bib` and
`.enw` reference-file workflows.

**Built from** — A unified MCP server with source adapters for PubMed E-utilities,
CrossRef REST metadata and arXiv Atom metadata, plus reusable workflow notes for
source-tier routing, search strategy, citation parsing, deduplication, RIS/BibTeX
field mapping and reference-file conversion.

**Setup note** — For Claude Code MCP use, run
`bash skills/nature-academic-search/install.sh your-email@example.com`, restart Claude Code,
and optionally set `NCBI_API_KEY` for higher PubMed rate limits. For plain prompt use,
copy the whole `skills/nature-academic-search/` directory like the other skills.

**Key rules enforced**

| Domain | Core rule |
|--------|-----------|
| Source routing | Start with structured API-backed sources: PubMed for biomedical searches, CrossRef for DOI and cross-disciplinary metadata, and arXiv for preprints |
| Fallback discipline | Escalate from T1 sources to limited APIs or scraped/manual sources only when needed, and warn when results may be incomplete |
| Deduplication | Merge multi-source hits by DOI, PMID, arXiv ID and normalized title rather than counting duplicate records as separate evidence |
| Citation verification | Resolve DOI, PMID and arXiv IDs before citation formatting; expose missing or failed metadata instead of filling fields by guesswork |
| MeSH strategy | Use MeSH lookup for biomedical PubMed queries when the task needs recall, controlled vocabulary or systematic search structure |
| File integrity | Preserve bibliographic fields when converting `.nbib`, `.ris`, `.bib` and `.enw`; do not fabricate volume, issue, pages, DOI or PMID values |

**MCP tools**

| Tool | Purpose |
|------|---------|
| `search_papers` | Search CrossRef, PubMed and arXiv with optional source selection and per-source result limits |
| `get_paper_by_id` | Fetch paper metadata by DOI, PMID or arXiv ID with automatic ID-type detection |
| `get_citation` | Generate formatted citations in styles such as APA, Nature, IEEE, Vancouver, Chicago and MLA |
| `lookup_mesh` | Query PubMed MeSH descriptors for biomedical search-term expansion |

**Reference files**

```text
skills/nature-academic-search/
├── README.md
├── SKILL.md
├── manifest.yaml
├── static/
├── install.sh
├── config/
│   ├── mcp-snippet.json
│   ├── settings-snippet.json
│   └── triggers-academic-search.toml
├── mcp-server/
│   ├── academic_search_server.py
│   ├── sources/
│   ├── tests/
│   └── utils/
├── references/
│   ├── citation-parser.md
│   ├── dedup-engine.md
│   ├── ris-bibtex-format.md
│   ├── search-strategy.md
│   ├── source-tiers.md
│   └── workflows/
└── scripts/
    ├── converters.py
    ├── format-converter.py
    └── preflight.py
```

**Example workflow** — Search the same topic across PubMed, CrossRef and arXiv, merge
and deduplicate candidate papers, verify key identifiers, look up MeSH terms for the
biomedical subset, then export or convert the selected references for Zotero, EndNote
or BibTeX.

---

## Shared design principles

All skills in this collection adhere to the following:

1. **Primary sources only** — rules are grounded in published *Nature* content or official
   journal guidelines, not general style preference.
2. **Explicit over implicit** — every rule is stated with a rationale, not just asserted.
3. **Section-aware** — academic writing and figures both require context-sensitivity;
   each skill applies different logic depending on which part of a paper is being handled.
4. **Output-first** — every skill returns something immediately usable: copy-paste prose,
   a `.svg` file, a `.pptx` deck, or a concrete recommendation. No intermediate planning documents.
5. **Extensible by design** — each skill is self-contained in its own directory; adding a
   new skill requires no changes to existing ones.

---

## Adding a new skill

To add a skill to this collection:

**1. Create a directory**
```
skills/nature-<topic>/
```

**2. Minimum required files**

| File | Required | Purpose |
|------|----------|---------|
| `SKILL.md` | Yes | Frontmatter (`name`, `description`) + rules + workflow; loaded by the agent after triggering |
| `README.md` | Yes | Human-readable reference in full English |
| `references/*.md` | Recommended for complex skills | Modular rule files (api, design theory, tutorials, chart types, …) |

**3. SKILL.md frontmatter template**
```yaml
---
name: nature-<topic>
description: >-
  One-sentence description of what the skill does and when to trigger it.
  Include the output format and the primary use case.
---
```

**4. Update this index**

Add a row to the [Skill index](#skill-index) table above:
```markdown
| [`nature-<topic>`](skills/nature-<topic>/README.md) | Draft / Stable | One-line purpose | trigger keywords |
```

**5. Status labels**

| Label | Meaning |
|-------|---------|
| `Draft` | Rules defined; not yet tested on real examples |
| `Beta` | Tested on examples; edge cases may remain |
| `Stable` | Validated on real academic content; rules are settled |

---

## Candidate skills (not yet built)

The following are documented gaps. Contributions welcome.

| Candidate | Scope | Priority |
|-----------|-------|----------|
| `nature-stats` | Statistical reporting conventions for *Nature* (effect sizes, confidence intervals, p-value formatting, sample size statements) | High |
| `nature-methods` | Deep-dive Methods writing assistant — reproducibility checklist, forbidden phrases, ethical approval templates, supplementary organisation | Medium |
| `nature-cover` | Cover letter drafting — hook paragraph, significance framing, fit-to-journal argument, ≤ 500-word limit | Medium |


## ☕ 如果内容对你有帮助，欢迎随缘支持一下

---

<div align="center">

| 微信赞赏 | 来自粉丝的小感动 |
| --- | --- |
| <img width="320" alt="微信赞赏" src="https://github.com/user-attachments/assets/83c101e7-2370-46e9-a840-cb506df98cf4" /> | <img width="320" alt="粉丝的鼓励" src="https://github.com/user-attachments/assets/0484300a-95e8-4cb3-ad73-478ba9bd19d6" /> |

</div>

### 💬 想说的话
 
项目会长期免费维护，大家正常使用就好。  
很多朋友还是学生党，所以完全不需要有任何“必须打赏”的压力。

如果这些内容刚好帮你节省了一些时间、解决了一点问题，  
又恰好想请作者喝杯咖啡，那我会非常开心 ☕  

你的支持会用于：

- 持续更新内容
- 服务器与工具费用
- 熬夜写文档时的续命奶茶（认真）

无论是否赞赏，都非常感谢你的关注与支持 ❤️
