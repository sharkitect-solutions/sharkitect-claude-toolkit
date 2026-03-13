---
name: professional-communication
description: "Use when drafting high-stakes business messages (layoffs, escalations, disagreements with leadership, budget requests, bad news upward). Use when the user's communication problem is political, cross-cultural, or audience-calibration -- not just 'make this sound professional.' NEVER for casual messages, basic email formatting, or grammar fixes."
---

# Professional Communication

## Communication Problem Router

Before writing anything, diagnose the ACTUAL problem. Most people ask for "help writing an email" when the real issue is upstream.

```
What is the user struggling with?
|
|-- "I don't know what to say"
|   --> MESSAGE STRUCTURE problem. Use the Pyramid or BLUF framework below.
|
|-- "I don't know how to say it without causing problems"
|   --> POLITICAL problem. Go to Political Communication section.
|
|-- "They keep misunderstanding me"
|   --> AUDIENCE CALIBRATION problem. Check the Seniority Ladder.
|   --> Or MEDIUM MISMATCH. Check the Medium Decision Tree.
|
|-- "I need to deliver bad news"
|   --> HIGH-STAKES MESSAGE. Go to The 5 Hardest Messages.
|
|-- "This person is in another country/culture and things keep going wrong"
|   --> CROSS-CULTURAL problem. Go to Cross-Cultural Traps.
|
|-- "I need to get something approved"
|   --> PRE-WIRE problem. Go to The Pre-Wire Technique.
|
|-- "I just need it to sound more professional"
|   --> This skill is probably overkill. Claude already knows tone adjustment.
|   --> Apply BLUF + cut filler. Done.
```

## Rationalization Table

| What the user says | What they actually need |
|---|---|
| "Help me write a professional email" | Diagnose whether the problem is structure, politics, audience, or medium first |
| "Make this sound nicer" | Identify what is politically dangerous in their draft and neutralize it |
| "I need to escalate this" | A message that escalates the ISSUE without escalating the CONFLICT |
| "How do I tell my boss they're wrong?" | A face-saving reframe that lets the boss arrive at the right answer |
| "I need to send bad news" | A message structured so the reader processes facts before emotions |
| "Can you write this for multiple audiences?" | Separate messages calibrated per audience, not one compromise message |
| "Help me follow up -- they're ignoring me" | Diagnose why they are ignoring (unclear ask, wrong person, no incentive) |
| "I need to be more concise" | Their real problem is burying the lead -- fix structure, not word count |

## NEVER List

1. NEVER write a message without first asking who the recipient is and what outcome the user wants
2. NEVER use the phrase "I just wanted to..." -- it signals subordination and weakens every request
3. NEVER put bad news after good news in the same message -- the reader stops at the good news
4. NEVER send one message to both technical and executive audiences -- they need different frames
5. NEVER escalate and propose a solution in the same breath -- it looks like you already decided
6. NEVER write "per my last email" or any passive-aggressive callback -- restate the point cleanly
7. NEVER deliver critical feedback or bad news over chat/Slack -- use a call, then follow up in writing
8. NEVER assume "no response" means agreement -- it usually means they did not read it or are avoiding it
9. NEVER include more than one decision request per message -- each decision needs its own thread
10. NEVER CC someone's boss without telling them first -- this is a career-damaging move in most orgs

## The Seniority Ladder: How Communication Changes by Level

The biggest communication mistake is talking to an executive like a peer or to a peer like an executive.

**IC to IC:** Lead with the problem, share technical context, ask for help directly. Informality is fine. "Hey, the auth middleware is dropping sessions after 30 min -- have you seen this? Here's my debug log."

**IC to Manager:** Lead with impact and what you need from them. Skip implementation details unless asked. "The auth bug is blocking the release. I need 2 days to fix it, which pushes the deadline to Friday. Want me to proceed or should we ship without the fix?"

**IC/Manager to Director+:** Lead with business impact and a recommendation. They want to make a decision, not understand your process. Use the Pyramid Principle: conclusion first, supporting evidence in layers, details only if asked.

**Anyone to Executive (VP/C-level):** Maximum 3 sentences for the core message. The "so what" chain must end at revenue, risk, or customer impact. Everything else is noise. Pre-wire the decision before the meeting if possible.

