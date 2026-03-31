## Context

The current PWA install mechanism is a `pwa-install-prompt` Toast component mounted in `app-shell.html`. It is gated by: `beforeinstallprompt` fired, not dismissed, onboarding completed, **authenticated**, and `sessionCount >= completedSessionCount + 2`. This design excludes guest users entirely and delays the prompt by at least 2 sessions after completion — both constraints that no longer serve the product goal of maximizing PWA adoption.

The `signup-prompt-banner` is a `position: fixed` bar that sits flush above the Nav Bar (`inset-block-end: calc(3.5rem + env(safe-area-inset-bottom, 0px))`). When both are visible, a naive FAB placement would either overlap the banner or require dynamic offset calculation.

The app shell uses a `grid` layout (`viewport` / `nav`) with overlay components positioned via `position: fixed` and `block-size: 0` to stay out of the grid flow.

## Goals / Non-Goals

**Goals:**
- Surface a persistent, discoverable PWA install entry point to all users (guest + authenticated) once onboarding completes
- Support both Android/Chrome (`beforeinstallprompt`) and iOS Safari (manual instruction sheet via `bottom-sheet`)
- Overlay naturally alongside `signup-prompt-banner` without layout calculation
- Animate subtly on first appearance; remain passive thereafter
- Disappear permanently on install (`appinstalled` event)

**Non-Goals:**
- Desktop browser support (FAB targets mobile PWA install)
- Replacing the `PostSignupDialog` PWA install row — it stays as a parallel path for authenticated first-signup flow
- Supporting Firefox (no `beforeinstallprompt`, no significant mobile market share for this use case)
- Re-showing the FAB after the user navigates away and returns (it is always visible post-completion until installed)

## Decisions

### Decision 1: FAB overlaid on signup-banner button row, not above it

**Chosen:** `position: fixed` FAB placed at the same `inset-block-end` as the signup-banner's button row (approximately `calc(3.5rem + env(safe-area-inset-bottom) + var(--space-s))` from the bottom), aligned `inset-inline-end: var(--space-s)`. The banner's "アカウント作成" button is `align-self: center` with `padding-inline: var(--space-xl)`, leaving clear horizontal space on both sides.

**Alternatives considered:**
- *Dynamic offset via ResizeObserver*: Accurate but adds JS complexity and a layout-read/write cycle every time the banner's height changes.
- *FAB above the banner*: Requires knowing the banner's rendered height, which varies with text wrapping. Same ResizeObserver problem.
- *Hide FAB when banner is visible*: Eliminates competition but means guest users — the primary signup-banner audience — never see the FAB.

**Rationale:** The overlay approach is zero-complexity, visually clean (FAB is compact), and the spatial separation from the dismiss button (top-right of banner) is sufficient to avoid tap target collision. If the button label wraps, the FAB may shift relative to the button row, but remains within the banner's safe zone.

### Decision 2: Remove auth and session-count gates from PwaInstallService

**Chosen:** Eligibility reduced to: `beforeinstallprompt` fired AND onboarding completed AND not yet installed. Auth state and session count removed.

**Alternatives considered:**
- *Keep session-count gate, extend to guests*: Delays install prompt unnecessarily. The original session-count rationale was to give the notification prompt a first-session window — but with the FAB being passive (not a disruptive Toast), this concern is moot.
- *Keep auth gate*: Excludes the guest users this feature is specifically designed to reach.

**Rationale:** The FAB is non-intrusive (no dismiss needed, no "only one prompt per session" pressure). The old gates were designed for disruptive Toasts. With a passive persistent UI element, the right gate is simply "has the user seen enough of the app to understand its value" — which onboarding completion captures cleanly.

### Decision 3: iOS instruction sheet uses existing bottom-sheet component

**Chosen:** On iOS (detected via `!('BeforeInstallPromptEvent' in window)` and user-agent check), tapping the FAB opens the existing `bottom-sheet` component with a static 3-step instruction list.

