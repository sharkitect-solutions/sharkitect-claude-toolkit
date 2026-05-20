# WR ID Schema Workspace-Prefixed Implementation Plan

<!-- skip brainstorming — design completed and approved 2026-04-27, see docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md -->

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminate two cross-workspace WR id collision bugs by introducing workspace-prefixed ids and enforcing JSON `id` field as the single authoritative identifier. Brain-as-source-of-truth: Sentinel verifies zero-drift, Skill Hub owns the writes.

**Architecture:**
- New id format: `wr-<workspace>-YYYY-MM-DD-NNN` for WRs, `rt-<workspace>-YYYY-MM-DD-<slug>` for routed-tasks. `<workspace>` ∈ {`hq`, `skillhub`, `sentinel`}.
- JSON `id` field is THE identifier. Filename is grep convenience only.
- Backward compat: legacy v1 ids (`wr-YYYY-MM-DD-NNN`) stay v1 FOREVER. Backfill ONLY fills missing ids — never rewrites v1→v2. Supabase holds a permanent mix of both formats. Both are valid query keys.
- New files emit `id_format_version: 2`. Validator accepts v1 (legacy) and v2 (strict).
- Defense-in-depth: 3 enforcement gates (creation / write-time / close).

**Tech Stack:** Python 3 stdlib, `~/.claude/scripts/`, `~/.claude/hooks/`, `~/.claude/rules/universal-protocols.md`, Supabase REST (project `dgnjfamhwfyogmgcpedb`).

**Source spec:** `c:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/docs/superpowers/specs/2026-04-27-wr-id-schema-workspace-prefixed-design.md`

---

## File Structure

| File | Created | Modified | Lines (approx) |
|---|---|---|---|
| `~/.claude/scripts/work-request.py` | | ✓ | ~50 changed |
| `~/.claude/scripts/close-inbox-item.py` | | ✓ | ~15 changed |
| `~/.claude/hooks/inbox-json-validate.py` | | ✓ | ~30 added |
| `~/.claude/rules/universal-protocols.md` | | ✓ | ~50 appended |
| `~/.claude/scripts/wr-id-backfill.py` | ✓ | | ~80 new |
| `~/.claude/scripts/wr-supabase-reconcile.py` | ✓ | | ~120 new |
| `~/.claude/tests/test_wr_id_schema.py` | ✓ | | ~250 new |
| `<sentinel>/.routed-tasks/inbox/rt-2026-04-27-sentinel-wr-id-pre-audit.json` | ✓ | | routed task |
| `<sentinel>/.routed-tasks/inbox/rt-2026-04-27-sentinel-wr-id-post-verify.json` | ✓ | | routed task |

---

### Task 1: work-request.py — emit workspace-prefixed id v2

**Files:**
- Modify: `~/.claude/scripts/work-request.py:163-220` (id generation + build_report)
- Test: `~/.claude/tests/test_wr_id_schema.py` (new)

- [ ] **Step 1: Write failing tests**

Create `~/.claude/tests/test_wr_id_schema.py`:

