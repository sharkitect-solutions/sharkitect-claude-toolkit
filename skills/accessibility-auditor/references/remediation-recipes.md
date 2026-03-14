# Remediation Recipes: Fix Patterns by WCAG Criterion

## 1.1.1 Non-text Content (Level A) -- Alt Text Decision Tree

**Is the image informative?**
- YES, conveys content --> `alt="[describe what the image communicates, not what it looks like]"`
- YES, is a functional control (icon button, linked image) --> `alt="[describe the action]"` (e.g., "Search", "Close", "Download PDF")
- YES, contains complex data (chart, graph, diagram) --> Short alt + long description via `aria-describedby` or adjacent text
- NO, purely decorative --> `alt=""` (empty string, NOT omitting the attribute)
- NO, redundant with adjacent text --> `alt=""` (decorative in context)

**Common mistakes:**
- "image of..." or "picture of..." prefixes (screen readers already announce "image")
- Alt text describing visual appearance instead of meaning ("blue circle" vs "status: online")
- CMS auto-generating alt from filename ("IMG_2847.jpg")
- Missing alt on `<input type="image">` (must describe the action, not the image)

## 1.3.1 Info and Relationships (Level A) -- Heading Hierarchy

**Rules:**
- Exactly one `<h1>` per page (the page title)
- Headings must not skip levels (h1 > h3 without h2 is invalid)
- Headings must reflect content structure, not visual styling
- Use CSS for visual sizing; use heading elements for semantic structure

**Repair checklist:**
1. Map the current heading tree: extract all h1-h6 elements in DOM order
2. Identify skips (h2 to h4), duplicates at wrong levels, missing h1
3. Restructure: if visual design requires different sizing, use CSS classes on correct heading levels
4. Data tables: add `<th scope="col">` for column headers, `<th scope="row">` for row headers
5. Layout tables (if unavoidable): add `role="presentation"` to suppress table semantics

## 1.4.3 Contrast (Level AA) -- Automated Fixing Workflow

**Step 1: Extract all color pairs.** Use axe-core or browser DevTools to identify all failing text/background combinations.

**Step 2: For each failure, choose a fix strategy:**
- Darken the text color (most common, least disruptive to brand)
- Lighten the background color
- Add a semi-transparent overlay behind text on images
- Increase font size to qualify as "large text" (3:1 threshold instead of 4.5:1)

