---
name: viral-generator-builder
description: "Build shareable generator tools (quizzes, calculators, name generators, avatar creators) optimized for viral sharing. Use when: (1) user wants to build a tool that generates personalized results, (2) user asks about viral mechanics for interactive content, (3) user needs share card or OG image design for generated results, (4) user wants quiz scoring or result distribution logic. Do NOT use for: general frontend development without viral/sharing focus (use frontend-design), marketing psychology theory without implementation (use marketing-psychology), free tool strategy without generator mechanics (use free-tool-strategy), content creation without interactive generation (use content-creator)."
---

# Viral Generator Builder

## File Index

| File | What It Contains | Load When |
|---|---|---|
| `SKILL.md` | Generator type selection, viral loop architecture, result design, input optimization, anti-patterns | Always loaded |
| `share-card-engineering.md` | OG image generation, platform-specific share specs, screenshot optimization, social preview cards | User asks about share cards, OG images, social sharing display, or screenshot design |
| `quiz-scoring-algorithms.md` | Weighted scoring, result distribution balancing, personality type mapping, fairness testing, algorithm selection | User asks about quiz logic, scoring fairness, result distribution, or personality test design |
| `viral-loop-analytics.md` | K-factor measurement for generators, cohort analysis, share-to-visit conversion, retention mechanics, A/B testing viral features | User asks about measuring virality, optimizing share rates, or analytics for generators |

Do NOT load companion files for "build me a name generator" requests -- SKILL.md covers the architecture decisions. Load companions when the user needs depth in share card design, scoring algorithms, or analytics.

## Scope Boundary

| Topic | In Scope | Out of Scope |
|---|---|---|
| Generator tool architecture | YES | General web app architecture |
| Quiz/personality test design | YES | Academic psychometric assessment |
| Name/text generator mechanics | YES | NLP/AI model training |
| Share card and OG image design | YES | General graphic design |
| Viral loop optimization | YES | General growth hacking |
| Result page design | YES | Landing page design |
| Input form optimization for generators | YES | General form UX (use form-cro) |
| Calculator tools with shareable output | YES | General calculator apps |
| Avatar/image generators | YES | Image generation AI (Midjourney, DALL-E) |
| Social sharing mechanics | YES | Social media strategy |
| Deterministic vs random result logic | YES | Cryptographic hash functions |
| Generator monetization (ads, leads) | YES | General ad tech |

## Generator Type Decision

First match based on business goal.

| Goal | Generator Type | Why This Type | Input Required | Viral Potential |
|---|---|---|---|---|
| Maximum shares, brand awareness | **Identity quiz** ("What [X] are you?") | Identity results trigger "that's SO me" sharing instinct. Berger (2013): social currency is the #1 sharing driver | 5-10 multiple choice questions | HIGHEST -- people share identity-confirming results. BuzzFeed's "What City Should You Live In?" got 20M+ shares |
| Lead generation (email capture) | **Score calculator** ("Your [X] score is...") | Scores create curiosity gaps. Gate detailed breakdown behind email. Calculators feel "useful" not "marketing" | 3-7 numeric/selection inputs | HIGH -- scores are inherently comparable. "I got 847, what did you get?" |
| SEO traffic + backlinks | **Name generator** ("Your [X] name is...") | Evergreen, simple, high replay value. Hundreds of long-tail keywords. Low maintenance once built | Name or 1-2 inputs | MEDIUM-HIGH -- fun to share but lower emotional investment than quiz results |
| Product demonstration | **Result previewer** ("See what your [X] looks like") | Shows product value through personalized preview. Conversion tool disguised as generator | Product-relevant inputs | MEDIUM -- shares only if result is visually impressive |
| Community building | **Comparison tool** ("How do you compare to...") | Creates in-group dynamics. Leaderboards drive repeat visits. Works for niche communities | Quiz or data inputs | HIGH in niche -- lower total volume but deeper engagement |

## The Viral Loop Architecture

Every generator follows the same 5-stage loop. Optimize each stage independently.

```
Stage 1: LAND (visitor arrives)
  |
Stage 2: INPUT (visitor provides minimal data)
  |
Stage 3: PROCESS (the "magic" -- your algorithm)
  |
Stage 4: RESULT (personalized, shareable output)
  |
Stage 5: SHARE (result posted to social/messaging)
  |
  +---> New visitor lands (Stage 1) -- loop repeats
```

