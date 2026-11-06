# My Artists

## Purpose

Displays and manages the artists a user follows, letting them adjust each artist's hype level with an inline slider, remove artists via an accessible edit mode with undo, and switch between list and grid views.

## Requirements

### Requirement: Edit-mode controls are accessible

The Edit toggle and the per-row remove controls SHALL be operable and understandable by assistive technology and keyboard users. The Edit toggle SHALL expose its pressed/active state, and each remove control SHALL have an accessible name identifying the artist it removes.

#### Scenario: Edit toggle exposes pressed state

- **WHEN** the Edit toggle is rendered
- **THEN** it SHALL be a real button operable by keyboard (Enter/Space)
- **AND** it SHALL expose its active state to assistive technology (e.g., `aria-pressed`)

#### Scenario: Remove control has an accessible name

- **WHEN** a per-row remove (−) control is shown in edit mode
- **THEN** it SHALL have an accessible name that identifies the artist to be unfollowed (e.g., "Unfollow {artist name}")
- **AND** it SHALL be operable by keyboard

### Requirement: Remove control unfollows immediately with Undo

Tapping the per-row remove (−) control in edit mode SHALL unfollow that artist immediately using the existing optimistic-removal flow, without a separate confirmation sheet, and SHALL surface an Undo affordance so the action is recoverable. Unfollow SHALL route through the existing follow-store flow (guest localStorage write or authenticated RPC) unchanged.

#### Scenario: Remove unfollows immediately

- **WHEN** the user taps the remove (−) control for an artist row in edit mode
- **THEN** the artist SHALL be removed from the list optimistically
- **AND** the unfollow SHALL be committed via the existing follow-store flow

#### Scenario: Undo restores the artist

- **WHEN** an unfollow has just been triggered via the remove control
- **AND** the user activates the Undo affordance before it expires
- **THEN** the artist SHALL be restored to the list
- **AND** the pending unfollow SHALL NOT be committed (or SHALL be reversed) consistent with the existing undo behavior

#### Scenario: Unfollow blocked during onboarding

- **WHEN** the user is still in onboarding (`OnboardingService.isOnboarding` is `true`)
- **AND** the user taps a remove control
- **THEN** the unfollow SHALL NOT execute, preserving the existing onboarding guard

### Requirement: My Artists list-view only
The My Artists route SHALL display artists in list view only. The grid toggle button, grid layout, context menu dialog, and all grid-specific interaction handlers SHALL be removed.

#### Scenario: My Artists page loads
- **WHEN** a user navigates to My Artists
- **THEN** artists are displayed in list view with no toggle button to switch views

#### Scenario: No grid-related CSS
- **WHEN** the My Artists stylesheet is loaded
- **THEN** it SHALL NOT contain `.artist-grid`, `.grid-tile`, or related grid layout rules

### Requirement: Followed artists and their hype levels

My Artists SHALL list the fan's followed artists, each with its hype level active on the hype control, and SHALL show the empty state, with a way to discover artists, when the fan follows none. A newly followed artist SHALL show Nearby active. When a signed-in fan picks a hype level, it SHALL show at once; when saving fails and one retry also fails, the previous level SHALL show again and a message SHALL say the change failed.

#### Scenario: Newly followed artist

- **WHEN** a fan opens My Artists right after following an artist
- **THEN** the artist is listed with Nearby active

#### Scenario: No followed artists

- **WHEN** a fan who follows no artist opens My Artists
- **THEN** the empty state is shown

#### Scenario: Hype change fails

- **WHEN** a signed-in fan picks Away for an artist at Home and saving fails twice
- **THEN** the artist shows Home again and a message says the change failed

### Requirement: Hype header legend stays above the scrolling list

The My Artists list view SHALL display a header row showing hype tier icons and labels above the artist rows. Only the artist rows SHALL scroll; the header SHALL stay outside the scrolling area, so no row can be drawn over it. The header SHALL remain the column header of the artist table for assistive technology.

