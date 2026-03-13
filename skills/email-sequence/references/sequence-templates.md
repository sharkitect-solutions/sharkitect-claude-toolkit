# Sequence Architecture Templates

Use these as starting structures. Customize timing, email count, and branching based on context from the user.

## Onboarding Sequence — SaaS Product (5-7 emails, 14 days)

```
E1: DELIVER — Welcome + single next step
│   Timing: Immediate (within 5 min)
│   Job: Deliver access, set expectations, one critical action
│   CTA: "Complete your setup" (deep link to first step)
│   → connects to E2 via: "Tomorrow I'll show you the fastest way to [first result]"
│
E2: TEACH — Quick win tutorial
│   Timing: +24 hours
│   Job: Enable their first small success
│   CTA: "Try it now" (deep link to feature)
│   → connects to E3 via: "Now that you've [done X], here's what [Customer] did next..."
│
E3: PROOF — Customer success story
│   Timing: +48 hours (Day 3)
│   Job: Show what's possible through someone relatable
│   CTA: "See how they did it" (case study link)
│   → connects to E4 via: Callback to their setup progress
│
│   [BRANCH POINT: Check if user completed key activation action]
│   ├─ YES → Skip to E5 (they're engaged, don't over-nurture)
│   └─ NO → Continue to E4
│
E4: OBJECTION — Address the #1 reason people stall
│   Timing: +48 hours (Day 5)
│   Job: Preemptively solve their hesitation
│   CTA: "Get help" or "Watch 2-min walkthrough"
│   → connects to E5 via: Pattern interrupt (shift from educational to personal)
│
E5: STORY — Personal note from founder/team
│   Timing: +72 hours (Day 7-8)
│   Job: Humanize the brand, create emotional connection
│   CTA: "Reply to this email" (engagement signal)
│   → connects to E6 via: "Next week I'll share our most powerful feature..."
│
E6: TEACH — Advanced feature highlight
│   Timing: +72 hours (Day 10-11)
│   Job: Show depth, create stickiness
│   CTA: "Try [advanced feature]"
│   → connects to E7 via: Sets up the ask
│
E7: CONVERT — Upgrade/commit push
    Timing: +72 hours (Day 13-14)
    Job: Close the loop — convert trial to paid or free to engaged
    CTA: "Upgrade now" or "Choose your plan"
    Exit: Sequence complete. Move to ongoing engagement.
```

**Exit conditions:** Converts at any point → exit + move to customer onboarding. Unsubscribes → exit. No opens on E1-E3 → move to re-engagement.

---

## Lead Nurture Sequence — Mid-Ticket Product (6-8 emails, 14-21 days)

```
E1: DELIVER — Lead magnet + introduce
│   Timing: Immediate
│   Job: Deliver the promised resource, brief intro
│   CTA: "Download your [resource]"
│   → connects to E2 via: "The guide covers X. But there's something it doesn't mention..."
│
E2: TEACH — Expand on lead magnet topic
│   Timing: +2 days
│   Job: Go deeper than the lead magnet, establish authority
│   CTA: "Read the full breakdown" (blog/content link)
│   → connects to E3 via: Escalation — surface problem → root cause
│
E3: TEACH — Problem deep-dive
│   Timing: +3 days (Day 5)
│   Job: Articulate their problem better than they can
│   CTA: "See if this applies to you" (quiz/assessment link, soft)
│   → connects to E4 via: "Most people try to fix this with [wrong approach]. Here's why..."
│
E4: STORY — The methodology origin story
│   Timing: +3 days (Day 8)
│   Job: Introduce your framework through narrative
│   CTA: Soft — "Reply if this resonates"
│   → connects to E5 via: Pattern interrupt after 3 heavy emails
│
E5: PROOF — Case study with specific numbers
│   Timing: +3 days (Day 11)
│   Job: Provide evidence your approach works
│   CTA: "See the full case study"
│   → connects to E6 via: "So [Customer] got [result]. The question is..."
│
│   [BRANCH POINT: High engagement (3+ opens, 1+ clicks)]
│   ├─ YES → E6 is a direct offer
│   └─ NO → E6 is another value email, push offer to E7
│
E6: OBJECTION — Address the "why not" head-on
│   Timing: +4 days (Day 15)
│   Job: Handle price, timing, or "I can do this myself" objection
│   CTA: "See the options" (pricing page, soft)
│   → connects to E7 via: Building urgency
│
E7: CONVERT — Direct offer with urgency
│   Timing: +4 days (Day 19)
│   Job: Make the ask clearly
│   CTA: "Start now" / "Get [product]"
│   → connects to E8 via: Only if E7 doesn't convert
│
E8: CONVERT — Final push / last chance (optional)
    Timing: +2 days (Day 21)
    Job: Deadline, scarcity, or reframe
    CTA: "Last chance" / "Doors close [date]"
    Exit: Sequence complete. Non-converters move to long-term newsletter.
```

---

## Re-Engagement Sequence — SaaS Usage Drop (3-5 emails, 14 days)

