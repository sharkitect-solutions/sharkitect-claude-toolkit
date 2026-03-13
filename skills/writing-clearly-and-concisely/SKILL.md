---
name: writing-clearly-and-concisely
description: "Use when writing or editing any prose a human will read: documentation, commit messages, error messages, UI text, reports, README files, comments, explanations, or pull request descriptions. Use when asked to improve, tighten, or clarify existing text. NEVER for code generation, data processing, or structured output with no prose component."
version: "2.0"
optimized: true
optimized_date: "2026-03-10"
---

# Writing Clearly and Concisely

## File Index

| File | Purpose | Load When |
|------|---------|-----------|
| `elements-of-style/02-elementary-rules-of-usage.md` | Grammar, punctuation, comma rules | Editing for correctness; comma or clause questions (~2,500 tokens) |
| `elements-of-style/03-elementary-principles-of-composition.md` | Active voice, concision, paragraph structure | Most writing tasks -- default first load (~4,500 tokens) |
| `elements-of-style/04-a-few-matters-of-form.md` | Headings, quotations, formatting conventions | Formatting questions (~1,000 tokens) |
| `elements-of-style/05-words-and-expressions-commonly-misused.md` | Word choice, common errors | Word choice questions; editing for word-level precision (~4,000 tokens) |
| `signs-of-ai-writing.md` | Wikipedia editors' field guide to AI writing patterns | Deep edit to remove AI voice; full pattern library |

**Default load for most tasks:** `03-elementary-principles-of-composition.md` covers active voice, positive form, concrete language, and omitting needless words -- the four principles that matter most.

## Limited Context Strategy

When context is tight, do not skip the reference files -- delegate:

1. Write your draft using the rules below
2. Dispatch a subagent with your draft and the single most relevant section file
3. Have the subagent copyedit and return the revision

Loading one section (~1,000-4,500 tokens) instead of everything preserves context without sacrificing quality.

## Rationalization Table

Before skimming past this skill, recognize these common excuses:

| Excuse | Why It's Wrong |
|--------|---------------|
| "This is just a quick message -- polish doesn't matter" | Quick messages are read more often than documentation. Sloppy quick messages compound. |
| "The user wants speed, not quality writing" | Speed and clarity are not opposites. Clear writing is faster to produce once the rules are internalized. |
| "I already know how to write well" | LLMs default to statistical prose: hedge words, puffery, passive voice. Knowing the rules and applying them under pressure are different. |
| "These rules are for literary writing, not technical docs" | Strunk wrote for exposition and argument, not poetry. His rules target exactly the kind of writing in error messages and README files. |
| "The content is complex, so the sentences have to be complex" | Complex ideas need simpler sentences, not longer ones. Complexity in thought does not require complexity in syntax. |
| "Active voice sounds too blunt for this context" | Direct is not rude. Passive voice obscures who acts and weakens every sentence it appears in. |
| "Omitting words will lose nuance" | Needless words add noise, not nuance. Cut the filler; the meaning sharpens. |
| "Formatting (bullets, bold) can replace clear prose" | Formatting organizes -- it does not clarify. Bulleted vague sentences are still vague sentences. |

## Red Flags

Stop and revise if you see any of these in your output:

- Sentences beginning with "There is," "There are," or "It is" when a real subject exists
- Any form of passive where the actor is known and relevant ("was configured" instead of "X configures")
- The word "not" used to evade rather than deny ("not very reliable" instead of "unreliable")
- Abstract nouns carrying the action that a verb should carry ("make a decision" instead of "decide")
- Two or more consecutive sentences of the pattern [clause] + conjunction + [clause]
- Hedging qualifiers stacked before a claim ("it might be worth considering whether")
- Promotional or empty adjectives: seamless, robust, powerful, cutting-edge, groundbreaking
- AI vocabulary: delve, leverage, multifaceted, foster, realm, tapestry, testament, pivotal, crucial
- Vague nouns where a specific noun fits ("a period of bad weather" instead of "rain for five days")
- Bullets with no parallel structure (mixing noun phrases and full sentences in the same list)
- Bold applied to more than two phrases per paragraph (formatting overuse masking weak prose)
- Emphatic word buried mid-sentence rather than placed last

## NEVER

- **NEVER use passive voice to dodge responsibility.** "Mistakes were made" is evasion, not writing.
- **NEVER write "the fact that."** It is always replaceable with "because," "since," "that," or a direct noun. No exceptions.
- **NEVER stack abstract nouns to sound authoritative.** "The implementation of the utilization of..." -- cut to the verb.
- **NEVER open a paragraph with a transition that belongs inside it.** "Additionally" and "Furthermore" as paragraph openers signal the paragraph has no topic sentence.
- **NEVER use AI puffery words.** Delve, leverage, tapestry, realm, testament, enduring legacy, pivotal moment -- these signal statistical regression, not thought.
- **NEVER apply empty "-ing" phrases.** "Ensuring reliability," "showcasing capabilities," "highlighting features" -- if the phrase names the goal rather than the action, cut or rewrite.
- **NEVER bold randomly.** Bold signals the most important words in a passage. If everything is bold, nothing is. Reserve it for terms introduced for the first time or genuine warnings.

## Strunk's Rules: The Critical Six

These six rules from Strunk's *Elements of Style* (1918) govern the most common failures. Apply them to every sentence.

### Rule 10: Use the active voice

Active voice is more direct, more vigorous, and shorter than passive.

| Weak (passive) | Strong (active) |
|----------------|-----------------|
| The config file was updated by the installer. | The installer updates the config file. |
| A survey of this region was made in 1900. | This region was surveyed in 1900. |
| There were a great number of dead leaves lying on the ground. | Dead leaves covered the ground. |

