# Gap Report Schema

Complete field specification for gap reports written by the resource-auditor skill.

## File Format

- **Format:** JSON
- **Location:** `{skill-hub-path}/.gap-reports/inbox/`
- **Naming:** `{YYYY-MM-DD}_{workspace-slug}_{brief-description}.json`
- **Encoding:** UTF-8

## Common Fields (All Gap Types)

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | string | YES | Unique ID: `gap-{YYYY-MM-DD}-{NNN}` (NNN = sequential within day) |
| `timestamp` | string | YES | ISO 8601 UTC: `2026-04-05T14:30:00Z` |
| `gap_type` | enum | YES | `UNUSED`, `MISSING`, or `FALLBACK` |
| `source_workspace` | string | YES | Workspace name from CLAUDE.md PROJECT_PURPOSE (e.g., "WORKFORCE HQ") |
| `source_workspace_path` | string | YES | Absolute path to workspace root (forward slashes) |
| `task_description` | string | YES | What task was completed (1-2 sentences) |
| `work_category` | string | YES | From audit categories: content, technical-content, code, automation, analysis, design, strategy, operations, data |
| `what_was_needed` | string | YES | Specific capability or resource the task required |
| `impact_assessment` | string | YES | How output quality was affected (be specific, not vague) |
| `severity` | enum | YES | `critical`, `warning`, or `info` |
| `recommended_fix` | object | YES | See Recommended Fix Object below |
| `status` | enum | YES | Always `new` when created by auditor |
| `edit_count_at_audit` | integer | YES | Value of the Write/Edit counter when the audit ran. Shows total deliverable edits in the task. |
| `nudges_delivered` | integer | YES | How many nudge reminders were injected during the task (edit_count // 5). |
| `nudges_acted_on` | integer | YES | How many nudges resulted in a mid-task audit (0 if only the post-task audit ran). |

## UNUSED-Specific Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `resources_available` | array | YES | Resources that exist and were relevant. Each: `{type, name, reason}` |
| `resources_used` | array | YES | Resources actually invoked (may be empty) |
| `resources_missed` | array | YES | Relevant resources not invoked. Each: `{type, name, severity}` |

**Resource types:** `skill`, `agent`, `document`, `mcp_tool`, `plugin`, `hook`

## MISSING-Specific Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `resources_used_as_fallback` | array | NO | If any generic resource was used instead. Each: `{type, name, note}` |
| `capability_gap` | string | YES | What capability doesn't exist (be specific about what's missing) |

## FALLBACK-Specific Fields

| Field | Type | Required | Description |
|---|---|---|---|
| `resources_used_as_fallback` | array | YES | Generic resources used. Each: `{type, name, note}` |
| `what_would_be_better` | string | YES | Description of the specialized resource that would improve output |

## Recommended Fix Object

```json
{
  "type": "skill | hook | plugin | claude_md_rule | package",
  "description": "Specific description of what to build",
  "components": ["skill: local-seo-optimizer", "companion: service-area-templates.md"]
}
```

| Fix Type | When to Use |
|---|---|
| `skill` | Missing domain knowledge or workflow |
| `hook` | Enforcement needed (resource exists but isn't being used) |
| `plugin` | Multiple skills + hooks + agents needed as a coordinated package |
| `claude_md_rule` | Simple behavioral rule (no new skill needed) |
| `package` | Combination: skill + hook + CLAUDE.md rule together |

## Severity Decision Tree

```
Did the gap cause the output to be WRONG or misleading?
  YES --> critical

Did the gap cause the output to miss IMPORTANT qualities
an expert would expect?
  YES --> warning

Is the gap a nice-to-have improvement that wouldn't change
the user's experience meaningfully?
  YES --> info
```

## Example: UNUSED Report

```json
{
  "id": "gap-2026-04-05-001",
  "timestamp": "2026-04-05T14:30:00Z",
  "gap_type": "UNUSED",
  "source_workspace": "WORKFORCE HQ",
  "source_workspace_path": "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ",
  "task_description": "Rewriting landing page hero section and contact form",
  "work_category": "content",
  "what_was_needed": "Brand voice compliance, CRO optimization for client-facing landing page",
  "resources_available": [
    {"type": "skill", "name": "hq-brand-review", "reason": "Client-facing content requires brand voice"},
    {"type": "skill", "name": "page-cro", "reason": "Landing page needs conversion optimization"}
  ],
  "resources_used": [],
  "resources_missed": [
    {"type": "skill", "name": "hq-brand-review", "severity": "critical"},
    {"type": "skill", "name": "page-cro", "severity": "critical"}
  ],
  "impact_assessment": "Output lacked brand voice consistency and had no CRO optimization. Would need rework.",
  "severity": "critical",
  "edit_count_at_audit": 12,
  "nudges_delivered": 2,
  "nudges_acted_on": 0,
  "recommended_fix": {
    "type": "package",
    "description": "Content creation in HQ needs mandatory enforcement skill + PreToolUse hook",
    "components": ["skill: content-enforcer", "hook: PreToolUse content detection"]
  },
  "status": "new"
}
```

## Example: MISSING Report

```json
{
  "id": "gap-2026-04-05-002",
  "timestamp": "2026-04-05T15:00:00Z",
  "gap_type": "MISSING",
  "source_workspace": "CLIENT-acme-plumbing",
  "source_workspace_path": "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/clients/acme-plumbing",
  "task_description": "Writing service area pages for local plumbing SEO",
  "work_category": "content",
  "what_was_needed": "Local SEO optimization with schema markup, NAP consistency, geo-targeted patterns",
  "resources_used_as_fallback": [
    {"type": "skill", "name": "seo-optimizer", "note": "General SEO lacks local SEO patterns"}
  ],
  "capability_gap": "No skill for local SEO, service-area pages, or home services industry patterns",
  "impact_assessment": "Output functional but generic. Specialized skill would produce 3-5x better content.",
  "severity": "warning",
  "edit_count_at_audit": 8,
  "nudges_delivered": 1,
  "nudges_acted_on": 0,
  "recommended_fix": {
    "type": "skill",
    "description": "Build local-seo-optimizer with service-area templates and geo-targeting patterns",
    "components": ["skill: local-seo-optimizer", "companion: service-area-templates.md"]
  },
  "status": "new"
}
```

## Example: FALLBACK Report

```json
{
  "id": "gap-2026-04-05-003",
  "timestamp": "2026-04-05T16:00:00Z",
  "gap_type": "FALLBACK",
  "source_workspace": "WORKFORCE HQ",
  "source_workspace_path": "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ",
  "task_description": "Writing API integration documentation for client delivery",
  "work_category": "technical-content",
  "what_was_needed": "Technical API documentation with endpoint references and code examples",
  "resources_used_as_fallback": [
    {"type": "skill", "name": "copywriting", "note": "Optimized for marketing, not technical accuracy"},
    {"type": "skill", "name": "documentation-templates", "note": "Lacks API-specific patterns"}
  ],
  "what_would_be_better": "Dedicated technical-documentation skill with endpoint tables, auth flow docs, SDK examples",
  "impact_assessment": "Documentation readable but lacked developer-focused patterns experts expect.",
  "severity": "warning",
  "edit_count_at_audit": 15,
  "nudges_delivered": 3,
  "nudges_acted_on": 0,
  "recommended_fix": {
    "type": "skill",
    "description": "Build technical-documentation skill with API reference templates",
    "components": ["skill: technical-documentation", "companion: api-reference-template.md"]
  },
  "status": "new"
}
```