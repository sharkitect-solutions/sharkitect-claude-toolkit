# Fix RLR MVP — Three Issues

## Context

The STL RLR Demo workflow (n8n ID: `e0lUI3Wdn9JdxEx2`, 8 nodes, ACTIVE in production) has three issues:
1. **Duplicate Airtable entries** — every single form submission creates TWO records
2. **Email going to spam** — emails from solutions@ land in spam folder
3. **Prompt tweaks needed** — email body nearly perfect but Chris wants adjustments

Priority #1 on the reordered pending list. Chain of command: Alex → Marcus → Orion → Node.

### Chris's Decisions
- **Dedup action:** Log duplicates to a separate "Suppressed Leads" table (audit trail) — BUT only suppress exact full-field matches (see below)
- **Dedup scope (CRITICAL):** This is a DEMO. Prospects intentionally submit multiple times with different dropdown options and comments to see how the email changes. Each unique combination must go through. Only suppress if ALL of: name, email, company, dropdown, AND text box content match exactly.
- **Sender name:** "Sharkitect Digital"
- **DMARC:** We provide the exact DNS record value; Chris updates at Namecheap
- **Email context:** Prospect is evaluating what THEIR clients would receive — they're testing the tool as a potential buyer of RLR. The email quality convinces them to hire Sharkitect. Not traditional warm outreach — it's a demo showcase.
- **Signature link:** Keep www.sharkitectdigital.com as PLAIN TEXT (not hyperlink). People can copy-paste it.

---

## Bug #1: Duplicate Airtable Entries

### Root Cause (CONFIRMED via execution trace)

**Jotform native Airtable integration running ALONGSIDE our webhook workflow.** NOT duplicate form submissions. NOT the two Airtable nodes in our workflow.

Evidence from Chris's test (execution 2172, app form):
- **Ghost record** `rec292UB1xnqiBjcK` — created at 12:26:37Z, Form URL: `https://www.jotform.com/inbox/SUBMISSION_ID`
- **Our record** `recnvFClKHUjm0P2u` — created at 12:26:40Z, Form URL: `https://form.jotform.com/FORM_ID`

Our Parse Raw Data code builds `https://form.jotform.com/${formID}`. The ghost uses `https://www.jotform.com/inbox/${submissionID}` — a Jotform inbox URL format our code NEVER generates.

n8n execution trace confirms our workflow works correctly internally:
- Parse Raw Data → 1 item out
- Create a record → 1 record created (`recnvFClKHUjm0P2u`)
- Update record → same record updated with email data
- Ghost record was created 3 seconds BEFORE our workflow's Create node ran

Ghost records have: all form data, NO Responded flag, NO email fields, NaN Response Time.

### Fix — Two Layers

**Layer 1 (PRIMARY): Chris disables the Jotform → Airtable native integration**
- Location: Jotform form settings → Integrations (check BOTH forms: App form `260626660403149` + Experience form `260447926790063`)
- Look for any Airtable integration/connection and disable/delete it
- This eliminates ghost records at the source

**Layer 2 (SAFETY NET): Dedup Gate in n8n workflow**
Protects against accidental exact-duplicate submissions (user hitting submit twice with identical data). IMPORTANT: This is a demo — prospects intentionally submit multiple times with different options to see how the email changes. Only suppress TRUE duplicates where ALL fields match.

**Step 1a: Create "Suppressed Leads" table in Airtable**
- Base: `appYGAqZZHT7Neoej` (OFFER DEMOS)
- Table name: `Suppressed Leads`
- Fields: First Name (text), Last Name (text), Email (email), Company Name (text), Offer Interest (text), Tell Us More (text), Original Record ID (text), Suppression Reason (text), Submission ID (text)
- Method: Airtable Metadata API (`POST /v0/meta/bases/{baseId}/tables`)

**Step 1b: Add 3 new nodes to n8n workflow**

1. **"Check Existing Lead"** (Airtable Search)
   - Search `tblLLdNlP4NqUQL2q` by Email = `{{ $json.email }}`
   - Credential: `VrYcW7FeENjt8101` (MVP - Demos)
   - `alwaysOutputData: true` (so IF node gets data even when no match)

