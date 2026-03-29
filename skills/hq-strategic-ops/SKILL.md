---
name: hq-strategic-ops
description: >
  Use when diagnosing architectural debt across Sharkitect's business systems, identifying structural
  misalignment between strategy and execution, conducting enterprise-level structural diagnosis, or
  evaluating whether operational problems are symptoms of deeper architectural issues.
  Activated by specific conditions: repeated process failures, scaling bottlenecks, tool proliferation,
  integration breakdowns, or when the same problem surfaces in 3+ departments.
  NEVER use for day-to-day operational issues (use hq-operations skill),
  technology-specific architecture decisions (use hq-tech-strategy skill),
  or competitive market analysis (use competitive-intelligence-analyst agent).
version: 0.1.0
---

# HQ Strategic Operations — Architectural Debt & Structural Diagnosis

## Scope Boundary

| In Scope | Out of Scope | Route To Instead |
|----------|-------------|-----------------|
| Cross-department structural diagnosis | Single-department process fixes | hq-operations |
| Architectural debt scoring & classification | Technology selection & implementation | hq-tech-strategy |
| Remediation pattern selection | Revenue model restructuring | hq-revenue-ops |
| Structural root cause analysis | Brand consistency issues | hq-brand-review |
| Growth bottleneck identification | Knowledge base organization | hq-knowledge-governance |
| Stakeholder communication of findings | Competitive market positioning | competitive-intelligence-analyst agent |

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/debt-framework.md` | Diagnosing structural problems, scoring architectural debt, classifying debt by Cynefin domain | Day-to-day operational issues, single-system problems |
| `references/remediation-patterns.md` | Selecting remediation approach, applying Theory of Constraints, Wardley Mapping debt classification, communicating findings to stakeholders | Initial diagnosis phase before debt is scored and classified |

## Paired Agents

Launch these agents (Task tool) for execution:
- `competitive-intelligence-analyst` — Market positioning context for structural decisions
- `market-research-analyst` — Industry benchmarking when evaluating structural alternatives
- `research-synthesizer` — Combining multi-source findings into structural diagnosis

Use this skill directly (without agent) for:
- Quick activation condition check (does this problem qualify for structural diagnosis?)
- Debt category classification (visible/hidden/accelerating)
- Routing structural problems to the right diagnostic approach

## 10 Activation Conditions

This skill activates ONLY when one or more of these conditions are present. If none apply, the problem is operational (route to hq-operations) or technical (route to hq-tech-strategy).

```
PROBLEM REPORTED
  |
  +-- AC-1: Same failure has occurred 3+ times despite fixes
  |     --> Pattern indicates structural cause, not execution failure
  |
  +-- AC-2: Problem affects 3+ departments simultaneously
  |     --> Cross-cutting issues are architectural, not departmental
  |
  +-- AC-3: Adding resources doesn't improve output
  |     --> Classic structural bottleneck signal
  |
  +-- AC-4: Tool count for same function exceeds 3
  |     --> Tool proliferation indicates missing architecture
  |
  +-- AC-5: Integration between systems requires manual steps
  |     --> Indicates structural gaps in system design
  |
  +-- AC-6: Decision-making requires data from 4+ sources
  |     --> Indicates fragmented information architecture
  |
  +-- AC-7: New hires take >30 days to become productive
  |     --> Onboarding complexity signals structural debt
  |
  +-- AC-8: Workarounds have become standard practice
  |     --> Normalized workarounds are hidden debt
  |
  +-- AC-9: Growth creates proportionally more operational work
  |     --> Indicates non-scalable architecture
  |
  +-- AC-10: Strategic pivots require >3 months of retooling
  |      --> Indicates brittle, tightly-coupled architecture
  |
  NONE OF THE ABOVE --> Not a structural problem.
  Route to hq-operations (process) or hq-tech-strategy (technical).
