# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html), i.e. MAJOR.MINOR.PATCH (Breaking.Feature.Patch).

Types of changes:

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

## [Unreleased]

### Changed

- HTTP client migrated from `urllib.request` to `requests` in `src/utils.py`
  and `src/citations.py`
- Ruff lint config tightened: enabled `S` (flake8-bandit) and `C90` (mccabe
  complexity, max 10) rule sets

### Security

- Removed `# noqa: S310` / `# nosec B310` suppressions; `requests` rejects
  `file://` and custom URL schemes by default, addressing the warning at
  the source rather than suppressing it

---

## [0.0.1] - 2026-03-23

### Added

- Composite `action.yaml` with inputs (OUT_DIR, TOPICS, PY_VER, TOKEN) and branding
- `pyproject.toml` with bumpversion config
- Bump-and-release workflow with signed commits via GitHub API
- Cleanup script for failed bump runs
- Version badge in README

### Changed

- `actions/checkout` `@v4` → `@v6`
- `github/codeql-action` `@v2` → `@v4`
- `github-actions` ecosystem added to dependabot

---
