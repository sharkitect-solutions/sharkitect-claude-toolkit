---
name: Data Privacy Compliance
description: >
  Use when building systems that collect, store, or process personal data and the user
  needs to determine which regulations apply, choose a lawful basis for processing,
  structure data processing agreements, handle cross-border transfers, or respond to
  data breaches. Use when privacy architecture decisions have enforcement consequences.
  NEVER for general security hardening without a privacy component. NEVER for
  cookie banner HTML/CSS implementation (use frontend skills). NEVER for HIPAA
  clinical workflow design (use healthcare-specific skills).
---

# Data Privacy Compliance

Expert decision layer for privacy regulation applicability, lawful basis selection,
enforcement risk assessment, and compliance architecture. This skill provides the
judgment Claude lacks by default -- what regulators actually enforce, where companies
actually get fined, and which compliance choices create real protection vs privacy theater.

## Regulation Applicability Decision Tree

Work through these questions IN ORDER. Stop at the first regulation that applies.
Multiple regulations often apply simultaneously -- do not stop after finding one.

```
Q1: Does the system process data about people in the EU/EEA/UK?
  YES --> GDPR applies (regardless of where your company is located)
  NO  --> Continue

Q2: Does the system process data about California residents AND does the
    business meet ANY threshold: $25M+ revenue, 100K+ consumers/households,
    OR 50%+ revenue from selling/sharing personal information?
  YES --> CCPA/CPRA applies
  NO  --> Continue

Q3: Does the system handle Protected Health Information AND is the entity
    a covered entity or business associate under US law?
  YES --> HIPAA applies
  NO  --> Continue

Q4: Does the system process data about residents of Brazil, Canada,
    Australia, Japan, South Korea, or other countries with data protection laws?
  YES --> Check country-specific regulation (LGPD, PIPEDA, APPs, APPI, PIPA)
  NO  --> No specific regulation, but apply privacy-by-design principles anyway

CRITICAL: If you answered YES to Q1, also check Q2-Q4. A SaaS company with
EU and California users is subject to BOTH GDPR and CCPA simultaneously.
The stricter requirement wins for overlapping obligations.
```

## Lawful Basis Selection (The Decision That Determines Everything)

Choosing the wrong lawful basis is the #1 GDPR mistake. It cannot be changed
retroactively. Choose BEFORE processing begins.

```
CONSENT
  Use when: User has genuine free choice, can refuse without consequence,
            and you can implement easy withdrawal
  Classic fit: Marketing emails, analytics cookies, newsletter signup
  Trap: If the user MUST consent to use your service, consent is not freely
        given and is INVALID. Use "contract" instead.
  Enforcement reality: Irish DPC fined Meta EUR 390M (Jan 2023) for claiming
        consent when users had no real choice

CONTRACT
  Use when: Processing is genuinely necessary to deliver the service the
            user signed up for
  Classic fit: Processing shipping address to deliver an order, storing
               login credentials for account access
  Trap: "Necessary" means the contract literally cannot be performed without
        this processing. Targeted ads are NOT necessary for social media.

LEGITIMATE INTEREST
  Use when: You have a real business need, impact on individuals is minimal,
            and they would reasonably expect the processing
  Classic fit: Fraud detection, network security, internal analytics
  REQUIRES: Documented Legitimate Interest Assessment (LIA) with three-part test:
    1. Purpose test: Is the interest real and lawful?
    2. Necessity test: Is this processing actually needed for that interest?
    3. Balancing test: Do individual rights override your interest?
  Trap: Companies use legitimate interest as a lazy alternative to consent.
        Regulators see right through this. If you skip the LIA, expect fines.
  Enforcement reality: Norwegian DPA fined Grindr EUR 6.5M for claiming
        legitimate interest for ad tracking without a proper LIA

LEGAL OBLIGATION
  Use when: A law requires you to process this data
  Classic fit: Tax records, anti-money-laundering checks, employment law
  Trap: Must cite the SPECIFIC law. "Regulatory compliance" is not specific enough.

PUBLIC INTEREST / VITAL INTEREST
  Use when: Government functions, medical emergencies
  Almost never applies to commercial software. Do not use as a shortcut.
```

## Rationalization Table