#### Scenario: Header renders with 4 columns

- **WHEN** the My Artists page renders in list view
- **THEN** the system SHALL display a header row below the page title
- **AND** the header SHALL contain 4 equally-spaced columns: 👀 Watch, 🔥 Home, 🔥🔥 Nearby, 🔥🔥🔥 Away, the same in every language
- **AND** each column SHALL vertically align with the corresponding dot stop on the artist rows

#### Scenario: Header column alignment matches artist row dot positions

- **WHEN** the header and any artist row are visible simultaneously
- **THEN** the center of each header label SHALL be horizontally aligned, within 1 px, with the center of the corresponding dot in the artist row

#### Scenario: Header remains visible during scroll

- **WHEN** the user scrolls the artist list by 300 px on a 375 × 600 px screen with 40 followed artists
- **THEN** the header SHALL stay at the same position it had before the scroll
- **AND** every header label SHALL be fully visible, with no part of a row, a dot or a track line drawn over it
- **AND** the header SHALL have a `[data-hype-header]` attribute for coach mark targeting

#### Scenario: Header stays clear while a row animates out

- **WHEN** the fan removes an artist in edit mode while the list is scrolled, in a browser that supports nested view-transition groups (`view-transition-group`, CSS View Transitions 2)
- **THEN** the row's exit animation SHALL NOT draw over the header
- **WHEN** the browser does NOT support nested view-transition groups
- **THEN** rows scrolled under the header MAY be drawn over it until the exit animation ends (the flat groups of the prior behavior); once it has ended, nothing SHALL be drawn over the header

#### Scenario: Table semantics are kept

- **WHEN** a screen reader reads the artist list
- **THEN** it SHALL announce a table whose column headers are the four hype labels and whose row headers are the artist names

### Requirement: Inline Dot Slider

Each artist row in the My Artists list view SHALL include a 4-stop discrete dot slider for hype level selection, enabling 1-tap changes without opening a bottom sheet.

The slider component SHALL be a pure presentation component with zero business logic. It SHALL expose `hype` as a `twoWay` bindable and render the active dot accordingly. The slider SHALL NOT contain authentication, onboarding, persistence, or event dispatch logic.

The slider SHALL use native HTML `<fieldset>` with a visually hidden `<legend>` as the group container. Each hype stop SHALL be a `<label>` wrapping a native `<input type="radio">` (visually hidden) and a visual dot `<span>`. The radio inputs SHALL use Aurelia 2's `model.bind`/`checked.bind` pattern with two-way binding on `hype`. When the user taps a dot, the radio's native behavior updates `hype` via Aurelia binding, which pushes to the parent's data via `twoWay` mode. The native `change` event bubbles through the light DOM to the parent, which decides whether to accept or revert the change.

#### Scenario: Slider renders on each artist row

- **WHEN** an artist row renders in list view
- **THEN** the row SHALL display the artist name (left-aligned, truncated with ellipsis) and the dot slider (right-aligned) on the same row
- **AND** the slider SHALL display 4 dot stops connected by a 2px track line
- **AND** the active dot SHALL be 14px diameter; inactive dots SHALL be 8px diameter
- **AND** each dot SHALL have a minimum 44x44px transparent tap target area

#### Scenario: User taps a dot

- **WHEN** a user taps any dot on a slider
- **THEN** the radio's native `checked` state SHALL update via Aurelia's `checked.bind`
- **AND** the `twoWay` binding SHALL push the new value to the parent's bound property
- **AND** the native `change` event SHALL bubble through the custom element boundary
- **AND** the parent SHALL handle the `change` event to apply business logic

#### Scenario: Parent accepts hype selection

- **WHEN** the parent does NOT revert the bound property after a `change` event
- **THEN** the slider SHALL remain at the new position (already updated by native radio behavior)

#### Scenario: Parent reverts hype selection

