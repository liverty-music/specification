## ADDED Requirements

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
