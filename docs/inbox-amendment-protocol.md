# Inbox Amendment Protocol

**Status:** Active (shipped 2026-04-28, plan Phase B + C complete -- 38/38 tests passing)
**Tool:** `~/.claude/scripts/inbox-amend.py`
**Companion tool:** `~/.claude/scripts/close-inbox-item.py` (extended with `--annotate` + `withdrawn` support)
**Spec:** `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md`

This document is reference material. Authoritative semantics for status vocabulary, Rejected vs Drift-Correction, Superseded vs Duplicate, and Blocked vs Deferred live in `~/.claude/rules/universal-protocols.md`. This file documents the CLI surface, schema, and decision rules that complement those protocols.

---

## When to Amend vs File New vs Withdraw

After filing a work request, routed-task, or lifecycle-review, things change. Severity is reassessed. New evidence comes in. The request is found to be a duplicate. The author changes their mind. Three distinct paths handle these cases.

| Situation | Action | Tool |
|-----------|--------|------|
| Add new context, severity reassessment, evidence, components, links to existing live request | **Amend** | `inbox-amend.py <mode>` |
| Fundamentally different request (different ask, different target, different category that doesn't fit `reclassify`) | **File new** | `work-request.py` (Skill Hub-bound) or direct routed-task creation |
| Newer item supersedes this one with a better-scoped or expanded version | **Amend with `supersede`** | `inbox-amend.py supersede --supersedes <new-id>` |
| Another request was filed for the exact same thing | **Amend with `duplicate`** | `inbox-amend.py duplicate --duplicate-of <surviving-id>` |
| Source no longer wants this work done; request was valid but author retracts | **Amend with `withdraw`** | `inbox-amend.py withdraw` |
| Misfiled / wrong directory / pattern was wrong / triggered by transient fluke | **Drift correction (delete + activity_stream event)** | NOT this CLI -- delete the JSON + Supabase row + insert `event_type='drift_correction'` per universal-protocols.md "Rejected vs Drift-Correction" |
| Target finished the work | **Close** (NOT amend) | `close-inbox-item.py --status completed` |
| Target reviewed and declined on merits | **Close** (NOT amend) | `close-inbox-item.py --status rejected` |
| Target needs to record an in-flight decision without closing (e.g., "deferring to focused session") | **Annotate** | `close-inbox-item.py --annotate` |

**Key decision rule for withdraw vs drift-correction:** Ask "would this request have been correctly filed if the author had the information they have now?" If YES, it's a real request the author still stands behind but no longer wants done -> withdraw. If NO (the request should never have existed), it's drift -> delete + drift_correction.

**Key constraint:** Only the originating workspace may amend its own filed items. `--from <canonical>` must match the item's `source_workspace` (for WRs) or `routed_from` (for routed-tasks). If you need a target-side modification, use `close-inbox-item.py --annotate` or coordinate via a new routed-task. Cross-workspace direct Edit on inbox files is denied at the permissions layer.

**Key constraint: status guard.** Amendments are allowed only when item status is in `{new, pending, deferred}`. Once the target sets `in_progress` or any close state (`completed | rejected | superseded | duplicate | withdrawn`), source amendments are locked. To unlock, the target manually sets status back to `pending`. After close, no amendment is allowed -- ever.

---

## All 13 Amendment Modes

Counted: 1 add-context, 2 severity-update, 3 priority-update, 4 component-add, 5 component-remove, 6 add-evidence, 7 link-related, 8 reclassify, 9 supersede, 10 duplicate, 11 withdraw, 12 reroute, 13 retract-amendment. Plus `bulk-amend` (the 14th subcommand, runs any of the above 13 across multiple files).

### Common arguments (every mode -- except bulk-amend)

| Flag | Required | Notes |
|------|----------|-------|
| `--file <path>` | Yes | Inbox JSON file to amend. |
| `--from <workspace>` | Yes | Canonical workspace name. Must match `source_workspace` or `routed_from`. Choices: `workforce-hq`, `skill-management-hub`, `sentinel`. |
| `--reason <text>` | Yes | Human-readable explanation. Must be `>= 10` characters. |
| `--note <text>` | No | Free-form additional context. Stored in event's `notes` field. |
| `--amendment-id <id>` | No | Override the auto-generated id (used for idempotent replay). Format: `amend-<YYYY-MM-DD>-<8-char-hex>`. |

### 1. add-context

Free-form addition: extra detail, follow-up note, narrative update.

```bash
python ~/.claude/scripts/inbox-amend.py add-context \
  --file "//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "User reported the same symptom on Sentinel; broader scope than initial filing" \
  --note "Affects all 3 workspaces, not just HQ. Updating priority next."
```

### 2. severity-update

Change `severity` field. Logs old + new in `fields_changed`.

```bash
python ~/.claude/scripts/inbox-amend.py severity-update \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Repro on production confirmed; original severity was understated" \
  --new-severity critical
```

Choices for `--new-severity`: `info | warning | high | critical`.

### 3. priority-update

Change `priority` field. Logs old + new.

```bash
python ~/.claude/scripts/inbox-amend.py priority-update \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Now blocking morning brief delivery -- escalating per user request" \
  --new-priority high
```

Choices for `--new-priority`: `low | medium | high | critical`.

### 4. component-add

Append to the `components` list. Deduplicates against existing entries.

```bash
python ~/.claude/scripts/inbox-amend.py component-add \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Investigation revealed n8n CEO brief workflow + error-autofix bridge both involved" \
  --components "n8n-ceo-briefs,error-autofix-bridge"
```

Comma-separated component names.

### 5. component-remove

Remove entries from the `components` list.

```bash
python ~/.claude/scripts/inbox-amend.py component-remove \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Telegram bot was a red herring; not a component of this issue" \
  --components "telegram-hq-bot"
```

### 6. add-evidence

Append a structured evidence entry to the `evidence` array AND the event's `structured_data.evidence`.

```bash
python ~/.claude/scripts/inbox-amend.py add-evidence \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Captured n8n execution log showing the failure mode" \
  --evidence-type log \
  --evidence-ref "https://sharkitect-solutions.app.n8n.cloud/execution/12345" \
  --note "Step 7 (Telegram send) timed out at 30s; root cause upstream"
```

Choices for `--evidence-type`: `log | screenshot | trace | url | file`.

### 7. link-related

Add a cross-reference to another inbox item, plan, project, or task.

```bash
python ~/.claude/scripts/inbox-amend.py link-related \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Blocked by Sentinel migration in wr-sentinel-2026-04-26-003" \
  --link-type blocked_by \
  --link-id "wr-sentinel-2026-04-26-003"
```

Choices for `--link-type`: `blocks | blocked_by | related | depends_on`.

### 8. reclassify

Change the `request_type`. Logs old + new.

```bash
python ~/.claude/scripts/inbox-amend.py reclassify \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "On review this is a bug in existing code, not a missing capability" \
  --new-type BUG
```

Choices for `--new-type`: `MISSING | UNUSED | FALLBACK | TASK | BUG | ENHANCE`.

### 9. supersede

Mark this item as superseded by a newer one. **Auto-closes** via `close-inbox-item.py --status superseded --superseded-by <new-id>`.

```bash
python ~/.claude/scripts/inbox-amend.py supersede \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Re-scoped after broader investigation; new wr covers the full surface" \
  --supersedes "wr-hq-2026-04-28-007"
```

After this runs: file moves to `processed/`, status set to `superseded`, `resolution.superseded_by = "wr-hq-2026-04-28-007"`, completion notification routed-task auto-written to source workspace's inbox (in this case, HQ's own -- self-filed gets skipped per protocol).

