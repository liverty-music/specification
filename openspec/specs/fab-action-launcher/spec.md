# fab-action-launcher Specification

## Purpose
Provides a single, thumb-reachable floating action launcher in the bottom corner of
the fan-web app that expands, on tap, into a labeled list of context-appropriate
actions — consolidating controls that were previously scattered in the top-right
header into one ergonomic, Material 3 Expressive surface.
## Requirements
### Requirement: Global thumb-zone floating launcher

The system SHALL render a single floating action button (FAB) that floats above all
page content in the bottom corner of the screen (the thumb-reachable "primary
zone"), on every route where at least one action is contributed. The FAB SHALL be
promoted to the browser top layer (not stacked via `z-index`). The FAB SHALL be
inset from the screen edges and SHALL be offset clear of the bottom navigation bar
so the two never overlap. The FAB SHALL be hidden whenever the navigation bar is
hidden (e.g. landing page, auth callback) or when the current route contributes zero
actions.

#### Scenario: FAB floats in the thumb zone above content

- **WHEN** a route that contributes at least one action is displayed
- **THEN** the FAB SHALL be visible in the bottom corner, inset from the screen edges
- **AND** it SHALL render above page content via the browser top layer
- **AND** it SHALL sit clear of the bottom navigation bar with no overlap

#### Scenario: FAB hidden when navigation is hidden

- **WHEN** the current route hides the bottom navigation bar (landing page or auth callback)
- **THEN** the FAB SHALL NOT be rendered

#### Scenario: FAB hidden when no actions are contributed

- **WHEN** the current route contributes zero actions to the launcher
- **THEN** the FAB SHALL NOT be rendered

### Requirement: Single-tap disclosure of a labeled action list

A single tap on the FAB SHALL toggle a panel that presents the contributed actions
as a vertical list, expanding upward from the FAB. Long-press or gesture activation
SHALL NOT be required. Every action item SHALL be presented as an icon **and** a
short text label together; icon-only items SHALL NOT be allowed. Each item SHALL
have a touch target of at least 48px in the block direction regardless of label
length. When collapsed, the FAB SHALL show a single action/`+` glyph; when expanded
it SHALL show a close (`×`) affordance.

#### Scenario: Tapping the FAB expands the action list

- **WHEN** the user taps the collapsed FAB
- **THEN** the panel SHALL open, listing every contributed action as a vertical list expanding upward
- **AND** the FAB glyph SHALL change from the open (`+`/action) glyph to a close (`×`) affordance

#### Scenario: Tapping again collapses the list

- **WHEN** the panel is open and the user taps the FAB (now a close affordance)
- **THEN** the panel SHALL close and the glyph SHALL return to the open glyph

#### Scenario: Every item shows icon and label

- **WHEN** the action list is open
- **THEN** each item SHALL render both an icon and a short text label
- **AND** no item SHALL be rendered as an icon alone

#### Scenario: Items are comfortably tappable

- **WHEN** the action list is open
- **THEN** each item's active (tappable) area SHALL be at least 48px in the block direction

### Requirement: Per-route contextual action registration

Route components SHALL contribute their actions to the launcher when activated and
SHALL remove them when deactivated, so the launcher's contents adapt to the current
page. Re-contributing from the same owner SHALL replace that owner's previous set
(not accumulate), so a within-route state change (e.g. dashboard mode switch) never
leaves stale items. After navigation away from a route, that route's actions SHALL
no longer appear.

#### Scenario: Dashboard contributes its actions

- **WHEN** the dashboard is displayed in My Timetable mode
- **THEN** the launcher SHALL present the dashboard's actions (beam toggle, filter, mode switch, help)

#### Scenario: Actions removed on navigation away

- **WHEN** the user navigates from a route that contributed actions to a route that does not
- **THEN** the previous route's actions SHALL no longer appear in the launcher

#### Scenario: Within-route mode change replaces, not accumulates

- **WHEN** the dashboard switches from My Timetable to All Nearby mode
- **THEN** the launcher SHALL present the All Nearby action set
- **AND** the My Timetable-only actions (beam toggle, filter) SHALL NOT remain in the list
- **AND** actions SHALL NOT be duplicated

### Requirement: Command and toggle action items

An action item SHALL be either a **command** (a one-shot action that, on tap,
performs its effect — e.g. opening an existing bottom sheet or switching view) or a
**toggle** (a persistent on/off control shown inline in the panel). A toggle item
SHALL reflect its current on/off state to assistive technology and SHALL flip that
state immediately on tap without leaving the panel. Command items that open another
surface SHALL close the launcher panel as that surface opens, so at most one overlay
is active at a time.

#### Scenario: Command item opens its surface and closes the panel

- **WHEN** the user taps a command item that opens a bottom sheet (filter or help)
- **THEN** the corresponding bottom sheet SHALL open
- **AND** the launcher panel SHALL close so only the sheet remains visible

#### Scenario: Toggle item flips state inline

- **WHEN** the user taps a toggle item (beam effect)
- **THEN** the underlying state SHALL flip immediately
- **AND** the item SHALL reflect the new state (pressed/selected) to assistive technology
- **AND** the panel SHALL remain open

### Requirement: Material 3 Expressive shape morph and spring motion

Opening and closing the launcher SHALL use physics-based (spring) motion rather than
a fixed linear ease, with the FAB shape morphing between a rounded button and the
rounded-rectangle panel and the glyph rotating between the open and close states.
Action items SHALL enter in a brief staggered sequence. All motion SHALL respect the
`prefers-reduced-motion: reduce` user preference by landing the same end state
without overshoot or staggered movement. The expanded panel SHALL maintain strong
contrast against its items and against the dimmed page behind it.

#### Scenario: Expansion uses spring motion with shape morph

- **WHEN** the user opens the launcher
- **THEN** the FAB SHALL morph toward the panel shape with a springy (overshooting) motion
- **AND** the glyph SHALL rotate from the open glyph to the close affordance
- **AND** the action items SHALL enter in a short staggered sequence

#### Scenario: Reduced motion lands the end state without bounce

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **AND** the user opens or closes the launcher
- **THEN** the panel SHALL reach its open/closed end state without overshoot or per-item stagger movement
- **AND** the launcher SHALL remain fully functional

#### Scenario: Expanded panel keeps strong contrast

- **WHEN** the launcher panel is open
- **THEN** the panel surface SHALL be visually distinct (strong contrast) from its action items and from the page behind it

### Requirement: Launcher accessibility contract

The FAB SHALL be an accessible disclosure control, not an ARIA menu: it SHALL expose
its expanded/collapsed state and reference the panel it controls. When the panel
opens, keyboard focus SHALL move into the panel; when it closes, focus SHALL return
to the FAB. The panel SHALL be dismissible by pressing Escape and by activating
outside it (light dismiss).

#### Scenario: FAB exposes disclosure state

- **WHEN** the FAB is rendered
- **THEN** it SHALL expose an expanded/collapsed state to assistive technology
- **AND** it SHALL reference the panel element it controls
- **AND** it SHALL NOT be exposed as an ARIA `menu` with `menuitem` children

#### Scenario: Focus moves into the panel and back

- **WHEN** the user opens the launcher
- **THEN** keyboard focus SHALL move into the panel (first action item)
- **WHEN** the user closes the launcher
- **THEN** focus SHALL return to the FAB

#### Scenario: Escape and outside activation dismiss the panel

- **WHEN** the panel is open and the user presses Escape or activates outside the panel
- **THEN** the panel SHALL close

### Requirement: Persisted left-handed placement

The system SHALL provide a left-handed mode that mirrors the FAB and its panel to
the opposite bottom corner, so left-handed users can reach the launcher one-handed.
The preference SHALL be user-settable and SHALL persist across sessions. The default
placement SHALL be the bottom-right (right-handed) corner.

#### Scenario: Default placement is bottom-right

- **WHEN** the user has never set a handedness preference
- **THEN** the FAB and its panel SHALL be placed in the bottom-right corner
- **AND** the panel SHALL expand from that corner

#### Scenario: Left-handed mode mirrors placement

- **WHEN** the user enables left-handed mode
- **THEN** the FAB and its panel SHALL be mirrored to the bottom-left corner
- **AND** the panel SHALL expand from that corner

#### Scenario: Preference persists across sessions

- **WHEN** the user has set a handedness preference and reloads the app
- **THEN** the launcher SHALL be placed according to the saved preference without further interaction

