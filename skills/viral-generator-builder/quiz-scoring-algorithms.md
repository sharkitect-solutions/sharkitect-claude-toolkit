# Quiz Scoring Algorithms for Viral Generators

## Algorithm Selection Decision

| Signal | Algorithm | Why | Complexity |
|---|---|---|---|
| 4-8 result types, each equally valid ("What type are you?") | **Weighted scoring** | Each answer adds points to one or more types. Highest score wins. Simple to implement, easy to balance | LOW |
| Results on a spectrum (beginner to expert, introvert to extrovert) | **Dimensional scoring** | Score on 1-3 continuous axes. Result determined by position on spectrum. More nuanced than types | MEDIUM |
| Results based on specific input combinations | **Rule-based matching** | If-then rules map specific answer combinations to results. Precise but rigid | LOW-MEDIUM |
| Same input always = same result (name generators, birthday generators) | **Hash-based deterministic** | Hash input string, use hash to index into result array. Reproducible and verifiable | LOW |
| Creative/unique results per user | **LLM-generated** | API call to generate personalized result text. Unique per user but non-deterministic | MEDIUM-HIGH |

## Weighted Scoring Implementation

The most common quiz algorithm. Each answer adds points to one or more result types.

### Weight Matrix Design

| Question | Answer A | Answer B | Answer C | Answer D |
|---|---|---|---|---|
| Q1: "Pick an activity" | Explorer +3 | Builder +3 | Strategist +3 | Connector +3 |
| Q2: "How do you recharge?" | Explorer +2, Connector +1 | Builder +2, Strategist +1 | Strategist +2, Explorer +1 | Connector +2, Builder +1 |
| Q3: "Pick a superpower" | Explorer +2 | Builder +3 | Strategist +2 | Connector +3 |

**Weight rules**:
- Primary type match: +3 points
- Secondary type match: +1-2 points
- Questions should NOT all map 1:1 to types (too predictable). Mix in cross-type scoring
- First 2-3 questions: high-signal (strongly differentiate types). Last 2-3: fine-tuning (break ties)

### Result Distribution Balancing

After designing your weight matrix, simulate 1000+ random answer combinations and check the distribution.

| Distribution | Assessment | Action |
|---|---|---|
| Each result 20-30% (for 4 types) | HEALTHY | No action needed. Even distribution means all results are achievable |
| One result >40% | SKEWED | Reduce that type's weights by 1 point on 2-3 questions. Or add a question that specifically differentiates that type from others |
| One result <10% | RARE (intentional or broken?) | If intentional: label as "Rare! Only 8% get this" (increases share value). If unintentional: increase weights for that type |
| Two results always tie | TIE PROBLEM | Add a tiebreaker question that only scores for those two types. Or add a tiebreaker rule (first type alphabetically, or secondary score comparison) |

### Tiebreaker Strategies

| Strategy | How It Works | User Experience |
|---|---|---|
| **Secondary score** | If two types tie on primary score, compare secondary score (sum of +1 and +2 bonuses) | Feels "fair" -- the nuance of answers matters |
| **First question priority** | In case of tie, the type with higher score on Q1 wins | Simple to implement. Works because Q1 is usually highest-signal |
| **Hybrid result** | Ties produce a unique "hybrid" result: "Explorer-Builder" | More results = more shareability. But requires designing hybrid result content for every possible pair |
| **Random with seed** | Tie broken by hashing user's name/input | Deterministic (same user always gets same tiebreak) but feels random. Use only if other methods don't work |

## Dimensional Scoring

Results determined by position on one or more axes, not just highest-type score.

### Single-Axis Example (Spectrum)

```
Introvert |----|----|----|----| Extrovert
Score:      0   25   50   75   100

Score 0-20:  "Deep Thinker" (strong introvert)
Score 21-40: "Selective Social" (mild introvert)
Score 41-60: "Balanced" (ambivert)
Score 61-80: "Social Catalyst" (mild extrovert)
Score 81-100: "Energy Radiator" (strong extrovert)
```

