## Context

On touch devices (`pointer: coarse`), the unfollow trash icon column is hidden via CSS to give the
hype slider more horizontal space. A swipe-to-unfollow replacement was explored but abandoned
because `<table>` layout constrains `overflow-x` on `display: table-row`, making reliable
horizontal pointer capture impossible without replacing the table structure.

The existing `BottomSheet` component (Popover API, `open` bindable, `sheet-closed` event) and the
existing `unfollowArtist()` method on `MyArtistsRoute` are both reusable without modification.

## Goals / Non-Goals

**Goals:**
- Touch devices: long-press (500ms) on any artist row opens a per-artist unfollow BottomSheet
- Desktop: retain the existing trash icon column — zero behaviour change
- Help page for `my-artists` documents the long-press gesture

**Non-Goals:**
- Swipe gestures — ruled out due to table layout constraints
- Haptic feedback — no Web Vibration API usage (inconsistent browser support)
- Animation of the row on long-press hold (visual feedback is cursor/OS-level)

## Decisions

### 1. Custom Attribute vs inline `pointerdown` handler

**Decision**: Aurelia 2 `@customAttribute('long-press')` in `src/custom-attributes/long-press.ts`.

**Rationale**: The gesture logic (timer, move-cancel, pointer event cleanup) is reusable and must
not pollute `MyArtistsRoute`. A Custom Attribute keeps the host element clean and matches the
project pattern (`ArtistColorCustomAttribute`, `BeamVarsCustomAttribute`).

**Alternative**: Inline `pointerdown.trigger` with timeout in the route VM. Rejected — gesture
state management in the VM increases coupling and is difficult to unit-test in isolation.

### 2. Long-press detection: `setTimeout` vs `PointerEvents` pressure

**Decision**: `pointerdown` starts a 500ms `setTimeout`; `pointermove`, `pointerup`, and
`pointercancel` cancel it. Movement threshold: 10px (Manhattan distance) to tolerate minor finger
jitter without false negatives.

**Rationale**: `PointerEvent.pressure` is unreliable across browsers and devices. The
`setTimeout` + cancel-on-move pattern is the established idiom for long-press.

**Alternative**: CSS `animation` trick (start animation on `:active`, fire JS on `animationend`).
Rejected — cannot reliably cancel on move without JS event listeners anyway, adds CSS coupling.

### 3. `pointer: coarse` guard location

**Decision**: The Custom Attribute itself checks `matchMedia('(pointer: coarse)')` at `attached()`
and skips listener attachment on non-touch devices.

**Rationale**: The CSS already hides the trash column via `@media (pointer: coarse)`. Keeping the
guard in the Custom Attribute makes it self-contained — the HTML template does not need a
conditional wrapper, and desktop behaviour is unchanged at zero cost.

### 4. BottomSheet per-row vs shared singleton

**Decision**: A single `<artist-unfollow-sheet>` component instance in `my-artists-route.html`,
outside the `<tbody>` repeat. The route VM holds the currently-selected `MyArtist` and passes it
as a bindable.

**Rationale**: One BottomSheet instance in the popover layer is cheaper than N popover elements
(one per row). The trade-off is that the route VM must track `selectedArtistForUnfollow`.

**Alternative**: One `<artist-unfollow-sheet>` inside each `<tr>`. Rejected — N popover elements
in the DOM; also, popover stacking context issues may arise inside `<table>`.

### 5. Custom event vs Aurelia EventAggregator for unfollow confirmation

**Decision**: The BottomSheet component emits an Aurelia `@bindable` callback (`unfollow-confirmed`
custom event via `<artist-unfollow-sheet unfollow-confirmed.trigger="openUnfollowSheet()">`).
Actually: the sheet fires a DOM `CustomEvent('unfollow-confirmed')` which the route handles via
`.trigger` binding; confirmed unfollow calls the existing `unfollowArtist()`.

**Rationale**: Direct `.trigger` binding is the idiomatic Aurelia 2 pattern. EventAggregator is
global state and unnecessary here.

## Risks / Trade-offs

- **`pointer: coarse` media query is static at attach time** — hot-plugging a mouse on a tablet
  will not re-enable the trash column until page reload. Acceptable: CSS already has the same
  limitation (the `@media` query evaluates at render time for initial layout).

- **Long-press conflicts with OS text selection** — `pointercancel` fires if the browser starts a
  text-selection drag. The attribute already cancels on `pointercancel`, so no ghost sheet opens.
  However, `user-select: none` on `<tr>` may be needed to prevent text-selection UI during hold.

- **Accessibility on touch-only devices** — long-press is not discoverable. Mitigation: help text
  in `page-help` documents the gesture. Keyboard users on touch devices still have no path to
  unfollow unless a keyboard is attached (desktop path restored via `pointer: fine`).

## Migration Plan

No data migration. All changes are frontend-only:
1. Deploy new `LongPressCustomAttribute` + `ArtistUnfollowSheet` registered in `main.ts`
2. Updated `my-artists-route.html` + `.ts` use the new custom attribute and sheet
3. Help page content update is delivered as a translation key update
4. No feature flag required — the touch guard in the Custom Attribute ensures desktop is unaffected

## Open Questions

- None — all decisions resolved.
