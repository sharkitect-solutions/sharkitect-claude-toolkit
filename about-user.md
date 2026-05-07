<!-- skip checkpoint: meta-doc rewrite to align with HQ wr-hq-2026-05-07-003 reconciliation -->

# About-User META Document (system-level)

> **This is the META layer.** It tells the AI WHERE to find Chris's persona profile + HOW to use it + HOW capture works. The actual profile content lives in HQ's K1 SoT (see Authoritative Source below).

> **Source of truth for the profile content:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/knowledge-base/governance/about-chris.md` (K1, HQ-owned). Per Supabase Ownership Protocol: read globally, write locally. Skill Hub + Sentinel READ it; only HQ writes it.

> **Coordination history:** HQ filed `wr-hq-2026-05-07-003` (FYI) on 2026-05-07 announcing v0.1 SEED of about-chris.md. This meta-doc absorbs HQ's 12-section structure + 8 signal categories + 4-tier cadence as canonical, replacing Skill Hub's earlier 11-dimension proposal. Reconciled in `wr-skillhub-2026-05-07-001` status_history.

---

## 1. Authoritative Source — what to load at session start

Every workspace's startup-guard MUST load this file at session start. The file is HQ-owned K1 SoT. Read-only for non-HQ workspaces.

**Path:** `1.- SHARKITECT DIGITAL WORKFORCE HQ/knowledge-base/governance/about-chris.md`
**Owner:** HQ (workforce-hq)
**Sections (canonical, 12 — defined by HQ):**
1. Who Chris is
2. How he thinks
3. Values
4. Communication
5. Operational preferences
6. Vision
7. Anti-patterns
8. How to make decisions on his behalf
9. Capture protocol
10. Application
11. Open questions (sequential Q&A in progress)
12. Capture log

**Confidence levels (per HQ quality bar):**
- Direct quote > paraphrase
- Confirmed pattern (≥2 instances) > single instance
- Source citation required
- Confidence marking per assertion (SEED → LOW → MEDIUM → HIGH)

**Versioning:** v0.1 SEED as of 2026-05-07. v1.0 target after Chris answers HQ's 8 open questions.

---

## 2. Capture mechanism — how signals flow

| Tier | Trigger | Owner | Output |
|---|---|---|---|
| **Real-time** | UserPromptSubmit hook fires on every user message | `~/.claude/hooks/voice-capture-hook.py` (Skill Hub-owned, global) | Raw sample → `voice-samples-raw.jsonl`; pattern-matched feedback → `voice-capture-log.jsonl` + `activity_stream` |
| **Session-end** | Session-checkpoint skill | Each workspace | Session-end synthesis appended to memory; significant signals routed to HQ via routed-task |
| **Weekly synthesis** | Sentinel dream consolidation, weekly cadence | Sentinel (`tools/dream-consolidation`) | Distilled signals written to `about_chris_synthesis` Supabase table tagged by HQ 12-section taxonomy. HQ pulls from this table weekly into `about-chris.md` |
| **Monthly drift detection** | Sentinel monthly audit | Sentinel | Drift report (sections aging without updates, contradictions between captured signals and current K1 state) routed to HQ for review |

The 8 signal categories HQ defined map onto the 12 sections (signal categories are inputs; sections are outputs). Mapping maintained in HQ's about-chris.md Capture protocol section.

---

## 3. Application — how AI uses the profile

| Decision class | When to consult | How |
|---|---|---|
| **Tier 1 — Routine work matching established patterns** | Always | Load profile at session start as context priors; act per established preferences without re-querying |
| **Tier 2 — High-stakes or novel decisions** | When the decision could materially affect revenue, brand, client relationship, or system architecture | Re-read relevant section of `about-chris.md` on-demand; cite source in your response if making a judgment call |
| **Tier 3 — Decisions outside captured signal** | When the profile doesn't cover the decision | Default to Pushback Protocol — articulate the gap to Chris, propose path, do not act unilaterally |

**Alignment with existing Proactive Autonomy Protocol (universal-protocols.md):** the Tier 1/2/3 framework above EXTENDS the existing 3-tier Proactive Autonomy Protocol with profile-grounded decision routing. The existing protocol defines confidence levels for proactive action; this layer adds the question "what does the profile say about this kind of decision?"

---

## 4. What the AI MUST do

1. **Load HQ's about-chris.md at session start.** Every workspace startup-guard reads it. Treat it as priors for the session's voice/decision behavior.
2. **Trust the runtime for capture.** voice-capture-hook handles real-time signal capture. Do NOT manually capture every interaction.
3. **Honor the silences.** What's NOT in about-chris.md matters. If you'd write something the profile doesn't endorse, default to Chris's known register (direct, decisive, non-yes-agent), not generic AI defaults.
4. **Flag profile gaps to Chris when they block a decision.** If Tier 3 fires, surface the gap explicitly so the next capture cycle fills it.
5. **Do not write to HQ's about-chris.md from outside HQ.** Cross-workspace edits violate Supabase Ownership Protocol. Route findings to HQ via routed-task instead.

## 5. What the AI must NEVER do

- **Never duplicate the profile.** Only HQ's about-chris.md is canonical. Workspace-local copies drift.
- **Never claim "I've added this to memory"** as acknowledgment of a correction. Capture is automatic; the runtime handles it.
- **Never refuse capture for a "non-feedback" message.** Continuous raw-sample capture handles this.
- **Never override profile-grounded decisions silently.** If you deviate from what the profile would predict, say so explicitly and cite reason.

---

## 6. Cross-references

- **Capture protocol (rule):** `~/.claude/rules/universal-protocols.md` § Continuous Voice & Preference Learning Protocol
- **Capture hook (runtime):** `~/.claude/hooks/voice-capture-hook.py`
- **Capture CLI (paired samples):** `~/.claude/scripts/voice-write.py`
- **HQ K1 SoT (profile content):** `1.- SHARKITECT DIGITAL WORKFORCE HQ/knowledge-base/governance/about-chris.md`
- **Sentinel synthesis pipeline (build pending):** `wr-skillhub-2026-05-07-001` (extended scope reconciled with HQ)
- **HQ FYI signal:** `wr-hq-2026-05-07-003`
- **Supplementary brand voice:** `~/.claude/skills/hq-brand-review/` + `~/.claude/skills/hq-content-enforcer/` (brand voice is a separate artifact from Chris persona profile per HQ direction)

---

## 7. Maintenance

- **This file (meta-doc):** Skill Hub-owned. Update when capture mechanism, application layer, or cross-references change.
- **HQ's about-chris.md (content):** HQ-owned. Updated by HQ on weekly synthesis cadence (after Sentinel writes to about_chris_synthesis Supabase table). HQ also updates ad-hoc when answering open questions or processing direct user direction.
- **Maintenance log table:** lives in HQ's about-chris.md § 12 Capture log. This meta-doc does not duplicate it.
