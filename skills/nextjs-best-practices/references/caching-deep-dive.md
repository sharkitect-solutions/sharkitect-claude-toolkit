# Caching Deep Dive

## Cache Key Mechanics

Next.js generates cache keys differently for each layer. Understanding key composition is essential for debugging stale data.

**Data Cache keys:** Composed of the fetch URL + serialized fetch options (method, headers, body). Two fetches to the same URL with different headers produce different cache entries. `POST` requests are never cached in the Data Cache. Custom headers added via `headers()` in a server component do NOT affect the cache key of fetches within that component -- this is a common source of confusion.

**Full Route Cache keys:** The route path + search params. `/products?page=1` and `/products?page=2` are separate cache entries. Dynamic route segments (`[id]`) create per-value entries at build time via `generateStaticParams`. Routes not listed in `generateStaticParams` are cached on first request (dynamic rendering with caching).

**Router Cache keys:** URL path + search params, stored in the browser's in-memory cache. This cache is NOT stored in localStorage or sessionStorage -- it is lost on tab close or page refresh. It cannot be directly invalidated from client code without calling `router.refresh()`.

---

## Four-Layer Interaction Map

Understanding which layers are active for different route types prevents the "it works on refresh but not on navigation" class of bugs.

### Static Route (no dynamic functions)

```
Request -> Router Cache (client)
  HIT -> return cached RSC payload (no server contact)
  MISS -> Full Route Cache (server)
    HIT -> return pre-rendered HTML + RSC payload
    MISS -> Render route
      fetch() -> Data Cache
        HIT -> use cached data
        MISS -> origin request -> store in Data Cache
      Store rendered output in Full Route Cache
      Return to client, store in Router Cache
```

### Dynamic Route (uses cookies(), headers(), searchParams)

```
Request -> Router Cache (client, 30s TTL)
  HIT -> return cached RSC payload
  MISS -> Skip Full Route Cache (dynamic routes are not fully cached)
    Render route on every request
      fetch() -> Data Cache (still active!)
        HIT -> use cached data
        MISS -> origin request -> store in Data Cache
      Return to client, store in Router Cache (30s)
```

Critical insight: Dynamic routes skip the Full Route Cache but still use the Data Cache. A route using `cookies()` re-renders on every request, but its `fetch()` calls still serve cached data unless explicitly opted out with `cache: 'no-store'`.

---

## Router Cache Behavior (Next.js 14.2+)

The Router Cache changed significantly in Next.js 14.2. Previous versions cached for 30 seconds regardless of route type. Current behavior:

| Segment Type | Cache Duration | Trigger for Refresh |
|-------------|---------------|---------------------|
| Static segment | 5 minutes | router.refresh(), full page reload, revalidation in server action |
| Dynamic segment | 30 seconds | Same as above, or TTL expiry |
| After server action mutation | 0 (invalidated) | Automatic after revalidatePath/revalidateTag in server action |

**The navigation staleness problem:** A user updates a record via a server action, which calls `revalidateTag('posts')`. The Data Cache and Full Route Cache are invalidated. But if the user navigates back to a list page using the browser back button, the Router Cache may still serve the stale version for up to 30 seconds. Solutions: (1) call `router.refresh()` after mutation, (2) use `revalidatePath` targeting the list route in the server action, (3) accept 30s staleness if appropriate for the use case.

---

## Revalidation Mechanics

### Time-Based (stale-while-revalidate)

When `revalidate: 60` is set and 65 seconds have passed since last cache write:

1. Next request receives the STALE cached response immediately (fast).
2. Next.js triggers a background revalidation -- re-renders the route or re-fetches the data.
3. If background revalidation succeeds, the cache is updated. Next request gets fresh data.
4. If background revalidation fails, the stale cache entry is retained. No error surfaced to users.

**Race condition:** Two requests arrive simultaneously after cache expiry. Both trigger background revalidations. Both receive stale data. The second revalidation overwrites the first, which is harmless if the data source is consistent but problematic if revalidation has side effects (API rate limits, metered endpoints).

### On-Demand Revalidation

**revalidateTag(tag):** Invalidates all Data Cache entries tagged with the specified string. Tags are set via `fetch(url, { next: { tags: ['posts'] } })`. This is surgical -- only tagged entries are invalidated. Use for: webhook-driven updates, after specific mutations, when you know exactly what data changed.

**revalidatePath(path):** Invalidates the Full Route Cache for the specified path AND all Data Cache entries fetched during that route's render. This is broad -- it re-renders the entire route. Use for: when you cannot predict which data fetches a route uses, or when multiple data sources changed simultaneously.

**Combining tags for granular control:** Tag fetches at multiple granularity levels. A product page might tag its fetches with both `product-123` and `products`. Updating a single product calls `revalidateTag('product-123')`. Updating the product catalog calls `revalidateTag('products')`.

---

## Cache Debugging Techniques

### Headers Inspection

Next.js sets cache-related headers that reveal cache behavior:

- `x-nextjs-cache: HIT` -- Full Route Cache served this response.
- `x-nextjs-cache: MISS` -- Route was rendered on-demand.
- `x-nextjs-cache: STALE` -- Stale response served, background revalidation triggered.

In development mode, add `logging: { fetches: { fullUrl: true } }` to `next.config.js` to see every fetch call, its cache status, and revalidation behavior in the server console.

### Common Stale Data Scenarios

**"Data updates on refresh but not navigation"** -- Router Cache is serving stale RSC payload. Fix: Add revalidatePath in the mutation's server action, or call router.refresh() after mutation.

**"Data never updates even on refresh"** -- Data Cache has indefinite TTL and no revalidation configured. Fix: Add `revalidate` interval or use `cache: 'no-store'` for that fetch.

**"ISR page shows old content after revalidation"** -- Full Route Cache was regenerated, but the Data Cache entries it uses are still stale. Fix: Revalidate both the route and its data tags, or ensure data fetches within the route have shorter `revalidate` intervals than the route itself.

**"Data is fresh in API route but stale in page"** -- Different cache contexts. API route handler fetches bypass the Full Route Cache. The page might be served from Full Route Cache with older embedded data. Fix: Use consistent revalidation tags across both the API route and the page's data fetches.

### Force-Bypassing Cache for Debugging

During development, set `const dynamic = 'force-dynamic'` at the route segment level to disable all caching for that route. Remove before production -- this disables the Full Route Cache and Data Cache, making every request hit origin.
