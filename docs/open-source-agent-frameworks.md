# OpenClaw / OpenCode / Hermes 接入教程

`nature-skills` 的核心单元是完整的技能目录，而不是单个 `SKILL.md` 文件。接入 OpenClaw、OpenCode、Hermes 这类开源 agent 框架时，推荐先保留一个稳定的本地仓库 clone，再让目标框架扫描或引用 `skills/` 下的完整目录。

## 通用准备

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

后续更新：

```bash
cd ~/ai-skills/nature-skills
git pull
```

关键规则：

1. 保留完整技能目录，例如 `skills/nature-reader/`，不要只复制 `SKILL.md`。
2. 如果技能引用共享文件，保留同级的 `skills/nature-shared/`。
3. 涉及脚本、MCP 服务或 API 的技能仍需要按技能 README 配置依赖、环境变量和本机凭据。

## OpenClaw

OpenClaw 的 workspace skill 目录通常是：

```text
~/.openclaw/workspace/skills/<skill>/SKILL.md
```

推荐用符号链接指向稳定 clone，这样后续 `git pull` 后不需要重复复制：

```bash
mkdir -p ~/.openclaw/workspace/skills
ln -s ~/ai-skills/nature-skills/skills/nature-reader ~/.openclaw/workspace/skills/nature-reader
ln -s ~/ai-skills/nature-skills/skills/nature-shared ~/.openclaw/workspace/skills/nature-shared
```

如果要接入多个技能，继续为每个 `nature-*` 目录创建链接即可：

```bash
ln -s ~/ai-skills/nature-skills/skills/nature-polishing ~/.openclaw/workspace/skills/nature-polishing
ln -s ~/ai-skills/nature-skills/skills/nature-writing ~/.openclaw/workspace/skills/nature-writing
```

如果你的系统或同步盘不适合使用符号链接，也可以复制完整目录：

```bash
cp -R ~/ai-skills/nature-skills/skills/nature-reader ~/.openclaw/workspace/skills/
cp -R ~/ai-skills/nature-skills/skills/nature-shared ~/.openclaw/workspace/skills/
```

复制方式需要在仓库更新后重新复制对应目录。

## OpenCode

OpenCode 可以从项目或全局的 `.agents/skills/**/SKILL.md` 发现 skills。想让所有项目都能用，可以放到全局目录：

```bash
mkdir -p ~/.agents/skills
ln -s ~/ai-skills/nature-skills/skills/nature-reader ~/.agents/skills/nature-reader
ln -s ~/ai-skills/nature-skills/skills/nature-polishing ~/.agents/skills/nature-polishing
ln -s ~/ai-skills/nature-skills/skills/nature-shared ~/.agents/skills/nature-shared
```

只想让某个项目使用时，在项目根目录放到 `.agents/skills/`：

```bash
cd /path/to/your/project
mkdir -p .agents/skills
ln -s ~/ai-skills/nature-skills/skills/nature-reader .agents/skills/nature-reader
ln -s ~/ai-skills/nature-skills/skills/nature-shared .agents/skills/nature-shared
```

较新的 OpenCode 配置也可以在 `opencode.json` 或 `opencode.jsonc` 中声明额外 skills 路径：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "skills": ["~/ai-skills/nature-skills/skills"]
}
```

如果你使用的是旧版 OpenCode，配置可能仍是下面这种结构：

```json
{
  "skills": {
    "paths": ["~/ai-skills/nature-skills/skills"]
  }
}
```

启动 OpenCode 后，可以先让它列出或使用某个技能，例如：

```text
Use the nature-reader skill to turn this paper into a Chinese-English Markdown reader.
```

## Hermes

Hermes 的默认技能目录是：

```text
~/.hermes/skills/
```

推荐方式是在 `~/.hermes/config.yaml` 中把 `nature-skills` 的 `skills/` 目录声明为外部技能目录：

```yaml
skills:
  external_dirs:
    - ~/ai-skills/nature-skills/skills
```

这样 Hermes 可以直接发现 `nature-reader`、`nature-polishing`、`nature-writing` 等技能，并通过 slash command 使用：

```text
/nature-reader 把这篇论文做成中英文对照 Markdown reader。
```

如果你不想让 Hermes 直接扫描外部仓库，也可以复制到 Hermes 自己的目录：

```bash
mkdir -p ~/.hermes/skills/research
cp -R ~/ai-skills/nature-skills/skills/nature-reader ~/.hermes/skills/research/
cp -R ~/ai-skills/nature-skills/skills/nature-polishing ~/.hermes/skills/research/
cp -R ~/ai-skills/nature-skills/skills/nature-shared ~/.hermes/skills/research/nature-shared
```

需要注意：Hermes 的外部技能目录不是只读保护边界。如果你允许 Hermes 修改技能，且外部目录对 Hermes 可写，它可能会原地修改该目录中的文件。团队共享或上游仓库 clone 建议保持只读，或者复制到 `~/.hermes/skills/` 后再使用。

## 推荐的最小组合

刚开始不需要一次性接入全部技能。推荐先接入：

| 任务 | 推荐技能 |
| --- | --- |
| 读论文、翻译、图文对应 | `nature-reader` |
| 论文润色、英文表达 | `nature-polishing` |
| 写摘要、引言、讨论 | `nature-writing` |
| 预审稿、模拟 reviewer | `nature-reviewer` |
| 返修、cover letter、审稿意见回复 | `nature-response` |
| 科研图、论文示意图 | `nature-figure` |
| 文献检索、严格他引、引用者画像 | `nature-academic-search` |

如果要一次性链接全部 `nature-*` 技能到某个目录，可以用：

```bash
mkdir -p ~/.agents/skills
for skill in ~/ai-skills/nature-skills/skills/nature-*; do
  ln -s "$skill" ~/.agents/skills/"$(basename "$skill")"
done
```

这个示例以 OpenCode 的全局 `.agents/skills` 目录为例。用于 OpenClaw 时，把目标目录换成 `~/.openclaw/workspace/skills`；用于 Hermes 时，优先使用 `external_dirs`。
