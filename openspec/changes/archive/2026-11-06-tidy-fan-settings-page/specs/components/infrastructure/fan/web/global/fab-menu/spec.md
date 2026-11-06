# Spec Delta

## ADDED Requirements

### Requirement: The launcher ends with Settings on the tab pages

On the pages of the four navigation tabs (Home, Discover, My Artists, Tickets), the launcher SHALL offer a Settings item (icon and the label 「設定」 / "Settings") after the actions the page contributes, as the item farthest from the FAB along the arc. Choosing it SHALL close the launcher and display the Settings route. The launcher SHALL NOT offer the Settings item on any other route, including Settings itself. The Settings item is the only way into Settings from the tab pages.

#### Scenario: Settings is the last item on the dashboard

- **WHEN** the dashboard is displayed to a fan who is not onboarding and the fan opens the launcher
- **THEN** the items are, from the FAB outward, the beam toggle, the filter, help and Settings

#### Scenario: Settings is the only item on Tickets

- **WHEN** the Tickets route is displayed
- **THEN** the FAB is shown
- **AND** opening it offers Settings as its only item

#### Scenario: Choosing Settings

- **WHEN** the fan chooses Settings in the launcher
- **THEN** the launcher closes and the Settings route is displayed

#### Scenario: No Settings item outside the tabs

- **WHEN** the Settings route, an Event page or an order detail is displayed
- **THEN** the launcher offers no Settings item

## MODIFIED Requirements

### Requirement: Global thumb-zone floating launcher

The system SHALL render a single 56px circular floating action button (FAB),
horizontally centred on the screen, whose centre lies on the top edge of the bottom
navigation bar so that it protrudes from a notch cut into the bar, on every route
where the launcher has at least one item: an action the route contributes, or the
Settings item of the tab pages. The notch SHALL leave a gap of at least
6px around the FAB. The FAB SHALL be filled with the brand gradient (primary to
secondary) and SHALL carry a brand-coloured glow. The FAB SHALL be promoted to the
browser top layer (not stacked via `z-index`), so it stays above and receives taps
over any route content, including canvases. The FAB SHALL NOT cover any navigation
tab. The FAB SHALL be hidden whenever the navigation bar is hidden (e.g. landing
page, auth callback), when the launcher has no item, or while the displayed route
hides the launcher (My Artists in edit mode). While a
snack bar is open or a persistent bottom banner is visible, the FAB SHALL sink into
the navigation bar (see "The FAB yields to a snack bar or a bottom banner"). While a bottom sheet is open, the FAB SHALL NOT be shown, so it never covers the sheet.

#### Scenario: FAB floats in the thumb zone above content

- **WHEN** a route where the launcher has at least one item is displayed
- **THEN** the FAB SHALL be horizontally centred, with its centre on the navigation bar's top edge
- **AND** the navigation bar SHALL show a notch around the FAB with a gap of at least 6px
- **AND** no navigation tab's icon or label SHALL be covered by the FAB

#### Scenario: A bottom banner is visible

- **WHEN** a route where the launcher has at least one item is displayed while the install banner or the signup prompt is visible
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

- **WHEN** a route outside the four tabs that contributes zero actions is displayed (for example Settings)
- **THEN** the FAB SHALL NOT be rendered
- **AND** the navigation bar SHALL show no notch (see Bottom Nav Bar)

#### Scenario: FAB hidden while the route hides the launcher

- **WHEN** My Artists is in edit mode
- **THEN** the FAB SHALL NOT be rendered, although the Settings item would otherwise be offered
- **AND** the FAB SHALL be shown again when edit mode ends

#### Scenario: FAB hidden while a bottom sheet is open

- **WHEN** a bottom sheet (for example the event detail sheet) is open on a route where the launcher has at least one item
- **THEN** the FAB SHALL NOT be shown
- **AND** the FAB SHALL be shown again when the sheet closes

### Requirement: The FAB shows its collapsed state after navigation

Whenever the FAB is shown after a navigation, it SHALL be collapsed: the action arc SHALL be closed, the glyph SHALL be the collapsed glyph, and the FAB SHALL expose the collapsed state to assistive technology. This SHALL hold even if the arc was open when the user left the previous route, including when the FAB stays shown from one route to the next (each tab page ends with the Settings item).

#### Scenario: Leaving with the arc open and coming back
- **WHEN** the user opens the action arc on the dashboard
- **AND** taps the Tickets tab, where the launcher offers only the Settings item
- **THEN** the FAB on Tickets SHALL show the collapsed (equalizer) glyph
- **AND** when the user taps the Home tab again, the FAB SHALL show the collapsed glyph
- **AND** the FAB SHALL expose the collapsed state (not expanded)

#### Scenario: Moving between two routes that both contribute actions
- **WHEN** the action arc is open on the dashboard and the user navigates to My Artists
- **THEN** the FAB on My Artists SHALL be collapsed
