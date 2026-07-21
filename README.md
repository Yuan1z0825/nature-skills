<div align="center">
  <p>
    <img src="assets/readme-banner-cn.png" alt="Nature Skills：面向全球学者的科研 Skill 库" width="100%">
  </p>
  <p>
    <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-2ea44f"></a>
    <a href="#5-安装"><img alt="Install" src="https://img.shields.io/badge/install-Claude%20Code%20%7C%20Codex%20%7C%20OpenClaw%20%7C%20OpenCode%20%7C%20Hermes-111827"></a>
    <a href="#6-技能索引"><img alt="Skills" src="https://img.shields.io/badge/skills-17-0ea5e9"></a>
    <a href="README_EN.md"><img alt="Language" src="https://img.shields.io/badge/language-中文%20%7C%20English-1f6feb"></a>
  </p>
  <p>
    <a href="https://yuan1z0825.github.io/nature-skills/">在线网站</a>
    · <a href="#5-安装">立即安装</a>
    · <a href="#4-快速开始">快速开始</a>
    · <a href="#6-技能索引">技能索引</a>
    · <a href="docs/open-source-agent-frameworks.md">其他安装</a>
    · <a href="#7-贡献与开发">贡献方式</a>
    · <a href="README_EN.md">English</a>
  </p>
</div>

---

`nature-skills` 面向全球 AI 学者收录可复用科研技能，强调真实问题解决、可验证工作流与可直接使用的科研产物。

## 目录

