---
name: documentation-templates
description: "Use when asked to write, generate, or structure documentation of any kind: READMEs, API docs, changelogs, ADRs, code comments, or llms.txt files. NEVER for writing content that documents a single function inline (use code comment conventions instead)."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
allowed-tools: Read, Glob, Grep
---

# Documentation Templates

## File Index

| File | Purpose |
|------|---------|
| `SKILL.md` | Templates, rules, and behavioral enforcement for all documentation types |

---

## Rationalization Table

These are the excuses Claude makes to skip proper documentation structure. Each one is wrong.

| Excuse | Why It's Wrong |
|--------|----------------|
| "This is a small project, a simple README is fine." | Minimal projects get minimal docs only if the user says so. Default to full structure regardless of project size. |
| "I'll just write prose descriptions for the API -- tables take too long." | Prose API docs are unscannable. Every endpoint gets the parameter table, response codes, and example. No exceptions. |
| "There's already a README, I'll just add a section." | If the existing README is missing sections from the template, surface the gaps and offer to fill them. |
| "The code is self-documenting, comments would be redundant." | Code explains *what*. Comments explain *why*. These are different things. The why is never redundant. |
| "They didn't ask for a changelog." | If the task involves versioning, releases, or change tracking, a changelog is part of the deliverable. Propose it. |
| "I'll do the ADR template but skip the Consequences section -- it's obvious." | Consequences are the entire point of an ADR. Skipping them makes the document useless for future decision-makers. |
| "An llms.txt file is overkill for this project." | If the project has public-facing docs or an API, an llms.txt is 15 lines of work and dramatically improves AI tool compatibility. |

---

## Red Flags

Stop and correct immediately if you see any of these patterns in your own output:

- [ ] README has no Quick Start section -- users cannot run the project in under 5 minutes
- [ ] API doc describes an endpoint in prose without a parameters table
- [ ] Changelog uses free-form text instead of Added / Changed / Fixed / Removed headers
- [ ] ADR is missing the Consequences section
- [ ] Code comment explains *what* the code does instead of *why* it exists
- [ ] JSDoc is present but missing `@throws` when the function can throw
- [ ] llms.txt file is missing the Core Files section
- [ ] Documentation section headers are inconsistent across a multi-file doc set
- [ ] Configuration options documented as prose instead of a table with Name / Description / Default columns
- [ ] Version number in changelog does not match the version in package.json / pyproject.toml / equivalent

---

## NEVER List

- NEVER omit the Consequences section from an ADR. An ADR without consequences is a log entry, not a decision record. Future engineers will repeat the same mistakes.
- NEVER write API docs in paragraph form. Parameters, types, required/optional, and response codes must be in tables. Prose is unscannable under time pressure.
- NEVER write a README that doesn't have a Quick Start. If setup is genuinely complex, the Quick Start links to a detailed setup guide -- it does not disappear.
- NEVER use generic placeholder text in delivered documentation. "Brief description here" and "TODO" entries in a delivered doc are failures, not drafts.
- NEVER document a configuration option without specifying its default value and valid range/type.
- NEVER generate a changelog without a date on each version entry. Undated changelogs are unauditable.
- NEVER add a comment explaining what one line of obvious code does. Comment the algorithm, the business rule, the edge case -- not `i++`.

---

## 1. README Structure

The README is the entry point for every human and AI that encounters this project. It must answer four questions in order: What is this? How do I run it? What can it do? How is it configured?

### Required Sections (in this order)

| Section | Required | Purpose |
|---------|----------|---------|
| Title + one-liner | Yes | Identity. What is this thing? |
| Badges (CI, coverage, version) | Situational | Trust signals for open-source projects |
| Quick Start | Yes | Running in under 5 minutes, no detours |
| Features | Yes | Capability inventory, scannable bullets |
| Configuration | Yes | Every option with name, description, default, valid values |
| API Reference / Docs link | Yes if API exists | Do not inline large API docs into README |
| Contributing | Yes for public repos | Without this, no one contributes correctly |
| License | Yes | Legal clarity |

### README Template

```markdown
# Project Name

One sentence. What this does and who it's for.

## Quick Start

```bash
# Install
npm install project-name

# Configure
cp .env.example .env

