# nature-skills Installation Guide

This file explains how to install the skills in this repository so they are actually usable in coding agents such as Codex and Claude Code.

The most important point is simple:

- `nature-skills` is **not** a Python package or npm package
- each `skills/nature-*` folder is one reusable skill unit
- in most cases, you should copy or reference the **entire folder**, not only `SKILL.md`
- `skills/_shared/` is shared support content for several router-style skills

Why that matters:

- many skills depend on `references/`
- newer router-style skills may depend on `static/`, `manifest.yaml`, and `../_shared`
- some skills also use `README.md` as supporting context
- copying only `SKILL.md` can silently break the workflow

---

## 1. What gets installed

Each installable skill lives under `skills/` and is centred on `SKILL.md`.
Some also include `README.md`, `manifest.yaml`, `static/`, `references/`,
assets, scripts, or eval files.

Typical examples:

```text
skills/
├── _shared/               # shared support files used by some skills
└── nature-<topic>/
    ├── SKILL.md
    ├── README.md          # common, but not guaranteed
    ├── manifest.yaml      # present for router-style skills
    ├── static/            # present for router-style skills
    ├── references/        # present for many skills
    └── ...
```

Examples in this repository:

- `nature-academic-search`
- `nature-citation`
- `nature-data`
- `nature-figure`
- `nature-paper2ppt`
- `nature-polishing`
- `nature-reader`
- `nature-response`
- `nature-reviewer`
- `nature-writing`

If you want one skill, install one folder.
If you want the full collection, install `skills/_shared` plus all
`skills/nature-*` folders.

---

## 2. Quick choice

Choose the path that matches your agent:

- **Codex plugin marketplace**: best if you want the packaged bundle
- **Codex local skills**: best if you want direct folder copying
- **Claude Code plugin marketplace**: best if you want direct plugin installation from this repository
- **Claude Code wrappers**: best if you prefer terminal-based agent workflows pinned to a local clone path
- **Other agents**: use the whole skill folder as a reusable prompt bundle

---

## 3. Install for Codex

Codex is the cleanest target for this repository because it can use the packaged
plugin or local skill folders directly.

### 3.1 Plugin marketplace installation

```bash
codex plugin marketplace add https://github.com/Yuan1z0825/nature-skills --ref main
codex plugin add nature-skills@nature-skills
```

After installation, start a new Codex session if the new skills do not appear
immediately. The plugin package contains all `nature-*` skills and the shared
support files they reference.

To update a Codex marketplace installation later:

```bash
codex plugin marketplace upgrade
codex plugin add nature-skills@nature-skills
```

### 3.2 Manual local-skill installation

Clone the repository:

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
```

### 3.3 Install one skill

Example: install `nature-polishing`

```bash
mkdir -p ~/.codex/skills
cp -R skills/_shared ~/.codex/skills/
cp -R skills/nature-polishing ~/.codex/skills/
```

Copying `_shared` is harmless even when the selected skill does not use it, and
it prevents broken relative references for skills that do.

### 3.4 Install all current skills

```bash
mkdir -p ~/.codex/skills
cp -R skills/_shared ~/.codex/skills/
for d in skills/nature-*; do
  cp -R "$d" ~/.codex/skills/
done
```

### 3.5 Verify

Start a fresh Codex session and ask for a task that clearly matches the skill, for example:

```text
Polish this abstract in Nature style.
```

or

```text
Turn this paper into a Chinese journal-club PPT.
```

If the installed skill is discovered correctly, Codex should use the skill-specific workflow instead of answering with a generic one-shot response.

### 3.6 Update later

When this repository changes:

```bash
cd /path/to/nature-skills
git pull
cp -R skills/_shared ~/.codex/skills/
cp -R skills/nature-polishing ~/.codex/skills/
```

If you installed all skills, re-copy `skills/_shared` and all `skills/nature-*`
folders after pulling.

For Codex marketplace installs, use the marketplace update commands from
section 3.1 rather than copying local skill folders.

### 3.7 Common Codex mistake

Do **not** do this:

```bash
cp skills/nature-polishing/SKILL.md ~/.codex/skills/
```

That copies only one file and drops the rest of the skill bundle.

Use this instead:

```bash
cp -R skills/_shared ~/.codex/skills/
cp -R skills/nature-polishing ~/.codex/skills/
```

---

## 4. Install for Claude Code

Claude Code can install this repository in **two** ways:

1. directly through the Claude Code plugin marketplace using the repository's
   `.claude-plugin/` metadata
2. through a thin wrapper/subagent that points to a stable local clone

### 4.1 Direct plugin installation (recommended when available)

This repository already ships Claude Code plugin metadata in:

```text
.claude-plugin/
  plugin.json
  marketplace.json
