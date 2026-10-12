# Spec Delta

## MODIFIED Requirements

### Requirement: Bubble UI re-experience on Discover tab
The system SHALL provide the onboarding Bubble UI as a reusable discovery experience on the Discover tab, with a simplified 3-row grid layout. After following an artist, the Discovery page SHALL call `ConcertService.ListByArtist` to check for existing concerts and update onboarding state. The page SHALL NOT call `SearchNewConcerts` directly.

#### Scenario: Default Bubble UI display
- **WHEN** the Discover tab is opened
- **THEN** the system SHALL display the physics-based artist Bubble UI (same as onboarding)
- **AND** the DNA Orb SHALL be displayed at the bottom
- **AND** tapping a bubble SHALL trigger the absorption animation and call `FollowService.Follow`
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
- **THEN** the page SHALL call `ConcertService.ListByArtist(artistId)` to check for existing upcoming concerts
- **AND** SHALL NOT call `SearchNewConcerts`
- **AND** if concerts exist, the page SHALL show a snack notification and update the onboarding coach mark state

#### Scenario: Concert check at page load uses List RPC
- **WHEN** the Discovery page loads and there are pre-seeded guest follows
- **THEN** the page SHALL call `ConcertService.ListByArtist(artistId)` for each followed artist
- **AND** SHALL NOT call `SearchNewConcerts`
- **AND** `artistsWithConcerts` SHALL be updated for each artist that has stored concerts
