# Edge Cases — When Standard Context7 Workflow Breaks Down

## Coverage Gaps and Fallback Strategies

Context7 indexes thousands of libraries but not all. Understanding coverage boundaries
prevents wasted lookups and ensures graceful degradation.

### Coverage Likelihood by Category

| Category | Coverage | Strategy |
|---|---|---|
| Top 200 npm/PyPI packages | Very high | Always use Context7 — docs are comprehensive |
| Popular frameworks (React, Next, Vue, Django, Rails) | Very high | Always use Context7 |
| Mid-tier packages (1K-50K weekly downloads) | Variable | Try Context7 first, prepare training-data fallback |
| Niche/new packages (<1K weekly downloads) | Low | Check Context7, expect empty results, rely on training data |
| Internal/proprietary packages | None | Skip Context7 entirely, ask user for docs |
| Language standard libraries (Python stdlib, JS builtins) | Unnecessary | Skip — Claude knows these cold |
| System tools (Docker, git, bash) | Partial | Try Context7 for specific version features only |

### The Graceful Degradation Ladder

When Context7 cannot provide what you need, fall through this ladder:

```
Level 1: Context7 (current, version-specific docs)
  |
  +-- Failed? Try alternate library name / reformulated query
      |
      +-- Still failed?
          |
Level 2: Training data (may be stale, but usually directionally correct)
  |
  +-- Caveat to user: "Based on training data as of [cutoff]. Verify
  |   against current docs for production use, especially if you're
  |   on a recent version."
  |
Level 3: Web search (search-specialist agent)
  |
  +-- For very new libraries or post-cutoff API changes
  |
Level 4: Ask the user
  |
  +-- "I don't have current docs for this library. Could you share
      the relevant documentation or a link?"
```

**Critical rule**: Never silently fall back. Always tell the user which level you're
operating at. "Based on Context7 docs for v15.2" vs "Based on training data — please
verify" are very different confidence levels.

---

## Version Conflict Resolution

### When User's Version Doesn't Match Available Docs

```
User requests v15.x, Context7 has v14.x docs
|
+-- Are v14 and v15 API-compatible for this specific feature?
    |
    +-- YES (minor feature, stable API surface)
    |   --> Use v14 docs. Note: "Docs are from v14; this API is stable
    |       across versions, but verify any v15-specific changes."
    |
    +-- NO (breaking changes between versions)
    |   --> Do NOT use v14 docs — they will generate broken code.
    |   --> Fall to training data + web search for v15 specifics.
    |   --> Caveat: "Context7 has v14 docs but v15 introduced breaking
    |       changes to this API. Using training data — verify."
    |
    +-- UNSURE
        --> Use v14 docs as reference. Explicitly caveat every code
            example: "This syntax is from v14 docs. v15 may differ."
```

### When Multiple Versions Exist in Resolution

Resolution may return:
- `/library/v5` (specific major version)
- `/library/latest` (rolling latest)
- `/org/library` (main repo, version unclear)

**Selection priority**:
1. Version-specific entry matching user's stated version
2. `/latest` entry if user didn't specify a version
3. Main repo entry as last resort

---

## Empty or Sparse Results

### Diagnostic Decision Tree

```
query-docs returned empty or near-empty results
|
+-- Was the library ID valid? (Did resolve-library-id return it?)
|   |
|   +-- NO --> Resolution failed. Try alternate name.
|   +-- YES --> Library is indexed but query missed. Continue.
|
+-- Was the query too specific?
|   |
|   +-- "useCallback memoization stale closure fix React 18.2.0"
|   |   --> Too narrow. Try: "useCallback memoization"
|   +-- "React" --> Too broad. Try the specific method/concept name.
|
+-- Was the query using the right terminology?
    |
    +-- Docs might call it "Server Actions" not "server mutations"
    +-- Docs might call it "Route Handlers" not "API routes" (Next 13+)
    +-- Try official terminology from the framework's naming conventions
```

### The Terminology Gap Problem

**Information retrieval insight (BM25/semantic search hybrid)**: Context7 uses semantic
matching, but documentation often uses specific brand terminology that differs from common
developer language. This is the same problem that plagues all retrieval systems — the
vocabulary mismatch between query terms and document terms.

| What Developers Say | What Docs Call It | Framework |
|---|---|---|
| "server mutations" | "Server Actions" | Next.js |
| "API routes" | "Route Handlers" | Next.js 13+ |
| "reactive state" | "Signals" | Solid, Angular, Preact |
| "state management" | "Stores" | Svelte, Pinia |
| "lazy loading" | "Dynamic imports" or "Code splitting" | Various |
| "middleware" | "Edge Functions" or "Middleware" | Varies by framework |
| "auth" | "Authentication" or specific method names | Most libraries |

**Strategy**: If your natural-language query returns poor results, try the official
terminology. Check the framework's docs naming conventions.

---

## Cross-Framework Confusion

When the user works with multiple frameworks that use the same concepts differently:

| Concept | React | Vue | Svelte | Angular |
|---|---|---|---|---|
| Reactive state | `useState` | `ref()` / `reactive()` | `$state` | `signal()` |
| Side effects | `useEffect` | `watch()` / `watchEffect()` | `$effect` | `effect()` |
| Computed values | `useMemo` | `computed()` | `$derived` | `computed()` |
| Component lifecycle | `useEffect` return | `onMounted` / `onUnmounted` | `onMount` / `onDestroy` | `ngOnInit` / `ngOnDestroy` |

**Strategy**: Always include the framework name in the resolution query, even if it seems
obvious. `resolve-library-id("vue")` then `query-docs("reactive state with ref")` is better
than `query-docs("reactive state")` which could match any framework's docs.

---

## Rate Limits and Service Availability

Context7 is an external service. It can be:
- **Temporarily slow** (>5s response): Proceed with training data, retry later if needed
- **Temporarily unavailable**: Fall to degradation ladder Level 2 immediately
- **Rate limited**: Space out queries; batch related questions into single targeted queries

**Never block the user**: If Context7 is slow or down, answer from training data with a
caveat rather than waiting indefinitely. The user's time matters more than perfect sourcing.

---

## The "Should I Even Bother?" Quick Test

Before any Context7 lookup, run this 3-second mental test:

1. **Is this an external library?** No --> skip
2. **Could the API have changed since my training data?** No --> skip
3. **Does the user care about a specific version?** No, and API is stable --> maybe skip
4. **Am I about to generate code that depends on exact method signatures?** Yes --> fetch

If you hit "fetch" on question 4, always fetch. Wrong method signatures are the #1 cause
of "it doesn't work" debugging sessions.