**Threshold placement**: Don't place thresholds at even intervals. The INTERESTING results should have narrower ranges (creating rarity). The "balanced" result should be slightly narrower than you'd expect -- nobody shares "you're average."

### Two-Axis Example (Quadrant)

```
                Analytical
                    |
     Strategist     |     Scientist
                    |
  Practical --------|-------- Creative
                    |
     Executor       |     Visionary
                    |
                Intuitive
```

Each question scores on BOTH axes. Result = quadrant + position within quadrant. 4 quadrant types + 4 edge types (between quadrants) = 8 possible results.

**Two-axis gotcha**: Center clustering. If most questions score small amounts on both axes, most users land near the center (the "Balanced" zone). Solution: include 2-3 "polarizing" questions that score heavily on one axis only.

## Hash-Based Deterministic Algorithms

For generators where the same input must always produce the same output.

### Simple Hash Function

| Input Processing | Method | Determinism | Distribution |
|---|---|---|---|
| Lowercase + trim | `input.toLowerCase().trim()` | "John" and "john" give same result. Expected behavior | N/A -- preprocessing step |
| Character sum | Sum of character codes: `input.split('').reduce((s,c) => s + c.charCodeAt(0), 0)` | Fully deterministic | POOR -- anagrams give same result ("cat" = "act"). Short inputs cluster |
| DJB2 hash | `hash = ((hash << 5) + hash) + charCode` with seed 5381 | Fully deterministic | GOOD -- well-distributed, fast, handles most input lengths |
| SHA-256 (first 8 chars as hex -> int) | Use Web Crypto API, take first 8 hex chars, parse as integer | Fully deterministic, cryptographic quality | EXCELLENT -- near-perfect distribution. Overkill for fun generators but useful if fairness matters |

**Hash distribution test**: Run your hash function on 1000 common names. Check that results are distributed within 5% of expected uniform distribution. If "Explorer" appears 35% of the time with common English names, your hash function has a bias for that result.

## Result Quality Assurance

| Test | What to Check | Failure Mode |
|---|---|---|
| **All-same-answer test** | Answer all A's, all B's, all C's, all D's. Each should give a DIFFERENT result | If all-A and all-B give the same result, your scoring has a dominant type |
| **Opposite-answer test** | The most opposite answer patterns should give the most opposite results | If "all adventurous answers" and "all cautious answers" give the same result, your axes aren't working |
| **Random simulation (n=1000)** | Generate 1000 random answer sets, check result distribution | Any result >40% or <5% signals scoring imbalance |
| **Edge case inputs** (for hash-based) | Empty string, single character, very long string, emoji, unicode | Hash functions can return NaN, overflow, or cluster for extreme inputs |
| **Duplicate detection** | Two different meaningful inputs should rarely give the same result | If "John" and "Jane" always get the same result, your hash isn't granular enough for your result set |

## Personality Type Frameworks for Quiz Design

Existing personality frameworks provide proven archetypes that feel "real" to users.

| Framework | Types | Best For | Licensing/IP |
|---|---|---|---|
| **Four elements** (Earth/Water/Fire/Air) | 4 | Casual quizzes, broad audience. Universal recognition | Public domain. Free to use |
| **Color personalities** (Red/Blue/Green/Yellow) | 4 | Professional/business quizzes. Similar to DISC but no licensing | Generic colors are not copyrightable. But avoid using trademarked names (True Colors, Insights Discovery) |
| **RPG classes** (Warrior/Mage/Rogue/Healer) | 4-8 | Gaming audiences, tech communities | Generic archetypes are public domain. Avoid D&D-specific class names |
| **Custom archetypes** | Any | When you want unique, shareable names | Create your own. Best for viral sharing because results are novel. "Midnight Architect" > "Type A personality" |

**Custom archetype design rules**:
1. Each name should be 2 words: [Adjective/Modifier] + [Noun/Role]. "Midnight Architect," "Solar Navigator," "Quiet Catalyst"
2. Each archetype should feel aspirational -- something you'd want to be
3. Names must be distinct enough that hearing two is clearly different
4. Avoid negative connotations -- "Chaotic Procrastinator" won't get shared
5. Test names with 5 people: can they guess what type of person each name describes?
