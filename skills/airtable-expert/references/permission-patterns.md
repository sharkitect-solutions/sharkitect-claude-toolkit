# Airtable Permission Patterns

Getting client-facing access right the first time. The Interface-Permission Gotcha is the most common way Airtable bases leak data.

## Load when

- Setting up any external user (client, contractor, vendor) with Airtable access
- Deciding between interface-only and full-base collaborator
- Auditing who can see what in an existing base
- Designing a multi-tenant interface (each client sees only their own records)

## The Three Permission Layers

Airtable permissions stack across three layers. Understanding the order is what prevents leaks.

```
1. WORKSPACE LEVEL
   Who can access this workspace at all
   Roles: Owner / Creator / Editor / Commenter / Read-only
   -- Workspace role is the CEILING. Base role cannot exceed it.

2. BASE LEVEL
   Who can do what in this specific base
   Roles: Owner / Creator / Editor / Commenter / Read-only / NONE
   -- "None" = invited but no access to the base itself (for interface-only use)

3. INTERFACE LEVEL
   Who can use a specific interface
   Roles: Can edit / Can comment / Can view
   -- Grants access to the INTERFACE without requiring base access
```

## The Interface-Permission Gotcha

**Symptom:** You share an interface with a client, but when they log in they ALSO see the base and all its tables in the left sidebar.

**Cause:** You added them as a base collaborator (even as "read-only") BEFORE sharing the interface. Base collaboration grants base visibility. Interface sharing alone does NOT.

**Correct sequence:**

1. Workspace admin invites the external user to the WORKSPACE only (or they accept a direct workspace invite)
2. In the BASE settings, their base role is set to **"None"** — they are a workspace member but have no direct base access
3. Open the interface → Share → invite the same user → set Interface role (Can edit / Can comment / Can view)
4. Result: when they log in, they see the interface in their sidebar but NOT the raw base

If the user was already added as a base collaborator, REMOVE them from the base collaborators list first, THEN share the interface.

## Interface-Only User Setup (the standard client flow)

```
Chris invites client@example.com:
  ├─ Workspace: add as Editor (or Creator if client needs to create stuff)
  │    OR
  │    Direct interface-only: skip workspace, use the interface share link
  │    (interface generates a user-scoped access)
  │
  ├─ Base: DO NOT add as collaborator. Base role for this user = None.
  │
  └─ Interface: Share → add user → Can edit / Can comment / Can view
```

**Verify before handoff:**
- Open the interface in an incognito window logged in as the client
- Confirm: interface loads, raw base is NOT visible in left sidebar
- Confirm: only the intended tables/fields are visible within the interface
- Confirm: internal-only fields (staff notes, cost prices, etc.) are NOT visible in any interface element

## Multi-Tenant Interface (each client sees only their own data)

**Scenario:** one base, many clients, each client must see only their own records.

**Setup:**
1. Add a `Client` field (collaborator type) to the relevant tables
2. In the interface, on each data-displaying element (Grid, Dashboard Number, etc.), add a filter:
   `{Client} = CURRENT_USER()`
3. Invite each client as an interface user with role "Can edit" or "Can view"
4. Set each client's base role to "None"

**CURRENT_USER()** returns the viewing user's Airtable identity. The filter automatically scopes data per session.

**Gotcha:** if a client's record has no `Client` assignment, they won't see anything (filter evaluates to false). Fallback: add a "Show unassigned" view only for admins, OR use a default-client automation that assigns new records.

## Public-Shared Views vs Interface Users

Two ways to expose Airtable data without requiring a user account:

| Method | How It Works | When to Use |
|--------|--------------|-------------|
| **Public view share link** | A specific Grid/Calendar/Kanban view of a table becomes accessible via a URL. Read-only. | Quick "look at this list" scenarios. No personalization possible. |
| **Public interface share link** | The entire interface becomes accessible via URL. Read-only unless authenticated. | Showcasing a dashboard publicly (e.g., public roadmap). |
| **Interface with invited users** | User logs in with their Airtable account. Full access per their role. | Client-facing workspaces, approval flows, anything requiring identity. |

Public links do NOT support editing. They do NOT support per-user filters. They are purely read-only show-and-tell.

**Security note:** anyone with the public link can see the data. Treat them like public URLs — don't put PII, credentials, or anything you'd be uncomfortable putting on the public web.

## PAT Scopes vs User Roles

PATs (Personal Access Tokens) exist INDEPENDENTLY of user roles:

- A PAT can have scopes (`schema.bases:write`, etc.) — see api-limitations.md
- A PAT is BOUND to the user who created it — that user's role is the ceiling
- If a user has "Editor" role and their PAT has `schema.bases:write` scope, the PAT still can't create tables because the user role doesn't permit it
- Creating a PAT for a service account? Add that service account as a base Owner/Creator first — otherwise the PAT is effectively read-only regardless of scope

## Row-Level Security (there isn't any, natively)

Airtable has NO row-level security at the base level. The multi-tenant pattern (filter by `CURRENT_USER()` in the interface) is a VIEW-level filter, not a security barrier:

- ✅ Interface users cannot navigate to the raw base and read other rows — because their base role is "None"
- ❌ If you accidentally grant them "Read-only" base role, they can see the raw base and ALL rows bypass the interface filter
- ❌ PATs with `data.records:read` scope on this base read ALL rows, ignoring any interface filter

**Implication:** the `{Client} = CURRENT_USER()` filter protects WITH the None-base-role. Both must be in place. Interface filters alone are NOT a security model.

## Permission Audit Checklist

For any client-facing base, run this monthly (or before any access change):

- [ ] Who has WORKSPACE access? Run: Workspace settings → Members. Remove departed contractors, old clients.
- [ ] Who has BASE access and at what role? Run: Base → Share. Verify each external user is at role = "None" unless they need raw base access.
- [ ] Which interfaces are SHARED PUBLICLY (via public link)? Are they intentional? Are the visible tables free of PII?
- [ ] For each interface, who is invited and at what role? Revoke any users who no longer need access.
- [ ] Any PATs still active for users who no longer work on this base? Revoke at https://airtable.com/create/tokens.

## Common Failure Modes

| Symptom | Cause | Fix |
|---------|-------|-----|
| Client sees all base tables, not just the interface | Base role is "Read only" or higher, not "None" | Change base role to "None", re-test |
| Client sees other clients' data in the interface | Filter is missing OR `CURRENT_USER()` doesn't match field, OR base role leaks visibility | Add `{Client} = CURRENT_USER()` filter; confirm base role is "None"; verify `Client` field is collaborator type not text |
| API keeps returning 403 NOT_AUTHORIZED | PAT scope missing, OR user role insufficient | Check PAT scopes; check workspace+base role of PAT owner |
| Public share link exposes fields user didn't want public | Field visibility is per-view, not per-record | Create a dedicated public view that hides sensitive fields; share THAT view's link, not the default view |
| Ex-contractor still has access weeks after offboarding | Workspace invite wasn't removed | Workspace → Members → Remove. Also revoke their PATs. |
