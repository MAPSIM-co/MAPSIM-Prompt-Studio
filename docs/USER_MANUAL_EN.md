# User Manual — MAPSIM Prompt Studio

## Purpose
MAPSIM Prompt Studio converts Persian natural-language requests into structured English prompts for AI assistants and coding agents. Treat generated output as a draft that requires review, not as a correctness guarantee.

## Installation and launch

### The one-command way (recommended)

Install Python 3.10 or later, then from the project root:

- **macOS / Linux / WSL:** `./run.sh` (if the executable bit was lost, e.g. after a ZIP download: `bash run.sh`)
- **Windows:** double-click `run.bat`, or run `.\run.ps1` in a terminal

The launcher finds an interpreter (3.10+), creates `.venv`, installs the pinned dependencies, refuses to start if the port is already taken, and opens the server at `http://127.0.0.1:8000`. The second run skips the installation unless `requirements.txt` changed, and reaches the server in about half a second. It never deletes an existing `.venv` and never reads `config.json`.

Useful switches — `--port 8005` (Windows: `-Port 8005`), `--host`, `--python /path/to/python3`, `--tests` (`-Tests`) to run the suite, `--reload` (`-Reload`) for development, `--open` (`-Open`) to launch the browser, `--help` (`-Help`) for the list. Windows has one extra switch, `-VenvDir NAME`, which builds or reuses the environment under another folder name.

### The manual way

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn prompt_compiler.app:app --host 127.0.0.1 --port 8000
```

`python main.py` starts the same app, but it reads its address from the environment and accepts no command-line flags — for another port use `./run.sh --port 8004` or `PROMPT_STUDIO_PORT=8004 python main.py`.

### First launch

Open `http://127.0.0.1:8000`, then open **تنظیمات** (Settings) and enter a Google AI Studio API key. Create one at `https://aistudio.google.com/apikey`. Alternatively export `PROMPT_STUDIO_API_KEY` (or `GEMINI_API_KEY`) before starting the server; an environment key wins over the stored one and nothing is written to disk.

## Typical workflow
1. Describe the objective in Persian. Include context, inputs, constraints, and acceptance criteria. Under the box, the counter shows your current length next to the allowed ceiling (20,000 characters) and turns red and bold the moment the request is too long to send — before you press convert.
2. Select a supported text-generation model.
3. Select **تبدیل کن** (Convert) and wait for the response — or press `Ctrl`/`⌘ + Enter` in the input box. A MAPSIM processing sheet covers the page until the answer arrives (see *Processing sheet during conversion*).
4. Review the result card, which is split into two complete halves: the Persian half gives the Persian prompt, the purpose and all four analysis groups (preserved requirements, assumptions, lost information, suggestions) in Persian, and the English half gives the same sections in English. Each half has its own copy button.
5. Use **بیشتر نمایش بده** / **Expand** to release a prompt box's height cap; every box scrolls comfortably on its own before that.
6. Copy either prompt, or both at once, and review before submitting to another tool.
7. Select **★ ذخیره در کتابخانه** to keep the result for later.

## Processing sheet during conversion
While the request is with the model, a MAPSIM-branded sheet covers the whole page so it is obvious the work is running and you should wait.
- The MAPSIM logo between two counter-rotating arcs, one current-status sentence, and a four-step strip: **خواندن درخواست** (reading the request), **ارسال به مدل** (sent to the model), **ساخت پرامپت** (building the prompt) and **آماده‌سازی خروجی** (preparing the output).
- The sheet also writes the elapsed seconds, the length of your request and the model in use, and the status sentence changes as the call ages — if it takes long it says plainly that no answer has come yet.
- The fourth step only lights up once the reply has actually arrived; the sheet never invents progress.
- While it is open the page behind is inert: `Tab` does not move focus, `Esc` does not dismiss the sheet, and another click cannot start a second request. It closes on its own when the answer or an error arrives, and **تبدیل کن** becomes clickable again.
- On a landscape phone the sheet compacts so everything stays visible, and with the operating system's reduce-motion setting on, the step text and the seconds counter carry the progress instead of the animation.

## Prompt library
The library panel (**کتابخانه پرامپت**) stores saved compilations in `library.json` on this machine.
- **Search** matches the title, the original Persian request, both prompts, the purpose, the tags and the Persian analysis text.
- **Tag chips** filter to one tag; the detected category is added as a tag automatically. **همه** clears the filter.
- **فقط علاقه‌مندی‌ها** shows favorites only; the star on a card toggles the favorite state.
- **بارگذاری** puts the saved request back into the input card and reopens its result; **حذف** removes the entry after confirmation.
- **ویرایش** opens a wide dialog where the full request, the Persian prompt and the English prompt are edited in tall multi-line boxes, with the title and tag fields above them. **ذخیره تغییرات** or `Ctrl/Cmd + Enter` saves, **انصراف**, `Esc` or a click on the dimmed margin closes without saving, and the character counter under the request box tracks the same 20,000-character limit as saving — it turns red past the ceiling, exactly like the counter in the main input card.
- Editing rewrites text only: the category, purpose and the four analysis groups are not recalculated, and the entry id and creation time are untouched. A title the program derived from the request follows the new text; a title you typed yourself is kept. Edited text is searchable immediately.
- Newest entries come first and the file keeps the last 500.

