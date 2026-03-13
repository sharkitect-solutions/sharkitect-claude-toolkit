# Advanced Trigger Engineering

Load when implementing custom popup triggers beyond basic scroll/time/exit, building engagement scoring systems for popup targeting, implementing session-aware frequency capping, or debugging trigger conflicts between multiple popups. Also load when the user wants cursor trajectory prediction, scroll velocity analysis, or idle detection. Do NOT load for popup copy, design decisions, or legal compliance.

## Scroll Velocity Detection

Scroll speed reveals intent. Fast downward scroll = scanning. Slow scroll = reading. Fast upward scroll = leaving.

### Implementation

```
// Track scroll velocity over 100ms intervals
let lastScrollY = window.scrollY;
let lastTime = performance.now();

const velocityCheck = setInterval(() => {
  const currentY = window.scrollY;
  const currentTime = performance.now();
  const deltaY = currentY - lastScrollY;
  const deltaT = currentTime - lastTime;

  const velocity = deltaY / deltaT;  // px/ms
  // Positive = scrolling down, Negative = scrolling up

  lastScrollY = currentY;
  lastTime = currentTime;

  // Trigger on fast upward scroll (leaving signal)
  if (velocity < -0.6) {  // 600px/sec upward
    showExitPopup();
    clearInterval(velocityCheck);
  }
}, 100);
```

### Velocity Thresholds

| Velocity (px/ms) | Behavior | Meaning | Trigger? |
|---|---|---|---|
| 0.0 to 0.2 | Slow downward scroll | Active reading | NO -- user is engaged, do not interrupt |
| 0.2 to 0.5 | Moderate downward scroll | Scanning/browsing | MAYBE -- acceptable for non-intrusive slide-in if engagement threshold met |
| 0.5+ | Fast downward scroll | Skimming, looking for specific content | NO -- user is searching, interruption will frustrate |
| -0.1 to -0.3 | Slow upward scroll | Re-reading, going back to check something | NO -- user is re-engaging with content |
| -0.3 to -0.6 | Moderate upward scroll | Looking for navigation or missed information | MAYBE -- only if combined with other exit signals |
| Below -0.6 | Fast upward scroll | Heading to top to leave or navigate away | YES -- strongest mobile exit proxy. Show exit-save popup |

**Mobile adjustment**: Mobile scroll velocity is naturally 1.5-2x faster than desktop due to flick gestures. Multiply desktop thresholds by 1.5 for mobile: exit trigger at -0.9 px/ms instead of -0.6.

## Cursor Trajectory Prediction (Desktop Only)

Predict where the cursor is heading BEFORE it reaches the browser edge. This allows earlier popup trigger (200-400ms before standard exit intent).

### How It Works

Track cursor position every 50ms. Fit a linear regression to the last 5-8 data points. If the projected trajectory crosses the top edge of the viewport within the next 300ms, trigger the popup.

### Trajectory Categories

| Trajectory | Detection | Meaning | Action |
|---|---|---|---|
| Moving toward address bar (top, center-left) | Y decreasing, X moving toward 200-600px range | Likely typing a new URL | Trigger exit popup |
| Moving toward tab close (top-right) | Y decreasing, X moving toward >80% viewport width | Closing tab | Trigger exit popup with higher urgency |
| Moving toward back button (top-left) | Y decreasing, X moving toward <10% viewport width | Going back to previous page | Trigger "before you go" popup |
| Moving toward content area from edge | Y increasing or stable, X moving toward center | Returning to page after brief departure | Do NOT trigger -- user is re-engaging |
| Erratic movement (no clear direction) | High variance in trajectory, frequent direction changes | Reading, mouse following eyes | Do NOT trigger -- normal browsing behavior |

### False Positive Mitigation

| Problem | Cause | Solution |
|---|---|---|
| Popup fires when user reaches for bookmark bar | Cursor moves up but intent is not to leave | Require cursor to leave viewport entirely (`mouseout` event) AND trajectory to match exit pattern. Don't trigger on trajectory alone |
| Popup fires when switching to another tab via keyboard | No cursor movement at all | Combine with `visibilitychange` API instead of cursor tracking for keyboard users |
| Popup fires when scrolling to top of page | On some mice/touchpads, cursor drifts upward during scroll-up | Ignore cursor position changes that coincide with scroll events (within 100ms of a scroll event, suppress trajectory analysis) |

## Engagement Scoring

Assign points based on user behavior. Trigger popups only when engagement score crosses a threshold. This replaces simple time/scroll triggers with a holistic engagement model.

### Scoring Model

| Behavior | Points | Rationale |
|---|---|---|
| Page load | 0 | Baseline. No engagement demonstrated yet |
| Scroll past 25% | +5 | Began consuming content |
| Scroll past 50% | +10 | Meaningful content engagement |
| Scroll past 75% | +15 | Deep engagement |
| Time on page: 30s | +5 | Minimum viable attention |
| Time on page: 60s | +10 | Sustained attention |
| Time on page: 120s+ | +15 | Highly engaged |
| Click on any internal link | +10 | Active exploration |
| Click on image/video | +8 | Interest in media content |
| Scroll-up (re-reading) | +5 | Re-engagement signal |
| 2nd page in session | +15 | Multi-page interest |
| 3rd+ page in session | +20 | Strong session engagement |
| Return visit (cookie detected) | +10 | Returning interest |
| Form field focus (without submit) | +12 | Considered converting but hesitated |

### Threshold Triggers

