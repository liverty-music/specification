# Fab Menu

## Purpose

Provides a single thumb-reachable floating action launcher that expands into a labeled list of actions relevant to the current route, such as toggling the dashboard's beam effect or opening filters, remembering a left- or right-handed placement.

## Requirements

### Requirement: App shell hosts the global FAB action launcher

The app shell SHALL host a single global FAB action launcher (see the
`fab-action-launcher` capability) as a top-layer surface alongside the bottom
navigation bar. The launcher SHALL be a single instance owned by the shell (not
re-created per route). The launcher SHALL be shown only when the bottom navigation
bar is shown; on routes that hide the navigation bar (Landing Page, Auth Callback)
the launcher SHALL NOT be rendered. So the launcher can float clear of the
navigation bar, the shell SHALL make the navigation bar's rendered height available
to the launcher (e.g. as a CSS custom property) rather than relying on a hard-coded
offset.

#### Scenario: Launcher present with the navigation bar

- **WHEN** the app shell renders a route that shows the bottom navigation bar
- **THEN** the shell SHALL render exactly one FAB action launcher instance in the top layer
- **AND** the launcher SHALL be positioned clear of the navigation bar using the navigation bar's published height plus the safe-area inset

#### Scenario: Launcher absent on fullscreen routes

- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the shell SHALL NOT render the FAB action launcher

#### Scenario: Navigation height is published for offset

- **WHEN** the bottom navigation bar is rendered
- **THEN** its rendered height SHALL be exposed to the launcher (e.g. via a CSS custom property on the shell)
- **AND** the launcher's bottom offset SHALL be derived from that height plus the bottom safe-area inset, without a hard-coded pixel constant

### Requirement: User can toggle the laser beam spotlight effect on the dashboard

The dashboard SHALL provide a toggle to enable or disable the laser beam spotlight
visual effect on the concert highway. The toggle SHALL be presented as an inline
toggle item within the FAB action launcher panel (see the `fab-action-launcher`
capability), not as a button in the page header. The preference SHALL be persisted
in localStorage under the key `liverty:beams:enabled`. The default state SHALL be
`false` (disabled). The toggle item SHALL be contributed to the launcher only while
the dashboard is in My Timetable mode.

#### Scenario: Default state is off on first visit

- **WHEN** a user visits the dashboard for the first time
- **AND** the `liverty:beams:enabled` key is not set in localStorage
- **THEN** the laser beam effect SHALL NOT be rendered on the concert highway
- **AND** the beam toggle item SHALL appear in its inactive (off) state

#### Scenario: Enabling the beam effect

- **WHEN** the user taps the beam toggle item while the effect is disabled
- **THEN** the laser beam spotlight overlay SHALL appear on the concert highway
- **AND** the toggle item SHALL reflect the active (on) state
- **AND** `liverty:beams:enabled` SHALL be set to `"true"` in localStorage

#### Scenario: Disabling the beam effect

- **WHEN** the user taps the beam toggle item while the effect is enabled
- **THEN** the laser beam spotlight overlay SHALL be removed from the concert highway
- **AND** the toggle item SHALL return to its inactive (off) state
- **AND** `liverty:beams:enabled` SHALL be set to `"false"` in localStorage

#### Scenario: Preference is restored on page reload

- **WHEN** the user reloads the dashboard
- **AND** `liverty:beams:enabled` is `"true"` in localStorage
- **THEN** the laser beam effect SHALL be enabled immediately on load without user interaction

#### Scenario: Toggle button placement and icon

- **WHEN** the dashboard is displayed in My Timetable mode
- **THEN** a beam toggle item SHALL be contributed to the FAB action launcher panel
- **AND** the item SHALL use the `spotlight` icon together with a text label
- **AND** the item SHALL reflect the current enabled state to assistive technology (pressed/selected)
- **AND** the beam toggle SHALL NOT be rendered as a button in the page header

### Requirement: Filter chip UI in page header

The dashboard filter SHALL be reached from the FAB action launcher (see the
`fab-action-launcher` capability) instead of a dedicated trigger button in the page
header; the page header SHALL NOT host a filter trigger. The launcher's filter item
SHALL visually indicate when a filter is active. Artist names SHALL NOT be rendered
as chips in the header. The filter item SHALL be contributed to the launcher only
while the dashboard is in My Timetable mode.

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

### Requirement: Material 3 Expressive expansion and spring motion

Opening and closing the launcher SHALL use physics-based (spring) motion rather than
a fixed linear ease: the panel SHALL expand (scale up) from the FAB corner with a
springy, slightly overshooting motion while its opacity fades in, and the glyph
SHALL rotate between the open and close states. Per the official Material 3 menu,
the panel's corner shape is FIXED and SHALL NOT be animated (no border-radius
morph). Action items SHALL enter in a brief staggered sequence. All motion SHALL
respect the `prefers-reduced-motion: reduce` user preference by landing the same
end state without overshoot or staggered movement. The expanded panel SHALL
maintain strong contrast against its items and against the dimmed page behind it.

#### Scenario: Expansion uses spring motion

- **WHEN** the user opens the launcher
- **THEN** the panel SHALL expand from the FAB with a springy (overshooting) scale-and-fade motion, its corner shape remaining fixed (no border-radius morph)
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
