## MODIFIED Requirements

### Requirement: User can toggle the laser beam spotlight effect on the dashboard

The dashboard SHALL provide a toggle to enable or disable the laser beam spotlight
visual effect on the concert highway. The toggle SHALL be presented as an inline
toggle item within the FAB action launcher panel (see the `fab-action-launcher`
capability), not as a button in the page header. The preference SHALL be persisted
in localStorage under the key `beams.enabled`. The default state SHALL be
`false` (disabled). The toggle item SHALL be contributed to the launcher whenever the dashboard
is shown.

#### Scenario: Default state is off on first visit

- **WHEN** a user visits the dashboard for the first time
- **AND** the `beams.enabled` key is not set in localStorage
- **THEN** the laser beam effect SHALL NOT be rendered on the concert highway
- **AND** the beam toggle item SHALL appear in its inactive (off) state

#### Scenario: Enabling the beam effect

- **WHEN** the user taps the beam toggle item while the effect is disabled
- **THEN** the laser beam spotlight overlay SHALL appear on the concert highway
- **AND** the toggle item SHALL reflect the active (on) state
- **AND** `beams.enabled` SHALL be set to `"true"` in localStorage

#### Scenario: Disabling the beam effect

- **WHEN** the user taps the beam toggle item while the effect is enabled
- **THEN** the laser beam spotlight overlay SHALL be removed from the concert highway
- **AND** the toggle item SHALL return to its inactive (off) state
- **AND** `beams.enabled` SHALL be set to `"false"` in localStorage

#### Scenario: Preference is restored on page reload

- **WHEN** the user reloads the dashboard
- **AND** `beams.enabled` is `"true"` in localStorage
- **THEN** the laser beam effect SHALL be enabled immediately on load without user interaction

#### Scenario: Toggle button placement and icon

- **WHEN** the dashboard is displayed
- **THEN** a beam toggle item SHALL be contributed to the FAB action launcher panel
- **AND** the item SHALL use the `spotlight` icon together with a text label
- **AND** the item SHALL reflect the current enabled state to assistive technology (pressed/selected)
- **AND** the beam toggle SHALL NOT be rendered as a button in the page header

### Requirement: Filter chip UI in page header

The dashboard filter SHALL be reached from the FAB action launcher (see the
`fab-action-launcher` capability) instead of a dedicated trigger button in the page
header; the page header SHALL NOT host a filter trigger. The launcher's filter item
SHALL visually indicate when a filter is active. Artist names SHALL NOT be rendered
as chips in the header. The filter item SHALL be contributed to the launcher while
the dashboard is shown and the fan is not onboarding.

#### Scenario: No active filter — header unchanged

- **WHEN** `filteredArtistIds` is empty
- **THEN** the launcher's filter item SHALL be in its default (inactive) visual state
- **AND** no artist name chips SHALL be rendered in the header

#### Scenario: Active filter — icon state only

- **WHEN** `filteredArtistIds` contains one or more IDs
- **THEN** the launcher's filter item SHALL display in its active visual state (e.g., color change via `[data-active="true"]` CSS)
- **AND** no artist name chips SHALL be rendered in the header

#### Scenario: Dismissing an active filter

- **WHEN** a filter is active and the user activates the launcher's filter item
- **THEN** the bottom sheet SHALL open with currently filtered artists pre-selected
- **AND** the user can deselect artists and confirm to reduce or clear the filter

#### Scenario: No filter trigger in the header

- **WHEN** the dashboard header is rendered
- **THEN** the header SHALL NOT contain a filter trigger button
- **AND** the filter SHALL be reachable only via the FAB action launcher

### Requirement: Single-tap disclosure of a labeled action list

A single tap on the FAB SHALL toggle the action arc: the contributed actions laid out
along an arc that follows the dominant thumb's sweep, with the FAB as the arc's tip.
For a right-handed user the arc SHALL start at the FAB and curve upward and to the
right, rising more than it widens, so that each item sits higher and further right
than the one before it. The first contributed action SHALL sit closest to the FAB.
Long-press or gesture activation SHALL NOT be required. Every action item SHALL be
presented as a 48px circular icon **and** a short text label together; icon-only
items SHALL NOT be allowed. Each label SHALL sit on the outer side of its icon (away
from the thumb) and SHALL NOT overlap any other item's icon or label. Every item SHALL
lie within the screen with at least a 16px margin. When collapsed, the FAB SHALL show
an equalizer glyph (three vertical bars of different heights) 32px tall; when
expanded it SHALL show a close (`×`) affordance.

#### Scenario: Tapping the FAB expands the action list

- **WHEN** the user taps the collapsed FAB
- **THEN** every contributed action SHALL be laid out along the arc, each item higher and further toward the dominant-hand side than the previous one
- **AND** the FAB glyph SHALL change from the equalizer glyph to a close (`×`) affordance

#### Scenario: Tapping again collapses the list

- **WHEN** the arc is open and the user taps the FAB (now a close affordance)
- **THEN** the arc SHALL close and the glyph SHALL return to the equalizer glyph

#### Scenario: Tapping outside the arc only closes it

- **WHEN** the arc is open and the user taps a navigation tab or the page's own content outside the arc
- **THEN** the arc SHALL close
- **AND** the tap SHALL NOT navigate or activate what lies beneath

#### Scenario: Every item shows icon and label

- **WHEN** the action arc is open
- **THEN** each item SHALL render both an icon and a short text label
- **AND** no item SHALL be rendered as an icon alone

#### Scenario: Labels never overlap icons

- **WHEN** the action arc is open with the dashboard's three actions (beam toggle, filter, help)
- **THEN** no label's box SHALL intersect another item's icon or label box
- **AND** every item SHALL lie at least 16px inside the screen edges

#### Scenario: Items are comfortably tappable

- **WHEN** the action arc is open
- **THEN** each item's tappable area SHALL be at least 48px in both directions

### Requirement: Per-route contextual action registration

Route components SHALL contribute their actions to the launcher when activated and
SHALL remove them when deactivated, so the launcher's contents adapt to the current
page. Re-contributing from the same owner SHALL replace that owner's previous set
(not accumulate), so a within-route state change (e.g. the end of the fan's onboarding on the dashboard) never
leaves stale items. After navigation away from a route, that route's actions SHALL
no longer appear.

#### Scenario: Dashboard contributes its actions

- **WHEN** the dashboard is displayed to a fan who is not onboarding
- **THEN** the launcher SHALL present the dashboard's actions (beam toggle, filter, help)

#### Scenario: Actions removed on navigation away

- **WHEN** the user navigates from a route that contributed actions to a route that does not
- **THEN** the previous route's actions SHALL no longer appear in the launcher

#### Scenario: Within-route mode change replaces, not accumulates

- **WHEN** the fan's onboarding completes while the dashboard is displayed
- **THEN** the launcher SHALL present the beam toggle, the filter and help
- **AND** actions SHALL NOT be duplicated
