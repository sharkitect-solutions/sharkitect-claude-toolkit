# The Ultimate Sharkitect AIOS — Vision & Build Plan (Master)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build, ship, and iterate the Ultimate Sharkitect AIOS — a multi-tenant AI Operating System that codifies the Sharkitect Digital partnership method into a subscription product clients deploy on their own machines.

**Architecture:** Hierarchical plan structure — this master plan locks Phase 0 (Foundation, immediate session) at task-level granularity and indexes Phases 1–10 (each gets its own detailed plan file written when that phase activates). The master spec is the architectural source of truth; per-phase plans are the build instructions.

**Tech Stack:**
- Python (PyInstaller for installer, stdlib-only for tools/scripts)
- Supabase (Postgres + RLS + triggers + functions)
- Anthropic API + Claude Code
- GitHub (toolkit master + AIOS distribution + client-managed backup org)
- Antigravity (default IDE for operators)
- Stripe (subscription enforcement)
- n8n (existing automation; not shipped to operators)

**Master spec:** `3.- Skill Management Hub/docs/superpowers/specs/2026-05-04-ultimate-sharkitect-aios-spec.md`

**Sub-specs:**
- AIOS Local Sandbox Workspace Design — `2026-05-03-aios-local-sandbox-workspace-design.md`
- AIOS Installer Design — `2026-05-03-aios-installer-design.md`
- AIOS Feedback Loop Spec v1.0 — `2026-05-03-aios-feedback-loop-spec-v1.0.md`

(skip brainstorming — brainstorming was invoked Session 21 and Session 22; this plan file is the terminal step per the writing-plans skill flow.)

---

## Phase 0 — Foundation (THIS SESSION — closing out)

**Goal:** Lock architectural foundation + dispatch consolidated packages to HQ + Sentinel + register parent project in Supabase.

### Task 1: Master spec written

- [x] Master spec authored covering 10 foundational principles, 24 architectural Qs (Q1–Q24), 14 parts
- [x] Sub-spec references embedded
- [x] Workspace lane discipline documented per-Q
- [x] Cross-workspace routing plan defined

### Task 2: HQ consolidated package dispatched

- [x] All HQ-owned items consolidated into single `kind: project_package` routed-task
- [x] Each item carries Skill Hub suggestion + reasoning + alternatives + explicit "pending HQ review with Chris" flag
- [x] Routed via Skill Hub OUT pattern

### Task 3: Sentinel consolidated package dispatched

- [x] All Sentinel-owned items consolidated (14 Central Hub tables + 5 audit classes + Project Package coordination triggers + cross-workspace state view)
- [x] Schema starting suggestions documented; Sentinel owns final design
- [x] Routed via Skill Hub OUT pattern

### Task 4: Register parent project + 10 phase tasks in Supabase

**Step 1:** Run `python ~/.claude/scripts/update-project-status.py add-project "Ultimate Sharkitect AIOS Build" --status pending --workspace skill-management-hub --priority high --notes "Master plan: ~/.claude/plans/the-ultimate-sharkitect-aios-vision-and-build-plan.md. Master spec: 3.- Skill Management Hub/docs/superpowers/specs/2026-05-04-ultimate-sharkitect-aios-spec.md. 10-phase implementation arc."` to create the parent project.

**Step 2:** Add Phase 0 sub-tasks (5 tasks, all already complete or in-progress this session) — assigned to skill-management-hub.

**Step 3:** Mark Phase 0 done sub-tasks as completed.

**Step 4:** Add Phase 1-10 placeholder tasks with `assigned_workspace` per master spec Part 12 ownership table:
- Phase 1 (sentinel) — Central Hub schema
- Phase 2 (skill-management-hub) — infrastructure
- Phase 3 (skill-management-hub) — installer Phase 1
- Phase 4 (workforce-hq) — first 4-5 operators
- Phase 5 (skill-management-hub) — .exe build
- Phase 6 (workforce-hq) — next 4-5 operators
- Phase 7 (skill-management-hub) — unattended go-live
- Phase 8 (skill-management-hub) — continuous improvement
- Phase 9 (skill-management-hub) — P2 + P3 extraction
- Phase 10 (cross-workspace) — Sharkitect AIOS HQ migration

**Step 5:** Encode Phase 3 dependency on both Phase 1 + Phase 2 via `add-dependency` calls.

### Task 5: Plans registry update

Add row to `~/.claude/docs/plans-registry.md` Active Plans table for this plan.

### Task 6: MEMORY.md session learnings

Add Session 22 entry to MEMORY.md Resume Instructions and create topic file `memory/session_22_aios_q17-q24_locked.md` with full Session 22 summary.

### Task 7: Final commit + push

Stage all changes, commit with descriptive message covering shipped specs + packages + plan + MEMORY updates, push to origin.

