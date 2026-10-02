# 实验日志示例：电化学测试

以下是一个电化学表征实验的完整日志示例。所有数据均为虚构。

---

```yaml
---
exp_id: OX-E-260615-001
date: 2026-06-15
salt_system: 氧化物体系
salt_batch: OX-A1-B001
salt_composition: "*** (*** wt%)"
exp_type: 电化学
test_method: CV
working_electrode: Pt丝
counter_electrode: Pt网
reference_electrode: "Ag/Ag+ 准参比"
temperature: 500
atmosphere: Ar
potential_window_V: "-1.5 ~ +1.0"
scan_rate_mV_s: 50
evaluation_target: "检测体系电化学窗口及杂质氧化还原峰"
anomaly: false
anomaly_ref:
tags: [电化学, CV, 窗口测试]
---

# 实验目的

测定候选配方 A1 在 500°C 下的电化学窗口，确认是否适合后续腐蚀实验。同时检测是否存在杂质氧化还原峰。

# 实验步骤

1. 手套箱中配制 A1 盐 30g，转入刚玉坩埚
2. 马弗炉 300°C 干燥 2h（去除吸附水）
3. 转移至电化学测试台，Ar 气氛下升温至 500°C
4. 三电极体系：Pt 丝工作电极、Pt 网对电极、Ag/Ag+ 准参比
5. CV 扫描：-1.5V 至 +1.0V，扫速 50 mV/s
6. 记录 3 圈，取第 3 圈为稳态数据

# 观察

- 盐熔化后呈透明液体，无明显悬浮物
- CV 曲线在 -0.8V 和 +0.6V 处出现小峰（疑似杂质）
- 电极表面无可见腐蚀

# 结果

- 电化学窗口约 2.5V（-1.5 至 +1.0V），适合后续腐蚀实验
- 需进一步 EIS 确认体系稳定性
- 杂质峰需通过标准加入法确认来源

# 异常

无。

# 下一步

- EIS 长时间稳定性测试（100h）
- 标准加入法标定杂质峰对应的化学物种
- 与 A2、A3 候选配方对比窗口宽度

---

# 原始材料

原始图片和语音记录归档于：
`raw/experiments/2026.06.15_A1电化学窗口测试_OX-E-260615-001/`

- `图片/IMG_6151.jpg` — 三电极测试台布置
- `图片/IMG_6152.jpg` — CV 曲线截图
