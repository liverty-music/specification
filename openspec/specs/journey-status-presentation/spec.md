# journey-status-presentation Specification

## Purpose
TBD - created by archiving change enhance-dashboard-filter. Update Purpose after archive.
## Requirements
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
Each journey status SHALL have a defined icon, and a meaning-based hue for surfaces that render the status with colour. The icon is the primary, always-present cue and SHALL be sufficient to distinguish the status on its own. The text label and the hue MAY both be omitted on compact surfaces (such as the concert-card badge) where the icon alone carries the status.

#### Scenario: Icon per status
- **WHEN** a journey status is rendered
- **THEN** its icon SHALL be: `tracking` 👀, `applied` 📝, `unpaid` 💰, `paid` 🎟️, `lost` 💔

#### Scenario: Hue per status
- **WHEN** a journey status is rendered with a colour treatment (filter chip or detail-control node)
- **THEN** its hue SHALL be the shared journey-hue token for that status: process (`tracking`, `applied`) neutral, `unpaid` amber, `paid` green, `lost` red

#### Scenario: Meaning survives without colour
- **WHEN** any journey status is rendered
- **THEN** it SHALL present its icon, so the status is distinguishable without relying on colour alone
- **AND** where a text label is shown, the label SHALL be sourced from the canonical `eventDetail.journeyStatus.*` i18n key

#### Scenario: Icon-only rendering retains an accessible name
- **WHEN** a journey status is rendered as an emoji without a visible text label
- **THEN** the rendering element SHALL carry a role that permits an accessible name (e.g. `role="img"`) together with the canonical label as that name (e.g. via `aria-label`), so assistive technology announces the status
- **AND** the canonical label SHALL NOT be exposed via `aria-label` on a bare element with an implicit `generic` role (a naming-prohibited role), since user agents do not reliably announce a name on such elements

### Requirement: Consistent rendering across components
A given journey status SHALL render with a consistent identity wherever it appears — the dashboard filter chips, the concert-card journey badge, and the concert-detail status control. The icon SHALL be the same across all surfaces. The hue and the visible text label SHALL appear on the filter chips and the detail control; both MAY be omitted on the concert-card badge, which renders the icon alone.

#### Scenario: Same status looks the same everywhere
- **WHEN** the same journey status appears as a filter chip, a card badge, and a detail-control node
- **THEN** all three SHALL show the same icon sourced from the canonical map
- **AND** the filter chip and the detail-control node SHALL show the same text label and hue sourced from the canonical map
- **AND** the card badge MAY show the icon alone, without the text label or hue background

