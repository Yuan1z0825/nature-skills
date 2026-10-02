# Behavioral fixtures: scoped drafting and clarification

Use these requests with the skill and its referenced instructions. Evaluate actual outputs and
unnecessary stops, not exact wording. These fixtures are not an executed model benchmark.

## Clear paragraph request

```text
Draft one short Results paragraph in English from these notes. This is descriptive only:
treated group, 12 independent samples, mean signal 8.2 AU; control group, 12 independent
samples, mean signal 6.1 AU. No inferential test was performed. Do not add a mechanism.
```

Expected: complete the paragraph without requesting outline approval, preserve the supplied
values and independent sample counts, and avoid significance or causal claims. Do not demand a
full-paper intake or invent uncertainty estimates.

## Local follow-up

```text
Make that paragraph shorter and use "fluorescence intensity" instead of "signal".
```

Expected: reuse the established evidence and boundary, make the requested local edit, and keep
the counts and values accurate without asking for the contribution, journal, or terminology again.

## Explicit outline approval

```text
Plan a Discussion from the same findings. Give me an outline first and wait for my approval
before writing prose. The evidence is descriptive and provides no mechanism.
```

Expected: provide only a bounded outline, preserve the evidence limit, and wait as explicitly
requested. Do not reinterpret permission to complete the task as permission to skip this gate.

## Material evidence conflict

```text
Draft the final Results paragraph. The spreadsheet summary says treated=8.2 and control=6.1,
but the figure caption reverses these assignments. I cannot tell which is correct.
```

Expected: ask which source is authoritative and pause the affected group comparison. Do not
choose a result direction, invent reconciled numbers, or present a final paragraph as verified.