### Task 8: Run formal `/session-checkpoint` (Full mode)

Final session-checkpoint runs the 10-step audit (resource audit / MEMORY / lessons / plan status / pending items / workspace checklist / `.tmp/` audit / git checkpoint / Supabase sync / session brief / pass-fail summary).

---

## Phase 1 — Sentinel Schema (DEFERRED to fresh session)

**Goal:** Provision `sharkitect-aios-central-hub` Supabase project + design + deploy 14 Central Hub tables + 5 audit classes + Project Package coordination triggers.

**Owner:** Sentinel

**Trigger to begin:** After HQ + Sentinel review consolidated packages with Chris and lock major decisions.

**Detailed plan to be written:** `~/.claude/plans/<date>-aios-phase1-sentinel-schema.md` (Sentinel writes when activated)

**High-level scope:**
- Provision new Supabase project `sharkitect-aios-central-hub`
- Schemas for: licenses, installations, client_backups, name_references, execution_log, system_learning, escalation_queue, improvement_proposals, update_log, stack_telemetry, usage_patterns, cross_client_recommendations, plugin_wipe_events, client_artifacts_review
- Audit classes: name_drift, update_telemetry, plugin_wipe_pattern, escalation_dwell_time, stack_pattern_emergence
- Project Package state view + auto-blocker-cleared trigger
- Migration tooling

**Acceptance criteria:** All 14 tables deployed with RLS + indexes; all 5 audit classes integrated; Project Package coordination triggers tested; schema documented for Skill Hub integration.

---

## Phase 2 — Skill Hub Infrastructure (PARALLEL to Phase 1)

**Goal:** Build Sharkitect-side toolkit pieces independent of Sentinel schema dependency.

**Owner:** Skill Hub

**Trigger to begin:** Anytime after Phase 0 (no schema dependency for these pieces).

**Detailed plan to be written:** `~/.claude/plans/<date>-aios-phase2-skill-hub-infra.md`

**High-level scope:**
- `sharkitect-aios-distribution` GitHub repo (curated subset of toolkit master)
- Tier-Auto pull mechanism (session-start hook + scheduled background pull + critical webhook listener)
- Plugin re-deploy mechanism (Q23 Option C) integrated into session-startup-guard
- NRTR `rename.py` tool (Q22)
- Sandbox workspace setup per sub-spec
- 7 foundational feedback-loop skills

**Acceptance criteria:** Distribution repo provisioned; pull mechanism tested via sandbox; plugin re-deploy tested; NRTR dry-run works; sandbox operational; 7 feedback-loop skills shipped + judged at quality gate.

---

## Phase 3 — Bootstrap Installer Phase 1 (DEPENDS ON Phases 1+2)

**Goal:** Concierge install kit + smart bootstrap CLAUDE.md + license validation + fingerprint check ready for first paying operator.

**Owner:** Skill Hub

**Trigger to begin:** After Phase 1 (schema available) AND Phase 2 (distribution + sandbox available).

**Detailed plan to be written:** `~/.claude/plans/<date>-aios-phase3-installer-phase1.md`

**High-level scope per `2026-05-03-aios-installer-design.md`:**
- Concierge install kit + INSTALL-SOP + CLAUDE-md-template + walkthrough card
- Smart bootstrap CLAUDE.md (license-tied dynamic fetch placeholder)
- Central Hub API endpoints: `POST /api/v1/license/validate`, `POST /api/v1/install/check-fingerprint`, `POST /api/v1/backup/provision`
- Per-operator bootstrap rendering engine
- Watermarking infrastructure
- Continuous re-validation at session start
- Fingerprint computation logic
- Reactivation flow UX

**Acceptance criteria:** Concierge install kit complete + dry-run on Chris's test machine; license + fingerprint check tested end-to-end; bootstrap fetch + replace flow validated; watermark detection tooling shipped; Q21 protection model verified (bootstrap content NEVER persisted in cleartext).

---

## Phase 4 — First 4-5 Operators (Concierge Installs)

**Goal:** Validate Phase 1 install flow against real operators in supervised conditions.

**Owner:** Workforce HQ (Chris) + Skill Hub (responsive support)

**Trigger to begin:** After Phase 3 ships + first paying operator signs up.

**High-level scope:**
- Schedule 60-90 min concierge session per operator
- Run install per Phase 1 SOP
- Capture concierge-feedback-form per session
- Surface gaps as Phase 5 .exe refinements

**Acceptance criteria:** 4-5 operators successfully installed + running AIOS; each completed `instantiate` interview; all concierge feedback captured.

---

## Phase 5 — Phase 2a Installer (.exe Build)

**Goal:** Build the standalone .exe installer with code-signing.

**Owner:** Skill Hub

**Trigger to begin:** After Phase 4 surfaces real install bugs + revenue justifies $400-600/yr code-signing certs (~3 paying customers).

