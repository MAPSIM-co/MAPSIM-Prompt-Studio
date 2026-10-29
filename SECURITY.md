# Security Policy

## Supported use

MAPSIM Prompt Studio is designed as a local, single-user utility. It is **not** hardened for public or multi-user deployment. Keep the server bound to `127.0.0.1` unless you have independently added appropriate authentication, TLS, network restrictions, and deployment controls.

## Reporting a vulnerability

Please do not publish API keys, personal prompt-library data, or exploit details in a public issue. Until a private security contact is configured for this repository, avoid including sensitive details in public reports. The repository owner should add a private reporting channel (for example, GitHub Security Advisories) before inviting external contributions.

## If a secret is exposed

1. Revoke the exposed provider credential immediately and create a replacement.
2. Remove the credential from tracked files and local logs.
3. If it was committed, remove it from repository history as well; a new commit that only deletes the key does not erase previous commits.
4. Review provider usage and billing for unexpected activity.
5. Keep `config.json`, `usage.json`, and `library.json` untracked. These may contain a credential or private user data.

## Safe defaults

- The application should listen on loopback by default.
- Supply credentials through `PROMPT_STUDIO_API_KEY` or `GEMINI_API_KEY` where practical.
- Do not commit `.env` files or local configuration/data files.
- Treat all prompts sent to Google Gemini as data shared with a third-party service; do not submit secrets or sensitive information unless appropriate for your use case.
