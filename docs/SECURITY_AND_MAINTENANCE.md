# Security and Maintenance

## Sensitive files
`config.json` may contain a live API key, `library.json` holds the operator's own requests and prompts, and `usage.json` holds request metadata. All three are ignored by git and written atomically with owner-only (`0600`) permissions. Keep them out of public source control; `config.example.json` is the file meant to be committed. Rotate a key immediately if it is exposed.

## API key handling
- The stored key is never rendered into HTML or returned by any endpoint; the page only sees `has_api_key`, a source label and a mask that reveals at most the last four characters.
- The key travels to Google in the `x-goog-api-key` header, never in a query string.
- `PROMPT_STUDIO_API_KEY` (then `GEMINI_API_KEY`) take precedence over the stored key, so a shared machine can run without writing secrets to disk.
- In the settings form an empty key field means "keep what is stored"; only the explicit remove option clears it.

## Request guards
Input longer than 20,000 characters is refused in the browser and again on the server — when converting, when saving to the library and when editing a saved request. Non-text payloads are rejected, models that cannot return text are refused before any call, and the library is capped at 500 entries. `PATCH /library/{id}` reads only the fields the editor writes (`title`, `tags`, `favorite`, `input`, `purpose`, `persian_prompt`, `english_prompt`) and drops anything else, so a body cannot overwrite an entry's id, creation time or stored analysis.

## Network exposure
`main.py` binds to `127.0.0.1` unless `PROMPT_STUDIO_HOST` says otherwise, and so do the launchers unless `--host` / `-BindHost` is passed. Avoid `0.0.0.0` on untrusted networks unless authentication, TLS, access controls, and deployment hardening have been implemented — an open port on a café network means any peer can spend your API key through this page. Both launchers print a warning before binding to a non-loopback address.

## Installation and launch scripts
`run.sh`, `run.ps1` and `run.bat` write only inside the project folder: `.venv/` and the `.venv/.requirements.sha256` marker. They never delete an existing environment, never run anything as root, never pipe a remote script into a shell, and never read `config.json` — they only test whether it exists so they can decide whether to print the first-run hint. Dependency installation is the one step that needs outbound access (PyPI), and it is skipped whenever `requirements.txt` is unchanged, which also keeps a reinstall from silently pulling different packages.

`.github/workflows/ci.yml` installs and starts the app through those same scripts on three operating systems, and fails the build when `config.json`, `usage.json`, `library.json` or an API-key-shaped string is present in the tree. Treat that job as the pre-publish check for a repository that is meant to be cloned by strangers.

## Dependencies
Dependencies are pinned in `requirements.txt`: FastAPI, uvicorn, Jinja2, python-multipart and httpx. Because the pins are exact, a first install is reproducible; transitive packages still resolve to their latest compatible versions, so re-check them after any change and record what you tested. The front end is plain CSS and JavaScript with no build step — adding a framework would be a deliberate architecture change, not a convenience. Review provider model availability and dependency security advisories before production use. The current application should be treated as a local utility, not as a hardened multi-user service.

## Data lifecycle
Usage history is pruned to the last seven days on write. The library keeps the 500 most recent entries and drops the oldest. Back up only what is needed, remove old records according to your retention needs, and do not share logs or `library.json` without reviewing their contents.

## Brand and third-party notices
MAPSIM branding identifies this customized distribution. The underlying Google Gemini API remains a third-party service. Retain all applicable upstream licenses and notices for dependencies and bundled assets.


## Public repository release hygiene

Do not track `config.json`, `usage.json`, `library.json`, `.env`, virtual environments, logs, or local cache files. The checked-in `config.example.json` must contain an empty API key. If a credential appears in a ZIP, commit, issue, or log, revoke it at the provider immediately and review usage. If it was committed, remove it from Git history too; a normal follow-up deletion is not enough.

The project currently has no top-level `LICENSE`. Do not infer a license from public repository visibility. The owner must select a license before granting reuse rights or soliciting contributions. See `SECURITY.md` and `docs/PUBLIC_REPOSITORY_READINESS.md`.
