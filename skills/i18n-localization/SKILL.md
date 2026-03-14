---
name: i18n-localization
description: |
  Internationalization architecture, translation management, and locale-aware formatting.
  TRIGGER: "i18n", "internationalization", "localization", "l10n", "translations", "locale",
  "RTL support", "right-to-left", "pluralization", "ICU message format", "react-i18next",
  "next-intl", "vue-i18n", "gettext", "translation keys", "language switching"
  EXCLUDE: Content writing/copywriting (use copywriting), general React/Vue/Angular questions without i18n context
---

# i18n & Localization

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/framework-setup.md` | Setting up i18n in a specific framework, language detection, SSR translations | General i18n questions, migration planning |
| `references/rtl-pluralization.md` | RTL support, bidirectional text, plural rules, ICU MessageFormat deep dive | LTR-only projects, simple string replacement |
| `references/migration-extraction.md` | Brownfield migration, string extraction, TMS setup, CI/CD translation pipelines | Greenfield projects, framework-specific setup |

---

## What Are You Internationalizing?

Route to the correct approach before writing any code.

**IF greenfield (new project):**
- Architecture-first: pick framework library, define namespace strategy, set up locale file structure BEFORE writing components
- Load `references/framework-setup.md` for framework-specific patterns
- Wire language detection chain early: URL segment > cookie > Accept-Language > default

**IF brownfield (existing app with hardcoded strings):**
- Load `references/migration-extraction.md` for extraction strategy
- DO NOT attempt full extraction in one pass -- prioritize by page traffic
- Phase 1: highest-traffic user-facing pages. Phase 2: forms and errors. Phase 3: admin/internal. Phase never: log messages.

**IF adding RTL support to an existing i18n app:**
- Load `references/rtl-pluralization.md`
- Audit all CSS for physical properties (margin-left, padding-right) -- every one must become logical
- RTL is not "just flip the CSS" -- icon mirroring, bidirectional text isolation, and number rendering all need separate handling

**IF complex message formatting (plurals, dates, gender-dependent text):**
- Load `references/rtl-pluralization.md` (ICU section)
- English "one/other" plural rules are the EXCEPTION -- most languages have 3-6 plural categories
- ICU MessageFormat is the only format that handles nested gender+plural combinations correctly

**IF translation workflow/ops (TMS, CI/CD, translator handoff):**
- Load `references/migration-extraction.md` (TMS section)
- Context is everything for translation quality -- screenshots and component metadata reduce revision cycles by 40-60%

---

## Architecture Decision Tree

Pick the library that matches your stack. Do not mix i18n libraries within the same rendering layer.

| Stack | Library | Key Setup Pattern | Gotcha |
|-------|---------|-------------------|--------|
| React SPA | react-i18next | Namespaced JSON, lazy-loaded per route via `i18next-http-backend` | Suspense boundary required for async loading |
| Next.js (App Router) | next-intl | Middleware-based locale routing, RSC server translations | `useTranslations` only works in Client Components unless using `getTranslations` in Server Components |
| Next.js (Pages Router) | next-i18next | `serverSideTranslations` in getStaticProps/getServerSideProps | Must pass namespaces explicitly -- missed namespace = silent empty string |
| Vue 3 | vue-i18n | Composition API `useI18n()`, per-route lazy loading | Global vs component-local scope confusion causes key collisions |
| Angular | @angular/localize | Build-time i18n, AOT compiled, one build per locale | No runtime language switching -- requires full rebuild per locale |
| Django | django.utils.translation | gettext .po/.mo files, `{% trans %}` template tags | `makemessages` misses strings in JavaScript -- need separate js catalog extraction |
| Flask | Flask-Babel | gettext .po/.mo, Jinja2 `{{ _('key') }}` | Lazy strings required for module-level translated text |
| Node.js backend | i18next | Can share translation files with frontend react-i18next | Server must set locale per-request (middleware), not globally |
| Rails | rails-i18n | YAML locale files, `t('.key')` scoped to view path | Deeply nested YAML keys silently return nil on typo |

---

## Translation Key Naming Convention

Namespace hierarchy: `{feature}.{component}.{element}`

```
auth.login.title          = "Sign In"
auth.login.submit_button  = "Sign In to Your Account"
auth.login.error.invalid  = "Invalid email or password"
auth.signup.title         = "Create Account"
cart.summary.item_count   = "{count, plural, one {# item} other {# items}}"
cart.checkout.cta         = "Proceed to Checkout"
common.actions.save       = "Save"
common.actions.cancel     = "Cancel"
common.errors.network     = "Connection failed. Please try again."
```

Rules:
- snake_case for keys (kebab-case breaks dot-access in some libraries)
- `common.*` namespace for shared strings (buttons, labels, errors)
- Feature namespaces match route/module structure
- NEVER use English text as the key -- keys are identifiers, not content
- Max 4 levels deep -- beyond that, split into separate namespace files

---

## Locale File Organization

**JSON (recommended for JS/TS projects):**
```
locales/
  en/
    common.json       # Shared: buttons, labels, generic errors
    auth.json         # Login, signup, password reset
    dashboard.json    # Dashboard-specific
  es/
    common.json
    auth.json
    dashboard.json
