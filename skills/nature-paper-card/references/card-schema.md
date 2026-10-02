# Paper Card schema

## Contents

- [01 Basic Information](#01-basic-information)
- [02 One-Sentence Summary](#02-one-sentence-summary)
- [03 Research Question](#03-research-question)
- [04 Research Background and Development Path](#04-research-background-and-development-path)
- [05 Core Pain Points Identified by the Paper](#05-core-pain-points-identified-by-the-paper)
- [06 Core Idea](#06-core-idea)
- [07 Method Overview](#07-method-overview)
- [08 Core Module Breakdown](#08-core-module-breakdown)
- [09 Essential Formulas and Symbols](#09-essential-formulas-and-symbols)
- [10 Experimental Design and Evidence Chain](#10-experimental-design-and-evidence-chain)
- [11 Correct Interpretation of the Conclusions](#11-correct-interpretation-of-the-conclusions)
- [12 Limitations Explicitly Acknowledged by the Authors](#12-limitations-explicitly-acknowledged-by-the-authors)
- [13 Critical Analysis](#13-critical-analysis)
- [14 Knowledge Learned](#14-knowledge-learned)
- [15 Connections to Existing Knowledge](#15-connections-to-existing-knowledge)
- [16 Research Ideas](#16-research-ideas)


Use all headings in this order. Translate the headings and tables into the user's language when needed. Keep a section concise when the paper does not require extensive treatment.

## 01 Basic Information

Record title, authors and affiliations, venue, year, paper type, field, keywords, DOI or arXiv identifier, code, dataset, reading date, and the paper's position in the user's research direction. Mark unavailable fields.

## 02 One-Sentence Summary

Answer in one sentence: what problem, what approach, through what mechanism, and what bounded result. Avoid promotional adjectives.

## 03 Research Question

State:

- the concrete problem;
- why it matters;
- why existing approaches are insufficient;
- one precise `Can ... ?` research question when appropriate.

## 04 Research Background and Development Path

Map stages, representative approaches, advantages, limitations, and the paper's claimed position. Label whether this path is externally verified or only framed by the paper.

## 05 Core Pain Points Identified by the Paper

Use:

| Pain point | Manifestation | Cause or author explanation | Evidence from the paper |
|---|---|---|---|

Do not turn an author explanation into an established root cause without evidence.

## 06 Core Idea

Separate:

1. surface method;
2. core insight;
3. possible general lesson.

Label the general lesson `[Analysis]`.

## 07 Method Overview

Record input, output, modules, training, tools, feedback loop, and assumptions. Add a text flow from input to output.

## 08 Core Module Breakdown

Use:

| Module | Function | Why it is needed | Input and output | Supporting evidence | Known or expected effect of removal |
|---|---|---|---|---|---|

Distinguish measured ablation effects from expected effects.

## 09 Essential Formulas and Symbols

Include only formulas essential to understanding. For each, give the formula, symbol meanings, purpose, intuition, and source pointer. Use `Not applicable` when appropriate.

## 10 Experimental Design and Evidence Chain

First record datasets or population, scale, metrics, baselines, budget, backbone or instrument, oracle inputs, and evaluation protocol.

Then use:

| Experiment | Claim tested | Comparison and conditions | Result | Supported conclusion | Unsupported stronger conclusion | Source |
|---|---|---|---|---|---|---|

## 11 Correct Interpretation of the Conclusions

Audit task scope, oracle or ground-truth inputs, end-to-end status, compute cost, historical-data dependence, model dependence, hardest cases, population or domain boundary, and uncertainty. End with a bounded restatement of the main result.

## 12 Limitations Explicitly Acknowledged by the Authors

Include only author-acknowledged limitations:

| Limitation | Specific manifestation | Future direction proposed by the authors | Source |
|---|---|---|---|

If none are explicit, write `No explicit author-acknowledged limitation was found in the supplied source.` Do not fill the table. If useful, add a separate `Related constraints noted by the authors` subsection, clearly stating that these are not presented by the paper as formal limitations.

## 13 Critical Analysis

Use:

| `[Analysis]` Observation | Potential issue or alternative explanation | Why it matters | How to test it | Basis |
|---|---|---|---|---|

Include only specific, falsifiable concerns. Do not imitate a formal reviewer report.

## 14 Knowledge Learned

Extract transferable concepts, methods, formulas, and experimental designs. If not supplied by the user, title the subsection `Agent-derived knowledge candidates`.

## 15 Connections to Existing Knowledge

Connect the paper to verified external literature, user-provided knowledge, or clearly marked candidate directions. Cover similarities, combinations, conflicts, and transferable domains only when supported.

## 16 Research Ideas

For each candidate include:

- name;
- originating limitation or observation;
- core hypothesis;
- delta from the paper;
- initial method;
- validation;
- possible failure modes;
- innovation status: `unverified`, `partially checked`, or `prior-art checked`.

Title Agent-generated content `Agent-derived research candidates`, not `My research ideas`.
