# 实验日志示例：热稳定性测试

以下是一个热稳定性实验的完整日志示例。所有数据均为虚构。

---

```yaml
---
exp_id: HY-T-260601-001
date: 2026-06-01
salt_system: 混合盐体系
salt_batch: HY-B1-B001
salt_composition: "*** (*** wt%)"
exp_type: 热稳定性
furnace: 管式炉_1号
crucible: AL-005
total_salt_mass_g: 40.0
temperature_profile: "RT→200°C(4h,脱水)→500°C(8h)→700°C(2h)→炉冷"
atmosphere: "Ar (100 mL/min)"
condensate: "收集到 2.3g 无色液体"
absorption_solution: "0.1M NaOH 50mL"
anomaly: false
anomaly_ref:
tags: [热稳定性, 管式炉, Ar气氛]
---

# 实验目的

评估候选配方 B1 在 Ar 保护气氛下的热稳定性，确定高温段质量损失和分解产物。

# 实验步骤

1. 手套箱中配制 B1 盐 40.0g，转入刚玉坩埚
2. 管式炉 Ar 气氛（100 mL/min），200°C 干燥 4h（去除吸附水）
3. 升温至 500°C 恒温 8h，再升温至 700°C 恒温 2h
4. 出气口接冷凝管 + NaOH 吸收瓶
5. 各温度段取样记录，炉冷后称重

# 观察

- 200°C 段无明显变化
- 500°C 段冷凝管收集到 ~2.3g 无色液体（可能是结晶水或低沸点组分）
- 700°C 段盐颜色由白色变为浅黄，但未见明显分解
- 冷凝液 pH 约 6（弱酸性）

# 结果

- 总质量损失：11.5%（以原始质量计）
- 主要失重发生在 200-500°C 段（脱水），500-700°C 段失重仅 1.2%
- 残余盐 ICP-OES 分析显示组分比例无明显变化
- 热稳定性合格

# 异常

无。

# 下一步

- 对比 B2、B3 候选配方的热稳定性
- 延长 700°C 恒温时间至 24h 验证长期稳定性
- Karl Fischer 滴定定量残余水分

---

# 原始材料

`raw/experiments/2026.06.01_B1热稳定性_HY-T-260601-001/`
