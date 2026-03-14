# Brownfield Migration and Translation Operations

How to internationalize an existing codebase without breaking production, and how to run translation operations at scale.

---

## String Extraction Strategy

### AST-Based Extraction Tools

Manual find-and-replace misses strings. Use AST-aware tooling.

| Tool | Stack | What It Does |
|------|-------|--------------|
| `i18next-parser` | React/JS/TS | Scans JSX/TSX for `t()` calls, generates namespace JSON files |
| `babel-plugin-react-intl` | React (react-intl) | Extracts `<FormattedMessage>` and `defineMessages` at build time |
| `formatjs extract` | React/JS/TS | CLI extraction for FormatJS/react-intl ecosystem |
| `django-admin makemessages` | Django | Scans Python + templates for `_()` and `{% trans %}` |
| `xgettext` | C/C++/PHP | GNU gettext extraction from source code |
| `vue-i18n-extract` | Vue | Detects unused keys and missing translations |

### Finding Hardcoded Strings

For codebases without i18n, finding all hardcoded user-facing strings is the first step.

**Regex patterns to identify candidates (not exhaustive but catches 80%+):**
```
# JSX string literals in render output
/<[A-Z][a-zA-Z]*[^>]*>[^<{]*[a-zA-Z]{3,}[^<{]*</      # Text content in JSX elements
/placeholder=["'][A-Za-z]/                                # Placeholder attributes
/title=["'][A-Za-z]/                                      # Title attributes
/aria-label=["'][A-Za-z]/                                 # Accessibility labels
/alt=["'][A-Za-z]/                                        # Image alt text
/label:?\s*["'][A-Za-z]/                                  # Object property labels
```

**What NOT to extract:**
- Log messages (`console.log`, `logger.info`) -- these stay in English for debugging
- Error codes and technical identifiers
- API endpoint paths
- CSS class names and HTML IDs
- Environment variable names
- Regular expressions

### Prioritization Order

Do not attempt to extract everything at once. Prioritize by user impact.

| Priority | Category | Examples | When |
|----------|----------|----------|------|
| P0 | Core navigation | Header, footer, nav menus, breadcrumbs | Sprint 1 |
| P1 | High-traffic pages | Homepage, landing pages, product pages | Sprint 1-2 |
| P2 | Forms and validation | Input labels, error messages, success messages | Sprint 2 |
| P3 | Transactional emails | Order confirmation, password reset, welcome | Sprint 3 |
| P4 | Settings and account | Profile, preferences, billing | Sprint 3-4 |
| P5 | Admin/internal tools | Dashboards, reports, admin panels | Sprint 5+ |
| Never | Logs and debug | console.log, Sentry breadcrumbs, dev tools | Never |

---

## Migration Playbook

### Phase 1: Foundation (1-2 weeks)

1. Install i18n library (see framework-setup.md for specific library)
2. Configure locale detection chain (URL > cookie > Accept-Language > default)
3. Set up locale file structure with English-only JSON/PO files
4. Extract strings from top 5 highest-traffic pages
5. Replace hardcoded strings with `t()` calls
6. Deploy with English only -- validates the plumbing works

**Critical validation:** After Phase 1 deploy, the app must look and behave identically. If anything changed visually, a string was missed or a key is wrong.

### Phase 2: Second Language (1 week)

1. Add one non-English language (choose one with active users)
2. Use machine translation (DeepL or Google Translate) for initial pass
3. Have a native speaker review the machine output
4. Test the full user journey in the new language
5. Fix layout issues caused by text expansion

**Why only one language first:** One language exposes every architectural problem (missing keys, layout breaks, locale detection bugs). Fix these before scaling to more languages.

### Phase 3: Scale (ongoing)

1. Extract remaining pages by priority order
2. Add additional languages based on user analytics
3. Set up TMS integration for professional translation
4. Implement CI/CD quality checks (see below)
5. Establish translation review process

### Phase 4: Optimization (ongoing)

1. Implement namespace lazy loading (do not ship all translations upfront)
2. Add locale-specific formatting (dates, numbers, currency)
3. Set up translation memory in TMS to reduce costs
4. Add screenshot context for translators
5. Monitor missing translation rates per locale

---

## Translation Management Systems (TMS)

### Comparison Table

| Feature | Crowdin | Lokalise | Phrase | POEditor |
|---------|---------|----------|--------|----------|
| Pricing (starter) | Free (open source) | $120/mo | $63/mo (Strings) | $14.90/mo |
| GitHub/GitLab sync | Native | Native | Native | API only |
| CLI tool | crowdin-cli | lokalise2 | phrase pull/push | API scripts |
| In-context editing | Yes (proxy) | Yes (SDK) | Yes (In-Context Editor) | No |
| Machine translation | DeepL, Google, MS | DeepL, Google, MS | DeepL, Google | Google, MS |
| Screenshot context | Yes | Yes | Yes | No |
| Branching support | Yes | Yes | Yes | No |
| ICU MessageFormat | Yes | Yes | Yes | Partial |
| Plural rule support | Full CLDR | Full CLDR | Full CLDR | Basic |
| Translation memory | Yes | Yes | Yes | Yes |
| Glossary management | Yes | Yes | Yes | Basic |
| Best for | Open source, large teams | Speed, modern UI | Enterprise, multi-product | Budget, small teams |

