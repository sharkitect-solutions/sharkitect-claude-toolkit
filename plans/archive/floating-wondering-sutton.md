# Plan: Smart Two-Tier Line Count Hook (v2)

## Context

After analyzing the AIOS Builder CLAUDE.md (2,178 lines), the picture is clear:

CLAUDE.md has a **two-state lifecycle**:
- **Bootstrap Mode** — verbose build guide, can be 700-2,200+ lines. Intentional. Needed during setup.
- **Runtime Mode** — lean 87-150 line pointer file. Activated after setup completes.

The hook should respect this lifecycle, not fight it. An 800-line hard limit would break the AIOS Builder template. But NO limit would allow bloated runtime files.

**Practical constraint:** CLAUDE.md is loaded into context EVERY session. A 2,178-line file (~27K tokens) eats context during setup — acceptable because you need the instructions. During daily runtime — wasteful, those tokens should be available for actual work.

## Design: Mode-Aware Hook

### Detection: Is this Bootstrap or Runtime?

Simple heuristic — check if the file contains bootstrap blueprint markers:
- If the file contains `## Section 7: Bootstrap Tool` OR `/Instantiate` OR `Bootstrap Mode` → it's a bootstrap template
- If not → it's a runtime file or normal project file

### Tier 1: MEMORY.md — Hard block at 150 lines
Same as current. No exceptions. Shrinking edits always allowed.

### Tier 2: CLAUDE.md — Mode-dependent

| Mode | Detected By | Soft Warning | Hard Limit |
|------|------------|-------------|-----------|
| **Bootstrap** | Contains bootstrap markers | 1500 lines | 2500 lines |
| **Runtime** | No bootstrap markers | 150 lines | 250 lines |

**Bootstrap mode (template/setup):**
- Soft warn at 1500 lines ("Bootstrap CLAUDE.md is getting large. Consider externalizing to /references/")
- Hard block at 2500 lines ("Even bootstrap mode shouldn't exceed 2500 lines")

**Runtime mode (daily operation):**
- Soft warn at 150 lines ("Runtime CLAUDE.md should be 87-150 lines per AIOS spec")
- Hard block at 250 lines ("Runtime CLAUDE.md is too large. Compress or externalize content.")

### How mode detection works in the hook:

```python
def detect_claude_mode(file_path):
    """Detect if CLAUDE.md is in Bootstrap or Runtime mode."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Read first 5000 chars — enough to find markers without reading the whole file
            head = f.read(5000).lower()
    except (OSError, UnicodeDecodeError):
        return "runtime"  # Default to stricter mode if unreadable
    
    bootstrap_markers = [
        "bootstrap mode",
        "section 7: bootstrap tool",
        "/instantiate",
        "instantiation blueprint",
    ]
    for marker in bootstrap_markers:
        if marker in head:
            return "bootstrap"
    return "runtime"
```

## Critical File

`C:\Users\Sharkitect Digital\.claude\hooks\check-line-count.py`

## Full Implementation

