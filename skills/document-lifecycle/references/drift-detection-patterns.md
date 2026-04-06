# Drift Detection Patterns

Expert reference for identifying when tracked documents have become stale based on current work activity.

## Drift Patterns by Category

### Strategy Drift

| Signal | Example | Check Against |
|--------|---------|---------------|
| Niche/market shift | User works with flooring companies but strategy says "HVAC and plumbing" | `knowledge-base/strategy/` docs — target market, niche definition |
| Target audience change | Proposals target property managers but docs say "homeowners" | Buyer persona documents, ICP definitions |
| Business model pivot | Revenue discussions reference "retainer packages" but docs say "project-based" | Revenue model, pricing structure docs |
| Service expansion | Deliverables include services not listed in strategy | Service catalog, capabilities documents |
| Geographic shift | Work targets new regions not in strategy | Market definition, service area docs |

### Pricing Drift

| Signal | Example | Check Against |
|--------|---------|---------------|
| Rate changes | Proposal quotes $750/month but pricing doc says $500/month | Rate cards, pricing tiers |
| Package restructuring | References "Growth Package" but docs list "Professional Package" | Package definitions, tier names |
| Discount patterns | Systematic 20% discounts suggest listed prices are too high | Discount policies, standard rates |
| New service pricing | Work priced for a service with no entry in pricing doc | Service catalog pricing |
| Payment terms shift | Net-30 discussed but docs say Net-15 | Payment terms, contract templates |

### Process Drift

| Signal | Example | Check Against |
|--------|---------|---------------|
| Tool changes | References Monday.com but SOPs document Asana workflows | Tool-specific SOPs, workflow docs |
| Workflow modifications | Steps consistently skipped or reordered vs documented SOP | Step-by-step procedure docs |
| New processes | Recurring task pattern with no matching SOP | SOP directory, workflow index |
| Role changes | Tasks done by different people than documented | Team responsibility docs, RACI matrices |
| Automation replacing manual | "The system handles that now" but SOP describes manual steps | Process documentation |

### Client Drift

| Signal | Example | Check Against |
|--------|---------|---------------|
| Scope changes | Deliverables don't match project scope document | Project scope, SOW docs |
| Relationship status | Active work on "completed" project or silence on "active" one | Project status docs, client records |
| Contact changes | Different contacts referenced than documented | Client contact lists |
| Priority shifts | Client's stated priorities differ from project docs | Project briefs, kick-off notes |

### Brand Drift

| Signal | Example | Check Against |
|--------|---------|---------------|
| Voice changes | Content tone more casual than brand guide specifies | Brand voice guide, tone guidelines |
| Messaging changes | Taglines or value props differ from documented versions | Messaging framework, positioning docs |
| Positioning shift | Content positions differently than brand docs describe | Competitive positioning, brand strategy |

### Technical Drift

| Signal | Example | Check Against |
|--------|---------|---------------|
| Config changes | System uses settings different from documented config | CLAUDE.md, tool configuration docs |
| Architecture changes | New tools or integrations not in tech docs | System architecture docs, integration list |
| Process automation | Manual processes automated but docs still describe manual | Technical SOPs, workflow documentation |
| Dependency changes | New libraries or services not in stack documentation | Tech stack docs, dependency lists |

## Signal Detection Techniques

### Keyword Extraction
Extract key nouns from the document: proper nouns, dollar amounts, tool names, role titles, company names, industry terms. Compare against the same extracted from current work. Mismatches in these high-signal terms are drift candidates.

### Assertion Mapping
Documents make implicit assertions: "We serve HVAC companies" (niche claim), "Starter package is $500/month" (price claim), "We use Asana for project management" (tool claim). List each testable assertion, then check if recent work confirms or contradicts it.

### Temporal Analysis
Check dates and timeframes in documents:
- "Q1 2026 goals" — review after Q1 ends
- "This month's priorities" — stale after the month
- "Current project timeline" — check against actual progress
- "As of March 2026" — flag when significantly past that date

### Negation Detection
Watch for explicit negation signals from the user:
- "We don't do that anymore"
- "We stopped using X"
- "That's not how we handle it now"
- "We moved away from that approach"

Any of these → immediately check if the negated item appears in tracked documents as current.

## False Positive Avoidance

**Do NOT flag drift when:**

1. **Temporary deviation** — User says "just for this project" or "trying something new." One-off experiments aren't drift. They're exploration.

2. **Aspirational content** — Strategy docs may describe future state. Work that doesn't match aspirations isn't drift — the docs describe where they're going, not where they are now.

