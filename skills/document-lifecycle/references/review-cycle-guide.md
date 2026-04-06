# Review Cycle Guide

Reference material for document lifecycle review cycles, escalation procedures, and review techniques.

## Category Definitions

### Strategy (90 days)
**Documents:** Business direction, niche focus, target market definition, value proposition, competitive positioning, growth strategy.
**Why 90 days:** Strategy changes slowly but has massive downstream impact. A stale niche definition means every proposal, pitch, and content piece targets the wrong audience. Quarterly review catches market pivots without creating review fatigue.
**Stales fastest:** Target market definition (clients come from unexpected industries), competitive positioning (market moves fast).
**Warning signs:** User discusses industries not in strategy docs. Proposals reference capabilities not listed. Elevator pitch language doesn't match documented positioning.

### Client (30 days)
**Documents:** Client details, active project timelines, scope documents, contact lists, project status, deliverable trackers.
**Why 30 days:** Client work evolves weekly. Projects change scope, contacts change roles, timelines shift. Monthly review is the minimum cadence to catch drift before it causes wrong deliverables.
**Stales fastest:** Project timelines (slip constantly), scope documents (requirements evolve through conversation), contact info (people change roles/leave).
**Warning signs:** Deliverables reference old scope. Work continues on "completed" projects. Different contacts referenced than documented.

### Operations (90 days)
**Documents:** Workflows, SOPs, team processes, decision frameworks, tool usage guides, onboarding procedures.
**Why 90 days:** Processes are relatively stable but evolve through practice. The documented SOP often lags behind the actual process by 2-3 iterations. Quarterly review catches the gap before it becomes a chasm.
**Stales fastest:** Tool-specific procedures (tools update frequently), multi-step workflows (people find shortcuts and stop following the documented version).
**Warning signs:** Tasks done differently than documented. Steps skipped regularly. New tools used that aren't in process docs.

### Pricing (60 days)
**Documents:** Service costs, package structures, rate cards, discount policies, pricing tiers, proposal templates with pricing.
**Why 60 days:** Pricing changes with market conditions, competitive pressure, and business learning. Two months is enough time for pricing to drift through ad-hoc adjustments that never get documented.
**Stales fastest:** Package structures (new services added, old ones bundled), discount policies (ad-hoc discounts become standard practice but docs still show list price).
**Warning signs:** Proposals use different numbers than pricing doc. New packages appear in conversations. Discounts applied that aren't in policy.

### Brand (120 days)
**Documents:** Brand voice guide, visual identity, messaging framework, taglines, tone guidelines, editorial standards.
**Why 120 days:** Brand evolves slowly and intentionally. Frequent review would create unnecessary churn. Quarterly-plus cadence catches genuine evolution (audience shift, market repositioning) without triggering on normal variation.
**Stales fastest:** Messaging framework (positioning language evolves through use), tone guidelines (voice naturally adapts to audience feedback).
**Warning signs:** Content tone doesn't match guide. Taglines or value props in deliverables differ from documented versions. Visual assets reference old colors/fonts.

### Technical (60 days)
**Documents:** CLAUDE.md configuration, system architecture notes, tool settings, integration documentation, API configurations.
**Why 60 days:** Technical systems evolve through development cycles. New tools get added, configurations change, integrations get updated. Two months of unchecked technical drift can cause cascading failures.
**Stales fastest:** CLAUDE.md (actively edited but rarely reviewed holistically), integration configs (APIs change versions, endpoints move).
**Warning signs:** Tools fail with unexpected errors. Configs reference deprecated settings. New integrations added but not documented.

## Escalation Ladder Deep Dive

### Current (within cycle)
No action. Document was reviewed within its configured cycle period.

### Due (past next_review)
**Trigger:** `next_review` date has passed, no prior deferral.
**Message template:**
> "[aios-core] Document review reminder: N document(s) are due for review. Run document-lifecycle skill when you have a moment."
**Behavior:** Gentle, non-blocking. Appears once at session start.

### Deferred (user said "later")
**Trigger:** User deferred a due review. Clock starts on 3-day re-ask.
**Message template:**
> "[aios-core] Deferred document reviews: N document(s) were deferred X days ago and need attention soon."
**Behavior:** Slightly firmer. Still deferrable one more time.

### Overdue (3+ days deferred)
**Trigger:** 3+ days since `deferred_at`.
**Message template:**
> "[aios-core] Document reviews overdue: N document(s) have been deferred for X days. These documents may contain outdated information affecting your work."
**Behavior:** Names the risk. This is the last deferral allowed.

### Critical (7+ days deferred)
**Trigger:** 7+ days since `deferred_at`.
**Category-specific risk messages:**

