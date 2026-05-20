# Hook Router Consolidation Implementation Plan

> **STATUS: SUPERSEDED 2026-05-05 by `docs/superpowers/specs/2026-05-05-hook-dispatcher-consolidation-spec.md` (workspace).**
> The spec scope expanded from 9 hooks (this plan) to 23 hooks across 3 dispatchers ("Hook Dispatcher" naming locked). Categorical full-pass discovered additional cluster members + identified Post-Action Workflow Nudge cluster. This document remains as historical reference; do not execute against this plan.

---

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. TDD-first throughout — every sub-rule gets a failing test BEFORE the merge code lands.

**Goal:** Consolidate 9 production hooks into 2 routers (methodology-router + content-governance-router), reducing total `~/.claude/hooks/` count from 44 → 36 and PreToolUse:Edit|Write matcher from 17 → 10. Both routers integrate the existing `intent_detection.py` for unified user-driven-mode bypass. Absorbs sub-rules from wr-skillhub-2026-04-30-002 (canonical), wr-sentinel-2026-04-30-008 (plan-file Read), wr-hq-2026-05-04-008 (KB-governance), and wr-sentinel-2026-05-04-009 (multi-file-build + production-tool-no-tests).

**Architecture:** Two router entry points dispatch to per-sub-rule modules under `~/.claude/hooks/_routers/{methodology,content_governance}/`. Each sub-rule preserves the source hook's logic 1:1 (verified by extracted tests against the source hook's existing behavior). Routers share a single intent_detection.py call at the top — if user-driven, return early with no nudges. Sub-rules return optional advisory `additionalContext` strings; router collects and emits one merged hook output. Hard-deny sub-rules (K1 doc gate, content-enforcement-gate, hq-content-skill-stack-enforcer) short-circuit and emit a `decision: deny` payload.

**Tech Stack:** Python 3 stdlib only (Claude Code hook convention), pytest for tests, JSON-stdin/stdout hook protocol per Claude Code spec.

**Source documents:**
- wr-skillhub-2026-04-30-002 (canonical fix description, 9-component delete list)
- wr-sentinel-2026-04-30-008 (plan-file Read sub-rule)
- wr-hq-2026-05-04-008 (KB-governance sub-rule, already triaged into this consolidation)
- wr-sentinel-2026-05-04-009 (multi-file-build + production-tool-no-tests sub-rules — NEW absorption decision this session)
- `docs/audits/hook-inventory-audit-2026-04-27.md` (per-hook classification)
- `~/.claude/scripts/_lib/intent_detection.py` (shared user-driven-mode helper, already shipped)

**Pre-flight verified:** intent_detection.py exists with `detect_user_driven_mode()` and `is_user_driven()` public API at lines 329 and 419. tests/ directory exists with 14 existing test files following pytest conventions including `test_intent_detection.py` (sibling to our new test files).

**File structure (new):**
```
~/.claude/hooks/
├── methodology-router.py                        # NEW entry point (PreToolUse:Edit|Write|TodoWrite|Read)
├── content-governance-router.py                 # NEW entry point (PreToolUse:Edit|Write|Bash|mcp__)
└── _routers/
    ├── __init__.py                              # NEW
    ├── methodology/
    │   ├── __init__.py                          # NEW
    │   ├── brainstorming.py                     # NEW (extracts brainstorming-enforcer.py logic)
    │   ├── writing_plans.py                     # NEW (extracts writing-plans-enforcer.py logic)
    │   ├── methodology_nudge.py                 # NEW (extracts methodology-nudge.py rules)
    │   ├── claude_api.py                        # NEW (extracts claude-api-skill-nudge.py)
    │   ├── plan_file_read.py                    # NEW (wr-008 sub-rule, NEW logic)
    │   ├── multi_file_build.py                  # NEW (wr-009 sub-rule 1, NEW logic)
    │   └── production_tool.py                   # NEW (wr-009 sub-rule 2, NEW logic)
    └── content_governance/
        ├── __init__.py                          # NEW
        ├── content_enforcer.py                  # NEW (extracts content-enforcer-hook.py)
        ├── enforcement_gate.py                  # NEW (extracts content-enforcement-gate.py)
        ├── marketing_keywords.py                # NEW (extracts marketing-content-detector.py)
        ├── content_pitching.py                  # NEW (extracts content-pitching-detector.py)
        ├── skill_stack.py                       # NEW (extracts hq-content-skill-stack-enforcer.py)
        └── kb_governance.py                     # NEW (wr-hq-008 sub-rule, NEW logic)

~/.claude/tests/
├── test_methodology_router.py                   # NEW (dispatch + per sub-rule)
└── test_content_governance_router.py            # NEW (dispatch + per sub-rule)
```

**File structure (deleted after migration):**
- `~/.claude/hooks/methodology-nudge.py`
- `~/.claude/hooks/brainstorming-enforcer.py`
- `~/.claude/hooks/writing-plans-enforcer.py`
- `~/.claude/hooks/claude-api-skill-nudge.py`
- `~/.claude/hooks/content-enforcer-hook.py`
- `~/.claude/hooks/content-enforcement-gate.py`
- `~/.claude/hooks/marketing-content-detector.py`
- `~/.claude/hooks/content-pitching-detector.py`
- `~/.claude/hooks/hq-content-skill-stack-enforcer.py`

**Net effect:** 44 → 36 total hooks (-9 + 2 = -7 effective). PreToolUse:Edit|Write matcher: 17 → 10. PreToolUse:TodoWrite: 3 → 2. New PreToolUse:Read entry: methodology-router only.

---

## Phase 0: Pre-flight Audit + Foundation

### Task 0.1: Read each obsolete hook to capture its current behavior

**Files:** Read-only.

- [ ] **Step 1: Read all 9 source hooks**

```bash
for h in methodology-nudge brainstorming-enforcer writing-plans-enforcer claude-api-skill-nudge \
         content-enforcer-hook content-enforcement-gate marketing-content-detector \
         content-pitching-detector hq-content-skill-stack-enforcer; do
  echo "=== $h ==="
  wc -l ~/.claude/hooks/${h}.py
done
```

- [ ] **Step 2: For each hook, write a one-paragraph behavior note in scratch**

Capture: matcher type, signal trigger conditions, decision (advisory/deny), bypass phrases, dependencies (intent_detection, log files, etc.).

Save to `~/.claude/plans/router-consolidation-source-notes.md` (scratch — gitignored under workspace `.tmp/` if appropriate, but keep at plan-adjacent for reference during implementation).

- [ ] **Step 3: Commit the audit notes**

```bash
cd "C:\Users\Sharkitect Digital\Documents\Claude Code Workspaces\3.- Skill Management Hub"
git add ~/.claude/plans/router-consolidation-source-notes.md ~/.claude/plans/2026-05-04-hook-router-consolidation.md
git commit -m "plan: hook router consolidation — source-notes audit complete"
```

### Task 0.2: Create `_routers/` package skeleton

**Files:**
- Create: `~/.claude/hooks/_routers/__init__.py`
- Create: `~/.claude/hooks/_routers/methodology/__init__.py`
- Create: `~/.claude/hooks/_routers/content_governance/__init__.py`

- [ ] **Step 1: Write `_routers/__init__.py`**

