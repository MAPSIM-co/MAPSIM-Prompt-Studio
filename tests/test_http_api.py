"""HTTP-surface tests: pages, settings, usage, translate guards and the library.

Everything runs in-process through ``TestClient`` — no socket is opened, no
provider is called, and every read/write lands in a throw-away temp directory so
the real ``config.json`` / ``library.json`` of the operator are never touched.
"""

import json
import os
import pathlib
import re
import sys
import tempfile
import time
import unittest
from unittest import mock

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient

from prompt_compiler import config as config_module
from prompt_compiler.api.routes import translation as translation_route
from prompt_compiler.catalog import MODELS
from prompt_compiler.services import library as library_service
from prompt_compiler.services import usage as usage_service
from prompt_compiler.app import app


SECRET = "FAKE-NEVER-RENDERED-0123456789"
TEMP = pathlib.Path(tempfile.mkdtemp(prefix="ps_http_tests_"))
client = TestClient(app)

COMPILED = {
    "detected_category": "coding",
    "detected_subcategory": "api",
    "detected_purpose": "Build a Flask API with registration and login.",
    "english_prompt": "Build a Flask REST API with user registration and login.",
    "persian_prompt": "یک API با Flask بساز که ثبت‌نام و ورود داشته باشد.",
    "preserved_requirements": ["Use Flask", "Registration", "Login"],
    "assumptions": ["SQLite storage"],
    "missing_information": ["Password hashing method"],
    "suggestions": ["Add rate limiting"],
}


def clear_files():
    for name in ("config.json", "usage.json", "library.json", "library.json.tmp"):
        path = TEMP / name
        if path.exists():
            path.unlink()


def point_storage_at_temp():
    config_module.CONFIG_FILE = TEMP / "config.json"
    config_module.USAGE_FILE = TEMP / "usage.json"
    config_module.LIBRARY_FILE = TEMP / "library.json"
    usage_service.USAGE_FILE = TEMP / "usage.json"
    library_service.LIBRARY_FILE = TEMP / "library.json"


class HttpTestCase(unittest.TestCase):
    """Shared isolation: fresh files, no environment key, no network."""

    def setUp(self):
        clear_files()
        point_storage_at_temp()
        patcher = mock.patch.dict(os.environ, {}, clear=False)
        patcher.start()
        self.addCleanup(patcher.stop)
        for name in config_module.API_KEY_ENV_VARS:
            os.environ.pop(name, None)

    def store(self, **values):
        payload = dict(config_module.DEFAULT_CONFIG)
        payload.update(values)
        (TEMP / "config.json").write_text(json.dumps(payload), encoding="utf-8")
        return payload


