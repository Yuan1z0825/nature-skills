## Summary

Adds a small GitHub Actions workflow that runs the local skill metadata validator on pull requests and pushes that touch skill definitions or the supporting README/validator files.

## What it checks

The workflow runs:

```bash
python scripts/validate-skill-metadata.py
```

It validates:

- required `SKILL.md`, `README.md`, `README_EN.md`, and `manifest.yaml`
- matching skill names between `SKILL.md` and `manifest.yaml`
- valid manifest YAML
- manifest file paths that actually exist
- README badge count matching the number of triggerable skills

## Why

This prevents metadata drift from landing silently in the repository and gives maintainers a cheap review gate for future skill changes.

## Validation

Validated locally with the script before pushing.
