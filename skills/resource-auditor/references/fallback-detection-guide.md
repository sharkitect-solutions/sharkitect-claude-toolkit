# Fallback Detection Guide

Patterns that indicate a FALLBACK gap -- when a generic or adjacent resource was used where a specialized tool would produce meaningfully better results.

## What Makes It a Fallback (Not Just "Using What's Available")

A fallback is NOT: using a general-purpose skill for a general-purpose task.
A fallback IS: using a general-purpose skill for a task with domain-specific requirements the skill doesn't address.

**The test:** Would a domain expert look at the output and say "this is competent but clearly not from someone who specializes in this"?

## Signal Categories

### 1. Domain Mismatch Signals

The skill was designed for a different domain than the task requires.

| Signal | Example | Why It's a Fallback |
|---|---|---|
| Marketing skill used for technical writing | `copywriting` for API documentation | Copywriting optimizes for persuasion; API docs need precision, completeness, developer empathy |
| General SEO used for local SEO | `seo-optimizer` for service-area pages | General SEO lacks LocalBusiness schema, NAP consistency, geo-targeting patterns |
| General writing used for legal/compliance | `writing-clearly-and-concisely` for privacy policy | Legal docs need jurisdiction-specific clauses, regulatory language, liability structures |
| Frontend skill used for email HTML | `frontend-developer` for email templates | Email HTML has unique constraints (no JS, limited CSS, client rendering differences) |
| General analytics used for attribution | `business-analyst` for marketing attribution | Attribution needs multi-touch models, incrementality testing, channel interaction analysis |

### 2. Adaptation Effort Signals

The resource "worked" but required significant manual adaptation.

| Signal | Indicates |
|---|---|
| "I adapted the template for this specific use case" | Template wasn't designed for this domain |
| "I modified the approach because the skill covers a different scenario" | Skill is adjacent, not on-target |
| "I combined two skills to cover this task" | Neither skill fully covers the domain |
| "I supplemented the skill with web research" | Skill lacks the specific knowledge needed |
| "I used general principles from the skill but applied domain-specific adjustments" | Skill provides framework but not domain content |

### 3. Output Quality Signals

The output is functional but lacks expert-level qualities.

| Signal | What's Missing |
|---|---|
| Output uses generic terminology instead of industry jargon | Industry-specific vocabulary and conventions |
| Output follows a general structure instead of domain-specific format | Domain-standard templates and structures |
| Output lacks domain-specific metrics or benchmarks | Industry KPIs, benchmarks, standards |
| Output provides general best practices instead of domain-specific ones | Specialized patterns only experts know |
| Output misses regulatory or compliance requirements | Domain-specific legal/compliance knowledge |

### 4. Self-Assessment Phrases

Things Claude might say (or think) that indicate a fallback:

| Phrase | Gap Type |
|---|---|
| "I used general best practices for this" | Likely FALLBACK if domain-specific practices exist |
| "This follows standard patterns" | FALLBACK if the domain has non-standard specialized patterns |
| "I don't have a specific skill for this, so I applied..." | MISSING or FALLBACK |
| "The closest skill I have is..." | FALLBACK -- adjacent skill used |
| "I combined knowledge from training with..." | MISSING -- no installed skill covers this |
| "Based on general principles..." | Could be MISSING or FALLBACK depending on context |

## Severity Assessment for Fallbacks

### Critical Fallback
- Output would need significant rework if reviewed by a domain expert
- Key domain requirements are missing (not just suboptimal)
- Client/user would notice the gap without being told

### Warning Fallback
- Expert would improve the output but it's functional
- Domain-specific optimizations are missing but basics are covered
- A specialized skill would produce meaningfully better results (2x+ improvement)

### Info Fallback
- Minor domain-specific enhancements possible
- Output is good; specialized skill would add polish
- Difference between "good" and "great" rather than "generic" and "expert"

## Common Fallback Patterns by Workspace Type

### Client Workspaces (Industry-Specific)
Most common fallback: using general marketing/content skills without industry-specific companions.
- General `copywriting` instead of industry-tailored content patterns
- General `seo-optimizer` instead of vertical-specific SEO (local, e-commerce, SaaS)
- General `email-sequence` instead of industry-specific nurture flows

### Technical Workspaces
Most common fallback: using general coding skills without framework-specific guidance.
- General code review without framework-specific anti-patterns
- General testing without domain-specific test strategies
- General architecture without platform-specific constraints

### HQ / Operations Workspace
Most common fallback: using general business skills without operational context.
- General project management without agency-specific workflow patterns
- General analytics without Sharkitect's specific KPI framework
- General reporting without brand-aligned deliverable templates