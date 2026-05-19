"""Shared fixtures for UserPromptSubmit dispatcher + sub-rule tests."""
import json


def make_context(
    recent_tool_calls=None,
    active_plans=None,
    session_brief=None,
    workspace="skill-management-hub",
    bypass_phrases_in_prompt=None,
):
    """Build a context dict for sub-rule check() calls."""
    return {
        "recent_tool_calls": recent_tool_calls or [],
        "active_plans": active_plans or [],
        "session_brief": session_brief,
        "workspace": workspace,
        "bypass_phrases_in_prompt": bypass_phrases_in_prompt or [],
    }


def make_tool_call(name, args_summary="", ts="2026-05-18T12:00:00Z"):
    """Build a single recent tool call entry."""
    return {"name": name, "args_summary": args_summary, "ts": ts}


def write_dispatcher_config(tmp_path, enabled_subrules=None):
    """Write a dispatcher config JSON to a temp dir; return path."""
    cfg = {
        "enabled_subrules": enabled_subrules or ["sharkitect.verify_state"],
        "log_dir": str(tmp_path / "logs"),
    }
    cfg_path = tmp_path / "userpromptsubmit-dispatcher.json"
    cfg_path.write_text(json.dumps(cfg, indent=2))
    return cfg_path
