# Discovery

## Purpose

Lets a user discover and follow new artists through an interactive physics-based bubble interface and text search, available throughout onboarding and afterward, with sound and animation feedback on each follow. A swap tile beside the orb switches to the All Nearby view, which lists the concerts near the fan's area within a chosen period, including concerts of artists the fan does not follow yet.

## Requirements

### Requirement: DNA Extraction UI Concept
The system SHALL provide a gamified artist discovery interface using a "DNA Extraction" metaphor with an interactive orb (glass sphere) UI that collects user preferences, with visual differentiation per artist and onboarding guidance.

#### Scenario: Initial bubble display with DNA Orb
- **WHEN** a guest or a signed-in fan opens the Discovery screen
- **THEN** the system SHALL display up to 50 artist bubbles in the center area using physics-based animation, or up to 30 when the canvas is narrower than 390 px
- **AND** the system SHALL display a "Music DNA Orb" (glass sphere UI) at the bottom of the screen
- **AND** the orb SHALL serve as a visual inventory for collected artists

#### Scenario: Per-artist bubble color differentiation
- **WHEN** artist bubbles are rendered
- **THEN** each bubble SHALL have a unique gradient color derived from the artist's name using a deterministic HSL-based algorithm
- **AND** the colors SHALL provide visual variety across the bubble field (not uniform purple)

#### Scenario: Onboarding guidance overlay
- **WHEN** the Discovery screen is displayed for the first time during onboarding
- **THEN** the page-help sheet for Discovery SHALL open on its own, as the page-help surface's "Auto-open on First Page Visit" requirement states
- **AND** the onboarding progress row SHALL be shown under the genre chips

#### Scenario: Background visual depth
- **WHEN** the Artist Discovery screen is displayed
- **THEN** the background SHALL include subtle visual elements (e.g., particle field, starfield, or animated gradient) to create depth
- **AND** these elements SHALL NOT compete with the foreground bubbles and orb for attention

### Requirement: Bubble Burst On Tap
When a user taps an artist bubble, the system SHALL play a burst effect that makes the bubble visibly pop in place before the absorption-into-orb animation continues, providing tactile "pop" feedback while preserving the orb color-injection metaphor.

#### Scenario: Bubble over-inflates then ruptures
- **WHEN** a user taps an artist bubble
- **THEN** the bubble SHALL briefly over-inflate (scale up beyond its rest size) as a short anticipation before rupturing
- **AND** a bright rupture ring plus an additive light bloom SHALL flash open at the burst point so the burst reads as a pop of light
- **AND** the over-inflation SHALL replace the previous horizontal squash anticipation

#### Scenario: Burst sprays luminous droplets in the bubble's hue
- **WHEN** the bubble ruptures
- **THEN** a spray of droplet particles (on the order of 15–20) SHALL be emitted immediately at the tap point
- **AND** the droplets SHALL be tinted with the tapped bubble's own hue but rendered luminously (additive glow with a white-hot core) so they read as sparks of light rather than flat same-color dots
- **AND** the droplets SHALL travel outward with a slight downward gravity so they arc like flung liquid, then fade out

#### Scenario: Burst hands off to absorption
- **WHEN** the burst anticipation reaches its peak
- **THEN** the existing absorption animation SHALL start (shrink, comet trail, color injection, shockwave) so the artist's color still flies into the orb

#### Scenario: Reduced motion suppresses the burst
- **WHEN** the user has `prefers-reduced-motion` enabled and taps a bubble
- **THEN** the over-inflation, rupture ring, and droplet spray SHALL be suppressed
- **AND** the interaction SHALL proceed directly to absorption, consistent with the existing reduced-motion handling

---

### Requirement: Similar Artist Chain Reaction
The system SHALL generate new artist recommendations dynamically using the backend ArtistService.ListSimilar RPC with a limit parameter. Tapping an artist bubble SHALL follow the artist; the follow shows at once and does not wait for the server. New bubbles SHALL be added to the bubble field under the field's capacity and deduplication rules.

#### Scenario: Similar artist bubble spawning
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL call the backend `ArtistService.ListSimilar` RPC with the selected artist's ID and `limit=30`
- **AND** the system SHALL deduplicate the results (excluding seen and followed artists)
- **AND** the system SHALL add the results to the bubble field, evicting the oldest bubbles if the field would exceed 50
- **AND** evicted bubbles SHALL be faded out before new bubbles spawn
- **AND** new bubbles representing similar artists SHALL spawn from the original bubble's position
- **AND** the new bubbles SHALL appear with a "pop" emergence animation
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Follow RPC called on bubble tap
- **WHEN** a user taps an artist bubble
- **THEN** the artist SHALL show as followed at once, before any server answer
- **AND** for a guest the follow SHALL be kept on the device and no request SHALL be sent for the follow itself
- **AND** for a signed-in fan the follow SHALL be sent to the server, and if it fails the follow SHALL be undone and the artist's bubble SHALL return to the field

#### Scenario: Similar artist spawning after search follow
- **WHEN** a user follows an artist from the search results and the absorption animation completes
- **THEN** the system SHALL trigger the same similar artist loading as a direct bubble tap
- **AND** new similar artist bubbles SHALL spawn from the horizontal centre of the canvas, 17% of the canvas height from its top

### Requirement: Search result item is fully tappable
Each search result item SHALL use the entire row as the interactive tap area, replacing the small follow button.

#### Scenario: Full row tap to follow
- **WHEN** the search results list is displayed
- **THEN** each result item row SHALL be tappable across its full width and height
- **AND** tapping anywhere on the row SHALL trigger the follow action for that artist
- **AND** the row SHALL NOT contain a separate follow button or + icon

#### Scenario: Visual affordance for tappable rows
- **WHEN** search result items are displayed
- **THEN** each unfollowed row SHALL display `cursor: pointer` on hover
- **AND** each row SHALL show a background color change on hover/active state
- **AND** the row SHALL have sufficient touch target size (minimum 48px height)

#### Scenario: Followed artist row is visually distinct and non-interactive
- **WHEN** a search result item represents an already-followed artist
- **THEN** the row SHALL display a ✓ (check) icon
- **AND** the row SHALL appear visually muted (reduced opacity or distinct styling)
- **AND** tapping the row SHALL have no effect (no duplicate follow, no animation)

---

### Requirement: Physics-Based Bubble Animation
The system SHALL implement smooth, natural bubble movement using physics simulation.

#### Scenario: Realistic bubble physics
- **WHEN** artist bubbles are displayed
- **THEN** the system SHALL use a physics engine (e.g., Matter.js, D3.js force simulation)
- **AND** bubbles SHALL float, bounce, and interact naturally
- **AND** performance SHALL be optimized for mobile devices using component optimization or Canvas/WebGL rendering

---

### Requirement: Small-screen bubble and orb density adaptation
On narrow canvases (width < 390px), the system SHALL limit the number of simultaneously rendered artist bubbles and constrain the DNA Orb radius to prevent visual crowding and maintain readability of bubble labels.

#### Scenario: Bubble count is capped on narrow screens
- **WHEN** the Discovery canvas width is less than 390px
- **THEN** the number of artist bubbles simultaneously rendered in the physics layer SHALL NOT exceed 30
- **AND** this cap SHALL apply both on initial render and when the bubble set is reconciled after the user follows an artist
- **AND** bubble size SHALL remain unchanged to preserve label readability

#### Scenario: Bubble count is uncapped on wider screens
- **WHEN** the Discovery canvas width is 390px or greater
- **THEN** the number of artist bubbles simultaneously rendered SHALL follow the existing pool capacity (up to 50)

#### Scenario: DNA Orb radius is constrained on narrow screens
- **WHEN** the Discovery canvas width is less than 390px
- **THEN** the DNA Orb rendered radius SHALL NOT exceed 70px

#### Scenario: DNA Orb radius follows follow-count on wider screens
- **WHEN** the Discovery canvas width is 390px or greater
- **THEN** the DNA Orb radius SHALL follow the existing follow-count-driven stage escalation (up to 90px)

#### Scenario: Bubble area top edge fades gracefully
- **WHEN** artist bubbles are rendered near the top boundary of the Discovery canvas
- **THEN** the bubble area SHALL apply a fade-out at its top edge so that bubbles dissolve toward the genre-chip bar rather than being hard-clipped at the boundary