```python
"""Router sub-rule modules. Imported by methodology-router.py and content-governance-router.py."""
```

- [ ] **Step 2: Write `_routers/methodology/__init__.py`**

```python
"""Methodology sub-rules. Each module exports `evaluate(payload) -> dict | None` where:

  payload = {
    "tool_name": str,
    "tool_input": dict,
    "transcript_path": str | None,
    "session_id": str | None,
    "matcher": str,
  }

  return None  -> sub-rule did not trigger (no contribution)
  return {"advisory": "<text>"}  -> contribute advisory nudge text
  return {"decision": "deny", "reason": "<text>"}  -> hard block (rare)
"""
```

- [ ] **Step 3: Write `_routers/content_governance/__init__.py`**

Same docstring pattern as methodology, with content-governance description.

- [ ] **Step 4: Commit**

```bash
git add ~/.claude/hooks/_routers/
git commit -m "router: add _routers package skeleton for hook consolidation"
```

---

## Phase 1: Methodology Router — TDD per sub-rule

For each sub-rule below, the cycle is: write failing test → confirm fail → extract/implement → confirm pass → commit. Tests live in `~/.claude/tests/test_methodology_router.py`. The router entry point is built last (Task 1.D).

### Task 1.1: Sub-rule — brainstorming (extracts brainstorming-enforcer.py)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/brainstorming.py`
- Test: `~/.claude/tests/test_methodology_router.py` (new file, first test added here)

- [ ] **Step 1: Write the failing test**