class WorkspacePageTests(HttpTestCase):
    def test_page_renders_the_workspace(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.text
        for marker in ("persian-prompt", "translate-btn", "library-modal", "usage-sidebar",
                       "theme-toggle", "sidebar-backdrop", "settings-modal"):
            self.assertIn(f'id="{marker}"', html, marker)

    def test_api_key_is_never_rendered(self):
        self.store(gemini_api_key=SECRET)
        html = client.get("/").text
        self.assertNotIn(SECRET, html)
        self.assertNotIn(f'value="{SECRET}"', html)
        self.assertIn('name="gemini_api_key"', html)

    def test_theme_is_applied_before_first_paint(self):
        html = client.get("/").text
        head = html.split("</head>")[0]
        self.assertIn("mapsim-theme", head)
        self.assertIn('data-theme="dark"', html)

    def test_static_assets_ship_the_theme_and_panel_contract(self):
        css = client.get("/static/style.css")
        self.assertEqual(css.status_code, 200)
        self.assertIn('[data-theme="light"]', css.text)
        self.assertIn("html.no-scroll body", css.text)

        script = client.get("/static/script.js")
        self.assertEqual(script.status_code, 200)
        self.assertIn("mapsim-theme", script.text)

    def test_processing_overlay_is_hidden_until_a_conversion_starts(self):
        html = client.get("/").text
        self.assertTrue(re.search(r'<div id="busy-overlay"[^>]*\bhidden\b', html),
                        "the processing overlay must not show on a fresh page")
        for marker in ("busy-steps", "busy-stage", "busy-elapsed", "busy-length", "busy-model"):
            self.assertIn(f'id="{marker}"', html, marker)
        self.assertIn('id="busy-stage" role="status"', html)

        css = (config_module.PROJECT_ROOT / "static" / "style.css").read_text(encoding="utf-8")
        self.assertIn(".busy[hidden]", css)
        self.assertIn("position: fixed", css.split(".busy {", 1)[1].split("}", 1)[0])

        script = (config_module.PROJECT_ROOT / "static" / "script.js").read_text(encoding="utf-8")
        self.assertIn("if (busyActive) return;", script)
        compile_body = script.split("async function compile()", 1)[1].split("function updateCounter", 1)[0]
        self.assertIn("startBusy(modelName(modelId));", compile_body)
        self.assertIn("stopBusy();", compile_body)

    def test_processing_sheet_outranks_every_panel_and_holds_the_keyboard(self):
        css = (config_module.PROJECT_ROOT / "static" / "style.css").read_text(encoding="utf-8")
        self.assertTrue(re.search(r"\.busy \{[^}]*z-index:\s*1500", css),
                        "the sheet must sit above the panels, below the toast")
        toast_rule = css.split(".toast {", 1)[1].split("}", 1)[0] if ".toast {" in css else ""
        toast_z = re.search(r"z-index:\s*(\d+)", toast_rule)
        self.assertTrue(toast_z and int(toast_z.group(1)) > 1500, "a toast has to land on top of the sheet")

        script = (config_module.PROJECT_ROOT / "static" / "script.js").read_text(encoding="utf-8")
        self.assertIn("if (busyActive) {", script)
        self.assertIn("if (event.key === 'Tab') event.preventDefault();", script)

    def test_input_counter_warns_before_the_request_is_sent(self):
        """The ceiling used to be discoverable only by failing, and the over-limit
        class had no CSS rule behind it."""
        html = client.get("/").text
        self.assertIn('id="input-limit"', html)

        script = (config_module.PROJECT_ROOT / "static" / "script.js").read_text(encoding="utf-8")
        self.assertIn("byId('input-limit').textContent = faInt(MAX_INPUT_LENGTH);", script)
        self.assertIn("classList.toggle('over-limit', length > MAX_INPUT_LENGTH)", script)
        self.assertIn("el['entry-input-counter'].classList.toggle('over-limit', length > MAX_INPUT_LENGTH)", script)
        self.assertNotIn("toLocaleString('fa-IR') + ' نویسه'", script)

        css = (config_module.PROJECT_ROOT / "static" / "style.css").read_text(encoding="utf-8")
        self.assertIn("#input-counter.over-limit", css)
        self.assertIn("#entry-input-counter.over-limit", css)
        rule = css.split("#input-counter.over-limit", 1)[1].split("}", 1)[0]
        self.assertIn("var(--danger)", rule)

    def test_prose_links_are_finger_targets(self):
        """Three links sat in running text with a 19-21px line box; a thumb on a
        phone could not aim at them."""
        css = (config_module.PROJECT_ROOT / "static" / "style.css").read_text(encoding="utf-8")
        rule = css.split(".note a,", 1)[1].split("}", 1)[0]
        for selector in (".mi-price a", ".field-help a", ".mapsim-footer a"):
            self.assertIn(selector, rule, selector)
        self.assertRegex(rule, r"padding-block:\s*13px")

    def test_script_only_reaches_for_ids_that_exist(self):
        """The panel rewrite broke on an id that no longer existed in the template."""
        html = client.get("/").text
        template_ids = set(re.findall(r'id="([^"]+)"', html))
        script = (config_module.PROJECT_ROOT / "static" / "script.js").read_text(encoding="utf-8")

        cached = re.search(r"function cacheElements\(\)\s*\{\s*\[(.*?)\]\s*\.forEach", script, re.S).group(1)
        wanted = set(re.findall(r"'([^']+)'", cached))
        wanted.update(re.findall(r"byId\('([^']+)'\)", script))
        wanted.discard("theme-color")  # injected lazily, but keep the guard honest
        self.assertEqual(sorted(wanted - template_ids), [])


class ModelsEndpointTests(HttpTestCase):
    def test_catalog_is_exposed_with_quota_fields(self):
        body = client.get("/models").json()
        self.assertEqual(len(body), len(MODELS))
        self.assertTrue(all({"id", "name", "category", "generate"} <= set(item) for item in body))


class UsageEndpointTests(HttpTestCase):
    def test_empty_usage_reports_zeroes(self):
        body = client.get("/usage").json()
        self.assertEqual(body["today"]["requests"], 0)
        self.assertEqual(body["today"]["total"], 0)
        self.assertEqual(len(body["models"]), len(MODELS))

    def test_recorded_calls_are_aggregated(self):
        usage_service.record_usage("gemini-3.5-flash", {
            "promptTokenCount": 100,
            "candidatesTokenCount": 50,
            "thoughtsTokenCount": 25,
            "totalTokenCount": 175,
        })
        body = client.get("/usage").json()
        self.assertEqual(body["today"]["requests"], 1)
        self.assertEqual(body["today"]["total"], 175)

        selected = [item for item in body["models"] if item["id"] == "gemini-3.5-flash"][0]
        self.assertEqual(selected["today_requests"], 1)
        self.assertEqual(selected["minute_requests"], 1)
        self.assertEqual(selected["minute_tokens"], 175)

    def test_yesterday_and_stale_events_are_out_of_today(self):
        now_ms = int(time.time() * 1000)
        usage_service.save_usage([
            {"m": "gemini-3.5-flash", "t": now_ms - 26 * 3600 * 1000, "in": 1, "out": 1, "th": 0, "tot": 2},
            {"m": "gemini-3.5-flash", "t": now_ms - 120_000, "in": 10, "out": 5, "th": 0, "tot": 15},
        ])
        body = client.get("/usage").json()
        self.assertEqual(body["today"]["requests"], 1)
        self.assertEqual(body["today"]["total"], 15)
        selected = [item for item in body["models"] if item["id"] == "gemini-3.5-flash"][0]
        self.assertEqual(selected["minute_requests"], 0)

    def test_events_older_than_a_week_are_pruned_on_write(self):
        now_ms = int(time.time() * 1000)
        usage_service.save_usage([{"m": "gemini-3.5-flash", "t": now_ms - 30 * 24 * 3600 * 1000,
                                   "in": 1, "out": 1, "th": 0, "tot": 2}])
        usage_service.record_usage("gemini-3.5-flash", {"totalTokenCount": 7})
        kept = usage_service.load_usage()
        self.assertEqual([event["tot"] for event in kept], [7])


class SettingsEndpointTests(HttpTestCase):
    def post(self, **fields):
        payload = {"gemini_api_key": "", "gemini_model": "gemini-3.5-flash", "system_prompt_override": ""}
        payload.update(fields)
        return client.post("/settings", data=payload)

    def test_blank_key_keeps_the_stored_one(self):
        self.store(gemini_api_key=SECRET)
        body = self.post().json()
        self.assertTrue(body["has_api_key"])
        self.assertEqual(body["api_key_source"], "stored")
        self.assertEqual(config_module.load_config()["gemini_api_key"], SECRET)
        self.assertNotIn(SECRET, json.dumps(body))

    def test_submitted_key_replaces_the_stored_one(self):
        self.store(gemini_api_key="OLD-KEY-0000")
        self.post(gemini_api_key=SECRET)
        self.assertEqual(config_module.load_config()["gemini_api_key"], SECRET)

    def test_clear_sentinel_deletes_the_key(self):
        self.store(gemini_api_key=SECRET)
        body = self.post(gemini_api_key=config_module.CLEAR_API_KEY).json()
        self.assertEqual(config_module.load_config()["gemini_api_key"], "")
        self.assertFalse(body["has_api_key"])
        self.assertEqual(body["api_key_source"], "")

    def test_masked_display_never_reveals_the_key(self):
        self.post(gemini_api_key=SECRET)
        body = self.post().json()
        self.assertNotIn(SECRET, json.dumps(body))
        self.assertTrue(body["api_key_masked"].startswith("••••••••"))

    def test_environment_key_wins_and_reports_its_source(self):
        os.environ["PROMPT_STUDIO_API_KEY"] = SECRET
        body = self.post().json()
        self.assertEqual(body["api_key_source"], "environment")
        self.assertNotIn(SECRET, json.dumps(body))

    def test_settings_file_is_owner_only(self):
        self.post(gemini_api_key=SECRET)
        self.assertEqual(oct((TEMP / "config.json").stat().st_mode)[-3:], "600")

    def test_model_choice_is_persisted(self):
        self.post(gemini_model="gemini-3.1-pro")
        self.assertEqual(config_module.load_config()["gemini_model"], "gemini-3.1-pro")


class TranslateEndpointTests(HttpTestCase):
    def setUp(self):
        super().setUp()
        self.calls = []

        async def fake_call(config, system_prompt, text, model_id):
            self.calls.append((system_prompt, text, model_id))
            return json.dumps(COMPILED), {"promptTokenCount": 10, "candidatesTokenCount": 4,
                                          "thoughtsTokenCount": 0, "totalTokenCount": 14}

        patcher = mock.patch.object(translation_route, "call_gemini", fake_call)
        patcher.start()
        self.addCleanup(patcher.stop)

    def translate(self, **body):
        return client.post("/translate", json=body)

    def test_empty_prompt_is_rejected(self):
        response = self.translate(prompt="   ")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.calls, [])

    def test_non_text_prompt_is_rejected(self):
        self.assertEqual(self.translate(prompt={"a": 1}).status_code, 400)
        self.assertEqual(self.calls, [])

    def test_oversized_prompt_is_rejected_before_the_provider(self):
        response = self.translate(prompt="x" * (library_service.MAX_INPUT_LENGTH + 1))
        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.calls, [])

    def test_non_generating_model_is_rejected(self):
        response = self.translate(prompt="یک چیزی", model="gemini-embedding-001")
        self.assertEqual(response.status_code, 400)
        error = response.json()["error"]
        self.assertIn("برای تبدیل استفاده نمی‌شود", error)
        self.assertIn("Gemini Embedding 1", error, "the rejected model is named in Persian guidance")
        self.assertEqual(self.calls, [])

    def test_malformed_body_is_rejected(self):
        response = client.post("/translate", content=b"{not json",
                               headers={"content-type": "application/json"})
        self.assertEqual(response.status_code, 400)

    def test_valid_prompt_returns_parsed_result_and_records_usage(self):
        self.store(gemini_api_key=SECRET)
        response = self.translate(prompt="یک API با Flask بساز", model="gemini-3.5-flash")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["parsed"]["english_prompt"], COMPILED["english_prompt"])
        self.assertEqual(body["parsed"]["detected_category"], "coding")
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.calls[0][1], "یک API با Flask بساز")
        self.assertEqual(client.get("/usage").json()["today"]["requests"], 1)

    def test_configured_model_is_used_when_none_is_sent(self):
        self.store(gemini_model="gemini-3.1-pro")
        response = self.translate(prompt="ساخت یک اسکریپت")
        self.assertEqual(response.json()["model"], "gemini-3.1-pro")
        self.assertEqual(self.calls[0][2], "gemini-3.1-pro")