**Alternatives considered:**
- *Custom modal*: Adds a new component primitive for a single use case.
- *Toast with instructions*: Too small for multi-step instructions.

**Rationale:** `bottom-sheet` already handles popover lifecycle, dismiss, accessibility, and `prefers-reduced-motion`. Reuse is the right call.

### Decision 4: Retire the existing pwa-install-prompt Toast

**Chosen:** `pwa-install-prompt` component and its `if.bind="showNav"` mount in `app-shell.html` are removed. `PwaInstallService.dismiss()` and `StorageKeys.pwaInstallPromptDismissed` are also removed.

**Alternatives considered:**
- *Keep Toast as fallback*: Two install paths with diverging logic creates confusion and test surface.

**Rationale:** The FAB supersedes the Toast entirely. `PostSignupDialog` retains its own install button as a contextual path; that is sufficient as a secondary surface.

### Decision 5a: FAB visibility binding — `show.bind` + `aria-hidden` instead of `if.bind`

**Chosen:** The FAB `<button>` uses `show.bind="isVisible"` combined with `aria-hidden.bind="isVisible ? 'false' : 'true'"` to control visibility.

**Alternatives considered:**
- *`if.bind="isVisible"`*: Removes the element from the DOM entirely when invisible, which means assistive technology (AT) cannot discover the element before it becomes visible.

**Rationale:** `show.bind` sets `display: none` but keeps the node in the DOM and the accessibility tree. This allows screen readers and AT to discover the button's existence via a tree walk even before it becomes interactive. The `aria-hidden` attribute gates actual AT exposure: `aria-hidden="true"` when hidden (so AT ignores it), `aria-hidden="false"` when visible (so AT announces it). This pattern satisfies both the "no premature AT announcement" and "discoverable in advance" requirements.

### Decision 5b: Entry animation — slide-up + 2-pulse ripple, then static

**Chosen:** On first render (controlled by a one-shot CSS class added after `attached()`):
- FAB slides up: `transform: translateY(150%) → translateY(0)`, 400ms ease-out
- After slide completes, a ripple ring animates outward and fades — `animation-iteration-count: 2`, then stops
- Idle state: brand gradient `box-shadow` glow (matching Nav Bar top border gradient), no loop
- Tap: `transform: scale(0.92)` for 50ms, then `scale(1)` for 100ms
- `@media (prefers-reduced-motion: reduce)`: replace slide+ripple with `opacity: 0 → 1` fade only

**Rationale:** UX guideline — continuous animations on decorative elements are distracting. The 2-pulse fires once on entry to attract attention, then stops. The static gradient glow provides brand coherence without motion.

## Risks / Trade-offs

- **iOS detection reliability**: User-agent sniffing is fragile. Prefer feature detection (`'BeforeInstallPromptEvent' in window` is false on iOS). This is reliable for the current Safari versions.
- **FAB tap target near dismiss button**: The `×` dismiss of the signup-banner is top-right; the FAB is bottom-right of the banner. On very short viewports the gap may be tight. Minimum 44px touch target for each must be verified during implementation.
- **`beforeinstallprompt` not fired on desktop**: FAB will not appear on desktop Chrome if the app does not meet installability criteria. This is acceptable — the FAB is a mobile-first feature.
- **PostSignupDialog PWA row still uses `pwaInstall.canShow`**: After this change, `canShow` no longer requires auth or session count. The dialog row will now show on first signup session if `beforeinstallprompt` has fired. This is a behavior change — slightly more aggressive, but acceptable given the simplified model.

## Open Questions

- Should the FAB also appear during the `MY_ARTISTS` onboarding step (just before completion), or strictly after `COMPLETED`? Current design: strictly after `COMPLETED` to avoid distraction during the guided flow.
- Should there be a maximum number of sessions after which the FAB is hidden even if not installed? Current design: no max — the FAB stays until installed. If this feels too persistent, a cap (e.g., 30 sessions) can be added later.
