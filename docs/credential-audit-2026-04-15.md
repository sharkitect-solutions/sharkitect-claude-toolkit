# Credential Audit -- Sharkitect Digital

> **Audit date:** 2026-04-15
> **Status:** REFERENCE DOCUMENT -- cleanup deferred until after Foundation Reset (Phases 7-9)
> **Owner:** Workforce HQ (owns the master .env) | Skill Hub (produced this audit)
> **Action required:** Manual verification items flagged with VERIFY below

---

## 1. Cross-Workspace Key Map

Which workspaces have which keys. Duplicates are expected for shared infrastructure (Supabase, Telegram HQ bot, etc.) but should use identical values.

| Key | HQ | Skill Hub | Sentinel | Values Match? |
|-----|----|-----------|----------|---------------|
| SUPABASE_URL | Y | Y | Y | YES -- all 3 identical |
| SUPABASE_SERVICE_ROLE_KEY | Y | Y | Y | YES -- all 3 identical |
| SUPABASE_ANON_KEY | Y | - | - | N/A (HQ only) |
| SUPABASE_PAT_KEY | Y | - | - | N/A (HQ only) |
| OPENAI_API_KEY | Y | Y | Y | YES -- all 3 identical |
| ANTHROPIC_API_KEY | Y | - | Y | YES -- HQ and Sentinel match |
| TELEGRAM_HQ_BOT_TOKEN | Y | Y | Y | YES -- all 3 identical |
| TELEGRAM_MY_USER_ID / TELEGRAM_CHAT_ID | Y | Y | Y (as CHAT_ID) | YES -- same value, different var name in Sentinel |
| GITHUB_PAT_KEY | Y (no) | Y | Y | Skill Hub + Sentinel match. HQ does NOT have it. |
| N8N_API_KEY | Y | - | Y | YES -- HQ and Sentinel match |
| N8N_INST_URL | Y | - | Y | YES -- HQ and Sentinel match |
| GOOGLE_OAUTH_CLIENT_ID | Y | - | - | N/A (HQ only) |
| GOOGLE_OAUTH_CLIENT_SECRET | Y | - | - | N/A (HQ only) |
| GOOGLE_API_KEY | Y | - | - | N/A (HQ only) |
| GOOGLE_CX | Y | - | - | N/A (HQ only) |
| SHARKITECT_HQ_CALENDAR_ID | Y | - | Y | YES -- both identical |
| FIRECRAWL_API_KEY | Y (inactive) | Y | - | Same value, active in Skill Hub, inactive in HQ |
| TELEGRAM_ALEX_BOT_TOKEN | Y | - | - | N/A (HQ only) |
| AIRTABLE_API_SHARKITECT_FULL_ACCESS_KEY | Y | - | - | N/A (HQ only) |
| AIRTABLE_API_SHARKITECT_AIOS_KEY | Y | - | - | N/A (HQ only) |
| SLACK_WEBHOOK_URL | Y | - | - | N/A (HQ only) |
| SLACK_BOT_TOKEN | Y | - | - | N/A (HQ only) |
| HUBSPOT_API_KEY | Y | - | - | N/A (HQ only) |
| NOTION_API_KEY | Y | - | - | N/A (HQ only) |
| MONDAY_API_KEY | Y | - | - | N/A (HQ only) |

### Inconsistency: Sentinel uses TELEGRAM_CHAT_ID, HQ and Skill Hub use TELEGRAM_MY_USER_ID
Same value (8227246993), different variable name. Not a bug (different scripts read different var names), but worth standardizing during cleanup.

---

## 2. Credential-by-Credential Audit

### SECTION A: Shared Infrastructure (used by 2+ workspaces)