2. **"Is Exact Duplicate?"** (Code node — NOT a simple IF)
   - Receives: Airtable search results + parsed form data (via `$('Parse Raw Data')`)
   - Logic: If Airtable returned 0 results → `isNew = true`. If results exist, loop through ALL matches and check if ANY record matches on ALL 5 fields:
     - First Name (exact match)
     - Email (exact match)
     - Company Name (exact match)
     - Offer Interest / dropdown (exact match)
     - Tell Us More / text box (exact match)
   - Output: `{ isNew: true/false, matchedRecordId: "recXXX" or null }`
   - WHY Code node instead of IF: Need multi-field comparison across potentially multiple Airtable results. IF node can't loop through array results and compare 5 fields.

3. **"Route New vs Duplicate"** (IF node)
   - Condition: `{{ $json.isNew }}` equals true
   - TRUE → "Create a record" (new/unique submission, proceed normally)
   - FALSE → "Log Suppressed Lead" (exact duplicate found)

4. **"Log Suppressed Lead"** (Airtable Create)
   - Write to new "Suppressed Leads" table
   - Fields: name, email, company, offer interest, tell us more from parsed data + Original Record ID from Code node + reason "Exact duplicate submission"
   - Credential: `VrYcW7FeENjt8101`

**Step 1c: Rewire connections**
- Remove: Parse Raw Data → Create a record
- Add: Parse Raw Data → Check Existing Lead → Is Exact Duplicate? → Route New vs Duplicate
- Route TRUE → Create a record
- Route FALSE → Log Suppressed Lead

### Updated flow (11 nodes total):
```
Jotform Webhook → Parse Raw Data → Check Existing Lead → Is Exact Duplicate? → Route New vs Duplicate
  ├── TRUE → Create a record → Write Email → Prepare Context → Send Email → Clean Email Body → Update record
  └── FALSE → Log Suppressed Lead (end)
```

---

## Bug #2: Email Going to Spam

### Root Cause (MULTI-FACTOR)
1. DMARC = `p=none` (no enforcement)
2. Gmail Send node has `options: {}` (no sender name, no reply-to)
3. solutions@ is low-volume sender with minimal reputation
4. **Hyperlinks in email body** — emails contain URLs (sharkitectdigital.com, "schedule a time here" links) which can trigger spam filters, especially from new/low-reputation senders

### Fix Part A — Gmail node (n8n workflow update, same API push as Bug #1)
- Add to "Send Email via Gmail" node options:
  - `"senderName": "Sharkitect Digital"`
  - `"replyTo": "solutions@sharkitectdigital.com"`

### Fix Part B — DMARC tightening (Chris updates DNS at Namecheap)

**Exact DNS record to update:**
- Type: TXT
- Host: `_dmarc`
- Value: `v=DMARC1; p=quarantine; rua=mailto:admin@sharkitectdigital.com; adkim=r; aspf=r`
- TTL: Automatic

This replaces the current `p=none` with `p=quarantine` — non-aligned emails get quarantined instead of delivered. After 2-4 weeks of monitoring, tighten to `p=reject`.

### Fix Part C — Reduce hyperlink spam signals (prompt update, combined with Issue #3)
- Keep `www.sharkitectdigital.com` in signature but as PLAIN TEXT (no `<a href>` — people can copy-paste)
- Booking link stays as the ONLY clickable hyperlink in the email
- This drops from 2 clickable links → 1, lowering spam score for a low-reputation sender

---

## Issue #3: Prompt Optimization (Chris's Feedback — 2026-03-11)

### Chris's Specific Complaints

1. **Too formal/stiff** — Output reads corporate despite prompt saying "conversational." Chris wants warm, casual, friendly tone matching his blue-collar client base (trades owners). "Not your general typical AI-sounding response."
2. **Bad wording** — Example: *"That's not a productivity problem. That's a sign your tools were never built to work together in the first place."* Feels forced, overwritten, AI-ish. Chris: "just not really well written."
3. **Paragraph structure broken** — Last email was "one big jumbled paragraph." Chris wants max 2 sentences per paragraph, spaced for scanning. Easy to read on mobile.
4. **Hyperlink inconsistency** — "schedule a time here" sometimes has the `<a href>` link, sometimes plain text. Must be consistent every time.
5. **Not differentiated** — Should feel unique and human. This is warm outreach (prospect reached out first via demo form), not cold email. Should feel like a real founder responding personally.
6. **Model stays Haiku** — Optimize the prompt first. Higher model risks being MORE formal. Only upgrade if Haiku can't handle it after prompt fix.

### Prompt Changes (7 specific modifications)

All changes target the Write Email node → `parameters.messages.values[0].content`