#### Scenario: DNA Orb grows from a fixed bottom baseline on narrow screens
- **WHEN** the Discovery canvas width is less than 390px
- **THEN** the DNA Orb SHALL be anchored to a fixed baseline near the bottom of the canvas so its bottom stays at a constant offset from the canvas floor regardless of follow count
- **AND** as the user follows more artists the orb SHALL grow upward from that baseline rather than expanding around a fixed center
- **AND** the orb SHALL start from a small seed radius and remain unobtrusive at zero follows

#### Scenario: Bubble field fills toward the orb on narrow screens
- **WHEN** the Discovery canvas width is less than 390px
- **THEN** artist bubbles SHALL be distributed down the canvas toward the orb so that no large empty gap remains between the bubble cluster and the orb

#### Scenario: Bubble distribution is unchanged on wider screens
- **WHEN** the Discovery canvas width is 390px or greater
- **THEN** the existing bubble distribution SHALL be preserved

---

### Requirement: Bubble pool initialization based on followed-artist count
The system SHALL initialize the bubble pool differently based on whether the user follows any artists. On page load, the system SHALL hydrate the follow state from the persisted store before initializing the pool.

#### Scenario: No followed artists (Step 1-a)
- **WHEN** the discovery page loads
- **AND** the user follows zero artists (including after checking persisted guest state)
- **THEN** the system SHALL detect the user's country via browser timezone detection
- **AND** the system SHALL call `ArtistService.ListTop` with `limit=50` and the detected country
- **AND** if country detection returns empty, the system SHALL pass an empty country (global chart fallback)
- **AND** the system SHALL populate the bubble pool with the response artists

#### Scenario: User has followed artists (Step 1-b)
- **WHEN** the discovery page loads
- **AND** the user follows one or more artists (including artists restored from persisted guest state)
- **THEN** the system SHALL randomly select up to 5 followed artists as seeds
- **AND** the system SHALL call `ArtistService.ListSimilar` for each seed in parallel with the limit evenly distributed to fill the number of bubbles the screen shows: 50 total (e.g., 5 seeds × limit=10, 2 seeds × limit=25), or 30 on a screen narrower than 390 px (e.g., 5 seeds × limit=6)

#### Scenario: Seed results are revealed as each seed answers
- **WHEN** the initial load takes the similar-seed path on a cold visit
- **AND** one seed's `ListSimilar` response arrives while other seeds are still pending
- **THEN** that seed's artists SHALL replace ghost placeholder bubbles without waiting for the other seeds
- **AND** the field shown at that moment SHALL already exclude followed artists and duplicates
- **AND** the remaining ghost placeholder bubbles SHALL stay until later responses replace them or the load completes

#### Scenario: Progressive reveal converges to the all-at-once field
- **WHEN** every seed has answered (or failed) and any sparse top-up has been applied
- **THEN** the set of artists in the final field SHALL equal the set produced by applying the field invariants to all seed results and the top-up at once
- **AND** no ghost placeholder bubble SHALL remain

#### Scenario: A failed seed does not hold back the others
- **WHEN** one seed's `ListSimilar` call fails while the others succeed
- **THEN** the succeeding seeds' artists SHALL be revealed as they arrive
- **AND** the failed seed SHALL contribute no artists

#### Scenario: Seed selection with fewer than 5 followed artists
- **WHEN** the user follows fewer than 5 artists
- **THEN** the system SHALL use all followed artists as seeds
- **AND** the limit per seed SHALL be `floor(N / followedCount)`, where N is the number of bubbles the screen shows (50, or 30 below 390 px)

#### Scenario: Follow state hydration on page reload
- **WHEN** the discovery page loads during onboarding
- **AND** previously followed artists exist in persisted guest storage
- **THEN** the system SHALL restore the followed-artist state from persisted storage before initializing the bubble pool
- **AND** the restored followed-artist IDs SHALL be used for deduplication when loading the initial bubble pool
- **AND** the restored followed artists SHALL be passed as input when initializing the bubble pool

### Requirement: Bubble pool deduplication
The system SHALL remove duplicate and already-followed artists from the bubble field. The followed artists SHALL be the fan's current follows at the moment the field is produced or updated.

#### Scenario: Deduplication on initial load (Step 2)
- **WHEN** the bubble field is populated from any source
- **THEN** the system SHALL remove artists that match any already-seen artist by name (case-insensitive), internal ID, or MBID
- **AND** the system SHALL remove artists the fan currently follows
- **AND** the system SHALL cap the field at a maximum of 50 bubbles

#### Scenario: Deduplication after tap refill (Step 5)
- **WHEN** similar artists are added to the field after a tap
- **THEN** the system SHALL apply the same deduplication rules as Step 2, against the fan's current follows
- **AND** already-seen artists from prior fetches SHALL be excluded

#### Scenario: Deduplication on genre reload
- **WHEN** the genre filter reloads the bubble field
- **THEN** the system SHALL apply the same deduplication rules as Step 2, against the fan's current follows

### Requirement: Tap-to-refill flow
The system SHALL fetch similar artists on each bubble tap and manage the bubble pool's lifecycle accordingly.

#### Scenario: Successful tap and refill (Steps 3-4)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL follow the tapped artist
- **AND** the system SHALL call `ArtistService.ListSimilar` with `limit=30` for the tapped artist
- **AND** the system SHALL add deduplicated results to the pool via the coordinated eviction mechanism
- **AND** the cycle SHALL repeat for subsequent taps (Step 6)

#### Scenario: No similar artists found
- **WHEN** the `ListSimilar` response leaves no new artist after deduplication
- **THEN** the system SHALL first refill from the top artists, as "Canvas replenishes bubbles when similar artists are exhausted" states
- **AND** only when the top artists also leave no new artist SHALL the system display an informational snack 「{{name}}の類似アーティストはこれ以上ありません」
- **AND** the system SHALL NOT evict any existing bubbles

#### Scenario: ListSimilar RPC failure
- **WHEN** the `ListSimilar` call fails
- **THEN** the system SHALL NOT evict any existing bubbles
- **AND** the system SHALL display a warning snack to the user

### Requirement: Canvas replenishes bubbles when similar artists are exhausted
When a user follows an artist and the similar-artist lookup returns no new (unseen) artists, the system SHALL automatically fetch replacement bubbles from the top-artist pool to keep the canvas populated.

#### Scenario: Similar artists fully deduplicated
- **WHEN** user taps a bubble AND the similar-artist lookup returns zero new bubbles after deduplication
- **THEN** the system SHALL fetch fresh artists from the top-artist pool as replacements
- **AND** any unseen artists SHALL be spawned as new bubbles near the absorption point

#### Scenario: Top artist pool also exhausted
- **WHEN** user taps a bubble AND both similar artists and replacement bubbles return zero new artists
- **THEN** the system SHALL keep the remaining bubbles without an error
- **AND** the system SHALL display the informational snack 「{{name}}の類似アーティストはこれ以上ありません」

#### Scenario: Replacement bubbles partially available
- **WHEN** user taps a bubble AND similar artists are exhausted but 5 of 50 top artists are unseen
- **THEN** the system SHALL spawn only the 5 unseen artists as new bubbles
- **AND** the previously seen artists SHALL NOT reappear on the canvas

### Requirement: Bubble Field Consistency and Capacity Enforcement

The discovery page SHALL manage the current display field (`Artist[]`) as the
single source of truth for which artist bubbles are shown, and every other
representation — the physics bodies, any cache — SHALL be a derived
projection of that field. Pool state and physics state SHALL be synchronized
such that the rendered physics-body count equals the field count at rest,
including after a background refresh replaces the field. No representation
other than the field SHALL hold authoritative membership. The discovery page
SHALL enforce a 50-bubble capacity limit by coordinating pool eviction with
physics fade-out in a single atomic operation.

#### Scenario: Adding bubbles synchronizes pool and physics
- **WHEN** new artist bubbles are added to the field
- **THEN** the discovery page SHALL update the field AND the physics projection SHALL reconcile to it
- **AND** the field count and physics body count SHALL be equal after the operation

#### Scenario: Removing a bubble synchronizes pool and physics
- **WHEN** an artist bubble is removed from the field (e.g., followed)
- **THEN** the discovery page SHALL remove it from the field AND the physics projection SHALL remove the body
- **AND** no orphaned physics bodies SHALL remain

#### Scenario: Eviction synchronizes pool and physics
- **WHEN** the field owner evicts oldest bubbles to make room for new ones
- **THEN** the evicted physics bodies SHALL fade out
- **AND** the evicted artists SHALL be removed from the field
- **AND** the field and physics counts SHALL remain equal after eviction completes

