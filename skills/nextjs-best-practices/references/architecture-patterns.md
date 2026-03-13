# Architecture Patterns

## React Server Components: Streaming Mechanics

RSC streaming works by splitting the server response into chunks at Suspense boundaries. The server sends the initial HTML shell immediately, then streams additional chunks as each Suspense boundary resolves. The browser progressively hydrates completed chunks without waiting for the entire page.

**The wire format:** RSC does not send HTML for server components. It sends a JSON-like serialized tree (the RSC payload) that describes the component hierarchy and data. Client components receive references to their JavaScript bundles. The client-side React runtime reconstructs the tree, rendering server component output as static HTML and hydrating client component references into interactive elements.

**Streaming sequence:**
1. Server begins rendering the component tree top-down.
2. When a Suspense boundary is encountered with an unresolved async child, the server sends the fallback content for that boundary.
3. The server continues rendering sibling branches that are not blocked.
4. As each async operation resolves, the server streams a replacement chunk for that Suspense boundary.
5. The client receives the chunk and swaps the fallback content with the resolved content. No full-page re-render.

**Performance implication:** TTFB is determined by the fastest branch, not the slowest. A page with a 50ms header fetch and a 3-second recommendations fetch shows the header in 50ms and streams recommendations when ready. Without Suspense, TTFB equals 3 seconds.

---

## Partial Prerendering (PPR)

PPR (experimental in Next.js 14+) combines static and dynamic rendering at the component level within a single route. The static shell is served from CDN at edge speeds, while dynamic holes stream in as they resolve.

**How it works:** At build time, Next.js renders the route and identifies Suspense boundaries wrapping dynamic content (components that use cookies(), headers(), or uncached fetches). The static portions become the prerendered shell. The dynamic portions are rendered on-demand at request time and streamed into the shell.

**Architectural requirements:**
- Every dynamic section must be wrapped in a Suspense boundary
- The static shell must be meaningful without dynamic content (not just a loading spinner)
- Dynamic sections should be leaves, not branches -- a dynamic parent makes all children dynamic

**Use case:** E-commerce product page. Static shell: product image, description, specifications (rarely change, serve from CDN). Dynamic holes: price (personalized), inventory count (real-time), user reviews (frequently updated). The shell loads in <100ms from CDN. Dynamic holes stream in 200-500ms later.

---

## Server Actions vs API Routes: Decision Framework

| Criterion | Server Action | Route Handler |
|-----------|--------------|---------------|
| Caller | Your own React components | External clients, webhooks, mobile apps |
| Progressive enhancement | Yes (works without JS) | No (requires fetch/XHR) |
| Router cache integration | Automatic revalidation | Manual revalidation |
| File upload | Supports FormData natively | Supports any request format |
| CORS | Not applicable (same-origin) | Configurable |
| Streaming response | No | Yes (ReadableStream) |
| Caching response | Not cacheable | Cacheable (GET handlers) |
| Rate limiting | Implement manually | Standard HTTP middleware |
| Authentication | Via cookies (automatic) | Via headers or cookies |

**When to use both:** An e-commerce checkout might use a server action for the "Place Order" button (progressive enhancement, automatic cache revalidation for the order summary) AND a route handler for the payment processor's webhook endpoint (external caller, needs CORS, standard HTTP response).

**Server action gotcha:** Server actions are POST requests under the hood. They always run on the server, even when called from a client component. But they are NOT API endpoints -- they do not have stable URLs and cannot be called from outside your application. Treat them as RPC calls bound to your React component tree.

---

## Dynamic Imports and Code Splitting

Next.js automatically code-splits at the route level -- each page.tsx is a separate chunk. But within a route, all synchronously imported client modules are bundled together.

### Named Export Pattern

```
// WRONG: imports entire charting library even if only using BarChart
const Charts = dynamic(() => import('chart-library'))

// RIGHT: import only the specific export
const BarChart = dynamic(() =>
  import('chart-library').then(mod => mod.BarChart)
)
```

This matters because many component libraries export dozens of components from a single entry point. Without named export selection, the dynamic import defeats the purpose -- the entire library loads when any component is used.

### Module-Level vs Route-Level Splitting

**Route-level** (automatic): Each page.tsx, layout.tsx, loading.tsx, and error.tsx produces a separate chunk. No configuration needed.

**Module-level** (manual): Use `next/dynamic` or native `React.lazy` for components that: (a) are large (>20KB), (b) are not visible on initial render (below fold, in modals, in tabs), or (c) depend on browser-only APIs.

**Shared chunks:** Components imported by multiple routes are extracted into shared chunks automatically. This means common UI components (headers, footers, navigation) are downloaded once and cached across route navigations.

---

## Parallel Route Composition for Dashboards

Parallel routes solve the dashboard layout problem: multiple independent panels that load at different speeds and have independent error states.

### Architecture Pattern

```
app/dashboard/
  layout.tsx          -- composes @analytics, @activity, @alerts
  page.tsx            -- default content for unmatched slots
  @analytics/
    page.tsx          -- analytics panel (slow: 2s API call)
    loading.tsx       -- skeleton while loading
    error.tsx         -- isolated error boundary
  @activity/
    page.tsx          -- activity feed (fast: 200ms)
    loading.tsx
    error.tsx
  @alerts/
    page.tsx          -- alerts panel (medium: 500ms)
    loading.tsx
    error.tsx
```

Each slot loads independently via streaming. The activity feed appears in 200ms, alerts in 500ms, analytics in 2s -- each with its own loading skeleton. If analytics fails, only that panel shows an error; the rest remain functional.

### Conditional Slots

Parallel routes enable authentication-based layouts:

```
// layout.tsx
export default function Layout({ auth, dashboard }) {
  const session = getSession()
  return session ? dashboard : auth
}
```

The `@auth` slot shows login/register pages. The `@dashboard` slot shows the authenticated experience. Both are defined as parallel routes, and the layout selects which to render based on session state. No client-side redirect flicker.

---

## Route Handler Patterns

### Streaming Responses

Route handlers can return streaming responses for real-time data:

```
export async function GET() {
  const stream = new ReadableStream({
    async start(controller) {
      for await (const event of eventSource) {
        controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(event)}\n\n`))
      }
      controller.close()
    }
  })
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' }
  })
}
```

### Static Route Handlers

GET route handlers with no dynamic functions (cookies, headers, searchParams) are treated as static and cached at build time. This is useful for generating static JSON endpoints consumed by external services. Force dynamic behavior with `export const dynamic = 'force-dynamic'` if the handler must re-execute on every request.
