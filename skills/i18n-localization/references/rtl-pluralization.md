# RTL Support and Complex Pluralization

Production-grade RTL implementation and CLDR plural rules. These are the details that separate "works in demo" from "works in production across 30+ locales."

---

## CSS Logical Properties Complete Reference

Physical properties assume LTR. Logical properties adapt to text direction automatically. Replace every physical property -- there are no exceptions.

| Physical Property | Logical Replacement | Behavior in RTL |
|-------------------|---------------------|-----------------|
| `margin-left` | `margin-inline-start` | Becomes right margin |
| `margin-right` | `margin-inline-end` | Becomes left margin |
| `padding-left` | `padding-inline-start` | Becomes right padding |
| `padding-right` | `padding-inline-end` | Becomes left padding |
| `border-left` | `border-inline-start` | Applies to right side |
| `border-right` | `border-inline-end` | Applies to left side |
| `left` (positioning) | `inset-inline-start` | Becomes right position |
| `right` (positioning) | `inset-inline-end` | Becomes left position |
| `text-align: left` | `text-align: start` | Becomes right-aligned |
| `text-align: right` | `text-align: end` | Becomes left-aligned |
| `float: left` | `float: inline-start` | Floats right |
| `border-radius: 4px 0 0 4px` | `border-start-start-radius: 4px` | Radius follows direction |
| `top` | `inset-block-start` | Unchanged (block axis) |
| `bottom` | `inset-block-end` | Unchanged (block axis) |
| `width` | `inline-size` | Unchanged semantically |
| `height` | `block-size` | Unchanged semantically |

**Shorthand conversion:**
```css
/* Physical (breaks in RTL) */
.card { margin: 0 2rem 0 1rem; padding: 1rem 2rem 1rem 0.5rem; }

/* Logical (works in all directions) */
.card {
  margin-block: 0;
  margin-inline: 1rem 2rem;  /* start end */
  padding-block: 1rem;
  padding-inline: 0.5rem 2rem;
}
```

---

## Icon Mirroring Rules

Not all icons should mirror in RTL. This is a common source of bugs.

**Icons that MUST mirror (directional meaning):**
- Arrow icons (back, forward, navigation)
- Chevrons (expand/collapse when indicating direction)
- Text indent/outdent icons
- List bullet alignment indicators
- Progress bars and sliders
- Undo/redo arrows
- Reply/forward icons in email

**Icons that must NOT mirror:**
- Checkmarks and X marks (universal symbols)
- Media playback (play/pause/stop -- standardized worldwide)
- Clock icons (clockwise is universal)
- Search magnifying glass
- Heart, star, and other abstract symbols
- Brand logos
- Mathematical operators (+, -, =)
- Music notes
- Phone receiver icon

**Implementation:**
```css
/* Mirror all directional icons when in RTL context */
[dir="rtl"] .icon--directional { transform: scaleX(-1); }

/* Or use logical properties on the icon container */
.breadcrumb-separator::after {
  content: "\203A";  /* Right-pointing angle bracket */
}
[dir="rtl"] .breadcrumb-separator::after {
  content: "\2039";  /* Left-pointing angle bracket */
}
```

---

## Bidirectional Text Handling

Mixed-direction content (e.g., Arabic text containing English brand names or URLs) is where most RTL implementations break.

**The `<bdi>` element (bidirectional isolation):**
```html
<!-- Without bdi: "Product 42ABC" can reorder digits in RTL context -->
<p>{{ t('order.product') }}: <bdi>{{ productCode }}</bdi></p>
```

**Unicode bidirectional control characters:**
- `\u200F` (RLM -- Right-to-Left Mark): Force RTL context for ambiguous characters
- `\u200E` (LRM -- Left-to-Right Mark): Force LTR context
- `\u2066` (LRI -- Left-to-Right Isolate): Start LTR isolation
- `\u2069` (PDI -- Pop Directional Isolate): End isolation

**Common bidirectional bugs:**
| Scenario | Bug | Fix |
|----------|-----|-----|
| Email address in RTL text | `user@example.com` renders as `com.example@user` | Wrap in `<bdi>` or `<span dir="ltr">` |
| Phone number with parentheses | `(555) 123-4567` parentheses misplaced | Wrap in `<bdi dir="ltr">` |
| Mixed Arabic + numbers | `3 items` becomes `items 3` (correct in RTL) but `item #3` does not reorder correctly | Use `<bdi>` for the number token |
| URL in RTL paragraph | Path separators and dots render in wrong order | Always wrap URLs in `<span dir="ltr">` |
| Currency with code | `USD 100` may display as `100 USD` unexpectedly | Use `Intl.NumberFormat` which handles placement per locale |

---

## CLDR Plural Rules

