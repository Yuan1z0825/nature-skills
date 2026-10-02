## Summary

Adds a small repository validator that checks the Chinese and English READMEs for each skill stay mirrored.

## What it checks

The script validates every skill pair for:

- matching `README.md` / `README_EN.md` presence
- matching heading counts
- mirrored language-switch links
- proper title-first structure
- `nature-shared` support-package wording consistency

## Why

The repository now has a consistent README pattern across skills. This validator helps maintain that pattern and catches drift before it lands.

## Validation

Ran locally:

```text
README mirror validation passed: 17 mirrored skill docs checked.
```
