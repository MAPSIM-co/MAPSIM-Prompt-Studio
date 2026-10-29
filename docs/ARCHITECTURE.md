# Architecture and Developer Notes

## Overview
- `main.py`: compatibility entry point, exported helpers and the loopback-default uvicorn runner.
- `run.sh` / `run.ps1` / `run.bat`: one-command bootstrap and launch for macOS-Linux and Windows; see *Bootstrap and launch contract*.
- `.github/workflows/ci.yml`: runs the launchers on three operating systems, then the static checks and the committed-secret guard.
- `prompt_compiler/app.py`: FastAPI application and router registration.
- `prompt_compiler/api/routes/`: page, model, settings, usage, translation and library endpoints.
- `prompt_compiler/prompt_engine.py`: prompt transformation instructions and output parsing, including the bilingual `persian_analysis` contract and `mirror_analysis`.
- `prompt_compiler/catalog.py`: model catalog, grouping, and the Persian decision metadata (`MODEL_INFO`: class, speed, cost tier, best use, limits, `recommended`) that the model pickers render.
- `prompt_compiler/services/gemini.py`: provider API request logic.
- `prompt_compiler/services/usage.py`: local usage event accounting.
- `prompt_compiler/services/library.py`: saved prompts with tags, favorites, search and editing; the only place that touches `library.json`. `EDITABLE_FIELDS` is the whole write surface of `PATCH /library/{id}`.
- `prompt_compiler/config.py`: project paths, API-key resolution and JSON settings persistence.
- `templates/index.html`: Persian RTL interface.
- `static/style.css`: the single token-driven stylesheet; `:root` holds the dark palette and `[data-theme="light"]` overrides it.
- `static/script.js`: one IIFE — theme, panel state, models, compile, processing overlay, settings, library client and usage rendering.
- `tests/`: automated tests.

## Request flow
The browser submits a Persian prompt to the translation route. The route validates the payload (text, non-empty, within `MAX_INPUT_LENGTH`) and rejects models that cannot generate text before any network call. It then reads configuration, chooses the system prompt and model, calls the Gemini service, parses the model output, records usage, and returns structured data to the browser. Model/network failures are returned as errors, never as a successful prompt.

Saving to the library posts the same shape the compile response produced (`input`, `model`, `parsed`), so the browser never has to reassemble a result.

## Bilingual analysis contract
The compile response carries the English analysis at the top level (`detected_purpose`, `preserved_requirements`, `assumptions`, `missing_information`, `suggestions`) and its Persian mirror in `persian_analysis`. The interface renders two complete halves from those two sources.

`prompt_engine.mirror_analysis(persian, english)` is the single rule that keeps both halves the same length: a missing or short Persian item is filled from the English one, position by position. It runs in the parser, so every response is already mirrored, and again in `library.create_entry`, so entries saved from an older response are mirrored at rest. `script.js` applies the same rule (`mirrorList`) as a last defense for an old server or a hand-edited `library.json`. The fallback only ever replaces absent Persian content; a genuinely empty English group stays empty in both halves.

Cost is presented as a relative tier plus a link to Google's official pricing page rather than invented numbers, and the RPM/TPM/RPD figures are the catalog's recorded ceilings, not the provider's paid quota.

## Library editing contract
`PATCH /library/{id}` accepts exactly `EDITABLE_FIELDS` — `title`, `tags`, `favorite`, `input`, `purpose`, `persian_prompt`, `english_prompt`. Everything else in the body is dropped before the service sees it, so an entry's `id`, `created_at` and stored analysis cannot be rewritten through the editor.

`input` keeps the guards that saving uses: blank is rejected with a Persian message, and so is anything over `MAX_INPUT_LENGTH`; the route turns either into HTTP 400 and leaves the stored entry untouched. When the request text changes, a title the program derived from it is re-derived, while a title the operator typed is kept — `title` is applied after `input`, so an explicit title always wins.

The editor dialog (`#entry-modal`) is the only write path from the browser and sends all five text fields at once, so a half-saved entry is not possible. Editing never calls the provider: analysis groups are stored as they were compiled.

