---
name: security-best-practices
description: "Use when performing security reviews, writing secure-by-default code, generating vulnerability reports, or hardening existing codebases. Also use when the user mentions security audit, secure coding, OWASP, vulnerability assessment, or security best practices. NEVER use for general code review without security focus (use clean-code), penetration testing execution, or compliance certification (use data-privacy-compliance)."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Security Best Practices

Performs language-and-framework-specific security reviews, writes secure-by-default code, and generates prioritized vulnerability reports with actionable fixes.

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| SKILL.md | Security review procedure, depth calibration, cross-language principles, report format, override handling | Always (auto-loaded) |
| threat-modeling-guide.md | STRIDE methodology applied, trust boundary identification, attack surface enumeration, threat prioritization, business logic security threats, common threat modeling failures | When performing threat modeling, assessing attack surface for new features, or evaluating security architecture |
| security-anti-patterns.md | Authentication anti-patterns (7), authorization anti-patterns (7), data handling anti-patterns (7), infrastructure anti-patterns (7), error handling anti-patterns (5), dependency anti-patterns (6) | When reviewing code for security issues, educating developers, or when a review finds vulnerabilities |
| dependency-security-guide.md | Dependency audit procedure, vulnerability triage (CVSS+EPSS), lock file security, update strategies, npm/pip/Go-specific risks, CI/CD pipeline security, SBOM generation | When auditing dependencies, setting up supply chain security, or responding to vulnerability disclosures |
| references/golang-general-backend-security.md | Go backend security patterns | Project uses Go |
| references/javascript-express-web-server-security.md | Express.js server hardening | Project uses Express |
| references/javascript-general-web-frontend-security.md | Frontend security fundamentals | Any web frontend project |
| references/javascript-jquery-web-frontend-security.md | jQuery-specific XSS prevention | Project uses jQuery |
| references/javascript-typescript-nextjs-web-server-security.md | Next.js server security | Project uses Next.js |
| references/javascript-typescript-react-web-frontend-security.md | React frontend security | Project uses React |
| references/javascript-typescript-vue-web-frontend-security.md | Vue frontend security | Project uses Vue |
| references/python-django-web-server-security.md | Django security configuration | Project uses Django |
| references/python-fastapi-web-server-security.md | FastAPI security patterns | Project uses FastAPI |
| references/python-flask-web-server-security.md | Flask security hardening | Project uses Flask |

**Loading rule**: For web applications with both frontend and backend, load BOTH the backend framework guide AND the relevant frontend guide. If the frontend framework is unspecified, load `javascript-general-web-frontend-security.md`.

## Scope Boundary

| This Skill Handles | Defer To |
|---|---|
| Security code review and vulnerability identification | clean-code (general code quality without security focus) |
| Secure-by-default coding patterns | senior-backend (general backend architecture decisions) |
| OWASP Top 10 and framework-specific security | vulnerability-scanner (automated scanning and EPSS-based triage) |
| Threat modeling and attack surface analysis | data-privacy-compliance (GDPR/HIPAA/SOC2 compliance frameworks) |
| Dependency and supply chain security | docker-expert (container security and image hardening) |
| Security report generation | senior-architect (system-level architecture review) |

## Security Review Procedure

1. **Identify the stack**: Inspect the project for ALL languages and frameworks -- check `package.json`, `requirements.txt`, `go.mod`, directory structure, and import statements. List your evidence.
2. **Load reference files**: Read ALL reference files matching the detected stack from the File Index above. For full-stack apps, load both frontend and backend guides.
3. **Select operating mode** based on the trigger:
   - **Passive mode** (default when writing code): Apply security patterns from reference files to all new code. Flag critical vulnerabilities found in existing code as you encounter them.
   - **Active review mode** (user requests security review): Full audit against all reference file guidance. Produce a prioritized report.
   - **Report mode** (user requests vulnerability report): Generate `security_best_practices_report.md` with executive summary, findings by severity, line numbers, and impact statements.
4. **Prioritize findings** by severity: Critical (exploitable, data exposure) > High (privilege escalation, injection) > Medium (misconfiguration, weak defaults) > Low (best practice deviation, hardening opportunity).
5. **Implement fixes** one finding at a time. Consider second-order impacts -- insecure code is often relied on elsewhere. Test after each fix. Clear commit messages referencing the specific finding ID.

## Review Depth Calibration

