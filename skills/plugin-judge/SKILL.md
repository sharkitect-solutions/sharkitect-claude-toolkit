---
name: plugin-judge
description: >
  Use when evaluating, auditing, scoring, or reviewing Claude Code plugins
  (installed packages containing hooks, skills, agents, MCPs, and scripts) for
  quality. Use when comparing plugins, running plugin quality audits, deciding
  which plugins to keep/remove/absorb, or assessing custom plugin builds. Use
  when a user says "score this plugin", "evaluate this plugin", "audit my plugins",
  "should I keep this plugin", "rate this plugin". Do NOT use for: skill-judge
  (evaluating standalone SKILL.md files), agent-judge (evaluating standalone
  agent .md files), plugin-dev (building/developing plugins), hook-development
  (writing hooks).
---

# Plugin Judge

Evaluate Claude Code plugins against an 8-dimension rubric designed specifically for plugin packages. Plugins are structurally different from skills and agents -- they are installable packages containing hooks, skills, agents, MCPs, and scripts that operate as integrated units. Evaluating a plugin with skill-judge or agent-judge criteria would be comparing limes to apples.

---

## File Index

| File | Load When | Do NOT Load |
|---|---|---|
| `references/plugin-common-failures.md` | First evaluation of session, unfamiliar with the 7 plugin failure patterns, need quick reference | Already evaluated 2+ plugins this session (patterns memorized) |
| `references/plugin-scoring-calibration.md` | Unsure about D1 scoring for a plugin type, need hook quality benchmarks, verifying thresholds | Confident in calibration from recent evaluations |
| `references/plugin-dimension-examples.md` | Need concrete high/low examples for a specific dimension, calibrating for unfamiliar plugin category | Already calibrated from recent similar evaluations |

---

## Scope Boundary

| Request | This Skill | Use Instead |
|---|---|---|
| "Score/evaluate this plugin" | YES | - |
| "Audit all my plugins for quality" | YES | - |
| "Should I keep or remove this plugin?" | YES | - |
| "Compare these two plugins" | YES | - |
| "Which plugins need improvement?" | YES | - |
| "Score this skill (SKILL.md)" | NO | skill-judge |
| "Score this agent (.md)" | NO | agent-judge |
| "Build a new plugin" | NO | plugin-dev, hook-development |
| "Create a new skill" | NO | ultimate-skill-creator |

---

## Core Philosophy

### The Plugin Value Formula

> **Good Plugin = Automation ROI + Structural Integrity + Component Quality**

A plugin's value comes from three sources:
1. **Automation ROI** -- does it save time or enforce standards that manual effort cannot?
2. **Structural integrity** -- correct package layout, portable hooks, reliable execution
3. **Component quality** -- embedded skills/agents/hooks are individually strong

### Plugin vs Skill vs Agent

| Concept | Contains | Triggering | Primary Value |
|---------|----------|------------|---------------|
| **Skill** | SKILL.md + references | Description match on user intent | Expert knowledge injection |
| **Agent** | Single .md file | Description match on every message | Subagent behavior shaping |
| **Plugin** | Hooks + skills + agents + MCPs + scripts | Hooks fire on events automatically; skills/agents by description | Automated operations, enforcement, integration |

Critical distinction: skills and agents activate when Claude CHOOSES to load them. Plugin hooks fire AUTOMATICALLY on events -- they operate whether Claude "decides" to or not. This makes hook quality a safety-critical dimension.

### The Three Plugin Archetypes

| Archetype | Composition | Example | Risk Profile |
|-----------|-------------|---------|--------------|
| **Hooks-dominant** | Primarily hooks (SessionStart, PreToolUse, etc.) | superpowers, security-guidance | HIGH -- bad hooks break sessions |
| **Components-dominant** | Primarily skills/agents, minimal or no hooks | python-development, retellai-pack | LOW -- just knowledge packages |
| **Integrated** | Hooks + skills + agents working together | hookify, conductor | MEDIUM -- hooks amplify components |

Evaluate each archetype against the rubric, but weight D2/D3/D4 more heavily for hooks-dominant plugins (where hook quality is the entire value proposition) and D5 more heavily for components-dominant plugins (where embedded content quality is the value).

