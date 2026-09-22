# Discovery

## Purpose

Lets a user discover and follow new artists through an interactive physics-based bubble interface and text search, available throughout onboarding and afterward, with sound and animation feedback on each follow.

## Requirements

### Requirement: DNA Extraction UI Concept
The system SHALL provide a gamified artist discovery interface using a "DNA Extraction" metaphor with an interactive orb (glass sphere) UI that collects user preferences, with visual differentiation per artist and onboarding guidance.

#### Scenario: Initial bubble display with DNA Orb
- **WHEN** a user reaches the Artist Discovery step after authentication
- **THEN** the system SHALL display approximately 30 artist bubbles in the center area using physics-based animation
- **AND** the system SHALL display a "Music DNA Orb" (glass sphere UI) at the bottom of the screen
- **AND** the orb SHALL serve as a visual inventory for collected artists

#### Scenario: Per-artist bubble color differentiation
- **WHEN** artist bubbles are rendered
- **THEN** each bubble SHALL have a unique gradient color derived from the artist's name using a deterministic HSL-based algorithm
- **AND** the colors SHALL provide visual variety across the bubble field (not uniform purple)

#### Scenario: Onboarding guidance overlay
- **WHEN** the Artist Discovery screen is displayed for the first time during onboarding
- **THEN** the system SHALL display a popover guide explaining the interaction (per `onboarding-popover-guide` capability)
- **AND** the popover SHALL dismiss via light-dismiss or explicit close

#### Scenario: Background visual depth
- **WHEN** the Artist Discovery screen is displayed
- **THEN** the background SHALL include subtle visual elements (e.g., particle field, starfield, or animated gradient) to create depth
- **AND** these elements SHALL NOT compete with the foreground bubbles and orb for attention

---

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
The system SHALL generate new artist recommendations dynamically using the backend ArtistService.ListSimilar RPC with a limit parameter. The frontend SHALL call the Follow RPC when a user taps an artist bubble. The fetch SHALL NOT directly mutate the bubble pool — the caller SHALL manage eviction and insertion via `addToPool()`.

#### Scenario: Similar artist bubble spawning
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL call the backend `ArtistService.ListSimilar` RPC with the selected artist's ID and `limit=30`
- **AND** the system SHALL deduplicate the results (excluding seen and followed artists)
- **AND** the system SHALL add results to the pool via `addToPool()`, evicting oldest bubbles if the pool would exceed 50
- **AND** evicted bubbles SHALL be faded out before new bubbles spawn
- **AND** new bubbles representing similar artists SHALL spawn from the original bubble's position
- **AND** the new bubbles SHALL appear with a "pop" emergence animation
- **AND** the new bubbles SHALL integrate into the physics-based layout

#### Scenario: Follow RPC called on bubble tap
- **WHEN** a user taps an artist bubble
- **THEN** the frontend SHALL call `this.artistClient.follow({ artistId: new ArtistId({ value: artist.id }) })`
- **AND** the call SHALL be non-blocking (fire-and-forget with error logging)
- **AND** the local state SHALL update immediately without waiting for the RPC response

#### Scenario: Similar artist spawning after search follow
- **WHEN** a user follows an artist from the search results and the absorption animation completes
- **THEN** the system SHALL trigger the same similar artist loading as a direct bubble tap
- **AND** new similar artist bubbles SHALL spawn from the orb position

---

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

### Requirement: Completion Action via DNA Orb
The system SHALL use the DNA Orb as the primary navigation element to proceed to the dashboard.

#### Scenario: Dashboard navigation button
- **WHEN** the user has followed one or more artists
- **THEN** the system SHALL display a tappable button on or near the DNA Orb
- **AND** the button SHALL show the text: "[View Live Schedule (X artists)]" where X is the follow count
- **AND** when tapped, the system SHALL proceed to the Dashboard

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
- **AND** the system SHALL call `ArtistService.ListSimilar` for each seed in parallel with the limit evenly distributed to fill 50 total (e.g., 5 seeds × limit=10, 2 seeds × limit=25)

#### Scenario: Seed selection with fewer than 5 followed artists
- **WHEN** the user follows fewer than 5 artists
- **THEN** the system SHALL use all followed artists as seeds
- **AND** the limit per seed SHALL be `floor(50 / followedCount)`