# Run
npm start
```

Visit http://localhost:3000.

## Features

- **Feature name**: What it does and why it matters
- **Feature name**: What it does and why it matters

## Configuration

| Variable | Description | Default | Valid Values |
|----------|-------------|---------|--------------|
| `PORT` | HTTP server port | `3000` | 1024-65535 |
| `LOG_LEVEL` | Logging verbosity | `info` | debug, info, warn, error |
| `DB_URL` | Database connection string | None (required) | Valid PostgreSQL URL |

## Documentation

- [API Reference](./docs/api.md)
- [Architecture](./docs/architecture.md)
- [Contributing Guide](./CONTRIBUTING.md)

## License

MIT - see [LICENSE](./LICENSE)
```

**Why this order matters:** New users scan top-to-bottom. They need to understand identity before setup, and setup before features. Burying Quick Start below a Features wall causes abandonment.

---

## 2. API Documentation Structure

Every endpoint gets the same structure. Consistency is what makes API docs scannable under pressure. A developer debugging a 404 at 2am should never have to hunt for response codes.

### Per-Endpoint Template

```markdown
## METHOD /path/:param

One sentence: what this endpoint does.

**Authentication:** Bearer token / API key / None

**Parameters:**

| Name | Type | Location | Required | Description |
|------|------|----------|----------|-------------|
| `id` | string | path | Yes | User UUID |
| `include` | string | query | No | Comma-separated related resources to embed |

**Request Body** (if applicable):

```json
{
  "field": "value",
  "optionalField": "value"
}
```

**Response Codes:**

| Code | Meaning | Body |
|------|---------|------|
| 200 | Success | User object |
| 400 | Validation error | `{ "error": "message" }` |
| 401 | Unauthorized | `{ "error": "Invalid token" }` |
| 404 | Not found | `{ "error": "User not found" }` |

**Example:**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  https://api.example.com/users/abc-123
```

```json
{
  "id": "abc-123",
  "email": "user@example.com",
  "createdAt": "2026-01-01T00:00:00Z"
}
```
```

**Why the parameter location column matters:** A developer sending `id` in the wrong location (body vs path vs query) will get a 400 or 404 with no obvious reason. Explicit location eliminates that class of bug.

---

## 3. Code Comment Guidelines

Comments explain *why*, not *what*. The code already says what. The comment's job is to carry context that can't be expressed in code: the business rule, the bug that made this necessary, the algorithm being implemented, the edge case being handled.

### JSDoc / TSDoc Template

```typescript
/**
 * Brief description: what the function does, not how.
 *
 * Include the "why" if non-obvious: the business rule, the constraint,
 * the historical reason this approach was chosen.
 *
 * @param paramName - What this value represents; valid range if relevant
 * @param options - Config object; document each property if non-obvious
 * @returns What is returned and under what conditions
 * @throws {ErrorType} When this error is thrown and why
 *
 * @example
 * // Show the common use case, not the trivial one
 * const result = processPayment(cart, { retries: 3 });
 */
```

### When to Comment Decision Table

| Situation | Action | Reason |
|-----------|--------|--------|
| Complex algorithm | Comment the algorithm name and logic | Future maintainers need the mental model |
| Business rule encoded in code | Comment the rule and its source | Rules change; knowing why prevents accidental removal |
| Non-obvious conditional | Comment the edge case being handled | `if (x > 0 && !user.suspended)` needs a why |
| Workaround for external bug | Comment the bug reference (issue URL) | Without it, the workaround looks wrong and gets "fixed" |
| Self-explanatory assignment | No comment | `const count = items.length` needs nothing |
| Loop with obvious iteration | No comment | The code is the comment |

---

## 4. Changelog (Keep a Changelog format)

Changelogs are read by: developers upgrading dependencies, product managers tracking releases, support teams triaging bugs, and security teams auditing changes. Structure for all of them.

The format is [Keep a Changelog](https://keepachangelog.com/) + [Semantic Versioning](https://semver.org/).

### Changelog Template

```markdown
# Changelog

