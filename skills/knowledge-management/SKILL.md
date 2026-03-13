---
name: knowledge-management
description: "Use when designing knowledge bases, creating SOPs, writing runbooks, structuring documentation systems, building internal wikis, or establishing information architecture for teams. Use when someone says 'create a knowledge base', 'write an SOP', 'build a runbook', 'organize our documentation', 'set up an internal wiki', or 'our docs are a mess'. Use when designing tagging taxonomies, content governance models, documentation review cadences, or knowledge transfer plans. Use when migrating between documentation platforms. Use when capturing institutional knowledge during incidents or employee departures. Do NOT use for external-facing product documentation, API documentation, marketing content libraries, or developer documentation portals (use technical-writing or docs-as-code skills instead)."
---

# Knowledge Management -- Internal Documentation Systems for Teams

## File Index

| File | Load When | Do NOT Load |
|------|-----------|-------------|
| `references/sop-framework.md` | Creating SOPs, defining SOP standards, establishing review workflows, writing procedural documentation | Taxonomy design, runbook creation, platform migration |
| `references/runbook-patterns.md` | Writing runbooks, designing incident response docs, building deployment procedures, on-call documentation | SOP creation, taxonomy design, general KB architecture |
| `references/taxonomy-design.md` | Designing information architecture, building tagging systems, planning cross-linking, staleness detection, platform migration | SOP writing, runbook creation, specific procedure authoring |

## Scope Boundary

| Domain | This Skill Covers | Use Instead |
|--------|-------------------|-------------|
| External product docs | -- | technical-writing |
| API documentation | -- | api-patterns |
| Marketing content library | -- | content-research-writer |
| Developer portal design | -- | docs-as-code |
| Project management SOPs | PM-specific SOP templates only | project management |
| Compliance documentation | Knowledge architecture only | compliance / legal |
| Training curriculum design | Documentation-based onboarding paths | HR / L&D |

---

## Knowledge Architecture Principles

### The Four Content Types

Every knowledge base contains exactly four content types. Mixing them causes findability collapse.

1. **Reference**: Facts that do not change with context. API endpoints, configuration values, org charts, glossaries, contact directories. Structured as tables, lists, or lookup entries. Never narrate reference content -- users scan, they do not read.

2. **Procedural**: Step-by-step instructions for completing a task. SOPs, runbooks, how-to guides, checklists. Written in imperative voice with numbered steps. Every procedure has exactly one entry point and explicit exit criteria.

3. **Conceptual**: Explanations of why things work the way they do. Architecture decisions, design rationale, system overviews, onboarding context. Written in narrative form with diagrams. Conceptual docs answer "why" -- never embed procedures inside them.

4. **Troubleshooting**: Symptom-to-resolution mappings. Decision trees, known-issue databases, FAQ entries (when properly structured). Organized by observable symptom, not by root cause. Users arrive with symptoms; they discover root causes.

**Why the separation matters:** When procedure and concept are mixed in one document, the document serves neither purpose. Engineers scanning for steps get buried in explanations. New hires seeking understanding get lost in imperative commands. Separate them. Link between them.

### Taxonomy Design

Three taxonomy models exist. Choose based on team size and content volume.

**Hierarchical** (tree structure): Best for teams under 20 with under 500 documents. Simple to navigate, easy to maintain. Breaks down when content belongs in multiple categories. Example: Engineering > Backend > Deployment > AWS deploys.

**Faceted** (multi-axis classification): Best for teams of 20-200 with 500-5,000 documents. Each document tagged along multiple independent axes (team, system, content-type, lifecycle-stage). Enables powerful filtering. Requires disciplined tagging governance or it degrades into folksonomy. Example: [Team: Backend] [System: Payments] [Type: Runbook] [Stage: Active].

**Flat + Search** (tag-based with full-text search): Best for teams over 200 or content volumes above 5,000 documents. Minimal structure, maximum flexibility. Depends entirely on search quality, metadata discipline, and synonym management. Without controlled vocabulary, findability collapses within 6 months.

Never use folksonomy (uncontrolled user-generated tags) as the primary organization system. Folksonomy creates tag proliferation where "deploy", "deployment", "deploying", and "deploy-process" all exist as separate tags pointing to overlapping content. Within 12 months, no one can find anything.

See `references/taxonomy-design.md` for detailed comparison tables, tagging governance rules, and migration checklists.

For SMBs: start document-based (Notion, Confluence, SharePoint, markdown). Add cross-linking as the system matures. Graph-based systems (Obsidian, Roam) require high contributor discipline most teams under 50 cannot sustain.