#### Scenario: Follow state hydration on page reload
- **WHEN** the discovery page loads during onboarding
- **AND** previously followed artists exist in persisted guest storage
- **THEN** the system SHALL restore the followed-artist state from persisted storage before initializing the bubble pool
- **AND** the restored followed-artist IDs SHALL be used for deduplication when loading the initial bubble pool
- **AND** the restored followed artists SHALL be passed as input when initializing the bubble pool

### Requirement: Bubble pool deduplication
The system SHALL remove duplicate and already-followed artists from the bubble pool. Follow state SHALL be provided externally via a `followedIds` parameter rather than tracked internally by the pool.

#### Scenario: Deduplication on initial load (Step 2)
- **WHEN** the bubble pool is populated from any source
- **THEN** the caller SHALL provide a `followedIds: ReadonlySet<string>` parameter to the dedup method
- **AND** the system SHALL remove artists that match any already-seen artist by name (case-insensitive), internal ID, or MBID
- **AND** the system SHALL remove artists whose ID is in the provided `followedIds` set
- **AND** the system SHALL cap the pool at a maximum of 50 bubbles

#### Scenario: Deduplication after tap refill (Step 5)
- **WHEN** similar artists are added to the pool after a tap
- **THEN** the system SHALL apply the same deduplication rules as Step 2
- **AND** the caller SHALL provide the current `followedIds` derived from the followed-artists state
- **AND** already-seen artists from prior fetches SHALL be excluded

#### Scenario: Deduplication on genre reload
- **WHEN** the genre filter reloads the bubble pool
- **THEN** the caller SHALL provide the current `followedIds` derived from the followed artists list
- **AND** the system SHALL apply the same deduplication rules as Step 2

### Requirement: Bubble pool cap and eviction on tap
The system SHALL enforce the 50-bubble cap at **both** the pool layer and the physics engine. The physics engine SHALL never hold more than 50 active bodies at any time, regardless of the code path that triggered the addition.

#### Scenario: Physics engine enforces the cap when bubbles are added
- **WHEN** one or more artists are added as bubbles
- **AND** the physics engine already holds 50 or more bodies
- **THEN** the physics engine SHALL add no further bodies
- **AND** it SHALL NOT throw — excess entries are silently skipped

#### Scenario: Stale bodies removed on artist set replacement
- **WHEN** the canvas receives a new set of real (non-ghost) artists
- **AND** the physics engine already holds bodies from a previous artist set
- **THEN** bodies whose artist ID is not present in the new set SHALL be faded out and removed from the physics engine
- **AND** only after stale bodies are scheduled for removal SHALL the new artists be added
- **AND** the total active body count SHALL remain within the 50-bubble cap throughout the transition

### Requirement: Tap-to-refill flow
The system SHALL fetch similar artists on each bubble tap and manage the bubble pool's lifecycle accordingly.

#### Scenario: Successful tap and refill (Steps 3-4)
- **WHEN** a user taps an artist bubble
- **THEN** the system SHALL follow the tapped artist
- **AND** the system SHALL call `ArtistService.ListSimilar` with `limit=30` for the tapped artist
- **AND** the system SHALL add deduplicated results to the pool via the coordinated eviction mechanism
- **AND** the cycle SHALL repeat for subsequent taps (Step 6)

#### Scenario: No similar artists found
- **WHEN** the `ListSimilar` response returns zero artists
- **THEN** the system SHALL NOT evict any existing bubbles
- **AND** the system SHALL display an informational toast notification to the user

#### Scenario: ListSimilar RPC failure
- **WHEN** the `ListSimilar` call fails
- **THEN** the system SHALL NOT evict any existing bubbles
- **AND** the system SHALL display a warning toast notification to the user

### Requirement: Canvas replenishes bubbles when similar artists are exhausted
When a user follows an artist and the similar-artist lookup returns no new (unseen) artists, the system SHALL automatically fetch replacement bubbles from the top-artist pool to keep the canvas populated.

#### Scenario: Similar artists fully deduplicated
- **WHEN** user taps a bubble AND the similar-artist lookup returns zero new bubbles after deduplication
- **THEN** the system SHALL fetch fresh artists from the top-artist pool as replacements
- **AND** any unseen artists SHALL be spawned as new bubbles near the absorption point