#### A1. Supabase Shared Brain
| Var | Value status | Used by |
|-----|-------------|---------|
| SUPABASE_URL | ACTIVE | All 3 workspaces. Every tool that writes to Supabase brain. |
| SUPABASE_SERVICE_ROLE_KEY | ACTIVE | All 3 workspaces. Bypasses RLS -- used by Python scripts. |
| SUPABASE_ANON_KEY | ACTIVE | HQ only. Used by client-facing code or anon queries. |
| SUPABASE_PAT_KEY | ACTIVE | HQ only. Personal access token for Supabase Management API. |

**Notes:** Service role key is the most sensitive credential in the entire system. If leaked, all brain data is exposed. The anon key is safe to expose (it respects RLS). PAT key is for Supabase dashboard/management operations.

#### A2. OpenAI
| Var | Value status | Used by |
|-----|-------------|---------|
| OPENAI_API_KEY | ACTIVE | All 3 workspaces. Embeddings (text-embedding-3-small in Skill Hub/HQ, text-embedding-3-large in Sentinel). |

**Notes:** Single key across all workspaces. Sentinel comment says "3-large, 3072 dims" while HQ says "3-small, 1536 dims". VERIFY: Are both models actually being used? If so, the embedding dimensions must match within each table or similarity search breaks.

#### A3. Anthropic (Claude API)
| Var | Value status | Used by |
|-----|-------------|---------|
| ANTHROPIC_API_KEY | ACTIVE | HQ (Alex Telegram bot brain.py), Sentinel (brief synthesis with claude-haiku-4-5). |

**Notes:** Not in Skill Hub .env. Skill Hub doesn't run any Claude API calls directly (it uses Claude Code itself, not the API). Correct distribution.

#### A4. Telegram HQ Bot
| Var | Value status | Used by |
|-----|-------------|---------|
| TELEGRAM_HQ_BOT_TOKEN | ACTIVE | All 3 workspaces. Automated briefs and alerts (one-way to Chris). |
| TELEGRAM_MY_USER_ID / TELEGRAM_CHAT_ID | ACTIVE | All 3 workspaces. Chris's Telegram user ID for message delivery. |

**Notes:** This is the one-way broadcast bot. All workspaces can send alerts to Chris via this bot. Working correctly.

#### A5. GitHub
| Var | Value status | Used by |
|-----|-------------|---------|
| GITHUB_PAT_KEY | ACTIVE | Skill Hub (sync-skills.py pushes to toolkit repo), Sentinel (repo monitor). |
| GitHub_PROFILE | REFERENCE | Skill Hub only. Just a URL, not a credential. |

**Notes:** HQ does NOT have this key. It doesn't need it -- HQ doesn't push to GitHub. Correct distribution.

#### A6. n8n
| Var | Value status | Used by |
|-----|-------------|---------|
| N8N_API_KEY | ACTIVE | HQ (workflow management), Sentinel (workflow monitoring). |
| N8N_INST_URL | ACTIVE | HQ, Sentinel. Points to sharkitect-solutions.app.n8n.cloud. |

**Notes:** Skill Hub does NOT have n8n keys. Correct -- Skill Hub doesn't interact with n8n directly. API-first strategy (no quota limits), MCP as fallback.

#### A7. Google Calendar
| Var | Value status | Used by |
|-----|-------------|---------|
| SHARKITECT_HQ_CALENDAR_ID | ACTIVE | HQ (briefs pull calendar events), Sentinel (morning report). |

**Notes:** Just a calendar identifier (email address), not a secret. Used by scripts that query Google Calendar.

#### A8. Firecrawl
| Var | Value status | Used by |
|-----|-------------|---------|
| FIRECRAWL_API_KEY | ACTIVE in Skill Hub, INACTIVE in HQ (Section 3.6, commented out) | Skill Hub uses it for web scraping via firecrawl skill. |

**Notes:** Same key value in both places. HQ has it commented out. Clean.

---

### SECTION B: HQ-Only Credentials (Internal Platform)

