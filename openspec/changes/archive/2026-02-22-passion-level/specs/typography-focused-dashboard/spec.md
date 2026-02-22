# Capability: Typography-Focused Dashboard

## ADDED Requirements

### Requirement: Must Go Mutation UI

When a Must Go artist's event appears in Lane 2 (Region) or Lane 3 (Other), the event card SHALL visually mutate to draw attention.

#### Scenario: Must Go event in Region lane

- **GIVEN** a Must Go artist has an event in the Region lane
- **WHEN** the dashboard renders that event
- **THEN** the card SHALL be expanded with a badge, vivid accent color with glow shadow, and bolder typography

#### Scenario: Must Go event in Other lane

- **GIVEN** a Must Go artist has an event in the Other lane
- **WHEN** the dashboard renders that event
- **THEN** the card SHALL be promoted from text-only to card style with a badge, background color, and ring border

#### Scenario: Must Go event in Main lane is not mutated

- **GIVEN** a Must Go artist has an event in the Main lane
- **WHEN** the dashboard renders that event
- **THEN** the card SHALL render normally (Main lane cards are already prominent)

#### Scenario: Non-Must-Go events are not mutated

- **GIVEN** an artist with Local Only or Keep an Eye passion level
- **WHEN** the dashboard renders their event in any lane
- **THEN** the card SHALL render in its normal style without mutation

### Requirement: Mutation Layout Handling

The dashboard layout SHALL accommodate mutated cards without breaking lane alignment.

#### Scenario: Multiple mutated cards on same date

- **GIVEN** multiple Must Go artists have events on the same date in Lane 2 or Lane 3
- **WHEN** the dashboard renders that date group
- **THEN** all mutated cards SHALL render without overflow, stacking vertically within their lane