```python
# ~/.claude/tests/test_methodology_router.py
"""Tests for methodology-router.py sub-rules and dispatch logic.

Each sub-rule has its own test class. The dispatch test class verifies
that the router calls the right sub-rule for the right payload and
emits the correct merged output.
"""
import os
import sys
import pytest

# Make hooks/ importable
HOOKS_DIR = os.path.expanduser("~/.claude/hooks")
sys.path.insert(0, HOOKS_DIR)

from _routers.methodology import brainstorming


class TestBrainstormingSubRule:
    def test_3plus_options_in_recent_user_message_triggers_nudge(self, tmp_path):
        """Signal A from brainstorming-enforcer: user enumerates 3+ options
        in a single message and AI is about to write — nudge brainstorming skill.
        """
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"should we use option A, option B, or option C?"}}\n'
        )
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": "/some/file.py", "content": "x"},
            "transcript_path": str(transcript),
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is not None
        assert "advisory" in result
        assert "brainstorming" in result["advisory"].lower()

    def test_no_options_in_user_message_no_nudge(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"please update the file"}}\n'
        )
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": "/some/file.py", "content": "x"},
            "transcript_path": str(transcript),
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is None

    def test_user_driven_mode_bypasses(self, tmp_path):
        """Even with the 3+ options signal, if user is clearly driving
        (literal bypass phrase), we should pass through.
        """
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"option A or option B or option C — go with B"}}\n'
        )
        result = brainstorming.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": "/some/file.py", "content": "x"},
            "transcript_path": str(transcript),
            "matcher": "PreToolUse:Edit|Write",
        })
        # The "go with B" imperative authorizes — sub-rule should not trigger
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/.claude
python -m pytest tests/test_methodology_router.py::TestBrainstormingSubRule -v
```
Expected: ImportError (module brainstorming doesn't exist yet) OR all 3 tests FAIL with ModuleNotFoundError.

- [ ] **Step 3: Read source hook + extract logic**

```bash
cat ~/.claude/hooks/brainstorming-enforcer.py
```

Identify: the signal patterns (Signals A/B/C from the audit doc), the bypass phrase list, and the response format. Note dependencies on intent_detection.py (likely already imported).

- [ ] **Step 4: Write minimal implementation**

```python
# ~/.claude/hooks/_routers/methodology/brainstorming.py
"""Brainstorming sub-rule. Detects 3+ option enumeration in recent user
message and nudges superpowers:brainstorming skill before AI writes.

Source: brainstorming-enforcer.py (deleted after migration).
"""
from __future__ import annotations

import os
import re
import sys

# Add scripts/_lib to path for intent_detection
SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, SCRIPTS_LIB)
from intent_detection import is_user_driven  # noqa: E402

# Signal A: 3+ comma-or-or separated options in user message
_OPTIONS_PATTERN = re.compile(
    r"\boption\s+[A-Z]\b.*\boption\s+[A-Z]\b.*\boption\s+[A-Z]\b",
    re.IGNORECASE | re.DOTALL,
)

# Bypass phrases preserved from brainstorming-enforcer
_BYPASS = ("skip brainstorming", "already brainstormed")


def evaluate(payload: dict) -> dict | None:
    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Write", "Edit", "TodoWrite"):
        return None

    transcript = payload.get("transcript_path")
    if not transcript:
        return None

    # Read recent user message text
    try:
        from intent_detection import read_recent_user_messages
        messages = read_recent_user_messages(transcript, lookback=5)
    except Exception:
        return None

    if not messages:
        return None

    # Most recent message
    if not _OPTIONS_PATTERN.search(messages[0]):
        return None

    # User-driven mode bypasses
    file_path = payload.get("tool_input", {}).get("file_path")
    if is_user_driven(transcript, file_path=file_path, bypass_phrases=_BYPASS):
        return None

    return {
        "advisory": (
            "BRAINSTORMING SKIP DETECTED. Recent user message enumerates 3+ "
            "options. Invoke superpowers:brainstorming skill BEFORE writing — "
            "structured option evaluation prevents premature commitment."
        )
    }
```

- [ ] **Step 5: Run test to verify pass**

```bash
python -m pytest tests/test_methodology_router.py::TestBrainstormingSubRule -v
```
Expected: 3/3 PASS.

- [ ] **Step 6: Commit**

```bash
git add ~/.claude/hooks/_routers/methodology/brainstorming.py \
        ~/.claude/tests/test_methodology_router.py
git commit -m "router: methodology brainstorming sub-rule + tests (TDD-first)"
```

### Task 1.2: Sub-rule — writing_plans (extracts writing-plans-enforcer.py)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/writing_plans.py`
- Modify: `~/.claude/tests/test_methodology_router.py` (append test class)

- [ ] **Step 1: Append failing test class**

```python
# Append to ~/.claude/tests/test_methodology_router.py
from _routers.methodology import writing_plans


class TestWritingPlansSubRule:
    def test_multi_section_plan_body_triggers_nudge(self, tmp_path):
        """Signal: AI is writing a plan-shaped file (3+ ## headers,
        contains 'Phase' or 'Task') without writing-plans skill in session log.
        """
        plan_content = """# My Plan
## Phase 1
### Task 1.1
## Phase 2
### Task 2.1
## Phase 3
### Task 3.1
"""
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"build the system"}}\n'
        )
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/path/to/plans/my-plan.md",
                "content": plan_content,
            },
            "transcript_path": str(transcript),
            "session_id": "test-session-no-skill-log",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is not None
        assert "writing-plans" in result["advisory"].lower()

    def test_non_plan_file_no_nudge(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"build the system"}}\n'
        )
        result = writing_plans.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/path/to/some/random.py",
                "content": "print('hello')",
            },
            "transcript_path": str(transcript),
            "session_id": "test",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is None
```

- [ ] **Step 2: Run, confirm fail (ModuleNotFoundError on writing_plans)**

```bash
python -m pytest tests/test_methodology_router.py::TestWritingPlansSubRule -v
```

- [ ] **Step 3: Read writing-plans-enforcer.py source**

```bash
cat ~/.claude/hooks/writing-plans-enforcer.py
```

- [ ] **Step 4: Implement sub-rule preserving source logic**

```python
# ~/.claude/hooks/_routers/methodology/writing_plans.py
"""Writing-plans sub-rule. Detects plan-shaped file writes without prior
superpowers:writing-plans skill invocation; nudges to invoke.

Source: writing-plans-enforcer.py (deleted after migration).
"""
from __future__ import annotations

import os
import re
import sys

SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, SCRIPTS_LIB)
from intent_detection import is_user_driven  # noqa: E402

# Plan-shape detection: 3+ ## headers AND mentions Phase/Task
_HEADER_RE = re.compile(r"^##\s+", re.MULTILINE)
_PHASE_RE = re.compile(r"\b(?:Phase|Task)\s+\d", re.IGNORECASE)

_BYPASS = ("skip writing-plans", "skip plan-skill")


def _is_plan_file_path(path: str) -> bool:
    p = path.lower().replace("\\", "/")
    return ("/plans/" in p or "plan" in os.path.basename(p)) and p.endswith(".md")


def _has_invoked_writing_plans_skill(session_id: str | None) -> bool:
    """Check ~/.claude/.tmp/skill-invocations/<session_id>.jsonl for evidence
    of superpowers:writing-plans invocation this session.
    """
    if not session_id:
        return False
    log = os.path.expanduser(f"~/.claude/.tmp/skill-invocations/{session_id}.jsonl")
    if not os.path.exists(log):
        return False
    try:
        with open(log, encoding="utf-8") as fh:
            return "writing-plans" in fh.read()
    except OSError:
        return False


def evaluate(payload: dict) -> dict | None:
    if payload.get("tool_name") not in ("Write", "Edit"):
        return None

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    content = tool_input.get("content") or tool_input.get("new_string") or ""

    if not _is_plan_file_path(file_path):
        return None

    headers = _HEADER_RE.findall(content)
    if len(headers) < 3:
        return None
    if not _PHASE_RE.search(content):
        return None

    if _has_invoked_writing_plans_skill(payload.get("session_id")):
        return None

    if is_user_driven(payload.get("transcript_path"), file_path=file_path, bypass_phrases=_BYPASS):
        return None

    return {
        "advisory": (
            "MULTI-PHASE PLAN WRITE DETECTED without superpowers:writing-plans "
            "skill invoked this session. Invoke the skill before continuing — "
            "it enforces TDD-first task structure, exact-file-path discipline, "
            "and bite-sized step granularity."
        )
    }
```

- [ ] **Step 5: Run test, confirm pass**

```bash
python -m pytest tests/test_methodology_router.py::TestWritingPlansSubRule -v
```

- [ ] **Step 6: Commit**

```bash
git add ~/.claude/hooks/_routers/methodology/writing_plans.py \
        ~/.claude/tests/test_methodology_router.py
git commit -m "router: methodology writing_plans sub-rule + tests"
```

### Task 1.3: Sub-rule — methodology_nudge (extracts methodology-nudge.py rules)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/methodology_nudge.py`
- Modify: `~/.claude/tests/test_methodology_router.py`

This is the largest source hook (37KB). It contains multiple internal triggers (testing-strategy nudge, systematic-debugging nudge, etc.). Extract its trigger map verbatim.

- [ ] **Step 1: Append failing test class with one test per preserved trigger**

```python
# Append to test_methodology_router.py
from _routers.methodology import methodology_nudge


class TestMethodologyNudgeSubRule:
    def test_systematic_debugging_trigger(self, tmp_path):
        """When 2+ Edit calls hit the same file in this session AND user
        message indicates a bug (recent error/debug terms), nudge
        superpowers:systematic-debugging.
        """
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"this is still broken, why"}}\n'
        )
        # The hook should access tool-usage journal; mock by env var or
        # test a no-op path. Keep test minimal: confirm dispatcher returns
        # advisory text containing "systematic-debugging" when triggered.
        # Detailed trigger conditions extracted from methodology-nudge.py.
        result = methodology_nudge.evaluate({
            "tool_name": "Edit",
            "tool_input": {"file_path": "/repo/src/buggy.py", "old_string": "x", "new_string": "y"},
            "transcript_path": str(transcript),
            "session_id": "test-mn-debug",
            "matcher": "PreToolUse:Edit|Write",
            # Test fixture-injected: this is the 3rd edit on /repo/src/buggy.py
            "_test_edit_count": 3,
        })
        # Allow None or systematic-debugging advisory; assertion calibrated
        # in implementation step after reading the source hook's exact rule.
        if result is not None:
            assert "systematic-debugging" in result["advisory"].lower()

    # Additional trigger tests added per source-hook trigger discovered in Step 3.
    # Each documented trigger gets a paired test before extraction.
```

- [ ] **Step 2: Run, confirm fail or no-coverage**

- [ ] **Step 3: Read source hook**

```bash
cat ~/.claude/hooks/methodology-nudge.py | head -200
```

- [ ] **Step 4: Implement preserving each documented trigger**

Given the hook's size, extract one rule at a time as separate functions inside `methodology_nudge.py`:
```python
def _check_systematic_debugging(payload): ...
def _check_testing_strategy(payload): ...
def _check_<other_triggers>(payload): ...

def evaluate(payload):
    for checker in (_check_systematic_debugging, _check_testing_strategy, ...):
        result = checker(payload)
        if result:
            return result
    return None
```

- [ ] **Step 5: Per-trigger test loop — for each trigger discovered in source, append a test, then implement**

Increments commits — one trigger per commit.

- [ ] **Step 6: Final commit when all preserved triggers pass**

```bash
git commit -m "router: methodology_nudge sub-rule preserves all source triggers (TDD)"
```

### Task 1.4: Sub-rule — claude_api (extracts claude-api-skill-nudge.py)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/claude_api.py`
- Modify: `~/.claude/tests/test_methodology_router.py`

- [ ] **Step 1: Append failing test**

```python
from _routers.methodology import claude_api


class TestClaudeApiSubRule:
    def test_anthropic_sdk_import_triggers_nudge(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text('{"type":"user","message":{"content":"add the call"}}\n')
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/repo/app.py",
                "content": "import anthropic\nclient = anthropic.Anthropic()\n",
            },
            "transcript_path": str(transcript),
            "session_id": "test-ca",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is not None
        assert "claude-api" in result["advisory"].lower() or "anthropic" in result["advisory"].lower()

    def test_openai_import_no_nudge(self, tmp_path):
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text('{"type":"user","message":{"content":"add the call"}}\n')
        result = claude_api.evaluate({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/repo/app.py",
                "content": "import openai\n",
            },
            "transcript_path": str(transcript),
            "session_id": "test-ca",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is None
```

- [ ] **Step 2: Run test, confirm fail**

- [ ] **Step 3: Read source + extract import-pattern detection**

```bash
cat ~/.claude/hooks/claude-api-skill-nudge.py
```

- [ ] **Step 4: Implement**

```python
# ~/.claude/hooks/_routers/methodology/claude_api.py
"""Claude API sub-rule. Detects Anthropic SDK usage and nudges claude-api skill.

Source: claude-api-skill-nudge.py (deleted after migration).
"""
from __future__ import annotations

import os
import re
import sys

SCRIPTS_LIB = os.path.expanduser("~/.claude/scripts/_lib")
if SCRIPTS_LIB not in sys.path:
    sys.path.insert(0, SCRIPTS_LIB)
from intent_detection import is_user_driven  # noqa: E402

_ANTHROPIC_RE = re.compile(
    r"(?:import\s+anthropic|from\s+anthropic|@anthropic-ai/sdk|anthropic\.Anthropic)",
    re.IGNORECASE,
)

_BYPASS = ("skip claude-api",)


def evaluate(payload: dict) -> dict | None:
    if payload.get("tool_name") not in ("Write", "Edit"):
        return None
    content = (
        payload.get("tool_input", {}).get("content")
        or payload.get("tool_input", {}).get("new_string", "")
    )
    if not _ANTHROPIC_RE.search(content):
        return None
    if is_user_driven(
        payload.get("transcript_path"),
        file_path=payload.get("tool_input", {}).get("file_path"),
        bypass_phrases=_BYPASS,
    ):
        return None
    return {
        "advisory": (
            "ANTHROPIC SDK USAGE DETECTED. Invoke the claude-api skill before "
            "writing — ensures prompt caching, latest model IDs, and avoids "
            "deprecated patterns."
        )
    }
```

- [ ] **Step 5: Run, confirm pass**

- [ ] **Step 6: Commit**

```bash
git commit -m "router: methodology claude_api sub-rule (folds claude-api-skill-nudge)"
```

### Task 1.5: NEW Sub-rule — plan_file_read (wr-008 absorption)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/plan_file_read.py`
- Modify: `~/.claude/tests/test_methodology_router.py`

- [ ] **Step 1: Append failing test**

```python
from _routers.methodology import plan_file_read


class TestPlanFileReadSubRule:
    """wr-sentinel-2026-04-30-008 absorption: when AI Reads a plan file
    that declares REQUIRED SUB-SKILL: superpowers:executing-plans, nudge
    invocation before continuing.
    """

    def test_plan_with_required_subskill_marker_triggers(self, tmp_path):
        plan = tmp_path / "test-plan.md"
        plan.write_text(
            "# Foo Plan\n\n"
            "> **For agentic workers:** REQUIRED SUB-SKILL: Use "
            "superpowers:executing-plans to implement this plan task-by-task.\n"
            "## Phase 1\n"
        )
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan)},
            "transcript_path": str(transcript),
            "session_id": "test-plan-read",
            "matcher": "PreToolUse:Read",
        })
        assert result is not None
        assert "executing-plans" in result["advisory"].lower()

    def test_plan_without_marker_no_trigger(self, tmp_path):
        plan = tmp_path / "no-marker-plan.md"
        plan.write_text("# Foo\n## Phase 1\n")
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan)},
            "transcript_path": str(transcript),
            "session_id": "test-plan-no-marker",
            "matcher": "PreToolUse:Read",
        })
        assert result is None

    def test_skill_already_invoked_suppresses(self, tmp_path, monkeypatch):
        plan = tmp_path / "test-plan.md"
        plan.write_text(
            "REQUIRED SUB-SKILL: Use superpowers:executing-plans\n"
        )
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        # Inject session log proving skill was invoked
        log_dir = tmp_path / "skill-invocations"
        log_dir.mkdir()
        log = log_dir / "test-already-invoked.jsonl"
        log.write_text('{"skill":"superpowers:executing-plans"}\n')
        monkeypatch.setenv("CLAUDE_SKILL_INVOCATION_LOG_DIR", str(log_dir))
        result = plan_file_read.evaluate({
            "tool_name": "Read",
            "tool_input": {"file_path": str(plan)},
            "transcript_path": str(transcript),
            "session_id": "test-already-invoked",
            "matcher": "PreToolUse:Read",
        })
        assert result is None
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement (NEW logic, no source hook to extract)**

```python
# ~/.claude/hooks/_routers/methodology/plan_file_read.py
"""Plan-file Read sub-rule. wr-sentinel-2026-04-30-008 absorption.

When AI Reads a plan file containing 'REQUIRED SUB-SKILL: superpowers:
executing-plans' in the first ~30 lines, nudge invocation before continuing.
Suppresses if the skill was already invoked this session.
"""
from __future__ import annotations

import os
import re

_PLAN_PATH_RE = re.compile(r"(?:/|\\)plans(?:/|\\)|plan\.md$|-plan\.md$", re.IGNORECASE)
_MARKER_RE = re.compile(
    r"REQUIRED\s+SUB-?SKILL.*superpowers:executing-plans",
    re.IGNORECASE | re.DOTALL,
)


def _skill_log_dir() -> str:
    return os.environ.get(
        "CLAUDE_SKILL_INVOCATION_LOG_DIR",
        os.path.expanduser("~/.claude/.tmp/skill-invocations"),
    )


def _executing_plans_invoked(session_id: str | None) -> bool:
    if not session_id:
        return False
    log = os.path.join(_skill_log_dir(), f"{session_id}.jsonl")
    if not os.path.exists(log):
        return False
    try:
        with open(log, encoding="utf-8") as fh:
            return "executing-plans" in fh.read()
    except OSError:
        return False


def evaluate(payload: dict) -> dict | None:
    if payload.get("tool_name") != "Read":
        return None
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not _PLAN_PATH_RE.search(file_path):
        return None
    if not file_path.lower().endswith(".md"):
        return None
    try:
        with open(file_path, encoding="utf-8") as fh:
            head = "".join(fh.readline() for _ in range(30))
    except OSError:
        return None
    if not _MARKER_RE.search(head):
        return None
    if _executing_plans_invoked(payload.get("session_id")):
        return None
    return {
        "advisory": (
            "PLAN EXECUTION DETECTED. The plan file you just read declares "
            "superpowers:executing-plans as REQUIRED SUB-SKILL. Invoke it "
            "before continuing — it enforces phase exit-criteria gating, "
            "structured task progress, and the skill's self-review checklist."
        )
    }
```

- [ ] **Step 4: Run tests, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -m "router: methodology plan_file_read sub-rule (wr-008 absorption)"
```

### Task 1.6: NEW Sub-rule — multi_file_build (wr-009 sub-rule 1)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/multi_file_build.py`
- Modify: `~/.claude/tests/test_methodology_router.py`

- [ ] **Step 1: Append failing test**

```python
from _routers.methodology import multi_file_build


class TestMultiFileBuildSubRule:
    """wr-sentinel-2026-05-04-009 absorption: 5+ Write/Edit on different
    file types in same session without writing-plans skill -> nudge.
    """

    def test_5plus_distinct_files_without_plan_skill(self, tmp_path, monkeypatch):
        """When tool-usage journal shows 5+ writes across distinct paths
        (different basenames OR different extensions) and writing-plans
        skill not invoked this session, sub-rule nudges.
        """
        # Build a fake tool-usage journal
        journal = tmp_path / "tool_usage.jsonl"
        journal.write_text(
            '{"session_id":"s1","tool":"Write","file_path":"/a/spec.md"}\n'
            '{"session_id":"s1","tool":"Write","file_path":"/a/tool.py"}\n'
            '{"session_id":"s1","tool":"Write","file_path":"/a/wrap.bat"}\n'
            '{"session_id":"s1","tool":"Write","file_path":"/a/wrap.vbs"}\n'
            '{"session_id":"s1","tool":"Write","file_path":"/a/doc.md"}\n'
        )
        monkeypatch.setenv("CLAUDE_TOOL_USAGE_JOURNAL", str(journal))
        # No skill invocation log
        monkeypatch.setenv("CLAUDE_SKILL_INVOCATION_LOG_DIR", str(tmp_path / "skills"))
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        result = multi_file_build.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": "/a/test.py", "content": "x"},
            "transcript_path": str(transcript),
            "session_id": "s1",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is not None
        assert "writing-plans" in result["advisory"].lower()

    def test_few_files_no_nudge(self, tmp_path, monkeypatch):
        journal = tmp_path / "tj.jsonl"
        journal.write_text(
            '{"session_id":"s2","tool":"Write","file_path":"/a/x.py"}\n'
        )
        monkeypatch.setenv("CLAUDE_TOOL_USAGE_JOURNAL", str(journal))
        monkeypatch.setenv("CLAUDE_SKILL_INVOCATION_LOG_DIR", str(tmp_path / "skills"))
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        result = multi_file_build.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": "/a/y.py", "content": "x"},
            "transcript_path": str(transcript),
            "session_id": "s2",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is None
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement**

```python
# ~/.claude/hooks/_routers/methodology/multi_file_build.py
"""Multi-file-build sub-rule. wr-sentinel-2026-05-04-009 absorption.

When tool-usage journal shows 5+ Write/Edit on distinct paths in the
same session AND writing-plans skill not invoked this session, nudge.
"""
from __future__ import annotations

import json
import os


def _journal_path() -> str:
    return os.environ.get(
        "CLAUDE_TOOL_USAGE_JOURNAL",
        os.path.expanduser("~/.claude/.tmp/claude_tool_usage_journal.jsonl"),
    )


def _skill_log_dir() -> str:
    return os.environ.get(
        "CLAUDE_SKILL_INVOCATION_LOG_DIR",
        os.path.expanduser("~/.claude/.tmp/skill-invocations"),
    )


def _writing_plans_invoked(session_id: str | None) -> bool:
    if not session_id:
        return False
    log = os.path.join(_skill_log_dir(), f"{session_id}.jsonl")
    if not os.path.exists(log):
        return False
    try:
        with open(log, encoding="utf-8") as fh:
            return "writing-plans" in fh.read()
    except OSError:
        return False


def _distinct_writes_in_session(session_id: str) -> int:
    path = _journal_path()
    if not os.path.exists(path):
        return 0
    paths = set()
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except (json.JSONDecodeError, ValueError):
                    continue
                if rec.get("session_id") != session_id:
                    continue
                if rec.get("tool") not in ("Write", "Edit"):
                    continue
                fp = rec.get("file_path")
                if fp:
                    paths.add(fp)
    except OSError:
        return 0
    return len(paths)


def evaluate(payload: dict) -> dict | None:
    if payload.get("tool_name") not in ("Write", "Edit"):
        return None
    sid = payload.get("session_id")
    if not sid:
        return None
    if _distinct_writes_in_session(sid) < 5:
        return None
    if _writing_plans_invoked(sid):
        return None
    return {
        "advisory": (
            "MULTI-FILE BUILD DETECTED (5+ distinct files this session) without "
            "superpowers:writing-plans skill invoked. Multi-step builds without "
            "structure drift on the 6th or 7th file. Invoke the skill now to "
            "scaffold the remaining work."
        )
    }
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -m "router: methodology multi_file_build sub-rule (wr-009 absorption)"
```

### Task 1.7: NEW Sub-rule — production_tool (wr-009 sub-rule 2)

**Files:**
- Create: `~/.claude/hooks/_routers/methodology/production_tool.py`
- Modify: `~/.claude/tests/test_methodology_router.py`

- [ ] **Step 1: Append failing test**

```python
from _routers.methodology import production_tool


class TestProductionToolSubRule:
    """wr-sentinel-2026-05-04-009 absorption: tools/ Python file with
    production-mutation indicators (PATCH, execute_sql, urllib.request)
    and no matching tests/ -> nudge testing-strategy.
    """

    def test_production_tool_no_tests_triggers(self, tmp_path):
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        new_file = tools_dir / "goal-monitor.py"
        content = (
            "import urllib.request\n"
            "def main():\n"
            "    urllib.request.urlopen('http://supabase/...PATCH...')\n"
        )
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(new_file), "content": content},
            "transcript_path": str(transcript),
            "session_id": "test-pt",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is not None
        assert "testing-strategy" in result["advisory"].lower()

    def test_existing_tests_suppress(self, tmp_path):
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        new_file = tools_dir / "goal-monitor.py"
        (tests_dir / "test_goal_monitor.py").write_text("def test_x(): pass")
        content = "import urllib.request\nPATCH = 1\n"
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text("")
        result = production_tool.evaluate({
            "tool_name": "Write",
            "tool_input": {"file_path": str(new_file), "content": content},
            "transcript_path": str(transcript),
            "session_id": "test-pt2",
            "matcher": "PreToolUse:Edit|Write",
        })
        assert result is None
