---
id: 001-significance-inflation
ai_tells_present:
  - significance-inflation
  - rule-of-three
  - vague-attributions
category: encyclopedic
source_prompt: "Write a short paragraph introducing the historical significance of the printing press."
difficulty: easy
notes: |
  Demonstrates the canonical LLM failure mode for any "history of X" prompt:
  puffing importance via abstract significance claims, forcing a rule-of-three
  list, and citing unnamed "scholars" or "historians" in place of actual
  sources. Humanized version replaces all three with concrete dates and
  attributable facts.
---

## Input (AI-generated, raw)

The invention of the printing press by Johannes Gutenberg around 1440 stands as a testament to the transformative power of technology, marking a pivotal moment in the evolution of human communication. This groundbreaking innovation profoundly reshaped European society by democratizing knowledge, accelerating literacy, and laying the foundation for the modern world. Scholars and historians have long underscored its enduring significance, noting that it set the stage for the Renaissance, the Reformation, and the Scientific Revolution -- three movements that together shaped Western thought.

## Expected (Humanized, canonical)

Johannes Gutenberg printed the first European book using movable type around 1455, the Gutenberg Bible. Within fifty years, presses operated in more than 250 European cities and produced an estimated 20 million books. The technology cut the cost of book production roughly tenfold compared to hand-copied manuscripts, which is the main reason historians link it to the spread of vernacular Bibles during the Reformation and the wider circulation of scientific texts in the following century.

## Rationale

- "stands as a testament to" / "marking a pivotal moment in the evolution of" -> deleted; replaced with the concrete date (1455 Gutenberg Bible).
- "groundbreaking innovation" / "profoundly reshaped" -> deleted; replaced with the measurable economic claim (tenfold cost reduction) that actually explains why it mattered.
- "democratizing knowledge, accelerating literacy, laying the foundation" rule-of-three -> deleted; replaced with one specific outcome (vernacular Bibles in the Reformation).
- "Scholars and historians have long underscored" vague attribution -> deleted; replaced with a directional claim ("historians link it to") that the reader could verify.
- The "three movements that together shaped Western thought" rule-of-three is replaced with a single, narrower causal link the reader can check.
