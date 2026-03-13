---
name: agent-memory-systems
description: "Use when designing memory architecture for AI agents or chatbots. Use when choosing between conversation buffer, summary, entity, knowledge graph, or vector store memory types. Use when implementing RAG chunking strategies or retrieval pipelines. Use when debugging agent memory failures — forgetting context, inconsistent answers, or retrieving wrong information. Use when planning memory lifecycle (TTL, consolidation, contradiction handling). NEVER for Claude Code's own MEMORY.md file management — that's a separate system."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Agent Memory Systems

Think like a cognitive architect, not a database engineer. Memory failures look like intelligence failures — when an agent "forgets" or gives inconsistent answers, it's almost always a retrieval problem, not a storage problem.

Before designing any memory system, ask:
- **What must the agent remember?** (facts, relationships, procedures, or conversations?)
- **For how long?** (this session, this user, or forever?)
- **How will it retrieve?** (exact match, semantic similarity, or graph traversal?)
- **What's the cost of forgetting?** (minor annoyance vs. critical failure?)

These four questions determine your entire architecture. Skip them and you'll build the wrong system.

## Memory Type Decision Tree

```
What does the agent need to remember?
│
├─ Recent conversation context (< 20 turns)
│  └─ Conversation Buffer
│     Cost: Linear token growth. Cap at ~10K tokens.
│     Trap: Devs use this as default because it's easy,
│           then wonder why costs explode at scale.
│
├─ Conversation gist across long sessions
│  └─ Conversation Summary Memory
│     Cost: Fixed token budget, but LOSSY.
│     Trap: Summaries silently drop numbers, names, dates.
│     Rule: If precision matters, don't summarize — extract.
│
├─ Facts about specific entities (users, products, topics)
│  └─ Entity Memory
│     Cost: Scales with entity count, not conversation length.
│     Trap: Entity extraction is fragile — "my wife" and "Sarah"
│           must resolve to the same entity. Requires coreference.
│
├─ Relationships between entities
│  └─ Knowledge Graph Memory
│     Cost: Most complex to build and query.
│     When: Relationships matter MORE than raw facts.
│     Example: "Who reported to whom during Q3?" requires graph.
│     Trap: Graph queries are hard to write correctly. Test early.
│
└─ Large knowledge base (docs, FAQs, manuals)
   └─ Vector Store (RAG)
      Cost: Scales well for storage, but retrieval quality varies wildly.
      When: More than ~50 pages of reference material.
      Trap: Chunking determines 80% of retrieval quality.
            Bad chunks = bad answers, regardless of model quality.
```

**Hybrid is the norm.** Production agents typically combine 2-3 types: conversation buffer for immediate context + entity memory for user facts + vector store for knowledge base.

## Chunking Strategies — Where Most Memory Systems Fail

Chunking is the single highest-leverage decision in any RAG system. The difference between good and bad chunking is 40-60% retrieval accuracy.

| Strategy | When to Use | When It Fails |
|----------|-------------|---------------|
| **Fixed-size (512 tokens)** | Uniform content (API docs, glossaries) | Breaks mid-thought on narrative content |
| **Recursive splitting** | Code, structured documents | Still syntactic — misses semantic boundaries |
| **Semantic chunking** | Long-form content, articles, manuals | 3x slower to index; embedding quality dependent |
| **Contextual chunking** | High-stakes retrieval where accuracy matters | Increases storage 20-30% (each chunk gets context prepended) |
| **Agentic chunking** | High-value, low-volume content (contracts, policies) | Expensive — LLM call per boundary decision |

### Contextual Chunking — The Expert Move

Prepend a 1-2 sentence context summary to each chunk before embedding:

```
Without context: "The fee is 2.5% per transaction."
With context: "From the Stripe pricing page, merchant processing section: The fee is 2.5% per transaction."
```

This costs 20-30% more storage but dramatically improves retrieval because the embedding captures WHERE the information lives, not just WHAT it says. Always use this for production systems.

### Chunk Overlap Rule

Overlap chunks by 10-20% of chunk size. Without overlap, answers that span chunk boundaries become invisible to retrieval. This is the #1 cause of "the answer is in the docs but the agent can't find it."

## Retrieval Failure Modes

When an agent gives wrong or incomplete answers despite having the right information stored, diagnose with this hierarchy:

1. **Wrong chunks retrieved** — Query doesn't semantically match stored content. Fix: hybrid search (vector + keyword). Hybrid search improves retrieval by 30-50% over vector-only.

2. **Right chunk, split answer** — The answer spans two chunks. Fix: increase chunk overlap to 20%. Check: do retrieved chunks end mid-sentence?