The Unicode CLDR defines plural categories per language. English (one/other) is the simplest case. Most languages are far more complex.

**Plural categories (CLDR standard):**
| Category | When Used | Example Languages |
|----------|-----------|-------------------|
| `zero` | Exactly 0 | Arabic, Latvian, Welsh |
| `one` | Singular or special | English (1), French (0, 1), Russian (1, 21, 31...) |
| `two` | Dual form | Arabic (2), Hebrew (2), Slovenian (2, 102) |
| `few` | Small quantities | Polish (2-4, 22-24), Czech (2-4), Arabic (3-10) |
| `many` | Large quantities | Polish (5-21, 25-31), Arabic (11-99), Russian (5-20) |
| `other` | Everything else | All languages (required fallback) |

**Why this matters -- Polish example:**
```
1 plik        (one)     -- 1 file
2 pliki       (few)     -- 2-4 files
5 plikow      (many)    -- 5-21 files
22 pliki      (few)     -- 22-24 files (cycles!)
100 plikow    (other)   -- 100 files
```
Simple one/other pluralization shows "5 pliki" instead of "5 plikow" -- grammatically wrong.

**Arabic plural rules (all 6 categories used):**
```
0 -- zero    (no items)
1 -- one     (1 item)
2 -- two     (2 items, dual form)
3-10 -- few  (3-10 items)
11-99 -- many (11-99 items)
100+ -- other
```

**ICU MessageFormat for full plural support:**
```
{count, plural,
  zero {No files}
  one {# file}
  two {# files (dual)}
  few {# files}
  many {# files}
  other {# files}
}
```
The ICU library automatically selects the correct category per locale using CLDR rules. You supply all forms; the runtime picks the right one.

---

## ICU MessageFormat Deep Dive

**Nested selects (gender + plural):**
```
{hostGender, select,
  female {{guestCount, plural,
    =0 {{hostName} does not give a party}
    one {{hostName} invites {guestName} to her party}
    other {{hostName} invites {guestCount} people to her party}
  }}
  male {{guestCount, plural,
    =0 {{hostName} does not give a party}
    one {{hostName} invites {guestName} to his party}
    other {{hostName} invites {guestCount} people to his party}
  }}
  other {{guestCount, plural,
    =0 {{hostName} does not give a party}
    one {{hostName} invites {guestName} to their party}
    other {{hostName} invites {guestCount} people to their party}
  }}
}
```
This is the canonical ICU complexity test. If your i18n library cannot handle this, it cannot handle production localization.

**Escaping curly braces:**
```
// To display literal braces in ICU format, use single quotes
'{' yields literal {
'literal {text}' yields literal {text}
```

**Custom number/date formatting in ICU:**
```
// Number skeleton syntax
{price, number, ::currency/USD precision-integer}
{percent, number, ::percent .00}

// Date skeleton syntax
{date, date, ::dMMMMyyyy}      // "March 15, 2026" or "15 marzo 2026"
{time, time, ::jmm}            // "3:30 PM" or "15:30" depending on locale
```

---

## Testing RTL

**Pseudo-localization for RTL testing:**
Generate a pseudo-RTL locale that reverses strings and adds RTL markers without needing actual translations. This catches layout bugs instantly.

```javascript
// Pseudo-RTL generator
function pseudoRTL(str) {
  const rtlMap = { 'a': '\u0627', 'b': '\u0628', 'e': '\u0639', 'o': '\u0648' };
  return '\u200F' + str.split('').reverse().map(c => rtlMap[c] || c).join('') + '\u200F';
}
```

**Common RTL visual bugs checklist:**
- [ ] Sidebar appears on the right side
- [ ] Breadcrumbs read right-to-left with correct separators
- [ ] Form labels align to the right of inputs
- [ ] Scroll direction is correct in horizontal carousels
- [ ] Dropdown menus open to the left
- [ ] Toast/notification slides in from the left
- [ ] Progress bars fill from right to left
- [ ] Tables maintain correct column order
- [ ] Shadows and gradients flip correctly
- [ ] Border-radius corners are on correct sides

**Browser dev tools RTL simulation:**
```javascript
// Quick RTL toggle for testing (paste in console)
document.documentElement.dir = document.documentElement.dir === 'rtl' ? 'ltr' : 'rtl';
document.documentElement.lang = document.documentElement.dir === 'rtl' ? 'ar' : 'en';
```

**Automated RTL testing with Playwright:**
```typescript
test('layout renders correctly in RTL', async ({ page }) => {
  await page.goto('/ar/dashboard');
  const sidebar = page.locator('.sidebar');
  const box = await sidebar.boundingBox();
  // Sidebar should be on the right side in RTL
  expect(box.x).toBeGreaterThan(page.viewportSize().width / 2);
});
```