## Themes and devices
- The moon/sun button in the header switches between the dark neon theme and the light theme. The choice is remembered per browser, applied before the page paints, and follows the operating-system preference until you override it.
- The two halves of the engineered-output card share one surface and one border, so they differ only in writing direction and font — never in colour.
- The layout adapts from a 360px phone to a wide desktop. On screens 1000px and wider, the token-usage panel docks as a column beside the workspace; on smaller screens it slides in over the page and the library opens as a full-height sheet.
- **Layout:** no horizontal scrolling from 360px up, and every control a finger can hit is at least 44px. That includes the small links inside paragraphs — the API-key help link, the pricing link in the model panel and its help list, and the API guide link in the footer — which carry invisible vertical padding to reach a real touch target without moving a line of text. The model selector clips its own label on a narrow phone instead of pushing the page sideways. In the library editor the two prompt boxes sit side by side on a tablet and stack on a phone.
- `Esc` closes the top-most dialog or panel (the library editor sits above the library sheet), keyboard focus stays inside an open dialog, and every control is labelled for screen readers. During a conversion `Esc` will not close the processing sheet and `Tab` is held on the page.

## Settings
The modal is three numbered blocks: **۱ کلید دسترسی** (API key), **۲ مدل پیش‌فرض** (default model) and **۳ سیستم پرامپت اختصاصی** (optional system prompt).
- **API key:** Used for Gemini requests. The stored value is never displayed in the browser — an empty field means "keep it", and the remove option is the only way to delete it. The file is written with owner-only (`0600`) permissions, and an environment key (`PROMPT_STUDIO_API_KEY` / `GEMINI_API_KEY`) always wins over the stored one. The expandable help states where the key lives and what to do if it leaks.
- **Default model:** The picker is split into two groups — text-generation models this app can use, and models it cannot (image, audio, agents, embedding), which are listed disabled with the Persian reason. Each option label carries its class (`سبک (Lite)`, `متعادل`, `پرچم‌دار (Pro)`), and the panel under the picker shows that model's best use, speed, cost tier and the recorded RPM/TPM/RPD ceilings. Costs are relative tiers, not prices; the panel links to Google's official pricing page.
- **System prompt override (optional):** This field *replaces* the built-in instruction; it is not appended to it. Empty means the default, which is what keeps the output aligned with this page. Use an override to change tone or length, force a domain (for example always target MQL5/MetaTrader 5), or ask for shorter, more concrete analysis items. **درج نمونهٔ آماده** inserts a sample that keeps every output key, and **خالی کردن (بازگشت به پیش‌فرض)** reverts. Warning: an override that drops the required JSON keys (`english_prompt`, `persian_prompt`, `persian_analysis`, …) makes the response unparseable and the analysis sections stay empty.
- **Token usage:** A local estimate from this machine's own request log (kept for seven days), not an authoritative provider invoice.

## Better prompts
- Preserve exact technical names, paths, versions, and constraints in the input.
- For coding tasks, ask the target agent to inspect the repository, make focused changes, run tests, and report only verifiable results.
- Do not include passwords, API keys, or sensitive customer information.
- Review any generated instructions before executing code or destructive actions.

## Troubleshooting
- **The processing sheet stays for a long time:** the model has not answered yet. Check the internet connection, the account quota and the API key, and do not start a new request while it is open — something is already running behind it. It cannot strand the page: the server gives up on an unresponsive provider after 180 seconds, the sheet closes with a Persian connection error, and **تبدیل کن** becomes clickable again.
- **API key errors:** Verify the key and account access to the selected model.
- **Connection errors:** Check internet access and network restrictions to Google AI Studio.
- **Rate limit/model unavailable:** Select another available model or retry after the provider limit resets.
- **"Request too long":** A single request is capped at 20,000 characters; split it or remove pasted files. The counter under the box already says the limit and turns red before the app refuses the request.
- **The Persian analysis half repeats the English items:** a server started before this version does not return `persian_analysis`. Restart it. Until then the app deliberately copies the English items into the Persian half so a half is never blank.
- **The request text will not save in the editor:** the box cannot be empty and is capped at 20,000 characters. A server started before this version ignores those text fields on `PATCH /library/{id}` — restart it.
- **Nothing saves to the library:** `library.json` must be writable; check that the folder is not read-only and no stale `library.json.tmp` is left behind.
- **Server fails to start:** Confirm the virtual environment is active and dependencies installed; run the command from the project root.
- **Invalid configuration:** Stop the server, back up `config.json`, and validate its JSON syntax.

## Privacy and security
For generation, prompt text is sent to the configured provider API. Do not assume prompts are private without reviewing the provider's current terms and account settings. Saved requests, prompts and usage stay on this machine in `library.json` and `usage.json`. Never commit `config.json`, `library.json`, API keys, usage logs, or sensitive prompt history to a public repository.