```

## Debt Category Quick Reference

Full framework in companion file. Quick classification:

| Category | Definition | Detection Signal | Urgency |
|----------|-----------|-----------------|---------|
| **Visible** | Known problems being tolerated | Team openly discusses workarounds | Moderate — schedule remediation |
| **Hidden** | Unknown problems masked by workarounds | Discovered during audits or failures | High — investigate scope |
| **Accelerating** | Problems that worsen with growth | Each new client/project amplifies the issue | Critical — remediate before next growth phase |

## Structural Diagnosis Process

1. **Activation check**: Does the problem meet 1+ activation conditions?
2. **Debt classification**: Is this visible, hidden, or accelerating debt?
3. **Impact mapping**: Which departments, processes, and systems are affected?
4. **Root cause analysis**: What structural element (process, tool, data flow, organizational) is the source?
5. **Remediation options**: What changes would resolve the structural issue?
6. **Cost-benefit**: What's the cost of remediation vs. the cost of continued debt?

## Anti-Patterns

1. **Treating Symptoms**: Fixing individual failures without investigating whether they share a structural root cause. Three related failures that each get individual fixes = three patches on a structural crack. In SMBs with 5-15 people, symptom-fixing consumes an average of 12 hours/week across the team before anyone notices the pattern.

2. **Solo Founder Bypass**: The owner works around the structure instead of fixing it. In SMBs, this happens in 70%+ of structural debt cases. The bypass becomes the new process, and when the owner is unavailable, the team has no process at all. Consequence: every vacation or sick day exposes the debt as a full operational stall. Detection: ask "what happens when [owner] is out for a week?" -- if the answer involves "we wait," this anti-pattern is active.

3. **Tool-as-Architecture**: Buying a new tool and calling it a structural fix. Tools without process change have a 60% failure rate within 6 months (Gartner SMB adoption data). The tool gets blamed, a new tool is purchased, and the cycle repeats. A 10-person company with this pattern typically accumulates 3-5 overlapping tools per function within 18 months, each partially adopted. Detection: count tools per business function -- if >2, this pattern is likely active.

4. **Premature Automation**: Automating a broken process before fixing the process itself. Automation amplifies both efficiency AND dysfunction. A manual process with a 15% error rate that gets automated becomes a system that generates errors at machine speed. In SMBs, this commonly appears as n8n/Zapier workflows built on top of inconsistent data entry, producing confident-looking outputs from garbage inputs. Fix the process first, then automate.

5. **Debt Denial**: Acknowledging that workarounds exist but refusing to classify them as debt. "It works" is not the same as "it's sustainable." In a 10-person company, a single normalized workaround costs an average of 3-5 hours/week across the team. Five normalized workarounds = one full-time employee equivalent spent on waste.

6. **Analysis Without Action**: Producing detailed debt assessments that sit in documents while the debt compounds. Every diagnosis must end with a prioritized remediation queue with owners and deadlines. If a debt assessment is older than 30 days with no action taken, the assessment itself has become debt -- it consumed resources and produced nothing.

## Edge Cases

**Overlapping debt categories**: A single item can be visible AND accelerating (known workaround that gets worse with growth). Score it in BOTH categories. For the remediation queue, use the higher-urgency category to determine priority. Do not double-count in the total debt score -- use the higher of the two scores.

**Organization disagrees about whether something is debt**: Common when the person who built the system is still on the team. The builder sees a reasonable tradeoff; others see a workaround. Resolution: apply the 3x test from the debt framework. "If we 3x our load, does this scale?" removes subjective judgment. If the answer is "no" or "it gets worse," it is debt regardless of intent.

**Debt discovered during crisis vs. planned audit**: Crisis-discovered debt gets emergency scoring -- skip the full assessment template and go straight to the remediation decision tree (see remediation-patterns.md). Score blast radius and capacity only. Full assessment happens AFTER the crisis is contained. Planned audit debt follows the standard process. Never let crisis-discovered debt skip the remediation queue entirely -- after the emergency fix, it must be formally assessed and tracked.

**Debt across service lines with different owners**: When structural debt spans multiple service lines (e.g., a shared CRM process that affects both VDR and RLR), the remediation owner must be someone with authority across both lines. If no such person exists, that absence is itself structural debt -- flag it as a hidden debt item with score 4+ (cross-department impact).