| What teams say | What is actually true | Correct approach |
|---|---|---|
| "We need all this data for analytics" | Data minimization requires collecting only what is necessary for the stated purpose. "Analytics" is not a purpose -- name the specific business question. | Define exact metrics needed. Collect only the fields those metrics require. Aggregate or anonymize within 30 days. |
| "Legitimate interest covers our tracking" | Without a documented LIA, legitimate interest claims fail enforcement. Tracking across sites almost never passes the balancing test. | Conduct a formal three-part LIA. If tracking is cross-site or involves profiling, use consent instead. |
| "Our privacy policy covers us" | A privacy policy is a disclosure document, not a legal shield. It does not create consent or establish a lawful basis. | Privacy policy PLUS a lawful basis for each processing activity PLUS proper consent mechanisms where consent is the basis. |
| "We anonymize the data so GDPR does not apply" | Pseudonymization is not anonymization. If data can be re-identified with reasonable effort, it is still personal data. True anonymization is irreversible. | Use k-anonymity testing: if any combination of quasi-identifiers maps to fewer than 5 individuals, it is not anonymous. |
| "Users agreed to our Terms of Service" | ToS acceptance is not GDPR consent. Consent must be specific, informed, freely given, and withdrawable. Bundled consent in ToS is invalid. | Separate consent from ToS. Each processing purpose gets its own opt-in. Never gate service access on non-essential consent. |
| "We are a US company so GDPR does not apply" | GDPR applies based on WHERE THE DATA SUBJECTS ARE, not where the company is. Processing EU resident data triggers GDPR regardless of company location. | If you have EU users, you are subject to GDPR. Appoint an EU representative (Art. 27) if you have no EU establishment. |
| "Our vendor handles compliance for us" | Data controllers cannot delegate compliance responsibility. You remain liable for your processors' failures. | Execute a proper DPA with every vendor. Audit their compliance. You are jointly liable if they breach. |
| "We only need a cookie banner" | Cookie consent is one small piece. Without lawful basis documentation, processing records, DSAR procedures, and breach response plans, you are exposed. | Cookie consent is step 1 of approximately 40. Build the full compliance program. |

## NEVER List

1. NEVER use pre-ticked checkboxes for consent -- this violates GDPR Art. 7 and was explicitly ruled invalid by the CJEU in Planet49 (Case C-673/17)
2. NEVER bundle consent for multiple purposes into a single checkbox -- each purpose requires separate, granular consent
3. NEVER treat cookie walls ("accept all or leave") as valid consent in the EU -- French CNIL and Austrian DSB have fined for this pattern repeatedly
4. NEVER store raw consent timestamps without the full consent record (what was shown, what was selected, version of notice) -- you must prove WHAT was consented to, not just WHEN
5. NEVER assume "delete" means only the primary database -- deletion requests require removing data from backups, analytics pipelines, third-party processors, CDNs, logs, and data warehouses
6. NEVER send a data subject access request response containing OTHER people's data -- redact third-party personal data before sending. This is a common breach source.
7. NEVER rely on Privacy Shield for EU-US transfers -- it was invalidated by Schrems II (July 2020). Use the EU-US Data Privacy Framework (adopted July 2023) only if your organization is certified, otherwise use SCCs.
8. NEVER start processing before documenting the lawful basis -- GDPR requires this determination BEFORE processing begins. Retroactive basis selection is explicitly prohibited.
9. NEVER use "we take your privacy seriously" as a substitute for specific disclosures -- regulators treat vague language as a transparency violation
10. NEVER assume encryption alone satisfies GDPR security requirements -- Art. 32 requires appropriate technical AND organizational measures, including access controls, regular testing, and staff training

## Enforcement Reality Table

What regulators actually fine for vs what companies spend their compliance budget on.

| What companies worry about | Fine frequency | What regulators actually fine for | Fine severity |
|---|---|---|---|
| Cookie banner design | LOW | Insufficient lawful basis for processing | VERY HIGH (Meta EUR 1.2B, Amazon EUR 746M) |
| Privacy policy wording | LOW | Lack of transparency in actual data practices | HIGH (Google EUR 150M by French CNIL) |
| Data breach technical details | MEDIUM | Late or incomplete breach notification | HIGH (British Airways GBP 20M, Marriott GBP 18.4M) |
| DSAR response format | LOW | Failure to respond to DSARs within deadline | MEDIUM |
| Employee training records | LOW | No lawful basis documented for processing activities | VERY HIGH |
| Consent banner UX | MEDIUM | Dark patterns that manipulate consent | HIGH (Epic Games USD 520M FTC, though not GDPR) |
| Vendor security audits | LOW | Missing or inadequate Data Processing Agreements | MEDIUM-HIGH |
| Data retention schedules | LOW | Processing data beyond stated retention period | MEDIUM |