#### Scenario: Top artist pool also exhausted
- **WHEN** user taps a bubble AND both similar artists and replacement bubbles return zero new artists
- **THEN** the system SHALL gracefully accept an empty canvas without errors
- **AND** the complete button (if visible) SHALL remain functional

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
When the user already follows artists, the initial load seeds bubbles from those artists' similar artists. Because the similar lists shrink as follow count grows (seeds are capped, the per-seed limit shrinks, and deduplication removes followed and overlapping artists), the system SHALL top up the field with global top artists whenever the deduplicated seed-similar results fall below 30 bubbles. Similar artists SHALL keep priority. This guarantees the field is never empty and stays reasonably full regardless of how many artists the user follows.

#### Scenario: Sparse seed-similar results are topped up
- **WHEN** the initial load takes the similar-seed path and the deduplicated similar results are below 30 bubbles
- **THEN** the system SHALL append global top artists (deduplicated against followed and already-included artists) up to the bubble cap
- **AND** the similar artists SHALL retain priority order ahead of the top-artist fillers

#### Scenario: Empty seed-similar still fills the field
- **WHEN** the similar lookups resolve to nothing (no matches, errors, or all results deduped away)
- **THEN** the system SHALL fill the field with global top artists rather than leaving it empty

#### Scenario: Sufficient seed-similar results are not diluted
- **WHEN** the deduplicated similar results meet or exceed 30 bubbles
- **THEN** the system SHALL NOT fetch or append top artists

### Requirement: Physics layer is a pure projection of the field
The physics/canvas layer SHALL render the field it is given and SHALL NOT own bubble policy. It SHALL NOT apply the capacity cap, deduplication, or followed-artist exclusion; those are guaranteed upstream by the field owner. The physics layer SHALL expose a reconcile operation that diffs its current bodies against a target `Artist[]` and applies only the additions and removals needed to match it.

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
- **AND** if a hard safety cap is ever hit, it SHALL be logged rather than dropped silently

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
The system SHALL provide the onboarding Bubble UI as a reusable discovery experience on the Discover tab, with a simplified 3-row grid layout. After following an artist, the Discovery page SHALL call `ConcertService.List` to check for existing concerts and update onboarding state. The page SHALL NOT call `SearchNewConcerts` directly.

#### Scenario: Default Bubble UI display
- **WHEN** the Discover tab is opened
- **THEN** the system SHALL display the physics-based artist Bubble UI (same as onboarding)
- **AND** the DNA Orb SHALL be displayed at the bottom
- **AND** tapping a bubble SHALL trigger the absorption animation and call `ArtistService.Follow`
- **AND** the page grid SHALL use `grid-template-rows: auto auto 1fr` (search bar, genre chips, bubble area)

#### Scenario: Genre filtering
- **WHEN** the Bubble UI is displayed
- **THEN** genre/tag chips SHALL be displayed above the bubble area (e.g., Rock, Pop, Anime, Jazz, Electronic, Hip-Hop)
- **AND** tapping a genre chip SHALL regenerate bubbles with artists from that genre via `ArtistService.ListTop` with the selected tag
- **AND** genre results SHALL be global (not country-filtered) due to Last.fm API constraints
- **AND** the active genre chip SHALL be visually highlighted

#### Scenario: Genre deselection reverts to regional results
- **WHEN** a genre chip is active
- **AND** the user taps the same genre chip again (deselection)
- **THEN** the system SHALL regenerate bubbles using `ArtistService.ListTop` with the detected country and no tag
- **AND** the system SHALL return to showing regional top artists

#### Scenario: Already-followed artists
- **WHEN** an artist bubble represents an already-followed artist
- **THEN** the bubble SHALL be visually distinguished (e.g., dimmed, checkmark overlay)
- **AND** tapping it SHALL NOT trigger a duplicate follow action

#### Scenario: Concert check after follow uses List RPC
- **WHEN** a user follows an artist from the Discovery page (bubble tap or search follow)
- **THEN** the page SHALL call `ConcertService.List(artistId)` to check for existing upcoming concerts
- **AND** SHALL NOT call `SearchNewConcerts`
- **AND** if concerts exist, the page SHALL show a snack notification and update the onboarding coach mark state

