# Audit Methodology Deep Dive

## Automated Tool Comparison

| Tool | Detection Rate | Unique Strength | Limitation | Best For |
|------|---------------|-----------------|------------|----------|
| axe-core | ~30-35% of WCAG issues | Zero false positives by design; CI-integratable | Misses keyboard, screen reader, cognitive issues | CI/CD gating, developer testing |
| Lighthouse | ~25-30% | Built into Chrome DevTools; performance context | Runs subset of axe rules; less comprehensive | Quick audits, performance+a11y correlation |
| WAVE | ~30% | Visual inline error overlay; excellent for non-technical stakeholders | Browser extension only; no CI integration | Visual audit presentations, training |
| Pa11y | ~25-30% | CLI-first; headless; Docker-friendly | Smaller rule set than axe | CI pipelines, scripted batch audits |
| IBM Equal Access | ~30% | Best cognitive disability coverage; unique rules other tools miss | Slower scan times; fewer integrations | Government/enterprise compliance |
| Deque axe Monitor | ~30-35% | Scheduled crawling; trend tracking; issue management | Paid; requires account | Enterprise ongoing monitoring |

Key insight: running axe-core AND IBM Equal Access together catches ~40% of issues (they have ~15% rule overlap). No combination of automated tools exceeds 50% detection.

## Sampling Strategy for Large Sites

Sites with 100+ pages cannot audit every page. Use representative sampling:

**Mandatory Pages (always audit)**
- Homepage
- Login / registration flow
- Primary conversion funnel (checkout, signup, contact form)
- Search results page
- Error pages (404, 500)
- Accessibility statement page

**Template-Based Sampling**
1. Identify unique page templates (product page, blog post, landing page, dashboard)
2. Audit 2-3 instances of each template
3. Findings from one instance apply to all pages sharing that template

**User Flow Sampling**
Audit complete task flows end-to-end, not isolated pages:
- Guest browsing to purchase
- Account creation to first use
- Password reset
- Content creation / form submission
- Error recovery

**Sample Size Guidelines**
| Site Size | Minimum Sample | Template Coverage |
|-----------|---------------|-------------------|
| < 50 pages | All pages | 100% |
| 50-200 pages | 30-40 pages | All templates + key flows |
| 200-1000 pages | 50-75 pages | All templates + top 10 flows |
| 1000+ pages | 75-100 pages + automated crawl | All templates + top 20 flows |

## Severity Classification

| Severity | Definition | Examples | SLA Target |
|----------|-----------|----------|------------|
| Critical (P0) | Complete barrier; user cannot complete task | Keyboard trap in checkout, no form labels on login, CAPTCHA with no alternative | Fix within 2 weeks |
| Major (P1) | Significant barrier; workaround may exist but is burdensome | Missing skip link on 50+ nav items, contrast failures on primary CTA, unlabeled icon buttons | Fix within 30 days |
| Minor (P2) | Inconvenience; does not block task completion | Redundant ARIA roles, heading level skip (h2 to h4), decorative image with non-empty alt | Fix within 90 days |
| Enhancement | Beyond AA compliance; improves experience | AAA contrast, expanded keyboard shortcuts, enhanced focus indicators | Backlog / next release |

## VPAT / ACR Documentation

A Voluntary Product Accessibility Template (VPAT) generates an Accessibility Conformance Report (ACR). Required for government procurement (Section 508) and increasingly requested by enterprise buyers.

**VPAT Structure**
- Product description and version
- Evaluation methods used (tools, manual testing, assistive technology)
- WCAG 2.1 AA criteria table with conformance level per criterion:
  - Supports: fully meets the criterion
  - Partially Supports: some functionality meets, some does not
  - Does Not Support: majority of functionality does not meet
  - Not Applicable: criterion is not relevant to the product
- Remarks explaining partial support or workarounds
- Evaluator information and date

**Common VPAT Mistakes**
- Claiming "Supports" without testing (auditors verify claims)
- Not specifying which assistive technologies were tested
- Omitting known issues (dishonesty destroys credibility in procurement)
- Using outdated template versions (use VPAT 2.4 Rev 508 or ITI template)

## Legal Defensibility: "Substantial Compliance"

No court requires 100% WCAG conformance. The legal standard is "substantial compliance" which means:
- Documented ongoing remediation effort
- Prioritized critical barriers are addressed
- Conformance roadmap with realistic timelines
- Regular re-auditing schedule (annually minimum)
- Accessible alternative pathways for known gaps (phone support, email)
- Published accessibility statement with contact information

What triggers lawsuits: complete inaction, overlay-only "solutions", ignoring demand letters, no accessibility statement, and zero evidence of remediation effort.

## Regression Testing Strategy

**CI Integration with axe-core**
```
# package.json script
"test:a11y": "axe-core --exit --tags wcag2a,wcag2aa --exclude .third-party"
```

**Threshold Configuration**
- New projects: zero violations allowed (gate on any failure)
- Legacy projects: set baseline count, gate on regressions (new violations above baseline)
- Track violation count over time; require monotonic decrease

**What to Gate On**
- Gate (block deploy): Critical/Major severity, Level A violations
- Warn (allow deploy): Minor severity, Level AA nice-to-haves
- Ignore: Known false positives (document in exclusion list with justification)

**Regression Patterns That Slip Through**
- New component added without keyboard support (no existing test covers it)
- CSS refactor removes focus styles from specific elements
- Third-party library update breaks ARIA attributes
- Dynamic content loaded after axe scan completes (test after interactions, not just page load)
- Dark mode introduced without re-checking contrast ratios

## Third-Party Content Liability

You are generally responsible for accessibility of:
- Embedded iframes you control
- Third-party widgets you chose to integrate (chat, analytics overlays)
- Social media embeds (provide accessible alternatives)
- Payment processors (choose vendors with ACRs -- Stripe, Braintree publish them)
- Video players (use accessible players; ensure captions exist)

You are NOT typically responsible for:
- Content in user-generated iframes you do not control
- External sites linked from your page
- Browser or OS-level assistive technology bugs

Gray area: CMS-authored content. Train content authors on accessibility (alt text, heading hierarchy, link text). Provide authoring tools that enforce or prompt for accessibility metadata.

## Remediation Prioritization Framework

Plot each finding on a 2x2 matrix:

| | Low Effort | High Effort |
|---|-----------|-------------|
| **High Impact** | DO FIRST: alt text, lang attribute, form labels, color contrast | PLAN NEXT: keyboard navigation overhaul, custom widget rebuild |
| **Low Impact** | BATCH FIX: redundant ARIA cleanup, heading hierarchy | DEFER: complex data visualization alternatives, legacy PDF remediation |

Always fix P0 (Critical) issues first regardless of effort. Within the same priority, favor fixes that affect the most users or the most critical user flows.
