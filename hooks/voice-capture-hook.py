"""voice-capture-hook.py -- automated voice signal capture (UserPromptSubmit).

Filed by:
  - wr-sentinel-2026-05-04-005 (warning, structural autonomy gap).

What it does
============
Fires on every UserPromptSubmit. Pattern-matches the user's prompt for voice
signals (corrections, preferences, approvals) and writes them silently to
the voice-capture log + activity_stream via voice-write.py.

User direction (verbatim, 2026-05-04):
  "Even though I am not telling you, it should be updating. Every time we
  work, every time we do anything, every time we write emails or any
  communications, those should be captured, even if I am not telling you."

Signal categories
=================
  correction  -- explicit corrective phrases ("no, that's not", "don't do",
                 "stop doing", "wrong", "fix this", "never X")
  preference  -- preference / rather statements ("I prefer", "I'd rather",
                 "more like", "I don't like", "I want X instead")
  approval    -- positive confirmation of recent AI behavior ("perfect",
                 "exactly right", "keep doing that", "yes that's it")

False-positive guards
=====================
  - Slash commands skipped (start with '/')
  - Prompts <= 2 words skipped (too short to be feedback)
  - Patterns inside fenced code blocks (```...```) ignored
  - Patterns inside quotes (single, double, backtick) ignored at the line level
  - Same prompt in same session deduped via hash cache

Output behavior
===============
  - SILENT. Hook never emits additionalContext (per user direction).
  - Logs to <home>/.claude/.tmp/voice-capture-log.jsonl
  - Fires fire-and-forget subprocess to voice-write.py correction (background)
  - VOICE_CAPTURE_DRY_RUN=1 in env disables the subprocess (used by tests)

Hook budget impact
==================
  +1 to UserPromptSubmit:* matcher (was 3, now 4; cap is 6). No swap needed.
  Per Hook Introduction Rule 2026-04-27 (universal-protocols.md).

Sunset clause
=============
  90-day zero-fire review per Hook Introduction Rule. Logged via
  cron-activity-logger.py (PostToolUse:* matcher).
"""

import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Config ──────────────────────────────────────────────────────────

MIN_WORDS = 3
LOG_FILENAME = "voice-capture-log.jsonl"
DEDUP_FILENAME = "voice-capture-dedup.json"
DEDUP_MAX_ENTRIES = 200  # cap to avoid unbounded growth

# Continuous raw-sample stream (Continuous Voice & Preference Learning Protocol).
# Every user message that passes filters lands here as a raw sample for
# dream-consolidation pattern distillation. Source: 2026-05-06 user direction
# expanding the protocol from reactive-only to continuous.
RAW_SAMPLES_FILENAME = "voice-samples-raw.jsonl"
RAW_SAMPLES_DEDUP_FILENAME = "voice-samples-raw-dedup.json"
RAW_SAMPLES_DEDUP_MAX_ENTRIES = 500  # higher than feedback dedup -- more turns
RAW_SAMPLES_MAX_LEN = 8000  # truncate longer prompts to bound storage


# Pattern lists. Each entry is (regex, category). Word-boundary anchored.
# Patterns chosen for unambiguous-feedback context. Deliberately conservative;
# v2 may add LLM-based extraction for richer signal.
CORRECTION_PATTERNS = [
    r"\bno,?\s+(that'?s\s+not|that\s+is\s+not|that's\s+wrong|not\s+(?:what|how)|don'?t)",
    r"\bdon'?t\s+(do|use|say|write|add|include|put|call)\b",
    r"\bstop\s+(doing|using|writing|adding|saying|calling)\b",
    r"\bnever\s+(use|do|say|write|add|include|put|call)\b",
    r"\bthat'?s\s+wrong\b",
    r"\bthat\s+is\s+wrong\b",
    r"\bnot\s+(what|how)\s+i\s+(meant|wanted|want|asked)",
    r"\bfix\s+(this|that)\b",
    r"\bremove\s+(the|that|this|all)\b",
    r"\bbe\s+more\s+(direct|brief|concise|specific|casual|formal)",
    r"\btoo\s+(formal|casual|generic|wordy|verbose|long|short|technical|fluffy)",
]

PREFERENCE_PATTERNS = [
    r"\bi\s+prefer\s+\w+",
    r"\bi'?d\s+rather\s+\w+",
    r"\bi\s+don'?t\s+like\s+(how|the|that|this)",
    r"\bi\s+want\s+(it|that|this)\s+(more|less|to\s+be)",
    r"\bmore\s+like\s+(how|the\s+way|what)",
    r"\binstead\s+of\b",
    r"\brather\s+than\b",
]

