---
id: 002-promotional-language
ai_tells_present:
  - promotional-language
  - copula-avoidance
  - em-dash-overuse
category: travel-tourism
source_prompt: "Describe the small town of Ronda, Spain for a travel website."
difficulty: easy
notes: |
  LLMs default to brochure voice for any travel/tourism/cultural-heritage
  prompt. The "nestled in the heart of" / "boasts" / "vibrant rich" cluster
  is one of the most recognizable AI tells. Em dashes pile on because
  brochure writing also overuses them.
---

## Input (AI-generated, raw)

Nestled in the heart of Andalusia's breathtaking countryside, the picturesque town of Ronda boasts a rich tapestry of history and culture -- a vibrant destination that stands as a testament to Spain's enduring beauty. The town features stunning natural landscapes, captivating Moorish architecture, and offers visitors a truly unforgettable experience. With its iconic Puente Nuevo bridge soaring above the dramatic El Tajo gorge, Ronda serves as a must-visit gem for travelers seeking authentic Spanish charm.

## Expected (Humanized, canonical)

Ronda is a town in Andalusia, southern Spain, with a population of around 33,000. It sits on a plateau split by the El Tajo gorge, which drops about 100 meters straight down. The Puente Nuevo bridge across the gorge was completed in 1793 and is the most photographed landmark in the area. The old town on the south side preserves Moorish-period architecture, including the 13th-century Arab Baths and the Mondragon Palace.

## Rationale

- "Nestled in the heart of" + "breathtaking countryside" + "picturesque" + "vibrant" + "rich tapestry" -> all deleted. Brochure voice replaced with measurable facts (population ~33,000, gorge depth ~100 meters, bridge year 1793).
- "boasts a rich tapestry of" / "stands as a testament to" / "serves as a must-visit gem for" -- all copula-avoidance constructions -> rewritten with plain "is" / "sits on" / "preserves".
- The em dash in "endurance beauty -- a vibrant destination" is removed; replaced with a comma in the rewrite (no em dashes at all in the humanized version).
- "stunning natural landscapes, captivating Moorish architecture, and offers visitors a truly unforgettable experience" rule-of-three with "truly" intensifier -> replaced with two specific architectural references (Arab Baths, Mondragon Palace) that the reader can verify.
- Removed all promotional adjectives: stunning, captivating, breathtaking, picturesque, vibrant, must-visit, iconic, unforgettable, dramatic, authentic, charm.
