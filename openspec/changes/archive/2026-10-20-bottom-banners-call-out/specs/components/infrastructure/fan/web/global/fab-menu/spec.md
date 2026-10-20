## ADDED Requirements

### Requirement: The FAB yields to a snack bar or a bottom banner

While any snack bar is open, or a persistent bottom banner (the signup prompt or the install banner) is visible, the FAB SHALL sink into the navigation bar's centre slot so the snack bar or the banner can sit directly above the navigation bar without covering the FAB. Sunk, the FAB SHALL be 40px across and SHALL lie entirely within the navigation bar's height, and it SHALL stay tappable. When no snack bar is open and no bottom banner is visible, the FAB SHALL return to its normal size and position. The movement SHALL use spring motion and SHALL respect `prefers-reduced-motion: reduce` by landing the end state without overshoot.

#### Scenario: A snack bar opens
- **WHEN** a snack bar opens on a route where the FAB is shown
- **THEN** the FAB SHALL shrink to 40px across
- **AND** no part of the FAB SHALL extend above the navigation bar's top edge
- **AND** the FAB and the snack bar SHALL NOT overlap

#### Scenario: A bottom banner is visible
- **WHEN** a route that shows the FAB is displayed while the install banner or the signup prompt is visible
- **THEN** the FAB SHALL be 40px across and lie entirely within the navigation bar's height
- **AND** the FAB and the banner SHALL NOT overlap
- **AND** no content above the banner SHALL be covered by the FAB

#### Scenario: The sunk FAB still opens the actions
- **WHEN** a snack bar is open or a bottom banner is visible, and the user taps the sunk FAB
- **THEN** the action arc SHALL open as it does from the normal FAB

#### Scenario: A snack bar opens above a bottom banner
- **WHEN** a snack bar opens while a bottom banner is visible
- **THEN** the FAB SHALL stay sunk
- **AND** the snack bar SHALL sit above the banner, overlapping neither the FAB nor the banner

#### Scenario: The last snack bar closes
- **WHEN** the last open snack bar closes and no bottom banner is visible
- **THEN** the FAB SHALL return to 56px across, protruding from the notch

#### Scenario: The bottom banner goes away
- **WHEN** the visible bottom banner is removed (the app is installed, or the guest signs up) and no snack bar is open
- **THEN** the FAB SHALL return to 56px across, protruding from the notch

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
the navigation bar (see "The FAB yields to a snack bar or a bottom banner").

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

## REMOVED Requirements

### Requirement: The FAB yields to an open snack bar

**Reason**: Replaced by "The FAB yields to a snack bar or a bottom banner": a visible bottom banner now sinks the FAB too, and the FAB no longer floats above a banner, so "A snack bar opens above a bottom banner" changes and "The bottom banner goes away" is added.
**Migration**: None. Its scenarios keep their names in the new requirement.
