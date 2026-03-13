# Legal Compliance for Comparative Advertising

## Jurisdiction Overview

Comparative advertising law varies significantly by jurisdiction. Publishing comparison pages that target international audiences requires awareness of the strictest applicable standard.

| Jurisdiction | Governing Law | Key Principle | Enforcement Risk |
|-------------|--------------|---------------|------------------|
| United States | Lanham Act Section 43(a), FTC Act Section 5 | Claims must be truthful and substantiable. Comparative ads are broadly permitted. | Competitor-initiated lawsuits (private right of action). FTC enforcement for deceptive claims. |
| European Union | Directive 2006/114/EC (Misleading and Comparative Advertising) | Comparative advertising is permitted only if it is not misleading, compares like-for-like, does not discredit competitors, and does not create confusion. | National advertising standards authorities. Competitor complaints to regulatory bodies. |
| United Kingdom | CAP Code (Advertising Standards Authority), Business Protection from Misleading Marketing Regs 2008 | Similar to EU directive post-Brexit. ASA has jurisdiction over online advertising including comparison pages. | ASA complaints (fast, public rulings). Competitor-initiated. |
| Australia | Australian Consumer Law (Competition and Consumer Act 2010) | Misleading or deceptive conduct broadly defined. Comparative advertising permitted if truthful. | ACCC enforcement. Competitor or consumer complaints. |

---

## US Lanham Act -- Detailed Requirements

### Section 43(a) Elements for Comparative Advertising Claims

To prevail in a Lanham Act false advertising claim, a plaintiff must prove:

1. **False or misleading statement of fact** -- The claim must be factual (not opinion) and either literally false or misleading in context.
2. **In commercial advertising or promotion** -- Comparison pages on commercial websites qualify.
3. **Deceived or likely to deceive** -- The target audience (buyers) would be misled.
4. **Material** -- The false statement is likely to influence a purchasing decision.
5. **Injury** -- The plaintiff (competitor) suffered or is likely to suffer competitive injury.

### Claim Categories and Legal Risk

| Claim Type | Example | Risk Level | Substantiation Needed |
|-----------|---------|-----------|----------------------|
| Factual superiority | "Our API is 3x faster than Competitor X" | High | Independent benchmark data, reproducible methodology |
| Puffery | "We offer the best user experience" | Low | None (recognized as opinion, not fact) |
| Price comparison | "50% less than Competitor X" | Medium-High | Current pricing verification, same-tier comparison, same billing period |
| Feature comparison | "Competitor X does not support SSO" | High | Current verification, specify tier (SSO may exist on enterprise plan) |
| Customer preference | "87% of teams prefer us over Competitor X" | High | Survey methodology, sample size, recency, question framing |
| Implied claim | Feature table showing competitor with "No" on critical features | Medium | Each "No" must be verified. Implied claims are actionable under Lanham Act. |

### Safe Harbor Language Patterns

Use these phrases to reduce legal exposure without weakening the comparison:

- "As of [date], based on publicly available information..."
- "Based on [source] pricing as of [date]. Verify current pricing at [competitor URL]."
- "This comparison reflects [specific plan tier]. Features may differ by plan."
- "We invite [Competitor] to contact us to correct any inaccuracies."
- "Information gathered from [source]. Last verified [date]."

---

## EU Directive 2006/114/EC -- Requirements

The EU directive permits comparative advertising only when ALL of the following conditions are met:

| Condition | What It Means | Common Violation |
|-----------|--------------|------------------|
| Not misleading | All claims are accurate and substantiable | Outdated pricing data, feature claims from old product versions |
| Compares like-for-like | Products meet same needs or are intended for same purpose | Comparing enterprise tier of one product to startup tier of another |
| Objectively compares material features | Comparison is based on verifiable, relevant characteristics | Cherry-picking dimensions where you win, ignoring dimensions where you lose |
| Does not discredit or denigrate | Does not unfairly damage competitor's reputation | Mocking tone, emphasizing competitor failures (outages, data breaches) |
| Does not create confusion | Does not confuse consumers between the advertiser and competitor | Using competitor's exact color scheme or visual identity in comparison |
| Does not take unfair advantage of competitor's reputation | Does not free-ride on competitor's brand equity | Using competitor's brand name as primary keyword in meta title without comparison context |

