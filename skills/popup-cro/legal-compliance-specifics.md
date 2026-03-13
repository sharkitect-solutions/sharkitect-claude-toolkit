# Popup Legal Compliance Specifics

Load when the user's site targets EU, UK, California, or Canadian audiences, when implementing cookie consent popups, when adding email capture popups to regulated industries, or when the user asks about Google's mobile interstitial penalty. Also load when the user reports organic traffic drops after adding popups. Do NOT load for popup copy optimization or trigger timing strategy unrelated to compliance.

## Google Intrusive Interstitials: The Exact Rules

### What Google Penalizes (Mobile Only)

Google's "intrusive interstitials" signal was introduced January 10, 2017, and expanded as part of the Page Experience Update (2021) and subsequent 2024 updates.

| Popup Behavior | Penalized? | Google's Stated Reason |
|---|---|---|
| Full-screen modal before any user interaction on mobile | YES | "Content is not easily accessible to the user on the transition from search results" |
| Modal that covers majority of page on initial load (mobile) | YES | Same -- user cannot see the content they searched for |
| Above-fold layout where standalone interstitial must be dismissed to access content | YES | User must take action before seeing any content |
| Popup triggered AFTER first user interaction (scroll, tap, 30s+) | NO | User has already accessed and begun consuming content |
| Banner using <15% of screen real estate | NO | Google considers this "reasonable" -- not blocking content access |
| Cookie/consent banner (any size, including full-screen) | NO | Legal obligation exemption. GDPR, ePrivacy, and similar laws require consent collection |
| Age verification interstitial | NO | Legal obligation exemption |
| Login dialog for paywalled content (member-only sites) | NO | First-click-free is gone. Paywalls are not penalized |
| App install banner (if system-provided, not custom) | Depends | Chrome's own app install banner: NO. Custom "Download our app" modal: YES if it covers content |

### The Penalty Mechanism

| Aspect | Detail |
|---|---|
| Scope | Mobile rankings ONLY. Desktop rankings are unaffected |
| Severity | Page-level, not site-level. Only pages with intrusive interstitials are demoted |
| Recovery time | Removing the interstitial leads to recovery within 1-2 crawl cycles (days to weeks, not months) |
| Detection method | Googlebot renders pages with a mobile viewport. If a modal covers >50% of viewport in the rendered screenshot, the signal is triggered |
| Workaround | Delay popup until after ANY user interaction event (scroll, click, or 30s+ time on page). This is technically compliant -- Google's own documentation says "on the transition from the search result" |

### How CRO Tools Handle This

| Tool | Default Behavior | Google Compliance |
|---|---|---|
| OptinMonster | Page-load triggers available but flagged as "not recommended for mobile" | User must manually set mobile trigger to scroll/time delay |
| Sumo/SumoMe | Default shows on page load | User must configure mobile-specific delay |
| Privy | Separate mobile/desktop trigger settings | Defaults to time delay on mobile |
| Sleeknote | Auto-detects mobile and applies Google-safe timing | Compliant by default |
| ConvertFlow | Offers "Google-safe mode" toggle | Must be explicitly enabled |

## EU: ePrivacy Directive + GDPR + Digital Services Act

Three overlapping EU regulations affect popups.

### Cookie Consent (ePrivacy Directive 2002, updated 2009)

| Requirement | What It Means for Popups |
|---|---|
| Prior consent required for non-essential cookies | Marketing cookies (tracking pixels, analytics, personalization) require explicit opt-in BEFORE setting cookies. A popup tool that sets cookies on load (before consent) violates ePrivacy |
| "Strictly necessary" exemption | Session cookies, load balancers, user preference cookies (like "dismiss this popup" flag) do NOT require consent |
| Consent must be freely given | "Accept all" cannot be the only visible option. Reject must be equally prominent. Pre-checked boxes for consent are banned. Cookie walls ("accept or leave") are banned in most EU jurisdictions (EDPB guidance) |
| Consent is per-purpose | "Marketing cookies" and "Analytics cookies" must be separate choices. Bundling all non-essential cookies into one "Accept" is non-compliant per EDPB Guidelines 05/2020 |

### GDPR Impact on Email Capture Popups

| Requirement | Popup Implementation |
|---|---|
| Lawful basis for processing | Email capture popup must state WHY you're collecting the email and WHAT you'll send. "Subscribe to our newsletter" is insufficient -- state the content type and frequency |
| Right to withdraw | Unsubscribe must be as easy as subscribing. If a 1-click popup captured the email, a 1-click unsubscribe must be provided in every email |
| Data minimization | Capture ONLY what's needed. If you need an email for a newsletter, do NOT require name, phone, company, job title. Each additional field must have a stated purpose |
| Transparency | Link to privacy policy must be visible on or near the popup. Not in 6px footer text -- in a readable, accessible location |
| Children's data (under 16, or under 13 in some member states) | If the site could attract minors, age verification may be required before capturing data. This is relevant for gaming, education, and entertainment sites |

