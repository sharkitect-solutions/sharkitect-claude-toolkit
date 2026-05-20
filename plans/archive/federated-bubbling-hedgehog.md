# Universal Protocol Registry — Implementation Plan

## Context

**Problem:** Each workspace (HQ, Skill Hub, Sentinel) has its own CLAUDE.md with duplicated protocol definitions — pre-task checklists, post-task checklists, memory protocols, session-end steps. When a protocol is improved in one workspace, others don't know. This causes inconsistent behavior (e.g., Sentinel skipping full end-of-session) and stale references.

**Root cause:** No single source of truth for universal protocols. Each CLAUDE.md defines its own copy. No propagation mechanism exists.

**Solution:** Create `~/.claude/rules/universal-protocols.md` — a global rule file auto-loaded into every session. Update the `BOOTSTRAP.md` template in the toolkit repo to reference the universal rule instead of duplicating protocols. Leave existing workspace CLAUDE.md files as-is (the rule is authoritative; duplication is harmless). Update supporting infrastructure (session-start.py, bootstrap.py, sync tool, INSTALL-GUIDE).

---

## Design Decisions

1. **Leave existing CLAUDE.md files as-is.** The universal rule auto-loads and is authoritative. Existing duplication is harmless. Cleanup happens organically when each workspace is next modified.

2. **Bootstrap template is `BOOTSTRAP.md` in toolkit repo root.** Already placed there by user. During instantiation, agent copies it to new workspace and renames to `CLAUDE.md`. Update it to reference universal rule instead of duplicating protocols.

3. **AIOS Builder excluded.** Client-facing product template with its own protocol structure. Universal rule's scope gate skips it.

---

## Phase 1: Create `~/.claude/rules/universal-protocols.md`

**File:** `C:\Users\Sharkitect Digital\.claude\rules\universal-protocols.md`

Single source of truth, auto-loaded into every session in every workspace.

### Content Structure

```markdown
# Universal Protocols — Sharkitect Digital

> **Scope:** All Sharkitect Digital internal workspaces.
> **Skip when:** CLAUDE.md PROJECT_PURPOSE contains "Universal AI Operating System"
> or workspace type is "client-project".

## Pre-Task Checklist (before ANY work)

- [ ] Read the request carefully. Confirm understanding before acting.
- [ ] Check your toolkit — review all available skills, agents, tools, plugins, and MCPs. Use what's relevant.
- [ ] Check MEMORY.md — review prior learnings, patterns, and preferences.
- [ ] Check workflows/ — is there an existing SOP? Follow it.
- [ ] Plan before executing — identify what needs to be done, in what order.
- [ ] If ambiguous, ask ONE clarifying question before proceeding.

> Workspace CLAUDE.md may add workspace-specific items. Run those too.

## Post-Task Checklist (after ANY work)

- [ ] Verify all outputs are saved, correct, and complete.
- [ ] Check cross-references — if Document A changed, update Document B.
- [ ] Update MEMORY.md with session learnings (decisions, patterns, preferences).
- [ ] If new patterns or processes were discovered, record them.
- [ ] Confirm nothing is left in an inconsistent or half-finished state.
- [ ] Run `/session-checkpoint` before closing the session.

> Workspace CLAUDE.md may add workspace-specific items. Run those too.

## Session Lifecycle

**Session Start:**
1. Read MEMORY.md — check pending items, patterns, preferences.
2. `git pull` if remote exists (cross-computer sync).
3. Resume from where last session left off.

**During Session (at stage completions):**
1. Update MEMORY.md with decisions and progress.
2. Push state to Supabase (if configured).
3. Git checkpoint (commit + push) at significant milestones.

**Session End:**
- Run `/session-checkpoint` — this invokes the full 9-step end-of-session protocol
  (resource audit, MEMORY.md, lessons, plan status, pending items, workspace checklist,
  git commit+push, Supabase sync, summary report).
- The session-checkpoint skill handles everything. Do NOT skip it.

## Memory Protocol

### Architecture
- **Project MEMORY.md** — Auto-loaded every session. Hard limit: 200 lines.
  Keep as concise index. Move details into topic files in same directory.
- **Topic files** — For content that won't fit in 200 lines.
  Reference from MEMORY.md (e.g., session-history.md, patterns.md).

### What to Record
- Decisions and reasoning behind them
- Patterns confirmed across 2+ interactions
- User preferences (communication style, decision patterns)
- Solutions to recurring problems
- Process improvements that proved effective
- Failures, root causes, and what was done instead

### What NOT to Record
- Temporary session context that won't matter next time
- Speculation or unverified conclusions
- Duplicate information already in project documentation
- Information that contradicts established rules without user approval

### 200-Line Discipline
- Most important info in FIRST 150 lines
- Session history → separate session-history.md
- Technical notes → topic-specific files
- Regularly prune outdated entries

## Extension Rule

Workspace CLAUDE.md files define ONLY workspace-specific additions to these
protocols. They should NOT duplicate items listed above. If a workspace CLAUDE.md
contradicts this rule, the workspace CLAUDE.md wins for that workspace
(local override principle).
```

