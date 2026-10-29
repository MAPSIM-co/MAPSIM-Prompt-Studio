# MAPSIM Prompt Studio

A local, MAPSIM-branded prompt-engineering workspace. You write a request in ordinary Persian; the tool sends it to a Google Gemini model and returns an **engineered English prompt** plus a bilingual breakdown of what was preserved, assumed, lost and suggested — with a library to keep every result, a token-usage dashboard, and a light/dark RTL interface.

No database, no build step, no front-end framework, no accounts. The only outbound call is to `generativelanguage.googleapis.com`, and your prompts and API key stay on your machine.

**English** · [فارسی](#راهنمای-فارسی-full-persian-guide)

---

## Contents

- [What you get](#what-you-get)
- [Highlights](#highlights)
- [Requirements](#requirements)
- [Run it with one command](#run-it-with-one-command)
- [First run: connect a model](#first-run-connect-a-model)
- [Launcher options and environment variables](#launcher-options-and-environment-variables)
- [Using the workspace](#using-the-workspace)
- [HTTP API](#http-api)
- [Project layout](#project-layout)
- [Tests, static checks and CI](#tests-static-checks-and-ci)
- [Data files, permissions and privacy](#data-files-permissions-and-privacy)
- [Troubleshooting](#troubleshooting)
- [راهنمای فارسی (Full Persian guide)](#راهنمای-فارسی-full-persian-guide)
- [Provider and licensing notes](#provider-and-licensing-notes)
- [Acknowledgements](#acknowledgements)

| | |
|---|---|
| Version | 2.2.0 |
| Runs on | macOS, Linux, Windows 10/11, WSL |
| Needs | Python 3.10 – 3.13, an internet connection for the first install |
| Start | one command — `./run.sh` (macOS/Linux) or `run.bat` (Windows) |
| Opens at | <http://127.0.0.1:8000> |
| Tests | 111 in-process tests, 0 network calls |
| License | [MIT](LICENSE) — Copyright (c) 2026 MAPSIM.co |

## What you get

```
Persian request                                    Engineered result
"برای سرویس پرداخت ما لاگر رویداد بساز که      ┌─ فارسی  → Persian prompt + purpose
 از کافکا استفاده کند و اطلاعات کاربر را        │          + 4 analysis groups, in Persian
 ذخیره نکند…"                                   ├─ English → English prompt + purpose
        │                                        │          + 4 analysis groups
        ├─ run.sh ─► FastAPI ─► Gemini ─► parsed ─┴─ save ★ to library, copy either half,
        │                                            reload or edit it later
        └─ local usage dashboard (today's tokens, per-model RPM/TPM/RPD)
```

## Highlights

- **Bilingual result card** — the Persian half carries the Persian prompt, purpose and all four analysis groups in Persian; the English half carries the same sections in English. If a model reply omits the Persian mirror, `prompt_compiler.prompt_engine.mirror_analysis` fills it from the English items, so a half is never blank beside a populated one.
- **Processing you can watch** — while the model answers, a MAPSIM sheet covers the workspace: four-step strip, live elapsed counter, input length, model name and the current stage in plain Persian. A slow call never looks frozen, and a second click cannot start a duplicate request.
- **Prompt library** — save any result with tags and a favorite flag, search the stored text (the Persian analysis included), filter by tag, reload it into the workspace, or edit the whole record in a full-size dialog with tall scrolling boxes.
- **Model picker that explains itself** — 42 catalogued models, 13 of which can compile text; usable and unusable models are separate groups, each option names its class in Persian, and the panel below the picker gives speed, cost tier, best use and the recorded RPM/TPM/RPD ceilings with a link to Google's official pricing page.
- **Light and dark themes** — the neon MAPSIM identity, an AA-contrast light palette, the choice persisted in `localStorage`, and applied before first paint so there is no flash of the wrong theme.
- **Responsive down to 360 px** — measured at 360/390/414/521/768/1024/1440/1920 px with zero horizontal overflow and no tap target under 44 px.
- **Token-usage dashboard** — today's request and token totals plus per-model rate-limit meters, polled only while the panel is visible; history is kept for seven days.
- **Secret-safe by default** — the key is never sent to the browser (only a `••••••••last4` mask is), the server binds to `127.0.0.1`, and an environment key always wins over the stored one so nothing needs to be written to disk.
- FastAPI + Jinja2 + vanilla JS/CSS, five pinned dependencies, Persian fonts (Vazirmatn) bundled locally, interactive API docs at `/docs`.

## Requirements

- **Python 3.10 or newer** — 3.10, 3.12 and 3.13 are what this project actually runs on; nothing else needs to be installed.
- **An internet connection** for the first run only, so `pip` can fetch the pinned dependencies, and later for the model call itself.
- **A Google AI Studio API key** — free to create at <https://aistudio.google.com/apikey>. Gemini is the underlying provider; this project is the interface around it.
- ~50 MB of disk for `.venv`. Nothing is written outside the project folder.

## Run it with one command

The launcher is the supported path. It creates the virtual environment, installs the pinned dependencies, checks the port and starts the server — no activation step, no manual `pip install`.

### macOS, Linux, WSL

```bash
git clone <your-repository-url> prompt-studio
cd prompt-studio
./run.sh
```

If you downloaded a ZIP instead of cloning, or the executable bit was lost, run it through the shell instead:

```bash
bash run.sh
```

### Windows 10 / 11

Double-click **`run.bat`**, or from a terminal:

```powershell
cd C:\path\to\prompt-studio
.\run.ps1
```

`run.bat` is a thin wrapper that calls `run.ps1` with `-ExecutionPolicy Bypass`, so it works even when script execution is blocked for PowerShell; passing arguments works too (`run.bat -Port 8005`).

### What the launcher does

| Step | Behaviour |
|---|---|
| 1. Find Python | Tries `PROMPT_STUDIO_PYTHON`, then `python3` / `python` / `py -3`, then the usual install folders. It must be 3.10+; if nothing qualifies, the script prints OS-specific install instructions and stops. |
| 2. Create `.venv` | Runs `python -m venv .venv`. An existing `.venv` is **never** deleted — a broken one is reported, with the rename-and-retry command to fix it. On Windows, a `venv\` folder left by the previous `run.bat` is reused as-is, so upgrading does not reinstall the dependencies. |
| 3. Install dependencies | `pip install -r requirements.txt`, then writes `.venv/.requirements.sha256`. On later runs that hash is compared, so an unchanged `requirements.txt` skips the whole install — the second launch reached the served page in 561 ms when measured. |
| 4. Check the port | Binds `HOST:PORT` once and releases it. If something else is listening, it says so and exits instead of letting uvicorn print a stack trace. |
| 5. Start uvicorn | `python -m uvicorn prompt_compiler.app:app --host 127.0.0.1 --port 8000`, prints the URL, and warns if you are binding to anything other than loopback. Press `Ctrl+C` to stop. |

It also tells you when no API key is configured yet, and never reads `config.json` — only checks that it exists.

### Manual installation (if you prefer)

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn prompt_compiler.app:app --host 127.0.0.1 --port 8000
```

Then open <http://127.0.0.1:8000>.

## First run: connect a model

1. Press **تنظیمات** (Settings) in the header.
2. Paste your key into **کلید API** and choose a model — the recommended default is *Gemini 3.5 Flash*.
3. Save. The page then shows the key as `••••••••last4`; the full value is never returned to the browser again.

To keep the key off disk entirely, export it before starting:

```bash
export PROMPT_STUDIO_API_KEY="your-key"     # GEMINI_API_KEY is accepted too
./run.sh
```

An environment key always wins over the stored one, and the settings panel says which source is in use.

## Launcher options and environment variables

| Option (POSIX) | Option (Windows) | Effect |
|---|---|---|
| `./run.sh --port 8005` | `.\run.ps1 -Port 8005` | start on another port |
| `./run.sh --host 0.0.0.0` | `.\run.ps1 -BindHost 0.0.0.0` | bind elsewhere — the launcher warns, because that exposes your key to the network |
| `./run.sh --python /path/to/python3.12` | `.\run.ps1 -Python C:\Python312\python.exe` | pick the interpreter used to build `.venv` |
| `./run.sh --tests` | `.\run.ps1 -Tests` | install dependencies and run the test suite, then exit |
| `./run.sh --reload` | `.\run.ps1 -Reload` | development mode: restart when a file changes |
| `./run.sh --open` | `.\run.ps1 -Open` | open the page in the default browser once the server answers |
| — | `.\run.ps1 -VenvDir NAME` | build or reuse the virtual environment under another folder name |
| `./run.sh --help` | `.\run.ps1 -Help` | usage |

| Variable | Default | Meaning |
|---|---|---|
| `PROMPT_STUDIO_HOST` | `127.0.0.1` | bind address for `main.py` and for the launchers |
| `PROMPT_STUDIO_PORT` | `8000` | port for `main.py` and for the launchers |
| `PROMPT_STUDIO_PYTHON` | — | interpreter the launcher should use |
| `PROMPT_STUDIO_API_KEY` / `GEMINI_API_KEY` | — | key supplied through the environment; beats `config.json` and is never written to disk |

> `main.py` does **not** parse command-line flags: `python main.py --port 8004` silently keeps 8000. Use the launcher (`./run.sh --port 8004`) or the environment variables (`PROMPT_STUDIO_PORT=8004 python main.py`).

## Using the workspace

1. **Write the request.** The counter under the box shows the live length and the 20,000-character ceiling, and turns red the moment the text is too long to send. `Ctrl`/`⌘ + Enter` starts the conversion; the processing sheet stays up until the answer lands.
2. **Read both halves.** Each half has its own prompt box, purpose line and four analysis lists (*preserved requirements*, *assumptions*, *lost information*, *suggestions*). `بیشتر نمایش بده` / `Expand` releases a box's height cap; each half has its own copy button, plus a copy-both action.
3. **Keep what matters.** `★ ذخیره در کتابخانه` saves the result; the library panel searches text, filters by tag or favorite, loads an entry back into the workspace, and `ویرایش` opens a wide dialog where the stored request and both prompts are edited in tall boxes. Search reads the Persian analysis, so a Persian phrase finds entries that only contain it in Persian.
4. **Watch the budget.** `مصرف توکن` opens today's totals and the per-model RPM/TPM/RPD meters.
5. **Tune the engine.** `تنظیمات` holds the key, the model, and an optional system-prompt override with a contract-safe sample. Leaving the override blank restores the shipped prompt.

Keyboard: `Ctrl`/`⌘ + Enter` converts (and saves inside the library editor); `Esc` closes the top-most panel or dialog but never the processing sheet; `Tab` stays inside an open dialog and is held while a conversion is running.

## HTTP API

Swagger UI: <http://127.0.0.1:8000/docs>. All bodies are UTF-8 JSON unless the route takes a form. Error messages shown to the operator are Persian.

| Method | Path | Purpose | Notes |
|---|---|---|---|
| `GET` | `/` | the workspace page | renders the model choices split into usable/unusable |
| `GET` | `/models` | the model catalog | 42 rows: class, speed, cost tier, best use, RPM/TPM/RPD, Persian reason for non-generating rows |
| `GET` | `/usage` | token dashboard data | today's totals plus per-model minute/day counters |
| `POST` | `/settings` | store key, model, override | form-encoded; an empty key field keeps the stored key, `gemini_api_key=__CLEAR__` deletes it (the Settings dialog does that through its «حذف کلید ذخیره‌شده» checkbox); the reply carries only the mask |
| `POST` | `/translate` | compile a request | body `{"prompt": "…", "model": "…"}`; `400` empty/non-text/non-generating model, `413` over 20,000 characters, `500` with a Persian message when the provider is unreachable (180 s cap) |
| `GET` | `/library` | list/search saved entries | query `q`, `tag`, `favorite`, `limit` (1–500, default 100) |
| `POST` | `/library` | save an entry | `201` with the stored entry |
| `PATCH` | `/library/{id}` | edit an entry | accepts only `title`, `tags`, `favorite`, `input`, `purpose`, `persian_prompt`, `english_prompt`; `id`, `created_at` and the stored analysis cannot be rewritten through it |
| `DELETE` | `/library/{id}` | remove an entry | `404` when the id is unknown |
| `GET` | `/static/*` | CSS, JS, fonts, logo | mounted from `static/` |

## Project layout

```
mapsim-prompt-studio/
├── run.sh                    one-command setup + launch (macOS, Linux, WSL)
├── run.ps1                   one-command setup + launch (Windows)
├── run.bat                   double-click wrapper for run.ps1
├── main.py                   entry point, reads PROMPT_STUDIO_HOST/PORT
├── requirements.txt          five pinned dependencies
├── config.example.json       sanitized settings template
├── prompt_compiler/
│   ├── app.py                FastAPI factory and router registration
│   ├── catalog.py            model catalog (42 rows, 13 text-generation)
│   ├── config.py             paths, config load/save, key masking, env precedence
│   ├── prompt_engine.py      system prompt, output parsing, bilingual mirroring
│   ├── api/routes/           pages, models, usage, settings, translation, library
│   └── services/             gemini HTTP call, library storage, usage storage
├── templates/index.html      the whole workspace, one server-rendered page
├── static/                   style.css, script.js, Vazirmatn fonts, MAPSIM logo
├── tests/                    111 in-process tests
├── docs/                     user manuals (EN + FA), architecture, security notes
├── .gitattributes            LF for `*.sh`, CRLF for `*.bat` / `*.ps1`, binary for fonts and images
└── .github/workflows/ci.yml  launcher + static checks on three operating systems
```

`config.json`, `usage.json` and `library.json` are generated locally and are git-ignored.

## Tests, static checks and CI

```bash
./run.sh --tests                                       # 111 tests, macOS / Linux
.\run.ps1 -Tests                                       # 111 tests, Windows
./.venv/bin/python -m unittest discover -s tests -v    # the same suite directly
./.venv/bin/python -m compileall -q main.py prompt_compiler tests
node --check static/script.js
```

The suite runs in-process through Starlette's `TestClient`: it opens no socket, calls no provider, and redirects `config.json`, `usage.json` and `library.json` to a temporary directory. 55 tests cover the prompt engine and the bilingual mirror; 56 cover the HTTP surface, the library service, the UI contract (stacking order, guards, counters, tap targets) and the launchers themselves.

Use the project virtual environment for the direct command — a bare `python3` without `fastapi` makes `tests/test_http_api.py` fail on import and looks like a regression.

CI (`.github/workflows/ci.yml`) does not import the app: it runs `./run.sh --tests` / `.\run.ps1 -Tests`, then starts the server through the launcher and fetches `/`, `/models` and the static assets on `ubuntu-latest`, `macos-latest` and `windows-latest` across Python 3.10 and 3.13. A separate job checks `node --check`, `compileall`, and fails the build if `config.json`, `usage.json`, `library.json` or an API key ever appears in the tree.

## Data files, permissions and privacy

| File | Contents | Notes |
|---|---|---|
| `config.json` | API key, selected model, system-prompt override | written `0600` through a temp file; **treat as a secret**, it is plain text |
| `library.json` | saved prompts, tags, favorites, analysis | written `0600`; never uploaded |
| `usage.json` | per-request token counters | pruned to the last seven days on each write |
| `config.example.json` | sanitized template | the only one meant for source control |

- The browser never receives the key: `public_config()` exposes only `has_api_key`, a `••••••••last4` mask and which source is active.
- The server binds to `127.0.0.1` by default. `--host 0.0.0.0` (or a LAN address) makes every machine on the network able to spend your key — the launchers warn before doing it.
- Outbound traffic goes to one host, `generativelanguage.googleapis.com`, and only when you press convert.
- Do not commit real keys, usage records or personal prompts. Before publishing, run `git status`, review `git diff --stat` and confirm none of the three local files are staged.

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Something is already listening on 127.0.0.1:8000` then `! Port 8000 is busy` | An older instance is still running. Stop it, or use another port: `./run.sh --port 8005` / `run.bat -Port 8005`. The launcher refuses to start a second server on a taken port rather than letting uvicorn print a stack trace. |
| `python main.py --port 8004` still serves 8000 | `main.py` reads environment variables, not flags. Use `./run.sh --port 8004` or `PROMPT_STUDIO_PORT=8004 python main.py`. |
| The launcher reports no usable Python (`Python 3.10+ is required.`) | Install a modern interpreter — the script prints the matching hint: `brew install python3` (macOS), `sudo apt install -y python3 python3-venv` (Debian/Ubuntu), `dnf install python3` (Fedora), `winget install Python.Python.3.12` (Windows). |
| `'…' is not a usable Python 3.10+ interpreter` | The path you passed to `--python` / `-Python` is not an interpreter or is older than 3.10 — pass a real 3.10+ binary, or drop the flag and let the launcher search. |
| `Could not create the virtual environment` on Debian/Ubuntu | The venv module is a separate package: `sudo apt install -y python3-venv`. |
| Dependency install fails (`pip could not be upgraded…` / `This step needs internet access…`) | `pip` needs internet the first time. Behind a proxy, configure pip and re-run — the app itself needs no connection until you convert. |
| Windows: "running scripts is disabled on this system" | Start with `run.bat`, which passes `-ExecutionPolicy Bypass`, or run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first. |
| `bash ./run.sh: /usr/bin/env bash^M: bad interpreter` | The file was checked out with CRLF (only possible if `.gitattributes` was bypassed, e.g. with `core.autocrlf=true`). Re-clone, or repair: `sed -i 's/\r$//' run.sh` on Linux, `sed -i '' 's/\r$//' run.sh` on macOS. |
| The Persian half repeats the English items | The server is older than 2.2 and cannot return the mirror. Restart it, then hard-reload the page so the new `style.css` and `script.js` are fetched. |
| «اتصال به سرویس Google AI Studio برقرار نشد» | The machine cannot reach `generativelanguage.googleapis.com` (DNS, proxy, firewall, regional block). The sheet gives up after 180 seconds and the button returns. |
| «این مدل پرامپت متنی تولید نمی‌کند» | A non-generating catalog row (image, embedding, video) was selected. Pick one from the usable group. |
| "Request too long" / «درخواست از ۲۰٬۰۰۰ نویسه بیشتر است» | Split the request or remove pasted boilerplate; the counter under the box turns red before you press convert. |
| The processing sheet stays for a long time | The request is still in flight — the elapsed counter proves it. It cannot be dismissed on purpose (`Esc` is ignored, the page behind is `inert`); after 180 s the call is abandoned and a Persian error is shown. |
| Settings saved but the key still missing | An environment key overrides the stored one. `unset PROMPT_STUDIO_API_KEY GEMINI_API_KEY`, or clear the field in Settings. |

---

## راهنمای فارسی (Full Persian guide)

> متأسفانه رابط کاربری این ابزار کاملاً فارسی است، اما این راهنما برای کسانی نوشته شده که می‌خواهند پروژه را از گیت‌هاب بخوانند یا روی سیستم خود اجرا کنند. نسخهٔ کامل راهنمای کاربر فارسی در فایل [`docs/USER_MANUAL_FA.md`](docs/USER_MANUAL_FA.md) آمده است.

### این ابزار چه می‌کند؟

نقشه‌ٔ کاربری فارسی‌زبان برای مهندسی پرامپت. شما درخواست خود را به فارسیِ ساده می‌نویسید؛ برنامه آن را به مدل گوگل (Gemini) می‌فرستد و در برابر، **پرامپت انگلیسیِ مهندسی‌شده** را همراه با چهار گروه تحلیل (نکات حفظ‌شده، فرض‌ها، اطلاعات از دست رفته، پیشنهادها) نشان می‌دهد. هر دو بخش فارسی و انگلیسی کامل هستند، می‌توانید هر کدام را جداگانه کپی کنید، و نتیجه را در کتابخانهٔ محلی ذخیره، جست‌وجو ویرایش یا بارگذاری کنید.

هیچ دیتابیس، هیچ حساب کاربری و هیچ سرویس جانبی‌ای در کار نیست. تنها ارتباط بیرونی با `generativelanguage.googleapis.com` و فقط وقتی رخ می‌دهد که دکمهٔ «تبدیل کن» را می‌زنید.

### پیش‌نیازها

- **پایتون ۳.۱۰ یا جدیدتر** (روی ۳.۱۰، ۳.۱۲ و ۳.۱۳ آزمایش شده است). نصب هر چیز دیگری لازم نیست.
- **اینترنت** برای بار اول (برای نصب پکیج‌ها) و هنگام تبدیل درخواست‌ها.
- **کلید Google AI Studio** از نشانی <https://aistudio.google.com/apikey>.

### نصب و اجرا با یک دستور

**مک یا لینوکس (و WSL):**

```bash
git clone <نشانی مخزن> prompt-studio
cd prompt-studio
./run.sh
```

اگر پروژه را به‌صورت ZIP دانلود کرده‌اید یا اجازهٔ اجرا گرفته‌اید: `bash run.sh`.

**ویندوز:** فایل **`run.bat`** را دوبار کلیک کنید، یا در ترمینال:

```powershell
cd C:\path\to\prompt-studio
.\run.ps1
```

دستور اجرا خودش محیط مجازی `.venv` را می‌سازد، وابستگی‌ها را نصب می‌کند، پورت را بررسی می‌کند و سرور را روشن می‌کند. بار دوم نصب دوباره انجام نمی‌شود (تا وقتی `requirements.txt` تغییر نکرده باشد) و برنامه در حدود یک ثانیه بالا می‌آید. اگر پوشهٔ `.venv` خراب باشد، هرگز پاکش نمی‌کند؛ می‌گوید چه کار کنید.

پس از بالا آمدن، نشانی <http://127.0.0.1:8000> را در مرورگر باز کنید.

### اولین اجرا: وصل کردن مدل

۱. دکمهٔ **تنظیمات** را در نوار بالا بزنید.
۲. کلید خود را در فیلد **کلید API** بچسبانید و یک مدل انتخاب کنید (پیشنهاد پیش‌فرض: *Gemini 3.5 Flash*).
۳. ذخیره کنید. از این پس کلید فقط به‌صورت `••••••••۴رقمِ آخر` نمایش داده می‌شود و مقدار کامل هرگز به مرورگر برنمی‌گردد.

برای اینکه کلید اصلاً روی دیسک نرود، پیش از اجرا آن را در متغیر محیطی بگذارید؛ کلید محیطی همیشه بر کلید ذخیره‌شده اولویت دارد:

```bash
export PROMPT_STUDIO_API_KEY="کلید-شما"     # GEMINI_API_KEY هم پذیرفته می‌شود
./run.sh
```

### گزینه‌های اجرا

| دستور | کار |
|---|---|
| `./run.sh --port 8005` یا `.\run.ps1 -Port 8005` | اجرای روی پورت دیگر |
| `./run.sh --host 0.0.0.0` یا `.\run.ps1 -BindHost 0.0.0.0` | در دسترس قرار دادن برای شبکه — برنامه هشدار می‌دهد، چون کلید شما را در دسترس دیگران می‌گذارد |
| `./run.sh --python /usr/bin/python3.12` یا `.\run.ps1 -Python C:\Python312\python.exe` | انتخاب مفسری که `.venv` با آن ساخته می‌شود |
| `./run.sh --tests` یا `.\run.ps1 -Tests` | نصب وابستگی‌ها و اجرای آزمون‌ها |
| `./run.sh --reload` یا `.\run.ps1 -Reload` | حالت توسعه؛ با تغییر فایل‌ها سرور ری‌استارت می‌شود |
| `./run.sh --open` یا `.\run.ps1 -Open` | باز کردن خودکار صفحه در مرورگر |
| `.\run.ps1 -VenvDir NAME` (فقط ویندوز) | ساخت یا استفادهٔ مجدد از محیط مجازی در پوشه‌ای با نام دیگر |
| `./run.sh --help` یا `.\run.ps1 -Help` | نمایش راهنما |

متغیرهای محیطی: `PROMPT_STUDIO_HOST` (پیش‌فرض `127.0.0.1`)، `PROMPT_STUDIO_PORT` (پیش‌فرض `8000`)، `PROMPT_STUDIO_PYTHON`، `PROMPT_STUDIO_API_KEY` و `GEMINI_API_KEY`.

> فایل `main.py` گزینهٔ خط فرمان را نمی‌خواند: `python main.py --port 8004` بی‌صدا روی همان ۸۰۰۰ می‌ماند. برای تغییر پورت از `./run.sh --port 8004` یا `PROMPT_STUDIO_PORT=8004 python main.py` استفاده کنید.

### کار با محیط

۱. درخواست را در کادر ورودی بنویسید. شمارنده زیر کادر طول متن و سقف **۲۰٬۰۰۰ نویسه** را نشان می‌دهد و به‌محض بلند شدن متن قرمز می‌شود. با `Ctrl`/`⌘ + Enter` تبدیل آغاز می‌شود و ورقهٔ پردازش تا رسیدن پاسخ روی صفحه می‌ماند.
۲. خروجی دو بخش کامل دارد: بخش فارسی و بخش انگلیسی. هر بخش کادر پرامپت، هدف و چهار فهرست تحلیل خودش را دارد؛ دکمهٔ «بیشتر نمایش بده» محدودیت ارتفاع را برمی‌دارد و هر بخش دکمهٔ کپی مستقل دارد.
۳. با «★ ذخیره در کتابخانه» نتیجه را نگه دارید. کتابخانه جست‌وجوی متن (شامل تحلیل فارسی)، فیلتر برچسب و علاقه‌مندی، بارگذاری دوباره و «ویرایش» دارد؛ ویرایش در یک پنجرهٔ بزرگ با کادرهای بلند انجام می‌شود، نه یک فیلد تک‌خطی.
۴. «مصرف توکن» جمع درخواست‌ها و توکن‌های امروز و شمارنده‌های RPM/TPM/RPD هر مدل را نشان می‌دهد. تاریخچه هفت روز نگه داشته می‌شود.
۵. در «تنظیمات» می‌توانید مدل را عوض کنید، کلید را بچرخانید، یا پرامپت سیستم را دست‌کاری کنید؛ اگر آن را خالی بگذارید، متن پیش‌فرض بازمی‌گردد.

### فایل‌های محلی و حریم خصوصی

- `config.json`: کلید API، مدل انتخابی و پرامپت سیستم. با مجوز `0600` نوشته می‌شود و چون متنِ ساده است باید مانند یک راز با آن رفتار شود.
- `library.json`: پرامپت‌ها، برچسب‌ها و تحلیل‌های ذخیره‌شده — هرگز جایی بارگذاری نمی‌شود.
- `usage.json`: شمارش توکن‌ها، فقط برای هفت روز گذشته.
- هر سه فایل در `.gitignore` هستند؛ تنها `config.example.json` برای انتشار است.
- پیش‌فرض سرور فقط روی `127.0.0.1` گوش می‌دهد. روشن کردن آن روی شبکه یعنی هر رایانهٔ هم‌شبکه می‌تواند با کلید شما کار کند.

### عیب‌یابی

| مشکل | راه‌حل |
|---|---|
| پیام `Something is already listening on 127.0.0.1:8000` و سپس `! Port 8000 is busy` | نسخهٔ قبلی هنوز اجراست؛ آن را متوقف کنید یا `./run.sh --port 8005` / `run.bat -Port 8005` بزنید. برنامه عمداً روی پورت اشغال‌شده دومین سرور را بالا نمی‌آورد. |
| `python main.py --port 8004` باز هم ۸۰۰۰ می‌دهد | `main.py` گزینه نمی‌خواند؛ از دستور اجرا یا `PROMPT_STUDIO_PORT` استفاده کنید. |
| پیام `Python 3.10+ is required.` (پایتون پیدا نشد) | اسکریپت خودش راهنمای نصب را چاپ می‌کند: `brew install python3` (مک) / `sudo apt install -y python3 python3-venv` (دبیان و اوبونتو) / `sudo dnf install python3` (فدورا) / `winget install Python.Python.3.12` (ویندوز). |
| پیام `'…' is not a usable Python 3.10+ interpreter` | مسیری که به `--python` یا `-Python` داده‌اید مفسر نیست یا نسخه‌اش از ۳.۱۰ قدیمی‌تر است؛ مسیر درست بدهید یا گزینه را حذف کنید تا خودِ اسکریپت بگردد. |
| در اوبونتو ساخت `.venv` شکست خورد | `sudo apt install -y python3-venv` |
| نصب پکیج‌ها خطا داد | بار اول به اینترنت نیاز دارد (`pip could not be upgraded` / `This step needs internet access`). پشت پروکسی pip را تنظیم و دوباره اجرا کنید؛ خودِ برنامه تا زمان تبدیل به شبکه نیاز ندارد. |
| در ویندوز اجرای اسکریپت ممنوع است | از `run.bat` استفاده کنید (خودش `-ExecutionPolicy Bypass` می‌دهد) یا پیشتر `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` بزنید. |
| خطای `bad interpreter` در لینوکس یا مک | فایل با خطوط ویندوزی (CRLF) چک‌اوت شده؛ دوباره کلون کنید یا تعمیرش کنید: روی لینوکس `sed -i 's/\r$//' run.sh` و روی مک `sed -i '' 's/\r$//' run.sh`. |
| بخش فارسی عین متن انگلیسی است | سرور قدیمی‌تر از نسخهٔ ۲.۲ است؛ آن را ری‌استارت کنید و صفحه را با `Ctrl+Shift+R` دوباره بار بگیرید. |
| «اتصال به سرویس Google AI Studio برقرار نشد» | دسترسی به `generativelanguage.googleapis.com` را (DNS، پروکسی، فایروال) بررسی کنید. مهلت درخواست ۱۸۰ ثانیه است؛ بعد از آن رها و همین پیام فارسی نشان داده می‌شود. |
| «این مدل پرامپت متنی تولید نمی‌کند» | یکی از مدل‌های تصویر/سازِ ویدیو/جاسازی انتخاب شده؛ از گروه مدل‌های قابل استفاده انتخاب کنید. |
| درخواست بلندتر از حد مجاز | متن را بشکنید یا boilerplate چسبانده‌شده را بردارید؛ شمارنده پیش از زدن دکمه قرمز می‌شود. |
| ورقهٔ پردازش مدت زیادی روی صفحه می‌ماند | درخواست هنوز در جریان است — شمارندهٔ زمانِ جاری این را ثابت می‌کند. عمداً بسته نمی‌شود (`Esc` بی‌اثر است و پشت صفحه `inert` است)؛ بعد از ۱۸۰ ثانیه رها و پیام فارسی نشان داده می‌شود. |
| کلید ذخیره شد ولی دوباره خواسته شد | یک کلید محیطی بر ذخیرهٔ دیسک اولویت دارد؛ `unset PROMPT_STUDIO_API_KEY GEMINI_API_KEY`، یا در تنظیمات گزینهٔ حذف کلید را بزنید. |

### آزمون‌ها

```bash
./run.sh --tests        # ۱۱۱ آزمون
.\run.ps1 -Tests
```

همهٔ آزمون‌ها درونِ خودِ پروسه (in-process) اجرا می‌شوند: هیچ سوکتی باز نمی‌شود، هیچ درخواستی به گوگل فرستاده نمی‌شود، و فایل‌های محلی به پوشهٔ موقت منتقل می‌شوند تا اطلاعات کاربر دست‌نخورده بماند.

### یادداشت ارائه‌دهنده و مجوز

برند و لوگوی MAPSIM برای این پروژه است؛ گوگل جمنای فقط ارائه‌دهندهٔ API است و صاحب این رابط نیست — ابزار تنها از نقطهٔ عمومی `generateContent` آن استفاده می‌کد. کتابخانه‌های شخص ثالث و فایل‌های فونت Vazirmatn زیر مجوز خودشان می‌آیند و اعلان‌های بالادستی را حذف نکنید. مجوز خودِ این منبع، **MIT** (Copyright (c) 2026 MAPSIM.co) است و در فایل [`LICENSE`](LICENSE) ریشهٔ مخزن آمده است: می‌توانید آن را استفاده، کپی، تغییر و توزیع کنید — حتی تجاری — به شرطی که اعلان کپی‌رایت و مجوز همراهش بماند.

---

## Provider and licensing notes

MAPSIM branding and the supplied logo are used for this project. Google Gemini remains the underlying API provider, not the product owner or brand of this interface — the tool only calls its public `generateContent` endpoint.

Third-party libraries (FastAPI, Starlette, Uvicorn, httpx, Jinja2, python-multipart) and the bundled Vazirmatn font files remain subject to their respective licenses; do not remove applicable upstream license notices when redistributing them. This project's own source is released under the [MIT License](LICENSE) (Copyright (c) 2026 MAPSIM.co), which is the file at the top of this repository — you may use, copy, modify and redistribute it, including commercially, as long as the copyright and permission notice travel with it.

## Acknowledgements

Built as part of the MAPSIM trading-tools workspace. If this repository helps you, the most useful contributions are Persian wording corrections from real operators, model-catalog updates with dated sources, and test coverage for the library editor.
