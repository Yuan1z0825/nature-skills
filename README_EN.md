<div align="center">
  <p>
    <img src="assets/readme-banner-en.png" alt="Nature Skills: Reusable Research Skills for AI Scholars" width="100%">
  </p>
  <p>
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-2ea44f"></a>
    <a href="#installation"><img alt="Install" src="https://img.shields.io/badge/install-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20OpenCode%20%7C%20Hermes-111827"></a>
    <a href="#skill-index"><img alt="Skills" src="https://img.shields.io/badge/skills-17-0ea5e9"></a>
    <a href="README.md"><img alt="Language" src="https://img.shields.io/badge/language-English%20%7C%20中文-1f6feb"></a>
  </p>
  <p>
    <a href="#installation">Install</a>
    · <a href="#quick-start">Quick Start</a>
    · <a href="#skill-index">Skill Index</a>
    · <a href="docs/open-source-agent-frameworks_EN.md">Other Install</a>
    · <a href="#shared-design-principles">Design Principles</a>
    · <a href="#adding-a-skill">Contributing</a>
    · <a href="README.md">中文</a>
  </p>
</div>

---

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

## Quick Start

After installation, you can give the agent a paper, paragraph, reviewer letter,
or task description directly. These prompts are ready to copy:

| Goal | Prompt |
| --- | --- |
| Read a paper / bilingual reader | `Turn this PDF into a figure-aware Chinese-English Markdown reader.` |
| Generate a paper presentation | `Create a Chinese journal-club PPT from this paper, keeping key figures and source labels.` |
| Polish or translate a manuscript paragraph | `Rewrite this Chinese paragraph into Nature-style academic English without changing the meaning.` |
| Draft an abstract, introduction, or discussion | `Using these results and figures, draft a Nature-style abstract and introduction.` |
| Simulate pre-submission review | `Evaluate this manuscript from a Nature reviewer perspective and produce three reviewer reports.` |
| Respond to reviewer comments | `Use this revision email to draft point-by-point replies, a cover letter, and redline locations for the revised manuscript.` |
| Search literature, strict citations, and citer profiles | `Create a table with this paper's citation count, strict external citation count, DOI, and whether major scholars or Fellows cited it.` |
| Create scientific figures or schematics | `Use this method and result description to draft a publication-ready scientific figure or manuscript schematic.` |

If you are unsure which skill to use, describe the task naturally. If you already
know the skill name, explicitly say "use `nature-reader`" or "use
`nature-response`" in the prompt.

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

### Claude Code Installation

Claude Code cannot use `scripts/update-codex-skills.sh` directly because that
script only syncs skills into Codex's `~/.codex/skills/`. For Claude Code, keep a
stable local clone and create a subagent or slash command wrapper that points to
the real `skills/*/SKILL.md`. This preserves the skill directory structure and
lets the workflow keep using `references/`, `static/`, `manifest.yaml`, scripts,
assets, and `skills/_shared/`.

If Claude Code is not installed yet:

```bash
npm install -g @anthropic-ai/claude-code
claude
```

Clone the repository to a stable path:

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

Recommended method: create a Claude Code subagent wrapper for the skills you use
often. Example for `nature-reader`:

```bash
mkdir -p ~/.claude/agents
cat > ~/.claude/agents/nature-reader.md <<'EOF'
---
name: nature-reader
description: Use for Chinese-English paper reading, figure-aware translation, and source-grounded paper notes.
---

When invoked, first read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md` and follow it as the governing workflow.
Read supporting files from `~/ai-skills/nature-skills/skills/nature-reader/` and `~/ai-skills/nature-skills/skills/_shared/` only when needed.
Do not replace this skill with a generic paper-reading response.
EOF
```

Then start a new Claude Code session and ask for the subagent explicitly:

```text
Use the nature-reader subagent to turn this paper into a Chinese-English Markdown reader.
```

If you prefer a slash command, create a command wrapper instead:

```bash
mkdir -p ~/.claude/commands
cat > ~/.claude/commands/nature-reader.md <<'EOF'
Read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md` first and follow it strictly.
Read directly needed supporting files from `~/ai-skills/nature-skills/skills/nature-reader/` and `~/ai-skills/nature-skills/skills/_shared/`.

$ARGUMENTS
EOF
```

Use it inside Claude Code:

```text
/nature-reader Turn this paper into a full Chinese-English side-by-side Markdown reader.
```

