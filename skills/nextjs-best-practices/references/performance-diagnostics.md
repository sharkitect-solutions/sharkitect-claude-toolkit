# Performance Diagnostics

## Bundle Analysis

### Setup and Thresholds

Install `@next/bundle-analyzer` and add to `next.config.js` with `ANALYZE=true` environment variable trigger. Run `ANALYZE=true next build` to generate the interactive treemap.

**Size thresholds per route (gzipped):**

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| First Load JS (shared) | <70KB | 70-100KB | >100KB |
| Page-specific JS | <30KB | 30-50KB | >50KB |
| Total first load per route | <100KB | 100-150KB | >150KB |
| Largest single chunk | <50KB | 50-80KB | >80KB |

These thresholds are calibrated for 3G performance. At 100KB first load JS, the parse+execute time on a mid-range mobile device is approximately 300-500ms. At 200KB, it exceeds 1 second, directly impacting INP and LCP.

### Common Bundle Bloat Sources

**date-fns/moment.js:** Full import of date-fns or moment adds 30-70KB. Import individual functions: `import { format } from 'date-fns/format'` instead of `import { format } from 'date-fns'`.

**lodash:** Full lodash import adds 70KB+. Use `lodash-es` with tree-shaking, or import per-function: `import debounce from 'lodash/debounce'`.

**Icon libraries:** Importing from `react-icons` barrel file pulls in every icon set. Import specific icons: `import { FiMenu } from 'react-icons/fi'`.

**CSS-in-JS runtime:** Libraries like styled-components or emotion add 10-15KB of runtime. Consider Tailwind CSS (zero runtime) or CSS Modules for server components.

**Polyfills:** Next.js includes polyfills for older browsers. If targeting modern browsers only, configure `browserslist` in package.json to exclude them.

### The `optimizePackageImports` Config

Next.js 13.5+ supports `experimental.optimizePackageImports` in next.config.js. List packages that use barrel exports, and Next.js will automatically transform barrel imports to direct file imports at build time:

```
experimental: {
  optimizePackageImports: ['@heroicons/react', 'date-fns', 'lodash-es', 'react-icons']
}
```

This eliminates "The Barrel Export Bomb" without requiring developers to change import styles.

---

## Core Web Vitals Optimization

### LCP (Largest Contentful Paint) -- Target < 2.5s

LCP measures when the largest visible element renders. For most Next.js pages, this is either a hero image or a heading text block.

**Common LCP killers in Next.js:**
- Fetching data in client components (adds client-server waterfall: HTML -> JS -> hydrate -> fetch -> render)
- Missing `priority` on hero images (lazy-loads the LCP element)
- Web fonts blocking render (not using next/font)
- Large unoptimized images (not using next/image with proper sizes)
- Render-blocking JavaScript from third-party scripts

**Fix checklist:**
1. Server-fetch all data needed for above-the-fold content
2. Add `priority` to the LCP image (only 1-2 per page)
3. Use `next/font` with `display: 'swap'` for all fonts
4. Preload critical above-fold images via `<link rel="preload">`
5. Defer third-party scripts with `next/script` strategy="lazyOnload"

### INP (Interaction to Next Paint) -- Target < 200ms

INP measures the latency between user interaction and the next visual update. In Next.js, poor INP usually stems from heavy client-side hydration or expensive re-renders.

**Common INP issues:**
- Over-hydration: large component trees marked `use client` that hydrate expensive event listeners on mount
- Synchronous state updates triggering cascading re-renders
- Large list rendering without virtualization
- Third-party scripts (analytics, chat widgets) blocking the main thread during interaction

**Diagnostic approach:**
1. Chrome DevTools Performance tab: record a user interaction, check "Main" thread for long tasks (>50ms)
2. Look for "Hydration" markers in the performance timeline -- if hydration takes >200ms, too much is client-rendered
3. React DevTools Profiler: identify components that re-render on every interaction

