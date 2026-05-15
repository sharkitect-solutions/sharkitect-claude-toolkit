---
status: active
last_rebuilt: 2026-05-14
reason: Initial creation for Alt 5 Phase 1 SoT-Reference build (Task 5).
---

# Pointer-Only Validator (Companion)

**Authority pointer:** `~/.claude/scripts/skill_judge_pointer_validator.py` is the implementation. This file documents the heuristic, thresholds, and escalation criteria.

## H4 hybrid heuristic

| Layer | Check | Threshold |
|---|---|---|
| **H1** | prose-line ratio among non-header lines | `< 0.40` (else FAIL) |
| **H2** | citation density (>=1 K1 path per non-header lines) | `>=1 per 30` (else FAIL) |
| **H3** | AI-judge pass with K1 SoT loaded | invoked only when H1 != H2 (BORDERLINE) |

## Classification outcomes

- **POINTER**: H1 PASS + H2 PASS. Companion is structurally compliant.
- **BORDERLINE**: H1 != H2. Escalate to H3 (skill-judge AI pass loads K1 SoT side-by-side).
- **PROSE**: H1 FAIL + H2 FAIL. Companion encodes canonical content. Skill-judge REFUSES certification.

## What counts as a citation

A `knowledge-base/...md` path pattern (with optional backticks). See `CITATION_RE` in the validator module.

## Tuning notes

Thresholds were initialized from the rebuilt `hq-revenue-ops/references/{client-tiers,pricing-psychology}.md` files (concrete Alt 5 exemplars). Re-tune if false-positive rate exceeds 10% on real companion audits.
