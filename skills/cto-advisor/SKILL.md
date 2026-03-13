---
name: cto-advisor
description: "Use when advising on CTO-level decisions: tech debt prioritization, rewrite vs refactor, build vs buy, engineering team scaling, architecture governance, vendor lock-in assessment, or production reliability strategy. NEVER for individual contributor coding tasks, code review, or project management mechanics."
---

# CTO Advisor

## CTO Decision Router

What type of decision?

1. TECH DEBT --> Tech Debt Priority Matrix
2. REWRITE vs REFACTOR --> The Rewrite Decision
3. BUILD vs BUY --> Build vs Buy Framework
4. TEAM SCALING --> Team Scaling & Topology
5. HIRING --> Hiring Decision Framework
6. ARCHITECTURE --> Architecture Governance
7. VENDOR/CLOUD --> Vendor Lock-In Assessment
8. RELIABILITY vs VELOCITY --> Reliability-Velocity Tradeoff
9. CTO ROLE --> CTO Identity by Stage

---

## Tech Debt Priority Matrix

Not all tech debt is bad. Deliberate debt (ship faster, fix later with a plan) is a legitimate strategy. Accidental debt (didn't know better) is the real problem. The key insight: tech debt has an INTEREST RATE -- some debt compounds weekly, some barely accrues at all.

### The 2x2: Impact x Compound Rate

|                    | LOW COMPOUND RATE              | HIGH COMPOUND RATE               |
|--------------------|--------------------------------|----------------------------------|
| HIGH IMPACT        | Schedule fix (next quarter)    | FIX NOW -- this is an emergency  |
| (many teams hit)   | e.g., legacy UI nobody loves   | e.g., shared DB coupling         |
| LOW IMPACT         | Ignore safely -- track it      | Fix opportunistically            |
| (one team/service) | e.g., old admin panel          | e.g., one team's test debt       |

### How to measure compound rate

Ask: "If we ignore this for 6 months, how much worse does it get?"

- HIGH compound: shared database schema, cross-service coupling, missing CI/CD (every new feature makes it worse)
- LOW compound: legacy UI, old documentation, unused microservice (stays roughly the same)

### The "interest rate" test for any debt item

1. How many teams does this block or slow down? (Impact)
2. Does each new feature make this debt worse? (Compound rate)
3. What is the cost of fixing it now vs in 6 months? (Growing cost = high compound)
4. Is there a natural trigger coming? (Migration, rewrite, team change = free opportunity)

### NEVER allocate debt reduction as a fixed percentage

"20% of sprint capacity for tech debt" sounds disciplined but fails in practice. Why: teams treat it as a dumping ground for pet refactors, not strategic debt. Instead, treat debt items like features -- prioritize by impact x compound rate, fund the top items explicitly, and track outcomes.

---

## The Rewrite Decision

### When rewrites fail (most of the time)

Big-bang rewrites fail because the old system keeps changing during the rewrite. By the time the new system is "done," the requirements have moved. The team ends up maintaining two systems indefinitely.

### The only safe rewrite pattern: Strangler Fig

Route new traffic to new code. Migrate old functionality piece by piece. The old system shrinks naturally. This works because you're never maintaining two complete systems.

### When a full rewrite is actually justified

ALL THREE must be true:
1. Codebase is under 10,000 lines AND fewer than 3 developers touch it
2. The old system is NOT actively changing (stable or frozen requirements)
3. You can complete the rewrite in under 6 weeks

If any condition is false, use Strangler Fig instead. "We can rewrite it better" is almost always wrong -- teams rewrite it DIFFERENTLY, not better, and introduce new bugs in previously-stable code.

### Before/After: Tech Debt Prioritization

BEFORE (common mistake):
"We have 47 tech debt items. Let's allocate 20% of each sprint to chip away at them. Engineers can pick what they want to work on."
--> Result: 6 months later, 47 debt items is now 52. Engineers fixed what was fun, not what mattered. New debt accumulated faster than old debt was paid down. No measurable impact on velocity.

AFTER (expert approach):
"We scored all debt by impact x compound rate. Three items are high-impact, high-compound: shared database coupling, missing integration tests on the payment path, and the hand-rolled auth system. We're funding a 2-person team for 6 weeks to strangle the shared DB. The other two go into next quarter's roadmap as first-class work items with success metrics."
--> Result: shared DB migration completes. Deployment frequency for 3 teams doubles. The two remaining items have clear timelines and owners.

---

## Build vs Buy Framework

### The one rule

Build ONLY if it is a core differentiator AND you have the team to maintain it for years. Buy everything else.

"We can build it better" is almost always wrong. You can build it differently. You cannot build it better than a company whose entire business is that one product, while also building your actual product.

### The maintenance trap

Building is 20% of the cost. Maintaining is 80%. When you build internally:
- You need on-call for it
- You need to patch security vulnerabilities in it
- You need to onboard every new hire on it
- You need to upgrade its dependencies quarterly
- You lose the engineer who built it (and eventually you will)

### Decision checklist

Build if ALL are true:
- [ ] This is what makes your product unique (not infrastructure, not auth, not logging)
- [ ] No commercial product covers >70% of your requirements
- [ ] You have 2+ engineers who will maintain it for 2+ years
- [ ] You've calculated TCO for 3 years including maintenance, on-call, and turnover risk

Buy if ANY are true:
- [ ] It's commodity functionality (auth, payments, monitoring, CI/CD, email)
- [ ] A vendor does it better than you can with your current team
- [ ] You need it working in under 3 months
- [ ] The problem domain is not your core expertise

---

## Team Scaling and Topology

### The fundamental scaling traps

1. Hiring too fast is worse than hiring too slow. Every new hire reduces team productivity for 3-6 months (onboarding cost). More than 25% growth per quarter breaks knowledge transfer.

2. Adding people to a late project makes it later (Brooks's Law). Communication paths grow as n*(n-1)/2. A team of 5 has 10 paths. A team of 10 has 45. A team of 20 has 190. The coordination cost eventually exceeds the productivity gain.

3. Team topology matters more than headcount. Two well-structured teams of 5 outperform one team of 12 every time.

### When to create a platform team

ONLY when you have 5+ product teams. Before that, platform work is a tax on product delivery -- the overhead of a separate team exceeds the benefit.

Signs you actually need a platform team:
- 3+ product teams are building the same internal tools independently
- Developer environment setup takes more than 1 day
- Teams are waiting on shared infrastructure changes for more than 1 sprint

### Architecture team: don't create one

Dedicated architecture teams become disconnected from production reality within 6 months. They produce designs nobody implements. Instead: embed senior architects in product teams. Have them rotate quarterly. Architecture decisions come from people who live with the consequences.

### Stream-aligned vs component teams

Component teams (frontend team, backend team, database team) are intuitive but create handoff bottlenecks. Every feature requires coordination across 3+ teams.

Stream-aligned teams (owns a business capability end-to-end) have higher autonomy and faster delivery. They take 6-12 months to become fully effective, but after the first year they consistently outperform component teams.

Switch to stream-aligned when: feature delivery requires more than 2 team handoffs on average.

---

## Hiring Decision Framework

### Senior-first for new domains

When entering a new technology area (first ML project, first mobile app, first distributed system): hire senior engineers first. They build the patterns, tooling, and standards. Juniors hired into a domain with no senior guidance will build something that needs to be rewritten.

### Junior-friendly for established codebases

When the patterns are set, the CI/CD works, the tests are comprehensive: juniors can extend and contribute effectively. They learn from the codebase and the surrounding seniors.

### Never hire purely for current technology stack

Technologies change every 2-3 years. Hire for learning ability, systems thinking, and communication. A senior Go developer who has never touched your stack will outperform a junior who already knows it within 3 months.

### The hiring velocity rule

One engineering hire per month is sustainable with a single recruiter and existing interview capacity. Two per month requires a dedicated recruiting function. Four+ per month requires a recruiting TEAM and will still probably result in lowered hiring bar.

---

## CTO Identity by Company Stage

### The identity crisis

Most CTO failures come from playing the wrong role for the company stage. Every transition feels like a demotion -- you're giving up what you're best at.

| Stage      | IC Work | Management | Where You Add Value                     |
|------------|---------|------------|-----------------------------------------|
| Seed       | 80%     | 20%        | Writing code, making architecture calls |
| Series A   | 50%     | 50%        | Building team, setting standards        |
| Series B   | 20%     | 80%        | Strategy, hiring, cross-functional work |
| Series C+  | 5%      | 95%        | Board, fundraising tech narrative       |

If these ratios don't shift as the company grows, YOU are the bottleneck. The most common failure: a seed-stage CTO who is still writing 80% code at Series B. The team can't grow because all decisions funnel through one person's PR reviews.

### Signs you're in the wrong mode

- You're the only person who can deploy to production --> you're still seed-mode
- Engineers wait for your code review before merging --> you're blocking, not leading
- You haven't talked to a customer in 3 months --> you've disconnected from the business
- You spend more than 50% of time in meetings but can't name 3 decisions you made this week --> you're in meetings, not managing

---

## Architecture Governance

### The reversibility test

Make irreversible decisions slowly and reversible ones fast.

Irreversible (take weeks, involve many people):
- Primary programming language
- Cloud provider
- Database engine for core data
- Microservices vs monolith

Reversible (decide in a day, change if wrong):
- API framework within a language
- CI/CD tool
- Monitoring vendor
- Internal tool choices

### Distributed systems: the default is wrong

"Let's use microservices" is the new "let's use Java." Most companies under 50 engineers should run a modular monolith. Microservices add: network latency, distributed debugging complexity, deployment orchestration overhead, data consistency challenges.

Start with a monolith. Extract services only when a specific module has different scaling needs OR a separate team needs to deploy independently. The trigger should be operational pain, not architectural aesthetics.

---

## Vendor Lock-In Assessment

### The real cost of switching vendors

The technical migration is usually 20% of the switching cost. The other 80%:
- Data migration and validation (often months, not weeks)
- Team retraining (every engineer needs to learn new APIs, new debugging tools, new failure modes)
- Updating every integration, webhook, and automation
- Re-establishing monitoring, alerting, and runbooks
- Lost institutional knowledge about vendor-specific workarounds

### Multi-cloud is usually wrong

Multi-cloud sounds like good risk management. In practice: you pay more (no volume discounts), your team needs to know two platforms, your abstractions leak, and you use the lowest common denominator of both clouds instead of the best features of one.

When multi-cloud IS justified:
- Regulatory requirement (data sovereignty, specific regions)
- Acquisition brought a second cloud and migration cost exceeds dual-cloud cost
- Specific service is genuinely best-in-class on a different cloud (rare)

For everyone else: pick one cloud, use it well, negotiate good pricing.

### Assessing lock-in before it happens

For any new vendor or service, ask: "What happens when we need to leave?"
- Can we export all our data in a standard format?
- Are we using proprietary APIs or standard protocols?
- How much custom code is vendor-specific?
- What is the estimated migration effort in engineer-months?

If the answer to the first two questions is "no," either negotiate data portability guarantees in the contract or factor 6-12 months of migration work into your long-term cost model.

---

## Production Reliability vs Feature Velocity

### The false tradeoff

"Stability vs speed" is a false dichotomy. The data (from Accelerate/DORA research) shows: the fastest teams deploy the most AND break the least. High reliability enables faster deployment because the team trusts the system.

### The trust equation

Low reliability --> fear of deploying --> larger, riskier batches --> more failures --> even lower reliability (death spiral)

High reliability --> confidence in deploying --> smaller, safer changes --> fewer failures --> even higher reliability (virtuous cycle)

### Rollback-first culture

Most outages are caused by deployments, not infrastructure failures. The single most impactful reliability practice: make rollback instant and automatic. If every deployment can be reverted in under 2 minutes, the cost of a bad deploy drops from "hours of debugging" to "2 minutes of downtime."

### The "5 whys" problem

Root cause analysis often stops at "why #2" because it gets political. "Why did the deploy fail?" -> "Because there were no integration tests" -> "Because the team doesn't have time to write tests" -> "Because leadership prioritizes features over quality" -> uncomfortable silence.

If your postmortems consistently stop at the proximate cause (bad code, missed test) instead of the systemic cause (incentive structure, staffing, process), they won't prevent recurrence.

---

## CTO Decision Anti-Patterns (Rationalization Table)

| Decision Mistake | Sounds Like | Why It Fails | Expert Move |
|------------------|-------------|--------------|-------------|
| "Let's rewrite it properly" | "The codebase is unmaintainable" | Old system keeps changing during rewrite; you end up maintaining two systems | Strangler fig: route new traffic to new code, migrate piece by piece |
| "We need microservices" | "We need to scale" | 90% of startups under 50 engineers don't need distributed systems overhead | Start monolith, extract services only when operational pain demands it |
| "Let's build it ourselves" | "We can build it better and cheaper" | You can build it DIFFERENTLY; maintenance is 80% of cost | Build only core differentiators; buy commodity |
| "We should go multi-cloud" | "We can't depend on one vendor" | Double the cost, half the expertise, lowest common denominator features | Single cloud done well beats multi-cloud done poorly |
| "Let's hire faster" | "We need more engineers to ship faster" | Communication overhead grows quadratically; onboarding consumes existing team capacity | Max 25% headcount growth per quarter; senior-first |
| "20% of sprints for tech debt" | "We'll chip away at it" | Becomes a dumping ground for pet refactors; no strategic prioritization | Fund specific debt items as first-class projects with success metrics |
| "Everyone should be full-stack" | "We need flexibility" | Generalists plateau at intermediate in each specialty; deep problems need deep expertise | T-shaped: deep in one area, functional in adjacent areas |
| "Let's create an architecture team" | "We need architectural consistency" | Disconnects from production reality within 6 months; designs nobody implements | Embed architects in product teams, rotate quarterly |

## NEVER List

1. NEVER rewrite a system that is still actively changing -- use Strangler Fig
2. NEVER hire more than 25% headcount growth per quarter -- onboarding breaks
3. NEVER create a platform team with fewer than 5 product teams to serve
4. NEVER allocate tech debt as a vague percentage -- fund specific projects
5. NEVER choose technology based on what looks good on a resume
6. NEVER let the CTO be the only person who can deploy to production
7. NEVER adopt microservices because "everyone does it" -- need operational pain first
8. NEVER sign a vendor contract without asking "what happens when we leave?"
9. NEVER skip postmortem systemic causes because they're politically uncomfortable
10. NEVER build auth, payments, or monitoring in-house unless it's literally your product
