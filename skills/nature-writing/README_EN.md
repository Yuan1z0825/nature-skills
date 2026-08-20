# `nature-writing` Skill

[中文说明](README.md)

`nature-writing` drafts or rebuilds Nature-style manuscript sections and prepares initial-submission packages from author-provided claims, figures, results, notes, or Chinese drafts.

## What To Use It For

- Build titles, abstracts, introductions, result narratives, discussions, conclusions, or significance paragraphs.
- Organize claim-evidence narrative from figures and data.
- Turn Chinese research notes into English manuscript paragraphs.
- Build the background, gap, question, and contribution chain for an Introduction.
- Reorder Results or Discussion at the section level rather than only polishing sentences.
- Classify results as core discovery, necessary support, conclusion-changing qualification, robustness, heterogeneity, provenance, alternative inference, or edge case; allocate them across main text, captions, Methods/source data, and SI; and compress the main text to the shortest sufficient evidence chain.
- Prepare an initial cover letter, title page, highlights, author contributions, availability statements, and other declarations.
- Organize reviewer suggestions, a deliverable matrix, and a pre-submission completeness audit.
- Run the stage-aware official checklist for a flagship `Nature Article`: initial files, title/text/display limits, Extended Data, SI, Reporting Summary, ethics, and specialist materials.
- Apply a dedicated stage-aware `Nature Machine Intelligence` contract covering Article/Analysis word and six-display limits, the required cover letter, up to ten Extended Data items, substantial conference-paper extensions, and data/central-code review access.
- For flagship Nature, Nature Communications, NMI, and other Nature Portfolio titles, structure Results so each subsection advances a claim, permit evidence-bound local interpretation, and make Discussion synthesize across Results rather than re-demonstrate them.
- For every Nature / Nature Portfolio target, make Introductions converge rapidly on an exact unknown, use literature to construct the known–unknown tension, express novelty through the question and answerable design, and align each Introduction question with a Results answer.
- For every Nature / Nature Portfolio target, compress abstracts into a shortest evidence chain—exact gap, answer-enabling design, one main discovery, one or two decisive supports or boundaries, and a bounded payoff—retaining numbers only when they define or materially support the central claim. These three defaults were initially distilled from published NMI papers, with the Results–Discussion guidance further reinforced by flagship Nature comparisons, and generalized as Nature-style guidance; they are not official submission rules.

## Typical Requests

- "Write a Nature-style abstract from these figures and results."
- "Rebuild the logic of this introduction; do not only polish the sentences."
- "Turn these Chinese results into an English Results narrative."
- "Prepare an initial cover letter and complete submission package from this manuscript."

## What You Need To Provide

- Core claim, figures, key results, experimental facts, and target reader.
- Target section, length, language, and terminology that must be preserved.
- Confirmed references, limitations, and conclusions that must not be added.

## Outputs

- Section outline, claim-evidence map, or ready-to-paste prose.
- A Results allocation table, deletion/replacement record, and before/after main-text word-count delta when needed.
- Revision suggestions for novelty, significance, evidence chain, and reader path.
- Facts, references, or figure notes requiring author confirmation.
- Initial-submission materials, editable LaTeX templates, a missing-input checklist, and a `ready / ready_with_author_checks / blocked` status.

## Boundaries

- The skill does not invent experimental results, statistical significance, mechanism explanations, or references.
- If an English draft only needs sentence-level polishing, use `nature-polishing`.
- If claim support requires literature search first, use `nature-citation` or `nature-academic-search`.
- This skill handles first submission; use `nature-response` for revision cover letters, rebuttals, and point-by-point responses.

## Related Skills

- `nature-polishing`: English polishing, translation, and style tightening.
- `nature-citation`: match supporting references for claims.
- `nature-figure`: align figure conclusions and panel design with manuscript narrative.
- `nature-response`: revision cover letters, responses to reviewers, and revision correspondence.
- `nature-reviewer`: simulated review before submission.