- **WHEN** the parent reverts the bound property (e.g., `artist.hype = prevValue`) after a `change` event
- **THEN** the `twoWay` binding SHALL push the reverted value back to the slider
- **AND** the slider SHALL return to the previous dot position
- **AND** the programmatic update SHALL NOT trigger another `change` event (native DOM behavior)

#### Scenario: Active dot reflects hype tier CSS effects

- **WHEN** the slider renders with a specific hype level selected
- **THEN** the active dot SHALL apply CSS glow effects based on the `HypeType` enum value:
  - WATCH (1): `1px solid white/10` border, no glow
  - HOME (2): artist-color border at 40% opacity, `box-shadow: 0 0 8px` at 30% opacity
  - NEARBY (3): artist-color `2px solid` border, `box-shadow: 0 0 16px` at 50% opacity, gentle pulse animation
  - AWAY (4): animated gradient border, layered glow (`0 0 24px` at 60% + `0 0 48px` at 20%), strong pulse animation
- **AND** the CSS `data-level` attribute SHALL use `HypeType` enum values (1, 2, 3, 4)
- **AND** the artist color SHALL be derived from the existing deterministic color generator

#### Scenario: Reduced motion preference

- **WHEN** the user has `prefers-reduced-motion: reduce` enabled
- **THEN** all pulse and gradient rotation animations on active dots SHALL be disabled
- **AND** static border and glow styles SHALL remain visible

#### Scenario: Native radio input semantics

- **WHEN** the artist table renders
- **THEN** the entire table SHALL be wrapped in a `<fieldset>` with a visually hidden `<legend>` (the page title serves as label)
- **AND** each hype stop within a row SHALL be a `<label>` containing a visually hidden `<input type="radio">` and a visual dot `<span>`
- **AND** all radio inputs for one artist SHALL share a `name` attribute scoped to the artist (e.g., `hype-{artistId}`)
- **AND** the selected radio SHALL be `checked` via Aurelia's `model.bind`/`checked.bind` pattern

### Requirement: Slider Track Vertical Centering

The slider track line SHALL be vertically centered within the slider grid cell using CSS logical properties.

#### Scenario: Track is vertically centered

- **WHEN** the slider renders
- **THEN** the `.hype-slider-track` element SHALL use `inset-block-start: 50%` and `translate: 0 -50%` to center vertically within the grid row
- **AND** the track SHALL remain centered across viewport sizes

### Requirement: Slider dot positions align with header columns

The 4 dot stops of every artist row SHALL align with the 4 header legend columns at every viewport width.

#### Scenario: Slider spans header dot columns

- **WHEN** the page renders on a 320 px, a 375 px and a 768 px wide screen
- **THEN** on each width the center of every dot stop SHALL be horizontally aligned, within 1 px, with the center of its header column

### Requirement: Animated list enter and exit

Content and following lists SHALL animate item insertion and removal (enter/exit) rather than swapping the
DOM instantly, using discrete-transition primitives with a reduced-motion fallback that lands the end state.

#### Scenario: Unfollow animates the item out

- **WHEN** a user removes an item from a list (e.g. unfollows an artist)
- **THEN** the item animates out before removal rather than disappearing instantly

#### Scenario: New item animates in

- **WHEN** an item is added to a rendered list
- **THEN** it animates in (enter transition) rather than appearing abruptly

#### Scenario: Reduced motion lands end state

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** list changes apply without transition, arriving directly at the final state

### Requirement: Hype Change Persisted for Guest Users

The system SHALL persist hype changes made by guest users to localStorage without reverting them, and SHALL keep hype editing fully decoupled from onboarding state. Changing a hype level SHALL NOT advance, complete, or otherwise mutate onboarding state, and a repeated hype change (second tap onward) SHALL always apply.

#### Scenario: Guest user changes hype during onboarding