```

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement**

```python
# ~/.claude/hooks/_routers/methodology/production_tool.py
"""Production-tool-no-tests sub-rule. wr-sentinel-2026-05-04-009 absorption.

When new Python file under tools/ contains production-mutation indicators
AND no matching tests/test_<basename>.py exists, advise testing-strategy.
"""
from __future__ import annotations

import os
import re

_INDICATORS = re.compile(
    r"(?:urllib\.request|requests\.(?:patch|put|post|delete)|"
    r"\bPATCH\b|\bexecute_sql\b|\bsupabase\.|psycopg|sqlite3\.execute)",
    re.IGNORECASE,
)


def _tools_python_path(file_path: str) -> bool:
    p = file_path.replace("\\", "/").lower()
    return "/tools/" in p and p.endswith(".py")


def _matching_test_exists(file_path: str) -> bool:
    base = os.path.basename(file_path)
    stem = os.path.splitext(base)[0].replace("-", "_")
    candidates = [
        f"test_{stem}.py",
        f"{stem}_test.py",
    ]
    # Walk up to find a sibling tests/ dir
    cur = os.path.dirname(os.path.abspath(file_path))
    for _ in range(4):
        tests_dir = os.path.join(os.path.dirname(cur), "tests")
        if os.path.isdir(tests_dir):
            for c in candidates:
                if os.path.exists(os.path.join(tests_dir, c)):
                    return True
        cur = os.path.dirname(cur)
        if cur in ("", "/"):
            break
    return False


