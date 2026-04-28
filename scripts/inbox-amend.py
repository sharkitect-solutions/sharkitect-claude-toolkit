#!/usr/bin/env python
"""inbox-amend.py -- Generic source-side inbox item amendment CLI.

Applies to work-request, routed-task, and lifecycle-review JSON files
in inbox/ directories. Source workspace amends own filed items via this
CLI; direct Edit on cross-workspace inbox files is denied by the
permissions system. The CLI enforces source identity, status guard
(locked once target sets in_progress or any close state), and
append-only history in the source_amendments[] array.

Modes (13 total):
  add-context, severity-update, priority-update, component-add,
  component-remove, add-evidence, link-related, reclassify, supersede,
  duplicate, withdraw, reroute, retract-amendment, bulk-amend.

Schema (each amendment is appended to source_amendments[]):
  See spec at <Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md.

Pure stdlib. Atomic write via tempfile + os.replace.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path


CANONICAL_WORKSPACES = ("workforce-hq", "skill-management-hub", "sentinel")
AMENDABLE_STATUSES = {"new", "pending", "deferred"}
CLOSE_INBOX_SCRIPT = Path.home() / ".claude" / "scripts" / "close-inbox-item.py"
AUTO_CLOSE_MAP = {
    "supersede": "superseded",
    "duplicate": "duplicate",
    "withdraw": "withdrawn"
}


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _gen_amendment_id() -> str:
    today = dt.date.today().isoformat()
    return f"amend-{today}-{uuid.uuid4().hex[:8]}"


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def _atomic_write_json(p: Path, data: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=p.name + ".", suffix=".tmp", dir=p.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _validate_source(item: dict, claimed_from: str) -> tuple[bool, str]:
    if claimed_from not in CANONICAL_WORKSPACES:
        return False, f"--from must be one of {CANONICAL_WORKSPACES}; got {claimed_from!r}"
    actual = item.get("source_workspace") or item.get("routed_from")
    if not actual:
        return False, "Item has neither source_workspace nor routed_from -- cannot validate identity"
    if actual != claimed_from:
        return False, (
            f"Source mismatch: --from={claimed_from!r} but item.source_workspace={actual!r}. "
            "Only the originating workspace may amend its own filed items. "
            "Cross-workspace coordination uses routed-tasks instead."
        )
    return True, ""


def _validate_status_guard(item: dict) -> tuple[bool, str]:
    s = item.get("status", "new")
    if s in AMENDABLE_STATUSES:
        return True, ""
    return False, (
        f"Item status={s!r} is locked -- source amendments only allowed in "
        f"{sorted(AMENDABLE_STATUSES)}. Once target sets in_progress or "
        "closes, source must coordinate via routed-task."
    )


def _is_idempotent_replay(item: dict, amendment_id: str) -> bool:
    return any(
        a.get("amendment_id") == amendment_id
        for a in item.get("source_amendments", [])
    )


def _build_event(args, mode: str, fields_changed: dict | None = None,
                 structured_data: dict | None = None) -> dict:
    """Build amendment event with full forward-compat schema."""
    return {
        "amendment_id": args.amendment_id or _gen_amendment_id(),
        "timestamp": _now_iso(),
        "actor": args.from_,
        "actor_type": "workspace",
        "amendment_type": mode,
        "reason": args.reason,
        "fields_changed": fields_changed or {},
        "structured_data": structured_data or {},
        "notes": getattr(args, "note", None) or "",
        "supersedes": getattr(args, "supersedes", None),
        "duplicate_of": getattr(args, "duplicate_of", None),
        "retracts_amendment": getattr(args, "retracts_amendment", None),
        "retracted": False,
        "retracted_at": None,
        "retracted_by_amendment_id": None,
        # Forward-compat slots
        "condition": None,
        "template_id": None,
        "expires_at": None,
        "parent_etag": None,
        "triggers": []
    }


def _apply_event(item: dict, event: dict, top_level_updates: dict | None = None) -> None:
    item.setdefault("source_amendments", []).append(event)
    if top_level_updates:
        for k, v in top_level_updates.items():
            item[k] = v


def _maybe_auto_close(args, item: dict, event: dict, mode: str) -> None:
    """Call close-inbox-item.py for supersede/duplicate/withdraw."""
    close_status = AUTO_CLOSE_MAP.get(mode)
    if not close_status:
        return
    ref_arg = []
    if mode == "supersede":
        ref_arg = ["--superseded-by", args.supersedes]
    elif mode == "duplicate":
        ref_arg = ["--duplicate-of", args.duplicate_of]

    what_was_done = f"Source amendment ({mode}): {args.reason}"
    argv = [
        sys.executable, str(CLOSE_INBOX_SCRIPT),
        "--file", str(args.file),
        "--status", close_status,
        "--resolved-by", args.from_,
        "--what-was-done", what_was_done,
    ] + ref_arg

    if getattr(args, "close_script_stub", None):
        Path(args.close_script_stub).write_text(
            json.dumps({"argv": argv}), encoding="utf-8"
        )
        return
    subprocess.run(argv, check=True)


# ===== Mode handlers =====

def cmd_add_context(args, item: dict) -> dict:
    event = _build_event(args, "add_context")
    _apply_event(item, event)
    return event


def cmd_severity_update(args, item: dict) -> dict:
    old = item.get("severity")
    event = _build_event(args, "severity_update",
                         fields_changed={"severity": {"from": old, "to": args.new_severity}})
    _apply_event(item, event, top_level_updates={"severity": args.new_severity})
    return event


def cmd_priority_update(args, item: dict) -> dict:
    old = item.get("priority")
    event = _build_event(args, "priority_update",
                         fields_changed={"priority": {"from": old, "to": args.new_priority}})
    _apply_event(item, event, top_level_updates={"priority": args.new_priority})
    return event


def cmd_component_add(args, item: dict) -> dict:
    components = list(item.get("components", []))
    incoming = [c.strip() for c in args.components.split(",") if c.strip()]
    new = [c for c in incoming if c not in components]
    components.extend(new)
    event = _build_event(args, "component_add",
                         fields_changed={"components": {"from": item.get("components", []), "to": components}},
                         structured_data={"components_added": new})
    _apply_event(item, event, top_level_updates={"components": components})
    return event


def cmd_component_remove(args, item: dict) -> dict:
    to_remove = {c.strip() for c in args.components.split(",") if c.strip()}
    components = [c for c in item.get("components", []) if c not in to_remove]
    event = _build_event(args, "component_remove",
                         fields_changed={"components": {"from": item.get("components", []), "to": components}},
                         structured_data={"components_removed": list(to_remove)})
    _apply_event(item, event, top_level_updates={"components": components})
    return event


def cmd_add_evidence(args, item: dict) -> dict:
    entry = {"type": args.evidence_type, "ref": args.evidence_ref, "note": args.note or ""}
    event = _build_event(args, "add_evidence", structured_data={"evidence": [entry]})
    item.setdefault("evidence", []).append(entry)
    _apply_event(item, event)
    return event


def cmd_link_related(args, item: dict) -> dict:
    link = {"type": args.link_type, "id": args.link_id}
    event = _build_event(args, "link_related", structured_data={"related_items": [link]})
    item.setdefault("related_items", []).append(link)
    _apply_event(item, event)
    return event


def cmd_reclassify(args, item: dict) -> dict:
    old = item.get("request_type")
    event = _build_event(args, "reclassify",
                         fields_changed={"request_type": {"from": old, "to": args.new_type}})
    _apply_event(item, event, top_level_updates={"request_type": args.new_type})
    return event


def cmd_supersede(args, item: dict) -> dict:
    if not args.supersedes:
        raise SystemExit("supersede mode requires --supersedes <new-id>")
    event = _build_event(args, "supersede")
    _apply_event(item, event)
    return event


def cmd_duplicate(args, item: dict) -> dict:
    if not args.duplicate_of:
        raise SystemExit("duplicate mode requires --duplicate-of <surviving-id>")
    event = _build_event(args, "duplicate")
    _apply_event(item, event)
    return event


def cmd_withdraw(args, item: dict) -> dict:
    event = _build_event(args, "withdraw")
    _apply_event(item, event)
    return event


def cmd_reroute(args, item: dict) -> dict:
    new_target = args.new_target
    new_target_dir = Path(args.new_target_inbox_dir).resolve()
    if not new_target_dir.exists():
        raise SystemExit(f"new-target-inbox-dir does not exist: {new_target_dir}")

    # Collision check: abort if destination filename already taken
    new_path = new_target_dir / Path(args.file).name
    if new_path.exists():
        raise SystemExit(
            f"Reroute collision: destination already exists at {new_path}. "
            "Aborting to prevent overwrite. Rename source or choose different "
            "destination."
        )

    old_target = item.get("routed_to")
    history = list(item.get("routed_to_history", []))
    history.append({
        "from": old_target,
        "to": new_target,
        "timestamp": _now_iso(),
        "reason": args.reason
    })
    event = _build_event(args, "reroute",
                         fields_changed={"routed_to": {"from": old_target, "to": new_target}})
    item["routed_to"] = new_target
    item["routed_to_history"] = history
    _apply_event(item, event)
    # Move file
    _atomic_write_json(new_path, item)
    Path(args.file).unlink()
    args.file = new_path
    return event


def cmd_retract_amendment(args, item: dict) -> dict:
    if not args.retracts_amendment:
        raise SystemExit("retract-amendment mode requires --retracts-amendment <amendment-id>")
    found = False
    new_id = args.amendment_id or _gen_amendment_id()
    for a in item.get("source_amendments", []):
        if a.get("amendment_id") == args.retracts_amendment:
            a["retracted"] = True
            a["retracted_at"] = _now_iso()
            a["retracted_by_amendment_id"] = new_id
            found = True
            break
    if not found:
        raise SystemExit(
            f"No amendment with id {args.retracts_amendment!r} found in source_amendments[]"
        )
    args.amendment_id = new_id
    event = _build_event(args, "retract_amendment")
    _apply_event(item, event)
    return event


def cmd_bulk_amend(args) -> int:
    """Apply same amendment across multiple files via subordinate process calls."""
    files = [Path(f.strip()) for f in args.files.split(",") if f.strip()]
    if not files:
        raise SystemExit("bulk-amend requires --files <comma-separated paths>")
    failures = []
    for f in files:
        sub_argv = [
            sys.executable, str(Path(__file__).resolve()),
            args.mode,
            "--file", str(f),
            "--from", args.from_,
            "--reason", args.reason
        ]
        if args.note:
            sub_argv += ["--note", args.note]
        proc = subprocess.run(sub_argv, capture_output=True, text=True)
        if proc.returncode != 0:
            failures.append((f, proc.returncode, proc.stderr))
    if failures:
        print(f"BULK-AMEND PARTIAL FAILURE: {len(failures)} of {len(files)} file(s) failed:",
              file=sys.stderr)
        for f, code, err in failures:
            print(f"  {f}: rc={code} stderr={err.strip()[:200]}", file=sys.stderr)
        return 1
    print(f"BULK-AMEND OK: {len(files)} files updated")
    return 0


# ===== Argparse =====

def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--file", type=Path, required=True)
    p.add_argument("--from", dest="from_", required=True, choices=CANONICAL_WORKSPACES)
    p.add_argument("--reason", required=True, help=">= 10 char human-readable explanation")
    p.add_argument("--note", default=None)
    p.add_argument("--amendment-id", default=None)
    p.add_argument("--close-script-stub", default=None, help=argparse.SUPPRESS)


def main() -> int:
    parser = argparse.ArgumentParser(prog="inbox-amend.py")
    # Note: parent dest is "command" not "mode" because bulk-amend has its own
    # --mode flag (the sub-amendment to apply across files), which would
    # otherwise overwrite args.mode after parsing.
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add-context"); _add_common_args(p)

    p = sub.add_parser("severity-update"); _add_common_args(p)
    p.add_argument("--new-severity", required=True, choices=("info", "warning", "high", "critical"))

    p = sub.add_parser("priority-update"); _add_common_args(p)
    p.add_argument("--new-priority", required=True, choices=("low", "medium", "high", "critical"))

    p = sub.add_parser("component-add"); _add_common_args(p)
    p.add_argument("--components", required=True)

    p = sub.add_parser("component-remove"); _add_common_args(p)
    p.add_argument("--components", required=True)

    p = sub.add_parser("add-evidence"); _add_common_args(p)
    p.add_argument("--evidence-type", required=True, choices=("log", "screenshot", "trace", "url", "file"))
    p.add_argument("--evidence-ref", required=True)

    p = sub.add_parser("link-related"); _add_common_args(p)
    p.add_argument("--link-type", required=True, choices=("blocks", "blocked_by", "related", "depends_on"))
    p.add_argument("--link-id", required=True)

    p = sub.add_parser("reclassify"); _add_common_args(p)
    p.add_argument("--new-type", required=True,
                   choices=("MISSING", "UNUSED", "FALLBACK", "TASK", "BUG", "ENHANCE"))

    p = sub.add_parser("supersede"); _add_common_args(p)
    p.add_argument("--supersedes", required=True)

    p = sub.add_parser("duplicate"); _add_common_args(p)
    p.add_argument("--duplicate-of", required=True)

    p = sub.add_parser("withdraw"); _add_common_args(p)

    p = sub.add_parser("reroute"); _add_common_args(p)
    p.add_argument("--new-target", required=True, choices=CANONICAL_WORKSPACES)
    p.add_argument("--new-target-inbox-dir", required=True)

    p = sub.add_parser("retract-amendment"); _add_common_args(p)
    p.add_argument("--retracts-amendment", required=True)

    p = sub.add_parser("bulk-amend")
    p.add_argument("--files", required=True)
    p.add_argument("--from", dest="from_", required=True, choices=CANONICAL_WORKSPACES)
    p.add_argument("--reason", required=True)
    p.add_argument("--mode", required=True)
    p.add_argument("--note", default=None)

    args = parser.parse_args()

    if args.command == "bulk-amend":
        return cmd_bulk_amend(args)

    if len(args.reason) < 10:
        print(f"--reason must be >= 10 chars (got {len(args.reason)})", file=sys.stderr)
        return 2

    item = _read_json(args.file)

    ok, err = _validate_source(item, args.from_)
    if not ok:
        print(err, file=sys.stderr)
        return 3

    ok, err = _validate_status_guard(item)
    if not ok:
        print(err, file=sys.stderr)
        return 4

    if not args.amendment_id:
        args.amendment_id = _gen_amendment_id()

    if _is_idempotent_replay(item, args.amendment_id):
        print(f"Idempotent replay: amendment_id {args.amendment_id} already present, no-op",
              file=sys.stderr)
        return 0

    handler = {
        "add-context": cmd_add_context,
        "severity-update": cmd_severity_update,
        "priority-update": cmd_priority_update,
        "component-add": cmd_component_add,
        "component-remove": cmd_component_remove,
        "add-evidence": cmd_add_evidence,
        "link-related": cmd_link_related,
        "reclassify": cmd_reclassify,
        "supersede": cmd_supersede,
        "duplicate": cmd_duplicate,
        "withdraw": cmd_withdraw,
        "reroute": cmd_reroute,
        "retract-amendment": cmd_retract_amendment,
    }[args.command]

    event = handler(args, item)

    # For non-reroute modes, write the file. (reroute already wrote during move.)
    if args.command != "reroute":
        _atomic_write_json(args.file, item)

    auto_close_key = {"supersede": "supersede", "duplicate": "duplicate", "withdraw": "withdraw"}.get(args.command)
    if auto_close_key:
        _maybe_auto_close(args, item, event, auto_close_key)

    print(f"OK: {args.command} amendment {event['amendment_id']} applied to {args.file}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
