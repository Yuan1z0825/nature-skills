# OpenClaw / OpenCode / Hermes Integration Guide

The core unit in `nature-skills` is a complete skill directory, not a standalone `SKILL.md` file. For open-source agent frameworks such as OpenClaw, OpenCode, and Hermes, keep a stable local clone of this repository and let the target framework scan or reference complete directories under `skills/`.

## Common Setup

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

To update later:

```bash
cd ~/ai-skills/nature-skills
git pull
```

Rules:

1. Keep the complete skill directory, such as `skills/nature-reader/`; do not copy only `SKILL.md`.
2. Keep sibling shared content in `skills/nature-shared/` when a skill references it.
3. Skills that use scripts, MCP services, or APIs still require their own dependencies, environment variables, and local credentials.

## OpenClaw

OpenClaw workspace skills usually live at:

```text
~/.openclaw/workspace/skills/<skill>/SKILL.md
```

Use symlinks to point OpenClaw at the stable clone:

```bash
mkdir -p ~/.openclaw/workspace/skills
ln -s ~/ai-skills/nature-skills/skills/nature-reader ~/.openclaw/workspace/skills/nature-reader
ln -s ~/ai-skills/nature-skills/skills/nature-shared ~/.openclaw/workspace/skills/nature-shared
```

Add more skills by linking more `nature-*` directories:

```bash
ln -s ~/ai-skills/nature-skills/skills/nature-polishing ~/.openclaw/workspace/skills/nature-polishing
ln -s ~/ai-skills/nature-skills/skills/nature-writing ~/.openclaw/workspace/skills/nature-writing
```

If symlinks are inconvenient, copy the full directories instead:

```bash
cp -R ~/ai-skills/nature-skills/skills/nature-reader ~/.openclaw/workspace/skills/
cp -R ~/ai-skills/nature-skills/skills/nature-shared ~/.openclaw/workspace/skills/
```

When using copy-based installation, copy the directories again after repository updates.

## OpenCode

OpenCode can discover skills from project or global `.agents/skills/**/SKILL.md` directories. For global use:

```bash
mkdir -p ~/.agents/skills
ln -s ~/ai-skills/nature-skills/skills/nature-reader ~/.agents/skills/nature-reader
ln -s ~/ai-skills/nature-skills/skills/nature-polishing ~/.agents/skills/nature-polishing
ln -s ~/ai-skills/nature-skills/skills/nature-shared ~/.agents/skills/nature-shared
```

For a single project, place the links under that project's `.agents/skills/`:

```bash
cd /path/to/your/project
mkdir -p .agents/skills
ln -s ~/ai-skills/nature-skills/skills/nature-reader .agents/skills/nature-reader
ln -s ~/ai-skills/nature-skills/skills/nature-shared .agents/skills/nature-shared
```

Newer OpenCode configs can also declare an additional skills path in `opencode.json` or `opencode.jsonc`:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["~/ai-skills/nature-skills/skills"]
}
```

Older OpenCode versions may still use this shape:

```json
{
  "skills": {
    "paths": ["~/ai-skills/nature-skills/skills"]
  }
}
```

After starting OpenCode, ask it to use a skill explicitly:

```text
Use the nature-reader skill to turn this paper into a Chinese-English Markdown reader.
```

## Hermes

Hermes stores local skills under:

```text
~/.hermes/skills/
```

The recommended approach is to add the `nature-skills` `skills/` directory as an external skill directory in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - ~/ai-skills/nature-skills/skills
```

Hermes can then discover skills such as `nature-reader`, `nature-polishing`, and `nature-writing`, and use them as slash commands:

```text
/nature-reader Turn this paper into a Chinese-English Markdown reader.
```

If you do not want Hermes to scan the external repository directly, copy selected skills into Hermes' own directory:

```bash
mkdir -p ~/.hermes/skills/research
cp -R ~/ai-skills/nature-skills/skills/nature-reader ~/.hermes/skills/research/
cp -R ~/ai-skills/nature-skills/skills/nature-polishing ~/.hermes/skills/research/
cp -R ~/ai-skills/nature-skills/skills/nature-shared ~/.hermes/skills/research/nature-shared
```

Note that Hermes external skill directories are not a read-only protection boundary. If the external directory is writable by Hermes and you allow skill edits, Hermes may modify files in place. For shared team directories or upstream clones, keep them read-only or copy selected skills into `~/.hermes/skills/`.

## Suggested Starter Set

You do not need to install every skill at first. A practical starter set is:

| Task | Recommended skill |
| --- | --- |
| Paper reading, translation, figure-text alignment | `nature-reader` |
| Manuscript polishing and English academic expression | `nature-polishing` |
| Abstract, introduction, and discussion drafting | `nature-writing` |
| Pre-submission reviewer simulation | `nature-reviewer` |
| Revision response, cover letter, reviewer replies | `nature-response` |
| Scientific figures and manuscript schematics | `nature-figure` |
| Literature search, strict self-citation audit, citer profiling | `nature-academic-search` |

To link every `nature-*` skill into one directory:

```bash
mkdir -p ~/.agents/skills
for skill in ~/ai-skills/nature-skills/skills/nature-*; do
  ln -s "$skill" ~/.agents/skills/"$(basename "$skill")"
done
```

This example uses OpenCode's global `.agents/skills` directory. For OpenClaw, replace the target with `~/.openclaw/workspace/skills`; for Hermes, prefer `external_dirs`.
