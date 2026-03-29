# MVA (Minimal Viable Architecture) Methodology

## Evaluation Criteria

For every technology decision, score these 5 dimensions on a 1-5 scale:

| Dimension | Score 1 (Low) | Score 5 (High) |
|-----------|---------------|-----------------|
| **Urgency** | Nice to have, no deadline | Blocking revenue or operations |
| **Complexity** | Simple config or API call | Custom development, multiple components |
| **Existing Coverage** | Nothing covers this today | Current tools handle 80%+ |
| **Maintenance Cost** | Set-and-forget | Requires ongoing attention, updates |
| **Expansion Risk** | Solution scales naturally | Will need replacement at 2x load |

### Decision Matrix

| Urgency | Existing Coverage | Decision |
|---------|------------------|----------|
| High (4-5) | Low (1-2) | BUILD — custom solution needed now |
| High (4-5) | High (4-5) | BUY/CONFIGURE — use existing tools, customize |
| Low (1-2) | Any | WAIT — revisit when urgency increases |
| Medium (3) | Low (1-2) | EVALUATE — research options, decide next quarter |
| Medium (3) | Medium (3) | BUY — find the best existing solution |

## Build vs Buy Decision Tree

```
Does an existing tool/service solve 80%+ of the need?
  |
  YES --> Can it be configured/extended to cover the remaining 20%?
  |         YES --> BUY (configure existing)
  |         NO  --> Is the remaining 20% critical?
  |                   YES --> BUILD (custom, but leverage existing for 80%)
  |                   NO  --> BUY (accept the 80%)
  |
  NO  --> Is this a core competency that differentiates us?
            YES --> BUILD (invest in custom solution)
            NO  --> Is there an emerging tool that will likely cover this in 6 months?
                      YES --> WAIT (use workaround, revisit in 6 months)
                      NO  --> BUILD (minimal version, document expansion path)
```

## Expansion Path Documentation

Every BUILD decision MUST include an expansion path document:

```markdown
## Expansion Path: [System Name]

### Current State (MVA)
- What it does now
- Capacity: handles [X] volume
- Dependencies: [list]

### Trigger for Expansion
- What signal means we need to expand (e.g., >1000 daily events, >50 users)

### Expansion Plan
- Phase 1: [Quick scaling step] — estimated effort: [hours]
- Phase 2: [Architecture change] — estimated effort: [days]
- Phase 3: [Full replacement if needed] — estimated effort: [weeks]

### Exit Cost
- What it costs to migrate away from this system entirely
- Data portability: [easy/moderate/hard]
```

## Technology Risk Assessment

For any new platform, API, or integration:

| Risk Category | Question | Weight |
|--------------|----------|--------|
| **Technical Failure** | What happens if this service goes down? | High |
| **Scalability** | Can it handle 10x current load? | Medium |
| **Security** | What data does it access? What's the breach impact? | High |
| **Vendor Lock-in** | How hard is it to switch? | Medium |
| **Cost Volatility** | Can pricing change unexpectedly? | Low |
| **Operational Complexity** | How much ongoing maintenance? | Medium |
| **Human Dependency** | Does it require specialized knowledge to operate? | Low |

Score each 1-5. Total > 25 = HIGH RISK (requires mitigation plan). Total > 18 = MODERATE (proceed with monitoring). Total < 18 = LOW (proceed).
