# Taxonomy Design for Knowledge Bases

## Taxonomy Types Comparison

| Model | Structure | Best For | Strengths | Weaknesses |
|-------|-----------|----------|-----------|------------|
| Hierarchical | Tree (parent-child) | <500 docs, <20 people | Simple navigation, clear ownership | Single-parent limit, deep nesting |
| Faceted | Multi-axis tags | 500-5,000 docs, 20-200 people | Flexible filtering, multiple views | Requires tag governance, complex setup |
| Flat + Search | Minimal hierarchy + search | >5,000 docs, >200 people | Low maintenance, scales infinitely | Depends entirely on search quality |
| Folksonomy | User-generated tags | Never as primary (use as supplement) | Low friction for contributors | Tag proliferation, synonyms, unfindable content |

### Hierarchical Design Rules

- Maximum 3 levels of nesting. Beyond 3 levels, navigation breaks down.
- Each level should have 5-9 items (Miller's Law applied to categories). More than 9 items at one level = split or rethink.
- Category names must be mutually exclusive. If a document could logically go in two categories, the taxonomy is wrong.
- Include an "Archive" or "Deprecated" branch. Content retirement needs a defined destination.

Example structure for a 30-person engineering team:

```
Engineering/
  Architecture/          (ADRs, system diagrams, design docs)
  Runbooks/              (incident response, deployment, on-call)
  SOPs/                  (operational procedures, change management)
  Onboarding/            (new hire guides, tool setup, reading paths)
  Reference/             (API specs, config values, glossary)
Operations/
  HR/                    (policies, benefits, leave procedures)
  Finance/               (expense policies, approval workflows)
  Facilities/            (office guides, security procedures)
Product/
  Roadmap/               (plans, prioritization frameworks)
  Research/              (user research, market analysis)
  Requirements/          (PRDs, specifications)
Archive/
  [Year]/                (retired content, organized by year)
```

### Faceted Design Rules

Define 4-6 independent facets. Each document is tagged along every facet.

**Recommended facets for most SMBs:**

| Facet | Values (examples) | Purpose |
|-------|-------------------|---------|
| Team | Engineering, Product, Operations, Sales, Support | Ownership |
| Content Type | Reference, Procedural, Conceptual, Troubleshooting | Navigation by purpose |
| System/Domain | Payments, Auth, Onboarding, Billing, Infrastructure | Technical scope |
| Lifecycle | Draft, Active, Review Needed, Deprecated | Freshness management |
| Audience | All Staff, Engineering, Managers, New Hires | Access and relevance |

**Facet governance rules:**
- New facet values require approval from the KB admin (or designated owner)
- Facet values cannot be created ad-hoc by contributors -- use a controlled vocabulary
- Review facet values quarterly; merge synonyms, retire unused values
- Every document must be tagged on at least Team, Content Type, and Lifecycle facets

---

## Content Type Definitions

### When to Use Each Type

| Content Type | User Question | Format | Examples |
|-------------|--------------|--------|----------|
| Reference | "What is X?" / "What are the values for Y?" | Tables, lists, key-value pairs | API endpoints, config values, org chart, glossary |
| Procedural | "How do I do X?" | Numbered steps, checklists | SOPs, runbooks, how-to guides |
| Conceptual | "Why does X work this way?" | Narrative with diagrams | Architecture decisions, design rationale, system overviews |
| Troubleshooting | "X is broken, what do I do?" | Symptom-based decision trees | Known issues, FAQ (structured), error resolution guides |

### Content Type Mixing Rules

- **Never mix Procedural and Conceptual in one document.** Users scanning for steps get lost in explanations. Users reading for understanding get interrupted by commands. Create two documents and cross-link them.
- **Reference content is always standalone.** Never embed reference tables inside procedural or conceptual documents. Link to the reference source.
- **Troubleshooting documents link to Procedural documents for resolution.** The troubleshooting doc identifies the problem; the procedural doc provides the fix. Do not duplicate the fix steps.

---

## Tagging Strategy

### Controlled Vocabulary

A controlled vocabulary is a pre-approved list of tags. Contributors select from the list; they cannot create new tags without approval. This is the single most important governance mechanism for preventing tag proliferation.

**Implementation steps:**
1. Seed the vocabulary with 30-50 tags based on existing content
2. Assign a vocabulary owner (person who approves new tags)
3. Publish the vocabulary in a visible location (linked from the contribution guide)
4. Review quarterly: merge synonyms, add missing terms, retire unused tags
5. When a contributor requests a tag that is a synonym of an existing tag, redirect to the existing tag and add the synonym to a synonym ring

### Synonym Ring Pattern

Map common search terms to controlled vocabulary terms:

| User Searches For | Maps To (Controlled Tag) |
|-------------------|-------------------------|
| deploy, deployment, deploying, ship, release | deployment |
| auth, authentication, login, sign-in, SSO | authentication |
| oncall, on-call, pager, incident | on-call |
| hire, hiring, recruit, recruiting, talent | hiring |

Configure the search engine or documentation platform to treat all terms in each row as equivalent. Without synonym rings, users who search for "deploy" will not find documents tagged "deployment."

### Tag Governance Process

```
Contributor wants new tag
  |
  Q: Does a synonym already exist?
  |-- YES --> Use existing tag. Add synonym to synonym ring.
  |-- NO --> Q: Will 3+ documents use this tag within 30 days?
              |-- YES --> Approve. Add to controlled vocabulary.
              |-- NO --> Deny. Suggest existing broader tag.
```

---

## Cross-Linking Patterns

### Bidirectional Links

When Document A links to Document B, Document B should display a backlink to Document A. This enables discovery from either direction.

**Platforms with native backlinks:** Notion, Obsidian, Roam, Confluence (via plugin)
**Platforms requiring manual backlinks:** GitHub wikis, SharePoint, Google Docs

For platforms without native backlinks, maintain a "Related Documents" section at the bottom of each document. Update both documents when creating a link.

### Hub-and-Spoke Pattern

Designate hub documents that serve as navigation centers for a topic area. Hub documents contain no original content -- only structured links to spoke documents.

```
Hub: Payment System Documentation
  |-- Architecture Overview (Conceptual)
  |-- Payment Processing SOP (Procedural)
  |-- Payment Failure Runbook (Troubleshooting)
  |-- Payment API Reference (Reference)
  |-- Payment Config Values (Reference)
```

**Hub rules:**
- One hub per major system or domain
- Hub documents are the first link given to new team members for that domain
- Hub documents are reviewed monthly to ensure all links are current
- If a link from the hub goes to a stale document, that is a freshness management failure

### Sequential Linking

For onboarding paths and multi-step learning journeys, use explicit "Previous / Next" links:

```
Document: Setting Up Your Development Environment
  Previous: Welcome to the Team (Overview)
  Next: Your First Code Change (Tutorial)
```

Sequential links create guided paths through content. Without them, new hires click randomly and miss foundational context.

---

## Search Optimization

### Metadata Standards

Every document should contain structured metadata, either in frontmatter, document properties, or a designated metadata section:

| Field | Required | Purpose | Example |
|-------|----------|---------|---------|
| Title | Yes | Primary search match | "Customer Refund SOP" |
| Owner | Yes | Freshness accountability | "jane.doe@company.com" |
| Last Updated | Yes | Staleness detection | "2026-03-01" |
| Next Review | Yes | Proactive freshness | "2026-06-01" |
| Tags | Yes | Faceted filtering | ["finance", "procedural", "refunds"] |
| Summary | Recommended | Search snippet, AI retrieval | "Step-by-step procedure for processing customer refund requests under $5,000" |
| Audience | Recommended | Access scoping | "Support Team, Finance" |
| Status | Recommended | Lifecycle tracking | "Active" / "Draft" / "Deprecated" |

### Search Quality Checklist

- [ ] Full-text search indexes document body, title, and metadata
- [ ] Synonym rings configured for common term variations
- [ ] Search results display title, summary snippet, last updated date, and owner
- [ ] Search results are ranked by relevance, with recent updates weighted higher
- [ ] Zero-result searches are logged and reviewed monthly (content gap signal)
- [ ] Most-searched terms are reviewed quarterly (content demand signal)

---

## Staleness Detection Rules

### Automated Detection Criteria

| Rule | Condition | Action |
|------|-----------|--------|
| Review overdue | Current date > Next Review date | Notify owner. Flag in dashboard. |
| Edit decay | No edits in 6 months AND page views declining | Flag as likely stale. Notify owner for review. |
| Orphaned | Owner departed AND no ownership transfer | Escalate to team lead. Must be reassigned within 7 days. |
| Reference rot | Contains URLs, version numbers, or dates older than 12 months | Flag for reference update check. |
| High-risk stale | Referenced by active SOPs/runbooks AND no edits in 12 months | Priority flag. Incorrect reference content causes execution failures. |

### Staleness Dashboard

Maintain a living dashboard showing:
- Total documents by lifecycle status (Active, Draft, Review Needed, Deprecated)
- Percentage of documents with overdue reviews
- Count of unowned documents
- Top 10 most-viewed documents with oldest update dates (high-impact staleness risk)
- Count of documents with no views in 90 days (retirement candidates)

---

## Platform Migration Checklist

### Pre-Migration (Weeks 1-2)

- [ ] Inventory all content in current platform: document count by category, owner, last updated
- [ ] Identify actively-used content (viewed in past 90 days) vs archive content
- [ ] Map current taxonomy to target platform taxonomy. Resolve structural differences before migrating.
- [ ] Identify content that requires format conversion (tables, diagrams, embedded files)
- [ ] Choose migration method: API export (best), structured export (good), HTML scrape (fallback)
- [ ] Set up target platform: configure taxonomy, access controls, templates
- [ ] Communicate migration timeline and plan to all stakeholders

### Migration Execution (Weeks 3-6)

- [ ] Phase 1: Migrate actively-used content first (highest priority, most likely to expose issues)
- [ ] Phase 2: Migrate reference and procedural content
- [ ] Phase 3: Migrate archive content last
- [ ] Preserve internal links: rewrite URLs to point to new platform locations
- [ ] Preserve metadata: owner, dates, tags, lifecycle status
- [ ] Verify formatting: spot-check 10% of migrated documents for layout issues
- [ ] Test search: confirm migrated content is indexed and findable

### Post-Migration (Weeks 7-8)

- [ ] Run parallel systems for 30 days minimum
- [ ] Redirect all old platform URLs to new platform equivalents (do not break bookmarks)
- [ ] Announce new platform as the canonical source
- [ ] Block new content creation in old platform (read-only mode)
- [ ] Audit: verify document counts match (source vs target)
- [ ] Audit: verify search quality on 20 common queries
- [ ] Gather user feedback after 2 weeks of use
- [ ] Decommission old platform after 60 days with no reported issues
