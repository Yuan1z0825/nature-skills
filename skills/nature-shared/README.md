# `nature-shared/` - nature-* 技能的共享支持包

这个目录是一个可安装但不应单独触发的支持包。它保存多个 `nature-*` 技能共同依赖的公共定义与参考材料，避免在不同技能目录中重复维护同一套内容。安装整套技能时，它会与其他技能一起被发现和更新。

同级技能会通过 `manifest.yaml` 中的相对路径引用这里的文件，例如：

```yaml
always_load:
  - ../nature-shared/core/reader-workflow.md
```

## 当前内容

| 文件 | 使用方 |
|---|---|
| `core/reader-workflow.md` | `nature-polishing`, `nature-writing` |
| `core/paper-type-taxonomy.md` | `nature-polishing`, `nature-writing` |
| `core/ethics.md` | `nature-polishing`, `nature-writing` |
| `core/research-compliance.md` | `nature-writing` 及需要 Nature Portfolio 专项合规检查的技能 |
| `core/terminology-ledger.md` | `nature-polishing`, `nature-writing`, `nature-reader`, `nature-paper2ppt` |
| `core/consistency-sweep.md` | `nature-polishing`, `nature-reviewer`, `nature-response`, `nature-statistics` |
| `core/main-text-discipline.md` | `nature-writing`, `nature-polishing`, `nature-response` |
| `journal-formats/nat-comms.md` | `nature-polishing`, `nature-writing` |
| `journal-formats/nature.md` | `nature-writing` 及需要旗舰 `Nature Article` 精确投稿规则的技能 |
| `journal-formats/nature-machine-intelligence.md` | NMI 投稿的写作、润色、图表、数据与统计工作流 |

`scripts/check_consistency.py` 为一致性扫描提供机械初筛，可报告术语变体、同值不同精度和等值长度单位混用。输出是待人工核对的风险提示，不会自动改稿。

## 什么时候把文件放到这里

只有当**两个或更多技能**需要复用同一份内容时，才把文件放入 `nature-shared/`。如果内容只服务于一个技能，应保留在该技能自己的 `static/` 或 `references/` 目录中。

## 什么时候保持技能内局部内容

共享层只放**定义和参考材料**，例如论文类型分类、读者工作流、伦理规则或术语表。具体技能如何诊断、起草、修改或输出结果，仍应保留在各自的 `static/fragments/` 中。多个技能可以复用同一套论文类型分类，但在其上执行不同的任务逻辑。

## 与其它技能的关系

`nature-shared/` 不是独立工作流，而是被其他 `nature-*` 技能按需读取的公共依赖包。