### 10. duplicate

Mark this item as a duplicate of an existing surviving item. **Auto-closes** via `close-inbox-item.py --status duplicate --duplicate-of <surviving-id>`.

```bash
python ~/.claude/scripts/inbox-amend.py duplicate \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Sentinel filed wr-sentinel-2026-04-27-002 two days earlier with better scope" \
  --duplicate-of "wr-sentinel-2026-04-27-002"
```

After this runs: status set to `duplicate`, `resolution.duplicate_of` populated, file moved to `processed/`.

### 11. withdraw

Source pulls back a request that was valid but no longer wanted. **Auto-closes** with status `withdrawn`.

```bash
python ~/.claude/scripts/inbox-amend.py withdraw \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "Decided to defer the underlying initiative; not pursuing this fix in current quarter"
```

After this runs: status set to `withdrawn`, file moved to `processed/`.

**Note:** Supabase migration to add `withdrawn` to `cross_workspace_requests.inbox_items_status_check` is filed to Sentinel via plan Phase G. Until that ships, the Supabase POST on a withdraw close will be rejected by the CHECK constraint -- expect a soft Supabase error in the close output. The local JSON close still succeeds.

### 12. reroute

Move the item from one target workspace's inbox to another. Updates `routed_to` and appends to `routed_to_history`. Performs an actual file move (atomic write to destination, then unlink source).