**Change 1: Voice description — warmer, less corporate**
Replace the current Christopher's voice paragraph with:
> Christopher's voice: He writes like he's texting a friend who asked for advice — short, real, no fluff. He talks TO people, not AT them. He drops the formality that most founders hide behind. He sounds like someone you'd grab a beer with who also happens to know systems inside and out. He references specific things the prospect said — not categories or labels. He never repeats himself. He starts at the point.

**Change 2: Add explicit STRUCTURE rule to BODY CONSTRAINTS**
Add after "Do not count HTML tags in the word count" line:
> PARAGRAPH STRUCTURE — NON-NEGOTIABLE:
> - Maximum 2 sentences per `<p>` tag. No exceptions.
> - Each new thought gets its own `<p>` tag.
> - The email should feel airy and scannable — like a text message chain, not a business letter.
> - If a paragraph has 3+ sentences, split it. Always.
> - Test: can someone scan this email in 10 seconds and get the gist? If not, add more spacing.

**Change 3: Strengthen the anti-AI-sounding instruction + diagnostic depth**
Add to VOICE & TONE section:
> ANTI-AI RULE: Read your draft back. If ANY sentence sounds like it came from a template, a LinkedIn post, or a marketing email — rewrite it. Real founders don't write "That's a sign your tools were never built to work together." They write "Your tools aren't talking to each other. That's the problem." Simple. Direct. Human.
>
> BUILD ON WHAT THEY SAID: When the prospect describes a problem, don't just restate it — go deeper. If they say "my tools aren't talking to each other," acknowledge it AND show diagnostic thinking: "You're right — and the real question is whether that's the root cause or just what's visible on the surface. Sometimes fixing that one thing clears up three other problems downstream." Show curiosity. Show that you're already thinking about their specific situation. Don't parrot — diagnose.
>
> DEMO CONTEXT: This person is testing a demo. They filled out a form to see what their own clients would receive if they hired Sharkitect to build this for them. They're evaluating the email quality as a potential buyer. The email needs to impress them — not as a recipient of outreach, but as someone judging whether this is good enough for THEIR customers. Write like a real founder who genuinely cares about getting to the root of the problem. Friendly. Genuine. Zero sales pressure. Show them this is the kind of quality their clients would get.

**Change 4: Fix hyperlink consistency**
Replace the current scheduling link instruction in BODY STRUCTURE section 3 with:
> MANDATORY: The booking link MUST appear as a clickable HTML hyperlink EVERY time. Never as plain text. Use EXACTLY this HTML:
> `<a href="https://www.sharkitectdigital.com/meetings/sharkitect/mvp-demo">schedule a time here</a>`
> This is not optional. If the link appears without the `<a href>` tag, the output is broken.

**Change 5: Lower the voice percentages to shift tone**
Replace voice percentages with:
> - 35% Conversational — talk like a real person, not a brand
> - 25% Precise — every sentence carries weight, no filler
> - 20% Engineering-minded — think in systems, not slogans
> - 15% Teacher — explain, don't sell; inform, don't pressure
> - 5% Defiant — subtly anti-hype; we do not sound like everyone else

**Change 6: Add 2-sentence example to READING LEVEL section (with casual warmth)**
Add example:
> EMAIL RHYTHM EXAMPLE (follow this pattern):
> BAD (wall of text):
> "I read that you're copying data between tools by hand. That's not a productivity problem. That's a sign your tools were never built to work together in the first place. What I'd like to show you is a diagnostic of how your current setup actually moves information."
>
> GOOD (scannable, warm, diagnostic):
> "I saw you're copying data between tools by hand. That's the kind of thing that eats hours without anyone noticing — until it starts cutting into your profits or your personal time.
>
> The good news? You already spotted it. That puts you ahead of most.
>
> I'd love to walk you through a quick look at how your setup actually moves information right now — not what it should do, but what it actually does. Sometimes fixing that one bottleneck clears up three other problems you didn't even know were connected."

