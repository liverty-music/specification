## MODIFIED Requirements

### Requirement: Global thumb-zone floating launcher

The system SHALL render a single 56px circular floating action button (FAB),
horizontally centred on the screen, whose centre lies on the top edge of the bottom
navigation bar so that it protrudes from a notch cut into the bar, on every route
where at least one action is contributed. The notch SHALL leave a gap of at least
6px around the FAB. The FAB SHALL be filled with the brand gradient (primary to
secondary) and SHALL carry a brand-coloured glow. The FAB SHALL be promoted to the
browser top layer (not stacked via `z-index`), so it stays above and receives taps
over any route content, including canvases. The FAB SHALL NOT cover any navigation
tab. The FAB SHALL be hidden whenever the navigation bar is hidden (e.g. landing
page, auth callback) or when the current route contributes zero actions. While a
snack bar is open or a persistent bottom banner is visible, the FAB SHALL sink into
the navigation bar (see "The FAB yields to a snack bar or a bottom banner"). While a bottom sheet is open, the FAB SHALL NOT be shown, so it never covers the sheet.

#### Scenario: FAB floats in the thumb zone above content

- **WHEN** a route that contributes at least one action is displayed
- **THEN** the FAB SHALL be horizontally centred, with its centre on the navigation bar's top edge
- **AND** the navigation bar SHALL show a notch around the FAB with a gap of at least 6px
- **AND** no navigation tab's icon or label SHALL be covered by the FAB

#### Scenario: A bottom banner is visible

- **WHEN** a route that contributes at least one action is displayed while the install banner or the signup prompt is visible
- **THEN** the FAB SHALL be sunk into the navigation bar, 40px across and horizontally centred
- **AND** no part of the FAB SHALL extend above the navigation bar's top edge

#### Scenario: FAB stays above the Discovery dna orb

- **WHEN** the Discovery route is displayed and the dna orb extends behind the FAB
- **THEN** the FAB SHALL be in the browser top layer
- **AND** a tap at the FAB's centre SHALL reach the FAB, not the orb

#### Scenario: FAB hidden when navigation is hidden

- **WHEN** the current route hides the bottom navigation bar (landing page or auth callback)
- **THEN** the FAB SHALL NOT be rendered

#### Scenario: FAB hidden when no actions are contributed

- **WHEN** the current route contributes zero actions to the launcher
- **THEN** the FAB SHALL NOT be rendered
- **AND** the navigation bar SHALL show no notch (see Bottom Nav Bar)

#### Scenario: FAB hidden while a bottom sheet is open

- **WHEN** a bottom sheet (for example the event detail sheet) is open on a route that contributes at least one action
- **THEN** the FAB SHALL NOT be shown
- **AND** the FAB SHALL be shown again when the sheet closes