```bash
python ~/.claude/scripts/inbox-amend.py reroute \
  --file "//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/4.- Sentinel/.routed-tasks/inbox/rt-hq-2026-04-28-old-target.json" \
  --from workforce-hq \
  --reason "On review this is Skill Hub territory (skill modification), not Sentinel monitoring" \
  --new-target skill-management-hub \
  --new-target-inbox-dir "//c/Users/Sharkitect Digital/Documents/Claude Code Workspaces/3.- Skill Management Hub/.work-requests/inbox"
```

**Collision check:** If the destination already has a file with the same name, reroute aborts with an error. Rename the source or pick a different destination.

Choices for `--new-target`: `workforce-hq | skill-management-hub | sentinel`.

### 13. retract-amendment

Undo a prior amendment without removing it from history. The original event stays, but its `retracted` flag flips to `true`. A new event records the retraction.

```bash
python ~/.claude/scripts/inbox-amend.py retract-amendment \
  --file "<path>/wr-hq-2026-04-28-001.json" \
  --from workforce-hq \
  --reason "The severity bump was based on a misread log; reverting to original assessment" \
  --retracts-amendment "amend-2026-04-28-a1b2c3d4"
```

**Important:** retract-amendment does NOT roll back the top-level field changes the original amendment made (e.g., it does not flip `severity` back to its pre-amendment value). It only marks the original event as retracted in the history. If you also want to reverse a field change, follow up with the appropriate amendment (e.g., another `severity-update` to reset).

If the cited `--retracts-amendment` id is not found in `source_amendments[]`, the command exits with `SystemExit` and a clear error.

### bulk-amend

Apply the same amendment across multiple files via subprocess fan-out. **Continue-on-failure:** processes every file even if some fail; reports failures at the end.

```bash
python ~/.claude/scripts/inbox-amend.py bulk-amend \
  --files "<path>/wr-001.json,<path>/wr-002.json,<path>/wr-003.json" \
  --from workforce-hq \
  --mode add-context \
  --reason "Bulk update: all three relate to the n8n cadence engine project" \
  --note "Tagging for project-level rollup"
```

**Behavior:**
- `--files` is comma-separated, no spaces inside paths (or quote the whole list).
- `--mode` is the sub-amendment to run (e.g., `add-context`, `severity-update`).
- `--reason` and `--note` are forwarded to every sub-call.
- On a sub-call failure (e.g., status guard rejected one file, source mismatch on another): bulk-amend continues with the remaining files and prints a summary at the end with the failing file paths, return codes, and stderr excerpts.
- Exit code: `0` if all succeeded; `1` if ANY failed.

**v1 limitation:** bulk-amend does NOT forward mode-specific arguments like `--new-severity` or `--evidence-ref`. If you need to apply a `severity-update` across many files, you currently must call inbox-amend.py once per file (or use a shell loop). bulk-amend is most useful for `add-context` and `link-related` style amendments where the `--reason` + `--note` are sufficient.

