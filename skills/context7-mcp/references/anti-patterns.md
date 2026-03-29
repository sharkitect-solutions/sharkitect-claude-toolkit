# Anti-Patterns — Context7 Failures That Waste Time and Tokens

Eight named patterns derived from common retrieval failures. Each one looks reasonable in the
moment but produces worse outcomes than the alternative.

---

## The Eight Failure Patterns

| # | Name | What Happens | Why It Fails | Fix |
|---|---|---|---|---|
| 1 | **The Confidence Trap** | Skip Context7 because "I know this library" | Training data may be 6-18 months stale. APIs change between minor versions. You generate code against v14 syntax when the user is on v15. | If the user mentions a version, or the library ships frequent breaking changes (Next.js, React, Tailwind, Prisma), always fetch. The 2-second lookup prevents a 20-minute debugging session. |
| 2 | **The Token Dump** | Query with just the library name: `query: "React"` | Returns high-level overview text instead of actionable API details. Consumes 800-1500 tokens of context for content that doesn't answer the question. | Query at the method or config-key level. `"useEffect cleanup async"` returns exactly what you need in ~300 tokens. |
| 3 | **The Wrong Fork** | Pick a community wrapper or fork from resolution results instead of the official package | Community forks lag behind official releases. API surfaces may differ. User gets code that works with the fork but not their actual dependency. | Always prefer the official package entry. Check the library ID path — official packages usually have the org name (e.g., `/vercel/next.js`, `/prisma/prisma`). |
| 4 | **The Resolution Skip** | Guess the library ID instead of calling `resolve-library-id` | Library IDs are not predictable. `/vercel/next.js` is not `/next/next.js`. Guessing wastes a `query-docs` call on a nonexistent ID and produces empty results. | Always resolve first. The resolution call is cheap (~100ms). Skipping it to "save time" costs more time when the guess is wrong. |
| 5 | **The Single Shot** | Accept poor results from the first query without reformulating | First query may use the wrong terms. The docs might index the concept under a different name than you used. Accepting sparse results means providing a worse answer. | If first results are sparse or irrelevant: reformulate. Try the method name, the config key, the error message text, or a different description of the same concept. Two queries > one bad answer. |
| 6 | **The Version Blindspot** | Ignore version-specific library IDs when the user mentions a version | Library behavior changes significantly between major versions. React 18 Suspense differs from React 19 Suspense. Fetching generic docs may return the wrong version's API. | When resolution returns version-specific entries AND the user mentioned a version, always pick the version-matched entry. This is not optional. |
| 7 | **The Redundant Fetch** | Fetch docs for something Claude knows with certainty | Standard library methods (`JSON.parse`, `os.path.join`), basic language syntax, and stable APIs that haven't changed in years don't benefit from fetching. It wastes tokens and adds latency for zero knowledge gain. | Apply the decision gate. If it's a builtin, standard library, or a stable API the user didn't ask about a specific version of — answer from training data. |
| 8 | **The Doc Parrot** | Copy-paste raw documentation snippets without adapting to the user's context | Users have a specific project, framework, and coding style. Raw doc examples use generic variable names and minimal setup. Pasting them makes the response look lazy and requires the user to translate. | Adapt examples: use the user's variable names, framework conventions, and project structure. Cite the docs as source but write the code for their context. |

---

## Pattern Interaction Effects

Some anti-patterns compound:

- **Confidence Trap + Version Blindspot**: "I know React" + ignoring that the user is on
  React 19 = generating React 18 patterns for a React 19 project. Double failure.

- **Token Dump + Single Shot**: Broad query returns overview text, and you accept it without
  narrowing. The user gets a vague answer backed by 1000 tokens of wasted context.

- **Resolution Skip + Wrong Fork**: Guessing the library ID AND not checking if it's the
  official package = potentially fetching docs for a completely different library.

---

## The Meta-Pattern: When to Suspect You're in an Anti-Pattern

Ask yourself these three questions after each Context7 interaction:

1. **Did I get specific, actionable API information?** If no — you may be in Token Dump or
   Single Shot. Reformulate the query.

2. **Am I confident this matches the user's actual dependency version?** If no — you may be
   in Version Blindspot or Wrong Fork. Check the resolution results more carefully.

3. **Would this answer be the same without the fetch?** If yes — you may be in Redundant
   Fetch or Confidence Trap (in reverse). Either the fetch was unnecessary, or you're not
   actually using the fetched content.
