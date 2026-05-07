<!-- skip checkpoint: mid-session save, persona seed document creation -->

# About the User -- Persona Profile (auto-maintained)

> **Source of truth for who the user is.** Loaded at session start by every workspace. Maintained continuously by Sentinel's dream consolidation pipeline (per wr-skillhub-2026-05-07-001). Manual edits are allowed but will be reconciled against captured signals on next nightly run -- if a manual edit contradicts captured evidence, the dream consolidation flags it for review rather than silently overwriting.

> **Goal:** sufficient depth that AI can make autonomous decisions in the user's voice and preferences without asking. "Could almost clone me" is the benchmark.

> **Source protocol:** Continuous Voice & Preference Learning Protocol in `~/.claude/rules/universal-protocols.md`.

**Last full synthesis:** _(populated by dream consolidation; currently SEEDED ONLY)_
**Confidence level:** SEED -- minimal capture data so far; populated rapidly over next 2-3 weeks of continuous capture.

---

## 1. Identity -- who they are

**Name:** Chris Sharkey
**Company:** Sharkitect Digital (sharkitectdigital.com)
**Email:** solutions@sharkitectdigital.com
**Role:** Founder / CEO / operator. Builds an AI workforce ("AIOS") to support SMB clients while staying lean as a solo operator with family responsibilities.

**Recurring concerns (from captured work):**
- Operational autonomy -- the system should run without him so he can focus on revenue + family
- Quality + accuracy over speed (zero-tolerance for sloppy work, accuracy is non-negotiable)
- Brand integrity (Sharkitect voice is deliberate; generic AI voice erodes it)
- Cost discipline (unit economics, sustainable bootstrapping)

_(Populated further by dream consolidation as more sessions land.)_

## 2. Likes -- what they engage with

_(Empty -- to be populated from voice-samples-raw.jsonl topic-engagement clustering. Initial signals: dispatcher consolidation work, brain-dump capture pattern, AIOS architecture decisions, autonomous self-healing systems, naming conventions.)_

## 3. Dislikes -- what they reject

_(Empty -- to be populated from corrections + push-backs. Initial signals from MEMORY.md feedback files: yes-agent behavior, generic AI voice patterns, hook proliferation friction, engineery names that fail the 5-second test.)_

## 4. Voice -- what they sound like

_(Empty -- to be populated from raw-sample sentence-rhythm + word-frequency distillation. Manual seed signals from captured voice samples: uses "nonsense" colloquially ("small nonsense"), uses "almost clone me", uses "guys" plural-second-person to address the system. Direct register, decisive openers.)_

## 5. Speech style -- how they like to talk

_(Empty -- to be populated. Manual seed: long flowing requests followed by direct asks; uses bullet lists in their own messages when enumerating; will dictate verbatim when intent matters; pushes back when AI proposes complexity.)_

## 6. Preferences -- choices they make consistently

_(Empty -- to be populated from decision-pattern observation. Manual seed signals from MEMORY.md feedback files:_
- _Optimize-to-max, not stop-at-gate (B 96+ for skills/agents, push to A)_
- _Verify before filing -- 2-minute check on every WR premise_
- _Resolution before move -- never move WR to processed without resolution object_
- _Inbox-driven coordination -- never copy-paste between workspaces_
- _Pushback is mandatory -- never yes-agent_
- _Annealing loop is mandatory -- build-judge-optimize-deploy_
- _Proactive autonomy -- 100% confidence = just build it; high = pitch with reasoning; lower = flag and explore)_

## 7. Vision -- what they're building toward

_(Empty -- to be populated from long-term-direction language clustering. Manual seed signals:_
- _AIOS as universal AI operating system for SMBs_
- _Sharkitect AIOS Central Hub as cross-client learning + delivery infrastructure_
- _Three-product strategy P1/P2/P3 (locked S21-S22)_
- _Self-healing tiered system that improves without operator intervention_
- _Voice/persona profile sufficient for the system to make autonomous decisions in the user's voice_
- _"World-class," "elite," "non-negotiable" appear repeatedly as quality bar)_

## 8. Brand -- their public-facing voice

**Brand:** Sharkitect Digital
_(Brand voice details captured under `~/.claude/skills/hq-brand-review/` + `hq-content-enforcer`. The dream consolidation should pull brand voice attributes from those skill files plus voice-samples-raw analysis on outbound client communications.)_

## 9. Way of thinking -- mental models

_(Empty -- to be populated from framework-usage and metaphor-recurrence clustering. Manual seed signals:_
- _WAT framework (Workflows, Agents, Tools)_
- _Probabilistic AI handles reasoning; deterministic code handles execution_
- _Capture is input, synthesis is output -- this very document's pattern_
- _One-in-one-out budget exchanges (hooks, complexity)_
- _Documentation without runtime detection is insufficient -- pair rules with hooks_
- _Deferred not equal to processed -- discipline against silent drift)_

## 10. What they say (explicit) -- positive direction

_(Empty -- populated from explicit requests + named goals + articulated standards captured across sessions. Manual seed: see the universal-protocols.md `## Continuous Voice & Preference Learning Protocol` section for the most recent verbatim direction.)_

## 11. What they don't say but mean (implicit)

_(Empty -- inferred from gaps, silences, and topic pivots. Highest-difficulty dimension to populate; requires longitudinal data. Will be populated only after 2-3 weeks of continuous capture provides the baseline against which silences and pivots become readable.)_

---

## How to use this document (for the AI)

1. **Load at session start.** Every workspace's startup-guard should pull this doc into context.
2. **Reference before voice-bearing output.** Before writing emails, proposals, social posts, or any content that will represent the user, check this doc for the relevant voice/brand/preference signals.
3. **Honor the silences.** What's NOT in this doc matters. If you'd write something the doc doesn't endorse, default to the user's known register (direct, decisive, non-yes-agent), not generic AI defaults.
4. **Update is automatic.** Do NOT manually edit this document during normal work. It updates nightly. Manual edits are reserved for explicit user direction or correction of distillation errors flagged by Sentinel.
5. **Confidence-gating.** When the document is at SEED confidence, treat its content as priors only. As confidence rises (per dream consolidation's confidence score), use it more authoritatively for autonomous decisions.

---

## Maintenance log

| Date | Event | Source |
|---|---|---|
| 2026-05-06 | SEED -- initial structure created with manual seed signals from MEMORY.md + captured voice samples | S29 ship of Continuous Voice & Preference Learning Protocol |

_(Dream consolidation will append entries here on each nightly run.)_
