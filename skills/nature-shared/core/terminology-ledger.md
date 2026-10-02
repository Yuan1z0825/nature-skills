# Terminology Ledger

A manuscript must use one name for one thing. The same method, model, dataset,
gene, metric, or concept must not drift across shifting names, spellings, or
capitalisation. Reviewers read inconsistent terminology as careless work, and a
term that changes between sections forces the reader to re-learn it.

Build the ledger **before** drafting or polishing prose, and treat it as the
single source of truth for the rest of the job. Consistency against a standard
is impossible if the standard was never written down.

## 1. Build the ledger on first contact

When you first receive a manuscript, draft, or set of notes, extract every
recurring domain term into a ledger before editing any prose:

- methods, models, systems, algorithms, modules, frameworks
- datasets, benchmarks, cohorts, materials, reagents
- genes, proteins, species, cell lines (respect established field nomenclature)
- metrics, units, statistical symbols, mathematical notation
- abbreviations and acronyms, each with its full form
- key concepts the paper defines or repeatedly relies on

For each term, record its canonical form, its first-use expansion (for
abbreviations), and any variants already present in the source.

## 2. Present the ledger to the user

Show a compact table before or alongside the first output:

| Canonical term | First-use definition | Variants seen in source | Decision |
|---|---|---|---|
| scRNA-seq | single-cell RNA sequencing (scRNA-seq) | "single cell RNA-seq", "scRNAseq" | spell out once, then use "scRNA-seq" |

Flag every collision explicitly: the same concept under different names, or one
name reused for two different concepts. Ask the user to confirm the canonical
choice only when the decision is genuinely ambiguous or domain-sensitive.
Otherwise adopt the form the source uses most often and state that choice.

## 3. Lock and enforce

Once set, the ledger is fixed for the whole job:

- Use only canonical forms in every output. Do not introduce synonyms to vary
  the prose. Terminology consistency outranks lexical variety in scientific
  writing.
- Define each abbreviation once, at first use, then use the short form.
- Keep units, symbols, and notation identical across every section.
- When drafting or polishing a later section, reference the ledger built from
  the earlier sections instead of re-deciding term by term.
- If the user later renames a term, change every occurrence in the manuscript,
  not just the current passage, and update the ledger.

## 4. Do not invent terms

Do not coin new names for the author's methods, modules, or concepts. If a term
is missing, undefined, or used inconsistently in ways you cannot resolve from
the source, ask the user or flag it. Never fill the gap with a guessed name.
