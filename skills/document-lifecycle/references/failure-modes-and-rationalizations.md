# Failure Modes and Rationalizations

Expert reference for document lifecycle anti-patterns, their consequences, and the rationalizations that enable them.

## Named Failure Modes

### 1. The Rubber Stamp

**Pattern:** Confirming every document "looks good" without reading it or quoting any specific assertion.

**Why it happens:** Time pressure. The review feels like bureaucracy, not value. The Agent reasons: "This doc was fine last time, it's probably fine now."

**Consequence:** Stale information persists silently. A pricing doc confirmed as "accurate" with outdated rates leads to proposals quoting wrong numbers. A strategy doc confirmed without reading leads to content targeting the wrong market for weeks until someone notices. In testing across 30+ document reviews, rubber-stamped reviews missed drift 4x more often than reviews that quoted specific assertions.

**Detection signals:**
- Review completes in under 30 seconds for a multi-page document
- Confirmation message contains no specific quotes or assertions from the document
- Review summary is generic: "Reviewed and confirmed accurate" with no details
- Same confirmation language used across multiple different documents

**Fix:** Quote at least one specific assertion from the document when confirming accuracy. "Your pricing shows Starter at $500/month and Growth at $1,200/month -- still current?" proves the document was read. The act of extracting a quote forces actual reading.

---

### 2. The Infinite Defer

**Pattern:** Always pushing reviews to "later" without ever completing them.

**Why it happens:** Every individual deferral seems reasonable. "The user is busy." "This isn't urgent right now." "Next session for sure." But deferrals compound -- each one makes the next easier to justify.

**Consequence:** Documents age past usefulness. A strategy doc deferred for 3 weeks during a business pivot becomes a dangerous artifact -- it describes a direction the business has already abandoned, but anyone reading it (including AI agents in other workspaces) treats it as current truth. Deferred pricing docs during a rate increase mean every auto-generated proposal quotes old rates.

**The math:** If a 60-day cycle document gets deferred 3 times (each deferral adds ~5 days), the document is now 75+ days old. For pricing documents, that's 2.5 months of potential rate changes, package restructuring, or discount policy shifts that aren't reflected.

**Detection signals:**
- Same document deferred 2+ times in a row
- Deferral reasons are vague: "not a good time" rather than "blocked by X until Y"
- Pattern of deferring ALL documents, not just specific ones
- Documents reaching "overdue" or "critical" states regularly

**Fix:** Hard stop after 2 deferrals. The third triggers critical state with risk-specific messaging. No exceptions. The escalation ladder exists precisely because informal "I'll do it later" fails systematically.

---

### 3. The Partial Review

**Pattern:** Only checking sections related to current work, skipping the rest.

**Why it happens:** Efficiency instinct. "I'm working on pricing, so I'll check the pricing sections." The unreviewed sections feel irrelevant to the current task.

**Consequence:** Drift hides in sections you're NOT actively using. A client document's scope section may be current (you're delivering against it), but the contact list is 3 months stale (the original contact left the company). When you need to email the client, you use the wrong person. Strategy documents are worst: the mission statement section stays stable, but the target market section (which you don't reference during internal work) drifts silently.

**The insight:** Sections that are actively used get implicitly validated through daily work. Sections that are NOT used have zero implicit validation -- scheduled review is their ONLY quality check.

**Detection signals:**
- Review summary mentions only one section of a multi-section document
- Review time is proportional to one section, not the full document
- Same sections confirmed every review, other sections never mentioned
- "Skipped sections X, Y, Z -- not relevant to current work"

**Fix:** Full document scan during scheduled reviews, not just the triggered section. Drift resolution (Mode 1) can be section-specific because it's triggered by specific work. Scheduled review (Mode 2) must be comprehensive because it's the safety net.

---

### 4. The Silent Update

**Pattern:** Updating a document without recording what changed in the lifecycle metadata.

**Why it happens:** The update feels self-documenting. "I changed the pricing from $500 to $750 -- anyone reading the doc will see the new price." Recording the change in `last_review_summary` feels redundant.

**Consequence:** Review history is lost. Without a summary of what changed, future reviewers can't distinguish "confirmed unchanged" from "updated significantly." When a document has been reviewed 5 times, the review history should tell the story: "Confirmed accurate" -> "Updated pricing tier names" -> "Major revision: new target market" -> "Confirmed after expansion." Without summaries, it's just 5 timestamps with no context.

**Downstream impact:** Sentinel's freshness reports lose their diagnostic value. A document showing "5 reviews, 0 change descriptions" is opaque -- was it stable for 5 cycles, or did it change every time with no record?

**Detection signals:**
- `last_review_summary` is empty or generic ("updated")
- Document content changed (git diff) but lifecycle shows "confirmed" not "updated"
- Multiple consecutive reviews with no summary text