**Detailed plan to be written:** `~/.claude/plans/<date>-aios-phase5-exe-installer.md`

**High-level scope:**
- PyInstaller build pipeline + GitHub Actions matrix (Win/Mac/Linux)
- Apple Developer Program + Windows code-signing cert acquisition
- License-key-gated download URL infrastructure
- Auto-update mechanism for the installer itself
- Resumable bootstrap state (`.installer-state.json`)
- Error handling + rollback for every step
- Telemetry to Central Hub

**Acceptance criteria:** 3-platform .exe builds via CI; code-signed (Mac + Windows); tested across all 3 OSes; license-gated download URL working; auto-update tested.

---

## Phase 6 — Next 4-5 Operators (.exe with Concierge)

**Goal:** Validate .exe in real-world conditions with Chris on screen-share watching.

**Owner:** Workforce HQ (Chris) + Skill Hub (responsive support)

**Trigger to begin:** After Phase 5 ships.

**High-level scope:**
- Schedule .exe-with-concierge session per operator
- Operator self-installs while Chris watches (NOT driving)
- Catch .exe edge cases
- Help operator when stuck
- Log every help-needed moment as Phase 7 refinement

**Acceptance criteria:** Last 3 .exe installs completed without Chris intervention; telemetry shows zero post-install errors.

---

## Phase 7 — Phase 2b Unattended (.exe Self-Install Goes Live)

**Goal:** Steady-state operation: operators self-install via .exe with no concierge.

**Owner:** Skill Hub (maintenance only)

**Trigger to begin:** After Phase 6 acceptance criteria met.

**High-level scope:** Phase 6 exit criteria met → flip to public availability; marketing collateral updated; sales process updated.

---

## Phase 8 — Continuous Improvement (Steady-State)

**Goal:** System Learning Loop weekly cycles + cross-client recommendations + beta tester feedback iteration.

**Owner:** Cross-workspace (Skill Hub + Sentinel + HQ)

**Trigger to begin:** After Phase 7 + first 5+ paying operators producing telemetry.

**Detailed plan to be written:** `~/.claude/plans/<date>-aios-phase8-continuous-improvement.md`

**High-level scope:**
- Weekly System Learning Loop scheduled job
- Cross-client recommendation generation
- Beta tester feedback intake + iteration
- Stack tracking pattern emergence
- Audit cadence engine running per audit_cadence column

---

## Phase 9 — P2 + P3 Product Extraction

**Goal:** Extract Standalone Edition (P2) + Workspace Add-On Bootstrap (P3) from P1 architecture.

**Owner:** Skill Hub

**Trigger to begin:** After P1 stable + revenue justifies extraction work.

**High-level scope:**
- P2 Standalone Edition: simpler version of P1 for solo operators / single-machine
- P3 Workspace Add-On Bootstrap: for adding workspaces to existing P1 deployments + Sharkitect-internal use

---

## Phase 10 — Sharkitect AIOS HQ Migration

**Goal:** Migrate Sharkitect's own ops to the AIOS pattern as an internal P1 instance.

**Owner:** Cross-workspace

**Trigger to begin:** After P1 stable + Sentinel migration tooling ready.

**Detailed plan to be written:** `~/.claude/plans/<date>-aios-phase10-sharkitect-hq-migration.md`

**High-level scope:**
- Pre-migration audit of current Sharkitect ops state across all 3 workspaces
- Migration tooling (Sentinel-owned)
- Test on Chris's secondary computer first
- Then migrate primary
- Sharkitect uses its own product as a real client = strongest dogfood

---

## Self-Review

**1. Spec coverage:** Every section of the master spec maps to a phase. Full coverage. ✅

**2. Placeholder scan:** Phases 1-10 are intentionally summarized at high-level with detailed plan files referenced (deferred to phase activation). Phase 0 has bite-sized tasks with concrete commands. No "TBD" in actionable Phase 0 tasks. ✅

**3. Type consistency:** Function names referenced (`add-project`, `add-task`, `add-dependency`, `task ... completed`) match `update-project-status.py` API. Workspace names canonical. ✅

**4. Scope check:** Master coordination plan for a 10-phase project. Phase 0 task-bite-sized; Phases 1-10 summarized with their own plans deferred. Correct decomposition for multi-month, multi-workspace product build. ✅

---

## Execution Handoff

**Plan complete and saved.**

**Phase 0 closeout (current session):** Tasks 4-8 (Supabase project entry, plans registry update, MEMORY.md update, final commit + push, formal `/session-checkpoint`) executing inline now.

**Phase 1+ activation:** Each phase activated in fresh session per its trigger. At activation, the owning workspace writes the detailed phase-specific plan and uses superpowers:executing-plans or superpowers:subagent-driven-development to implement.
