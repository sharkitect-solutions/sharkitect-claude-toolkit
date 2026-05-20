# Phase 6 Preparation Prompts

> **When to use:** Run ONE prompt per workspace AFTER Phase 5 is complete in that workspace. The workspace has just finished verifying all its systems -- now interrogate it about its Supabase relationship.
>
> **What this produces:** Each workspace generates a structured report. All three reports go to Sentinel as input for Phase 6 planning.
>
> **Where reports land:** Each workspace saves its report to `~/.claude/docs/phase6-prep/` with the naming convention `phase6-prep-{workspace}.md`.

---

## Prompt 1: Workforce HQ

```
Phase 5A is complete. Before we move on, I need you to produce a Supabase Data Relationship Report for this workspace. This feeds into Phase 6 where Sentinel will restructure and optimize our Supabase brain.

Be brutally honest. If something is broken, half-baked, or you're not sure about it -- say so. This is an audit, not a sales pitch.

Create a file at ~/.claude/docs/phase6-prep/phase6-prep-hq.md with the following sections:

## 1. WHAT I WRITE TO SUPABASE

For each table this workspace writes to, document:
- Table name
- What triggers the write (which system, what event)
- Fields written and their format
- Frequency (real-time, daily, on-demand)
- Is the data actually useful? Or are we writing it because we were told to?
- Data quality: is what we're writing clean, complete, and consistent?

## 2. WHAT I READ FROM SUPABASE

For each table this workspace reads from, document:
- Table name
- Which system reads it and why
- Fields read
- Is the data there when we need it? Or is it often stale/empty/wrong?
- What data do we WISH was there but isn't?
- Any queries that are ugly, slow, or unreliable because of schema issues?

## 3. WHAT I SHOULD BE DOCUMENTING BUT AM NOT

Think about everything this workspace does -- client work, proposals, briefs, error handling, business ops. What activities produce valuable information that currently disappears after the session ends? What would Sentinel, Skill Hub, or future CEO briefs benefit from knowing about HQ's work?

## 4. WHAT I NEED FROM OTHER WORKSPACES

What data from Skill Hub or Sentinel would make HQ's systems work better? For example: does the CEO brief need to know about gap resolutions from Skill Hub? Does error handling need system health data from Sentinel?

## 5. PAIN POINTS

What's frustrating about Supabase right now from this workspace's perspective? Schema problems, missing tables, data that's in the wrong place, queries that don't make sense, things you have to work around?

## 6. AUTONOMY REQUIREMENTS

If this workspace were to operate with ZERO human intervention for a full day, what Supabase data would it need to read and write to do its job? Map out the ideal state -- not what exists today, but what SHOULD exist for full autonomy.

Also review ~/.claude/docs/supabase-data-flow-tracker.md for any entries logged during Phase 5. Incorporate those observations into your report.
```

---

## Prompt 2: Skill Management Hub

```
Phase 5B is complete. Before we move on, I need you to produce a Supabase Data Relationship Report for this workspace. This feeds into Phase 6 where Sentinel will restructure and optimize our Supabase brain.

Be brutally honest. If something is broken, half-baked, or you're not sure about it -- say so. This is an audit, not a sales pitch.

Create a file at ~/.claude/docs/phase6-prep/phase6-prep-skillhub.md with the following sections:

## 1. WHAT I WRITE TO SUPABASE

For each table this workspace writes to, document:
- Table name
- What triggers the write (which system, what event)
- Fields written and their format
- Frequency (real-time, daily, on-demand)
- Is the data actually useful? Or are we writing it because we were told to?
- Data quality: is what we're writing clean, complete, and consistent?

## 2. WHAT I READ FROM SUPABASE

For each table this workspace reads from, document:
- Table name
- Which system reads it and why
- Fields read
- Is the data there when we need it? Or is it often stale/empty/wrong?
- What data do we WISH was there but isn't?
- Any queries that are ugly, slow, or unreliable because of schema issues?

## 3. WHAT I SHOULD BE DOCUMENTING BUT AM NOT

Think about everything this workspace does -- gap processing, skill building, plugin management, sync operations, manifest refreshes. What activities produce valuable information that currently disappears after the session ends? What would Sentinel, HQ, or CEO briefs benefit from knowing about Skill Hub's work?

For example: when a gap report is processed and a new skill is built, does that resolution get logged to Supabase with enough detail for the evening system report to say "3 gaps resolved today: built X, fixed Y, deployed Z"?

## 4. WHAT I NEED FROM OTHER WORKSPACES

What data from HQ or Sentinel would make Skill Hub's systems work better? For example: does gap processing need to know about HQ's current project priorities to triage severity? Does the marketplace scanner need to know what skills HQ is currently lacking?

## 5. PAIN POINTS

What's frustrating about Supabase right now from this workspace's perspective? Schema problems, missing tables, data that's in the wrong place, queries that don't make sense, things you have to work around?

## 6. AUTONOMY REQUIREMENTS

If this workspace were to operate with ZERO human intervention for a full day -- detecting gaps, building fixes, judging quality, deploying globally, and notifying workspaces -- what Supabase data would it need to read and write? Map out the ideal state for full autonomy.

Also review ~/.claude/docs/supabase-data-flow-tracker.md for any entries logged during Phase 5. Incorporate those observations into your report.
```