#### B1. Telegram Alex Bot (Interactive)
| Var | Value status | Used by |
|-----|-------------|---------|
| TELEGRAM_ALEX_BOT_TOKEN | ACTIVE | HQ only. Two-way conversational bot via n8n. |
| TELEGRAM_ALEX_BOT_USERNAME | REFERENCE | @AlexMyEA_Bot |

**Notes:** Separate from HQ bot. Alex handles interactive conversations. Working via n8n workflow.

#### B2. Google Workspace (OAuth + API)
| Var | Value status | Used by |
|-----|-------------|---------|
| GOOGLE_OAUTH_CLIENT_ID | ACTIVE | HQ. Used by gws CLI for Gmail/Calendar/Drive access. |
| GOOGLE_OAUTH_CLIENT_SECRET | ACTIVE | HQ. OAuth flow for Google services. |
| GOOGLE_API_KEY | ACTIVE | HQ. Server-side Google API access. |
| GOOGLE_CX | ACTIVE | HQ. Custom Search Engine ID for web search. |
| ADMIN_EMAIL | REFERENCE | admin@sharkitectdigital.com |
| SOLUTIONS_EMAIL | REFERENCE | solutions@sharkitectdigital.com |

**VERIFY (manual):**
- [ ] Log into Google Cloud Console (console.cloud.google.com)
- [ ] Check GOOGLE_API_KEY restrictions: Is it unrestricted? Which APIs is it enabled for?
- [ ] Check OAuth consent screen status: Is it in testing or production mode?
- [ ] Check API quotas and billing: Are there unexpected charges?
- [ ] Verify GOOGLE_CX still points to a working Custom Search Engine

**User note:** You mentioned having a Google API key "that supposedly does not have any restrictions and can do anything." This is likely GOOGLE_API_KEY. An unrestricted API key is a security risk -- it should be locked down to only the APIs you actually use (Custom Search, Calendar, Gmail). Check the Cloud Console.

#### B3. Airtable
| Var | Value status | Used by |
|-----|-------------|---------|
| AIRTABLE_API_SHARKITECT_FULL_ACCESS_KEY | ACTIVE | HQ. Full access to all Sharkitect Airtable bases. n8n workflows, direct API calls. |
| AIRTABLE_API_SHARKITECT_AIOS_KEY | ACTIVE | HQ. Scoped key for AIOS-specific bases. |
| AIRTABLE_ERA_BASE_ID | UNCERTAIN | HQ. ERA classification system. ERA is noted as "not working (Pending Task)." |
| AIRTABLE_OPS_BASE_ID | ACTIVE | HQ. Error auto-fix bridge operations logging. |
| AIRTABLE_OPS_TABLE_ID | ACTIVE | HQ. Specific table in ops base for error tracking. |

**VERIFY:**
- [ ] Is AIRTABLE_ERA_BASE_ID still needed? ERA is marked as not working.
- [ ] Are both Airtable PAT keys (full access + AIOS) still valid? Airtable PATs can expire.

#### B4. Slack
| Var | Value status | Used by |
|-----|-------------|---------|
| SLACK_WEBHOOK_URL | UNCERTAIN | HQ. Incoming webhook for posting messages. |
| SLACK_BOT_TOKEN | UNCERTAIN | HQ. Bot token for Slack API access. |
| CHRIS_SLACK_USER_ID | REFERENCE | HQ. Chris's Slack user ID for mentions/DMs. |

**VERIFY:**
- [ ] Is Slack actively used in any current workflow? Or was this set up and abandoned?
- [ ] Check if the webhook URL is still valid (Slack webhooks can be revoked).
- [ ] Check if the bot token is still active in the Slack workspace.

#### B5. HubSpot
| Var | Value status | Used by |
|-----|-------------|---------|
| HUBSPOT_API_KEY | ACTIVE | HQ. CRM access via PAT. |

**Notes:** Section 3 has extended HubSpot keys (client secret, PAK key, dev API key, MCP auth) all commented out. These were likely from an OAuth app setup that was abandoned in favor of the PAT.