---

## SOP Creation Framework

### SOP Structure (Mandatory Sections)

Every SOP contains these seven sections. Omitting any section creates ambiguity that causes execution failures.

1. **Purpose**: One sentence stating what this procedure achieves and why it exists.
2. **Scope**: Who executes this, when, and under what conditions. Explicit exclusions.
3. **Roles & Responsibilities**: RACI or equivalent for every stakeholder. No unnamed actors.
4. **Prerequisites**: What must be true before starting. System access, approvals, prior steps completed.
5. **Procedure**: Numbered steps in imperative voice. Decision points as if/then branches. Expected outputs after each major step.
6. **Exceptions & Edge Cases**: Known deviations, who authorizes them, and fallback procedures.
7. **Revision History**: Version, date, author, change summary. Minimum annual review.

### SOP Complexity Tiers

Not every procedure needs a full SOP. Match document weight to task complexity:

| Tier | Format | When to Use | Example |
|------|--------|-------------|---------|
| Checklist | Bulleted list with checkboxes | Linear tasks, no branching, under 15 steps | Office opening procedure |
| Quick Reference | One-page card with key steps | Frequent tasks performed by trained staff | Password reset process |
| Standard SOP | Full 7-section document | Cross-functional procedures, compliance-relevant tasks | Customer refund process |
| Complex SOP | Full SOP + decision trees + appendices | Multi-path procedures, regulatory requirements | Incident response escalation |

**Why tiers matter:** Over-documenting simple tasks wastes author time and creates maintenance burden. Under-documenting complex tasks creates execution gaps. Match the format to the complexity.

### SOP Lifecycle

```
DRAFT -> REVIEW -> APPROVE -> PUBLISH -> [Active Use] -> REVIEW -> REVISE or RETIRE
```

- **Draft**: Author writes; single owner. No shared access until review-ready.
- **Review**: Subject matter expert validates accuracy. At least one person who performs the task must review.
- **Approve**: Process owner or manager signs off. For compliance SOPs: designated compliance officer.
- **Publish**: Move to the canonical location. Remove or archive previous version. Notify affected teams.
- **Review cadence**: Quarterly for incident-related SOPs. Semi-annually for operational SOPs. Annually for administrative SOPs. After every major incident that reveals an SOP gap.
- **Retire**: When a process is eliminated or replaced. Archive (do not delete) with retirement date and reason.

See `references/sop-framework.md` for the complete SOP template, writing standards checklist, and decision tree documentation patterns.

---

## Runbook Design

### Runbook vs SOP

SOPs define how a process should work under normal conditions. Runbooks define how to respond when conditions are abnormal. The distinction matters because they serve different cognitive states: SOP users are following a routine; runbook users are under stress.

| Attribute | SOP | Runbook |
|-----------|-----|---------|
| User state | Calm, routine | Stressed, time-pressured |
| Branching | Minimal | Extensive (symptom-based) |
| Rollback steps | Rarely needed | Mandatory |
| Escalation path | Optional | Required with SLAs |
| Automation level | Manual or semi | Should progress toward full automation |
| Review trigger | Calendar-based | After every use |

### Runbook Structure

Every runbook contains these sections:

1. **Trigger Condition**: Observable symptom that activates this runbook. Written as "When you observe X" -- not "When system Y fails." Users see symptoms, not root causes.
2. **Severity Assessment**: Decision matrix to determine urgency. Maps symptoms to severity levels.
3. **Prerequisite Checks**: System access, tool availability, communication channels open. Verify before acting.
4. **Diagnostic Steps**: Ordered investigation sequence. Each step produces observable output. "Expected: X. If instead you see Y, go to Step N."
5. **Resolution Procedure**: Fix steps with explicit verification after each. "Run command. Expected output: X. If output differs, STOP and escalate."
6. **Rollback Steps**: How to undo every change made during resolution. Mandatory -- never optional.
7. **Escalation Path**: Who to contact at each severity level, response time expectations, communication templates.
8. **Post-Incident Checklist**: Documentation requirements, follow-up items, knowledge base update triggers.

### Runbook Automation Progression

Runbooks should progress through four automation levels:

| Level | Description | Trigger |
|-------|-------------|---------|
| L0: Manual | Human reads and executes every step | Initial creation |
| L1: Assisted | Scripts handle data gathering; human decides and acts | After 3 manual executions |
| L2: Semi-Automated | Scripts execute; human approves at decision points | After pattern is stable |
| L3: Fully Automated | System detects, resolves, and reports. Human reviews post-facto | After 10+ successful L2 runs |

