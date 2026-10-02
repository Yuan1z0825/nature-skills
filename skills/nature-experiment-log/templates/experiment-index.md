# 实验索引

Dataview 查询入口，自动汇总所有实验日志。

```dataview
TABLE date, salt_system, exp_type, material, anomaly
FROM "实验日志"
WHERE exp_id
SORT date DESC
```

## 使用

1. 将此文件放在 vault 的 `实验日志/` 目录下
2. 确保所有日志文件包含 YAML frontmatter（`exp_id`, `date`, `salt_system`, `exp_type` 等字段）
3. Obsidian 打开此文件即可看到交互式实验列表

## 自定义

按你的实验体系调整查询字段。常见扩展：
- 按体系筛选：`WHERE salt_system = "氯盐"`
- 按异常筛选：`WHERE anomaly = true`
- 按日期范围：`WHERE date >= date(2026-01-01)`