```
E1: TEACH — Value reminder disguised as help
│   Timing: Triggered by inactivity threshold (e.g., 14 days no login)
│   Job: Re-engage through usefulness, not guilt
│   CTA: "Check out what's new" or "Try this tip"
│   → connects to E2 via: If no response, shift to personal
│   IMPORTANT: Do NOT say "We noticed you haven't logged in" — it's creepy and accusatory.
│   Instead: "Here's something our most successful users do with [feature]..."
│
E2: STORY — Personal check-in from team
│   Timing: +3 days
│   Job: Human touch — are they stuck? Is something wrong?
│   CTA: "Reply to this email" or "Book a quick call"
│   → connects to E3 via: Escalate the stakes
│
E3: PROOF — What they're missing (social proof + FOMO)
│   Timing: +4 days (Day 7)
│   Job: Show what active users are achieving
│   CTA: "Log in and try [specific feature]"
│   → connects to E4 via: Final attempt before backing off
│
│   [BRANCH POINT: Any engagement (open + click)]
│   ├─ YES → Exit re-engagement, return to normal communications
│   └─ NO → Continue to E4
│
E4: CONVERT — Offer or ultimatum
│   Timing: +7 days (Day 14)
│   Job: Last real attempt — offer incentive or ask directly
│   CTA: "Claim your [discount/extended trial]" or "Should we close your account?"
│   Exit: If no response → suppress from active sequences, move to quarterly win-back.
```

---

## Win-Back Sequence — Cancelled Customers (3 emails, 60-90 days)

```
E1: TEACH — What's new since they left
│   Timing: 14-30 days post-cancellation
│   Job: Show genuine product improvements (not begging)
│   CTA: "See what's changed" (changelog or feature page)
│   Tone: Confident, no desperation. "We've been busy" not "We miss you."
│   → connects to E2 via: Long gap — let them process
│
E2: PROOF — Customer return story
│   Timing: 45-60 days post-cancellation
│   Job: Normalize coming back through someone else's story
│   CTA: "Read [Customer]'s story" (case study)
│   → connects to E3 via: Set up the offer
│
E3: CONVERT — Incentive to return
    Timing: 75-90 days post-cancellation
    Job: Make return easy and incentivized
    CTA: "Reactivate with [X% off / free month]"
    Exit: Sequence complete. No further emails unless they opt back in.
```

**Key win-back rule:** If you know WHY they cancelled (from exit survey), reference it: "You mentioned [reason]. Here's what we did about it." This alone can double win-back conversion.

---

## Expansion Sequence — Free to Paid Upgrade (3-5 emails, 7-14 days)

```
E1: TEACH — Show what they're missing
│   Timing: Triggered by usage limit hit or premium feature attempt
│   Job: Frame the upgrade as unlocking what they already want
│   CTA: "See what [plan] includes"
│   → connects to E2 via: "Here's what [similar user] got after upgrading..."
│
E2: PROOF — Upgrade success story
│   Timing: +3 days
│   Job: Show ROI through real example
│   CTA: "Calculate your savings" (ROI calculator link, if available)
│   → connects to E3 via: Address the hesitation
│
E3: OBJECTION — Price objection handled
│   Timing: +3 days
│   Job: Reframe price as investment with data
│   CTA: "Start your upgrade"
│   → connects to E4 (optional) via: Add urgency
│
E4: CONVERT — Urgency/incentive (optional)
│   Timing: +3 days
│   Job: Limited-time discount or about-to-lose-access framing
│   CTA: "Upgrade before [date]"
│   Exit: Sequence complete. If no conversion → return to free user communications.
```

---

## Email Copy Structure Reference

### Per-Email Anatomy

```
SUBJECT LINE: [35-50 chars, position-appropriate — see Rule 3 in SKILL.md]
PREVIEW TEXT: [Extends subject, 90-140 chars, never repeats subject]

[HOOK — 1 sentence max. Earns the next sentence.]

[CONTEXT — 1-2 sentences. Why this matters to THEM right now.]

[VALUE — The substance. Keep to one idea. Format varies by email role:
  - TEACH: Insight, framework, or tactic (3-5 short paragraphs or bullets)
  - STORY: Narrative arc (situation → complication → resolution)
  - PROOF: Specific metrics and quotes (before → after)
  - OBJECTION: State the objection honestly → reframe → evidence]

[CTA — One primary call to action. Button for primary, text link for secondary.
  Button text = Action verb + outcome: "Get your plan" not "Click here"
  Place CTA after value delivery, never before.]

[SIGN-OFF — Human, warm, brief. First name of sender.]
```

### Word Count Targets by Email Role

| Role | Word Count | Why |
|------|-----------|-----|
| Deliver | 75-125 | Get out of the way. Deliver the thing. |
| Teach | 200-350 | Enough to provide real value, short enough to finish. |
| Story | 250-400 | Stories need room to breathe but must stay tight. |
| Proof | 150-250 | Let the data and quotes do the work. |
| Objection | 150-300 | State it, reframe it, prove it. Done. |
| Convert | 100-200 | The sequence did the work. Be direct. |
