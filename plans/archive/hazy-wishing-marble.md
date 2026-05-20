# Session 1 Execution Plan — AIOS Restructure (Phases 2-3)

## Context

This is Session 1 of the approved 5-session system restructure. The 16-agent folder model is being eliminated. Claude Code is one agent with many skills. CLAUDE.md needs slimming from 348→~220 lines, and a memory architecture decision document needs to be written.

**Source plan:** `knowledge-base/projects/aios-vision-definition/restructure-retrospective.md`
**Pickup marker when done:** "Session 1 complete. CLAUDE.md slimmed. Memory architecture decided."

---

## Phase 2: Memory Architecture Decision Document (~15 min)

### Research Summary (completed during planning)

**Current state:** Supabase pgvector, ~2K vectors (428 memories + 1,348 kb_docs), OpenAI text-embedding-3-small (1536 dims). Working perfectly.

**AIOS scale target:** 50 clients × ~5K vectors each = ~250K vectors total.

**Finding: Supabase pgvector handles this trivially.** pgvector with pgvectorscale extension supports up to ~50M vectors. 250K is <1% of that capacity. Pinecone only becomes relevant at 5M+ vectors.

**Multi-tenant pattern for AIOS:** Separate Supabase projects per client (strongest isolation, simplest billing, independent scaling). Master AIOS queries across projects via service role keys.

**Decision: Stay with Supabase pgvector. Build abstraction layer. Evaluate Pinecone only at 5M+ vectors.**

### Task 2.1: Write memory-architecture.md

Create `knowledge-base/projects/aios-vision-definition/memory-architecture.md` containing:
- Decision: Supabase pgvector (current + AIOS)
- Three-tier memory model (Hot/Warm/Cold from restructure plan)
- Multi-tenant strategy: separate Supabase projects per client
- Abstraction layer specification (swap-ready interface)
- Scale thresholds: when to evaluate Pinecone (5M+ vectors)
- Cost analysis: current ($25/mo) vs AIOS (50 × $25/mo = $1,250/mo for Supabase, vs Pinecone serverless at ~$500-2,000/mo depending on queries)
- Sources cited from research

**Key files:** NEW `knowledge-base/projects/aios-vision-definition/memory-architecture.md`

---

## Phase 3: Slim CLAUDE.md (348→~220 lines) (~25 min)

### Section-by-section plan

| Section | Lines | Action | Target |
|---------|-------|--------|--------|
| WAT framework intro (1-12) | 12 | SLIM — keep core principle, cut layer details | ~5 |
| Instantiation (14-47) | 34 | **REMOVE** — already done, never runs again | 0 |
| Project Config (50-55) | 6 | REWRITE — remove "16 agents", update purpose | ~5 |
| Workforce Governance (58-207) | **150** | **REMOVE ENTIRELY** — agent model eliminated | 0 |
| How to Operate (210-227) | 18 | KEEP, minor trim | ~15 |
| Task Protocols (230-270) | 41 | KEEP generic, REMOVE project-specific agent items | ~20 |
| Persistent Memory (273-313) | 41 | KEEP — this is platform truth | ~35 |
| Skills Evaluation (316-321) | 6 | KEEP as-is | 6 |
| File Structure (324-335) | 12 | UPDATE — agents/ → _archive/agents/, add skill-specs ref | ~12 |
| Blueprint sections (338-348) | 11 | **REMOVE** — already created | 0 |

**Estimated total: ~98 lines from existing content**

### New sections to ADD

| New Section | Purpose | Target Lines |
|-------------|---------|-------------|
| 5 Non-Negotiables | Replace 12 with 5 enforced rules | ~25 |
| Checkpoint Protocol | Context management across sessions | ~20 |
| Architecture Overview | 3-level model (Claude Code → n8n → Supabase) | ~15 |
| Active Skills list | Updated, no agent references | ~5 |
| Environment summary | Condensed from current | ~15 |

**Estimated new content: ~80 lines**
**Grand total target: ~178-220 lines**

### Task 3.1: Draft new CLAUDE.md

Structure:
1. **Project Purpose** (~5 lines) — What this workspace is, one-agent model
2. **Architecture Overview** (~15 lines) — 3-level model, multi-folder strategy
3. **5 Non-Negotiables** (~25 lines) — Supabase is truth, Checkpoint, Verify, Push back, Change=propagate
4. **How to Operate** (~15 lines) — Tools first, workflows, verify, memory mandatory
5. **Task Protocols** (~20 lines) — Generic pre/post checklists only (no agent-specific items)
6. **Checkpoint Protocol** (~20 lines) — NEW: context management, Supabase state saves
7. **Persistent Memory** (~35 lines) — Kept from current
8. **Skills & Evaluation** (~10 lines) — Active skills list + evaluation trigger
9. **File Structure** (~12 lines) — Updated table
10. **Environment** (~15 lines) — Condensed credentials/integrations reference

### Task 3.2: Verify line count < 250

Count lines after writing. If over 250, identify what to trim further.

### Task 3.3: Verify CLAUDE.md loads clean

Read back the file to confirm no formatting issues, no broken references.

---

## Post-Phase Checklist

- [ ] `memory-architecture.md` written and saved
- [ ] CLAUDE.md slimmed to <250 lines
- [ ] CLAUDE.md loads clean (no truncation, no broken refs)
- [ ] Update MEMORY.md: mark Session 1 progress, update CURRENT WORK section
- [ ] Update Supabase project status (AIOS → active, current_phase = "Session 1 complete")
- [ ] Update session-history.md with Session 1 entry
- [ ] Pickup marker saved: "Session 1 complete. CLAUDE.md slimmed. Memory architecture decided."

---

## Verification

1. Read `knowledge-base/projects/aios-vision-definition/memory-architecture.md` — confirm complete and well-structured
2. Read `CLAUDE.md` — confirm <250 lines, no agent governance, no instantiation, has 5 non-negotiables
3. Read `MEMORY.md` — confirm CURRENT WORK updated with Session 1 completion status
4. Quick Supabase check — confirm project status updated

---

## Key Files Modified

| File | Action |
|------|--------|
| `knowledge-base/projects/aios-vision-definition/memory-architecture.md` | NEW — architecture decision doc |
| `CLAUDE.md` | REWRITE — 348→~220 lines |
| `MEMORY.md` | UPDATE — progress markers |
| `session-history.md` (in memory dir) | UPDATE — Session 1 entry |
