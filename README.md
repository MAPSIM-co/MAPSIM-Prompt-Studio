# MAPSIM Prompt Studio

<p align="center">
  <img src="static/images/mapsim-logo.jpeg" alt="MAPSIM Prompt Studio logo" width="180">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Interface-Persian%20%2B%20English-8A2BE2" alt="Persian and English interface">
  <img src="https://img.shields.io/badge/Platforms-macOS%20%7C%20Linux%20%7C%20Windows-555" alt="Supported platforms">
</p>

**MAPSIM Prompt Studio** is a local, MAPSIM-branded prompt-engineering workspace. Write a request in natural Persian, send it to a Google Gemini model, and receive an engineered English prompt together with a bilingual analysis of preserved requirements, assumptions, missing information, and suggestions.

The application also includes a prompt library, token-usage dashboard, model catalogue, and responsive light/dark interface with right-to-left (RTL) support.

- No database server or user account is required.
- No front-end build step or JavaScript framework is required.
- The launcher creates a local Python virtual environment and installs the required dependencies.
- The application contacts Google's Gemini API when you submit a conversion request.
- Your API key is sent to Google for authentication. Do not submit confidential information unless you are comfortable sharing it with the API provider.

**English** · [راهنمای فارسی](#راهنمای-فارسی)

> **Public repository security:** Never commit `config.json`, `.env`, `usage.json`, or `library.json`. These are local files and may contain credentials or private prompt data. The repository should contain only the sanitized `config.example.json`. If a real API key has been exposed, revoke it with the provider. Deleting the exposed file does not invalidate the key.

> **License status:** This project does not currently include a top-level `LICENSE` file. Public visibility does not automatically grant permission to use, modify, or redistribute the code. The repository owner should select and add a license before inviting contributions or redistribution. See [Public Repository Readiness](docs/PUBLIC_REPOSITORY_READINESS.md).

---

## Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Quick start](#quick-start)
- [Optional Linux system service](#optional-linux-system-service)
- [Logging and disk usage](#logging-and-disk-usage)
- [First-time configuration](#first-time-configuration)
- [Launcher options and environment variables](#launcher-options-and-environment-variables)
- [Using the workspace](#using-the-workspace)
- [HTTP API](#http-api)
- [Project structure](#project-structure)
- [Tests and continuous integration](#tests-and-continuous-integration)
- [Local data, permissions, and privacy](#local-data-permissions-and-privacy)
- [Troubleshooting](#troubleshooting)
- [راهنمای فارسی](#راهنمای-فارسی)
- [Provider, third-party software, and licensing](#provider-third-party-software-and-licensing)
- [Acknowledgements](#acknowledgements)

## Project information

| Item | Details |
|---|---|
| Version | 2.2.0 |
| Platforms | macOS, Linux, Windows 10/11, and WSL |
| Python | 3.10 or newer; see the compatibility note below |
| Initial setup | Internet access is required to install Python packages |
| Model conversion | Internet access and a Google AI Studio API key are required |
| Start | `./run.sh` on macOS/Linux/WSL, or `run.bat` on Windows |
| Local address | `http://127.0.0.1:8000` |
| Automated tests | The project documentation reports 111 tests; run the test command to verify the current checkout |

> **Compatibility note:** The project description supplied with this release identifies Python 3.10–3.13 as supported/tested. Confirm the current CI matrix and dependency constraints before advertising support for additional Python versions.

## Overview

A typical workflow looks like this:

```text
Persian request
      |
      v
Local MAPSIM Prompt Studio
      |
      v
FastAPI application
      |
      v
Google Gemini API
      |
      v
Structured result
      |
      +--> Persian engineered prompt and analysis
      |
      +--> English engineered prompt and analysis
      |
      +--> Save, search, edit, reload, or copy from the local library

Local usage dashboard
(request totals, token totals, and model rate-limit counters)
```

The application sends the submitted prompt and the selected model request to Google's Gemini API. The prompt library and usage data are stored locally in the project directory.

## Features

- **Bilingual result:** The Persian and English result sections each contain an engineered prompt, purpose, and four analysis groups: preserved requirements, assumptions, missing information, and suggestions.
- **Processing status:** A processing panel displays the current stage, elapsed time, input length, and selected model while a conversion is running. It prevents a second conversion from being started while the first is active.
- **Prompt library:** Save results with titles, tags, and favorites. Search saved content, filter by tag or favorite status, reload an entry, or edit it.
- **Model catalogue:** Browse available models and their recorded capabilities, speed, cost tier, recommended use, and rate limits. The actual model list and availability depend on the catalogue shipped with the installed version.
- **Light and dark themes:** Switch themes; the preference is stored in browser `localStorage`.
- **Responsive interface:** The interface is designed for desktop and mobile screen sizes and supports Persian right-to-left text.
- **Token-usage dashboard:** Review daily request and token totals and per-model rate-limit counters. The supplied implementation describes a seven-day usage-history window.
- **Local key handling:** The API key is not returned to the browser. The interface displays a masked value. An environment variable takes precedence over a key stored in the local configuration file.
- **Local web interface:** FastAPI, Jinja2, and vanilla JavaScript/CSS are used. API documentation is available at `/docs`.

## Requirements

1. **Python 3.10 or newer.** The launcher searches for an eligible interpreter. The exact supported versions are determined by the project's dependencies and CI configuration.
2. **Internet access for initial setup.** The launcher uses `pip` to download the Python dependencies. Internet access is also required when sending a request to Gemini.
3. **A Google AI Studio API key.** Create a key at <https://aistudio.google.com/apikey>. The key is required for model conversion, but not necessarily to start the local interface.
4. **Disk space.** The virtual environment and installed dependencies require additional disk space. The actual size depends on the operating system and Python installation.

No separate database server, Node.js installation, or front-end build tool is required by the described application.

## Quick start

The launcher is the recommended installation and startup method. It creates or reuses the project's virtual environment, installs dependencies when needed, checks the selected port, and starts the local web server.

### macOS, Linux, and WSL

If you are cloning the repository:

```bash
git clone https://github.com/MAPSIM-co/MAPSIM-Prompt-Studio.git
cd MAPSIM-Prompt-Studio
chmod +x run.sh
./run.sh
```

Replace `<repository-url>` with the actual URL of the Git repository.

If you downloaded and extracted a ZIP archive, open a terminal in the extracted project directory and run:

```bash
bash run.sh
```

Using `bash run.sh` does not require the executable permission bit to be set.

### Windows 10 and Windows 11

The simplest option is to double-click:

```text
run.bat
```

Alternatively, open PowerShell in the project directory and run:

```powershell
.\run.ps1
```

`run.bat` is intended as a Windows command-prompt/double-click entry point. It invokes the PowerShell launcher. If you use `run.ps1` directly and Windows blocks script execution, use `run.bat` or follow the PowerShell execution-policy guidance in [Troubleshooting](#troubleshooting).

### After startup

Open this address in your browser:

<http://127.0.0.1:8000>

The server runs locally on the computer by default. Keep the terminal window open while using the interactive launcher. Press `Ctrl+C` in that terminal to stop it.

### What the launcher does

The launcher is designed to perform the setup steps automatically:

1. **Find Python:** It searches for an eligible interpreter, including configured paths and common executable names.
2. **Create or reuse the virtual environment:** It creates `.venv` if needed. An existing environment should not be deleted automatically.
3. **Install dependencies:** It installs the pinned packages from `requirements.txt` when the dependency file changes or the environment needs setup.
4. **Check the port:** It checks whether the selected host and port are already in use and reports a conflict.
5. **Start the server:** It launches the FastAPI application through Uvicorn and prints the local URL.

The exact search order, dependency-hash behavior, and recovery messages are implemented in `run.sh` and `run.ps1`. If those scripts change, update this section to match them.

## Optional Linux system service

On Linux systems that use **systemd**, you can install MAPSIM Prompt Studio as a background service. A system service can start automatically at boot and continue running after you close the terminal.

Run the installer from the project directory as the normal Linux user who owns the project. **Do not run the installer script itself with `sudo`.** The script should request elevated privileges only for system-level service installation steps.

```bash
./install_service.sh
```

If the script does not have executable permission:

```bash
bash install_service.sh
```

To install the service on a different port:

```bash
PROMPT_STUDIO_PORT=8005 ./install_service.sh
```

The installer is expected to prepare the Python environment, create the systemd unit, enable the service at boot, and start it. Review the script before running it, especially on a production machine.

### Manage the service

Check service status:

```bash
sudo systemctl status mapsim-prompt-studio
```

Start or restart the service:

```bash
sudo systemctl start mapsim-prompt-studio
sudo systemctl restart mapsim-prompt-studio
```

Stop the service:

```bash
sudo systemctl stop mapsim-prompt-studio
```

View warnings and errors recorded today:

```bash
sudo journalctl -u mapsim-prompt-studio -p warning --since today
```

Follow new warning and error messages:

```bash
sudo journalctl -u mapsim-prompt-studio -p warning -f
```

Remove the service:

```bash
./uninstall_service.sh
```

Or, if executable permission is not set:

```bash
bash uninstall_service.sh
```

The uninstaller should remove the systemd unit without deleting the project directory, virtual environment, API key, prompt library, or usage data. Confirm this behavior in `uninstall_service.sh` before using it on a machine containing important local data.

> **Service URL:** The default service configuration is intended to listen on `127.0.0.1`, normally at `http://127.0.0.1:8000`. If you choose a different port, use that port in the browser address. Do not expose the service to a public or shared network without adding appropriate authentication and network protection.

## Logging and disk usage

The project is intended to keep routine logging and local storage modest:

- Uvicorn access logging can be disabled so ordinary page requests do not generate a log entry each time.
- In systemd mode, service output can be limited to warnings and errors. The system journal may also apply rate limits.
- Python bytecode generation can be disabled for the service to avoid creating `__pycache__` directories during service operation.
- The launcher does not need a separate, continuously growing application log file.
- Usage history is described as limited to the most recent seven days.
- Saved prompt-library records remain until the user deletes them. Review and remove old records from the application if local data storage needs to be reduced.
- The `.venv` directory contains the installed Python dependencies. Removing it frees disk space, but the dependencies must be installed again before the next launch.

### Important: system journal retention

The system journal is managed by Linux, not by MAPSIM Prompt Studio. Application-level log filtering does not set a guaranteed maximum size for the entire system journal.

A Linux administrator can inspect journal disk usage with:

```bash
sudo journalctl --disk-usage
```

To request removal of archived journal data older than a specified period:

```bash
sudo journalctl --vacuum-time=7d
```

To limit archived journal storage by size:

```bash
sudo journalctl --vacuum-size=200M
```

These commands affect the system journal and may remove logs belonging to other services. Use them only if you understand the machine's log-retention requirements. For a persistent system-wide limit, configure `SystemMaxUse` and, where appropriate, `SystemKeepFree` in the systemd journald configuration, then restart `systemd-journald` according to your distribution's documentation.

## First-time configuration

1. Open MAPSIM Prompt Studio in your browser.
2. Select **تنظیمات (Settings)** in the application header.
3. Paste your Google AI Studio key into the **کلید API (API Key)** field.
4. Select a text-generation model.
5. Save the settings.

The interface should display a masked key after saving. The full key should not be returned to the browser.

### Use an environment variable instead of storing the key in the application configuration

On macOS and Linux:

```bash
export PROMPT_STUDIO_API_KEY="your-api-key"
./run.sh
```

`GEMINI_API_KEY` may also be accepted by the application. Use the environment variable name supported by the installed version. An environment-provided key is intended to take precedence over a key stored in `config.json`.

Environment variables set in a terminal apply to processes started from that terminal. For a systemd service, follow the service script's supported environment configuration method; exporting a variable in an unrelated terminal will not automatically pass it to the service.

> Never paste an API key into a public issue, screenshot, source file, or shared terminal transcript.

## Launcher options and environment variables

The following options are documented by the supplied launcher interface. Confirm them against `run.sh` and `run.ps1` if you are using a modified version.

| Purpose | macOS/Linux/WSL (`run.sh`) | Windows PowerShell (`run.ps1`) |
|---|---|---|
| Use another port | `./run.sh --port 8005` | `.\run.ps1 -Port 8005` |
| Select bind address | `./run.sh --host 127.0.0.1` | `.\run.ps1 -BindHost 127.0.0.1` |
| Select Python interpreter | `./run.sh --python /path/to/python3.12` | `.\run.ps1 -Python C:\Python312\python.exe` |
| Run tests | `./run.sh --tests` | `.\run.ps1 -Tests` |
| Enable development reload | `./run.sh --reload` | `.\run.ps1 -Reload` |
| Open browser automatically | `./run.sh --open` | `.\run.ps1 -Open` |
| Show help | `./run.sh --help` | `.\run.ps1 -Help` |
| Choose virtual-environment directory | Check `run.sh --help` | `.\run.ps1 -VenvDir NAME` |

Environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `PROMPT_STUDIO_HOST` | `127.0.0.1` | Bind address |
| `PROMPT_STUDIO_PORT` | `8000` | Listening port |
| `PROMPT_STUDIO_PYTHON` | Automatic detection | Python interpreter for the launcher |
| `PROMPT_STUDIO_API_KEY` | Not set | API key supplied through the environment |
| `GEMINI_API_KEY` | Not set | Alternative API-key variable, if supported by the installed version |

> **Security warning:** Binding to `0.0.0.0` makes the service reachable through network interfaces. Do not use this setting on an untrusted network unless you have configured suitable access controls, firewall rules, and authentication. The default loopback address (`127.0.0.1`) is safer for a single-user local installation.

> **Entry-point note:** The supplied project description says that `main.py` reads `PROMPT_STUDIO_HOST` and `PROMPT_STUDIO_PORT` rather than parsing command-line flags. Therefore, use the launcher options or environment variables instead of assuming `python main.py --port 8004` will change the port.

## Using the workspace

1. **Write a request.** Enter the task in the input area. The character counter shows the input length and the documented 20,000-character limit. Use `Ctrl+Enter` or `⌘+Enter` to start conversion.
2. **Review both outputs.** Read the Persian and English prompts, purpose statements, and analysis groups. Expand a section if its content is truncated.
3. **Copy the result.** Use the copy control for an individual language or the control for copying both outputs, where available.
4. **Save useful results.** Save an entry to the local prompt library. Add tags or mark it as a favorite to make it easier to find later.
5. **Search and edit the library.** Search saved content, filter entries, reload an entry, or edit it.
6. **Review usage.** Open the token-usage panel to view request totals, token totals, and the available model rate-limit counters.
7. **Configure the model.** Use Settings to manage the API key, selected model, and any supported system-prompt override.

### Keyboard shortcuts

The supplied interface documents these shortcuts:

- `Ctrl+Enter` / `⌘+Enter`: start conversion.
- `Esc`: close the topmost panel or dialog when it is safe to do so. It does not dismiss an active processing panel.
- `Tab`: move between controls. An open dialog may keep keyboard focus within the dialog.

Shortcuts can vary by browser and operating system.

## HTTP API

Interactive API documentation is available at:

<http://127.0.0.1:8000/docs>

The following table summarizes the routes described by the project. Request and response schemas should be checked in the running API documentation because they may change between releases.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Render the workspace |
| `GET` | `/models` | Return the model catalogue |
| `GET` | `/usage` | Return usage-dashboard data |
| `POST` | `/settings` | Save settings; form-encoded |
| `POST` | `/translate` | Compile a prompt request |
| `GET` | `/library` | List or search saved library entries |
| `POST` | `/library` | Save a library entry |
| `PATCH` | `/library/{id}` | Update supported fields of an entry |
| `DELETE` | `/library/{id}` | Delete an entry |
| `GET` | `/static/*` | Serve static assets |

Example conversion request:

```json
{
  "prompt": "Describe the task in Persian here.",
  "model": "the-selected-model-id"
}
```

The exact accepted model identifiers, error responses, request limits, and editable library fields are defined by the running application. Use `/docs` as the authoritative schema for the installed version.

## Project structure

```text
mapsim-prompt-studio/
├── run.sh                       macOS/Linux/WSL launcher
├── run.ps1                      Windows PowerShell launcher
├── run.bat                      Windows command-prompt wrapper
├── install_service.sh           optional Linux systemd installer
├── uninstall_service.sh         Linux systemd uninstaller
├── main.py                      application entry point
├── requirements.txt             pinned Python dependencies
├── config.example.json           sanitized configuration template
├── prompt_compiler/
│   ├── app.py                   FastAPI application
│   ├── catalog.py               model catalogue
│   ├── config.py                configuration and API-key handling
│   ├── prompt_engine.py         prompt construction and result parsing
│   ├── api/routes/              HTTP route handlers
│   └── services/                provider, library, and usage services
├── templates/                   HTML templates
├── static/                      CSS, JavaScript, fonts, and logo
├── tests/                       automated tests
├── docs/                        user manuals and technical documentation
├── .gitattributes               text and binary file handling
└── .github/workflows/ci.yml     continuous integration workflow
```

Local runtime files such as `config.json`, `usage.json`, and `library.json` are generated by the application and should be excluded from source control.

## Tests and continuous integration

Run the test suite through the project launcher:

macOS/Linux/WSL:

```bash
./run.sh --tests
```

Windows PowerShell:

```powershell
.\run.ps1 -Tests
```

If the virtual environment has already been created, the suite can also be run directly:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

On Windows:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Additional static checks, if the relevant tools are installed:

```bash
.venv/bin/python -m compileall -q main.py prompt_compiler tests
node --check static/script.js
```

The supplied project description reports an in-process test suite that avoids real provider calls and uses temporary locations for local data during tests. Check the current test code and CI workflow for the exact test count and coverage.

## Local data, permissions, and privacy

| File | Typical contents | Handling |
|---|---|---|
| `config.json` | API key, selected model, system-prompt override | Treat as secret; plain-text configuration |
| `library.json` | Saved prompts, tags, favorites, and analysis | Contains user-created content |
| `usage.json` | Request and token counters | Usage history |
| `config.example.json` | Sanitized example settings | Suitable for source control if it contains no secrets |

Security recommendations:

- Do not commit real API keys or private prompt-library data.
- Keep local runtime files in `.gitignore`.
- Restrict access to configuration and data files to the account that runs the application.
- The browser should receive only a masked API-key representation, never the full secret.
- Keep the server bound to `127.0.0.1` for normal single-user use.
- The application sends the prompt and related request data to Google's Gemini API when conversion is requested. Do not send information that you are not authorized to share with that provider.
- Before publishing changes, inspect `git status` and `git diff` and check that no local data or credentials are staged.

## Troubleshooting

| Problem | Possible cause and action |
|---|---|
| Python is not found or is too old | Install Python 3.10 or newer, then reopen the terminal. On Debian/Ubuntu, the virtual-environment package may also be required. |
| Virtual environment creation fails on Debian/Ubuntu | Install the venv package for your Python version, for example `sudo apt install python3-venv`. |
| Dependency installation fails | Check internet access, DNS, proxy settings, and package-index access. Initial setup requires `pip` to download dependencies. |
| The default port is already in use | Stop the other application using port 8000, or start MAPSIM Prompt Studio on another port using `./run.sh --port 8005`. |
| The page does not open | Confirm that the launcher reports a successful startup and that the browser address matches the configured host and port. |
| Windows blocks a PowerShell script | Use `run.bat`, or open PowerShell and use a process-scoped execution-policy bypass if permitted by your organization's security policy. |
| `bad interpreter` or `^M` appears on Linux/macOS | The shell script may have Windows CRLF line endings. Convert `run.sh` to Unix LF line endings and retry. |
| Gemini conversion fails | Check the API key, model selection, internet access, DNS, proxy, firewall, provider availability, and account limits. |
| The selected model cannot generate text | Select a text-generation model supported by the installed model catalogue. |
| The request exceeds the input limit | Shorten or split the request. The interface documents a 20,000-character limit. |
| The key appears to be ignored | An environment-provided key may take precedence over the locally stored key. Check `PROMPT_STUDIO_API_KEY` and `GEMINI_API_KEY`. |
| The Linux service does not start | Run `sudo systemctl status mapsim-prompt-studio` and inspect warnings with `sudo journalctl -u mapsim-prompt-studio -p warning --since today`. |
| The service cannot access the project | Confirm that the service runs as the intended user and that the user can read the project and execute the virtual-environment Python interpreter. |

For Python installation instructions, use the official Python documentation: <https://www.python.org/downloads/>.

---

# راهنمای فارسی

این بخش برای کاربران فارسی‌زبان نوشته شده است. توضیحات و راهنمای استفاده فارسی هستند؛ اما نام فایل‌ها، دستورهای ترمینال، نام متغیرها، شناسه‌های API و اصطلاحات استاندارد فنی به شکل اصلی انگلیسی باقی می‌مانند تا بتوانید آن‌ها را دقیقاً در سیستم خود پیدا و اجرا کنید.

## راهنمای خواندن اصطلاحات فنی

در این راهنما، قاعده زیر رعایت می‌شود:

| نوع عبارت | شیوه استفاده |
|---|---|
| نام فایل و پوشه، مانند `run.sh` و `config.json` | ترجمه نمی‌شود؛ دقیقاً با همین نام در پروژه وجود دارد. |
| دستور ترمینال، مانند `sudo systemctl status ...` | ترجمه نمی‌شود؛ باید عیناً کپی و اجرا شود. |
| نام ابزار و فناوری، مانند `Python`، `FastAPI` و `Uvicorn` | نام اصلی حفظ می‌شود و در اولین کاربرد، کارکرد آن توضیح داده می‌شود. |
| متغیر محیطی، مانند `PROMPT_STUDIO_PORT` | ترجمه نمی‌شود؛ نام آن باید دقیقاً در سیستم استفاده شود. |
| اصطلاح فنی دارای معادل فارسی | ابتدا معادل فارسی و سپس اصطلاح انگلیسی در پرانتز می‌آید. |
| متن رابط کاربری | نام فارسی دکمه یا بخش نوشته می‌شود و در صورت نیاز نام انگلیسی آن نیز در پرانتز می‌آید. |

### واژه‌نامه کوتاه

| اصطلاح | معنی و کاربرد |
|---|---|
| API (رابط برنامه‌نویسی کاربردی) | راه ارتباطی نرم‌افزار با یک سرویس دیگر؛ این پروژه از آن برای ارتباط با Gemini استفاده می‌کند. |
| API Key (کلید دسترسی) | رشته محرمانه‌ای که هویت و مجوز دسترسی شما به سرویس را مشخص می‌کند. |
| Launcher (لانچر یا اجراگر) | اسکریپتی که آماده‌سازی محیط و اجرای برنامه را خودکار می‌کند. |
| Virtual Environment (محیط مجازی پایتون) | پوشه‌ای مستقل برای نصب کتابخانه‌های پایتون پروژه؛ در این پروژه نام آن معمولاً `.venv` است. |
| Dependency (وابستگی نرم‌افزاری) | کتابخانه یا بسته‌ای که برنامه برای اجرا به آن نیاز دارد. |
| Port (درگاه شبکه) | شماره‌ای که برنامه از طریق آن روی رایانه قابل دسترسی می‌شود؛ مقدار پیش‌فرض این پروژه `8000` است. |
| Host / Bind Address (نشانی میزبان) | نشانی شبکه‌ای که برنامه روی آن گوش می‌دهد؛ مقدار محلی و امن‌تر برای استفاده شخصی `127.0.0.1` است. |
| Localhost (میزبان محلی) | اشاره به همان رایانه‌ای که برنامه روی آن اجرا شده است. |
| systemd | سیستم مدیریت سرویس در بسیاری از توزیع‌های لینوکس؛ برای اجرای خودکار برنامه در پس‌زمینه استفاده می‌شود. |
| Service (سرویس) | برنامه‌ای که در پس‌زمینه اجرا می‌شود و معمولاً به بازماندن پنجره ترمینال وابسته نیست. |
| Journal / journald | سامانه ثبت و نگهداری گزارش رویدادها در سیستم‌های مبتنی بر systemd. |
| Log (گزارش اجرا) | پیام‌های ثبت‌شده درباره وضعیت، هشدارها و خطاهای برنامه. |
| Access Log (گزارش درخواست‌ها) | گزارشی که درخواست‌های ورودی وب را ثبت می‌کند؛ غیرفعال‌کردن آن از تولید پیام برای هر درخواست عادی جلوگیری می‌کند. |
| Rate Limit (محدودیت نرخ) | سقف تعداد درخواست یا میزان مصرف در یک بازه زمانی. |
| RPM | تعداد درخواست در دقیقه (Requests Per Minute). |
| TPM | تعداد توکن در دقیقه (Tokens Per Minute). |
| RPD | تعداد درخواست در روز (Requests Per Day). |
| JSON | قالب متنی ساختاریافته برای نگهداری و تبادل داده؛ پسوند فایل‌هایی مانند `config.json` است. |
| RTL | چیدمان راست‌به‌چپ برای زبان‌هایی مانند فارسی. |
| CI (یکپارچه‌سازی مداوم) | اجرای خودکار آزمون‌ها و بررسی‌ها هنگام ثبت تغییرات در مخزن کد. |

## MAPSIM Prompt Studio چیست؟

MAPSIM Prompt Studio یک محیط محلی برای مهندسی پرامپت است. شما درخواست خود را با زبان فارسی و به شکل عادی می‌نویسید. برنامه درخواست را به مدل Google Gemini می‌فرستد و یک **پرامپت انگلیسیِ مهندسی‌شده** به همراه تحلیل فارسی و انگلیسی تولید می‌کند.

خروجی شامل چهار گروه تحلیلی است:

1. **نیازمندی‌های حفظ‌شده (Preserved Requirements):** مواردی که از درخواست اصلی بدون حذف حفظ شده‌اند.
2. **فرض‌ها (Assumptions):** مواردی که برای کامل‌کردن درخواست فرض شده‌اند.
3. **اطلاعات ناقص یا حذف‌شده (Missing / Lost Information):** مواردی که در ورودی مشخص نبوده‌اند یا در تبدیل نیاز به توجه دارند.
4. **پیشنهادها (Suggestions):** پیشنهادهایی برای دقیق‌تر، کامل‌تر و قابل‌اجراتر شدن پرامپت.

نتیجه را می‌توانید کپی کنید، در کتابخانه محلی ذخیره کنید، بعداً جست‌وجو کنید یا ویرایش و دوباره بارگذاری کنید.

## امکانات اصلی

- تولید خروجی کامل فارسی و انگلیسی.
- نمایش وضعیت پردازش و زمان سپری‌شده هنگام دریافت پاسخ.
- کتابخانه محلی برای ذخیره، جست‌وجو، برچسب‌گذاری، علاقه‌مندی و ویرایش پرامپت‌ها.
- فهرست مدل‌ها و اطلاعات مربوط به کاربرد و محدودیت‌های آن‌ها.
- پوسته روشن و تاریک (Light / Dark Theme).
- رابط واکنش‌گرا برای نمایشگرهای مختلف.
- داشبورد مصرف توکن و آمار درخواست‌ها.
- نگهداری کلید API به‌صورت محافظت‌شده‌تر؛ مقدار کامل کلید نباید به مرورگر برگردانده شود.
- اجرای محلی با FastAPI و نمایش مستندات API در مسیر `/docs`.

## پیش‌نیازهای نصب

برای نصب و اجرای پروژه به موارد زیر نیاز دارید:

1. **Python نسخه 3.10 یا جدیدتر:** لانچر نسخه مناسب را جست‌وجو می‌کند. نسخه‌های دقیقاً پشتیبانی‌شده را با تنظیمات CI و فایل وابستگی‌های پروژه بررسی کنید.
2. **اینترنت در نصب اولیه:** برای دریافت کتابخانه‌های پایتون از طریق `pip` لازم است. هنگام تبدیل درخواست به Gemini نیز اینترنت لازم است.
3. **کلید Google AI Studio:** از نشانی زیر دریافت کنید:
   <https://aistudio.google.com/apikey>
4. **فضای دیسک:** محیط مجازی و کتابخانه‌های موردنیاز در پوشه `.venv` نصب می‌شوند و فضای جداگانه‌ای مصرف می‌کنند.

برای اجرای برنامه به نصب جداگانه Node.js، پایگاه داده یا ابزار ساخت رابط کاربری نیاز نیست.

## نصب و اجرای سریع

لانچر (`Launcher`) روش پیشنهادی نصب و اجرا است. این اسکریپت محیط مجازی را می‌سازد یا از محیط موجود استفاده می‌کند، وابستگی‌ها را در صورت نیاز نصب می‌کند، درگاه انتخابی را بررسی می‌کند و سرور محلی را اجرا می‌کند.

### مک، لینوکس و WSL

اگر پروژه را از Git دریافت می‌کنید:

```bash
git clone https://github.com/MAPSIM-co/MAPSIM-Prompt-Studio.git
cd MAPSIM-Prompt-Studio
chmod +x run.sh
./run.sh
```

به‌جای `<repository-url>` نشانی واقعی مخزن GitHub خود را قرار دهید.

اگر فایل ZIP را دانلود کرده‌اید، آن را استخراج کنید، ترمینال را در پوشه اصلی پروژه باز کنید و اجرا کنید:

```bash
bash run.sh
```

استفاده از `bash run.sh` حتی در صورتی که مجوز اجرایی فایل تنظیم نشده باشد، معمولاً امکان اجرای آن را فراهم می‌کند.

### ویندوز 10 و 11

روش ساده‌تر این است که روی فایل زیر دوبار کلیک کنید:

```text
run.bat
```

یا PowerShell را در پوشه اصلی پروژه باز کنید و بنویسید:

```powershell
.\run.ps1
```

فایل `run.bat` برای اجرای ساده از طریق Command Prompt یا دوبار کلیک در ویندوز در نظر گرفته شده است و لانچر PowerShell را فراخوانی می‌کند.

### پس از اجرا

مرورگر را باز کنید و به نشانی زیر بروید:

<http://127.0.0.1:8000>

در اجرای تعاملی، تا زمانی که از برنامه استفاده می‌کنید پنجره ترمینال را باز نگه دارید. برای توقف برنامه، در همان پنجره `Ctrl+C` را فشار دهید.

## لانچر چه کارهایی انجام می‌دهد؟

لانچر (`run.sh` یا `run.ps1`) مراحل معمول آماده‌سازی را خودکار می‌کند:

1. **پیداکردن Python:** نسخه مناسب پایتون را در مسیرهای متداول یا مسیر تنظیم‌شده جست‌وجو می‌کند.
2. **ساخت محیط مجازی:** در صورت نیاز پوشه `.venv` را می‌سازد. این محیط محل نصب کتابخانه‌های اختصاصی پروژه است.
3. **نصب وابستگی‌ها:** بسته‌های ثبت‌شده در `requirements.txt` را نصب می‌کند.
4. **بررسی درگاه:** بررسی می‌کند درگاه موردنظر قبلاً توسط برنامه دیگری اشغال نشده باشد.
5. **اجرای سرور:** برنامه را از طریق Uvicorn اجرا می‌کند و نشانی محلی را نمایش می‌دهد.

جزئیات دقیق جست‌وجوی Python، تشخیص تغییر وابستگی‌ها و نحوه بازیابی خطاها به نسخه واقعی اسکریپت‌های `run.sh` و `run.ps1` وابسته است.

## نصب سرویس دائمی در لینوکس (اختیاری)

اگر می‌خواهید برنامه در پس‌زمینه اجرا شود و بعد از خاموش و روشن شدن سیستم به‌صورت خودکار بالا بیاید، می‌توانید از سرویس `systemd` استفاده کنید.

این روش برای سیستم‌هایی است که از systemd پشتیبانی می‌کنند. ترمینال را در پوشه اصلی پروژه باز کنید و با همان کاربری که مالک پوشه پروژه است اجرا کنید.

**اسکریپت نصب را با `sudo` اجرا نکنید.** اسکریپت باید فقط برای عملیات سیستمی موردنیاز، دسترسی مدیریتی درخواست کند تا فایل‌های پروژه و محیط مجازی با مالکیت کاربر عادی باقی بمانند.

```bash
./install_service.sh
```

اگر فایل مجوز اجرا ندارد:

```bash
bash install_service.sh
```

برای استفاده از درگاه دیگری، مثلاً `8005`:

```bash
PROMPT_STUDIO_PORT=8005 ./install_service.sh
```

این نصب‌کننده برای آماده‌سازی محیط پایتون، ساخت فایل سرویس systemd، فعال‌سازی اجرای خودکار هنگام روشن‌شدن سیستم و شروع سرویس طراحی شده است. پیش از اجرا، محتوای اسکریپت را بررسی کنید؛ به‌ویژه اگر آن را روی سرور مهم یا سیستم عملیاتی اجرا می‌کنید.

### مدیریت سرویس

بررسی وضعیت سرویس:

```bash
sudo systemctl status mapsim-prompt-studio
```

شروع سرویس:

```bash
sudo systemctl start mapsim-prompt-studio
```

راه‌اندازی مجدد سرویس:

```bash
sudo systemctl restart mapsim-prompt-studio
```

متوقف‌کردن سرویس:

```bash
sudo systemctl stop mapsim-prompt-studio
```

مشاهده هشدارها و خطاهای امروز:

```bash
sudo journalctl -u mapsim-prompt-studio -p warning --since today
```

مشاهده زنده پیام‌های هشدار و خطا:

```bash
sudo journalctl -u mapsim-prompt-studio -p warning -f
```

حذف سرویس:

```bash
./uninstall_service.sh
```

اگر مجوز اجرایی تنظیم نشده است:

```bash
bash uninstall_service.sh
```

اسکریپت حذف باید فقط فایل سرویس systemd را حذف کند و نباید پوشه پروژه، محیط مجازی، کلید API، کتابخانه پرامپت‌ها یا آمار مصرف را پاک کند. پیش از اجرا، رفتار واقعی `uninstall_service.sh` را بررسی کنید.

> **نشانی سرویس:** تنظیم پیش‌فرض برای گوش‌دادن روی `127.0.0.1` و درگاه `8000` است؛ بنابراین برنامه فقط از همان رایانه قابل دسترسی خواهد بود. اگر درگاه دیگری انتخاب کرده‌اید، همان شماره را در نشانی مرورگر وارد کنید. سرویس را بدون احراز هویت و محافظت شبکه روی اینترنت یا شبکه عمومی قرار ندهید.

## کاهش لاگ و مصرف فضای دیسک

برای کاهش مصرف منابع و جلوگیری از رشد بی‌رویه فایل‌ها، این نکات در طراحی پروژه در نظر گرفته شده‌اند:

- غیرفعال‌کردن Access Log در Uvicorn باعث می‌شود برای هر بازدید معمولی صفحه یک خط گزارش تولید نشود.
- در حالت systemd می‌توان خروجی سرویس را به هشدارها و خطاها محدود کرد.
- برای جلوگیری از تولید فایل‌های اضافی `__pycache__`، اجرای پایتون سرویس می‌تواند با غیرفعال‌کردن تولید bytecode تنظیم شود.
- برنامه برای کار عادی به فایل لاگ مستقل و دائماً در حال رشد نیاز ندارد.
- تاریخچه مصرف در پیاده‌سازی توصیف‌شده به هفت روز اخیر محدود است.
- اطلاعات کتابخانه پرامپت‌ها تا زمانی که کاربر آن‌ها را حذف نکند باقی می‌مانند. برای کاهش فضای مصرفی، موارد قدیمی و غیرضروری را از داخل برنامه حذف کنید.
- پوشه `.venv` شامل پایتون و کتابخانه‌های موردنیاز پروژه است. حذف آن فضا آزاد می‌کند، اما برای اجرای بعدی باید دوباره ساخته و وابستگی‌ها نصب شوند.

### نکته مهم درباره لاگ لینوکس

`journald` سامانه ثبت گزارش در لینوکس است و مدیریت فضای کلی آن در اختیار سیستم‌عامل و مدیر سیستم قرار دارد؛ محدودکردن پیام‌های خود برنامه به معنی تعیین سقف قطعی برای کل فضای لاگ سیستم نیست.

برای مشاهده فضای مصرف‌شده توسط journal:

```bash
sudo journalctl --disk-usage
```

برای حذف گزارش‌های آرشیوشده قدیمی‌تر از هفت روز:

```bash
sudo journalctl --vacuum-time=7d
```

برای محدودکردن حجم گزارش‌های آرشیوشده به حدود ۲۰۰ مگابایت:

```bash
sudo journalctl --vacuum-size=200M
```

**هشدار:** دو دستور آخر روی گزارش‌های journal سیستم اثر می‌گذارند و ممکن است گزارش سایر سرویس‌ها را نیز حذف کنند. فقط در صورتی از آن‌ها استفاده کنید که سیاست نگهداری لاگ‌های سیستم را می‌دانید.

برای تعیین محدودیت دائمی، مدیر سیستم می‌تواند گزینه‌هایی مانند `SystemMaxUse` و `SystemKeepFree` را در تنظیمات journald بررسی و متناسب با نیاز کل سیستم تنظیم کند. این تنظیمات مختص MAPSIM نیستند.

## تنظیم اولیه و اتصال به Gemini

پس از اجرای برنامه:

1. در سربرگ برنامه، گزینه **تنظیمات (Settings)** را انتخاب کنید.
2. کلید خود را در فیلد **کلید API (API Key)** وارد کنید.
3. یک مدل متنی قابل تولید انتخاب کنید.
4. تنظیمات را ذخیره کنید.

پس از ذخیره، کلید باید به شکل ماسک‌شده نمایش داده شود؛ مقدار کامل آن نباید دوباره به مرورگر ارسال شود.

### استفاده از متغیر محیطی به‌جای ذخیره کلید در فایل

در macOS و لینوکس:

```bash
export PROMPT_STUDIO_API_KEY="your-api-key"
./run.sh
```

در نسخه توصیف‌شده، `GEMINI_API_KEY` نیز ممکن است به‌عنوان نام جایگزین پذیرفته شود. نام متغیر پشتیبانی‌شده را در کد نسخه نصب‌شده بررسی کنید.

کلیدی که از متغیر محیطی دریافت می‌شود، طبق طراحی اعلام‌شده بر کلید ذخیره‌شده در `config.json` اولویت دارد.

**نکته سرویس لینوکس:** متغیری که در یک ترمینال با `export` تعریف می‌کنید، لزوماً به سرویس systemd منتقل نمی‌شود. برای سرویس دائمی باید روش تعریف متغیر محیطی مورد پشتیبانی اسکریپت نصب یا فایل unit را استفاده کنید.

کلید API را در Issue عمومی، تصویر صفحه، فایل کد یا گزارش قابل اشتراک‌گذاری قرار ندهید.

## گزینه‌های اجرای برنامه

گزینه‌های زیر در توضیحات لانچر پروژه آمده‌اند. در صورت تغییر نسخه اسکریپت‌ها، ابتدا راهنمای همان نسخه را با `--help` بررسی کنید.

| کاربرد | مک / لینوکس / WSL | ویندوز PowerShell |
|---|---|---|
| تغییر درگاه | `./run.sh --port 8005` | `.\run.ps1 -Port 8005` |
| تعیین نشانی میزبان | `./run.sh --host 127.0.0.1` | `.\run.ps1 -BindHost 127.0.0.1` |
| انتخاب نسخه Python | `./run.sh --python /path/to/python3.12` | `.\run.ps1 -Python C:\Python312\python.exe` |
| اجرای آزمون‌ها | `./run.sh --tests` | `.\run.ps1 -Tests` |
| حالت توسعه و بارگذاری مجدد | `./run.sh --reload` | `.\run.ps1 -Reload` |
| بازکردن خودکار مرورگر | `./run.sh --open` | `.\run.ps1 -Open` |
| نمایش راهنما | `./run.sh --help` | `.\run.ps1 -Help` |
| تعیین نام پوشه محیط مجازی | راهنمای `run.sh --help` را بررسی کنید | `.\run.ps1 -VenvDir NAME` |

### متغیرهای محیطی

متغیر محیطی (Environment Variable) مقداری است که پیش از اجرای برنامه در محیط سیستم تعریف می‌کنید تا برنامه آن را بخواند.

| نام متغیر | مقدار پیش‌فرض | کاربرد |
|---|---|---|
| `PROMPT_STUDIO_HOST` | `127.0.0.1` | نشانی میزبان برای اجرای سرور |
| `PROMPT_STUDIO_PORT` | `8000` | شماره درگاه |
| `PROMPT_STUDIO_PYTHON` | تشخیص خودکار | مسیر مفسر Python |
| `PROMPT_STUDIO_API_KEY` | تعریف‌نشده | کلید API |
| `GEMINI_API_KEY` | تعریف‌نشده | نام جایگزین کلید API، در صورت پشتیبانی نسخه |

> **هشدار امنیتی:** استفاده از `0.0.0.0` باعث می‌شود برنامه از طریق رابط‌های شبکه در دسترس دستگاه‌های دیگر قرار بگیرد. برای استفاده شخصی همان `127.0.0.1` را حفظ کنید. برای دسترسی شبکه‌ای باید کنترل دسترسی، احراز هویت و فایروال مناسب داشته باشید.

طبق توضیح پروژه، `main.py` متغیرهای محیطی `PROMPT_STUDIO_HOST` و `PROMPT_STUDIO_PORT` را می‌خواند و الزاماً آرگومان خط فرمان را پردازش نمی‌کند. بنابراین برای تغییر درگاه از گزینه‌های لانچر یا متغیر محیطی استفاده کنید؛ صرفاً نوشتن `python main.py --port 8004` را راه مطمئن تغییر درگاه فرض نکنید.

## آموزش کار با محیط برنامه

1. **نوشتن درخواست:** متن درخواست خود را در کادر ورودی بنویسید. شمارنده زیر کادر تعداد نویسه‌ها را نشان می‌دهد. سقف اعلام‌شده ۲۰٬۰۰۰ نویسه است. برای شروع تبدیل از `Ctrl+Enter` در ویندوز و لینوکس یا `⌘+Enter` در مک استفاده کنید.
2. **بررسی خروجی:** خروجی فارسی و انگلیسی را جداگانه بررسی کنید. هر بخش شامل پرامپت، هدف و چهار گروه تحلیل است.
3. **کپی خروجی:** از دکمه کپی همان بخش استفاده کنید یا در صورت وجود، هر دو خروجی را هم‌زمان کپی کنید.
4. **ذخیره در کتابخانه:** با گزینه «ذخیره در کتابخانه» نتیجه را نگه دارید. برای پیدا کردن آسان‌تر، عنوان، برچسب یا علامت علاقه‌مندی اضافه کنید.
5. **جست‌وجو و ویرایش:** در کتابخانه می‌توانید متن ذخیره‌شده را جست‌وجو کنید، فیلتر بگذارید، نتیجه را دوباره بارگذاری کنید یا ویرایش کنید.
6. **بررسی مصرف:** از بخش «مصرف توکن» برای مشاهده آمار درخواست‌ها و توکن‌ها استفاده کنید.
7. **تنظیم مدل:** در «تنظیمات» کلید API، مدل انتخابی و گزینه‌های قابل تنظیم پرامپت سیستم را مدیریت کنید.

### میانبرهای صفحه‌کلید

- `Ctrl+Enter` یا `⌘+Enter`: شروع تبدیل.
- `Esc`: بستن پنل یا پنجره باز، در مواردی که رابط اجازه دهد؛ پنل پردازش فعال با این کلید بسته نمی‌شود.
- `Tab`: حرکت بین کنترل‌های صفحه. در پنجره‌های محاوره‌ای ممکن است تمرکز صفحه داخل همان پنجره نگه داشته شود.

رفتار میانبرها ممکن است با مرورگر و سیستم‌عامل تفاوت داشته باشد.

## رابط برنامه‌نویسی (HTTP API)

مستندات تعاملی API پس از اجرای برنامه در نشانی زیر در دسترس است:

<http://127.0.0.1:8000/docs>

API راهی است که برنامه‌های دیگر می‌توانند از طریق آن با MAPSIM Prompt Studio ارتباط برقرار کنند. مسیرها و کاربردهای اعلام‌شده:

| روش | مسیر | کاربرد |
|---|---|---|
| `GET` | `/` | نمایش صفحه اصلی |
| `GET` | `/models` | دریافت فهرست مدل‌ها |
| `GET` | `/usage` | دریافت داده‌های داشبورد مصرف |
| `POST` | `/settings` | ذخیره تنظیمات |
| `POST` | `/translate` | تبدیل درخواست به پرامپت |
| `GET` | `/library` | مشاهده و جست‌وجوی کتابخانه |
| `POST` | `/library` | ذخیره یک مورد در کتابخانه |
| `PATCH` | `/library/{id}` | ویرایش فیلدهای مجاز یک مورد |
| `DELETE` | `/library/{id}` | حذف یک مورد |
| `GET` | `/static/*` | دریافت فایل‌های ظاهری مانند CSS، JavaScript و تصویرها |

نمونه ساختار درخواست تبدیل:

```json
{
  "prompt": "متن درخواست فارسی در این قسمت قرار می‌گیرد.",
  "model": "شناسه مدل انتخاب‌شده"
}
```

ساختار دقیق ورودی، خروجی، خطاها و شناسه مدل‌ها را از مستندات `/docs` در نسخه در حال اجرا بررسی کنید.

## ساختار پوشه‌های پروژه

```text
mapsim-prompt-studio/
├── run.sh                       اجراگر مک، لینوکس و WSL
├── run.ps1                      اجراگر PowerShell ویندوز
├── run.bat                      فایل واسط اجرای ویندوز
├── install_service.sh           نصب‌کننده سرویس systemd در لینوکس
├── uninstall_service.sh         حذف‌کننده سرویس لینوکس
├── main.py                      نقطه شروع برنامه
├── requirements.txt             وابستگی‌های Python
├── config.example.json          نمونه تنظیمات بدون اطلاعات محرمانه
├── prompt_compiler/
│   ├── app.py                   برنامه FastAPI
│   ├── catalog.py               فهرست مدل‌ها
│   ├── config.py                تنظیمات و مدیریت کلید API
│   ├── prompt_engine.py         ساخت و تحلیل پرامپت
│   ├── api/routes/              مسیرهای HTTP
│   └── services/                سرویس‌های Gemini، کتابخانه و مصرف
├── templates/                   قالب‌های HTML
├── static/                      فایل‌های CSS، JavaScript، فونت و لوگو
├── tests/                       آزمون‌های خودکار
├── docs/                        مستندات فنی و راهنمای کاربران
├── .gitattributes               تنظیم نحوه مدیریت فایل‌ها در Git
└── .github/workflows/ci.yml     گردش کار آزمون خودکار
```

فایل‌هایی مانند `config.json`، `usage.json` و `library.json` در زمان استفاده محلی ایجاد می‌شوند و نباید در مخزن عمومی Git قرار بگیرند.

## اجرای آزمون‌ها

برای اجرای آزمون‌ها از لانچر استفاده کنید.

مک، لینوکس و WSL:

```bash
./run.sh --tests
```

ویندوز PowerShell:

```powershell
.\run.ps1 -Tests
```

اگر محیط مجازی از قبل ساخته شده باشد، می‌توانید آزمون‌ها را مستقیماً اجرا کنید.

مک و لینوکس:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

ویندوز:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

بررسی‌های تکمیلی، در صورت نصب بودن ابزارهای مربوط:

```bash
.venv/bin/python -m compileall -q main.py prompt_compiler tests
node --check static/script.js
```

تعداد آزمون‌ها و میزان پوشش را از اجرای واقعی آزمون‌ها و فایل CI همان نسخه بررسی کنید؛ عدد درج‌شده در مستندات ممکن است با نسخه‌های بعدی تغییر کند.

## فایل‌های محلی، امنیت و حریم خصوصی

| فایل | محتوای معمول | نکته امنیتی |
|---|---|---|
| `config.json` | کلید API، مدل انتخابی و تنظیمات پرامپت سیستم | محرمانه است؛ مقدار کلید به‌صورت متن ساده ذخیره می‌شود. |
| `library.json` | پرامپت‌ها، برچسب‌ها، علاقه‌مندی‌ها و تحلیل‌ها | ممکن است شامل اطلاعات شخصی یا محرمانه شما باشد. |
| `usage.json` | شمارنده درخواست‌ها و توکن‌ها | داده مصرف محلی است. |
| `config.example.json` | نمونه تنظیمات پاک‌سازی‌شده | در صورت نداشتن اطلاعات محرمانه برای مخزن مناسب است. |

توصیه‌های امنیتی:

- کلید واقعی API و اطلاعات خصوصی را در GitHub منتشر نکنید.
- فایل‌های محلی را در `.gitignore` نگه دارید.
- دسترسی فایل‌های تنظیمات و داده را به حساب کاربری اجراکننده محدود کنید.
- مرورگر باید فقط نسخه ماسک‌شده کلید را دریافت کند، نه مقدار کامل آن.
- برای استفاده شخصی، سرور را روی `127.0.0.1` نگه دارید.
- هنگام تبدیل، متن درخواست و اطلاعات لازم برای فراخوانی مدل به Google Gemini ارسال می‌شود. اطلاعاتی را ارسال نکنید که مجاز به اشتراک‌گذاری آن با ارائه‌دهنده نیستید.
- پیش از انتشار تغییرات، خروجی `git status` و `git diff` را بررسی کنید و مطمئن شوید فایل‌های محلی یا کلیدها برای commit انتخاب نشده‌اند.

## عیب‌یابی

| مشکل | علت احتمالی و راه‌حل |
|---|---|
| Python پیدا نمی‌شود یا نسخه آن قدیمی است | Python نسخه 3.10 یا جدیدتر نصب کنید و ترمینال را دوباره باز کنید. |
| ساخت `.venv` در Debian/Ubuntu شکست می‌خورد | بسته محیط مجازی نسخه پایتون را نصب کنید؛ برای نمونه `sudo apt install python3-venv`. |
| نصب وابستگی‌ها شکست می‌خورد | اینترنت، DNS، پروکسی و دسترسی به مخزن بسته‌های Python را بررسی کنید. |
| درگاه پیش‌فرض اشغال است | برنامه‌ای را که از درگاه 8000 استفاده می‌کند متوقف کنید یا با `./run.sh --port 8005` درگاه دیگری انتخاب کنید. |
| صفحه در مرورگر باز نمی‌شود | پیام موفقیت لانچر و نشانی میزبان و درگاه را بررسی کنید. |
| ویندوز اجرای PowerShell را مسدود می‌کند | از `run.bat` استفاده کنید یا در صورت مجازبودن سیاست امنیتی سیستم، محدودیت را فقط برای همان فرایند PowerShell تغییر دهید. |
| خطای `bad interpreter` یا `^M` در مک/لینوکس | احتمالاً فایل Shell با پایان خط ویندوزی CRLF ذخیره شده است. آن را به قالب Unix یعنی LF تبدیل کنید. |
| تبدیل Gemini انجام نمی‌شود | کلید API، مدل، اینترنت، DNS، پروکسی، فایروال، وضعیت سرویس و محدودیت حساب را بررسی کنید. |
| مدل انتخاب‌شده متن تولید نمی‌کند | یک مدل تولید متن از فهرست مدل‌های قابل استفاده انتخاب کنید. |
| درخواست از سقف مجاز بیشتر است | متن را کوتاه یا به چند درخواست تقسیم کنید. سقف اعلام‌شده ۲۰٬۰۰۰ نویسه است. |
| کلید ذخیره‌شده استفاده نمی‌شود | ممکن است متغیر محیطی بر کلید ذخیره‌شده اولویت داشته باشد. متغیرهای `PROMPT_STUDIO_API_KEY` و `GEMINI_API_KEY` را بررسی کنید. |
| سرویس لینوکس شروع نمی‌شود | وضعیت را با `sudo systemctl status mapsim-prompt-studio` و گزارش‌ها را با `sudo journalctl -u mapsim-prompt-studio -p warning --since today` بررسی کنید. |
| سرویس به پروژه دسترسی ندارد | کاربر تعریف‌شده در سرویس و مجوز خواندن پوشه پروژه و اجرای Python داخل محیط مجازی را بررسی کنید. |

برای دریافت Python از منبع رسمی استفاده کنید:

<https://www.python.org/downloads/>

---

## ارائه‌دهنده سرویس، کتابخانه‌های جانبی و مجوز

نام و هویت بصری MAPSIM برای این پروژه استفاده شده است. Google Gemini ارائه‌دهنده مدل و API مورد استفاده برنامه است؛ این موضوع به معنی مالکیت Google بر رابط MAPSIM یا وابستگی برند MAPSIM به Google نیست. برنامه برای تبدیل درخواست‌ها از API عمومی Gemini استفاده می‌کند.

کتابخانه‌های جانبی مانند FastAPI، Starlette، Uvicorn، httpx، Jinja2 و python-multipart و همچنین فایل‌های فونت Vazirmatn تابع مجوزهای انتشار خود هستند. هنگام بازنشر پروژه، اعلان‌های مجوز مربوط به آن‌ها را حذف نکنید.

این مخزن در حال حاضر فایل اصلی `LICENSE` ندارد. تا زمان افزودن مجوز، نباید فرض کنید که دیگران حق استفاده آزاد، تغییر یا بازنشر کد را دارند. مالک مخزن باید پیش از دعوت از مشارکت‌کنندگان، مجوز مناسب را انتخاب و اضافه کند.

## قدردانی

این پروژه به‌عنوان بخشی از مجموعه ابزارهای MAPSIM توسعه یافته است. پیشنهادهای مفید برای مشارکت عبارت‌اند از اصلاح متن فارسی بر اساس تجربه کاربران، به‌روزرسانی فهرست مدل‌ها همراه با منبع و تاریخ، و افزودن آزمون برای بخش‌های کتابخانه و ویرایشگر.
