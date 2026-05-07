---
id: 004-vague-attributions
ai_tells_present:
  - vague-attributions
  - knowledge-cutoff-hedging
  - subjectless-fragments
category: news-summary
source_prompt: "Summarize the recent debate about AI regulation in the European Union."
difficulty: medium
notes: |
  When asked about anything recent or contested, LLMs default to "experts
  argue" / "observers note" / "some critics" framing because they cannot
  cite specific sources from after their training cutoff (and often refuse
  to even when they can). The humanized version either cites a specific
  source or replaces the claim with a verifiable structural fact.
---

## Input (AI-generated, raw)

The debate around AI regulation in the European Union has continued to intensify in recent months. Experts argue that comprehensive oversight is essential, while industry observers have noted concerns about innovation being stifled. Several sources have suggested that the EU AI Act represents a landmark approach, though critics maintain that key provisions may need refinement. While specific details on implementation timelines remain limited, the conversation has been characterized by a mix of optimism and apprehension across stakeholder groups. Ongoing dialogue is expected to shape the final regulatory framework.

## Expected (Humanized, canonical)

The EU AI Act was approved by the European Parliament in March 2024 and entered into force on August 1, 2024. Most provisions begin applying on August 2, 2026, though prohibitions on certain "unacceptable risk" uses (such as social scoring by public authorities) took effect in February 2025. The Act categorizes AI systems by risk tier and imposes the heaviest obligations on "high-risk" systems, including conformity assessments and CE marking. Industry groups including DigitalEurope have argued the conformity-assessment requirement is operationally heavy for SME developers; the European Commission has pushed back that the obligations are calibrated to risk tier and necessary for market trust.

## Rationale

- "Experts argue" / "industry observers have noted" / "Several sources have suggested" / "critics maintain" -- four vague attributions in a row -> replaced with one named industry group (DigitalEurope) and one named institution (European Commission) actually involved in the public debate.
- "While specific details on implementation timelines remain limited" knowledge-cutoff hedging -> deleted; the rewrite gives the actual timeline (August 1, 2024 entry into force; August 2, 2026 main application).
- "Ongoing dialogue is expected to shape" subjectless-fragment / passive-voice closer -> deleted; the rewrite ends on a concrete contested issue (conformity assessment for SMEs) rather than a hedge.
- "characterized by a mix of optimism and apprehension across stakeholder groups" -> replaced with the specific structural claim (risk-tier categorization, CE marking).
- "in recent months" / "landmark approach" / "key provisions may need refinement" -- all generic phrasing -> deleted.
