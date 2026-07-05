<h1 align="center">Nature Skills</h1>

<p align="center">
  Reusable Codex skills for AI scholars worldwide
</p>

<p align="center">
  <strong>English</strong> · <a href="README.md">中文</a>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-2ea44f"></a>
  <img alt="Language" src="https://img.shields.io/badge/language-English%20%7C%20中文-1f6feb">
  <img alt="Skills" src="https://img.shields.io/badge/skills-16%20research%20skills-0ea5e9">
  <img alt="Codex" src="https://img.shields.io/badge/Codex-ready-111827">
</p>

<p align="center">
  <a href="#installation">Install</a> ·
  <a href="#skill-index">Skill Index</a> ·
  <a href="#shared-design-principles">Design Principles</a> ·
  <a href="#adding-a-skill">Contributing</a> ·
  <a href="README.md">中文</a>
</p>

- Hello everyone, I am Yizhe Yuan, the founder of `nature-skills`. Thank you for
  following this project. We have published many video tutorials on Douyin; you
  can search by topic name to find them, and I sincerely hope they help you.
- If you have a concrete need, please open an issue. If we think the request is
  meaningful and feasible, we will try to move it forward. Pull requests are also
  welcome; please follow the contribution format later in this document so that
  reviews and merges can be handled efficiently.
- `nature-skills` collects general-purpose research skills for AI scholars
  worldwide. It is an early form of a "skill journal": the goal is not empty
  storytelling, but solving real domain problems.
- Knowledge Planet: `Nature Skills` and the philosophy behind it.

## Main Contributors