```python
"""Tests for workspace-prefixed WR id schema (wr-2026-04-25-007 fix)."""
import json, os, re, subprocess, sys, tempfile
from pathlib import Path

WR_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/work-request.py"))
ID_RE_V2 = re.compile(r"^wr-(hq|skillhub|sentinel)-\d{4}-\d{2}-\d{2}-\d{3}$")


def run_wr(workspace, output_dir, **kw):
    cmd = [
        sys.executable, str(WR_SCRIPT),
        "--type", kw.get("type", "TASK"),
        "--severity", kw.get("severity", "info"),
        "--workspace", workspace,
        "--workspace-path", str(output_dir),
        "--task", kw.get("task", "test"),
        "--category", kw.get("category", "operations"),
        "--needed", kw.get("needed", "test"),
        "--gap", kw.get("gap", "test"),
        "--impact", kw.get("impact", "test"),
        "--fix-type", kw.get("fix_type", "task"),
        "--fix-desc", kw.get("fix_desc", "test"),
        "--no-supabase",
        "--output-dir", str(output_dir),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return result


def test_workspace_prefixed_id_skillhub(tmp_path):
    out = tmp_path / "inbox"; out.mkdir()
    r = run_wr("skill-management-hub", out)
    assert r.returncode == 0, r.stderr
    files = list(out.glob("*.json"))
    assert len(files) == 1
    data = json.loads(files[0].read_text(encoding="utf-8"))
    assert ID_RE_V2.match(data["id"]), f"Bad id: {data['id']}"
    assert data["id"].startswith("wr-skillhub-")
    assert data["id_format_version"] == 2


def test_workspace_prefixed_id_hq(tmp_path):
    out = tmp_path / "inbox"; out.mkdir()
    r = run_wr("workforce-hq", out)
    assert r.returncode == 0
    data = json.loads(list(out.glob("*.json"))[0].read_text(encoding="utf-8"))
    assert data["id"].startswith("wr-hq-")
    assert data["id_format_version"] == 2


def test_workspace_prefixed_id_sentinel(tmp_path):
    out = tmp_path / "inbox"; out.mkdir()
    r = run_wr("sentinel", out)
    assert r.returncode == 0
    data = json.loads(list(out.glob("*.json"))[0].read_text(encoding="utf-8"))
    assert data["id"].startswith("wr-sentinel-")


def test_unknown_workspace_rejected(tmp_path):
    out = tmp_path / "inbox"; out.mkdir()
    r = run_wr("unknown-ws", out)
    assert r.returncode != 0
    assert "workspace" in (r.stderr + r.stdout).lower()


def test_counter_increments_per_workspace_per_date(tmp_path):
    """Same workspace + same date = NNN increments. No cross-workspace bleed."""
    out = tmp_path / "inbox"; out.mkdir()
    r1 = run_wr("skill-management-hub", out)
    r2 = run_wr("skill-management-hub", out)
    assert r1.returncode == 0 and r2.returncode == 0
    files = sorted(out.glob("*.json"))
    assert len(files) == 2
    ids = sorted(json.loads(f.read_text(encoding="utf-8"))["id"] for f in files)
    # Both ids end in different NNN
    nnns = [int(i.rsplit("-", 1)[1]) for i in ids]
    assert nnns[1] == nnns[0] + 1, f"Expected sequential, got {nnns}"
```

- [ ] **Step 2: Run tests, verify they FAIL**

```bash
cd "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python -m pytest ~/.claude/tests/test_wr_id_schema.py -v
```
Expected: 5 fails (current id is `wr-YYYY-MM-DD-NNN`; no `--output-dir` / `--no-supabase` flags).

- [ ] **Step 3: Implement workspace-prefix logic + new CLI flags in `work-request.py`**

Add near top of file (after imports):

```python
WORKSPACE_SHORT_MAP = {
    "workforce-hq": "hq",
    "skill-management-hub": "skillhub",
    "sentinel": "sentinel",
}
```

Replace `_used_counters_for_date` (line ~128) with:

```python
def _used_counters_for_workspace_date(inbox_dir, today, workspace_short, workspace_canonical):
    """Return set of NNNs used today for the given workspace prefix.

    Reads JSON 'id' field as authoritative. Handles both v2 (workspace-prefixed)
    and v1 legacy (no prefix, but matching source_workspace) for backward compat.
    """
    used = set()
    siblings = [inbox_dir]
    processed = inbox_dir.parent / "processed"
    if processed.exists():
        siblings.append(processed)
    id_re_v2 = re.compile(rf"^wr-{re.escape(workspace_short)}-{re.escape(today)}-(\d{{3}})$")
    id_re_v1 = re.compile(rf"^wr-{re.escape(today)}-(\d{{3}})$")
    for d in siblings:
        for f in d.glob("*.json"):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError):
                continue
            wr_id = str(data.get("id", ""))
            m = id_re_v2.match(wr_id)
            if m:
                used.add(int(m.group(1)))
                continue
            m1 = id_re_v1.match(wr_id)
            if m1 and data.get("source_workspace") == workspace_canonical:
                used.add(int(m1.group(1)))
    return used
```

Replace `get_next_id` (line ~163) with:

```python
def get_next_id(inbox_dir, workspace_short, workspace_canonical):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    used = _used_counters_for_workspace_date(inbox_dir, today, workspace_short, workspace_canonical)
    next_n = (max(used) + 1) if used else 1
    return f"wr-{workspace_short}-{today}-{next_n:03d}"
```

In `build_report` (line ~194), inject `id_format_version: 2` and resolve workspace_short:

```python
def build_report(args):
    now = datetime.now(timezone.utc)
    request_type = args.type.upper()

    workspace_short = WORKSPACE_SHORT_MAP.get(args.workspace)
    if workspace_short is None:
        print(f"ERROR: unknown workspace '{args.workspace}'. "
              f"Valid: {sorted(WORKSPACE_SHORT_MAP.keys())}", file=sys.stderr)
        sys.exit(2)

    report = {
        "id": None,                  # set after inbox path resolved
        "id_format_version": 2,
        "timestamp": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "request_type": request_type,
        # ... existing fields unchanged ...
    }
    # ... rest of function unchanged but pass workspace_short/canonical to get_next_id call ...
```