**Step 3: Dark mode considerations.**
Dark mode is not exempt from contrast requirements. Common dark mode failures:
- Gray text on dark gray background (#888 on #333 = 3.5:1, fails AA)
- Link colors that meet contrast on light but fail on dark backgrounds
- Placeholder text that becomes invisible in dark mode
- SVG icons that do not adapt to dark backgrounds

**Step 4: Verify dynamically themed content.** If users can customize colors (themes, branded portals), validate all possible combinations or enforce minimum contrast programmatically.

## 2.1.1 Keyboard (Level A) -- Component Keyboard Patterns

| Widget | Required Keys | Behavior |
|--------|--------------|----------|
| Button | Enter, Space | Activate the button |
| Link | Enter | Follow the link |
| Checkbox | Space | Toggle checked state |
| Radio group | Arrow keys | Move between options and select |
| Select / listbox | Arrow keys, Enter | Navigate options, select current |
| Slider | Arrow keys, Home, End, Page Up/Down | Adjust value by step, jump to min/max |
| Tab interface | Arrow keys, Home, End | Switch tabs (Tab key moves to panel, not next tab) |
| Tree view | Arrow keys, Enter, * | Expand/collapse, activate, expand all siblings |
| Menu | Arrow keys, Enter, Escape | Navigate items, activate, close |
| Dialog | Tab, Shift+Tab, Escape | Cycle through focusable elements, close |
| Combobox | Arrow keys, Enter, Escape, typing | Navigate suggestions, select, close, filter |

**Universal requirements for all custom controls:**
- Must be focusable (tabindex="0" if not natively focusable)
- Must have visible focus indicator
- Must prevent default on Space key (to avoid page scrolling)
- Must not trap keyboard (user can always Tab or Escape out)

## 2.4.3 Focus Order (Level A) -- Dynamic Content Focus

**SPA Route Changes:**
When the route changes in a single-page application, the browser does NOT reset focus like a full page load. Without intervention, focus stays on the link/button that triggered navigation, which is now potentially gone from the DOM.

**Fix pattern:**
1. After route change, move focus to the new page's `<h1>` or a container with `tabindex="-1"`
2. Announce the new page title via `document.title` update (screen readers read it)
3. Consider a live region announcement: "Navigated to [Page Name]"

**AJAX/Dynamic Content:**
When new content loads into the page (search results, infinite scroll, accordion expansion):
- If user triggered the action: move focus to the new content container
- If content loaded passively (notification, chat message): use `aria-live` region, do NOT steal focus
- If content replaces existing content: move focus to the replacement container

**Lazy-loaded Content and Virtual Scrolling:**
- Lazy-loaded images: include alt text in the initial placeholder markup, not just the loaded image
- Virtual scroll lists: ensure `aria-setsize` and `aria-posinset` are set so screen readers know the total count and current position
- Infinite scroll: provide a "Load More" button alternative (keyboard users cannot "scroll" to trigger loading)

## 2.4.7 Focus Visible (Level AA) -- CSS Focus Patterns

**The `:focus-visible` solution:**
```css
/* Remove default outline for mouse users */
:focus:not(:focus-visible) {
  outline: none;
}
/* Show custom outline for keyboard users */
:focus-visible {
  outline: 3px solid #4A90D9;
  outline-offset: 2px;
}
```

**Why not just `:focus`?** The `:focus` pseudo-class fires on both mouse click and keyboard focus. Designers dislike outlines on clicked buttons. `:focus-visible` fires only when the browser determines focus was set via keyboard (Tab, arrow keys) or programmatically. This gives keyboard users visible focus without annoying mouse users.

**Minimum visibility requirements (WCAG 2.2, 2.4.13 AA):**
- Focus indicator must have at least 2px thickness
- Contrast between focused and unfocused state must be at least 3:1
- Focus indicator must not be fully obscured by other content (2.4.11 Focus Not Obscured)

## 3.3.1 Error Identification (Level A) -- Form Validation Patterns

**Requirements:**
- Error messages must be in text (not just color, not just icon)
- Errors must identify which field is wrong
- Errors must describe what went wrong in human terms ("Enter an email address" not "Invalid input")

**Announcement pattern:**
1. Associate error message with field: `aria-describedby="error-msg-id"` on the input
2. Mark field as invalid: `aria-invalid="true"` on the input
3. On form submission with errors: move focus to the first invalid field OR to a summary of errors at the top of the form
4. Error summary approach: list all errors as links that jump to the corresponding field

**Live error validation (as user types):**
- Debounce validation (500ms minimum) to avoid announcing errors mid-typing
- Use `aria-live="polite"` on the error container
- Clear the error text (not just hide it) when the field becomes valid
- Do NOT validate on blur alone (screen reader users move focus differently than sighted users)

## 4.1.2 Name, Role, Value (Level A) -- Custom Component Audit

For every custom interactive component, verify:

| Property | How to Check | Common Failure |
|----------|-------------|----------------|
| Accessible name | Chrome DevTools > Accessibility tab > Name | Missing aria-label or associated label |
| Role | DevTools > Accessibility tab > Role | Generic "div" or "span" instead of button/link/etc. |
| State | aria-expanded, aria-checked, aria-selected | State not updating on interaction |
| Value | aria-valuenow, aria-valuemin, aria-valuemax | Sliders/progress with no value announcement |
| Description | aria-describedby | Help text not programmatically associated |

## SPA-Specific Patterns

**Route change announcement:**
Maintain a visually hidden `aria-live="polite"` region. On every route change, update its text to the new page title. This replaces the browser's native page-load announcement that SPAs bypass.

**Error boundaries (React):**
When a component crashes behind an error boundary, the replacement error UI must be focusable. If the crashed component held focus, the error boundary must capture and redirect focus to its own content.

**Client-side rendered content:**
Screen readers parse the accessibility tree, not the DOM. If content is rendered client-side after initial page load, ensure the accessibility tree is updated before announcing or focusing the new content. React's `useEffect` with a ref is the standard pattern; `setTimeout(..., 0)` is a fragile workaround.

## React-Specific Patterns

**Focus management with refs:**
Use `useRef` to store references to elements that need programmatic focus. Call `ref.current.focus()` after state updates that change page structure (modal open, route change, error display). Do NOT use `autoFocus` on elements that appear after initial render -- it fires only on mount, not on visibility change.

**Testing with @testing-library:**
- `getByRole('button', { name: 'Submit' })` -- verifies accessible name
- `getByLabelText('Email')` -- verifies label association
- `screen.getByRole('alert')` -- verifies error announcement
- `userEvent.tab()` -- tests keyboard navigation order
- `expect(element).toHaveAttribute('aria-expanded', 'true')` -- tests state management

## Video and Audio Accessibility

**Captions (1.2.2 Level A):**
- Synchronized captions for all prerecorded audio content in video
- Auto-generated captions (YouTube, Rev) are a starting point, not the final deliverable -- error rate is 10-30%
- Captions must include speaker identification and significant sound effects ("[applause]", "[phone ringing]")

**Audio descriptions (1.2.5 Level AA):**
- Narration of visual information not conveyed by the audio track
- Required when video shows something important that is not spoken (on-screen text, visual demonstrations, facial expressions critical to meaning)
- Extended audio descriptions (1.2.7 AAA) pause the video to describe complex visual scenes

**Transcripts (1.2.1 Level A):**
- Text alternative for audio-only content (podcasts, audio clips)
- Must include all spoken content plus significant non-speech sounds
- Should include timestamps for long content

**Media player controls:**
- All controls must be keyboard accessible
- Play/pause must be reachable by Tab and operable by Space/Enter
- Volume, seek, and caption toggle must be keyboard operable
- Controls must have accessible names (not just icons)
- Auto-play is prohibited unless there is a mechanism to pause/stop within 3 seconds
