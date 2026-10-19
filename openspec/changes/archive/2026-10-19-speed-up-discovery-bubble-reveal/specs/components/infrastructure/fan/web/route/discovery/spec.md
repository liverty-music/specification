## MODIFIED Requirements

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
- **THEN** the initial load SHALL start during app start-up, without waiting for the route to load: once the session is known, after the follow list for a signed-in fan and after restoring an onboarding guest's persisted follows
- **AND** if the field is built before the route shows it, the route SHALL show those artists directly, without ghost placeholder bubbles
- **AND** the route SHALL NOT start a second initial load while the start-up load is running

#### Scenario: Cache is updated after each successful load
- **WHEN** an initial load or refresh completes successfully
- **THEN** the resulting field SHALL be persisted to the single bubble-field cache
- **AND** the next re-entry SHALL use the updated field

## ADDED Requirements

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