| Score Threshold | Popup Type | Why This Threshold |
|---|---|---|
| 15-25 | Non-intrusive bottom bar | Minimal engagement -- only show something ignorable |
| 25-40 | Slide-in with offer | Moderate engagement -- earned the right to offer value |
| 40-60 | Center modal with lead magnet | Strong engagement -- user is interested, high conversion probability |
| 60+ | Personalized offer modal | Deep engagement -- tailor the popup to their browsing behavior (e.g., "We noticed you're reading about [topic]") |
| Form focus without submit (+12) | Re-engagement popup after 30s idle | They considered converting. A gentle nudge ("Still have questions? Chat with us") has 5-12% conversion |

### Implementation Architecture

```
class EngagementScorer {
  constructor() {
    this.score = 0;
    this.firedThresholds = new Set();
    this.init();
  }

  addPoints(points, reason) {
    this.score += points;
    this.checkThresholds();
  }

  checkThresholds() {
    const thresholds = [
      { score: 20, popup: 'bottom-bar' },
      { score: 40, popup: 'slide-in' },
      { score: 60, popup: 'modal' }
    ];

    for (const t of thresholds) {
      if (this.score >= t.score && !this.firedThresholds.has(t.score)) {
        this.firedThresholds.add(t.score);
        // Check frequency cap before showing
        if (PopupFrequencyManager.canShow(t.popup)) {
          showPopup(t.popup);
          return;  // Show at most one popup per threshold crossing
        }
      }
    }
  }
}
```

## Session-Aware Frequency Capping

### Storage Architecture

| Storage Layer | What It Stores | Persistence | Limitation |
|---|---|---|---|
| `sessionStorage` | Current session popup state (shown/dismissed/converted) | Until tab closes | Cleared on tab close. New tab = new session. Incognito = always fresh |
| `localStorage` | Cross-session state (last shown timestamp, dismiss count, conversion status) | Until cleared by user | Cleared by "Clear browsing data". 5-10MB limit. Not synced across devices |
| Cookie | Lightweight flag for server-side frequency decisions | Configurable expiry | 4KB limit. Sent with every request (bandwidth cost). Can be blocked by browsers |
| Server-side (API) | Authoritative conversion status, cross-device state | Permanent until deleted | Requires user identification (email, account ID). Only works for known users |

### Frequency Logic Decision Table

| Visitor State | Session Storage | Local Storage | Server Check | Show Popup? |
|---|---|---|---|---|
| New visitor, first session | Empty | Empty | N/A (unknown user) | YES (after engagement threshold) |
| Same session, already saw popup | `shown: true` | -- | -- | NO (max 1 per session) |
| Same session, dismissed popup | `dismissed: true` | Write timestamp | -- | NO (session + start cooldown) |
| New session, dismissed <7 days ago | Empty | `lastDismissed: recent` | -- | NO (cooldown active) |
| New session, dismissed >7 days ago | Empty | `lastDismissed: expired` | -- | YES (cooldown expired) |
| Any session, converted (email captured) | -- | `converted: true` | Check email in DB | NO (permanent suppress for capture popups) |
| Converted user, new device | Empty | Empty | Email found in DB (if logged in) | NO if identifiable. YES if anonymous (unavoidable) |

### Cross-Tab Coordination

If a user has multiple tabs open, showing a popup on Tab A and then showing the same popup on Tab B when they switch is hostile.

```
// Use BroadcastChannel API for cross-tab popup state
const channel = new BroadcastChannel('popup-state');

channel.addEventListener('message', (event) => {
  if (event.data.type === 'popup-shown') {
    suppressAllPopups();  // Another tab showed a popup
  }
});

function showPopup(popupType) {
  channel.postMessage({ type: 'popup-shown', popup: popupType });
  displayPopup(popupType);
}
```

| Browser | BroadcastChannel Support |
|---|---|
| Chrome 54+ | Full support |
| Firefox 38+ | Full support |
| Safari 15.4+ (2022) | Full support |
| Edge 79+ | Full support |

**Fallback for older Safari**: Use `localStorage` event listener. Writing to `localStorage` fires a `storage` event in other tabs (but NOT the tab that wrote it).

## Idle Detection for Re-Engagement

Detect when a user stops interacting (idle) and use it as a re-engagement signal.

| Idle Duration | Likely State | Popup Strategy |
|---|---|---|
| 15-30 seconds | Reading long content or processing information | NO popup -- this is normal reading behavior |
| 30-60 seconds | Distracted or multi-tasking | MAYBE -- only if engagement score is >30 and form field was previously focused |
| 60-120 seconds | Likely switched focus to another tab/app | Show re-engagement on return (`visibilitychange`) instead of during idle |
| 120+ seconds | Session effectively abandoned | Do not show popup. The user has left. Save the trigger for their next visit |

### Idle Detection Implementation

```
let idleTimer;
const IDLE_THRESHOLD = 60000; // 60 seconds

function resetIdle() {
  clearTimeout(idleTimer);
  idleTimer = setTimeout(onIdle, IDLE_THRESHOLD);
}

// Track meaningful interactions (not just mousemove)
['click', 'scroll', 'keydown', 'touchstart'].forEach(event => {
  document.addEventListener(event, resetIdle, { passive: true });
});

function onIdle() {
  // User has been idle for 60s
  // Don't show popup now -- wait for re-engagement
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      showReengagementPopup();  // "Welcome back!" with contextual offer
    }
  }, { once: true });
}
```

**Do NOT use `mousemove` for idle detection.** Users reading content don't move the mouse. `mousemove` detects physical inactivity, not cognitive inactivity. Use `scroll`, `click`, `keydown`, and `touchstart` as the interaction signals.
