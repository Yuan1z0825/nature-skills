# `nature-citation` 技能

[English](README_EN.md)

`nature-citation` 用于把论文段落、手稿片段或单条科学判断拆成可引用的 claim，并为每个 claim 寻找 Nature Portfolio、Science family 和 Cell Press 范围内的支撑文献。

## 适合用它做什么

- 给 introduction、discussion 或 reviewer response 中的关键判断补引用。
- 将长段落拆成稳定编号的 claim 单元，例如 `S001`、`S002`。
- 限定只查 Nature、Science、Cell 及其子刊，或只保留旗舰刊。
- 为每个候选文献说明支撑位置、证据强度和插入建议。
- 默认导出可检查的 RIS 文件，并在导出前拦截缺失名字、仅有姓氏或作者列表不完整的记录。
- 通过 DOI 或 PMID 获取结构化作者信息，保留作者顺序、名字/首字母、后缀和团体作者。

## 典型请求

- “把这段 introduction 分段补 Nature 系列引用。”
- “只用 CNS 及子刊，为这些 claim 找近五年的支撑文献。”
- “我已经确认这些 DOI，帮我导出 Zotero 可导入文件。”

## 你需要提供

- 待引用的段落、claim 列表、DOI 清单或 PMID 清单。
- 期刊范围、时间范围、是否允许综述、是否只要旗舰刊。
- 目标引用格式和导出格式，例如 `RIS`、`ENW` 或 Zotero `RDF`。

## 产出

- claim 分段表和候选文献表。
- 每个 claim 的建议插入位置、候选 DOI、期刊、年份和支撑说明。
- 可选的 JSON、TSV、Markdown、HTML 审查材料。
- 可导入文献管理器的引用文件。默认使用 RIS，EndNote 导入时选择 `Reference Manager (RIS)`。

## 边界

- 只把论文作为候选支撑，不会替作者保证其必然适合最终引用。
- 不会使用博客、新闻稿或搜索摘要作为唯一依据。
- 当文献只能支撑相邻但不完全相同的 claim 时，会明确标注证据偏差。

## 相关技能

- `nature-academic-search`：更宽范围的文献搜索和引用指标审计。
- `nature-ref-verifier`：校验已选参考文献的元数据。
- `nature-writing`：把引用选择整合回手稿论证。
