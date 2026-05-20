---
status: PHASE_3_COMPLETE
created: 2026-05-17
last_updated: 2026-05-20
last_updated_by: chris+claude
owner: sentinel
co_owners: [skill-management-hub, workforce-hq]
granularity: STRATEGIC (atomic TDD-task decomposition deferred to each Phase's entry gate)
trigger_source: Analysis session 2026-05-17 — sharkitect-solutions/agentmemory + mycelium repo comparison
precursor_plan: 4.- Sentinel/docs/plans/2026-05-08-memory-index-distillation.md (COMPLETE)
related_supabase_project_id: f80eddf0-4aa8-4a9f-971c-794d356ddf25
sequencing: Queued behind Reports Restructure Phase 1 (Sentinel project f8774243) + 2 stale-doc CRITICAL closures
phase_status:
  phase_1: COMPLETE 2026-05-19 (S61) — 1345/1345 embedded
  phase_2: COMPLETE 2026-05-19 (S62) — 87 + 189 + 1572 = 1848 rows shipped + embedded; see docs/plans/2026-05-19-mrl-phase-2-corpus-expansion.md
  phase_3: COMPLETE 2026-05-20 (S64) — search_memories_mrl RPC + tools/mrl-retrieve.py + 5/5 smoke queries PASS + side-effects verified; see 4.- Sentinel/docs/plans/2026-05-20-mrl-phase-3-retrieval-pipeline.md
  phase_4: PENDING — SessionStart augment skill (Skill Hub)
  phase_5: PENDING — decay + signal feedback
  phase_6: PENDING — augment → replace switch (2-week validation gated)
---

# Memory Retrieval Layer (MRL) — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` when executing this plan. **GRANULARITY NOTE:** This is a STRATEGIC plan defining scope + phase boundaries + decisions + risks. It is NOT atomic-task-ready. Atomic TDD task breakdown (writing-plans skill compliant: file paths + test commands + expected output + commit messages per 2-5 minute step) is REQUIRED at each Phase entry gate, AFTER reading the source files listed in "Codebase investigation required at Phase entry" below. Do NOT execute any Phase by following the high-level bullets directly.

**Goal:** Add semantic retrieval over the existing `public.memories` table so each workspace's session start loads top-K relevant memory chunks (~5K tokens) instead of full-file context (~50K tokens of `universal-protocols.md` + CLAUDE.md + MEMORY.md). Target: **5-10x token reduction** with better recall on rules that matter for the current task.

**Architecture:** Extend existing `memory-index-distillation` pipeline (Sentinel-owned, shipped 2026-05-08) with OpenAI `text-embedding-3-large` embeddings on insert, corpus expansion (universal-protocols + lessons-learned + topic files as new `source` values), top-K cosine retrieval tool, SessionStart augment skill (Skill Hub-owned), and nightly decay via dream-consolidation. **Augment-first** for 2 weeks (loads existing context PLUS retrieved chunks — no replacement); **Replace mode** only after retrieval quality is validated.

**Tech Stack:** Python stdlib + Supabase REST patterns (mirror `voice-synthesis.py`); OpenAI `text-embedding-3-large` (3072 dims, $0.13/1M tokens); Postgres + pgvector (`vector(3072)`, cosine via `<=>` operator, no HNSW — exceeds 2000-dim limit, sequential scan is sub-ms at our row count); dream-consolidation phase wiring; Skill Hub SessionStart hook or auto-invoke skill.

**Dependency Order:** Embedder built FIRST (Phase 1 backfills the 467+ unembedded rows). Corpus expansion SECOND (Phase 2 reuses the embedder for new sources). Retrieval tool THIRD (Phase 3 reads embedded corpus). SessionStart skill FOURTH (Phase 4 calls retrieval). Decay FIFTH (Phase 5 maintains corpus health). Replace-mode switch LAST (Phase 6 only after 14-day validation window post Phase 4).

## Codebase investigation required at Phase entry (writing-plans compliance)

Before atomic task breakdown for any phase, the implementer MUST read these files and note conventions, helpers, and patterns to reuse:

| Phase | Required reads |
|---|---|
| Phase 1 (embedder) | `4.- Sentinel/tools/voice-synthesis.py` (Supabase REST helpers + OpenAI client pattern + env loader), `4.- Sentinel/tools/memory-index-distillation.py` (existing distillation flow), `4.- Sentinel/.env` (verify OPENAI_API_KEY present, key scope, rate limits) |
| Phase 2 (corpus) | `4.- Sentinel/tools/memory-index-distillation.py` (chunking, dedup, build_record), `~/.claude/rules/universal-protocols.md` (chunk-boundary heuristics for `##`/`###`), `~/.claude/lessons-learned.md` (entry format), workspace `memory/*.md` topic file conventions |
| Phase 3 (retrieval) | `4.- Sentinel/tools/ops-brain.py` (existing query patterns + result formatting), pgvector docs for `vector_cosine_ops` and `<=>` semantics |
| Phase 4 (SessionStart) | `~/.claude/hooks/session-startup-guard.py` (existing SessionStart hook structure), `~/.claude/skills/` (auto-invoke skill conventions vs hook conventions) |
| Phase 5 (decay) | `4.- Sentinel/tools/dream-consolidation.py` (phase pattern, `run_dream_cycle` integration), existing dream phases for output format consistency |
| Phase 6 (switch) | Telemetry log + 14-day retrieval recall measurements before any action |

---

**Status anchor:** PENDING (awaiting Reports Restructure Phase 1 close)
**Owner:** Sentinel (schema + indexing + decay), Skill Hub (SessionStart hook), HQ (corpus contribution via K1 SoTs)
**Source:** Analysis session 2026-05-17 — comparison of `github.com/sharkitect-solutions/agentmemory` + `github.com/sharkitect-solutions/mycelium` against current memory architecture. Adopt patterns, not codebases.

---

## Goal

Add **semantic retrieval over the existing `public.memories` table** so each workspace's session start loads top-K relevant memory chunks (~5K tokens) instead of full-file context (~50K tokens of `universal-protocols.md` + CLAUDE.md + MEMORY.md). Target: **5-10x token reduction** with better recall on rules that matter for the current task.

**Augment-first, replace-later.** Phase 1-4 ship augment mode (load full context + retrieved chunks). After 2 weeks of validated retrieval quality, flip to replace mode.

---

## Pre-existing landscape (preflight 2026-05-17)

Per Verification-Before-Building, the foundation is largely already built:

| Asset | Status | Owner | What it does |
|---|---|---|---|
| `public.memories` table | **LIVE** (1335 rows, 868 embedded) | Sentinel | Stores memories with `embedding vector(3072)`, `use_count`, `last_accessed`, `decay_days`, `freshness_verified_at`, `active`, `tags` |
| `tools/memory-index-distillation.py` | **LIVE** (Sentinel, shipped 2026-05-08) | Sentinel | Distills MEMORY.md bullets → `memories`. Idempotent SHA-256 keys. Wired into dream-consolidation. **Does NOT embed.** |
| Existing embedded sources | **LIVE** | Various | `local_sync` (345), `seeded` (340), `claude_code` (86), `observation` (77), `directive` (17) — all embedded. Embedding pipeline EXISTS somewhere. |
| The gap | **OPEN** | — | `memory_index_distillation` source has 256 rows with **zero embeddings** (0% coverage). `conversation` source has 198 rows / 1 embedded. |

### What's missing
1. Embeddings not populated for the `memory_index_distillation` source (the highest-value rows — distilled MEMORY.md content).
2. Corpus is too narrow — only MEMORY.md bullets get distilled. `universal-protocols.md` sections, `lessons-learned.md` entries, and workspace `memory/*.md` topic files are NOT in `memories` directly.
3. No retrieval tool (top-K by cosine).
4. No SessionStart integration injecting retrieved chunks.
5. No decay job (`use_count` and `last_accessed` are populated but not acted on for rank/eviction).

---

## Decisions locked (2026-05-17)

| Decision | Locked value | Rationale |
|---|---|---|
| Embedding model | **OpenAI `text-embedding-3-large` (3072 dims)** | Matches existing column dimension. Preserves existing 868 embeddings. No schema change. Cost delta vs `-small` is ~25¢/year on our corpus — negligible. |
| Vendor | OpenAI (already have key) | User-locked 2026-05-17. Anthropic ecosystem alt (Voyage) considered but rejected to avoid new vendor. |
| Mode | Augment-first, replace after 2 weeks | Safety: validate retrieval recall before removing fallback context. |
| Storage | Extend existing `public.memories`, NOT a new table | Schema is already designed for this pattern. Preflight match score 10. |
| Index strategy | Sequential cosine scan (no HNSW) | `vector(3072)` exceeds pgvector's 2000-dim HNSW limit. Sequential cosine on ~1500 rows is sub-millisecond — HNSW is irrelevant at this scale. Revisit if corpus exceeds ~100K rows. |
| BM25 / hybrid retrieval | Defer to v1.1 | Phase 1-4 ship vector-only. Add BM25 + RRF fusion only if retrieval quality is insufficient. KISS. |

---

## Files

| Action | Path | Owner |
|---|---|---|
| Create | `tools/mrl-embed.py` | Sentinel — OpenAI embedder + Supabase upsert |
| Create | `tools/mrl-retrieve.py` | Sentinel — top-K cosine retrieval, updates `use_count` + `last_accessed` |
| Modify | `tools/memory-index-distillation.py` | Sentinel — embed-on-insert + expand corpus sources |
| Modify | `tools/dream-consolidation.py` | Sentinel — add `phase_mrl_decay` |
| Create | `~/.claude/skills/mrl-context-augment/` | Skill Hub — SessionStart skill that calls retrieval |
| Modify | `docs/supabase-schema-index.md` | Sentinel — document new sources |
| Insert | `public.assets` rows | Sentinel — register `mrl-embed`, `mrl-retrieve`, `mrl-context-augment` |

---

## Phases

### Phase 1 — Embedder + backfill (Sentinel, ~1 session)

**Goal:** Close the embedding gap on the 467+ unembedded rows. Establish the OpenAI embedding pipeline that all later phases reuse.

1. Build `tools/mrl-embed.py` — CLI: `embed-rows <source> [--limit N]`, `embed-text "<text>"`, `test`
   - Calls OpenAI `text-embedding-3-large`, dim=3072
   - Reuses `voice-synthesis.py` Supabase REST patterns + env loader
   - Batch size 100 per OpenAI call; 1 row per Supabase UPSERT (transactional)
2. Backfill all 256 `memory_index_distillation` rows + 197 `conversation` rows
3. Verify: `SELECT count(*) FILTER (WHERE embedding IS NULL) FROM memories;` → expected 0 (or near-0, modulo deleted rows)
4. Self-tests: empty text rejection, dimension match assertion, idempotence (re-running doesn't re-embed)
5. Register asset: `script/mrl-embed` (Sentinel-owned)

### Phase 2 — Corpus expansion + embed-on-insert (Sentinel, ~1 session)

**Goal:** Get the high-value rule + lessons + topic-file content INTO `memories` (with embeddings), so retrieval has rich corpus.

1. Extend `tools/memory-index-distillation.py`:
   - New source `universal_protocol_section` — chunk `~/.claude/rules/universal-protocols.md` by `##` and `###` headings; one row per section; section heading goes in `metadata.section_path`
   - New source `lessons_learned_entry` — chunk `~/.claude/lessons-learned.md` by entry; one row per entry; category in `tags`
   - New source `topic_file` — read each workspace's `memory/*.md` topic files directly (not just bullets that link to them); one row per topic file (or per ## heading if file is long)
   - Add `--with-embeddings` flag → calls `mrl-embed.py` after upsert
2. Live run: `python tools/memory-index-distillation.py run --with-embeddings`
3. Expected outcome: ~50-100 new rows for universal-protocols, ~30-80 for lessons-learned, ~20-50 per workspace for topic files. All embedded.
4. Verify: corpus inventory query (rows by source, % embedded)
5. Update `docs/supabase-schema-index.md` with new source values

### Phase 3 — Retrieval pipeline (Sentinel, ~0.5 session)

**Goal:** Top-K cosine retrieval tool that the SessionStart skill calls.

1. Build `tools/mrl-retrieve.py`:
   - CLI: `retrieve "<query text>" [--workspace WS] [--top-k 10] [--token-budget 5000] [--source-filter pattern]`
   - Embeds query via `mrl-embed.py`
   - Cosine search: `SELECT key, content, source, metadata, 1 - (embedding <=> $1::vector) AS sim FROM memories WHERE active = true [+ optional filters] ORDER BY embedding <=> $1::vector LIMIT $top_k * 3`
   - Post-filter by `active = true`, dedupe by content hash, fit to token budget
   - **Side effects on retrieval:** UPDATE `last_accessed = now(), use_count = use_count + 1` for each returned row
   - Output: JSON or text format
2. Self-tests: query embedding cache, deterministic output, token budget enforcement
3. Smoke test 5 queries representative of typical session-start signals:
   - "I'm working on Sentinel Reports Restructure Phase 1" → expect retrieval of plan content, related rules
   - "RLS disabled on supabase tables" → expect retrieval of Supabase Ownership Protocol, RLS-related sections
   - "How do I close an inbox item?" → expect close-inbox-item docs + protocol sections
   - "What's the rule on voice capture?" → expect Continuous Voice & Preference Learning Protocol
   - "How do I write a plan?" → expect Plan Lifecycle Protocol + writing-plans skill ref
4. Register asset: `script/mrl-retrieve` (Sentinel-owned)

### Phase 4 — SessionStart augment skill (Skill Hub, ~1 session)

**Goal:** Inject top-K retrieved chunks into session context at start. Augment mode (load existing context + retrieved chunks).

1. Build skill: `~/.claude/skills/mrl-context-augment/SKILL.md`
   - Description: triggers on session start when current workspace has Sentinel/HQ/Skill Hub MEMORY.md (i.e., AIOS workspaces)
   - Derives query signal from: (a) recent user prompts in conversation history (last 3), (b) workspace name, (c) any active plan path mentioned in MEMORY.md
   - Calls `tools/mrl-retrieve.py` with token budget 5000
   - Returns top-K chunks as `additionalContext` formatted with source path + section heading for citation
2. Wire into a SessionStart hook OR add as auto-invoke skill triggered by startup-guard
3. **Augment mode discipline:** Do NOT remove or shrink existing CLAUDE.md / universal-protocols loading. This phase ADDS top-K, doesn't replace.
4. Telemetry: log retrieval calls to `<tempdir>/mrl-retrieval-log.jsonl` (query, top-K rows, scores, latency, token count)
5. Register asset: `skill/mrl-context-augment` (Skill Hub-owned)

### Phase 5 — Decay + signal feedback (Sentinel, ~0.5 session)

**Goal:** Memory ages out naturally; high-value items rise.

1. Add `phase_mrl_decay` to `dream-consolidation.py`:
   - For each row: compute `effective_score = use_count * exp(-days_since_last_accessed / decay_days)`
   - Below threshold (e.g., effective_score < 0.1 AND last_accessed older than 90 days): set `active = false` (soft delete; never DROP)
   - High-frequency rows surface in dream synthesis output for awareness
2. Add `tools/mrl-stats.py` — CLI surfacing: top-K most-accessed memories, bottom-K decayed, retrieval log summary
3. Verify decay computation against known patterns (stable test fixture)
4. Wire into nightly dream cycle

### Phase 6 — Augment → Replace switch (deferred 2 weeks post-Phase-4)

**Goal:** Once retrieval is proven, replace full-file context loading.

1. Two-week validation window after Phase 4 ships
2. Measure: token consumption deltas, missing-rule incidents (caught by self-audit + brain-dump captures), retrieval recall on representative queries
3. If quality bar met (zero missing-rule incidents in 14 days, retrieval recall ≥ 90% on smoke tests):
   - Modify SessionStart to load TOP-K only (skip universal-protocols.md full load)
   - Keep CLAUDE.md + workspace MEMORY.md as before (small, high-signal anchors)
4. Document the switch as a Pivot Cleanup Protocol-compatible change
5. Roll back trigger: any missing-rule incident → revert to augment mode + investigate retrieval gap

---

## Risks + mitigations

| Risk | Mitigation |
|---|---|
| OpenAI API outage breaks SessionStart | Skill catches retrieval errors and returns empty context; augment mode keeps system functional |
| Retrieval misses a critical rule the AI needs | **Augment-first sequencing**: full context still loads in Phases 1-5. Only Phase 6 introduces replace mode, gated on 2-week validation. |
| `vector(3072)` cosine scan becomes slow at scale | Doesn't matter until ~100K rows. Switch to IVFFlat index then (HNSW unavailable at 3072 dims). |
| Embedding cost spike from frequent dream consolidation runs | Idempotency: `mrl-embed.py` skips rows that already have embeddings unless `--force`. Re-embedding never happens on identical content. |
| `last_accessed` thrash causes UPDATE storms | UPDATE only on retrieval, not on every row touch; batch in retrieval tool |
| User-supplied query is empty or non-sense | `mrl-retrieve.py` validates query length ≥ 5 chars; returns empty result with diagnostic |

---

## Out of scope (deferred)

- BM25 hybrid retrieval + RRF fusion (Tier 1.5 — add if vector-only recall is insufficient)
- Hebbian co-activation graph (Tier 3 from analysis session — unclear ROI vs current cross-reference discipline)
- PostToolUse capture symmetric to voice (Tier 2 from analysis — separate plan after MRL ships)
- Multi-tenant ACL on retrieval results (tenant_id filtering exists in schema; not enforced in Phase 4 skill)
- P2P federation across multiple AIOS clients (mycelium's future direction; not needed for hub-and-spoke)

---

## Cross-references

- Analysis source: 2026-05-17 conversation comparing `agentmemory` + `mycelium` repos
- Precursor plan: `4.- Sentinel/docs/plans/2026-05-08-memory-index-distillation.md` (COMPLETE)
- Existing skill: `~/.claude/skills/agent-memory-systems/` (referenced; design guidance, not direct reuse)
- Schema doc: `4.- Sentinel/docs/supabase-schema-index.md`
- Protocols: Universal Protocols → Supabase Ownership Protocol (read globally, write locally) — MRL retrieval is global read; only Sentinel writes to its rows

---

## Phase entry / exit gates

| Phase | Entry gate | Exit gate |
|---|---|---|
| 1 | Reports Restructure Phase 1 CLOSED + 2 stale-doc CRITICALs RESOLVED | 0 unembedded rows in `memory_index_distillation` + `conversation` sources; self-tests green |
| 2 | Phase 1 exit verified | Universal-protocols + lessons-learned + topic files all ingested; verify corpus growth |
| 3 | Phase 2 exit verified | 5 smoke-test queries return contextually-relevant top-K; self-tests green |
| 4 | Phase 3 exit verified | Skill auto-invokes on AIOS workspace session start; telemetry log populated |
| 5 | Phase 4 exit verified | Decay phase runs cleanly in dream-consolidation; stats tool returns expected ranks |
| 6 | 14 days post Phase 4 + retrieval quality validated | Token consumption reduced 5-10x on representative session profiles |