**Fix:** Always include `last_review_summary` describing what changed and why. Even confirmations benefit: "Confirmed: pricing unchanged since last review, all 3 tiers verified against recent proposals." The summary is the audit trail.

---

### 5. The Question Dump

**Pattern:** Asking the user to confirm 15+ assertions at once during a scheduled review.

**Why it happens:** Thoroughness instinct. "I should check everything." The Agent reads the document, identifies every potentially stale assertion, and presents them all in one message.

**Consequence:** Cognitive overload triggers rubber-stamping. When presented with 15 questions, users don't carefully evaluate each one -- they pattern-match to "yes, that's all fine." Testing shows that confirmation accuracy drops significantly after the 5th question in a single review. By question 10+, users are confirming assertions they haven't actually verified.

**The research:** Decision fatigue is well-documented. A judge making parole decisions is more likely to deny at the end of a long session. A user confirming document accuracy follows the same pattern -- the later questions get less attention.

**Detection signals:**
- Review message contains 6+ numbered questions
- All questions are confirmed with a single "yes" or "looks good"
- Questions cover multiple sections (should be batched across reviews)
- Questions include items the Agent could have verified from context

**Fix:** Maximum 3-5 targeted questions per document. Source from brain memories first (recent decisions, activity). Only ask the user about things you truly can't verify from available context. If a document has 15 potentially stale assertions, split into multiple review sessions rather than dumping all at once.

---

## Rationalization Table

These thoughts indicate you're about to skip or shortcut a review. Each has a surface logic that falls apart under examination.

| Rationalization | Surface Logic | Why It Fails | What To Do Instead |
|---|---|---|---|
| "I just reviewed this last week" | Feels recent enough | The review cycle is computed, not felt. Time perception is unreliable. Check the metadata -- `last_reviewed` and `next_review` are the source of truth, not your memory of when you last looked at it. | Run `supabase-sync.py pull-lifecycle` and check the actual dates. Trust the system, not the feeling. |
| "Nothing has changed" | Workspace seems stable | You don't know what changed outside your sessions. Client calls, market shifts, team decisions, pricing adjustments -- these happen between AI sessions. A document's stability can only be confirmed by reading it, not by assuming it. | Read the document. Compare against recent brain memories. Ask 2-3 targeted questions about the most likely-to-change sections. |
| "This is just a config file" | Low perceived importance | Config drift causes cascading tool failures across every workspace. A wrong Supabase URL, a deprecated API endpoint, a renamed environment variable -- these are silent until they break something critical during production work. Technical docs have shorter cycles (60 days) for exactly this reason. | Treat technical documents with the same rigor as strategy documents. A wrong config breaks tools. A wrong strategy breaks proposals. Both matter. |
| "The user is busy right now" | Respecting their time | Stale docs waste MORE time than the review takes. A 5-minute pricing review prevents a 2-hour proposal rework when the client notices wrong numbers. A 10-minute strategy review prevents a week of content targeting the wrong audience. The review cost is always less than the stale-information cost. | Use the deferral mechanism if timing is genuinely bad. But defer formally (tracked, with re-ask) -- never informally skip. |
| "I'll check it next session" | Feels like a reasonable delay | Next session you'll say the same thing. Informal postponement has no tracking, no re-ask, no escalation. The document drops off the radar entirely. Formal deferral (escalation_state=deferred, deferred_at=now) ensures it comes back. Informal postponement is a memory hole. | Either review now or defer formally using the deferral command. There is no third option. |

## Failure Mode Interactions

Failure modes rarely appear alone. They combine and reinforce each other:

| Combination | How It Works | Severity |
|---|---|---|
| Rubber Stamp + Infinite Defer | "Looks good" on documents you never fully read, defer the ones that would take effort | Critical -- the easiest documents get false confirmation, the hardest get no review at all |
| Partial Review + Silent Update | Check one section, update it, record nothing about what changed or what wasn't checked | High -- creates false confidence that the full document is current |
| Question Dump + Rubber Stamp | Present 15 questions, user rubber-stamps all of them with "yes" | High -- feels thorough but produces no actual verification |
| Infinite Defer + "User is busy" | Use time pressure as permanent justification for never reviewing | Critical -- document becomes permanently stale with a seemingly valid excuse |

## Recovery Procedures

When you detect a failure mode in progress:

| State | Recovery |
|---|---|
| **Caught mid-rubber-stamp** | Stop. Go back. Read the document. Quote 3 specific assertions before confirming. |
| **Caught mid-defer-chain** | Acknowledge the pattern. Present the specific risk for this document category. Complete the review now. |
| **Caught mid-partial-review** | Expand to full document scan. Note which sections were initially skipped and why. |
| **Caught mid-question-dump** | Trim to the 3-5 highest-priority questions. Move remaining items to a follow-up review. |
| **Caught post-silent-update** | Write the summary retroactively: `push-lifecycle "<doc_path>" last_review_summary="<what changed>"` |