# MVP Shipping Playbook

Load when scoping an MVP, defining what to build first, or planning a 2-week ship cycle.

## Feature Scoping Decision

For every proposed feature, run this filter in order:

| Question | If YES | If NO |
|---|---|---|
| Can a user get value without this feature? | Cut it from MVP | Keep evaluating |
| Does this feature require building infrastructure (auth, billing, notifications)? | Infrastructure stays; feature on top is negotiable | Easier to include |
| Would you need this feature to charge money? | Include it | Cut it |
| Is this feature differentiating or table-stakes? | Table-stakes = include. Differentiating = include ONE, defer the rest | -- |
| Can you fake this with a manual process for the first 20 users? | Fake it. Concierge MVP. | Build it |

**The concierge test**: If you can manually deliver the feature's outcome to 20 customers via email/Slack/spreadsheet, do NOT build it yet. Build it when manual delivery takes more than 2 hours per day.

## 2-Week Ship Plan Template

| Day | Focus | Deliverable | Anti-Pattern to Avoid |
|---|---|---|---|
| 1-2 | Core data model + auth | Users can sign up, core entity CRUD works | Over-engineering the schema. 3 tables max for MVP. |
| 3-4 | Core value loop | The ONE thing the product does, end-to-end | Building settings, admin panels, or edge case handling |
| 5-6 | Payment integration | Stripe Checkout or Lemon Squeezy. Users can pay. | Building custom billing logic. Use hosted checkout pages. |
| 7-8 | Polish core flow | Error states, loading states, mobile responsive | Adding new features. Polish what exists. |
| 9-10 | Landing page + onboarding | First-run experience, marketing page | A/B testing, analytics setup, SEO optimization |
| 11-12 | Deploy + monitoring | Production deploy, basic error alerting | Kubernetes, Docker orchestration, CI/CD pipelines |
| 13-14 | Soft launch + feedback | Share with 10-20 prospects, collect feedback | Waiting for perfection. Ship with known rough edges. |

**Hard rule**: If you cannot ship in 2 weeks, you are building too much. Cut features until it fits.

## Build vs Buy Decision Matrix

| Component | Build | Buy/Use Service | Decision Signal |
|---|---|---|---|
| Authentication | Never for MVP | Clerk, Supabase Auth, Firebase Auth, NextAuth | Auth is solved. Building it wastes 2-5 days minimum. |
| Payments | Never for MVP | Stripe, Lemon Squeezy, Paddle | PCI compliance alone makes this non-negotiable. |
| Email sending | Never for MVP | Resend, Postmark, SendGrid | Deliverability requires reputation. Use a provider. |
| File storage | Never for MVP | S3, Cloudflare R2, Supabase Storage | Object storage is commodity infrastructure. |
| Search | Build simple (SQL LIKE/ILIKE) | Algolia, Typesense, Meilisearch | Build until >10K records or fuzzy search needed. |
| Analytics | Build simple (event log table) | PostHog, Mixpanel, Plausible | Build until you need funnels, cohorts, or retention curves. |
| Background jobs | Build simple (cron + DB queue) | Inngest, Trigger.dev, BullMQ | Build until you need retries, scheduling, or fan-out. |
| PDF generation | Build (html-to-pdf libraries) | -- | Libraries work fine. Services are overkill for MVP. |

**Override**: If you have built a component before and can reuse code, "build" may be faster than integrating a new service. Time-to-ship beats architectural purity.

## Deployment Decision for Solo Founders

| Hosting | When to Use | Monthly Cost | Scaling Ceiling |
|---|---|---|---|
| Vercel + Supabase | Next.js app, low-medium traffic | $0-25 | ~50K MAU before costs spike |
| Railway | Full-stack with custom backend, cron jobs | $5-20 | ~100K MAU |
| Fly.io | Need multi-region, WebSocket, or Docker | $5-30 | ~500K MAU |
| VPS (Hetzner, DigitalOcean) | Maximum control, predictable costs | $5-20 | Scales with VPS size |
| AWS/GCP/Azure | Never for MVP | $50+ before you know it | Infinite but complex |

**Cost trap**: Serverless platforms (Vercel, Netlify) have generous free tiers but punishing overage pricing. Set billing alerts at $20, $50, $100. A single viral HN post can generate a $500 Vercel bill overnight.

## Technical Debt Budget

| Acceptable in MVP | Must Fix Before 50 Paying Customers | Must Fix Before 200 Customers |
|---|---|---|
| No tests (but no regressions either) | Critical path tests (signup, payment, core feature) | 60%+ test coverage on business logic |
| Manual deploys | One-command deploy script | Basic CI/CD (push to main = deploy) |
| Single server, single region | Automated backups | Database replica or backup restore tested |
| Inline styles, messy CSS | Consistent component library | Design system basics |
| Console.log debugging | Error tracking (Sentry) | Structured logging + alerting |
| No rate limiting | Basic rate limiting on auth endpoints | Rate limiting on all public endpoints |
| SQLite or single Postgres | Still fine | Still fine until 100K+ rows with complex queries |

**Philosophy**: Technical debt is a loan against future time. At MVP stage, the interest rate is low because you might pivot and the code gets thrown away. At 200 customers, the interest rate is high because downtime costs you money and reputation.

## Common MVP Mistakes (with costs)

| Mistake | Time Wasted | What to Do Instead |
|---|---|---|
| Building admin dashboard before launch | 3-5 days | Use Supabase dashboard or direct DB queries |
| Custom design system | 5-10 days | Shadcn/ui, DaisyUI, or any component library |
| Multi-tenancy architecture from day one | 3-7 days | Single-tenant. Add tenancy when you have tenant #2. |
| OAuth with 4+ providers | 2-3 days | Email + password (or magic link). Add Google OAuth as the ONE social login if needed. |
| Internationalization before launch | 3-5 days | Ship in one language. Translate when international users request it AND are willing to pay. |
| Building a mobile app alongside web | 2-4 weeks | Web-first. Mobile when >30% of traffic is mobile AND users request native features. |
| Notification system (email + in-app + push) | 3-5 days | Email-only notifications. In-app when users miss emails. Push when you have a mobile app. |
| Building import/export before launch | 2-3 days | Manual CSV import via script. Export via database query. Build UI when >5 users request it. |