To install other skills, replace `nature-reader` with the target directory name,
such as `nature-polishing`, `nature-writing`, `nature-reviewer`,
`nature-response`, or `nature-figure`. To update later:

```bash
cd ~/ai-skills/nature-skills
git pull
```

As long as the wrapper still points to this stable clone path, no repeated file
copy is needed.

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

For OpenClaw, OpenCode, Hermes, and other open-source agent frameworks, see the [OpenClaw / OpenCode / Hermes integration guide](docs/open-source-agent-frameworks_EN.md).

### Directory Layout

```text
skills/
├── _shared/              # keep this when skills reference ../_shared
├── nature-<topic>/
│   ├── README.md
│   ├── README_EN.md
│   ├── SKILL.md
│   ├── manifest.yaml     # present in router-style skills
│   ├── static/           # present in router-style skills
│   └── references/...
└── nature-proposal-writer/
    ├── README.md
    ├── README_EN.md
    ├── SKILL.md
    ├── scripts/...
    ├── templates/...
    └── references/...
```

### Other Agent Scenarios

For OpenClaw, OpenCode, and Hermes, see the dedicated [integration guide](docs/open-source-agent-frameworks_EN.md).

For other agents, keep a stable repository clone and create a lightweight
subagent, slash command, or custom prompt wrapper that points to the real
`skills/*/SKILL.md` files. Preserve `skills/_shared/`.

For manual or other-agent use:

1. Copy complete skill directories into your prompt library or project.
2. Preserve `SKILL.md`, `manifest.yaml`, `static/`, `references/`, scripts,
   assets, and required `skills/_shared/` files.