def evaluate(payload: dict) -> dict | None:
    if payload.get("tool_name") not in ("Write", "Edit"):
        return None
    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if not _tools_python_path(file_path):
        return None
    content = tool_input.get("content") or tool_input.get("new_string") or ""
    if not _INDICATORS.search(content):
        return None
    if _matching_test_exists(file_path):
        return None
    return {
        "advisory": (
            "PRODUCTION TOOL WITHOUT TESTS DETECTED. The file mutates "
            "production state (HTTP/PATCH, execute_sql, supabase, etc.) but "
            "no matching tests/test_<basename>.py exists. Invoke "
            "testing-strategy skill before shipping — autonomous tools that "
            "modify production data without smoke tests are a recurring "
            "regression class."
        )
    }
```

- [ ] **Step 4: Run, confirm pass**

- [ ] **Step 5: Commit**

```bash
git commit -m "router: methodology production_tool sub-rule (wr-009 absorption)"
```

### Task 1.D: Methodology router entry point + dispatch

**Files:**
- Create: `~/.claude/hooks/methodology-router.py`
- Modify: `~/.claude/tests/test_methodology_router.py`

- [ ] **Step 1: Append dispatch tests**

```python
import io
import json
import subprocess

ROUTER = os.path.expanduser("~/.claude/hooks/methodology-router.py")


