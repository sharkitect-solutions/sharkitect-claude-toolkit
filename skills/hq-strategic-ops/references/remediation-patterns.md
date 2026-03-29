# Remediation Patterns & Strategic Frameworks

## Theory of Constraints (Goldratt)

Every system has exactly ONE constraint that limits throughput. Fixing non-constraints is waste.

**The 5 Focusing Steps:**
1. **IDENTIFY** the constraint -- the single bottleneck causing 80% of symptoms. In structural debt, this is rarely where people complain loudest. Map the value chain end-to-end; the constraint is where work queues up.
2. **EXPLOIT** the constraint -- maximize its output without spending money. Remove interruptions, eliminate non-value-add tasks, ensure it never sits idle. Example: if the constraint is a single person who approves all client onboarding, eliminate every non-essential approval from their plate.
3. **SUBORDINATE** everything else to the constraint -- all other processes pace themselves to the constraint. Do not optimize upstream processes that dump more work into the bottleneck. Overproduction upstream of a constraint creates hidden inventory debt.
4. **ELEVATE** the constraint -- invest to increase its capacity. Hire, automate, restructure. Only do this AFTER steps 2-3, because elevation is expensive and steps 2-3 are often sufficient.
5. **REPEAT** -- once the constraint moves (it always does), go back to step 1. The new constraint is usually the next weakest link.

**SMB application**: In a 5-15 person company, the constraint is almost always a specific person, not a system. The founder/owner is the constraint in 70%+ of cases. Structural remediation that doesn't address the human bottleneck fails.

## Wardley Mapping for Debt Classification

Classify every component by its evolution stage:

| Stage | Characteristics | Debt Signal |
|-------|----------------|-------------|
| **Genesis** | Novel, uncertain, requires experimentation | Using commodity tools for genuinely novel problems (under-investing) |
| **Custom** | Understood but built bespoke for your needs | Using custom solutions where products exist (over-investing) |
| **Product** | Standardized, multiple vendors available | Building custom when you should be buying (most common SMB debt) |
| **Commodity** | Utility, interchangeable, price-driven | Treating commodity as custom -- maintaining what you should outsource |

**The Wardley Debt Rule**: Structural debt accumulates when components are treated as a LOWER evolution stage than they actually are. The most common pattern in SMBs: treating Product-stage capabilities as Genesis (building from scratch what you could buy off the shelf). Second most common: treating Commodity as Custom (maintaining internal infrastructure that should be a SaaS subscription).

**Mapping exercise**: List every business component. Classify its ACTUAL evolution stage. Classify how you CURRENTLY treat it. The gap between actual and current = your structural debt surface area.

## 5 Named Remediation Patterns

### 1. Strangler Fig

Gradually replace the old system while it still runs. New functionality routes through the new system; old functionality stays until migrated.

- **Use when**: High-risk replacements where cutover failure would be catastrophic. Systems with many downstream dependencies.
- **Do NOT use when**: The old system is too broken to maintain during the transition period. If the old system's maintenance cost exceeds the parallel-run cost, use Big Bang instead.
- **Duration**: 3-12 months for SMB-scale systems.
- **Cost profile**: Higher total cost, much lower risk. You pay more but you sleep at night.

### 2. Parallel Run

Run old and new systems simultaneously. Compare outputs. Switch over only when parity is verified.

- **Use when**: Data-critical migrations where errors are unacceptable (financial systems, client records, compliance-tracked processes).
- **Do NOT use when**: Systems with side effects (sending emails, triggering workflows) -- you will get double-fires.
- **Duration**: 2-8 weeks of parallel operation is typical.
- **Cost profile**: 2x operational load during the validation window. Budget for the person-hours to compare outputs daily.

### 3. Big Bang Cutover

Replace everything at once on a scheduled date. Old system off, new system on.