### Digital Services Act (DSA) -- Effective Feb 2024

| DSA Requirement | Popup Impact |
|---|---|
| Ban on "dark patterns" | Guilt-trip decline text ("No, I don't want to save money") is explicitly listed as a dark pattern in DSA Recital 67. Non-compliant |
| Interface fairness | Popup design cannot make one option significantly harder to select than another. "Accept" in large green button + "Reject" in tiny gray text = non-compliant |
| Transparency of advertising | If the popup promotes a paid product or service, it must be clearly identifiable as advertising |
| Profiling restrictions | Behavioral targeting for popup triggers (showing different popups based on user profiling data) requires explicit consent first |

## California: CCPA / CPRA

| Requirement | Popup Implementation |
|---|---|
| "Do Not Sell or Share My Personal Information" link | Must be prominently displayed on the website. If a popup captures data that will be shared with third parties (ad partners, data brokers), the DNSS link must be accessible WITHOUT dismissing the popup first |
| Opt-out mechanism | If popup sets tracking cookies that share data with third parties, California users must be able to opt out. This is separate from cookie consent -- CCPA requires an explicit "Do Not Sell" mechanism |
| Financial incentive disclosure | If the popup offers a discount for email signup, this is a "financial incentive" under CCPA. You must disclose the value of the consumer's data and allow them to withdraw from the incentive at any time |
| Global Privacy Control (GPC) | If a user's browser sends the GPC signal (`Sec-GPC: 1` header), you MUST treat it as an opt-out of sale/sharing. Do NOT show "opt in to tracking" popups to GPC users -- the browser has already communicated their choice. CPRA made GPC legally binding as of Jan 2023 |
| Age verification (under 16) | If you KNOW or have reason to believe a user is under 16, you need opt-IN consent (not just opt-out) before selling their data. Sites that target teens must implement age gates |

## Canada: CASL (Anti-Spam Law)

| Requirement | Popup Implementation |
|---|---|
| Express consent required | Email capture popups must use explicit opt-in. Pre-checked checkboxes violate CASL. The user must actively check a box or click a button that clearly states "I agree to receive commercial electronic messages" |
| Identify the sender | The popup must identify who is sending the emails (company name) and include contact information (mailing address or link to it) |
| Unsubscribe mechanism | Every email must include a working unsubscribe link. Must be processed within 10 business days. This applies to the emails sent AFTER popup capture, not the popup itself |
| Implied consent limits | If relying on implied consent (existing business relationship), it expires after 2 years (customer) or 6 months (inquiry). Popup-captured email consent is express and does not expire (but can be withdrawn) |

## Compliance Decision Matrix

| User's Audience | Cookie Consent Popup Required? | Email Capture Rules | "Do Not Sell" Link Required? | Dark Pattern Restrictions |
|---|---|---|---|---|
| US only (non-California) | No federal requirement (check state laws: Colorado, Connecticut, Virginia, Oregon all have privacy laws as of 2025) | CAN-SPAM: opt-out sufficient (no pre-consent needed) | Not required (but state laws expanding) | No federal dark pattern law (FTC enforcement case-by-case) |
| California | Yes (if sharing data with third parties for "sale" under CCPA) | CAN-SPAM + CCPA: opt-out + DNSS link | YES, prominently | FTC Act Section 5 + CCPA |
| EU/EEA | YES (ePrivacy Directive) | GDPR: explicit opt-in, purpose limitation, data minimization | Not applicable (GDPR uses consent/legitimate interest framework) | YES (DSA dark pattern ban) |
| UK | YES (PECR -- UK's ePrivacy equivalent) | UK GDPR: same as EU GDPR | Not applicable | UK equivalent of DSA pending |
| Canada | Not explicitly (PIPEDA covers consent broadly) | CASL: express opt-in required for commercial emails | Not applicable | CASL covers misleading representations |
| Global audience | YES (default to highest standard: EU compliance) | Default to GDPR standard (explicit opt-in) | Include DNSS for California compliance | Follow DSA dark pattern rules |

**The practical default**: If your site has any international traffic, implement GDPR-compliant cookie consent + explicit email opt-in + neutral decline text. This satisfies the strictest jurisdiction and avoids per-region complexity. The only additional requirement for California-targeted sites is the "Do Not Sell" link.