#### Scenario: Background refresh preserves render parity
- **WHEN** a background load produces a new field that differs from the currently rendered set
- **THEN** the physics projection SHALL converge to exactly the new field
- **AND** the rendered body count SHALL equal the new field count at rest
- **AND** no field member SHALL be dropped from rendering because fading-out bodies temporarily occupied capacity

#### Scenario: Adding bubbles within capacity
- **WHEN** new bubbles are added and current count plus new count does not exceed 50
- **THEN** the discovery page SHALL add all new bubbles without eviction

#### Scenario: Adding bubbles exceeding capacity
- **WHEN** new bubbles are added and current count plus new count exceeds 50
- **THEN** the discovery page SHALL first fade out the oldest physics bodies (FIFO)
- **AND** SHALL remove the corresponding pool entries
- **AND** SHALL then add the new bubbles to both pool and physics
- **AND** the total count SHALL NOT exceed 50

### Requirement: Bubble canvas reads deferred until element is visible
The system SHALL NOT read canvas dimensions while the canvas element has `display: none` or zero-size layout.

#### Scenario: Canvas rect read when visible
- **WHEN** the system needs canvas dimensions and the canvas element is visible
- **THEN** the system SHALL return accurate width and height values

#### Scenario: Canvas rect read when hidden
- **WHEN** the system needs canvas dimensions and the canvas element is hidden (e.g., during search mode)
- **THEN** the system SHALL defer the read until the element becomes visible (via `requestAnimationFrame`)
- **AND** SHALL NOT spawn bubbles at position (0, 0)

### Requirement: Bubble field reset restores global top artists
The system SHALL provide a reset operation that discards the current bubble field and re-seeds it with the global top artists, keeping pool state and physics state synchronized. The reset SHALL be independent of the user's followed artists and SHALL NOT use the follow-seeded similar-artist path.

#### Scenario: Reset replaces the pool with global top artists
- **WHEN** the reset operation is invoked
- **THEN** the system SHALL fetch the global top artists for the user's country with no genre filter, up to 50 artists
- **AND** SHALL exclude followed artists from the result
- **AND** SHALL replace the entire pool with the deduplicated result capped at the 50-bubble limit

#### Scenario: Reset clears accumulated discovery state
- **WHEN** the reset operation is invoked after similar-artist bubbles have accumulated
- **THEN** the system SHALL clear the deduplication seen-sets and re-track only the newly seeded artists
- **AND** SHALL discard prior eviction history so the new field is a clean baseline

#### Scenario: Reset re-synchronizes physics state
- **WHEN** the reset operation completes
- **THEN** the canvas SHALL be reloaded so the rendered physics bodies match the new pool
- **AND** the pool count and physics body count SHALL be equal after reset completes

### Requirement: Initial load tops up a sparse discovery field
When the user already follows artists, the initial load seeds bubbles from those artists' similar artists. Because the similar lists shrink as follow count grows (seeds are capped, the per-seed limit shrinks, and deduplication removes followed and overlapping artists), the system SHALL top up the field with global top artists whenever the deduplicated seed-similar results fall below 30 bubbles. Similar artists SHALL keep priority. This guarantees the field is never empty and stays reasonably full regardless of how many artists the user follows. Whether global top artists are appended SHALL be decided only by the 30-bubble rule, independent of when they were requested.

#### Scenario: Sparse seed-similar results are topped up
- **WHEN** the initial load takes the similar-seed path and the deduplicated similar results are below 30 bubbles
- **THEN** the system SHALL append global top artists (deduplicated against followed and already-included artists) up to the bubble cap
- **AND** the similar artists SHALL retain priority order ahead of the top-artist fillers

#### Scenario: Empty seed-similar still fills the field
- **WHEN** the similar lookups resolve to nothing (no matches, errors, or all results deduped away)
- **THEN** the system SHALL fill the field with global top artists rather than leaving it empty

#### Scenario: Sufficient seed-similar results are not diluted
- **WHEN** the deduplicated similar results meet or exceed 30 bubbles
- **THEN** the system SHALL NOT append top artists to the field, even if they were already fetched

#### Scenario: Top-up does not wait for a second round trip
- **WHEN** the deduplicated similar results are below 30 bubbles once every seed has answered
- **THEN** the top-up SHALL be applied without starting a new `ArtistService.ListTop` call after the seed lookups finish

### Requirement: Physics layer is a pure projection of the field
The physics/canvas layer SHALL render the field it is given and SHALL NOT own bubble policy. It SHALL NOT apply the capacity cap, deduplication, or followed-artist exclusion; those are guaranteed upstream by the field owner. The physics layer SHALL expose a reconcile operation that diffs its current bodies against a target `Artist[]` and applies only the additions and removals needed to match it. As a safety net it SHALL never hold more than 50 active bodies; an addition beyond 50 SHALL be skipped and logged, never dropped silently and never thrown.

#### Scenario: Reconcile to a target list
- **WHEN** the physics layer is asked to reconcile to a target field
- **THEN** it SHALL keep bodies whose artist is still in the target, remove bodies no longer in the target, and add bodies for new artists in the target
- **AND** the resulting body set SHALL equal the target

#### Scenario: Fading-out bodies do not block replacements
- **WHEN** bodies are fading out while new artists are being added in the same reconcile
- **THEN** the fading-out bodies SHALL NOT count against capacity such that new artists are dropped
- **AND** every artist in the target SHALL receive a body

#### Scenario: Physics never silently drops a target member
- **WHEN** a reconcile target is applied
- **THEN** the physics layer SHALL NOT silently discard any target artist due to a capacity check
- **AND** if the 50-body safety cap is ever hit, the skipped additions SHALL be logged rather than dropped silently

#### Scenario: Stale bodies removed on artist set replacement
- **WHEN** the canvas receives a new set of real (non-ghost) artists
- **AND** the physics engine already holds bodies from a previous artist set
- **THEN** bodies whose artist is not in the new set SHALL be faded out and removed
- **AND** the total active body count SHALL remain within 50 throughout the transition

### Requirement: Bubble invariants are applied once at the field boundary
The invariants — exclude followed artists, deduplicate by name/id/mbid, and enforce the 50-bubble capacity — SHALL be applied exactly once, when the field owner produces or updates the field. Downstream consumers (router hooks, genre/reset/search flows, the physics layer) SHALL NOT re-apply these invariants independently.

#### Scenario: Followed exclusion happens once
- **WHEN** the field is produced or updated from any source (initial load, cache re-entry, genre, reset, similar top-up)
- **THEN** followed-artist exclusion SHALL be applied by the field owner as part of producing the field
- **AND** no consumer SHALL re-filter followed artists after the field is produced

#### Scenario: Capacity enforced once
- **WHEN** the field is produced or updated
- **THEN** the 50-bubble capacity SHALL be enforced by the field owner
- **AND** the physics layer SHALL receive a field already within capacity and SHALL NOT re-cap it

### Requirement: Bubble UI re-experience on Discover tab
The system SHALL provide the onboarding Bubble UI as a reusable discovery experience on the Discover tab, with a simplified 3-row grid layout. After following an artist, the Discovery page SHALL call `ConcertService.ListByArtist` to check for existing concerts and update the onboarding progress row. The page SHALL NOT call `SearchNewConcerts` directly.

#### Scenario: Default Bubble UI display
- **WHEN** the Discover tab is opened
- **THEN** the system SHALL display the physics-based artist Bubble UI (same as onboarding)
- **AND** the DNA Orb SHALL be displayed at the bottom
- **AND** tapping a bubble SHALL trigger the absorption animation and follow the artist (kept on the device for a guest, sent to the server for a signed-in fan)
- **AND** the page SHALL be laid out as the search bar, the genre chips (with the onboarding progress row under them while onboarding), and the bubble area filling the rest

#### Scenario: Genre filtering
- **WHEN** the Bubble UI is displayed
- **THEN** genre/tag chips SHALL be displayed above the bubble area (e.g., Rock, Pop, Anime, Jazz, Electronic, Hip-Hop)
- **AND** tapping a genre chip SHALL regenerate bubbles with artists from that genre via `ArtistService.ListTop` with the selected tag
- **AND** genre results SHALL be global (not country-filtered), because the top-artist listing does not accept a genre and a country together
- **AND** the active genre chip SHALL be visually highlighted

#### Scenario: Genre deselection reverts to regional results
- **WHEN** a genre chip is active
- **AND** the user taps the same genre chip again (deselection)
- **THEN** the system SHALL regenerate bubbles using `ArtistService.ListTop` with the detected country and no tag
- **AND** the system SHALL return to showing regional top artists

