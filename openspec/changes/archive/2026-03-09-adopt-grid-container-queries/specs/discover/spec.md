## MODIFIED Requirements

### Requirement: Bubble UI Re-experience
The system SHALL provide the onboarding Bubble UI as a reusable discovery experience on the Discover tab. The discover page layout SHALL use CSS Grid with explicit row tracks for its structural layout.

#### Scenario: Default Bubble UI display
- **WHEN** the Discover tab is opened
- **THEN** the system SHALL display the physics-based artist Bubble UI (same as onboarding)
- **AND** the DNA Orb SHALL be displayed at the bottom
- **AND** tapping a bubble SHALL trigger the absorption animation and call `ArtistService.Follow`

#### Scenario: Genre filtering
- **WHEN** the Bubble UI is displayed
- **THEN** genre/tag chips SHALL be displayed above the bubble area (e.g., Rock, Pop, Anime, Jazz, Electronic, Hip-Hop)
- **AND** tapping a genre chip SHALL regenerate bubbles with artists from that genre
- **AND** the active genre chip SHALL be visually highlighted

#### Scenario: Already-followed artists
- **WHEN** an artist bubble represents an already-followed artist
- **THEN** the bubble SHALL be visually distinguished (e.g., dimmed, checkmark overlay)
- **AND** tapping it SHALL NOT trigger a duplicate follow action

#### Scenario: Discover page grid layout structure
- **WHEN** the discover page renders
- **THEN** `.discover-layout` SHALL use `display: grid` with `grid-template-rows: auto auto 1fr`
- **AND** the search bar SHALL occupy the first `auto` row
- **AND** the genre chips SHALL occupy the second `auto` row
- **AND** the bubble area SHALL occupy the `1fr` row
- **AND** the layout SHALL NOT use `display: flex` with `flex-direction: column`

### Requirement: Manual Search
The system SHALL provide a text search for targeted artist discovery. Search results SHALL use CSS Grid with Subgrid for consistent column alignment across all result items.

#### Scenario: Search bar display
- **WHEN** the Discover tab is opened
- **THEN** a search bar SHALL be displayed at the top of the screen

#### Scenario: Entering search mode
- **WHEN** a user taps the search bar and begins typing
- **THEN** the Bubble UI SHALL be hidden
- **AND** search results SHALL appear as a vertical list below the search bar

#### Scenario: Search results grid alignment
- **WHEN** search results are displayed
- **THEN** each result SHALL show the artist name with a follow action button
- **AND** `.results-list` SHALL use `display: grid` with column tracks for avatar, name, and action
- **AND** each `.result-item` SHALL use `grid-template-columns: subgrid` to align columns across items
- **AND** already-followed artists SHALL show a followed indicator instead of a follow button

#### Scenario: Exiting search mode
- **WHEN** a user clears the search text or taps the clear button
- **THEN** the search results SHALL be hidden
- **AND** the Bubble UI SHALL be restored