- **WHEN** a guest user changes a hype level while `OnboardingService.isOnboarding` is `true`
- **AND** the user is not authenticated
- **THEN** the system SHALL persist the hype value in the artist's entry of `guest.followedArtists`
- **AND** the system SHALL NOT revert the hype change in the UI
- **AND** the system SHALL NOT mutate onboarding state (no step advance, no completion)
- **AND** the signup-prompt-banner SHALL already have been visible (per the `Signup Banner on My Artists` requirement in the `signup-prompt-banner` capability); no additional banner-visibility mutation is required by this change handler

#### Scenario: Repeated hype change applies every time

- **WHEN** a guest user changes a hype level
- **AND** then changes a hype level a second (or subsequent) time on the same or another artist
- **THEN** every change SHALL apply and persist
- **AND** no change SHALL be reverted due to onboarding state

#### Scenario: Guest user changes hype after onboarding completion

- **WHEN** a guest user (onboarding completed) changes a hype level on the My Artists page
- **THEN** the system SHALL persist the hype value in `GuestService`
- **AND** the system SHALL NOT show a modal dialog
- **AND** the signup-prompt-banner SHALL remain visible (non-modal, persistent per its own capability spec)

### Requirement: View Toggle (List / Grid)

The My Artists page SHALL offer a view toggle between List view (default) and Grid (Festival) view.

#### Scenario: Toggling view mode

- **GIVEN** the My Artists page header
- **WHEN** the user taps the view toggle button
- **THEN** the page SHALL switch between List and Grid view

### Requirement: Grid (Festival) View

The Grid view SHALL display followed artists as poster-style tiles in a responsive grid layout.

#### Scenario: Away tiles are larger

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype level Away (HYPE_TYPE_AWAY)
- **THEN** their tile SHALL span 2 columns and 2 rows

#### Scenario: Non-Away tiles are standard size

- **GIVEN** the Grid view is active
- **WHEN** an artist has hype level Watch, Home, or Nearby
- **THEN** their tile SHALL span 1 column and 1 row

#### Scenario: Long-press opens context menu

- **GIVEN** the Grid view is active
- **WHEN** the user long-presses a tile
- **THEN** a context menu SHALL appear with passion level options and an unfollow action

### Requirement: My Artists page help content documents all available gestures

The My Artists page help content SHALL explain how to unfollow an artist via edit mode. The help text SHALL say that choosing "編集" / "Edit" in the action menu at the bottom centre (the FAB in the bottom navigation bar) reveals a per-row remove control that unfollows immediately (with Undo). The help content SHALL NOT reference a long-press-to-unfollow gesture or an Edit control in the page header. The exact help copy is stated by the page help surface ("Page-specific Help Content").

#### Scenario: Help text visible to touch device users

- **WHEN** the user opens the My Artists page help (on any device, including touch)
- **THEN** help content explains that choosing Edit in the action menu at the bottom centre reveals a per-row remove control to unfollow an artist
- **AND** the help content does not mention a long-press unfollow gesture or a header Edit control

#### Scenario: Help text available in all supported locales

- **WHEN** the app is displayed in any supported locale (Japanese, English)
- **THEN** the edit-mode unfollow help text is translated and rendered correctly

### Requirement: My Artists hype column headers render invariant English

The artists-table column-header cells (`.hype-col-header` in `my-artists-route.html`) SHALL render the four hype tier labels as invariant English brand expressions (`Watch`, `Home`, `Nearby`, `Away`) directly in the template, not through an `entity.hype.values.*` i18n binding.

#### Scenario: Column header label rendering

- **WHEN** the My Artists table renders in either JA or EN locale
- **THEN** each `.hype-col-header` cell SHALL display `[emoji]` followed by the invariant English tier label
- **AND** the cell SHALL NOT contain a `<small t="entity.hype.values.*">` element

#### Scenario: Tier label per column

