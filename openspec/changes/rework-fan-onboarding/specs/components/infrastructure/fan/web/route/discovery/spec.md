## ADDED Requirements

### Requirement: Onboarding progress row
While the fan is onboarding, the Discovery screen SHALL show a progress row directly under the genre chips that tells how close the fan's timetable is to ready. The row SHALL sit outside the bubble field, so it never overlaps a bubble or the orb. Its value SHALL be (followed artists without a found concert) / 5 + (followed artists with a found concert) / 3, capped at 1, where a concert is found for an artist when the catalog lookup after its follow returns at least one concert. Below 1 the row SHALL show the label 「タイムテーブル完成まで」 and a bar filled to the value. At 1 the row SHALL become a button labelled 「タイムテーブルができました →」 that opens the Dashboard. The row SHALL expose its value to assistive technology as a progress value from 0 to 100 percent. The row SHALL be hidden in search mode, like the genre chips, and SHALL NOT be shown once onboarding is complete.

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
- **THEN** the progress row becomes the 「タイムテーブルができました →」 button

#### Scenario: Ready by found concerts
- **WHEN** an onboarding fan follows 3 artists and each lookup finds at least one concert
- **THEN** the progress row becomes the 「タイムテーブルができました →」 button

#### Scenario: Button opens the Dashboard
- **WHEN** the fan taps the 「タイムテーブルができました →」 button
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
- **THEN** the row becomes the 「タイムテーブルができました →」 button
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

## MODIFIED Requirements

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

### Requirement: Bubble physics pauses when Discover tab is inactive
The system SHALL manage Bubble UI resources efficiently while the bubble field is not visible.

#### Scenario: Search mode pauses the simulation
- **WHEN** the user enters search mode
- **THEN** the physics simulation SHALL be paused, and it SHALL resume when search mode ends

#### Scenario: Hidden document pauses the simulation
- **WHEN** the document becomes hidden (the app goes to the background or the browser tab is switched)
- **THEN** the physics simulation SHALL be paused, and it SHALL resume when the document is visible again

#### Scenario: Tab deactivation
- **WHEN** the user navigates away from the Discover tab
- **THEN** the physics simulation SHALL be stopped and its resources released

#### Scenario: Tab reactivation
- **WHEN** the user returns to the Discover tab
- **THEN** the bubble field SHALL be drawn again from the cached field, as "Discovery bubble pool caching on re-entry" states

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

## REMOVED Requirements

### Requirement: Completion Action via DNA Orb
**Reason**: The orb never had a "View Live Schedule" button in the shipped app; the Home tab and, during onboarding, the onboarding progress row lead to the Dashboard.
**Migration**: None. See "Onboarding progress row".

### Requirement: Bubble pool cap and eviction on tap
**Reason**: Contradicted "Physics layer is a pure projection of the field" (silent skip vs logged skip) and duplicated the field's capacity rules.
**Migration**: The 50-body safety cap and the stale-body scenario moved into "Physics layer is a pure projection of the field"; the field's capacity is in "Bubble Field Consistency and Capacity Enforcement".

### Requirement: Artist discovery service manages bubble state with optimistic follow
**Reason**: Described internal types and methods that no longer exist, and a follow retry the app does not do.
**Migration**: The behaviour is covered by "Similar Artist Chain Reaction", "Bubble pool deduplication", "Bubble Field Consistency and Capacity Enforcement" and "Interactive Artist Discovery (Bubble Network UI)".

### Requirement: Artist discovery page dismisses guidance overlay
**Reason**: The guidance overlay and its 5-second dismissal were removed from the app.
**Migration**: First-visit guidance is the page-help sheet (page-help surface, "Auto-open on First Page Visit").

### Requirement: Onboarding guidance rendered within unified DiscoverPage
**Reason**: The onboarding popover was removed; the screen is the Discovery route, not `/discover`.
**Migration**: First-visit guidance is the page-help sheet; the layout is in "Bubble UI re-experience on Discover tab".

### Requirement: Popover guide on discover page entry during onboarding
**Reason**: The popover guide was replaced by the page-help sheet.
**Migration**: See the page-help surface, "Auto-open on First Page Visit".

### Requirement: Interactive Artist Discovery (Bubble Network UI)
**Reason**: Its coach-mark scenarios described a spotlight on the bottom navigation that fired only on a change of the counts within one visit, so a fan who reopened Discovery past the threshold never saw it; it also named a data source and a service the app does not use.
**Migration**: Replaced by "Following artists on Discovery" (same follow, lookup and failure rules) and "Onboarding progress row" (the hint that the timetable is ready).