```

**PO/MO (recommended for Python/PHP):**
```
locale/
  en/LC_MESSAGES/django.po
  es/LC_MESSAGES/django.po
  ar/LC_MESSAGES/django.po
```

**Decision: JSON vs PO vs YAML:**
- JSON: Best ecosystem tooling, native JS import, supported by all TMS platforms
- PO (gettext): Battle-tested for server-side, translator-friendly format, supports plural forms natively
- YAML: Only use for Rails -- everywhere else it adds parser complexity with no benefit
- XLIFF: Enterprise/iOS -- required by Apple, supported by most enterprise TMS

---

## ICU MessageFormat Quick Reference

ICU is the standard for complex translated strings. Works across react-intl, i18next (with plugin), vue-i18n, and most TMS platforms.

| Type | Syntax | Example |
|------|--------|---------|
| Interpolation | `{name}` | `Hello, {name}!` |
| Plural | `{count, plural, one {# item} other {# items}}` | CLDR categories: zero/one/two/few/many/other |
| Select | `{gender, select, female {her} male {his} other {their}}` | Gender, category routing |
| Selectordinal | `{pos, selectordinal, one {#st} two {#nd} few {#rd} other {#th}}` | Ordinal suffixes |
| Number | `{price, number, ::currency/USD}` | Locale-aware currency |
| Date | `{today, date, ::dMMMM}` | Locale-aware date |

**Nested (plural inside select) -- the canonical complexity test:**
```
{gender, select,
  female {{count, plural,
    one {{name} added # photo to her album}
    other {{name} added # photos to her album}
  }}
  other {{count, plural,
    one {{name} added # photo to their album}
    other {{name} added # photos to their album}
  }}
}
```
If your i18n library cannot handle nested select+plural, it cannot handle production localization.

---

## Named Anti-Patterns

### 1. The String Concatenator
`t('hello') + name + t('welcome')` -- breaks in every language with different word order (Japanese, Arabic, Turkish, German). Use single keys with interpolation: `t('greeting', { name })`. Concatenation guarantees broken translations in 80%+ of languages.

### 2. The Hardcoded Formatter
`new Date().toLocaleDateString()` without explicit locale uses browser default, not user preference. A US user in Germany sees German dates. Always pass `userLocale` explicitly to `Intl.DateTimeFormat`, `Intl.NumberFormat`.

### 3. The Monolith Bundle
Loading all 50 languages in the main bundle (10MB+ for large apps). Ship only the active locale via dynamic import: `await import(\`./locales/${locale}/common.json\`)`. Lazy-load additional namespaces on route change.

### 4. The Key Novelist
Using English text as keys: `t('Click here to submit your order')`. When copy changes, the key changes, every translation breaks, and TMS loses translation memory match. Use structured keys: `t('checkout.submit.cta')`.

### 5. The Locale Guesser
Assuming locale from IP geolocation alone. 20%+ of users browse from a country that does not match their language. Use preference chain: saved preference > URL segment > Accept-Language > default. Always provide a visible language switcher.

### 6. The Pixel Perfect
Fixed-width layouts (`width: 120px`) that shatter when German text is 30-40% longer or Chinese is 30% shorter. Use `min-width` + `padding-inline` instead of fixed width. Test with pseudo-localization.

### 7. The Unicode Ignorer
`'cafe\u0301' === 'caf\u00e9'` returns false -- same visual character, different bytes. Thai, Arabic, and Devanagari use combining characters extensively. Always `str.normalize('NFC')` before comparison or storage.

### 8. The Context Amnesiac
Sending `{ "save": "Save" }` to translators without context. Is "save" a verb (Guardar) or noun (Partida guardada)? Add description metadata. Context descriptions and screenshots cut revision cycles by 50%.

---

## Text Expansion Reference

Plan layouts for the LONGEST expected language, not English.

| Language | Expansion vs English | Direction | Notable Formatting |
|----------|---------------------|-----------|--------------------|
| German | +30-40% | LTR | Compound nouns create very long words |
| Finnish | +30-40% | LTR | Agglutinative -- single words replace phrases |
| French | +15-25% | LTR | Accent characters, narrow no-break space before punctuation |
| Spanish | +15-25% | LTR | Inverted punctuation marks |
| Portuguese | +15-25% | LTR | Gendered articles affect surrounding text |
| Russian | +15-25% | LTR | 6 grammatical cases affect word endings |
| Arabic | -20-25% | RTL | Contextual letter shaping, right-aligned |
| Hebrew | -20-25% | RTL | No uppercase/lowercase distinction |
| Chinese (Simplified) | -30-50% | LTR | No spaces between words, vertical text optional |
| Japanese | -20-40% | LTR/Vertical | Three scripts (kanji, hiragana, katakana), line break rules differ |
| Korean | -10-20% | LTR/Vertical | Syllable blocks, honorific levels affect entire sentence structure |
| Thai | +15-20% | LTR | No spaces between words, complex line-break rules |

---

## Number, Date, and Currency Formatting

Never format manually. Use the `Intl` API (browser/Node 13+).

| API | Usage | Example Output Variation |
|-----|-------|-------------------------|
| `Intl.NumberFormat(locale)` | `format(1234567.89)` | en: 1,234,567.89 / de: 1.234.567,89 |
| `Intl.NumberFormat(locale, {style:'currency', currency})` | `format(1234.56)` | en-US: $1,234.56 / de-DE: 1.234,56 $ / ja: ¥1,235 |
| `Intl.DateTimeFormat(locale, {dateStyle:'long'})` | `format(date)` | en-US: March 15, 2026 / ja: 2026/3/15 |
| `Intl.RelativeTimeFormat(locale, {numeric:'auto'})` | `format(-3, 'day')` | "3 days ago" / "vor 3 Tagen" |

Currency code is NOT locale -- a German user can view USD prices. Always separate locale (formatting) from currency (business logic).

**Calendar/number gotchas:**
- Japanese imperial calendar: Reiwa 8 = 2026. Thai Buddhist: 2569 = 2026 CE.
- Arabic-Indic numerals: some `ar` locales render Eastern Arabic digits by default
- Week start: US = Sunday, Europe = Monday, Middle East = Saturday
- India lakh grouping: 12,34,567 not 1,234,567

---

## Troubleshooting

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Missing translation shows raw key | Namespace not loaded or key typo | Enable missing-key warnings in dev; add fallback language chain |
| SSR/SSG hydration mismatch | Server locale differs from client locale | Pass locale from server to client via cookie or URL; use `suppressHydrationWarning` for dates |
| Same key returns different text on different pages | Namespace collision between routes | Use route-specific namespaces; audit for duplicate keys across files |
| RTL layout partially broken | Mixed physical and logical CSS properties | Run CSS audit for margin-left/right, padding-left/right, text-align: left/right |
| Plurals wrong in Polish/Arabic | Using simple `one/other` instead of CLDR categories | Implement full CLDR plural rules (zero/one/two/few/many/other) via ICU MessageFormat |
| Text truncated in buttons/labels | Fixed-width design not accounting for expansion | Use min-width + padding instead of fixed width; test with pseudo-localization |
| Date/number wrong for user locale | Defaulting to server locale or browser locale | Use explicit locale parameter from user preference, not implicit defaults |
| Translation memory not matching in TMS | Keys changed instead of just values | Keep keys stable; only change values. Use key deprecation, not key rename |
| Build fails after adding new locale | Locale not registered in framework config | Add locale to next.config.js / i18n config / angular.json -- every framework has a locale registry |