```python
"""
check-line-count.py - PreToolUse hook for MEMORY.md and CLAUDE.md line limits

Two-tier, mode-aware protection:
  MEMORY.md: Hard block at 150 lines. No exceptions.
  CLAUDE.md: Mode-dependent limits.
    - Bootstrap mode (setup templates): soft warn 1500, hard block 2500
    - Runtime mode (daily operation): soft warn 150, hard block 250

Content-aware: Write checks new content, Edit calculates net change.
Shrinking edits ALWAYS allowed on over-limit files.
"""

import json
import sys


MEMORY_HARD_LIMIT = 150

CLAUDE_LIMITS = {
    "bootstrap": {"soft": 1500, "hard": 2500},
    "runtime":   {"soft": 150,  "hard": 250},
}

BOOTSTRAP_MARKERS = [
    "bootstrap mode",
    "section 7: bootstrap tool",
    "/instantiate",
    "instantiation blueprint",
]


def normalize_path(path):
    return path.replace("\\", "/")


def count_lines(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        return 0


def count_content_lines(content):
    if not content:
        return 0
    return content.count("\n") + (1 if not content.endswith("\n") else 0)


def detect_claude_mode(file_path, new_content=None):
    """Detect if CLAUDE.md is in Bootstrap or Runtime mode.
    Checks new_content first (for Write), falls back to existing file."""
    text = ""
    if new_content:
        text = new_content[:5000].lower()
    else:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read(5000).lower()
        except (OSError, UnicodeDecodeError):
            pass

    for marker in BOOTSTRAP_MARKERS:
        if marker in text:
            return "bootstrap"
    return "runtime"


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    norm = normalize_path(file_path)
    basename = norm.rsplit("/", 1)[-1] if "/" in norm else norm

    if basename not in ("MEMORY.md", "CLAUDE.md"):
        sys.exit(0)

    current_lines = count_lines(file_path)
    new_content = tool_input.get("content", "") if tool_name == "Write" else None

    # Calculate projected line count
    if tool_name == "Write":
        projected = count_content_lines(new_content)
    elif tool_name == "Edit":
        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")
        net_change = new_string.count("\n") - old_string.count("\n")
        projected = current_lines + net_change
        if net_change <= 0:
            sys.exit(0)  # Shrinking edits always allowed
    else:
        sys.exit(0)

    # --- MEMORY.md: simple hard block ---
    if basename == "MEMORY.md":
        if projected >= MEMORY_HARD_LIMIT:
            print(
                f"BLOCKED: {basename} would be {projected} lines "
                f"(limit: {MEMORY_HARD_LIMIT}). "
                f"Move content to topic files or Supabase.",
                file=sys.stderr,
            )
            sys.exit(2)
        sys.exit(0)

    # --- CLAUDE.md: mode-dependent ---
    mode = detect_claude_mode(file_path, new_content)
    limits = CLAUDE_LIMITS[mode]

    if projected >= limits["hard"]:
        print(
            f"BLOCKED: CLAUDE.md ({mode} mode) would be {projected} lines "
            f"(hard limit: {limits['hard']}). "
            f"{'Externalize content to /references/ or /context/.' if mode == 'bootstrap' else 'Compress to runtime mode or externalize content.'}",
            file=sys.stderr,
        )
        sys.exit(2)

    if projected >= limits["soft"]:
        print(
            f"WARNING: CLAUDE.md ({mode} mode) will be {projected} lines "
            f"(soft limit: {limits['soft']}, hard limit: {limits['hard']}). "
            f"{'Bootstrap templates can be large, but consider externalizing if possible.' if mode == 'bootstrap' else 'Runtime CLAUDE.md should be 87-150 lines per AIOS spec. Consider compressing.'}"
        )
        sys.exit(0)  # Warn but allow

    sys.exit(0)


if __name__ == "__main__":
    main()
```

## Behavior Matrix

| File | Mode | Lines | Result |
|------|------|-------|--------|
| MEMORY.md | — | < 150 | Allow |
| MEMORY.md | — | >= 150 (growing) | **HARD BLOCK** |
| MEMORY.md | — | >= 150 (shrinking) | Allow |
| CLAUDE.md | Bootstrap | < 1500 | Allow |
| CLAUDE.md | Bootstrap | 1500-2499 | **SOFT WARN** |
| CLAUDE.md | Bootstrap | >= 2500 | **HARD BLOCK** |
| CLAUDE.md | Runtime | < 150 | Allow |
| CLAUDE.md | Runtime | 150-249 | **SOFT WARN** |
| CLAUDE.md | Runtime | >= 250 | **HARD BLOCK** |
| Other files | — | Any | Allow |

## Verification

1. Write MEMORY.md 160 lines → HARD BLOCK
2. Shrinking edit on 155-line MEMORY.md → ALLOW
3. Write bootstrap CLAUDE.md 730 lines → ALLOW (under 1500 soft)
4. Write bootstrap CLAUDE.md 2178 lines → SOFT WARN (between 1500-2500)
5. Write bootstrap CLAUDE.md 2600 lines → HARD BLOCK
6. Write runtime CLAUDE.md 100 lines → ALLOW
7. Write runtime CLAUDE.md 200 lines → SOFT WARN
8. Write runtime CLAUDE.md 300 lines → HARD BLOCK