**v1 limitation:** bulk-amend's continue-on-failure can leave a mixed state where some files received the amendment and others did not. Always check the summary report. To re-run on the failed subset, fix the cause (often a stale `--from` for a routed-from item, or a status that was set to `in_progress`) and re-execute with the failed paths.

---

## Schema Reference

Every amendment is appended to the item's `source_amendments[]` array. Each event is built by `_build_event` in `inbox-amend.py` and has these fields:

| Field | Type | Source | Meaning |
|-------|------|--------|---------|
| `amendment_id` | string | `args.amendment_id` or `_gen_amendment_id()` | Unique id. Format: `amend-<YYYY-MM-DD>-<8-char-hex>`. Used for idempotent replay -- if this id already exists in `source_amendments[]`, the operation is a no-op. |
| `timestamp` | string (ISO 8601 UTC) | `_now_iso()` | When the amendment was applied. |
| `actor` | string | `args.from_` | Canonical workspace name that filed the amendment. Must match the item's `source_workspace` or `routed_from`. |
| `actor_type` | string | hardcoded `"workspace"` | Reserved for future actor types (user, hook, automation). v1 always `"workspace"`. |
| `amendment_type` | string | mode argument | One of: `add_context`, `severity_update`, `priority_update`, `component_add`, `component_remove`, `add_evidence`, `link_related`, `reclassify`, `supersede`, `duplicate`, `withdraw`, `reroute`, `retract_amendment`. **Note: underscore separator** in the stored value (CLI subcommand uses hyphen, schema uses underscore). |
| `reason` | string | `args.reason` | Human-readable explanation. CLI requires `>= 10` characters at validation time. |
| `fields_changed` | object | mode handler | Map of field-name -> `{from, to}` for top-level field updates. Empty `{}` for modes that don't change top-level fields (e.g., `add_context`, `add_evidence`). Populated for `severity_update`, `priority_update`, `component_add`, `component_remove`, `reclassify`, `reroute`. |
| `structured_data` | object | mode handler | Mode-specific structured payload. Populated for `add_evidence` (`{"evidence": [{type, ref, note}]}`), `link_related` (`{"related_items": [{type, id}]}`), `component_add` (`{"components_added": [...]}`), `component_remove` (`{"components_removed": [...]}`). Empty `{}` otherwise. |
| `notes` | string | `args.note` (or `""`) | Free-form additional context. |
| `supersedes` | string \| null | `args.supersedes` (or null) | Set on `supersede` mode -- id of the newer item that absorbs this one. Null otherwise. |
| `duplicate_of` | string \| null | `args.duplicate_of` (or null) | Set on `duplicate` mode -- id of the surviving canonical item. Null otherwise. |
| `retracts_amendment` | string \| null | `args.retracts_amendment` (or null) | Set on `retract_amendment` mode -- id of the prior amendment being retracted. Null otherwise. |
| `retracted` | boolean | always `false` at write | Becomes `true` on the ORIGINAL event when a later `retract_amendment` cites it. |
| `retracted_at` | string \| null | always `null` at write | Filled on the original event when it gets retracted. |
| `retracted_by_amendment_id` | string \| null | always `null` at write | Filled on the original event with the new amendment's id when retracted. |
| `condition` | null | reserved | Future: conditional amendments ("if status=X then apply"). v1 always null. |
| `template_id` | null | reserved | Future: amendment template library. v1 always null. |
| `expires_at` | null | reserved | Future: time-bounded amendments. v1 always null. |
| `parent_etag` | null | reserved | Future: optimistic concurrency control for AI agents amending the same item simultaneously. v1 always null. |
| `triggers` | list | reserved | Future: amendment-driven re-evaluation in target workspaces. v1 always `[]`. |

The reserved forward-compat fields (`condition`, `template_id`, `expires_at`, `parent_etag`, `triggers`) are deliberately written into every event in v1 so future versions can populate them without a schema migration.

