# Flagship Nature Article data, code and materials requirements

Use this reference when the target is the flagship journal **Nature**. It adds
journal-specific submission placement and specialist checks to the general
repository and FAIR workflow.

## Contents

1. Data Availability
2. Mandatory and specialist deposition gate
3. Code Availability
4. Materials and protocols
5. Controlled, clinical and third-party data
6. Structure-data submission files
7. Nature readiness output
8. Official sources

## Data Availability

- Every original-research Article needs a headed `Data Availability` statement.
- Place it with the Methods/end-of-Methods material according to the current
  Nature Article sequence.
- Map primary and reused datasets to repositories, accession numbers or exact
  Source Data/Supplementary files.
- Make the minimum dataset needed to interpret, verify and extend the work
  transparent.
- Supply supporting data to editors and referees when requested.
- Require full public access at publication unless a disclosed, justified
  restriction applies.
- Formally cite deposited datasets in the reference list using author, title,
  repository and full identifier URL.

Large datasets should normally use repositories rather than Supplementary
Information. A personal site, mutable cloud folder or unarchived GitHub branch
is not a durable repository record.

## Mandatory and specialist deposition gate

Check community repositories and accession numbers for applicable data,
including:

- protein sequences
- DNA/RNA sequences and sequencing data
- genetic polymorphisms and linked genotype/phenotype data
- macromolecular structures and electron-microscopy maps
- gene-expression data, including MIAME compliance where applicable
- small-molecule crystallography
- proteomics
- Earth, space and environmental data where a community repository exists

This list is a routing reminder, not a substitute for the current mandatory
repository table. Verify the current official page before naming the required
repository.

## Code Availability

For previously unreported custom code, algorithms or software central to the
main claims:

- make the code available to editors and referees on request during assessment
- include a separate headed `Code Availability` statement
- state how the code can be accessed and every restriction
- prefer an archived, versioned, DOI-minting repository for publication
- cite the archived software record in the reference list
- do not claim readiness when a central code dependency is unavailable and the
  editor has not accepted the restriction

Keep code version, environment, licence, model weights and execution data
separate in the inventory when they have different access routes.

## Materials and protocols

- Disclose any restriction on unique materials at submission and in the
  manuscript.
- Name who will handle material requests when it is not the corresponding
  author.
- Use RRIDs or other persistent identifiers for key antibodies, cell lines,
  organisms and tools where available.
- Report cell-line source, authentication and distribution restrictions.
- Deposit step-by-step protocols on a citable platform when available and cite
  the DOI or stable record in Methods.

## Controlled, clinical and third-party data

For controlled access, state:

- why access is restricted
- the responsible committee or institutional route
- eligibility and application procedure
- expected response timeframe
- data-use-agreement and reuse restrictions
- what discoverable metadata remain public

For clinical trial data, also state what de-identified participant data and
documents will be shared, when and for how long, with whom, for which analyses,
and by what mechanism. `Undecided` is not an acceptable final sharing plan.

For third-party or proprietary data, identify the provider to editors, disclose
the restriction and confirm that peer-review and post-publication verification
access is permitted under the stated terms.

## Structure-data submission files

When small-molecule crystallography applies, coordinate with the shared
research-compliance checklist for `.cif`, structure factors, probability-
ellipsoid artwork and CheckCIF output. For macromolecular structures, confirm
the required validation report and release-on-publication status.

## Nature readiness output

Add these columns to the standard data audit:

| Dataset/code/material | Claim supported | Required repository/file | Reviewer access | Publication access | Statement placement | Status |
|---|---|---|---|---|---|---|

Use `blocked` for missing mandatory deposition, inaccessible claim-critical
data/code, undefined controlled access, or missing structure validation files.

## Official sources

Verified 2026-08-08:

- Nature initial submission: <https://www.nature.com/nature/for-authors/initial-submission>
- Nature Portfolio reporting standards and availability: <https://www.nature.com/nature-portfolio/editorial-policies/reporting-standards>
- Nature forms and declarations: <https://www.nature.com/nature/for-authors/forms-and-declarations>