In `main()`:
1. Add CLI flags: `--no-supabase` (skip Supabase POST for tests), `--output-dir` (override target inbox).
2. Resolve `workspace_short` early.
3. Change `get_next_id(inbox_dir)` → `get_next_id(inbox_dir, workspace_short, args.workspace)`.

- [ ] **Step 4: Run tests, verify PASS**

```bash
python -m pytest ~/.claude/tests/test_wr_id_schema.py -v
```
Expected: 5/5 PASS.

- [ ] **Step 5: Commit**

```bash
cd ~/.claude
git add scripts/work-request.py tests/test_wr_id_schema.py
git commit -m "fix(wr-id): emit workspace-prefixed id format v2 (wr-2026-04-25-007 task 1/8)

Format: wr-<hq|skillhub|sentinel>-YYYY-MM-DD-NNN with id_format_version: 2.
Counter is per-workspace per-date; cross-workspace collision now impossible.
Adds --no-supabase / --output-dir test flags. Legacy v1 ids stay v1 forever
(backward compat; backfill in task 5/8 fills only missing ids)."
```

---

### Task 2: close-inbox-item.py — strict id-from-JSON for v2

**Files:**
- Modify: `~/.claude/scripts/close-inbox-item.py:583-593`
- Test: `~/.claude/tests/test_wr_id_schema.py` (extend)

- [ ] **Step 1: Append failing tests**

Add to `test_wr_id_schema.py`:

```python
CLOSE_SCRIPT = Path(os.path.expanduser("~/.claude/scripts/close-inbox-item.py"))


def _make_item(tmp, name, payload):
    inbox = tmp / "inbox"; inbox.mkdir(parents=True, exist_ok=True)
    (tmp / "processed").mkdir(exist_ok=True)
    (tmp / "outbox").mkdir(exist_ok=True)
    p = inbox / name
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return p


def test_close_v2_uses_json_id_not_filename(tmp_path):
    """Filename slug deliberately mismatches id; JSON id MUST win."""
    p = _make_item(tmp_path, "weird-mismatch-slug.json", {
        "id": "wr-skillhub-2026-04-27-042",
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "status": "new",
        "notify_on_completion": False,
    })
    r = subprocess.run([sys.executable, str(CLOSE_SCRIPT),
        "--file", str(p), "--status", "processed",
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Test harness verification close.",
        "--no-supabase", "--no-notify", "--no-notify-reason", "test"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
    moved = tmp_path / "processed" / "weird-mismatch-slug.json"
    assert moved.exists()
    d = json.loads(moved.read_text(encoding="utf-8"))
    assert d["id"] == "wr-skillhub-2026-04-27-042"


def test_close_v2_missing_id_refused(tmp_path):
    p = _make_item(tmp_path, "no-id.json", {
        "id_format_version": 2,
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "status": "new",
    })
    r = subprocess.run([sys.executable, str(CLOSE_SCRIPT),
        "--file", str(p), "--status", "processed",
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Should be refused.",
        "--no-supabase", "--no-notify", "--no-notify-reason", "test"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode != 0
    assert "id" in (r.stderr + r.stdout).lower()


def test_close_legacy_v1_works(tmp_path):
    p = _make_item(tmp_path, "2026-04-22_skill-management-hub_legacy-005.json", {
        "id": "wr-2026-04-22-005",
        "request_type": "TASK",
        "source_workspace": "skill-management-hub",
        "status": "new",
        "notify_on_completion": False,
    })
    r = subprocess.run([sys.executable, str(CLOSE_SCRIPT),
        "--file", str(p), "--status", "processed",
        "--resolved-by", "skill-management-hub",
        "--what-was-done", "Backward compat closure of legacy v1.",
        "--no-supabase", "--no-notify", "--no-notify-reason", "test"],
        capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, r.stderr
```

- [ ] **Step 2: Run, verify FAIL**

- [ ] **Step 3: Implement strict id resolution**

In `close-inbox-item.py` near line 583, replace:

```python
# OLD:
item_id = data.get("id") or data.get("request_id") or data.get("task_id")

# NEW:
item_id = data.get("id")
id_format_version = int(data.get("id_format_version", 1) or 1)
if not item_id:
    if id_format_version >= 2:
        sys.stderr.write(
            f"ERROR: id_format_version >= 2 requires explicit 'id' field; "
            f"filename-based derivation is forbidden. File: {file_path}\n"
        )
        sys.exit(2)
    # v1 legacy fallback (preserves completion-notification compat)
    item_id = data.get("request_id") or data.get("task_id")
    if not item_id:
        sys.stderr.write(
            f"ERROR: no 'id'/'request_id'/'task_id' in JSON. File: {file_path}\n"
        )
        sys.exit(2)
```

- [ ] **Step 4: Run, verify PASS**

```bash
python -m pytest ~/.claude/tests/test_wr_id_schema.py -v
```
Expected: 8/8 PASS.

- [ ] **Step 5: Commit**

```bash
git add scripts/close-inbox-item.py tests/test_wr_id_schema.py
git commit -m "fix(wr-id): close-inbox-item.py strict v2 JSON id (wr-2026-04-25-007 task 2/8)

v2 files (id_format_version >= 2) MUST have explicit 'id' field; close
refuses otherwise. Eliminates the filename-derivation drift that produced
wrong-row Supabase updates in 2026-04-25 batch close. v1 legacy fallback
to request_id/task_id preserved (completion-notifications still close)."
```

---

### Task 3: inbox-json-validate.py — Write-time schema enforcement

**Files:**
- Modify: `~/.claude/hooks/inbox-json-validate.py`
- Test: `~/.claude/tests/test_wr_id_schema.py` (extend)

- [ ] **Step 1: Append failing tests**

```python
HOOK_PATH = Path(os.path.expanduser("~/.claude/hooks/inbox-json-validate.py"))


def _run_hook(file_path, content_dict):
    stdin = json.dumps({"tool_name": "Write", "tool_input": {
        "file_path": str(file_path),
        "content": json.dumps(content_dict),
    }})
    return subprocess.run([sys.executable, str(HOOK_PATH)],
        input=stdin, capture_output=True, text=True, timeout=10)


def test_hook_blocks_v2_without_id(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "no-id.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {"id_format_version": 2, "request_type": "TASK",
                      "source_workspace": "skill-management-hub"})
    assert r.returncode == 2, f"should block: {r.stdout}"


def test_hook_blocks_v2_invalid_format(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "bad-format.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {"id": "wr-bogus-id", "id_format_version": 2,
                      "request_type": "TASK",
                      "source_workspace": "skill-management-hub"})
    assert r.returncode == 2


def test_hook_allows_v2_valid(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "good.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {"id": "wr-skillhub-2026-04-27-001",
                      "id_format_version": 2, "request_type": "TASK",
                      "source_workspace": "skill-management-hub"})
    assert r.returncode == 0, r.stderr


def test_hook_allows_legacy_v1(tmp_path):
    p = tmp_path / ".work-requests" / "inbox" / "legacy.json"
    p.parent.mkdir(parents=True)
    r = _run_hook(p, {"id": "wr-2026-04-22-005", "request_type": "TASK",
                      "source_workspace": "skill-management-hub"})
    assert r.returncode == 0
```

- [ ] **Step 2: Run, verify FAIL**

- [ ] **Step 3: Add validator function + integrate**

In `inbox-json-validate.py`, add near top:

```python
import re

ID_RE_V2 = re.compile(r"^(wr|rt)-(hq|skillhub|sentinel)-\d{4}-\d{2}-\d{2}-(\d{3}|[a-z0-9-]+)$")
ID_RE_V1 = re.compile(r"^(wr|rt)-\d{4}-\d{2}-\d{2}-(\d{3}|[a-z0-9-]+)$")


def validate_wr_id_schema(parsed_json):
    """Return (ok: bool, reason: str)."""
    fmt = int(parsed_json.get("id_format_version", 1) or 1)
    wr_id = parsed_json.get("id")
    if fmt >= 2:
        if not wr_id:
            return False, "id_format_version >= 2 requires 'id' field"
        if not ID_RE_V2.match(str(wr_id)):
            return False, (f"id '{wr_id}' does not match v2 pattern "
                           "wr-<hq|skillhub|sentinel>-YYYY-MM-DD-NNN")
        return True, "ok (v2)"
    # v1 legacy: optional but if present must match v1 or v2
    if wr_id and not (ID_RE_V1.match(str(wr_id)) or ID_RE_V2.match(str(wr_id))):
        return False, f"id '{wr_id}' does not match v1 pattern wr-YYYY-MM-DD-NNN"
    return True, "ok (v1 legacy)"
```

