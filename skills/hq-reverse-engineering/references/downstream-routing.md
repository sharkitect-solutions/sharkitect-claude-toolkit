# Downstream Routing — Where Intelligence Goes Next

## Routing Decision Tree

After producing an intelligence report, route the output based on the user's intent:

```
INTELLIGENCE REPORT COMPLETE
  |
  +-- User wants to BUILD something based on findings?
  |     YES --> Route to BLUEPRINTING workflow
  |     |     1. Feed report to hq-tech-strategy (Orion) for MVA assessment
  |     |     2. If approved: route to ai-systems-architect or backend-architect agent
  |     |     3. Agent produces architecture blueprint
  |     |     4. Blueprint goes to n8n-workflow-architect if automation is involved
  |     |
  |     NO  --> Continue
  |
  +-- User wants to COMPETE or POSITION against the subject?
  |     YES --> Route to STRATEGY workflow
  |     |     1. Feed report to competitive-intelligence-analyst agent for market positioning
  |     |     2. Route to marketing-strategist agent for differentiation strategy
  |     |     3. Route to hq-revenue-ops (Felix) for pricing/positioning implications
  |     |
  |     NO  --> Continue
  |
  +-- User wants to LEARN or ADOPT the subject's approach?
  |     YES --> Route to KNOWLEDGE workflow
  |     |     1. Feed HIGH+ confidence findings to hq-knowledge-governance (Sage) for KB storage
  |     |     2. Create knowledge base entry with proper K-classification
  |     |     3. Cross-reference with existing knowledge
  |     |
  |     NO  --> Report stands alone (archive in Supabase as reference)
```

## Common Routing Patterns

| Scenario | Primary Route | Example |
|----------|--------------|---------|
| "Reverse engineer how Liam Otley builds his AIOS" | BLUEPRINTING → hq-tech-strategy → ai-systems-architect | Extract architecture → MVA assess → design our version |
| "What's HighLevel doing differently?" | STRATEGY → competitive-intelligence-analyst → marketing-strategist | Extract features → position against → differentiate |
| "How does Synthflow handle voice AI routing?" | LEARN → hq-knowledge-governance → technical reference | Extract patterns → classify K3 → store for future reference |
| "Can we replicate this n8n workflow from the tutorial?" | BLUEPRINTING → n8n-workflow-architect → n8n-workflow-builder | Extract steps → design workflow → build it |

## Handing Off Between Agents

When routing intelligence to another agent, include:

1. **The full intelligence report** (not a summary — agents need the details)
2. **The specific question** the downstream agent should answer
3. **Confidence caveats** — explicitly flag which findings are LOW/SPECULATIVE
4. **The user's intent** — what are they trying to accomplish with this information?

Example handoff prompt for the Task tool:
```
Analyze this competitive intelligence report and design an MVA architecture
for our version of the subject's system.

KEY CONTEXT:
- Subject: [name]
- Our goal: [what we want to build/improve]
- HIGH confidence findings: [list]
- Items needing validation before building: [list]

Use the MVA principle: smallest defensible system, documented expansion path.
```

## Feedback Loop

After downstream agents produce their outputs, the user may want to:
- Return to the reverse-engineer agent for deeper analysis on specific findings
- Validate SPECULATIVE items through additional research
- Update the intelligence report with new findings

This is expected and healthy. Intelligence gathering is iterative, not one-shot.
