# Nature Machine Intelligence submission requirements

Canonical, stage-aware rules for manuscripts submitted to **Nature Machine
Intelligence** (`NMI`; route key `nat-mach-intell`). This file contains the
journal facts. A requesting skill supplies its own drafting, polishing, figure,
data or statistics action layer.

Do not substitute the flagship *Nature* or *Nature Communications* limits.
When an editor gives manuscript-specific instructions, those instructions take
priority over this public-page snapshot.

## Contents

1. Authority and stage gate
2. Editorial scope and article types
3. Article and Analysis contract
4. Other content types
5. Initial-submission package
6. Writing, structure and accessibility
7. Cover letter, review mode and related work
8. Data, code and reporting standards
9. Figures, Extended Data and Supplementary Information
10. Accepted-in-principle production contract
11. Requirements not stated as fixed numbers
12. Official sources

## 1. Authority and stage gate

Record the active stage before applying a rule:

- `initial_submission`: before the first editorial decision. A complete,
  reviewable manuscript is required, but no special house formatting is
  required.
- `revision`: after peer review. Follow the handling editor's instructions in
  addition to the public guide and preserve a point-by-point response record.
- `accepted_in_principle`: supply editable text, production-quality figures,
  final declarations, supporting-information inventory and requested forms.
- `proof`: correct production errors only; do not silently introduce a new
  scientific claim or analysis.

Do not block an initial submission for missing final-production typography,
editable source artwork, final table placement or ORCID linking. Do block or
flag an initial package that lacks required scientific content, a cover letter,
required availability statements, disclosed overlap or review access to data
and central custom code.

## 2. Editorial scope and article types

### Scope fit

The journal considers high-quality original research and reviews across
machine learning, robotics and artificial intelligence, including the broader
scientific, societal and industrial effects of these technologies. It aims to
support dialogue across disciplines, so a technically strong paper still needs
an intelligible question, consequence and audience beyond one narrow benchmark
community.

For an original-research **Article**, verify that the work presents substantial
novel research and a complex, well-supported story. Several techniques or
approaches may be needed, but method count is not a substitute for scientific
importance, validation or scope fit.

### Supported content types

The public content-type guide includes:

- Article
- Analysis
- Review Article
- Perspective
- Correspondence
- Comment
- Reusability Report

Primary research is normally eligible for either subscription publication or
Gold open access. Non-primary content types are not normally eligible for Gold
open access and should not be used to smuggle in new primary findings; only
minimal supporting data are appropriate where the content type permits them.

## 3. Article and Analysis contract

### Article limits

| Item | Current NMI requirement |
|---|---|
| Main text | up to **3,500 words** |
| Excluded from main-text count | abstract, Methods, references and figure legends |
| Abstract | up to **150 words**, unreferenced |
| Display items | up to **6** figures and tables combined |
| References | typically up to **50** |
| Supplementary Information | permitted when relevant |

### Analysis limits

| Item | Current NMI requirement |
|---|---|
| Main text | up to **3,500 words** |
| Excluded from main-text count | abstract, online Methods, references and figure legends |
| Abstract | **100–150 words**, unreferenced |
| Display items | up to **6** figures and tables combined |
| References | typically up to **50** |

### Article and Analysis structure

Use this sequence unless the editor authorizes a justified variant:

1. Introduction, without an `Introduction` heading
2. Results
3. Discussion
4. Methods

Results and Methods may use short topical subheadings. Discussion should not
use subheadings. The Methods section should be concise but contain enough
detail for interpretation and replication; original research publishes Methods
online.

Treat the six-item display allowance as a combined figure-plus-table budget.
Plan the evidence hierarchy before drafting rather than shrinking essential
validation into unreadable composite panels.

## 4. Other content types