#### Scenario: Concert check at page load uses List RPC
- **WHEN** the Discovery page loads and there are pre-seeded guest follows
- **THEN** the page SHALL call `ConcertService.List(artistId)` for each followed artist
- **AND** SHALL NOT call `SearchNewConcerts`
- **AND** `artistsWithConcerts` SHALL be updated for each artist that has stored concerts

---

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
- **THEN** each result SHALL show the artist name with a follow action button
- **AND** tapping the follow button SHALL trigger the DNA Orb absorption effect
- **AND** already-followed artists SHALL show a followed indicator instead of a follow button

#### Scenario: Exiting search mode
- **WHEN** a user clears the search text or taps the clear button
- **THEN** the search results SHALL be hidden
- **AND** the Bubble UI SHALL be restored

---

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
The system SHALL manage Bubble UI resources efficiently when the tab is not active.

#### Scenario: Tab deactivation
- **WHEN** the user navigates away from the Discover tab
- **THEN** the physics simulation SHALL be paused to conserve resources

#### Scenario: Tab reactivation
- **WHEN** the user returns to the Discover tab
- **THEN** the physics simulation SHALL resume from its paused state

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
- **WHEN** no cached field exists (first visit or cache cleared)
- **THEN** the route SHALL initialize with ghost placeholder bubbles as the current behavior
- **AND** switch to real artists when the initial load completes

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

### Requirement: Interactive Artist Discovery (Bubble Network UI)

The system SHALL provide an engaging, gamified interface for users to discover and follow artists using Last.fm API data. During onboarding, followed artists are stored locally (not via backend RPC). The system SHALL trigger a background concert search for each followed artist and track which artists have concerts. The Coach Mark SHALL appear when the progression condition is reached and SHALL hint that the personal timetable is ready; it is owned by `CoachMarkService` (see `onboarding-spotlight`). Navigation to the Dashboard is never forced — the dashboard is always reachable and the user taps the Home nav tab at their own pace. Tapping the coach mark target SHALL navigate only; it SHALL NOT advance any onboarding step (there is no step machine).

#### Scenario: Guest user follows artist via bubble tap

- **WHEN** a guest user (in onboarding) taps an artist bubble
- **THEN** the system SHALL trigger the absorption animation
- **AND** the system SHALL store the artist locally (routed to the guest follow queue for unauthenticated users)
- **AND** the system SHALL initiate a background concert search/track for the artist via `ConcertService`
- **AND** the system SHALL NOT call any backend RPC for the follow operation itself

#### Scenario: Guest follow default hype level

- **WHEN** a guest user (in onboarding) requests the list of followed artists
- **THEN** the system SHALL return each followed artist with hype level `'watch'` (observation tier)

#### Scenario: Discover to Dashboard coach-mark trigger

- **WHEN** a user is in onboarding (`isOnboarding === true`)
- **AND** either the user has followed 5 or more artists, OR the live `artistsWithConcertsCount` >= 3
- **AND** the coach mark has not yet been shown this session
- **THEN** the system SHALL activate a coach mark spotlight on the Dashboard nav icon via `CoachMarkService`
- **AND** the trigger SHALL be evaluated from live follow/concert counts on the Discovery screen, not from a mirrored count cache
- **AND** the user MAY tap the Dashboard icon at any time (with or without the spotlight) to navigate to `/dashboard`
- **AND** tapping the Dashboard icon SHALL navigate only and SHALL NOT advance any onboarding step

#### Scenario: Coach Mark does not reappear

- **WHEN** the coach mark has already been shown for the current onboarding session
- **THEN** the system SHALL NOT display it again even if the user follows more artists

#### Scenario: Pre-seeded follows on page reload

- **WHEN** the discovery page loads during onboarding
- **THEN** the system SHALL hydrate follows from the locally stored guest follows into the active follow list
- **AND** the system SHALL initiate a concert search via `ConcertService` for any artists not yet tracked

#### Scenario: Snack notification on concert found

- **WHEN** a followed artist's search completes with status `completed`
- **AND** `listConcerts(artistId)` returns at least one concert
- **THEN** the system SHALL display a snack notification indicating the artist has upcoming events

### Requirement: Artist discovery service manages bubble state with optimistic follow
The `ArtistDiscoveryService` SHALL manage artist bubbles, track seen artists across three deduplication sets, and perform optimistic follow/unfollow with retry and rollback.