**Top-level item updates.** Some modes also update top-level fields on the item (not just append to `source_amendments[]`):

| Mode | Top-level updates |
|------|-------------------|
| `severity-update` | `severity` |
| `priority-update` | `priority` |
| `component-add` | `components` (extended list) |
| `component-remove` | `components` (filtered list) |
| `reclassify` | `request_type` |
| `reroute` | `routed_to`, `routed_to_history` (appended) |
| `add-evidence` | `evidence[]` (appended) |
| `link-related` | `related_items[]` (appended) |

The other 5 modes (`add-context`, `supersede`, `duplicate`, `withdraw`, `retract-amendment`) do not change top-level fields directly. `supersede`, `duplicate`, and `withdraw` change top-level `status` indirectly via the auto-close call to `close-inbox-item.py`.

---

## Status State Machine

10 states total: 5 open + 5 close. Authoritative diagram lives in the spec at `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md` "Status State Machine" section. Status vocabulary is defined in `~/.claude/rules/universal-protocols.md` "Status Vocabulary Layers" -- do not redefine.

| Layer | Open | Close |
|-------|------|-------|
| Open states | `new`, `pending`, `deferred`, `blocked`, `in_progress` | -- |
| Close states | -- | `completed`, `rejected`, `superseded`, `duplicate`, `withdrawn` |

**Locked transitions** (anything not listed is denied):

| From | To | Who controls | Mechanism |
|------|-----|-------------|-----------|
| (none) | `new` | source | filing tool (`work-request.py`, direct routed-task creation) |
| `new` | `pending` | target | target session triages |
| `pending` | `in_progress` | target | target starts work (locks source amendments) |
| `pending` <-> `deferred` | both directions | target/source | target defers / source defers |
| `pending` -> `blocked` | target | target detects dependency (records `blocked_by`) |
| `blocked` -> `pending` | target | target detects blocker cleared (verifies via Supabase) |
| `in_progress` -> `completed` \| `rejected` | target | `close-inbox-item.py --status` |
| `pending` \| `deferred` -> `superseded` | source | `inbox-amend.py supersede` (auto-closes) |
| `pending` \| `deferred` -> `duplicate` | source | `inbox-amend.py duplicate` (auto-closes) |
| `pending` \| `deferred` -> `withdrawn` | source | `inbox-amend.py withdraw` (auto-closes) |
| (any close) -> (anything) | -- | DENIED. Closed items stay closed. No resurrection. |

---

## Status Transitions per Amendment Mode

| Amendment Mode | Source's pre-condition (item.status must be in) | Item's post-condition status | Side effect |
|----------------|------------------------------------------------|------------------------------|-------------|
| `add-context` | `{new, pending, deferred}` | unchanged | -- |
| `severity-update` | `{new, pending, deferred}` | unchanged | top-level `severity` updated |
| `priority-update` | `{new, pending, deferred}` | unchanged | top-level `priority` updated |
| `component-add` | `{new, pending, deferred}` | unchanged | top-level `components` extended |
| `component-remove` | `{new, pending, deferred}` | unchanged | top-level `components` filtered |
| `add-evidence` | `{new, pending, deferred}` | unchanged | top-level `evidence[]` appended |
| `link-related` | `{new, pending, deferred}` | unchanged | top-level `related_items[]` appended |
| `reclassify` | `{new, pending, deferred}` | unchanged | top-level `request_type` updated |
| `supersede` | `{new, pending, deferred}` | `superseded` | file moved to `processed/`; `resolution.superseded_by` set; auto-completion notification routed-task |
| `duplicate` | `{new, pending, deferred}` | `duplicate` | file moved to `processed/`; `resolution.duplicate_of` set; auto-completion notification routed-task |
| `withdraw` | `{new, pending, deferred}` | `withdrawn` | file moved to `processed/`; auto-completion notification routed-task. **Supabase POST may fail** until Sentinel migration adds `withdrawn` to enum (Phase G). |
| `reroute` | `{new, pending, deferred}` | unchanged | file moved to new target's inbox; top-level `routed_to` updated; `routed_to_history` appended |
| `retract-amendment` | `{new, pending, deferred}` | unchanged | flips a prior amendment's `retracted: true`. Does NOT roll back top-level field changes. |