#### Scenario: Already-followed artists
- **WHEN** the bubble field is shown
- **THEN** no bubble SHALL represent an artist the fan already follows, as "Bubble pool deduplication" states
- **AND** a bubble SHALL leave the field as soon as its artist is followed

#### Scenario: Concert check after follow uses List RPC
- **WHEN** a user follows an artist from the Discovery page (bubble tap or search follow)
- **THEN** the page SHALL call `ConcertService.ListByArtist(artistId)` to check for existing upcoming concerts
- **AND** SHALL NOT call `SearchNewConcerts`
- **AND** if concerts exist, the page SHALL show a snack notification and count the artist as having a found concert for the onboarding progress row

#### Scenario: Concert check at page load uses List RPC
- **WHEN** the Discovery page loads and there are pre-seeded guest follows
- **THEN** the page SHALL call `ConcertService.ListByArtist(artistId)` for each followed artist
- **AND** SHALL NOT call `SearchNewConcerts`
- **AND** each artist that has stored concerts SHALL count as having a found concert for the onboarding progress row

### Requirement: Manual search on Discover tab
The system SHALL provide a text search for targeted artist discovery.

#### Scenario: Search bar display
- **WHEN** the Discover tab is opened
- **THEN** a search bar SHALL be displayed at the top of the screen

#### Scenario: Entering search mode
- **WHEN** a user taps the search bar and begins typing
- **THEN** the Bubble UI SHALL be hidden
- **AND** search results SHALL appear as a vertical list below the search bar

#### Scenario: Search results
- **WHEN** search results are displayed
- **THEN** each result SHALL be a row tappable across its full area, as "Search result item is fully tappable" states
- **AND** tapping an unfollowed row SHALL follow the artist and trigger the DNA Orb absorption effect
- **AND** already-followed artists SHALL show a ✓ and SHALL NOT respond to a tap

#### Scenario: Exiting search mode
- **WHEN** a user clears the search text or taps the clear button
- **THEN** the search results SHALL be hidden
- **AND** the Bubble UI SHALL be restored

### Requirement: Search bar icon explicit sizing
The search bar SVG icons SHALL have explicit intrinsic dimensions to prevent layout overflow.

#### Scenario: Search icon renders at fixed size
- **WHEN** the discover page renders
- **THEN** the `.search-icon` SVG SHALL have explicit `inline-size` and `block-size` values
- **AND** the icon SHALL have `flex-shrink: 0` to prevent compression by the flex container
- **AND** the search bar SHALL maintain a compact single-line height regardless of viewport width

#### Scenario: Clear button renders at fixed size
- **WHEN** a search query is entered and the clear button appears
- **THEN** the `.clear-button` SHALL have explicit `inline-size` and `block-size` values
- **AND** the button SHALL have `flex-shrink: 0` to prevent compression
- **AND** the button's SVG child SHALL be constrained to the button's dimensions

---

### Requirement: Bubble physics pauses when Discover tab is inactive
The system SHALL manage Bubble UI resources efficiently while the bubble field is not visible.

#### Scenario: Search mode pauses the simulation
- **WHEN** the user enters search mode
- **THEN** the physics simulation SHALL be paused, and it SHALL resume when search mode ends

#### Scenario: All Nearby view pauses the simulation
- **WHEN** the fan switches Discovery to the All Nearby view
- **THEN** the physics simulation SHALL be paused
- **AND** it SHALL resume when the fan switches back to the artist bubbles, unless search mode is on or the document is hidden

#### Scenario: Hidden document pauses the simulation
- **WHEN** the document becomes hidden (the app goes to the background or the browser tab is switched)
- **THEN** the physics simulation SHALL be paused, and it SHALL resume when the document is visible again

#### Scenario: Tab deactivation
- **WHEN** the user navigates away from the Discover tab
- **THEN** the physics simulation SHALL be stopped and its resources released

#### Scenario: Tab reactivation
- **WHEN** the user returns to the Discover tab
- **THEN** the bubble field SHALL be drawn again from the cached field, as "Discovery bubble pool caching on re-entry" states

### Requirement: Reset to Top 50 control
The Discover tab SHALL provide a Reset control that returns the bubble field to the global Top 50 artists, independent of the user's followed artists. The control SHALL be an icon-only (refresh/reset) button placed at the leading edge of the genre row as a fixed sibling beside the horizontally-scrollable genre chips, so it remains visible while the chips scroll. The control SHALL expose an accessible label.

#### Scenario: Reset restores global Top 50
- **WHEN** the user activates the Reset control
- **THEN** the system SHALL replace the entire bubble pool with the global Top 50 artists fetched via `listTop(country, '', 50)`
- **AND** SHALL NOT use the follow-seeded similar-artist load path
- **AND** the followed artists SHALL be excluded from the displayed bubbles

#### Scenario: Reset clears active genre filter
- **WHEN** a genre chip is active and the user activates the Reset control
- **THEN** the system SHALL clear the active genre selection
- **AND** no genre chip SHALL remain in the active state after reset

#### Scenario: Reset control stays visible while chips scroll
- **WHEN** the genre chips are scrolled horizontally
- **THEN** the Reset control SHALL remain visible at the leading edge of the genre row
- **AND** the genre chips SHALL scroll within their own container beside the control, never overlapping or obscuring it

#### Scenario: Reset control is accessible
- **WHEN** assistive technology inspects the Reset control
- **THEN** the control SHALL expose a descriptive accessible label
- **AND** SHALL be operable as a button

### Requirement: Discovery bubble pool caching on re-entry
The system SHALL cache the last successfully generated bubble field (`Artist[]`) in a single app-lifetime store so that discovery page re-entries can paint real artists immediately without waiting on network RPCs. There SHALL be exactly one authoritative bubble-field cache; the raw `listTop` SWR cache and the display-field cache SHALL NOT be maintained as two independent snapshots of the same field.

#### Scenario: Re-entry paints cached artists instantly
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** at least one cached artist is not yet followed
- **THEN** the bubble field SHALL be initialized from the cached field synchronously while the page loads
- **AND** followed artists SHALL be excluded as part of producing the field
- **AND** no ghost bubbles SHALL be shown
- **AND** any background refresh SHALL reconcile the field via a non-destructive delta (see "Re-entry preserves the in-session bubble field"), NOT a wholesale replacement that recomposes or shrinks the visible field

#### Scenario: Re-entry with all cached artists already followed
- **WHEN** the user navigates to Discovery after a prior visit
- **AND** every artist in the cached field has since been followed
- **THEN** producing the field SHALL exclude all of them, leaving the field empty (no stale bubbles rendered)
- **AND** the background refresh SHALL run immediately and refill the field with fresh artists
- **AND** the field SHALL remain empty until the refresh completes (ghost placeholder bubbles are NOT shown on the cached-but-filtered path, unlike a cold visit)

#### Scenario: Cache excludes followed artists on re-entry
- **WHEN** the cached bubble field contains artists that the user has since followed
- **THEN** those artists SHALL be excluded when the field is produced
- **AND** the followed artists SHALL NOT appear as bubbles in the physics engine

#### Scenario: Cold visit uses ghost bubbles
- **WHEN** Discovery is shown for the first time in the page and no field has been built yet (the initial load is still running)
- **THEN** the route SHALL initialize with ghost placeholder bubbles
- **AND** ghost bubbles SHALL switch to real artists in place as artists arrive (per seed on the similar-seed path, all at once on the top-artists path)

#### Scenario: Initial load starts during start-up when the app opens on Discovery
- **WHEN** the page is opened on Discovery
- **THEN** the initial load SHALL start during app start-up, without waiting for the route to load: once the session is known; for a signed-in fan, at once when follows are kept on the device for the account (see "Seeds come from the follows kept on the device"), otherwise after the follow list; and after restoring an onboarding guest's persisted follows
- **AND** if the field is built before the route shows it, the route SHALL show those artists directly, without ghost placeholder bubbles
- **AND** the route SHALL NOT start a second initial load while the start-up load is running

#### Scenario: Seeds come from the follows kept on the device
- **WHEN** a signed-in fan's follow list has been loaded on this device before, for the same account
- **AND** the app opens on Discovery
- **THEN** the start-up initial load SHALL choose its seeds from the followed artists kept from that load, without waiting for this session's follow list
- **AND** the field SHALL still exclude the artists in the follow list current when the field is set
- **AND** signing out SHALL remove the kept follows, and another account SHALL NOT use them

