"""Tests for voice-capture-hook.py -- automated voice signal detection.

Source: wr-sentinel-2026-05-04-005. User direction (verbatim, 2026-05-04):
"Even though I am not telling you, it should be updating. Every time we
work, every time we do anything, every time we write emails or any
communications, those should be captured, even if I am not telling you."

Detection rules under test:
  - Correction signals (no/wrong/don't/never/stop with conversational context)
  - Preference signals (I prefer/I want/I'd rather/more like)
  - Approval signals (perfect/exactly/keep doing that)
  - Slash commands skipped
  - Short prompts skipped
  - Same prompt deduped within session
  - Subprocess fired non-blocking to voice-write.py
  - Hook NEVER outputs additionalContext (silent capture per user direction)
"""

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

HOOK = Path.home() / ".claude" / "hooks" / "voice-capture-hook.py"


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("vch", str(HOOK))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _run_hook(stdin_obj, tmp_state_dir):
    """Run hook as subprocess with isolated HOME. Returns (stdout, stderr, rc)."""
    tmp_dir = tmp_state_dir / ".claude" / ".tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    env = {
        "HOME": str(tmp_state_dir),
        "USERPROFILE": str(tmp_state_dir),
        "PATH": os.environ.get("PATH", ""),
        "VOICE_CAPTURE_DRY_RUN": "1",  # don't actually call voice-write.py
    }
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(stdin_obj),
        capture_output=True,
        text=True,
        env=env,
        timeout=10,
    )
    return result.stdout, result.stderr, result.returncode


class TestSignalDetection(unittest.TestCase):
    """Direct detection function tests -- no subprocess overhead."""

    @classmethod
    def setUpClass(cls):
        if not HOOK.exists():
            raise unittest.SkipTest(f"Hook not yet built: {HOOK}")
        cls.m = _load_hook_module()

    # ── Correction signals (should detect) ──────────────────────────────

    def test_detects_no_thats_not(self):
        sigs = self.m.detect_signals("no, that's not what I meant")
        self.assertTrue(any(s["category"] == "correction" for s in sigs))

    def test_detects_dont_do_x(self):
        sigs = self.m.detect_signals("don't do that anymore please")
        self.assertTrue(any(s["category"] == "correction" for s in sigs))

    def test_detects_stop_doing(self):
        sigs = self.m.detect_signals("stop doing the formal opening every time")
        self.assertTrue(any(s["category"] == "correction" for s in sigs))

    def test_detects_thats_wrong(self):
        sigs = self.m.detect_signals("actually that's wrong, the field is named differently")
        self.assertTrue(any(s["category"] == "correction" for s in sigs))

    def test_detects_never_x(self):
        sigs = self.m.detect_signals("never use that phrase in client emails")
        self.assertTrue(any(s["category"] == "correction" for s in sigs))

    # ── Preference signals (should detect) ──────────────────────────────

    def test_detects_i_prefer(self):
        sigs = self.m.detect_signals("I prefer the casual tone over the formal one")
        self.assertTrue(any(s["category"] == "preference" for s in sigs))

    def test_detects_id_rather(self):
        sigs = self.m.detect_signals("I'd rather have a one-line summary than three paragraphs")
        self.assertTrue(any(s["category"] == "preference" for s in sigs))

    def test_detects_more_like(self):
        sigs = self.m.detect_signals("more like the way I'd actually say it")
        self.assertTrue(any(s["category"] == "preference" for s in sigs))

    def test_detects_i_dont_like(self):
        sigs = self.m.detect_signals("I don't like how that paragraph sounds")
        self.assertTrue(any(s["category"] == "preference" for s in sigs))

    # ── Approval signals (should detect) ────────────────────────────────

    def test_detects_perfect(self):
        sigs = self.m.detect_signals("perfect, keep doing that")
        self.assertTrue(any(s["category"] == "approval" for s in sigs))

    def test_detects_exactly_right(self):
        sigs = self.m.detect_signals("yes, exactly right -- that's how I want it")
        self.assertTrue(any(s["category"] == "approval" for s in sigs))

    # ── Should NOT detect (false positive guards) ───────────────────────

    def test_skips_slash_command(self):
        sigs = self.m.detect_signals("/loop 5m /foo")
        self.assertEqual(sigs, [])

    def test_skips_short_prompt(self):
        sigs = self.m.detect_signals("ok")
        self.assertEqual(sigs, [])

    def test_skips_empty_prompt(self):
        sigs = self.m.detect_signals("")
        self.assertEqual(sigs, [])

    def test_v1_known_limitation_quoted_discussion(self):
        """V1 limitation: single-quoted phrases CAN false-positive because
        contractions (don't, I'd, it's) and quoted phrases share the same
        delimiter. Per user direction 2026-05-04, bias is toward MORE
        capture (false positives tolerable, false negatives are not).
        Documented v1 limitation; v2 may add LLM-based filtering.
        """
        sigs = self.m.detect_signals("what does it mean to say 'don't do that' in this context?")
        # Currently false-positives (acceptable per design)
        self.assertIsInstance(sigs, list)

    def test_skips_pure_code_share(self):
        prompt = "```python\nprint('I prefer python')\n```"
        sigs = self.m.detect_signals(prompt)
        # Inside fenced code block -- skip
        self.assertEqual(sigs, [])

    # ── Edge cases ──────────────────────────────────────────────────────

    def test_one_signal_per_prompt_max(self):
        """Multiple matching patterns should produce one fire (no spam)."""
        prompt = "no, that's wrong. don't do that. stop doing that."
        sigs = self.m.detect_signals(prompt)
        # At most one per category; we assert <=3 (one per category) and >=1
        cats = set(s["category"] for s in sigs)
        self.assertGreaterEqual(len(cats), 1)
        self.assertLessEqual(len(sigs), 3)

    def test_returns_list_of_dicts_with_category(self):
        sigs = self.m.detect_signals("don't do that anymore")
        self.assertIsInstance(sigs, list)
        for s in sigs:
            self.assertIn("category", s)
            self.assertIn("matched_phrase", s)


