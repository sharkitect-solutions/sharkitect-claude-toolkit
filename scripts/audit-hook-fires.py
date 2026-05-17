"""
audit-hook-fires.py - Aggregate hook fires from log-hook-fire.py telemetry.

Filed by: wr-skillhub-2026-05-15-001 (Skill Hub). Companion CLI to
~/.claude/hooks/log-hook-fire.py. Enables the Hook Introduction Rule
sunset clause: identify hooks that fired zero times in the last N days
so they can be reviewed for retirement.

How it works:
  1. Read ~/.claude/.tmp/hook-fire-log.jsonl (one tool call per line).
  2. Read ~/.claude/settings.json to enumerate every registered hook
     and its matcher.
  3. For each tool call, infer which hooks WOULD have fired by matching
     the tool name against each hook's matcher (regex-aware).
  4. Aggregate fire counts per hook over a rolling window (default 90d).
  5. Output ranked table; flag zero-fire hooks as retirement candidates.

Inference caveat (documented honestly):
  A single PostToolUse hook cannot directly observe other hooks executing.
  We infer fires by joining tool calls to matcher rules. A hook that
  early-exits, denies, or has internal guards still counts as fired
  because the script DID execute. For "did this hook do anything in
  90 days?" (the Hook Introduction Rule question) inferred count is
  the right signal.

Usage:
  python ~/.claude/scripts/audit-hook-fires.py
  python ~/.claude/scripts/audit-hook-fires.py --window-days 30
  python ~/.claude/scripts/audit-hook-fires.py --zero-fire-only
  python ~/.claude/scripts/audit-hook-fires.py --json

Pure Python stdlib.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_FILE = Path.home() / ".claude" / ".tmp" / "hook-fire-log.jsonl"
SETTINGS_FILE = Path.home() / ".claude" / "settings.json"


def parse_iso(ts):
    """Parse ISO-8601 timestamp string -> aware datetime. Returns None on failure."""
    if not ts or not isinstance(ts, str):
        return None
    try:
        s = ts.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        return None


def load_settings():
    if not SETTINGS_FILE.exists():
        return {}
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def enumerate_hooks(settings):
    """
    Yield (event, matcher, hook_path) for every command hook registered
    in settings.json. Pulls hook_path out of the command string by best-
    effort regex.
    """
    cmd_path_re = re.compile(r'"([^"]+\.py)"')
    hooks_cfg = (settings or {}).get("hooks", {})
    for event, entries in hooks_cfg.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            matcher = entry.get("matcher", "*")
            for h in entry.get("hooks", []):
                cmd = h.get("command", "")
                m = cmd_path_re.search(cmd)
                if not m:
                    continue
                hook_path = m.group(1)
                yield event, matcher, hook_path


def matcher_to_regex(matcher):
    """
    Convert Claude Code matcher string to a regex that matches against a
    tool_name. Matcher syntax (per hook-development skill):
      "Write"          exact tool name
      "Write|Edit"     pipe-separated alternatives
      "*"              wildcard (all tools)
      "mcp__.*"        regex
    """
    if not matcher or matcher == "*":
        return re.compile(r".*")
    # Pipe-separated alternatives where each alternative is a regex itself.
    # Wrap each in non-capturing group and anchor to full match.
    alternatives = matcher.split("|")
    parts = []
    for alt in alternatives:
        alt = alt.strip()
        if not alt:
            continue
        # Treat as regex; matchers like "mcp__" need to match "mcp__anything".
        # If the matcher has no regex metachars, treat as prefix-or-exact:
        # the convention from the registry shows "mcp__" matches any MCP tool.
        if not any(c in alt for c in ".*+?[](){}|^$\\"):
            # Plain alternative: treat as prefix-or-exact match
            parts.append(re.escape(alt) + r".*")
        else:
            parts.append(alt)
    if not parts:
        return re.compile(r".*")
    pattern = r"^(?:" + "|".join(parts) + r")$"
    try:
        return re.compile(pattern)
    except re.error:
        # Bad regex -> match nothing (safer than match all)
        return re.compile(r"$.")


def event_is_visible_in_tool_call_log(event):
    """
    log-hook-fire is a PostToolUse * hook, so the log only contains tool
    calls. We can infer fires for PreToolUse and PostToolUse hooks (both
    trigger on the same tool_name). Other events (SessionStart,
    UserPromptSubmit, Stop, etc.) don't appear in the tool-call log and
    are reported as 'unknown' (?) fire count.
    """
    return event in ("PreToolUse", "PostToolUse")


def read_log_entries(window_start):
    """Yield log entries within [window_start, now]. Skips malformed lines."""
    if not LOG_FILE.exists():
        return
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except Exception:
                continue
            ts = parse_iso(entry.get("timestamp"))
            if not ts:
                continue
            if window_start and ts < window_start:
                continue
            yield entry


def audit(window_days):
    """
    Returns:
      hooks_summary: list of dicts {event, matcher, hook_path, inferred_fires, status}
      log_meta: dict {total_calls, window_start_iso, first_log_iso, last_log_iso}
    """
    window_start = None
    if window_days and window_days > 0:
        window_start = datetime.now(timezone.utc) - timedelta(days=window_days)

    settings = load_settings()
    registered = list(enumerate_hooks(settings))

    # Count tool calls in window and track log span
    total_calls = 0
    tool_call_records = []
    first_ts = None
    last_ts = None
    for entry in read_log_entries(window_start):
        total_calls += 1
        tool = entry.get("tool_name") or ""
        if not tool:
            continue
        tool_call_records.append(tool)
        ts = parse_iso(entry.get("timestamp"))
        if ts:
            if first_ts is None or ts < first_ts:
                first_ts = ts
            if last_ts is None or ts > last_ts:
                last_ts = ts

    # For each registered hook, count how many tool calls match its matcher.
    # Inference only valid for PreToolUse / PostToolUse events.
    summary = []
    for event, matcher, hook_path in registered:
        matcher_re = matcher_to_regex(matcher)
        if event_is_visible_in_tool_call_log(event):
            count = sum(1 for t in tool_call_records if matcher_re.match(t))
            inference_kind = "inferred-from-tool-calls"
        else:
            count = None  # Unknown -- event not visible in tool-call telemetry
            inference_kind = f"event={event}-not-visible"

        summary.append({
            "event": event,
            "matcher": matcher,
            "hook_path": hook_path,
            "inferred_fires": count,
            "inference_kind": inference_kind,
        })

    log_meta = {
        "total_tool_calls_in_window": total_calls,
        "window_days": window_days,
        "window_start_iso": window_start.isoformat().replace("+00:00", "Z") if window_start else None,
        "first_logged_iso": first_ts.isoformat().replace("+00:00", "Z") if first_ts else None,
        "last_logged_iso": last_ts.isoformat().replace("+00:00", "Z") if last_ts else None,
        "log_file": str(LOG_FILE),
        "log_exists": LOG_FILE.exists(),
    }
    return summary, log_meta


def render_table(summary, log_meta, zero_only=False):
    """Print human-readable report."""
    print("=" * 76)
    print("HOOK FIRE AUDIT")
    print("=" * 76)
    print(f"Log file: {log_meta['log_file']}")
    print(f"Log exists: {log_meta['log_exists']}")
    if log_meta["window_start_iso"]:
        print(f"Window: last {log_meta['window_days']} days "
              f"(since {log_meta['window_start_iso']})")
    else:
        print("Window: all-time")
    print(f"Total tool calls in window: {log_meta['total_tool_calls_in_window']}")
    if log_meta["first_logged_iso"]:
        print(f"First log entry: {log_meta['first_logged_iso']}")
        print(f"Last log entry:  {log_meta['last_logged_iso']}")
    print()

    rows = summary
    if zero_only:
        rows = [r for r in summary if r["inferred_fires"] == 0]

    # Sort: visible+zero first, then visible by fire count ascending, then unknown
    def sort_key(r):
        fires = r["inferred_fires"]
        if fires is None:
            return (2, 0, r["hook_path"])
        return (0 if fires == 0 else 1, fires, r["hook_path"])

    rows.sort(key=sort_key)

    print(f"{'EVENT':<18} {'MATCHER':<28} {'FIRES':>8}  HOOK")
    print("-" * 76)
    zero_count = 0
    unknown_count = 0
    for r in rows:
        fires = r["inferred_fires"]
        if fires is None:
            fires_s = "?"
            unknown_count += 1
        else:
            fires_s = str(fires)
            if fires == 0:
                zero_count += 1
        hp = r["hook_path"]
        # Trim very long paths to last 2 segments
        parts = hp.replace("\\", "/").split("/")
        hp_short = "/".join(parts[-2:]) if len(parts) > 2 else hp
        print(f"{r['event']:<18} {r['matcher']:<28} {fires_s:>8}  {hp_short}")

    print()
    print(f"Zero-fire hooks (in window): {zero_count}")
    print(f"Unknown (event not visible in tool-call telemetry): {unknown_count}")
    if log_meta["total_tool_calls_in_window"] == 0:
        print()
        print("NOTE: log is empty (cold-start). Zero-fire counts are not yet")
        print("      actionable. The Hook Introduction Rule sunset clause uses")
        print("      a 90-day window; let telemetry accrue before retiring.")


def main():
    ap = argparse.ArgumentParser(
        description="Aggregate hook fires from log-hook-fire.py telemetry; "
                    "identify zero-fire hook retirement candidates per the "
                    "Hook Introduction Rule sunset clause.")
    ap.add_argument("--window-days", type=int, default=90,
                    help="Rolling window in days (default: 90; per Hook "
                         "Introduction Rule sunset clause). Use 0 for all-time.")
    ap.add_argument("--zero-fire-only", action="store_true",
                    help="Show only hooks with zero fires in the window.")
    ap.add_argument("--json", action="store_true",
                    help="Emit JSON instead of human-readable table.")
    args = ap.parse_args()

    window = args.window_days if args.window_days > 0 else 0
    summary, log_meta = audit(window)

    if args.json:
        out = {"meta": log_meta, "hooks": summary}
        print(json.dumps(out, indent=2, default=str))
        return 0

    rows = summary
    if args.zero_fire_only:
        rows = [r for r in summary if r["inferred_fires"] == 0]
    render_table(rows if args.zero_fire_only else summary, log_meta,
                 zero_only=args.zero_fire_only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
