# Plan: HQ Restructure Deliverables — Analysis & Build

## Context

The HQ workspace completed a major restructure eliminating a 16-agent folder model and replacing it with "one agent, many skills." This produced: 5 hook specifications, 2 prototype hook scripts, 16 skill specs, and architecture decision documents. This plan analyzes those deliverables against our existing 138 skills + 48 agents + 44 plugins and defines what actually needs building.

**Architecture principle confirmed in discussion:** Every skill should be paired with sub-agent(s) via the Task tool. Skills contain decision frameworks and routing rules that the main agent follows. Sub-agents do the actual execution work. Skills can't call sub-agents directly — the main agent reads the skill, decides which sub-agents to launch, and synthesizes results.

---

## Phase 1: Hooks (5 hooks — 3 global, 2 project-local)

### Hook Architecture Decisions

**Prototype scripts have 3 bugs to fix:**
1. Wrong event: PostToolUse (too late) → should be PreToolUse (block before edit)
2. `jq` dependency → use Python (stdlib only, matching all other custom scripts)
3. Line count timing: PreToolUse checks CURRENT file state — blocks edits when already at/over limit

**Format: Settings.json hooks (not plugin hooks)**
- Global hooks → `~/.claude/settings.json` + scripts in `~/.claude/hooks/`
- Project-local hooks → HQ workspace `.claude/settings.json` + scripts in HQ `tools/hooks/`
- Rationale: Plugin format requires `${CLAUDE_PLUGIN_ROOT}` and plugin installation. Settings hooks are simpler for standalone enforcement rules.

### Hook 1: MEMORY.md Line Count Enforcer (GLOBAL)
- **Event:** PreToolUse | **Matcher:** `Edit|Write`
- **Script:** `~/.claude/hooks/check-line-count.py` (shared with Hook 2)
- **Logic:** Parse stdin JSON → check `tool_input.file_path` → if matches `*MEMORY.md` and file ≥150 lines → exit 2 (deny) with message
- **Exit codes:** 0=allow, 2=deny (per Claude Code hook spec)

### Hook 2: CLAUDE.md Line Count Enforcer (GLOBAL)
- Same script as Hook 1, parameterized: `*CLAUDE.md` → 250 line limit
- Single Python script handles both via filename detection

### Hook 3: Checkpoint Reminder (GLOBAL)
- **Event:** PostToolUse | **Matcher:** `Edit|Write`
- **Script:** `~/.claude/hooks/checkpoint-reminder.py`
- **Logic:** Track Edit/Write calls in temp counter file → if ≥3 non-MEMORY.md edits since last MEMORY.md edit → stdout reminder → reset counter
- **State file:** `~/.claude/.tmp/.checkpoint-counter` (survives across tool calls within session)
- Non-blocking (exit 0 always, message via stdout)

### Hook 4: Incoming File Age Warning (HQ PROJECT-LOCAL)
- **Event:** PreToolUse | **Matcher:** `Read`
- **Script:** HQ `tools/hooks/file-age-warning.py`
- **Logic:** If path contains `resources/incoming/` and file mtime >2 days → stdout warning
- Non-blocking (exit 0 always)

### Hook 5: Agent Folder Access Blocker (HQ PROJECT-LOCAL)
- **Event:** PreToolUse | **Matcher:** `Edit|Write`
- **Script:** HQ `tools/hooks/agent-folder-blocker.py`
- **Logic:** If path matches `*/agents/*` AND NOT `*_archive/agents/*` → exit 2 (deny)

### Build Order
1. Write `~/.claude/hooks/check-line-count.py` (hooks 1+2)
2. Write `~/.claude/hooks/checkpoint-reminder.py` (hook 3)
3. Write HQ `tools/hooks/file-age-warning.py` (hook 4)
4. Write HQ `tools/hooks/agent-folder-blocker.py` (hook 5)
5. Back up `~/.claude/settings.json` → add global `hooks` section
6. Update HQ `.claude/settings.json` with project-local hooks (fix existing PostToolUse → PreToolUse)
7. Test all 5 hooks

