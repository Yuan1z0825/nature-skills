# tools / 可选脚本

## Contents

- [国知局公布公告检索（epub.cnipa.gov.cn，Step 5 查新优先）](#国知局公布公告检索epubcnipagovcnstep-5-查新优先)
- [Office 文档（Word / PPT）转成可扫描文本](#office-文档word-ppt转成可扫描文本)
- [mermaid_render.py — mermaid：图示 → PNG + 定稿 Markdown + 默认生成 Word](#mermaid_renderpy-mermaid图示-png-定稿-markdown-默认生成-word)
- [math_render.py — LaTeX 公式 → PNG](#math_renderpy-latex-公式-png)
- [md_to_docx.py — Markdown → Word](#md_to_docxpy-markdown-word)
- [iteration_dialog_log.py — 修订对话记录（迭代用）](#iteration_dialog_logpy-修订对话记录迭代用)
- [docx_to_md.py — Word → Markdown + 抽取图片](#docx_to_mdpy-word-markdown-抽取图片)
- [pptx_to_md.py — PowerPoint → Markdown + 抽取图片](#pptx_to_mdpy-powerpoint-markdown-抽取图片)
- [扩展其它脚本时](#扩展其它脚本时)


本目录存放**可重复执行的辅助脚本**。技能主流程以 `SKILL.md` 与 `references/disclosure/` 为准；本目录侧重格式转换等可执行工具。

## 国知局公布公告检索（epub.cnipa.gov.cn，Step 5 查新优先）

| 脚本 | 作用 |
|------|------|
| **`cnipa_epub_search.py`** | **（Step 5 优先）** 一步：拉取 + 解析，**不写结果页 HTML 落盘**；**Agent 须按 `prior_art_search.md` 分多次调用、每轮一词并自行合并 JSON**；脚本在**单次命令多词**时也会进程内循环检索并合并（人工/本地便利）；**stdout 仅一行** `EPUB_HITS_JSON:`；stderr 上 `EPUB_*` 为 **ASCII**；UTF-8 / PowerShell 见 **references/disclosure/tooling.md**。 |
| **`cnipa_epub_crawler.py`** | 仅 Playwright 拉取并**默认保存**结果页 HTML；stdout 亦含 **`EPUB_HITS_JSON:`**。 |
| **`cnipa_epub_parse.py`** | 仅解析已保存的 HTML：`python scripts/disclosure/cnipa_epub_parse.py path/to/_last_result_xxx.html`；字段含标题、公开号、链接、**`abstract`**（若有）。 |

依赖：`pip install -r scripts/disclosure/requirements-cnipa.txt` 与 `python -m playwright install chromium`。环境变量见各脚本文件头。默认结果 HTML 落在 **`scripts/disclosure/_last_result_*.html`**（已 `.gitignore`）。

抓取失败或解析无命中时，Agent 按 **`references/disclosure/prior_art_search.md`** 降级 **WebSearch**（如 Google 学术 / Google Patents）。

---

## Office 文档（Word / PPT）转成可扫描文本

用本技能 **`docx_to_md.py`**、**`pptx_to_md.py`**（纯 Python + 仓库根目录 `requirements.txt`），见下文各节；与 `SKILL.md`「工具与数据来源」一致。

## mermaid_render.py — mermaid：图示 → PNG + 定稿 Markdown + **默认生成 Word**

将 fenced **mermaid**（`` ```mermaid`` ``）逐块交给 **`mmdc`** 渲染为 PNG；输出 `.md` 中**保留** mermaid 围栏源码，并追加 ``<!-- ![图示 n](mermaid_figures/…) -->`` 供 **`md_to_docx.py`** 嵌入 Word（Word **仅**嵌 PNG，不写 mermaid 代码块）。**3.2 系统框图**与 **3.4 流程图**均用 mermaid（`flowchart` / `subgraph` 等），交底书正文**不再**要求单独的文字框图或 PlantUML。

**生图失败降级**：某一围栏 `mmdc` 失败时**不中断**——该处**保留**原 `` ```mermaid`` … `` ``` `` 源码；其余块照常出图。仍写出定稿 `.md`，并**照常尝试**生成 Word（未出图块在 Word 中为 **Consolas 代码块**，与 `md_to_docx` 行为一致）。

### 依赖：mermaid（须 Node.js + `mmdc`）

| 方式 | 安装 | 说明 |
|------|------|------|
| **本地 npm（推荐）** | **Node.js** + 本目录 `npm install`（见 `package.json`） | 优先使用 `scripts/disclosure/node_modules/.bin/mmdc`，避免每次 npx 拉包 |
| **npx** | 未执行 `npm install` 时由脚本调用 `npx -y @mermaid-js/mermaid-cli mmdc` | 首次可能较慢 |
| **全局 npm** | `npm install -g @mermaid-js/mermaid-cli` | 提供 **PATH** 上的 `mmdc` |

mermaid 脚本按顺序查找：`scripts/disclosure/node_modules/.bin/mmdc` → **PATH** 上的 `mmdc` → `npx`。

生成 Word 仍需：`pip install -r requirements.txt`（与上表无关）。

**npm 推荐（本地 CLI）**：

```bash
cd tools
npm install
```

`package.json` 已包含 **`puppeteer`**（`@mermaid-js/mermaid-cli` 的 peer）。**Puppeteer 23+** 可能不会在 `npm install` 时自动下载浏览器；若自检或 `mmdc` 报错 **Could not find Chrome**，在 **`scripts/disclosure/`** 再执行：

```bash
npx puppeteer browsers install chrome-headless-shell
```

（或按报错提示选用 `chrome` 等；详见 [Puppeteer 文档](https://pptr.dev/)。）

### mermaid CLI 与手动试转

**`mermaid_render.py` 与 11.x 一致**：在 **`mmdc -i <.mmd> -o <.png> -b white`** 基础上默认追加 **`-s 2 -w 1400 -H 1050`**（更高像素密度与视口，系统框图在 Word 中更清晰）。需要再锐化可 **`--mmdc-scale 3`**（PNG 更大）；恢复接近旧版可 **`--mmdc-scale 1 --mmdc-width 800 --mmdc-height 600`**。
若某处写的是 `npx -y @mermaid-js/mermaid-cli -i …`，**少了子命令 `mmdc`**，参数会错位；正确示例：

```bash
npx -y @mermaid-js/mermaid-cli mmdc -i sample.mmd -o sample.png -b white
```

可自建极简 `sample.mmd`（如一行 `flowchart LR; A-->B`）试转；能出 PNG 则说明 **mmdc + Chrome** 正常，否则按上文安装 **`puppeteer` 浏览器**。

### 用法

```bash
# 写出定稿 .md，并在同目录生成同名 .docx（默认）；-o 须为「案件名_YYYYMMDDHHmmss.md」（见 references/disclosure/disclosure_builder.md §7.3 第 5 点）
python3 scripts/disclosure/mermaid_render.py -i draft.md -o "一种XXX方法及系统_20260408143025.md"

# 指定 .docx 路径（.md 主名仍须含时间戳）
python3 scripts/disclosure/mermaid_render.py -i draft.md -o out/一种XXX方法及系统_20260408143025.md --docx out/一种XXX方法及系统_20260408143025.docx

# 仅 Markdown，不要 Word
python3 scripts/disclosure/mermaid_render.py -i draft.md -o "一种XXX方法及系统_20260408143025.md" --no-docx

# 更高清晰度（可选）
python3 scripts/disclosure/mermaid_render.py -i draft.md -o "…定稿.md" --mmdc-scale 3 --mmdc-width 1600 --mmdc-height 1200

# 指定 mermaid 图片子目录（相对输出 .md）
python3 scripts/disclosure/mermaid_render.py -i draft.md -o out/一种XXX方法及系统_20260408143025.md --assets-dir figures/mermaid
```

**Word 生成失败**（缺依赖、版式报错等）时：脚本仍以退出码 **0** 结束（Markdown 已成功）；stderr 会打印 **`md_to_docx.py` 的手动命令**，请复制执行。

Windows 上若仅装 Node 未执行 `npm install`，脚本会通过 `npx -y @mermaid-js/mermaid-cli mmdc` 调用（首次可能较慢）。

### 与交底书约定

- 技能要求定稿**同时**交付 **Markdown + Word**，且 **`-o` 主文件名须含 `_{YYYYMMDDHHmmss}`**（`references/disclosure/disclosure_builder.md` §7.3 第 5 点，含首次定稿）；**3.2 系统框图**与 **3.4 流程图**均用 fenced mermaid，**不要** ASCII 文字流程图或框图。
- 交付代理人前：运行 `mermaid_render.py` 一步即可（默认再调 `md_to_docx.py`）；若 Word 失败，按 stderr 提示手动执行 `md_to_docx.py`。

---

## math_render.py — LaTeX 公式 → PNG

将 Markdown 中的 **LaTeX 公式**（``$...$`` / ``\\(...\\)`` 行内；``$$...$$`` / ``\\[...\\]`` 块级）用 **matplotlib mathtext** 渲染为 PNG；**保留 LaTeX 原文**，图片引用写入 HTML 注释 ``<!-- ![...](math_figures/...) -->``（Markdown 预览不显示图），供 **`md_to_docx.py`** 嵌入 Word。

**Mermaid 框图**：``mermaid_render.py`` **保留** `` ```mermaid`` 源码，并追加 ``<!-- ![图示 n](mermaid_figures/...) -->``（预览隐藏图引用，Word 仍大图嵌入）。

**mathtext 兼容**：渲染前自动将常见 LaTeX 简写映射为 mathtext 符号（如 ``\ge``→``\geq``、``\le``→``\leq``、``\land``→``\wedge``）；块级式内**换行压成一行**、``\tag{1}`` 转为式末 ``(1)``；仍无法解析的公式保留原文。

**失败降级**：某一公式渲染失败时**不中断**——该处**保留原文**（``$...$`` 或 ``$$...$$``）；``md_to_docx`` 对未转换的 ``$$`` 块以 **Consolas 代码块**写入 Word。

**Word 版式**：**全部公式图**（行内与块级式 (1) 等）在 Word 中统一按约 **0.17 英寸**高度嵌入；**mermaid 框图/流程图**仍按 **5.5×8.2 英寸**上限等比嵌入。块级 PNG 默认与行内同字号（10.5pt）渲染，避免块级式显得过粗过大。

### 依赖

```bash
pip install -r requirements.txt   # 含 matplotlib
```

### 用法

```bash
python3 scripts/disclosure/math_render.py -i draft.md -o draft_with_math.md
python3 scripts/disclosure/math_render.py -i draft.md -o out.md --assets-dir math_figures
```

定稿流水线：**``mermaid_render.py`` 默认先跑公式再跑 mermaid**（可用 ``--no-math`` 跳过）。单独转 Word 时 **`md_to_docx.py` 也会自动尝试公式渲染**（``--no-math-render`` 可关闭）。

---

## md_to_docx.py — Markdown → Word

将交底书 Markdown 转为 `.docx`，**`#`–`######` 映射为 Word 内置「标题 1」–「标题 9」**，正文为宋体 10.5pt，代码块为 Consolas，便于交给代理人或所内用 Word 修订。

**图示**：定稿应用 **`mermaid_render.py`** 将 mermaid 转为 PNG；若个别块生图失败被降级保留围栏，本脚本会将**仍存在的** `` ```mermaid`` 块按**代码块**写入 Word。本脚本不调用 `mmdc`。

### 依赖

```bash
pip install -r requirements.txt
```

依赖为 `python-docx`（见仓库根目录 `requirements.txt`）。

### 用法

```bash
python3 scripts/disclosure/md_to_docx.py --input path/to/交底书.md --output path/to/交底书.docx
```

图片 `![](相对路径.png)`：默认相对 **Markdown 文件所在目录**；也可指定根目录：

```bash
python3 scripts/disclosure/md_to_docx.py -i ./outputs/case/disclosure.md -o ./outputs/case/disclosure.docx --base-dir ./outputs/case
```

**插图**：对 PNG/GIF/JPEG 会读取像素尺寸，在默认 **最大宽 5.5" × 最大高 8.2"** 内**等比缩放**并同时指定 `width`/`height`，避免竖长流程图仅按宽度放大后**高度超出版心**、打印或阅读时像被裁切。可按纸张边距调整，例如：

```bash
python3 scripts/disclosure/md_to_docx.py -i a.md -o a.docx --image-max-width-inches 6 --image-max-height-inches 9
```

在技能根目录中使用 `scripts/disclosure/` 路径；在其它工作目录执行时使用该脚本目录的绝对路径。

### 支持的 Markdown 子集

| 元素 | 行为 |
|------|------|
| `#`–`######` | Word 标题 1–9 |
| 段落 | 宋体正文，支持 `**粗体**`、`` `行内代码` ``；**相邻非空行（中间无空行）各自成段**，「（1）…（2）…」会分行显示 |
| `-` / `*` 列表 | 项目符号列表 |
| `1.` 列表 | 编号列表 |
| ` ``` ` 围栏 | 等宽代码块 |
| `\| 表格 \|` | 简单表格（Table Grid）；单元格内 ``\\(...\\)``、``$...$``、``<!-- -->`` 及 ``\\|`` 中的 ``|`` **不会**被当作列分隔符 |
| `> ` | 左缩进引用 |
| `---` 等 | 浅色分隔线 |
| `![](path)` | 嵌入图片（路径需存在；默认宽/高上限内等比缩放；公式图与正文混排） |
| `$` / `\\(...\\)` / `$$` / `\\[...\\]` LaTeX | 默认先 **`math_render`** 转 PNG（注释隐藏引用）；失败则 **原文**写入 Word |

**未完整支持**：复杂嵌套列表、HTML 块、**未预渲染的** mermaid 围栏（仍为代码块）、脚注、任务列表等。定稿前请运行 **`mermaid_render.py`**；若仅用外部工具导出 PNG，可直接写 `![](...)`。

### 版式说明（md_to_docx）

- 不同语言 Word 中「标题 1」显示名可能为「Heading 1」或「标题 1」，样式仍为大纲级别标题，可用导航窗格与目录域。
- 若需所内固定模版（页眉、首页不同），可在本脚本生成后套用单位 `.dotx`，或后续扩展 `python-docx` 打开模版再写入。

---

## iteration_dialog_log.py — 修订对话记录（迭代用）

每轮 **`merger.md` / `correction_handler.md`** 交付后，在**案件目录**追加一条 **`交底书修订对话记录.md`**：含**本地时间与 UTC**、用户说明摘要、本轮交付文件名、合并/纠正摘要摘录。规则见 **`references/disclosure/iteration_context.md`**。

**依赖**：仅标准库。

```bash
python3 scripts/disclosure/iteration_dialog_log.py --case-dir outputs/某案件 --kind merge \
  --user "补充了调度装置资料，合并进第三章" \
  --summary "已扩写 3.4，并更新实施例；未改保护点表述。" \
  --artifacts "一种XXX方法及系统_20260408143025.md,一种XXX方法及系统_20260408143025.docx"
```

- `--kind`：`merge` 或 `correct`。
- `--log-name`：可选，默认 `交底书修订对话记录.md`；英文环境可改用 `disclosure_revision_log.md`。
- 无法执行脚本时，由 Agent 按同结构手工追加。

---

## docx_to_md.py — Word → Markdown + 抽取图片

将 **.docx**（Word / WPS 等另存为 docx）转为 **Markdown**，并把文档内嵌图片落到磁盘，便于 **`Read` 与 Step 2 扫描**（与直接读二进制 .docx 相比更稳）。**Step 2** 对扫描树内**每一个** `.docx` 都应先转换再读产出 `.md`，见 `references/disclosure/project_scan.md`。

### 依赖

与 `md_to_docx` 共用根目录 `requirements.txt`（`python-docx` + **`mammoth`**）。

```bash
pip install -r requirements.txt
```

### 用法

```bash
python3 scripts/disclosure/docx_to_md.py --input path/to/设计说明.docx --output outputs/case/design.md
```

- 默认图片目录：`outputs/case/design_media/`，Markdown 内为相对路径 `![](design_media/img_0001.png)`。
- 自定义图片目录：

```bash
python3 scripts/disclosure/docx_to_md.py -i ./raw/spec.docx -o ./knowledge/spec.md --media-dir ./knowledge/spec_assets
```

转换警告（如部分样式、WMF 图）会输出到 **stderr**，仍可能生成可用 `.md`。

### 局限（mammoth）

- 仅 **`.docx`**（OOXML）；老版 **`.doc`** 不支持。
- **Markdown 输出在 mammoth 侧标记为 deprecated**，复杂排版可能弱于「先导出 HTML 再转 MD」；专利扫描一般足够。若版式崩坏，建议所内 **另存为 PDF 或纯文本** 再扫。
- **WMF/EMF** 等 Windows 图元可能需单独处理（见 [mammoth WMF 配方](https://github.com/mwilliamson/python-mammoth)）。

在技能根目录中使用 `scripts/disclosure/` 路径；在其它工作目录执行时使用该脚本目录的绝对路径。Windows 无 `python3` 时用 `python`。

---

## pptx_to_md.py — PowerPoint → Markdown + 抽取图片

将 **.pptx** / **.ppsx** 按**幻灯片页**导出为 Markdown，并抽取幻灯片中的**嵌入位图**（`PICTURE` 形状），便于 **`Read` 与 Step 2 扫描**。**Step 2** 对扫描树内**每一个** `.pptx` 均应先转换再读 `.md`，见 `references/disclosure/project_scan.md`。

### 依赖

根目录 `requirements.txt` 中的 **`python-pptx`**。

```bash
pip install -r requirements.txt
```

### 用法

```bash
python3 scripts/disclosure/pptx_to_md.py --input path/to/评审材料.pptx --output outputs/case/review.md
```

- 默认图片目录：`outputs/case/review_media/`，文件名形如 `slide03_img0001.png`。
- 自定义图片目录：

```bash
python3 scripts/disclosure/pptx_to_md.py -i ./raw/deck.pptx -o ./knowledge/deck.md --media-dir ./knowledge/deck_media
```

每页输出二级标题 `## 第 N 页`，其后为该页形状中的**文本与表格**（简化为管道表）及图片引用；若存在**演讲者备注**，以「**备注**」小节附于该页末尾。

### 局限（python-pptx）

- 仅 **`.pptx` / `.ppsx`**（OOXML）；**`.ppt`** 不支持，请先另存。
- **图表、SmartArt、嵌入 OLE** 等若未以普通图片形状存在，**不会**自动栅格化为 PNG；可先在 PowerPoint 中另存为图片或导出 PDF 作补充材料。
- 文本按形状遍历顺序输出，与视觉阅读顺序可能略有差异。

在技能根目录中使用 `scripts/disclosure/` 路径；在其它工作目录执行时使用该脚本目录的绝对路径。Windows 无 `python3` 时用 `python`。

---

## 扩展其它脚本时

- Word / PPT 转换依赖写在 `requirements.txt`。
- 在 `SKILL.md`「工具与数据来源」表中增加一行调用说明。
- 勿将密钥写入仓库；配置使用环境变量或用户主目录。