```

So Claude Code users can install the bundle directly:

```bash
claude plugin marketplace add Yuan1z0825/nature-skills
claude plugin install nature-skills@nature-skills
```

After installation:

- restart Claude Code or open a fresh session if the plugin does not appear
- the complete `nature-skills` bundle should be available without manually
  creating wrappers

To update a Claude Code plugin installation later:

```bash
claude plugin marketplace update nature-skills
claude plugin update nature-skills@nature-skills
```

### 4.2 Wrapper / subagent installation

If you prefer a local clone path and explicit wrappers, the practical solution is:

1. keep a local clone of this repository
2. create a small Claude Code wrapper
3. let that wrapper tell Claude Code to read the real `SKILL.md` from this repository

This keeps the original skill structure intact and avoids breaking supporting files such as `references/`, `README.md`, assets, or scripts when a skill depends on them.

Official Claude Code documentation:

- Setup: <https://docs.anthropic.com/en/docs/claude-code/setup>
- Subagents: <https://docs.anthropic.com/en/docs/claude-code/sub-agents>
- Slash commands: <https://docs.anthropic.com/en/docs/claude-code/slash-commands>

### 4.2.1 Install Claude Code first

If you have not installed Claude Code yet:

```bash
npm install -g @anthropic-ai/claude-code
claude
```

### 4.2.2 Clone this repository to a stable local path

Example:

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

In the examples below, the repository path is:

```text
~/ai-skills/nature-skills
```

If you use a different path, replace it consistently.

### 4.2.3 Recommended wrapper method: create a subagent

Create a user-level subagent:

```bash
mkdir -p ~/.claude/agents
cat > ~/.claude/agents/nature-polishing.md <<'EOF'
---
name: nature-polishing
description: Use proactively for Nature-style academic polishing, restructuring, or Chinese-to-English manuscript refinement.
---

When invoked, first read `~/ai-skills/nature-skills/skills/nature-polishing/SKILL.md`.
Treat that file as the governing workflow.
If the skill references supporting files, read only the specific files you need from
`~/ai-skills/nature-skills/skills/nature-polishing/` and
`~/ai-skills/nature-skills/skills/_shared/`.
Do not replace the skill with a generic polishing response.
EOF
```

Then start a new Claude Code session and ask:

```text
Use the nature-polishing subagent to revise this abstract.
```

### 4.2.4 Alternative wrapper method: create a slash command

If you prefer a command instead of a subagent:

```bash
mkdir -p ~/.claude/commands
cat > ~/.claude/commands/nature-polishing.md <<'EOF'
Read `~/ai-skills/nature-skills/skills/nature-polishing/SKILL.md` first and follow it strictly.
Read any directly needed supporting files from `~/ai-skills/nature-skills/skills/nature-polishing/`.

$ARGUMENTS
EOF
```

Then inside Claude Code:

```text
/nature-polishing Rewrite this abstract for Nature.
```

### 4.2.5 Why the wrapper approach is better than copying only `SKILL.md`

This repository was not designed as a single-file Claude Code prompt pack.

If you only copy `SKILL.md` into `~/.claude/agents/` and leave the rest behind:

- relative supporting material is no longer colocated
- future updates in the original repository are harder to reuse
- some skills become incomplete in practice

Keeping the repo cloned and pointing Claude Code at the real folder is more robust.

### 4.2.6 Install more skills for Claude Code

Repeat the same pattern for other folders:

- `nature-academic-search`
- `nature-figure`
- `nature-citation`
- `nature-data`
- `nature-reader`
- `nature-paper2ppt`
- `nature-polishing`
- `nature-response`
- `nature-reviewer`
- `nature-writing`

Use the plugin-marketplace path if you want the full bundle with the least
manual setup. Use wrappers if you want each skill pinned to a specific local
clone path and editable outside the plugin lifecycle.

For example, a `nature-paper2ppt` wrapper should point to:

```text
~/ai-skills/nature-skills/skills/nature-paper2ppt/SKILL.md
```

The same pattern works for `nature-reader`:

```text
~/ai-skills/nature-skills/skills/nature-reader/SKILL.md
```

### 4.7 Update later

```bash
cd ~/ai-skills/nature-skills
git pull
```

If your wrapper points to this stable clone path, no further reinstall step is needed.

For Claude Code marketplace installs, use the marketplace update commands from
section 4.1.

---

## 4.8 Maintainer release versioning

Plugin managers cache installed bundles by version. If the repository changes
but the plugin version remains unchanged, Codex or Claude Code may keep using an
older cached bundle.

Before publishing a marketplace update, refresh all plugin manifest versions
from the current Git commit:

```bash
~/miniconda3/python.exe scripts/sync_plugin_version.py
```

The script updates `.claude-plugin/plugin.json`,
`.claude-plugin/marketplace.json`, and
`plugins/nature-skills/.codex-plugin/plugin.json`.

A practical release sequence is:

```bash
git add skills README.md install.md plugins .claude-plugin scripts
git commit -m "Update nature skills"
~/miniconda3/python.exe scripts/sync_plugin_version.py
git add .claude-plugin plugins/nature-skills/.codex-plugin
git commit -m "Refresh plugin version"
git push
```

The second commit records the short hash of the content commit that it packages.
This avoids relying on a manually maintained version number while still giving
the plugin managers a changed version key. After the second commit, verify that
relationship with:

```bash
~/miniconda3/python.exe scripts/sync_plugin_version.py --check --ref HEAD~1
```

---

## 5. Install for other agents

If your agent supports reusable prompt folders, profile files, or custom system prompts, use the real skill directory under `skills/` as the portable unit:

```text
skills/
├── _shared/
└── nature-<topic>/
    ├── SKILL.md
    ├── README.md
    ├── manifest.yaml
    ├── static/
    ├── references/
    └── ...
