# RIS, EndNote, and Zotero RDF Output

EndNote can import RIS files using the `Reference Manager (RIS)` import option. Use `.ris` as the
default exchange format because it is plain text, widely supported, and easy to inspect.

## Contents

- [RIS mapping for journal articles](#ris-mapping-for-journal-articles)
- [Author-integrity preflight](#author-integrity-preflight)
- [EndNote import instruction](#endnote-import-instruction)
- [Zotero RDF guidance](#zotero-rdf-guidance)

## RIS mapping for journal articles

Use these tags:

```text
TY  - JOUR
TI  - Article title
AU  - Author, Given
AU  - Consortium Name,
T2  - Journal title
JO  - Journal title
PY  - Publication year
Y1  - YYYY/MM/DD when available
VL  - Volume
IS  - Issue
SP  - First page or article number
EP  - Last page
DO  - DOI
AN  - PMID:12345678
UR  - URL
SN  - ISSN
N2  - Abstract or short metadata note, only when safely available
ER  -
```

Rules:

- Write one `AU` line per author and preserve the source order.
- Personal names use `Family, Given` or `Family, Given, Suffix`. Keep source-provided initials and name particles.
- Corporate or consortium authors require a trailing comma, for example `AU  - NMSS Validation Group,`. Double an embedded comma before adding the trailing comma.
- A surname-only personal line such as `AU  - Chaudhuri` is incomplete. Do not deliver or import it as a finished record.
- Use `TY  - JOUR` for journal articles.
- End every record with `ER  -`.
- Do not invent missing fields.
- Write DOI in `DO`; a DOI URL in `UR` may be retained as well.
- Preserve a known PMID in `AN` so the record can be traced back to PubMed.
- Keep notes concise; avoid copying long abstracts into RIS unless the source terms allow it.

## Author-integrity preflight

Before export, verify all of the following:

1. The metadata source supplies a structured, ordered author list.
2. Every personal author has both a family name and a given name or initials.
3. Suffixes such as `Jr.` and `III`, name particles, and collective authors are retained.
4. One `AU` line is emitted for every source author. The exporter must not shorten the list to `et al.`.
5. Biomedical records with incomplete Crossref authors are refetched by PMID and compared against PubMed or the publisher page.

Bad:

```text
AU  - Chaudhuri
AU  - Schapira
```

Ready for EndNote:

```text
AU  - Chaudhuri, K Ray
AU  - Schapira, Anthony H V
```

The script blocks missing or surname-only author metadata by default. `--allow-incomplete-authors` is an explicit exception for cases where the limitation is understood; it must not be used to describe the export as verified.

## EndNote import instruction

Tell the user:

```text
In EndNote: File > Import > File, choose the `.ris` file, set Import Option to
Reference Manager (RIS), then import.
```

Menu labels vary slightly by EndNote version and operating system, so avoid over-specific UI claims
unless the user gives their exact EndNote version.

## Zotero RDF guidance

Use `.rdf` when the user explicitly asks for Zotero import/export.

Preferred structure:

```xml
<rdf:RDF ...>
  <bib:Article rdf:about="https://doi.org/...">
    <z:itemType>journalArticle</z:itemType>
    <dcterms:isPartOf rdf:resource="urn:..."/>
    <bib:authors>...</bib:authors>
    <dc:title>...</dc:title>
    <dc:date>YYYY-MM-DD</dc:date>
    <dc:identifier>...</dc:identifier>
    <bib:pages>...</bib:pages>
    <z:citationKey>...</z:citationKey>
  </bib:Article>
  <bib:Journal rdf:about="urn:...">...</bib:Journal>
</rdf:RDF>
```

Rules:

- Export one `bib:Article` per citation.
- Represent authors as `foaf:Person` nodes inside `rdf:Seq`.
- Deduplicate journal container nodes by journal/ISSN/volume/issue identity.
- Do not invent abstracts, attachments, or fields that are not present in metadata.