---

## Evaluation Dimensions (120 points total)

### D1: Package Structure (15 points)

Does the plugin have correct directory layout and valid manifests?

| Score | Criteria |
|-------|----------|
| 0-3 | Missing install path, no manifest, no detectable components |
| 4-7 | Path exists but missing plugin.json or package.json, incomplete layout |
| 8-11 | Valid manifest, correct layout, minor issues (missing CHANGELOG, no .gitignore) |
| 12-15 | Perfect: plugin.json with name+version+description, hooks/ with hooks.json, skills/ organized, agents/ present, README + CHANGELOG |

**Required structure for full marks**:
```
plugin-name/
  .claude-plugin/plugin.json    # OR package.json at root
  hooks/hooks.json              # If plugin has hooks
  skills/skill-name/SKILL.md    # If plugin has skills
  agents/agent-name.md          # If plugin has agents
  README.md
  CHANGELOG.md
```

**Scoring adjustments**:
- No manifest at all: cap at 4
- hooks.json with invalid JSON: cap at 3
- Empty plugin (0 components): auto 0

---

### D2: Hook Quality (15 points)

Are hooks well-crafted with appropriate matchers, types, and exit behavior?

| Score | Criteria |
|-------|----------|
| 0-3 | No hooks, or hooks with invalid JSON / broken commands |
| 4-7 | Hooks exist but have broad matchers (.*), missing timeouts, unclear purpose |
| 8-11 | Targeted matchers, correct hook types, reasonable timeouts |
| 12-15 | Precise matchers (specific tool names or patterns), correct event-type pairing, timeouts set, graceful error handling |

**Hook quality checklist**:
- Matchers are specific (not `.*` unless the event semantically requires it -- Stop and SessionStart legitimately match all)
- Command hooks target sub-50ms execution
- Prompt hooks are context-aware with clear instructions
- Timeouts specified for hooks that could hang
- Exit codes used correctly: 0 = success, 2 = blocking error

