# Literature Gap Analysis Methodology

## When to use

When the user asks to confirm whether a specific research topic has been explored:
- "搜一下 XX 体系有没有人做过"
- "确认这个方向是不是空白"
- "看看这个四元系有没有文献"

## Workflow (4 steps)

### Step 1: Multi-source search

Search the exact topic string across at least 3 sources:
- Web search with exact phrase match (e.g., `"MgCl2-KCl-NaCl-ZnCl2"`)
- Broader search with key components (e.g., `material A material B compound`)
- Adjacent/related terms (e.g., `compound A thermal storage application`)

→ Record hit counts per query.

### Step 2: Decompose and classify

If direct hits = 0, decompose the system into sub-systems:

| Sub-system | Search | Status |
|------------|--------|--------|
| MgCl₂-KCl-NaCl (ternary) | keyword | studied / not studied |
| NaCl-KCl-ZnCl₂ (ternary) | keyword | studied / not studied |
| MgCl₂-KCl-ZnCl₂ (ternary) | keyword | studied / not studied |
| MgCl₂-NaCl-ZnCl₂ (ternary) | keyword | studied / not studied |

Classify hits into three tiers:
- **直接相关**: exact quaternary system → if 0, confirmed gap
- **边缘相关**: contains 2-3 of 4 components → extract key data (method, salt composition, findings)
- **无关**: only 1 component → skip

### Step 3: Extract edge papers

For each 边缘相关 paper, extract:
- Full citation (authors, journal, year, DOI if available)
- Salt composition used
- Method (CV, DSC, XRD, simulation, etc.)
- Key finding relevant to the gap topic
- What can be borrowed for the user's work

### Step 4: Output gap report

Write to `outputs/literature/<topic>_gap_report.md` with these sections:

1. **核心结论** — one sentence: confirmed gap or partial overlap
2. **子体系文献全景** — table per sub-system with representative works
3. **边缘相关文献** — extracted details from edge papers
4. **空白分析** — why nobody did it + why it's worth doing
5. **论文 gap statement 草稿** — English paragraph ready for introduction
6. **建议下一步** — concrete experimental/computational next steps
7. **搜索方法论记录** — all search terms and hit counts (for reproducibility)

### Cost control

- Search: ≤4 parallel web_search calls per decomposition level
- Extract: only edge papers (≤5), not every hit
- No browser: use web_extract, skip paywalled pages silently
- Aim for ≤6 tool calls total