3. **Context-dependent variation** — A proposal for a specific client may deviate from general pricing. Custom quotes aren't pricing drift — they're client-specific adjustments.

4. **Historical references** — Discussing past work that used old processes isn't drift. It's history. Only flag if the past process is described as current in docs.

5. **Single-instance exception** — One task done differently doesn't invalidate an SOP. Could be a justified exception.

### The 2-Instance Rule
A single contradiction is a data point. Two contradictions in the same direction within a short period is a pattern. Flag on the pattern, not the single instance.

**Exception:** If the user explicitly states a permanent change ("We're switching to X from now on"), flag immediately on one instance.

### Confidence Scoring

| Confidence | Signal Pattern | Action |
|-----------|---------------|--------|
| **High** | User explicitly states change + doc contradicts | Flag immediately |
| **Medium** | 2+ implicit contradictions in same direction | Flag as potential drift |
| **Low** | Single implicit contradiction | Note internally, watch for second instance |
| **Noise** | Temporary/aspirational/context-specific variation | Do not flag |

## Resolution Patterns

| Severity | Signal | Resolution |
|----------|--------|------------|
| **Minor correction** | Single fact changed (phone number, tool name, contact) | Update in place, same document |
| **Section update** | One section outdated, rest is fine | Rewrite the section, preserve rest |
| **Major revision** | Core assumptions changed (new niche, new pricing model) | Full document rewrite with user input |
| **Document retirement** | Document describes something no longer relevant | Mark inactive in lifecycle, archive |
| **Document split** | One doc covers two topics that have diverged | Create two new docs, retire original |

**When multiple drift items found simultaneously:** Address highest-severity first. A major revision supersedes minor corrections in the same document.

## Quantified Drift Thresholds

These thresholds help calibrate when drift signals cross from "noise" to "actionable":

| Category | Escalation Trigger | Rationale |
|---|---|---|
| Strategy | 2+ proposals targeting industries not in strategy docs within 30 days | One proposal to a new industry is exploration. Two is a pattern indicating the niche has shifted. |
| Pricing | Any dollar amount in a proposal differing by >10% from pricing doc | Small rounding or custom adjustments are normal. >10% deviation means the pricing doc is wrong or a new tier exists undocumented. |
| Operations | Same SOP step skipped or reordered in 3+ consecutive task executions | Once is a shortcut. Twice is habit. Three times means the SOP no longer matches reality. |
| Client | Any work on a project marked "completed" in client docs, OR silence >14 days on a project marked "active" | Status mismatches cause wrong resource allocation and missed deadlines. |
| Brand | Content tone audit fails brand guide in 2+ independent deliverables | One tone mismatch could be context-dependent. Two across different deliverables means the voice has evolved past the guide. |
| Technical | Any tool failure traceable to a config value that differs from documented config | Config drift causes immediate operational failures. Zero tolerance -- one failure = one drift flag. |

## Cross-Category Drift Cascades

Drift in one category often signals drift in related categories. When you detect drift, check these cascade paths:

| Primary Drift | Check These Too | Why |
|---|---|---|
| Strategy (niche change) | Pricing (new market may need different rates), Brand (messaging for new audience), Operations (new workflows for new services) | A niche shift touches everything downstream |
| Pricing (rate change) | Client docs (active proposals may quote old rates), Operations (quoting process may need update) | Price changes propagate to every client-facing document |
| Client (scope change) | Pricing (scope change may affect billing), Operations (new deliverables may need new SOPs) | Scope changes create new work that may not have processes |
| Technical (tool change) | Operations (SOPs referencing old tool), Brand (if tool affects content delivery) | Tool changes invalidate every SOP that references the old tool |
| Brand (voice shift) | All content-related client docs, Strategy (if voice shift reflects positioning change) | Voice changes must propagate to all client-facing content |

**The cascade rule:** When flagging drift in any category, spend 60 seconds checking the cascade paths above. A strategy drift that also invalidates pricing and brand docs is a major revision across 3 documents, not a minor correction in one.

## Comparison Quick Reference

```
DRIFT CHECK PROCEDURE
[ ] Read document fully — note every factual assertion
[ ] List key terms: proper nouns, dollar amounts, tool names, role titles
[ ] Check current task: do any terms contradict document terms?
[ ] Check recent brain memories: any decisions that supersede document content?
[ ] Check for temporal staleness: any dates or timeframes that have passed?
[ ] Apply 2-instance rule: single deviation or confirmed pattern?
[ ] If drift confirmed: classify severity (minor/section/major/retire/split)
[ ] Present with both quotes: "Doc says [X], but [evidence shows Y]"
```