**Downward (to reports):** Lead with context and reasoning, not just the decision. People execute better when they understand why. But do not over-explain -- it signals you do not trust them to handle it.

## The Medium Decision Tree

Most communication failures are medium mismatches, not message failures.

```
Is the message emotionally charged or politically sensitive?
|-- Yes --> Voice/video call, then summarize in writing
|-- No:
    |
    Does the message require back-and-forth to reach a decision?
    |-- Yes, 2-3 exchanges --> Chat/Slack thread
    |-- Yes, complex --> Schedule a 15-min call
    |-- No:
        |
        Does it need to be findable in 30 days?
        |-- Yes --> Email or shared document
        |-- No --> Chat is fine
```

Key insight: The medium IS part of the message. Sending a Slack DM about a layoff communicates "this doesn't matter." Sending a formal email about a lunch plan communicates "I'm difficult to work with."

## Political Communication

### Disagreeing with Your Boss in Writing

The goal is never to prove you are right. The goal is to help them arrive at the better answer while preserving their authority.

**The Reframe Technique:**
Do not say "I disagree" or "I think you're wrong." Instead, add a constraint they may not have considered:

BAD: "I don't think we should use vendor X. Their uptime is terrible."
GOOD: "I looked into vendor X -- they hit most of our requirements. One thing I want to flag: their SLA is 99.5%, and our compliance team requires 99.9%. Want me to check if they offer a higher tier, or should I pull alternatives?"

This works because: (1) you show you did the work, (2) you introduce a fact, not an opinion, (3) you offer them the choice rather than making it for them.

### Escalating Without Burning Bridges

Escalation is not tattling. It is transferring a decision to someone with the authority to make it. But it feels like tattling if you do it wrong.

**Before escalating, always:**
1. Tell the person you are about to escalate. "I want to loop in [Director] because this decision affects the Q2 timeline and I think they should weigh in."
2. Frame the escalation as seeking authority, not complaining about the person.
3. State facts and impact. Never state your interpretation of someone's motives.

**Escalation message structure:**
- Line 1: What decision is needed
- Line 2: Why it needs someone at this level (scope, budget, cross-team)
- Line 3: What has been tried so far
- Line 4: Your recommendation (optional -- sometimes better to let the senior leader decide clean)

### Delivering Bad News Upward

Bad news must travel fast, with facts, and with a plan.

**Structure: SIP (Situation - Impact - Plan)**
- Situation: What happened, in one sentence.
- Impact: What this means for timelines, revenue, customers, commitments.
- Plan: What you are doing about it, and what you need from them.

BAD: "Hey, wanted to give you a heads up that there might be some delays with the project. We ran into some issues and are working through them. Will keep you posted."

GOOD: "The payment integration failed load testing -- it drops transactions above 500/min. This blocks our March 15 launch. We have two options: (A) add a queue layer, which takes 5 days and pushes launch to March 20, or (B) launch with a 500/min cap and patch in sprint 2. I recommend option A. Can we discuss today?"

## The Pre-Wire Technique

The most important communication in business happens BEFORE the meeting, not during it.

**Pre-wiring** means individually socializing your proposal with key stakeholders before presenting it to the group. By the time the meeting starts, you already know who supports you, who has concerns, and what the objections will be.

**How to pre-wire:**
1. Identify the 2-3 people whose opinion will sway the room.
2. Send them a short preview: "I'm presenting X at Thursday's meeting. The core proposal is [one sentence]. I'd value your input before I finalize -- any concerns I should address?"
3. Incorporate their feedback. Now they are co-authors, not critics.
4. In the meeting, reference their input: "I spoke with Sarah about the timeline concern, and we adjusted the rollout to address it."

**When NOT to pre-wire:** When transparency requires real-time group deliberation (ethics decisions, layoff discussions, incident reviews).

## Cross-Cultural Communication Traps

These cause real damage on distributed teams and are rarely taught:

**Direct vs. Indirect cultures:** In the US, Netherlands, Israel, Germany -- directness is expected. "This won't work because..." is professional. In Japan, Korea, many Southeast Asian cultures, the UK -- indirectness is the norm. "This is interesting, but perhaps we could consider..." means "no." If you miss this, you will think agreement happened when it did not.