| Content type | Length | Displays | References | Key boundary |
|---|---:|---:|---:|---|
| Review Article | **3,000–4,000 words** | illustrations strongly encouraged | up to **100** | synthesize a field; annotations are encouraged for the most important references, normally no more than 10% of the list |
| Perspective | **3,000–4,000 words** | as justified | up to **100** | present a scholarly, forward-looking viewpoint rather than a disguised original Article |
| Correspondence | **500–1,000 words** | up to **1** | up to **10** | should not contain research data or analysis |
| Comment | **1,500–2,000 words** | as justified | up to **15** | should not be a normal primary-research report |
| Reusability Report | follow the Article format | follow the Article format | follow the Article format | evaluate robustness or reusability of existing code rather than merely announcing software |

Do not infer an Article limit for an unlisted or commissioned format. Check the
current content-type page or the commissioning editor's instructions.

## 5. Initial-submission package

### Accepted review formats

At initial submission, NMI does not require special formatting if the material
is complete and reviewable. The journal accepts:

- PDF
- Microsoft Word
- TeX/LaTeX, submitted as a compiled PDF for review

### Package inventory

Prepare:

- one complete manuscript file containing the Methods, figures and any
  Extended Data used at review stage
- a **cover letter**
- Supplementary Information when needed for the conclusions, understanding or
  replication

The manuscript should include:

- author names and affiliations, unless optional double-anonymized review is
  selected
- enough findings, methods and material detail for editorial and peer review
- a complete reference list
- optional Extended Data, within the ten-item limit

Every figure, table, Extended Data item and supplementary item must be cited in
the manuscript. Supporting information is sent to reviewers, so it must be
reviewable and must not contain claims that the main text depends on but never
states.

## 6. Writing, structure and accessibility

- Write for readers beyond the immediate machine-learning or application
  subfield.
- Make titles and abstracts intelligible to scientists outside the specialty.
- Explain unavoidable jargon and define non-standard abbreviations at first
  use; minimize abbreviations when plain language is shorter.
- State the scientific or societal question, not only the architecture and
  benchmark score.
- Report quantitative evidence and important limitations without inflating
  association, benchmark gain or simulation performance into general-world
  effectiveness.
- Keep Methods concise but reproducible. A numeric Methods word limit is not
  stated on the current public NMI pages.

For algorithmic papers, distinguish the contribution from parameter scaling,
data leakage, additional supervision, compute advantages and benchmark-specific
tuning. For deployed or societal claims, describe the population, setting,
failure modes and transfer boundary.

## 7. Cover letter, review mode and related work

### Cover letter

The initial package includes a cover letter. It should:

- explain the work's importance and fit for NMI's diverse readership
- disclose related manuscripts under consideration or in press
- disclose any prior discussion of the work with an NMI editor
- place author affiliations and contact details here when double-anonymized
  review is selected
- optionally recommend or oppose reviewers, giving a concise reason for an
  exclusion request

The cover letter is confidential and is not shown to reviewers. Do not repeat
the abstract; use it to help the editor understand novelty, audience, overlap
and any sensitive procedural context.

### Double-anonymized peer review

Double-anonymized review is optional. Authors who select it must:

- remove identifying author and affiliation information from the manuscript
- anonymize self-citations, acknowledgements, repository links and file
  metadata where necessary without making the science uninterpretable
- provide author information in the cover letter and submission system
- select the double-anonymized option during submission

The authors, not the journal, are responsible for effective anonymization.

### Preprints, conference papers and overlapping work

- A preprint is not treated as prior publication. Disclose it and provide its
  DOI and licence where available; a preprint may be posted during review.
- NMI may consider a journal manuscript extending a conference proceeding only
  when the new submission **substantially extends** the results, methodology,
  analysis, conclusions or implications. The editor decides whether the
  extension is sufficient.
- Cite and disclose the conference paper, identify the concrete extension and
  obtain any reuse permission or attribution required for text, figures or
  tables.
- Disclose and supply related manuscripts with overlapping authors that are
  under consideration or in press.
- Do not submit work with significant overlap simultaneously to another
  journal.

