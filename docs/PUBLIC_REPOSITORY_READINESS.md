# Public Repository Readiness

This document records the packaging hygiene applied to the public-release candidate. It is not a claim that the application is suitable for internet-facing production deployment.

## Included

- Application source, static assets, launchers, templates, and model catalog.
- Automated tests and GitHub Actions workflow.
- English and Persian user manuals, architecture notes, maintenance/security guidance, and changelog.
- Sanitized `config.example.json`.

## Excluded from the release archive

- `.venv/` and its machine-specific Python interpreter symlinks.
- `config.json`, `usage.json`, and `library.json` (local settings, usage, and prompt data).
- Python bytecode, `__pycache__`, `.DS_Store`, AppleDouble `._*` files, and `__MACOSX/` archive metadata.
- A duplicate logo file that was byte-identical to `static/images/mapsim-logo.jpeg` and was not referenced by the application.

## Required owner actions before/after publication

- [ ] Revoke and replace any provider API key that was ever included in an archive or commit. Deleting it from the current tree does not revoke it or remove it from Git history.
- [ ] Choose and add an appropriate top-level `LICENSE` if reuse/contributions are intended. No license was invented as part of this cleanup.
- [ ] Configure a private vulnerability-reporting channel in GitHub.
- [ ] Push to a new/clean repository, inspect the tracked file list, and confirm GitHub Actions passes on the target branch.
- [ ] Review Google Gemini model availability, provider terms, third-party notices, and dependency security advisories before production use.

## Validation performed for this package

- Python unit suite: 111 tests passed on Python 3.13 in the packaging environment.
- JavaScript syntax: `node --check static/script.js`.
- Python byte-compilation: `python -m compileall -q main.py prompt_compiler tests`.
- Secret and hygiene scans: checked for provider-key-shaped strings, private-key headers, local absolute user paths, runtime data files, caches, and OS metadata. Replaced a fake test credential that matched the CI secret-detection pattern, so the scanner no longer flags the test fixture as a possible real key.

CI has not been run on GitHub as part of preparing this ZIP. The CI workflow should be considered pending until its first run in the target repository.
