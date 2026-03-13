# Launch Psychology & Adoption Dynamics

Why people adopt or ignore new products -- behavioral economics research that explains launch outcomes better than marketing intuition.

## The Adoption Decision Is Not Rational

Users don't evaluate products on features. They evaluate on perceived switching cost vs perceived gain. If switching cost exceeds perceived gain by even a small margin, they stay with the status quo -- regardless of how objectively better the new product is.

## Switching Cost Taxonomy

Every product switch involves multiple cost types. Users rarely articulate which cost is blocking them.

| Cost Type | What It Is | Example | Launch Implication |
|---|---|---|---|
| Procedural | Time and effort to learn the new system | Migrating from Notion to a new tool requires rebuilding all templates | Provide migration tools, import wizards, or "bring your data" features BEFORE launch |
| Financial | Direct monetary cost of switching | Annual subscription already paid for current tool; new tool costs extra | Time launches to coincide with competitor renewal periods; offer overlap credits |
| Relational | Loss of accumulated relationships/reputation | Leaving a Slack community where you have history and status | Build community features that import social proof (invite existing network, show mutual connections) |
| Emotional | Attachment to current solution, fear of the unknown | "I've used Excel for 20 years, I know how it works" | Familiarity-first design: make the first interaction feel like the old tool, then reveal new capabilities |
| Data | Risk of losing accumulated data or history | Years of conversation history in current messaging app | Guarantee data portability; show import/export before asking for commitment |

**Quantified threshold** (Gourville 2006, Harvard Business Review): New products must be roughly **9x better** than existing solutions to overcome status quo bias. Innovators overvalue their improvements by ~3x; users overvalue their current solution by ~3x. 3 x 3 = 9x gap.

## Rogers' Diffusion -- Tactical Implications Per Segment

The adoption curve isn't just descriptive -- each segment requires fundamentally different launch tactics.

| Segment | % of Market | What They Value | Launch Tactic | Messaging Frame |
|---|---|---|---|---|
| Innovators | 2.5% | Novelty, being first, technical capability | Private alpha invite with raw/unpolished product; they WANT to find bugs | "You're the first to see this" |
| Early Adopters | 13.5% | Strategic advantage, vision alignment, status | Beta with exclusive access; show the vision, not just features | "This will change how you work" |
| Early Majority | 34% | Proven results, peer validation, low risk | Case studies from early adopters; integrations with tools they already use | "Teams like yours are already using this" |
| Late Majority | 34% | Stability, support, industry standard status | Enterprise features, SLAs, compliance certs, phone support | "The industry standard for..." |
| Laggards | 16% | No choice -- forced by market or regulation | Mandatory migration support, backwards compatibility | "Easy transition from [old tool]" |

**The Chasm** (Geoffrey Moore): The gap between Early Adopters and Early Majority is where most launches die. Early Adopters buy vision. Early Majority buys proof. The same messaging that attracted your beta users will REPEL the mainstream. You must deliberately shift messaging from "revolutionary" to "reliable" at this transition.

**Bowling Alley Strategy**: Don't cross the chasm in one leap. Pick one specific niche within the Early Majority (a "pin"), dominate it completely (references, case studies, integrations specific to that niche), then use that credibility to expand to adjacent niches. Each niche conquered makes the next easier.

## Loss Aversion in Free Trials

**Endowment Effect** (Kahneman, Thaler): People value things they possess more than identical things they don't. After using a product for 7+ days, users psychologically "own" it. Losing access triggers loss aversion (~2x stronger than equivalent gain).

| Trial Design | Psychology | Conversion Impact |
|---|---|---|
| 14-day trial with full features | User builds habits and data; loss aversion kicks in at ~day 7 | Higher conversion but higher support cost during trial |
| 7-day trial with full features | Urgency + endowment effect peak overlap | Best for simple products where value is obvious quickly |
| Freemium (permanent free tier) | No loss aversion trigger; user never feels they'll lose anything | Lower conversion rate but larger top-of-funnel; works for network-effect products |
| Reverse trial (start premium, downgrade to free) | Maximum loss aversion -- user EXPERIENCES premium, then loses it | Highest conversion rate for products with clear premium value (Loom, Grammarly model) |

**The day-8 email**: Send a personalized email on day 8 of a 14-day trial showing what the user has built/created/stored. Frame it as "here's what you'd lose" not "here's what you'd gain by upgrading." Loss-framed messages convert 1.5-2x better than gain-framed messages (Tversky & Kahneman 1981).

## Social Proof Cascade Dynamics

Social proof doesn't scale linearly. It has activation thresholds and tipping points.

| Stage | Social Proof Type | Threshold | Impact |
|---|---|---|---|
| Pre-launch | Founder credibility, advisor names | 1-3 recognizable names | Enough to get press/influencer attention |
| Alpha/Beta | Waitlist count, beta user testimonials | 500+ waitlist or 50+ active beta users | Creates FOMO; validates market interest |
| Early Access | Usage metrics, customer logos | 1,000+ users or 5+ recognizable logos | Shifts perception from "experiment" to "real product" |
| Growth | User-generated content, community size | 10,000+ users or active community | Self-sustaining: new users create proof that attracts more users |

**Cascade trigger**: Social proof becomes self-reinforcing once ~15-20% of a target niche is using the product (Centola 2018). Below that threshold, each user must be individually convinced. Above it, adoption spreads through observation ("everyone in my team uses it").

**Anti-pattern -- Premature social proof**: Showing "Join 47 users" is worse than showing nothing. Small numbers trigger negative social proof ("if only 47 people use this, it must not be good"). Hide user counts until they're impressive for your category. For B2B SaaS, 500+ is the minimum credible number; for consumer, 10,000+.

## Network Effect Activation

Products with network effects have a critical mass threshold below which the product is nearly useless.

| Network Type | Critical Mass Signal | Launch Implication |
|---|---|---|
| Direct (messaging, social) | Users can find 3+ existing connections on the platform | Seed with intact social groups (teams, friend groups), not individuals |
| Indirect (marketplace) | Enough supply that demand-side users find what they need >70% of the time | Subsidize the supply side first; curate to create the illusion of completeness |
| Data (ML, recommendations) | Recommendations feel relevant, not random | Pre-populate with curated data; don't show ML-powered features until you have enough data to make them good |

## Commitment Escalation Ladder

Each step in the adoption journey should ask for slightly more commitment than the last. Jumping steps triggers abandonment.

1. **See** -- social media post, ad, word of mouth (zero commitment)
2. **Click** -- visit landing page (tiny commitment: attention)
3. **Subscribe** -- join waitlist or email list (small commitment: contact info)
4. **Try** -- create account, start trial (medium commitment: time)
5. **Use** -- complete core use case successfully (significant commitment: effort + data)
6. **Pay** -- convert to paid (high commitment: money)
7. **Advocate** -- refer others, write reviews (highest commitment: reputation)

**Failure mode**: Asking for Step 6 (pay) before Step 5 (successful core use case) is the most common launch conversion killer. The user hasn't experienced enough value to justify the financial commitment. Ensure every user completes the core use case before seeing any upgrade prompt.
