# Architectural Debt Framework

## Cross-Domain Diagnostic Lenses

### Systems Thinking: Meadows' Leverage Points

Donella Meadows identified 12 leverage points where interventions change system behavior. Most teams intervene at the WRONG level -- they adjust parameters (hire more people, increase budget, add a tool) when the leverage point is structural.

**Leverage points ranked by effectiveness (ascending):**
- **Low leverage (where most teams intervene)**: Constants/parameters, buffer sizes, material flows. These are easy to change but have minimal systemic effect. Example: hiring another person to handle the workload caused by a broken process.
- **Medium leverage**: Information flows, rules of the system, self-organization. Example: changing who sees what data, or rewriting the approval rules that create bottlenecks.
- **High leverage (where structural debt lives)**: Goals of the system, mindset/paradigm, power to transcend paradigms. Example: changing WHAT the team optimizes for, not HOW they optimize.

**Application to debt diagnosis**: When you identify architectural debt, classify where the current "fix attempts" are intervening. If they are adjusting parameters (more people, more tools, more budget) while the debt is structural (wrong rules, wrong information flows, wrong goals), the fixes will fail regardless of investment. Redirect intervention to the correct leverage level.

### Cynefin Framework (Snowden): Problem Domain Classification

Before choosing a remediation approach, classify the debt problem into its Cynefin domain:

| Domain | Characteristics | Debt Example | Correct Response |
|--------|----------------|--------------|-----------------|
| **Clear** (formerly Simple) | Cause and fix are known. Best practice exists. | Missing SOP for a standard process | Sense-Categorize-Respond. Apply the known fix. |
| **Complicated** | Fix requires expertise but is discoverable through analysis | Integration architecture that needs redesign | Sense-Analyze-Respond. Bring in the expert. Multiple right answers exist. |
| **Complex** | Cause-effect only visible in retrospect. Emergent behavior. | Cultural debt -- team behaviors that resist structural change | Probe-Sense-Respond. Run small experiments. Do NOT plan a big-bang fix. |
| **Chaotic** | No discernible cause-effect. Crisis mode. | System failure during growth spike exposing multiple hidden debts | Act-Sense-Respond. Stabilize first, diagnose later. |

**Critical insight**: Most SMB structural debt is Complicated (fixable with the right expertise), but teams treat it as Complex (running experiments when they should hire an expert) or worse, as Clear (applying a "best practice" template to a problem that needs analysis). Misclassifying the domain leads to wrong remediation patterns.

**Mapping debt categories to Cynefin**:
- Visible debt: Usually Clear or Complicated. Known problem, discoverable fix.
- Hidden debt: Usually Complicated or Complex. Requires investigation to understand scope.
- Accelerating debt: Often Complex. The interaction between growth and debt creates emergent behavior that linear analysis misses.

---

## Debt Taxonomy

### Visible Debt

**Definition**: Problems the organization knows about and has chosen to tolerate — either because remediation is expensive, the impact seems manageable, or other priorities take precedence.

**Examples at Sharkitect**:
- Manual data transfer between systems that should be automated
- Known limitations in current tooling that require workarounds
- Documentation that's outdated but "everyone knows" the correct process
- Integrations that require restart/refresh to stay synced

**Detection**: Team members can list these when asked. They appear in retrospectives and complaint patterns.

**Risk level**: Moderate. Visible debt is managed (even if poorly) because it's acknowledged. The danger is when visible debt normalizes and people stop mentioning it.

**Scoring (1-5)**:
- 1: Minor inconvenience, <5 min/week of workaround time
- 2: Regular friction, 5-30 min/week of workaround time
- 3: Significant impact, 30-120 min/week of workaround time
- 4: Major drag, >2 hours/week of workaround time
- 5: Critical blocker, prevents key activities or causes errors

### Hidden Debt

**Definition**: Problems the organization doesn't know about — masked by workarounds that have become invisible, by people who compensate silently, or by processes that appear to work but are fragile.

**Examples at Sharkitect**:
- One person holds all knowledge of a critical process (bus factor = 1)
- A system appears reliable because someone manually checks and corrects errors
- Data quality looks good because consumers silently discard bad records
- Performance is acceptable because usage hasn't hit the hidden cliff

**Detection**: Hidden debt only surfaces through structured audits, departures of key people, system failures, or scale events. You cannot find hidden debt by asking — you must look.

**Audit triggers**:
- Key person departs or goes on leave
- System load increases >50%
- New integration added to existing system
- Quarterly operational audit (scheduled discovery)

**Risk level**: High. Hidden debt is the most dangerous category because it compounds silently. When it surfaces, it often does so as a crisis rather than a gradual degradation.

