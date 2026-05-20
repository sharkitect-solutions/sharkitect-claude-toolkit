# Phase 8.3: Build Custom Plugins — Execution Plan

## Context

Phase 8.0 (tooling), 8.1 (audit), and 8.2 (gap analysis) are COMPLETE. Build queue APPROVED by user.

- 44 plugins audited: 16 REMOVE, 11 REVIEW, 17 KEEP
- 7 gap categories identified, 3 custom plugins designed
- 12 absorption targets processed (most are REFERENCE_ONLY or SKIP)
- Key deliverables: `.tmp/gap-analysis/toolkit-gaps.json`, `absorption-queue.json`, `build-queue.json`

**Sharkitect Digital** is an AI Transformation Partner for HVAC & Plumbing SMBs ($1M-$30M, KC metro). 4 service lines (VDR, RLR, SLW, CPS), partnership model ($2,500-$7,000+/mo), solopreneur + 16 AI workforce agents. Tech stack: n8n (primary automation), Twilio, Airtable, HubSpot, Claude Code.

**Completed**: 8.0 (tooling), 8.1 (audit: 44 plugins scored), 8.2 (gap analysis: 3 plugins designed)
**Current**: 8.3 (build 3 custom plugins) — BUILD QUEUE APPROVED

---

## Plugin Architecture (Reference)

Claude Code plugins are packages containing any combination of:
- **Skills** (`skills/SKILL.md` + companions)
- **Agents** (`agents/*.md`)
- **Hooks** (`hooks/hooks.json` + scripts)
- **Scripts** (`src/*.py`)
- **README.md** + **CHANGELOG.md**

Plugin hooks use a specific JSON format (different from settings.json):
```json
{
  "description": "Plugin description",
  "hooks": {
    "EventName": [{ "matcher": "ToolName", "hooks": [{ "type": "prompt|command", ... }] }]
  }
}
```

Marketplace manifest format: `.claude-plugin/marketplace.json` at repo root. Plugins listed with local paths (`./plugins/name`) or external Git URLs. Users register with `/plugin marketplace add org/repo`, install with `/plugin install name@marketplace`.

9 hook events: PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact, Notification.

Key constraints:
- Hooks load at session start ONLY — mid-session edits have no effect
- All matching hooks run in PARALLEL (non-deterministic order)
- Command hooks: sub-50ms, deterministic. Prompt hooks: context-aware, reasoning.
- SessionStart/SessionEnd/PreCompact/Notification: command hooks only
- Must use `${CLAUDE_PLUGIN_ROOT}` for portable paths
- Exit 0 = success, Exit 2 = blocking error (stderr), Other = non-blocking

---

## Phase 8.3 Execution Plan (APPROVED)

### Step 1: PRE-01 — Uninstall 16 REMOVE Plugins (IMMEDIATE)

User must run these 16 `/plugin uninstall` commands. Safety verified: zero hooks, zero dependencies, zero unique functionality.

```
/plugin uninstall pyright-lsp@claude-plugins-official
/plugin uninstall typescript-lsp@claude-plugins-official
/plugin uninstall code-simplifier@claude-plugins-official
/plugin uninstall zapier-zap-builder@claude-code-plugins-plus
/plugin uninstall discovery-questionnaire@claude-code-plugins-plus
/plugin uninstall sow-generator@claude-code-plugins-plus
/plugin uninstall roi-calculator@claude-code-plugins-plus
/plugin uninstall excel-analyst-pro@claude-code-plugins-plus
/plugin uninstall gamma-pack@claude-code-plugins-plus
/plugin uninstall documenso-pack@claude-code-plugins-plus
/plugin uninstall make-scenario-builder@claude-code-plugins-plus
/plugin uninstall customerio-pack@claude-code-plugins-plus
/plugin uninstall customer-sales-automation@claude-code-workflows
/plugin uninstall content-marketing@claude-code-workflows
/plugin uninstall data-validation-suite@claude-code-workflows
/plugin uninstall seo-content-creation@claude-code-workflows
```

### Step 2: PRE-02 — Uninstall 8 REVIEW Plugins (AFTER ABSORPTION)

Remove after confirming absorption is complete or skipped:
- deepgram-pack, brand-strategy-framework, retellai-pack, data-engineering, business-analytics, security-scanning, python-development, prettier-markdown-hook

Keep 3 temporarily for extraction during builds:
- pr-review-toolkit (extract silent-failure-hunter concept for code-reviewer)
- feature-dev (extract 7-phase workflow pattern for executing-plans)
- llm-application-dev (extract 2026 embedding model data for prompt-engineering-guidance)

### Step 3: BUILD-01 — aios-core Plugin (Priority 1, ~2 sessions)

**Purpose**: Session lifecycle management — the AIOS foundation.

**Components**:
| Component | Type | Event | Purpose |
|-----------|------|-------|---------|
| SessionStart hook | prompt | startup\|clear\|compact | Workspace detection via cwd, load workspace-specific context, complement Superpowers |
| SessionEnd hook | command | — | Detect skill/agent file modifications, prompt sync, check uncommitted changes |
| PreCompact hook | command | — | Preserve active todos, decisions, modified paths to `.tmp/compact-context.md` |
| session-end-check.py | script | — | SessionEnd logic |
| pre-compact-preserve.py | script | — | PreCompact logic |

