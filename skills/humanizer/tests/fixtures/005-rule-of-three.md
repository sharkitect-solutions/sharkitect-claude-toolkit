---
id: 005-rule-of-three
ai_tells_present:
  - rule-of-three
  - elegant-variation
  - negative-parallelisms
category: business-explainer
source_prompt: "Describe what makes a good product manager."
difficulty: easy
notes: |
  LLMs default to lists of three for any "what makes a good X" prompt -- the
  rhythm feels balanced and authoritative without requiring a real argument.
  The "It's not about X, it's about Y" negative parallelism is the close-out
  pattern that often follows. Elegant variation (cycling synonyms for the
  same noun) shows up when the LLM is trying to avoid repetition.
---

## Input (AI-generated, raw)

A great product manager combines vision, execution, and empathy. They must inspire teams, align stakeholders, and deliver outcomes. The best practitioners are not just project managers; they are strategic thinkers, customer advocates, and team leaders. It's not about managing tasks, it's about driving impact. The product manager serves as a strategist, the leader functions as a translator, the role acts as a bridge between business and technology. Ultimately, success in this position requires a delicate balance of analytical rigor, creative thinking, and interpersonal skills.

## Expected (Humanized, canonical)

A good product manager makes the calls that the engineering, design, and business sides cannot make on their own -- which problem to solve next, when to ship, and what to cut. Most of the day-to-day is talking: to customers about what they actually do (not what they say they want), to engineers about what is feasible, and to leadership about what is worth funding. The job changes shape by stage. At an early-stage startup, a PM mostly does customer development and writes specs. At a mature company, a PM mostly defends scope and runs the prioritization meetings.

## Rationale

- "vision, execution, and empathy" rule-of-three #1 -> replaced with one specific decision triple (which problem / when to ship / what to cut) that names actual PM trade-offs.
- "inspire teams, align stakeholders, and deliver outcomes" rule-of-three #2 -> replaced with one specific activity (talking) that names who and about what.
- "strategic thinkers, customer advocates, and team leaders" rule-of-three #3 -> deleted entirely; the elegant-variation chain that follows ("strategist / translator / bridge") is also deleted.
- "It's not about managing tasks, it's about driving impact" negative parallelism -> deleted; the meaningful version of this contrast is implicit in the "makes the calls others cannot" framing.
- "The product manager serves as / The leader functions as / The role acts as" -- elegant variation cycling three different nouns for the same person -> all deleted.
- "delicate balance of analytical rigor, creative thinking, and interpersonal skills" closing rule-of-three -> deleted; replaced with the concrete stage-based contrast (early-stage vs mature) which is more useful and harder to write generically.