### Critical Implementation Notes
- Windows paths: use `normalize_path()` (replace `\\` with `/`) — pattern from quality-gate.py
- stdin JSON format for PreToolUse: `{"tool_name": "Edit", "tool_input": {"file_path": "...", "old_string": "...", "new_string": "..."}}`
- PreToolUse exit 2 = deny with stderr message shown to model
- PostToolUse exit 0 always, stdout message injected into conversation
- Hooks loaded at session start ONLY — editing mid-session has no effect

---

## Phase 2: Skill + Agent Pairing Analysis

### How Skills and Agents Work Together

```
User request → Main agent reads SKILL instructions
                → Skill routing rules say "launch agent X, Y, Z"
                → Main agent launches sub-agents via Task tool
                → Sub-agents execute (isolated context, own tools)
                → Results return to main agent
                → Main agent synthesizes using skill's format
```

Skills define WHAT to do and HOW to combine results. Agents DO the work. Every skill must explicitly name which agents it pairs with in its description and routing logic.

### Skill-to-Agent Pairing Map

| Skill | Paired Existing Agents | Gap Agent Needed? | Gap Description |
|-------|----------------------|-------------------|-----------------|
| **hq-orchestrator** (Marcus) | ALL 48 agents (router) | No | Marcus IS the routing logic — it directs to existing agents |
| **hq-tech-strategy** (Orion) | `ai-systems-architect`, `backend-architect`, `devops-engineer`, `mcp-server-architect` | No | MVA/security tiering is decision framework; execution goes to existing agents |
| **hq-knowledge-governance** (Sage) | `research-synthesizer` (closest) | **YES** | Nothing does KB auditing, K1-K5 classification, cross-reference integrity, governance compliance |
| **hq-brand-review** (Vera) | `communication-excellence-coach`, `content-strategist` | **YES** | Existing agents do tone/communication, not brand drift detection, banned terms, visual consistency, 6-step brand review protocol |
| **hq-revenue-ops** (Felix) | `sales-researcher`, `customer-success-manager`, `financial-analyst` | No | Strong existing coverage. Companion file adds Sharkitect client tiering. |
| **hq-operations** (Atlas) | `business-analyst`, `project-manager`, `scrum-master` | No | Strong existing coverage. Companion file adds SOP 10-field template. |
| **hq-strategic-ops** (Axiom) | `competitive-intelligence-analyst`, `market-research-analyst` | No | Existing agents do market research. Companion file adds architectural debt framework + 10 activation conditions. |
| **Echo** (Reverse Engineering) | `search-specialist`, `competitive-intelligence-analyst` (support) | **YES** | Nothing does structured reverse engineering from vague sources (YouTube, tutorials, competitor demos), confidence-level scoring, intelligence report generation |
| **smb-cfo** (Sterling) | `financial-analyst` | No | Already paired. Add Sharkitect pricing companion file. |
| **marketing-strategy-pmm** (Cleo) | `marketing-strategist`, `content-strategist` | No | Already paired. Add Sharkitect ICP companion file. |
| **contract-legal** (Lex) | `legal-advisor` | No | Already paired. Add Sharkitect risk framework companion file. |

### New Agents to Build (3)