**Fix patterns:**
- Move data fetching to server components to reduce client component count
- Use `React.memo` for expensive pure components that receive stable props
- Virtualize lists with >50 items (react-window, @tanstack/virtual)
- Use `startTransition` for non-urgent state updates to keep the UI responsive

### CLS (Cumulative Layout Shift) -- Target < 0.1

CLS measures visual stability during page load. Next.js applications commonly trigger CLS from:

- Images without explicit width/height (next/image handles this automatically)
- Web fonts causing text reflow (next/font eliminates this)
- Dynamic content injected above existing content (ads, banners, cookie notices)
- Suspense boundaries that change size between fallback and resolved content

**Fix:** Set explicit dimensions on all media elements. Design Suspense fallbacks (loading.tsx) to match the approximate dimensions of the resolved content. Use `min-height` on containers that will receive dynamic content.

---

## Hydration Mismatch Debugging

Hydration mismatches occur when server-rendered HTML differs from what React expects during client hydration. Next.js 14+ provides detailed error messages identifying the mismatched elements.

### Most Common Causes

**Browser extensions:** Extensions inject DOM elements (Grammarly, ad blockers, password managers) that were not present in server-rendered HTML. Not fixable -- suppress with `suppressHydrationWarning` on affected elements.

**Date/time rendering:** `new Date().toLocaleString()` produces different output on server (UTC timezone) and client (user timezone). Fix: render dates in a client component, or use a consistent formatter.

**CSS-in-JS class name mismatch:** Server and client generate different class name hashes. Fix: ensure deterministic class generation (configured by default in modern CSS-in-JS libraries with Next.js).

**Conditional rendering based on `typeof window`:** `typeof window !== 'undefined'` is false on server, true on client, causing different render output. Fix: use `useEffect` for client-only rendering, or `next/dynamic` with `ssr: false`.

**HTML nesting violations:** `<p>` containing `<div>`, `<a>` containing `<a>`, or other invalid nesting. Browsers auto-correct invalid HTML, producing a different DOM than React expects. Fix: fix the HTML structure.

### Debugging Approach

1. Open browser console -- Next.js 14+ shows the exact element and attribute that mismatched
2. Compare the raw server HTML (view source) with the hydrated DOM (DevTools Elements panel)
3. Search for `typeof window`, `Date`, `Math.random`, or `navigator` in components rendered on the server
4. Check for conditional rendering that depends on client-only state

---

## Turbopack vs Webpack

Turbopack is the Rust-based successor to Webpack for Next.js. As of Next.js 14+, it is stable for development (`next dev --turbo`) and in preview for production builds.

### Performance Comparison

| Metric | Webpack | Turbopack | Improvement |
|--------|---------|-----------|-------------|
| Dev server cold start (large app) | 15-30s | 2-5s | 5-10x |
| Hot Module Replacement | 500ms-2s | 50-200ms | 5-10x |
| Route compilation (first visit) | 2-5s | 200-500ms | 5-10x |
| Memory usage (large app) | 1-4GB | 500MB-1.5GB | ~2x less |

**Migration considerations:** Turbopack does not support all Webpack plugins. Check the compatibility list before migrating. Custom Webpack configurations in next.config.js (`webpack` key) are ignored by Turbopack. The `turbo` key in next.config.js is used for Turbopack-specific configuration.

---

## Serverless Cold Start Optimization

On Vercel and similar platforms, each route deploys as an independent serverless function. Cold starts occur after 5-15 minutes of inactivity. Edge runtime cold starts are 5-50ms (negligible). Node.js cold starts range from 150ms (small functions) to 1-3s (functions with native modules like Sharp or bcrypt).

**Reduction strategies:** Use `output: 'standalone'` to trace per-route dependencies and exclude unused node_modules. Minimize per-route imports -- a route importing pdf-lib has a larger cold start than one with minimal dependencies. Use Edge runtime for latency-critical routes (auth checks, A/B assignment, geolocation). Use `generateStaticParams` aggressively -- static routes serve from CDN with zero cold start.