---

## Phase 2: Update `BOOTSTRAP.md` Template

**File:** `sharkitect-claude-toolkit/BOOTSTRAP.md` (already exists at toolkit root)

### Changes to make:

**1. Add rename instruction at the very top (before "# Agent Instructions"):**
```markdown
<!-- BOOTSTRAP TEMPLATE — When instantiating a new workspace:
     1. Copy this file to the new workspace root
     2. Rename to CLAUDE.md
     3. Follow the Instantiation section below -->
```

**2. Replace the Task Protocols section (~lines 74-143) with universal rule reference:**
```markdown
## Task Protocols

Every task follows structured pre-task and post-task protocols. This is non-negotiable.

> **Universal protocols** (pre-task checklist, post-task checklist, memory protocol,
> session lifecycle, git backup) are loaded automatically from
> `~/.claude/rules/universal-protocols.md`. They apply to every session in every
> Sharkitect internal workspace. You do NOT need to duplicate them here.

### Pre-Task Checklist (WORKSPACE-SPECIFIC additions only)

**Project-specific (populated during instantiation based on PROJECT_PURPOSE):**
<!-- Add items here based on project structure. Examples:
- [ ] Run `python tools/sync-skills.py` to check for unsynced changes
- [ ] Check the client brief and requirements document
- [ ] Read relevant source files before modifying
-->

### Post-Task Checklist (WORKSPACE-SPECIFIC additions only)

**Project-specific (populated during instantiation based on PROJECT_PURPOSE):**
<!-- Add items here based on project structure. Examples:
- [ ] Run `python tools/sync-skills.py --sync --push`
- [ ] Verify sync report in `.tmp/last-sync.json`
- [ ] Run `/session-checkpoint` before closing (MANDATORY — from universal rule)
-->
```

**3. Replace the Persistent Memory section (~lines 147-187) with reference:**
```markdown
## Persistent Memory

> **Memory protocol** (200-line discipline, what-to-record, session protocol) is
> defined in `~/.claude/rules/universal-protocols.md` and loads automatically.
> Only workspace-specific memory architecture details go here.

### Memory Architecture

- **Project MEMORY.md** — Located at `.claude/projects/<project>/memory/MEMORY.md`.
  Auto-loaded every session. Hard limit: 200 lines. Keep as concise index.
- **Topic files** — Detailed notes in same memory directory. Reference from MEMORY.md.
```

**4. Add Step 5b to Skills Evaluation Workflow (Section 9, after Step 5):**
```markdown
### Step 5b: Validate Universal Protocols
Check if `~/.claude/rules/universal-protocols.md` exists:
- If YES: PASS (universal protocols will auto-load in every session)
- If NO: Flag as critical gap. Install from toolkit repo:
  `cp sharkitect-claude-toolkit/rules/universal-protocols.md ~/.claude/rules/`
  Or warn user to run INSTALL-GUIDE.md Step 7.
```

**5. Update bootstrap.py (Section 7) — add rules inventory to Phase 3:**

After the existing inventory section (~line 502 in template), add:
```python
    rules = inventory_rules(claude_home)
    ...
    print(f"  Rules found: {len(rules)}")
```

And add the inventory function:
```python
def inventory_rules(claude_home):
    """Scan ~/.claude/rules/ for all .md files."""
    rules_dir = claude_home / "rules"
    inventory = []
    if not rules_dir.exists():
        return inventory
    for rule_file in rules_dir.glob("*.md"):
        inventory.append({
            "name": rule_file.stem,
            "path": str(rule_file),
        })
    return inventory
```

And add to the report's actions_needed (~after Superpowers check):
```python
    # Check for universal protocols rule
    universal_rule = claude_home / "rules" / "universal-protocols.md"
    if not universal_rule.exists():
        report["actions_needed"].append({
            "priority": "CRITICAL",
            "action": "Install Universal Protocols",
            "reason": "Universal protocols rule not found. Install from toolkit repo: "
                      "copy rules/universal-protocols.md to ~/.claude/rules/",
        })
```

---

## Phase 3: Update Toolkit Repo Artifacts

### Add rule to repo
**File:** `sharkitect-claude-toolkit/rules/universal-protocols.md`
- Identical copy of the file created in Phase 1

### Update INSTALL-GUIDE.md
**File:** `sharkitect-claude-toolkit/INSTALL-GUIDE.md`

