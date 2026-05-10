# Validation Report: Universal Research Statistics Analysis Skill v1.0.0

## Summary

The v1.0.0 package was validated with multiple simulated general research datasets, including:

1. independent three-group experimental data,
2. repeated pre/post measurements,
3. factorial design with baseline/final variables and GLM-compatible outcomes.

## Validation checks

- CLI execution completed successfully for all scenarios.
- Required outputs were generated: `analysis_results.xlsx`, `three_line_tables.docx`, `methods_results.docx`.
- Optional PNG/PDF figures were generated when `--make-figures` was enabled.
- Word three-line tables were rendered to PNG for layout QA.
- Pytest smoke test passed.
- The default output policy was checked: p-value only, no q-value/FDR q-value by default.

## Scientific policy confirmed

- Small or invalid modules are skipped and recorded.
- Group labels containing letters and numbers are protected from erroneous numeric conversion.
- Ordinal/score outcomes are routed to non-parametric summaries/tests.
- Multi-group Word tables include compact letter display; detailed post hoc sheets are generated only when requested.

## Limitations

This validation confirms software behavior under simulated datasets. It does not validate any scientific conclusion from real data. Real studies require checking study design, measurement units, missingness, independence, and preregistered analysis plans when applicable.