**Why it matters:** Passive voice obscures the actor (who does what?), adds length, and produces limp sentences. The habitual use of active voice is the single highest-leverage writing habit.

Exception: use passive when the actor is unknown, irrelevant, or when the object is the paragraph's subject ("The Restoration dramatists are little read today").

### Rule 11: Put statements in positive form

Make definite assertions. "Not" used as evasion produces vague, weak prose. Say what is, not what isn't.

| Weak (negative) | Strong (positive) |
|-----------------|-------------------|
| He was not very often on time. | He usually came late. |
| Not important | Trifling |
| Did not remember | Forgot |
| Did not pay attention to | Ignored |

**Why it matters:** Readers want to be told what is. Negatives force them to construct the positive themselves, adding cognitive load and reducing conviction.

### Rule 12: Use definite, specific, concrete language

Prefer the specific to the general. Prefer the concrete to the abstract.

| Vague | Specific |
|-------|----------|
| A period of unfavorable weather set in. | It rained every day for a week. |
| He showed satisfaction as he took possession of his well-earned reward. | He grinned as he pocketed the coin. |
| The system experienced degraded performance. | Response times increased from 200ms to 4s. |

**Why it matters:** Readers think in particulars, not generals. Abstract words force readers to invent their own image. Specific words put the same image in every reader's mind -- and are always shorter.

### Rule 13: Omit needless words

Every word must earn its place. A sentence needs no unnecessary words for the same reason a machine needs no unnecessary parts.

Common traps:

| Wordy | Concise |
|-------|---------|
| the question as to whether | whether |
| owing to the fact that | because |
| in spite of the fact that | although |
| he is a man who | he |
| in a hasty manner | hastily |
| at this point in time | now |
| has the ability to | can |

**Why it matters:** Needless words dilute meaning and tire readers. Every cut makes the sentence faster and the meaning clearer.

### Rule 16: Keep related words together

The position of words shows their relationship. Modifiers separated from what they modify create ambiguity or absurdity.

| Ambiguous | Clear |
|-----------|-------|
| He only found two mistakes. | He found only two mistakes. |
| He wrote three articles about Spain, which were published in Harper's. | He published in Harper's three articles about his adventures in Spain. |
| All the members were not present. | Not all the members were present. |

**Why it matters:** Misplaced modifiers attach to the wrong word, changing or obscuring meaning. Keep subject and verb close. Put modifiers next to what they modify.

### Rule 18: Place emphatic words at the end

The most prominent position in a sentence is the end. The second most prominent is the beginning. The middle is where words get buried.

| Buried emphasis | End emphasis |
|-----------------|--------------|
| Humanity has hardly advanced in fortitude since that time, though it has advanced in many other ways. | Humanity, since that time, has advanced in many other ways, but it has hardly advanced in fortitude. |
| Because of its hardness, this steel is principally used for making razors. | This steel is principally used for making razors, because of its hardness. |

**Why it matters:** The last word rings in the reader's ear. Ending on a weak word ("however," "as well," "also") wastes the most valuable real estate in the sentence.

## Remaining Strunk Rules (Supporting Six)

Apply these as a secondary pass:

| Rule | Summary |
|------|---------|
| 1 | Form the possessive singular with 's (Charles's, not Charles') |
| 2 | Use a comma after each term in a series except the last |
| 3 | Enclose parenthetic expressions between commas |
| 4 | Place a comma before a conjunction introducing a coordinate clause |
| 5 | Do not join independent clauses with only a comma (comma splice) |
| 6 | Do not break sentences into fragments unless deliberately rhetorical |
| 7 | A participial phrase at the start of a sentence must refer to the grammatical subject |
| 8 | One paragraph per topic |
| 9 | Begin each paragraph with a topic sentence |
| 14 | Avoid a succession of loose "and/but/so" sentences -- vary structure |
| 15 | Express coordinate ideas in parallel grammatical form |
| 17 | In summaries, keep to one tense throughout |

## AI Writing Patterns to Avoid

LLMs regress to statistical means, producing puffed-up, generic prose. These patterns appear because they are common in training data, not because they are good writing.

**Puffery and grandiosity:**
- pivotal, crucial, vital, testament, enduring legacy, rich tapestry
- groundbreaking, seamless, robust, cutting-edge, innovative, transformative

**Empty "-ing" constructions:**
- "ensuring reliability" -- ensuring what? rewrite as a verb
- "showcasing features," "highlighting capabilities," "providing value"
- These name goals, not actions. Cut or replace with a specific verb.

**Overused AI vocabulary (avoid entirely):**
- delve, leverage, multifaceted, foster, realm, tapestry, nuanced, holistic
- comprehensive, streamlined, dynamic, synergistic, empower, unlock potential

**Formatting overuse:**
- Excessive bullets where connected prose would be clearer
- Emoji decorations on headers or list items
- Bold on every third phrase (bold used as emphasis loses meaning when overused)
- Headers for single-paragraph sections

**The fix:** Be specific. Name the actual thing. Use a direct verb. Say what it does, not what it "enables," "showcases," or "leverages."

For the full Wikipedia editors' field guide with documented examples, load `signs-of-ai-writing.md`.

## Workflow

For most writing tasks:

1. **Draft** using the critical six rules as a checklist (active, positive, concrete, concise, related words together, strong endings)
2. **Scan** the red flags list against your output
3. **Load** `03-elementary-principles-of-composition.md` if a sentence or paragraph resists the checklist -- the full rule text with examples resolves most edge cases
4. **Check vocabulary** against the AI patterns list before finalizing
