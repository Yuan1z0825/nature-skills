# Source basis for `nature-statistics`

This file keeps the skill conservative. It is a local summary of sources the agent should use to justify reporting checks; it is not a replacement for the target journal's current author instructions.

## Primary source hierarchy

1. **Target journal instructions and user-supplied protocol**
   - Use these first when the user provides them.
   - If a reviewer comment or statistical analysis plan gives a stricter requirement, follow that local constraint.

2. **Nature Portfolio reporting standards**
   - Nature Portfolio frames reporting transparency around the ability of readers to replicate and build on published claims.
   - Where relevant, manuscripts sent for review may require completed reporting summary documents.
   - For life sciences, behavioural and social sciences, ecology, evolution and environmental sciences, the reporting summary asks authors to provide details of experimental and analytical design that are often poorly reported.
   - Source: https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards

3. **Nature / Nature Methods statistics guidance**
   - The Nature collection `Statistics for Biologists` groups practical guidance on statistical design, P values, power, sample size, error bars, multiple comparisons, nonparametric tests, experimental design, replication, nested designs, regression, outliers, and correlation versus causation.
   - Treat this collection as practical guidance for common failure modes, not as a single mandatory checklist for every field.
   - Source: https://www.nature.com/collections/qghhqm
   - For a flagship Nature Article, load `nature-article-requirements.md` rather
     than treating this general guidance as the journal's exact checklist.

4. **Study-type reporting guidelines**
   - Use these only when the study type clearly applies or the user requests them.
   - Examples: CONSORT for randomized trials, STROBE for observational studies, PRISMA for systematic reviews, ARRIVE for animal research, and field-specific community standards.

5. **Conservative statistical reporting practice**
   - If no field-specific rule is available, require enough information for a reader to identify the design, analysis unit, test/model, assumptions, correction strategy, sample size, uncertainty, and software.

## Implementation boundaries

The skill should not pretend that Nature has one universal statistical recipe. It should instead enforce transparent reporting and identify risks that reviewers commonly challenge.

Use careful language:

- Prefer: `The manuscript should define the independent experimental unit.`
- Avoid: `Nature requires this exact test.` unless the journal instruction actually says so.

When the user supplies a target journal or reporting summary, ask for or use that document before relying on generic guidance.

## Key reporting principles used by this skill

- Replication depends on the independent experimental unit, not merely the number of measurements.
- Statistical tests are interpretable only relative to the design, assumptions, and data structure.
- P values should not carry the full evidential burden; effect estimates, uncertainty, design quality, and reproducibility matter.
- Multiple testing changes interpretation and usually needs a declared correction or a clearly justified family of planned comparisons.
- Figures should expose the data structure: `n`, error-bar meaning, test/model, correction, and whether points represent independent units or subsamples.
- Missing statistical details should be surfaced as author questions, not silently repaired.