A runbook that stays at L0 for more than 6 months and is executed monthly or more frequently is a candidate for immediate automation investment.

See `references/runbook-patterns.md` for incident response, deployment, and on-call runbook templates plus game day testing methodology.

---

## Documentation System Design

### Single Source of Truth (SSOT) Principle

Every fact exists in exactly one canonical location. All other references link to the source -- never copy it. When a fact changes, update the source; links remain valid.

**Why SSOT fails in practice:** Teams copy content because linking is inconvenient, the source is in a different platform, or they do not trust the source will be maintained. SSOT requires three supports: easy cross-linking, clear ownership, and enforced freshness.

### Freshness Management

Documentation without freshness management becomes a liability within 12 months. Stale documentation is worse than no documentation because it creates false confidence.

**Ownership**: Every document has exactly one named owner (person, not team). When the owner leaves, ownership transfers before their last day. Unowned documents are flagged within 7 days.

**Review dates**: Every document carries a "Next Review" date visible in metadata. Overdue reviews trigger automated notifications to the owner.

**Staleness detection rules**:
- No edits in 6 months + declining page views = likely stale. Flag for review.
- Owner departed + no transfer = orphaned. Escalate to team lead immediately.
- Referenced by active procedures but not updated in 12 months = high-risk stale. Priority review.
- Contains dates, versions, or URLs older than 12 months = likely contains outdated references.

For technical teams, consider docs-as-code: Git-based version control, PR reviews, static site rendering (MkDocs, Docusaurus), automated link/freshness checks. This works when contributors are developers; it fails when primary contributors are non-technical. Choose tools that match your contributor base.

---

## Team Knowledge Workflows

### Incident-to-Knowledge Pipeline

Every incident produces knowledge. Capture it or lose it. Flow: Incident Resolved -> Blameless Post-Mortem (within 48h) -> Extract reusable knowledge -> Create/Update KB article, runbook, or SOP -> Link to related docs -> Assign owner.

The post-mortem is NOT the KB article. Post-mortems are temporal (what happened on this date). KB articles are evergreen (how to handle this class of problem). Extract the reusable knowledge and file it separately.

### Onboarding Documentation Paths

Structure onboarding as ordered reading paths, not a pile of links. Week 1: company context + tooling setup. Week 2: domain knowledge + architecture. Week 3: procedural SOPs + runbooks. Week 4: deep dives + historical context. Each path document links to the canonical source -- never duplicates content.

### Knowledge Transfer for Departing Employees

When an employee gives notice, initiate knowledge transfer immediately:

1. **Inventory**: What do they own? Documents, processes, relationships, undocumented knowledge.
2. **Prioritize**: Rank by bus factor. Knowledge only they possess gets captured first.
3. **Capture method**: Recorded interviews for complex knowledge. Written SOPs for procedures. Pair sessions for tacit skills.
4. **Transfer ownership**: Every document, every system, every relationship gets a new owner before their last day.
5. **Verify**: New owner executes each transferred procedure at least once while the departing employee is still available for questions.

---

## Platform-Agnostic Implementation

### Tool Selection Criteria

Evaluate documentation platforms against these seven criteria:

| Criterion | Weight | What to Evaluate |
|-----------|--------|------------------|
| Contributor friction | High | How many clicks from "I know something" to "it's published"? |
| Search quality | High | Full-text search, metadata filtering, synonym support? |
| Governance support | Medium | Review workflows, approval chains, access control, audit trails? |
| Cross-linking | Medium | Bidirectional links, link validation, orphan detection? |
| API/Integration | Medium | Can other systems read/write content? Automation support? |
| Migration ease | Low | Can you export all content in a portable format? |
| Cost per user | Low | Total cost including admin overhead, not just license fee |

Contributor friction is weighted highest because the #1 reason knowledge bases fail is that people stop contributing. Every click between "I know this" and "it's documented" reduces contribution rate by approximately 15%.

### Platform Migration

Key principles: export in the most structured format available, map taxonomies before migrating content, preserve internal links, migrate in phases (active first), run parallel systems 30+ days, redirect old URLs, and audit post-migration.

See `references/taxonomy-design.md` for the complete migration checklist.

---

## Named Anti-Patterns