| Stage | Key Metric | Benchmark | Optimization Lever |
|---|---|---|---|
| Land -> Input | Start rate | 60-80% (should be near-automatic) | Reduce visible input fields. Show example result immediately. "Enter your name to find out" > "Take our 20-question quiz" |
| Input -> Result | Completion rate | 70-90% for <5 inputs. 40-60% for 5-10 inputs | Progress indicator. Never show all questions at once. Each question should feel like progress, not work |
| Result -> Share | Share rate | 5-15% organic (no prompt). 15-30% with good share UX | Result must pass the "screenshot test." Share buttons at eye level. Pre-written share text with result |
| Share -> New Land | Click-through rate | 2-8% of people who see the share | OG image must show enough to create curiosity but NOT the full result. "I got Midnight Architect -- what are you?" |
| Overall K-factor | K = shares_per_user x new_users_per_share | K > 0.3 = good. K > 0.7 = strong viral. K > 1.0 = exponential (very rare for generators) | Focus on the weakest stage. A 2x improvement on the worst stage beats 10% improvement on all stages |

## Result Design Principles

The result page IS the product. Everything else is scaffolding to reach it.

| Principle | Implementation | Why It Works |
|---|---|---|
| **Identity, not information** | "You're a Midnight Architect" not "You prefer working at night and like structure" | Identity labels become social currency. People share labels, not descriptions. Bartle player types (1996) proved this for games -- same psychology applies |
| **Flattering but specific** | Every result should make the user feel good about something specific to THEM | People share content that makes them look good (Berger 2013, Principle 1: Social Currency). Nobody shares "You're average" |
| **Visually distinct per result** | Each result type gets its own color scheme, icon, or illustration | Visual distinction makes results feel "real" and unique. Also makes screenshot shares more eye-catching in feeds |
| **Comparison bait** | Include "Only 12% of people get this result" or compatibility info | Comparison drives conversation: "Wait, you got the same as me?" Rarity creates bragging rights |
| **Deterministic when possible** | Same inputs = same result = shareable AND verifiable | Friends can verify by entering the same inputs. Randomness kills the "try it yourself" share motivation |

## Input Optimization

Every input field is a dropout point. The conversion cost of each additional field is ~10-15% of remaining users.

| Input Count | Expected Completion | Best For | UX Pattern |
|---|---|---|---|
| 1 (name only) | 85-95% | Name generators, simple calculators | Single field + big "Generate" button. No scroll, no pages |
| 2-3 inputs | 75-85% | Score calculators, compatibility tools | All fields visible on one screen. No pagination needed |
| 5-7 questions | 55-70% | Personality quizzes, type sorters | One question per screen + progress bar. Tinder-swipe UX for mobile |
| 8-10 questions | 40-55% | Detailed assessments, comprehensive quizzes | Progress bar mandatory. Show "You're 60% done!" not "Question 6 of 10" (Nunes & Dreze endowed progress) |
| 10+ questions | <40% | Almost never worth it | If you need 10+ questions, your algorithm isn't smart enough. Simplify |

**The first-question rule**: The first input/question must be answerable in <3 seconds and feel relevant to the promised result. "What's your name?" or "Pick the image that speaks to you" -- not "Describe your work habits in detail."

## Algorithm Selection

| Algorithm Type | Best For | Tradeoff | Implementation Complexity |
|---|---|---|---|
| **Hash-based deterministic** | Name generators, "your X based on birthday" | Same input always = same output. Shareable and verifiable. But results feel "random" -- no perceived intelligence | LOW -- hash input, modulo into result array |
| **Weighted scoring** | Personality quizzes, "what type are you" | Results feel earned through answers. But distribution can be uneven (40% get Type A, 5% get Type D) | MEDIUM -- weight matrix per question, sum scores, highest wins |
| **Multi-axis mapping** | Complex personality types, compatibility tools | Rich results with multiple dimensions. But harder to explain and share concisely | HIGH -- multiple score axes, 2D/3D result space, nearest-archetype matching |
| **Threshold-based** | Calculators, score assessments | Clear "you passed/failed" or tier assignment. Easy to understand. But binary/tiered results limit variety | LOW -- sum inputs, compare to thresholds |
| **LLM-generated** | Creative generators (story, brand name, description) | Unique per user, feels "AI-powered." But expensive per generation, non-deterministic, latency | MEDIUM-HIGH -- API call, prompt engineering, result caching |

