---
name: document-lifecycle
description: "Use when (1) a hook signals potential drift between current work and tracked documents, (2) session-start alerts show documents due/overdue/critical for review, (3) user requests a document freshness check, or (4) completing a task that changed business direction, pricing, processes, or strategy. Two modes: drift resolution (compare doc against current work, present contradictions) and scheduled review (read doc, diff against recent activity, ask targeted confirmation questions). Manages escalation ladder from gentle reminder through hard stop. Do NOT use for: content creation enforcement (use hq-content-enforcer), post-task resource gap detection (use resource-auditor), brain memory management (handled by supabase-sync)."
---

# Document Lifecycle Manager

Ensures documents across all workspaces stay current through real-time drift detection and scheduled freshness reviews. Tracks review history, manages escalation, and prevents stale information from corrupting downstream work.

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/review-cycle-guide.md` | Needing category definitions, cycle lengths, escalation details, example review dialogues, or override guidance | Simple drift checks where you already know the category and cycle |
| `references/drift-detection-patterns.md` | Analyzing potential drift, comparing doc content against work context, classifying drift type, or checking false positive criteria | Scheduled reviews where drift was already identified by Sentinel |
| `references/failure-modes-and-rationalizations.md` | Catching yourself skipping a review, rationalizing a deferral, or noticing a failure pattern in your review behavior; also load during post-review self-audit | Reviews proceeding normally with no resistance or shortcut temptation |

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Check if this doc is still accurate" | YES | -- |
| "Review overdue documents" | YES | -- |
| "A hook flagged potential drift" | YES | -- |
| "Update document after review" | YES | -- |
| "Defer a document review" | YES | -- |
| "Am I using brand voice correctly?" | NO | hq-content-enforcer + hq-brand-review |
| "Did I use all available resources?" | NO | resource-auditor |
| "Sync memories to Supabase" | NO | supabase-sync.py |
| "Score this skill" | NO | skill-judge |

## Mode 1: Drift Resolution

Triggered during work when a hook or observation suggests current activity contradicts a tracked document.

```
HOOK SIGNALS DRIFT
  |
  v
READ FLAGGED DOCUMENT
  |
  v
COMPARE AGAINST CURRENT WORK CONTEXT
  |
  +--> Real drift? --YES--> PRESENT CONTRADICTION
  |                           |
  |                           +--> User updates doc --> UPDATE LIFECYCLE
  |                           |                         (reset to current)
  |                           |
  |                           +--> User defers --> SET deferred_at,
  |                                                escalation=deferred
  |
  +--> False positive? --YES--> No action. Log for pattern improvement.
```

### Drift Comparison Steps

1. **Read the flagged document fully** -- not just the section that triggered
2. **Identify specific assertions** -- factual claims the document makes (niche, pricing, processes, tools, team roles)
3. **Compare each assertion** against what was just discussed, written, or decided in current work
4. **If contradiction found**, present BOTH sides with direct quotes:
   > "Your strategy doc states: *'Our primary niche is HVAC and plumbing contractors.'* However, in this session we've been working on a proposal for a flooring company. Which is accurate?"
5. **If user updates the doc**: edit the document, then run:
   ```
   python tools/supabase-sync.py push-lifecycle "<doc_path>" last_reviewed=now escalation_state=current last_review_outcome=updated last_review_summary="<what changed>"
   ```
6. **If user defers**:
   ```
   python tools/supabase-sync.py push-lifecycle "<doc_path>" escalation_state=deferred deferred_at=now
   ```

## Mode 2: Scheduled Review

Triggered when session-start alerts show documents past their review cycle, or when Sentinel's freshness auditor flags overdue items.

```
DOCUMENT FLAGGED AS DUE/OVERDUE/CRITICAL
  |
  v
[1] READ THE DOCUMENT -- full content, not summary
  |
  v
[2] PULL RECENT WORK CONTEXT
    Query brain memories for this workspace's recent activity.
    What has the user been working on? Any decisions made?
  |
  v
[3] DIFF-BASED CHECK
    Compare document assertions against recent work.
    Present contradictions: "Doc says X, recent work shows Y"
  |
  v
[4] TARGETED QUESTIONS (for unverifiable sections)
    Ask SPECIFIC questions -- max 3-5 per document.
    GOOD: "Your pricing shows $500/month for the starter package. Still current?"
    BAD:  "Is the pricing section still accurate?"
  |
  v
[5] USER CONFIRMS OR UPDATES
  |
  v
[6] UPDATE LIFECYCLE
```

### Update Commands

**Confirmed (no changes needed):**
```
python tools/supabase-sync.py push-lifecycle "<doc_path>" last_reviewed=now escalation_state=current last_review_outcome=confirmed last_review_summary="Reviewed and confirmed accurate" review_count=<N+1>
```

**Updated (changes made):**
```
python tools/supabase-sync.py push-lifecycle "<doc_path>" last_reviewed=now escalation_state=current last_review_outcome=updated last_review_summary="<what changed>" review_count=<N+1>
```

**Major revision:**
```
python tools/supabase-sync.py push-lifecycle "<doc_path>" last_reviewed=now escalation_state=current last_review_outcome=major-revision last_review_summary="<scope of rewrite>" review_count=<N+1>
```

## Escalation Ladder

| State | Trigger | Behavior | Deferrable? |
|-------|---------|----------|-------------|
| `current` | Within review cycle | No alerts | N/A |
| `due` | Past `next_review` date | Gentle reminder at session start | Yes -- moves to `deferred` |
| `deferred` | User said "later" | Re-asks after 3 days | Yes -- one more time |
| `overdue` | 3+ days deferred | Firmer reminder, explains importance | Yes -- but warned this is the last deferral |
| `critical` | 7+ days deferred | Hard stop with specific risk reasoning | Must acknowledge before other work |

**Deferral command:**
```
python tools/supabase-sync.py push-lifecycle "<doc_path>" escalation_state=deferred deferred_at=now
```

## Category Reference

| Category | Cycle | Examples |
|----------|-------|---------|
| strategy | 90 days | Business direction, niche focus, target market, value proposition |
| client | 30 days | Client details, active projects, timelines, contacts, scope |
| operations | 90 days | Workflows, SOPs, team processes, decision frameworks |
| pricing | 60 days | Service costs, packages, rates, discount policies |
| brand | 120 days | Brand voice guide, visual identity, messaging framework |
| technical | 60 days | CLAUDE.md, tool configs, system architecture, integrations |

## Failure Modes (5 Named Anti-Patterns)

| Anti-Pattern | Core Error | Quick Fix |
|---|---|---|
| **The Rubber Stamp** | Confirming without reading or quoting assertions | Quote at least one specific assertion when confirming |
| **The Infinite Defer** | Always pushing to "later" with no tracking | Hard stop after 2 deferrals -- no exceptions |
| **The Partial Review** | Only checking sections related to current work | Full document scan in Mode 2; drift hides in unused sections |
| **The Silent Update** | Updating without recording what changed | Always include `last_review_summary` with specifics |
| **The Question Dump** | Asking 15+ confirmations at once | Max 3-5 targeted questions; source from brain first |

**If you catch yourself rationalizing a shortcut** ("just reviewed this," "nothing changed," "user is busy," "just a config file," "next session"): load `references/failure-modes-and-rationalizations.md` for the full breakdown of why each rationalization fails and what to do instead.