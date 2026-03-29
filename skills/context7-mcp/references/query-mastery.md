# Query Mastery — Getting the Best Results from Context7

## The Retrieval Quality Equation

Context7 uses semantic search over indexed documentation. Like any retrieval system, output
quality is bounded by input quality. The same library lookup can return perfect API signatures
or useless overview text depending entirely on how you formulate the query.

**Information retrieval principle**: Precision and recall trade off. Broad queries maximize
recall (find something) but minimize precision (find the right thing). Narrow queries do the
opposite. The sweet spot is a query specific enough to target the right documentation section
but general enough to not miss it entirely.

---

## Query Specificity Hierarchy

From most to least effective:

| Level | Example Query | What You Get | Token Cost |
|---|---|---|---|
| **Method + behavior** | `"useEffect cleanup function async"` | Exact usage pattern | ~200-400 |
| **Method name** | `"useEffect"` | Method signature + basic usage | ~300-600 |
| **Category** | `"React hooks"` | Overview of multiple hooks | ~500-1000 |
| **Library name** | `"React"` | High-level overview (mostly useless) | ~800-1500 |

**Rule of thumb**: Query at the method/config-key level. Drop to category level only if you
don't know the specific API name. Never query at the library level.

---

## Resolution Disambiguation Strategies

### Monorepo Packages

Many frameworks publish multiple packages from a single repo. Resolution may return the
umbrella repo when you want a specific sub-package:

| Framework | Umbrella | Specific Package | When to Use Specific |
|---|---|---|---|
| Next.js | `/vercel/next.js` | Same | Always (it's the main package) |
| TanStack | `/tanstack/query` | `/tanstack/react-query` | When using React adapter specifically |
| AWS SDK | `/aws/aws-sdk` | `/aws/aws-sdk-js-v3` | When using v3 (current) |
| Google Cloud | `/googleapis/google-cloud-node` | Specific client library | When targeting one service |

**Strategy**: Start with the specific sub-package name. If resolution fails, try the umbrella.

### Name Collisions

Some names map to multiple unrelated libraries:

| Name | Possibilities | Disambiguation |
|---|---|---|
| `router` | React Router, Vue Router, Express Router | Check user's framework context |
| `query` | TanStack Query, jQuery, SQL query builders | Check ecosystem (React = TanStack) |
| `store` | Pinia, Zustand, MobX, Redux | Check framework + user's existing code |
| `auth` | NextAuth, Passport, Firebase Auth, Supabase Auth | Check what the project already uses |

**Strategy**: When the user says a generic name, check their project context (package.json,
imports, framework) before resolving. Include the framework in the resolution query:
`libraryName: "react-router"` not just `"router"`.

---

## Multi-Library Workflows

### Pattern: Integration Questions

"How do I use Prisma with Next.js App Router?" involves two libraries.

**Decision tree**:
```
Which library's API is the primary unknown?
|
+-- The integration point (e.g., Prisma client in Server Components)
|   --> Fetch Prisma docs first with query: "server components client instantiation"
|   --> Then fetch Next.js docs with query: "server components data fetching"
|
+-- Both equally unknown
    --> Fetch the less familiar library first (it's the bigger knowledge gap)
    --> Fetch the second library focused on the integration surface
```

### Pattern: Migration Questions

"How do I migrate from Express to Hono?" — fetch both, compare APIs.

1. Fetch source framework docs for the specific feature being migrated
2. Fetch target framework docs for the equivalent feature
3. Map source patterns to target patterns in your response

---

## Token Budget Optimization

Context7 fetches cost real context tokens. In a conversation with system prompts, skill
content, and history, every token matters.

**Budget-conscious patterns**:

| Scenario | Approach | Why |
|---|---|---|
| User asks about ONE method | Single targeted query | ~300 tokens, exact answer |
| User asks about a workflow (3+ methods) | One query for the workflow concept | Better than 3 separate method queries |
| User is exploring ("what can X do?") | Category-level query, summarize, then drill down on what interests them | Avoids fetching everything upfront |
| Follow-up question about same library | Reuse prior fetch if still in context | Zero additional tokens |

**Anti-budget pattern**: Fetching docs "just in case" for libraries you're confident about.
If you know Express middleware syntax cold and the user isn't asking about a new version,
skip the fetch.

---

## Benchmark Scores in Resolution Results

Resolution returns benchmark scores alongside library IDs. These indicate documentation
coverage quality:

| Score Range | Meaning | Implication |
|---|---|---|
| High (top quartile) | Comprehensive docs indexed | Queries will return detailed, specific results |
| Medium | Partial coverage | Core APIs covered, edge cases may be missing |
| Low | Sparse indexing | May only have overview/getting-started content |

**When scores are low**: Fetch anyway (something is better than nothing), but prepare a
fallback answer from training data. Mention the version caveat to the user.

**When multiple entries exist for the same library**: Higher benchmark score = more complete
documentation = better query results. Pick the higher score unless a version-specific entry
matches the user's needs more precisely.