#### Scenario: Cache is updated after each successful load
- **WHEN** an initial load or refresh completes successfully
- **THEN** the resulting field SHALL be persisted to the single bubble-field cache
- **AND** the next re-entry SHALL use the updated field

### Requirement: Re-entry preserves the in-session bubble field
Within a session, navigating away from Discovery and back SHALL preserve the field the user was viewing rather than re-deriving it. When the cached field is fresh (within a 15-minute cache TTL), the system SHALL reuse it and apply only a non-destructive delta; it SHALL NOT perform a wholesale replacement that recomposes the field or reduces it below the 30-bubble display floor.

#### Scenario: Fresh field is reused on re-entry
- **WHEN** the user returns to Discovery within the 15-minute cache TTL
- **THEN** the previously displayed field SHALL be reused as the starting field
- **AND** the rendered bubble count SHALL NOT drop below the count shown before leaving, except for artists the user followed while away

#### Scenario: Non-destructive delta on refresh
- **WHEN** a background refresh runs on re-entry
- **THEN** it SHALL remove only newly-followed artists and top up only if the field is below 30 bubbles
- **AND** it SHALL NOT replace the entire field with a freshly-fetched set that changes composition or shrinks the field

#### Scenario: Follow while away is reconciled without collapsing the field
- **WHEN** the user followed one or more artists on another route and returns to Discovery
- **THEN** only the newly-followed artists SHALL be removed from the field
- **AND** the remaining bubbles SHALL stay, with top-up applied only to restore the 30-bubble display floor

#### Scenario: Stale field triggers a full reload
- **WHEN** the user returns to Discovery after the 15-minute cache TTL has expired
- **THEN** the system MAY perform a full reload as on a cold visit
- **AND** the reload SHALL still converge to a field within capacity with render parity

### Requirement: Bubble Tap Sound Character

The discovery page SHALL play a single fixed two-part "pu-chu" pop sound effect when a user taps an artist bubble, synthesized procedurally via the Web Audio API (no recorded audio assets), such that the tap reads as a crisp, satisfying bubble pop rather than a retro-game tone. Every tap SHALL sound identical — there is no musical scale, no per-bubble pitch, and no combo.

#### Scenario: Tap plays a fixed pop on every tap
- **WHEN** a user taps an artist bubble and audio is unlocked and not muted
- **THEN** the system SHALL play the same fixed pop regardless of which bubble is tapped
- **AND** the pop SHALL NOT vary in pitch with the bubble's hue or with how rapidly taps occur

#### Scenario: Pop is a low "pu" thump followed by a high "chu" chirp
- **WHEN** the tap pop is synthesized
- **THEN** a low-pitched plosive "pu" thump SHALL fire first
- **AND** a higher-pitched "chu" chirp SHALL fire a short beat later (on the order of ~20ms) so the pop reads as two distinct parts
- **AND** the "chu" chirp's pitch SHALL drop quickly from above onto its target pitch (a fast downward chirp animated with a Web Audio frequency ramp, not held constant)

#### Scenario: Pop has a plosive noise breath
- **WHEN** the "pu" thump begins
- **THEN** a short low-pass-filtered noise burst SHALL be layered at its attack to provide the lippy plosive onset

#### Scenario: Pop timbre is dry and percussive
- **WHEN** the pop plays
- **THEN** each voice's amplitude SHALL rise quickly and decay to near-silence within a short interval (a short percussive tail, not a sustained tone)
- **AND** the low-pass resonance SHALL be low so the pop reads as dry and crisp rather than wet or wobbly

---

### Requirement: Landing Tone On Absorption

When a tapped bubble completes its absorption into the orb, the system SHALL play a soft, low fixed settle ("landing") tone.

#### Scenario: Absorption completion plays a settle tone
- **WHEN** a bubble finishes being absorbed into the orb
- **THEN** the system SHALL play a soft, low fixed tone that settles downward in pitch
- **AND** the tone SHALL be the same on every absorption (it does not derive from the bubble's hue) and SHALL omit the plosive noise breath

---

### Requirement: Sound Respects Mute and Volume Settings

The tap and landing sounds SHALL honor the user's existing mute and volume preferences and the browser autoplay policy.

#### Scenario: Muted user taps a bubble
- **WHEN** the user has muted sound and taps a bubble
- **THEN** no audible tap or landing tone SHALL be produced

#### Scenario: Volume preference applied
- **WHEN** the user has set a volume level
- **THEN** the tap and landing tones SHALL be scaled to that level via the master output

#### Scenario: Audio unlocked within a user gesture
- **WHEN** audio has not yet been unlocked by a user gesture
- **THEN** no AudioContext SHALL be forcibly started outside a gesture, consistent with the existing lazy-unlock behavior

### Requirement: Discover page debounces search with stale response guard
The Discovery screen SHALL debounce artist search input by 300ms and discard stale responses.

#### Scenario: Search is debounced
- **WHEN** the search query changes
- **THEN** no search request SHALL be sent until 300ms after the last change

#### Scenario: Stale search response is discarded
- **WHEN** the search query changes again before a previous search responds
- **THEN** the previous response SHALL be discarded

#### Scenario: Genre tag toggle activates and deactivates
- **WHEN** a genre chip is selected and then selected again
- **THEN** the first selection SHALL load the top artists of that genre and the second SHALL load the regional top artists with no genre

#### Scenario: Clear search restores bubble view
- **WHEN** the fan clears the search
- **THEN** the search query SHALL be emptied and the bubble canvas SHALL resume

### Requirement: Followed count reflects localStorage state
The count of followed artists SHALL update at once whenever the fan follows, unfollows, or clears all followed artists, so that everything that shows the count changes immediately. The orb's intensity SHALL grow with the follows made during the current visit to Discovery.

#### Scenario: Initial page load with existing guest data
- **WHEN** an onboarding guest with 3 follows kept on the device opens Discovery
- **THEN** the followed count is 3 and the onboarding progress row reflects the 3 follows
- **AND** the orb starts at its resting size, since no follow has been made during this visit

#### Scenario: Follow an artist during onboarding
- **WHEN** the user taps a bubble to follow an artist
- **THEN** the orb SHALL receive a color injection with the bubble's hue
- **AND** the orb's base intensity SHALL increase per the easing curve

#### Scenario: Unfollow an artist
- **WHEN** the user unfollows a previously followed artist
- **THEN** the followed count SHALL decrement by 1 immediately
- **AND** the orb's base intensity SHALL NOT decrease (visual intensity is one-directional within a session)

### Requirement: Search and genre filter available during onboarding
The search bar and genre filter chips SHALL be visible and functional during onboarding, allowing users to find specific artists they already know.

#### Scenario: Onboarding user searches for an artist
- **WHEN** the user is in onboarding mode and types a query into the search bar
- **THEN** search results SHALL appear and the user SHALL be able to follow artists from the results
- **AND** the follow SHALL be kept the same way as a bubble-tap follow (on the device for a guest, on the server for a signed-in fan)

### Requirement: Search result follow triggers bubble view transition and absorption animation
When a user follows an artist from the search results, the system SHALL transition back to the bubble view, wait for the canvas to be visible, and play the orb absorption animation, providing the same visual feedback as a direct bubble tap.

#### Scenario: Follow from search triggers absorption
- **WHEN** a user taps a search result item for an unfollowed artist
- **THEN** the system SHALL execute the follow action (optimistic UI update)
- **AND** the system SHALL exit search mode (clear results, hide search result list)
- **AND** the system SHALL resume the bubble canvas
- **AND** the system SHALL wait for the canvas to be visible with a non-zero size
- **AND** the system SHALL spawn a temporary bubble at the horizontal centre of the canvas, 17% of the canvas height from its top
- **AND** the system SHALL immediately start the absorption animation for that bubble toward the orb
- **AND** on absorption completion, the orb SHALL absorb the bubble's hue
- **AND** the system SHALL request similar artists immediately, not after the absorption completes

#### Scenario: Search input is cleared after follow
- **WHEN** a user follows an artist from the search results
- **THEN** the search query input SHALL be cleared
- **AND** the search mode SHALL be deactivated

#### Scenario: Follow failure rolls back and stays in search mode
- **WHEN** a user taps a search result item
- **AND** the follow action fails (network error or backend error)
- **THEN** the system SHALL NOT exit search mode
- **AND** the system SHALL NOT spawn or absorb a bubble
- **AND** the system SHALL display an error snack telling the fan that the follow failed
- **AND** the search results SHALL remain visible and interactive

### Requirement: Snack announces an artist's upcoming live events
The system SHALL provide instant feedback about available live events with a snack.

#### Scenario: Live event notification on artist follow
- **WHEN** a user follows an artist
- **AND** the artist has upcoming live events in the catalog
- **THEN** the system SHALL display a snack with the message 「{{name}}の開催予定のライブが見つかりました！」
- **AND** the snack SHALL stay for the duration the snack-bar surface sets for its length, then fade out

#### Scenario: No notification for artists without events
- **WHEN** a user taps an artist bubble
- **AND** the artist has no upcoming live events in the database
- **THEN** the system SHALL NOT display a snack
- **AND** the bubble absorption animation SHALL proceed normally

### Requirement: Revealed bubble names fade in on real time
When a bubble appears (a ghost switching to a real artist, or a new artist added to the field), its artist name SHALL become readable within 300 ms of real time, at any frame rate down to 10 frames per second. The fade-in SHALL follow elapsed real time and SHALL NOT slow down when frames take longer.

#### Scenario: Normal frame rate
- **WHEN** a ghost bubble switches to a real artist and frames arrive every 16 ms
- **THEN** the artist name is drawn within 300 ms of the switch

#### Scenario: Slow frames
- **WHEN** a ghost bubble switches to a real artist and frames arrive every 100 ms
- **THEN** the artist name is drawn within 300 ms of the switch, not after the longer time a 32 ms per-frame cap would imply

#### Scenario: Reduced motion
- **WHEN** the user prefers reduced motion
- **THEN** the artist name is readable no later than with motion enabled

### Requirement: Cold-load reveal timings are reported
On a cold visit to Discovery (the first time Discovery is shown in the page, including when the start-up load already built the field), the fan app SHALL send exactly one usage analytics event once all bubbles show artist names, carrying the time from the moment Discovery was opened to: the first bubble drawn (a ghost placeholder, or an artist when the artists arrive before any ghost is drawn), the first artist name drawn, and every bubble showing an artist name, in milliseconds. The moment Discovery was opened is the start of the page load when Discovery is the first page of the visit, and the start of the in-app navigation otherwise; the event SHALL state which of the two applies. It SHALL also state which initial-load path ran (top artists or similar seeds) and the number of seeds. Re-entries that paint a cached field SHALL NOT send this event. The event SHALL obey the analytics consent setting and the query-string rule of the analytics surface.

#### Scenario: Cold visit with followed artists
- **WHEN** a fan who follows artists opens Discovery with no cached field and analytics on
- **THEN** one event is sent with the similar-seed path, the seed count, whether Discovery was the first page, and the three timings in milliseconds

#### Scenario: Artists arrive before a ghost is drawn
- **WHEN** a cold visit's artists arrive before the first ghost bubble is drawn
- **THEN** one event is sent, with the time to the first bubble drawn taken from the first artist bubble

#### Scenario: Re-entry
- **WHEN** the fan returns to Discovery within the session and the cached field is painted
- **THEN** no reveal-timing event is sent

#### Scenario: Analytics off
- **WHEN** the fan has turned analytics off in Settings
- **THEN** no reveal-timing event is sent

#### Scenario: Leaving before the reveal completes
- **WHEN** the fan leaves Discovery before every bubble shows an artist name
- **THEN** no reveal-timing event is sent for that visit

### Requirement: Ghost placeholder bubbles ignore taps
A ghost placeholder bubble SHALL NOT respond to a tap or to keyboard selection: no follow, no similar-artist request, no sound or haptic feedback. Real artist bubbles shown next to ghost bubbles during a progressive reveal SHALL respond to taps as usual.

#### Scenario: Tap on a ghost
- **WHEN** the fan taps a ghost placeholder bubble during a cold load
- **THEN** nothing is followed, no similar artists are requested, and the ghost stays in place

#### Scenario: Tap on a revealed artist while other bubbles are still ghosts
- **WHEN** the fan taps a revealed artist bubble while other bubbles are still ghosts
- **THEN** the artist is followed and similar artists are requested once the initial load has finished, as for any tap

### Requirement: Cold load meets a time budget
On the reference setup, a cold load of Discovery SHALL draw the first artist name within 6.0 s of the start of the page load for a signed-in fan with followed artists, and within 3.0 s for a guest, each as the median of about 10 loads. The time to the first bubble and from the first bubble to the first name SHALL be measured and recorded with each release of this work, but are not held to a bound: drawing the ghost bubbles sooner lengthens the second without making the fan wait longer. The reference setup is desktop Chrome with device emulation at a 375 px viewport, DevTools' "Slow 4G" network throttling and 4x CPU throttling (the Lighthouse mobile profile), and the HTTP cache enabled, on a repeat visit (the app's code already cached). The times are those reported by the cold-load reveal timings (`ghosts_ms`, `first_name_ms`). A first visit, which downloads the app's code, is reported but not held to the bounds.

