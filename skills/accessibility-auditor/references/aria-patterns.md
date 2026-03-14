# ARIA Patterns: Production Implementation

## The Five Rules of ARIA

1. **No ARIA is better than bad ARIA.** Incorrect ARIA actively harms users. A `<div>` with no role is neutral; a `<div role="button">` without keyboard handling is a lie.
2. **Use native HTML first.** `<button>`, `<a>`, `<input>`, `<select>`, `<details>` have built-in semantics, keyboard behavior, and focus management. ARIA adds nothing to them.
3. **All interactive ARIA elements must be keyboard operable.** Adding `role="button"` without `tabindex="0"` and `keydown` handlers is an accessibility violation, not an improvement.
4. **Do not use `aria-hidden="true"` on focusable elements.** This creates ghost elements -- invisible to screen readers but reachable by keyboard. The user lands on them and hears nothing.
5. **All interactive elements must have accessible names.** Via content, `aria-label`, `aria-labelledby`, or the HTML `<label>` element.

## Decision Tree: Native vs ARIA

- Need a clickable action? --> Use `<button>`. Not `<div role="button">`.
- Need navigation? --> Use `<a href>`. Not `<span role="link">`.
- Need a checkbox? --> Use `<input type="checkbox">`. Not `<div role="checkbox">`.
- Need a dropdown? --> Use `<select>`. Only use ARIA combobox if you need autocomplete/filtering.
- Need expandable content? --> Use `<details>/<summary>`. Only use ARIA if you need animation or custom styling that `<details>` cannot support.
- Need a dialog? --> Use `<dialog>` element (modern browser support is now sufficient). Add ARIA only if you must support older browsers.

If no native element exists for your pattern (tree view, menu bar, tab interface, combobox with filtering), then ARIA is appropriate.

## Modal Dialog Pattern

**Required attributes:**
- Container: `role="dialog"`, `aria-modal="true"`, `aria-labelledby="[title-id]"`
- Optional: `aria-describedby="[description-id]"` for additional context

**Focus management:**
1. On open: move focus to the first focusable element inside the dialog (or the dialog itself if no focusable children). Store the element that triggered the dialog.
2. While open: trap focus. Tab from last focusable element wraps to first. Shift+Tab from first wraps to last.
3. On close: restore focus to the triggering element. Remove `aria-hidden` from background content.
4. Background: add `aria-hidden="true"` to all content outside the dialog. Use `inert` attribute where supported (progressive enhancement).

**Keyboard:**
- Escape: close the dialog
- Tab / Shift+Tab: cycle through focusable elements within the dialog
- Do NOT close on backdrop click alone -- always provide an explicit close button

**Common mistake:** Forgetting to restore focus on close. The user pressed a button, a dialog appeared, they closed it, and now focus is lost (jumps to `<body>`). This is disorienting for keyboard and screen reader users.

## Combobox / Autocomplete Pattern

**Roles and structure:**
- Input: `role="combobox"`, `aria-expanded="true|false"`, `aria-autocomplete="list|both|none"`, `aria-controls="[listbox-id]"`, `aria-activedescendant="[option-id]"`
- Listbox: `role="listbox"`, `id="[listbox-id]"`
- Options: `role="option"`, `aria-selected="true|false"`

**Keyboard:**
- Down Arrow: open listbox (if closed), move highlight to next option
- Up Arrow: move highlight to previous option
- Enter: select highlighted option, close listbox
- Escape: close listbox without selecting, clear input if listbox was already closed
- Home / End: move to first / last option
- Type-ahead: filter options as user types (debounce 300ms)

**Live announcements:**
- When results load: announce count via `aria-live="polite"` region ("5 results available")
- When no results: announce "No results found"
- When selection changes: `aria-activedescendant` update causes screen reader to announce the newly highlighted option

**Screen reader quirk:** JAWS in forms mode requires `role="combobox"` on the input itself. NVDA announces the listbox label when the combobox opens. VoiceOver requires explicit `aria-activedescendant` updates (it does not track DOM focus within listbox).

## Tab Interface Pattern

**Roles and structure:**
- Tab list: `role="tablist"`, `aria-label="[descriptive-label]"`
- Tabs: `role="tab"`, `aria-selected="true|false"`, `aria-controls="[panel-id]"`
- Panels: `role="tabpanel"`, `aria-labelledby="[tab-id]"`