If status is outside `{new, pending, deferred}`, the CLI exits rc=4 with a "status locked" error. To unlock, the target manually flips status back to `pending` (e.g., via direct Supabase update + manual JSON edit -- this is rare and requires Skill Hub or schema-owner involvement).

---

## Auto-Close Behavior on supersede / duplicate / withdraw

Three modes terminate the item by invoking `close-inbox-item.py`. The mapping (from `inbox-amend.py` line 37-41):

| Amendment mode | close-inbox-item.py `--status` | Required cross-reference flag |
|----------------|-------------------------------|-------------------------------|
| `supersede` | `--status superseded` | `--superseded-by <args.supersedes>` |
| `duplicate` | `--status duplicate` | `--duplicate-of <args.duplicate_of>` |
| `withdraw` | `--status withdrawn` | (none) |

The auto-close call is constructed by `_maybe_auto_close` (line 138). It always passes:
- `--file <args.file>`
- `--status <mapped close status>`
- `--resolved-by <args.from_>`
- `--what-was-done "Source amendment (<mode>): <args.reason>"`
- The cross-reference flag (for supersede / duplicate)

`subprocess.run(argv, check=True)` -- if the close fails for any reason (status guard rejection, file path issue, Supabase POST hard failure), the auto-close raises and `inbox-amend.py` exits with the close's return code. The amendment event is already in `source_amendments[]` because the file write happened BEFORE the auto-close call. This means: a failed auto-close leaves the item with the amendment recorded but status NOT yet flipped. Re-running the same `inbox-amend.py` invocation will hit the idempotent-replay short-circuit (because the `amendment_id` is already present) and will NOT re-attempt the auto-close. To recover: call `close-inbox-item.py` directly with the appropriate `--status` and `--resolved-by`.

`close-inbox-item.py` does its own work as part of the close: writes `resolution`, appends `status_history`, atomic move to `processed/`, best-effort Supabase POST, and writes a completion-notification routed-task to the source workspace's `.routed-tasks/inbox/` per the Completion Notification Protocol (unless `--no-notify` is passed -- which `inbox-amend.py` does NOT pass).

**Self-filed exemption:** When the source is closing its OWN item (e.g., HQ withdrawing its own WR filed to Skill Hub, but the close is invoked by HQ via `--from workforce-hq` -- so `routed_from == workforce-hq` and `resolved_by == workforce-hq`), the completion notification is skipped per the protocol's anti-ping-pong rule. This is correct -- HQ doesn't need to notify itself.

### Hidden test flag: `--close-script-stub`

`_add_common_args` registers `--close-script-stub` with `argparse.SUPPRESS` (hidden from `--help`). When set during testing, `_maybe_auto_close` writes the would-be argv to a JSON stub file instead of invoking subprocess. This is for unit tests only and should not be used in production.

---

## Idempotency / Replay Safety

`inbox-amend.py` checks for replay before applying any mode handler:

```python
def _is_idempotent_replay(item: dict, amendment_id: str) -> bool:
    return any(
        a.get("amendment_id") == amendment_id
        for a in item.get("source_amendments", [])
    )
```

If the caller passes `--amendment-id <id>` (or the auto-generated id was already used in a prior successful run) AND that id is already present in `source_amendments[]`, the script:

1. Prints `Idempotent replay: amendment_id <id> already present, no-op` to stderr.
2. Exits rc=0 without applying anything (no file write, no auto-close).

**When this matters:**

- Re-running a script after a transient failure (network blip on Supabase POST during the auto-close phase) is safe -- the second run does nothing if the first wrote the amendment but the auto-close failed. To complete the close, call `close-inbox-item.py` directly.
- Distributed retry scenarios (an automation retries a failed amendment) won't double-apply.