---

## Prompt 3: Sentinel

```
Phase 5C is complete. Before we move on to Phase 6, I need you to produce a Supabase Data Relationship Report for this workspace. This is especially important because Sentinel will OWN Phase 6 (Supabase restructure and data governance).

Be brutally honest. If something is broken, half-baked, or you're not sure about it -- say so. This is an audit, not a sales pitch.

Create a file at ~/.claude/docs/phase6-prep/phase6-prep-sentinel.md with the following sections:

## 1. WHAT I WRITE TO SUPABASE

For each table this workspace writes to, document:
- Table name
- What triggers the write (which system, what event)
- Fields written and their format
- Frequency (real-time, daily, on-demand)
- Is the data actually useful? Or are we writing it because we were told to?
- Data quality: is what we're writing clean, complete, and consistent?

## 2. WHAT I READ FROM SUPABASE

For each table this workspace reads from, document:
- Table name
- Which system reads it and why
- Fields read
- Is the data there when we need it? Or is it often stale/empty/wrong?
- What data do we WISH was there but isn't?
- Any queries that are ugly, slow, or unreliable because of schema issues?

## 3. WHAT I SHOULD BE DOCUMENTING BUT AM NOT

Think about everything this workspace does -- morning reports, dream consolidation, doc lifecycle dispatch, repo monitoring, watcher oversight. What activities produce valuable information that currently disappears? What context is lost between sessions?

## 4. WHAT I NEED FROM OTHER WORKSPACES

What data from HQ or Skill Hub would make Sentinel's systems work better? For example: does the morning report need HQ to log project completions in real-time? Does the watcher need Skill Hub to write heartbeats for the gap pipeline?

## 5. PAIN POINTS

What's frustrating about Supabase right now from this workspace's perspective? Schema problems, missing tables, data that's in the wrong place, queries that don't make sense, things you have to work around?

## 6. AUTONOMY REQUIREMENTS

If this workspace were to operate with ZERO human intervention for a full day -- generating reports, consolidating memories, dispatching reviews, monitoring repos, watching watchers -- what Supabase data would it need? Map the ideal state.

## 7. DATA GOVERNANCE VISION (Sentinel Only)

As the future owner of Supabase data governance, describe:
- What does "clean data" look like for this system? Define quality standards.
- How should data contracts work? (who writes what, in what format, how often)
- What audits should run automatically? (stale data, orphaned records, schema drift, missing writes)
- How should violations be handled? (alert Chris? auto-fix? log and batch?)
- What's the minimum viable governance that gets us 80% of the value?

Also review ~/.claude/docs/supabase-data-flow-tracker.md for any entries logged during Phase 5. Incorporate those observations -- you'll need all of this when you build the Phase 6 plan.
```

---

## After All Three Reports Are Done

Open Sentinel and paste this:

```
All three Phase 6 preparation reports are ready:
- ~/.claude/docs/phase6-prep/phase6-prep-hq.md
- ~/.claude/docs/phase6-prep/phase6-prep-skillhub.md
- ~/.claude/docs/phase6-prep/phase6-prep-sentinel.md

Also review the data flow tracker from Phase 5: ~/.claude/docs/supabase-data-flow-tracker.md

Read all four documents. Cross-reference them. Then build the Phase 6 plan:

1. Map the complete data flow: every producer, every consumer, every table, every gap
2. Identify schema changes needed (new tables, merged tables, renamed fields, new indexes)
3. Define data contracts per workspace (who writes what, when, in what format)
4. Design the governance framework (automated audits, quality checks, violation handling)
5. Prioritize: what fixes give us the biggest improvement in data quality and autonomy?
6. Sequence the work: what can be done without breaking running systems?

The goal: Fortune 500-grade data infrastructure that enables full autonomous operation. Every workspace knows exactly what to document, where, and why. Every report pulls clean, complete, real-time data. The brain is structured, governed, and self-auditing.

Save the plan to ~/.claude/plans/ and register it in ~/.claude/docs/plans-registry.md.
```