#### Scenario: Signed-in fan with followed artists
- **WHEN** a signed-in fan who follows artists opens Discovery about 10 times on the reference setup
- **THEN** the median time from the start of the page load to the first artist name is at most 6.0 s
- **AND** the median times to the first bubble and from the first bubble to the first name are recorded

#### Scenario: Guest
- **WHEN** a guest who follows no artists opens Discovery about 10 times on the reference setup
- **THEN** the median time from the start of the page load to the first artist name is at most 3.0 s
- **AND** the median times to the first bubble and from the first bubble to the first name are recorded

### Requirement: A guest's follows and the ready timetable are reported

While the fan is a guest, each follow that takes effect SHALL send one usage analytics event with the artist and the number of artists the guest now follows; a signed-in fan's follow is reported by the server. When the onboarding progress row is shown as the link to the Dashboard (the row is hidden while search results are shown), the page SHALL send one usage analytics event with the number of followed artists and of artists with concerts at that moment, at most once per visit to Discovery.

#### Scenario: Guest follows a fifth artist
- **WHEN** a guest who follows 4 artists follows another
- **THEN** one guest-follow event is sent with that artist and a count of 5

#### Scenario: Timetable becomes ready
- **WHEN** an onboarding fan's follows make the progress row ready
- **THEN** one timetable-ready event is sent with the two counts

#### Scenario: Ready while searching
- **WHEN** an onboarding fan's follow from search results makes the progress row ready
- **THEN** no timetable-ready event is sent until the search is closed and the row is shown

### Requirement: Onboarding progress row
While the fan is onboarding, the Discovery screen SHALL show a progress row directly under the genre chips that tells how close the fan's timetable is to ready. The row SHALL sit outside the bubble field, so it never overlaps a bubble or the orb. Its value SHALL be (followed artists without a found concert) / 5 + (followed artists with a found concert) / 3, capped at 1, where a concert is found for an artist when the catalog lookup after its follow returns at least one concert. Below 1 the row SHALL show the label 「タイムテーブル完成まで」, a bar filled to the value and the value in percent; the bar SHALL move to a new value with a short animation (none with a reduced-motion preference). At 1 the row SHALL become a button labelled 「完成しました！」 that opens the Dashboard, with an icon of the finished timetable that invites the tap in place of an arrow; its accessible name also says where it leads (「タイムテーブルを見る」). The row SHALL expose its value to assistive technology as a progress value from 0 to 100 percent. The row SHALL be hidden in search mode, like the genre chips, and SHALL NOT be shown once onboarding is complete.

#### Scenario: Follow without a found concert
- **WHEN** an onboarding fan with no follows follows an artist whose catalog lookup returns no concert
- **THEN** the progress row shows 20 percent

#### Scenario: Follow with a found concert
- **WHEN** an onboarding fan with no follows follows an artist whose catalog lookup returns 2 concerts
- **THEN** the progress row first shows 20 percent after the follow, and 33 percent once the lookup returns

#### Scenario: Every follow advances the row
- **WHEN** an onboarding fan follows 2 artists with found concerts and then 1 artist without a found concert
- **THEN** the progress row moves from 67 percent to 87 percent

#### Scenario: Ready by follows alone
- **WHEN** an onboarding fan follows 5 artists and no lookup finds a concert
- **THEN** the progress row becomes the 「完成しました！」 button

#### Scenario: Ready by found concerts
- **WHEN** an onboarding fan follows 3 artists and each lookup finds at least one concert
- **THEN** the progress row becomes the 「完成しました！」 button

#### Scenario: Button opens the Dashboard
- **WHEN** the fan taps the 「完成しました！」 button
- **THEN** the Dashboard opens

