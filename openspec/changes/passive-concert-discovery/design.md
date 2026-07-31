## Context

The Dashboard today calls `ConcertService.ListByFollower` (authenticated) or `ConcertService.ListWithProximity` (unauthenticated guest path) and renders the result as a `ConcertHighway` with HOME/NEARBY/AWAY lanes. The proximity model (Haversine 200 km, `admin_area` HOME match) is already implemented end-to-end and shared via `entity.GroupByDateAndProximity`.

Concert data coverage is bounded by follows: only artists that at least one user follows have concerts in the DB. The new feature intentionally works within this constraint — data richness grows as the user base grows.

## Goals / Non-Goals

**Goals:**
- Let users browse all concerts in the DB near a geographic reference point, filtered by a date range
- Reuse the existing proximity model, `ProximityGroup` response format, and `ConcertHighway` UI without duplication
- Introduce `entity.v1.GeoLocation` as a clean, semantically neutral parameter type (not user-specific like `Home`)
- Refactor `UserHomeSelector` so selection and persistence are separate responsibilities

**Non-Goals:**
- Proactive regional AI crawling (discovery is limited to concerts already in the DB)
- Map or calendar display modes (list only for MVP)
- AWAY-tier results in the All Nearby view
- Pagination (result sets are small at current scale)
- Persisting the user's area override selection across sessions

## Decisions

### D1 — Dashboard toggle, not a new nav tab

**Decision:** Add a "My Timetable / All Nearby" segment toggle to the Dashboard rather than a fifth nav tab.

**Rationale:** The Discovery tab's identity is artist-first (bubble UI); inserting a list view there would be jarring. A fifth tab is the hardest pattern to discover — users open the Dashboard daily, so the toggle is immediately visible. The visual similarity between the two modes (same `ConcertHighway` component) is a feature: it signals continuity, not a context switch.

**Alternative considered:** Discovery tab integration — rejected because of the visual mismatch (bubbles vs. list) and intent mismatch (artist discovery vs. concert discovery).

### D2 — `entity.v1.GeoLocation` as a new proto entity

**Decision:** Define a new `entity.v1.GeoLocation` message `{ double latitude, double longitude, string admin_area }` as the `ListByLocation` parameter type.

**Rationale:** `entity.v1.Home` is semantically tied to "where the user lives" — using it as a generic location parameter would mean the RPC implicitly assumes caller intent. `Proximity` is an output classification enum (HOME/NEARBY/AWAY), not an input concept, so `ListByProximity` would conflate input and output domains. `GeoLocation` is neutral: it is a geographic reference point that any caller can construct from any source.

`latitude/longitude` fields are required in the message (FE resolves centroid before the call); `admin_area` is used server-side for HOME-tier classification (exact `venue.admin_area` match). This avoids a server-side reverse-geocoding step while keeping the server free of ISO 3166-2 centroid-resolution logic.

**Alternative considered:** Pass `string level_1` only and let the server resolve the centroid via `geo.ResolveCentroid` — simpler for the caller but ties the RPC to an ISO 3166-2-aware server contract. Rejected in favour of a purely spatial input.

### D3 — FE owns centroid resolution

**Decision:** The frontend resolves prefecture centroid coordinates from a bundled constant table (47 JP prefectures) before calling `ListByLocation`.

