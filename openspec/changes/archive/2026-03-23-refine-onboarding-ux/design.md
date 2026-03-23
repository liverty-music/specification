## Design Decisions

### D1: Bottom Sheet CSS Selector Fix — Safe-by-Default Pattern

**Decision:** Fix the CSS selector to match Aurelia's boolean attribute output.

**Context:** Aurelia's `data-dismissable.bind="dismissable"` outputs `data-dismissable="false"` when the value is `false` — the attribute is always present with a string value. The CSS selector `:not([data-dismissable])` checks for attribute absence, which never matches.

**Approach:** Use explicit value matching:

```css
/* Before (broken): checks attribute absence */
.scroll-area:not([data-dismissable]) .dismiss-zone { ... }

/* After: checks attribute value */
.scroll-area:not([data-dismissable="true"]) .dismiss-zone { ... }
```

**Alternative considered — safe-by-default inversion:** Default dismiss-zone to `scroll-snap-align: none` and only enable on `[data-dismissable="true"]`. Rejected because the `initial-snap` animation pattern relies on `--_snap-align` custom property toggling via `@keyframes`, and inverting the default would require reworking the animation. The minimal selector fix is sufficient and preserves the existing animation design.

**Alternative considered — revert to `if.bind="dismissable"`:** Rejected because dismiss-zone must remain in DOM for the `initial-snap` CSS animation pattern to work. This pattern eliminates the JS `scrollTo` + `requestAnimationFrame` hack that was needed previously (see commit `15a2538`).

### D2: Coach Mark Tooltip — Transparent Background

**Decision:** Remove the tooltip's solid background and drop-shadow.

**Context:** The coach mark overlay already darkens the viewport to 70% opacity. Adding a solid `--color-surface-overlay` background to the tooltip creates two dark layers stacked, which feels visually heavy. The handwritten font (`Klee One`) works better as text floating directly on the dark overlay — lighter and more natural.

**Changes:**
- `.coach-mark-tooltip`: `background: transparent`, `filter: none`
- The existing `color: var(--color-white)` and `font-family: var(--coach-font-handwritten)` remain unchanged

### D3: Welcome Page Language Toggle

**Decision:** Add a minimal language switcher below the CTA buttons on the Welcome page.

**Context:** Language switching currently requires navigating to Settings, which is only accessible after authentication. The welcome page is the first touchpoint — if the language is wrong, the user cannot fix it.

**Implementation:**
- Extract `selectLanguage(lang)` logic from `settings-route.ts` into a shared function (e.g., `changeLocale(i18n, lang)` in a utility module)
- Add two language buttons (EN / JA) in the welcome template footer, below the Log In button
- Current language is highlighted with a distinct style (bold or underline)
- Uses same persistence mechanism: `localStorage.setItem('language', lang)` + `i18n.setLocale(lang)`

### D4: Bottom Sheet Spec Update — Architecture Alignment

**Decision:** Update the `bottom-sheet-ce` spec to reflect the current implementation architecture.

**Context:** The spec still describes the `15a2538` architecture (dialog as popover host and scroll container). The current implementation (`72c768a`) separates popover (CE host) from scroll (`.scroll-area` div). The spec's DOM structure scenario, non-dismissable scenario, and scroll-driven animation scenario need updating.

**Key spec changes:**
- DOM structure: `<bottom-sheet popover> > .scroll-area > .dismiss-zone + .sheet-body`
- Non-dismissable: dismiss-zone always in DOM, CSS controls `scroll-snap-align` via `data-dismissable` attribute value
- `scrollTo` + `requestAnimationFrame` replaced by `initial-snap` CSS animation
- Scroll-timeline on `.scroll-area` (not on dialog)
- Semantic improvement: `.sheet-body` uses `<section>` element

## Architecture Diagram

```
Bottom Sheet Component (after fix)
====================================

<bottom-sheet popover="manual" role="dialog" aria-label="...">
│  ← CE host: popover API, opacity transition, ::backdrop
│  ← @starting-style handles display:none → block transition
│
├── <div class="scroll-area" data-dismissable="false">
│   │  ← scroll-snap container, initial-snap animation
│   │  ← scroll-timeline: --sheet-scroll
│   │
│   ├── <div class="dismiss-zone" aria-hidden="true">
│   │      ← block-size: 100dvh (swipe target)
│   │      ← scroll-snap-align: none  ← CSS disables when
│   │         not data-dismissable="true"
│   │
│   └── <section class="sheet-body">
│          ← scroll-snap-align: end (always active)
│          ← browser snaps here on open ✓
│          ├── <div class="handle-bar">
│          └── <au-slot>  ← projected content


Selector fix:
  .scroll-area:not([data-dismissable="true"]) .dismiss-zone {
      scroll-snap-align: none;   ← dismiss-zone snap disabled
      pointer-events: none;      ← no interaction
  }

  Result: only .sheet-body has active snap → browser snaps to sheet ✓
```

## Onboarding Flow After Changes

```
┌─────────────────────────────────┐
│         LIVERTY MUSIC           │
│                                 │
│  Never miss a live show         │
│  from the bands you love.       │
│                                 │
│  ┌───────────────────────┐      │
│  │    Get Started         │      │
│  └───────────────────────┘      │
│  ┌───────────────────────┐      │
│  │    Log In              │      │
│  └───────────────────────┘      │
│                                 │
│         EN  ·  日本語            │  ← NEW: language toggle
└─────────────────────────────────┘
         │
         ▼ Get Started
┌─────────────────────────────────┐
│  Discovery (DNA Orb)            │
│  Follow 3+ artists              │
│                                 │
│  Coach mark spotlight on Home:  │
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│  ░                             ░│
│  ░  Check out your             ░│ ← CHANGED: no bg, text only
│  ░  timetable!                 ░│    on dark overlay
│  ░  ╔════════╗                 ░│
│  ░  ║  Home  ║                 ░│
│  ░  ╚════════╝                 ░│
│  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└─────────────────────────────────┘
         │
         ▼ Tap Home
┌─────────────────────────────────┐
│  Dashboard                      │
│  1. Celebration overlay (2.5s)  │
│  2. User Home Selector opens ✓  │ ← FIXED: sheet body visible
│  3. Lane intro sequence         │
│  4. My Artists spotlight        │
└─────────────────────────────────┘
```