#### Scenario: Already ready when Discovery opens
- **WHEN** an onboarding guest whose stored follows already reach a value of 1 opens Discovery
- **THEN** the button is shown as soon as the follows and their lookups are restored, without a further follow

#### Scenario: The row never overlaps the bubble field
- **WHEN** the progress row is shown on a 375 px wide screen
- **THEN** no bubble and no part of the orb is drawn under the row

#### Scenario: Search mode hides the row
- **WHEN** the fan types in the search bar
- **THEN** the progress row is hidden together with the genre chips, and returns when search mode ends

#### Scenario: Onboarding complete
- **WHEN** a fan whose onboarding is complete opens Discovery
- **THEN** no progress row is shown

#### Scenario: Screen reader
- **WHEN** assistive technology reads the progress row at 40 percent
- **THEN** it announces the label and a progress value of 40 percent

### Requirement: Following artists on Discovery

The system SHALL provide an engaging, gamified interface for users to discover and follow artists from the catalog's artist listings. A guest's follows are kept on the device and not sent to the server; a signed-in fan's follows are sent to the server. After each follow the system SHALL look up the artist's concerts already in the catalog and count the followed artists that have upcoming concerts; it SHALL NOT start a concert search itself (a first follow starts one on the server, as the story stories/follow-an-artist describes). A follow SHALL show at once; following an artist that is already followed SHALL change nothing; when a signed-in fan's follow fails, it SHALL be undone, the artist's bubble returns and an error snack is shown. While the fan is onboarding, the onboarding progress row SHALL show how close the timetable is to ready and SHALL turn into a button to the Dashboard when ready. Navigation to the Dashboard is never forced — the Dashboard is always reachable from the Home tab of the bottom navigation at the fan's own pace.

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL keep the follow on the device
- **AND** the system SHALL look up the artist's concerts already in the catalog
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself

#### Scenario: Guest follow default hype level

- **WHEN** a guest follows an artist
- **THEN** the follow is kept on the device at hype level Nearby

#### Scenario: Ready timetable is offered without a spotlight

- **WHEN** an onboarding fan's follows reach the ready value of the onboarding progress row
- **THEN** the row becomes the 「完成しました！」 button
- **AND** no spotlight or coach mark is shown on the bottom navigation
- **AND** the fan MAY open the Dashboard from the Home tab at any time, ready or not

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL restore the follows kept on the device into the active follow list
- **AND** the system SHALL look up the catalog's concerts for every restored artist

#### Scenario: Snack notification on concert found

- **WHEN** the lookup for a followed artist finds at least one concert in the catalog
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events

#### Scenario: Following an already-followed artist

- **WHEN** a fan taps an artist they already follow
- **THEN** nothing changes and no request is sent

#### Scenario: Signed-in follow fails

- **WHEN** a signed-in fan follows an artist and the follow fails
- **THEN** the artist is no longer shown as followed and its bubble returns to the field
- **AND** an error snack tells the fan that the follow failed

### Requirement: Swap tile switches between the artist bubbles and the All Nearby view