3. **Semantic drift** — Query wording diverges from stored wording ("cancel subscription" vs "terminate account"). Fix: query expansion — generate 3-5 rephrasings, retrieve for each, merge results.

4. **Recency bias** — Recent memories dominate older but more relevant ones. Fix: temporal decay function. Recent memories get a boost but it decays over days/weeks.

5. **Embedding model mismatch** — Changed embedding models without re-indexing. ALL existing vectors are now in a different semantic space. There is no fix except full re-indexing.

## Memory Lifecycle Management

### What to Forget

Not all memories should live forever. Implement TTL (time-to-live) tiers:

| Memory Type | TTL | Why |
|-------------|-----|-----|
| Session context | End of session | Noise if kept — corrections, tangents, filler |
| Task-specific facts | 24-72 hours | Relevant only to the active task |
| User preferences | 30-90 days | Preferences change; stale ones cause friction |
| Domain knowledge | Permanent (with version) | Core knowledge base; version to handle updates |

### Handling Contradictions

When new information contradicts stored memory:
1. **Don't silently overwrite.** Flag the conflict.
2. **Timestamp both.** Later information is usually more accurate.
3. **Keep both with confidence scores** if unsure which is correct.
4. **Ask the user** in high-stakes domains (medical, legal, financial).

### Memory Consolidation

Periodically (daily or weekly), consolidate granular memories into higher-level summaries:
- 50 individual "user asked about X" entries → "User is actively learning Python, focus areas: async, testing, deployment"
- This reduces retrieval noise and improves semantic matching for broad queries.

## Rationalization Table

| Rationalization | When It Appears | Why It's Wrong |
|----------------|-----------------|----------------|
| "Just use a vector store for everything" | Starting a new agent project | Vector stores are terrible for structured facts, entity relationships, and session context. Match memory type to data type. |
| "We'll optimize chunking later" | MVP/prototype phase | Chunking determines 80% of retrieval quality. Bad chunks in production poison every answer. Get it right early. |
| "Bigger chunks = more context" | Choosing chunk size | Bigger chunks reduce retrieval precision. The embedding represents the average of the chunk — large chunks average out to generic vectors. |
| "The embedding model doesn't matter that much" | Selecting infrastructure | Domain-specific embeddings outperform general-purpose by 20-40% on domain queries. This compounds across every retrieval. |
| "We can switch embedding models later" | Architecture decisions | Switching requires full re-indexing of every stored vector. On large datasets this is days of compute. Choose carefully upfront. |

## Red Flags

- [ ] Agent stores raw conversation turns as memory — too much noise (corrections, filler, tangents). Extract structured facts instead.
- [ ] Using cosine similarity alone for retrieval — always combine with keyword/BM25 search (hybrid) for 30-50% better results.
- [ ] No metadata on stored memories — without timestamps, source, confidence scores, you can't filter, rank, or debug.
- [ ] Same embedding model for all content types — code, prose, and structured data need different treatment.
- [ ] No chunk overlap — answers spanning boundaries become invisible to retrieval.
- [ ] Memory system has no way to forget — unbounded growth degrades retrieval quality over time.

## NEVER

- NEVER change embedding models without planning full re-indexing — old and new vectors live in incompatible semantic spaces, retrieval silently degrades to near-random
- NEVER store memories without timestamps — you lose the ability to handle contradictions, apply recency weighting, or implement TTL
- NEVER use chunk sizes > 1024 tokens for retrieval — large chunks produce generic embeddings that match too many queries loosely instead of the right query precisely
- NEVER skip hybrid search (vector + keyword) in production — pure vector search misses exact matches that keyword search catches trivially ("error code 4502")
- NEVER assume entity extraction is solved — coreference resolution ("she", "the client", "Mrs. Chen") is still fragile; test with real conversations, not clean examples
- NEVER build memory without a retrieval test suite — if you can't measure retrieval accuracy, you can't improve it

## Implementation Checklist

When building a new agent memory system:
1. Answer the four architecture questions (what, how long, how retrieve, cost of forgetting)
2. Select memory types from the decision tree — plan for hybrid if more than one data type
3. Choose chunking strategy — default to semantic + contextual for prose, recursive for code
4. Set chunk overlap to 15% minimum
5. Implement hybrid search (vector + BM25) from day one
6. Add metadata to every stored memory (timestamp, source, confidence, type)
7. Define TTL tiers and implement automated cleanup
8. Build a retrieval test suite with 20+ queries before going to production
9. Monitor retrieval accuracy weekly — it degrades as the memory grows
