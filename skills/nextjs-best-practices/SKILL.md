---
name: nextjs-best-practices
description: "Use when building Next.js applications with App Router, designing server/client component architecture, implementing data fetching strategies, configuring caching and revalidation, or optimizing Next.js performance. Do NOT use for Pages Router legacy patterns, general React questions unrelated to Next.js, or static site generators other than Next.js."
---

# Next.js Best Practices (App Router)

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/caching-deep-dive.md` | Configuring cache layers, debugging stale data, setting revalidation strategies, understanding cache key mechanics, troubleshooting router cache behavior | Component architecture decisions, bundle optimization, deployment configuration |
| `references/architecture-patterns.md` | Designing RSC component trees, choosing server actions vs API routes, implementing parallel routes, planning partial prerendering, structuring dynamic imports | Caching configuration, performance metrics, bundle size analysis |
| `references/performance-diagnostics.md` | Analyzing bundle size, optimizing Core Web Vitals, debugging hydration mismatches, comparing Turbopack vs Webpack, reducing serverless cold starts | Component architecture design, caching strategy, route design |

## Scope Boundary

| In Scope | Out of Scope |
|----------|-------------|
| App Router architecture and conventions | Pages Router (getServerSideProps, getStaticProps) |
| Server/Client Component design patterns | General React (hooks, state management libraries) |
| Next.js data fetching (fetch, cache, server actions) | Generic REST API design (use api-patterns skill) |
| Caching architecture (four layers) | CDN configuration unrelated to Next.js |
| Middleware and route handlers | Express.js or other Node frameworks |
| next/image, next/font optimization | General image editing or design tools |
| Vercel and self-hosted deployment | Cloud infrastructure setup (use senior-devops skill) |
| Turbopack migration and config | Raw Webpack plugin development |

---

## Server vs Client Component Architecture

Every component in the App Router is a Server Component by default. The `use client` directive is a boundary declaration, not a component annotation -- it tells the bundler "everything imported from this point down ships to the browser." This distinction drives every architectural decision.

### The Component Boundary Model

Server Components execute once on the server, produce serialized HTML and RSC payload, and never re-render on the client. They can directly access databases, file systems, and secrets. Their JavaScript never enters the client bundle -- a 50KB server component adds zero bytes to the client.

Client Components execute on both server (for initial HTML) and client (for hydration and interactivity). Every import inside a `use client` file becomes part of the client bundle, regardless of whether that import uses browser APIs.

**The boundary infection rule:** When you mark a file `use client`, every module it imports becomes a client module. A single `useState` in a parent component forces every child's code into the client bundle, even if those children are pure display components. This is the root cause of "The Client Creep" anti-pattern.

### Decision Framework

Place the `use client` boundary at the narrowest possible point -- leaf components, not branch components.

**Must be Client Component:** Uses useState, useEffect, useRef, useContext, event handlers (onClick, onChange), browser APIs (window, document, localStorage, IntersectionObserver), third-party libraries that access browser globals.

**Must be Server Component:** Accesses database directly, reads file system, uses server-only secrets (API keys, tokens), performs heavy computation that should not ship to client, renders large static content.

**The Composition Pattern:** When a page needs both data fetching and interactivity, do not make the page a client component. Instead, keep the page as a server component, fetch data there, and pass it as props to a thin client component that handles only the interactive parts.

```
// WRONG: entire page is client, data fetching moves to useEffect
'use client'
export default function Dashboard() { ... }

