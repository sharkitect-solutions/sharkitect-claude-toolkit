"""
stale-pointer-nudge.py - PostToolUse Read advisory for skill-ref companions.

Fires on Read of files matching ~/.claude/skills/**/references/*.md.
Scans for citations to K1 SoT paths. If a cited K1 SoT has status: SUPERSEDED
(or its file is missing), injects an additionalContext nudge asking the AI to
follow the superseded_by pointer or refresh the reference.

NOT a transparent redirect (per Alt 5 design choice). Advisory only.

Bypass: include 'skip stale-pointer' in the read content or current user message.

Pure stdlib. ASCII-only.
"""
from __future__ import annotations

import fnmatch
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace


SKILL_REF_GLOB = "*/.claude/skills/*/references/*.md"
BYPASS_PHRASE = "skip stale-pointer"
# Two patterns to find K1-style path citations:
# 1. Backtick-delimited: captures full paths including spaces (Windows absolute paths)
# 2. Unquoted relative: captures relative knowledge-base/... paths (no spaces)
_BACKTICK_RE = re.compile(r"`([^`]*knowledge-base[^`]*\.md)`")
_RELATIVE_RE = re.compile(r"(?<![`\w/\\])knowledge-base[/\\][A-Za-z0-9_./\\-]+\.md")


def _normalize(p: str) -> str:
    return p.replace("\\", "/").lower()


def _is_skill_ref(path: str) -> bool:
    norm = _normalize(path)
    # fnmatch on the normalized path against the normalized glob
    return fnmatch.fnmatch(norm, SKILL_REF_GLOB)


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


def _check_citation(cited_path: str, search_root: Path) -> str | None:
    """Return a finding string if cited path is superseded or missing; else None."""
    candidate = Path(cited_path)
    if not candidate.is_absolute():
        candidate = search_root / cited_path
    if not candidate.exists():
        return f"cited K1 path not found: {cited_path}"
    try:
        fm = _parse_frontmatter(candidate.read_text(encoding="utf-8"))
    except OSError:
        return None
    if fm.get("status", "").lower() == "superseded":
        sb = fm.get("superseded_by", "<unknown>")
        return f"cited K1 `{cited_path}` is SUPERSEDED; follow pointer to `{sb}`"
    return None


def evaluate(payload: dict, k1_search_root: Path | None = None) -> SimpleNamespace:
    if payload.get("tool_name") != "Read":
        return SimpleNamespace(additional_context=None)
    file_path = payload.get("tool_input", {}).get("file_path", "")
    if not _is_skill_ref(file_path):
        return SimpleNamespace(additional_context=None)
    try:
        text = Path(file_path).read_text(encoding="utf-8")
    except OSError:
        return SimpleNamespace(additional_context=None)
    if BYPASS_PHRASE in text.lower():
        return SimpleNamespace(additional_context=None)
    root = k1_search_root or Path.cwd()
    findings = []
    seen: set[str] = set()
    # Pattern 1: backtick-delimited paths (captures spaces, absolute paths)
    for m in _BACKTICK_RE.finditer(text):
        cited = m.group(1)
        if cited not in seen:
            seen.add(cited)
            f = _check_citation(cited, root)
            if f:
                findings.append(f)
    # Pattern 2: unquoted relative knowledge-base/... paths
    for m in _RELATIVE_RE.finditer(text):
        cited = m.group(0)
        if cited not in seen:
            seen.add(cited)
            f = _check_citation(cited, root)
            if f:
                findings.append(f)
    if not findings:
        return SimpleNamespace(additional_context=None)
    msg = (
        "[stale-pointer-nudge] Skill-ref companion being read has citations to K1 SoTs "
        "that need attention:\n  - " + "\n  - ".join(findings)
        + "\nFollow the superseded_by pointer or refresh the reference per "
        "SoT-Reference Discipline (universal-protocols.md)."
    )
    return SimpleNamespace(additional_context=msg)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    result = evaluate(payload)
    if result.additional_context:
        print(json.dumps({"additionalContext": result.additional_context}))
    sys.exit(0)


if __name__ == "__main__":
    main()
