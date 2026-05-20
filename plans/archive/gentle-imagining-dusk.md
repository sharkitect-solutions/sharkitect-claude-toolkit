# Phase 5.5: Marketplace Re-Scan + Revised Phase 6 Plan

## Context

Phase 5 gap analysis searched only davila7/claude-code-templates (500 skills). We've since discovered two major new sources — VoltAgent (825+ skills from official dev teams) and Antigravity (1,250+ community + official skills). User requested a full re-scan of all 15 gaps against these new marketplaces before committing to BUILD/BUY decisions.

**Goal**: Re-evaluate every gap against 3 marketplace sources. Revise BUILD/BUY recommendations. Produce updated gap analysis. Then execute Phase 6 with better-informed decisions.

---

## Re-Scan Results: Gap-by-Gap Analysis

### Marketplace Sources Now Available

| Source | Skills | CLI | Strength |
|---|---|---|---|
| davila7/claude-code-templates | 500+ | `npx claude-code-templates@latest --skill <name> --yes` | Broad coverage, Claude-specific |
| VoltAgent/awesome-agent-skills | 825+ | `npx skills add VoltAgent/awesome-agent-skills --skill <name> --global --yes` | Official dev teams (Stripe, Cloudflare, HashiCorp) |
| sickn33/antigravity-awesome-skills | 1,250+ | `npx skills add sickn33/antigravity-awesome-skills --skill <name> --global --yes` | Largest catalog, 9 categories |

### Revised Gap Decisions

#### Still BUILD (5 gaps — no adequate marketplace coverage found)

| # | Gap | Why BUILD survives re-scan |
|---|---|---|
| 1 | **SMB CFO** | VoltAgent has EveryInc finance + Antigravity has pricing/ROI tools, but none cover full SMB scope (P&L, cash flow, runway, monthly close, tax planning). Fragments exist, comprehensive skill doesn't. |
| 2 | **Customer Success** | Antigravity has analytics-product and customer-io-pack (already installed as plugin). No skill covers the post-sale lifecycle: health scoring, churn prediction, renewal management, QBR prep. |
| 6 | **HR / People Ops** | Neither VoltAgent nor Antigravity has dedicated HR skills. Antigravity has payroll fragments only. Clear gap across all 2,575+ skills. |
| 9 | **Contract / Legal** | Antigravity only has Brazilian law specialists (advogado-especialista). No general contract templates (MSA, NDA, SLA, ToS). Still a void. |
| 10 | **Knowledge Management** | Existing marketplace skills (agent-memory-systems, notion-template-business, documentation-templates) are already installed. Gap is KM *strategy* — SOP frameworks, runbook design, information architecture — not tools. |

#### Upgraded to BUY_EVALUATE (1 gap moved from BUILD)

| # | Gap | New marketplace coverage found | Candidates to evaluate |
|---|---|---|---|
| 3 | **Proposal / SOW** | VoltAgent: Corey Haines (30+ sales skills), Pawel Huryn (50+ product skills) may include proposal/scoping content. Stronger than previously identified. | Search VoltAgent for sales-document/proposal skills. Compare with existing sow-generator plugin. If marketplace skill scores 85+ pre-optimization, optimize it. If not, BUILD. |

#### Confirmed BUY_EVALUATE (2 gaps — now with more source options)

| # | Gap | Sources expanded | Candidates |
|---|---|---|---|
| 4 | **API Design** | davila7: api-patterns, api-integration-specialist. Antigravity: api-design-principles, api-security-testing. VoltAgent: likely has API skills from vendor teams. | Install best candidate from each source, score all, keep winner. |
| 5 | **Testing Strategy** | davila7: testing-patterns, senior-qa, tdd-workflow. Antigravity: testing-strategy, pytest-patterns, test-automation. VoltAgent: Anthropic + Trail of Bits testing skills. | Strong coverage — high confidence one can reach B gate with optimization. |

#### Confirmed BUY (6 gaps — now with multi-source comparison)

| # | Gap | Best source candidates | Install plan |
|---|---|---|---|
| 7 | **Client Reporting** | Antigravity: data-storytelling, analytics-product (but these are analytics, not client-facing reports). davila7: none direct. | **CHANGED to BUILD** — on closer analysis, no marketplace skill covers client-facing progress reports, milestone docs, ROI summaries. Analytics tools =/= client reporting strategy. |
| 8 | **CI/CD & DevOps** | davila7: senior-devops + github-actions-creator. VoltAgent: HashiCorp, Cloudflare, Netlify official. Antigravity: conductor-pack (23 skills). | Install davila7's senior-devops (broadest). Compare with VoltAgent if needed. |
| 11 | **E-commerce** | davila7: shopify-development. Antigravity: likely has Shopify skills too. | Install davila7's shopify-development. |
| 12 | **Payment/Billing** | davila7: stripe-integration. VoltAgent: Official Stripe team skills. | **VoltAgent's official Stripe may be higher quality.** Install both, score, keep winner. |
| 13 | **Accessibility** | davila7: accessibility-auditor. Antigravity: accessibility-compliance, wcag-compliance, inclusive-design. | Install davila7's accessibility-auditor + Antigravity's wcag-compliance. Score both. |
| 14 | **i18n** | davila7: i18n-localization. Antigravity: likely has i18n skills. | Install davila7's i18n-localization. |

#### Still SKIP (1 gap)

