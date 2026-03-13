---
name: senior-architect
description: "Use when designing system architecture, evaluating technology trade-offs, creating architecture diagrams, defining service boundaries, planning database schemas, or reviewing architectural decisions. NEVER use for UI/UX design decisions, individual code-level refactoring, or DevOps pipeline configuration."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Senior Architect

## File Index

| File | Purpose | Load When |
|---|---|---|
| `references/architecture_patterns.md` | Pattern catalog with implementation details | Designing a new system or evaluating architectural patterns |
| `references/system_design_workflows.md` | Step-by-step design process and review procedures | Running an architecture review or structured system design session |
| `references/tech_decision_guide.md` | Technology selection criteria and comparison matrices | Evaluating tech stack choices or comparing specific technologies |
| `scripts/architecture_diagram_generator.py` | Generates architecture diagrams from spec | Creating or updating architecture diagrams |
| `scripts/project_architect.py` | Analyzes existing project structure and surfaces issues | Reviewing an existing codebase's architectural health |
| `scripts/dependency_analyzer.py` | Maps and validates dependency relationships | Checking dependency health, circular deps, or coupling metrics |

---

## Architecture Review Procedure

When this skill activates, follow this sequence before writing any recommendation:

1. **MANDATORY**: Read `references/architecture_patterns.md` for pattern context applicable to the domain
2. **Inventory constraints**: List the non-negotiable constraints (team size, existing tech, compliance requirements, budget, timeline). Constraints eliminate options faster than preferences do.
3. **Run decision matrices below**: Work through each applicable matrix. Record which signal led to which choice. If signals conflict (e.g., team is small but domain boundaries are well-defined), document the conflict and present both options with explicit trade-offs to the decision-maker.
4. **Check the Trade-off Resolution Table**: For every "vs" in the design, verify the resolution matches the table below before defaulting.
5. **Run `scripts/dependency_analyzer.py`** on any existing codebase to surface hidden coupling before proposing changes.
6. **Generate diagram**: Run `scripts/architecture_diagram_generator.py` to produce a visual baseline.

When signals in a decision matrix point in opposite directions, do NOT pick the "safer" default. Surface the conflict explicitly: "Signal A suggests X, but Signal B suggests Y. Here is the trade-off..." The decision-maker needs to see the tension, not a pre-resolved answer.

---

## Architecture Decision Framework

Before recommending any architecture, work through these decision matrices in order.

### System Topology: Monolith vs Microservices

| Signal | Monolith | Microservices |
|---|---|---|
| Team size | < 10 engineers | > 20 engineers with clear ownership |
| Deployment cadence | Weekly or less | Multiple teams deploy independently |
| Domain boundaries | Unclear or evolving | Well-defined, stable bounded contexts |
| Operational maturity | Low (no on-call, no observability) | High (distributed tracing, alerting, runbooks) |
| Current pain point | None or feature velocity | Deployment coupling between teams |

Default: start monolith. Extract services only when deployment coupling is proven painful, not anticipated.

### Database Selection

| Criterion | PostgreSQL | NoSQL (Mongo/DynamoDB) | Redis | ClickHouse/BigQuery |
|---|---|---|---|---|
| Data shape | Relational, normalized | Deeply nested documents, schema-per-entity | Ephemeral, key-value, session | Append-only analytics, time-series |
| Consistency need | Strong (ACID required) | Eventual acceptable | Eventual acceptable | Eventual acceptable |
| Query pattern | Ad hoc, joins, aggregations | Primary key or simple lookups | Single-key reads/writes | Aggregations over large scan ranges |
| Scale target | < 100M rows / table | > 100M items with single-key access pattern | < 1GB hot data | Analytics over billions of events |

Default: PostgreSQL. Move to NoSQL only when the data shape genuinely does not fit relational model -- not for "scalability."

### API Style Selection

| Use Case | REST | GraphQL | gRPC |
|---|---|---|---|
| Public-facing API consumed by unknown clients | Yes | Possible | No |
| Mobile clients with variable bandwidth | Possible | Yes (query what you need) | Possible |
| Internal service-to-service (same org) | Yes | Rarely | Yes (high throughput, strong contracts) |
| Real-time subscriptions | No | Yes (subscriptions) | Yes (streaming) |
| Team has GraphQL operational experience | Required | Yes | N/A |
| Schema evolution with backward compat | Easy (versioned paths) | Moderate (deprecation) | Hard (proto versioning) |

Default: REST for external APIs, gRPC for internal high-throughput services, GraphQL only when client-driven query flexibility is the actual requirement and the team has operational experience.

### Sync vs Async Communication

| Signal | Use Sync (HTTP/gRPC) | Use Async (Queue/Event) |
|---|---|---|
| Caller needs the response to continue | Always | Never |
| Operation is < 2s expected latency | Yes | No |
| Operation can fail and caller retries | Yes | Yes |
| Producer and consumer must scale independently | No | Yes |
| Order of processing matters strictly | Easier with sync | Requires sequencing discipline |
| Fire-and-forget acceptable | No | Yes |

Default: sync. Add async only when the operation is genuinely fire-and-forget or when independent scaling of producer/consumer is the proven bottleneck.

### Build vs Buy

| Factor | Buy / Use OSS | Build |
|---|---|---|
| Is this a commodity capability? | Yes | No |
| Does it differentiate the product? | No | Yes |
| Maintenance burden over 3 years | Low (active community) | High (owned forever) |
| Integration effort | < 2 weeks | N/A |
| Vendor lock-in risk acceptable? | Must evaluate | N/A |

Default: buy commodity, build differentiators. Authentication, payments, search indexing, email delivery -- buy. Core domain logic that generates competitive advantage -- build.

