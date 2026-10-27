## Context

See proposal.md for why the All Nearby view moves. Today all of it lives inside the dashboard route of the frontend:

- `dashboard-route.ts` holds the view state (`viewMode`, the area override, the date range, a route-local result cache, `loadAllNearby()`, the area selector and date-range sheet refs) next to the timetable state. 42 `isAllNearby` branches run through the file, and `buildFabActions()` contributes the mode-swap item to the FAB menu.
- `dashboard-route.html` holds the area/date chip row, the All Nearby `<concert-highway hide-away show-venue-always>`, its empty state, a second `<user-home-selector>` and the `<date-range-sheet>`.
- `event-detail-sheet.open(event, source, isAllNearby)` shows the follow action when `isAllNearby` is true. When the sheet manages history, closing it returns to the dashboard address it captured on open.

Discovery is a four-row grid (search, genre, progress, bubbles). The bubble physics keeps a fixed 130 px orb zone above the canvas floor that no bubble enters (`bubble-physics.ts`, `orbZoneHeight`). The orb's radius grows with follows and is capped by `MAX_RADIUS` 90 px, or `NARROW_MAX_RADIUS` 56 px below 390 px width (`stage-effects.ts`). The FAB already sinks while a snack bar is open through a `:root:has(.snack-item:popover-open, …)` rule in `global.css`; a bottom banner shrinks the route area by `--bottom-banner-height`.

The tile and its icon were settled with the user on a local prototype (`~/.cache/nearby-discoverability/sample/index.html` on the planning machine); this document records the geometry so the prototype is not needed to build it.

## Goals / Non-Goals

**Goals:**
- Move the All Nearby view to Discovery without changing what it shows or how its filters behave.
- Keep the bubble field exactly as large as today.
- Leave the dashboard with one view and no All Nearby code.

**Non-Goals:**
- Letting a guest follow from the event detail sheet. Today a guest gets the sign-up banner; the new story keeps that. Allowing guest follows there (stored on the device like bubble follows, counted by the onboarding progress row) is a separate proposal.
- Showing a count of nearby concerts on the tile or the dashboard empty state (rejected by the user: it costs a `ListByLocation` call per visit).
- A weekly "concerts near you this weekend" push, or any backend change.

## Decisions

### D1. The All Nearby view lives on Discovery, switched by a tile beside the orb

Alternatives considered with the user, in order: a segment control above the dashboard timetable (the current spec text; costs about 44 px of timetable height), a pill in the shell header (the 2026-08-09 design; needs a route-to-header slot), keeping the FAB item, a segment above the Discovery search bar, a search row that morphs into the filter row, a title that becomes the switch, and a pinned "lens" chip in the genre row. All of the Discovery ones either took height from the bubble field or mixed a view switch into filter controls. The band beside the orb is empty by construction, so a tile there costs the field nothing.

### D2. Tile position follows the largest orb, not the current one

The tile's inline-start edge is `50% + max-orb-radius + var(--space-s)` from the centre, with `--orb-max-r` 90 px, overridden to 56 px in a container narrower than 390 px; its block-end offset keeps it inside the 130 px orb zone. On a 375 px screen this puts the centre at about 283 px from the left edge. Following the current orb radius instead would move the tile as the fan follows artists. Left-handed mode (`fab-menu` handedness preference) mirrors it with `inset-inline-end`.

### D3. The icon is one inline SVG component driven by `data-view`

A small custom element (`discovery-swap-button`) renders `<button>` with the label and an inline SVG (viewBox 64×64):

- Arrows: two filled tapered "swoosh" paths, point-symmetric about (32, 32). Each is built from a centre line at radius `23.5 + 2.2·sin(2πt − 0.6)` swept clockwise over 132° (168°→300° and 348°→480°), half-width growing from 0.7 to 4.4 (`t^0.85`), smoothed with Catmull-Rom curves, a rounded tail, and a head 9.6 wide and 24° long with slightly concave sides. Arrow 1 is `--color-brand-primary` (magenta), arrow 2 `--color-stage-near` (cyan). The paths are generated once and pasted as static `d` attributes.
- Glyphs, drawn around (0, 0): the artist glyph is three bubbles (hues 275, 182, 46 at saturation 85–95 %, lightness 88 → 68 → 52 %, a pink-to-cyan sheen, a white glint, a thin white rim) plus three four-point sparkles; the All Nearby glyph is an orange ticket marked LIVE with a white pin and a dark pin hole.
- Slots: the active glyph sits at (31, 31) at scale 1.5 over the arrows with a small drop shadow; the other sits at (53, 53) at scale 0.42 on a dark badge disc.
- Motion: CSS transitions on `transform` (620 ms, `cubic-bezier(0.34, 1.5, 0.64, 1)`); the arrows' rotation is an accumulated `--ring-turn` (+180° per tap, kept by the component) so they always turn the same way. Sparkles twinkle with a CSS animation, not SMIL, so `prefers-reduced-motion: reduce` can stop them along with every transition.
- Colours come from tokens; no literal colour that reads in one theme only.

