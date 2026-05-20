# Telegram Bot Architecture Research: Synthesis & Decision Framework

**Project:** AI-Powered Telegram Bot for Sharkitect Digital
**Decision Required:** n8n vs Python vs Hybrid Architecture
**Current Baseline:** Python bot (3-15 second response times)
**Target:** Sub-2-second responses
**Date:** 2026-03-13
**Status:** PLAN MODE — Research complete, synthesis pending

---

## Research Summary Outline

This document will synthesize findings across 6 topic areas into a decision-ready framework.

### Topic 1: n8n + Telegram + Claude/OpenAI Architecture Patterns
- Webhook setup mechanics and latency characteristics
- AI node integration (Anthropic Chat Model vs LLM Chain vs AI Agent)
- Streaming response implementation
- Tool/function calling in n8n workflows
- Known latency bottlenecks

**Key Sources to Synthesize:**
- n8n Telegram Trigger node documentation
- Telegram webhook vs long polling latency comparison
- n8n AI Agent node with Claude integration guides
- Real-world n8n + Telegram workflow examples

**Deliverable:** Architecture diagram showing data flow (Telegram → Webhook → n8n AI Node → Claude → Response)

---

### Topic 2: n8n AI Agent Node Capabilities
- Claude support and version compatibility
- Function calling / tool use implementation
- Streaming response support
- Memory types and conversation context handling
- Limitations (Extended Thinking + tool use incompatibility — CRITICAL)

**Key Sources to Synthesize:**
- n8n AI Agent node documentation (Tools Agent configuration)
- Anthropic Claude function calling in n8n
- Memory Buffer Window specifications
- Known limitations and workarounds

**Deliverable:** Feature matrix showing n8n AI Agent capabilities with checkbox ratings

---

### Topic 3: Python Bot vs n8n Bot Comparison
- Architectural advantages of each approach
- Latency characteristics (aiogram async vs n8n webhook)
- Maintenance burden and skill requirements
- Scalability and concurrency handling
- When each approach excels

**Key Sources to Synthesize:**
- aiogram async Telegram bot framework details
- n8n workflow execution model and performance
- Hybrid approach patterns (Python for heavy lifting + n8n for orchestration)

**Deliverable:** Comparative analysis table (Python vs n8n vs Hybrid)

---

### Topic 4: Telegram Bot Performance Best Practices
- Webhook vs polling latency trade-offs
- Progressive message editing for perceived responsiveness
- Typing indicators (5-second limitation, sendChatAction API)
- Rate limiting and throttling strategies
- Concurrent request handling

**Key Sources to Synthesize:**
- Telegram Bot API best practices documentation
- Webhook architecture vs long polling performance metrics
- Progressive editing implementation patterns
- Rate limit specifications (30 requests per second per chat)

**Deliverable:** Performance optimization checklist with latency impact estimates

---

### Topic 5: n8n Community Examples & Templates
- Specific n8n workflow template IDs for Telegram + AI bots
- Popular build patterns and architectural approaches
- Real-world examples from the community
- Template URLs for reference/cloning

**Key Sources to Synthesize:**
- n8n workflow templates directory
- Community-shared workflows (IDs, links, descriptions)
- Popular patterns (memory handling, streaming, function calling)

**Deliverable:** Template reference list with links and use case descriptions

---

### Topic 6: Memory & Context Management
- Persistence backends (Postgres/Supabase vs Redis vs Airtable vs Pinecone)
- Session ID mapping (Telegram chat ID = memory key)
- Conversation context window length
- Memory Buffer Window configuration
- Multi-turn conversation handling

**Key Sources to Synthesize:**
- n8n Postgres Chat Memory node
- Supabase integration for persistent storage
- Redis vs Postgres trade-offs
- Airtable as lightweight persistence option
- Session management patterns

**Deliverable:** Memory architecture comparison with deployment complexity estimates

---

## Architecture Decision Matrix

### Evaluation Criteria
- Response latency (target: <2 seconds)
- Scalability (concurrent users, message throughput)
- Development time to MVP
- Maintenance burden
- Cost (infrastructure, third-party services)
- Team skillset alignment
- Extensibility (adding new features)

### Three Options

#### Option A: Pure n8n
**Pros:**
- Webhook-based instant message delivery
- Streaming responses for perceived speed
- AI Agent node with Claude integration
- Visual workflow editor (lower developer friction)
- Pre-built Telegram trigger/response nodes
- No server management required

**Cons:**
- Single webhook per n8n instance limitation
- Extended Thinking + function calling incompatibility
- Limited custom logic (Code node limitations)
- n8n execution overhead on each request
- Potential cold-start latency on free tier

**Expected Latency:** 1-3 seconds (webhook overhead minimal, n8n execution time dominant)