3. If the target agent has its own format requirements, adjust the frontmatter
   and body structure.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Yuan1z0825/nature-skills&type=Date&cache_bust=2026-06-07T16)](https://star-history.com/#Yuan1z0825/nature-skills&Date)

## Skill Index

The current `skills/` directory contains the following triggerable skills.
`skills/_shared/` is shared content and is not counted in the skill index. Click a skill name or the "Details" link to open its dedicated documentation page.

| Skill | Status | Purpose | Example Triggers | Details |
|---|---|---|---|---|
| [`nature-figure`](skills/nature-figure/README_EN.md) | Stable | Submission-grade Python or R scientific figure workflow for Nature / high-impact journals, with a figures4papers-style demo and OpenRouter GPT Image 2 schematic-draft generation | "Nature figure", "submission-grade figure", "publication plot", "scientific figure", "figures4papers", "paper schematic", "GPT Image 2" | [Details](skills/nature-figure/README_EN.md) |
| [`nature-polishing`](skills/nature-polishing/README_EN.md) | Stable | Polish, restructure, or translate academic prose into Nature-style English | "Nature style", "polishing", "academic writing", "English manuscript" | [Details](skills/nature-polishing/README_EN.md) |
| [`nature-writing`](skills/nature-writing/README_EN.md) | Draft | Draft Nature-style manuscript sections and rebuild a paper argument | "Nature writing", "write an abstract", "write introduction", "manuscript draft", "paper writing" | [Details](skills/nature-writing/README_EN.md) |
| [`nature-reviewer`](skills/nature-reviewer/README_EN.md) | Draft | Simulate Nature-style reviewer assessment from the reviewer perspective, returning three reviewer reports and a synthesis | "Nature reviewer", "pre-submission review", "reviewer report", "reviewer-perspective assessment" | [Details](skills/nature-reviewer/README_EN.md) |
| [`nature-citation`](skills/nature-citation/README_EN.md) | Beta | Search support literature strictly within Nature / CNS families and export ENW, RIS, or Zotero RDF | "Nature citation", "CNS citation", "segmented citation", "supporting references", "Zotero RDF" | [Details](skills/nature-citation/README_EN.md) |
| [`nature-data`](skills/nature-data/README_EN.md) | Draft | Prepare Data Availability statements, data repository plans, and FAIR checks | "Data Availability", "data availability", "repository", "FAIR metadata" | [Details](skills/nature-data/README_EN.md) |
| [`nature-statistics`](skills/nature-statistics/README_EN.md) | Draft | Audit, revise, or draft statistical reporting for Nature / high-impact journal manuscripts, covering sample size, independent units, replicates, p values, multiple comparisons, effect sizes, confidence intervals, figure statistics, and reviewer comments | "Nature statistics", "statistical analysis", "p value", "sample size", "replicates", "multiple comparisons", "figure statistics", "statistics review" | [Details](skills/nature-statistics/README_EN.md) |
| [`nature-reader`](skills/nature-reader/README_EN.md) | Beta | Generate full-paper Markdown readers with source anchors, figure-text alignment, and Chinese-English side-by-side translation | "nature reader", "full Markdown", "source-aligned text", "figure-text alignment", "full translation" | [Details](skills/nature-reader/README_EN.md) |
| [`nature-response`](skills/nature-response/README_EN.md) | Beta | Parse revision emails; draft, audit, and revise revision cover letters, point-by-point response letters, red-marked manuscripts, and LaTeX templates | "response to reviewers", "rebuttal letter", "cover letter", "major revision", "revision email", "reviewer-comment response", "LaTeX template" | [Details](skills/nature-response/README_EN.md) |
| [`nature-paper2ppt`](skills/nature-paper2ppt/README_EN.md) | Beta | Generate Chinese PPTX journal-club or paper-presentation decks from research papers | "paper PPT", "journal club", "paper to slides", "paper presentation" | [Details](skills/nature-paper2ppt/README_EN.md) |
| [`nature-paper-to-patent`](skills/nature-paper-to-patent/README_EN.md) | Beta | Generate evidence-constrained Chinese invention patent drafts from papers, technical reports, or project materials | "paper to patent", "Chinese patent", "paper-to-patent", "claims drafting" | [Details](skills/nature-paper-to-patent/README_EN.md) |
| [`nature-ref-verifier`](skills/nature-ref-verifier/README_EN.md) | Beta | Cross-check references across multiple sources and flag author, title, year, volume, issue, and page inconsistencies | "verify refs", "check references", "reference verification", "ref check" | [Details](skills/nature-ref-verifier/README_EN.md) |
| [`nature-academic-search`](skills/nature-academic-search/README_EN.md) | Beta | Multi-source literature search, citation verification, strict other-citation audits, article-level citation metric tables, influential citer profiling, and reference management | "search papers", "find articles", "literature search", "literature lookup", "verify DOI", "strict other citation", "article citation table", "influential citer" | [Details](skills/nature-academic-search/README_EN.md) |
| [`nature-downloader`](skills/nature-downloader/README_EN.md) | Beta | Legally obtain academic full text/PDFs through library access, Chrome login state, and open-access routes | "download papers", "library paper download", "CARSI", "Web of Science", "PDF download" | [Details](skills/nature-downloader/README_EN.md) |
| [`nature-literature-pipeline`](skills/nature-literature-pipeline/README_EN.md) | Stable | Automated literature discovery pipeline: multi-source retrieval, six-axis scoring, deep-reading delivery, and local archiving | "literature pipeline", "daily literature", "literature push", "daily literature push", "cron" | [Details](skills/nature-literature-pipeline/README_EN.md) |
| [`nature-experiment-log`](skills/nature-experiment-log/README_EN.md) | Draft | Standardize experiment images, voice, and text into Obsidian experiment logs with YAML frontmatter and archived source materials | "experiment log", "record experiment", "Obsidian vault", "Feishu research group" | [Details](skills/nature-experiment-log/README_EN.md) |
| [`nature-proposal-writer`](skills/nature-proposal-writer/README_EN.md) | Beta | Proposal-first research writing state machine: establish evidence, argument, and section contracts before drafting or reviewing text | "researchwrite", "proposal", "opening report", "research plan", "research writing QA" | [Details](skills/nature-proposal-writer/README_EN.md) |

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
| `README_EN.md` | Yes | English documentation paired with the Chinese details page |
| `references/*.md` | Recommended for complex skills | Modular rule files, API references, design theory, tutorials, chart types, and similar material |

Each `README.md` / `README_EN.md` should use a consistent information structure so users can open a details page and quickly decide whether the skill fits:

```markdown
# nature-<topic>

## What It Does
## When to Use It
## Copy-Paste Prompts
## Required Inputs
## Expected Outputs
## Dependencies / API Keys / Local Environment
## FAQ
## Related Skills
```

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
| [`nature-<topic>`](skills/nature-<topic>/README_EN.md) | Draft / Stable | One-sentence purpose | Trigger terms | [Details](skills/nature-<topic>/README_EN.md) |
```

### 5. Status Labels

| Status | Meaning |
|---|---|
| `Draft` | Rules are defined but not yet tested on real cases |
| `Beta` | Tested on examples, with possible edge-case issues |
| `Stable` | Validated on real academic content and relatively stable |

---
