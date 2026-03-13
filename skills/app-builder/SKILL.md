---
name: app-builder
description: "Use when building a new full-stack application from scratch, scaffolding a project, selecting a tech stack, or coordinating multi-agent application development. NEVER use for single-file scripts, adding features to an existing app (use feature-building.md directly), or non-application artifacts like documents or reports."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# App Builder

## File Index

| File | Description | When to Read |
|------|-------------|--------------|
| `project-detection.md` | Keyword matrix, project type detection | Starting new project |
| `tech-stack.md` | 2025 default stack, alternatives | Choosing technologies |
| `agent-coordination.md` | Agent pipeline, execution order | Coordinating multi-agent work |
| `scaffolding.md` | Directory structure, core files | Creating project structure |
| `feature-building.md` | Feature analysis, error handling | Adding features to existing project |
| `templates/SKILL.md` | Project templates index | Scaffolding new project |

---

## Templates (13)

| Template | Tech Stack | When to Use |
|----------|------------|-------------|
| [nextjs-fullstack](templates/nextjs-fullstack/TEMPLATE.md) | Next.js + Prisma | Full-stack web app |
| [nextjs-saas](templates/nextjs-saas/TEMPLATE.md) | Next.js + Stripe | SaaS product |
| [nextjs-static](templates/nextjs-static/TEMPLATE.md) | Next.js + Framer | Landing page |
| [nuxt-app](templates/nuxt-app/TEMPLATE.md) | Nuxt 3 + Pinia | Vue full-stack app |
| [express-api](templates/express-api/TEMPLATE.md) | Express + JWT | REST API |
| [python-fastapi](templates/python-fastapi/TEMPLATE.md) | FastAPI | Python API |
| [react-native-app](templates/react-native-app/TEMPLATE.md) | Expo + Zustand | Mobile app |
| [flutter-app](templates/flutter-app/TEMPLATE.md) | Flutter + Riverpod | Cross-platform mobile |
| [electron-desktop](templates/electron-desktop/TEMPLATE.md) | Electron + React | Desktop app |
| [chrome-extension](templates/chrome-extension/TEMPLATE.md) | Chrome MV3 | Browser extension |
| [cli-tool](templates/cli-tool/TEMPLATE.md) | Node.js + Commander | CLI app |
| [monorepo-turborepo](templates/monorepo-turborepo/TEMPLATE.md) | Turborepo + pnpm | Monorepo |
| [astro-static](templates/astro-static/TEMPLATE.md) | Astro | Content-heavy static site |

---

## Related Agents

| Agent | Role |
|-------|------|
| `project-planner` | Task breakdown, dependency graph |
| `frontend-specialist` | UI components, pages |
| `backend-specialist` | API, business logic |
| `database-architect` | Schema, migrations |
| `devops-engineer` | Deployment, preview |

---

## Project Type Decision Matrix

Use all signals together, not just one, to select the right template.

| Signals Present | Project Type | Template |
|-----------------|-------------|----------|
| Auth + payments + subscriptions | SaaS product | nextjs-saas |
| Auth + CRUD + database + API | Full-stack web app | nextjs-fullstack |
| Marketing copy + animations + no auth | Landing page / static site | nextjs-static or astro-static |
| Vue ecosystem preference or Nuxt SSR required | Vue full-stack | nuxt-app |
| REST-only, no UI, JSON consumers | Backend API | express-api or python-fastapi |
| iOS + Android from one codebase, no desktop | Mobile app | react-native-app or flutter-app |
| Runs installed on the user's OS, accesses filesystem | Desktop app | electron-desktop |
| Intercepts/modifies browser requests or DOM | Browser extension | chrome-extension |
| Terminal invocation, flag parsing, local automation | CLI tool | cli-tool |
| Multiple apps sharing packages in one repo | Monorepo | monorepo-turborepo |

Tiebreaker: if two templates fit, prefer the one whose tech stack the user explicitly named.

---

## Tech Stack Override Guidance

Defaults in `tech-stack.md` apply unless any of these conditions are met:

| Condition | Override |
|-----------|----------|
| User has an existing DB (MySQL, MongoDB, etc.) | Swap Prisma adapter or ORM to match |
| User names a specific auth provider (Auth0, Supabase Auth) | Replace default Clerk/NextAuth with named provider |
| Team is Vue-only or React-only by policy | Route to matching template family regardless of feature set |
| Mobile target is enterprise or requires heavy native modules | Prefer Flutter (Riverpod) over Expo |
| Hosting is constrained (no Node, serverless-only, etc.) | Switch API layer to match hosting constraints (FastAPI, edge functions) |
| Performance SLA explicitly stated | Enable SSR/ISR or move to edge runtime; note trade-offs |

When overriding, state the deviation and reason in the plan before scaffolding.

---

## Rationalization Table

Counter these when the reasoning surfaces during orchestration.

| Rationalization | Why It Fails |
|-----------------|-------------|
| "I'll just pick a template and adjust later" | Wrong template propagates into agent instructions; fixing midway doubles rework |
| "The user didn't specify a stack so I'll use the most popular one" | Popularity is not a fit signal; use the decision matrix, then confirm with user |
| "Feature-building.md covers this so I don't need to scaffold" | feature-building.md assumes a project already exists; scaffolding must come first |
| "I can coordinate agents without reading agent-coordination.md" | Execution order and handoff contracts are non-obvious; skipping causes agent collision |
| "The tech stack is standard so I don't need tech-stack.md" | Override conditions (auth provider, hosting, team policy) live there; missing them causes rework |
| "I'll start coding while the user clarifies requirements" | Ambiguous project type leads to wrong template selection; clarify first, scaffold second |

---

## Red Flags

- User asked to add a feature to an existing project but app-builder was activated instead of feature-building.md
- Scaffolding began before project type was confirmed from the decision matrix
- Agent coordination started without reading agent-coordination.md first
- Tech stack selected based on a single signal (e.g., "they said Next.js") without checking override conditions
- Template chosen by name recognition rather than matching signals in the decision matrix
- User request is a script, document, report, or automation task — not an application
- Plan was generated without stating which companion files were read
- Two templates selected for the same project with no tiebreaker reasoning given

---

## NEVER

- NEVER scaffold before confirming the project type via the decision matrix
- NEVER skip reading agent-coordination.md before launching multi-agent pipelines
- NEVER use app-builder for adding features to an existing application — route to feature-building.md
- NEVER apply a tech stack override without stating the reason in the plan
- NEVER generate a plan that omits which templates and companion files were consulted
