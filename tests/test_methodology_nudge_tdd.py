"""Tests for the TDD pattern detection in methodology-nudge.py.

Source: wr-skillhub-2026-04-29-001 -- multi-file deliverable + test edits
without superpowers:test-driven-development invocation should nudge once
per session on the threshold-crossing edit.

Detection rules under test:
  - 2+ distinct deliverable files + 1+ test files = nudge
  - Test files classified by name pattern (test_*, *_test, *.test.*, *.spec.*)
  - Deliverable = code extension (.py/.js/.ts/etc.) AND not a test
  - Skip if TDD skill already invoked (skill log entry)
  - Fire once per session (already_nudged debounce)
  - Excluded paths bypass entirely (.tmp/, /processed/, /inbox/, etc.)
"""

import importlib.util
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


HOOK = Path.home() / ".claude" / "hooks" / "methodology-nudge.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("mn", str(HOOK))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run_hook(stdin_obj, tmp_state_dir, skill_log_entries=None):
    """Run methodology-nudge.py as subprocess with isolated state + skill log dirs.

    Uses HOME override so the hook reads/writes state under tmp_state_dir/.claude/.tmp.
    Returns (stdout, stderr, returncode).
    """
    tmp_dir = tmp_state_dir / ".claude" / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Pre-seed skill invocation log if requested
    if skill_log_entries:
        today = datetime.now().strftime("%Y-%m-%d")
        log_path = tmp_dir / f"skill-invocations-{today}.json"
        log_path.write_text(json.dumps({
            "invocations": [{"skill": s} for s in skill_log_entries]
        }), encoding="utf-8")

    env = {
        "HOME": str(tmp_state_dir),
        "USERPROFILE": str(tmp_state_dir),  # Windows
        "PATH": __import__("os").environ.get("PATH", ""),
    }
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(stdin_obj),
        capture_output=True,
        text=True,
        env=env,
    )
    return result.stdout, result.stderr, result.returncode


def _parse_nudge(stdout):
    """Return additionalContext text from hook stdout, or '' if no nudge."""
    if not stdout.strip():
        return ""
    try:
        out = json.loads(stdout)
    except json.JSONDecodeError:
        return ""
    return out.get("hookSpecificOutput", {}).get("additionalContext", "") or ""


# ---- Direct unit tests of the regex classifiers ----------------------------

def test_test_file_re_matches_common_patterns():
    mn = _load_hook_module()
    cases = [
        "src/test_foo.py",
        "tests/test_bar.py",
        "lib/foo_test.go",
        "client/foo.test.ts",
        "client/foo.spec.tsx",
        "frontend/__tests__/Component.tsx",
    ]
    for path in cases:
        assert mn.TEST_FILE_RE.search(path), f"expected test match for {path}"


def test_test_file_re_rejects_non_tests():
    mn = _load_hook_module()
    cases = [
        "src/foo.py",
        "lib/handler.go",
        "client/Component.tsx",
        "scripts/contest_runner.py",  # 'test' substring but not test pattern
    ]
    for path in cases:
        assert not mn.TEST_FILE_RE.search(path), f"unexpected test match for {path}"


def test_deliverable_ext_re_matches_code_only():
    mn = _load_hook_module()
    yes = ["src/foo.py", "lib/handler.go", "x.ts", "x.jsx", "x.rb", "x.sh"]
    no = ["README.md", "data.json", "config.yaml", "notes.txt", "diagram.png"]
    for path in yes:
        assert mn.DELIVERABLE_EXT_RE.search(path), f"expected deliverable for {path}"
    for path in no:
        assert not mn.DELIVERABLE_EXT_RE.search(path), f"unexpected deliverable for {path}"


# ---- Integration tests via subprocess --------------------------------------

def _write_input(tool, file_path, content="x"):
    return {
        "tool_name": tool,
        "tool_input": {"file_path": file_path, "content": content},
    }


