---
name: marketing-psychology
description: "Use when applying psychological principles or mental models to marketing copy, pricing, landing pages, or conversion optimization. Also use when analyzing why a marketing approach is or isn't working through a behavioral science lens. NEVER use for clinical psychology, academic research, or non-marketing behavioral analysis."
version: "2.0"
optimized: true
optimized_date: "2026-03-11"
---

# Marketing Psychology & Mental Models

**Check first**: If `.claude/product-marketing-context.md` exists, read it before applying models. Tailor all recommendations to that specific product and audience.

## File Index

| File | Purpose | When to Load |
|---|---|---|
| SKILL.md | Mental Model Quick Index, Challenge-to-Model mapping, Psychology Conflict Resolution, Common Misapplication, Ethical Boundaries | Always (auto-loaded) |
| quantified-effects-reference.md | Effect sizes with study citations for 20+ principles: anchoring (20-50% shift, Tversky & Kahneman 1974), decoy effect (32%->62%, Ariely 2008), social proof (+26%, Goldstein et al. 2008), loss aversion (1.5-2.5x, Kahneman & Tversky 1979), paradox of choice (10x conversion difference, Iyengar & Lepper 2000), and boundary conditions for each | Load when the user needs data to justify a psychological approach, wants to know "how much impact does X have?", or is prioritizing which principles to apply based on expected effect size. Do NOT load for general principle selection when effect size doesn't matter. |
| application-failure-modes.md | When principles backfire: social proof backfire scenarios (5), scarcity reactance thresholds (5), loss aversion ceiling by price point (5 ranges), cultural variance across 4 regions, principle stacking diminishing returns, defaults-to-dark-patterns boundary | Load when applying a specific principle and checking whether it will backfire in context, diagnosing why a psychological approach isn't working, targeting international audiences, or when the user asks "when does X not work?" Do NOT load for basic principle definitions. |
| dark-pattern-regulations.md | Dark pattern taxonomy (9 types with jurisdictions), EU DSA Article 25 specifics, FTC Click-to-Cancel and Negative Option Rules (2024), California ARL/CCPA/CPRA, UK DMCC Act 2024, compliance checklist for 10 common tactics, safe pattern alternatives | Load when the user's marketing targets regulated markets, when reviewing tactics for legal compliance, or when recommending urgency/scarcity/default tactics that may cross regulatory lines. Do NOT load for general psychology application in non-compliance contexts. |

---

## Mental Model Quick Index

| Category | Models | When to Apply |
|----------|--------|---------------|
| Foundational Thinking | First Principles, Jobs to Be Done, Inversion, Pareto, Occam's Razor, Second-Order Thinking, Theory of Constraints, Opportunity Cost, Barbell Strategy, Map != Territory, Probabilistic Thinking, Local vs. Global Optima, Law of Diminishing Returns | Strategy framing and problem diagnosis |
| Buyer Psychology | Loss Aversion, Endowment Effect, Status-Quo Bias, Sunk Cost Fallacy, Hyperbolic Discounting, Regret Aversion, Zero-Price Effect, IKEA Effect, Mental Accounting, Zeigarnik Effect, Goal-Gradient Effect, Peak-End Rule, Paradox of Choice, Default Effect, Pratfall Effect | Understanding why customers do or don't buy |
| Persuasion | Reciprocity, Scarcity, Authority, Social Proof, Commitment & Consistency, Liking/Similarity, Unity Principle, Foot-in-the-Door, Door-in-the-Face, Framing Effect, Contrast Effect, Mimetic Desire, Mere Exposure Effect, Confirmation Bias, Availability Heuristic, Bandwagon Effect | Crafting offers, CTAs, and trust signals |
| Pricing | Anchoring, Charm Pricing, Decoy Effect, Rule of 100, Rounded-Price Effect, Price Relativity/Good-Better-Best, Mental Accounting (pricing) | Setting and presenting prices |
| Design & Delivery | Hick's Law, BJ Fogg Behavior Model, EAST Framework, COM-B Model, Nudge Theory, AIDA Funnel, Rule of 7, Activation Energy, North Star Metric, Cobra Effect | Page layout, UX, and campaign structure |
| Growth & Scaling | Network Effects, Flywheel Effect, Switching Costs, Compounding, Feedback Loops, Critical Mass, Exploration vs. Exploitation, Survivorship Bias, Lindy Effect | Retention, scaling, and channel strategy |

---

## Challenge-to-Model Quick Reference

| Challenge | Relevant Models |
|-----------|-----------------|
| Low conversions | Hick's Law, Activation Energy, BJ Fogg, Framing Effect |
| Price objections | Anchoring, Framing, Mental Accounting, Loss Aversion |
| Building trust | Authority, Social Proof, Reciprocity, Pratfall Effect |
| Increasing urgency | Scarcity, Loss Aversion, Zeigarnik Effect |
| Retention / churn | Endowment Effect, Switching Costs, Status-Quo Bias |
| Growth stalling | Theory of Constraints, Local vs. Global Optima, Compounding |
| Decision paralysis | Paradox of Choice, Default Effect, Nudge Theory |
| Onboarding | Goal-Gradient, IKEA Effect, Commitment & Consistency |