**VERIFY:**
- [ ] Is HubSpot actively used in current workflows? Or just configured?
- [ ] Can the Section 3 HubSpot keys be permanently deleted (not just commented out)?

#### B6. Notion
| Var | Value status | Used by |
|-----|-------------|---------|
| NOTION_API_KEY | UNCERTAIN | HQ. Integration token. |

**VERIFY:**
- [ ] Is the Notion API key used by any active workflow or script? The user mentioned a "confidential Notion thing" for credential tracking, but is the API key actively called by any automation?
- [ ] Section 3 has workspace ID and teamspace URL commented out. Can these be deleted?

#### B7. Monday.com
| Var | Value status | Used by |
|-----|-------------|---------|
| MONDAY_API_KEY | ACTIVE | HQ. Platform-level API access. |

**Notes:** Used for client work (FF Construction has Monday.com boards). Active as long as that client relationship exists.

#### B8. Google SMTP (App Passwords)
| Var | Value status | Used by |
|-----|-------------|---------|
| SMTP_ACCOUNT_1_EMAIL + PASSWORD | UNCERTAIN | HQ. admin@ app password for sending email via SMTP. |
| SMTP_ACCOUNT_2_EMAIL + PASSWORD | UNCERTAIN | HQ. solutions@ app password for sending email via SMTP. |

**VERIFY:**
- [ ] Are these SMTP app passwords used by any active workflow? Or were they set up for a project that's no longer active?
- [ ] Google App Passwords can be revoked from Google Account > Security > App Passwords. Check if they're still listed.

#### B9. Error Auto-Fix Bridge
| Var | Value status | Used by |
|-----|-------------|---------|
| AUTOFIX_WEBHOOK_SECRET | ACTIVE | HQ. Webhook authentication for error-autofix bridge server. |
| AUTOFIX_HOST | ACTIVE | HQ. Bridge server host (127.0.0.1). |
| AUTOFIX_PORT | ACTIVE | HQ. Bridge server port (8765). |

**Notes:** Bridge is documented as RUNNING in HQ. FastAPI + cloudflared tunnel. Needs auto-restart on reboot.

#### B10. ERA Classification
| Var | Value status | Used by |
|-----|-------------|---------|
| CLIENT_DOMAINS | CONFIGURED | HQ. fantasticfloorskc.com. |
| LEAD_DOMAINS | EMPTY | HQ. Not configured. |
| VENDOR_DOMAINS | EMPTY | HQ. Not configured. |
| COLLEAGUE_DOMAINS | EMPTY | HQ. Not configured. |
| N8N_ERROR_SENDER | EMPTY | HQ. Not configured. |

**Notes:** ERA is documented as "not working (Pending Task)." These are configuration values, not API keys. Keep if ERA will be revived; remove if ERA is permanently abandoned.

**VERIFY:**
- [ ] Is ERA going to be revived? If not, move all ERA-related vars to Section 3 (inactive) or delete.

#### B11. Paths and Reference URLs
| Var | Value status | Used by |
|-----|-------------|---------|
| WORKFORCE_HQ_PATH | REFERENCE | HQ. Local filesystem path. Machine-specific. |
| HOME_LANDING_PAGE | REFERENCE | HQ. sharkitectdigital.com URL. |
| REDIRECT_LANDING_PAGE | REFERENCE | HQ. Form redirect URL. |

**Notes:** These are not credentials. They're configuration constants. Fine to keep.

#### B12. Brevo (Section 4 -- unsorted)
| Var | Value status | Used by |
|-----|-------------|---------|
| BREVO_API_KEY | UNCERTAIN | HQ. Comment says "SPEED TO LEAD DEMO". |

**VERIFY:**
- [ ] Is the Speed to Lead demo still active? If not, move to Section 3 (inactive).
- [ ] Is there an active Brevo billing account? Free tier or paid?

---

### SECTION C: Client Credentials