**Rationale:** `user.home.centroid.latitude/longitude` (via the nested `Coordinates` sub-message on `Home`) are already present on the `User` proto response, so the default (user's home area) requires no extra lookup. Note: `centroid_latitude` and `centroid_longitude` are reserved field names on `Home` proto and must not be used; the correct path is `home.centroid.latitude` / `home.centroid.longitude`. For the area-override case, a 47-entry constant is negligible bundle cost and avoids adding a new RPC or embedding geography logic on the server for this path.

### D4 — `ListWithProximity` renamed to `ListByArtists`

**Decision:** Rename the existing RPC. The primary filter is `artist_ids`; "WithProximity" described the output format, not the filter axis, creating ambiguity next to the new `ListByLocation`.

**Migration:** The rename is a breaking proto change. It will be guarded behind a BSR major version bump. The frontend is the only current caller — both the old and new name will be emitted during the transition window if needed, but since specification and frontend are released together, a clean cut is preferred.

### D5 — `UserHomeSelector` responsibility split

**Decision:** Remove `IUserStore` and persistence logic from `UserHomeSelector`. The component emits `onHomeSelected(code: string)` only; callers own the save/no-save decision.

**Rationale:** The current design mixes selection UI and account-write side-effects in one component, making it untestable in isolation and impossible to reuse for the area-override filter (which must not write to the account). Splitting makes the component a pure UI primitive.

**Affected callers:** Settings page (must call `userStore.updateHome(code)` in its `onHomeSelected` handler), Onboarding flow (same), new Dashboard "All Nearby" area selector (updates local route state only).

### D6 — Date range: FE computes, RPC accepts explicit `from`/`to`

**Decision:** The frontend computes concrete `LocalDate` pairs from preset labels (今週末, 7日以内, 30日以内, カスタム) and passes them to `ListByLocation`. The server enforces a 30-day maximum (`to - from ≤ 30 days`) via protovalidate.

**Rationale:** Preset semantics (e.g., "今週末" = next Sat–Sun relative to today) are a UI concern. The RPC stays stateless and timezone-agnostic; the FE already knows the user's locale context.

### D7 — AWAY concerts excluded from All Nearby response

**Decision:** `ListByLocation` returns only HOME and NEARBY concerts; AWAY-only `ProximityGroup` entries are stripped from the result of `GroupByDateAndProximity` by the use-case layer.

**Rationale:** The feature answers "what's on near me?" — venues beyond 200 km and outside the home admin_area are not "near" by definition. Including them would dilute the signal and require a third lane the UI doesn't show.

### D8 — Follow CTA in EventDetailSheet, not on concert card

**Decision:** The "Follow this artist" button appears in the `EventDetailSheet` (opened on card tap) rather than inline on the card.

**Rationale:** Inline action buttons on every card in a dense list create visual noise and accidental taps. The detail sheet is already the place for action: ticket journey, source URL. Adding follow there is consistent and preserves the card as a pure information surface.

## Risks / Trade-offs

**[Sparse results for new users]** → Users with few follows see few concerts. Mitigation: empty-state copy links to Discover tab with clear explanation ("Follow more artists to see more concerts here").

**[HOME-tier classification depends on caller-supplied `admin_area`]** → A caller passing wrong coordinates + wrong admin_area gets incorrect HOME classification. Mitigation: the FE always derives `admin_area` from the same ISO 3166-2 code that drives the centroid lookup; the mapping is deterministic.

**[Breaking rename of `ListWithProximity`]** → Requires a BSR major bump and coordinated frontend deploy. Mitigation: spec and frontend are released together under the same change; no external consumers of this RPC exist today.

**[`UserHomeSelector` refactor touches onboarding and settings]** → Risk of regression in home-setting flows. Mitigation: the component's `onHomeSelected` callback already exists; callers add one line (`userStore.updateHome(code)`). Covered by existing E2E smoke tests.

## Migration Plan

1. Merge specification PR (proto changes, new entity, rename, new RPC)
2. Publish GitHub Release → BSR gen
3. Backend: implement `ListByLocation` handler + `ListByArtists` rename; upgrade generated package; `make check`
4. Frontend: refactor `UserHomeSelector`; add centroid constants; implement Dashboard toggle + All Nearby mode; upgrade generated package; `make check`
5. Open BE + FE PRs after local `make check` passes (no draft PRs before BSR gen completes)
6. Merge in dependency order: BE → FE (FE depends on no BE state, but deploy ordering is cleaner)

**Rollback:** Revert FE to previous tag (toggle disappears); BE `ListByArtists` is additive, old name is gone but no external callers exist.

## Open Questions

- None blocking implementation. The explore-mode discussion resolved all major design questions.
