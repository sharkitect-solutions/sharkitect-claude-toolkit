---
name: hq-orchestrator
description: >
  Use when a task touches multiple business domains (revenue + brand, tech + operations, legal + finance),
  requires coordinating 2+ specialist agents, needs cross-department synthesis for executive decision-making,
  or when the user asks to route a request to the right team/department.
  NEVER use for single-domain tasks where one specialist agent suffices (use that agent directly),
  generic task parallelism without business routing logic (use dispatching-parallel-agents skill),
  or general multi-agent coordination without Sharkitect business context (use multi-agent-coordinator agent).
version: 0.1.0
---

# HQ Orchestrator — Sharkitect Workforce Routing & Synthesis

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/routing-rules.md` | Any task needing domain classification or agent routing | Single-domain tasks with obvious agent match |
| `references/synthesis-format.md` | Combining results from 2+ agents into executive output | Single-agent results that need no synthesis |
| `references/department-taxonomy.md` | Unclear which department owns a task, or cross-department disputes | Task clearly belongs to one department |

## Core Principle

You are ONE agent with access to many specialists via the Task tool. This skill gives you the routing logic to decide WHICH specialists to launch and the synthesis format to combine their results. You do not "become" Marcus — you USE Marcus's routing rules.

## Routing Decision Tree

```
INCOMING TASK
  |
  +-- Classify domain(s) using Department Taxonomy
  |     |
  |     +-- Single domain? --> Route directly to matched agent(s)
  |     |
  |     +-- Multiple domains? --> Identify PRIMARY + SUPPORTING departments
  |           |
  |           +-- Load routing-rules.md for cross-department patterns
  |           +-- Launch agents in PARALLEL where possible
  |           +-- Synthesize using synthesis-format.md
  |
  +-- Check for advisory triggers:
  |     - Impacts company direction? --> Include strategic-ops (Axiom) agent
  |     - Has legal exposure? --> Include legal-advisor agent
  |     - Irreversible decision? --> Flag for user confirmation before executing
  |     - Affects 2+ departments? --> Include this orchestrator routing
  |
  +-- Execute and synthesize
        |
        +-- Parallel launch where agents are independent
        +-- Sequential launch where output feeds input
        +-- Return SINGLE synthesized recommendation to user
```

## Cross-Department Routing Patterns

| Request Pattern | Primary Agent(s) | Supporting Agent(s) | Synthesis Rule |
|----------------|------------------|---------------------|----------------|
| Client proposal | `sales-researcher` | `financial-analyst`, `legal-advisor`, `brand-reviewer` | Revenue-first: lead with deal value, support with risk + brand alignment |
| Tech architecture decision | `ai-systems-architect` | `financial-analyst`, `devops-engineer` | Tech-first: lead with architecture, support with cost + operations |
| Marketing campaign | `marketing-strategist` | `content-strategist`, `sales-researcher` | Pipeline-first: lead with pipeline impact, support with brand + revenue alignment |
| Process redesign | `business-analyst` | `project-manager`, `scrum-master` | Operations-first: lead with efficiency gains, support with timeline + team impact |
| Knowledge audit | `knowledge-governance` | `research-synthesizer` | Governance-first: lead with compliance, support with content quality |
| Brand review | `brand-reviewer` | `communication-excellence-coach`, `content-strategist` | Brand-first: lead with consistency, support with tone + messaging |
| Pricing decision | `financial-analyst` | `sales-researcher`, `competitive-intelligence-analyst` | Finance-first: lead with unit economics, support with market + competitive context |
| Legal/compliance | `legal-advisor` | `financial-analyst` | Risk-first: lead with exposure assessment, support with financial impact |

## Anti-Patterns (Mistakes That Cost Time)

1. **Routing Everything Through Orchestration**: Single-domain tasks don't need routing. If a user asks "review this contract," just launch `legal-advisor` directly. Orchestration adds latency for zero value on single-domain tasks.

2. **Sequential When Parallel Works**: If brand review and financial analysis don't depend on each other's output, launch them in parallel. Sequential launches when parallel is possible doubles execution time.

3. **Forgetting Advisory Triggers**: Any decision that is irreversible, affects company direction, or has legal exposure MUST include the relevant advisory agent. Missing this creates unreviewed risk.

4. **Synthesizing Without Conflict Resolution**: When two agents disagree (e.g., sales says "discount" but finance says "hold price"), DO NOT average. Present both positions with reasoning and let the user decide.

5. **Over-Routing Low-Stakes Tasks**: Internal documentation, simple edits, routine updates — these don't need multi-agent orchestration. Reserve orchestration for decisions with business impact.

## Synthesis Protocol

When combining results from multiple agents:

1. **Lead with the recommendation** — not the process
2. **Identify agreement** — where do all agents align?
3. **Surface disagreements** — present conflicting positions with reasoning
4. **Quantify where possible** — attach numbers to claims (revenue impact, risk score, timeline)
5. **End with decision prompt** — present 2-3 clear options for the user, ranked by the orchestrator's assessment

Output format: See `references/synthesis-format.md` for the full template.
