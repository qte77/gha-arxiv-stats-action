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
