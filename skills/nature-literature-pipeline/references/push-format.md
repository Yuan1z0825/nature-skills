# Feishu Push Format

> Daily literature digest template delivered to the dedicated Feishu group.
> The `{placeholder}` values are filled by the fine-reading stage.

## Template

```markdown
📅 {YYYY-MM-DD} 文献日报 | Research Field Daily

━━━━━━━━━━━━━━━━━━━━

🏅 #{N} | {Title}
{Journal/Source}, {Year} | {Authors} et al. | {Institution} | ⭐ {score}/10 | 分流：{A-E tier}
DOI: {doi if available} | arXiv: {arxiv_id if available}

💡 一句话：{one-line takeaway — why this paper matters or why it is only deferred}

🔬 方法：{experiment/simulation, salt system, temperature, alloy/coating, characterization/electrochemical techniques}

📊 关键结果：{specific data or conclusions, with units and test conditions; no vague summaries}

🧭 点评：{value to the research mainline, limitations, whether worth full-text reading}

📎 {best available link: DOI / arXiv / PDF / repository}

━━━━━━━━━━━━━━━━━━━━

🏅 #{N+1} | ...
```

Daily pushes should NOT include a fixed "与 vault 的关联" field or forced wiki links; that's low-information. Vault/wiki connections belong in archival notes and later manual wiki integration. If a paper clearly hits a tracked author/network, mention it naturally in the commentary.

## Field Guidelines

| Field | Principle |
|-------|-----------|
| 💡 一句话 | 15秒可判断是否值得点开原文。抓核心贡献，不要泛泛描述 |
| 🔬 方法 | 实验/模拟？什么盐体系？什么表征（CV/EIS/SEM/XRD/TEM）？什么合金？ |
| 📊 关键结果 | 必须是具体数据或明确结论。禁止"有重要发现""提供了新的视角"等空泛表述 |
| 🧭 点评 | 说明对研究主线的实际价值、局限、是否值得全文精读；不机械写 vault 关联 |
| ⭐ 评分 | 粗筛综合得分（0-10），帮助判断优先级；内部六维评分仍用 0-100 并校验各维度上限 |

## Example

All papers, identifiers, dates, and numerical results in this example are synthetic.

```markdown
📅 YYYY-MM-DD 文献日报 | Research Field Daily

━━━━━━━━━━━━━━━━━━━━

🏅 #1 | Electrochemical monitoring of impurity X in compound A-B-C system via advanced voltammetry
Electrochimica Acta, 2026 | Zhang, Li, Wang et al. | CAS Institute | ⭐ 9.2/10 | 分流：A_核心主线
DOI: <DOI> | arXiv: <ARXIV_ID>

💡 一句话：First application of method X to system Y for impurity quantification, detection limit improved ~5× over prior art。

🔬 方法：500°C MgCl₂-KCl-NaCl；Pt 工作电极，Ag/AgCl 参比；Ar + 不同 H₂O 分压；SWV 定量 MgOHCl，同时用滴定交叉验证。

📊 关键结果：
  · SWV 检测限 8 ppm O（vs. prior art CV method ~39 ppm）
  · 峰电流与 MgOHCl 浓度线性 R²=0.997（0-200 ppm 范围）
  · 200 h 稳定性测试中峰位漂移 <5 mV

🧭 点评：A 类候选。价值在于把杂质监测灵敏度从 CV 推到 SWV，直接服务监测-控制-验证闭环；需要全文核查参比电极稳定性和标定方法。

📎 https://example.org/paper

━━━━━━━━━━━━━━━━━━━━

🏅 #2 | ...
```

## Delivery

```python
send_message(
    target="feishu:<chat_id>",
    message="<formatted_digest>"
)
```

Use `send_message(action='list')` to discover the chat_id if unknown. The target must be a group the Hermes bot has been added to as a member (Feishu group settings → bots → add).