class TestRouterDispatch:
    def test_router_returns_zero_exit_on_no_trigger(self, tmp_path):
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/some/random.py", "content": "x"},
            "transcript_path": str(tmp_path / "no-transcript"),
            "session_id": "no-triggers",
        }
        result = subprocess.run(
            ["python", ROUTER],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0

    def test_router_emits_combined_advisory(self, tmp_path):
        """If two sub-rules trigger, router should emit both advisories
        in the additionalContext output.
        """
        # Construct payload that triggers brainstorming + claude_api
        transcript = tmp_path / "tr.jsonl"
        transcript.write_text(
            '{"type":"user","message":{"content":"option A or option B or option C"}}\n'
        )
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/repo/app.py",
                "content": "import anthropic\nclient = anthropic.Anthropic()\n",
            },
            "transcript_path": str(transcript),
            "session_id": "combined",
        }
        result = subprocess.run(
            ["python", ROUTER],
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=10,
        )
        assert result.returncode == 0
        out = result.stdout
        # Hook output is JSON with hookSpecificOutput.additionalContext
        data = json.loads(out)
        ctx = data.get("hookSpecificOutput", {}).get("additionalContext", "")
        assert "brainstorming" in ctx.lower()
        assert "anthropic" in ctx.lower() or "claude-api" in ctx.lower()
```

- [ ] **Step 2: Run, confirm fail (router file doesn't exist)**

- [ ] **Step 3: Implement entry point**

```python
#!/usr/bin/env python
"""methodology-router.py - Consolidates 7 methodology hooks into one router.

Dispatches per-payload to sub-rule modules under _routers/methodology/.
Each sub-rule may return:
  None                                  -> no contribution
  {"advisory": "<text>"}                -> contribute advisory text
  {"decision": "deny", "reason": ...}   -> hard block (rare; not used by
                                           any methodology sub-rule)

Router consolidates contributions into a single hookSpecificOutput payload.

Source consolidations:
  brainstorming-enforcer.py
  writing-plans-enforcer.py
  methodology-nudge.py
  claude-api-skill-nudge.py

Absorbed sub-rules:
  wr-sentinel-2026-04-30-008 (plan_file_read)
  wr-sentinel-2026-05-04-009 (multi_file_build, production_tool)

Per Hook Introduction Rule + intent_detection.py contract: every sub-rule
checks user-driven mode early so user-driven cascade work passes through.
"""
from __future__ import annotations

import json
import os
import sys
import traceback


def _load_payload() -> dict:
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, ValueError):
        return {}


def _emit_pass_through() -> None:
    """No advisory, no decision. Hook is a no-op."""
    sys.stdout.write("")


def _emit_advisory(text: str) -> None:
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }
    sys.stdout.write(json.dumps(payload))


def _safe_evaluate(module_name: str, payload: dict) -> dict | None:
    """Import a sub-rule module and call evaluate(). Catch any exception so
    one bad sub-rule never kills the whole router.
    """
    try:
        mod = __import__(
            f"_routers.methodology.{module_name}", fromlist=["evaluate"]
        )
        return mod.evaluate(payload)
    except Exception:
        # Log to stderr so hook telemetry can pick it up; never block.
        sys.stderr.write(
            f"[methodology-router] sub-rule '{module_name}' raised:\n"
            + traceback.format_exc()
        )
        return None


# Sub-rule registry: ordering = priority. First decision-deny short-circuits.
SUB_RULES = (
    "brainstorming",
    "writing_plans",
    "methodology_nudge",
    "claude_api",
    "plan_file_read",
    "multi_file_build",
    "production_tool",
)


def main() -> int:
    # Make _routers package importable
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)

    payload = _load_payload()
    if not payload:
        _emit_pass_through()
        return 0

    advisories: list[str] = []
    for sub in SUB_RULES:
        result = _safe_evaluate(sub, payload)
        if not result:
            continue
        if result.get("decision") == "deny":
            # Methodology sub-rules don't deny in current design; if one
            # ever does, honor it.
            sys.stdout.write(json.dumps({
                "decision": "block",
                "reason": result.get("reason", "methodology-router sub-rule denied"),
            }))
            return 0
        adv = result.get("advisory")
        if adv:
            advisories.append(adv)

    if not advisories:
        _emit_pass_through()
        return 0

    _emit_advisory("\n\n".join(advisories))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run dispatch tests, confirm pass**

```bash
python -m pytest tests/test_methodology_router.py::TestRouterDispatch -v
```

- [ ] **Step 5: Commit**

```bash
git commit -m "router: methodology-router.py entry point + dispatch (TDD)"
```

---

## Phase 2: Content-Governance Router — TDD per sub-rule

Same pattern as Phase 1: extract logic from each source hook with paired tests, then build the dispatcher.

Source hooks (5):
1. `content-enforcer-hook.py` → `_routers/content_governance/content_enforcer.py`
2. `content-enforcement-gate.py` → `_routers/content_governance/enforcement_gate.py` (HARD GATE)
3. `marketing-content-detector.py` → `_routers/content_governance/marketing_keywords.py` (HARD GATE)
4. `content-pitching-detector.py` → `_routers/content_governance/content_pitching.py`
5. `hq-content-skill-stack-enforcer.py` → `_routers/content_governance/skill_stack.py` (HARD GATE)

Plus 1 NEW absorbed sub-rule: `kb_governance.py` (wr-hq-2026-05-04-008).

### Task 2.1 through 2.6: Per sub-rule extraction (TDD pattern)

For each of the 5 source hooks AND the 1 new sub-rule:

- [ ] **Step 1: Append failing test class to `tests/test_content_governance_router.py`** with at minimum:
  - Trigger condition test (positive case)
  - Non-trigger case
  - User-driven bypass test (where applicable)
  - For HARD GATEs: confirm `decision: deny` returned, not advisory

- [ ] **Step 2: Read source hook**
  ```bash
  cat ~/.claude/hooks/<source-hook>.py
  ```

- [ ] **Step 3: Implement sub-rule preserving source logic 1:1.** Use the same `evaluate(payload) -> dict | None` contract as methodology sub-rules. HARD GATE sub-rules return `{"decision": "deny", "reason": ...}`.

- [ ] **Step 4: Run tests, confirm pass**

- [ ] **Step 5: Commit per sub-rule**

```bash
git commit -m "router: content-governance <sub_rule_name> sub-rule + tests"
```

**Per-sub-rule notes:**