def test_no_nudge_on_first_deliverable_alone(tmp_path):
    """Single deliverable file, no tests yet -- no nudge."""
    out, _, rc = _run_hook(_write_input("Write", "/p/src/foo.py"), tmp_path)
    assert rc == 0
    assert "TDD PATTERN" not in _parse_nudge(out)


def test_no_nudge_with_only_tests(tmp_path):
    """Only test files touched, no deliverables -- no nudge."""
    _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/tests/test_b.py"), tmp_path)
    assert "TDD PATTERN" not in _parse_nudge(out)


def test_no_nudge_with_two_deliverables_no_tests(tmp_path):
    """2 deliverables but no test file touched -- no nudge."""
    _run_hook(_write_input("Write", "/p/src/a.py"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/src/b.py"), tmp_path)
    assert "TDD PATTERN" not in _parse_nudge(out)


def test_nudge_fires_when_threshold_crosses(tmp_path):
    """deliv1 + test1 + deliv2 -> nudge fires on the deliv2 edit."""
    _run_hook(_write_input("Write", "/p/src/a.py"), tmp_path)
    _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/src/b.py"), tmp_path)
    nudge = _parse_nudge(out)
    assert "TDD PATTERN" in nudge
    assert "deliverable file(s)" in nudge
    assert "test-driven-development" in nudge


def test_nudge_fires_when_test_arrives_after_two_deliverables(tmp_path):
    """deliv1 + deliv2 + test1 -> nudge fires on the test1 edit."""
    _run_hook(_write_input("Write", "/p/src/a.py"), tmp_path)
    _run_hook(_write_input("Write", "/p/src/b.py"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    assert "TDD PATTERN" in _parse_nudge(out)


def test_nudge_suppressed_when_tdd_skill_invoked(tmp_path):
    """Same threshold-crossing scenario, but TDD skill already in log -> no nudge."""
    _run_hook(_write_input("Write", "/p/src/a.py"), tmp_path)
    _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    out, _, _ = _run_hook(
        _write_input("Write", "/p/src/b.py"),
        tmp_path,
        skill_log_entries=["superpowers:test-driven-development"],
    )
    assert "TDD PATTERN" not in _parse_nudge(out)


def test_nudge_fires_only_once_per_session(tmp_path):
    """Once nudged, subsequent threshold-crossings stay silent."""
    _run_hook(_write_input("Write", "/p/src/a.py"), tmp_path)
    _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    out1, _, _ = _run_hook(_write_input("Write", "/p/src/b.py"), tmp_path)
    out2, _, _ = _run_hook(_write_input("Write", "/p/src/c.py"), tmp_path)
    assert "TDD PATTERN" in _parse_nudge(out1)
    assert "TDD PATTERN" not in _parse_nudge(out2)


def test_excluded_path_does_not_count(tmp_path):
    """Files under .tmp/ and /processed/ etc. are excluded entirely."""
    # 2 edits in .tmp + 1 test should NOT cross threshold (both deliv excluded)
    _run_hook(_write_input("Write", "/p/.tmp/scratch.py"), tmp_path)
    _run_hook(_write_input("Write", "/p/.tmp/scratch2.py"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    assert "TDD PATTERN" not in _parse_nudge(out)


def test_doc_files_do_not_count_as_deliverable(tmp_path):
    """README.md / data.json are not deliverables for TDD purposes."""
    _run_hook(_write_input("Write", "/p/README.md"), tmp_path)
    _run_hook(_write_input("Write", "/p/data.json"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    assert "TDD PATTERN" not in _parse_nudge(out)


def test_test_file_classified_first_not_as_deliverable(tmp_path):
    """test_*.py must NEVER count toward deliverable threshold."""
    # 3 test files, no real deliverables -- never fires
    _run_hook(_write_input("Write", "/p/tests/test_a.py"), tmp_path)
    _run_hook(_write_input("Write", "/p/tests/test_b.py"), tmp_path)
    out, _, _ = _run_hook(_write_input("Write", "/p/tests/test_c.py"), tmp_path)
    assert "TDD PATTERN" not in _parse_nudge(out)
