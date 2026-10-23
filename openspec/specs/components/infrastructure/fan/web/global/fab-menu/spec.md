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
the launcher SHALL NOT be rendered. So the launcher can sit in the navigation bar's
centre notch, the shell SHALL make the navigation bar's rendered height available
to the launcher (e.g. as a CSS custom property) rather than relying on a hard-coded
offset.

#### Scenario: Launcher present with the navigation bar

- **WHEN** the app shell renders a route that shows the bottom navigation bar
- **THEN** the shell SHALL render exactly one FAB action launcher instance in the top layer
- **AND** the launcher SHALL be positioned in the navigation bar's centre notch using the navigation bar's published height plus the safe-area inset

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
in localStorage under the key `beams.enabled`. The default state SHALL be
`false` (disabled). The toggle item SHALL be contributed to the launcher only while
the dashboard is in My Timetable mode.

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

- **WHEN** the action arc is open with the dashboard's four actions (beam toggle, filter, mode switch, help)
- **THEN** no label's box SHALL intersect another item's icon or label box
- **AND** every item SHALL lie at least 16px inside the screen edges

#### Scenario: Items are comfortably tappable

- **WHEN** the action arc is open
- **THEN** each item's tappable area SHALL be at least 48px in both directions

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
a fixed linear ease: on open, each action item SHALL travel from the FAB along the
arc to its place with a springy, slightly overshooting motion while it fades in, in a
brief staggered sequence starting with the item closest to the FAB; on close, the
items SHALL travel back into the FAB. The glyph SHALL morph between the equalizer and
the close affordance, and the equalizer bars SHALL bounce once only at the moment the
launcher opens (never while idle). A scrim SHALL dim the page behind the open arc and SHALL take every tap outside the arc's items: such a tap SHALL only close the arc, never reach the page beneath. The FAB SHALL stay above the scrim as the close affordance.
All motion SHALL respect the `prefers-reduced-motion: reduce` user preference by
landing the same end state without overshoot, travel, stagger or bounce. The open
arc SHALL maintain strong contrast between its items and the dimmed page behind it.

#### Scenario: Expansion uses spring motion

- **WHEN** the user opens the launcher
- **THEN** each item SHALL start at the FAB and travel along the arc to its place with a springy (overshooting) motion while fading in
- **AND** the items SHALL enter in a short staggered sequence, closest to the FAB first
- **AND** the glyph SHALL morph from the equalizer to the close affordance, the bars bouncing once

#### Scenario: Idle glyph is still

- **WHEN** the FAB is collapsed and the user does not interact with it
- **THEN** the equalizer bars SHALL NOT move

#### Scenario: Reduced motion lands the end state without bounce

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **AND** the user opens or closes the launcher
- **THEN** the items SHALL appear in or disappear from their places without travel, overshoot, stagger or bounce
- **AND** the launcher SHALL remain fully functional

#### Scenario: Expanded panel keeps strong contrast

- **WHEN** the action arc is open
- **THEN** each item SHALL be visually distinct (strong contrast) from the dimmed page behind it

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

### Requirement: The FAB shows its collapsed state after navigation

Whenever the FAB is shown after a navigation, it SHALL be collapsed: the action arc SHALL be closed, the glyph SHALL be the collapsed glyph, and the FAB SHALL expose the collapsed state to assistive technology. This SHALL hold even if the arc was open when the user left the previous route.

#### Scenario: Leaving with the arc open and coming back
- **WHEN** the user opens the action arc on the dashboard
- **AND** taps the Tickets tab, where no actions are contributed
- **AND** taps the Home tab again
- **THEN** the FAB SHALL show the collapsed (equalizer) glyph
- **AND** the FAB SHALL expose the collapsed state (not expanded)

#### Scenario: Moving between two routes that both contribute actions
- **WHEN** the action arc is open on the dashboard and the user navigates to My Artists
- **THEN** the FAB on My Artists SHALL be collapsed

### Requirement: Persisted handedness of the action arc

The system SHALL provide a left-handed mode that mirrors the action arc so it
curves upward and to the left, following the left thumb's sweep. The FAB itself SHALL
stay in the centre notch in both modes. The preference SHALL be user-settable and
SHALL persist across sessions. The default SHALL be right-handed.

#### Scenario: Default arc curves to the right

- **WHEN** the user has never set a handedness preference
- **THEN** the FAB SHALL be in the centre notch
- **AND** the action arc SHALL curve upward and to the right, with labels on the left of their icons

#### Scenario: Left-handed mode mirrors the arc

- **WHEN** the user enables left-handed mode
- **THEN** the FAB SHALL stay in the centre notch
- **AND** the action arc SHALL curve upward and to the left, with labels on the right of their icons

#### Scenario: Preference persists across sessions

- **WHEN** the user has set a handedness preference and reloads the app
- **THEN** the action arc SHALL open toward the saved side without further interaction

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