NMI does **not** consider presubmission enquiries. Prepare the full initial
submission instead.

## 8. Data, code and reporting standards

### Data Availability

Every original-research manuscript needs a Data Availability statement that
maps each supporting dataset to an access route. At initial submission:

- give repository names, persistent identifiers or accession numbers when
  available
- prefer recognized repositories for large or reusable datasets instead of
  burying them in Supplementary Information
- make supporting data available to editors and reviewers on request
- disclose legal, ethical, privacy, commercial, controlled-access,
  third-party or proprietary restrictions at submission and describe the
  access procedure precisely in the manuscript
- avoid an unqualified `available upon request` statement

### Code Availability

Place a separate headed **Code availability** section after Data Availability
and before the references. It must state how central custom code or algorithms
can be accessed and describe any restrictions.

For code central to the conclusions:

- make it available to editors and reviewers during peer review
- provide executable instructions, environment/dependency information and the
  inputs needed to reproduce key results
- prefer a DOI-minting repository such as Zenodo or Code Ocean and an
  Open Source Initiative-approved licence when release is possible
- expect the central code to be peer reviewed
- complete the **Software Submission Checklist** when newly developed code is
  central to the paper

Never invent a repository, DOI, licence, access condition or software version.
Route repository and statement drafting to `nature-data` and statistical
completeness to `nature-statistics`.

### Reporting and protocols

- Complete the appropriate Nature Portfolio reporting summary when the study
  type or field requires one, including relevant life, behavioural, social,
  ecological and specified physical-science routes.
- Apply study-type standards such as CONSORT, STROBE, PRISMA or ARRIVE when
  applicable.
- Sharing step-by-step protocols through a persistent protocol platform is
  encouraged; cite the protocol in Methods.
- Apply `../core/research-compliance.md` to human, animal, clinical, image,
  structure, chemistry, taxonomy and provenance-sensitive work.

### AI-assisted writing

- A large language model cannot be an author.
- Human authors remain responsible for the manuscript.
- Disclose substantive LLM use in Methods or another suitable section.
- Pure AI-assisted copy editing does not require a declaration under the
  current Nature Portfolio policy.
- Apply the confidentiality and non-invention rules in `../core/ethics.md`.

## 9. Figures, Extended Data and Supplementary Information

### Initial submission

- Figures must be legible and assessable by reviewers; final production files
  are not required at this stage.
- Use no more than **6** main display items for an Article or Analysis, counting
  figures and tables together.
- Use no more than **10** Extended Data figures and tables combined.
- Cite every Extended Data item in the main text.

### Legend content

Each legend should begin with a brief title and then describe the panels. It
should define:

- visual encodings and panel labels
- centre and error-bar definitions
- the exact `n` and unit of analysis
- statistical tests, sidedness, corrections and exact P-value policy where
  applicable
- scale bars and necessary sample identifiers

Avoid placing a second Methods section in the legend. The current live NMI AIP
page says that a legend should not exceed the word limit of the article type,
but the current Content Types page does **not** assign a separate numeric limit
to each figure legend.

The official NMI brief submission guide revised 9 July 2018 explicitly said to
keep each figure legend below **300 English words**. Because that number is not
repeated on the current live pages, treat it as a **historical advisory ceiling**,
not as a current journal hard limit.

Use this operating guardrail unless the live submission system or handling
editor gives a newer instruction:

- count the title and all panel descriptions as **one whole-figure legend**;
  300 words is not a per-panel allowance
- aim for **150–250 English words** for an ordinary multi-panel legend
- keep the complete legend below **300 English words** as a conservative
  preflight ceiling
- move expendable methodological detail to Methods or Supplementary
  Information, but retain the `n`, uncertainty and statistical information
  needed to interpret the figure

### Supplementary Information

- Keep SI relevant to the conclusions, understanding or replication.
- Number Supplementary figures and tables separately from main and Extended
  Data items.