**References**: security-guidance (hook architecture), superpowers (SessionStart pattern), conductor (state persistence)

**Build process**:
1. Read `workflows/plugin-build.md` for SOP
2. Scaffold with `python tools/plugin-scaffold.py`
3. Read security-guidance hooks.json as architecture template
4. Read plugin-dev skill for hooks.json format reference
5. Write hooks.json (plugin format with wrapper key)
6. Write Python scripts (stdlib only, Windows-compatible, sub-50ms for command hooks)
7. Write README.md + CHANGELOG.md
8. Validate with `python tools/audit-plugins.py`
9. Score with plugin-judge — must pass B gate (96+/120)
10. Install and test (requires session restart for hooks to load)

### Step 4: BUILD-02 — quality-gate Plugin (Priority 2, ~2 sessions)

**Purpose**: Automated structural validation of skill/agent files on Write/Edit. A linter, not a reviewer.

**Components**:
| Component | Type | Event | Purpose |
|-----------|------|-------|---------|
| PostToolUse hook | command | Write\|Edit | Validate skill SKILL.md and agent .md files: frontmatter, description triggers, line count, File Index |
| validate-skill.py | script | — | Skill file structural validation |
| validate-agent.py | script | — | Agent file structural validation |

**References**: security-guidance (PreToolUse adapted to PostToolUse), skill-judge (validation criteria), agent-judge (validation criteria)

**Key constraint**: Lightweight checks only (structure, not content quality). Content quality requires full skill-judge/agent-judge which is too heavy for a real-time hook.

### Step 5: BUILD-03 — auto-sync Plugin (Priority 3, ~1 session)

**Purpose**: Automatic detection of skill/agent changes with sync prompting.

**Components**:
| Component | Type | Event | Purpose |
|-----------|------|-------|---------|
| PostToolUse hook | command | Write\|Edit | Track writes to ~/.claude/skills/ and ~/.claude/agents/, maintain .tmp/modified-this-session.json |
| Stop hook | prompt | — | Check modified-this-session.json, inject sync reminder |
| track-changes.py | script | — | File change tracking logic |

**References**: ralph-loop (Stop hook pattern), hookify (PostToolUse tracking)

### Quality Policy

- Every plugin passes plugin-judge B gate (96+/120)
- Every script tested on Windows
- Every hook uses `${CLAUDE_PLUGIN_ROOT}` for portability
- All Python scripts: stdlib only, no external dependencies

---

## Hook Coverage After Phase 8.3

| Event | Before | After |
|-------|--------|-------|
| SessionStart | superpowers only | superpowers + **aios-core** |
| SessionEnd | NONE | **aios-core** |
| PreCompact | NONE | **aios-core** |
| PreToolUse | security-guidance + hookify | security-guidance + hookify (unchanged) |
| PostToolUse | hookify (unconfigured) | **quality-gate** + **auto-sync** + hookify |
| Stop | ralph-loop + hookify | **auto-sync** + ralph-loop + hookify |
| UserPromptSubmit | hookify (unconfigured) | hookify (unchanged, low priority) |
| SubagentStop | NONE | NONE (by design) |
| Notification | NONE | NONE (low priority) |

## Remaining Phase 8 (after 8.3)

| Sub-Phase | Sessions | Scope |
|-----------|----------|-------|
| 8.4 Business Ops Gap Analysis | 2-3 | Map Sharkitect's 4 service lines + 16 workforce agents against toolkit |
| 8.5 Build Business Components | 3-5 | Build whatever 8.4 identifies (plugins/skills/agents/MCPs) |
| 8.6 Package for Distribution | 2-3 | Marketplace-ready toolkit with manifest |
| 8.7 Final Sync | 1 | Push everything to GitHub |

---

## Critical Files for Phase 8.3

| Purpose | Path |
|---------|------|
| Plugin build workflow | `workflows/plugin-build.md` |
| Plugin scaffold tool | `tools/plugin-scaffold.py` |
| Plugin audit tool | `tools/audit-plugins.py` |
| Plugin-judge | `~/.claude/skills/plugin-judge/SKILL.md` |
| Hook development skill | `~/.claude/skills/hook-development/SKILL.md` |
| Plugin-dev reference | `~/.claude/plugins/cache/claude-plugins-official/plugin-dev/` |
| Security-guidance hooks template | `~/.claude/plugins/cache/claude-plugins-official/security-guidance/hooks/` |
| Ralph-loop Stop hook template | `~/.claude/plugins/cache/claude-plugins-official/ralph-loop/hooks/` |
| Superpowers SessionStart template | `~/.claude/plugins/cache/claude-plugins-official/superpowers/hooks/` |
| Build queue | `.tmp/gap-analysis/build-queue.json` |
| Toolkit gaps | `.tmp/gap-analysis/toolkit-gaps.json` |
| Absorption queue | `.tmp/gap-analysis/absorption-queue.json` |

---

## Verification

For each custom plugin build:
1. Structure validated with `python tools/audit-plugins.py`
2. Scored with plugin-judge — must pass B gate (96+/120)
3. All scripts tested on Windows
4. All hooks use `${CLAUDE_PLUGIN_ROOT}` for portability
5. All Python: stdlib only, no external dependencies
6. Install and test in live session (requires restart for hooks to load)
7. README.md + CHANGELOG.md documented
