---
name: find-bugs
description: Use when asked to review code changes for bugs, find security vulnerabilities, audit code quality on a branch, or perform a security review of local changes. Also triggered by: "review my changes," "check for bugs," "security audit," "code review this branch." NEVER for style-only reviews, formatting checks, or reviewing code that has not been changed in the current branch.
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Find Bugs

Review changes on this branch for bugs, security vulnerabilities, and code quality issues.

## Rationalization Table

Excuses that lead to incomplete reviews. Recognize them and reject them.

| Rationalization | Why It Is Wrong |
|---|---|
| "The diff is small, so there probably aren't any issues." | Small changes introduce critical bugs constantly -- size is not a proxy for safety. |
| "I already know this framework handles X securely." | Framework defaults are regularly misconfigured or overridden by the changed code. |
| "The user just wants a quick look, not a full audit." | A partial audit with unexamined files is worse than no audit -- it creates false confidence. |
| "This file looks like boilerplate, I can skip it." | Boilerplate is frequently the source of injections, hardcoded secrets, and missing auth checks. |
| "I checked the main logic path -- the edge cases are probably fine." | Business logic bugs live almost exclusively in edge cases, not happy paths. |
| "There are no user inputs in this file, so security checks don't apply." | Internal functions are called with attacker-controlled data passed from layers above. |
| "I found two real issues -- that's enough to report." | The review is not complete until every phase and every checklist item has been evaluated. |
| "The tests cover this, so I don't need to review it carefully." | Tests confirm what was tested, not what was missed. Review independently of test coverage. |

## Red Flags Checklist

Observable signs that this skill is being violated. Stop and correct before proceeding.

- [ ] One or more files in the diff were not individually examined
- [ ] Attack surface mapping was skipped or abbreviated for any file
- [ ] Phase 3 security checklist items were left unchecked without a stated reason
- [ ] The verification phase (Phase 4) was skipped for any reported issue
- [ ] The pre-conclusion audit (Phase 5) was skipped or partially completed
- [ ] Issues were reported without citing evidence that they are real and unfixed
- [ ] "No issues found" was reported without explicitly clearing every checklist item
- [ ] Issues were invented or inflated to appear thorough
- [ ] The severity scale was used inconsistently across findings
- [ ] Stylistic or formatting issues were included in the report
- [ ] The review was stopped before all modified files were listed and confirmed read
- [ ] Surrounding context was not read to verify a potential issue

## NEVER List

| Prohibition | Why |
|---|---|
| NEVER skip any file that appears in the diff | Every unread file is an unaudited attack surface. |
| NEVER report findings without completing Phase 4 verification | Unverified issues produce noise and erode trust in the review. |
| NEVER invent issues or exaggerate severity to appear thorough | False positives waste developer time and conceal real risk. |
| NEVER report "no issues found" without explicitly clearing each Phase 3 checklist item | A clean report without a completed checklist is unverified, not safe. |
| NEVER make code changes -- report findings only | Changes without explicit user decision bypass the developer's review authority. |
| NEVER assume a file is safe based on its name, size, or apparent purpose | Assumption-based skips are the primary source of missed vulnerabilities. |

---

## Phase 1: Complete Input Gathering

1. Get the FULL diff: `git diff master...HEAD`
2. If output is truncated, read each changed file individually until you have seen every changed line
3. List all files modified in this branch before proceeding

## Phase 2: Attack Surface Mapping

For each changed file, identify and list:

* All user inputs (request params, headers, body, URL components)
* All database queries
* All authentication/authorization checks
* All session/state operations
* All external calls
* All cryptographic operations

## Phase 3: Security Checklist (check EVERY item for EVERY file)

* [ ] **Injection**: SQL, command, template, header injection
* [ ] **XSS**: All outputs in templates properly escaped?
* [ ] **Authentication**: Auth checks on all protected operations?
* [ ] **Authorization/IDOR**: Access control verified, not just auth?
* [ ] **CSRF**: State-changing operations protected?
* [ ] **Race conditions**: TOCTOU in any read-then-write patterns?
* [ ] **Session**: Fixation, expiration, secure flags?
* [ ] **Cryptography**: Secure random, proper algorithms, no secrets in logs?
* [ ] **Information disclosure**: Error messages, logs, timing attacks?
* [ ] **DoS**: Unbounded operations, missing rate limits, resource exhaustion?
* [ ] **Business logic**: Edge cases, state machine violations, numeric overflow?

## Phase 4: Verification

For each potential issue:

* Check if it is already handled elsewhere in the changed code
* Search for existing tests covering the scenario
* Read surrounding context to verify the issue is real

## Phase 5: Pre-Conclusion Audit

Before finalizing, you MUST:

1. List every file you reviewed and confirm you read it completely
2. List every checklist item and note whether you found issues or confirmed it is clean
3. List any areas you could NOT fully verify and why
4. Only then provide your final findings

## Output Format

**Prioritize**: security vulnerabilities > bugs > code quality

**Skip**: stylistic/formatting issues

For each issue:

* **File:Line** -- Brief description
* **Severity**: Critical/High/Medium/Low
* **Problem**: What's wrong
* **Evidence**: Why this is real (not already fixed, no existing test, etc.)
* **Fix**: Concrete suggestion
* **References**: OWASP, RFCs, or other standards if applicable

If you find nothing significant, say so -- don't invent issues.

Do not make changes -- just report findings. I'll decide what to address.