- **Yizhe Yuan**: founder of `nature-skills`.
- **Xin-Rui Ma**: second contributor, PhD student at the School of Civil
  Engineering, Southeast University, focusing on deep learning and agent-assisted
  research for structural design.
  - GitHub: [Travisma2233](https://github.com/Travisma2233)
  - Email: [travisma2233@gmail.com](mailto:travisma2233@gmail.com)
  - Google Scholar: [Xin-Rui Ma](https://scholar.google.com/citations?user=CDydADoAAAAJ&hl=en)
  - ResearchGate: [Xin-Rui Ma](https://www.researchgate.net/profile/Xin-Rui-Ma?ev=hdr_xprf)

# Some Personal Views

- Recently, I noticed that the Nature Skills design has drawn attention from
  Google DeepMind and has been referenced by them. They drew on its citation
  system, script ideas, and skill-design philosophy to launch Science Skills. To
  be honest, this makes me pleased: when leading international AI institutions
  begin to draw inspiration from our work, it means original ideas from Chinese
  developers are being seen by the world. This is not a feeling of loss from
  being copied, but a sign of Chinese strength taking root in open source and
  naturally growing outward.
- The focus of our skill design has never been to require every user to fully
  master the whole philosophy. The point is that the philosophy itself can be
  understood and reused by machines. If you want to create a new skill or adapt
  this system to your own field, you can give the Nature Skills GitHub repository
  to Codex and let it learn the design pattern, then help you create or modify a
  skill. This is how ideas become operational rather than remaining oral
  explanations.
- The real value of Nature Skills may not be limited to any individual module.
  It may be that the project has quietly opened a new door: many people realize
  for the first time that Codex or other agents can operate a local computer for
  research. I have been fortunate to witness and accompany many people through
  this shift in research workflow. When they say, "so research can be done this
  way," that break in understanding and liberation of thought matters more to me
  than the skills themselves. This is not merely the success of a tool, but the
  beginning of a new way of thinking spreading among people.
- In practice, almost every useful tool can be distilled into a standardized
  process, and standardized processes can be packaged as reusable skills.

<table>
  <tr>
    <td align="center">
      <b>Follow Douyin for video tutorials</b><br>
      <img width="300" alt="Douyin tutorials" src="https://github.com/user-attachments/assets/37d4b0b6-3d22-4492-bb01-c0d9bae5a9e0" />
    </td>
    <td align="center">
      <b>Knowledge Planet 50 CNY/year</b><br>
      <img width="300" alt="Knowledge Planet" src="https://github.com/user-attachments/assets/7a7e467a-59d4-4514-9b42-eefd01bf9591" />
    </td>
    <td align="center">
      <b>Agent Research Community</b><br>
      <img width="300" alt="Agent Research Community" src="https://github.com/user-attachments/assets/28d1886a-69be-46bc-a1cb-777d7510ddab" />
    </td>
  </tr>
</table>

---

## Installation

`nature-skills` is a collection of reusable skill packages organized around
`SKILL.md`. Each top-level skill directory under `skills/` is an installable unit,
such as `nature-*`; `skills/_shared/` contains shared content and should also be
kept when installing the complete repository.

### Recommended Codex Installation

Use the repository script to install or update Codex skills. It syncs every
top-level skill directory under `skills/` and verifies the copied contents with
`diff`. It does not overwrite unrelated Codex skills.

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
scripts/update-codex-skills.sh --pull
```

If you already have a clone:

```bash
cd nature-skills
scripts/update-codex-skills.sh --pull
```

Verify that the current Codex installation matches this checkout:

```bash
scripts/update-codex-skills.sh --check
```

If you use this script for long-term updates and want to remove directories that
were previously managed by this installer but no longer exist upstream:

```bash
scripts/update-codex-skills.sh --pull --prune
```

`--prune` only removes directories recorded by this installer. It will not guess
or delete unrelated skills.

You can also ask Codex to install the repository for you:

```text
Install Codex skills from this repository:
https://github.com/Yuan1z0825/nature-skills.git

Clone the repository, run scripts/update-codex-skills.sh --pull, and then run
scripts/update-codex-skills.sh --check to verify the installation. Keep complete
skill directories under skills/; do not copy only SKILL.md.
```

To install only one skill, specify the skill name:

```text
Install only nature-reader from this repository:
https://github.com/Yuan1z0825/nature-skills.git

If the skill needs shared files, install skills/_shared as well.
```

Key rule: keep the full directory structure. Many skills depend on
`references/`, `static/`, `manifest.yaml`, scripts, assets, or shared files.

### Manual Installation

Manual copy is not recommended. If you do not want to run the script, copy every
top-level directory under `skills/`:

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
mkdir -p ~/.codex/skills
for d in skills/*/; do
  name="${d%/}"
  name="${name##*/}"
  rsync -a --delete "$d" "$HOME/.codex/skills/$name/"
done
```

The installer does not install Python dependencies automatically. Install them
only when you need the corresponding scripts or MCP services:

```bash
python -m pip install -r skills/nature-paper-to-patent/requirements.txt
python -m pip install -r skills/nature-academic-search/mcp-server/requirements.txt
```

`nature-academic-search` also requires `PUBMED_EMAIL`. Optional Scopus,
ScienceDirect, and other provider credentials should be configured locally and
must not be committed to the repository.

After installation, start a new Codex session and describe your task naturally,
for example:

```text
Turn this paper into a full Chinese-English side-by-side Markdown reader.
```

```text
Create a Chinese PPT deck from this paper.
```

### Directory Layout

```text
skills/
├── _shared/              # keep this when skills reference ../_shared
├── nature-<topic>/
│   ├── README.md
│   ├── SKILL.md
│   ├── manifest.yaml     # present in router-style skills
│   ├── static/           # present in router-style skills
│   └── references/...
└── nature-proposal-writer/
    ├── README.md
    ├── SKILL.md
    ├── scripts/...
    ├── templates/...
    └── references/...
```

### Non-Codex Scenarios

For Claude Code or other agents, keep a stable repository clone and create a
lightweight subagent, slash command, or custom prompt wrapper that points to the
real `skills/*/SKILL.md` files. Preserve `skills/_shared/`.

For manual or non-Codex use:

1. Copy complete skill directories into your prompt library or project.
2. Preserve `SKILL.md`, `manifest.yaml`, `static/`, `references/`, scripts,
   assets, and required `skills/_shared/` files.
3. If the target agent has its own format requirements, adjust the frontmatter
   and body structure.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Yuan1z0825/nature-skills&type=Date&cache_bust=2026-06-07T16)](https://star-history.com/#Yuan1z0825/nature-skills&Date)

## Skill Index

The current `skills/` directory contains the following triggerable skills.
`skills/_shared/` is shared content and is not counted in the skill index.

| Skill | Status | Purpose | Example Triggers |
|---|---|---|---|
| [`nature-figure`](skills/nature-figure/README.md) | Stable | Submission-grade Python or R scientific figure workflow for Nature / high-impact journals, with a figures4papers-style demo | "Nature figure", "submission-grade figure", "publication plot", "scientific figure", "figures4papers" |
| [`nature-polishing`](skills/nature-polishing/README.md) | Stable | Polish, restructure, or translate academic prose into Nature-style English | "Nature style", "polishing", "academic writing", "English manuscript" |
| [`nature-writing`](skills/nature-writing/README.md) | Draft | Draft Nature-style manuscript sections and rebuild a paper argument | "Nature writing", "write an abstract", "write introduction", "manuscript draft", "paper writing" |
| [`nature-reviewer`](skills/nature-reviewer/README.md) | Draft | Simulate Nature-style reviewer assessment from the reviewer perspective, returning three reviewer reports and a synthesis | "Nature reviewer", "pre-submission review", "reviewer report", "reviewer-perspective assessment" |
| [`nature-citation`](skills/nature-citation/README.md) | Beta | Search support literature strictly within Nature / CNS families and export ENW, RIS, or Zotero RDF | "Nature citation", "CNS citation", "segmented citation", "supporting references", "Zotero RDF" |
| [`nature-data`](skills/nature-data/README.md) | Draft | Prepare Data Availability statements, data repository plans, and FAIR checks | "Data Availability", "data availability", "repository", "FAIR metadata" |
| [`nature-reader`](skills/nature-reader/README.md) | Beta | Generate full-paper Markdown readers with source anchors, figure-text alignment, and Chinese-English side-by-side translation | "nature reader", "full Markdown", "source-aligned text", "figure-text alignment", "full translation" |
| [`nature-response`](skills/nature-response/README.md) | Beta | Parse revision emails; draft, audit, and revise revision cover letters, point-by-point response letters, red-marked manuscripts, and LaTeX templates | "response to reviewers", "rebuttal letter", "cover letter", "major revision", "revision email", "reviewer-comment response", "LaTeX template" |
| [`nature-paper2ppt`](skills/nature-paper2ppt/README.md) | Beta | Generate Chinese PPTX journal-club or paper-presentation decks from research papers | "paper PPT", "journal club", "paper to slides", "paper presentation" |
| [`nature-paper-to-patent`](skills/nature-paper-to-patent/README.md) | Beta | Generate evidence-constrained Chinese invention patent drafts from papers, technical reports, or project materials | "paper to patent", "Chinese patent", "paper-to-patent", "claims drafting" |
| [`nature-academic-search`](skills/nature-academic-search/README.md) | Beta | Multi-source literature search, citation verification, strict other-citation audits, article-level citation metric tables, influential citer profiling, and reference management | "search papers", "find articles", "literature search", "literature lookup", "verify DOI", "strict other citation", "article citation table", "influential citer" |
| [`nature-downloader`](skills/nature-downloader/README.md) | Beta | Legally obtain academic full text/PDFs through library access, Chrome login state, and open-access routes | "download papers", "library paper download", "CARSI", "Web of Science", "PDF download" |
| [`nature-literature-pipeline`](skills/nature-literature-pipeline/README.md) | Stable | Automated literature discovery pipeline: multi-source retrieval, six-axis scoring, deep-reading delivery, and local archiving | "literature pipeline", "daily literature", "literature push", "daily literature push", "cron" |
| [`nature-experiment-log`](skills/nature-experiment-log/README.md) | Draft | Standardize experiment images, voice, and text into Obsidian experiment logs with YAML frontmatter and archived source materials | "experiment log", "record experiment", "Obsidian vault", "Feishu research group" |
| [`nature-proposal-writer`](skills/nature-proposal-writer/README.md) | Beta | Proposal-first research writing state machine: establish evidence, argument, and section contracts before drafting or reviewing text | "researchwrite", "proposal", "opening report", "research plan", "research writing QA" |

---

## Shared Design Principles

1. **Prefer primary sources**: rules should be grounded in published Nature
   content, official journal guidance, or explicit local sources rather than
   generic taste.
2. **Make rules explicit**: explain the reason behind each rule instead of
   giving unsupported assertions.
3. **Respect section and task context**: writing, figures, citations, and
   responses depend on the manuscript section and task.
4. **Output first**: every skill should produce something directly usable, such
   as paste-ready text, `.svg`, `.pptx`, `.docx`, or concrete instructions.
5. **Keep skills extensible**: each skill should be self-contained, and adding a
   new skill should not require modifying existing skills.

---

## Adding a Skill

When adding a skill to this repository, follow this process.

### 1. Create Directory

```text
skills/nature-<topic>/
```

### 2. Minimum Files

| File | Required | Purpose |
|---|---:|---|
| `SKILL.md` | Yes | Frontmatter (`name`, `description`) plus rules and workflow loaded by the agent |
| `README.md` | Yes | Human-facing Chinese documentation |
| `references/*.md` | Recommended for complex skills | Modular rule files, API references, design theory, tutorials, chart types, and similar material |

### 3. `SKILL.md` Frontmatter Template

```yaml
---
name: nature-<topic>
description: >-
  One sentence explaining what the skill does, when it should trigger, primary
  outputs, and core use cases.
---
```

### 4. Update Skill Index

After adding a skill, update the [Skill Index](#skill-index) table:

```markdown
| [`nature-<topic>`](skills/nature-<topic>/README.md) | Draft / Stable | One-sentence purpose | Trigger terms |
```

### 5. Status Labels

| Status | Meaning |
|---|---|
| `Draft` | Rules are defined but not yet tested on real cases |
| `Beta` | Tested on examples, with possible edge-case issues |
| `Stable` | Validated on real academic content and relatively stable |

---