- **WHEN** the table renders
- **THEN** the four `.hype-col-header` cells SHALL display, in order:
  - `👀 Watch`
  - `🔥 Home`
  - `🔥🔥 Nearby`
  - `🔥🔥🔥 Away`
- **AND** these surface forms SHALL remain identical across all supported locales

### Requirement: Signup Banner on My Artists

The My Artists page SHALL display a persistent fixed banner above the bottom navigation bar prompting unauthenticated users to sign up. The banner SHALL be visible for any guest user on the My Artists page, regardless of onboarding state.

#### Scenario: Banner appears for guest user during onboarding

- **WHEN** an unauthenticated user views the My Artists page
- **AND** the user is in the My Artists onboarding step (or any earlier step that has progressed to this page)
- **THEN** the system SHALL display the signup-prompt-banner
- **AND** the banner SHALL be present from the moment the artist list has finished loading

#### Scenario: Banner appears for guest user after onboarding

- **WHEN** an unauthenticated user views the My Artists page
- **AND** the user has completed onboarding (`onboarding.isCompleted` is true)
- **THEN** the system SHALL display the signup-prompt-banner

#### Scenario: Banner not shown for authenticated users

- **WHEN** an authenticated user views the My Artists page
- **THEN** the signup banner SHALL NOT be rendered

#### Scenario: Banner disappears after signup

- **WHEN** the user completes signup (isAuthenticated becomes true) while on the My Artists page
- **THEN** the signup banner SHALL be removed from the DOM

### Requirement: Each artist has a stable color

Each artist in the My Artists list SHALL be shown in a color derived from the artist's name alone, so the same artist always appears in the same color and different artists appear in different hues.

#### Scenario: Same artist, same color

- **WHEN** the same artist is shown twice, in the same session or a later one
- **THEN** both show the identical color

#### Scenario: Different artists, different hues

- **WHEN** two artists with different names are shown
- **THEN** their colors have different hues

#### Scenario: Artist with an empty name

- **WHEN** an artist's name is empty
- **THEN** the artist is still shown in a valid color

### Requirement: Edit in the action launcher reveals per-row remove controls

The My Artists page SHALL offer an "編集" / "Edit" action in its FAB action launcher whenever at least one followed artist is listed. Choosing it SHALL put the list into edit mode and close the launcher; in edit mode each artist row SHALL display a remove (−) control as a single-tap, single-pointer affordance available on all pointer types (touch and mouse), in place of the row's hype controls, and a "完了" / "Done" bar SHALL be shown in the list. Pressing Done SHALL leave edit mode and hide the remove controls. While in edit mode the FAB action launcher SHALL NOT be shown, so neither Edit nor the Settings item of the tab pages is offered; it SHALL be shown again when edit mode ends. Edit mode SHALL NOT depend on any path-based or timed gesture (no swipe, no long-press), satisfying single-pointer operability (WCAG 2.5.1).

#### Scenario: Entering edit mode reveals remove controls

- **WHEN** the user chooses Edit in the FAB action launcher on the My Artists page
- **THEN** every artist row displays a remove (−) control in place of its hype controls
- **AND** the Done bar is shown and the launcher closes
- **AND** the FAB is not shown until the user presses Done

#### Scenario: Leaving edit mode hides remove controls

- **WHEN** the user presses Done while in edit mode
- **THEN** the remove controls are no longer displayed
- **AND** the list returns to its default presentation with hype controls

#### Scenario: Remove control is available on all pointer types

- **WHEN** the My Artists page is viewed on a touch device OR a mouse device
- **AND** edit mode is active
- **THEN** the per-row remove (−) control is visible and operable with a single tap or click
- **AND** no interaction requires a long-press or swipe gesture

#### Scenario: Default (non-editing) list shows no persistent per-row unfollow control

- **WHEN** the My Artists page loads and edit mode is NOT active
- **THEN** no persistent per-row unfollow control is shown on any pointer type, keeping the default list uncluttered
- **AND** unfollow is reachable only after entering edit mode