- [1. 项目发起人与运营信息](#1-项目发起人与运营信息)
  - [1.1 创始人介绍](#11-创始人介绍)
  - [1.2 知识星球](#12-知识星球)
  - [1.3 自营 GPT / Claude 代充与成品号](#13-自营-gpt--claude-代充与成品号)
  - [1.4 商务合作](#14-商务合作)
- [2. Skills 主要开发者](#2-skills-主要开发者)
- [3. 项目理念与社区](#3-项目理念与社区)
- [4. 快速开始](#4-快速开始)
- [5. 安装](#5-安装)
  - [5.1 `npx skills` 安装方式](#51-npx-skills-安装方式)
  - [5.2 Claude Code 安装方式](#52-claude-code-安装方式)
  - [5.3 Codex 安装方式](#53-codex-安装方式)
  - [5.4 其他 Agent 场景](#54-其他-agent-场景)
- [6. 技能索引](#6-技能索引)
- [7. 贡献与开发](#7-贡献与开发)
- [8. Star 历史](#8-star-历史)

## 1. 项目发起人与运营信息

### 1.1 创始人介绍

大家好，我是 `nature-skills` 的创立者袁一哲。感谢大家持续关注本项目。我们在抖音更新了许多视频教程，大家可以根据名称检索查看，希望能够真正帮助到科研工作。

### 1.2 知识星球

知识星球名称：**Nature Skills 以及背后的哲学**。

<img width="300" height="400" alt="Nature Skills 知识星球" src="https://github.com/user-attachments/assets/64e37909-0a48-4bfb-8471-c2aff971a0f6" />

### 1.3 自营 GPT / Claude 代充与成品号

严格筛选渠道商，提供完全正规的充值渠道与服务。欢迎访问 **Nature AI 充值卡网**：

<table>
  <tr>
    <td align="center" width="68%">
      <a href="https://apiciyuan.top/">
        <img src="assets/nature-ai-gpt-claude-service.png" alt="Nature AI GPT 与 Claude 代充及成品号服务" width="100%">
      </a>
      <br>
      <strong>Nature AI 充值卡网</strong>
      <br>
      <a href="https://apiciyuan.top/">https://apiciyuan.top/</a>
    </td>
    <td align="center" width="32%">
      <img src="assets/nature-ai-wechat.jpg" alt="Nature AI 客服 WeChat 二维码" width="280">
      <br>
      <strong>微信客服</strong>
      <br>
      <sub>扫码添加</sub>
    </td>
  </tr>
</table>

### 1.4 商务合作

如有商务合作意向，欢迎发送邮件至 [natureskills2026@outlook.com](mailto:natureskills2026@outlook.com)。

## 2. Skills 主要开发者

| 开发者 | 项目角色 | 主要方向与贡献 | 主页与联系 |
|---|---|---|---|
| **袁一哲** | 创始人 / 维护者 | 项目发起、技能体系设计与社区运营 | — |
| **马昕瑞** | 核心开发者 | Skills 日常维护 | [Gmail](mailto:travisma2233@gmail.com) |
| **胡彬** | 主要贡献者 | Agentic Agent | [GitHub](https://github.com/Flyme886) · [Email](mailto:mhoang12205@gmail.com) |

## 3. 项目理念与社区

### 3.1 自己的一些浅薄观点

- 最近发现，我设计的 Nature Skills 被谷歌 DeepMind 关注并借鉴，他们参考了其中的引用体系、脚本思路以及技能设计哲学，推出了 Science Skills。说实话，这让我挺欣慰的——当国外的顶尖 AI 机构开始从我们的工作中汲取灵感时，说明中国开发者的原创思想正在被世界看见。这不是被复制的失落，而是中国力量在开源土壤里生根后，自然向外生长出的影响力。
- 我们设计 Skills 的重心，从来不是要求每个人都来啃透这套思想，而是这套思想本身就具备被机器理解并复用的能力。你如果想创立一个全新的 Skill，或者把它适配到自己的专属领域，根本不需要从头学起——直接把 Nature Skills 的 GitHub 地址发给 Codex，它就能自动学习其中的设计精髓，帮你完成新 Skill 的创建和修改。这才是思想的真正解放：它不再依赖口口相传，而是通过 AI 直接流淌进每一个需要它的角落。
- Nature Skills 真正的价值，或许并不在于那些具体的技能模块，而在于它悄悄推开了一扇新的大门——它让很多人第一次意识到，原来可以借助 Codex 或智能体来操控本地电脑做科研。我有幸见证并陪伴了许多人完成科研范式的转变。当他们惊叹“原来科研还可以这样去做”的那一刻，这种认知上的破壁和解放，远比 Skills 本身更让我觉得有意义。它不是一个工具的成功，而是一种新的思考方式开始在人群中蔓延。
- 在当下，几乎所有实用的工具都可以被提炼为标准化流程，而标准化流程恰好可以封装成可复用技能。

### 3.2 视频教程与社区

<table>
  <tr>
    <td align="center">
      <b>视频教程请关注抖音</b><br>
      <img width="300" alt="抖音视频教程" src="https://github.com/user-attachments/assets/37d4b0b6-3d22-4492-bb01-c0d9bae5a9e0" />
    </td>
    <td align="center">
      <b>Agent 科研交流群</b><br>
      <img width="300" alt="Agent 科研交流群" src="https://github.com/user-attachments/assets/28d1886a-69be-46bc-a1cb-777d7510ddab" />
    </td>
    <td align="center">
      <b>袁博个人微信</b><br>
      <img width="300" alt="袁博个人微信" src="https://github.com/user-attachments/assets/88e6b293-bda3-4094-94f9-aff4aa5a8842" />
    </td>
  </tr>
</table>

## 4. 快速开始

安装完成后，可以直接把论文、段落、审稿意见或任务描述交给 Agent。下面这些提示词可以直接复制使用：

| 想做什么 | 直接这样说 |
|---|---|
| 读论文 / 中英文对照 | `把这篇 PDF 做成图文对应的中英文对照 Markdown reader。` |
| 生成文献汇报 PPT | `把这篇论文做成中文组会汇报 PPT，保留关键图件和来源标注。` |
| 润色或翻译论文段落 | `把这段中文改写成 Nature 风格英文，保持学术含义不变。` |
| 写摘要、引言或讨论 | `根据这些结果和图件，帮我起草 Nature 风格的摘要和引言。` |
| 预投稿审稿模拟 | `从 Nature 审稿人视角评估这篇稿件，给出三份 reviewer reports。` |
| 回复审稿意见 | `根据这封返修邮件，帮我写逐点回复、cover letter，并标出修改稿需要标红的位置。` |
| 查文献、他引和引用者画像 | `整理这篇文章的引用数、严格他引数、DOI，并看引用者里有没有院士、Fellow 或领域大牛。` |
| 做科研图或论文示意图 | `根据这段方法和结果，帮我生成投稿级科研图或论文示意图草稿。` |

如果你不确定该用哪个技能，直接描述任务即可；如果已经知道技能名，可以在提示词中明确写“使用 `nature-reader`”或“使用 `nature-response`”。

## 5. 安装

`nature-skills` 是一组围绕 `SKILL.md` 组织的可复用技能包。`skills/` 下的每个顶层技能目录都是一个可安装单元，例如 `nature-*`；`nature-shared` 是供其他技能读取的共享支持包，默认不作为独立触发技能计入技能索引。

### 5.1 `npx skills` 安装方式

需要先安装 [Node.js 18 或更高版本](https://nodejs.org/)。无需全局安装 CLI；先查看仓库中可安装的技能名：

```bash
npx skills add Yuan1z0825/nature-skills --list
```

把全部技能全局安装到 Codex。`nature-shared` 会随全量安装一起加入，因此依赖共享参考资料的技能也能正常工作：

```bash
npx skills add Yuan1z0825/nature-skills --global --agent codex --skill '*' --yes --copy
```

只为当前项目安装一个独立技能时，省略 `--global`。例如：

```bash
npx skills add Yuan1z0825/nature-skills --agent codex --skill nature-figure --yes --copy
```

单独安装 `nature-reader`、`nature-paper2ppt`、`nature-polishing` 或 `nature-writing` 时，同时选择共享支持包：

```bash
npx skills add Yuan1z0825/nature-skills --global --agent codex \
  --skill nature-reader --skill nature-shared --yes --copy
```

也可以把全部技能安装到 CLI 支持的所有 agent：

```bash
npx skills add Yuan1z0825/nature-skills --all
```

检查全局安装结果并更新：

```bash
npx skills list --global --agent codex --json
npx skills update --global --yes
```

只更新一个技能，或只更新当前项目中的技能：

```bash
npx skills update nature-reader --global --yes
npx skills update --project --yes
```

技能选择参数使用 `--list` 显示的 frontmatter 名称；例如目录 `nature-proposal-writer` 当前显示为 `researchwrite`。`npx skills` 管理的是技能文件，Python、R、浏览器或 MCP 等可选运行依赖仍需按下文说明单独配置。

### 5.2 Claude Code 安装方式

Claude Code 不能直接使用 `scripts/update-codex-skills.sh`，因为这个脚本只负责同步到 Codex 的 `~/.codex/skills/`。用于 Claude Code 时，推荐保留一个稳定的本地 clone，再用 subagent 或 slash command 指向真实的 `skills/*/SKILL.md`。这样不会破坏技能目录结构，也能继续读取 `references/`、`static/`、`manifest.yaml`、脚本、资产和 `skills/nature-shared/`。

如果还没有安装 Claude Code：

```bash
npm install -g @anthropic-ai/claude-code
claude
```

先把仓库 clone 到一个稳定路径：

```bash
mkdir -p ~/ai-skills
cd ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git
```

推荐方式：为常用技能创建 Claude Code subagent wrapper。以 `nature-reader` 为例：

```bash
mkdir -p ~/.claude/agents
cat > ~/.claude/agents/nature-reader.md <<'EOF'
---
name: nature-reader
description: Use for Chinese-English paper reading, figure-aware translation, and source-grounded paper notes.
---

When invoked, first read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md` and follow it as the governing workflow.
Read supporting files from `~/ai-skills/nature-skills/skills/nature-reader/` and `~/ai-skills/nature-skills/skills/nature-shared/` only when needed.
Do not replace this skill with a generic paper-reading response.
EOF
```

然后开启新的 Claude Code 会话，直接请求使用这个 subagent：

```text
Use the nature-reader subagent to turn this paper into a Chinese-English Markdown reader.
```

如果你更喜欢 slash command，也可以创建命令 wrapper：

```bash
mkdir -p ~/.claude/commands
cat > ~/.claude/commands/nature-reader.md <<'EOF'
Read `~/ai-skills/nature-skills/skills/nature-reader/SKILL.md` first and follow it strictly.
Read directly needed supporting files from `~/ai-skills/nature-skills/skills/nature-reader/` and `~/ai-skills/nature-skills/skills/nature-shared/`.

$ARGUMENTS
EOF
```

在 Claude Code 中使用：

```text
/nature-reader 把这篇论文做成中英文对照的完整 Markdown reader。
```

安装其他技能时，把示例中的 `nature-reader` 换成对应目录名即可，例如 `nature-polishing`、`nature-writing`、`nature-reviewer`、`nature-response` 或 `nature-figure`。后续更新只需要：

```bash
cd ~/ai-skills/nature-skills
git pull
```

只要 wrapper 仍然指向这个稳定 clone 路径，就不需要重复复制技能文件。

**自动更新（可选）**

如果你希望 Claude Code 每次开启会话时自动拉取上游更新，可以用 `scripts/autoupdate-skills.sh` 配合一个 `SessionStart` 钩子。

这套方式把技能**直接复制**进 `~/.claude/skills/`（Claude Code 会自动发现该目录，技能以目录名直接加载），而不是使用上面的 wrapper。两种方式二选一即可。

先保留一个**专用**的稳定 clone（只用于同步技能，请不要在里面做开发提交）：

```bash
mkdir -p ~/ai-skills
git clone https://github.com/Yuan1z0825/nature-skills.git ~/ai-skills/nature-skills
```

首次安装，把技能复制进 Claude Code 的技能目录：

```bash
~/ai-skills/nature-skills/scripts/autoupdate-skills.sh --force
```

然后在 `~/.claude/settings.json` 里加一个 `SessionStart` 钩子（若已有 `hooks`，把这一项合并进去，不要整体覆盖）：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/ai-skills/nature-skills/scripts/autoupdate-skills.sh",
            "async": true,
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

`async: true` 让它在后台运行、不阻塞启动。脚本自带保护：默认 6 小时内不重复联网检查、断网或拉取失败自动跳过（`exit 0`，绝不卡住会话）、只有上游 HEAD 真正变化时才重新同步、并且拒绝在有未提交改动的 clone 上强行前进。拉到的新版会在**下一次**开启会话时生效（当前会话的技能已经加载完毕）。运行日志在 `~/.local/state/nature-skills/autoupdate.log`。

目标目录与检查频率都可配置：

```bash
# 默认同步到 ~/.claude/skills；用 --dest 指到别处，例如 Codex：
~/ai-skills/nature-skills/scripts/autoupdate-skills.sh --dest ~/.codex/skills
# 只在最多每小时检查一次：
~/ai-skills/nature-skills/scripts/autoupdate-skills.sh --throttle 3600
```

### 5.3 Codex 安装方式

推荐使用仓库自带脚本安装或更新 Codex skills。脚本会同步 `skills/` 下所有顶层技能目录，并在复制后做 `diff` 验证；它不会覆盖其他无关 Codex skills。

```bash
git clone https://github.com/Yuan1z0825/nature-skills.git
cd nature-skills
scripts/update-codex-skills.sh --pull
```

如果已经 clone 过仓库：

```bash
cd nature-skills
scripts/update-codex-skills.sh --pull
```

验证当前 Codex 安装是否和这个 checkout 一致：

```bash
scripts/update-codex-skills.sh --check
```

如果你长期用这个脚本更新，并希望清理上游已经删除的旧技能目录：

```bash
scripts/update-codex-skills.sh --pull --prune
```

`--prune` 只会删除以前由这个脚本记录过、但当前仓库已经不再包含的目录。第一次运行没有历史记录时，它不会猜测删除旧目录。

也可以把仓库链接交给 Codex，让 Codex 执行安装脚本。推荐提示词：

```text
请从这个仓库安装 Codex skills：
https://github.com/Yuan1z0825/nature-skills.git

请 clone 仓库后运行 scripts/update-codex-skills.sh --pull。
安装后再运行 scripts/update-codex-skills.sh --check 验证。
请保留 skills/ 下的完整技能目录，不要只复制 SKILL.md。
```

如果只安装单个技能，请明确说明技能名：

```text
只安装这个仓库里的 nature-reader：
https://github.com/Yuan1z0825/nature-skills.git

如果该技能需要共享文件，也请一并安装 skills/nature-shared。
```

关键规则：保留完整目录结构。请复制或引用整个技能文件夹，而不是只复制 `SKILL.md`，因为许多技能依赖 `references/`、`static/`、`manifest.yaml`、脚本、资产或共享文件。

默认安装只同步技能文件，不联网或改动现有 Python 环境。需要相关脚本或 MCP 服务时，可显式要求安装器把仓库中声明的 Python 依赖安装到独立虚拟环境：

```bash
scripts/update-codex-skills.sh --with-python-deps
scripts/update-codex-skills.sh --check --check-deps
```

默认虚拟环境位于 `${XDG_DATA_HOME:-$HOME/.local/share}/nature-skills/venv`；可用 `--venv /path` 或 `NATURE_SKILLS_VENV=/path` 覆盖，并可用 `--python /path/to/python` 选择创建环境的解释器。安装器还会为该专用环境配置启动钩子：仅在用户没有设置 `MPLCONFIGDIR` 时，把 Matplotlib 缓存指向沙箱可写的临时目录，避免重复字体缓存警告。安装成功后，虚拟环境及其 Python 路径会记录在 Codex skills 目录下的 `.nature-skills-python-runtime`。

国知局公布公告检索需要额外下载 Playwright Chromium，体积较大，因此保持单独启用：

```bash
scripts/update-codex-skills.sh --with-cnipa-browser
```

依赖安装失败会使脚本返回非零状态，不会把不完整的运行环境报告为成功。默认安装和自动更新不会静默安装这些依赖。

`nature-academic-search` 的 MCP 服务还需要单独配置 `PUBMED_EMAIL`，Scopus / ScienceDirect 等可选 provider 需要使用本机凭据配置，不要把 API key 写入仓库文件。

安装后，请开启一个新的 Codex 会话，然后自然描述任务，例如：

```text
把这篇论文做成中英文对照的完整 Markdown reader。
```

```text
把这篇论文做成中文PPT。
```

如果你使用 OpenClaw、OpenCode、Hermes 等开源 agent / 编程框架，请看 [OpenClaw / OpenCode / Hermes 接入教程](docs/open-source-agent-frameworks.md)。

**自动更新（可选）**

Codex 支持全局 `SessionStart` hook。保留一个专用 clone 后，可以在每次启动或恢复 Codex 会话时检查更新，并把新版同步到 `~/.codex/skills/`。

先创建专用 clone 并完成首次同步：

```bash
mkdir -p ~/.codex
git clone https://github.com/Yuan1z0825/nature-skills.git ~/.codex/.nature-skills-src
~/.codex/.nature-skills-src/scripts/autoupdate-skills.sh \
  --dest ~/.codex/skills --force
```

然后创建或合并 `~/.codex/hooks.json`：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "/bin/bash \"$HOME/.codex/.nature-skills-src/scripts/autoupdate-skills.sh\" --dest \"$HOME/.codex/skills\"",
            "timeout": 75,
            "statusMessage": "Checking Nature Skills updates"
          }
        ]
      }
    ]
  }
}
```

若 `hooks.json` 中已有其他 hook，请合并 `SessionStart` 项，不要整体覆盖。首次启用或修改 hook 后，在 Codex 中运行 `/hooks` 检查并信任它。Codex 当前按同步方式执行 command hook，因此这里依靠脚本自带的 6 小时节流、60 秒网络保护和断网自动跳过，避免每次会话都重复联网或因更新失败阻断启动。

更新日志位于 `~/.local/state/nature-skills/autoupdate.log`。拉取到的新技能通常在下一次会话中完整生效。

### 5.4 其他 Agent 场景

OpenClaw、OpenCode、Hermes 的具体接入方式见 [OpenClaw / OpenCode / Hermes 接入教程](docs/open-source-agent-frameworks.md)。

用于其他 agent 时，建议保留一个稳定的仓库 clone，再创建轻量 subagent、slash command 或 custom prompt wrapper，指向真实的 `skills/*/SKILL.md`，并保留 `skills/nature-shared/`。

手动或其他 agent 使用时：

1. 将完整技能目录复制到你的 prompt library 或项目中。
2. 保留 `SKILL.md`、`manifest.yaml`、`static/`、`references/`、脚本、资产和需要的 `skills/nature-shared/` 文件。
3. 如目标 agent 有自己的格式要求，可调整 frontmatter 和正文结构。

## 6. 技能索引

当前 `skills/` 下包含以下可触发技能；`skills/nature-shared/` 是共享内容目录，不计入技能索引。点击技能名或“详情页”可以进入每个 skill 的单独说明页面。

| 技能 | 状态 | 用途 | 触发词 | 详情页 |
|-------|--------|---------|-----------------|--------|
| [`nature-figure`](skills/nature-figure/README.md) | Stable | 面向 Nature / 高影响力期刊的 Python 或 R 投稿级科研图工作流，内置 figures4papers demo，并支持通过 OpenRouter GPT Image 2 生成论文示意图草稿 | “Nature figure”, “投稿级图片”, “publication plot”, “scientific figure”, “figures4papers”, “论文示意图”, “GPT Image 2” | [详情](skills/nature-figure/README.md) |
| [`nature-polishing`](skills/nature-polishing/README.md) | Stable | 将学术文本润色、重构或翻译为 Nature 风格英文 | “Nature style”, “润色”, “academic writing”, “论文英文” | [详情](skills/nature-polishing/README.md) |
| [`nature-writing`](skills/nature-writing/README.md) | Draft | 起草 Nature 风格手稿章节，并重建论文论证 | “Nature writing”, “写摘要”, “写引言”, “manuscript draft”, “论文写作” | [详情](skills/nature-writing/README.md) |
| [`nature-reviewer`](skills/nature-reviewer/README.md) | Draft | 从审稿人视角模拟 Nature 风格评审，输出三份 reviewer reports 和综合意见 | “Nature reviewer”, “预投稿评审”, “reviewer report”, “审稿人视角评估” | [详情](skills/nature-reviewer/README.md) |
| [`nature-citation`](skills/nature-citation/README.md) | Beta | 检索严格限定在 Nature / CNS 系列的支撑文献，并导出 ENW、RIS 或 Zotero RDF | “Nature citation”, “CNS citation”, “分段引用”, “支撑文献”, “Zotero RDF” | [详情](skills/nature-citation/README.md) |
| [`nature-data`](skills/nature-data/README.md) | Draft | 准备 Data Availability statement、数据仓储方案和 FAIR 检查 | “Data Availability”, “数据可用性”, “repository”, “FAIR metadata” | [详情](skills/nature-data/README.md) |
| [`nature-statistics`](skills/nature-statistics/README.md) | Draft | 审查、改写或起草 Nature / 高影响力期刊投稿中的统计报告，覆盖样本量、独立分析单位、重复数、p 值、多重比较、效应量、置信区间、图注统计和审稿人统计意见 | “Nature statistics”, “统计审查”, “statistical analysis”, “p value”, “sample size”, “replicates”, “multiple comparisons”, “图注统计”, “统计分析小节” | [详情](skills/nature-statistics/README.md) |
| [`nature-reader`](skills/nature-reader/README.md) | Beta | 生成带来源锚点、图文对应和中英文对照的全文 Markdown reader | “nature reader”, “全文 Markdown”, “原文对照”, “图文对应”, “全文翻译” | [详情](skills/nature-reader/README.md) |
| [`nature-response`](skills/nature-response/README.md) | Beta | 解析返修邮件，起草、审查和修改返修 cover letter、逐点回复审稿人的 response letter、标红修改稿，并提供 LaTeX 模板 | “response to reviewers”, “rebuttal letter”, “cover letter”, “major revision”, “返修邮件”, “审稿意见回复”, “修回信”, “LaTeX 模板” | [详情](skills/nature-response/README.md) |
| [`nature-paper2ppt`](skills/nature-paper2ppt/README.md) | Beta | 从科研论文生成中文 PPTX 文献汇报 deck | “paper PPT”, “journal club”, “paper to slides”, “论文汇报” | [详情](skills/nature-paper2ppt/README.md) |
| [`nature-paper-to-patent`](skills/nature-paper-to-patent/README.md) | Beta | 从论文、技术报告或项目材料生成有证据约束的中国发明专利草稿，并支持专利点挖掘、查新和技术交底书迭代 | “paper to patent”, “Chinese patent”, “论文转专利”, “权利要求书”, “技术交底书”, “专利点” | [详情](skills/nature-paper-to-patent/README.md) |
| [`nature-ref-verifier`](skills/nature-ref-verifier/README.md) | Stable | 参考文献多源交叉验证：逐字段对比作者/标题/年份/卷期/页码，标记卷年冲突、作者编造、页码偏差等 | “verify refs”, “校验文献”, “check references”, “文献验证”, “ref check” | [详情](skills/nature-ref-verifier/README.md) |
| [`nature-academic-search`](skills/nature-academic-search/README.md) | Beta | 多源文献检索、引用核验、严格他引审计、文章引用指标表、高影响力引用者画像和参考文献管理 | “search papers”, “find articles”, “literature search”, “查文献”, “verify DOI”, “严格他引”, “文章引用表”, “引用我的文章的人有没有大牛” | [详情](skills/nature-academic-search/README.md) |
| [`nature-downloader`](skills/nature-downloader/README.md) | Beta | 通过图书馆资源入口、Chrome 登录态和开放获取路径合法获取学术全文/PDF | “download papers”, “图书馆下载文献”, “CARSI”, “Web of Science”, “PDF 下载” | [详情](skills/nature-downloader/README.md) |
| [`nature-literature-pipeline`](skills/nature-literature-pipeline/README.md) | Stable | 自动化文献发现管线：多源检索、六维评分、精读推送和本地归档 | “literature pipeline”, “每日文献”, “文献推送”, “daily literature push”, “cron” | [详情](skills/nature-literature-pipeline/README.md) |
| [`nature-experiment-log`](skills/nature-experiment-log/README.md) | Draft | 标准化记录实验图片、语音和文字材料，生成带 YAML frontmatter 的 Obsidian 实验日志并归档原始材料 | “实验日志”, “记录实验”, “experiment log”, “Obsidian vault”, “飞书科研群” | [详情](skills/nature-experiment-log/README.md) |
| [`nature-proposal-writer`](skills/nature-proposal-writer/README.md) | Beta | proposal-first 科研写作状态机，先建立证据、论证和章节契约，再起草或审查文本 | “researchwrite”, “proposal”, “开题报告”, “研究方案”, “科研写作 QA” | [详情](skills/nature-proposal-writer/README.md) |

## 7. 贡献与开发

### 7.1 共享设计原则

所有技能都遵守以下原则：

1. **优先使用一手来源**：规则基于已发表 Nature 内容、官方期刊指南或明确的本地来源，而不是泛泛审美偏好。
2. **显式胜过隐式**：每条规则都应说明理由，而不是只给断言。
3. **感知章节与任务上下文**：学术写作、图件、引用和回复都依赖上下文；不同论文部分使用不同逻辑。
4. **输出优先**：每个技能都应返回能直接使用的产物，例如可粘贴文本、`.svg`、`.pptx`、`.docx` 或具体建议。
5. **可扩展**：每个技能自包含在自己的目录中，新增技能不应要求修改既有技能。

### 7.2 仓库目录结构

```text
skills/
├── nature-shared/              # 当技能引用 ../nature-shared 时需要保留
├── nature-<topic>/
│   ├── README.md
│   ├── README_EN.md
│   ├── SKILL.md
│   ├── manifest.yaml     # router-style 技能会包含
│   ├── static/           # router-style 技能会包含
│   └── references/...
└── nature-proposal-writer/
    ├── README.md
    ├── README_EN.md
    ├── SKILL.md
    ├── scripts/...
    ├── templates/...
    └── references/...
```

### 7.3 新增技能流程

向本仓库添加技能时，请按以下流程：

**1. 创建技能目录**

```text
skills/nature-<topic>/
```

**2. 添加必需文件**

| 文件 | 是否必需 | 用途 |
|------|----------|------|
| `SKILL.md` | 必需 | frontmatter（`name`、`description`）+ 规则 + 工作流；触发后由 agent 加载 |
| `README.md` | 必需 | 面向人的中文说明文档 |
| `README_EN.md` | 必需 | 与中文详情页配套的英文说明文档 |
| `references/*.md` | 复杂技能推荐 | 模块化规则文件，例如 API、设计理论、教程、图表类型等 |

**3. 编写中英文 README**

每个新增技能都必须同时提供 `README.md` 和 `README_EN.md`。README 是面向人的技能入口页，不是 `SKILL.md` 的重复版，也不是安装手册。它的目标是让用户在 30 秒内判断：这个 skill 能不能解决我的问题、我要给它什么、它会产出什么、边界在哪里。

基本规则：

- 中文 README 和英文 README 必须一一镜像：标题数量一致、顺序一致、信息点一致；英文页不要写成另一套独立模板。
- 顶部固定为技能名、语言切换链接和一句定位说明。
- 默认使用下面的基础结构；只有确实需要时才插入可选章节。
- 不要在单个 skill README 中重复仓库安装教程、作者信息、变更日志、开发过程、完整文件树或大段内部实现细节。
- 复杂规则、API 参数、长教程、脚本说明和模板索引应放进 `references/`、`static/`、`scripts/` 或 `SKILL.md`，README 只保留路标。
- 如果技能有视觉资产，可以放一个小型预览表；不要把 README 变成大型图库或长篇技术手册。

中文 README 基础结构：

```markdown
# `nature-<topic>` 技能

[English](README_EN.md)

一句话说明这个技能的定位、主要任务和使用边界。

## 适合用它做什么
## 典型请求
## 你需要提供
## 产出
## 边界
## 相关技能
```

英文 README 必须对应为：

```markdown
# `nature-<topic>` Skill

[中文说明](README.md)

One sentence describing the skill's role, main task, and usage boundary.

## What To Use It For
## Typical Requests
## What You Need To Provide
## Outputs
## Boundaries
## Related Skills
```

可选章节必须中英文同步插入，并保持相同顺序。常见可选章节包括：

| 中文章节 | 英文章节 | 使用场景 |
|----------|----------|----------|
| `## 工作方式` | `## Workflow` | 需要解释核心流程或路由方式 |
| `## 运行和依赖` | `## Runtime and Dependencies` | 有脚本、MCP、API key、本地配置或外部依赖 |
| `## 示例预览` | `## Example Preview` | 有少量图件、截图或可视化资产值得展示 |
| `## 内置参考` | `## Built-In References` | 需要指向 `references/`、`assets/` 或 demo |
| `## 方法来源` | `## Method Sources` | 写作、审查或分析规则来自特定来源 |
| `## 三种模式` | `## Three Modes` | 技能有清晰的 compose/revise/hybrid 等模式 |
| `## 与 ... 的关系` | `## Relationship With ...` | 容易和另一个技能混淆，需要说明分工 |

提交前至少做这些 README 检查：

```bash
python scripts/validate-readmes.py
git diff --check
for d in skills/nature-*; do
  [ -f "$d/README.md" ] && [ -f "$d/README_EN.md" ] || continue
  rg -q '^\[English\]\(README_EN\.md\)$' "$d/README.md"
  rg -q '^\[中文说明\]\(README\.md\)$' "$d/README_EN.md"
  test "$(rg -c '^## ' "$d/README.md")" = "$(rg -c '^## ' "$d/README_EN.md")"
done
```

**4. 录制使用教程**

提交 PR 时，请同时录制一个简短的使用教程，说明这个 skill 解决什么问题、如何触发、需要什么输入，以及会产出什么结果。可以在 PR 描述中附上视频、录屏链接或可公开访问的教程地址。

**5. 配置 `SKILL.md` frontmatter**

```yaml
---
name: nature-<topic>
description: >-
  用一句话说明这个技能做什么、什么时候触发、主要输出格式和核心使用场景。
---
```

**6. 更新技能索引**

在上方 [技能索引](#6-技能索引) 表格中添加一行：

```markdown
| [`nature-<topic>`](skills/nature-<topic>/README.md) | Draft / Stable | 一句话用途 | 触发词 | [详情](skills/nature-<topic>/README.md) |
```

**7. 设置状态标签**

| 标签 | 含义 |
|-------|------|
| `Draft` | 规则已定义，但尚未在真实案例上测试 |
| `Beta` | 已在示例上测试，仍可能存在边界问题 |
| `Stable` | 已在真实学术内容上验证，规则相对稳定 |

---

## 8. Star 历史

[![Star History Chart](assets/star-history.svg?v=20260715T1629Z)](https://star-history.com/#Yuan1z0825/nature-skills&Date)
