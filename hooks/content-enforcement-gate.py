"""
content-enforcement-gate.py - PreToolUse HARD BLOCK for HQ client content

Complements (does NOT replace) content-enforcer-hook.py (which nudges on
Write/Edit). This gate blocks SEND operations for client-facing content
when the required governance skills have not been invoked in the session.

Active only in WORKFORCE HQ workspace. Three enforcement layers:

  1. WARN on Write/Edit to client-facing content paths if hq-content-enforcer
     skill not invoked recently (soft warn, additionalContext).

  2. BLOCK on Bash commands that SEND content externally:
       - gws gmail +send / +forward
       - mailto, sendmail
       - twilio.* messages create (SMS)
       - curl/wget POSTing to non-sharkitectdigital.com
     until BOTH hq-content-enforcer AND hq-brand-review have been invoked
     in the current session.

  3. BYPASS path: Bash command containing the literal token
     "ALLOW_SEND_BYPASS=<reason>" gets through (logged for audit).

Reads ~/.claude/.tmp/skill-invocations-YYYY-MM-DD.json (written by
skill-invocation-tracker hook).

Pure stdlib. Input/output JSON via stdin/stdout.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


TMP_DIR = Path.home() / ".claude" / ".tmp"

# Required skills (any of the namespaced forms accepted)
SKILL_CONTENT_ENFORCER = "hq-content-enforcer"
SKILL_BRAND_REVIEW = "hq-brand-review"

CONTENT_PATH_HINTS = (
    "/deliverables/", "/content/", "/website/", "/marketing/",
    "/campaigns/", "/outreach/", "/copy/", "-draft", "_draft",
    "-body.html", "-body.txt", "_body.html", "_body.txt",
)
CONTENT_FILENAME_HINTS = (
    "landing", "email", "proposal", "form", "copy", "page", "post",
    "blog", "article", "social", "pitch", "script", "case-study",
    "newsletter", "announcement", "hero", "cta", "headline",
    "tagline", "ad", "brochure", "flyer", "sow",
)
CONTENT_EXTS = {".md", ".html", ".txt", ".mdx", ".htm", ".docx", ".eml"}

EXCLUDE_HINTS = (
    "/.tmp/", "/.claude/", "/tools/", "/workflows/", "/.git/",
    "/node_modules/", ".env", "package.json", "settings.json",
    "memory.md", "claude.md", "document-map.md", "index.md",
    "/inbox/", "/processed/", "/outbox/",
)

# Bash send-pattern regexes
SEND_PATTERNS = [
    re.compile(r"\bgws\s+gmail\s+\+(send|forward)\b", re.I),
    re.compile(r"\bsendmail\b", re.I),
    re.compile(r"\bmail\s+-s\s+", re.I),
    re.compile(r"\btwilio\b.*\bmessages\b.*\bcreate\b", re.I),
    re.compile(r"\bcurl\b.*\b-X\s+(POST|PUT)\b", re.I),
    re.compile(r"\bwget\b.*--post-(data|file)\b", re.I),
]

# Recipient exemption (sending to ourselves doesn't need review)
INTERNAL_RECIPIENT_RE = re.compile(r"@sharkitectdigital\.com\b", re.I)

BYPASS_RE = re.compile(r"ALLOW_SEND_BYPASS\s*=\s*(\S+)")


def is_hq_workspace():
    cwd = os.getcwd().replace("\\", "/").lower()
    return "workforce" in cwd and "hq" in cwd


def load_skill_log():
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = TMP_DIR / f"skill-invocations-{today}.json"
    if not log_path.exists():
        return []
    try:
        data = json.loads(log_path.read_text(encoding="utf-8"))
        return [str(rec.get("skill", "")).lower() for rec in data.get("invocations", [])]
    except (json.JSONDecodeError, OSError):
        return []


def skill_invoked(name, log):
    target = name.lower()
    return any(
        e == target or e.endswith(":" + target) or e.startswith(target + ":")
        for e in log
    )


def is_content_file(file_path):
    if not file_path:
        return False
    p = file_path.replace("\\", "/").lower()
    if any(h in p for h in EXCLUDE_HINTS):
        return False
    ext = os.path.splitext(p)[1]
    if ext not in CONTENT_EXTS:
        return False
    if any(h in p for h in CONTENT_PATH_HINTS):
        return True
    base = os.path.basename(p)
    if any(h in base for h in CONTENT_FILENAME_HINTS):
        return True
    return False


def is_external_send(cmd):
    """True if the Bash command appears to send content externally."""
    for pat in SEND_PATTERNS:
        if pat.search(cmd):
            # If recipients are all internal, allow
            recipients = re.findall(r"[\w.+-]+@[\w-]+\.[\w.-]+", cmd)
            if recipients and all(INTERNAL_RECIPIENT_RE.search(r) for r in recipients):
                return False
            return True
    return False


def deny(reason):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def warn(text):
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": text,
        }
    }))


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0

    if not is_hq_workspace():
        return 0

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {}) or {}
    if isinstance(tool_input, str):
        try:
            tool_input = json.loads(tool_input)
        except (json.JSONDecodeError, TypeError):
            tool_input = {}

    log = load_skill_log()
    enforcer_run = skill_invoked(SKILL_CONTENT_ENFORCER, log)
    brand_run = skill_invoked(SKILL_BRAND_REVIEW, log)

    # ---- Layer 1: warn on Write/Edit to client content (soft) ------------
    if tool_name in ("Write", "Edit"):
        file_path = str(tool_input.get("file_path", ""))
        if is_content_file(file_path):
            missing = []
            if not enforcer_run:
                missing.append("`hq-content-enforcer`")
            if not brand_run:
                missing.append("`hq-brand-review`")
            if missing:
                warn(
                    f"CLIENT-FACING CONTENT being written: {os.path.basename(file_path)}.\n"
                    f"Missing skill invocations this session: {', '.join(missing)}.\n"
                    "Invoke them BEFORE finalizing. The send-time gate will BLOCK external "
                    "delivery (gws gmail +send, twilio SMS, external POST) until both are run."
                )
        return 0

    # ---- Layer 2: HARD BLOCK on external send Bash commands --------------
    if tool_name == "Bash":
        cmd = str(tool_input.get("command", ""))

        # Bypass path
        bypass = BYPASS_RE.search(cmd)
        if bypass:
            # Allow but log to audit file
            audit_log = TMP_DIR / "content-gate-bypass-audit.log"
            try:
                TMP_DIR.mkdir(parents=True, exist_ok=True)
                with open(audit_log, "a", encoding="utf-8") as f:
                    f.write(json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "reason": bypass.group(1),
                        "cwd": os.getcwd(),
                        "cmd_snippet": cmd[:240],
                    }) + "\n")
            except OSError:
                pass
            return 0

        if not is_external_send(cmd):
            return 0

        missing = []
        if not enforcer_run:
            missing.append("`hq-content-enforcer`")
        if not brand_run:
            missing.append("`hq-brand-review`")
        if not missing:
            return 0

        deny(
            "BLOCKED: External send detected (client-facing content) but governance "
            f"skills not invoked this session: {', '.join(missing)}.\n\n"
            "REQUIRED before sending:\n"
            "  1. Invoke `hq-content-enforcer` to apply content rules + brand voice\n"
            "  2. Invoke `hq-brand-review` to score the staged content\n\n"
            "If this command is internal-only or a true edge case, append "
            "ALLOW_SEND_BYPASS=<short-reason> to the command (audit-logged to "
            "~/.claude/.tmp/content-gate-bypass-audit.log).\n\n"
            "Source: wr-2026-04-17-002. See docs/mandatory-skill-invocations.md."
        )
        return 0

    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
    sys.exit(0)
