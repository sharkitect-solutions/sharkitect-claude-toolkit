# Intelligence Report Template

Use this template for all structured reverse engineering outputs.

```markdown
## Intelligence Report: [Subject Name]

**Date:** [YYYY-MM-DD]
**Analyst:** reverse-engineer agent
**Input type:** [YouTube video / Product demo / Tutorial / Article / Code / Mixed]
**Analysis depth:** [Quick Scan / Standard / Deep Dive]
**Overall confidence:** [CONFIRMED / HIGH / MEDIUM / LOW]

---

### 1. Executive Summary
[2-3 sentences: What is the subject? What did we learn? What's the key takeaway?]

### 2. Key Findings

| Finding | Confidence | Evidence Source | Implications for Sharkitect |
|---------|-----------|----------------|----------------------------|
| [Finding 1] | [90%] | [Source] | [What this means for us] |
| [Finding 2] | [75%] | [Source] | [What this means for us] |
| ... | ... | ... | ... |

### 3. Architecture Assessment

**Confirmed Components:**
- [Technology/pattern with HIGH+ confidence]

**Inferred Components:**
- [Technology/pattern with MEDIUM confidence] — Basis: [why we think this]

**Speculative Components:**
- [Technology/pattern with LOW confidence] — Basis: [limited evidence]

### 4. Business Model Assessment
- **Pricing model:** [what we observed/inferred]
- **Target market:** [who they serve]
- **Key differentiator:** [what makes them unique]
- **Revenue indicators:** [any signals of scale/revenue]

### 5. Competitive Implications

**What they do better than us:**
- [Specific capability with evidence]

**What we do better:**
- [Specific capability with evidence]

**Opportunities identified:**
- [Gap or weakness we could exploit]

### 6. Validation Needed
[Items tagged LOW or SPECULATIVE that need verification before acting on them]
- [ ] [Item 1] — Suggested validation method: [how to verify]
- [ ] [Item 2] — Suggested validation method: [how to verify]

### 7. Recommended Next Steps
1. [Immediate action based on HIGH+ confidence findings]
2. [Validation action for MEDIUM confidence findings]
3. [Research action for LOW confidence findings]

---

**Disclaimer:** This analysis is based on available information and inference. Findings tagged below HIGH confidence require validation before strategic decisions.
```

## Worked Example — Quick Scan Output

Below is a completed Quick Scan for a hypothetical AI scheduling tool to show how confidence tags, evidence sourcing, and the template come together in practice:

```
## Intelligence Report: CalendarBot AI

**Date:** 2026-03-28
**Analyst:** reverse-engineer agent
**Input type:** YouTube video (product demo, 12 min)
**Analysis depth:** Quick Scan
**Overall confidence:** MEDIUM

### Key Findings

| Finding | Confidence | Source (Admiralty) | Implications |
|---------|-----------|-------------------|-------------|
| Uses OpenAI API for NLP parsing | HIGH 80% | Video shows API call in devtools (B2) | Standard approach, no moat |
| React + Next.js frontend | CONFIRMED 95% | Wappalyzer scan + visible React devtools (A1) | Common stack, easy to replicate |
| Google Calendar API integration | HIGH 85% | Shown in demo + job posting mentions it (B1) | Table stakes for scheduling |
| Custom ML model for scheduling optimization | LOW 45% | Founder claim in video, no corroboration (C4) | If true, significant differentiator |
| ~500 paying users | SPECULATIVE 30% | Inferred from Stripe badge + team size of 3 (E3) | Unvalidated — do not use for sizing |

### Validation Needed
- [ ] Custom ML model claim — check for published papers, HuggingFace repos, or patent filings
- [ ] User count — look for press releases, ProductHunt launch data, or LinkedIn employee count
```

Notice: the ML model claim stays LOW despite the founder saying it on video, because a single self-reported source (C4) cannot push past LOW. The React finding hits CONFIRMED because two independent, reliable sources agree (A1).

## Tool Failure Fallbacks

When primary tools (WebSearch, WebFetch, Firecrawl) are unavailable or failing:

**If WebSearch is down:**
- Use the Playwright MCP browser to navigate directly to target URLs and take snapshots
- Ask the user to paste relevant URLs or content manually
- Check cached/archived versions via web.archive.org (navigate with Playwright)

**If WebFetch/Firecrawl is down:**
- Use Playwright browser_navigate + browser_snapshot to read page content
- For JavaScript-heavy sites, use browser_evaluate to extract specific data
- Fall back to manual user input: "I cannot scrape this page — please paste the key content"

**If ALL web tools are unavailable:**
- Work exclusively with user-provided input (videos, screenshots, pasted text)
- Lower all confidence baselines by one tier (e.g., what would be MEDIUM becomes LOW)
- State the limitation explicitly in the report header: "Analysis conducted without live web access — confidence scores adjusted downward"
- Skip Phase 4 (Cross-Reference Validation) entirely and note it as incomplete

**General rule:** Never silently degrade quality. If a tool fails, say so in the report and adjust confidence accordingly.

## Report Quality Checklist

Before submitting any intelligence report:
- [ ] Every finding has a confidence score
- [ ] Every confidence score has a stated basis
- [ ] No SPECULATIVE items presented as facts
- [ ] Competitive implications are balanced (strengths AND weaknesses)
- [ ] Validation needed section covers all LOW/SPECULATIVE items
- [ ] Next steps are actionable and prioritized
- [ ] If tools were unavailable, limitations are stated in the report header