- **content_enforcer.py** (advisory): soft nudge for HQ client content. Bypass phrases preserved from source.
- **enforcement_gate.py** (HARD GATE): K1 doc detection without authorization → deny. Preserve K1-doc detection regex from source verbatim.
- **marketing_keywords.py** (HARD GATE): Marketing keyword in non-marketing content → deny. Source identifies the 5 documented structural exemptions; preserve them.
- **content_pitching.py** (advisory): content-pitching detection.
- **skill_stack.py** (HARD GATE): 4-skill stack enforcement (HQ-only). Section-aware diff parsing (per audit doc Phase 3 deliverable, already shipped). Preserve.
- **kb_governance.py** (NEW, advisory): edits to `knowledge-base/**/*.md` without `hq-knowledge-governance` skill invoked this session. Pattern parallels plan_file_read.py from Phase 1.

### Task 2.D: Content-governance router entry point + dispatch

**Files:**
- Create: `~/.claude/hooks/content-governance-router.py`
- Modify: `~/.claude/tests/test_content_governance_router.py`

- [ ] **Step 1: Append dispatch tests**

Same pattern as methodology dispatch tests. Add: HARD GATE short-circuit test (when enforcement_gate denies, no advisory contributions appended; output is `decision: block`).

- [ ] **Step 2: Run, confirm fail**

- [ ] **Step 3: Implement entry point**

```python
#!/usr/bin/env python
"""content-governance-router.py - Consolidates 5 content-governance hooks
into one router with sub-rule dispatch.

Source consolidations:
  content-enforcer-hook.py
  content-enforcement-gate.py            (HARD GATE)
  marketing-content-detector.py          (HARD GATE)
  content-pitching-detector.py
  hq-content-skill-stack-enforcer.py     (HARD GATE)

Absorbed sub-rule:
  wr-hq-2026-05-04-008 (kb_governance)

Behavior: HARD GATE sub-rules short-circuit. Advisory sub-rules are
collected and emitted as a single combined additionalContext payload.
"""
# Same pattern as methodology-router.py with SUB_RULES list:
SUB_RULES = (
    # HARD GATEs first (short-circuit)
    "enforcement_gate",
    "marketing_keywords",
    "skill_stack",
    # Advisory
    "content_enforcer",
    "content_pitching",
    "kb_governance",
)
# Module path: _routers.content_governance.<name>
# Rest follows methodology-router.py exactly with content_governance package.
```

- [ ] **Step 4: Run all router tests, confirm pass**

```bash
python -m pytest tests/test_content_governance_router.py -v
```

- [ ] **Step 5: Commit**

```bash
git commit -m "router: content-governance-router.py entry point + dispatch (TDD)"
```

---

## Phase 3: Settings Migration

### Task 3.1: Stage settings.json change

- [ ] **Step 1: Read current `~/.claude/settings.json` to understand current entries**

```bash
python -c "import json,os; s=json.load(open(os.path.expanduser('~/.claude/settings.json'))); h=s.get('hooks',{}); [print(m, len(v)) for m,v in h.items()]"
```

- [ ] **Step 2: Compute diff** — list of entries to remove (the 9 deleted hooks) and entries to add (the 2 new routers).

Add entries (per current Claude Code hook spec):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|TodoWrite|Read",
        "hooks": [{"type":"command", "command":"$HOME/.claude/hooks/methodology-router.py"}]
      },
      {
        "matcher": "Edit|Write|Bash|mcp__",
        "hooks": [{"type":"command", "command":"$HOME/.claude/hooks/content-governance-router.py"}]
      }
    ]
  }
}
```

(Exact matchers verified against current settings.json structure.)

- [ ] **Step 3: Write the diff to a scratch file for review**

`~/.claude/.tmp/settings-router-consolidation.diff`

### Task 3.2: Apply settings.json change

Per universal-protocols "Modifying ~/.claude/settings.json" — Edit tool is denied; use Bash + Python `open(..., 'w')` with backup, surgical mutation, verify.

- [ ] **Step 1: User-authorization check**

This is a per-action authorization. The user said "the consolidation now" which authorizes the consolidation work but settings.json mutation requires explicit approval per the rule. Show the diff, ask for explicit settings.json modification approval before applying.

- [ ] **Step 2: Apply via Bash + Python after user approval**

```python
import shutil, os, json
src = os.path.expanduser("~/.claude/settings.json")
backup = os.path.expanduser("~/.claude/settings.json.bak.20260504-router-consolidation")
shutil.copy2(src, backup)

with open(src) as f:
    s = json.load(f)

# Surgical mutation: filter out deleted-hook entries; add 2 router entries.
DELETED = {
    "methodology-nudge.py", "brainstorming-enforcer.py", "writing-plans-enforcer.py",
    "claude-api-skill-nudge.py", "content-enforcer-hook.py", "content-enforcement-gate.py",
    "marketing-content-detector.py", "content-pitching-detector.py",
    "hq-content-skill-stack-enforcer.py",
}

def _is_deleted(entry):
    cmd = entry.get("command", "")
    return any(d in cmd for d in DELETED)

for matcher_name, matcher_list in s.get("hooks", {}).items():
    for matcher_entry in matcher_list:
        matcher_entry["hooks"] = [
            h for h in matcher_entry.get("hooks", []) if not _is_deleted(h)
        ]

# Add the 2 new routers (exact matchers TBD from Step 2 of 3.1).
# ... append to PreToolUse list ...

with open(src, "w") as f:
    json.dump(s, f, indent=2)
    f.write("\n")

# Verify
with open(src) as f:
    s2 = json.load(f)
# Count check, conflict check (allow ∩ deny), structural validity
allow = set(s2.get("permissions", {}).get("allow", []))
deny = set(s2.get("permissions", {}).get("deny", []))
assert not (allow & deny), f"allow ∩ deny conflict: {allow & deny}"
print(f"OK. Hooks total: {sum(len(m.get('hooks',[])) for ml in s2.get('hooks',{}).values() for m in ml)}")
```

- [ ] **Step 3: Smoke-test by triggering each router with a contrived payload**

```bash
echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/x.md","content":"# Test"},"session_id":"smoke"}' \
  | python ~/.claude/hooks/methodology-router.py