- Make each Supplementary figure plus legend fit on one PDF page.
- Cite every supplementary item in the manuscript.
- Combine simple SI into one PDF; provide complex tables or datasets as Excel
  or CSV, and software packages as ZIP or TAR where appropriate.

## 10. Accepted-in-principle production contract

Apply these only after the editor requests final files:

### Text and tables

- Submit editable Microsoft Word or TeX/LaTeX source; PDF is not accepted as
  the final manuscript source.
- Place tables at the end of the manuscript; complex tables may be supplied in
  Excel.
- Number references sequentially and include DOI-bearing data and code records
  in the reference list where cited.
- Do not use footnotes.
- Use short bold Methods headings.
- Keep acknowledgements brief, do not thank anonymous reviewers or editors,
  and provide the funding statement separately.
- Link the corresponding authors' ORCID records before final acceptance when
  requested.

### Figure production

- Cite figures in sequential order.
- Supply figure panels at **at least 300 dpi** and no more than **180 mm** wide.
- Use editable **5–7 pt sans-serif** labels and Symbol for Greek characters.
- Use scale bars instead of magnification and define them in the legend.
- Keep labels, scale bars and error bars editable rather than flattened into a
  raster when the production workflow permits.
- Provide source data. Full unprocessed gels or blots are required for relevant
  figures, and statistical source data should be organized by figure, normally
  in an Excel workbook.

### Extended Data and supporting-information inventory

- Keep the combined Extended Data total at no more than **10**.
- Fit each Extended Data figure or table on one PDF page.
- Cite each item in the main text and include its legend in the Inventory of
  Supporting Information.
- Finalize the SI numbering, citations, file formats and inventory before
  upload.

## 11. Requirements not stated as fixed numbers

The current official NMI pages reviewed for this contract do not publish:

- a fixed title character or word limit
- a separate numeric Methods word limit
- a current separate numeric per-figure-legend word limit; the older official
  2018 guide's below-300-word instruction is retained only as an advisory
  preflight ceiling

Do not borrow numbers from flagship *Nature*, *Nature Communications* or a
third-party checklist. Do not present NMI's historical below-300-word figure-
legend instruction as a current hard limit. Write concisely, then follow any
new editor- or submission-system instruction at the active stage.

Open-access article-processing charges and currencies can change. If the author
asks for cost planning, check the live Publishing Options page instead of
treating a stored price as a submission rule.

## 12. Official sources

Current pages verified **2026-08-14**:

- Submission guidelines: <https://www.nature.com/natmachintell/submission-guidelines>
- Content types: <https://www.nature.com/natmachintell/content>
- Preparing your submission: <https://www.nature.com/natmachintell/submission-guidelines/preparing-your-submission>
- Initial formatting: <https://www.nature.com/natmachintell/submission-guidelines/initial-formatting>
- Writing and language: <https://www.nature.com/natmachintell/submission-guidelines/writing-and-language>
- Accepted-in-principle and formatting: <https://www.nature.com/natmachintell/submission-guidelines/aip-and-formatting>
- Double-anonymized peer review: <https://www.nature.com/natmachintell/submission-guidelines/dapr>
- Editorial policies: <https://www.nature.com/natmachintell/editorial-policies>
- Reporting standards, data and code: <https://www.nature.com/natmachintell/editorial-policies/reporting-standards>
- Preprints and conference proceedings: <https://www.nature.com/natmachintell/editorial-policies/preprints-conference-proceedings>
- Presubmission enquiries: <https://www.nature.com/natmachintell/submission-guidelines/presubmission-enquiries>
- Aims and scope: <https://www.nature.com/natmachintell/aims>
- Publishing options: <https://www.nature.com/natmachintell/submission-guidelines/publishing-options>

Historical official source retained for conservative preflight only:

- Brief guide for submission to Nature Machine Intelligence, revised 9 July
  2018: <https://www.nature.com/documents/natmachintell-brief-submission-guide.pdf>
