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
  +-- Is it K1 SoT prose? (knowledge-base/governance/**.md or knowledge-base/strategy/**.md path,
  |     OR document classified K1 in DOCUMENT-MAP, OR foundational source-of-truth type:
  |     brand-identity-guide, positioning, ICP, messaging-framework, voice-profile,
  |     audience-profile, or other governance/strategy SoT)
  |     YES --> writing-clearly-and-concisely (FIRST -- preventive prose quality at draft time)
  |             + hq-brand-review (LAST -- detective quality gate)
  |             ALSO LOAD: knowledge-base/DOCUMENT-MAP.md (verify tier classification before authoring)
  |             ALSO LOAD: knowledge-base/governance/voice-profile-chris.md if Chris is the
  |                        document's named author or signatory
  |             FOR EMBEDDED OPERATOR-FACING COPY (example email, embedded landing-page hero,
  |                pitch line, etc.): route THAT specific copy through this enforcer's other
  |                branches (e.g., embedded cold email -> cold-email + outreach-specialist;
  |                embedded hero -> page-cro + seo-optimizer). The K1 doc as a whole still goes
  |                through writing-clearly-and-concisely.
  |             INVOKE hq-knowledge-governance skill in parallel for K-tier classification
  |                discipline (cross-reference integrity in DOCUMENT-MAP + INDEX, version-bump,
  |                changelog metadata). Prose quality + governance discipline are orthogonal
  |                concerns -- both fire on K1 SoT writes.
  |             RATIONALE: K1 SoTs propagate to N downstream surfaces. Sentence-length and
  |                parallel-structure violations baked into K1 prose multiply across every
  |                downstream surface that quotes or references the SoT. Preventive prose
  |                quality at draft time is cheaper than fix-after-review iteration.
  |                Source: wr-hq-2026-05-06-002 (Cohort A3 Lock session, brand-review caught
  |                a 50-word compound sentence in executive-summary opening that
  |                writing-clearly-and-concisely would have prevented preventively).
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
2. **Load voice-profile-chris.md if from-Chris client content** (see Voice Profile Load Rule below)
3. **Load any required KB docs** (pricing, services, etc.)
4. **Invoke domain skills** (CRO, SEO, etc.) to understand optimization requirements
5. **Invoke copywriting/content-creator** to draft content following all loaded guidance
6. **Invoke hq-brand-review** on the completed draft (always last -- final quality gate)

## Writing-Clearly Load Rule (NON-NEGOTIABLE for K1 SoT prose)

When content is **K1 SoT prose** -- file path under `knowledge-base/governance/**/*.md` or `knowledge-base/strategy/**/*.md`, OR document classified K1 in `knowledge-base/DOCUMENT-MAP.md`, OR document type matches a foundational SoT (brand-identity-guide, positioning, ICP, messaging-framework, voice-profile, audience-profile, or other governance/strategy SoT) -- you MUST invoke `writing-clearly-and-concisely` skill BEFORE drafting, IN ADDITION TO `brand-quick-ref.md`. The brand-quick-ref enforces voice attributes (Confident, Direct, Expert, Approachable, Action-Oriented) but does NOT enforce sentence-length, parallel-structure, or readability standards. K1 prose quality propagates to every downstream surface that quotes or references the SoT; preventive prose quality at draft time is cheaper than fix-after-review iteration.

**Required for these document patterns:**
- Files under `knowledge-base/governance/` (any `.md`)
- Files under `knowledge-base/strategy/` (any `.md`)
- Documents marked `tier: K1` in frontmatter or DOCUMENT-MAP
- Foundational SoT types: brand-identity-guide, positioning, ICP/audience-profile, messaging-framework, voice-profile, value-proposition, competitive-positioning

**Not required when:**
- Knowledge base operational docs (K3/K4 tier: SOPs, runbooks, technical specs)
- Internal Slack messages, code comments, JSON/YAML configs
- Edits that don't change prose (frontmatter-only updates, table-cell tweaks, link-only adds)

**Parallel skill invocation:** Also invoke `hq-knowledge-governance` for K-tier classification + cross-reference integrity (DOCUMENT-MAP + INDEX consistency, version-bump, changelog metadata). Prose quality and governance discipline are orthogonal concerns -- both fire on K1 SoT writes. The dependency between them is sequential: `writing-clearly-and-concisely` runs at DRAFT TIME (preventive); `hq-knowledge-governance` runs at COMMIT TIME (audit + propagation); `hq-brand-review` runs LAST as the detective gate.

**Failure mode this prevents:** brand-quick-ref alone scores Brand-Clear technically (e.g. 27/30) while K1 prose still contains 50-word compound sentences, parallel-structure violations, or unclear lead-language that brand-review catches AFTER drafting. Required fix-after-review iterations on K1 docs compound across N downstream surfaces. Source: wr-hq-2026-05-06-002 -- Cohort A3 Lock session, brand-review caught a 50-word compound sentence in `executive-summary.md` opening (Direct attribute scored 5/10, below 7-9 target). `writing-clearly-and-concisely` would have prevented the violation at draft time; estimated 17 cascade docs at ~5 min avoidable cost each = ~85 min if pattern recurs without preventive control.

## Voice Profile Load Rule (NON-NEGOTIABLE for from-Chris content)

When content is **authored AS CHRIS** -- author identity = Chris, message originates from solutions@, sender persona is Chris -- you MUST load `knowledge-base/governance/voice-profile-chris.md` (from workforce-hq cwd) IN ADDITION TO brand-quick-ref.md before drafting. brand-quick-ref.md is the brand RULES (compliance scoring); voice-profile-chris.md is the STYLE within those rules (sample-based actual voice patterns, greeting/closing conventions, signature tiers, voice equation by content type).

**Required for these content types when authored as Chris:**
- Cold email (any prospecting message under his name)
- Email sequence / nurture (multi-touch under his name)
- One-off business email (copywriting from-Chris)
- Proposal / SOW (signed by Chris)
- Sales script (Chris running the call)

**Not required when:**
- Generic Sharkitect copy (landing pages, marketing site, social posts not bylined)
- Content in a client's voice (use the client's brand instead)
- Internal documentation, code comments, technical specs

**Failure mode this prevents:** brand-quick-ref.md alone scores brand-clear technically (e.g. 27/30) while still missing Chris's actual voice (Hey [Name] greeting, "Talk soon," closing, signature tier matching context). Source: wr-hq-2026-04-28-002 -- Hibu follow-up email drafted 4 iterations all 27/30 Brand-Clear and ALL flagged by Chris as "doesn't sound like me." Required manual voice-profile load to land properly.

## Additional KB Docs by Content Type

| Content Type | Additional Docs to Load | Why |
|---|---|---|
| **K1 SoT prose** (governance/, strategy/, foundational SoT) | `knowledge-base/DOCUMENT-MAP.md` (verify tier classification) + INVOKE `writing-clearly-and-concisely` skill BEFORE drafting + INVOKE `hq-knowledge-governance` skill in parallel + `governance/voice-profile-chris.md` if Chris is named author | Tier verification prevents misclassification (K1 vs K2). Writing-clearly-and-concisely enforces sentence-length + parallel-structure preventively at draft time (brand-review alone is detective). Knowledge-governance enforces cross-ref integrity + version-bump + changelog metadata. Voice-profile load when Chris is signatory. |
| Cold email (from Chris) | `governance/voice-profile-chris.md` | Chris's actual voice patterns (greeting, closing, signature tiers, voice equation by content type) |
| Email sequence (from Chris) | `governance/voice-profile-chris.md` | Same -- multi-touch sequences must maintain Chris's voice across all messages |
| One-off email (from Chris) | `governance/voice-profile-chris.md` | Same -- single emails under his name need voice fidelity |
| Proposal / SOW / Contract | `revenue/pricing-structure.md`, `revenue/service-definitions.md`, `governance/voice-profile-chris.md` (when signed by Chris) | Correct pricing tiers, service names, scope inclusions; voice fidelity for Chris-signed docs |
| SOW with signature block (no master agreement, e.g. Growth Essentials) | Above + invoke `contract-legal` skill | Termination, late-fee, governing-law, acceptance criteria clauses must be self-contained |
| Sales script (Chris running call) | `revenue/service-definitions.md`, `governance/voice-profile-chris.md` | Accurate service descriptions, value propositions; Chris's actual phrasing patterns |
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