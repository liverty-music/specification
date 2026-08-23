## Why

The `<bottom-sheet>` swipe-to-dismiss has two user-facing defects that a prior tuning fix (reduced duration, `pointer-events` lock, `pointerup` threshold) could not resolve because they are architectural, not parametric:

1. **Bounce-back**: after a swipe-down dismiss gesture the sheet often reappears when the user scrolls up to interact with the page. `close()` is committed prematurely on snap detection while a *separate* opacity/`overlay` fade keeps the still-scrollable element alive for 160ms; an upward gesture in that window re-snaps it to the sheet body.
2. **Operation lock**: the user cannot tap another card (e.g. open a different concert's detail) until the sheet has *fully* closed, because the modal `<dialog>` `::backdrop` plus `overlay ... allow-discrete` keeps the dialog in the Top Layer — blocking all background pointer events — for the entire close animation.

Both stem from the same root: the sheet is a **modal `<dialog>` opened with `showModal()`**, whose close is a time-based fade decoupled from the scroll gesture. Google/web.dev's official pattern for this exact UI (the `navigation-drawer` guide) uses a **non-modal `popover` driven entirely by scroll-snap**, where dismiss *is* the scroll and state is read from an `IntersectionObserver`. Aligning to that standard removes both defects by construction and keeps the scroll-linked backdrop fade we already have.

## What Changes

- **BREAKING (internal primitive behavior)**: Re-architect `<bottom-sheet>` from a modal `<dialog>.showModal()` host to the web.dev `navigation-drawer` pattern:
  - Promote the sheet via **`popover="manual"`** (non-modal Top Layer) instead of `<dialog>.showModal()`.
  - Make an **`IntersectionObserver` on the sheet body the single source of truth** for open/closed state; all dismiss paths (swipe, tap-outside, ESC, Android back, programmatic) converge in its callback.
  - **Close = scroll the container to the closed snap stop**; call `hidePopover()` only after the observer confirms the sheet is off-screen. The scroll (native momentum/velocity, fully interruptible) *is* the close animation.
  - **Remove** the `scrollsnapchange`/`scrollend`/`pointerup` scroll-ratio heuristics (`< 0.25`, `< 0.1`) and the `pointer-events: none` bounce-back lock — they become unnecessary.
  - Because `popover` is non-modal, **manually re-implement the a11y affordances** `showModal()` gave for free: set the rest of the document `inert` while the sheet is open, move focus into the sheet on open and restore it on close, and handle Escape via a `keydown` listener. `inert` is lifted the moment the close scroll begins, so the closing window is interactive (fixes operation lock).
- Keep the **scroll-timeline backdrop fade** (`@supports (animation-timeline: scroll())`), unchanged in intent.
- **`100dvh` → `100svh`** for the scroll area / dismiss zone so the sheet height does not jump when the iOS Safari address bar resizes mid-swipe (web.dev guidance).
- **`overscroll-behavior-y: contain` → `overscroll-behavior: none`** to fully stop the dismiss swipe from chaining into page scroll.
- Retain the existing cross-browser `initial-snap` keyframe hack for the open-position snap (works in Safari/Firefox). Do **not** adopt `scroll-initial-target: nearest` yet — it is Chromium-only (unsupported in Safari & Firefox as of 2026-08) and not Baseline; design records that it should replace the keyframe hack only after it reaches Baseline.

## Capabilities

### New Capabilities
<!-- None. -->

### Modified Capabilities
- `bottom-sheet-ce`: The dismiss/lifecycle mechanism changes at the requirement level — Top-Layer promotion moves from modal `<dialog>.showModal()` to non-modal `popover="manual"`; dismiss detection and open/closed state move to an `IntersectionObserver` (removing scroll-ratio heuristics and the `pointer-events` lock); close becomes scroll-to-closed-stop with deferred `hidePopover()`; focus-trap / `inert` / ESC become CE-managed; `100dvh`→`100svh`; `overscroll-behavior: none`.

## Impact

- **Frontend only.** No proto / RPC / backend changes.
- Affected component: `frontend/src/components/bottom-sheet/` (`.ts`, `.html`, `.css`, `.spec.ts`).
- Consumers keep their public contract unchanged: the `open` bindable, `dismissable` bindable, and `sheet-closed` event are preserved, so `event-detail-sheet`, `post-signup-dialog`, `date-range-sheet`, `artist-unfollow-sheet`, `user-home-selector`, `page-help`, etc. need no API changes. Non-dismissable consumers retain modal-like blocking via CE-managed `inert`.
- Observable UX improvement on the dashboard: a closing event-detail sheet no longer blocks tapping another concert card.
- Test surface: `bottom-sheet.spec.ts` and the artist-filter chip-check E2E regression guard.