**Practical impact:** EU rules are stricter than US rules. A comparison page that is legal in the US may violate EU directive on the "does not discredit" or "objectively compares" requirements. If your page is accessible in the EU, apply EU standards as the baseline.

---

## Trademark and Screenshot Usage

### Competitor Trademark Rules

| Usage | Generally Permitted | Generally Prohibited |
|-------|-------------------|---------------------|
| Competitor name in body text for comparison | Yes (nominative fair use) | N/A |
| Competitor name in page title / URL | Yes, if for genuine comparison | Using name to imply endorsement or affiliation |
| Competitor logo on your comparison page | Risky -- varies by jurisdiction | Altering the logo, placing it in a way that implies endorsement |
| Competitor name in meta title / description | Yes, if comparison is genuine | Competitor-name-only titles (e.g., "Notion" without comparison context) |
| Competitor name in paid search ads | Permitted in US (Google allows it). Restricted in some EU countries. | Using competitor name in ad copy to imply you ARE the competitor |

### Screenshot Rules

| Scenario | Guidance |
|----------|---------|
| Competitor's public-facing website | Generally permitted for commentary and comparison (fair use / fair dealing) |
| Competitor's product UI (behind login) | Higher risk. May violate terms of service. Use only if necessary for comparison. |
| Altering screenshots | Never alter a competitor's screenshot. Annotations (arrows, highlights) are acceptable. Cropping to mislead is not. |
| Dated screenshots | Always include the date the screenshot was captured. A 2-year-old screenshot of a competitor's UI is misleading. |

---

## Competitor Response Playbook

### When a Competitor Objects to Your Comparison Page

| Objection Type | Appropriate Response | Escalation |
|----------------|---------------------|------------|
| "Your pricing data is wrong" | Verify immediately. If wrong, correct within 24 hours. If correct, respond with source and date. | None needed if you have documentation |
| "Your feature claim is false" | Verify against current product. If they added the feature, update page. If disputed, add nuance. | Legal review if claim is contested and material |
| "Cease and desist letter" | Do not ignore. Do not comply reflexively. Forward to legal counsel immediately. | Legal counsel within 48 hours |
| "We demand you remove the page" | You have no obligation to remove truthful comparative content (US law). Evaluate whether claims are defensible. | Legal review of all claims on the page |
| "We will sue for trademark infringement" | Nominative fair use protects comparative use of trademarks. Document your good-faith comparison purpose. | Legal counsel for trademark analysis |
| Public social media complaint | Respond factually and briefly. Offer to correct any verified inaccuracy. Do not engage in public argument. | PR/comms review if it escalates |

### Documentation Protocol

For every comparison page, maintain a verification file that records:

- Date each claim was verified
- Source for each factual claim (URL, screenshot with date, pricing page archive)
- Methodology for any quantitative claims (benchmark setup, survey methodology)
- Change log of all edits to the page with reasons

This documentation is your defense if a competitor challenges your claims. Without it, even truthful claims become expensive to defend because you cannot quickly produce substantiation.

### Proactive Legal Checklist

Before publishing any comparison page, verify:

- [ ] All pricing data verified within the last 30 days with source URLs recorded
- [ ] All feature claims verified against current product version (not beta or deprecated)
- [ ] No unsubstantiated superlatives ("the only," "the best," "the fastest") without data
- [ ] Competitor trademarks used only in comparative context, not to imply endorsement
- [ ] Screenshots dated and unaltered
- [ ] "Last verified" date displayed on the page
- [ ] Page accessible in EU? Apply EU directive standards as baseline
- [ ] Competitor response channel documented (email for corrections, visible on page)