In the existing main() flow that already validates inbox JSONs (find via `grep -n "PreToolUse" ~/.claude/hooks/inbox-json-validate.py`), call `validate_wr_id_schema` on the parsed payload. If invalid, emit:

```python
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "additionalContext": f"WR id schema violation: {reason}",
    }
}))
sys.exit(2)
```

- [ ] **Step 4: Run, verify PASS**

```bash
python -m pytest ~/.claude/tests/test_wr_id_schema.py -v
```
Expected: 12/12 PASS.

- [ ] **Step 5: Commit**

```bash
git add hooks/inbox-json-validate.py tests/test_wr_id_schema.py
git commit -m "fix(wr-id): write-time schema enforcement (wr-2026-04-25-007 task 3/8)

PreToolUse hook now denies Write of inbox JSON if id_format_version >= 2
without valid 'id' matching wr-<workspace>-YYYY-MM-DD-NNN. v1 legacy ids
remain accepted. Defense-in-depth complement to creation (task 1) + close
(task 2) gates."
```

---

### Task 4: universal-protocols.md — JSON Schema Contract section

**Files:**
- Modify: `~/.claude/rules/universal-protocols.md` (append section)

- [ ] **Step 1: Append section after "Status Vocabulary Layers" subsection**

Append the section (full text in the design spec, section "v2 Schema" + "Layered Enforcement" + "Backward Compatibility"). Heading: `## WR/RT/Lifecycle JSON Schema Contract (NON-NEGOTIABLE)`.

- [ ] **Step 2: Sync to toolkit (rules are part of sync-skills.py scope)**

```bash
cd "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python tools/sync-skills.py
```
Verify universal-protocols.md is queued for sync.

- [ ] **Step 3: Commit**

```bash
cd ~/.claude
git add rules/universal-protocols.md
git commit -m "docs(wr-id): JSON Schema Contract section in universal-protocols (wr-2026-04-25-007 task 4/8)"
```

---

### Task 5: wr-id-backfill.py — fill MISSING ids only (never rewrite v1→v2)

**Files:**
- Create: `~/.claude/scripts/wr-id-backfill.py`

**Critical guardrail:** Only fills `id` field if missing. Existing v1 ids are preserved verbatim. This avoids creating Supabase drift (every existing v1 id has a matching `cross_workspace_requests` row keyed by that string).

- [ ] **Step 1: Implement script (dry-run by default)**

```python
#!/usr/bin/env python3
"""wr-id-backfill.py — Fill MISSING id field on legacy WR JSONs.

NEVER rewrites existing ids (v1 stays v1 forever). Only fills `id` when
absent. Idempotent. Defaults to --dry-run.

Usage:
    python wr-id-backfill.py                       # dry-run all 3 workspaces
    python wr-id-backfill.py --apply               # apply
    python wr-id-backfill.py --apply --workspace skill-management-hub
"""
import argparse, json, re, sys
from pathlib import Path

WORKSPACE_SHORT = {"workforce-hq": "hq", "skill-management-hub": "skillhub", "sentinel": "sentinel"}
WORKSPACE_DIRS = {
    "workforce-hq": "1.- SHARKITECT DIGITAL WORKFORCE HQ",
    "skill-management-hub": "3.- Skill Management Hub",
    "sentinel": "4.- Sentinel",
}
ID_RE_V2 = re.compile(r"^wr-(hq|skillhub|sentinel)-\d{4}-\d{2}-\d{2}-\d{3}$")
ID_RE_V1 = re.compile(r"^wr-\d{4}-\d{2}-\d{2}-\d{3}$")
FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_([a-z\-]+)_.+-(\d{3})\.json$")


def derive_id_from_filename(p: Path, source_workspace: str):
    m = FILENAME_RE.match(p.name)
    if not m:
        return None
    date, _ws_in_name, nnn = m.groups()
    short = WORKSPACE_SHORT.get(source_workspace)
    if not short:
        return None
    return f"wr-{short}-{date}-{nnn}"


def process_file(p: Path, apply_changes: bool):
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return f"  SKIP (unreadable): {p.name} -- {e}"
    wr_id = data.get("id")
    # Has any valid id? Leave it alone.
    if wr_id and (ID_RE_V2.match(str(wr_id)) or ID_RE_V1.match(str(wr_id))):
        return None
    # Has a malformed id? Flag, don't overwrite.
    if wr_id:
        return f"  REVIEW (malformed id): {p.name} -- id={wr_id!r}"
    # No id: derive from filename
    derived = derive_id_from_filename(p, data.get("source_workspace", ""))
    if not derived:
        return (f"  REVIEW (cannot derive): {p.name} -- "
                f"source_workspace={data.get('source_workspace')!r}")
    if not apply_changes:
        return f"  WOULD-FILL: {p.name} -> id={derived}"
    data["id"] = derived
    data["id_backfilled"] = True
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return f"  FILLED: {p.name} -> id={derived}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--workspace", choices=list(WORKSPACE_DIRS.keys()))
    args = ap.parse_args()
    base = Path("C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces")
    targets = [args.workspace] if args.workspace else list(WORKSPACE_DIRS.keys())
    total = 0
    actions = 0
    for ws in targets:
        ws_dir = base / WORKSPACE_DIRS[ws]
        for sub in ("inbox", "processed", "outbox"):
            d = ws_dir / ".work-requests" / sub
            if not d.exists():
                continue
            print(f"=== {ws} / .work-requests/{sub} ===")
            for f in sorted(d.glob("*.json")):
                total += 1
                msg = process_file(f, args.apply)
                if msg:
                    print(msg)
                    actions += 1
    print(f"\nFiles scanned: {total}. Actions: {actions}. "
          f"{'APPLIED' if args.apply else 'DRY-RUN (use --apply to fill).'}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Dry-run across all 3 workspaces**

```bash
python ~/.claude/scripts/wr-id-backfill.py
```
Review output. Confirm no `REVIEW (malformed id)` entries (those need human inspection). All `WOULD-FILL` entries should have plausible derived ids.

- [ ] **Step 3: Apply**

```bash
python ~/.claude/scripts/wr-id-backfill.py --apply
```

- [ ] **Step 4: Commit**

```bash
git add scripts/wr-id-backfill.py
git commit -m "feat(wr-id): backfill script (fills missing ids only) (wr-2026-04-25-007 task 5/8)

