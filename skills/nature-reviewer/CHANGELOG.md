# nature-reviewer Changelog

## 1.5.0 - 2026-09-27

This release adds a mandatory forensic consistency audit to the reviewer workflow. The audit supplements the three mutually blind reviewer reports and does not replace or modify them.

### Added

- New reference: `references/forensic-consistency-audit.md`.
- New post-review audit stage that runs only after every reviewer report is frozen and before synthesis.
- Audit coverage for arithmetic identities, totals, percentages, deltas, ranges, precision consistency, and subgroup reconciliation.
- Audit coverage for metric bounds and identities under the stated aggregation level.
- Audit coverage for pixel, tile, image, region, event, cluster, macro, and paired-unit definitions.
- Audit coverage for prose-table and prose-figure contradictions, including ranking, superlative, and every-threshold claims.
- Audit coverage for duplicate rows, identical intervals, suspiciously repeated outputs, dispersion anomalies, and influential groups.
- Audit coverage for training, validation, test, continuation, placebo, support, query, and exclusion provenance.
- Audit coverage for spatial, temporal, hierarchical, target, and subject leakage.
- Reproducibility gate requiring existing headline numbers to reproduce before new experiments are used to support a paper.
- New evidence-status vocabulary:
  - `confirmed_internal_error`
  - `aggregation_ambiguity`
  - `provenance_gap`
  - `suspected_duplication`
  - `unresolved_input_needed`
  - `not_assessable`
  - `passed`
- New synthesis field: `Forensic consistency findings`.
- New QA section: `Forensic consistency checks`.
- New regression test: `test_forensic_consistency_audit_is_required_after_freezing`.

### Changed

- `SKILL.md` workflow now inserts the forensic audit between report freezing and synthesis.
- `manifest.yaml` version updated from `1.4.0` to `1.5.0`.
- `manifest.yaml` now routes to the forensic audit reference when arithmetic, aggregation, provenance, leakage, or reproduction checks are required.
- `references/reviewer-workflow.md` now defines the audit as a separate editorial pass and keeps audit findings separate from reviewer consensus.
- `references/qa-checklist.md` now blocks release when a confirmed central arithmetic, bounds, aggregation, provenance, or reproduction contradiction is omitted.
- `README.md` and `README_EN.md` now document the new audit capability.
- Audit findings are never fed back into reviewer contexts, and frozen reviewer reports are never edited after comparison.

### Preserved

- Three mutually blind reviewer reports remain the default.
- Report freezing occurs before comparison.
- Reviewer-local concern IDs remain stable.
- Consensus is still assigned only when at least two reviewers independently identify the same underlying concern.
- Existing reviewer isolation and non-invention rules remain unchanged.
- No new runtime dependency is required.

### Compatibility

The default reviewer count and report structure are unchanged. The main visible addition is the `Forensic consistency findings` subsection in the post-review synthesis. Authors and reviewers may also see audit findings promoted to `Risk / unsupported claims` when they affect a central claim.

### Validation

- Skill validator passed.
- All reviewer instruction contract tests passed.
- No manuscript-specific examples, local paths, or private project content are included.
- The audit was designed not to contaminate reviewer contexts or manufacture consensus.

### 中文摘要

`1.5.0` 主要增加了强制执行的 forensic consistency audit。该检查在三位 reviewer 报告全部冻结后、cross-review synthesis 之前运行，重点检查：

- 算术、百分比、delta、range 和计数一致性；
- metric 数学上下限与聚合层级；
- 正文、表格、图件之间的数值和排序矛盾；
- 重复行、相同区间、离散度异常和高影响组；
- train、validation、test、placebo、support、query 和数据泄漏；
- 新实验前，旧结果是否能够复现。

审计结果不会反馈给 reviewer，也不会修改冻结报告。它只进入 synthesis 和 risk，并与 reviewer consensus 保持分离。