APPROVAL_PATTERNS = [
    r"\bperfect[,!.\s]",
    r"\bexactly\s+(right|like|that|what)\b",
    r"\byes,?\s+(exactly|that'?s|keep|perfect)",
    r"\bkeep\s+doing\s+(that|this|it)",
    r"\bthat'?s\s+(it|right|exactly|perfect|the\s+(?:way|tone))",
    r"\bnailed\s+it\b",
]

CATEGORIES = [
    ("correction", CORRECTION_PATTERNS),
    ("preference", PREFERENCE_PATTERNS),
    ("approval", APPROVAL_PATTERNS),
]


# ── Public detection API ────────────────────────────────────────────

def _strip_codeblocks_and_quotes(text: str) -> str:
    """Remove fenced code blocks and quoted strings from a prompt before
    pattern matching, so quoted patterns (e.g. discussing a phrase rather
    than using it as feedback) don't trigger.

    Only strips double-quoted spans and backtick-fenced code. Single quotes
    are too commonly contractions ("don't", "I'd", "that's") to strip safely.
    """
    if not text:
        return ""
    # Fenced code blocks (```...```)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    # Inline backticks (`...`)
    text = re.sub(r"`[^`\n]*`", "", text)
    # Double-quoted phrases ("...")
    text = re.sub(r'"[^"\n]*"', "", text)
    return text


def detect_signals(prompt: str):
    """Return a list of detected voice signals.

    Each signal: {"category": str, "matched_phrase": str}

    Returns [] if prompt is too short, slash-command, or no patterns match.
    Caps at one match per category (no spam).
    """
    if not prompt:
        return []
    p = prompt.strip()
    if not p:
        return []
    if p.startswith("/"):
        return []
    if len(p.split()) < MIN_WORDS:
        return []

    cleaned = _strip_codeblocks_and_quotes(p).lower()
    if not cleaned.strip():
        return []

    out = []
    for category, patterns in CATEGORIES:
        for pat in patterns:
            m = re.search(pat, cleaned, flags=re.IGNORECASE)
            if m:
                out.append({
                    "category": category,
                    "matched_phrase": m.group(0).strip(),
                })
                break  # one per category
    return out


# ── Persistence ─────────────────────────────────────────────────────

def _tmp_dir() -> Path:
    home = Path(os.environ.get("HOME") or os.environ.get("USERPROFILE") or str(Path.home()))
    d = home / ".claude" / ".tmp"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def _load_dedup() -> dict:
    path = _tmp_dir() / DEDUP_FILENAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_dedup(d: dict) -> None:
    path = _tmp_dir() / DEDUP_FILENAME
    if len(d) > DEDUP_MAX_ENTRIES:
        items = sorted(d.items(), key=lambda kv: kv[1].get("ts", ""))
        d = dict(items[-DEDUP_MAX_ENTRIES:])
    try:
        path.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


def _is_dup(prompt_hash: str, session_id: str) -> bool:
    d = _load_dedup()
    key = f"{session_id}:{prompt_hash}"
    return key in d


def _mark_seen(prompt_hash: str, session_id: str) -> None:
    d = _load_dedup()
    key = f"{session_id}:{prompt_hash}"
    d[key] = {"ts": _now_iso()}
    _save_dedup(d)


def _log_capture(entry: dict) -> None:
    path = _tmp_dir() / LOG_FILENAME
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


# ── Continuous raw-sample stream ─────────────────────────────────────
# Source: 2026-05-06 user direction expanding Continuous Voice & Preference
# Learning Protocol from reactive-only to continuous. Every user message
# that passes filters lands here as a raw sample for dream-consolidation
# pattern distillation (sentence rhythm, word choice, formality, etc.).

def _load_raw_dedup() -> dict:
    path = _tmp_dir() / RAW_SAMPLES_DEDUP_FILENAME
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_raw_dedup(d: dict) -> None:
    path = _tmp_dir() / RAW_SAMPLES_DEDUP_FILENAME
    if len(d) > RAW_SAMPLES_DEDUP_MAX_ENTRIES:
        items = sorted(d.items(), key=lambda kv: kv[1].get("ts", ""))
        d = dict(items[-RAW_SAMPLES_DEDUP_MAX_ENTRIES:])
    try:
        path.write_text(json.dumps(d), encoding="utf-8")
    except Exception:
        pass


def _is_raw_dup(prompt_hash: str, session_id: str) -> bool:
    d = _load_raw_dedup()
    return f"{session_id}:{prompt_hash}" in d


