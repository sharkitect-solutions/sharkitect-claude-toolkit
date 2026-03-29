---
name: context7-mcp
description: >
  Use when answering questions about external libraries, frameworks, SDKs, or package APIs
  where training data may be outdated or insufficient. Use when a user asks "How do I...",
  "What's the API for...", "Show me an example of..." involving a specific package. Use when
  generating code that depends on library-specific syntax, configuration, or API signatures.
  Use when the user mentions a version number ("React 19", "Next.js 15", "Prisma 6"). Use
  when you are unsure if your training data reflects the current API surface. Do NOT use for:
  language builtins or standard library (Python stdlib, JS built-ins -- Claude knows these),
  conceptual questions not tied to a specific package API, internal or proprietary libraries
  not in public registries, debugging runtime errors (use systematic-debugging skill).
---

# Context7 MCP — Live Documentation Retrieval

## Why This Skill Exists

Training data has a cutoff. Libraries ship breaking changes between minor versions. A single
wrong parameter name, a renamed export, or a deprecated method turns "probably correct" code
into a debugging session. Context7 bridges the gap by fetching current, version-specific
documentation at query time — turning guesses into verified answers.

The cost of a Context7 lookup is ~2 seconds and ~500 tokens. The cost of generating code
against a stale API is 10-30 minutes of user debugging. The math is clear.

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "How do I use [library] to..." | YES | — |
| "What's the current API for..." | YES | — |
| "Show me [framework] v15 example" | YES | — |
| Code generation using external packages | YES | — |
| Python builtins / JS standard library | NO | Answer directly — Claude knows these |
| Conceptual "what is X" questions | NO | Answer directly |
| Internal / proprietary library | NO | Ask user for documentation |
| Debugging runtime errors | NO | systematic-debugging skill |
| Comparing libraries for selection | NO | search-specialist agent + this skill for finalists |
| MCP server configuration questions | NO | mcp-expert agent |

---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/query-mastery.md` | Formulating queries for ambiguous libraries, multi-library questions, optimizing token usage, resolution returning unexpected results | Simple single-library lookup with obvious ID match |
| `references/anti-patterns.md` | First Context7 usage of session, seeing poor or irrelevant results, need failure pattern checklist | Already completed 3+ successful lookups this session (patterns memorized) |
| `references/edge-cases.md` | Library not found, empty docs returned, version conflicts, need fallback strategy, user asking about niche or very new library | Standard lookup returning good results |

---

## Core Workflow

### Decision Gate: Should I Use Context7?

```
Is the question about a specific external library, framework, or SDK?
|
+-- NO --> Answer from training data. STOP.
|
+-- YES --> Is it a stable, well-known API that hasn't changed in 2+ years?
    |
    +-- YES, and user didn't mention a version --> Answer from training data. STOP.
    |
    +-- NO, or user mentioned a specific version, or you're unsure --> PROCEED.
```

**Always use Context7 for**: React, Next.js, Vue, Svelte, Angular, Tailwind, Prisma, Drizzle,
Supabase, tRPC, Astro, Remix, Nuxt, SvelteKit, Hono, Bun, Deno — these move fast.

**Skip Context7 for**: `JSON.parse`, `os.path.join`, `Array.prototype.map`, `console.log` —
Claude knows standard library methods perfectly.

### Step 1: Resolve the Library ID

Call `resolve-library-id` with:
- **`libraryName`**: The canonical npm/PyPI package name, not the brand name
- **`query`**: The user's full question (improves relevance ranking)

**Package name vs brand name — this matters:**

| User Says | Resolve As | Why |
|---|---|---|
| "Next.js" or "Next" | `nextjs` | Brand ≠ package name |
| "Tailwind" | `tailwindcss` | Brand ≠ package name |
| "Express" | `express` | Direct match |
| "Prisma" | `prisma` | Direct match |
| "@tanstack/query" | `@tanstack/query` | Include scope |
| "React Router" | `react-router` | Two-word → hyphenated |
| "Vue" | `vue` | Direct match |
| "Supabase JS" | `@supabase/supabase-js` | Scoped package |

### Step 2: Evaluate Resolution Results

```
Got results?
|
+-- EMPTY --> Try alternate name (brand name if you used package name, or vice versa)
|   +-- Still empty --> Fall back to training data. Add caveat: "based on training
|       data as of [cutoff] — verify against current docs for production use."
|
+-- SINGLE CLEAR MATCH --> Use it. Go to Step 3.
|
+-- MULTIPLE MATCHES -->
    |
    +-- User mentioned a version? --> Pick version-specific ID if available
    |
    +-- Official vs community fork? --> Always pick official (higher trust)
    |
    +-- Same library, different entries? --> Pick highest benchmark score
    |       (higher score = more comprehensive documentation coverage)
    |
    +-- Genuinely different libraries? --> Pick the one matching user's ecosystem
```

### Step 3: Fetch Documentation

Call `query-docs` with:
- **`libraryId`**: The resolved ID from Step 2
- **`query`**: Make it specific. Targeted queries return better results.

**Query specificity hierarchy** (most to least effective):
1. `"useEffect cleanup function async"` — specific method + behavior
2. `"useEffect hook"` — specific method
3. `"React hooks"` — category
4. `"React"` — entire library (too broad, wastes tokens)

```
Got useful documentation?
|
+-- YES --> Go to Step 4.
|
+-- SPARSE or IRRELEVANT --> Reformulate query with different terms.
|   +-- Try: method name, class name, config key, error message text
|   +-- Still poor? --> Fall back to training data with version caveat.
|
+-- EMPTY --> Library may not be indexed. Fall back to training data with caveat.
```

### Step 4: Synthesize Response

1. **Use fetched docs as primary source** — they're more current than training data
2. **Adapt code examples** to the user's project context (don't paste raw doc snippets)
3. **Cite the library version** when the docs specify one
4. **If docs contradict training data**: trust the docs. Mention the change if significant
   (e.g., "Note: as of v15, this API changed from X to Y")
5. **Never fabricate** — if the docs don't cover what the user asked, say so clearly

---

## Multi-Library Questions

When a question spans multiple libraries (e.g., "How do I use Prisma with Next.js App Router?"):

1. Identify which library's API is the primary unknown (usually the integration point)
2. Resolve and fetch for that library first
3. If the answer requires the second library's specifics, resolve and fetch it too
4. Synthesize across both doc sets — don't just concatenate

**Token budget**: Two fetches ≈ 1000 tokens. Still cheaper than wrong code.
