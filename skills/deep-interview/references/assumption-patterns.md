# Hidden Assumption Patterns by Domain

Common assumptions that users make without realizing it. Use these patterns to
proactively surface blind spots during interviews.

## Software Architecture

| Hidden Assumption | Why It's Dangerous | Probing Question |
|---|---|---|
| "Single user" | No concurrency, no auth, no multi-tenancy considered | "Will multiple people or processes use this simultaneously?" |
| "Always online" | No offline mode, no retry, no queue | "What happens when the network is unavailable?" |
| "Data fits in memory" | No pagination, no streaming, no batching | "What's the expected data volume? Could it grow 100x?" |
| "Input is well-formed" | No validation, no error messages, no graceful degradation | "What does bad input look like? What should happen?" |
| "Happy path only" | No error handling, no recovery, no logging | "What are the three most likely failure modes?" |
| "Current tech stack" | User assumes you know their stack without saying it | "What language/framework/platform is this for?" |
| "Greenfield" | May actually be adding to existing system with constraints | "Is this new, or does it integrate with existing code?" |

## Automation & Workflows

| Hidden Assumption | Why It's Dangerous | Probing Question |
|---|---|---|
| "Runs once" | No idempotency, no scheduling, no state management | "Is this a one-time script or does it run repeatedly?" |
| "Instant execution" | No timeout handling, no progress tracking, no cancellation | "How long might this take? What if it takes 10x longer?" |
| "Credentials available" | No auth setup, no secrets management, no token refresh | "Where do credentials come from? Do they expire?" |
| "Reliable triggers" | No missed-event handling, no duplicate detection | "What if the trigger fires twice? Or not at all?" |
| "Sequential processing" | No parallel execution needs, no ordering guarantees | "Does order matter? Can items be processed in parallel?" |

## APIs & Integrations

| Hidden Assumption | Why It's Dangerous | Probing Question |
|---|---|---|
| "Stable API" | No versioning strategy, no deprecation handling | "Does this API change? How will we handle breaking changes?" |
| "Unlimited rate" | No throttling, no backoff, no queue | "Are there rate limits? What happens when we hit them?" |
| "Consistent data" | No schema validation, no type coercion, no null handling | "Is the response format guaranteed? What about optional fields?" |
| "Available always" | No circuit breaker, no fallback, no cache | "What if the external service is down for an hour?" |
| "Free tier sufficient" | No cost modeling, no usage forecasting | "What's the expected call volume? Have you checked pricing tiers?" |

## User-Facing Products

| Hidden Assumption | Why It's Dangerous | Probing Question |
|---|---|---|
| "Desktop only" | No responsive design, no mobile considerations | "What devices will people use this on?" |
| "Tech-savvy users" | No onboarding, no help text, no error recovery | "What's the least technical user look like?" |
| "English only" | No i18n, no RTL, no character encoding issues | "Will this need to support other languages or locales?" |
| "Modern browser" | No polyfills, no fallbacks, no progressive enhancement | "What browsers and versions need to work?" |
| "Light usage" | No performance optimization, no caching, no CDN | "What's the expected concurrent user count? Peak vs average?" |

## Data & Storage

| Hidden Assumption | Why It's Dangerous | Probing Question |
|---|---|---|
| "Data is clean" | No deduplication, no normalization, no validation on write | "Where does the data come from? Has it been validated?" |
| "Schema is stable" | No migration strategy, no backward compatibility | "Will the data shape change over time? How often?" |
| "Backup exists" | No disaster recovery, no point-in-time restore | "What happens if this data is lost? Is it reconstructable?" |
| "Small dataset" | No indexing strategy, no query optimization | "How much data now? In 6 months? In 2 years?" |
| "Single source of truth" | No sync conflicts, no eventual consistency issues | "Does this data live in multiple places? Who owns it?" |

## Internal Tools & Scripts

| Hidden Assumption | Why It's Dangerous | Probing Question |
|---|---|---|
| "Only I use it" | No documentation, no error messages, no discoverability | "Will anyone else ever run this? Or maintain it?" |
| "My machine only" | No cross-platform, no environment setup, no dependency docs | "Where else might this need to run?" |
| "Temporary solution" | Temporary solutions become permanent. No maintenance plan. | "What's the lifespan of this? A week, a month, forever?" |
| "Current state only" | No versioning, no changelog, no rollback | "Will this evolve? How will you track changes?" |
| "No observability needed" | No logging, no metrics, no alerting | "How will you know if this stops working?" |

## Using These Patterns

During Phase 3 (Assumption Exposure), scan the user's request against the relevant
domain tables above. For each matching hidden assumption:

1. **Name it explicitly.** "I notice we haven't discussed [X]. The common assumption
   here is [Y]."
2. **Explain the risk.** "If this assumption is wrong, [consequence]."
3. **Offer the choice.** "Should we define this now, or accept the assumption and
   move forward?"

The goal is NOT to exhaustively cover every assumption. Target the 3-5 most likely
to cause rework if wrong. Use the "Why It's Dangerous" column to prioritize by
consequence severity.