// RIGHT: server page with client islands
export default async function Dashboard() {
  const data = await getMetrics()    // server-only, zero client JS
  return (
    <div>
      <MetricsSummary data={data} />  {/* server component */}
      <InteractiveChart data={data} /> {/* 'use client' -- small island */}
    </div>
  )
}
```

### Module Dependency Awareness

Barrel files (index.ts re-exporting everything) are particularly dangerous at client boundaries. If a client component imports one utility from a barrel file, the bundler may pull the entire barrel into the client bundle. Use direct imports (`import { formatDate } from './utils/date'`) instead of barrel imports (`import { formatDate } from './utils'`) in any file marked `use client`.

---

## Data Fetching Patterns

### Server-Side Fetch with Automatic Deduplication

Next.js extends the native `fetch` API with automatic request deduplication. When multiple server components in the same render tree fetch the same URL with the same options, Next.js executes the request once and shares the result. This deduplication happens at the React rendering level using the request URL and options as the cache key.

**Critical detail:** Deduplication only works with `fetch()`. ORM calls, database queries, and SDK calls are NOT deduplicated automatically. For those, wrap them in `React.cache()` to get request-level memoization:

```
import { cache } from 'react'
export const getUser = cache(async (id: string) => {
  return db.user.findUnique({ where: { id } })
})
```

`React.cache()` memoizes for the duration of a single server request. It does not persist across requests. This is request-level memoization, not data caching.

### Parallel vs Sequential Loading

Sequential data fetching (waterfalls) is the most common performance problem in server components. Each `await` blocks the next:

```
// WATERFALL: 200ms + 150ms + 300ms = 650ms total
const user = await getUser(id)
const posts = await getPosts(user.id)
const comments = await getComments(posts[0].id)
```

When requests are independent, use `Promise.all` or `Promise.allSettled`:

```
// PARALLEL: max(200ms, 150ms) = 200ms total
const [user, posts] = await Promise.all([getUser(id), getPosts(id)])
```

When requests have real dependencies (need user ID to fetch posts), use Suspense boundaries to stream independent parts while dependent parts load. Each `<Suspense>` boundary creates an independent streaming chunk -- the server sends completed HTML as each boundary resolves, rather than waiting for the entire page.

### Server Actions vs Route Handlers

**Server actions** (`'use server'`) are for mutations triggered by user interaction: form submissions, button clicks, data updates. They are tightly coupled to the React component tree, support progressive enhancement (work without JavaScript), and automatically revalidate the router cache after execution.

**Route handlers** (`route.ts`) are for external API consumption: webhooks, third-party integrations, mobile app backends, CORS-enabled endpoints. They follow standard HTTP semantics and are not coupled to React.

Use server actions for your own UI. Use route handlers when something outside your React app needs to call your backend.

---

## Caching Architecture

Next.js has four distinct cache layers that interact in non-obvious ways. Misunderstanding their interaction causes stale data bugs that are difficult to diagnose.

### The Four Layers

**Request Memoization** (React layer) -- Deduplicates identical fetch calls within a single server render. Duration: one request. No configuration needed. Only applies to GET requests via `fetch()`.

**Data Cache** (Next.js layer) -- Persists fetch results across requests and deployments. Duration: indefinite (until revalidated). Controlled by `fetch` options: `cache: 'force-cache'` (default), `cache: 'no-store'`, or `next: { revalidate: N }`. This is the layer most developers think about when they say "caching."

**Full Route Cache** (Next.js layer) -- Caches the complete rendered HTML and RSC payload for static routes at build time. Duration: indefinite (until revalidated). Dynamic routes (using cookies(), headers(), searchParams, or `cache: 'no-store'` fetch) opt out automatically.

**Router Cache** (Client layer) -- Caches RSC payloads in the browser during navigation. Duration: 30 seconds for dynamic segments, 5 minutes for static segments (as of Next.js 14.2+). This is the layer that causes "I updated the data but the page still shows old content" during client-side navigation.

### Cache Invalidation Strategies

**Time-based:** `fetch(url, { next: { revalidate: 60 } })` makes the Data Cache entry stale after 60 seconds. The next request triggers a background revalidation (stale-while-revalidate pattern) -- the stale response is served immediately while a fresh response is generated.

**On-demand:** `revalidateTag('posts')` invalidates all cache entries tagged with 'posts'. `revalidatePath('/dashboard')` invalidates the specific route's Full Route Cache and Data Cache entries. On-demand revalidation is immediate -- it does not serve stale content.

**Cache stampede prevention:** When a popular page's cache expires, hundreds of simultaneous requests can hit the origin. Use `revalidateTag` from a webhook or server action rather than short `revalidate` intervals. For high-traffic pages, keep `revalidate` at 60+ seconds and use on-demand revalidation for known mutations.

See `references/caching-deep-dive.md` for cache key mechanics, layer interaction diagrams, and debugging techniques.

---

## Route Design

### Parallel Routes for Complex Layouts

Parallel routes (`@slot` convention) render multiple pages simultaneously in the same layout. The canonical use case is a dashboard with independently loading panels:

```
app/
  dashboard/
    @analytics/page.tsx    // loads independently
    @activity/page.tsx     // loads independently
    @notifications/page.tsx // loads independently
    layout.tsx             // composes all three slots
    page.tsx               // default content
