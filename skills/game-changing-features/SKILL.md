---
name: game-changing-features
description: >
  Use when the user wants to identify 10x product opportunities, asks "what should we build next",
  says "game-changing", "10x", "high-leverage features", or wants to discover transformative
  product moves rather than incremental improvements. NEVER for RICE scoring or PRD writing
  (product-manager-toolkit). NEVER for brand positioning or go-to-market strategy
  (product-strategist). NEVER for marketing campaign ideation (marketing-ideas). NEVER for
  executive-level business strategy (ceo-advisor).
version: 2.0
optimized: true
optimized_date: 2026-03-11
---

# Game-Changing Features

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| SKILL.md | Opportunity discovery (5 methods), 10x vs 10% litmus test, innovation theater detection (6), evaluation rigor, prioritization traps (7) | Always (auto-loaded) |
| opportunity-sizing-playbook.md | TAM expansion sizing (5-step), conversion funnel impact, retention impact quantification, build cost estimation (4 components + ROI), confidence-weighted sizing (5 evidence tiers), comparison framework | When quantifying feature impact, building business cases, or comparing multiple opportunities by expected value |
| competitive-moat-analysis.md | Moat types and durability (6), defensibility scoring (4 dimensions), feature moat patterns (5) and anti-moat patterns (3), build vs buy vs partner decision matrix, timing analysis (4 market stages), platform shift timing | When evaluating whether a feature creates lasting competitive advantage or deciding build vs buy vs partner |
| feature-validation-methods.md | Validation method selection (6 methods by constraint), fake door test design, painted door tests, Wizard of Oz, pre-order/waitlist validation, evidence quality tiers (5), validation sequencing (5 phases), kill criteria by phase | When testing a feature hypothesis before investment, designing validation experiments, or assessing evidence quality |

## Scope Boundary

| Need | Use This Skill | Not This One |
|------|---------------|--------------|
| Find 10x product opportunities | game-changing-features | -- |
| RICE scoring, PRD quality, sprint planning | product-manager-toolkit | game-changing-features |
| Market positioning, competitive moats, GTM | product-strategist | game-changing-features |
| Marketing campaign brainstorming | marketing-ideas | game-changing-features |
| Executive business strategy, M&A, org design | ceo-advisor | game-changing-features |

---

## Opportunity Discovery Framework

Do not brainstorm from a blank page. Use these five systematic methods to surface real opportunities backed by evidence.

### 1. Jobs-to-Be-Done Adjacency Mapping
Identify jobs users hire COMPETITORS for that they wish YOUR product handled. Each adjacent job is a potential 10x feature.
- What tools do users open immediately before or after using this product?
- What do users copy-paste OUT of this product into another tool?
- What job did users EXPECT this product to do when they first signed up?

### 2. Workflow Interrupt Analysis
Every time a user LEAVES your product to use another tool, that exit point is an opportunity.
- Map the user's full workflow. Where does your product start and stop?
- Each exit = friction. Each re-entry = context loss. Eliminating either = value.
- Priority: exits that happen EVERY session, not occasional ones.

### 3. Support Ticket Mining
- Top 10 feature requests = things users are willing to ASK for (surface demand).
- Complaints about workarounds = things users NEED but found ugly alternatives (deeper demand).
- "How do I...?" questions about things that SHOULD be obvious = UX failures masquerading as feature gaps.

### 4. Power User Behavior Audit
What do the top 5% of users do that the other 95% don't?
- These behaviors reveal unproductized value -- the product CAN do it, but most users don't discover it.
- Productizing power-user behavior (making it default, surfacing it, automating it) is consistently high-leverage.
- Warning: some power-user behavior is niche. Validate that the behavior WOULD help the 95% if they knew about it.

### 5. Churn Interview Patterns
- What did churned users switch TO? That product's core differentiator is your gap.
- WHY did they switch? "Missing feature X" is surface. "Couldn't accomplish Y" is the real signal.
- Users who churned in the first 14 days had onboarding failures. Users who churned after 90 days had value-ceiling failures. Different problems, different features.

---

## 10x vs 10% Litmus Test

Before investing in any idea, run it through these five gates. A genuine 10x opportunity passes at least 3 of 5.

| Gate | 10x Signal | 10% Signal |
|------|-----------|------------|
| **Capability** | Creates something users COULDN'T do before | Makes existing capability faster/easier |
| **Audience** | Opens product to a new user segment | Improves experience for existing users |
| **Compounding** | Gets more valuable over time (data/network/habit effects) | Value is static after launch |
| **Defensibility** | Would take a competitor 6+ months to replicate | Competitor could copy in 1 sprint |
| **Pricing power** | Changes the pricing conversation (new tier, new metric) | Doesn't affect willingness to pay |