| Trigger | Depth | Focus |
|---------|-------|-------|
| Writing new code in an existing project | Passive -- apply secure defaults from reference files | Input validation, auth patterns, output encoding |
| User says "review security" or "security check" | Active -- audit changed files against reference guidance | Full OWASP Top 10 coverage for the detected stack |
| User requests vulnerability report | Report -- comprehensive audit of entire codebase scope | All findings with severity, line numbers, fix recommendations |
| Quick fix on a single file | Passive -- scan the file for critical issues only | Injection, auth bypass, secrets exposure |

## Cross-Language Security Principles

These apply regardless of framework. Framework-specific rules in reference files override these when they conflict.

| Principle | Implementation | Why |
|-----------|---------------|-----|
| Never use incrementing IDs for public resources | UUID4 or random hex for any externally-exposed ID | Prevents enumeration attacks and leaks resource count |
| Validate all external input at system boundaries | Whitelist validation on user input, API responses, file reads | Injection and type confusion attacks exploit unvalidated input |
| Secrets never in code or env-committed files | Use secrets management (vault, env vars loaded at runtime, Docker secrets) | Secrets in code persist in git history even after deletion |
| Parameterize all database queries | Use ORM query builders or parameterized statements -- never string concatenation | SQL injection remains the #1 exploited vulnerability class |
| Output encode for the destination context | HTML-encode for DOM, URL-encode for query params, JSON-encode for API responses | XSS exploits output that reaches the browser unencoded |
| Principle of least privilege | Minimal permissions for DB users, API keys, file access, container users | Limits blast radius when a component is compromised |

## Report Format

When generating a report, write to `security_best_practices_report.md` (or user-specified location):

1. **Executive summary** (3-5 sentences): total findings, critical count, overall risk posture
2. **Findings by severity** (Critical > High > Medium > Low): each with numeric ID, one-sentence impact statement (critical only), affected file and line numbers, recommended fix
3. **After writing**: summarize findings to the user directly, offer to explain any finding, then ask if they want to begin fixes

Fix one finding at a time. Confirm no regressions after each fix. Follow the project's commit and testing conventions.

## Override Handling

Project documentation or user instructions may override specific security practices. When overriding:
- Apply the override without arguing
- Optionally note the security trade-off once
- Suggest documenting the override reason in project files for future reference

## TLS and Cookie Caveats

- Do NOT report lack of TLS as a finding -- most dev environments use TLS proxies out of scope
- `Secure` cookie flag breaks non-TLS environments -- gate it behind a production/TLS flag
- Do NOT recommend HSTS unless the user explicitly understands its permanent browser-caching implications -- HSTS misconfiguration causes major outages

## Rationalization Table

| Rationalization | Why It Fails |
|---|---|
| "This is just a prototype, security doesn't matter yet" | Prototypes become production code; insecure patterns established early persist because refactoring is deferred indefinitely |
| "The framework handles security automatically" | Frameworks provide defaults, not guarantees; misconfiguration, custom endpoints, and raw queries bypass framework protections |
| "We'll add security in the next sprint" | Security debt compounds faster than technical debt; each insecure endpoint is an active attack surface, not a future TODO |
| "Only internal users will access this" | Internal tools get exposed through VPN splits, contractor access, lateral movement after breach; internal != trusted |
| "I already know the common vulnerabilities" | Knowledge of vulnerabilities doesn't prevent them -- structured reference checklists catch what tired developers miss |
| "The input is always clean because we control the client" | Clients can be bypassed with curl, browser devtools, or a compromised frontend; server-side validation is mandatory |

## Red Flags

- No input validation on any API endpoint -- every external input must be validated server-side
- SQL queries built with string concatenation or f-strings instead of parameterized queries
- Secrets (API keys, database passwords) hardcoded in source files or committed .env files
- Application running as root in production containers
- CORS configured with `*` wildcard on authenticated endpoints
- Authentication tokens stored in localStorage instead of httpOnly cookies
- Error messages exposing stack traces, file paths, or database schema to end users
- No rate limiting on authentication endpoints (login, password reset, OTP verification)

## NEVER

- Report lack of TLS or recommend HSTS without explicit user understanding of the implications
- Skip loading the framework-specific reference file when one exists for the detected stack
- Bundle multiple unrelated security fixes into a single commit -- each finding gets its own commit
- Apply a security fix without considering whether it breaks existing functionality -- insecure code is often load-bearing
- Generate a vulnerability report without including specific file paths and line numbers for each finding
