# Reference Renumbering in docx Body Text

## Problem

When removing or reordering references in a review paper, both the reference list AND all in-text citations must be renumbered. Running text replacement in cascade (high→low) causes citation numbers to collapse into each other.

## Correct Order

1. **Fix body citations FIRST** (before modifying reference list)
2. **Process LOW to HIGH** when iterating over remap keys
3. **Skip reference paragraphs** during body citation replacement to avoid double-processing

## Python Pattern

```python
# remap: dict of {old_number: new_number_or_None_if_deleted}

# STEP 1: Fix body citations only (before ref list modification)
for p in doc.paragraphs:
    if p is in reference section:  # skip!
        continue
    for run in p.runs:
        for old_n in sorted(remap.keys()):  # 1,2,3,... low→high
            new_n = remap[old_n]
            if new_n is None and old_n == DELETED:
                run.text = run.text.replace(f'[{old_n}]', f'[{NEIGHBOR}]')
            elif new_n is not None and new_n != old_n:
                run.text = run.text.replace(f'[{old_n}]', f'[{new_n}]')

# STEP 2: Delete old ref section
# STEP 3: Append new ref list with correct numbers
```

## Why High→Low Fails

Processing [46]→[45], then [45]→[44], ... causes newly created [45]s from step 1 to be incorrectly re-replaced to [44] by step 2. The cascade collapses all citations in the range to the lowest number.

## Verification

```python
gaps = [n for n in range(1, total+1) if n not in ref_list_numbers]
dupes = set(n for n in ref_list_numbers if ref_list_numbers.count(n) > 1)
orphans = body_citation_numbers - set(range(1, total+1))
assert gaps == [] and dupes == set() and orphans == set()
```