Discovery SHALL show a swap tile beside the orb, inside the band below the floor that bubbles never cross, so that no bubble and no part of the orb is ever drawn under the tile and the bubble field keeps the same size it has without the tile. The tile SHALL sit on the dominant-hand side of the orb, just outside the largest size the orb can grow to: on a 375 px wide screen, right-handed, its centre is between 260 px and 300 px from the left edge. In left-handed mode (the FAB menu's handedness setting) it SHALL be mirrored to the left of the orb.

The tile's icon SHALL draw two arrows in a loop, one magenta and one cyan. The glyph of the view on screen SHALL be drawn large over the arrows, and the glyph of the other view SHALL be drawn as a small badge in the tile's bottom corner: the artist bubbles are three bubbles (purple, teal and gold) with small sparkles, and the All Nearby view is a ticket marked LIVE with a white location pin. The tile SHALL show no text label. Its accessible name SHALL name the view a tap leads to: 「近くのライブ」 on the artist bubbles and 「アーティスト」 on the All Nearby view (English: "Near you" and "Artists").

A tap SHALL switch the view. The arrows SHALL make a half turn, always in the same direction, while the two glyphs trade places and sizes with a spring motion, and the new view SHALL appear as a circle growing out of the tile; the whole motion SHALL end within 700 ms. With a reduced-motion preference the view and the icon SHALL change at once, without motion.

#### Scenario: The tile never covers the bubble field
- **WHEN** Discovery shows the artist bubbles on a 375 px wide screen for a fan whose orb has reached its largest size
- **THEN** no bubble and no part of the orb is drawn under the swap tile
- **AND** the bubble field has the same height as it would without the tile

#### Scenario: Switching to the All Nearby view
- **WHEN** the fan taps the swap tile on the artist bubbles
- **THEN** Discovery shows the All Nearby view with its area chip, date chip and concert list
- **AND** the tile shows the ticket glyph large and the bubbles as the corner badge, and its accessible name is 「アーティスト」

#### Scenario: Switching back to the artist bubbles
- **WHEN** the fan taps the swap tile on the All Nearby view
- **THEN** Discovery shows the artist bubbles, the search bar and the genre chips again
- **AND** the tile shows the bubbles large and the ticket as the corner badge, and its accessible name is 「近くのライブ」

#### Scenario: Reduced motion
- **WHEN** a fan with a reduced-motion preference taps the swap tile
- **THEN** the view and the icon change at once, without the half turn or the growing circle

#### Scenario: Left-handed mode
- **WHEN** the fan has turned on left-handed mode
- **THEN** the swap tile sits to the left of the orb, mirrored

#### Scenario: A snack bar is open
- **WHEN** a snack bar opens on Discovery, for example after a follow that finds concerts
- **THEN** the swap tile moves up so that it sits above the snack bar, overlapping neither the snack bar nor the bubble field
- **AND** the tile stays tappable, and returns to its place when the snack bar closes

#### Scenario: Search mode
- **WHEN** the fan types in the search bar
- **THEN** the swap tile is hidden together with the genre chips, and returns when search mode ends

#### Scenario: The FAB menu is open
- **WHEN** the FAB action arc is open on Discovery
- **THEN** a tap on the swap tile only closes the arc, as for any page content under the arc's scrim

### Requirement: Discovery's view is addressable and remembered

Discovery SHALL open on the All Nearby view when its address carries `view=nearby`, at any onboarding state. Switching views SHALL rewrite the address (`/discovery?view=nearby` or `/discovery`) without adding a history entry. Without `view=nearby` in the address, Discovery SHALL open on the view the fan used last on the same device, except while the fan is onboarding, when it SHALL open on the artist bubbles. When the device cannot keep that choice, Discovery SHALL open on the artist bubbles.

#### Scenario: Link to the All Nearby view
- **WHEN** the fan opens `/discovery?view=nearby`
- **THEN** Discovery shows the All Nearby view

#### Scenario: Switching rewrites the address
- **WHEN** the fan switches from the artist bubbles to the All Nearby view
- **THEN** the address becomes `/discovery?view=nearby`
- **AND** going back leaves Discovery as it would have without the switch

#### Scenario: The last view is remembered
- **WHEN** a fan whose onboarding is complete leaves Discovery on the All Nearby view and later opens Discovery from the bottom navigation
- **THEN** Discovery shows the All Nearby view

#### Scenario: Onboarding opens on the artist bubbles
- **WHEN** an onboarding guest who last used the All Nearby view opens Discovery from the bottom navigation
- **THEN** Discovery shows the artist bubbles

#### Scenario: The device keeps nothing
- **WHEN** the device's storage is unavailable and the fan opens `/discovery`
- **THEN** Discovery shows the artist bubbles

### Requirement: All Nearby view uses ListByLocation

The All Nearby view on Discovery SHALL call `ConcertService.ListByLocation` and keep its result for the visit, so switching away from it and back does not fetch it again.

#### Scenario: All Nearby result cached independently

- **WHEN** the user switches to the All Nearby view and `ListByLocation` returns a result
- **THEN** the result SHALL be kept for the visit
- **AND** switching to the artist bubbles and back to the All Nearby view SHALL reuse the kept result when the area and date range have not changed

#### Scenario: Cache invalidated on filter change

- **WHEN** the user changes the area or date preset in the All Nearby view
- **THEN** the All Nearby cache SHALL be invalidated
- **AND** `ListByLocation` SHALL be called again with the new parameters

#### Scenario: The bubble field is kept while the All Nearby view is shown

- **WHEN** the fan switches from the artist bubbles to the All Nearby view and back
- **THEN** the bubble field SHALL show the same artists it showed before the switch
- **AND** no follow made before the switch SHALL be lost

### Requirement: Date Preset Selector in the All Nearby View

The All Nearby view SHALL expose its date filter as a single date chip that opens one date-range bottom sheet. The sheet SHALL offer three quick presets (今週末, 7日以内, 30日以内) and a directly-editable custom range (start/end date fields), so a custom range is adjusted without any intermediate menu or drill-down. There is no standalone "カスタム" preset chip; custom selection is simply editing the date fields.

#### Scenario: Date chip opens the range sheet in one tap

- **WHEN** the user taps the date chip
- **THEN** a date-range bottom sheet SHALL open containing both the quick presets and editable start/end date fields

#### Scenario: Available quick presets

- **WHEN** the date-range sheet is displayed
- **THEN** it SHALL offer exactly three quick presets: 今週末, 7日以内, 30日以内
- **AND** it SHALL provide directly-editable start (開始) and end (終了) date fields for a custom range

#### Scenario: 今週末 preset date range

- **WHEN** the user selects 今週末
- **AND** today is Monday through Friday
- **THEN** `from` SHALL be set to the next Saturday and `to` to the next Sunday

#### Scenario: 今週末 when today is Saturday or Sunday

- **WHEN** the user selects 今週末
- **AND** today is Saturday
- **THEN** `from` SHALL be today and `to` SHALL be the next day (Sunday)
- **WHEN** the user selects 今週末
- **AND** today is Sunday
- **THEN** `from` and `to` SHALL both be today

#### Scenario: 7日以内 preset date range

- **WHEN** the user selects 7日以内
- **THEN** `from` SHALL be today and `to` SHALL be today + 6 days (inclusive 7-day window)

#### Scenario: 30日以内 preset date range

- **WHEN** the user selects 30日以内
- **THEN** `from` SHALL be today and `to` SHALL be today + 29 days (inclusive 30-day window)

#### Scenario: Quick preset applies and closes in one tap

- **WHEN** the user taps a quick preset in the sheet
- **THEN** the corresponding range SHALL be applied and the sheet SHALL close without a further confirmation tap

#### Scenario: Custom range is edited then applied

- **WHEN** the user edits the start and/or end date fields in the sheet
- **THEN** the sheet SHALL remain open for adjustment
- **AND** an apply action SHALL confirm the edited range and close the sheet

#### Scenario: Custom range validation

- **WHEN** the user edits the custom date fields
- **THEN** the UI SHALL prevent `to` from being earlier than `from`
- **AND** the UI SHALL prevent the inclusive range from exceeding 30 days
- **AND** an inline hint SHALL communicate an invalid range and block applying it

### Requirement: Area Selector in the All Nearby View

The All Nearby view SHALL present the current reference area as an **area chip** in the single-row filter bar, and allow the user to override it for the duration of the session by opening the shared `user-home-selector` from that chip.

#### Scenario: Default area is user home

- **WHEN** the All Nearby view opens for an authenticated user who has set a home area
- **THEN** the area chip SHALL display the user's home area name (prefecture display name)
- **AND** the `GeoLocation` passed to `ListByLocation` SHALL use `user.home.centroid.latitude`, `user.home.centroid.longitude`, and `user.home.level_1` as `admin_area` (`centroid` is the nested `Coordinates` sub-message on the `Home` proto; `centroid_latitude`/`centroid_longitude` are reserved field names)

#### Scenario: Area override via UserHomeSelector

- **WHEN** the user taps the area chip
- **THEN** the `user-home-selector` component SHALL open
- **AND** on selection, the route SHALL update its local area state with the new ISO 3166-2 code
- **AND** `ListByLocation` SHALL be called with the new area's centroid coordinates and admin_area
- **AND** the new area SHALL NOT be saved to the user's account

#### Scenario: Area override is session-scoped

- **WHEN** the user reloads the page or navigates away and returns
- **THEN** the area chip SHALL reset to the user's persisted home area
- **AND** any previous session override SHALL be discarded

#### Scenario: Area override for unauthenticated user

- **WHEN** an unauthenticated user opens the All Nearby view
- **AND** no guest home is stored in localStorage
- **THEN** the area chip SHALL prompt the user to choose an area
- **AND** the chosen area SHALL be used for the session without persisting to localStorage

### Requirement: All Nearby Concert List

The All Nearby view SHALL display concerts returned by `ConcertService.ListByLocation` using the same concert timetable as the dashboard, with HOME and NEARBY lanes only. The list SHALL build only a window of dates around where the fan is looking and keep every group aligned with the stage header, as the dashboard requirement "The timetable renders a window of dates around the fan" states for the timetable. Tapping a card SHALL open the concert the same way as on the dashboard: a first-party concert opens its Event page, a discovered concert opens the event detail sheet.

#### Scenario: HOME and NEARBY lanes rendered

- **WHEN** `ListByLocation` returns proximity groups
- **THEN** the concert timetable SHALL render HOME-tier concerts in the HOME lane and NEARBY-tier concerts in the NEARBY lane
- **AND** AWAY-tier concerts SHALL NOT be displayed

#### Scenario: Venue name shown for all lanes

- **WHEN** a concert card is rendered in the All Nearby list
- **THEN** the venue name (listed or resolved) SHALL be shown regardless of the lane (HOME or NEARBY)
- **AND** this differs from the dashboard timetable, whose HOME-lane cards leave the venue out

#### Scenario: Empty state

- **WHEN** `ListByLocation` returns an empty group list
- **THEN** Discovery SHALL display an empty-state message explaining that no concerts were found for the selected area and date range
- **AND** the empty state SHALL suggest a longer period or another area, while the area chip and the date chip stay available above it

#### Scenario: First-party concert opens its event page

- **WHEN** the fan taps the card of a concert whose Series belongs to an Organizer in the All Nearby list
- **THEN** the app SHALL navigate to `/events/<id>` and SHALL NOT open the detail sheet

#### Scenario: Closing the detail sheet returns to the list

- **WHEN** the fan opens a discovered concert from the All Nearby list and closes the detail sheet
- **THEN** Discovery SHALL still show the All Nearby view with the same area, date range and scroll position

### Requirement: Compact All Nearby Filter Bar on Discovery

The All Nearby view SHALL present its filters as a single, fixed-height row of two chips — an area chip and a date chip — in the place of the search bar and the genre chips, such that selecting or adjusting any filter never changes the height of the filter area and therefore never reduces the concert timetable's height.

#### Scenario: Filter bar is a single row of two chips

- **WHEN** the All Nearby view is active
- **THEN** the filter area SHALL render exactly two controls on one row: an area chip and a date chip
- **AND** neither chip SHALL expand the filter area inline when tapped

#### Scenario: Timetable height is unaffected by filter interaction

- **WHEN** the user opens the area sheet, opens the date sheet, or changes any filter
- **THEN** the height of the concert timetable SHALL NOT decrease as a result
- **AND** all complex input SHALL occur in a bottom sheet overlay rather than inline expansion

### Requirement: Localized All Nearby Date Display on Discovery

Every user-facing date and date-range in the All Nearby filter SHALL be formatted for the Japanese locale via `Intl.DateTimeFormat('ja-JP')`; the browser's native `MM/DD/YYYY` input rendering SHALL NOT be the primary display of the selected range.

#### Scenario: Date chip shows a localized range

- **WHEN** a custom range from 2026-08-12 to 2026-08-20 is applied
- **THEN** the date chip SHALL display the localized range `8/12〜8/20`

#### Scenario: Single-day range

- **WHEN** the applied range has `from` equal to `to`
- **THEN** the date chip SHALL display that single localized date (e.g. `8/10`) rather than a `〜`-joined pair

#### Scenario: Preset shows its name

- **WHEN** a quick preset (今週末 / 7日以内 / 30日以内) is applied
- **THEN** the date chip SHALL display that preset's name rather than a raw date range

### Requirement: Natural Japanese Copy for the All Nearby View

All user-facing Japanese strings on the All Nearby surface SHALL read as natural, native Japanese; machine-translated or awkward phrasing SHALL be corrected. Japanese and English i18n keys SHALL remain at parity.

#### Scenario: All Nearby strings are natural Japanese

- **WHEN** the swap tile's accessible names, area prompt, empty-state text, date-preset labels, and range hint are displayed in Japanese
- **THEN** each SHALL be phrased in natural Japanese
- **AND** every `allNearby.*` key present in the Japanese bundle SHALL also exist in the English bundle (and vice versa)