### The Wiki Graveyard
Docs created during setup, never maintained. Within 12 months, team stops checking wiki entirely. **Detect:** >30% of docs have no edits in 6+ months with no review date. **Fix:** Assign owners, set mandatory review dates, run monthly staleness reports, archive unowned/unviewed docs.

### The Tribal Knowledge Trap
Critical knowledge exists only in people's heads. Their absence paralyzes the team. **Detect:** Bus factor of 1 on any critical process. **Fix:** Quarterly knowledge audits. Every critical process must have a second person who can execute it unassisted. Record SME interviews for tacit knowledge.

### The Documentation Sprawl
Docs scattered across Notion, Confluence, Google Docs, Slack bookmarks, email. Nothing findable. **Detect:** Ask 3 team members where a process is documented -- different answers = sprawl. **Fix:** Declare one canonical platform. Migrate active content over 90 days. Redirect old URLs. Block new content in non-canonical locations.

### The Perfect Draft Paralysis
People avoid publishing because docs are not "complete." Knowledge stays undocumented for months. **Detect:** Low contribution rates, stale draft folders. **Fix:** "Good enough" standard: if it helps one person besides the author, publish now. Improve incrementally via review workflows.

### The Copy-Paste Plague
Same content duplicated across multiple docs. Source changes, copies diverge, trust collapses. **Detect:** >3 copies of the same procedure. **Fix:** Identify canonical source, replace copies with links, add SSOT reminder to contribution guidelines.

### The Meeting-as-Documentation Fallacy
Meetings and Slack threads serve as the knowledge system. Info decays in days, is unsearchable, and reaches only attendees. **Detect:** "Where is this documented?" Answer: "check the Slack thread." **Fix:** Rule: decisions from meetings get documented in KB within 24 hours. Rotating scribe role.

---

## Rationalization Table

| Temptation | Why It Fails | Do This Instead |
|------------|-------------|-----------------|
| "We'll document it later when things slow down" | Things never slow down. Knowledge decays exponentially after the event. Within 2 weeks, critical details are lost. | Document within 48 hours of the event. Accept imperfect first drafts. Polish later. |
| "Everyone already knows how this works" | Everyone currently present knows. New hires, contractors, and future team members do not. Team turnover averages 15-20% annually. | If it takes more than 5 minutes to explain verbally, it needs a document. |
| "Our docs tool is too clunky, so people don't contribute" | The tool is rarely the real problem. Contribution friction exists in every tool. The real issue is missing contribution norms and incentives. | Reduce friction (templates, quick-capture), but also establish contribution expectations in team norms. |
| "We need to reorganize the whole wiki before adding more content" | Reorganization projects take months and stall contribution during that time. Meanwhile, knowledge continues to decay. | Add content now using the existing structure. Reorganize incrementally -- one section per sprint. |
| "A shared Slack channel is basically the same as documentation" | Slack is a river, not a lake. Information flows past and becomes unsearchable within days. Channel history is not structured, not reviewed, and not owned. | Use Slack for discussion. Extract decisions and knowledge into the KB within 24 hours. |
| "We need a perfect taxonomy before we start" | Perfect taxonomies are designed through use, not upfront planning. Starting without content produces categories that do not match real needs. | Start with a minimal hierarchy (5-10 top-level categories). Refine after 100 documents based on actual usage patterns. |

---

## Red Flags Checklist

Monitor these indicators. Any single flag warrants investigation. Three or more simultaneously demand immediate action.

- [ ] **No document ownership model** -- unowned documents become stale within 3 months. Every document needs exactly one named owner.
- [ ] **No review cadence defined** -- documentation without scheduled review dates degrades to unreliable within 6-12 months.
- [ ] **Documentation in 3+ platforms with no declared canonical source** -- The Documentation Sprawl is active. Declare one source of truth.
- [ ] **SOP has no revision history or version number** -- impossible to know if the procedure reflects current practice.
- [ ] **Runbook has no rollback steps** -- the team will create irreversible damage during an incident when the fix attempt fails.
- [ ] **Onboarding relies on "shadow someone for a week"** -- tribal knowledge dependency instead of documented paths.
- [ ] **Post-incident reviews produce action items but no KB updates** -- knowledge is being generated and then lost.
- [ ] **Bus factor of 1 on any critical process** -- one person's absence would halt operations. Knowledge transfer is overdue.
- [ ] **Tag taxonomy has more than 3 synonyms for the same concept** -- folksonomy degradation is active. Implement controlled vocabulary.
- [ ] **More than 40% of documents have no edits in the past 6 months** -- The Wiki Graveyard is forming. Run staleness audit immediately.
