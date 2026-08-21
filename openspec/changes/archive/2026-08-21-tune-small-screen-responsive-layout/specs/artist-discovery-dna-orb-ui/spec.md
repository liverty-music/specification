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