All notable changes to this project will be documented here.
Format: [Keep a Changelog](https://keepachangelog.com/). Versioning: [SemVer](https://semver.org/).

## [Unreleased]

### Added
- Brief description of new feature

## [2.1.0] - 2026-03-10

### Added
- New endpoint `GET /users/search` with full-text search support

### Changed
- `POST /users` now returns 201 instead of 200 (breaking for clients checking status code)

### Deprecated
- `GET /users/list` - use `GET /users` instead; will be removed in v3.0

### Fixed
- Race condition in session cleanup that caused stale tokens to persist

## [2.0.0] - 2026-01-15

### Removed
- `DELETE /users/purge` (replaced by `POST /admin/purge` with audit logging)

### Security
- Upgraded bcrypt from 4.x to 5.x to address CVE-2025-XXXX
```

**Section meanings:** Added = new features. Changed = changes to existing functionality. Deprecated = features being removed in a future release. Removed = features removed this release. Fixed = bug fixes. Security = security-related fixes.

**Why dates on every version:** Undated changelogs make it impossible to correlate a bug report with a release. Always include the release date.

---

## 5. Architecture Decision Record (ADR)

ADRs document *why* the system is built the way it is. Without them, every architectural constraint looks like an accident and gets "fixed" by the next developer. The Consequences section is what makes an ADR worth writing.

### ADR Template

```markdown
# ADR-[NNN]: [Short title describing the decision]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-[NNN]
**Deciders:** [names or roles]

## Context

What situation forced this decision? What constraints exist?
What options were on the table? What information was available at the time?

## Decision

What did we decide to do? State it clearly and without hedging.

## Rationale

Why this option over the alternatives? What were the deciding factors?
If alternatives were considered and rejected, name them and explain why.

## Consequences

### Positive
- What gets better as a result of this decision

### Negative
- What gets harder, more expensive, or less flexible
- What future options are now foreclosed

### Risks
- What could go wrong, and what would trigger revisiting this decision
```

**Why Consequences are mandatory:** The positive consequences justify the decision. The negative consequences are what future developers need to know before they "improve" something. Without them, the ADR is a press release, not a decision record.

---

## 6. AI-Friendly Documentation

As of 2025, documentation is consumed by both humans and AI systems (RAG pipelines, MCP servers, LLM agents). Documentation structured for AI consumption is also better for humans. These are not in conflict.

### llms.txt Template

`llms.txt` is a convention (analogous to `robots.txt`) that tells AI crawlers and agents how to understand a project. Place it at the project root.

```markdown
# Project Name

> One sentence: objective and primary use case.

## Core Files

- [src/index.ts](src/index.ts): Entry point, server initialization
- [src/api/](src/api/): REST API route handlers
- [src/services/](src/services/): Business logic layer
- [docs/api.md](docs/api.md): Full API reference

## Key Concepts

- **Concept name**: One-sentence explanation of what this is and why it matters
- **Concept name**: One-sentence explanation

## Architecture Notes

- [Brief description of the main architectural pattern and why it was chosen]
- [Any non-obvious constraints an AI agent should know before modifying code]

## Optional: Full Documentation

- [docs/api.md](docs/api.md)
- [docs/architecture.md](docs/architecture.md)
```

### RAG-Optimized Structure Rules

When documentation will be indexed for retrieval:

| Rule | Why |
|------|-----|
| Every section must be self-contained | RAG chunks by section; orphaned context causes wrong answers |
| Use H1/H2/H3 hierarchy consistently | Heading hierarchy is used as chunk metadata for relevance scoring |
| Code examples must be complete (runnable) | Partial examples produce hallucinated completions when retrieved |
| Avoid pronouns that reference prior sections | "As mentioned above" means nothing to a retrieved chunk |
| Data structures get JSON/YAML examples | Schema descriptions without examples require inference to use |

---

## 7. Structure Principles

These are the principles behind every template in this skill. When a situation isn't covered by a template, apply these.

| Principle | Implementation | Why |
|-----------|---------------|-----|
| **Scannable over readable** | Headers, tables, bullets > prose paragraphs | Docs are consulted under time pressure, not read linearly |
| **Examples before explanation** | Show the output first, then explain it | Readers pattern-match; they need the target shape before the rules |
| **Progressive detail** | Overview -> required config -> advanced config -> edge cases | Users should be able to stop reading as soon as they have what they need |
| **Self-contained sections** | Each section works without the others | Docs are rarely read in full; each section is often the only section read |
| **Defaults always specified** | Every config option shows its default | "What happens if I don't set this" is the most common config question |
| **Dates on everything versioned** | Changelogs, ADRs, deprecation notices | Time context is necessary for auditing and debugging |
