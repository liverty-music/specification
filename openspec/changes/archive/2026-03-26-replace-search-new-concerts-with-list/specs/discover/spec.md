## MODIFIED Requirements

### Requirement: Bubble UI Re-experience
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

### Requirement: Manual Search
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

### Requirement: Performance on Tab Switch
The system SHALL manage Bubble UI resources efficiently when the tab is not active.

#### Scenario: Tab deactivation
- **WHEN** the user navigates away from the Discover tab
- **THEN** the physics simulation SHALL be paused to conserve resources

#### Scenario: Tab reactivation
- **WHEN** the user returns to the Discover tab
- **THEN** the physics simulation SHALL resume from its paused state