| Category | Critical Risk Statement |
|----------|----------------------|
| strategy | "Defines your business niche and target market -- stale info means proposals, pitches, and content target the wrong audience" |
| client | "Contains active project details -- outdated data leads to wrong deliverables and client miscommunication" |
| operations | "Describes how work gets done -- stale processes mean inconsistent execution and repeated mistakes" |
| pricing | "Defines service costs and packages -- wrong pricing in proposals means revenue loss or client confusion" |
| brand | "Governs brand voice and identity -- stale brand docs produce inconsistent messaging across all channels" |
| technical | "Configures system behavior -- outdated configs cause tool failures, wrong workflows, and wasted effort" |

**Behavior:** Hard stop. Must acknowledge before continuing other work.

## Example Review Dialogues

### Drift Resolution Example

**Context:** Claude is writing a proposal for a flooring company. The drift-detection hook fires because "flooring" matches key terms in the strategy document.

**Claude:** "I noticed a potential drift. Your strategy document (`knowledge-base/strategy/target-market.md`) states:

> *'Our primary niche is HVAC and plumbing contractors in the residential market.'*

However, we're currently writing a proposal for a flooring company. Has your target market expanded beyond HVAC and plumbing?"

**User:** "Yes, we expanded to include flooring and general construction. Update that doc."

**Claude:** Updates `target-market.md` to reflect the expanded niche. Then runs:
```
python tools/supabase-sync.py push-lifecycle "knowledge-base/strategy/target-market.md" last_reviewed=now escalation_state=current last_review_outcome=updated last_review_summary="Expanded target market from HVAC/plumbing to include flooring and general construction"
```

### Scheduled Review Example

**Context:** Pricing document flagged as due (60-day cycle reached). No drift detected during work.

**Claude:** "Your pricing document (`knowledge-base/revenue/pricing.md`) is due for review. Let me check it against recent activity.

I found one potential issue: In recent work, you referred to the 'Growth Package' but your pricing doc lists a 'Professional Package' at that tier. Was the package renamed?

I also have a few questions about sections I can't verify from context:
1. The starter package is listed at $500/month -- is that still current?
2. The setup fee shows $1,500 -- still accurate?
3. The annual discount is listed as 15% -- has this changed?"

**User:** "Yes, we renamed Professional to Growth. Pricing is all still the same."

**Claude:** Updates the package name in the doc. Then runs:
```
python tools/supabase-sync.py push-lifecycle "knowledge-base/revenue/pricing.md" last_reviewed=now escalation_state=current last_review_outcome=updated last_review_summary="Renamed Professional Package to Growth Package. Pricing amounts confirmed accurate." review_count=4
```

## Override Guidance

**When to change a document's category:**
- Document was auto-classified by path but its content doesn't match (e.g., a "strategy" folder doc that's actually an operations SOP)
- Business changes make a document more time-sensitive (e.g., a brand doc becomes client-specific during a rebrand)

**When to shorten a cycle:**
- Document covers a rapidly changing domain (e.g., pricing during a market shift)
- Document has been flagged for drift 2+ times within its current cycle
- Business is in a transition period (pivot, expansion, rebrand)

**When to lengthen a cycle:**
- Document covers stable, mature content (e.g., company history, founding values)
- Document has been confirmed unchanged in 3+ consecutive reviews

**Multi-category documents:**
When a document spans categories (e.g., a client proposal with pricing), use the SHORTER cycle. A client proposal with pricing data should use the client cycle (30 days), not the pricing cycle (60 days).

**Document retirement:**
When a document is no longer relevant, mark it inactive rather than deleting:
```
python tools/supabase-sync.py push-lifecycle "<doc_path>" escalation_state=current last_review_outcome=retired last_review_summary="No longer relevant: <reason>"
```
Then set `is_active=false` in the doc_lifecycle table.

## Review Session Best Practices

- **Batch by category** when multiple documents are due. Review all pricing docs together, then all strategy docs. Context switching between categories reduces accuracy.
- **Maximum 5 documents per review session.** After 5, fatigue leads to rubber-stamping. If more than 5 are due, split across sessions.
- **Priority order:** critical > overdue > due. Always address the most urgent first.
- **Start with the most-likely-changed document.** If you know the user has been working in a specific area, review those docs first while context is fresh.
- **Maximum 3-5 targeted questions per document.** More than that triggers the Question Dump anti-pattern.
- **Never ask "is everything still accurate?"** Always ask about specific assertions. The vague question gets a vague rubber-stamp answer.
- **Source your questions:** Pull from brain memories first (recent decisions, activity). Only ask the user about things you truly can't verify from available context.