**Algorithm gotcha**: Weighted scoring quizzes need result distribution testing. If 60% of test-takers get the same result, the quiz feels broken. Test with 100+ random answer combinations. Adjust weights until no result exceeds 35% frequency and no result is below 8%.

## Monetization Decision

| Goal | Monetization Method | Implementation | Revenue Potential |
|---|---|---|---|
| Email list building | Gate detailed results behind email | Show headline result free, full breakdown after email capture. "You're a Midnight Architect -- enter your email for your full profile" | $0 direct, $2-10 per lead value depending on niche |
| Ad revenue | Display ads on result page | Result page gets the most time-on-page. Place ad between result and share buttons. Never before result (kills completion) | $5-15 RPM. At 100K monthly results: $500-1500/month |
| Product upsell | Result includes product recommendation | "As a Midnight Architect, you'd love [product]." Must feel natural, not forced | Varies. Affiliate: $1-50 per conversion. Own product: unlimited |
| Sponsored generators | Brand pays for custom quiz/generator | "[Brand] presents: What kind of [X] are you?" Branded results, branded share cards | $2K-50K per sponsored generator depending on audience size |

## Anti-Patterns

### 1. The Generic Result
Results that could apply to anyone. "You're creative and sometimes prefer being alone." Zero identity signal, zero share motivation. **Symptom**: share rate below 3%. **Fix**: Each result should make 70% of non-recipients say "that doesn't describe me at all."

### 2. The Friction Wall
Too many inputs before any payoff. 15-question quiz with no preview of what the result looks like. Users have no reason to invest time without knowing the reward. **Symptom**: >50% drop-off before completion. **Fix**: Show an example result on the landing page. "See what type you are in 5 questions."

### 3. The Invisible Share
Share buttons buried below the fold, no pre-written share text, no OG image configured. The result page works great -- but nobody shares because sharing is hard. **Symptom**: high completion rate but share rate <2%. **Fix**: Share button at eye level on result page. Pre-fill share text. Generate unique OG image per result.

### 4. The Ugly Card
OG image is auto-generated with no design thought. Default gray box with tiny text. In a social feed, it looks like spam. Nobody clicks. **Symptom**: share-to-click ratio below 1%. **Fix**: Design OG images at 1200x630px. Bold text, strong colors, readable at thumbnail size. Result visible without clicking.

### 5. The One-and-Done
No reason to return or re-engage. User takes quiz once, shares, never comes back. All viral value captured in one cycle. **Symptom**: 0% return visitor rate. **Fix**: Daily/weekly changing generators, "compare with friends" feature, new quiz variants, result collections.

### 6. The Random Disappointment
Non-deterministic results that change on reload. User shares "I got Midnight Architect," friend tries with same inputs, gets different result. Trust destroyed. **Symptom**: comments saying "I got something different when I tried again." **Fix**: Hash-based determinism for input-dependent generators. Seed randomness with user input.

## Rationalizations

- "More questions means more accurate results" (The Friction Wall -- accuracy doesn't matter if nobody completes it)
- "People will find the share button" (The Invisible Share -- they won't, they'll screenshot and crop your branding out)
- "The result content matters more than how it looks" (The Ugly Card -- on social feeds, visual presentation IS the content)
- "We can add sharing features later" (sharing is architecture, not a feature -- retrofitting viral loops is 5x harder)
- "AI-generated results are always better than templated ones" (The Random Disappointment -- LLM results are non-deterministic, which breaks the verification loop)

## Red Flags

- No OG image configured for result pages
- Share rate measured but share-to-click rate not tracked
- Quiz has more than 10 questions without proven completion rate data
- Results page loads in >2 seconds (every second of latency = 7% fewer shares)
- No mobile-specific share UX (>60% of generator traffic is mobile)
- Same share text for every result type
- Generator works only in English but targets global audience

## NEVER

- NEVER show the full result in the OG image/share card -- show enough to create curiosity, not enough to satisfy it
- NEVER randomize results without seeding from user input -- non-deterministic results kill the viral verification loop
- NEVER gate the PRIMARY result behind email/payment -- gate the DETAILED breakdown, not the headline result
- NEVER launch a generator without testing result distribution with 100+ simulated inputs
- NEVER skip mobile optimization -- generators are impulse content consumed on phones during social media browsing
