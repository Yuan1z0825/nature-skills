---
name: nature-ref-verifier
description: >-
  对学术文献逐条执行多源交叉验证，逐字段对比作者、标题、年份、卷期、页码，
  标记卷年/DOI年冲突、作者顺序异常、页码偏差等问题，输出结构化验证报告。
  可批量处理整篇论文/开题报告的参考文献列表，也可单条校验，支持与 Zotero 同步修正。
---

# nature-ref-verifier — 学术参考文献多源验证技能

## 触发词

`verify references`、`校验文献`、`check references`、`核对参考文献`、`文献验证`、`ref check`

## 适用场景

- 开题报告/论文提交前，对全部参考文献做最终核查
- 收到审稿意见指出引用错误时，精准定位问题
- 从旧项目迁移参考文献到新论文时，批量验证有效性
- Zotero 库定期健康检查

## 工作流

### Step 1: 解析输入

支持三种输入格式：

**A. 整篇论文/开题报告**
- 提取所有 `[N]` 编号的参考文献列表
- 自动识别每条的 DOI（如有）

**B. 单条参考文献**
- 用户直接粘贴一条引用文本
- 或传入 Zotero item key

**C. BibTeX 文件**
- 直接解析 `.bib`，逐条校验

### Step 2: 多源并行查询

**Step 2.0（最便宜、最先做）：DOI 可解析性检查。** 对每条有 DOI 的文献先请求 `https://api.crossref.org/works/<DOI>`：404 → DOI 本身错误（高度疑似错号）；200 → 比对返回记录的标题/作者/卷期页与条目，不一致即"DOI 张冠李戴"。单次请求即可发现实践中最常见的一类错误（一次 35 条核查中 7/9 的错误属于此类）。

对每条文献，并行查询以下来源（可用哪些取决于环境配置）：

| 来源 | 适用文献 | 典型覆盖率 |
|------|---------|-----------|
| **Crossref** | 有 DOI 的外文期刊 | ~70%（IEEE 老文献、中文期刊常有缺失）|
| **IEEE Xplore** | IEEE 期刊/会议 | IEEE DOI 404 时的备选 |
| **WebSearch (Bing/Google)** | 无 DOI 或来源缺失的文献 | 兜底方案 |
| **CNKI/万方** (kimi-datasource / webbridge) | 中文期刊、学位论文 | 中文文献必查 |
| **Zotero 本地库** (zotero-mcp) | 已入库文献 | 快速比对已有数据 |

**查询策略：** 优先用 DOI 查 Crossref，失败后降级用标题+作者搜 Web。

**批量策略：** 超过 20 条时按 10–15 条一组拆给并行子代理，每组独立查询后汇总——35 条规模实测 3 个并行子代理即可在一次往返内完成，串行会慢一个数量级。

### Step 3: 字段级对比

对每条文献执行以下对比矩阵，按严重程度分为三级：

#### 🔴 Critical（必须修正）

| 检查项 | 说明 | 典型案例 |
|--------|------|---------|
| 作者**姓名/顺序**不一致 | 第一作者不同、顺序颠倒、完全编造 | Smogavec→Leckebusch、Vainikainen→Mikhnev |
| 作者**漏人** | 条目作者数少于出版方记录（常见于 5+ 作者文献只录前 3-4 人） | TGRS 2019 PCA 文漏第 5 作者 Ge；TAES 2021 UAV 文漏第 5 作者 Kim |
| **页码**差异 ≥5 | 页码完全不匹配 | Noon: 1309-1319→1444-1449 |
| **文章号字母误判** | 文章号含字母被写成形近数字（T/7、l/1、O/0） | SPIE 101880T 误作 1018807 |
| **标题核心词**不一致 | 非大小写/标点差异 | Iwasaki T→Wu K H、Zhang W→Zhu M H |
| DOI 指向不同论文 | DOI 存在但标题/作者不对应 | Abidi 1995: 10.1109/4.482157→10.1109/4.482187 |
| DOI 张冠李戴 | DOI 可解析但解析到**另一篇**论文（比对标题作者即可发现） | JAG 2017 SVD 文 DOI 指向同卷 ERT 论文；AST 2022 旋翼文 DOI 指向涡轮噪声论文 |

#### 🟡 Warning（建议核对）

| 检查项 | 说明 | 典型案例 |
|--------|------|---------|
| **卷年** ≠ DOI 年 | 卷归属年份与 DOI 编号年不一致 | Dadrass 卷2025/上线2024、Ni 卷2022/DOI含2020 |
| **Early Access 元数据漂移** | IEEE 等期刊 Early Access 转正式出版后卷/期/页/年会变化，**以 CrossRef 现值为准** | TGRS autoencoder 文 59(12):10437-10449,2021 → 60:1-13,2022 |
| 作者**中间名缺失/多余** | "Rabiner L" vs "Rabiner L R" | 一般不影响检索 |
| **期号**缺失 | 脚本有卷无期 | Smogavec 2025: 17→17(10) |
| 页码偏差 ≤4 | 细微差异 | Leckebusch 15-24→15-25 |
| 出版社名写法差异 | "IET" vs "IEE" | 历史名称变更 |