def _mark_raw_seen(prompt_hash: str, session_id: str) -> None:
    d = _load_raw_dedup()
    d[f"{session_id}:{prompt_hash}"] = {"ts": _now_iso()}
    _save_raw_dedup(d)


def _should_capture_raw(prompt: str) -> bool:
    """Same filters as feedback capture: skip slash commands and <MIN_WORDS.
    Empty/whitespace prompts are skipped as well."""
    if not prompt:
        return False
    p = prompt.strip()
    if not p:
        return False
    if p.startswith("/"):
        return False
    if len(p.split()) < MIN_WORDS:
        return False
    return True


def _log_raw_sample(entry: dict) -> None:
    path = _tmp_dir() / RAW_SAMPLES_FILENAME
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass


def _capture_raw_sample(prompt: str, session_id: str, workspace: str) -> None:
    """Append a raw voice sample for the user's message. Continuous-capture
    mandate of the Continuous Voice & Preference Learning Protocol. Silent
    fail-open. Truncates long prompts; dedups within session."""
    if not _should_capture_raw(prompt):
        return

    h = _prompt_hash(prompt)
    if _is_raw_dup(h, session_id):
        return

    text = prompt.strip()
    truncated = False
    if len(text) > RAW_SAMPLES_MAX_LEN:
        text = text[:RAW_SAMPLES_MAX_LEN] + "..."
        truncated = True

    word_count = len(prompt.split())
    char_count = len(prompt)

    entry = {
        "ts": _now_iso(),
        "session_id": session_id,
        "workspace": workspace,
        "prompt_hash": h,
        "word_count": word_count,
        "char_count": char_count,
        "truncated": truncated,
        "text": text,
    }
    _log_raw_sample(entry)
    _mark_raw_seen(h, session_id)


def _detect_workspace_canonical() -> str:
    """Best-effort detection of canonical workspace name from CWD."""
    s = os.getcwd().replace("\\", "/").lower()
    if "/3.- skill management hub" in s or "/3.-" in s:
        return "skill-management-hub"
    if ("workforce" in s and "hq" in s) or "/1.-" in s:
        return "workforce-hq"
    if "sentinel" in s or "/4.-" in s:
        return "sentinel"
    return "unknown"


def _fire_voice_write_correction(description: str, workspace: str) -> None:
    """Fire-and-forget subprocess to voice-write.py correction. Never blocks."""
    if os.environ.get("VOICE_CAPTURE_DRY_RUN") == "1":
        return
    home = Path(os.environ.get("HOME") or os.environ.get("USERPROFILE") or str(Path.home()))
    script = home / ".claude" / "scripts" / "voice-write.py"
    if not script.exists():
        return
    try:
        creationflags = 0x00000008 if os.name == "nt" else 0  # DETACHED_PROCESS
        subprocess.Popen(
            [sys.executable, str(script), "correction", description, "--workspace", workspace],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=creationflags,
        )
    except Exception:
        pass


# ── Main ────────────────────────────────────────────────────────────

def main() -> int:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return 0
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return 0  # Bad input: fail open, silent

        prompt = payload.get("prompt") or ""
        session_id = (payload.get("session_id") or "default")[:64]
        workspace = _detect_workspace_canonical()

        # CONTINUOUS RAW-SAMPLE CAPTURE (Continuous Voice & Preference Learning
        # Protocol). Runs on EVERY UserPromptSubmit before pattern matching --
        # every prompt is a voice sample regardless of whether explicit feedback
        # patterns match. Silent + fail-open + dedup'd separately from feedback.
        try:
            _capture_raw_sample(prompt, session_id, workspace)
        except Exception:
            pass  # never let raw-capture failures block feedback capture

        signals = detect_signals(prompt)
        if not signals:
            return 0

        h = _prompt_hash(prompt)
        if _is_dup(h, session_id):
            return 0

        cats = sorted(set(s["category"] for s in signals))
        sample_phrase = signals[0]["matched_phrase"]
        snippet = prompt.strip()
        if len(snippet) > 240:
            snippet = snippet[:237] + "..."
        description = (
            f"Voice signal auto-captured ({'+'.join(cats)}): "
            f"matched '{sample_phrase}'. Prompt: {snippet}"
        )

        _log_capture({
            "ts": _now_iso(),
            "session_id": session_id,
            "workspace": workspace,
            "prompt_hash": h,
            "signals": signals,
            "description": description,
        })

        _mark_seen(h, session_id)
        _fire_voice_write_correction(description, workspace)

    except Exception:
        return 0

    return 0  # silent: no stdout output


if __name__ == "__main__":
    sys.exit(main())
