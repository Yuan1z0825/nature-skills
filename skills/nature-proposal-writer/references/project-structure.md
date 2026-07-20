# Project structure

Default working directory:

```text
<outputs>/researchwrite/<project-slug>/
```

Archive only with approval:

```text
<archive-root>/researchwrite/<project-slug>/
```

Do not write to any external archive, vault, or synced folder unless explicitly requested.

## Files

```text
00_scope.md
01_research_canon.md
02_evidence_table.md
03_argument_map.md
04_section_contracts.md
05_style_guide.md
state.json

sources/
  user_materials/
  literature/
  data/

drafts/
  proposal_v0.md
  proposal_v1.md
  sections/

revision_briefs/
qa_logs/
exports/
```

## state.json minimum

```json
{
  "project": "",
  "mode": "compose|revise|hybrid",
  "text_type": "doctoral_proposal",
  "language": "zh|en|mixed",
  "target_reader": "",
  "current_round": 0,
  "scores": [],
  "technical_debts": [],
  "status": "intake|foundation|drafting|revision|export"
}
```
