# Voice Profiling Exercise — Plan

## Context

Chris's voice capture pipeline (`voice-write.py` + Supabase `voice_samples`) is live but nearly empty (3 samples). The brand identity guide defines *brand voice rules* but not Chris's *personal communication voice* — how he actually writes emails, adapts tone per audience, structures messages, opens/closes, etc. Without this data, AI-generated content requires manual correction every time instead of getting it right on the first draft.

This session seeds the voice database with 50+ samples by analyzing real emails Chris has sent, reviewing approved documents, running a live email exercise (KPI report to Juan), and going through structured Q&A to resolve ambiguities.

**What Chris told us explicitly:**
- Match his own voice AND mirror the client's tone/energy — while staying professional and authoritative
- Professional but casual (as the brand guide says)
- No filler phrases like "peace be with you" or "talk to you" — keep it clean
- Simple language, 5th-grade reading level, no jargon
- Wants to see conflicts between emails identified and resolved
- Wants options + questions to nail down preferences

---

## Phase 1: Email Extraction & Document Mining (~15 min)

**Goal:** Pull 15-25 of Chris's sent emails from Gmail (variety of audiences and contexts) + identify the best approved documents.

### 1.1 Extract emails via Gmail MCP
- Pull sent emails from BOTH `solutions@sharkitectdigital.com` AND `admin@sharkitectdigital.com`
- Target mix: emails to Juan/Emmanuel/Jesus (FF client), other prospects/clients, internal notes, follow-ups
- Chris has emailed several prospects/clients beyond FF — pull those for audience variety
- Get a range of dates (recent 2-3 months)
- Capture: subject, recipient, full body text, date

### 1.2 Catalog approved documents
- Read key deliverables already approved:
  - `proposal-exec-summary.md` (already read — strong example)
  - SOW Check Distribution Sync
  - KPI reports (Feb + Mar)
  - Any other client-facing docs
- These represent Chris's *approved* written voice for formal deliverables

### 1.3 Organize by category
- Group emails into: client (existing), prospect (cold/warm), internal, follow-up, delivery/handoff
- Note audience for each (Juan=CEO, Emmanuel=ops, Jesus=accounting, etc.)

**Files involved:** Gmail MCP tools, existing deliverables in `knowledge-base/clients/`

---

## Phase 2: Pattern Analysis (~20 min)

**Goal:** Identify Chris's actual voice patterns, consistency, and conflicts across all samples.

### 2.1 Structural patterns
- How does Chris open emails? (greeting style per audience)
- How does he close? (sign-off patterns)
- Average email length
- Paragraph structure (short/long, bullet points vs. prose)
- Subject line patterns

### 2.2 Tone patterns
- Formal ↔ casual spectrum per audience type
- How authority shows up (direct statements, qualifiers, hedging)
- Humor usage (if any)
- Energy level matching — examples of how Chris adapts to different recipients

### 2.3 Vocabulary patterns
- Common phrases Chris gravitates toward
- Phrases Chris never uses
- Technical vs. plain language choices
- Filler words or transitions he uses/avoids

### 2.4 Conflict detection
- Where does Chris's style differ between emails? (e.g., more formal in one, casual in another to same person)
- Do any emails contradict the brand guide?
- Are there patterns that conflict with what Chris just told us? (e.g., if some emails use jargon)
- Flag these for discussion in Phase 3

### 2.5 Produce analysis report
- Summarize findings in a structured format
- Present: "Here's what I found you do consistently" + "Here are conflicts/ambiguities"
- Prepare questions for Phase 3

---

## Phase 3: Findings Presentation & Discussion (~15 min)

**Goal:** Present analysis to Chris, resolve conflicts, get explicit approvals/rejections.

### 3.1 Present consistent patterns
- "You always do X" — confirm these as rules
- Log confirmed patterns as `approved` voice samples

### 3.2 Present conflicts
- "In email A you did X, in email B you did Y" — which do you prefer?
- "Your brand guide says X but your emails show Y" — which wins?
- Each resolution gets logged as approved + rejected pair

