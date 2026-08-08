# Nature Portfolio research-compliance routing

Use this conditional reference when a manuscript involves regulated research,
specialist reporting forms, sensitive images, structures, samples or materials.
It is a readiness screen, not legal, clinical or ethics-board advice.

## Contents

1. Applicability gate
2. Reporting summaries
3. Human-participant research
4. Animal research
5. Clinical research
6. Image integrity
7. Structures, chemistry and materials
8. Taxonomy and provenance-sensitive samples
9. Audit output
10. Official sources

## 1. Applicability gate

Classify every item as `required`, `not applicable`, or
`AUTHOR_INPUT_NEEDED`. Never infer an approval, consent, registration, permit,
protocol, accession, validation report or exemption.

Open only the relevant blocks below. Do not burden a computational or
theoretical manuscript with unrelated biomedical requirements.

## 2. Reporting summaries

Require the relevant current Nature Portfolio form when the study is:

- life sciences
- behavioural or social sciences
- ecology, evolution or environmental science
- a physical-science Article in a specifically covered area, including solar
  cells or claims of lasing

The form is supplied to editors and reviewers and published with accepted
manuscripts. Advanced form features require Adobe Reader. Treat the form as a
substantive cross-check against Methods, statistics and figure legends, not as
a checkbox exercise.

## 3. Human-participant research

Check that the submitted manuscript states:

- compliance with the Declaration of Helsinki where applicable
- the approving ethics committee's name and reference number
- details of any formally granted exemption and the committee granting it
- that informed consent was obtained from all participants
- consent for publication of identifiable information or images when relevant
- how population categories such as race, ethnicity, sex and gender were
  defined, justified and handled analytically when they are used
- safeguards for vulnerable groups, privacy and sensitive data

Route controlled-access data wording to `nature-data`.

## 4. Animal research

For experiments involving live vertebrates or higher invertebrates, check:

- the corresponding author's confirmation of compliance with relevant rules
- the institutional or licensing committee and relevant approval details
- sex and other animal characteristics that may affect results
- housing and husbandry details where they may influence results
- reporting against ARRIVE 2.0 where applicable
- accepted anaesthesia and euthanasia practice

Flag methods that appear inconsistent with accepted welfare norms rather than
trying to repair the wording.

## 5. Clinical research

### Registration

- register every qualifying prospective clinical trial in an acceptable WHO
  primary registry or ClinicalTrials.gov before enrolment of the first
  participant
- state the trial number clearly in both the abstract and Methods
- treat primary results from an unregistered qualifying trial as a blocking
  issue

### Submission files

Clinical trial reports should include:

- the latest English protocol, signed and dated
- all amendments plus a summary and rationale for changes
- the latest English statistical analysis plan when separate
- machine-readable versions of original documents not written in English
- visible design, analysis and outcome-reporting content even when sensitive
  material is redacted

Confirm that the primary analysis matches the prespecified protocol and SAP.
Explain deviations in Methods. Label unplanned post-hoc or exploratory analyses
in the abstract and manuscript.

### Study-type reporting

Use the current guideline that matches the design, including:

- CONSORT 2025 and relevant extensions for randomized trials
- CONSORT-AI for clinical trials involving AI interventions
- STROBE for observational studies
- PRISMA for systematic reviews and meta-analyses
- STARD or REMARK for diagnostic/prognostic biomarker studies
- TRIPOD or TRIPOD-AI for prediction models
- TARGET for observational target-trial emulation
- CARE or the applicable N-of-1 CONSORT extension for case reports/series
- BRISQ Tier 1 characteristics for human biospecimens when relevant

Do not provide clinical-statistical advice beyond manuscript reporting checks
without the protocol and SAP.

## 6. Image integrity

At review and revision, verify that:

- submitted images are minimally processed and faithfully represent originals
- unprocessed data and metadata are retained and can be supplied on request
- acquisition tools, software, settings and processing are described in Methods
- images gathered at different times or locations are not combined without
  disclosure and clear boundaries
- cloning, healing or tools that obscure manipulation are not used
- brightness and contrast changes are global, applied equally to controls and
  do not remove data
- pseudocolour, nonlinear/gamma changes and channel-specific adjustments are
  disclosed

For gels and blots, record lane rearrangement, loading controls, crop boundaries,
parallel processing and duplication checks. Accepted life-science papers require
unprocessed original gel and western-blot images for Supplementary Information.

## 7. Structures, chemistry and materials

### Small-molecule crystallography

Require at submission when applicable:

- a standard `.cif` file
- a structural figure with probability ellipsoids for Supplementary Information
- structure factors for every structure
- IUCr CheckCIF validation output as a PDF
- explanations for all A- or B-level alerts

### Other structures and materials

- obtain official wwPDB validation reports for macromolecular structures when
  required for peer review
- deposit electron-microscopy density maps and coordinate data in the required
  repositories
- identify individual organic and inorganic compounds in order of first
  appearance with logical bold numerals; do not number standard buffers,
  reagents or solvents
- for new compounds central to the conclusions, provide structure, synthesis
  and characterization in enough detail for reproduction
- use RRIDs or other persistent identifiers for key biological resources where
  available
- report cell-line source, authentication and distribution restrictions

## 8. Taxonomy and provenance-sensitive samples

- new or revised formal animal taxonomy may require registration and LSIDs from
  ZooBank
- geological, archaeological and palaeontological samples need transparent
  provenance, permits and compliance with local laws
- palaeontological and type specimens should be deposited in a recognized
  museum or collection with accession codes where applicable
- flag protected-site materials without documented permission

## 9. Audit output

Return a compact table:

| Requirement | Applies? | Evidence in manuscript/files | Status | Required action |
|---|---|---|---|---|

Use `blocked` for missing registration, approval, consent, essential protocol,
mandatory repository deposit, validation report or unavailable original data.
Use `AUTHOR_INPUT_NEEDED` when applicability or administrative facts are not
known.

## 10. Official sources

Verified 2026-08-08:

- Research ethics: <https://www.nature.com/nature-portfolio/editorial-policies/ethics-and-biosecurity>
- Clinical research: <https://www.nature.com/nature-portfolio/editorial-policies/clinical-research>
- Reporting and availability: <https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards>
- Image integrity: <https://www.nature.com/nature-portfolio/editorial-policies/image-integrity>
- Nature initial submission: <https://www.nature.com/nature/for-authors/initial-submission>