---

## Architecture Trade-off Resolution Table

| Conflict | Default Mistake | Correct Resolution |
|---|---|---|
| Consistency vs Availability | Apply strong consistency everywhere (safe default) | Determine consistency requirement per service per operation. Most reads tolerate stale data; only writes to shared financial or inventory state require strong consistency. |
| DRY vs Coupling | Extract shared library the moment code is duplicated | Duplication across service boundaries is cheaper than wrong abstractions. Extract only when the contract is stable and the abstraction is proven across 3+ independent use cases. |
| Microservices vs Monolith | Choose microservices for perceived future scalability | Start with a modular monolith. Introduce service extraction only when deployment coupling between teams is a demonstrated, recurring problem -- not an anticipated one. |
| SQL vs NoSQL | Default to NoSQL for "web scale" | PostgreSQL handles the vast majority of production workloads. NoSQL is appropriate only when the data access pattern is definitively key-value or document-shaped and the query pattern is known and stable. |
| Sync vs Async | Add message queues to every integration for "resilience" | Async adds operational complexity (dead letter queues, ordering guarantees, consumer lag). Use it only when fire-and-forget semantics are genuinely required or independent scaling is proven necessary. |
| Build vs Buy | Build for control and customization | Buy commodity capabilities (auth, payments, email, observability). The maintenance cost of owned infrastructure compounds over years. Build only what directly differentiates the product. |
| Abstraction vs Premature Generalization | Abstract interfaces to "allow swapping later" | Abstractions for hypothetical future swaps add indirection with no current benefit. Build the concrete implementation; refactor to an abstraction when a second consumer materializes. |
| Shared Library vs Duplication | Create a shared library for common utilities | Shared libraries create hidden coupling between services. A change to the library forces coordinated deploys. Prefer duplication at service boundaries; extract when the abstraction is stable and worth the coordination cost. |

---

## Rationalization Table

| What Someone Says | Why It's Wrong | What to Do Instead |
|---|---|---|
| "The team is small, we don't need architecture" | Small teams benefit most from clear boundaries -- they have the least capacity to manage unexpected coupling later | Define service and module boundaries explicitly even in a two-person project. The cost is low; the benefit compounds. |
| "We'll refactor later when we need to scale" | Architecture refactoring is 10x more expensive than initial design. Database schemas, API contracts, and auth models are expensive to reverse under live traffic. | Make deliberate decisions now. Document them. Revisit on a scheduled cadence, not in a crisis. |
| "Microservices will make us faster" | Microservices add operational complexity (distributed tracing, network failures, data consistency across services). They are faster only if deployment coupling is the actual bottleneck. | Measure whether deployment coupling is causing friction. If not, a monolith ships faster. |
| "We should use the latest framework or technology" | New technology has unknown failure modes in production. Mature technology has known failure modes and documented solutions. | Prefer technology where the failure modes are understood. Adopt new technology in a low-risk, non-critical path first. |
| "This decision doesn't matter, we can change it later" | Some decisions (database choice, API contracts, event schemas, auth provider) are structurally expensive to reverse under load. | Classify decisions by reversibility before making them. Irreversible decisions warrant more deliberation. |
| "Let's abstract this so we can swap the implementation" | Abstractions for hypothetical swaps add complexity for scenarios that rarely materialize and often guess wrong about the future interface. | Build the direct implementation. Extract an abstraction when a second concrete implementation actually exists. |
| "We need a shared library for this common code" | Shared libraries introduce deployment coupling. A version bump requires coordinated releases across every consumer. | Duplicate code at service boundaries. Extract a shared library only when the API is stable, the consumers are known, and the coordination overhead is worth it. |
| "The architecture diagram can wait until the system is built" | Undocumented architecture drifts from intention within weeks. New engineers build on assumptions rather than decisions. | Document the intended architecture before building. Use `scripts/architecture_diagram_generator.py` to generate a baseline from the spec. |

---

## Red Flags Checklist

Review before finalizing any architecture recommendation. Raise these explicitly if observed.

- [ ] Service boundaries drawn by technical layer (frontend/backend/database) rather than by domain or team ownership
- [ ] Shared database between two or more services that deploy independently
- [ ] Synchronous call chains longer than three hops (A calls B calls C calls D) -- a single timeout cascades to failure
- [ ] No defined consistency model for cross-service data (eventual vs strong vs read-your-writes)
- [ ] Authentication and authorization logic duplicated across services rather than delegated to a dedicated identity service
- [ ] A "utils" or "common" module that contains business logic rather than pure utilities
- [ ] A proposed microservices architecture where the team has no distributed systems operational experience (no tracing, no alerting, no runbooks)
- [ ] Schema-less storage (NoSQL) for data that requires relational queries or joins at query time
- [ ] API contracts defined by consumer implementation rather than by explicit schema (GraphQL schema, OpenAPI, proto)
- [ ] Architecture decisions made verbally with no written record -- decisions undocumented are decisions not made

---

## NEVER List

- NEVER recommend microservices to a team that has not yet deployed a monolith successfully -- operational complexity will overwhelm feature velocity
- NEVER recommend a shared database as the integration pattern between independently deployed services
- NEVER approve an architecture that has no defined strategy for handling partial failure (circuit breakers, retries with backoff, dead letter queues where appropriate)
- NEVER let data model decisions be deferred -- schema migrations under load are among the most dangerous production operations
- NEVER endorse adding a new technology to the stack without identifying who owns it in production and how failures will be diagnosed
- NEVER present a single architecture option when trade-offs exist -- always surface at least two options with explicit trade-off comparison so the decision-maker understands what they are choosing