### 3.3 Present options for ambiguous areas
- Where data isn't clear, offer 2-3 options with examples
- Chris picks, we log

### 3.4 Capture new rules Chris states
- Anything Chris says during discussion ("I always..." / "Never..." / "I prefer...")
- Log immediately via `voice-write.py`

---

## Phase 4: Live Exercise — Email to Juan (~15 min)

**Goal:** Write a real email (sending KPI report to Juan) and use it as a training exercise.

### 4.1 Context gathering
- What's the relationship status with Juan right now?
- What's the tone Chris wants for this specific email?
- What needs to be communicated (KPI report delivery, any action items, next steps)?

### 4.2 Draft email
- Write first draft applying everything learned in Phases 1-3
- Present to Chris

### 4.3 Correction cycle
- Chris reviews, corrects, adjusts
- Every correction = `rejected` sample + `approved` sample + `correction` event
- Iterate until Chris says "that's it"

### 4.4 Format extraction
- From the approved final: extract the email format template
- Log: greeting style, structure, closing, length, tone markers

---

## Phase 5: Structured Q&A (~15 min)

**Goal:** Fill remaining gaps through targeted questions. Cover areas emails alone can't reveal.

### 5.1 Email-specific questions
Topics to cover (questions developed after Phase 2 analysis):
- Greeting preferences per relationship stage (new prospect vs. existing client vs. long-term)
- How do you handle bad news in email? (delays, price changes, problems)
- Follow-up timing and tone (first follow-up vs. second vs. third)
- How do you say "no" to a client request?
- Email length preference per type (quick update vs. deliverable handoff vs. proposal cover)

### 5.2 Document voice questions
- How much personality goes into formal docs (SOWs, proposals)?
- Section headers: functional ("Timeline") vs. branded ("Your Roadmap")?
- How do you handle uncertainty in docs? ("approximately" vs. specific ranges)

### 5.3 Audience adaptation questions
- How do you shift tone for: CEO (Juan) vs. ops manager (Emmanuel) vs. accounting (Jesus)?
- How do you write to a prospect you've never met?
- How do you write to someone who's frustrated or upset?

### 5.4 Capture all answers
- Each preference = voice sample or feedback memory
- Total target: 50+ samples across all phases

---

## Phase 6: Synthesis & Storage (~10 min)

**Goal:** Consolidate everything into the voice database and create a usable voice profile.

### 6.1 Bulk voice sample capture
- All approved/rejected pairs from Phases 2-5 logged via `voice-write.py`
- Verify sample count meets 50+ target

### 6.2 Create voice profile document
- Write `knowledge-base/governance/voice-profile-chris.md` — a distilled reference
- Structure: email patterns, document patterns, audience adaptation rules, prohibited patterns
- Cross-reference with brand-identity-guide.md (voice profile = personal voice within brand rules)

### 6.3 Update memory
- Update `user_chris_preferences.md` with new findings
- Add `feedback_email_voice.md` for email-specific rules
- Update MEMORY.md with session results

### 6.4 Verify pipeline
- Run `voice-write.py stats` to confirm sample count
- Confirm Supabase has all samples

---

## Verification

- [ ] 50+ voice samples in Supabase `voice_samples` table
- [ ] Voice profile document created and cross-referenced
- [ ] Live email to Juan approved and sent (or ready to send)
- [ ] All conflicts from email analysis resolved with explicit Chris decisions
- [ ] Memory files updated with new voice rules
- [ ] `voice-write.py stats` shows healthy distribution across content types and audiences

---

## Key Files

| File | Role |
|------|------|
| `~/.claude/scripts/voice-write.py` | Pipeline for logging samples |
| `knowledge-base/governance/brand-identity-guide.md` | Brand voice rules (existing) |
| `knowledge-base/governance/voice-profile-chris.md` | Personal voice profile (TO CREATE) |
| `memory/user_chris_preferences.md` | Existing preferences (TO UPDATE) |
| `memory/feedback_email_voice.md` | Email voice rules (TO CREATE) |
| Gmail MCP | Source of real emails |
| `knowledge-base/clients/fantastic-floors/*/deliverables/*` | Approved client documents |
