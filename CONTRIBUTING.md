# Contributing

Thanks for considering a contribution to MAPSIM Prompt Studio.

## Before opening a pull request

1. Keep the application local-first and preserve the loopback-only default.
2. Never include API keys, `.env` files, `config.json`, `usage.json`, `library.json`, logs, virtual environments, or machine-specific paths.
3. Add or update tests for behavior changes.
4. Run the checks below from the repository root.

```bash
./run.sh --tests
node --check static/script.js
python -m compileall -q main.py prompt_compiler tests
```

On Windows, use `run.bat -Tests` or `run.ps1 -Tests` as documented in the README. The application does not need a provider API key to run its in-process test suite.

## Pull request notes

Describe the user-visible change, security implications, and any manual checks that were not automated. Do not attach real user prompt-library data or credentials.

## Licensing

A top-level project license has not been selected. Until the repository owner adds one, do not assume that public visibility grants permission to reuse, modify, or redistribute the project.