class LibraryEndpointTests(HttpTestCase):
    def save(self, **overrides):
        payload = {
            "input": "یک API با Flask بساز که کاربران بتوانند ثبت‌نام و وارد شوند.",
            "model": "gemini-3.5-flash",
            "parsed": COMPILED,
            "tags": ["Flask", " auth ", "bad tag!!"],
        }
        payload.update(overrides)
        return client.post("/library", json=payload)

    def test_empty_library(self):
        body = client.get("/library").json()
        self.assertEqual(body["entries"], [])
        self.assertEqual(body["tags"], [])
        self.assertEqual(body["total"], 0)

    def test_saving_builds_a_normalized_entry(self):
        response = self.save()
        self.assertEqual(response.status_code, 201)
        entry = response.json()["entry"]
        self.assertEqual(len(entry["id"]), 12)
        self.assertEqual(entry["category"], "coding")
        self.assertIn("flask", entry["tags"])
        self.assertIn("bad-tag", entry["tags"])
        self.assertIn("coding", entry["tags"], "the detected category is auto-tagged")
        self.assertEqual(entry["title"], entry["input"][:library_service.TITLE_LENGTH])

    def test_saved_entry_mirrors_the_analysis_into_persian(self):
        # A payload without persian_analysis (an older compile) must still give the
        # result card a complete Persian half.
        entry = self.save().json()["entry"]
        mirror = entry["persian_analysis"]
        self.assertEqual(mirror["preserved_requirements"], COMPILED["preserved_requirements"])
        self.assertEqual(mirror["suggestions"], COMPILED["suggestions"])
        self.assertEqual(mirror["detected_purpose"], COMPILED["detected_purpose"])

    def test_persian_mirror_text_is_searchable(self):
        bilingual = dict(COMPILED)
        bilingual["persian_analysis"] = {
            "detected_purpose": "ساخت یک API با Flask برای ثبت‌نام و ورود.",
            "preserved_requirements": ["استفاده از Flask", "ثبت‌نام", "ورود"],
            "assumptions": ["ذخیره‌سازی با SQLite"],
            "missing_information": ["نحوهٔ هش کردن رمز"],
            "suggestions": ["محدود کردن نرخ درخواست"],
        }
        self.save(parsed=bilingual)
        self.assertEqual(client.get("/library", params={"q": "محدود کردن نرخ"}).json()["returned"], 1)
        self.assertEqual(client.get("/library", params={"q": "ناموجود"}).json()["returned"], 0)

    def test_blank_input_is_rejected(self):
        response = client.post("/library", json={"input": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("درخواست", response.json()["error"])

    def test_oversized_input_is_rejected(self):
        response = client.post("/library", json={"input": "x" * (library_service.MAX_INPUT_LENGTH + 1)})
        self.assertEqual(response.status_code, 400)

    def test_non_dict_body_is_rejected(self):
        self.assertEqual(client.post("/library", json=["a"]).status_code, 400)
        self.assertEqual(client.patch("/library/abc", json=["a"]).status_code, 400)

    def test_newest_entry_is_first(self):
        first = self.save().json()["entry"]["id"]
        second = self.save(input="دستور دوم برای ساخت گزارش هفتگی").json()["entry"]["id"]
        entries = client.get("/library").json()["entries"]
        self.assertEqual([entries[0]["id"], entries[1]["id"]], [second, first])

    def test_search_matches_input_and_prompt(self):
        self.save()
        self.assertEqual(client.get("/library", params={"q": "flask"}).json()["returned"], 1)
        self.assertEqual(client.get("/library", params={"q": "REST"}).json()["returned"], 1)
        self.assertEqual(client.get("/library", params={"q": "بلیک‌برد"}).json()["returned"], 0)

    def test_tag_and_favorite_filters(self):
        entry = self.save().json()["entry"]
        self.assertEqual(client.get("/library", params={"tag": "Flask"}).json()["returned"], 1)
        self.assertEqual(client.get("/library", params={"tag": "none"}).json()["returned"], 0)
        self.assertEqual(client.get("/library", params={"favorite": True}).json()["returned"], 0)

        client.patch(f"/library/{entry['id']}", json={"favorite": True})
        self.assertEqual(client.get("/library", params={"favorite": True}).json()["returned"], 1)

    def test_tags_payload_counts_entries(self):
        self.save()
        self.save(input="ساخت یک داشبورد تحلیل داده")
        tags = client.get("/library").json()["tags"]
        self.assertTrue(all({"tag", "count"} <= set(item) for item in tags))
        self.assertGreaterEqual(tags[0]["count"], 1)

    def test_patch_applies_the_editor_fields_only(self):
        entry = self.save().json()["entry"]
        response = client.patch(f"/library/{entry['id']}", json={
            "title": "عنوان ویرایش‌شده",
            "tags": ["هسته", "core,, one"],
            "input": "متن تازهٔ درخواست",
            "english_prompt": "the rewritten english prompt",
            "persian_prompt": "پرامپت فارسی بازنویسی‌شده",
            "id": "must-be-ignored",
            "created_at": 0,
        })
        self.assertEqual(response.status_code, 200)
        updated = response.json()["entry"]
        self.assertEqual(updated["title"], "عنوان ویرایش‌شده")
        self.assertIn("core-one", updated["tags"])
        self.assertEqual(updated["input"], "متن تازهٔ درخواست")
        self.assertEqual(updated["english_prompt"], "the rewritten english prompt")
        self.assertEqual(updated["persian_prompt"], "پرامپت فارسی بازنویسی‌شده")
        self.assertEqual(updated["id"], entry["id"])
        self.assertEqual(updated["created_at"], entry["created_at"])

    def test_empty_request_edit_is_rejected(self):
        entry = self.save().json()["entry"]
        response = client.patch(f"/library/{entry['id']}", json={"input": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("خالی", response.json()["error"])
        self.assertEqual(library_service.find_entry(entry["id"])["input"], entry["input"])

    def test_oversized_request_edit_is_rejected(self):
        entry = self.save().json()["entry"]
        response = client.patch(
            f"/library/{entry['id']}",
            json={"input": "الف" * (library_service.MAX_INPUT_LENGTH + 1)},
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(library_service.find_entry(entry["id"])["input"], entry["input"])

    def test_derived_title_follows_an_edited_request(self):
        entry = self.save().json()["entry"]
        client.patch(f"/library/{entry['id']}", json={"input": "ساخت لاگر رویداد برای سرویس پرداخت"})
        self.assertEqual(
            library_service.find_entry(entry["id"])["title"],
            "ساخت لاگر رویداد برای سرویس پرداخت",
        )

    def test_handwritten_title_survives_an_edited_request(self):
        entry = self.save().json()["entry"]
        client.patch(f"/library/{entry['id']}", json={"title": "پرامپت هستهٔ پرداخت"})
        client.patch(f"/library/{entry['id']}", json={"input": "درخواست جایگزین‌شده"})
        self.assertEqual(library_service.find_entry(entry["id"])["title"], "پرامپت هستهٔ پرداخت")

    def test_edited_text_is_searchable_afterwards(self):
        entry = self.save().json()["entry"]
        client.patch(f"/library/{entry['id']}", json={"english_prompt": "rate limited webhook retry"})
        self.assertEqual(client.get("/library", params={"q": "webhook"}).json()["returned"], 1)

    def test_blank_title_edit_falls_back_to_the_request(self):
        entry = self.save().json()["entry"]
        client.patch(f"/library/{entry['id']}", json={"title": "  "})
        self.assertEqual(library_service.find_entry(entry["id"])["title"], entry["input"][:library_service.TITLE_LENGTH])

    def test_missing_entry_returns_404(self):
        self.assertEqual(client.patch("/library/zzzzzzzzzzzz", json={"title": "x"}).status_code, 404)
        self.assertEqual(client.delete("/library/zzzzzzzzzzzz").status_code, 404)

    def test_delete_removes_the_entry(self):
        entry = self.save().json()["entry"]
        self.assertEqual(client.delete(f"/library/{entry['id']}").json()["status"], "deleted")
        self.assertEqual(client.get("/library").json()["total"], 0)

    def test_limit_is_clamped(self):
        self.save()
        self.assertEqual(client.get("/library", params={"limit": 0}).status_code, 422)
        self.assertEqual(client.get("/library", params={"limit": 5000}).status_code, 422)
        self.assertEqual(client.get("/library", params={"limit": 1}).json()["returned"], 1)

    def test_library_file_is_owner_only_and_leaves_no_temp(self):
        self.save()
        path = TEMP / "library.json"
        self.assertEqual(oct(path.stat().st_mode)[-3:], "600")
        self.assertFalse((TEMP / "library.json.tmp").exists())


class LauncherContractTests(unittest.TestCase):
    """The one-command launchers are the front door of the repository.

    They are shell scripts, so nothing else in the suite touches them: this checks
    that the two implementations still agree on the version floor, the environment
    variables, the dependency file and the server target, and that neither of them
    ever reads the stored API key.
    """

    def read(self, *parts):
        return (config_module.PROJECT_ROOT.joinpath(*parts)).read_text(encoding="utf-8")

    def test_the_launchers_ship_with_the_repository(self):
        for path in ("run.sh", "run.ps1", "run.bat", ".gitattributes",
                     ".github/workflows/ci.yml", "requirements.txt", "config.example.json"):
            self.assertTrue((config_module.PROJECT_ROOT / path).is_file(), path)

    def test_both_platforms_agree_on_the_bootstrap_contract(self):
        posix = self.read("run.sh")
        windows = self.read("run.ps1")
        for text in (posix, windows):
            self.assertIn("requirements.txt", text)
            self.assertIn(".venv", text)
            self.assertIn("prompt_compiler.app:app", text)
            for variable in ("PROMPT_STUDIO_HOST", "PROMPT_STUDIO_PORT",
                             "PROMPT_STUDIO_API_KEY", "GEMINI_API_KEY"):
                self.assertIn(variable, text, variable)
            self.assertIn("127.0.0.1", text)
            self.assertIn("8000", text)
            self.assertIn("uvicorn", text)
        self.assertIn("MIN_PYTHON_MINOR=10", posix)
        self.assertIn("$MinMinor = 10", windows)

    def test_the_batch_file_delegates_to_the_power_shell_script(self):
        """Two implementations of the same bootstrap always drift; only one is real."""
        batch = self.read("run.bat")
        self.assertIn("run.ps1", batch)
        self.assertIn("-ExecutionPolicy Bypass", batch)
        self.assertIn("-File", batch)

    def test_neither_launcher_reads_the_stored_key(self):
        """The launchers may check that config.json exists; reading it would put a
        live key into a terminal log or a clipboard."""
        for text in (self.read("run.sh"), self.read("run.ps1"), self.read("run.bat")):
            self.assertNotIn("gemini_api_key", text)
            for token in ("cat config.json", "type config.json", "Get-Content config.json",
                          "Get-Content -LiteralPath 'config.json'", "Import-Csv config.json"):
                self.assertNotIn(token, text, token)
        self.assertIn("[ ! -f config.json ]", self.read("run.sh"))
        self.assertIn("Test-Path -LiteralPath 'config.json' -PathType Leaf", self.read("run.ps1"))

    def test_requirements_are_pinned_and_newline_terminated(self):
        raw = (config_module.PROJECT_ROOT / "requirements.txt").read_bytes()
        self.assertTrue(raw.endswith(b"\n"), "a missing final newline breaks diff tools and some pip reads")
        lines = [line for line in raw.decode("utf-8").splitlines() if line.strip()]
        self.assertEqual(len(lines), 5)
        for line in lines:
            self.assertIn("==", line, line)

    def test_the_workflow_starts_the_project_through_the_launcher(self):
        """If CI imported the app directly it would prove nothing about installation."""
        ci = self.read(".github", "workflows", "ci.yml")
        self.assertIn("./run.sh --tests", ci)
        self.assertIn(".\\run.ps1 -Tests", ci)
        for system in ("ubuntu-latest", "macos-latest", "windows-latest"):
            self.assertIn(system, ci, system)
        self.assertIn("node --check static/script.js", ci)


if __name__ == "__main__":
    unittest.main()
