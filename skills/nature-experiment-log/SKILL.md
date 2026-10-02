---
name: nature-experiment-log
description: "标准化实验日志记录——直接上传或读取本地图片、语音和文字，产出带 YAML frontmatter 的 Markdown；可选集成飞书 CLI 与 Obsidian。"
license: MIT
metadata:
  author: Jiahao8595
  hermes:
    tags: [research, experiment, logging, feishu, obsidian, automation]
    related_skills: [nature-literature-pipeline, feishu-cli-integration, obsidian]
---

# experiment-log — 实验日志标准化

## 输入方式

用户通过以下任一方式提交实验原始材料时自动加载：

- **直接上传** — 在当前会话提交图片、音频、语音转录或文字。
- **本地材料** — 提供本地文件或文件夹路径，由 agent 读取并整理。
- **飞书群** — 通过可选的 `feishu-cli-integration` 读取群消息和附件。

## 输出方式

- **本地 Markdown** — 将日志和原始附件保存到用户指定的普通本地文件夹；未指定目录时，先返回可保存的 Markdown，不擅自选择路径。
- **Obsidian vault** — 通过可选的 `obsidian` skill 写入 vault，并使用附带模板建立索引、异常记录和设备追踪。

核心流程不要求安装飞书或 Obsidian。使用飞书群输入时，才需要 bot 已加入目标群并具备 `im:message`、`im:message.group_msg` 和 `im:resource` 权限。

## 处理流程

1. 接收上传材料、读取本地文件，或从已配置的飞书群获取材料。
2. 通过 vision_analyze 和文本解析提取结构化信息。
3. 对缺失或模糊字段向用户确认，不猜测实验条件或结果。
4. 确认输出方式和目标目录，生成实验 ID 与样品批次 ID。
5. 写出 `{OUTPUT_ROOT}/实验日志/{体系}/{类型}/{exp_id}.md`。
6. 将原始附件归档到 `{OUTPUT_ROOT}/raw/experiments/YYYY.MM.DD_描述_EXPID/`，并在日志中建立引用。
7. 如启用索引模板，更新实验索引；发现异常时追加异常记录。
8. 告知用户生成文件及原始材料的具体位置。

模糊信息（温度记不清、样品编号不明）主动询问，不猜测写入。

## 目录结构

```
/vault/
├── raw/experiments/                       ← 原始层（归档）
│   └── YYYY.MM.DD_描述_EXPID/
│       ├── 笔记.md
│       ├── 图片/
│       └── 语音/
│
wiki/实验日志/                              ← 标准层（产出）
├── 实验索引.md
├── 异常记录.md
├── {体系A}/
│   ├── 实验类型1/
│   ├── 实验类型2/
│   └── ...
├── {体系B}/
│   └── ...
└── 公共/
    └── 设备与试剂追踪.md
```

## 实验 ID 规则

```
{体系代码}-{设备代码}-YYMMDD-{序号}
  │        │       │       └─ 当日序号（001 起）
  │        │       └─ 日期
  │        └─ 设备代码（M=马弗炉, T=管式炉, E=电化学, G=手套箱, F=可控气氛炉, B=通用）
  └─ 体系代码（自定义，如 CL / NO / OX / HY 等）
```

## 样品批次 ID 规则

```
{体系代码}-{候选编号}-B{序号}
  │        │         └─ 配盐批次序号
  │        └─ 候选配方编号
  └─ 体系代码
```

同一批样品跨多个实验时 `sample_batch` 保持一致，便于 dataview 追踪。

## 设备代码

| 代码 | 设备 | 场景 |
|------|------|------|
| M | 马弗炉 | 热处理、浸泡腐蚀 |
| T | 管式炉 | 气氛控制、脱水、热稳定性 |
| E | 电化学工作站 | CV/SWV/EIS |
| G | 手套箱 | 配盐、称量、取样 |
| F | 可控气氛炉 | 精密气氛控制 |
| B | 通用 | 干燥、清洗、制样 |

按实际设备扩展。

## 可选的 Obsidian 集成

本 skill 可以只向普通本地文件夹输出 Markdown，也可以与 [Obsidian](https://obsidian.md) vault 配合使用。Obsidian 是一个基于本地 Markdown 文件的笔记系统，配合 [Dataview](https://github.com/blacksmithgu/obsidian-dataview) 插件可实现实验数据的动态查询和仪表盘。

**为什么用 Obsidian：**
- 所有日志为纯文本 Markdown，可版本控制、可全文搜索
- YAML frontmatter 结构使 dataview 可自动生成实验列表、异常汇总、设备使用记录
- 本地存储，无云依赖性，数据安全

**安装 skill 后需在 vault 中创建以下文件：**

| 文件 | 模板 | 用途 |
|------|------|------|
| `实验日志/实验索引.md` | `templates/experiment-index.md` | Dataview 查询仪表盘 |
| `实验日志/异常记录.md` | `templates/anomaly-log.md` | 异常记录 |
| `实验日志/公共/设备与试剂追踪.md` | `templates/equipment-tracking.md` | 设备与试剂追踪 |

将模板文件复制到你的 Obsidian vault 对应位置即可使用。

## 参考示例

`references/` 目录包含三个完整的实验日志示例，覆盖常见实验类型：

| 文件 | 实验类型 |
|------|---------|
| `references/example-log.md` | 材料腐蚀浸泡实验 |
| `references/example-electrochemical.md` | 电化学表征（CV 窗口测试） |
| `references/example-thermal-stability.md` | 热稳定性实验 |

每个示例均包含完整的 YAML frontmatter 和 Markdown 正文，可直接作为模板修改使用。

## 可选的飞书 CLI 集成

需要从飞书群获取材料时，使用 `feishu-cli-integration` skill：

- 拉消息：`lark-cli im +chat-messages-list --chat-id oc_*** --page-size 30 --sort asc`
- 下载图片：`lark-cli im +messages-resources-download --message-id *** --file-key *** --type image --output <相对路径>`
- ⚠️ `--output` 只接受相对路径，先 `cd` 到 `raw/experiments/` 归档目录

群 ID 和 bot 权限按 `feishu-cli-integration` skill 的配置获取。

## 自定义指南

- **体系代码**：按你的实验体系自定义（如 CL/NO/OR/PO）
- **实验类型**：在 `wiki/实验日志/{体系}/` 下按需创建子目录
- **YAML 字段**：模板是建议结构，可增删字段
- **设备代码**：按实际实验室设备扩展
- **输出根目录**：可以是普通本地文件夹，也可以是 Obsidian vault 根目录

## 相关文件

| 文件 | 用途 |
|------|------|
| `references/example-log.md` | 完整实验日志示例 |
| `wiki/实验日志/实验索引.md` | Dataview 仪表盘 |
| `wiki/实验日志/异常记录.md` | 异常记录格式 |
| `wiki/实验日志/公共/设备与试剂追踪.md` | 设备、试剂追踪 |