**For plugins with no hooks** (components-only): Score based on archetype. Pure skill/agent packs get 5/15 (hooks aren't their purpose). If the plugin SHOULD have hooks but doesn't, score lower.

---

### D3: Hook Architecture (15 points)

Are the right events chosen for the job? Are command vs prompt hooks used correctly?

| Score | Criteria |
|-------|----------|
| 0-3 | Wrong events chosen, command/prompt misuse, session-breaking potential |
| 4-7 | Events somewhat appropriate but could be better matched |
| 8-11 | Correct events, proper command/prompt selection, good flow |
| 12-15 | Expert architecture: events perfectly matched to purpose, no redundant hooks, clean separation of concerns |

**Architecture rules** (violations = deductions):

| Rule | Violation | Deduction |
|------|-----------|-----------|
| SessionStart/SessionEnd/PreCompact/Notification are command-only | Prompt hook on these events | -5 |
| Command hooks must be deterministic and fast | Non-deterministic command hook | -3 |
| Hooks fire in PARALLEL (non-deterministic order) | Logic assumes sequential execution | -4 |
| Hooks load at session start ONLY | Plugin expects mid-session hook changes | -3 |

**For plugins with no hooks**: Same archetype-based scoring as D2. Components-only packs get 5/15.

---

### D4: Security & Portability (15 points)

Is the plugin safe to install and portable across machines?

| Score | Criteria |
|-------|----------|
| 0-3 | Hardcoded user paths, credential exposure, shell injection risk |
| 4-7 | Some portability issues (partial hardcoding, broad permissions) |
| 8-11 | Uses `${CLAUDE_PLUGIN_ROOT}`, no exposed credentials, reasonable scope |
| 12-15 | Perfect: all paths use `${CLAUDE_PLUGIN_ROOT}`, no credential exposure, no shell injection vectors, matchers are least-privilege |

**Security checklist**:

| Check | What to Look For | Red Flag |
|-------|-----------------|----------|
| Path portability | All file refs use `${CLAUDE_PLUGIN_ROOT}` | `/Users/john/`, `C:\Users\john\` |
| Credential safety | No API keys, tokens, passwords in any file | Hardcoded keys in scripts or configs |
| Shell injection | Commands don't pass unsanitized input to shell | `eval`, unquoted `$vars`, template strings in shell |
| Matcher scope | Matchers target specific tools, not everything | `.*` on PreToolUse/PostToolUse for non-universal hooks |
| File system access | Scripts don't read/write outside plugin or project scope | Reading `~/.ssh/`, writing to system directories |

**For plugins with no hooks or scripts**: Score on passive safety. Skill/agent content that could leak credentials or contain injection-vulnerable examples gets deducted.

---

### D5: Component Quality (15 points)

Are the embedded skills, agents, and scripts individually strong?

| Score | Criteria |
|-------|----------|
| 0-3 | Components are stubs, empty, or contain only generic/redundant content |
| 4-7 | Components exist with some content but lack expert knowledge or structure |
| 8-11 | Components have solid content, follow structural standards |
| 12-15 | Components would individually pass their respective quality gates (skill-judge B for skills, agent-judge B for agents) |

**Evaluation by component type**:

| Component | Evaluate Against | Key Check |
|-----------|-----------------|-----------|
| Embedded skills (SKILL.md) | Skill-judge dimensions (knowledge delta, companions, description) | Would it pass skill-judge B gate? |
| Embedded agents (.md) | Agent-judge dimensions (delta, description, tools, examples) | Would it pass agent-judge B gate? |
| Scripts (.py, .sh) | Code quality: error handling, documentation, edge cases | Is it production-ready? |
| MCP configs (.mcp.json) | Connection validity, security of connection params | Does it connect correctly? |

**Quick scoring**: For plugins with many components (e.g., 24-skill packs), spot-check 3-4 representative samples rather than evaluating all. Note the sampling in your evaluation.

**For hook-only plugins with no components**: Score 7/15 (hooks ARE the component -- their quality is assessed in D2/D3).

---

### D6: Business Value (15 points)

Does the plugin solve a real problem with measurable automation ROI?

| Score | Criteria |
|-------|----------|
| 0-3 | No clear use case, duplicate of existing capability, or empty plugin |
| 4-7 | Addresses a real need but only marginally better than manual approach |
| 8-11 | Clear value: saves time, enforces standards, or enables new workflows |
| 12-15 | High-impact: automates a painful manual process, prevents costly errors, or enables capability that didn't exist before |

**Value assessment framework**:

| Question | Score Impact |
|----------|-------------|
| "What happens if I remove this plugin?" | If answer is "nothing changes" = low value |
| "Does this automate something I'd do manually?" | Yes = higher value |
| "Does this prevent errors I'd otherwise make?" | Yes = higher value |
| "Is this the ONLY way to get this capability?" | Yes = highest value |
| "Does this overlap with my existing skills/agents?" | High overlap = lower incremental value |

**Context matters**: A plugin that provides 24 Retell AI skills has high value for someone building voice AI, low value for someone building data pipelines. Evaluate in context of the user's toolkit and business.

---

### D7: Documentation (15 points)

Does the plugin explain itself clearly enough to install, configure, and use?

| Score | Criteria |
|-------|----------|
| 0-3 | No README, no description anywhere |
| 4-7 | README exists but minimal (just name, no install/usage/configuration) |
| 8-11 | README with purpose + install + basic usage |
| 12-15 | Complete: purpose, install instructions, hook event descriptions, configuration options, usage examples, CHANGELOG with version history |

**Documentation checklist**:

| Element | Required for 12+ | Why |
|---------|-------------------|-----|
| Purpose statement | YES | "What does this plugin do and why should I install it?" |
| Installation instructions | YES | How to install from marketplace or local path |
| Hook event descriptions | YES (if hooks) | Which events fire, what matchers target, what happens |
| Configuration options | If applicable | Environment variables, settings files, customization |
| Usage examples | YES | Concrete scenarios showing the plugin in action |
| CHANGELOG | YES for 14+ | Version history, breaking changes, upgrade notes |
| Troubleshooting | Nice-to-have | Common issues and solutions |

---

### D8: Reliability & Testing (15 points)

Does the plugin handle errors gracefully and work consistently?

| Score | Criteria |
|-------|----------|
| 0-3 | No error handling, hooks crash on edge cases, untested |
| 4-7 | Some error handling but gaps (missing file checks, uncaught exceptions) |
| 8-11 | Solid error handling, hooks degrade gracefully on failure |
| 12-15 | Comprehensive: error handling in all hooks/scripts, graceful fallback on failure, timeout protection, tested edge cases documented |

**Reliability checklist for hooks**:

| Check | What It Means | Red Flag |
|-------|---------------|----------|
| Graceful degradation | Hook failure doesn't break the session | `exit 2` without good reason blocks the user |
| File existence checks | Scripts verify files exist before reading | `cat nonexistent.json` crashes |
| Timeout protection | Long-running commands have timeouts | Infinite loops in command hooks freeze session |
| Idempotency | Running the hook twice doesn't corrupt state | Hook appends to file without checking existing content |
| Edge case handling | Unusual inputs don't crash | Empty stdin, missing environment variables, special characters |

**For components-only plugins**: Score on component reliability -- do skills handle edge cases? Do agents have fallback procedures? Rate 7/15 baseline if no hooks to evaluate.

---

## Grade Scale

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 108-120 | Excellent -- production-ready, high-value plugin |
| A- | 104-107 | Very strong with minor polish needed |
| B+ | 100-103 | Strong, passes quality gate comfortably |
| B | 96-99 | Good, passes quality gate |
| C+ | 90-95 | Near quality gate, targeted fixes can reach B |
| C | 80-89 | Adequate, clear improvement path |
| C- | 70-79 | Below average, significant gaps |
| D+ | 60-69 | Poor, needs fundamental changes |
| F | <60 | Not viable -- remove or rebuild from scratch |

---

## NEVER Do When Evaluating

- **NEVER** evaluate a plugin using skill-judge or agent-judge criteria -- plugins are packages, not individual skills or agents
- **NEVER** give high D2/D3 scores to plugins that have no hooks -- hooks are what those dimensions measure
- **NEVER** ignore security issues because the plugin "works fine" -- hardcoded paths and shell injection are critical failures
- **NEVER** rate D5 high without actually reading embedded skills/agents -- large skill counts don't equal quality
- **NEVER** skip D6 (business value) because the plugin is technically sound -- a well-built plugin nobody needs is still low value
- **NEVER** assume hook-only plugins are better or worse than component-only plugins -- evaluate each archetype fairly
- **NEVER** inflate scores for first-party (official) plugins -- quality standards apply equally regardless of source
- **NEVER** skip arithmetic verification -- confirm D1+D2+D3+D4+D5+D6+D7+D8 = Total

---

## Evaluation Protocol

### Step 1: Identify Archetype
Read the plugin's pre-analysis data from `plugin-pre-analysis.json` or scan the install path directly. Classify as hooks-dominant, components-dominant, or integrated.

### Step 2: Examine All Components
- Read hooks.json (check format, matchers, types, events)
- Spot-check 2-4 embedded skills (SKILL.md) for content quality
- Spot-check embedded agents for description + body quality
- Read hook scripts for security and reliability
- Read README for documentation completeness

### Step 3: Score Each Dimension
For each of 8 dimensions: find specific evidence (quote relevant files or sections), assign score with one-line justification. Apply archetype adjustments where noted.

### Step 4: Calculate Total & Verify Arithmetic

```
Total = D1 + D2 + D3 + D4 + D5 + D6 + D7 + D8 (Max = 120)
```

**MANDATORY verification**: Add in pairs -- (D1+D2) + (D3+D4) + (D5+D6) + (D7+D8) = Total.

### Step 5: Generate Report
Include: Total/120 with grade, dimension table with individual scores and notes, archetype classification, recommendation (keep/review/remove), specific improvement guidance or absorption targets.

---

## The Meta-Question

> **"Does this plugin make my Claude Code environment meaningfully better than not having it installed?"**

If yes -- it earns its place. If no -- it's consuming disk space and (if it has hooks) processing time on every event, for nothing.