**Note:** If you do NOT pass `--amendment-id`, the script auto-generates a fresh UUID-based id every time. This means consecutive runs with no explicit id are NOT idempotent -- each run appends a new event. If you want idempotency, capture the amendment_id from the first run's output and pass it on retry.

The output line on success is:

```
OK: <command> amendment <amendment_id> applied to <file>
```

Capture `<amendment_id>` from stdout for retry safety.

---

## Validation Order + Exit Codes

Per `main()` in `inbox-amend.py`:

| Order | Check | Failure exit code | Error |
|-------|-------|-------------------|-------|
| 1 | argparse: `--reason` length `>= 10` | 2 | `--reason must be >= 10 chars (got <N>)` |
| 2 | argparse: choices on `--from`, `--new-severity`, `--new-priority`, `--new-type`, `--evidence-type`, `--link-type`, `--new-target` | 2 | argparse error message |
| 3 | source identity: `_validate_source` | 3 | `Source mismatch: --from=... but item.source_workspace=...` or `Item has neither source_workspace nor routed_from` |
| 4 | status guard: `_validate_status_guard` | 4 | `Item status=<status> is locked -- source amendments only allowed in [...]` |
| 5 | idempotent replay: `_is_idempotent_replay` | 0 | `Idempotent replay: amendment_id <id> already present, no-op` (success exit) |
| 6 | mode handler runs (may raise SystemExit for mode-specific errors like missing `--supersedes` on supersede mode) | 1 (SystemExit default) | Mode-specific |
| 7 | atomic file write | -- | re-raises on tempfile cleanup failure |
| 8 | auto-close (supersede/duplicate/withdraw only) -- subprocess.run(check=True) | close script's rc | -- |

---

## Limitations + Open Items (v1)

| Limitation | Impact | Workaround |
|------------|--------|------------|
| `source_amendments[]` array grows unbounded | A long-lived item (months of amendments) accumulates history. JSON file size grows. | Acceptable in v1. Items typically close within days. If an item amasses 50+ amendments, treat that as a signal to file new and supersede the old. |
| `bulk-amend` does not forward mode-specific args (e.g., `--new-severity`) | Only `add-context`-style amendments work cleanly across many files. | For mode-specific bulk operations, write a shell `for` loop over files. |
| `bulk-amend` continue-on-failure can produce mixed state | Some files amended, others not. | Always read the summary report. Re-run on the failed subset. |
| `withdrawn` not yet in Supabase enum | Supabase POST on withdraw close fails with CHECK constraint rejection. | Local JSON close still succeeds. Sentinel migration filed via plan Phase G. |
| `retract-amendment` does NOT reverse top-level field changes | A retracted `severity-update` still leaves the new `severity` value on the item. | Follow up with a fresh `severity-update` to reset the value if desired. |
| `--close-script-stub` is a hidden test flag | Not user-facing. | Don't use it outside tests. |
| Only canonical workspace names accepted | An ad-hoc workspace name in `--from` is rejected. | Add the new workspace to `CANONICAL_WORKSPACES` in `inbox-amend.py` AND the templates JSON (see permissions-architecture.md "Adding a new workspace" walkthrough). |

---

## See Also

- `~/.claude/docs/permissions-architecture.md` -- why direct Edit on inbox files is denied.
- `~/.claude/docs/permissions-emergency-override.md` -- when the deny is in your way.
- `~/.claude/rules/universal-protocols.md` -- Status Vocabulary Layers, Rejected vs Drift-Correction, Superseded vs Duplicate, Blocked vs Deferred. Authoritative for inbox semantics.
- `~/.claude/scripts/close-inbox-item.py` -- companion tool. The 5 close states (`completed | rejected | superseded | duplicate | withdrawn`) plus `--annotate` mode. `processed | resolved` auto-deprecate to `completed` with stderr warning.
- `<Skill Hub>/docs/superpowers/specs/2026-04-28-permissions-and-inbox-amendment-system-design.md` -- design rationale for amendments, permissions, and the validated CLI layer.