#### Scenario: Edit offered in the action launcher

- **WHEN** the My Artists page renders with at least one followed artist
- **THEN** the FAB action launcher offers Edit, then Help, then Settings
- **AND** the page header holds no Edit control

#### Scenario: Edit hidden when there is nothing to edit

- **WHEN** the My Artists page is loading, OR has zero followed artists (empty state)
- **THEN** Edit is not offered
- **AND** Help is still offered in the launcher

#### Scenario: Edit mode exits when the last artist is removed

- **WHEN** the user is in edit mode and removes the last remaining artist
- **THEN** the list transitions to the empty state
- **AND** edit mode is exited

#### Scenario: Edit mode is not persisted across navigation

- **WHEN** the user leaves the My Artists page while in edit mode and later returns
- **THEN** the page opens in the default (non-editing) state

### Requirement: A hype change says where new concerts are pushed

When a hype level change on My Artists applies, My Artists SHALL show one snack that says, in place words, which new concerts of the artist will reach the fan by push. The place words SHALL be 「全て」 for Away, the fan's home prefecture's short name (for example 「東京」) for Home, and that name followed by 「周辺」 (for example 「東京周辺」) for Nearby; with no home area, 「居住エリア」 takes the place of the prefecture name. The snack SHALL read, on one line when it fits:

| when | snack | action |
|---|---|---|
| push is on for this browser, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知します🔔」 | none |
| push is on for this browser, Watch | 「{{name}}の新着ライブはプッシュ通知しません」 | none |
| push is off for this browser, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知で受け取ろう🔔」 | the push offer (stated by the notification prompt surface) |
| guest, Home, Nearby or Away | 「{{name}}の{{places}}の新着ライブをプッシュ通知で受け取ろう🔔」 | 「登録する」, which starts sign-up |

The English locale SHALL show equivalent texts. Push is on for this browser when the fan allowed notifications and this browser is registered for push.

When push is on, and for a guest, the snack for a level SHALL appear only the first time the fan picks that level on this device; later picks of the same level show no snack. When push is off for a signed-in fan, the snack SHALL appear on every change, except that Watch shows no snack then. A guest picking Watch sees no snack. A change whose save fails SHALL show the failure message and no hype snack. Several changes to the same artist in a row SHALL leave only the latest snack for that artist on screen.

#### Scenario: First pick of Away with push on

- **WHEN** a signed-in fan with home JP-13 whose browser receives push sets ヨルシカ to Away for the first time on this device
- **THEN** a snack reads 「ヨルシカの全ての新着ライブをプッシュ通知します🔔」

#### Scenario: Second pick of the same level

- **WHEN** that fan later sets YOASOBI to Away
- **THEN** the change applies and no snack appears

#### Scenario: Nearby with push off

- **WHEN** a signed-in fan with home JP-13 whose notification permission is undecided sets Vaundy to Nearby, for the second time that day
- **THEN** a snack reads 「Vaundyの東京周辺の新着ライブをプッシュ通知で受け取ろう🔔」 with the push offer as its action

#### Scenario: Watch for the first time

- **WHEN** a signed-in fan whose browser receives push sets King Gnu to Watch for the first time on this device
- **THEN** a snack reads 「King Gnuの新着ライブはプッシュ通知しません」

#### Scenario: Guest picks Home

- **WHEN** a guest with home JP-27 sets ヨルシカ to Home for the first time on this device
- **THEN** a snack reads 「ヨルシカの大阪の新着ライブをプッシュ通知で受け取ろう🔔」 with the action 「登録する」

#### Scenario: Quick changes to one artist

- **WHEN** a fan sets ヨルシカ to Home and then to Away within a second, and both levels are picked for the first time
- **THEN** only the snack for Away remains on screen

#### Scenario: Save fails

- **WHEN** a signed-in fan changes a hype level and saving fails twice
- **THEN** the failure message is shown and no hype snack is shown
