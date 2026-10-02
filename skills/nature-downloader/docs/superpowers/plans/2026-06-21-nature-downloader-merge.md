# Nature Downloader Merge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild `nature-downloader` as a complete skill by combining the GitHub repository's real browser-based PDF downloader with the local multi-school configuration wizard.

**Architecture:** Import the upstream repository as the base. Add Python configuration modules under `src/`, data files under `data/`, and a small CLI wrapper that can configure schools, run health checks, and then invoke the existing Node download path. Keep credential handling in the browser only.

**Tech Stack:** Node.js ES modules for CDP/browser PDF download, Python 3 for school configuration and PDF text extraction, JSON/YAML config files, shell-level verification.

---

### Task 1: Import Upstream Repository

**Files:**
- Modify: workspace root

- [ ] Fetch `Flyme886/nature-downloader` into a temporary directory.
- [ ] Copy tracked upstream files into the workspace without overwriting `.git`.
- [ ] Verify that `README.md`, `SKILL.md`, and `scripts/` exist.

### Task 2: Merge Local Configuration Wizard

**Files:**
- Create: `src/config.py`
- Create: `src/wizard.py`
- Create: `src/validators.py`
- Create: `src/health_check.py`
- Create: `src/schools_loader.py`
- Create: `data/schools.yaml`
- Create: `data/school.schema.json`
- Create: `scripts/configure_school.py`
- Create: `tests/python/test_config_wizard.py`

- [ ] Copy local configuration modules and data files.
- [ ] Add a CLI wrapper for preset configuration, health check, and config display.
- [ ] Add Python tests using a temporary `LIT_DL_CONFIG_DIR`.
- [ ] Run Python tests and fix failures.

### Task 3: Bridge Config To Download Workflow

**Files:**
- Modify: `scripts/batch_download.mjs`
- Create: `scripts/lib/school-config.mjs`
- Modify: `scripts/lib/status-codes.mjs` if needed
- Create or modify: `tests/unit/school-config.test.mjs`

- [ ] Load `~/.config/lit-dl/school.json` or `LIT_DL_CONFIG_DIR/school.json`.
- [ ] Prefer configured discovery URL when present; fall back to the current Web of Science URL.
- [ ] Preserve the existing SJTU download path and status behavior.
- [ ] Add Node tests for config discovery and fallback behavior.

### Task 4: Update Skill Documentation

**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`

- [ ] Document first-run school configuration.
- [ ] Document the implemented download route and current limitations.
- [ ] Keep safety boundaries explicit: no credential scraping, no CAPTCHA bypass, no unauthorized mirrors.

### Task 5: Verify

**Commands:**
- `python3 -m unittest discover -s tests/python`
- `node --check scripts/batch_download.mjs`
- `node --check scripts/browser_pdf_downloader.mjs`
- `node --test tests/unit/*.test.mjs`

- [ ] Run all commands fresh.
- [ ] Report exact pass/fail status and any remaining limitations.