**Change 7: Signature — plain text URL, no hyperlink (spam mitigation, ties to Bug #2 Fix C)**
Replace the current sign-off HTML block instruction. Keep the website URL but as PLAIN TEXT (not a clickable link). People can copy-paste it.
> Use exactly the following HTML sign-off block, verbatim:
> ```
> <p>Christopher Sharkey<br>
> Founder &amp; CEO<br>
> Sharkitect Digital – Your AI Transformation Partner<br>
> www.sharkitectdigital.com<br>
> <em>Architect The Future | Engineer Intelligence</em></p>
> ```
> IMPORTANT: www.sharkitectdigital.com must be PLAIN TEXT — no `<a href>` tag. This reduces clickable hyperlinks to 1 (the booking link only), lowering spam score for new/low-reputation senders while still showing the website for copy-paste.

### Model Decision
- Keep Claude Haiku (`claude-haiku-4-5-20251001`) — Chris confirmed
- If post-optimization output is still too stiff, we can test Sonnet as a fallback
- Haiku + well-structured prompt = cheaper ($0.003/email) and potentially MORE casual than larger models

### Current prompt location
"Write Email" node → `parameters.messages.values[0].content` (system prompt with voice guidelines, output format, etc.)

---

## Implementation Steps

### Step 0: Chris disables Jotform → Airtable native integration (MANUAL)
- Check BOTH forms in Jotform settings → Integrations
- Disable/delete any Airtable integration
- This is the primary fix for duplicates — must happen before testing

### Step 1: Create Suppressed Leads table (Airtable Metadata API)
- POST to create table with 7 fields
- Record new table ID for n8n node configuration

### Step 2: Apply prompt optimization (7 changes — FEEDBACK RECEIVED)
- Chris provided detailed feedback (2026-03-11) — see Issue #3 section above
- Apply all 7 prompt modifications to the Write Email node
- Route through Quill for final prompt review before push (prompt optimization is Quill's domain)
- Changes combined with Bug #2 Fix Part C (signature link removal)

### Step 3: Build and push workflow update (n8n REST API)
- Add 4 new nodes (Airtable Search, Code node for full-field comparison, IF router, Airtable Create for suppressed)
- Update Gmail node options (senderName + replyTo)
- Update Write Email prompt (per Chris's feedback + link density reduction)
- Rewire connections
- Single PUT to `/api/v1/workflows/e0lUI3Wdn9JdxEx2`
- POST to `/api/v1/workflows/e0lUI3Wdn9JdxEx2/activate`

### Step 4: Provide DMARC record to Chris
- Give exact TXT record for Namecheap update

### Step 5: Test end-to-end
- Submit test lead via Jotform webhook → verify SINGLE record + email sent with "Sharkitect Digital" sender name
- Submit same email again → verify suppressed (logged to Suppressed Leads table, no email sent)
- Confirm no ghost records (Jotform integration disabled)
- Check email inbox placement after DMARC update

### Step 6: Clean up test data
- Delete ghost records from Airtable (the ones with `jotform.com/inbox/` URLs)

### Step 7: Update documentation
- Node MEMORY.md: workflow update from 8→11 nodes, full-field dedup gate pattern, suppressed leads table, Jotform integration root cause
- Project MEMORY.md: mark RLR fix complete, update pending list

---

## Key Resources

| Resource | Value |
|----------|-------|
| Workflow ID | `e0lUI3Wdn9JdxEx2` |
| Airtable Base | `appYGAqZZHT7Neoej` (OFFER DEMOS) |
| RLR Table | `tblLLdNlP4NqUQL2q` |
| Airtable Credential (n8n) | `VrYcW7FeENjt8101` (MVP - Demos) |
| Gmail Credential (n8n) | `9e239W0Wo7skoNh8` (Solutions Gmail) |
| n8n API | `N8N_API_KEY` + `N8N_INST_URL` from .env |
| Airtable API | `AIRTABLE_API_SHARKITECT_AIOS_KEY` from .env |
| App Form ID | `260626660403149` |
| Experience Form ID | `260447926790063` |

## Verification

1. **Jotform integration disabled:** Submit form → only 1 Airtable record (no ghost with inbox URL)
2. **Dedup test — exact duplicate:** Same name + email + company + dropdown + text → logged to Suppressed Leads, no email sent
3. **Dedup test — different options:** Same email but different dropdown or text box → NEW record created, email sent (this is expected demo behavior)
4. **Email delivery:** Sender shows "Sharkitect Digital", reply-to set, reduced link density
5. **Prompt quality:** Email has max 2 sentences per paragraph, warm/casual tone, booking link is clickable, website URL in signature as plain text (not hyperlink), diagnostic depth when prospect describes a problem, no AI-sounding phrases
6. **Workflow active:** Confirm status = active after API update (11 nodes total)
7. **DMARC:** After DNS update, test email lands in inbox (not spam)