**In Step 7 (Install Rules), add note after the copy commands:**
```markdown
### What the rules do

| Rule | Purpose |
|------|---------|
| `context7.md` | Instructs Claude to use Context7 MCP for library documentation lookups |
| `api-limitations.md` | Protocol for handling API/MCP limitations with manual workarounds |
| `universal-protocols.md` | **Core operating protocols** — pre-task, post-task, memory, session lifecycle, git backup. Auto-loaded into every session. Workspace CLAUDE.md files extend these with workspace-specific additions only. |
```

**Add new section after Step 8 (or update existing "For New Workspaces" section):**
```markdown
## Setting Up a New Workspace

1. Copy `BOOTSTRAP.md` from this repo to your new workspace root
2. Rename to `CLAUDE.md`
3. Open Claude Code in the workspace and say "instantiate"
4. The bootstrap process will:
   - Check prerequisites (Python, Node.js)
   - Create directories and tool files
   - Verify universal protocols rule is installed
   - Run skills evaluation for the project
   - Populate workspace-specific checklist items
```

---

## Phase 4: Add session-start.py Validation

**File:** `C:\Users\Sharkitect Digital\.claude\plugins\cache\local\aios-core\scripts\session-start.py`

Add function (near the other check functions):
```python
def check_universal_protocols():
    """Verify universal-protocols.md rule exists."""
    rule_path = Path.home() / ".claude" / "rules" / "universal-protocols.md"
    if not rule_path.exists():
        return (
            "[aios-core] WARN: ~/.claude/rules/universal-protocols.md not found. "
            "Universal protocols (pre-task, post-task, memory, session-end) may be missing. "
            "Install from toolkit repo: INSTALL-GUIDE.md Step 7."
        )
    return None
```

In `main()`, after `git_msg = check_git_sync(cwd)` block (~line 531), add:
```python
    # Universal protocols validation
    proto_msg = check_universal_protocols()
    if proto_msg:
        lines.append(proto_msg)
```

Also update the toolkit copy: `sharkitect-claude-toolkit/custom-plugins/aios-core/scripts/session-start.py`

---

## Phase 5: Extend Sync Tool for Rules

**File:** `tools/sync-skills.py`

Currently syncs `~/.claude/skills/` → `sharkitect-claude-toolkit/skills/`. Add parallel sync for rules:

1. Add `get_rules_dir()` function returning `Path.home() / ".claude" / "rules"`
2. Add `get_repo_rules_dir()` function finding `sharkitect-claude-toolkit/rules/`
3. In the main comparison logic, add rules as a second sync target alongside skills
4. When `--sync` is used, copy rules diffs too
5. When `--push` is used, rules changes are included in the commit

This ensures `python tools/sync-skills.py --sync --push` keeps the toolkit repo's rules/ directory current.

---

## Files Summary

| File | Action | Phase |
|------|--------|-------|
| `~/.claude/rules/universal-protocols.md` | **CREATE** | 1 |
| `sharkitect-claude-toolkit/BOOTSTRAP.md` | **EDIT** — add rename instruction, replace protocol sections with rule references, add Step 5b, update bootstrap.py | 2 |
| `sharkitect-claude-toolkit/rules/universal-protocols.md` | **CREATE** — toolkit copy | 3 |
| `sharkitect-claude-toolkit/INSTALL-GUIDE.md` | **EDIT** — add rule description, new workspace section | 3 |
| `aios-core/scripts/session-start.py` | **EDIT** — add check_universal_protocols() | 4 |
| `sharkitect-claude-toolkit/custom-plugins/aios-core/scripts/session-start.py` | **EDIT** — same change as above (toolkit copy) | 4 |
| `tools/sync-skills.py` | **EDIT** — add rules directory sync | 5 |

**NOT modified:** HQ CLAUDE.md, Skill Hub CLAUDE.md, Sentinel CLAUDE.md, AIOS Builder CLAUDE.md

---

## Verification Plan

1. **Rule loading:** Start new session in any workspace → universal-protocols.md appears in system-reminder context alongside api-limitations.md and context7.md
2. **End-of-session:** Run `/session-checkpoint` → all 9 steps execute including git commit+push
3. **Bootstrap template:** Verify BOOTSTRAP.md references universal rule, not duplicated protocols
4. **session-start.py:** Temporarily rename universal-protocols.md → start session → confirm warning → rename back
5. **Sync tool:** Run `python tools/sync-skills.py` → rules/ directory appears in diff report
6. **New workspace flow:** Copy BOOTSTRAP.md to test folder → rename to CLAUDE.md → instantiate → confirm Step 5b validates universal protocols exist

---

## Execution Order

1. **Phase 1** (create universal rule) — everything depends on this
2. **Phase 2** (update BOOTSTRAP.md) — after Phase 1
3. **Phase 3** (toolkit repo: rule copy + INSTALL-GUIDE) — after Phase 1 & 2
4. **Phase 4** (session-start.py) — independent, anytime after Phase 1
5. **Phase 5** (sync tool) — last

Phases 2+4 can run in parallel since they touch different files.
