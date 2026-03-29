# Plugin Scoring Calibration Data

Calibration benchmarks derived from auditing 44 plugins across 5 marketplaces. Use this reference to anchor scores against real examples and avoid drift.

---

## D1: Package Structure — Calibration

### By Archetype

| Archetype | Typical D1 Range | Why |
|-----------|-----------------|-----|
| Hooks-dominant (superpowers, hookify) | 10-14 | Usually have proper structure since hooks require correct layout to function |
| Components-dominant (retellai-pack, skill packs) | 8-12 | Often have plugin.json + README but skip CHANGELOG |
| Integrated (conductor, llm-application-dev) | 10-15 | Best-structured since they need all components working together |
| Empty shells (zapier-zap-builder, pyright-lsp) | 0-3 | Nothing to evaluate structurally |
| MCP-only (github, context7) | 4-8 | Minimal files -- often just .mcp.json and maybe plugin.json |

### Scoring Anchors

| Score | Real Example | What It Looks Like |
|-------|-------------|-------------------|
| 2 | pyright-lsp | 1 file (README), no manifest, no components, 1 KB total |
| 5 | github-mcp | 2 files (.mcp.json + plugin.json), no README, minimal but valid |
| 9 | retellai-pack | plugin.json + README + 30 skills in organized directories, but no CHANGELOG |
| 12 | hookify | plugin.json + hooks.json + skills + agents + README, proper directory structure |
| 14 | superpowers | Full structure: plugin.json, hooks.json, 14 skills, 1 agent, README, RELEASE-NOTES, LICENSE, .gitignore |

---

## D2: Hook Quality — Calibration

### Plugins with Hooks (score on actual hook quality)

| Score | Real Example | What It Looks Like |
|-------|-------------|-------------------|
| 3 | prettier-markdown-hook | Single hook, list format (Format B), no timeout on file operations |
| 8 | security-guidance | 1 hook on PreToolUse with specific matcher `Edit|Write|MultiEdit` -- targeted and purposeful |
| 10 | ralph-loop | Hook has clear purpose, reasonable implementation |
| 12 | hookify | 4 hooks across 4 events (PreToolUse, PostToolUse, Stop, UserPromptSubmit), Python scripts with proper delegation |
| 13 | superpowers | SessionStart hook with proper initialization, well-tested across many users |

### Plugins without Hooks (archetype-based scoring)

| Plugin Type | Default D2 Score | Rationale |
|-------------|-----------------|-----------|
| Pure skill pack (retellai-pack, deepgram-pack) | 5 | Hooks aren't their purpose; don't penalize, don't reward |
| Pure agent pack (pr-review-toolkit) | 5 | Same -- agents don't need hooks |
| MCP-only (github, context7) | 5 | MCP integration has its own value model |
| Empty shell | 0 | Nothing to evaluate |
| Plugin that SHOULD have hooks (based on stated purpose) | 2-3 | Missing expected functionality |

---

## D3: Hook Architecture — Calibration

### Architecture Quality Benchmarks

| Score | What It Looks Like |
|-------|-------------------|
| 3 | Wrong event chosen (PreToolUse when PostToolUse would be correct), or prompt hook on command-only event |
| 7 | Events are reasonable but could be optimized (e.g., checking on every Stop when only certain stops matter) |
| 10 | Events match purpose well, command/prompt types correct, no architectural violations |
| 13 | Expert: each hook event perfectly matched, clean separation between hooks, no redundancy, defensive programming |

### Event Selection Guide (for evaluating if plugin chose correctly)

