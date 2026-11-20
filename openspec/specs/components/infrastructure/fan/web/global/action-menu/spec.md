# Action Menu

## Purpose

Provides a single thumb-reachable floating action launcher that expands into a labeled list of actions relevant to the current route, such as toggling the timetable's beam effect or opening filters, remembering a left- or right-handed placement.

## Requirements

### Requirement: App shell hosts the global action menu

The app shell SHALL host a single global action menu (see the
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
- **THEN** the shell SHALL render exactly one action menu instance in the top layer
- **AND** the launcher SHALL be positioned in the navigation bar's centre notch using the navigation bar's published height plus the safe-area inset

#### Scenario: Launcher absent on fullscreen routes

- **WHEN** the user is on the Landing Page or Auth Callback route
- **THEN** the shell SHALL NOT render the action menu

#### Scenario: Navigation height is published for offset

- **WHEN** the bottom navigation bar is rendered
- **THEN** its rendered height SHALL be exposed to the launcher (e.g. via a CSS custom property on the shell)
- **AND** the launcher's bottom offset SHALL be derived from that height plus the bottom safe-area inset, without a hard-coded pixel constant

### Requirement: User can toggle the laser beam spotlight effect on the timetable

The timetable SHALL provide a toggle to enable or disable the laser beam spotlight
visual effect on the concert highway. The toggle SHALL be presented as an inline
toggle item within the action menu panel (see the `fab-action-launcher`
capability), not as a button in the page header. The preference SHALL be persisted
in localStorage under the key `beams.enabled`. The default state SHALL be
`false` (disabled). The toggle item SHALL be contributed to the launcher whenever the timetable
is shown.

#### Scenario: Default state is off on first visit

- **WHEN** a user visits the timetable for the first time
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

- **WHEN** the user reloads the timetable
- **AND** `beams.enabled` is `"true"` in localStorage
- **THEN** the laser beam effect SHALL be enabled immediately on load without user interaction

#### Scenario: Toggle button placement and icon

- **WHEN** the timetable is displayed
- **THEN** a beam toggle item SHALL be contributed to the action menu panel
- **AND** the item SHALL use the `spotlight` icon together with a text label
- **AND** the item SHALL reflect the current enabled state to assistive technology (pressed/selected)
- **AND** the beam toggle SHALL NOT be rendered as a button in the page header

### Requirement: Filter chip UI in page header

The timetable filter SHALL be reached from the action menu (see the
`fab-action-launcher` capability) instead of a dedicated trigger button in the page
header; the page header SHALL NOT host a filter trigger. The launcher's filter item
SHALL visually indicate when a filter is active. Artist names SHALL NOT be rendered
as chips in the header. The filter item SHALL be contributed to the launcher while
the timetable is shown and the fan is not onboarding.

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

- **WHEN** the timetable header is rendered
- **THEN** the header SHALL NOT contain a filter trigger button
- **AND** the filter SHALL be reachable only via the action menu

### Requirement: Global thumb-zone floating launcher

The system SHALL render a single 56px circular floating action button (action menu),
horizontally centred on the screen, whose centre lies on the top edge of the bottom
navigation bar so that it protrudes from a notch cut into the bar, on every route
where the launcher has at least one item: an action the route contributes, or the
Settings item of the tab pages. The notch SHALL leave a gap of at least
6px around the action menu. The action menu SHALL be filled with the brand gradient (primary to
secondary) and SHALL carry a brand-coloured glow. The action menu SHALL be promoted to the
browser top layer (not stacked via `z-index`), so it stays above and receives taps
over any route content, including canvases. The action menu SHALL NOT cover any navigation
tab. The action menu SHALL be hidden whenever the navigation bar is hidden (e.g. landing
page, auth callback), when the launcher has no item, or while the displayed route
hides the launcher (My Artists in edit mode). While a
snack bar is open or a persistent bottom banner is visible, the action menu SHALL sink into
the navigation bar (see "The action menu yields to a snack bar or a bottom banner"). While a bottom sheet is open, the action menu SHALL NOT be shown, so it never covers the sheet.

#### Scenario: action menu floats in the thumb zone above content

- **WHEN** a route where the launcher has at least one item is displayed
- **THEN** the action menu SHALL be horizontally centred, with its centre on the navigation bar's top edge
- **AND** the navigation bar SHALL show a notch around the action menu with a gap of at least 6px
- **AND** no navigation tab's icon or label SHALL be covered by the action menu

#### Scenario: A bottom banner is visible

- **WHEN** a route where the launcher has at least one item is displayed while the install banner or the signup prompt is visible
- **THEN** the action menu SHALL be sunk into the navigation bar, 40px across and horizontally centred
- **AND** no part of the action menu SHALL extend above the navigation bar's top edge

#### Scenario: action menu stays above the Discovery orb

- **WHEN** the Discovery route is displayed and the discovery orb extends behind the action menu
- **THEN** the action menu SHALL be in the browser top layer
- **AND** a tap at the action menu's centre SHALL reach the action menu, not the orb

#### Scenario: action menu hidden when navigation is hidden

- **WHEN** the current route hides the bottom navigation bar (landing page or auth callback)
- **THEN** the action menu SHALL NOT be rendered

#### Scenario: action menu hidden when no actions are contributed

- **WHEN** a route outside the four tabs that contributes zero actions is displayed (for example Settings)
- **THEN** the action menu SHALL NOT be rendered
- **AND** the navigation bar SHALL show no notch (see Bottom Nav Bar)

#### Scenario: action menu hidden while the route hides the launcher

- **WHEN** My Artists is in edit mode
- **THEN** the action menu SHALL NOT be rendered, although the Settings item would otherwise be offered
- **AND** the action menu SHALL be shown again when edit mode ends

#### Scenario: action menu hidden while a bottom sheet is open

- **WHEN** a bottom sheet (for example the concert sheet) is open on a route where the launcher has at least one item
- **THEN** the action menu SHALL NOT be shown
- **AND** the action menu SHALL be shown again when the sheet closes

### Requirement: Single-tap disclosure of a labeled action list

A single tap on the action menu SHALL toggle the action arc: the contributed actions laid out
along an arc that follows the dominant thumb's sweep, with the action menu as the arc's tip.
For a right-handed user the arc SHALL start at the action menu and curve upward and to the
right, rising more than it widens, so that each item sits higher and further right
than the one before it. The first contributed action SHALL sit closest to the action menu.
Long-press or gesture activation SHALL NOT be required. Every action item SHALL be
presented as a 48px circular icon **and** a short text label together; icon-only
items SHALL NOT be allowed. Each label SHALL sit on the outer side of its icon (away
from the thumb) and SHALL NOT overlap any other item's icon or label. Every item SHALL
lie within the screen with at least a 16px margin. When collapsed, the action menu SHALL show
an equalizer glyph (three vertical bars of different heights) 32px tall; when
expanded it SHALL show a close (`×`) affordance.

#### Scenario: Tapping the action menu expands the action list

- **WHEN** the user taps the collapsed action menu
- **THEN** every contributed action SHALL be laid out along the arc, each item higher and further toward the dominant-hand side than the previous one
- **AND** the action menu glyph SHALL change from the equalizer glyph to a close (`×`) affordance

#### Scenario: Tapping again collapses the list

- **WHEN** the arc is open and the user taps the action menu (now a close affordance)
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

- **WHEN** the action arc is open with the timetable's three actions (beam toggle, filter, help)
- **THEN** no label's box SHALL intersect another item's icon or label box
- **AND** every item SHALL lie at least 16px inside the screen edges

#### Scenario: Items are comfortably tappable

- **WHEN** the action arc is open
- **THEN** each item's tappable area SHALL be at least 48px in both directions

### Requirement: Per-route contextual action registration

Route components SHALL contribute their actions to the launcher when activated and
SHALL remove them when deactivated, so the launcher's contents adapt to the current
page. Re-contributing from the same owner SHALL replace that owner's previous set
(not accumulate), so a within-route state change (e.g. the end of the fan's onboarding on the timetable, or a switch between Discovery's views) never
leaves stale items. After navigation away from a route, that route's actions SHALL
no longer appear.

#### Scenario: Timetable contributes its actions

- **WHEN** the timetable is displayed to a fan who is not onboarding
- **THEN** the timetable's actions in the launcher SHALL be the beam toggle, the filter and help, followed by the Settings item (see "The launcher ends with Settings on the tab pages")

#### Scenario: Discovery contributes its actions per view

- **WHEN** Discovery shows the Concerts view
- **THEN** Discovery's actions in the launcher SHALL be the filter and help, the filter closest to the action menu, followed by the Settings item
- **WHEN** Discovery shows the artist bubbles
- **THEN** Discovery's only action in the launcher SHALL be help, followed by the Settings item

#### Scenario: Actions removed on navigation away

- **WHEN** the user navigates from a route that contributed actions to a route that does not
- **THEN** the previous route's actions SHALL no longer appear in the launcher

#### Scenario: Within-route mode change replaces, not accumulates

- **WHEN** the fan's onboarding completes while the timetable is displayed
- **THEN** the timetable's actions in the launcher SHALL be the beam toggle, the filter and help, followed by the Settings item
- **AND** actions SHALL NOT be duplicated

#### Scenario: Switching Discovery's view replaces its actions

- **WHEN** the fan switches Discovery from the Concerts view to the artist bubbles and back
- **THEN** Discovery's actions SHALL be help only on the bubbles, and the filter and help on the Concerts view, each followed by the Settings item
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
a fixed linear ease: on open, each action item SHALL travel from the action menu along the
arc to its place with a springy, slightly overshooting motion while it fades in, in a
brief staggered sequence starting with the item closest to the action menu; on close, the
items SHALL travel back into the action menu. The glyph SHALL morph between the equalizer and
the close affordance, and the equalizer bars SHALL bounce once only at the moment the
launcher opens (never while idle). A scrim SHALL dim the page behind the open arc and SHALL take every tap outside the arc's items: such a tap SHALL only close the arc, never reach the page beneath. The action menu SHALL stay above the scrim as the close affordance.
All motion SHALL respect the `prefers-reduced-motion: reduce` user preference by
landing the same end state without overshoot, travel, stagger or bounce. The open
arc SHALL maintain strong contrast between its items and the dimmed page behind it.

#### Scenario: Expansion uses spring motion

- **WHEN** the user opens the launcher
- **THEN** each item SHALL start at the action menu and travel along the arc to its place with a springy (overshooting) motion while fading in
- **AND** the items SHALL enter in a short staggered sequence, closest to the action menu first
- **AND** the glyph SHALL morph from the equalizer to the close affordance, the bars bouncing once

#### Scenario: Idle glyph is still

- **WHEN** the action menu is collapsed and the user does not interact with it
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

The action menu SHALL be an accessible disclosure control, not an ARIA menu: it SHALL expose
its expanded/collapsed state and reference the panel it controls. When the panel
opens, keyboard focus SHALL move into the panel; when it closes, focus SHALL return
to the action menu. The panel SHALL be dismissible by pressing Escape and by activating
outside it (light dismiss).

#### Scenario: action menu exposes disclosure state

- **WHEN** the action menu is rendered
- **THEN** it SHALL expose an expanded/collapsed state to assistive technology
- **AND** it SHALL reference the panel element it controls
- **AND** it SHALL NOT be exposed as an ARIA `menu` with `menuitem` children

#### Scenario: Focus moves into the panel and back

- **WHEN** the user opens the launcher
- **THEN** keyboard focus SHALL move into the panel (first action item)
- **WHEN** the user closes the launcher
- **THEN** focus SHALL return to the action menu

#### Scenario: Escape and outside activation dismiss the panel

- **WHEN** the panel is open and the user presses Escape or activates outside the panel
- **THEN** the panel SHALL close

### Requirement: The action menu shows its collapsed state after navigation

Whenever the action menu is shown after a navigation, it SHALL be collapsed: the action arc SHALL be closed, the glyph SHALL be the collapsed glyph, and the action menu SHALL expose the collapsed state to assistive technology. This SHALL hold even if the arc was open when the user left the previous route, including when the action menu stays shown from one route to the next (each tab page ends with the Settings item).

#### Scenario: Leaving with the arc open and coming back
- **WHEN** the user opens the action arc on the timetable
- **AND** taps the Tickets tab, where the launcher offers only the Settings item
- **THEN** the action menu on Tickets SHALL show the collapsed (equalizer) glyph
- **AND** when the user taps the Timetable tab again, the action menu SHALL show the collapsed glyph
- **AND** the action menu SHALL expose the collapsed state (not expanded)

#### Scenario: Moving between two routes that both contribute actions
- **WHEN** the action arc is open on the timetable and the user navigates to My Artists
- **THEN** the action menu on My Artists SHALL be collapsed

### Requirement: Persisted handedness of the action arc

The system SHALL provide a left-handed mode that mirrors the action arc so it
curves upward and to the left, following the left thumb's sweep. The action menu itself SHALL
stay in the centre notch in both modes. The preference SHALL be user-settable and
SHALL persist across sessions. The default SHALL be right-handed.

#### Scenario: Default arc curves to the right

- **WHEN** the user has never set a handedness preference
- **THEN** the action menu SHALL be in the centre notch
- **AND** the action arc SHALL curve upward and to the right, with labels on the left of their icons

#### Scenario: Left-handed mode mirrors the arc

- **WHEN** the user enables left-handed mode
- **THEN** the action menu SHALL stay in the centre notch
- **AND** the action arc SHALL curve upward and to the left, with labels on the right of their icons

#### Scenario: Preference persists across sessions

- **WHEN** the user has set a handedness preference and reloads the app
- **THEN** the action arc SHALL open toward the saved side without further interaction

### Requirement: The action menu yields to a snack bar or a bottom banner

While any snack bar is open, or a persistent bottom banner (the signup prompt or the install banner) is visible, the action menu SHALL sink into the navigation bar's centre slot so the snack bar or the banner can sit directly above the navigation bar without covering the action menu. Sunk, the action menu SHALL be 40px across and SHALL lie entirely within the navigation bar's height, and it SHALL stay tappable. When no snack bar is open and no bottom banner is visible, the action menu SHALL return to its normal size and position. The movement SHALL use spring motion and SHALL respect `prefers-reduced-motion: reduce` by landing the end state without overshoot.

#### Scenario: A snack bar opens
- **WHEN** a snack bar opens on a route where the action menu is shown
- **THEN** the action menu SHALL shrink to 40px across
- **AND** no part of the action menu SHALL extend above the navigation bar's top edge
- **AND** the action menu and the snack bar SHALL NOT overlap

#### Scenario: A bottom banner is visible
- **WHEN** a route that shows the action menu is displayed while the install banner or the signup prompt is visible
- **THEN** the action menu SHALL be 40px across and lie entirely within the navigation bar's height
- **AND** the action menu and the banner SHALL NOT overlap
- **AND** no content above the banner SHALL be covered by the action menu

#### Scenario: The sunk action menu still opens the actions
- **WHEN** a snack bar is open or a bottom banner is visible, and the user taps the sunk action menu
- **THEN** the action arc SHALL open as it does from the normal action menu

#### Scenario: A snack bar opens above a bottom banner
- **WHEN** a snack bar opens while a bottom banner is visible
- **THEN** the action menu SHALL stay sunk
- **AND** the snack bar SHALL sit above the banner, overlapping neither the action menu nor the banner

#### Scenario: The last snack bar closes
- **WHEN** the last open snack bar closes and no bottom banner is visible
- **THEN** the action menu SHALL return to 56px across, protruding from the notch

#### Scenario: The bottom banner goes away
- **WHEN** the visible bottom banner is removed (the app is installed, or the guest signs up) and no snack bar is open
- **THEN** the action menu SHALL return to 56px across, protruding from the notch

### Requirement: The launcher ends with Settings on the tab pages

On the pages of the four navigation tabs (Home, Discover, My Artists, Tickets), the launcher SHALL offer a Settings item (icon and the label 「設定」 / "Settings") after the actions the page contributes, as the item farthest from the action menu along the arc. Choosing it SHALL close the launcher and display the Settings route. The launcher SHALL NOT offer the Settings item on any other route, including Settings itself. The Settings item is the only way into Settings from the tab pages.

#### Scenario: Settings is the last item on the timetable

- **WHEN** the timetable is displayed to a fan who is not onboarding and the fan opens the launcher
- **THEN** the items are, from the action menu outward, the beam toggle, the filter, help and Settings

#### Scenario: Settings is the only item on Tickets

- **WHEN** the Tickets route is displayed
- **THEN** the action menu is shown
- **AND** opening it offers Settings as its only item

#### Scenario: Choosing Settings

- **WHEN** the fan chooses Settings in the launcher
- **THEN** the launcher closes and the Settings route is displayed

#### Scenario: No Settings item outside the tabs

- **WHEN** the Settings route, a Concert page or an order detail is displayed
- **THEN** the launcher offers no Settings item