**Scoring (1-5)**:
- 1: Low blast radius if exposed (<1 system affected)
- 2: Moderate blast radius (1-2 systems)
- 3: Significant blast radius (3-5 systems or 1 revenue-critical system)
- 4: Major blast radius (cross-department impact)
- 5: Existential blast radius (could halt operations)

### Accelerating Debt

**Definition**: Problems that get worse proportionally (or worse, exponentially) with growth. Adding clients, team members, or service lines amplifies the problem rather than diluting it.

**Examples at Sharkitect**:
- Manual onboarding steps that scale linearly with each new client
- Reporting that requires manual assembly (each new client = more manual work)
- Integration architecture that requires N^2 connections as systems are added
- Knowledge that lives in one person's head — each new question adds to their bottleneck

**Detection**: Accelerating debt is visible when you plot effort against scale. If the line curves up, it's accelerating.

**Key question**: "If we 3x our client base, does this process 3x in effort, or worse?"
- 3x effort for 3x clients = linear (uncomfortable but survivable)
- 9x effort for 3x clients = quadratic (unsustainable, remediate now)
- Effort doesn't scale with clients = solved (non-debt)

**Risk level**: Critical before any growth phase. Accelerating debt must be addressed BEFORE scaling, not after. Post-scale remediation is 5-10x more expensive because you're fixing while simultaneously serving the enlarged client base.

**Scoring (1-5)**:
- 1: Linear scaling (manageable with additional resources)
- 2: Super-linear (1.5x effort per 1x growth)
- 3: Quadratic (2x effort per 1x growth)
- 4: Exponential (>2x effort per 1x growth)
- 5: Combinatorial (effort scales with combinations of variables)

---

## Debt Assessment Template

```markdown
## Architectural Debt Assessment

**Date:** [YYYY-MM-DD]
**Scope:** [Full business / Specific department / Specific system]
**Activation conditions met:** [List AC numbers]

### Debt Inventory

#### Visible Debt
| Item | Score (1-5) | Affected Systems | Weekly Cost | Remediation Estimate |
|------|:-----------:|-----------------|-------------|---------------------|
| [Debt item] | [n] | [systems] | [hours or $] | [effort] |

#### Hidden Debt (Discovered)
| Item | Score (1-5) | Blast Radius | Discovery Method | Remediation Estimate |
|------|:-----------:|-------------|------------------|---------------------|
| [Debt item] | [n] | [scope] | [how found] | [effort] |

#### Accelerating Debt
| Item | Score (1-5) | Scale Factor | Current Impact | Impact at 3x Scale |
|------|:-----------:|-------------|----------------|-------------------|
| [Debt item] | [n] | [linear/quadratic/etc] | [current] | [projected] |

### Total Debt Score
- Visible: [sum] / [max]
- Hidden: [sum] / [max]
- Accelerating: [sum] / [max]
- **Combined: [total] / [max]**

### Debt Heat Map
| Department | Visible | Hidden | Accelerating | Total |
|-----------|:-------:|:------:|:------------:|:-----:|
| Revenue | [n] | [n] | [n] | [n] |
| Operations | [n] | [n] | [n] | [n] |
| Technology | [n] | [n] | [n] | [n] |
| Marketing | [n] | [n] | [n] | [n] |

### Remediation Queue (Priority-Ordered)

Priority order: Accelerating → Hidden → Visible (within each: highest score first)

1. **[Debt item]** — Category: [type] — Score: [n]
   - Root cause: [what's actually wrong]
   - Remediation: [what to do]
   - Effort: [hours/days]
   - Dependencies: [what must happen first]
   - Owner: [who's responsible]
   - Deadline: [date]

2. **[Debt item]** — Category: [type] — Score: [n]
   [same structure]

### Strategic Recommendations
- [High-level recommendation based on debt patterns]
- [Structural change that would prevent future debt accumulation]
- [Investment needed and expected ROI]
```

---

## Cross-Reference: When This Framework Overlaps Other Skills

| If the debt is... | This framework handles... | Route to... |
|-------------------|--------------------------|-------------|
| Technology-specific (wrong database, bad API design) | Diagnosing it as debt | hq-tech-strategy for remediation |
| Process-specific (bad SOP, missing procedure) | Diagnosing it as debt | hq-operations for SOP creation |
| Revenue-impacting (pricing model doesn't scale) | Diagnosing it as debt | hq-revenue-ops for pricing revision |
| Brand-related (inconsistent voice at scale) | Diagnosing it as debt | hq-brand-review for voice audit |
| Knowledge-related (information scattered, stale) | Diagnosing it as debt | hq-knowledge-governance for KB audit |

This framework diagnoses and scores the debt. Other skills remediate it. The strategic-ops skill is the diagnostic layer that identifies WHERE the problem is, then routes to the appropriate remediation skill.
