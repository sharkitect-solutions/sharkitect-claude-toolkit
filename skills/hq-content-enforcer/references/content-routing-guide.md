# Content Routing Guide

## How to Route: Decision Tree

```
TASK INVOLVES WRITING/EDITING TEXT
  |
  +-- Will clients, prospects, or the public see it?
  |     NO --> Skip content enforcer entirely. Proceed normally.
  |     YES --> Continue below
  |
  +-- What KIND of content is it?
  |
  +-- Does it live on a website or has a URL?
  |     YES --> Is it a blog/article? --> content-creator + seo-optimizer + hq-brand-review
  |             Is it a landing/service page? --> copywriting + page-cro + seo-optimizer + hq-brand-review
  |             Is it a form/signup? --> form-cro + signup-flow-cro + hq-brand-review
  |
  +-- Is it sent to someone (email, message)?
  |     YES --> First contact / cold? --> cold-email + outreach-specialist + hq-brand-review
  |             Part of a sequence? --> email-sequence + copywriting + hq-brand-review
  |             One-off business email? --> copywriting + hq-brand-review
  |
  +-- Is it a document (proposal, SOW, case study)?
  |     YES --> Proposal/SOW/contract/agreement? --> copywriting + writing-clearly-and-concisely + contract-legal + hq-brand-review
  |                               ALSO LOAD: knowledge-base/revenue/pricing-structure.md
  |                               ALSO LOAD: knowledge-base/revenue/service-definitions.md
  |                               contract-legal is MANDATORY when: (a) doc contains signature block, (b) no separate master agreement covers the engagement (e.g. Growth Essentials SOW IS the contract), (c) doc has termination/late-fee/governing-law clauses
  |             Case study? --> content-creator + copywriting + hq-brand-review
  |             Sales script? --> copywriting + hq-brand-review
  |                              ALSO LOAD: knowledge-base/revenue/service-definitions.md
  |
  +-- Is it for social media?
  |     YES --> social-content + hq-brand-review
  |
  +-- Is it a presentation?
  |     YES --> pptx + copywriting + hq-brand-review
  |
  +-- Is it ad copy (paid media)?
  |     YES --> copywriting + marketing-psychology + hq-brand-review
  |
  +-- None of the above? --> Default: copywriting + hq-brand-review (minimum baseline)
```

## Skill Invocation Order

For each content task, invoke skills in this sequence:

1. **Load brand-quick-ref.md** (always first -- sets the voice standard)
2. **Load any required KB docs** (pricing, services, etc.)
3. **Invoke domain skills** (CRO, SEO, etc.) to understand optimization requirements
4. **Invoke copywriting/content-creator** to draft content following all loaded guidance
5. **Invoke hq-brand-review** on the completed draft (always last -- final quality gate)

## Additional KB Docs by Content Type

| Content Type | Additional Docs to Load | Why |
|---|---|---|
| Proposal / SOW / Contract | `revenue/pricing-structure.md`, `revenue/service-definitions.md` | Correct pricing tiers, service names, scope inclusions |
| SOW with signature block (no master agreement, e.g. Growth Essentials) | Above + invoke `contract-legal` skill | Termination, late-fee, governing-law, acceptance criteria clauses must be self-contained |
| Sales script | `revenue/service-definitions.md` | Accurate service descriptions, value propositions |
| Case study | Client-specific project docs if available | Accurate outcomes, timelines, metrics |
| Landing page | `revenue/pricing-structure.md` (if pricing is shown) | Founding Partner rates, tier pricing |
| Blog (services topic) | `revenue/service-definitions.md` | Accurate descriptions of VDR, RLR, SLW, CPS |

## Bypass Conditions

The enforcer can be SKIPPED (not invoked) when:

1. **Internal documentation** -- SOPs, technical specs, code comments, internal Slack messages
2. **Content in a client's voice** (not Sharkitect's) -- use the client's brand guide instead
3. **Code or configuration** -- JSON, YAML, Python, etc.
4. **Data analysis or reporting** -- numbers and analysis don't need brand voice
5. **Direct quotes from external sources** -- testimonials, regulatory text, partner copy

The enforcer CANNOT be skipped for:
- ANY text a client, prospect, or the public will read
- ANY AI-generated text for external use
- ANY revision to existing client-facing content
- "Quick" or "urgent" content (urgency is not a bypass condition)

## Handling Existing Content Edits

When editing existing content (not writing from scratch):

1. Load brand-quick-ref.md
2. Read the existing content first
3. Assess: is the existing content already on-brand?
   - If YES: make the specific edit, then do a quick brand check on changed sections
   - If NO: flag the off-brand sections to the user. Ask: "Should I also fix the brand voice issues, or just make the specific edit you requested?"
4. Either way, run hq-brand-review on the final output

## Multi-Piece Content Projects

When creating multiple related pieces (e.g., a landing page + email sequence + social posts for a campaign):

1. Load brand-quick-ref.md ONCE at the start
2. Route each piece individually through the decision tree
3. Brand-review each piece as it's completed (not all at once)
4. After all pieces are done, check cross-piece consistency:
   - Same value propositions across all pieces?
   - Tone modulation matches each channel?
   - CTAs are consistent and not contradictory?