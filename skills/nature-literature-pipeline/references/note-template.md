# Literature Note Template (v2 — 2026-06-03)

## Contents

- [Standardized Frontmatter](#standardized-frontmatter)
- [Body Structure (6 sections)](#body-structure-6-sections)
- [核心主张](#核心主张)
- [方法](#方法)
- [关键发现](#关键发现)
- [批判](#批判)
- [Connection to Research](#connection-to-research)
- [下一步](#下一步)
- [File Naming Convention](#file-naming-convention)
- [Directory Discipline](#directory-discipline)
- [Bulk Standardization](#bulk-standardization)


> Standardized template for literature notes. Use for all new vault literature notes.
> Replaces the v1 template (date/建议分类/是否值得全文精读 format).

## Standardized Frontmatter

```yaml
---
title: "Original English Title"
authors: "Last1, F.; Last2, F."
year: 2024
journal: "Full Journal Name"
doi: "10.xxxx/..."
classification: "A_核心主线"
tags: [中文关键词1, 关键词2, 关键词3]
date_read: 2026-06-03
---
```

### Field Rules

| Field | Format | Example |
|-------|--------|---------|
| `title` | Original English, double-quoted | `"Corrosion of Alloys and Metals by Molten Nitrates"` |
| `authors` | `Last, F.; Last, F.` — comma+semicolon separated, >3 use `et al.` | `"Smith, J.A.; Jones, R.B."` |
| `year` | 4-digit integer, no quotes | `2004` |
| `journal` | Full name or report ID, double-quoted | `"Journal of Materials Engineering and Performance"` |
| `doi` | Full DOI string starting with `10.` | `"10.1016/j.solmat.2019.02.012"` |
| `classification` | **Must be full Chinese name** — one of: `A_核心主线`, `B_章节支撑`, `C_工程背景`, `D_方法借鉴`, `E_暂存低优先` | `"A_核心主线"` |
| `tags` | YAML list, 3-5 specific Chinese keywords | `[硝酸盐, 腐蚀, 氧离子, 综述]` |
| `date_read` | ISO date of first detailed reading | `2026-06-03` |

**Anti-patterns (do NOT use)**: `date` (use `year`), `建议分类` (use `classification`), `是否值得全文精读` (covered by classification), `source_urls` (extraneous), `note_date` (use `date_read`).

## Body Structure (6 sections)

```markdown
## 核心主张
[1-3 sentences. Mark evidence strength: 成熟共识 / 学界共识 / 争议 / 推测]

## 方法
[Key methods, advantages, limitations]

## 关键发现
[Bullet points of key data/findings/quantitative results]

## 批判
[Strengths, weaknesses, relevance gaps, evidence reliability]

## Connection to Research
[How this connects to the user's thesis: NO2-/NO3- ratio, CV fingerprint, atmosphere control, Hitec purification, material selection, experimental design]

## 下一步
[Actionable: cite in which chapter, follow up which reference, design which experiment, what to verify]
```

**Note**: No `# Heading` title line before the sections — the frontmatter `title` field serves that role. Avoid duplicate H1 headers.

## File Naming Convention

Format: `{FirstAuthorLast}{Year}_{中文核心关键词}.md`

- **First author**: last name only, title-cased. For hyphenated names preserve the hyphen (e.g., `Encinas-Sánchez`).
- **Year**: 4 digits, no space after author name.
- **Keywords**: 2-4 Chinese words connected by underscores, derived from the paper's core contribution (not generic like `文献`).

### Examples

| Good | Bad |
|------|-----|
| `Goods2004_商业硝酸盐_304_316_长期腐蚀.md` | `goodscorrosionofstainlesssteelscarbon2004.md` |
| `Author2018_topic_method.md` | `authortopicmethodology2018.md` |
| `Kruizenga2011_316SS失效分析_氧覆盖.md` | `kruizengastainlesssteelcorrosion2011.md` |
| `Author2025_topic_application.md` | `author2025topicengineeringapplication.md` |

## Directory Discipline

Subagents frequently create short directory names (`A/笔记/`, `B/笔记/`). Always verify and correct to full names:

- `A_核心主线/笔记/`
- `B_章节支撑/笔记/`
- `C_工程背景/笔记/`
- `D_方法借鉴/笔记/`
- `E_暂存低优先/笔记/`

## Bulk Standardization

When standardizing a batch of existing notes, the Python script pattern is:

1. Inventory all `.md` files across A-E directories
2. Parse existing frontmatter → extract known fields
3. Infer missing fields from body content (year regex, author regex, title from H1)
4. Generate standardized frontmatter + remove body H1 duplicates
5. Generate new filename from `AuthorYear + Chinese keywords`
6. Write to same directory, rename + collision-check
7. Save rename mapping CSV for rollback

Key extraction patterns:
- Year: `(19|20)\d{2}` in filename or frontmatter
- Authors: `\*\*([^*]+?)\s*\((\d{4})\)\*\*` in body for old-format notes
- Title: frontmatter `title` field or body `# Heading`
- Classification: normalize `A`/`B`/`C`/`D` → full Chinese names, default to directory name
- Tags: keyword pattern matching on title + body[:1000] against a Chinese tech-term map