```

Each slot gets its own loading.tsx and error.tsx, so one panel failing does not crash the others. Parallel routes also enable conditional rendering based on authentication state -- show `@auth/login` or `@auth/dashboard` based on session.

### Intercepting Routes for Modals

Intercepting routes (`(.)`, `(..)`, `(...)` conventions) let you show a route's content in a modal during client-side navigation while preserving the full page on direct URL access or refresh. Photo galleries, login modals, and detail views in lists use this pattern. On soft navigation (Link click), the intercepted route renders in the modal. On hard navigation (URL paste, refresh), the full page renders.

### Route Groups for Logical Boundaries

Route groups `(groupName)` organize routes without affecting the URL. Use them for: separate layouts per section (marketing vs app), authentication boundaries (public vs protected), and team ownership boundaries. Nest layouts inside route groups to avoid a single root layout growing unmanageable.

### Middleware Composition

Middleware runs at the edge before every request. Keep it thin -- it affects every route's TTFB.

**Good middleware uses:** Authentication redirects, geolocation-based routing, A/B test assignment (set cookie, not render logic), request header injection, bot detection, rate limiting headers.

**Bad middleware uses:** Database queries (no connection pooling at edge), heavy computation, business logic (use route handlers), response body transformation.

Use the `matcher` config to restrict middleware to specific paths. Without a matcher, middleware runs on every request including static assets, _next/static, and favicon.ico -- adding unnecessary latency to assets that should be served directly.

---

## Performance Optimization

### Bundle Size Management

Target: first-load JS per route under 70KB (compressed). Exceeding this degrades LCP on 3G connections to 4+ seconds. Measure with `@next/bundle-analyzer` and the `next build` output table.

**Dynamic imports** for heavy libraries: Any client-side library >20KB should be dynamically imported. Use `next/dynamic` with `ssr: false` for browser-only libraries (chart libraries, rich text editors, map renderers). Use named exports with dynamic imports to enable tree-shaking:

```
const Chart = dynamic(() => import('./Chart').then(mod => mod.Chart), {
  loading: () => <ChartSkeleton />,
  ssr: false
})
```

### Image Optimization

`next/image` automatically serves images in WebP/AVIF format, lazy loads below-the-fold images, and generates responsive srcsets. Configure the `sizes` prop to match your actual layout breakpoints -- without it, Next.js assumes the image takes the full viewport width and generates unnecessarily large variants.

**Sharp vs Squoosh:** In production, use Sharp (`npm install sharp`). Squoosh is the default for development but is 5-10x slower for image processing. Self-hosted deployments without Sharp will hit image optimization timeouts under load.

Mark above-the-fold images with `priority` to preload them, preventing LCP delays. Only 1-2 images per page should be priority -- over-prioritizing defeats the purpose.

### Font Optimization

`next/font` hosts fonts locally, eliminating external network requests to Google Fonts or similar CDNs. This alone removes 200-500ms of render-blocking time on first visit. Use `subsets: ['latin']` (or appropriate subset) to avoid downloading unused character ranges. Variable fonts reduce total font file size by 40-60% compared to loading multiple weights.

---

## Production Patterns

### Runtime Selection

**Edge Runtime** -- Cold start <50ms, limited APIs (no fs, no native Node modules, limited to Web APIs). Use for: middleware, simple API routes, authentication checks, A/B routing, geolocation. Available globally on Vercel/Cloudflare, reducing latency by 50-200ms for global audiences.

**Node.js Runtime** -- Cold start 200-500ms (varies by bundle size and region), full Node.js API access. Use for: database connections, file system access, native modules (Sharp, bcrypt), CPU-intensive work, any library that uses Node-specific APIs.

**Default to Node.js runtime.** Switch to Edge only when you have confirmed: (1) the route uses no Node-only APIs, (2) the latency improvement matters for that route, (3) the code runs correctly in the restricted Edge environment.

### Environment Variable Discipline

`NEXT_PUBLIC_` prefix exposes variables to the client bundle -- they are literally string-replaced at build time. Never prefix secrets, API keys, database URLs, or internal service URLs with `NEXT_PUBLIC_`. Server-only variables should fail loudly at startup if missing:

```
const API_KEY = process.env.STRIPE_SECRET_KEY
if (!API_KEY) throw new Error('STRIPE_SECRET_KEY is not set')
```

### Error Boundary Architecture

`error.tsx` creates automatic error boundaries per route segment. The error boundary catches runtime errors in its subtree and renders a fallback UI without crashing the entire application. Place `error.tsx` at each major route segment -- a failing product detail page should not crash the entire shop layout.

`global-error.tsx` at the app root catches errors in the root layout itself. It must include its own `<html>` and `<body>` tags because it replaces the entire document.

### Deployment: Vercel vs Self-Hosted

**Vercel:** Automatic ISR, edge middleware, image optimization, streaming, analytics integration. Zero-config for most Next.js features. Cost scales with traffic.

**Self-hosted (Docker/Node):** Requires manual configuration for ISR persistence (shared filesystem or Redis), image optimization (install Sharp, configure loader), and standalone output mode (`output: 'standalone'` in next.config.js reduces Docker image from ~1GB to ~100MB). No edge runtime unless using a separate edge platform.

---

## Named Anti-Patterns

### The Client Creep
A single `useState` or event handler placed too high in the component tree forces the `use client` boundary to encompass dozens of child components that need no client JavaScript. **Detect:** Client bundle exceeds 100KB for routes that are primarily content display. `use client` appears in layout files or page-level components rather than leaf components. **Fix:** Push `use client` to the smallest possible leaf. Extract interactive parts into thin client components. Keep pages and layouts as server components that compose client islands.

### The Waterfall Chain
Sequential `await` calls in server components where requests have no actual dependency on each other. **Detect:** Server component render time equals the sum (not the max) of its data fetching times. Loading spinners appear sequentially rather than simultaneously. **Fix:** Use `Promise.all` for independent requests. Wrap dependent sections in `<Suspense>` boundaries to stream completed sections while others load. Use `loading.tsx` per route segment for automatic streaming.

### The Cache Stampede
Short revalidation intervals on high-traffic pages, causing hundreds of origin requests when the cache expires simultaneously. **Detect:** Origin server CPU spikes at regular intervals matching `revalidate` values. Database query volume shows periodic bursts. **Fix:** Use longer revalidation intervals (60s+) combined with on-demand revalidation via webhooks for known mutations. Tag-based invalidation (`revalidateTag`) lets you invalidate only what changed.

### The Layout Trap
Putting dynamic data (user session, notifications, timestamps) in root layout.tsx. Layouts are cached separately and do not re-render when navigating between child pages -- the dynamic data becomes stale. **Detect:** User name or avatar does not update after login/logout without a full page refresh. Notification badges show stale counts during client navigation. **Fix:** Move dynamic data into client components within the layout that fetch their own data, or use parallel routes for dynamic layout sections.

### The Barrel Export Bomb
Using barrel files (`index.ts` with `export * from './...'`) in directories imported by client components. The bundler pulls every exported module into the client bundle, even if only one function is used. **Detect:** Client bundle contains server-only utilities, unused components, or libraries that should not be client-side. Bundle analyzer shows unexpected modules in client chunks. **Fix:** Use direct file imports in client components. Reserve barrel files for server-only code. Configure `optimizePackageImports` in next.config.js for known large packages.

### The Middleware Monster
Implementing business logic, database queries, or complex computation in middleware instead of route handlers. Middleware runs on every matched request at the edge, where cold starts are fast but capabilities are limited and per-invocation costs add up. **Detect:** Middleware file exceeds 50 lines. Middleware imports database clients or ORM libraries. Middleware execution time exceeds 10ms. **Fix:** Keep middleware to redirects, header manipulation, and lightweight auth checks. Move business logic to route handlers or server components.

---

## Rationalization Table

| Shortcut | Why It Seems OK | Why It Fails | Do This Instead |
|----------|----------------|--------------|-----------------|
| "Just add `use client` to the page" | Fixes the immediate useState error | Every component in that page now ships to the client. A 200-component page goes from 0KB client JS to 50-150KB. LCP degrades measurably. | Extract the interactive part into a thin client component. Keep the page server-rendered. |
| "Set `revalidate: 1` for fresh data" | One-second staleness seems acceptable | Under load, 1-second revalidation creates constant origin pressure. 1,000 concurrent users = up to 1,000 revalidation requests per second. | Use on-demand revalidation for mutations. Set `revalidate: 60+` for polling freshness. |
| "Put everything in middleware" | Middleware runs before the page, feels like the right place for auth logic | Middleware runs at the edge with limited APIs, no database access, and adds latency to every route including static assets. | Use middleware only for redirects and header injection. Put auth logic in server components or route handlers. |
| "Skip the Suspense boundaries" | The page loads fine in development | Without Suspense boundaries, the entire page blocks on the slowest data source. A 3-second API call blocks all content, even the parts that could have rendered in 200ms. | Wrap independent data-loading sections in Suspense. Use loading.tsx per route segment. |
| "Fetch data in client components with useEffect" | Familiar React pattern, works everywhere | Adds a client-server waterfall: HTML loads -> JS loads -> hydration -> useEffect fires -> API call -> render. Minimum 2-3 round trips vs 0 for server components. Kills LCP and causes layout shift. | Fetch in server components. Pass data as props. Use server actions for mutations. |

---

## Red Flags Checklist

Stop and reassess the architecture when any of these conditions appear:

- [ ] **First-load JS exceeds 100KB for any route** -- The route has too much client code. Audit `use client` boundaries and dynamic import heavy libraries.
- [ ] **Client bundle contains server-only code** -- Barrel imports or incorrect boundaries are leaking server modules. Check imports in all `use client` files.
- [ ] **Layout components use `use client`** -- Layouts should be server components. Extract interactive elements into child client components.
- [ ] **Multiple sequential `await` calls in a single server component with no data dependency** -- Waterfall detected. Parallelize with Promise.all or add Suspense boundaries.
- [ ] **`revalidate` value below 10 seconds on a high-traffic route** -- Cache stampede risk. Switch to on-demand revalidation.
- [ ] **Middleware file imports database or ORM libraries** -- Middleware runs at the edge without persistent connections. Move to route handlers.
- [ ] **Same data fetched in both server and client components** -- Architecture confusion. Fetch once in the server component, pass as props.
- [ ] **`no-store` on every fetch call** -- Effectively disabling the cache system. Audit which routes genuinely need dynamic data vs which can use time-based revalidation.
- [ ] **Error boundary (error.tsx) missing from routes with external data dependencies** -- Unhandled fetch failures will crash the route. Add error.tsx at each segment that fetches data.
