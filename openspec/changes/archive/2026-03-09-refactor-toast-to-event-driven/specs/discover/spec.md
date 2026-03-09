## MODIFIED Requirements

### Requirement: Bubble UI Re-experience
The system SHALL provide the onboarding Bubble UI as a reusable discovery experience on the Discover tab. The discover page SHALL NOT contain a `<toast-notification>` element; toast notifications are handled at the app shell level.

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

#### Scenario: Error notifications use app-level toast
- **WHEN** an error occurs on the discover page (load failure, search failure, follow failure)
- **THEN** the page SHALL publish a `Toast` event via `IEventAggregator`
- **AND** the toast SHALL be rendered by the app-level `<toast-notification>` element
