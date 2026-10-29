"""Supported model catalog and prompt categories."""

from collections import OrderedDict

from .config import DEFAULT_MODEL


_MODEL_ROWS = [
    {"id": "gemini-3.5-flash", "name": "Gemini 3.5 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.8-flash", "name": "Gemini 3.8 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.7-flash", "name": "Gemini 3.7 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.6-flash", "name": "Gemini 3.6 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-3.5-flash-lite", "name": "Gemini 3.5 Flash Lite", "category": "Text-out models", "rpm": 15, "tpm": 250_000, "rpd": 500, "generate": True},
    {"id": "gemini-3.1-pro", "name": "Gemini 3.1 Pro", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "gemini-3.1-flash-lite", "name": "Gemini 3.1 Flash Lite", "category": "Text-out models", "rpm": 15, "tpm": 250_000, "rpd": 500, "generate": True},
    {"id": "gemini-3-flash", "name": "Gemini 3 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite", "category": "Text-out models", "rpm": 10, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash", "category": "Text-out models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": True},
    {"id": "gemini-2.0-flash-lite", "name": "Gemini 2 Flash Lite", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "gemini-2.0-flash", "name": "Gemini 2 Flash", "category": "Text-out models", "rpm": None, "tpm": None, "rpd": None, "generate": True},
    {"id": "antigravity", "name": "Antigravity", "category": "Agents", "rpm": 60, "tpm": 100_000, "rpd": 100, "generate": False},
    {"id": "deep-research-pro", "name": "Deep Research Pro Preview", "category": "Agents", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "computer-use-preview", "name": "Computer Use Preview", "category": "Other models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-2.5-flash-preview-image", "name": "Nano Banana (Gemini 2.5 Flash Preview Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-2.5-flash-tts", "name": "Gemini 2.5 Flash TTS", "category": "Multi-modal generative models", "rpm": 3, "tpm": 10_000, "rpd": 10, "generate": False},
    {"id": "gemini-2.5-pro-tts", "name": "Gemini 2.5 Pro TTS", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3-pro-image", "name": "Nano Banana Pro (Gemini 3 Pro Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3.1-flash", "name": "Nano Banana 2 (Gemini 3.1 Flash Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3.1-flash-lite-image", "name": "Nano Banana 2 Lite (Gemini 3.1 Flash Lite Image)", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-3.1-flash-tts", "name": "Gemini 3.1 Flash TTS", "category": "Multi-modal generative models", "rpm": 3, "tpm": 10_000, "rpd": 10, "generate": False},
    {"id": "gemini-3.5-transcribe", "name": "Gemini 3.5 Transcribe", "category": "Live API", "rpm": 3, "tpm": 10_000, "rpd": 25, "generate": False},
    {"id": "gemini-embedding-001", "name": "Gemini Embedding 1", "category": "Other models", "rpm": 100, "tpm": 30_000, "rpd": 1_000, "generate": False},
    {"id": "gemini-embedding-2", "name": "Gemini Embedding 2", "category": "Other models", "rpm": 100, "tpm": 30_000, "rpd": 1_000, "generate": False},
    {"id": "gemini-omni-1.1-flash", "name": "Gemini Omni 1.1 Flash", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-omni-flash", "name": "Gemini Omni Flash", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-robotics-er-2-preview", "name": "Gemini Robotics ER 2 Preview", "category": "Other models", "rpm": 5, "tpm": 250_000, "rpd": 20, "generate": False},
    {"id": "gemma-4-26b", "name": "Gemma 4 26B", "category": "Other models", "rpm": 30, "tpm": 16_000, "rpd": 14_400, "generate": False},
    {"id": "gemma-4-31b", "name": "Gemma 4 31B", "category": "Other models", "rpm": 30, "tpm": 16_000, "rpd": 14_400, "generate": False},
    {"id": "lyria-3-clip", "name": "Lyria 3 Clip", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "lyria-3-pro", "name": "Lyria 3 Pro", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "veo-3-fast-generate", "name": "Veo 3 Fast Generate", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "veo-3-generate", "name": "Veo 3 Generate", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "veo-3-lite-generate", "name": "Veo 3 Lite Generate", "category": "Multi-modal generative models", "rpm": None, "tpm": None, "rpd": None, "generate": False},
    {"id": "gemini-2.5-flash-native-audio-dialog", "name": "Gemini 2.5 Flash Native Audio Dialog", "category": "Live API", "rpm": None, "tpm": 1_000_000, "rpd": None, "generate": False},
    {"id": "gemini-3-flash-live", "name": "Gemini 3 Flash Live", "category": "Live API", "rpm": None, "tpm": 65_000, "rpd": None, "generate": False},
    {"id": "gemini-3.5-live-translate", "name": "Gemini 3.5 Live Translate", "category": "Live API", "rpm": None, "tpm": 20_000, "rpd": None, "generate": False},
    {"id": "gemini-3.5-transcribe-live", "name": "Gemini 3.5 Transcribe Live", "category": "Live API", "rpm": None, "tpm": 20_000, "rpd": None, "generate": False},
    {"id": "gemini-3.8-live", "name": "Gemini 3.8 Live", "category": "Live API", "rpm": None, "tpm": 65_000, "rpd": None, "generate": False},
    {"id": "gemini-3.8-live-extended-thinking", "name": "Gemini 3.8 Live Extended Thinking", "category": "Live API", "rpm": None, "tpm": 65_000, "rpd": None, "generate": False},
]

#: Persian decision help for the model pickers. Costs are expressed as relative
#: tiers, never as invented prices; the pricing page link lives in the UI.
MODEL_INFO = {
    "gemini-3.8-flash": {
        "tier": "flash", "class_fa": "متعادل — تازه‌ترین نسل",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "پرامپت‌های پیچیده و چندبخشی که ساختار دقیق می‌خواهند",
        "note_fa": "جدیدترین نسخهٔ سری Flash؛ تعادل خوب میان کیفیت و سرعت با سقف درخواست روزانهٔ پایین.",
    },
    "gemini-3.7-flash": {
        "tier": "flash", "class_fa": "متعادل",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "استفادهٔ روزمره با کیفیت بالاتر از نسل‌های قدیمی‌تر",
        "note_fa": "نسل میانی Flash؛ وقتی ۳٫8 در دسترس نیست یا سقف کمتری لازم است.",
    },
    "gemini-3.6-flash": {
        "tier": "flash", "class_fa": "متعادل",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "کارهای عمومی متنی با طول متوسط",
        "note_fa": "نسل میانی Flash با رفتاری پایدار برای درخواست‌های معمولی.",
    },
    "gemini-3.5-flash": {
        "tier": "flash", "class_fa": "متعادل — پیشنهاد این برنامه",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "پیش‌فرض مناسب برای بیشتر تبدیل‌ها",
        "note_fa": "انتخاب پیش‌فرض استودیو: کیفیت قابل قبول در پرامپت‌های فنی، با سرعت و هزینهٔ متعادل.",
        "recommended": True,
    },
    "gemini-3-flash": {
        "tier": "flash", "class_fa": "متعادل — نسل ۳",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "مقایسهٔ کیفیت با نسخهٔ ۲٫۵ و استفادهٔ عمومی",
        "note_fa": "نسخهٔ پایهٔ نسل ۳ از سری Flash.",
    },
    "gemini-3.5-flash-lite": {
        "tier": "lite", "class_fa": "سبک (Lite) — ارزان‌ترین",
        "cost_fa": "کمترین هزینه", "speed_fa": "بسیار سریع",
        "use_fa": "تبدیل‌های کوتاه، پرامپت‌های ساده، حجم بالای درخواست",
        "note_fa": "بالاترین سقف درخواست روزانه در فهرست؛ برای درخواست‌های طولانی یا چندقید بهترین انتخاب نیست.",
    },
    "gemini-3.1-flash-lite": {
        "tier": "lite", "class_fa": "سبک (Lite)",
        "cost_fa": "کمترین هزینه", "speed_fa": "بسیار سریع",
        "use_fa": "کارهای دسته‌ای و درخواست‌های کوتاه با بودجهٔ محدود",
        "note_fa": "نسل ۳٫۱ از سری Lite؛ ارزان و پرسرعت با دقت کمتر از Flash.",
    },
    "gemini-2.5-flash-lite": {
        "tier": "lite", "class_fa": "سبک (Lite) — نسل پایدار ۲٫۵",
        "cost_fa": "کمترین هزینه", "speed_fa": "بسیار سریع",
        "use_fa": "تبدیل‌های ساده و آزمایش پیکربندی",
        "note_fa": "گزینهٔ سبک و آزموده برای کارهای سبک و بررسی سریع تنظیمات.",
    },
    "gemini-2.5-flash": {
        "tier": "flash", "class_fa": "متعادل — نسل پایدار ۲٫۵",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "وقتی رفتار آزمودهٔ نسل ۲٫۵ را می‌خواهید",
        "note_fa": "نسل قبلی Flash؛ رفتاری شناخته‌شده برای مقایسهٔ نتیجه.",
    },
    "gemini-3.1-pro": {
        "tier": "pro", "class_fa": "پرچم‌دار (Pro) — دقیق‌ترین",
        "cost_fa": "بیشترین هزینه", "speed_fa": "کندتر",
        "use_fa": "پرامپت‌های مهندسی‌شدهٔ پیچیده، چندزبانه و حساس به جزئیات",
        "note_fa": "بالاترین دقت استدلال در فهرست؛ مناسب کارهای مهمی که هزینه و زمان برایشان اولویت دوم است.",
    },
    "gemini-2.5-pro": {
        "tier": "pro", "class_fa": "پرچم‌دار (Pro) — نسل پایدار",
        "cost_fa": "بیشترین هزینه", "speed_fa": "کندتر",
        "use_fa": "تحلیل عمیق و پرامپت‌های با قواعد زیاد",
        "note_fa": "نسل قبلی Pro؛ همچنان قوی‌ترین گزینهٔ استدلالی با هزینهٔ بالا.",
    },
    "gemini-2.0-flash": {
        "tier": "flash", "class_fa": "متعادل — نسل قدیمی‌تر",
        "cost_fa": "هزینهٔ کم تا متوسط", "speed_fa": "سریع",
        "use_fa": "فقط برای مقایسهٔ رفتاری با نسل‌های جدیدتر",
        "note_fa": "نسل ۲٫۰؛ برای کارهای تازه پیشنهاد نمی‌شود.",
    },
    "gemini-2.0-flash-lite": {
        "tier": "lite", "class_fa": "سبک (Lite) — نسل قدیمی‌تر",
        "cost_fa": "کمترین هزینه", "speed_fa": "بسیار سریع",
        "use_fa": "فقط برای آزمایش و مقایسه",
        "note_fa": "قدیمی‌ترین گزینهٔ سبک فهرست؛ دقت و پایداری کمتری دارد.",
    },
}

#: Models that exist in the account but cannot compile a prompt here.
UNUSABLE_KIND = {
    "Multi-modal generative models": "تولید تصویر، صدا یا گفتار — پرامپت متنی نمی‌سازد",
    "Agents": "عامل خودگردان — با این رابط قابل اجرا نیست",
    "Live API": "ورودی/خروجی زندهٔ صوتی — برای این برنامه نیست",
    "Other models": "برداری‌سازی، ترجمهٔ هم‌زمان یا مدل‌های تخصصی",
}


def _with_info(row):
    model = dict(row)
    if model["generate"]:
        model.update(MODEL_INFO.get(model["id"], {}))
        model.setdefault("class_fa", "متعادل")
        model.setdefault("cost_fa", "هزینهٔ کم تا متوسط")
        model.setdefault("speed_fa", "سریع")
        model.setdefault("use_fa", "تبدیل درخواست فارسی به پرامپت ساختاریافته")
        model.setdefault("note_fa", "برای استفادهٔ عمومی مناسب است.")
        model.setdefault("recommended", False)
    else:
        model["unusable_fa"] = UNUSABLE_KIND.get(model["category"], "با این قابلیت برنامه قابل استفاده نیست")
        model["recommended"] = False
    return model


MODELS = [_with_info(row) for row in _MODEL_ROWS]

TEXT_MODEL_INFO = {model["id"]: model for model in MODELS if model["generate"]}


KNOWN_CATEGORIES = {
    "coding", "debugging", "research", "writing", "image_generation",
    "translation", "data_analysis", "planning", "automation", "general",
}


def group_models():
    groups = OrderedDict()
    for model in MODELS:
        groups.setdefault(model["category"], []).append(model)
    return groups