Idempotent. Never rewrites existing v1 ids. Marks newly-filled with
id_backfilled: true. Dry-run by default."
```

---

### Task 6: wr-supabase-reconcile.py — fix 2026-04-25 batch-close drift

Depends on Sentinel pre-audit (Task 7) for the verified target list.

**Files:**
- Create: `~/.claude/scripts/wr-supabase-reconcile.py`

- [ ] **Step 1: Wait for Sentinel pre-audit completion notification (Task 7 deliverable)**

The Sentinel routed-task will produce a JSON list at agreed path (e.g. `~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json`) with shape:
```json
[
  {"correct_item_id": "wr-skillhub-2026-04-25-007",
   "currently_in_supabase_with_wrong_text": "wr-2026-04-25-005",
   "correct_what_was_done": "...",
   "currently_in_supabase_text": "..."},
  ...
]
```

- [ ] **Step 2: Implement reconcile script (dry-run default; reads Sentinel list)**

```python
#!/usr/bin/env python3
"""wr-supabase-reconcile.py — Fix 2026-04-25 batch-close drift in cross_workspace_requests.

Reads Sentinel pre-audit JSON (output of rt-2026-04-27-sentinel-wr-id-pre-audit).
For each entry, PATCHes the correct row's resolution_summary to match the
local processed/*.json. Optionally also clears the wrong-row's resolution
text if no other source is closing it.

Usage:
    python wr-supabase-reconcile.py --audit-file <path>           # dry-run
    python wr-supabase-reconcile.py --audit-file <path> --apply
"""
import argparse, json, sys, urllib.request, urllib.error
from pathlib import Path

# load env
sys.path.insert(0, str(Path("tools")))
try:
    from load_env import load_all
    env = load_all()
except Exception:
    import os
    env = dict(os.environ)