- **Use when**: Tightly coupled systems where gradual migration is architecturally impossible. Small blast radius systems where failure is recoverable.
- **Do NOT use when**: You cannot afford rollback time. If reverting takes more than 4 hours, do not use Big Bang.
- **Risk**: Highest of all patterns. Mitigate with: dry runs, rollback plan tested in advance, cutover during lowest-activity window.
- **Duration**: 1 day cutover, but 2-4 weeks of preparation and 2 weeks of stabilization.

### 4. Incremental Decomposition

Break a monolithic process into modules. Replace one module at a time while others stay unchanged.

- **Use when**: Process debt -- a single large process has grown unwieldy. Each module has clear input/output boundaries.
- **Do NOT use when**: The process has no natural seams. If you cannot define input/output contracts between modules, decomposition will create integration debt.
- **Duration**: 1-2 weeks per module. Total depends on module count.
- **Cost profile**: Lowest risk per step, but requires upfront analysis to identify module boundaries correctly.

### 5. Debt Quarantine

Isolate the debt behind a clean interface. Prevent it from spreading. Schedule remediation for later.

- **Use when**: You cannot fix the debt now (no capacity, higher priorities), but you cannot let it grow. Buy time without making the problem worse.
- **Do NOT use when**: The debt is accelerating -- quarantine only works for stable debt. Accelerating debt breaks through quarantine.
- **Implementation**: Define a facade/API/wrapper that hides the debt. All new work goes through the clean interface. The debt stays behind it, untouched, until you have capacity.
- **Warning**: Quarantine is NOT a fix. It is a containment strategy. Set a review date. If quarantine exceeds 90 days without a remediation plan, escalate.

## Remediation Decision Tree

```
DEBT IDENTIFIED
  |
  +-- Score the debt (1-5 from debt-framework.md)
  |
  +-- Assess blast radius
  |     Low (1-2 systems) --> smaller patterns OK
  |     High (3+ systems or revenue-critical) --> conservative patterns required
  |
  +-- Check available capacity
  |     <20% of a person's time --> Quarantine only
  |     20-50% of a person's time --> Incremental Decomposition or Strangler Fig
  |     >50% dedicated capacity --> Any pattern viable
  |
  DECISION:
  |
  +-- Score 1-2 AND Low blast radius --> Debt Quarantine (contain, schedule later)
  +-- Score 3+ AND data-critical --> Parallel Run (verify before switching)
  +-- Score 3+ AND tightly coupled --> Big Bang Cutover (plan extensively, execute fast)
  +-- Score 3+ AND modular process --> Incremental Decomposition (safest iterative path)
  +-- Score 4-5 AND high blast radius AND capacity available --> Strangler Fig (lowest risk for high stakes)
  +-- ANY score AND no capacity --> Debt Quarantine (mandatory -- do not let debt spread while waiting)
```

## Stakeholder Communication Template

Use this 1-page format to present debt findings to non-technical decision-makers.

```markdown
# Structural Issue Brief: [Name of Debt Item]

**Date:** [YYYY-MM-DD]
**Prepared by:** [Name/Role]
**Decision needed by:** [Date -- give them a deadline]

## What's happening (2 sentences max)
[Plain-language description of the problem. No jargon. Focus on the business impact.]

## What it costs us today
- [Hours/week wasted]: [specific number]
- [Revenue at risk]: [specific dollar amount or "none currently"]
- [Growth blocked]: [what we cannot do because of this]

## What happens if we do nothing
- In 30 days: [concrete consequence]
- In 90 days: [concrete consequence]
- In 6 months: [concrete consequence]

## Recommended fix
- **Approach:** [Pattern name -- Strangler Fig, Parallel Run, etc.]
- **Effort:** [Person-hours or calendar weeks]
- **Cost:** [Dollar amount or opportunity cost]
- **Risk:** [What could go wrong and how we mitigate it]

## What I need from you
[ ] Approve the approach and timeline
[ ] Allocate [specific resource] for [specific duration]
[ ] [Any other specific ask]
```