| Purpose | Correct Event | Common Mistake |
|---------|--------------|----------------|
| Initialize plugin state | SessionStart (command) | Using UserPromptSubmit for init |
| Validate before tool runs | PreToolUse | Using PostToolUse (too late) |
| React to tool output | PostToolUse | Using PreToolUse (output not available) |
| Enforce quality on completion | Stop | Using PostToolUse (may miss final state) |
| Inject context into prompt | UserPromptSubmit (prompt) | Using SessionStart (can't inject prompt) |
| Clean up / save state | SessionEnd (command) | Using Stop (fires multiple times per session) |
| Preserve context | PreCompact (command) | No hook at all (context lost) |

---

## D4: Security & Portability — Calibration

| Score | What It Looks Like |
|-------|-------------------|
| 2 | Hardcoded absolute paths (`/Users/author/...`) in multiple locations |
| 5 | No hardcoded paths but uses `eval` or unquoted variables in shell scripts |
| 8 | Uses `${CLAUDE_PLUGIN_ROOT}` consistently, no obvious injection vectors |
| 12 | All paths portable, no credential exposure, matchers are least-privilege, scripts validate input |
| 14 | Above + explicit error handling for missing files, safe temp file usage, documented security model |

### Common Security Issues Found in Audit

| Issue | Frequency (of 44 plugins) | Severity |
|-------|--------------------------|----------|
| No `${CLAUDE_PLUGIN_ROOT}` usage (but no hardcoded paths either) | ~30 plugins | LOW (components-only plugins don't need it) |
| Hardcoded paths in hook scripts | 0 found in current inventory | CRITICAL when present |
| Overbroad matchers (`.*` on PreToolUse) | ~2 plugins | MEDIUM |
| No credential exposure found | 44/44 | GOOD (baseline met) |

---

## D5: Component Quality — Calibration

### Skill Pack Quality Benchmarks

| Score | What It Looks Like |
|-------|-------------------|
| 3 | Skills are thin stubs -- <50 lines each, generic content Claude already knows, no frontmatter descriptions |
| 6 | Skills have some domain content but lack companion files, weak descriptions, minimal expert knowledge |
| 9 | Skills have decent content, proper frontmatter, some domain expertise, but inconsistent quality across the pack |
| 12 | Skills consistently strong -- would individually score 80+ on skill-judge. Proper descriptions, expert content. |
| 14 | Skills would individually pass skill-judge B gate (96+). Rich companions, excellent descriptions, pure knowledge delta. |

### Sampling Strategy for Large Packs

For plugins with 10+ skills, spot-check this selection:
1. **First skill listed** (often the flagship)
2. **Most complex-sounding skill** (tests depth)
3. **Most generic-sounding skill** (tests for redundancy)
4. **Random mid-pack skill** (tests consistency)

If 3/4 samples score similarly, the sample is representative. If variance is high (one scores 12, another scores 4), note the inconsistency and average.

---

## D6: Business Value — Calibration

### Value Tiers

| Score Range | Value Level | Example |
|-------------|-------------|---------|
| 0-3 | No value | Empty shells, duplicate capabilities |
| 4-7 | Low-moderate | Generic skill packs for domains the user doesn't work in |
| 8-11 | Solid value | Fills a real gap (superpowers automation, security enforcement) |
| 12-15 | High value | Enables capability that didn't exist before, automates painful workflows |

### Context-Dependent Scoring

The SAME plugin can score differently depending on who's evaluating:

| Plugin | For a Voice AI developer | For a Data Engineer |
|--------|------------------------|---------------------|
| retellai-pack | 14 (core toolkit) | 2 (irrelevant domain) |
| data-engineering | 3 (irrelevant domain) | 13 (core toolkit) |
| superpowers | 12 (universal automation) | 12 (universal automation) |
| hookify | 10 (automation platform) | 10 (automation platform) |

**For Sharkitect Digital specifically**: VDR uses Retell AI (retellai-pack: HIGH value). n8n is primary automation (n8n skills: HIGH value). Gamma, Customer.io, Documenso: evaluate against actual service lines.

---

## D7: Documentation — Calibration

| Score | What It Looks Like |
|-------|-------------------|
| 2 | No README at all (13 of 44 plugins = 30% missing rate!) |
| 5 | README with name + 1-sentence description, nothing else |
| 8 | README with purpose + install + basic usage |
| 11 | Above + hook descriptions + configuration options |
| 14 | Complete: purpose, install, hooks, config, examples, CHANGELOG (0 of 44 had CHANGELOG) |

### Documentation Gap in Current Inventory

Current state across 44 plugins:
- README present: 31/44 (70%)
- CHANGELOG present: 0/44 (0%)
- LICENSE present: 20/44 (45%)

This means even "well-documented" plugins in our inventory max out around 11/15 on D7. A plugin with CHANGELOG scores higher than any current plugin on this dimension.

---

## D8: Reliability & Testing — Calibration

| Score | What It Looks Like |
|-------|-------------------|
| 2 | Scripts crash on missing files, no error handling, no timeouts |
| 5 | Basic error handling (try/except) but no graceful degradation |
| 8 | Hooks degrade gracefully (exit 0 on error rather than exit 2), scripts check file existence |
| 11 | Comprehensive: timeouts set, error handling in all scripts, idempotent operations |
| 14 | Above + documented edge cases, tested failure modes, monitoring/logging |

### Hook Reliability Benchmark

| Hook Behavior | Score Impact |
|---------------|-------------|
| Hook crashes and blocks session (exit 2 on trivial error) | D8: 0-3 |
| Hook crashes but non-blocking (exit 1) | D8: 4-6 |
| Hook catches errors and exits cleanly (exit 0) | D8: 7-9 |
| Hook catches errors, logs them, and continues | D8: 10-12 |
| Hook handles all edge cases gracefully with fallback behavior | D8: 13-15 |

---

## Grade Boundary Calibration

Based on 44-plugin audit, expected grade distribution:

| Grade | Expected % of Plugins | Characteristics |
|-------|----------------------|----------------|
| A (108+) | 2-5% | Only the best-maintained plugins with hooks + docs + components |
| A- (104-107) | 5-8% | Strong plugins with minor documentation gaps |
| B+ (100-103) | 8-12% | Solid plugins, well-structured, clear value |
| B (96-99) | 10-15% | Good plugins passing quality gate |
| C+ (90-95) | 10-15% | Near quality gate, fixable gaps |
| C (80-89) | 15-20% | Adequate, missing hooks or documentation |
| C- (70-79) | 10-15% | Below average, significant gaps |
| D+ (60-69) | 5-10% | Poor, needs restructuring |
| F (<60) | 15-25% | Empty shells, broken hooks, no value |

Most third-party plugins will score in the C-to-B range. F scores are almost exclusively empty shells and irrelevant domain packs.