---

## Innovation Theater Detection

These patterns FEEL innovative but deliver incremental value disguised as transformation.

1. **"AI-powered everything"** -- Adding AI as a feature checkbox vs. solving a real problem that happens to use AI. Test: remove the AI label. Is it still compelling?
2. **Dashboard proliferation** -- More charts != more insight. If users can't name the ONE metric they check daily, more dashboards won't help.
3. **Integration checklist** -- 50 integrations nobody configures vs. 3 deep integrations that work out of the box. Breadth impresses buyers; depth retains users.
4. **Feature parity** -- Copying competitors guarantees you're always one release behind. You can't out-feature the incumbent; you must out-frame the problem.
5. **Complexity masking as power** -- More settings, more options, more toggles. Power users tolerate complexity; everyone else bounces.
6. **Rebrand-as-feature** -- Renaming existing functionality, reshuffling navigation, adding a "new" label. Users notice. Trust erodes.

---

## Evaluation Rigor

Replace gut-feel scoring with structured assessment for each candidate feature.

### Impact Sizing (pick ONE, quantify it)
- **TAM expansion**: How many NEW users does this unlock? (e.g., "opens mobile segment = +40% addressable market")
- **Conversion lift**: What % improvement in signup-to-active? (e.g., "reduces time-to-value from 20min to 2min")
- **Retention improvement**: What % reduction in monthly churn? (e.g., "eliminates #1 churn reason = -15% churn")

### Decision Dimensions

| Dimension | Question | Why It Matters |
|-----------|----------|----------------|
| Reversibility | Can you ship it, learn, and roll back? | One-way doors need 10x more evidence |
| Dependencies | Does this UNLOCK other features downstream? | Unlocking features > terminal features |
| Evidence quality | User request (weak) / Behavioral data (medium) / Validated prototype (strong) | Weak evidence + high cost = dangerous |
| Cannibalization | Does this compete with an existing feature? | Internal competition confuses users |

---

## Prioritization Traps

These biases specifically corrupt FEATURE ideation (distinct from RICE/backlog traps in product-manager-toolkit).

1. **The founder's pet** -- Ideas championed by the CEO/founder get immunity from scrutiny. Test: would this survive if proposed by a junior PM?
2. **The complexity discount** -- Hard-to-build features get ASSUMED to be high-value. Difficulty of implementation has zero correlation with user value.
3. **Demo-driven development** -- Features that look spectacular in a sales demo but solve no real workflow problem. If the feature only impresses in a 5-minute presentation, it's a demo feature.
4. **The loud minority** -- 5 vocal users requesting something != market demand. Check: what % of your user base would ACTUALLY use this weekly?
5. **The sunk cost feature** -- "We already built half of it" as justification to finish. Half-built features with weak evidence should be killed, not completed.
6. **The strategic hand-wave** -- "It's strategic" used to bypass evidence requirements. Anything labeled "strategic" that can't name the specific user behavior it changes is theater.
7. **Recency bias** -- The last customer call, the latest competitor launch, the most recent churn interview disproportionately influence the roadmap. One data point is an anecdote, not a signal.

---

## Rationalization Table

| If You Catch Yourself Thinking... | The Real Issue |
|----------------------------------|----------------|
| "Users will figure it out" | You're shipping complexity you don't want to simplify |
| "We just need one big feature" | You're avoiding the harder work of making existing features excellent |
| "The market isn't ready yet" | You lack evidence and are using timing as an excuse |
| "This is strategic, metrics don't apply" | You can't articulate the value, so you're hiding behind abstraction |
| "Every competitor has this" | You're chasing parity instead of differentiation |
| "We'll iterate after launch" | You know it's not ready but want credit for shipping |

## Red Flags

1. Feature idea originated from a single customer conversation with no validation
2. The opportunity requires users to change established workflows with no clear incentive
3. You can't name 10 specific users who would use this feature weekly
4. The feature's value proposition requires a paragraph to explain instead of a sentence
5. Impact is described with qualitative words ("huge", "massive") instead of numbers
6. The idea has been on the roadmap for 3+ quarters with no progress (signal: nobody actually believes in it)
7. Building the feature requires a technology bet on something unproven in your stack
8. The feature solves a problem users have already found acceptable workarounds for

## NEVER

1. NEVER present unvalidated brainstorming as strategic recommendations -- label evidence quality explicitly
2. NEVER score opportunities with emoji or vague tiers -- use the structured evaluation dimensions
3. NEVER list features without connecting each one to a specific discovery method that surfaced it
4. NEVER skip the 10x vs 10% litmus test -- every candidate must be classified before evaluation
5. NEVER conflate "users asked for it" with "users need it" -- requests are surface signals, not ground truth
