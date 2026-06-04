## ADDED Requirements

### Requirement: Canonical journey-status presentation map
The frontend SHALL define a single canonical mapping from each ticket-journey status to its display label, icon, and semantic hue token. Every component that renders a journey status SHALL derive its label, icon, and hue from this map rather than defining them inline.

#### Scenario: Single source of truth
- **WHEN** a journey status needs a label, icon, or hue in any component
- **THEN** the value SHALL be read from the canonical map
- **AND** no component SHALL inline its own per-status label, icon, or hue

#### Scenario: Map covers every status
- **WHEN** the canonical map is defined
- **THEN** it SHALL include an entry for each of `tracking`, `applied`, `unpaid`, `paid`, and `lost`
- **AND** each entry SHALL provide a label (via the existing `eventDetail.journeyStatus.*` i18n key), an icon, and a hue token

### Requirement: Status icon and hue assignments
Each journey status SHALL have a defined icon and a meaning-based hue so the status is understandable through a non-colour cue (icon plus label) as well as colour.

#### Scenario: Icon per status
- **WHEN** a journey status is rendered
- **THEN** its icon SHALL be: `tracking` 👀, `applied` 📝, `unpaid` 💰, `paid` 🎟️, `lost` 💔

#### Scenario: Hue per status
- **WHEN** a journey status is rendered with colour
- **THEN** its hue SHALL be the shared journey-hue token for that status: process (`tracking`, `applied`) neutral, `unpaid` amber, `paid` green, `lost` red

#### Scenario: Meaning survives without colour
- **WHEN** any journey status is rendered
- **THEN** it SHALL present its icon and text label in addition to colour

### Requirement: Consistent rendering across components
A given journey status SHALL render with the same label, icon, and hue wherever it appears — the dashboard filter chips, the concert-card journey badge, and the concert-detail status control.

#### Scenario: Same status looks the same everywhere
- **WHEN** the same journey status appears as a filter chip, a card badge, and a detail-control node
- **THEN** all three SHALL show the same icon, label, and hue sourced from the canonical map