Key insight: 80% of major GDPR fines stem from just two issues -- insufficient lawful
basis and lack of transparency. Companies over-invest in cookie banners and
under-invest in lawful basis documentation and processing records.

## Data Processing Agreements: The 5 Clauses Vendors Get Wrong

When reviewing or drafting DPAs, focus on these failure points:

1. **Sub-processor notification**: The DPA must require the processor to notify you
   BEFORE engaging new sub-processors, not after. Many vendor templates say "we may
   use sub-processors" with no notification mechanism. This fails Art. 28(2).

2. **Audit rights**: "We will provide a SOC 2 report annually" is NOT sufficient audit
   rights. The controller must have the right to conduct or commission audits of the
   processor's facilities and practices. Accept SOC 2 as a practical alternative, but
   the CONTRACT must preserve direct audit rights.

3. **Data return/deletion on termination**: The DPA must specify BOTH return and deletion
   of data after the contract ends, with a specific timeline (30 days is standard).
   Many vendor DPAs say "data will be deleted in accordance with our retention policy"
   which gives the vendor unilateral control.

4. **International transfer mechanisms**: If the processor operates outside the EU, the
   DPA must specify the transfer mechanism (SCCs, adequacy decision, or BCRs). "Data
   may be processed globally" without specifying safeguards violates Chapter V GDPR.

5. **Breach notification timeline**: The processor must notify the controller "without
   undue delay" after becoming aware of a breach. Many vendor DPAs say "within 72
   hours" -- but that is the controller's deadline to notify the DPA, not the
   processor's deadline to notify the controller. Processors should notify within
   24-48 hours to give the controller time to assess and report.

## Cross-Border Data Transfers Post-Schrems II

Decision framework for transferring personal data outside the EU/EEA:

```
Is the destination country on the EU adequacy list?
  YES --> Transfer permitted without additional safeguards
          Adequate countries (as of 2024): Andorra, Argentina, Canada (PIPEDA),
          Faroe Islands, Guernsey, Israel, Isle of Man, Japan, Jersey,
          New Zealand, Republic of Korea, Switzerland, UK, Uruguay,
          EU-US Data Privacy Framework (for certified US companies only)
  NO  --> Continue

Is the US recipient certified under the EU-US Data Privacy Framework?
  YES --> Transfer permitted (replaces Privacy Shield, adopted July 2023)
          VERIFY certification at dataprivacyframework.gov before relying on this
  NO  --> Continue

Can you implement Standard Contractual Clauses (SCCs)?
  YES --> Use the June 2021 SCCs (old 2010 SCCs are expired)
          You MUST also conduct a Transfer Impact Assessment (TIA):
          - Does destination country law allow government access to data?
          - Are supplementary measures needed? (encryption, pseudonymization)
          - Document the assessment even if risk is low
  NO  --> Continue

Does the recipient have approved Binding Corporate Rules?
  YES --> Transfer permitted within the corporate group covered by BCRs
  NO  --> Transfer is likely not permissible. Consider data localization.
```

## The 72-Hour Breach Response Decision Tree

When a breach is detected, work through this immediately:

```
HOUR 0-4: CONTAIN AND CLASSIFY
  1. Stop the breach (isolate systems, revoke credentials, block access)
  2. Classify: Does the breach involve personal data?
     NO  --> Security incident, not a data breach. Handle via security procedures.
     YES --> Continue

HOUR 4-24: ASSESS RISK
  3. What type of data? (Names, emails, financial, health, children's data, ID numbers)
  4. How many individuals affected?
  5. Was the data encrypted? Was the key also compromised?
  6. Can affected individuals be identified?
  7. Is there evidence of actual access/exfiltration, or just exposure?

RISK ASSESSMENT:
  Data was encrypted AND key was NOT compromised
    --> Likely NO notification required (recital 87: unintelligible data)
  Data is low-sensitivity AND small number of people AND no evidence of access
    --> Document internally, likely no DPA notification required
  ANY sensitive data (health, financial, children, ID numbers) OR large scale
    --> Notify supervisory authority within 72 hours
  HIGH risk to individuals (identity theft likely, financial data exposed)
    --> Notify BOTH supervisory authority AND affected individuals directly

HOUR 24-72: NOTIFY IF REQUIRED
  Notification to supervisory authority must include:
  - Nature of breach and categories of data
  - Approximate number of individuals affected
  - Name and contact details of DPO
  - Likely consequences
  - Measures taken or proposed

  If you cannot gather all information within 72 hours, submit what you have
  and provide remaining information in phases. Late complete notification is
  better than no notification, but worse than timely partial notification.
```