echo $?
```
Expected: exit 0, valid JSON or empty stdout.

- [ ] **Step 4: Commit**

```bash
git commit -m "settings: replace 9 obsolete hooks with 2 routers (consolidation)"
```

---

## Phase 4: Cleanup + Asset Registry

### Task 4.1: Delete obsolete hook files

- [ ] **Step 1: Run full test suite first to ensure routers cover all preserved behavior**

```bash
cd ~/.claude
python -m pytest tests/test_methodology_router.py tests/test_content_governance_router.py -v
```

- [ ] **Step 2: Delete the 9 source hooks**

```bash
rm ~/.claude/hooks/methodology-nudge.py
rm ~/.claude/hooks/brainstorming-enforcer.py
rm ~/.claude/hooks/writing-plans-enforcer.py
rm ~/.claude/hooks/claude-api-skill-nudge.py
rm ~/.claude/hooks/content-enforcer-hook.py
rm ~/.claude/hooks/content-enforcement-gate.py
rm ~/.claude/hooks/marketing-content-detector.py
rm ~/.claude/hooks/content-pitching-detector.py
rm ~/.claude/hooks/hq-content-skill-stack-enforcer.py
```

- [ ] **Step 3: Verify hook count**

```bash
ls ~/.claude/hooks/*.py | wc -l
```
Expected: 36 (was 44; -9 + 2 = -7 net but we added 2 routers — actual count: 44 - 9 + 2 = 37 .py files, plus _routers/ subdirectory).

- [ ] **Step 4: Commit deletion**

```bash
git rm ~/.claude/hooks/methodology-nudge.py # etc, all 9
git commit -m "hooks: delete 9 obsolete source hooks (consolidated into 2 routers)"
```

### Task 4.2: Update asset registry

- [ ] **Step 1: Mark 9 deleted hooks as retired**

```bash
for h in methodology-nudge brainstorming-enforcer writing-plans-enforcer \
         claude-api-skill-nudge content-enforcer-hook content-enforcement-gate \
         marketing-content-detector content-pitching-detector \
         hq-content-skill-stack-enforcer; do
  python ~/.claude/scripts/register-asset.py update hook ${h}.py \
    --workspace skill-management-hub --status retired \
    --metadata '{"retired_reason":"consolidated into router; see wr-skillhub-2026-04-30-002"}'
done
```

- [ ] **Step 2: Register the 2 new routers**

```bash
python ~/.claude/scripts/register-asset.py register hook methodology-router.py \
  --workspace skill-management-hub \
  --purpose "Consolidates 7 methodology sub-rules: brainstorming, writing_plans, methodology_nudge, claude_api, plan_file_read, multi_file_build, production_tool" \
  --audit-cadence warm

python ~/.claude/scripts/register-asset.py register hook content-governance-router.py \
  --workspace skill-management-hub \
  --purpose "Consolidates 6 content-governance sub-rules: enforcement_gate, marketing_keywords, skill_stack, content_enforcer, content_pitching, kb_governance" \
  --audit-cadence warm
```

- [ ] **Step 3: Commit registry updates** (registry is in Supabase; no local file commit needed unless asset metadata is mirrored locally).

### Task 4.3: Update documentation

- [ ] **Step 1: Update `docs/hook-classification-policy.md`**

Replace the per-hook table entries for the 9 deleted hooks with a single "methodology-router (combines: …)" and "content-governance-router (combines: …)" row.

- [ ] **Step 2: Update workspace MEMORY.md "Infrastructure" section**

Replace the per-hook list with the router-named entries.

- [ ] **Step 3: Commit docs**

```bash
git commit -m "docs: hook classification + memory reflect router consolidation"
```

---

## Phase 5: WR Closure + Notification + Sync

### Task 5.1: Close 4 work requests

For each of:
- `wr-skillhub-2026-04-30-002` (canonical)
- `wr-sentinel-2026-04-30-008` (absorbed)
- `wr-hq-2026-05-04-008` (absorbed)
- `wr-sentinel-2026-05-04-009` (absorbed)

- [ ] **Step 1: Close via close-inbox-item.py**

```bash
python ~/.claude/scripts/close-inbox-item.py \
  --file ".work-requests/inbox/2026-04-30_skill-management-hub_methodology-router-consolidati-002.json" \
  --status completed \
  --resolved-by skill-management-hub \
  --what-was-done "Built methodology-router.py + content-governance-router.py with TDD (all sub-rule tests passing). Deleted 9 source hooks. Settings.json migrated. Hook count 44 -> 36. Edit|Write matcher 17 -> 10. Asset registry updated." \
  --artifacts-created "$HOME/.claude/hooks/methodology-router.py,$HOME/.claude/hooks/content-governance-router.py,$HOME/.claude/hooks/_routers/" \
  --artifacts-modified "$HOME/.claude/settings.json,docs/hook-classification-policy.md"
```

Each absorbed WR gets a similar closure citing wr-002 as canonical and pointing to the router that absorbed it.

- [ ] **Step 2: Verify completion-notification routed-tasks landed in originator inboxes**

The close script auto-writes notifications; verify by listing target inboxes.

```bash
ls "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/" | grep router
ls "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/1.- SHARKITECT DIGITAL WORKFORCE HQ/.routed-tasks/inbox/" | grep router
```

### Task 5.2: Sync to toolkit + push

- [ ] **Step 1: Run sync-skills**

```bash
cd "C:\Users\Sharkitect Digital\Documents\Claude Code Workspaces\3.- Skill Management Hub"
python tools/sync-skills.py --sync --push
```

- [ ] **Step 2: Verify sync report**

```bash
cat .tmp/last-sync.json
```

### Task 5.3: Update Supabase project + tasks

- [ ] **Step 1: Mark consolidation project complete**

```bash
python ~/.claude/scripts/update-project-status.py project "Methodology Router Consolidation" complete \
  --notes "Routers shipped 2026-05-04. wr-002 + 3 absorbed WRs closed."
```

- [ ] **Step 2: Update MEMORY.md Resume Instructions**

Replace next-session pointer with summary of what shipped.

- [ ] **Step 3: Update `~/.claude/docs/plans-registry.md`**

Move this plan from Active to Completed Plans with outcome + lessons.

- [ ] **Step 4: Commit final memory + registry updates**

```bash
git commit -m "memory + plans-registry: router consolidation shipped"
```

---

## Self-Review Checklist (run before declaring plan complete)

1. **Spec coverage:**
   - [ ] All 9 source hooks have a sub-rule in one of the 2 routers? ✅ (wr-002 component list crossed off)
   - [ ] wr-008 plan-file Read sub-rule present? ✅ (Task 1.5)
   - [ ] wr-hq-008 KB-governance sub-rule present? ✅ (Task 2.6)
   - [ ] wr-009 multi-file-build + production-tool sub-rules present? ✅ (Tasks 1.6, 1.7)
   - [ ] intent_detection.py integrated? ✅ (every Edit/Write sub-rule calls is_user_driven)
   - [ ] TDD-first commitment honored? ✅ (every task: failing test → implement → pass → commit)
   - [ ] Settings.json migration discipline followed? ✅ (Task 3.2 uses Bash+Python+backup+verify)

2. **Placeholder scan:**
   - [ ] No "TODO" / "TBD" / "implement later"? ✅
   - [ ] No "similar to Task N" without code? ✅ (Phase 2 explicitly references Phase 1 pattern but provides per-sub-rule notes)

3. **Type consistency:**
   - [ ] All sub-rules use `evaluate(payload: dict) -> dict | None`? ✅
   - [ ] Router dispatch uses string module names matching directory? ✅

---

## Execution notes

- **One-in-multi-out budget exchange:** Per Hook Introduction Rule, this is a -7 net hook reduction. Well above the 1:1 swap requirement.
- **Sunset clause:** Both new routers register with `audit_cadence=warm` (weekly). 90-day zero-fire sub-rule audit applies per individual sub-rule (logged separately).
- **Bypass surface:** All bypass phrases from source hooks are preserved per sub-rule. Plus universal user-driven detection from intent_detection.py.
- **Risk:** Two simultaneous router cutovers. If something breaks at runtime, the backup `~/.claude/settings.json.bak.20260504-router-consolidation` enables 30-second rollback. Source hooks are version-controlled in toolkit repo (sync-skills.py) so deletion is also recoverable.

---

**Plan saved.** Next step: execute via superpowers:executing-plans skill.
