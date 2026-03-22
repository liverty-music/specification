## MODIFIED Requirements

### Requirement: Bubble UI Re-experience
The system SHALL provide the onboarding Bubble UI as a reusable discovery experience on the Discover tab, with a simplified 3-row grid layout.

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