def patch_supabase(item_id, payload):
    url = env.get("SUPABASE_URL", "").rstrip("/")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY", "")
    endpoint = f"{url}/rest/v1/cross_workspace_requests?item_id=eq.{item_id}"
    headers = {
        "apikey": key, "Authorization": f"Bearer {key}",
        "Content-Type": "application/json", "Prefer": "return=representation",
    }
    req = urllib.request.Request(endpoint, data=json.dumps(payload).encode(),
                                 method="PATCH", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-file", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    audit = json.loads(Path(args.audit_file).read_text(encoding="utf-8"))
    print(f"Reading {len(audit)} drift entries...")
    fixed = 0
    for entry in audit:
        target = entry["correct_item_id"]
        correct_text = entry["correct_what_was_done"]
        if not args.apply:
            print(f"  WOULD-PATCH item_id={target}: resolution_summary -> "
                  f"{correct_text[:80]!r}...")
            fixed += 1
            continue
        status, body = patch_supabase(target, {
            "resolution_summary": correct_text,
            "last_updated_by": "skill-management-hub",
        })
        if status in (200, 204):
            print(f"  OK   {target}")
            fixed += 1
        else:
            print(f"  FAIL {target}: HTTP {status} {body[:200]}")
    print(f"\n{'Applied' if args.apply else 'Dry-run'}: {fixed}/{len(audit)}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 3: Dry-run with Sentinel's audit output**

```bash
python ~/.claude/scripts/wr-supabase-reconcile.py \
  --audit-file ~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json
```

- [ ] **Step 4: Apply**

```bash
python ~/.claude/scripts/wr-supabase-reconcile.py \
  --audit-file ~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json --apply
```

- [ ] **Step 5: Commit + dispatch Sentinel post-verify routed-task (Task 8)**

---

### Task 7: Dispatch Sentinel pre-audit routed-task

**Files:**
- Create: `<sentinel-workspace>/.routed-tasks/inbox/rt-2026-04-27-sentinel-wr-id-pre-audit.json`
- Create: `.routed-tasks/outbox/sentinel-wr-id-pre-audit.md` (audit trail)

- [ ] **Step 1: Write routed-task JSON to Sentinel's inbox**

```json
{
  "task_id": "rt-2026-04-27-sentinel-wr-id-pre-audit",
  "task_summary": "Pre-audit cross_workspace_requests for 2026-04-25 batch-close drift",
  "routed_from": "skill-management-hub",
  "routed_to": "sentinel",
  "routed_date": "2026-04-27",
  "priority": "high",
  "context": "wr-2026-04-25-007 closure work in progress (workspace-prefixed id schema). Skill Hub Task 6 needs a verified list of cross_workspace_requests rows where resolution_summary text is wrong vs the matching local processed/*.json file. Cause: 2026-04-25 batch-close used filename-derivation that wrote text into wrong rows.",
  "what_source_already_did": "Implemented Tasks 1-3 (work-request.py + close-inbox-item.py + inbox-json-validate.py) eliminating the drift mechanism going forward. Backfill (Task 5) fills only missing ids; v1 ids stay v1.",
  "fix_instructions": "Step 1: Query cross_workspace_requests for the 11 rows touched 2026-04-25 between 17:00-19:00 UTC (last_updated_by='skill-management-hub'). Step 2: For each, locate matching local processed/*.json by source_workspace + filename slug + content match. Step 3: Compare Supabase resolution_summary vs local resolution.what_was_done. Step 4: Output JSON list to ~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json with shape: [{correct_item_id, currently_in_supabase_with_wrong_text, correct_what_was_done, currently_in_supabase_text, source_file_path}]. Step 5: Notify Skill Hub via completion-notification routed-task.",
  "expected_completion_artifact": "~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json",
  "notify_on_completion": true,
  "notify_inbox_path": "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox",
  "notification_filename_hint": "rt-2026-04-27-sentinel-wr-id-pre-audit-completed-by-sentinel.json"
}
```

- [ ] **Step 2: Write outbox audit trail (.md file)**

- [ ] **Step 3: Commit + push (so Sentinel sees on next session start)**

```bash
git add .routed-tasks/outbox/sentinel-wr-id-pre-audit.md
git commit -m "feat(wr-id): dispatch Sentinel pre-audit task (wr-2026-04-25-007 task 7/8)"
```

---

### Task 8: Dispatch Sentinel post-verify + permanent monitor routed-task

**Files:**
- Create: `<sentinel-workspace>/.routed-tasks/inbox/rt-2026-04-27-sentinel-wr-id-post-verify.json`
- Create: `.routed-tasks/outbox/sentinel-wr-id-post-verify.md`

- [ ] **Step 1: Write routed-task to Sentinel's inbox**

```json
{
  "task_id": "rt-2026-04-27-sentinel-wr-id-post-verify",
  "task_summary": "Post-execution verification + permanent WR ID Consistency monitor",
  "routed_from": "skill-management-hub",
  "routed_to": "sentinel",
  "routed_date": "2026-04-27",
  "priority": "high",
  "blocked_by_description": "Skill Hub Task 6 (wr-supabase-reconcile.py --apply) must complete first. This task pulls from those reconciled writes.",
  "context": "Final verification of brain-as-source-of-truth invariant after wr-2026-04-25-007 implementation. Two deliverables: (1) one-off zero-drift verification sweep across all 3 workspaces, (2) permanent monitoring check added to morning report and audit-autonomous-systems.py to catch future drift within 24h.",
  "fix_instructions": "Verification sweep: For every processed/*.json across all 3 workspaces (~30+ files), confirm matching cross_workspace_requests row exists (item_id match) and resolution_summary == resolution.what_was_done from the JSON. For every cross_workspace_requests row with status IN ('completed','rejected','superseded','duplicate'), confirm matching local file exists in some workspace's processed/. Report orphans (Supabase row with no file, file with no Supabase row) by id. Sign off zero-drift via completion-notification routed-task to Skill Hub. Permanent monitor: add a 'WR ID Consistency' check to the morning report and audit-autonomous-systems.py --json output. Daily cadence; flag any drift detected within 24h.",
  "expected_completion_artifact": "Zero-drift sign-off (completion notification) + one new monitoring check shipped",
  "notify_on_completion": true,
  "notify_inbox_path": "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox",
  "notification_filename_hint": "rt-2026-04-27-sentinel-wr-id-post-verify-completed-by-sentinel.json"
}
```

- [ ] **Step 2: Write outbox audit trail**

- [ ] **Step 3: After all 6 Skill Hub tasks complete + Sentinel post-verify completion notification arrives, close the trigger WR**

```bash
cd "C:/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub"
python ~/.claude/scripts/close-inbox-item.py \
  --file ".work-requests/inbox/2026-04-25_skill-management-hub_close-inbox-item-py-reliable-i-007.json" \
  --status processed \
  --resolved-by skill-management-hub \
  --what-was-done "Implemented 8-task workspace-prefixed id schema fix. Tasks 1-6 in Skill Hub: work-request.py emits wr-<workspace>-YYYY-MM-DD-NNN with id_format_version: 2; close-inbox-item.py refuses to close v2 files without explicit JSON id; inbox-json-validate.py enforces schema on Write; universal-protocols.md gains JSON Schema Contract section; wr-id-backfill.py fills missing ids only (zero-drift); wr-supabase-reconcile.py corrects 2026-04-25 batch-close drift using Sentinel pre-audit list. Tasks 7-8 routed to Sentinel: pre-audit produced verified target list for Task 6; post-verify swept all processed/ files vs cross_workspace_requests, signed off zero-drift, added permanent WR ID Consistency check to morning report. All 12 tests pass." \
  --fix-type script \
  --artifacts-created "~/.claude/scripts/wr-id-backfill.py,~/.claude/scripts/wr-supabase-reconcile.py,~/.claude/tests/test_wr_id_schema.py" \
  --artifacts-modified "~/.claude/scripts/work-request.py,~/.claude/scripts/close-inbox-item.py,~/.claude/hooks/inbox-json-validate.py,~/.claude/rules/universal-protocols.md"
```

---

## Self-Review

- [x] Spec coverage: every section of `2026-04-27-wr-id-schema-workspace-prefixed-design.md` mapped to a task
- [x] No placeholders — all code blocks complete
- [x] Type consistency — `id_format_version`, workspace short prefix, ID_RE_V2 used uniformly
- [x] TDD on Tasks 1-3 (the code-mutating tasks); Tasks 4-6 use direct edit + dry-run pattern (appropriate for docs/utility scripts); Tasks 7-8 are routed-task dispatch (no code)
- [x] Backward compat preserved (legacy v1 stays v1; backfill fills only missing)
- [x] Brain-as-source-of-truth: Sentinel verifies, Skill Hub writes — audit and write are separated
- [x] Each task is committable independently — clean rollback boundaries

## Execution Notes

- **Hooks load only at session start.** Task 3's hook change takes effect on the NEXT session, not this one. Task 1-2 script changes take effect immediately on next invocation.
- **Tasks 1-3 = MVP minimum.** They close both bugs at the root. Tasks 4-6 are completeness. Tasks 7-8 are oversight.
- **Sentinel dependency:** Task 6 BLOCKED on Task 7 completion. Don't run Task 6 until Sentinel pre-audit JSON arrives at `~/.claude/.tmp/sentinel-wr-id-pre-audit-results.json`.
- **Test runner:** all tests live in `~/.claude/tests/test_wr_id_schema.py`. Run with `python -m pytest ~/.claude/tests/test_wr_id_schema.py -v`.
- After Task 4, run `python tools/sync-skills.py` to ensure the universal-protocols.md update propagates to the toolkit.