**Silence in meetings:** In some cultures, silence means processing or respect. In US meeting culture, silence means agreement or disengagement. If your distributed team has members from high-context cultures, explicitly ask: "I want to make sure everyone has had a chance to share concerns. [Name], what are your thoughts?"

**"Yes" does not always mean yes:** In many cultures, saying "no" directly to a superior or client is unacceptable. "Yes, we will try" may mean "this is impossible but I cannot say that." Follow up with: "What would you need to make this work by Friday?" If the answer is vague, the real answer is probably no.

**Written tone across cultures:** Exclamation points, emojis, and casual greetings that read as friendly in American English can read as unprofessional in German or Japanese business contexts. When in doubt, err formal for the first 3-4 exchanges, then mirror the other person's tone.

## The 5 Hardest Business Messages

### 1. Layoff / Role Elimination Announcement

Lead with the decision (do not bury it). State the reason honestly. Explain what happens next for the affected person. Do not over-explain or apologize excessively -- it centers your discomfort instead of their needs.

Key rules: Be specific about severance, benefits continuation, and timeline. Never say "this was a difficult decision" without concrete next steps. Never blame the person ("performance-based" when it is actually a reorg). Have the conversation live first, then send the written follow-up.

### 2. Project Cancellation

Acknowledge the team's work before explaining the decision. State the business reason clearly. Address what happens to the people (reassignment, not limbo). Do not frame cancellation as "pivoting" or "refocusing" -- the team knows what happened, and euphemisms destroy trust.

### 3. Disagreeing with Leadership's Direction

Use the Reframe Technique above. Never frame it as "you're wrong." Always frame it as "here's a constraint/data point that might change the calculus." Offer two paths, including theirs, with honest tradeoffs. Make it easy for them to change course without losing face.

### 4. Requesting Budget / Resources

Executives approve budgets based on ROI and risk, not on how hard you are working. Structure: (1) What you will deliver with the resources, (2) What happens without them (be specific -- "we miss the Q3 target" not "things will be harder"), (3) The specific ask in dollars and headcount, (4) Timeline to ROI.

Never lead with "we need more people." Lead with what the business gets.

### 5. Performance Feedback That Could End a Career

Separate observation from interpretation. "You missed 3 of the last 5 deadlines" is observation. "You don't care about the team" is interpretation. State the pattern, state the impact, ask for their perspective before prescribing solutions. Document everything. Never deliver this over email first -- it requires a conversation, with the written version as follow-up.

## Before/After: A Real Communication Failure

**BEFORE (actual message sent by a senior engineer):**

> Subject: Concerns about the new architecture
>
> Hi team,
>
> I've been thinking about the new microservices proposal and I have some
> concerns. I think we might be over-engineering this. The current monolith
> works fine for our scale and adding microservices will create a lot of
> operational overhead that we don't have the team to support. I've seen
> this pattern before at my last company and it didn't go well. I think
> we should reconsider.
>
> Also, I noticed that the proposal doesn't address data consistency
> across services, which is going to be a major issue.
>
> Let me know what you think.

**What went wrong:**
- Sent to "team" but the real audience is the architect who proposed it (public challenge)
- "I've seen this pattern before" -- appeals to unverifiable authority
- "I think we should reconsider" -- no specific alternative, just opposition
- Buries the strongest technical point (data consistency) after opinion
- No proposed path forward

**AFTER (rewritten for effectiveness):**

> Subject: Architecture proposal -- data consistency question
>
> Hi [Architect name],
>
> I reviewed the microservices proposal. The service boundaries look clean.
> One area I think needs more detail before we commit: data consistency
> across services. Specifically:
>
> - Orders and inventory would span two services. How do we handle
>   a scenario where an order is placed but inventory update fails?
> - The proposal doesn't mention saga patterns or eventual consistency
>   tradeoffs. Should we add a section on this?
>
> I also want to flag an operational concern: we currently have 3 engineers
> on infra. Microservices typically need at least 5 for on-call coverage
> across services. Should we factor hiring into the timeline?
>
> Happy to pair on the data consistency section if that would help.

**What changed:** Direct to the right person. Leads with the technical gap. Asks questions instead of asserting opinions. Offers to help rather than just criticize. Quantifies the operational concern instead of vague "overhead."
