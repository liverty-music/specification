## Context

The Welcome page at `/` currently renders two vertically-stacked screens inside a single scroll container with CSS scroll-snap. Screen 1 shows the hero (brand + title + subtitle + `[Get Started]` + `[Log In]` + language switcher + floating arrow hint); Screen 2 shows the concert timetable preview followed by a repeat of `[Get Started]` + `[Log In]`. The scroll-snap is set to `y mandatory`, forcing the viewport to snap to whichever screen is closer when the user stops scrolling. All state and markup live in `frontend/src/routes/welcome/welcome-route.{html,ts,css}`.

Behaviorally, this produces a pattern the user-facing design intends as "Promise → Proof" — Screen 1 delivers the core message, Screen 2 shows what the product looks like — but three observed problems break this narrative:

1. Screen 2 is undiscoverable. The only affordance is a 24×24 arrow icon at the bottom edge, which does not clearly communicate "there is another screen below."
2. `[Get Started]` is reachable on Screen 1 before the user ever reaches the proof. In analytics terms, this means users can commit to onboarding with no exposure to the preview that is meant to raise their expectations.
3. The arrow element is positioned with `position: absolute` but its nearest positioned ancestor is the scroll container (`welcome-route` itself), so it's pinned to the bottom of the viewport at all scroll positions and appears on Screen 2 too.

Exploration with the user (see the conversation that produced this change) ruled out a full single-scroll redesign because the team values the two-screen rhythm as a narrative device. The refinement below preserves that rhythm while fixing the discoverability, funnel, and positioning issues.

## Goals / Non-Goals

**Goals:**
- Ensure every user who taps `[Get Started]` has first seen the timetable preview.
- Make the existence of Screen 2 unambiguous from the initial viewport, without adding a separate paginator UI.
- Keep Screen 1 focused on the hero message — no competing CTAs, no ambiguous icon-only elements.
- Fix the floating-arrow positioning bug by removing the arrow entirely (its job is subsumed by the new affordance).
- Preserve the "two-screen snap" aesthetic as a soft rhythm, not a hard constraint.
- Respect `prefers-reduced-motion` for all new motion (smooth-scroll action, any new transitions).

**Non-Goals:**
- Not redesigning the timetable preview itself (read-only, data shape, card visuals all stay).
- Not making the preview interactive (no tap-to-expand, no card actions — explicitly descoped per user decision).
- Not touching the onboarding flow that begins after `[Get Started]`.
- Not changing the language switcher's behavior, position, or styling.
- Not modifying any backend, proto, or RPC. This change is frontend-only.
- Not introducing pagination dots or other explicit "1/2, 2/2" indicators — the peek serves this role with lower visual noise.

## Decisions

### D1. Remove `[Get Started]` and `[Log In]` from Screen 1; keep them on Screen 2 only

**Why:** This is the single highest-leverage fix for the funnel problem. As long as `[Get Started]` is reachable above the fold, a non-trivial share of users will tap it without scrolling to the preview — no amount of scroll-affordance tuning closes that leak.

**Alternatives considered:**
- *Leave `[Log In]` on Screen 1 as a text link.* Rejected because the design intent is explicitly "Screen 1 shows only the hero message." Any interactive element dilutes that focus. The 1-snap scroll cost for returning users is negligible, and returning users typically arrive at `/dashboard` directly via active session rather than hitting `/`.
- *Keep both CTAs on both screens (current state).* Rejected — this is the existing problem.
- *Move only `[Get Started]` and keep `[Log In]` on Screen 1.* Rejected for the same reason as the first alternative — any button on Screen 1 recreates the focus-dilution problem.

### D2. Add a `[See how it works ↓]` labeled button on Screen 1 as its sole action

**Why:** Replacing the icon-only arrow with a labeled `<button>` has three effects: (a) it communicates intent unambiguously ("there is something below worth seeing"), (b) it provides a tap/click target that keyboard and screen-reader users can discover (unlike a decorative `<div>`), (c) it becomes the only call-to-action on Screen 1, which reinforces the message-first framing without leaving the screen feeling dead.

The button smooth-scrolls to Screen 2 when activated. Under `prefers-reduced-motion: reduce`, it jumps instantly instead.

**Alternatives considered:**
- *Animated arrow with `aria-label`.* Improves a11y but doesn't solve the visual discoverability problem for sighted users. The icon alone still reads as "decoration."
- *Pagination dots (1/2, 2/2).* Adds a new UI affordance with its own learning cost. Redundant once the peek (D3) is in place. Decorative noise against the "hero only" intent.

### D3. Size Screen 1 at ~95svh so Screen 2's top edge peeks above the fold

**Why:** This is the structural signal that "more content exists below." Instead of relying on an icon to promise something, the page *shows* a sliver of that something. The peek can be the Screen 2 label ("Build your own concert timetable!") or the top of the frame/gradient — anything that visibly breaks the illusion of Screen 1 being a self-contained page.

The user explicitly chose "控えめ" (subtle) over "明確" (obvious) in conversation, so 95svh (≈5svh peek) is the target. This is a starting value — tuning in a visual review is expected.