Raster or Lottie assets were rejected: they cannot take tokens, add a load, and the geometry is small.

### D4. The All Nearby view becomes its own component, moved out of the dashboard

`<nearby-concerts>` takes over the dashboard's All Nearby state and template unchanged: area override (route-local, never saved), date range from `<date-range-sheet>`, the per-visit cache keyed by area and range, `loadAllNearby()` with its abort controller, the two-lane `<concert-highway>`, the empty state and the `<user-home-selector>` for the area. Discovery renders it under `if.bind="view === 'nearby'"` and hides the search bar, genre row, progress row and bubble area while it is shown. The cache lives in the Discovery route instance (passed in), so switching back and forth within a visit does not refetch, as the spec requires; a new visit starts empty, as the dashboard did.

Event selection is the dashboard's rule reused: a first-party concert navigates to `/events/:id`, a discovered one opens `event-detail-sheet` with the All Nearby flag. The sheet's history handling captures the current address on open; on Discovery that is `/discovery?view=nearby`, so closing returns there. This is verified by a test rather than assumed (see Risks).

Values on screen and where they come from: every card value (artist name, logo, venue, date, HOME/NEAR lane) is read from `ConcertService.ListByLocation`'s `ProximityGroup` response as today; the area chip shows the display name of the ISO 3166-2 code chosen in `user-home-selector` or the user's home from the user store; the date chip shows the range computed by `date-range-sheet`. The tile shows no data. Nothing is carried between screens except `view=nearby` in the address, which selects a view and carries no value.

### D5. View state: address first, then the remembered choice, then onboarding

`DiscoveryRoute.loading()` reads `view` from the query: `nearby` wins at any onboarding state; otherwise, outside onboarding, it reads `StorageKeys.discoveryView` through the existing storage adapter (wrapped so a throwing or empty storage yields `artists`); onboarding always yields `artists`. A `@watch` on the view writes the address with `history.replaceState` (the dashboard's filter-sync pattern) and stores the view. No history entry is added, so Back leaves Discovery as before.

### D6. Switching pauses the bubbles and reveals the new view from the tile

`switchView()` sets the view inside `document.startViewTransition` (instant without the API or with reduced motion), calls `dnaOrbCanvas.pause()` on entering All Nearby and `resume()` on leaving it unless search mode is on or the document is hidden, and sets `--swap-x/--swap-y` to the tile centre so `::view-transition-new` grows as a circle from it. The callback flushes Aurelia's queue synchronously (`runTasks()`), as the dashboard's mode switch does, because the browser suspends rAF while it snapshots.

### D7. The tile clears a snack bar the way the FAB does

The tile's block-end offset adds `var(--snack-stack-height, 0px)`, a custom property the snack-bar surface publishes on `:root` while a snack is open (next to the existing `--fab-sunk` rule in `global.css`). A bottom banner needs nothing: it already shrinks the route area. In search mode the tile is hidden with the genre row. The FAB scrim already covers page content while the arc is open.

### D8. Dashboard keeps one view

The dashboard drops `viewMode`, every `isAllNearby` branch, the chip row, the second `<user-home-selector>`, the `<date-range-sheet>`, the mode-swap FAB action and its re-registration on mode change (re-registration on onboarding change stays). Both empty states get `<a href="/discovery?view=nearby">` with the new key `dashboard.nearbyCta` 「近くのライブを見る」 / "See shows near you".

## Risks / Trade-offs

- [The detail sheet's close-to-address logic was written for the dashboard] → a unit test opens the sheet from `<nearby-concerts>` on Discovery and asserts the address after close is `/discovery?view=nearby`; fix the capture if it fails.
- [View Transition snapshots of a running canvas can flash] → the physics is paused inside the same callback before the snapshot; with no View Transitions support the swap is instant.
- [Discovery grows in responsibility] → the All Nearby code moves as one component with its own tests; Discovery only owns the view switch.
- [Removing the dashboard mode breaks muscle memory of the two current users] → acceptable; the dashboard's empty state and Discovery's help point to the new place.
- [The tile sits in the orb's absorption path when bubbles fly into the orb] → absorption targets the orb centre, and the tile is outside the largest orb; no overlap.

## Migration Plan

Frontend only, one PR. Deploy as usual; rollback is reverting the PR. The new local-storage key is optional: an old client ignores it and a new client without it opens on the artist bubbles. No data migration.
