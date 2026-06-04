## Context

The dashboard filter (`dashboard-artist-filter`) is implemented entirely in the frontend: `DashboardRoute` holds an `@observable filteredArtistIds` array and a `filteredDateGroups` getter that filters the loaded `DateGroup[]` by artist, syncing an `artists` URL query parameter via `history.replaceState`. The filter UI is the `artist-filter-bar` component, which opens a shared `bottom-sheet` and renders followed artists as checkbox chips (`checked.bind="pendingIds" model.bind="artist.id"`), committing the pending selection on confirm.

Ticket-journey status is already available on the frontend: `TicketJourneyService.ListByUser` is fetched on dashboard load and each `Concert` carries an optional `journeyStatus` (`tracking | applied | unpaid | paid | lost`). It is rendered today as a colour badge on the concert card and as a status control in the concert-detail sheet. The semantic hues already live as shared `--journey-hue-*` design tokens, but the per-status icon glyphs and labels are duplicated/inlined per component, with no single source of truth.

This change is frontend-only. No Protobuf, backend, or infrastructure work is required.

## Goals / Non-Goals

**Goals:**
- Make the artist facet useful for high-volume followers: per-artist concert count, count-descending sort, hide zero-concert artists.
- Add a ticket-journey-status filter facet to the same bottom sheet, with OR-within / AND-across-facet semantics and `journey` URL synchronisation.
- Make the filter (artist facet) usable by guests; gate the journey facet to authenticated users.
- Establish one canonical journey-status presentation map (label + emoji icon + hue token) consumed by every status-rendering component.

**Non-Goals:**
- No deadline display, urgency sorting, or reminders — those belong to the sales-phase / next-action features. The journey facet is *pure filtering on status*.
- No "no status set" pseudo-status as a selectable option (explicitly out of scope).
- No backend/proto change; journey data delivery is unchanged.
- No concert-series filter dimension (analysed and deferred; series is a grouping concern, not a filter).

## Decisions

### D1 — Journey filter: extend the existing getter, not a value-converter
Add `@observable filteredStatuses: JourneyStatus[]` and fold the journey predicate into `filteredDateGroups` as a single `keep` predicate: `(noArtist || ids.has(c.artistId)) && (noStatus || (c.journeyStatus && statuses.has(c.journeyStatus)))`. The getter already read-tracks its observable sources, so the view updates correctly. A value-converter was rejected: the logic depends on two VM-level observable arrays and runs in exactly one place, so a converter only relocates the logic and forces both arrays to be passed as parameters. The `!!c.artistId` ghost-card guard is preserved in both empty- and active-filter cases.

### D2 — Single URL writer to avoid double `replaceState`
Two facets each syncing the URL on change would fire `replaceState` twice in one commit (the first write missing the other facet). Resolve by building the URL from *both* arrays in one place and driving it from a **single watcher** keyed on both arrays (`@watch` on a composite of `filteredArtistIds` + `filteredStatuses`), which is async-batched and collapses the double commit into one write. URL shape: `/dashboard?artists=<ids>&journey=<statuses>`; each param omitted when its set is empty. Both params are parsed back in `loading()`.

### D3 — Counts computed over the *unfiltered* set, cached with `@computed`
`countedArtists` is a `@computed('dateGroups','followedArtists')` getter on `DashboardRoute` that builds a `Map<artistId, count>` from the full `dateGroups` (NOT `filteredDateGroups`, so counts stay stable as the user toggles chips), then returns `followedArtists` projected to `{id, name, count}`, filtered to `count > 0`, sorted by `count desc, name asc`. Explicit `@computed` deps act as the cache; dirty-checking never engages because every dependency is observable. The chip `repeat.for` uses `key.bind="artist.id"` so checkbox/`:has(input:checked)` state is reused when sort order changes.

### D4 — Facet gating: keep outer onboarding guard, gate only the journey section
The whole `artist-filter-bar` keeps `if.bind="!isOnboarding"` (onboarding still suppresses it; guests who are not onboarding pass it). The artist facet is always present. The journey `<section>` is wrapped in `if.bind="showJourneyFacet"` bound to `isAuthenticated`. `if.bind` (not `show.bind`) is used so the journey chips are absent from the DOM/accessibility tree for guests. Reactivity holds because `isAuthenticated` bottoms out on the auto-observed `user` property, so a mid-session sign-in adds the facet.

### D5 — Canonical journey-status map as a plain exported const
Define `JOURNEY_STATUS_CONFIG: readonly { status, labelKey, icon, hueToken }[]` in `src/entities/ticket-journey.ts`, alongside the existing plain exports (`JOURNEY_NAV_ORDER`, etc.) that already serve as the journey single-source-of-truth. Each consuming VM exposes it as a public field for `repeat.for`. Rejected: value-converter (wrong shape for iterating the 5 statuses; the scalar status→label lookup stays as the existing `t.bind` i18n call), static class member (couples to one component), DI service (overkill for static immutable data). Labels reuse the existing `eventDetail.journeyStatus.*` i18n keys. Icons: `tracking`👀, `applied`📝, `unpaid`💰, `paid`🎟️, `lost`💔.

### D6 — Filter chip ordering with a process/outcome break
Journey chips are ordered in journey-flow order with a line break between the process phase and the outcome phase, mirroring the concert-detail two-phase layout: process row = `TRACKING`, `APPLIED`; outcome row = `UNPAID`, `PAID`, `LOST`. Selected chip fills with its `--journey-hue-*`; unselected chip is a neutral outline carrying a small colour cue so the hue association survives in both states (icon + label provide the non-colour cue).

## Risks / Trade-offs

- [Emoji render inconsistently across OSes] → Centralising icons in one const means a future swap to SVG is a single edit; emoji are interpolated as plain text (HTML-escaped, no XSS surface).
- [Journey facet shown but most concerts have no status → selecting a status yields a near-empty highway] → Acceptable: this is the intended high-signal behaviour (surface the few engaged concerts); the existing empty-state placeholder is reused.
- [Guest "filter not visible" root cause is empirically onboarding/zero-follows, not an auth gate] → Implementation must verify the exact observed gate before claiming guest enablement; the spec states the intended availability and the code reconciles it.
- [Refactoring event-card/detail-sheet to the shared map could regress current rendering] → Behaviour is unchanged except the `LOST` glyph; covered by existing component/visual tests, and the i18n label keys are reused verbatim.

## Migration Plan

Pure additive frontend change, no data migration. Ships via the standard frontend release flow. Rollback is a straight revert of the frontend PR; the `journey` URL param degrades gracefully (ignored by the prior build). Note the frontend visual-baseline refresh constraint: the intentional UI changes (counted artist chips, journey chips, `LOST` icon) will require regenerating visual baselines.

## Open Questions

- None blocking. Section ordering (journey above artists), clear-all scope (clears both facets), and the exclusion of a "no status set" option are all decided.