## CCPA vs GDPR: The Differences That Trip Up Dual-Jurisdiction Companies

| Area | GDPR | CCPA/CPRA | Trap |
|---|---|---|---|
| Opt-in vs opt-out | Opt-IN for most processing (consent required first) | Opt-OUT model (processing allowed until consumer objects) | Building a GDPR-compliant opt-in system satisfies CCPA, but a CCPA opt-out system does NOT satisfy GDPR |
| Right to delete exceptions | Narrow exceptions (legal obligation, public interest, legal claims) | Broader exceptions (includes transaction completion, security, internal use compatible with expectations) | CCPA allows more reasons to refuse deletion. Do not assume GDPR exceptions are the same. |
| Private right of action | No direct private action under GDPR (only through supervisory authorities) | Private right of action for data breaches (statutory damages $100-$750 per consumer per incident) | CCPA class actions are a real financial threat. A breach affecting 100K Californians = $10M-$75M exposure |
| Sensitive data | Special categories require explicit consent (Art. 9) | "Sensitive personal information" -- consumers can limit USE, but collection may still occur | GDPR blocks collection entirely without explicit consent. CCPA only gives opt-out of use. |
| Data sales | No specific "sale" concept -- all processing needs a lawful basis | Specific "sale" and "sharing" definitions with dedicated opt-out rights | CCPA "sale" includes exchanging data for ANY valuable consideration, not just money. Ad tracking often qualifies. |

## Privacy Engineering in Practice

### Data Classification (Do This First)

Before any privacy architecture, classify ALL data fields:

- **P1 - Direct identifiers**: Name, email, phone, SSN, passport. Highest protection. Encrypt at rest and in transit. Strict access controls.
- **P2 - Indirect identifiers**: IP address, device ID, cookie ID, location. Can identify with combination. Pseudonymize where possible.
- **P3 - Sensitive**: Health, financial, biometric, political, sexual orientation, union membership, criminal records. Requires explicit consent under GDPR Art. 9.
- **P4 - Non-personal**: Truly anonymized aggregates, public information. No privacy restrictions, but verify anonymization is irreversible.

### Retention Automation

Do not rely on manual deletion. Automate retention with these rules:

- Every data field must have a documented retention period BEFORE collection begins
- Retention clock starts at the trigger event (account closure, last activity, contract end), not at collection time
- "Indefinite" is not a valid retention period. If you truly need data forever, document the specific legal or business justification
- Legal hold overrides must be trackable and auditable
- Backup deletion lags primary deletion -- document the maximum lag and ensure it is reasonable (30 days is standard)

## Before/After Example

**BEFORE (Privacy Theater):**
A SaaS company adds a cookie banner, writes a privacy policy, and considers themselves
GDPR compliant. They use legitimate interest for analytics and marketing. No LIA
documented. Vendors have standard terms but no DPAs. Data retention is "we delete it
when we get around to it." They collect full name, email, phone, company, job title,
IP address, and browsing history for a B2B lead generation tool.

**Risk exposure:** No lawful basis documentation means every processing activity is
a violation. Each undocumented legitimate interest claim is a separate infringement.
Missing DPAs mean joint liability for every vendor's data handling. No retention
schedule means indefinite storage in violation of storage limitation principle.

**AFTER (Expert Approach):**
Same company, restructured:
1. Mapped every data field to a specific, documented purpose
2. Conducted LIA for analytics (passed -- minimal data, reasonable expectation, low impact). Result documented.
3. Switched marketing to consent basis with granular opt-ins
4. Executed DPAs with all 12 vendors, negotiating sub-processor notification and 24-hour breach notification
5. Removed phone number and job title from mandatory fields (not necessary for service delivery)
6. Set retention: active account data kept during subscription + 90 days, marketing consent reviewed annually, analytics aggregated after 26 months
7. Documented Records of Processing Activities (RoPA) covering all 8 processing activities
8. Established DSAR response process with 25-day internal deadline (leaving 5-day buffer before 30-day GDPR deadline)

**Result:** Actual compliance vs compliance theater. The company can demonstrate
accountability under Art. 5(2) because every decision is documented with reasoning.
