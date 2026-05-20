# Sharkitect Digital — Master Plan (Clean Slate)

**Status:** TRANSITIONING — End-of-session housekeeping, then FF proposal
**Last updated:** 2026-03-19

---

## What's Happening RIGHT NOW

### Step 1: End-of-Session Housekeeping (THIS SESSION)
- [ ] Update MEMORY.md — add AIOS Vision Definition as urgent/critical/next-to-do
- [ ] Update MEMORY.md — FF PayLink status: CLIENT AGREED → PROPOSAL PHASE
- [ ] Update session-history.md
- [ ] End-of-session cleanup (resources/incoming/, .tmp/)
- [ ] Supabase sync
- [ ] Deactivate/pause anything that could cause issues during the rebuild freeze

### Step 2: Fantastic Floors PayLink Proposal (NEXT FRESH CHAT)
FF agreed to the PayLink solution. This is revenue — it comes first.
- Pricing: $3,375 setup (25% 2nd project discount), monthly partnership fee TBD
- Blueprint v2.0 already exists with 2 options (A=check distribution, B=distribution+monthly reporting)
- Option C (invoices) TABLED — Chris will provide info later
- Deliverables at `knowledge-base/projects/fantastic-floors-paylink/deliverables/`
- Felix leads per workforce governance
- Must be presentable to FF's CEO
- Timeframe/implementation plan needed

### Step 3: AIOS Vision Definition (AFTER FF PROPOSAL)
Come back to the 12 strategic questions. Do NOT proceed to building until the vision is 100% clear.

**Process:**
- Questions asked ONE AT A TIME — not batched. Each question gets its own discussion.
- Chris answers, asks clarifications, we discuss until that question is fully resolved before moving to the next.
- If a question sparks new questions, those get asked immediately — not deferred.
- After all questions are answered, additional questions may be added if gaps are identified.

**The 12 questions (pending Chris's answers):**

**Group 1 — Your Day-to-Day Reality:**
1. Walk me through a typical day. What actually eats your time?
2. What falls through the cracks? What keeps slipping?
3. What work are you doing that's below CEO-level?

**Group 2 — Client Lifecycle:**
4. How do clients currently come to you? What's the acquisition flow?
5. What happens in the first 30 days with a new client?
6. What does ongoing monthly service actually look like?

**Group 3 — The Ideal Future:**
7. Describe your ideal Tuesday 12 months from now. What are you doing? What are you NOT doing?
8. Solo forever or eventually hiring? How does AIOS fit either path?
9. AIOS as internal tool vs. AIOS as a product you sell — where's the line?

**Group 4 — Trust & Autonomy:**
10. Give me 3 examples of tasks you'd trust an AI to handle without asking you.
11. Give me 3 examples of client communications you'd let AI send without approval.
12. It's 2 AM. Something breaks. What do you want to happen?

**After all questions answered:** Create the Vision Blueprint (5 sections: what AIOS is, what it does, how it thinks, what success looks like, what it needs).

### Step 3.5: Post-Vision Gap Audit (BEFORE ANY PLANNING)
After all questions are answered and the Vision Blueprint is drafted:
- Full audit of every answer, decision, and assumption made during Step 3.
- Identify ANY remaining gaps, ambiguities, or unresolved dependencies.
- If gaps exist: ask additional questions until every gap is closed. No exceptions.
- Validate that the vision is complete enough to build a fully deployable, reliable plan.
- Only proceed to Step 4 when the audit confirms 100% coverage — zero open questions.

### Step 4: Plan the Build FROM SCRATCH (AFTER VISION IS LOCKED AND AUDITED)
No reuse of old plans. No assumptions from prior builds. Fresh architecture, fresh phasing, fresh everything — informed by the clearly defined and fully audited vision from Steps 3 + 3.5. The plan must be fully deployable and reliable — no "we'll figure it out later" items.

---

## What Exists Today (Reference Only — NOT a Build Plan)

These are assets that exist. Whether they stay, get rebuilt, or get scrapped will be decided in Step 4 AFTER the vision is locked. No premature decisions.

**Supabase (shared brain):** 292 memories, 51 KB docs, pgvector, semantic search. Working.
**17 n8n workflows:** All ACTIVE. Standalone Anthropic nodes (no tool-use loop). "Brains without hands."
**Python Telegram bot:** 11 tools, Claude Sonnet 4.6, Supabase sync, gws CLI. Currently ACTIVE.
**Operating rhythm scripts:** Morning/evening briefs, weekly audit, Supabase sync via Task Scheduler.
**16 agent knowledge bases:** ROLE, SKILLS, OPERATIONS, KNOWLEDGE, MEMORY for each agent.
**Builder/monitor scripts:** build_workforce_workflows.py, workforce_monitor.py, agent_factory.py, etc.

---

## Old Plan Status: ARCHIVED

The previous phased build plan (Phase 3.0-3.6: credential checklist → rebuild Alex as AI Agent → add tools → confirmation flow → autonomous ops → fallback switching → cleanup) is **ARCHIVED, NOT ACTIVE**. It was written before Chris called the full stop to re-evaluate from first principles.

That plan will NOT be used. Step 4 creates a new plan from scratch after the vision is defined.

---

## Why This Matters

Chris identified a critical pattern: old plans "set in stone" cause drift. When we discuss and learn new things but an old plan is still sitting there, it pulls us back to assumptions that may no longer be valid. The fix: no plan survives contact with a vision change. Define vision first, plan second, always.