#### C1. Fantastic Floors / FF Construction
| Var | Value status | Used by |
|-----|-------------|---------|
| FF_QBO_REALM_ID | ACTIVE | HQ. QuickBooks Online production environment. |
| FF_QBO_N8N_CREDENTIAL_ID | ACTIVE | HQ. n8n credential reference for QBO. |
| FF_QBO_SANDBOX_REALM_ID | ACTIVE | HQ. QBO sandbox for testing. |
| FF_QBO_SANDBOX_N8N_CREDENTIAL_ID | ACTIVE | HQ. n8n credential for sandbox. |
| FF_AIRTABLE_BASE_ID | ACTIVE | HQ. Check Distribution base. |
| AIRTABLE_FF_WORKFLOW_LOGGER_BASE_ID | ACTIVE | HQ. Workflow logging base. |
| FF_CHECK_DIST_WORKFLOW_ID | ACTIVE | HQ. Main check distribution workflow. |
| FF_CHECK_DIST_WORKFLOW_V1_ID | UNCERTAIN | HQ. V1 of workflow -- is this still used or superseded by the main one? |
| FF_MONDAY_BOARD_CONSTRUCTION | ACTIVE | HQ. Monday.com board for construction division. |
| FF_MONDAY_BOARD_FLOORS | ACTIVE | HQ. Monday.com board for floors division. |
| FF_N8N_AIRTABLE_CRED_ID | ACTIVE | HQ. n8n credential reference for Airtable. |

**VERIFY:**
- [ ] Is FF_CHECK_DIST_WORKFLOW_V1_ID still needed? Or has it been fully replaced by FF_CHECK_DIST_WORKFLOW_ID?
- [ ] Client status check: Is FF Construction still an active client?

---

### SECTION D: Inactive/Commented-Out Credentials (HQ Section 3)

These are commented out in HQ .env. Decision needed: keep, delete, or revive.

| Key | Service | Last known purpose | Recommendation |
|-----|---------|-------------------|----------------|
| TELEGRAM_ALEX_BOT_ID | Telegram | Bot numeric ID (reference only) | DELETE -- username is sufficient, ID is in the token |
| TELEGRAM_HQ_BOT_ID | Telegram | Bot numeric ID (reference only) | DELETE -- same reason |
| TELEGRAM_MY_USERNAME | Telegram | @SharkitectDigital | DELETE -- reference only, not a credential |
| TWILIO_ACCT_SID | Twilio | Voice/SMS -- "activate when Voice AI MVP begins" | KEEP -- future project |
| TWILIO_AUTH_TOKEN | Twilio | Voice/SMS auth | KEEP -- paired with above |
| HUBSPOT_CLIENT_SECRET | HubSpot | OAuth app setup | VERIFY: Was the OAuth app deleted? If so, DELETE. |
| HUBSPOT_PAK_KEY | HubSpot | Portal access key | VERIFY: Is this still valid? |
| HUBSPOT_DEV_API_KEY | HubSpot | Developer API key | VERIFY: Still active in HubSpot portal? |
| HUBSPOT_MCP_APP_ID | HubSpot | MCP server auth | VERIFY: Is HubSpot MCP still configured? |
| HUBSPOT_MCP_CLIENT_ID | HubSpot | MCP OAuth | VERIFY: Same as above |
| HUBSPOT_MCP_CLIENT_SECRET | HubSpot | MCP OAuth | VERIFY: Same as above |
| NOTION_WORKSPACE_ID | Notion | Workspace reference | DELETE -- can be retrieved from Notion API anytime |
| NOTION_COMMAND_CENTER_TEAMSPACE_URL | Notion | URL reference | DELETE -- it's a URL, not a credential |
| SERPAPI_API_KEY | SerpAPI | Search API | VERIFY: Active account? Being billed? |
| FIRECRAWL_API_KEY (HQ copy) | Firecrawl | Web scraping | KEEP COMMENTED -- active in Skill Hub, not needed in HQ |
| HUNTER_IO_API_KEY | Hunter.io | Email finder | VERIFY: Active account? Being billed? |
| SUPABASE_ORG_SLUG | Supabase | Org reference | DELETE -- not a credential, can be found in dashboard |
| SUPABASE_DB_PASSWORD | Supabase | Direct DB password | KEEP but VERIFY: Is direct DB access ever used? This is the most sensitive item in Section 3. |