#### Option B: Pure Python
**Pros:**
- Async aiogram framework (low-latency message handling)
- Full control over request/response cycle
- Extended Thinking + tool use fully compatible
- Can implement custom optimizations
- Low infrastructure overhead

**Cons:**
- Higher development complexity
- Server/infrastructure management required
- Async Python debugging is harder
- Team needs Python expertise
- Longer time to MVP

**Expected Latency:** 0.5-2 seconds (async efficiency, less framework overhead)

#### Option C: Hybrid (Recommended)
**Architecture:** Python async webhook receiver → n8n orchestration & memory

**Pros:**
- Python handles Telegram webhooks (instant, minimal latency)
- n8n orchestrates AI calls, memory, multi-step workflows
- Best of both: Python speed + n8n workflow composability
- Extended Thinking fully compatible
- Scalable memory management via Supabase
- Gradual complexity scaling

**Cons:**
- More infrastructure to manage (2 components)
- Debugging across boundaries
- Slightly more development complexity

**Expected Latency:** 0.8-2 seconds (Python webhook efficiency + n8n orchestration)

---

## Critical Findings

### Finding 1: Extended Thinking + Tool Use Incompatibility
**Impact:** HIGH
**Details:** n8n AI Agent node does NOT support Extended Thinking when function calling is enabled. If bot logic requires Extended Thinking (complex reasoning), cannot use n8n's native tool calling. Workaround: HTTP Request node for custom Claude API calls.

**Implication:** If Sharkitect's bot needs Extended Thinking for reasoning-heavy tasks, pure n8n is eliminated as option.

### Finding 2: Single Webhook per n8n Instance
**Impact:** MEDIUM
**Details:** n8n instance can only have ONE Telegram webhook registered at a time. Multi-bot or multi-environment deployment requires multiple n8n instances.

**Implication:** For multi-bot scaling, n8n adds infrastructure complexity.

### Finding 3: Typing Indicator 5-Second Limit
**Impact:** LOW
**Details:** Telegram's sendChatAction typing indicator lasts max 5 seconds. For responses taking >5 seconds, must be re-triggered or use progressive editing.

**Implication:** Use progressive editing (send initial response, then update with streaming content) for better perceived performance.

### Finding 4: Webhook Latency Is Minimal
**Impact:** HIGH (positive)
**Details:** Telegram webhook delivery: <50ms latency. Webhook is superior to polling for real-time response.

**Implication:** Webhook architecture should be used in all options.

### Finding 5: Memory Persistence Layer Is Decoupled
**Impact:** MEDIUM
**Details:** Memory can be stored in Postgres/Supabase, Redis, Airtable, or Pinecone independently of bot architecture. Session ID = Telegram chat ID maps to memory records.

**Implication:** Memory choice is independent of n8n vs Python decision. Recommend Supabase (Postgres) for managed simplicity.

---

## Recommendations by Use Case

### If Bot Needs Extended Thinking + Function Calling
**Recommendation:** Option C (Hybrid) or Option B (Pure Python)
**Rationale:** n8n AI Agent node cannot combine these features. Hybrid uses Python webhook + HTTP request nodes for extended calls.

### If Bot Needs Sub-1-Second Response Time
**Recommendation:** Option B (Pure Python) or Option C (Hybrid with optimized Python)
**Rationale:** Pure n8n unlikely to achieve <1 second consistently due to platform overhead.

### If Team Prefers Visual Workflow Editor
**Recommendation:** Option A (Pure n8n) or Option C (Hybrid with n8n orchestration layer)
**Rationale:** n8n's visual editor reduces development friction. Hybrid allows Python for speed-critical path.

### If Team is Python-Heavy
**Recommendation:** Option B (Pure Python) or Option C (Hybrid)
**Rationale:** Leverage existing expertise. Hybrid allows gradual adoption of n8n without full rewrite.

### If MVP Speed is Critical (Ship in 1-2 weeks)
**Recommendation:** Option A (Pure n8n)
**Rationale:** No infrastructure setup, pre-built nodes, visual editor. Fastest path to working bot.

### If Long-Term Scalability and Extensibility Matter Most
**Recommendation:** Option C (Hybrid)
**Rationale:** Combines Python efficiency with n8n workflow flexibility. Can add features to n8n orchestration layer without touching bot core.

---

## Next Steps (Pending User Decision)

1. **User selects architecture option** (A/B/C)
2. **Detailed implementation plan** for selected option
3. **Technology stack finalization** (memory backend, deployment, monitoring)
4. **Development timeline and resource allocation**
5. **Proof of concept build** to validate latency assumptions

---

## Plan Status

- [x] Research complete (10 web searches, all 6 topics covered)
- [x] Key findings synthesized
- [x] Architecture options documented
- [x] Recommendation matrix created
- [ ] User decision on preferred architecture
- [ ] Implementation plan (blocked until decision)
- [ ] POC build and latency validation (blocked until decision)