**Recommendation by team size:**
- Solo/small team (1-5 devs): POEditor or Crowdin free tier
- Mid-size (5-20 devs): Crowdin or Lokalise
- Enterprise (20+ devs, multiple products): Phrase or Crowdin Enterprise

---

## CI/CD Integration

### Missing Translation Detection

```yaml
# GitHub Actions example
- name: Check translation coverage
  run: |
    npx i18next-parser --fail-on-update  # Fails if new keys found without translations
    node scripts/check-coverage.js        # Custom: reports % coverage per locale
```

**Coverage check script pattern:**
```javascript
// scripts/check-coverage.js
const en = flattenKeys(require('../locales/en/common.json'));
const es = flattenKeys(require('../locales/es/common.json'));
const missing = en.filter(key => !es.includes(key));
if (missing.length > 0) {
  console.error(`Missing ${missing.length} Spanish translations:`);
  missing.forEach(k => console.error(`  - ${k}`));
  process.exit(1);  // Fail the build
}
```

### Automated TMS Sync

```yaml
# Crowdin CLI in CI -- upload new keys, download approved translations
- name: Upload sources to Crowdin
  run: crowdin upload sources --no-progress

- name: Download translations
  run: crowdin download --no-progress

- name: Create PR with new translations
  uses: peter-evans/create-pull-request@v5
  with:
    title: "i18n: Update translations from Crowdin"
    branch: i18n/crowdin-sync
```

### Quality Checks in CI

| Check | Tool/Method | What It Catches |
|-------|------------|-----------------|
| Missing translations | Key diff between locales | Untranslated strings shipping to production |
| Unused keys | `vue-i18n-extract`, custom script | Dead translations increasing bundle size |
| ICU syntax errors | `messageformat` parser in CI | Broken plural/select syntax crashing at runtime |
| Key naming violations | Custom lint rule | Inconsistent naming breaking conventions |
| Pseudo-localization test | Automated screenshot comparison | Layout breaks from text expansion |

---

## Pseudo-Localization

Pseudo-localization transforms English text into a visually distinct variant that exposes i18n bugs without waiting for real translations. It is the single most effective i18n testing technique.

**What pseudo-localization catches:**
- Hardcoded strings that missed extraction (they stay in English while pseudo text changes)
- Layout truncation from text expansion (pseudo adds ~35% length)
- Character encoding issues (pseudo uses accented characters)
- Concatenation bugs (pseudo makes word-order issues obvious)

**Implementation:**
```javascript
// Pseudo-locale generator
function pseudoLocalize(str) {
  const map = {
    'a': '\u00e5', 'b': '\u0180', 'c': '\u00e7', 'd': '\u00f0',
    'e': '\u00e9', 'f': '\u0192', 'g': '\u011d', 'h': '\u0125',
    'i': '\u00ee', 'j': '\u0135', 'k': '\u0137', 'l': '\u013c',
    'm': '\u1e3f', 'n': '\u00f1', 'o': '\u00f6', 'p': '\u00fe',
    'r': '\u0155', 's': '\u0161', 't': '\u0163', 'u': '\u00fb',
    'v': '\u1e7d', 'w': '\u0175', 'x': '\u1e8b', 'y': '\u00fd', 'z': '\u017e',
  };
  const pseudo = str.replace(/[a-z]/gi, c => {
    const lower = c.toLowerCase();
    const mapped = map[lower] || c;
    return c === c.toUpperCase() ? mapped.toUpperCase() : mapped;
  });
  // Add ~35% padding to simulate text expansion
  const pad = '\u2003'.repeat(Math.ceil(str.length * 0.35));
  return `[!! ${pseudo}${pad} !!]`;
}
```

**Usage in react-i18next:**
```typescript
// Add pseudo-locale in development only
if (process.env.NODE_ENV === 'development') {
  i18n.addResourceBundle('pseudo', 'common', generatePseudoBundle(enCommon));
}
// Switch to pseudo locale via language switcher to visually audit
```

**What to look for in pseudo-localization testing:**
- Any text that is NOT wrapped in `[!! ... !!]` brackets is a hardcoded string
- Any truncated text (missing `!!]` suffix) indicates a fixed-width container
- Any broken layout indicates insufficient flexibility for text expansion
- Any mojibake (garbled characters) indicates an encoding problem