#### Scenario: Load initial artists
- **WHEN** `loadInitialArtists` is called
- **THEN** it SHALL fetch artists from the backend, convert them to bubbles, and populate `availableBubbles`

#### Scenario: Follow artist with optimistic update
- **WHEN** `followArtist` is called with an artist
- **THEN** it SHALL immediately add the artist to `followedArtists` before the backend call completes

#### Scenario: Follow fails after retry — rollback
- **WHEN** `followArtist` backend call fails and the retry also fails
- **THEN** it SHALL remove the artist from `followedArtists` (rollback)

#### Scenario: Deduplication across name, id, and mbid
- **WHEN** an artist has already been seen (by name, id, or mbid)
- **THEN** it SHALL NOT be added to `availableBubbles` again

#### Scenario: Reload with genre tag
- **WHEN** `reloadWithTag` is called with a genre tag
- **THEN** it SHALL clear existing bubbles and fetch new artists filtered by the tag

#### Scenario: Evict oldest bubbles
- **WHEN** `evictOldest` is called with count N
- **THEN** it SHALL remove the N oldest bubbles from `availableBubbles`

### Requirement: Discover page debounces search with stale response guard
The `DiscoverPage` route SHALL debounce artist search input by 300ms and discard stale responses.

#### Scenario: Search is debounced
- **WHEN** the search query changes
- **THEN** `performSearch` SHALL NOT be called until 300ms after the last change

#### Scenario: Stale search response is discarded
- **WHEN** the search query changes again before a previous search responds
- **THEN** the previous response SHALL be discarded

#### Scenario: Genre tag toggle activates and deactivates
- **WHEN** a genre tag is selected and then selected again
- **THEN** the first selection SHALL call `reloadWithTag` and the second SHALL call `loadInitialArtists`

#### Scenario: Clear search restores bubble view
- **WHEN** `clearSearch` is called
- **THEN** the search query SHALL be emptied and the bubble canvas SHALL resume

### Requirement: Artist discovery page dismisses guidance overlay
The `ArtistDiscoveryPage` route SHALL auto-dismiss the guidance overlay after 5 seconds with a 400ms fade animation.

#### Scenario: Guidance auto-dismiss after 5 seconds
- **WHEN** the component is attached
- **THEN** the guidance overlay SHALL become hidden after 5000ms

#### Scenario: Fade animation before removal
- **WHEN** the guidance overlay begins dismissing
- **THEN** a 400ms fade-out animation SHALL complete before the element is removed

#### Scenario: Artist selection triggers follow and live event check
- **WHEN** an artist is selected
- **THEN** `followArtist` SHALL be called followed by `checkLiveEvents`

### Requirement: Onboarding guidance rendered within unified DiscoverPage
The onboarding guidance SHALL be rendered as a Popover API element within `DiscoverPage` at `/discover`, instead of as an inline grid row.

#### Scenario: Onboarding user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the onboarding popover guide SHALL be shown via `showPopover()`
- **AND** the search bar and genre filter SHALL also be available
- **AND** the discover page grid SHALL have 3 rows (`auto auto 1fr`), not 4

#### Scenario: Normal user navigates to discover
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** no onboarding popover SHALL be rendered
- **AND** no CTA button SHALL be shown (bottom navigation provides transitions)

#### Scenario: CTA button removed during onboarding
- **REMOVED**: The "ダッシュボードを生成する" CTA button is removed from the discover page. The CTA is replaced by a coach mark spotlight on the nav-bar Dashboard icon (defined in `onboarding-tutorial` Step 1 completion).

**Reason**: The nav-bar Dashboard icon spotlight teaches users about navigation while serving as the CTA. A separate button is redundant.
**Migration**: Remove the `complete-button-wrapper` and `complete-button` elements from `discover-page.html`. CTA behavior is handled by the coach mark component targeting `[data-nav-dashboard]`.

### Requirement: Followed count reflects localStorage state
The count of followed artists SHALL be an observable value that updates whenever the user follows, unfollows, or clears all followed artists, so that bindings re-evaluate immediately.