**Trade-off:** A peek too deep (e.g., 85svh) undermines "hero only" by showing too much of the preview and splitting attention; a peek too shallow (e.g., 99svh) is indistinguishable from the current 100svh. 95svh sits in the "clearly intentional but not competing" band.

**Alternatives considered:**
- *Full 100svh with overlay text "scroll for more" on Screen 1.* Adds text clutter and still relies on a promise rather than evidence.
- *Expose only at the fade-out mask.* Too subtle to register for most users; indistinguishable from a gradient decoration.

### D4. Relax `scroll-snap-type` from `y mandatory` to `y proximity`

**Why:** `mandatory` forces the viewport to snap whenever the user pauses scrolling, even mid-content. With Screen 2 content now peeking above the fold, a mandatory snap back to Screen 1 contradicts the peek's intent — the user sees the peek, tries to scroll a small amount to read it, and gets snapped back. `proximity` snaps only when the user's scroll position is close to a snap point, preserving mid-scroll reading.

**Alternatives considered:**
- *Remove `scroll-snap` entirely.* Equivalent to going full single-scroll. Conflicts with the team's preference for the two-screen rhythm.
- *Keep `mandatory`.* Defeats the peek.

### D5. Delete `.welcome-scroll-hint` element and its CSS entirely

**Why:** The labeled button (D2) and the peek (D3) fully replace the arrow's job. Removing it is the root-cause fix for the "arrow shows on Screen 2" positioning bug — no element, no bug. Patching `position: absolute` inside `.welcome-hero` (adding `position: relative` to the parent) would also work, but the arrow itself is now redundant, so removal is preferred over repair.

### D6. Keep the language switcher on Screen 1, placed between the hero copy and the new scroll button

**Why:** First-visit locale discovery is important — if a Japanese user lands on the English default, they need to switch locale without committing to sign-up first. Moving the switcher to Screen 2 creates a chicken-and-egg problem (the hero copy is in the wrong language while the user is still reading it). The user confirmed in conversation that the Screen 1 Hero-下 position is acceptable.

The switcher is visually low-weight (small text, low contrast) and does not compete with the hero message, so the "hero-only" intent remains intact in practice.

### D7. No changes to data loading, preview composition, or CTA handler logic

The `loadPreviewData()` method, the `PREVIEW_ARTIST_IDS` environment variable, the `handleGetStarted()` and `handleLogin()` methods, and the `concert-highway` props all remain as-is. This change is purely about visual layout and affordance; business logic is untouched.

## Risks / Trade-offs

- **Risk:** Returning users briefly confused by the absence of `[Log In]` on Screen 1 → **Mitigation:** In practice returning users with a valid session land on `/dashboard` via the `canLoad` redirect, so they rarely see `/`. Users with expired sessions have a one-screen scroll to reach `[Log In]`, which is a negligible friction increment and the labeled `[See how it works]` button visually signals "content continues." Monitor first-session-log-in funnel drop-off after release; revisit if there's a measurable impact.
- **Risk:** 95svh peek appears different on devices with browser chrome that dynamically resizes (mobile Safari address bar, Android chrome) because `svh` excludes dynamic UI but devices vary → **Mitigation:** `svh` is specifically designed to be stable against dynamic toolbar resizing, unlike `vh`. Validate on iOS Safari and Android Chrome during QA.
- **Risk:** `scroll-snap: y proximity` behaves inconsistently across browsers, especially on trackpads with inertia scroll → **Mitigation:** `proximity` is a well-supported, less aggressive variant of snap and inherently tolerates mid-scroll states better than `mandatory`. If any browser produces janky behavior, fall back to no snap for that browser via `@supports` feature query.
- **Risk:** Removing CTAs from Screen 1 means the page looks "empty" above the fold on very tall desktop viewports where the peek becomes barely visible → **Mitigation:** Desktop is not the primary target (PWA, music fans). The hero title/subtitle remain, and the `[See how it works ↓]` button is large enough to anchor the space. If real-world analytics show desktop drop-off, a max-width container can compress the layout further.
- **Trade-off:** Losing the `[Get Started]` click events on Screen 1 means the funnel metric "CTA taps per session on /" moves; downstream dashboards that chart this may show a step-change. Not a technical risk but worth flagging to the team tracking these metrics.

## Migration Plan

This is a visual/behavioral UX change with no data migration, no proto change, and no backend coordination. Deployment is a single frontend release:

1. Implement the template/CSS/handler changes in `frontend/src/routes/welcome/`.
2. Add i18n keys for the new button label in EN and JA resource files.
3. Update unit tests and E2E tests to reflect the new button topology.
4. QA on iOS Safari, Android Chrome, desktop Chrome/Firefox — verify peek, scroll affordance, snap behavior, keyboard navigation, and `prefers-reduced-motion`.
5. Merge to `main` → ArgoCD deploys the new frontend build to dev.
6. After soak, promote to production.

**Rollback:** Revert the merge commit. No persistent state is affected; the change is stateless.

## Open Questions

- None blocking. The peek depth (95svh vs. 92svh vs. 97svh) is a tuning decision deferred to visual review during implementation, not a pre-commit design question.