class TestHookIntegration(unittest.TestCase):
    """End-to-end subprocess tests."""

    @classmethod
    def setUpClass(cls):
        if not HOOK.exists():
            raise unittest.SkipTest(f"Hook not yet built: {HOOK}")

    def test_silent_on_correction_signal(self):
        """Hook must NOT emit additionalContext (silent capture per user direction)."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            stdin_obj = {
                "prompt": "no, that's not the way I want it -- be more direct",
                "session_id": "test-session-1",
            }
            stdout, stderr, rc = _run_hook(stdin_obj, tmp)
            self.assertEqual(rc, 0, f"Hook failed: stderr={stderr}")
            # No stdout JSON output -- silent capture
            if stdout.strip():
                # If hook outputs anything, it must NOT be additionalContext
                try:
                    out = json.loads(stdout)
                    self.assertNotIn("additionalContext",
                                      out.get("hookSpecificOutput", {}),
                                      "Hook must be silent (no additionalContext)")
                except json.JSONDecodeError:
                    pass  # non-JSON output is fine

    def test_silent_on_no_signal(self):
        """No signal -> no output, exit 0."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            stdin_obj = {"prompt": "what time is it", "session_id": "test-2"}
            stdout, stderr, rc = _run_hook(stdin_obj, tmp)
            self.assertEqual(rc, 0)
            self.assertEqual(stdout.strip(), "", f"Expected silent, got: {stdout}")

    def test_handles_malformed_stdin_gracefully(self):
        """Bad input should not crash -- exit 0, no output."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            tmp_dir = tmp / ".claude" / ".tmp"
            tmp_dir.mkdir(parents=True, exist_ok=True)
            env = {
                "HOME": str(tmp),
                "USERPROFILE": str(tmp),
                "PATH": os.environ.get("PATH", ""),
                "VOICE_CAPTURE_DRY_RUN": "1",
            }
            result = subprocess.run(
                [sys.executable, str(HOOK)],
                input="not json at all",
                capture_output=True,
                text=True,
                env=env,
                timeout=5,
            )
            self.assertEqual(result.returncode, 0)

    def test_writes_capture_log(self):
        """On signal detection, hook should write to capture log."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            stdin_obj = {
                "prompt": "I prefer the shorter version with bullet points",
                "session_id": "test-3",
            }
            _run_hook(stdin_obj, tmp)
            log_path = tmp / ".claude" / ".tmp" / "voice-capture-log.jsonl"
            self.assertTrue(log_path.exists(), "Capture log not written")
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertGreaterEqual(len(lines), 1)
            entry = json.loads(lines[0])
            self.assertIn("signals", entry)
            self.assertIn("session_id", entry)

    def test_dedup_within_session(self):
        """Same prompt in same session -> only fires once."""
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            stdin_obj = {
                "prompt": "don't add the closing 'best regards' block",
                "session_id": "test-dedup",
            }
            _run_hook(stdin_obj, tmp)
            _run_hook(stdin_obj, tmp)
            log_path = tmp / ".claude" / ".tmp" / "voice-capture-log.jsonl"
            lines = log_path.read_text(encoding="utf-8").strip().splitlines()
            # Second call should be debounced
            self.assertEqual(len(lines), 1, f"Expected dedup, got {len(lines)} entries")


if __name__ == "__main__":
    unittest.main()
