# Threat Modeling Guide

Load when performing threat modeling, assessing attack surface for a new feature, or evaluating the security architecture of an application before code review.

## When to Threat Model

| Trigger | Scope | Depth |
|---|---|---|
| New application or service | Full architecture | STRIDE on every component and data flow |
| New feature with authentication/authorization | Feature + adjacent components | Focus on trust boundaries the feature crosses |
| External API integration | Integration surface + data flows | Focus on data exposure, credential management, injection vectors |
| Infrastructure change (new cloud service, container, deployment target) | Infrastructure layer | Focus on network boundaries, IAM, secrets exposure |
| Post-incident (after a security event) | Affected component + blast radius | Reconstruct attacker path, identify missed threats |

## STRIDE Methodology Applied

| Category | Threat | Question to Ask | Common Findings |
|---|---|---|---|
| **S**poofing | Can an attacker pretend to be someone else? | "What authenticates this entity?" | Missing auth on internal APIs, JWT without signature validation, API keys in query params (logged by proxies) |
| **T**ampering | Can an attacker modify data in transit or at rest? | "What ensures this data hasn't been changed?" | Unsigned webhooks, unvalidated file uploads, missing checksums on downloads, TOCTOU race conditions |
| **R**epudiation | Can an attacker deny performing an action? | "Can we prove who did what and when?" | Missing audit logs on destructive actions, logs without user identity, mutable log storage |
| **I**nformation Disclosure | Can an attacker access data they shouldn't? | "What protects this data from unauthorized access?" | Verbose error messages, IDOR on API endpoints, debug endpoints in production, GraphQL introspection enabled |
| **D**enial of Service | Can an attacker make the system unavailable? | "What limits resource consumption per request/user?" | Missing rate limiting, unbounded queries (SELECT without LIMIT), regex ReDoS, synchronous file processing |
| **E**levation of Privilege | Can an attacker gain higher access than intended? | "What enforces this user's permission boundary?" | Role checks only on frontend, mass assignment on update endpoints, JWT claim manipulation, path traversal |

## Trust Boundary Identification

| Boundary Type | What Crosses It | Threat Focus |
|---|---|---|
| Client -> Server | User input, auth tokens, file uploads | Input validation, authentication, CSRF, XSS |
| Server -> Database | Queries, stored procedures | SQL injection, connection credential exposure, privilege escalation |
| Server -> External API | API keys, user data, request parameters | Credential exposure, SSRF, data leakage in error responses |
| Server -> Server (microservices) | Service tokens, internal payloads | Confused deputy, lateral movement, missing mTLS |
| CI/CD -> Production | Deployment artifacts, secrets, configuration | Supply chain injection, secret exposure in build logs, unsigned artifacts |
| User -> Admin boundary | Role claims, permission tokens | Privilege escalation, forced browsing, IDOR on admin endpoints |

**Trust boundary rule**: Every time data crosses a trust boundary, it must be validated on the RECEIVING side. Trusting the sender is the root cause of most security vulnerabilities. Even "internal" services get compromised.

## Attack Surface Enumeration

For each component, enumerate:

| Surface | What to Catalog | Why |
|---|---|---|
| Network endpoints | Every port, protocol, and URL path exposed | Unused endpoints are forgotten but still attackable |
| Authentication mechanisms | How each endpoint verifies identity | Inconsistent auth (some endpoints skip checks) is a top finding |
| Data inputs | Every field, parameter, header, cookie the application reads | Each input is a potential injection vector |
| Data outputs | Every response field, log entry, error message | Each output is a potential information disclosure |
| File operations | Every file read, write, upload, download | Each is a potential path traversal or upload abuse vector |
| Third-party dependencies | Every library, API, CDN, and external service | Each is a supply chain attack surface |
| Configuration | Every environment variable, config file, feature flag | Misconfiguration is the #3 OWASP category (2021) |

## Threat Prioritization

| Factor | Weight | Scale |
|---|---|---|
| Exploitability | High | How easy is it to exploit? (Script kiddie, skilled attacker, nation-state) |
| Impact | High | What happens if exploited? (Data breach, service disruption, financial loss) |
| Affected users | Medium | How many users are impacted? (One user, subset, all users) |
| Discoverability | Medium | How easily can an attacker find this? (Visible in source, requires reconnaissance, requires insider knowledge) |
| Reproducibility | Low | Can the exploit be automated/repeated? (One-shot, repeatable, automatable) |

**Prioritization pitfall**: Don't deprioritize low-exploitability threats just because they're hard to exploit today. Chained vulnerabilities combine low-severity findings into critical exploits. A "low" IDOR + a "low" information disclosure = a "critical" data breach.

## Common Threat Modeling Failures

| Failure | What Goes Wrong | Prevention |
|---|---|---|
| Scope creep | Model tries to cover everything, finishes nothing | Set explicit boundaries: "This model covers the payment flow only" |
| Assumes trusted inputs | Internal APIs, admin panels, or CI/CD pipelines marked as "trusted" without analysis | EVERY trust boundary gets STRIDE analysis. "Internal" doesn't mean "trusted." |
| One-time exercise | Threat model created at design time, never updated as code changes | Re-model when: new external integration, auth changes, data flow changes, post-incident |
| No developer involvement | Security team models alone without input from developers who know the actual implementation | Developers identify implementation-specific threats (race conditions, caching bugs, ORM quirks) that architecture diagrams miss |
| Focuses only on external threats | Insider threats, supply chain attacks, and compromised dependencies ignored | Include at least one "what if an attacker compromises a developer's machine?" scenario |
| Ignores business logic | All technical threats covered, but business logic abuse (coupon stacking, refund fraud, rate abuse) missed | Add a "business logic abuse" category to STRIDE -- what can a legitimate user do that harms the business? |

## Business Logic Security Threats

These are NOT covered by OWASP Top 10 or standard STRIDE but are frequently exploited:

| Threat | Example | Detection |
|---|---|---|
| Race condition abuse | Double-submit payment, withdraw more than balance by timing concurrent requests | Use database-level locks or optimistic locking for financial operations. Test with concurrent requests. |
| Coupon/promo stacking | Applying multiple exclusive discounts by manipulating request order | Enforce exclusivity server-side in a single transaction. Don't rely on frontend disabling the input. |
| Referral fraud | User creates multiple accounts to earn referral bonuses for themselves | Track device fingerprints, IP addresses, and payment methods across "different" referrals |
| Feature abuse as DoS | Legitimate feature (export, search, report generation) used to overload the system | Rate limit expensive operations per-user. Set timeouts on long-running queries. |
| Account enumeration via behavior | Different error messages for "user not found" vs "wrong password" | Use identical responses and timing for all auth failures. Add artificial delay to match worst-case timing. |
| Privilege persistence | User's role downgraded but cached permissions still allow access | Invalidate ALL sessions and tokens on role change. Don't cache permissions longer than the auth token lifetime. |
