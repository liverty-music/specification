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
- **AND** tapping a genre chip SHALL regenerate bubbles with artists from that genre
- **AND** the active genre chip SHALL be visually highlighted

#### Scenario: Already-followed artists
- **WHEN** an artist bubble represents an already-followed artist
- **THEN** the bubble SHALL be visually distinguished (e.g., dimmed, checkmark overlay)
- **AND** tapping it SHALL NOT trigger a duplicate follow action

## ADDED Requirements

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