| # | Gap | Rationale unchanged |
|---|---|---|
| 15 | **Database Migration** | Covered by deferred skills (database, supabase-postgres) once optimized. Both new marketplaces also have data engineering clusters but nothing better than what we'll have post-optimization. |

---

## REVISED TOTALS

| Action | Count | Original Phase 5 | Change |
|---|---|---|---|
| **BUILD custom** | 6 | 7 | +client-reporting (moved from BUY), -proposal-sow (moved to EVALUATE) |
| **BUY_EVALUATE** | 3 | 2 | +proposal-sow |
| **BUY** | 5 | 6 | -client-reporting (now BUILD) |
| **SKIP** | 1 | 1 | No change |

### BUILD Queue (6 skills, priority order)
1. smb-cfo
2. customer-success
3. proposal-sow (fallback if BUY_EVALUATE fails)
4. hr-people-ops
5. client-reporting
6. contract-legal
7. knowledge-management

### BUY_EVALUATE Queue (3 gaps, install best candidates then score)
1. Proposal/SOW — search VoltAgent sales skills
2. API Design — compare davila7/api-patterns vs Antigravity/api-design-principles
3. Testing Strategy — compare davila7/testing-patterns + senior-qa vs Antigravity options

### BUY Queue (5 installs)
1. senior-devops (davila7)
2. github-actions-creator (davila7)
3. shopify-development (davila7)
4. stripe-integration (davila7 + compare VoltAgent official Stripe)
5. accessibility-auditor (davila7 + compare Antigravity wcag-compliance)
6. i18n-localization (davila7)

---

## Deferred Skills (7 — optimize alongside or after Phase 6)

All already installed, need standard optimization pass:
nestjs-expert, nextjs-best-practices, invoice-organizer, supabase-postgres-best-practices, competitor-alternatives, database, file-organizer

---

## Execution Plan

### Step 1: Update Gap Analysis Artifacts (DONE in this phase)
- Rewrite `.tmp/audit-data/gap-analysis.json` with revised recommendations
- Update `.tmp/skills-manifest.json` with revised counts
- Update MEMORY.md with Phase 5.5 results

### Step 2: Execute BUY Installs
Install marketplace skills globally (5-6 installs):
```bash
npx claude-code-templates@latest --skill development/senior-devops --yes
npx claude-code-templates@latest --skill development/github-actions-creator --yes
npx claude-code-templates@latest --skill web-development/shopify-development --yes
npx claude-code-templates@latest --skill development/stripe-integration --yes
npx claude-code-templates@latest --skill creative-design/accessibility-auditor --yes
npx claude-code-templates@latest --skill development/i18n-localization --yes
```
For Stripe and Accessibility, also install VoltAgent/Antigravity alternatives to compare:
```bash
npx skills add VoltAgent/awesome-agent-skills --skill stripe --global --yes
npx skills add sickn33/antigravity-awesome-skills --skill wcag-compliance --global --yes
```
Score all with skill-judge. Keep highest scorer per gap.

### Step 3: Execute BUY_EVALUATE
Search and install candidates for Proposal/SOW, API Design, Testing Strategy:
```bash
# API Design
npx claude-code-templates@latest --skill development/api-patterns --yes
npx skills add sickn33/antigravity-awesome-skills --skill api-design-principles --global --yes

# Testing
npx claude-code-templates@latest --skill development/testing-patterns --yes
npx claude-code-templates@latest --skill development/senior-qa --yes

# Proposal/SOW
npx skills add VoltAgent/awesome-agent-skills --skill <best-match> --global --yes
```
Score each with skill-judge. If any scores 85+ pre-optimization, keep and optimize to B gate. If below 85, mark for BUILD instead.

### Step 4: BUILD Custom Skills (batched, 2-3 per batch)
Use ultimate-skill-creator pipeline for confirmed BUILD items:
- Each skill: create -> optimize -> score -> B gate (96+/120)
- Priority order: smb-cfo first, knowledge-management last
- Batch size: 2-3 per batch (user preference)
- Add any BUY_EVALUATE failures to BUILD queue

### Step 5: Optimize Deferred Skills (7 skills)
Standard optimization pass on already-installed skills:
nestjs-expert, nextjs-best-practices, invoice-organizer, supabase-postgres-best-practices, competitor-alternatives, database, file-organizer

### Step 6: Final Artifacts Update
- Update `.tmp/skills-manifest.json` with final totals
- Update `.tmp/audit-data/gap-analysis.json` with outcomes
- Update MEMORY.md with Phase 6 completion status
- Run `python tools/sync-skills.py --sync --push` to sync new skills to GitHub

---

## Verification

- [ ] Gap analysis JSON updated with revised recommendations
- [ ] Skills manifest updated with revised counts
- [ ] All BUY skills installed, scored, duplicates resolved
- [ ] All BUY_EVALUATE skills installed, scored, BUILD/keep decision made
- [ ] All BUILD skills created, optimized, scored, pass B gate (96+/120)
- [ ] All 7 deferred skills optimized to B gate
- [ ] Skills manifest reflects final state
- [ ] MEMORY.md updated with Phase 6 results

---

## Expected Final Count

Current: 111 skills (110 custom + 1 external gemini-api-dev)
+ BUY: ~5-6 new marketplace installs
+ BUY_EVALUATE: ~2-3 kept marketplace skills
+ BUILD: ~6 custom skills
+ Deferred: 7 optimized (already counted)
= ~124-127 total skills, all at B gate or above
