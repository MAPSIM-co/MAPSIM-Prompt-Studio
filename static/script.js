/*
   MAPSIM Prompt Studio — front-end controller
   Vanilla JS on the existing FastAPI surface: compile, library, usage, settings,
   theme and the responsive panel layout. No framework, no build step.
*/
(function () {
    'use strict';

    const MAX_INPUT_LENGTH = 20000;          // mirrors prompt_compiler.services.library
    const THEME_KEY = 'mapsim-theme';
    const USAGE_DOCK_BREAKPOINT = '(min-width: 1000px)';

    const CATEGORY_NAMES = {
        image_generation: '🖼️ ساخت تصویر',
        research: '📚 ریسرچ / تحقیق',
        coding: '💻 برنامه‌نویسی',
        debugging: '🐛 دیباگ / رفع خطا',
        writing: '✍️ نوشتن',
        translation: '🔁 ترجمه',
        data_analysis: '📊 تحلیل داده',
        planning: '🗺️ برنامه‌ریزی',
        automation: '🤖 اتوماسیون',
        general: '📋 عمومی'
    };

    const CATEGORY_LABELS = {
        image_generation: 'image_generation', research: 'research', coding: 'coding',
        debugging: 'debugging', writing: 'writing', translation: 'translation',
        data_analysis: 'data_analysis', planning: 'planning', automation: 'automation',
        general: 'general'
    };

    const THEME_COLORS = { dark: '#070b12', light: '#f4f7fb' };

    const TIER_ORDER = { lite: 0, flash: 1, pro: 2 };

    const EXPAND_LABELS = {
        'expand-persian-btn': { more: 'بیشتر نمایش بده', less: 'جمع کردن' },
        'expand-english-btn': { more: 'Expand', less: 'Collapse' }
    };

    // A complete, contract-safe override the operator can trim instead of writing
    // a system prompt from scratch: dropping the JSON keys breaks the parser.
    const SYSTEM_SAMPLE = [
        'You are a Prompt Compiler. Turn the user\'s Persian request into a precise, executable English prompt for an AI coding agent, then translate that finalized English prompt into a faithful Persian version.',
        'Never invent requirements, technologies, files or constraints the user did not state. Unknown details go to missing_information, optional ideas go to suggestions.',
        'Keep every prohibition at full strength in both languages. Technical names such as Flask, PostgreSQL or REST API stay unchanged.',
        'Return ONLY valid JSON with exactly these keys: detected_category, detected_subcategory, detected_purpose, english_prompt, persian_prompt, preserved_requirements, assumptions, missing_information, suggestions, persian_analysis.',
        'persian_analysis mirrors detected_purpose and the four analysis arrays item for item in Persian, same order, same count.',
        'Match the prompt length to the complexity of the request; do not inflate simple requests.'
    ].join('\n');

    const MODEL_PRICING_URL = 'https://ai.google.dev/gemini-api/docs/pricing';

    let MODELS = [];
    let usageData = null;
    let currentResult = null;
    let currentInput = '';
    let currentModel = '';
    let libraryEntries = [];
    let libraryTags = [];
    let activeTag = '';
    let favoriteOnly = false;
    let usageTimer = null;

    const el = {};

    function byId(id) {
        return document.getElementById(id);
    }

    function cacheElements() {
        [
            'persian-prompt', 'model-select', 'translate-btn', 'input-counter',
            'category-badge', 'subcategory-badge', 'purpose-fa', 'purpose-en',
            'output', 'output-persian', 'persian-box', 'english-box',
            'expand-persian-btn', 'expand-english-btn',
            'copy-btn', 'copy-persian-btn', 'copy-both', 'save-to-library', 'clear-workspace',
            'use-in-claude', 'use-in-opencode',
            'requirements-list', 'assumptions-list', 'missing-list', 'suggestions-list',
            'requirements-list-fa', 'assumptions-list-fa', 'missing-list-fa', 'suggestions-list-fa',
            'active-model', 'theme-toggle', 'toggle-library', 'toggle-sidebar', 'manage-settings',
            'usage-sidebar', 'close-sidebar', 'usage-content', 'usage-header-total', 'usage-header-requests',
            'workspace', 'library-modal', 'close-library', 'library-search', 'library-tags', 'library-fav-only',
            'library-count', 'library-list',
            'entry-modal', 'close-entry', 'save-entry-btn', 'cancel-entry-btn',
            'entry-title-input', 'entry-tags-input', 'entry-input', 'entry-input-counter',
            'entry-persian-prompt', 'entry-english-prompt',
            'busy-overlay', 'busy-steps', 'busy-stage', 'busy-elapsed', 'busy-length', 'busy-model',
            'settings-modal', 'settings-form', 'close-modal', 'save-status', 'api-key-input',
            'model-default', 'model-default-info', 'system-prompt-override',
            'system-sample-btn', 'system-reset-btn',
            'sidebar-backdrop', 'toast'
        ].forEach(function (id) { el[id] = byId(id); });
    }

    /* ---------------- helpers ---------------- */

    function toast(message) {
        el.toast.textContent = message;
        el.toast.classList.add('show');
        clearTimeout(toast.timer);
        toast.timer = setTimeout(function () { el.toast.classList.remove('show'); }, 3200);
    }

    function formatTokens(value) {
        if (value === null || value === undefined) return '—';
        if (value >= 1e6) return (value / 1e6).toFixed(2).replace(/\.00$/, '') + 'M';
        if (value >= 1e3) return (value / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
        return String(value);
    }

    function faInt(value) {
        return (value || 0).toLocaleString('fa-IR');
    }

    function faDate(milliseconds) {
        const date = new Date(milliseconds);
        return date.toLocaleDateString('fa-IR') + ' ' +
            date.toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });
    }

    function escapeHtml(text) {
        return String(text === null || text === undefined ? '' : text)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
    }

    async function copyText(text) {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return;
        }
        const area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();
        const ok = document.execCommand('copy');
        document.body.removeChild(area);
        if (!ok) throw new Error('copy-failed');
    }

    async function request(url, options) {
        const response = await fetch(url, options);
        let payload = null;
        try { payload = await response.json(); } catch (error) { payload = null; }
        if (!response.ok) {
            const message = (payload && (payload.error || payload.detail)) || 'خطا در ارتباط با سرور';
            throw new Error(message);
        }
        return payload;
    }

    /* ---------------- theme ---------------- */

    function applyTheme(theme) {
        document.documentElement.dataset.theme = theme;
        const meta = byId('theme-color');
        if (meta) meta.setAttribute('content', THEME_COLORS[theme]);
        el['theme-toggle'].textContent = theme === 'light' ? '☀' : '☾';
        el['theme-toggle'].setAttribute('aria-pressed', theme === 'light' ? 'true' : 'false');
        el['theme-toggle'].setAttribute('title', theme === 'light' ? 'حالت روشن — برای تاریک کلیک کنید' : 'حالت تاریک — برای روشن کلیک کنید');
    }

    function initTheme() {
        let stored = null;
        try { stored = localStorage.getItem(THEME_KEY); } catch (error) { /* private mode */ }
        applyTheme(stored === 'light' || stored === 'dark' ? stored :
            (window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'));

        el['theme-toggle'].addEventListener('click', function () {
            const next = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
            applyTheme(next);
            try { localStorage.setItem(THEME_KEY, next); } catch (error) { /* private mode */ }
        });

        window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', function (event) {
            let storedTheme = null;
            try { storedTheme = localStorage.getItem(THEME_KEY); } catch (error) { /* private mode */ }
            if (!storedTheme) applyTheme(event.matches ? 'light' : 'dark');
        });
    }

    /* ---------------- panels: usage + library ---------------- */

    const usageDocked = window.matchMedia(USAGE_DOCK_BREAKPOINT);
    let usageOpen = false;
    let libraryOpen = false;
    let usageReturnFocus = null;
    let libraryReturnFocus = null;
    let editingEntry = null;
    let entryReturnFocus = null;

    function isUsageOpen() {
        return usageOpen;
    }

    function isLibraryOpen() {
        return libraryOpen;
    }

    function isEntryOpen() {
        return !el['entry-modal'].hidden;
    }

    /* Only the usage overlay needs the shared backdrop; the library modal carries
       its own scrim, so stacking both would put a click-blocking layer over it. */
    function syncScrim() {
        const needsScrim = !usageDocked.matches && usageOpen;
        el['sidebar-backdrop'].classList.toggle('show', needsScrim);
        document.documentElement.classList.toggle(
            'no-scroll',
            needsScrim || libraryOpen || isEntryOpen() || busyActive || !el['settings-modal'].hidden
        );
    }

    const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]), ' +
        'select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

    // Topmost dialog wins the focus trap: the entry editor, then settings,
    // then the library sheet, then the usage overlay.
    function activeDialog() {
        if (isEntryOpen()) return el['entry-modal'];
        if (!el['settings-modal'].hidden) return el['settings-modal'];
        if (libraryOpen) return el['library-modal'];
        if (!usageDocked.matches && usageOpen) return el['usage-sidebar'];
        return null;
    }

    function trapTab(event) {
        const container = activeDialog();
        if (!container) return;
        const items = Array.prototype.filter.call(container.querySelectorAll(FOCUSABLE), function (node) {
            return node.offsetWidth > 0 || node.offsetHeight > 0;
        });
        if (!items.length) return;
        const current = document.activeElement;
        const inside = container.contains(current);
        const edge = event.shiftKey ? items[0] : items[items.length - 1];
        if (!inside || current === edge) {
            event.preventDefault();
            (event.shiftKey ? items[items.length - 1] : items[0]).focus();
        }
    }

    function layoutUsage() {
        const drawer = el['usage-sidebar'];
        const docked = usageDocked.matches;
        if (docked) {
            drawer.hidden = !usageOpen;
            drawer.classList.remove('open');
        } else {
            drawer.hidden = false;
            drawer.classList.toggle('open', usageOpen);
        }
        el.workspace.classList.toggle('usage-closed', !usageOpen);
        el['toggle-sidebar'].setAttribute('aria-expanded', usageOpen ? 'true' : 'false');
        el['toggle-sidebar'].classList.toggle('active', usageOpen);
        syncScrim();
        if (usageOpen) startUsagePolling(); else stopUsagePolling();
    }

    function layoutLibrary() {
        el['library-modal'].hidden = !libraryOpen;
        el['toggle-library'].setAttribute('aria-expanded', libraryOpen ? 'true' : 'false');
        el['toggle-library'].classList.toggle('active', libraryOpen);
        syncScrim();
    }

    function restoreFocus(previous) {
        if (previous && typeof previous.focus === 'function' && document.contains(previous)) {
            previous.focus();
        }
    }

    function openUsage(previous) {
        usageOpen = true;
        usageReturnFocus = previous || document.activeElement;
        layoutUsage();
        fetchUsage();
        if (!usageDocked.matches) el['close-sidebar'].focus();
    }

    function closeUsage(previous) {
        usageOpen = false;
        layoutUsage();
        restoreFocus(previous || usageReturnFocus);
    }

    function toggleUsage() {
        if (usageOpen) closeUsage(); else openUsage();
    }

    function openLibrary(previous) {
        libraryOpen = true;
        libraryReturnFocus = previous || document.activeElement;
        layoutLibrary();
        loadLibrary();
        el['library-search'].focus();
    }

    function closeLibrary(previous) {
        libraryOpen = false;
        if (isEntryOpen()) {
            // The editor belongs to the sheet, so it never outlives the library.
            el['entry-modal'].hidden = true;
            editingEntry = null;
            entryReturnFocus = null;
        }
        layoutLibrary();
        restoreFocus(previous || libraryReturnFocus);
    }

    function toggleLibrary() {
        if (libraryOpen) closeLibrary(); else openLibrary();
    }

    function startUsagePolling() {
        stopUsagePolling();
        if (!usageOpen) return;
        if (usageDocked.matches && document.visibilityState !== 'visible') return;
        usageTimer = setInterval(function () {
            if (document.visibilityState === 'visible') fetchUsage();
        }, 5000);
    }

    function stopUsagePolling() {
        if (usageTimer) clearInterval(usageTimer);
        usageTimer = null;
    }

    /* ---------------- models ---------------- */

    async function fetchModels() {
        try {
            MODELS = await request('/models');
            populateModelSelect();
            populateSettingsModels();
        } catch (error) {
            toast('خطا در دریافت لیست مدل‌ها');
        }
    }

    function byTier(a, b) {
        const left = TIER_ORDER[a.tier] === undefined ? 9 : TIER_ORDER[a.tier];
        const right = TIER_ORDER[b.tier] === undefined ? 9 : TIER_ORDER[b.tier];
        if (left !== right) return left - right;
        return b.id.localeCompare(a.id);
    }

    function usableModels() {
        return MODELS.filter(function (model) { return model.generate; }).sort(byTier);
    }

    function unusableModels() {
        return MODELS.filter(function (model) { return !model.generate; });
    }

    function modelById(id) {
        return MODELS.find(function (model) { return model.id === id; }) || null;
    }

    function pickDefaultModel(preferred) {
        const usable = usableModels();
        if (!usable.length) return '';
        const found = usable.some(function (model) { return model.id === preferred; });
        return found ? preferred : usable[0].id;
    }

    function optionLabel(model) {
        if (!model.generate) return model.name + ' ✕';
        const label = model.class_fa ? model.name + ' — ' + model.class_fa : model.name;
        return model.recommended ? label + ' ★' : label;
    }

    function optionHint(model) {
        if (!model.generate) return model.unusable_fa || 'در این برنامه قابل استفاده نیست';
        return [model.class_fa, model.speed_fa, model.cost_fa, model.use_fa]
            .filter(Boolean).join(' · ');
    }

    function fillGroup(select, label, models) {
        if (!models.length) return;
        const group = document.createElement('optgroup');
        group.label = label;
        models.forEach(function (model) {
            const option = document.createElement('option');
            option.value = model.id;
            option.textContent = optionLabel(model);
            option.title = optionHint(model);
            option.disabled = !model.generate;
            group.appendChild(option);
        });
        select.appendChild(group);
    }

    function populateModelSelect() {
        const select = el['model-select'];
        select.innerHTML = '';
        fillGroup(select, 'مدل‌های قابل استفاده (تولید متن)', usableModels());
        fillGroup(select, 'مدل‌هایی که اینجا قابل استفاده نیستند', unusableModels());
        select.value = pickDefaultModel(window.DEFAULT_MODEL);
        updateActiveModel(select.value);
    }

    function populateSettingsModels() {
        const select = el['model-default'];
        if (!select) return;
        const chosen = select.value || window.DEFAULT_MODEL;
        select.innerHTML = '';
        fillGroup(select, 'مدل‌های قابل استفاده در این برنامه (تولید متن)', usableModels());
        fillGroup(select, 'مدل‌هایی که در این برنامه قابل استفاده نیستند', unusableModels());
        select.value = pickDefaultModel(chosen);
        renderModelInfo(select.value);
    }

    function limitsSummary(model) {
        return [
            ['درخواست در دقیقه', model.rpm],
            ['توکن در دقیقه', model.tpm],
            ['درخواست در روز', model.rpd]
        ].map(function (row) {
            const value = (row[1] === null || row[1] === undefined)
                ? 'بدون سقف ثبت‌شده' : formatTokens(row[1]);
            return row[0] + ' ' + value;
        }).join(' · ');
    }

    // The picker reads class, use, speed and cost from the catalog so the
    // operator can choose without guessing; prices stay the provider's numbers.
    function renderModelInfo(id) {
        const box = el['model-default-info'];
        if (!box) return;
        const model = modelById(id);
        if (!model) {
            box.innerHTML = '<p class="mi-note">برای دیدن جزئیات، یک مدل انتخاب کنید.</p>';
            return;
        }
        if (!model.generate) {
            box.innerHTML = '<p class="mi-note">' +
                escapeHtml(model.unusable_fa || 'این مدل در برنامه قابل استفاده نیست.') + '</p>';
            return;
        }

        const rows = [
            ['کلاس', model.class_fa],
            ['بهترین کاربرد', model.use_fa],
            ['سرعت', model.speed_fa],
            ['هزینه (سطح نسبی)', model.cost_fa],
            ['سقف درخواست', limitsSummary(model)]
        ].filter(function (row) { return row[1]; });

        let html = '<div class="mi-head">' +
            '<span class="mi-name" dir="ltr">' + escapeHtml(model.name) + '</span>' +
            (model.recommended ? '<span class="mi-star">پیشنهاد این برنامه</span>' : '') +
            '</div>';
        if (model.note_fa) html += '<p class="mi-note">' + escapeHtml(model.note_fa) + '</p>';
        html += '<dl class="mi-grid">' + rows.map(function (row) {
            return '<div class="mi-cell"><dt>' + escapeHtml(row[0]) + '</dt>' +
                '<dd>' + escapeHtml(row[1]) + '</dd></div>';
        }).join('') + '</dl>';
        html += '<p class="mi-price">قیمت هر مدل در ' +
            '<a href="' + MODEL_PRICING_URL + '" target="_blank" rel="noopener">صفحهٔ رسمی Google</a>' +
            ' اعلام می‌شود؛ سطوح هزینه در این صفحه نسبی‌اند.</p>';
        box.innerHTML = html;
    }

    function modelName(id) {
        const found = modelById(id);
        return found ? found.name : id;
    }

    function updateActiveModel(id) {
        const model = modelById(id);
        el['active-model'].textContent = model ? model.name : (id || '—');
        el['active-model'].title = model ? optionHint(model) : (id || '');
    }

    /* ---------------- processing overlay ---------------- */

    // Stage copy is reassurance for a call whose length we cannot predict, so the
    // later entries only say "still working" and never claim a fake step forward.
    const BUSY_STAGES = [
        { step: 1, at: 0, text: 'درخواست شما خوانده و پرامپت سیستم آماده می‌شود.' },
        { step: 2, at: 1400, text: 'درخواست به مدل ارسال شد؛ در انتظار شروع پاسخ هستیم.' },
        { step: 3, at: 6000, text: 'مدل در حال نوشتن پرامپت ساختاریافته و تحلیل دو زبانه است.' },
        { step: 3, at: 18000, text: 'کمی طولانی شد؛ سرعت پاسخ به مدل و اتصال اینترنت بستگی دارد. صفحه را نبندید.' },
        { step: 3, at: 45000, text: 'هنوز پاسخی نرسیده است. اگر بیش از یک دقیقه شد، تبدیل را دوباره امتحان کنید و کلید API را بررسی کنید.' }
    ];

    let busyActive = false;
    let busyTimers = [];
    let busyTicker = null;

    function setShellInert(inert) {
        const shell = document.querySelector('.app-shell');
        if (shell && 'inert' in shell) shell.inert = inert;
    }

    function faElapsed(seconds) {
        if (seconds < 60) return faInt(seconds) + ' ثانیه';
        return faInt(Math.floor(seconds / 60)) + ' دقیقه و ' + faInt(seconds % 60) + ' ثانیه';
    }

    function setBusyStep(step) {
        const items = el['busy-steps'].children;
        for (let index = 0; index < items.length; index += 1) {
            const node = items[index];
            const number = index + 1;
            node.classList.toggle('is-done', number < step);
            node.classList.toggle('is-active', number === step);
            if (number === step) node.setAttribute('aria-current', 'step');
            else node.removeAttribute('aria-current');
        }
    }

    function setBusyStage(text) {
        el['busy-stage'].textContent = text;
    }

    function clearBusyTimers() {
        busyTimers.forEach(clearTimeout);
        busyTimers = [];
        if (busyTicker) {
            clearInterval(busyTicker);
            busyTicker = null;
        }
    }

    function startBusy(modelLabel) {
        busyActive = true;
        el['busy-model'].textContent = modelLabel || '—';
        el['busy-length'].textContent = faInt(el['persian-prompt'].value.trim().length) + ' نویسه';
        el['busy-elapsed'].textContent = '۰ ثانیه';
        el['busy-overlay'].hidden = false;
        setShellInert(true);
        syncScrim();
        setBusyStage(BUSY_STAGES[0].text);
        setBusyStep(BUSY_STAGES[0].step);

        BUSY_STAGES.slice(1).forEach(function (stage) {
            busyTimers.push(setTimeout(function () {
                if (!busyActive) return;
                setBusyStage(stage.text);
                setBusyStep(stage.step);
            }, stage.at));
        });

        const startedAt = Date.now();
        busyTicker = setInterval(function () {
            el['busy-elapsed'].textContent = faElapsed(Math.round((Date.now() - startedAt) / 1000));
        }, 1000);
    }

    function stopBusy() {
        clearBusyTimers();
        busyActive = false;
        el['busy-overlay'].hidden = true;
        setBusyStep(1);
        setShellInert(false);
        syncScrim();
    }

    /* ---------------- compile ---------------- */

    function parseResult(content) {
        try {
            const cleaned = String(content).replace(/```json\n?/g, '').replace(/```/g, '').trim();
            const parsed = JSON.parse(cleaned);
            return {
                detected_category: parsed.detected_category || 'general',
                detected_subcategory: parsed.detected_subcategory || parsed.detectedSubcategory || '',
                detected_purpose: parsed.detected_purpose || '',
                persian_prompt: parsed.persian_prompt || parsed.persianPrompt || '',
                english_prompt: parsed.english_prompt || parsed.englishPrompt || content,
                preserved_requirements: parsed.preserved_requirements || [],
                assumptions: parsed.assumptions || [],
                missing_information: parsed.missing_information || [],
                suggestions: parsed.suggestions || [],
                persian_analysis: parsed.persian_analysis || {}
            };
        } catch (error) {
            return {
                detected_category: 'general', detected_subcategory: '', detected_purpose: '',
                persian_prompt: '', english_prompt: content, preserved_requirements: [],
                assumptions: [], missing_information: [], suggestions: [], persian_analysis: {}
            };
        }
    }

    // The result card shows the same analysis twice. When a server or a library
    // entry predates the bilingual contract the Persian half would read as empty
    // next to a full English one, so the English items fill the gaps position by
    // position and both halves always show the same number of rows.
    function mirrorList(persian, english) {
        const items = Array.isArray(persian) ? persian.filter(Boolean) : [];
        const source = Array.isArray(english) ? english : [];
        if (!items.length) return source.slice();
        if (items.length < source.length) return items.concat(source.slice(items.length));
        return items;
    }

    function analysisPair(result) {
        const fa = result.persian_analysis || {};
        const en = {
            purpose: result.detected_purpose || '',
            requirements: result.preserved_requirements || [],
            assumptions: result.assumptions || [],
            missing: result.missing_information || [],
            suggestions: result.suggestions || []
        };
        return {
            fa: {
                purpose: fa.detected_purpose || en.purpose,
                requirements: mirrorList(fa.preserved_requirements, en.requirements),
                assumptions: mirrorList(fa.assumptions, en.assumptions),
                missing: mirrorList(fa.missing_information, en.missing),
                suggestions: mirrorList(fa.suggestions, en.suggestions)
            },
            en: en
        };
    }

    function setTextOrHide(node, text) {
        node.textContent = text || '';
        node.classList.toggle('hidden', !text);
    }

    function renderList(container, items, emptyText) {
        container.innerHTML = '';
        if (!items || !items.length) {
            const empty = document.createElement('div');
            empty.className = 'analysis-empty';
            empty.textContent = emptyText;
            container.appendChild(empty);
            return;
        }
        items.forEach(function (item) {
            const row = document.createElement('div');
            row.className = 'analysis-item';
            row.textContent = item;
            container.appendChild(row);
        });
    }

    function syncExpandButton(boxId, preId, btnId) {
        const box = el[boxId];
        const pre = el[preId];
        const button = el[btnId];
        if (!box || !pre || !button) return;
        const expanded = box.classList.contains('is-expanded');
        const overflows = pre.scrollHeight > pre.clientHeight + 4;
        button.classList.toggle('hidden', !currentResult || (!expanded && !overflows));
        button.textContent = EXPAND_LABELS[btnId][expanded ? 'less' : 'more'];
        button.setAttribute('aria-expanded', expanded ? 'true' : 'false');
    }

    function syncExpand() {
        syncExpandButton('persian-box', 'output-persian', 'expand-persian-btn');
        syncExpandButton('english-box', 'output', 'expand-english-btn');
    }

    function renderResult(result, inputText, modelId) {
        currentResult = result;
        currentInput = inputText || currentInput;
        currentModel = modelId || currentModel;

        el['category-badge'].textContent = CATEGORY_NAMES[result.detected_category] ||
            CATEGORY_LABELS[result.detected_category] || 'عمومی';

        if (result.detected_subcategory) {
            el['subcategory-badge'].textContent = result.detected_subcategory;
            el['subcategory-badge'].classList.remove('hidden');
        } else {
            el['subcategory-badge'].textContent = '';
            el['subcategory-badge'].classList.add('hidden');
        }

        const pair = analysisPair(result);
        setTextOrHide(el['purpose-fa'], pair.fa.purpose);
        setTextOrHide(el['purpose-en'], pair.en.purpose);

        el['output-persian'].textContent = result.persian_prompt || '—';
        el.output.textContent = result.english_prompt || '—';
        el['copy-persian-btn'].disabled = !result.persian_prompt;
        el['copy-btn'].disabled = !result.english_prompt;

        renderList(el['requirements-list-fa'], pair.fa.requirements, 'موردی ثبت نشده است.');
        renderList(el['assumptions-list-fa'], pair.fa.assumptions, 'موردی ثبت نشده است.');
        renderList(el['missing-list-fa'], pair.fa.missing, 'موردی ثبت نشده است.');
        renderList(el['suggestions-list-fa'], pair.fa.suggestions, 'پیشنهادی ثبت نشده است.');

        renderList(el['requirements-list'], pair.en.requirements, 'Nothing recorded.');
        renderList(el['assumptions-list'], pair.en.assumptions, 'Nothing recorded.');
        renderList(el['missing-list'], pair.en.missing, 'Nothing recorded.');
        renderList(el['suggestions-list'], pair.en.suggestions, 'Nothing recorded.');

        syncExpand();
    }

    async function compile() {
        if (busyActive) return;
        const text = el['persian-prompt'].value.trim();
        if (!text) {
            toast('لطفاً یک درخواست فارسی بنویسید');
            el['persian-prompt'].focus();
            return;
        }
        if (text.length > MAX_INPUT_LENGTH) {
            toast('درخواست بلندتر از حد مجاز است (' + faInt(MAX_INPUT_LENGTH) + ' نویسه)');
            return;
        }

        const modelId = el['model-select'].value;
        el['translate-btn'].disabled = true;
        el['translate-btn'].textContent = 'در حال تبدیل...';
        startBusy(modelName(modelId));

        try {
            const data = await request('/translate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text, model: modelId })
            });
            setBusyStep(4);
            setBusyStage('پاسخ رسید؛ دو بخش فارسی و انگلیسی چیده می‌شود.');
            renderResult(data.parsed || parseResult(data.result), text, data.model || modelId);
            fetchUsage();
            toast('تبدیل انجام شد ✓');
        } catch (error) {
            toast(error.message);
        } finally {
            stopBusy();
            el['translate-btn'].disabled = false;
            el['translate-btn'].textContent = 'تبدیل کن';
            updateCounter();
        }
    }

    function updateCounter() {
        const length = el['persian-prompt'].value.length;
        el['input-counter'].textContent = faInt(length) + ' نویسه';
        el['input-counter'].classList.toggle('over-limit', length > MAX_INPUT_LENGTH);
    }

    function toggleBox(boxId, preId, btnId) {
        const expanded = el[boxId].classList.toggle('is-expanded');
        if (!expanded) el[preId].scrollTop = 0;
        syncExpand();
    }

    // The two agent buttons are a clipboard hand-off: the prompt is copied and the
    // operator pastes it into their own terminal session.
    function useInAgent(target) {
        if (!currentResult || !currentResult.english_prompt) {
            toast('ابتدا یک درخواست را تبدیل کنید');
            return;
        }
        copyText(currentResult.english_prompt)
            .then(function () { toast('پرامپت انگلیسی کپی شد — در ' + target + ' آن را Paste کنید.'); })
            .catch(function () { toast('خطا در کپی'); });
    }

    /* ---------------- settings ---------------- */

    let settingsReturnFocus = null;

    function openSettings() {
        settingsReturnFocus = document.activeElement;
        el['settings-modal'].hidden = false;
        el['save-status'].textContent = '';
        el['save-status'].className = 'save-status';
        syncScrim();
        el['api-key-input'].focus();
    }

    function closeSettings() {
        el['settings-modal'].hidden = true;
        syncScrim();
        restoreFocus(settingsReturnFocus);
    }

    // The stored key is never read back from the server, so after a save the
    // masked state is rewritten here instead of waiting for a page reload.
    function refreshKeyState(data) {
        if (data.api_key_source === 'environment') return;
        const state = el['settings-modal'].querySelector('.key-state');
        if (!state) return;
        const clearBox = el['settings-modal'].querySelector('input[name="remove_api_key"]');
        if (data.has_api_key) {
            state.innerHTML = '<span class="key-dot ok"></span> کلید ذخیره‌شده: ' +
                '<span dir="ltr">' + escapeHtml(data.api_key_masked) + '</span>' +
                ' — برای نگه‌داشتن، فیلد را خالی بگذارید.';
            el['api-key-input'].placeholder = 'برای تغییر، کلید تازه را وارد کنید';
            if (clearBox) clearBox.checked = false;
        } else {
            state.innerHTML = '<span class="key-dot off"></span> هنوز کلیدی تنظیم نشده است؛ ' +
                'تا این فیلد خالی است، دکمهٔ «تبدیل کن» خطای کلید می‌دهد.';
            el['api-key-input'].placeholder = 'کلید Google AI Studio را وارد کنید';
        }
        el['api-key-input'].value = '';
    }

    async function saveSettings(event) {
        event.preventDefault();
        const formData = new FormData(el['settings-form']);
        // The stored key is never shown in the page, so an empty field means
        // "keep it". The remove checkbox is the only way to delete it.
        if (formData.get('remove_api_key')) {
            formData.set('gemini_api_key', '__CLEAR__');
        }
        formData.delete('remove_api_key');

        try {
            const data = await request('/settings', { method: 'POST', body: formData });
            el['save-status'].textContent = '✓ تنظیمات ذخیره شد';
            el['save-status'].className = 'save-status success';
            refreshKeyState(data);
            if (data.gemini_model) {
                el['model-select'].value = pickDefaultModel(data.gemini_model);
                updateActiveModel(el['model-select'].value);
            }
            setTimeout(closeSettings, 900);
        } catch (error) {
            el['save-status'].textContent = error.message;
            el['save-status'].className = 'save-status error';
        }
    }

    function fillSystemSample() {
        const area = el['system-prompt-override'];
        if (area.value.trim() && !window.confirm('متن فعلی با نمونهٔ آماده جایگزین شود؟')) return;
        area.value = SYSTEM_SAMPLE;
        area.focus();
        toast('نمونه درج شد؛ فقط خط‌هایی را عوض کنید که واقعاً لازم دارید.');
    }

    function clearSystemOverride() {
        const area = el['system-prompt-override'];
        area.value = '';
        area.focus();
        toast('خالی شد — با ذخیره، دستور پیش‌فرض خود برنامه دوباره فعال می‌شود.');
    }

    /* ---------------- library ---------------- */

    async function saveCurrentToLibrary() {
        if (!currentResult) {
            toast('اول یک درخواست را تبدیل کنید');
            return;
        }
        try {
            const data = await request('/library', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    input: currentInput,
                    model: currentModel,
                    parsed: currentResult
                })
            });
            toast('به کتابخانه اضافه شد ✓');
            if (isLibraryOpen()) loadLibrary();
            return data.entry;
        } catch (error) {
            toast(error.message);
        }
    }

    function libraryQuery() {
        const params = new URLSearchParams();
        const query = el['library-search'].value.trim();
        if (query) params.set('q', query);
        if (activeTag) params.set('tag', activeTag);
        if (favoriteOnly) params.set('favorite', 'true');
        params.set('limit', '100');
        return '/library?' + params.toString();
    }

    async function loadLibrary() {
        el['library-list'].innerHTML = '<div class="usage-loading">در حال بارگذاری...</div>';
        try {
            const data = await request(libraryQuery());
            libraryEntries = data.entries || [];
            libraryTags = data.tags || [];
            renderLibraryTags(libraryTags, data.total || 0);
            renderLibraryList();
        } catch (error) {
            el['library-count'].textContent = 'خطا';
            el['library-list'].innerHTML =
                '<div class="panel-error">' + escapeHtml(error.message) + '</div>';
        }
    }

    function renderLibraryTags(tags, total) {
        const strip = el['library-tags'];
        strip.innerHTML = '';
        if (!tags.length) return;

        const all = document.createElement('button');
        all.type = 'button';
        all.className = 'tag-chip' + (activeTag ? '' : ' active');
        all.textContent = 'همه (' + faInt(total) + ')';
        all.addEventListener('click', function () {
            activeTag = '';
            loadLibrary();
        });
        strip.appendChild(all);

        tags.slice(0, 14).forEach(function (item) {
            const chip = document.createElement('button');
            chip.type = 'button';
            chip.className = 'tag-chip' + (activeTag === item.tag ? ' active' : '');
            chip.innerHTML = escapeHtml(item.tag) + ' <span class="tag-count">' + faInt(item.count) + '</span>';
            chip.addEventListener('click', function () {
                activeTag = activeTag === item.tag ? '' : item.tag;
                loadLibrary();
            });
            strip.appendChild(chip);
        });
    }

    function renderLibraryList() {
        const list = el['library-list'];
        el['library-count'].textContent = faInt(libraryEntries.length) + ' مورد';
        list.innerHTML = '';

        if (!libraryEntries.length) {
            const empty = document.createElement('div');
            empty.className = 'panel-empty';
            empty.innerHTML = '<strong>موردی پیدا نشد</strong>' +
                'ابتدا یک درخواست را تبدیل کنید و روی «ذخیره در کتابخانه» بزنید.';
            list.appendChild(empty);
            return;
        }

        libraryEntries.forEach(function (entry) {
            list.appendChild(buildLibraryItem(entry));
        });
    }

    function buildLibraryItem(entry) {
        const item = document.createElement('article');
        item.className = 'lib-item' + (entry.favorite ? ' is-favorite' : '');
        item.dataset.id = entry.id;

        const category = CATEGORY_NAMES[entry.category] || CATEGORY_LABELS[entry.category] || '';
        const tags = (entry.tags || []).map(function (tag) {
            return '<span class="lib-tag">' + escapeHtml(tag) + '</span>';
        }).join('');

        item.innerHTML =
            '<div class="lib-top">' +
                '<h3 class="lib-title">' + escapeHtml(entry.title) + '</h3>' +
                '<button type="button" class="lib-fav" data-action="favorite" ' +
                    'aria-pressed="' + (entry.favorite ? 'true' : 'false') + '" ' +
                    'title="علاقه‌مندی">★</button>' +
            '</div>' +
            '<p class="lib-input">' + escapeHtml(entry.input) + '</p>' +
            '<p class="lib-prompt">' + escapeHtml(entry.english_prompt) + '</p>' +
            '<div class="lib-meta">' +
                (category ? '<span class="badge">' + escapeHtml(category) + '</span>' : '') +
                '<span>' + faDate(entry.created_at) + '</span>' +
                (entry.model ? '<span>' + escapeHtml(modelName(entry.model)) + '</span>' : '') +
            '</div>' +
            (tags ? '<div class="lib-tags">' + tags + '</div>' : '') +
            '<div class="lib-actions">' +
                '<button type="button" class="btn btn-ghost btn-small" data-action="load">بارگذاری</button>' +
                '<button type="button" class="btn btn-ghost btn-small" data-action="copy">کپی انگلیسی</button>' +
                '<button type="button" class="btn btn-ghost btn-small" data-action="edit">ویرایش</button>' +
                '<button type="button" class="btn btn-ghost btn-small btn-danger" data-action="delete">حذف</button>' +
            '</div>';

        return item;
    }

    function findEntry(id) {
        return libraryEntries.find(function (entry) { return entry.id === id; });
    }

    function updateEntryCounter() {
        const length = el['entry-input'].value.length;
        el['entry-input-counter'].textContent = faInt(length) + ' نویسه';
        el['entry-input-counter'].classList.toggle('over-limit', length > MAX_INPUT_LENGTH);
    }

    function openEntryEditor(entry, trigger) {
        editingEntry = entry;
        entryReturnFocus = trigger || document.activeElement;
        el['entry-title-input'].value = entry.title || '';
        el['entry-tags-input'].value = (entry.tags || []).join('، ');
        el['entry-input'].value = entry.input || '';
        el['entry-persian-prompt'].value = entry.persian_prompt || '';
        el['entry-english-prompt'].value = entry.english_prompt || '';
        el['entry-modal'].hidden = false;
        syncScrim();
        updateEntryCounter();
        el['entry-input'].focus();
    }

    function closeEntryEditor() {
        el['entry-modal'].hidden = true;
        const previous = entryReturnFocus;
        editingEntry = null;
        entryReturnFocus = null;
        syncScrim();
        restoreFocus(previous);
    }

    async function saveEntryEditor() {
        if (!editingEntry) return;
        const text = el['entry-input'].value.trim();
        if (!text) {
            toast('متن درخواست نمی‌تواند خالی بماند');
            el['entry-input'].focus();
            return;
        }
        if (text.length > MAX_INPUT_LENGTH) {
            toast('درخواست بلندتر از حد مجاز است (' +
                faInt(MAX_INPUT_LENGTH) + ' نویسه)');
            return;
        }

        const saved = await patchEntry(editingEntry.id, {
            title: el['entry-title-input'].value,
            tags: el['entry-tags-input'].value.split(/[،,]+/),
            input: text,
            persian_prompt: el['entry-persian-prompt'].value,
            english_prompt: el['entry-english-prompt'].value
        }, 'تغییرات ذخیره شد ✓');
        if (saved) closeEntryEditor();
    }

    async function handleLibraryAction(action, button) {
        const item = button.closest('.lib-item');
        if (!item) return;
        const id = item.dataset.id;
        const entry = findEntry(id);
        if (!entry) return;

        if (action === 'load') {
            el['persian-prompt'].value = entry.input;
            renderResult({
                detected_category: entry.category,
                detected_subcategory: entry.subcategory,
                detected_purpose: entry.purpose,
                persian_prompt: entry.persian_prompt,
                english_prompt: entry.english_prompt,
                preserved_requirements: entry.preserved_requirements,
                assumptions: entry.assumptions,
                missing_information: entry.missing_information,
                suggestions: entry.suggestions,
                persian_analysis: entry.persian_analysis || {}
            }, entry.input, entry.model);
            if (entry.model && el['model-select'].value !== entry.model) {
                el['model-select'].value = entry.model;
                updateActiveModel(entry.model);
            }
            updateCounter();
            closeLibrary();
            el['output'].scrollIntoView({ block: 'nearest' });
            toast('از کتابخانه بارگذاری شد');
            return;
        }

        if (action === 'copy') {
            try {
                await copyText(entry.english_prompt);
                toast('پرامپت انگلیسی کپی شد ✓');
            } catch (error) {
                toast('خطا در کپی');
            }
            return;
        }

        if (action === 'favorite') {
            await patchEntry(id, { favorite: !entry.favorite });
            return;
        }

        if (action === 'edit') {
            openEntryEditor(entry, button);
            return;
        }

        if (action === 'delete') {
            if (!window.confirm('این مورد از کتابخانه حذف شود؟')) return;
            try {
                await request('/library/' + encodeURIComponent(id), { method: 'DELETE' });
                toast('حذف شد');
                await loadLibrary();
            } catch (error) {
                toast(error.message);
            }
        }
    }

    async function patchEntry(id, changes, doneMessage) {
        try {
            await request('/library/' + encodeURIComponent(id), {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(changes)
            });
            await loadLibrary();
            toast(doneMessage || 'بروز شد ✓');
            return true;
        } catch (error) {
            toast(error.message);
            return false;
        }
    }

    /* ---------------- usage rendering ---------------- */

    function meterBar(label, used, limit, unit) {
        const width = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
        const caption = limit === null || limit === undefined
            ? '<span class="meter-used">' + formatTokens(used) + ' ' + unit + '</span>' +
              '<span class="meter-remaining">نامحدود</span>'
            : '<span class="meter-used">' + faInt(used) + ' / ' + formatTokens(limit) + ' ' + unit + '</span>' +
              '<span class="meter-remaining">باقی‌مانده: ' + faInt(Math.max(0, limit - used)) + '</span>';
        const state = width >= 90 ? ' bar-danger' : (width >= 70 ? ' bar-warn' : '');
        return '<div class="meter">' +
            '<div class="meter-head"><span class="meter-label">' + label + '</span>' + caption + '</div>' +
            '<div class="meter-track"><div class="meter-bar' + state + '" style="width:' + width.toFixed(1) + '%"></div></div>' +
            '</div>';
    }

    function renderHeaderUsage() {
        if (!usageData || !usageData.today) return;
        el['usage-header-total'].textContent = formatTokens(usageData.today.total) + ' توکن';
        el['usage-header-requests'].textContent = faInt(usageData.today.requests) + ' درخواست';
    }

    function renderUsage() {
        renderHeaderUsage();
        if (!isUsageOpen() || !usageData) return;

        const today = usageData.today;
        const selected = el['model-select'].value;
        const model = usageData.models.find(function (item) { return item.id === selected; }) || usageData.models[0];

        let html = '<div class="usage-summary">' +
            '<div class="sum-cell"><span class="sum-num">' + faInt(today.requests) + '</span><span class="sum-lbl">درخواست امروز</span></div>' +
            '<div class="sum-cell"><span class="sum-num">' + formatTokens(today.input) + '</span><span class="sum-lbl">توکن ورودی</span></div>' +
            '<div class="sum-cell"><span class="sum-num">' + formatTokens(today.output) + '</span><span class="sum-lbl">توکن خروجی</span></div>' +
            '<div class="sum-cell"><span class="sum-num">' + formatTokens(today.total) + '</span><span class="sum-lbl">جمع کل</span></div>' +
            '</div>';

        if (model) {
            html += '<div class="usage-model-card">' +
                '<div class="umc-title">مدل منتخب: <strong>' + escapeHtml(model.name) + '</strong></div>' +
                meterBar('درخواست امروز (RPD)', model.today_requests, model.rpd, '') +
                meterBar('توکن در دقیقه (TPM)', model.minute_tokens, model.tpm, 'توکن') +
                meterBar('درخواست در دقیقه (RPM)', model.minute_requests, model.rpm, '') +
                '</div>';
        }

        const used = usageData.models
            .filter(function (item) { return item.today_requests > 0; })
            .sort(function (a, b) { return b.today_tokens - a.today_tokens; });

        if (used.length) {
            html += '<div class="usage-model-list"><div class="uml-title">مصرف امروز مدل‌ها</div>';
            used.forEach(function (item) {
                html += '<div class="uml-row">' +
                    '<span class="uml-name" title="' + escapeHtml(item.name) + '">' + escapeHtml(item.name) + '</span>' +
                    '<span class="uml-val">' + faInt(item.today_requests) + ' درخواست</span>' +
                    '<span class="uml-tok">' + formatTokens(item.today_tokens) + ' توکن</span>' +
                    '</div>';
            });
            html += '</div>';
        } else {
            html += '<div class="usage-empty">هنوز مصرفی ثبت نشده — اولین درخواست خود را ارسال کنید.</div>';
        }

        el['usage-content'].innerHTML = html;
    }

    async function fetchUsage() {
        try {
            usageData = await request('/usage');
            renderUsage();
        } catch (error) {
            el['usage-header-total'].textContent = '— توکن';
            if (isUsageOpen()) {
                el['usage-content'].innerHTML = '<div class="panel-error">خطا در دریافت آمار مصرف</div>';
            }
        }
    }

    /* ---------------- wiring ---------------- */

    function bindEvents() {
        el['translate-btn'].addEventListener('click', compile);

        el['persian-prompt'].addEventListener('input', updateCounter);
        el['persian-prompt'].addEventListener('keydown', function (event) {
            if ((event.metaKey || event.ctrlKey) && event.key === 'Enter') {
                event.preventDefault();
                compile();
            }
        });

        el['model-select'].addEventListener('change', function () {
            updateActiveModel(el['model-select'].value);
            renderUsage();
        });

        el['copy-btn'].addEventListener('click', function () {
            if (!currentResult) return;
            copyText(currentResult.english_prompt)
                .then(function () { toast('پرامپت انگلیسی کپی شد ✓'); })
                .catch(function () { toast('خطا در کپی'); });
        });

        el['copy-persian-btn'].addEventListener('click', function () {
            if (!currentResult || !currentResult.persian_prompt) return;
            copyText(currentResult.persian_prompt)
                .then(function () { toast('پرامپت فارسی کپی شد ✓'); })
                .catch(function () { toast('خطا در کپی'); });
        });

        el['copy-both'].addEventListener('click', function () {
            if (!currentResult) {
                toast('خروجی برای کپی وجود ندارد');
                return;
            }
            const both = '【فارسی】\n' + (currentResult.persian_prompt || '—') +
                '\n\n【English】\n' + (currentResult.english_prompt || '—');
            copyText(both)
                .then(function () { toast('هر دو پرامپت کپی شد ✓'); })
                .catch(function () { toast('خطا در کپی'); });
        });

        el['save-to-library'].addEventListener('click', saveCurrentToLibrary);

        el['use-in-claude'].addEventListener('click', function () { useInAgent('Claude Code'); });
        el['use-in-opencode'].addEventListener('click', function () { useInAgent('OpenCode'); });

        el['expand-persian-btn'].addEventListener('click', function () {
            toggleBox('persian-box', 'output-persian', 'expand-persian-btn');
        });
        el['expand-english-btn'].addEventListener('click', function () {
            toggleBox('english-box', 'output', 'expand-english-btn');
        });

        el['clear-workspace'].addEventListener('click', function () {
            el['persian-prompt'].value = '';
            currentResult = null;
            renderResult({
                detected_category: '', detected_subcategory: '', detected_purpose: '',
                persian_prompt: '', english_prompt: '', preserved_requirements: [],
                assumptions: [], missing_information: [], suggestions: [], persian_analysis: {}
            }, '', '');
            currentResult = null;
            el['category-badge'].textContent = '';
            el['subcategory-badge'].classList.add('hidden');
            el['persian-box'].classList.remove('is-expanded');
            el['english-box'].classList.remove('is-expanded');
            syncExpand();
            updateCounter();
            el['persian-prompt'].focus();
        });

        el['toggle-sidebar'].addEventListener('click', toggleUsage);
        el['close-sidebar'].addEventListener('click', function () { closeUsage(); });

        el['toggle-library'].addEventListener('click', toggleLibrary);
        el['close-library'].addEventListener('click', function () { closeLibrary(); });

        let searchTimer = null;
        el['library-search'].addEventListener('input', function () {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(loadLibrary, 280);
        });

        el['library-fav-only'].addEventListener('change', function () {
            favoriteOnly = el['library-fav-only'].checked;
            loadLibrary();
        });

        el['library-list'].addEventListener('click', function (event) {
            const button = event.target.closest('[data-action]');
            if (button) handleLibraryAction(button.dataset.action, button);
        });

        el['close-entry'].addEventListener('click', closeEntryEditor);
        el['cancel-entry-btn'].addEventListener('click', closeEntryEditor);
        el['save-entry-btn'].addEventListener('click', saveEntryEditor);
        el['entry-input'].addEventListener('input', updateEntryCounter);
        el['entry-modal'].addEventListener('click', function (event) {
            if (event.target === el['entry-modal']) closeEntryEditor();
        });
        el['entry-modal'].addEventListener('keydown', function (event) {
            if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                event.preventDefault();
                saveEntryEditor();
            }
        });

        el['sidebar-backdrop'].addEventListener('click', function () {
            if (!usageDocked.matches && usageOpen) closeUsage();
        });

        el['manage-settings'].addEventListener('click', openSettings);
        el['close-modal'].addEventListener('click', closeSettings);
        el['settings-modal'].addEventListener('click', function (event) {
            if (event.target === el['settings-modal']) closeSettings();
        });
        el['settings-form'].addEventListener('submit', saveSettings);
        el['model-default'].addEventListener('change', function () {
            renderModelInfo(el['model-default'].value);
        });
        el['system-sample-btn'].addEventListener('click', fillSystemSample);
        el['system-reset-btn'].addEventListener('click', clearSystemOverride);

        // Long prompts are scrollable, so the "show more" control only appears
        // when a box actually overflows; re-check when the box changes size.
        let expandTimer = null;
        window.addEventListener('resize', function () {
            clearTimeout(expandTimer);
            expandTimer = setTimeout(syncExpand, 160);
        });

        // Clicking the dimmed area around the library sheet closes it.
        el['library-modal'].addEventListener('click', function (event) {
            if (event.target === el['library-modal']) closeLibrary();
        });

        document.addEventListener('keydown', function (event) {
            // The processing overlay owns the page: nothing behind it is reachable
            // and Escape must not discard an in-flight conversion.
            if (busyActive) {
                if (event.key === 'Tab') event.preventDefault();
                return;
            }
            if (event.key === 'Tab') {
                trapTab(event);
                return;
            }
            if (event.key !== 'Escape') return;
            if (isEntryOpen()) closeEntryEditor();
            else if (!el['settings-modal'].hidden) closeSettings();
            else if (isLibraryOpen()) closeLibrary();
            else if (isUsageOpen() && !usageDocked.matches) closeUsage();
        });

        usageDocked.addEventListener('change', layoutUsage);

        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState === 'visible') {
                fetchUsage();
                startUsagePolling();
            } else {
                stopUsagePolling();
            }
        });
    }

    document.addEventListener('DOMContentLoaded', function () {
        cacheElements();
        initTheme();
        bindEvents();
        layoutUsage();
        layoutLibrary();
        byId('input-limit').textContent = faInt(MAX_INPUT_LENGTH);
        updateCounter();
        fetchModels();
        fetchUsage();
    });
})();
