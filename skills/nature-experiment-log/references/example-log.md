# 实验日志示例

以下是一个材料腐蚀浸泡实验的完整日志示例。所有数据均为虚构，仅展示格式和填写规范。

---

```yaml
---
exp_id: CL-M-260529-001
date: 2026-05-29
salt_system: 氯盐
salt_batch: CL-Q1-B001
salt_composition: "Q1 (*** mol%)"
exp_type: 腐蚀验证
furnace: 马弗炉_1号
crucible: AL-001
total_salt_mass_g: 50.0
temperature_profile: "RT→300°C(2h,干燥)→500°C(300h)→炉冷"
atmosphere: Ar
material: 316L
material_category: 奥氏体不锈钢
sample_id: 316L-2026-001
sample_dimensions_mm: "20×10×2"
sample_surface: "SiC 1200目"
pre_mass_g: 3.4521
post_mass_g: 3.4489
mass_loss_g: 0.0032
corrosion_rate_um_year: ***
anomaly: false
anomaly_ref:
tags: [氯盐, 腐蚀验证, 316L, Q1]
---

# 实验目的

验证候选配方 Q1 在 500°C 下对 316L 奥氏体不锈钢的腐蚀行为，作为四元氯盐体系筛选的基线实验。

# 实验步骤

1. 配制 Q1 盐 50.0g，手套箱中混合均匀
2. 316L 样品 SiC 1200 目打磨，丙酮超声清洗，干燥称重
3. 马弗炉 Ar 气氛下 300°C 干燥 2h（去除吸附水）
4. 升温至 500°C，恒温 300h
5. 炉冷至室温，取出样品
6. 去离子水超声清洗，干燥称重
7. 计算失重和腐蚀速率

# 观察

- 盐冷却后呈浅黄色透明玻璃态，无明显分层
- 样品表面失去金属光泽，呈均匀暗灰色
- 坩埚内壁无可见腐蚀痕迹
- 未观察到异常气体释放或飞溅

# 结果

- 样品质量损失：0.0032 g（0.09%）
- 表面无明显局部腐蚀或点蚀
- 待 XRD 和 SEM-EDS 确认腐蚀产物组成

# 异常

无。

# 下一步

- SEM-EDS 截面分析确认腐蚀层结构和 Cr 贫化
- XRD 确认腐蚀产物相组成
- 与 Q2、Q3 候选配方平行实验对比

---

# 原始材料

原始图片和语音记录归档于：
`raw/experiments/2026.05.29_Q1腐蚀验证_316L_CL-M-260529-001/`

- `图片/IMG_5291.jpg` — 腐蚀前样品表面
- `图片/IMG_5292.jpg` — 腐蚀后样品表面
- `图片/IMG_5293.jpg` — 盐冷却后坩埚内部