#### Scenario: Initial page load with existing guest data
- **WHEN** the user navigates to `/discover` during onboarding and localStorage's guest followed-artists entry contains 3 artists
- **THEN** the orb SHALL reflect the accumulated intensity for 3 follows
- **AND** the coach-mark activation conditions SHALL evaluate correctly

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
- **AND** the follow operation SHALL use the same unified flow (localStorage during onboarding)

### Requirement: Popover guide on discover page entry during onboarding
The system SHALL display a one-time popover guide when an onboarding user navigates to the discover page, using the native Popover API with `popover="auto"` for light-dismiss behavior.

#### Scenario: Popover appears on onboarding entry
- **WHEN** `OnboardingService.isOnboarding` is `true` and the user navigates to `/discover`
- **THEN** the system SHALL call `showPopover()` on the guide element immediately upon component attachment
- **AND** the popover SHALL display a message explaining the interaction (e.g., "ライブ情報を追いかけたいアーティストをタップしてフォローしよう")
- **AND** the popover SHALL render in the top layer, outside the grid flow

#### Scenario: Popover dismissed via light-dismiss
- **WHEN** the popover is visible and the user taps outside the popover
- **THEN** the popover SHALL close via the browser's native light-dismiss mechanism
- **AND** no additional JavaScript dismiss handler SHALL be required

#### Scenario: Popover entry animation uses CSS only
- **WHEN** the popover opens
- **THEN** the popover SHALL animate from `opacity: 0; translate: 0 1rem` to `opacity: 1; translate: 0 0` using `@starting-style` and `:popover-open`
- **AND** the transition SHALL use `transition-behavior: allow-discrete` for `display` and `overlay` properties
- **AND** only compositor-thread properties (`opacity`, `translate`) SHALL be animated

#### Scenario: Popover exit animation
- **WHEN** the popover is dismissed
- **THEN** the popover SHALL animate from `opacity: 1; translate: 0 0` to `opacity: 0; translate: 0 1rem`
- **AND** the `display` transition SHALL keep the element visible during the exit animation

#### Scenario: Non-onboarding user does not see popover
- **WHEN** `OnboardingService.isOnboarding` is `false` and the user navigates to `/discover`
- **THEN** the popover element SHALL NOT be rendered in the DOM
- **AND** `showPopover()` SHALL NOT be called

#### Scenario: Popover shown only once per onboarding session
- **WHEN** the user dismisses the popover and continues using the discover page
- **THEN** the popover SHALL NOT reappear during the same page visit
- **AND** if the user navigates away and returns to `/discover` while still onboarding, the popover MAY appear again (no cross-navigation persistence required)

#### Scenario: Respects prefers-reduced-motion
- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** the popover SHALL appear and disappear instantly without transition animations

### Requirement: Search result follow triggers bubble view transition and absorption animation
When a user follows an artist from the search results, the system SHALL transition back to the bubble view, wait for the canvas to be visible, and play the orb absorption animation, providing the same visual feedback as a direct bubble tap.

#### Scenario: Follow from search triggers absorption
- **WHEN** a user taps a search result item for an unfollowed artist
- **THEN** the system SHALL execute the follow action (optimistic UI update)
- **AND** the system SHALL exit search mode (clear results, hide search result list)
- **AND** the system SHALL resume the bubble canvas
- **AND** the system SHALL wait for the canvas element to have non-zero dimensions (via `requestAnimationFrame`)
- **AND** the system SHALL spawn a temporary bubble at the upper area of the bubble canvas (approximately 15-20% from top)
- **AND** the system SHALL immediately start the absorption animation for that bubble toward the orb
- **AND** on absorption completion, the orb SHALL absorb the bubble's hue
- **AND** the system SHALL immediately dispatch the `need-more-bubbles` custom event to trigger similar artist loading (not deferred until absorption completion)

#### Scenario: Search input is cleared after follow
- **WHEN** a user follows an artist from the search results
- **THEN** the search query input SHALL be cleared
- **AND** the search mode SHALL be deactivated

#### Scenario: Follow failure rolls back and stays in search mode
- **WHEN** a user taps a search result item
- **AND** the follow action fails (network error or backend error)
- **THEN** the system SHALL NOT exit search mode
- **AND** the system SHALL NOT spawn or absorb a bubble
- **AND** the system SHALL display an error toast notification
- **AND** the search results SHALL remain visible and interactive
