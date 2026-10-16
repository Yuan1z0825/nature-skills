# Journal Scope

The script accepts explicit journal names, never a `Nature ` or `npj ` prefix alone.
Its local lists are conservative, not an exhaustive or permanently current portfolio directory.
Verify missing or renamed titles on the publisher's official pages before updating the lists.
The npj snapshot is in `data/npj-journals.json`, sourced from the
[official npj Series directory](https://www.nature.com/nature-portfolio/about-journals/npj-series)
on 2026-10-16. Unknown names remain outside the automated scope until verified.

## Default families

### Nature Portfolio

Include:

- `Nature`
- explicitly listed Nature journals, such as `Nature Medicine`, `Nature Biotechnology`,
  `Nature Methods`, `Nature Materials`, `Nature Genetics`, `Nature Communications`
- verified `Communications` journals when added to the local exact-title list
- explicitly listed `npj` journals
- `Scientific Reports`

Be careful with unrelated titles that include the common word "nature".

### Science family

Include by default:

- `Science`
- `Science Advances`
- `Science Translational Medicine`
- `Science Signaling`
- `Science Immunology`
- `Science Robotics`

The AAAS Science Partner Journal program is not included by default unless the user asks for partner
journals or broader AAAS coverage.

### Cell Press

Include the flagship `Cell`, major primary-research Cell Press journals, Cell Reports titles, and
Trends review journals. The local script recognizes common Cell Press titles and any title beginning
with `Trends in `.

Because Cell Press launches and reorganizes titles over time, verify official pages for exhaustive
coverage or a current journal list.

## Flagship-only scope

Use only:

- `Nature`
- `Science`
- `Cell`

This is appropriate when the user says "只看正刊", "主刊", "flagship only", or explicitly excludes
subjournals.

## Official source notes

- Crossref REST API can retrieve scholarly metadata, search works, and filter exact fields such as
  `container-title` and `issn`.
- NCBI E-utilities provide structured access to PubMed and other Entrez databases; observe request
  frequency guidance.
- EndNote documents `Reference Manager (RIS)` as an import option for RIS files.
- Nature Portfolio, AAAS, and Cell Press official pages should be checked when exact current journal
  coverage matters.
