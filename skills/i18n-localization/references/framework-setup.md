# Framework-Specific i18n Setup Patterns

Deep implementation patterns for each major framework. Not beginner tutorials -- these are the patterns that survive production at scale.

---

## react-i18next (React SPA)

**Setup with namespace lazy loading:**
```typescript
// i18n.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import HttpBackend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: 'en',
    ns: ['common'],           // Only load common namespace initially
    defaultNS: 'common',
    backend: {
      loadPath: '/locales/{{lng}}/{{ns}}.json',
    },
    detection: {
      order: ['localStorage', 'cookie', 'navigator'],  // User pref > browser default
      caches: ['localStorage'],
    },
    interpolation: { escapeValue: false },  // React already escapes
  });
```

**Per-route namespace loading (critical for performance):**
```typescript
// Route-level lazy loading -- only downloads translations the user needs
const DashboardPage = lazy(() => import('./pages/Dashboard'));

function Dashboard() {
  const { t } = useTranslation('dashboard');  // Triggers async load of dashboard.json
  return <Suspense fallback={<Skeleton />}><Content /></Suspense>;
}
```

**TypeScript typed keys (catches typos at compile time):**
```typescript
// i18n.d.ts
import 'i18next';
import common from '../locales/en/common.json';
import auth from '../locales/en/auth.json';

declare module 'i18next' {
  interface CustomTypeOptions {
    defaultNS: 'common';
    resources: { common: typeof common; auth: typeof auth };
  }
}
// Now t('auth.login.titl') is a compile error -- catches missing 'e'
```

**Trans component for inline markup:**
```tsx
// When translations contain HTML elements
<Trans i18nKey="terms.accept" components={{ bold: <strong />, link: <a href="/terms" /> }}>
  I accept the <bold>Terms</bold> and <link>Privacy Policy</link>
</Trans>
// Translation: "I accept the <bold>Terms</bold> and <link>Privacy Policy</link>"
// Translators see the tags but cannot inject arbitrary HTML
```

---

## next-intl (Next.js App Router)

**Middleware locale routing:**
```typescript
// middleware.ts
import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  locales: ['en', 'es', 'ar', 'ja'],
  defaultLocale: 'en',
  localePrefix: 'as-needed',  // /about (en default), /es/about, /ar/about
  localeDetection: true,       // Uses Accept-Language on first visit
});

export const config = { matcher: ['/', '/(en|es|ar|ja)/:path*'] };
```

**Server Component translations (no client JS shipped):**
```typescript
// app/[locale]/page.tsx
import { getTranslations } from 'next-intl/server';

export default async function HomePage() {
  const t = await getTranslations('home');
  return <h1>{t('title')}</h1>;  // Zero client-side i18n JavaScript
}

// Static generation for all locales
export function generateStaticParams() {
  return [{ locale: 'en' }, { locale: 'es' }, { locale: 'ar' }, { locale: 'ja' }];
}
```

**Client Component pattern (when interactivity is needed):**
```typescript
'use client';
import { useTranslations } from 'next-intl';

export function LanguageSwitcher() {
  const t = useTranslations('common');
  // useTranslations only works in Client Components
  // Server Components must use getTranslations (async)
}
```

**Layout with locale provider:**
```typescript
// app/[locale]/layout.tsx
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';

export default async function LocaleLayout({ children, params: { locale } }) {
  const messages = await getMessages();
  return (
    <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <NextIntlClientProvider messages={messages}>
        <body>{children}</body>
      </NextIntlClientProvider>
    </html>
  );
}
```

---

## vue-i18n (Vue 3)

**Composition API setup:**
```typescript
// i18n.ts
import { createI18n } from 'vue-i18n';

const i18n = createI18n({
  legacy: false,              // Use Composition API mode
  locale: 'en',
  fallbackLocale: 'en',
  messages: { en: {} },       // Start empty, lazy-load
  missingWarn: import.meta.env.DEV,  // Only warn in dev
});
```

**Per-route lazy loading with Vue Router:**
```typescript
// router.ts
const routes = [
  {
    path: '/dashboard',
    component: () => import('./pages/Dashboard.vue'),
    beforeEnter: async () => {
      const locale = i18n.global.locale.value;
      const messages = await import(`../locales/${locale}/dashboard.json`);
      i18n.global.mergeLocaleMessage(locale, { dashboard: messages.default });
    },
  },
];
```

**SFC i18n blocks (component-scoped translations):**
```vue
<template>
  <p>{{ t('greeting') }}</p>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
const { t } = useI18n();  // Uses component-local messages first, falls back to global
</script>

<i18n lang="json">
{ "en": { "greeting": "Hello" }, "es": { "greeting": "Hola" } }
</i18n>
```

---

## Django (Python gettext)

**Standard workflow:**
```bash
# Extract strings from Python/templates into .po files
python manage.py makemessages -l es -l ar -l ja --ignore=node_modules

# After translators edit .po files, compile to binary .mo
python manage.py compilemessages
```

**Template usage:**
```html
{% load i18n %}
<h1>{% trans "Welcome" %}</h1>
<p>{% blocktrans with name=user.name %}Hello, {{ name }}{% endblocktrans %}</p>
<p>{% blocktrans count counter=item_count %}{{ counter }} item{% plural %}{{ counter }} items{% endblocktrans %}</p>
```

**JavaScript translations (often forgotten):**
```python
# urls.py -- expose translation catalog to frontend JS
from django.views.i18n import JavaScriptCatalog
urlpatterns += [path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog')]
```
```html
<script src="{% url 'javascript-catalog' %}"></script>
<script>const translated = gettext('Save');</script>
```

**Critical gotcha:** `makemessages` only scans Python and template files. JavaScript strings in .js/.ts files need `djangojs` domain: `python manage.py makemessages -d djangojs -l es`

---

## Cross-Framework Patterns

**Language detection chain (universal priority order):**
1. Explicit user preference (saved in DB or cookie after manual switch)
2. URL segment (`/es/about`) or subdomain (`es.example.com`)
3. `Accept-Language` HTTP header (browser setting)
4. GeoIP lookup (least reliable -- only for anonymous first visit)
5. Default locale (fallback)

**SEO requirements (all frameworks):**
```html
<html lang="es">
<head>
  <link rel="alternate" hreflang="en" href="https://example.com/about" />
  <link rel="alternate" hreflang="es" href="https://example.com/es/about" />
  <link rel="alternate" hreflang="ar" href="https://example.com/ar/about" />
  <link rel="alternate" hreflang="x-default" href="https://example.com/about" />
  <link rel="canonical" href="https://example.com/es/about" />
</head>
```
Missing hreflang tags cause Google to index the wrong language version. `x-default` tells crawlers which URL to use when no locale matches.

**Language switcher implementation:**
- Preserve current page path when switching (do not redirect to home)
- Show language names in their native script: "Deutsch" not "German", "العربية" not "Arabic"
- Store selection in a persistent cookie (httpOnly, SameSite=Lax, 1-year expiry)
- Update the `lang` and `dir` attributes on the `<html>` element immediately