**Agent 1: `knowledge-governance.md`** (pairs with Sage skill)
- Domain: KB auditing, document classification, cross-reference integrity, governance compliance
- Tools: Read, Glob, Grep, Bash (for file analysis), WebFetch (for Supabase queries)
- Novel capabilities: K1-K5 classification engine, freshness scoring, orphan detection, conflict identification
- Model: sonnet (read-heavy analysis, doesn't need opus)

**Agent 2: `brand-reviewer.md`** (pairs with Vera skill)
- Domain: Brand voice enforcement, drift detection, banned term checking, visual consistency assessment
- Tools: Read, Glob, Grep (content analysis focused)
- Novel capabilities: 6-step brand review protocol, brand drift scoring, determination system (Brand-Clear / Aligned with Notes / Revision Required / Escalation Required)
- Model: sonnet (content analysis, doesn't need opus)

**Agent 3: `reverse-engineer.md`** (Echo)
- Domain: System deconstruction, competitive intelligence extraction, confidence-level assessment
- Tools: Read, Glob, Grep, WebSearch, WebFetch (Firecrawl for deep scraping)
- Novel capabilities: Takes vague/unstructured input (video transcripts, tutorials, competitor demos) → extracts architectural patterns → produces structured intelligence reports with fact-vs-hypothesis scoring → feeds into blueprinting/planning workflows
- Model: opus (complex reasoning required for reverse engineering from vague sources)
- Paired skill: `hq-reverse-engineering` (defines when to invoke Echo, output format, how to feed results to other agents)

### Updated Build Summary

| Category | Count | Items |
|----------|-------|-------|
| **FULL Skills** (SKILL.md + 3 companions) | 3 | hq-orchestrator, hq-knowledge-governance, hq-tech-strategy |
| **FULL Skill + Paired Agent** | 1 | hq-reverse-engineering skill + reverse-engineer.md agent (Echo) |
| **THIN Skills** (SKILL.md + 1-2 companions) | 4 | hq-brand-review, hq-revenue-ops, hq-operations, hq-strategic-ops |
| **New Agents** (paired with skills) | 3 | knowledge-governance, brand-reviewer, reverse-engineer |
| **Companion Files** (additions to existing skills) | 3 | smb-cfo, marketing-strategy-pmm, contract-legal |
| **SKIP** | 5 | Node (n8n), Vantage (n8n), Quill (covered), Scout (HQ plans), Alex (n8n) |
| **TOTAL NEW BUILDS** | 8 skills + 3 agents + 3 companion files |

---

## Phase 3: Build Hooks

Build all 5 hooks first — they're independent of skills and provide immediate enforcement value.

1. Write `~/.claude/hooks/check-line-count.py` (hooks 1+2)
2. Write `~/.claude/hooks/checkpoint-reminder.py` (hook 3)
3. Write HQ `tools/hooks/file-age-warning.py` (hook 4)
4. Write HQ `tools/hooks/agent-folder-blocker.py` (hook 5)
5. Back up + update global `~/.claude/settings.json`
6. Update HQ `.claude/settings.json`
7. Test all 5 (restart session required since hooks load at session start)

---

## Phase 4: Build Skills + Agents

### Wave 1 — Full Skills with Agent Pairing (use `ultimate-skill-creator`)

**4a. hq-orchestrator (Marcus) — SKILL only**
- SKILL.md: Routing decision tree, department classification, synthesis rules
- `references/routing-rules.md`: Request type → skill/agent routing table (maps to all 48+ agents)
- `references/synthesis-format.md`: Multi-skill output aggregation format
- `references/department-taxonomy.md`: Department classification with activation conditions
- Agent pairing: Routes to ALL existing agents — no dedicated agent needed

**4b. hq-knowledge-governance (Sage) — SKILL + NEW AGENT**
- SKILL.md: K1-K5 classification rules, governance compliance, audit triggers
- `references/k-classification.md`: K1-K5 taxonomy with examples
- `references/governance-protocol.md`: Compliance checks, review cadences
- `references/audit-methodology.md`: Knowledge audit process, freshness scoring
- **NEW AGENT:** `knowledge-governance.md` — executes KB audits, classification, integrity checks

**4c. hq-tech-strategy (Orion) — SKILL only**
- SKILL.md: MVA decision framework, security tiering, delegation protocol
- `references/mva-methodology.md`: MVA evaluation criteria, build vs buy
- `references/security-tiers.md`: Tier 0-3 definitions
- `references/tech-stack.md`: Sharkitect infrastructure map
- Agent pairing: `ai-systems-architect`, `backend-architect`, `devops-engineer`, `mcp-server-architect`

**4d. hq-reverse-engineering (Echo) — SKILL + NEW AGENT**
- SKILL.md: When to invoke Echo, input types accepted, output format, downstream routing
- `references/analysis-framework.md`: Structural deconstruction methodology, confidence scoring
- `references/intelligence-template.md`: Output report format (findings, confidence levels, recommendations)
- `references/downstream-routing.md`: How Echo output feeds into Vantage (blueprinting) and other workflows
- **NEW AGENT:** `reverse-engineer.md` — accepts vague input, does deep research, produces structured intelligence

### Wave 2 — Thin Skills with Agent Pairing

**4e. hq-brand-review (Vera) — SKILL + NEW AGENT**
- SKILL.md: Brand voice profile, banned terms, 6-step review protocol, drift detection
- `references/brand-guide.md`: Sharkitect voice characteristics, tone rules, examples
- **NEW AGENT:** `brand-reviewer.md` — executes 6-step brand review, drift scoring
- Also pairs with: `communication-excellence-coach` (tone), `content-strategist` (messaging)

**4f. hq-revenue-ops (Felix) — SKILL only**
- SKILL.md: Client tiering framework, deal governance, pricing validation with Sterling sign-off
- `references/client-tiers.md`: Tier definitions, pricing guardrails, escalation rules
- Agent pairing: `sales-researcher`, `customer-success-manager`, `financial-analyst`

**4g. hq-operations (Atlas) — SKILL only**
- SKILL.md: SOP 10-field template, drift detection, capacity state framework
- `references/sop-template.md`: 10-field SOP format with examples, capacity states
- Agent pairing: `business-analyst`, `project-manager`, `scrum-master`

**4h. hq-strategic-ops (Axiom) — SKILL only**
- SKILL.md: Architectural debt framework, 10 activation conditions, enterprise structural diagnosis
- `references/debt-framework.md`: Debt categories (visible/hidden/accelerating), scoring, remediation
- Agent pairing: `competitive-intelligence-analyst`, `market-research-analyst`, `research-synthesizer`

### Wave 3 — Companion File Additions to Existing Skills

**4i.** `smb-cfo/references/sharkitect-pricing-model.md` — deal economics, margin targets, pricing guardrails
**4j.** `marketing-strategy-pmm/references/sharkitect-icp.md` — ICP profiles, channel priorities, pipeline targets
**4k.** `contract-legal/references/sharkitect-risk-framework.md` — 12-category risk scoring, DRAFT label protocol

### Quality Gate
- Every new skill scored via `/skill-judge` — must pass B gate (96+/120)
- Every new agent scored via `/agent-judge` — must pass B gate (96+/120)
- Optimize using proven recipes if needed (decision trees, anti-patterns, cross-domain D1 boosters)

---

## Phase 5: De-confliction

### Trigger Precision
Every new `hq-*` skill MUST have:
1. Tight trigger description (specific Sharkitect business contexts, not generic)
2. Explicit exclusions naming the generic skills/agents it overlaps with
3. Clear "DO NOT use for" section listing what the generic tools handle

### Agent De-confliction
The 3 new agents must specify:
- What distinguishes them from similar existing agents
- Explicit "Do NOT use for" listing adjacent agent capabilities
- Tool least-privilege (only tools they actually need)

---

## Phase 6: AIOS Client Industry Planning (FUTURE — document only, don't build)

### Universal Skills (work for ANY AIOS client)
These skills are business-agnostic and would work for any company using the AIOS platform:
- **hq-orchestrator** → rename to `aios-orchestrator` for clients (routing logic is universal, routing RULES are per-client)
- **hq-knowledge-governance** → `aios-knowledge-governance` (K1-K5 classification works everywhere)
- **hq-operations** → `aios-operations` (SOP template, drift detection are universal)
- **hq-brand-review** → `aios-brand-review` (brand guide is per-client, review PROTOCOL is universal)
- **smb-cfo** (already generic) + companion file per client
- **contract-legal** (already generic) + companion file per client

### Industry-Specific Skills Needed (future builds)

| Industry | Unique Needs | Potential Skills/Agents |
|----------|-------------|------------------------|
| **HVAC** | Job scheduling, seasonal demand, equipment tracking, warranty mgmt | `industry-hvac-ops` skill, pairs with `project-manager` agent |
| **Construction** | Project phasing, permit tracking, subcontractor mgmt, materials procurement | `industry-construction-ops` skill, pairs with `project-manager` + `scrum-master` agents |
| **Plumbing/Electrical** | Emergency dispatch, parts inventory, certification tracking, compliance | `industry-trade-ops` skill, pairs with `business-analyst` agent |
| **Remodeling** | Design consultation, material estimation, timeline management, change orders | `industry-remodel-ops` skill, pairs with `project-manager` agent |
| **Hair Salons/Spas** | Appointment booking, stylist scheduling, product inventory, client retention | `industry-beauty-ops` skill, pairs with `customer-success-manager` agent |

### Implementation Pattern
For each industry, the pattern is:
1. **Same agents** — the 48+ agents are universal capabilities
2. **Same core skills** — orchestrator, knowledge governance, operations, brand review
3. **Different companion files** — industry-specific pricing, terminology, compliance rules, SOPs
4. **Possible new skills** — industry-specific workflows (e.g., permit tracking, appointment scheduling)

### Deliverable
Write `knowledge-base/projects/aios-vision-definition/industry-skill-roadmap.md` documenting this analysis. NOT a build task — a reference document for when AIOS client onboarding begins.

---

## Phase 7: Sync & Memory

1. Score all 8 new skills via `/skill-judge` (B gate: 96+/120)
2. Score all 3 new agents via `/agent-judge` (B gate: 96+/120)
3. Run de-confliction checks against existing 48 agents + 138 skills
4. Sync to GitHub: `python tools/sync-skills.py --sync --push`
5. Update this workspace's MEMORY.md
6. Update HQ workspace MEMORY.md (hooks now configured, restructure deliverables processed)
7. Write `industry-skill-roadmap.md` (Phase 6 future plan document)

---

## Verification

- [ ] All 5 hooks fire correctly (restart session, then test)
- [ ] Line count hooks deny edits when file is at/over limit
- [ ] Checkpoint reminder fires after 3+ non-MEMORY.md edits
- [ ] All 8 new skills pass B gate (96+/120)
- [ ] All 3 new agents pass B gate (96+/120)
- [ ] No trigger conflicts between hq-* skills and existing generic skills
- [ ] Every skill explicitly documents its agent pairings
- [ ] GitHub repo updated with all new skills + agents
- [ ] Global settings.json backup exists before modification
- [ ] Industry roadmap document written (Phase 6)

---

## Files to Create

### Hook Scripts
- `~/.claude/hooks/check-line-count.py`
- `~/.claude/hooks/checkpoint-reminder.py`
- HQ: `tools/hooks/file-age-warning.py`
- HQ: `tools/hooks/agent-folder-blocker.py`

### New Skills (8 total, all in `~/.claude/skills/`)
- `hq-orchestrator/SKILL.md` + 3 companions (routing-rules, synthesis-format, department-taxonomy)
- `hq-knowledge-governance/SKILL.md` + 3 companions (k-classification, governance-protocol, audit-methodology)
- `hq-tech-strategy/SKILL.md` + 3 companions (mva-methodology, security-tiers, tech-stack)
- `hq-reverse-engineering/SKILL.md` + 3 companions (analysis-framework, intelligence-template, downstream-routing)
- `hq-brand-review/SKILL.md` + 1 companion (brand-guide)
- `hq-revenue-ops/SKILL.md` + 1 companion (client-tiers)
- `hq-operations/SKILL.md` + 1 companion (sop-template)
- `hq-strategic-ops/SKILL.md` + 1 companion (debt-framework)

### New Agents (3 total, in `~/.claude/agents/`)
- `knowledge-governance.md` (pairs with hq-knowledge-governance skill)
- `brand-reviewer.md` (pairs with hq-brand-review skill)
- `reverse-engineer.md` (Echo — pairs with hq-reverse-engineering skill)

### Companion Files (additions to existing skills)
- `~/.claude/skills/smb-cfo/references/sharkitect-pricing-model.md`
- `~/.claude/skills/marketing-strategy-pmm/references/sharkitect-icp.md`
- `~/.claude/skills/contract-legal/references/sharkitect-risk-framework.md`

### Files to Modify
- `~/.claude/settings.json` — add `hooks` section (BACK UP FIRST)
- HQ `.claude/settings.json` — fix PostToolUse→PreToolUse, add hooks 4-5

### Future Planning Document (write, don't build)
- `knowledge-base/projects/aios-vision-definition/industry-skill-roadmap.md`

### Reference Files (read-only during build)
- `~/.claude/skills/hook-development/SKILL.md` — hook patterns, event types, exit codes
- `.tmp/plugins/quality-gate/scripts/quality-gate.py` — Python hook script pattern
- `~/.claude/skills/ultimate-skill-creator/SKILL.md` — meta-skill for skill builds
- `~/.claude/skills/ultimate-agent-creator/SKILL.md` — meta-skill for agent builds