```

Recommended rule:

1. copy the full skill directory
2. preserve `SKILL.md`, `manifest.yaml`, `static/`, `references/`, scripts,
   assets, and any needed `skills/_shared/` files together
3. adapt only the outer wrapper format required by the target agent

---

## 6. Which method should you use?

### Use Codex if:

- you want the packaged plugin marketplace path
- you want to copy folders into `~/.codex/skills/` and use them directly

### Use Claude Code if:

- you already work in Claude Code
- you are comfortable using subagents or slash commands as wrappers

### Use manual folder reuse if:

- your agent has no native skill system
- you still want the writing rules, references, and workflow as a reusable bundle

---

## 7. Troubleshooting

### Problem: the agent gives a generic answer instead of using the skill

Check:

- did you install the full `skills/nature-*` folder rather than only `SKILL.md`?
- did you also install `skills/_shared` if the skill references `../_shared`?
- did you start a fresh session after installation?
- are you asking for a task that clearly matches the skill?

### Problem: Claude Code wrapper exists but results are weak

Check:

- does the wrapper point to the correct local clone path?
- does that path still exist?
- did you explicitly tell Claude Code to use the subagent or slash command?

### Problem: updates in GitHub are not reflected locally

Run:

```bash
git pull
```

Then:

- for Codex local skills, copy `skills/_shared` and the updated folder(s) again
- for Codex plugin installation, run `codex plugin marketplace upgrade` and reinstall or refresh the plugin as needed
- for Claude Code wrappers, no reinstall is needed if the wrapper still points to the same clone path

For Claude Code plugin installation, run `claude plugin marketplace update
nature-skills` and `claude plugin update nature-skills@nature-skills`.

---

## 8. Minimal examples

### Codex: one-skill install

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
mkdir -p ~/.codex/skills
cp -R skills/_shared ~/.codex/skills/
cp -R skills/nature-polishing ~/.codex/skills/
```

### Codex: full install

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
mkdir -p ~/.codex/skills
cp -R skills/_shared ~/.codex/skills/
for d in skills/nature-*; do
  cp -R "$d" ~/.codex/skills/
done
```

### Claude Code: one subagent wrapper

```bash
npm install -g @anthropic-ai/claude-code
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
mkdir -p ~/.claude/agents
cat > ~/.claude/agents/nature-polishing.md <<'EOF'
---
name: nature-polishing
description: Use proactively for Nature-style academic polishing, restructuring, or Chinese-to-English manuscript refinement.
---

When invoked, first read `~/ai-skills/nature-skills/skills/nature-polishing/SKILL.md`.
Treat that file as the governing workflow.
If the skill references supporting files, read only the specific files you need from
`~/ai-skills/nature-skills/skills/nature-polishing/` and
`~/ai-skills/nature-skills/skills/_shared/`.
EOF
```

---

## 9. Final recommendation

If you only want the simplest path, use:

- **Codex** for direct skill-folder installation

If you mainly work in Claude Code, use:

- **a stable local clone of this repository**
- **thin wrappers in `~/.claude/agents/` or `~/.claude/commands/`**

That gives you a setup that is easy to update and does not discard the structure each skill depends on.