---

## Psychology Conflict Resolution

When two principles pull in opposite directions, use this table to decide which wins.

| Conflict | Resolution | Reasoning |
|----------|------------|-----------|
| Scarcity vs. Social Proof | New visitors: Social Proof wins. Returning visitors: Scarcity wins. | Trust must be established before urgency is credible. Urgency without trust reads as pressure. |
| Loss Aversion vs. Positive Framing | Loss framing for high-consideration decisions; positive framing for low-risk entry offers. | Loss framing amplifies stakes - useful when switching cost is high, counterproductive for low-commitment asks. |
| Reciprocity vs. Zero-Price Effect | Zero-Price for acquisition; Reciprocity for upgrade. | Free removes the evaluation friction at the top of funnel. Once inside, the relationship dynamic shifts to obligation. |
| Paradox of Choice vs. Good-Better-Best | Three tiers maximum. Present a single "recommended" default. | Choice architecture lets you have both: options exist but the default removes the paralysis. |
| Authority vs. Liking/Similarity | B2B and regulated categories: Authority leads. Consumer and community products: Similarity leads. | Buyers calibrate whose opinion they trust based on identity and risk profile of the purchase. |
| Commitment & Consistency vs. Door-in-the-Face | Use Foot-in-the-Door for nurture sequences; Door-in-the-Face for one-shot negotiation contexts. | Foot-in-the-Door builds an identity ("I'm a customer"). Door-in-the-Face is a one-time contrast play and doesn't build identity. |

---

## Common Misapplication Table

| Misapplication | What Goes Wrong | Correct Use |
|----------------|-----------------|-------------|
| Scarcity on non-scarce items | "Only 3 left!" on a digital product. Erodes trust permanently when buyers realize the scarcity is false. | Reserve scarcity for genuine time-limits (cohort close, sale end) or actual inventory constraints. |
| Loss Aversion for low-stakes offers | Aggressive loss framing on a $9 ebook triggers reactance, not urgency. | Match framing intensity to decision stakes. Loss framing earns its weight on high-ticket or irreversible decisions. |
| Anchoring with an unbelievable high | $10,000 crossed out to $47 on an unknown product. The anchor destroys credibility rather than reframing value. | Anchor must be believable and justified (competitor price, original price, component value). |
| Reciprocity with low-value "gifts" | A PDF checklist no one asked for, followed immediately by a hard pitch. | The gift must be genuinely useful and given without immediate strings. Delay the ask. |
| Default Effect without transparency | Pre-checked newsletter boxes in regions with GDPR/CAN-SPAM requirements. | Use defaults within legal bounds; always give an obvious opt-out. |

---

## Ethical Boundaries

Psychological influence becomes manipulation when:
- The urgency or scarcity is fabricated (false countdown timers that reset)
- The social proof is manufactured (fake reviews, paid testimonials presented as organic)
- Defaults exploit inattention rather than guide genuinely indifferent users
- Loss framing targets vulnerable users (financial stress, health anxiety) to override rational judgment
- Commitment traps make cancellation deliberately harder than signup

Boundary test: Would the customer feel respected or deceived if they saw exactly what you did and why?

---

## Rationalization Table

| When the user asks for this | Confirm before proceeding |
|----------------------------|--------------------------|
| "Add urgency to this page" | Is the deadline or scarcity real? Fabricated urgency will be recommended against. |
| "Make the free trial feel sticky" | Are you targeting genuine value delivery (Endowment Effect) or dark-pattern lock-in (cancellation friction)? |
| "Show social proof" | Is the social proof accurate? Volume claims, testimonials, and logos must be verifiable. |
| "Use loss aversion in this email" | What is the actual risk the user faces? Loss framing only works if the loss is real and relevant. |
| "Simplify this pricing page" | Are you also providing a recommended default, or just reducing options without guiding the decision? |
| "Add a decoy tier" | Is the decoy tier a real offering or a phantom? Phantom pricing tiers create legal exposure. |

---

## Red Flags

- Countdown timer that resets on page refresh
- "X people viewing this now" on a low-traffic page
- Removing the "no thanks" option from a pop-up
- Pre-checked upsell boxes below the fold
- Hiding the free plan or easy downgrade path
- Social proof with no dates (reviews from 2017 presented as current sentiment)
- Loss framing on a product where the "loss" is speculative or exaggerated

---

## NEVER

- Fabricate urgency, scarcity, or social proof signals
- Apply clinical psychology framing to marketing contexts (CBT, trauma, addiction language as sales hooks)
- Recommend dark patterns that would fail the ethical boundary test above
- Stack multiple pressure tactics on the same decision point (scarcity + loss aversion + countdown + social proof simultaneously)

---

## Task-Specific Questions

1. What specific behavior are you trying to influence?
2. What does your customer believe before encountering your marketing?
3. Where in the journey (awareness, consideration, decision) is this?
4. What is currently preventing the desired action?
5. Have you tested this with real customers?

---

## Related Skills

- **page-cro**: Apply psychology to page optimization
- **copywriting**: Write copy using psychological principles
- **popup-cro**: Use triggers and psychology in popups
- **ab-test-setup**: Test psychological hypotheses