---

## 3. Manual Verification Checklist

These items require logging into external services. Cannot be verified programmatically.

### Priority 1: Security & Billing (check first)
- [ ] **Google Cloud Console** -- Check GOOGLE_API_KEY restrictions. Lock down to only APIs in use.
- [ ] **Supabase DB Password** (Section 3) -- Is direct DB access enabled? If not, delete this password.
- [ ] **SerpAPI** -- Check if there's an active account being billed. If unused, cancel and delete key.
- [ ] **Hunter.io** -- Same as SerpAPI. Check billing status.
- [ ] **Brevo** -- Check account status and billing. Move to Section 3 if Speed to Lead demo is dead.

### Priority 2: Active Service Verification
- [ ] **Slack** -- Is Slack used in any active workflow? Test the webhook URL and bot token.
- [ ] **Notion API** -- Is any automation calling the Notion API? Or is it only used via MCP?
- [ ] **SMTP App Passwords** -- Are any workflows sending email via SMTP? Or has this been replaced by n8n Gmail integration?
- [ ] **HubSpot extended keys** (Section 3) -- Were the OAuth app and MCP integration abandoned? If yes, delete all 6 HubSpot keys in Section 3.

### Priority 3: Cleanup (nice-to-have)
- [ ] **ERA system** -- Decision: revive or abandon? Affects ~5 env vars.
- [ ] **FF_CHECK_DIST_WORKFLOW_V1_ID** -- Is V1 workflow still active or fully replaced?
- [ ] **Telegram reference IDs** (Section 3) -- Can be deleted, they're not credentials.
- [ ] **Notion/Supabase reference values** (Section 3) -- Can be deleted, not credentials.
- [ ] **Embedding model mismatch** -- Sentinel says text-embedding-3-large (3072 dims), HQ says text-embedding-3-small (1536 dims). Verify which model each workspace actually uses and whether this causes issues.

---

## 4. Recommended Cleanup Actions (Post-Foundation Reset)

When this is actioned, do it in this order:

1. **Manual verification** -- Work through the checklist above. Mark each item as verified/dead/billing-risk.
2. **HQ .env Section 4** -- Move Brevo to proper section (Section 1 if active, Section 3 if inactive).
3. **HQ .env Section 3** -- Delete confirmed-dead items. Keep items with future plans (Twilio).
4. **Standardize var names** -- Decide on TELEGRAM_MY_USER_ID vs TELEGRAM_CHAT_ID. Pick one, use everywhere.
5. **Skill Hub + Sentinel .env** -- Add section headers matching HQ format for consistency.
6. **Build credential registry** -- See `project_credential_registry.md` in Skill Hub memory. Supabase metadata table (no secrets).
7. **Build credential-template.env** -- For toolkit repo. All keys with comments, no values. New machine setup guide.

---

## 5. Summary Stats

| Category | Count |
|----------|-------|
| Total unique env vars across all workspaces | ~55 |
| Shared across 2+ workspaces | 10 keys |
| HQ-only (active) | ~25 keys |
| HQ-only (inactive/commented) | ~17 keys |
| Skill Hub-only | 1 key (FIRECRAWL_API_KEY active, GitHub_PROFILE reference) |
| Sentinel-only | 0 unique keys |
| Client-specific (FF Construction) | ~11 keys |
| Needing manual verification | 14 items |
| Recommended for deletion | 5 items (reference values, not credentials) |
| Billing risk (possibly paying for unused) | 3 items (SerpAPI, Hunter.io, Brevo) |
