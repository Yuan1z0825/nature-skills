## Summary

Adds a small validator that checks the main README skill index against the actual `skills/` directory layout.

## What it checks

- README skill index count matches the number of triggerable skills
- Chinese and English index tables list the same skills in the same order
- each index link points to an existing skill README
- `nature-shared` stays excluded from the triggerable skill count

## Validation

Ran locally:

```text
Skill index validation passed: 17 triggerable skills, 17 listed entries.
```
