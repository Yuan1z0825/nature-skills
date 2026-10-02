# Compose mode

Use when the user provides a topic, title, vague idea, or research direction and wants a proposal or research plan drafted.

## Contents

- [Overview](#overview)
- [Adaptive intake](#adaptive-intake)
- [Step-by-step](#step-by-step)
- [Step 1: Intake and scope](#step-1-intake-qa--00_scopemd)
- [Steps 2-5: Foundation files](#step-2-build-01_research_canonmd)
- [Steps 6-9: Review, drafting, QA, and export](#step-6-foundation-review)

## Overview

```text
Intake Q&A → scope lock → research canon → evidence table → argument map
→ section contracts → foundation review → section drafting → section QA
→ full proposal QA → export
```

Each step produces a concrete file or decision. Do not skip foundation steps.
Drafting begins only after foundation review passes the stage threshold (foundation_score > 7.5).

---

## Adaptive intake

Default: one question at a time. Switch to grouped questions (3-5 at once) only if the user asks to move faster. Do not ask questions whose answers are already present in the supplied materials or the current session.

### 本子-based intake (special pattern)

When the user is working from an existing 本子 (approved project blueprint) rather than composing from scratch, the intake phase is dominated by the user sharing structured pieces of the 本子 (abstract, research content, methods, innovations, targets). The agent should:

1. **Collect all before building**. If the user says "不要急着开始，先接收信息", do not jump to foundation files while information is still arriving.
2. **Let the user control the sequence**. They know the 本子 structure; they'll share what's relevant in their order.
3. **Acknowledge each piece concisely** — confirm receipt and key implications — but don't synthesize prematurely.
4. **Ask what's still missing** only after the user signals the flow is complete ("还有吗").
5. **Only then** proceed to scope → canon → evidence → argument map.

**Intake checklist by priority:**

| Priority | Must resolve | How |
|---|---|---|
| P0 | text type, target reader, topic/direction, output language, deliverable scope | ask if unknown |
| P1 | core scientific question, existing evidence, required content, forbidden claims, target style | ask if unknown or ambiguous |
| P2 | word count, format requirements, reference template, timeline | ask only if the user volunteers it or the task clearly requires it |

**Rule**: only ask questions whose answers change the writing path. If the user says "write a proposal about corrosion" and you already know from context it's a doctoral research plan for their supervisor, don't ask "what document type" — confirm the assumption: "I assume this is a doctoral research proposal for your supervisor, in Chinese, covering the first part of the project. Correct?"

---

## Step-by-step

### Step 1: Intake Q&A → `00_scope.md`

- **Match proposal depth to project timeline**: A proposal for work starting 1+ years out should be direction-level (框架对、逻辑通), not execution-level (操作级细节). Detailed methods belong in pre-experiment planning, not the proposal.
- **When user says "只是写一个大致的proposal，并不是具体的执行书"** — lock scope to direction-level. Avoid over-specifying equipment, SOPs, or safety protocols that belong in lab manuals.

**Input**: the user's topic or idea, plus relevant supplied materials and current-session context.

**Output**: `00_scope.md` filled with at minimum: project slug, mode, text type, target reader, language, deliverable scope.

**Pitfalls**:
- Don't ask P2 questions during intake unless the user brings them up. Scope first, details later.
- Don't treat intake as a questionnaire. One clarifying question that narrows a real ambiguity is worth ten checklist items.
- If the user says "先不管这些，直接开始写", lock scope with reasonable defaults from the available context and move to Step 2.

### Step 2: Build `01_research_canon.md`

**Input**: `00_scope.md`, user-provided domain context, and traceable literature from the available literature-search workflow.

**Output**: `01_research_canon.md` with at minimum:

| Section | Minimum content |
|---|---|
| Literature facts | ≥ 3 statements, each with source (author-year or DOI) |
| Experimental facts | ≥ 2 statements about what is known or measured (including user-provided prior work) |
| Thermodynamic/model facts | if applicable; flag as "model output, needs experimental verification" |
| Supervisor constraints | direct quotes or paraphrases of supervisor requirements |
| Terminology definitions | key terms that must be used consistently |
| Forbidden claims | claims that the text must not make (e.g., "cannot claim treatment A is effective without target-condition evidence") |
| Unresolved claims | facts that are debated or unverified; writing may note them but not resolve them |

**Pitfalls**:
- Don't derive canon from "common knowledge". Every entry must trace to a source.
- Don't treat literature conclusions as canon if they conflict. Mark as "unresolved" with both sides.
- Don't treat simulation output as experimental fact. Flag model data explicitly.
- Canon is a boundary file. Writing cannot silently alter it. If new evidence emerges during drafting, update canon first.

### Step 3: Build `02_evidence_table.md`

**Input**: `01_research_canon.md`, literature sources, and user-provided prior data.

**Output**: `02_evidence_table.md` — a table mapping claims to evidence.

Each row: `claim | evidence/source | strength | usable section | risk | status`

Strength values: `evidence-backed` / `plausible-inference` / `hypothesis` / `unsupported`

Status: same as strength, but updated as drafting progresses.

**Minimum**: ≥ 5 rows covering the core scientific claims the proposal will make.

**Pitfalls**:
- Don't inflate hypothesis to evidence-backed. "Component A may react with component B" remains a hypothesis until the reaction is supported under the target conditions.
- If a claim has no usable evidence, mark it `unsupported`. Don't hide it by omission. The argument map will decide whether to include, downgrade, or request evidence.
- Evidence that is "obvious from the literature" still needs a citation.

### Step 4: Build `03_argument_map.md`

**Input**: `01_research_canon.md`, `02_evidence_table.md`.

**Output**: `03_argument_map.md` with:

| Section | Content |
|---|---|
| Scientific tension | what is known, what is unknown, why the gap matters |
| Central research question | one sentence; must be answerable by the proposed work |
| Central thesis | one sentence; the answer you expect (or the hypothesis you test) |
| Supporting arguments | 2-4 arguments, each with: claim, evidence (from evidence table), limitation |
| Counterarguments | alternative explanations or opposing views; how the proposal addresses or acknowledges them |
| Final move | what the reader should conclude after reading the proposal |

**Pitfalls**:
- Don't write arguments that can't be supported by the evidence table. If you discover a gap, go back to Step 3 and add/flag evidence.
- A weak central research question ("study the behavior of...") produces a weak argument map. Falsifiable questions ("does treatment A reduce the target impurity more effectively than treatment B under matched conditions?") produce strong maps.
- Counterarguments are not weaknesses. A proposal that states how an uncontrolled variable could invalidate the preferred route is stronger than one that ignores it.

### Step 5: Build `04_section_contracts.md`

**Input**: `00_scope.md`, `03_argument_map.md`, default proposal structure.

**Output**: One contract per section. Each contract:

```
## Section: [name]
- Purpose: what this section must accomplish in the overall argument
- Inputs: which canon/evidence/argument items feed into this section
- Allowed claims: claims this section may make (from evidence table)
- Forbidden claims: claims this section must not make (from canon forbidden list + scope boundary)
- Required evidence: evidence that must appear in this section
- Validation checklist: 2-4 checks to verify the section does its job
```

**Default proposal sections** (adjustable to supervisor/school requirements):

1. 研究背景与意义
2. 国内外研究现状
3. 科学问题与研究目标
4. 研究内容
5. 技术路线与实验方法
6. 创新点
7. 可行性分析
8. 研究计划与预期成果

**Pitfalls**:
- Don't let "研究背景" contract allow claims that belong in "研究现状". Background = why this domain matters; literature review = what others did and what gap remains.
- Innovation section contract must forbid: "本研究具有重要的理论和工程意义". Allowed: specific, testable contribution statements.
- If the proposal is partial-stage (e.g., Part 1 only), load `references/partial-proposal-scope.md` and add a scope-boundary constraint to every section contract.

### Step 6: Foundation review

**Input**: all 5 foundation files.

**Process**: run professor with 1-2 specialists (doctoral proposal reviewer + domain expert). Score foundations using evaluation rubric. If `foundation_score < 7.5`, return to the weakest foundation file and fix it before drafting.

**Output**: professor review notes in `qa_logs/foundation_review.md`, updated foundation files if issues found.

**Gate**: do not begin drafting until `foundation_score > 7.5`.

### Step 7: Draft section by section

**Input**: all foundation files, section contracts.

**Process**: draft one section at a time. For each section:
1. Read the section contract.
2. Extract the allowed claims and required evidence.
3. Draft the section text, citing evidence as you go.
4. Run section QA (score via evaluation rubric; target: `section_score > 6.5`).
5. If score < 6.5, fix the section before moving on. Do not accumulate broken sections.

**Pitfalls**:
- First draft aims for forward progress, not perfection. A 6.5 section is keepable; don't polish to 9.0 before writing the next section.
- Don't cross-contaminate sections. If "研究内容" starts describing background, stop and check the section contract.
- Evidence that appears in the draft but not in the evidence table must be added to the evidence table. Don't let draft text become an ungoverned source of claims.

### Step 8: Full proposal QA

**Input**: completed draft, all foundation files.

**Process**: run full evaluation rubric on the complete proposal. Score all 8 dimensions. Record in `qa_logs/proposal_qa.md`.

**Gate**: `proposal_score > 7.0` for supervisor-facing; `> 8.0` for final polish.

If score < 7.0: identify the weakest 1-2 dimensions, return to the relevant foundation file or section, fix, re-draft affected sections, re-score.

### Step 9: Export

**Input**: QA-passed draft, `00_scope.md`.

**Process**: produce `exports/proposal_final.md` (archive) and `exports/proposal_final.docx` (submission). Run pre-delivery checks: no unresolved TODOs, no unsupported claims masquerading as facts, citation placeholders resolved, figure/table numbering consistent, version+date clear.

**Pitfalls**:
- Don't skip the .docx export. .md is for version control; .docx is what the supervisor reads.
- If the proposal is partial-stage, the export filename should reflect that (e.g., `part1_xxx.md` not `proposal_final.md`).