## Front-end contract
- Panels are driven by state, not by class juggling: `usageOpen` and `libraryOpen` decide `hidden`, the `.open` overlay class, the `.usage-closed` grid column, the shared backdrop and the `html.no-scroll` body lock.
- Above 1000px the usage panel is a sticky column inside `#workspace`; below it, an off-canvas overlay. The library is always a modal sheet, and on phones the sheet itself is the only scroll container.
- Dialogs stack: `#entry-modal` sits above `#library-modal` (`z-index: 1100` over `1000`), `activeDialog()` returns the topmost open one so `Tab` stays inside it, `Esc` closes that one only, and closing the library tears the editor down with it.
- Every id the script caches must exist in the template; `test_script_only_reaches_for_ids_that_exist` fails the build when the two drift apart.
- The theme key lives in `localStorage` under the same name in the pre-paint bootstrap and in `script.js`.
- Conversion feedback is one client-only sheet, `#busy-overlay` (`z-index: 1500`, above every dialog and below `#toast` so an error still shows). `startBusy()` / `stopBusy()` own it and no server state is involved: `BUSY_STAGES` schedules the step strip and the status sentence on timers, the elapsed counter ticks once a second, and the final step is set from the resolved response rather than from a timer, so the sheet cannot claim progress that has not happened. `compile()` returns early while `busyActive`, the app shell is made `inert` when supported, and the document keydown handler returns before the dialog logic so `Tab` is held and `Esc` cannot discard an in-flight request. `stopBusy()` runs from the `finally` block, which makes the success and the error path identical.
- The result card renders two symmetrical halves (`#persian-box`, `#english-box`); each half owns its prompt box, purpose line, four analysis lists and expand control, and `is-expanded` is the only class that removes a box's height cap. Both halves use the same `.lang-block` surface, border and padding — `.lang-block-en` repeats the shared tokens rather than introducing a second colour, so direction and font are the only differences.
- The 20,000-character ceiling has one source in the browser, `MAX_INPUT_LENGTH`, and it reaches the operator in three places: `#input-limit` is filled from that constant on load (the template's Persian `۲۰٬۰۰۰` is only the no-JS default), `#input-counter` and `#entry-input-counter` both toggle `over-limit` on every keystroke, and the refusal toasts format the same constant through `faInt()` so no number in the interface depends on the browser's locale data. `.over-limit` is a real CSS rule on both counters — a toggled class with no rule is a silent failure, and it was one here.
- Controls a finger has to hit are at least `--tap` (44px) tall, including the links that sit inside running text (`.note a`, `.mi-price a`, `.field-help a`, `.mapsim-footer a`). Those get invisible `padding-block`, which widens the tap area without moving a line of text, because a 19px line box is not a target on a phone.
- A hung conversion cannot strand the page: the route holds the provider with `httpx.AsyncClient(timeout=180)`, `call_gemini` failures surface as `httpx.HTTPError`, and the `/translate` route turns that into a Persian error message with HTTP 500 — which `compile()` shows in a toast and `stopBusy()` unwinds in its `finally` block.

## Bootstrap and launch contract
`run.sh` (macOS, Linux, WSL) and `run.ps1` (Windows, wrapped by `run.bat` for double-click) are the supported entry points, and both are two implementations of one contract: interpreter floor Python 3.10, virtual environment in `.venv`, dependencies from `requirements.txt`, defaults `127.0.0.1:8000`, and the same `prompt_compiler.app:app` target. `tests/test_http_api.py::LauncherContractTests` asserts that they agree, so the pair cannot drift silently.

Both scripts resolve a Python before creating anything (explicit `--python` / `-Python`, then `PROMPT_STUDIO_PYTHON`, then the usual names, then the common install folders), and they never delete an environment: a `.venv` without a working interpreter is reported with the rename command, not removed. On Windows the environment folder is `.venv` unless `venv\` already exists — the name the previous `run.bat` used — in which case it is reused so an upgrade does not install the dependencies twice, and `-VenvDir` overrides the choice. Dependency installation is keyed on `.venv/.requirements.sha256`, the SHA-256 of `requirements.txt`; an unchanged file skips pip entirely, which is what makes a second launch reach the server in about half a second. Before uvicorn starts, both probe the requested `HOST:PORT` by binding and releasing it, because uvicorn's own "address already in use" traceback is indistinguishable from a crash to an operator — and in this workspace a silently replaced running server would overwrite the last page they were looking at.

`run.bat` carries no logic: it only locates `powershell.exe` and re-invokes `run.ps1` with `-ExecutionPolicy Bypass`, so a machine whose script execution is blocked still has one working path. Neither script reads `config.json` — they test for its existence to decide whether to print the first-run hint — and neither prints the API key, which the guarded test also enforces.

`.github/workflows/ci.yml` deliberately does not import the app. It runs the launchers (`./run.sh --tests`, `.\run.ps1 -Tests`) on ubuntu, macOS and Windows across Python 3.10 and 3.13, then starts the server through the launcher and fetches `/`, `/models`, the stylesheets, the script and the logo. A second job runs `node --check` and `compileall` and fails if `config.json`, `usage.json`, `library.json` or an `AIza…` key appears in the tree. `.gitattributes` is part of the same contract: `*.sh` forced to LF (a CRLF shebang line is a `bad interpreter` error) and `*.bat`/`*.ps1` to CRLF.

## Local development
For local development use the launcher with reload: `./run.sh --reload` (Windows: `.\run.ps1 -Reload`), which is `python -m uvicorn prompt_compiler.app:app --reload --host 127.0.0.1 --port 8000` with the environment already prepared. `python main.py` is equivalent but reads its address from the environment — `PROMPT_STUDIO_HOST` and `PROMPT_STUDIO_PORT` — and parses no command-line flags, so `python main.py --port 8004` keeps port 8000. Run tests with `./run.sh --tests` or `python -m unittest discover -s tests -v` (on `./.venv/bin/python`; the bare interpreter has no FastAPI) and syntax checks with `python -m compileall -q main.py prompt_compiler tests` plus `node --check static/script.js`.

## Change policy
Keep provider-specific integration isolated in `services/`. Preserve compatibility exports in `main.py` unless intentionally deprecating them. Add tests for prompt parsing and route/service behavior when modifying contracts. Keep the dependency set as small as it is now — this project is deliberately framework-free on the front end. Never report tests as passed unless they were executed.