#### 🟢 Info（仅供参考）

| 检查项 | 说明 |
|--------|------|
| 标题大小写不同 | Title Case vs Sentence case |
| 期刊名缩写 vs 全称 | "IEEE Trans. AES" vs "IEEE Transactions on Aerospace and Electronic Systems" |
| 标点/连接词差异 | "and" vs "&" 等 |

### Step 4: 置信度评估

每条文献最终给出一个综合置信度：

| 等级 | 含义 |
|------|------|
| ✅ **Verified** | 多源一致，无需修改 |
| ⚠️ **Check suggested** | 存在 🟡 级差异，需人工判断 |
| ❌ **Needs fix** | 存在 🔴 级差异，必须更正 |
| ❓ **Unverifiable** | 所有来源均无法查到（如内部报告、老旧学位论文）|

### Step 5: 输出报告

支持以下输出格式：

**Markdown 摘要报告：**
```markdown
## 验证结果：56 条文献

- ✅ Verified: 42
- ⚠️ Check suggested: 8
- ❌ Needs fix: 4
- ❓ Unverifiable: 2

### ❌ 必须修正
| # | 问题 | 当前值 | 正确值 | 来源 |
|---|------|--------|--------|------|
| [6] | 作者错误 | Smogavec P | Leckebusch J | Wiley |
| [42] | 作者顺序颠倒 | Vainikainen P… | Mikhnev V A… | IEEE |

### ⚠️ 建议核对
| # | 问题 | 详情 |
|---|------|------|
| [18] | 卷年/DOI年不一致 | 卷年2025，DOI年2024 |
```

**BibTeX Patch：** 直接生成修正后的 `.bib` 文件内容。

**Zotero 更新指令：** 生成修正指令列表，用于批量修正 Zotero 库。注意写入路径的限制（2026 年实测）：

- **Zotero 7 本地 HTTP API（localhost:23119）只读**——写操作返回 501，zotero-mcp 类集成不稳定多源于此层包装或 Zotero 繁忙，直连 curl 加 `--max-time` 探测即可判断；
- **批量写入首选 pyzotero Web 模式**（需 userID + API key，全功能 CRUD，自带 429 退避）；
- 无 key 时可用本地 `/connector/saveItems` 端点**新增**条目（不能改已有条目）；
- 直接改 `zotero.sqlite` 仅在 Zotero 关闭后可行，且需手工维护多表关联与版本号，**仅作最后手段**；
- 修正前先确认条目在库：按标题检索为空则说明 bib 另有来源（如文献管理 CSV），Zotero 侧无需修正。

## 多来源交叉验证策略

```text
                   ┌─────────────┐
                   │  用户输入    │
                   │  DOI/标题   │
                   └──────┬──────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  字段拆分    │
                   │ author/title │
                   │ year/vol/pg │
                   └──────┬──────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ CrossRef │   │  IEEE   │   │ WebSearch│
    │  (DOI)  │   │ Xplore  │   │ (Bing/GG)│
    └────┬─────┘   └────┬─────┘   └────┬─────┘
         │              │              │
         ▼              ▼              ▼
    ┌──────────────────────────────────────┐
    │       字段级对比 + 差异评级          │
    │  author / title / year / vol / issue │
    │       pages / DOI / journal          │
    └────────────────┬─────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  置信度评估     │
            │ ✅ ⚠️ ❌ ❓    │
            └────────────────┘
```

## 已知局限与应对

| 局限 | 应对 |
|------|------|
| **中文 DOI 不在 Crossref 中** | 降级到 CNKI/万方（通过 webbridge 或 WebSearch）|
| **IEEE 老文献 DOI 返回 404** | 用 IEEE Xplore 直接搜（其 DOI 不在 Crossref 注册）|
| **学位论文无 DOI** | 用 CNKI / 万方 / ProQuest 验证标题+作者+年份 |
| **产品手册/专利** | 不验证元数据，只确认来源可访问 |
| **谷歌学术搜不到部分文献** | 切换搜索引擎（Bing、百度学术、Semantic Scholar）|

## 环境依赖

以下工具为可选，有则启用、无则降级：

- `pyzotero[cli]`：推荐的 Zotero 读写通道（本地只读 + Web 读写双模式，CLI 可直接被 agent 以 Bash 调用，无常驻进程）
- `zotero-cli` / `zotero-mcp`：Zotero 库读写（本地包装层，实测稳定性较差）
- `kimi-datasource`（scholar）：学术搜索
- `kimi-webbridge`：带登录态的 CNKI 查询
- 基础 WebSearch / FetchURL：通用兜底