**Focus management (roving tabindex):**
- Active tab: `tabindex="0"`
- Inactive tabs: `tabindex="-1"`
- Tab key: moves focus OUT of the tablist (into the panel), not to the next tab
- Arrow keys: move between tabs within the tablist

**Keyboard:**
- Left/Right Arrow (horizontal tabs): move to previous/next tab
- Up/Down Arrow (vertical tabs): move to previous/next tab
- Home: move to first tab
- End: move to last tab
- Space/Enter: activate the focused tab (only needed if tabs are NOT auto-activated)

**Auto-activation vs manual activation:**
- Auto (recommended): arrow key focus change immediately shows the corresponding panel
- Manual: arrow keys move focus, Enter/Space activates. Use when panel loading is expensive.

## Tree View Pattern

**Roles:** `role="tree"` > `role="treeitem"` with nested `role="group"` for children.

**Required attributes:**
- Expandable items: `aria-expanded="true|false"`
- Items with children: contain a `role="group"` wrapping child treeitems
- Selected items: `aria-selected="true|false"` (if selection is supported)
- Current item: managed via `aria-activedescendant` on the tree or roving tabindex on items

**Keyboard:**
- Up/Down Arrow: move to previous/next visible treeitem
- Right Arrow: expand closed node, or move to first child if already expanded
- Left Arrow: collapse open node, or move to parent if already collapsed
- Home / End: first / last visible treeitem
- Enter: activate the item (perform its default action)
- `*` (asterisk): expand all siblings at the current level

## Live Regions

**Choosing the right politeness level:**
- `aria-live="polite"`: announcement waits until user is idle. Use for: status updates, search results count, save confirmations, non-urgent notifications.
- `aria-live="assertive"`: interrupts current speech immediately. Use ONLY for: error alerts, session timeout warnings, critical system messages. Overuse of assertive trains users to ignore announcements.
- `role="status"`: implicit `aria-live="polite"`. Use for status messages.
- `role="alert"`: implicit `aria-live="assertive"`. Use for error messages.

**Critical implementation detail:** The live region container must exist in the DOM BEFORE content is injected. Dynamically creating a container with `aria-live` and immediately adding content will NOT trigger an announcement in most screen readers. Best practice: render an empty `aria-live` container on page load, then update its text content when announcements are needed.

**`aria-atomic` behavior:**
- `aria-atomic="true"`: screen reader reads the ENTIRE region when any part changes. Use for: time displays, score counters, short status messages.
- `aria-atomic="false"` (default): only the changed nodes are announced. Use for: chat logs, feed updates, long lists.

## Common ARIA Mistakes

| Mistake | Problem | Fix |
|---------|---------|-----|
| `<div role="button">` without `tabindex="0"` | Not keyboard focusable | Add `tabindex="0"` and keydown handler for Enter/Space |
| `role="menu"` for site navigation | `menu` role is for application menus (like File/Edit), not nav | Use `<nav>` with `<ul>/<li>/<a>` for site navigation |
| `aria-label` on non-interactive `<div>` | Most screen readers ignore `aria-label` on generic elements | Use `aria-label` on landmarks, form fields, interactive elements only |
| `aria-hidden="true"` on parent with focusable child | Creates invisible keyboard traps | Ensure no focusable descendants exist, or use `inert` instead |
| `role="listbox"` without `role="option"` children | Invalid ARIA; screen reader behavior undefined | Required children must match role's specification |
| `aria-expanded` on element without expandable content | Misleads users into expecting toggleable content | Only use when content actually expands/collapses |

## Screen Reader Rendering Differences

| Pattern | NVDA (Firefox) | JAWS (Chrome) | VoiceOver (Safari) |
|---------|---------------|---------------|---------------------|
| `aria-describedby` | Reads after a pause | Reads after name | May require VO+F3 to hear |
| `aria-live="polite"` | Queues reliably | Sometimes drops if rapid updates | Reliable but delayed |
| `role="application"` | Disables browse mode | Disables virtual cursor | Minimal effect; avoid this role |
| `aria-activedescendant` | Works in both modes | Requires forms mode | Requires explicit ID updates |
| `<dialog>` native | Good support | Good support | Announced as "web dialog" |
| `aria-errormessage` | Limited support | Good support | Not yet supported (use `aria-describedby` fallback) |

Key takeaway: always test with at least two screen reader + browser combinations. NVDA+Firefox and VoiceOver+Safari cover the widest range of rendering differences. JAWS+Chrome is the enterprise standard.
