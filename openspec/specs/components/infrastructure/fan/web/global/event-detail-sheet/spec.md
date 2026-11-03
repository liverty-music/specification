# Event Detail Sheet

## Purpose

Shows a detail sheet for a selected concert with a hero image, venue and time information, and an accessible ticket-journey status control that lets a user track their ticket-acquisition progress independent of actual ticket sales.

## Requirements

### Requirement: Event Detail Sheet Hero Image
The event detail sheet SHALL display the artist's background image as a hero section above the existing artist header when `artist_background` is available. The hero image SHALL NOT be displayed when no background image exists, preserving the current layout.

#### Scenario: Artist has background image
- **WHEN** the detail sheet opens for an event whose artist has `artist_background` in their fanart data
- **THEN** the sheet SHALL display the background image in a hero section above the artist header with `aspect-ratio: 16/9` and `object-fit: cover`

#### Scenario: Artist has no background image
- **WHEN** the detail sheet opens for an event whose artist has no `artist_background`
- **THEN** the sheet SHALL render the existing layout without a hero section

#### Scenario: Hero image with gradient fade
- **WHEN** the hero image is displayed
- **THEN** the bottom edge of the hero section SHALL fade into the sheet background color via a gradient overlay to ensure visual continuity

### Requirement: Event detail sheet computes URLs and handles touch dismiss
The event detail sheet SHALL compute Google Maps and Calendar URLs and support touch drag-to-dismiss with a 100px threshold.

#### Scenario: Google Maps URL construction
- **WHEN** the sheet is opened with an event that has a venue name
- **THEN** `googleMapsUrl` SHALL return a valid Google Maps search URL for the venue

#### Scenario: Google Calendar URL construction
- **WHEN** the sheet is opened with an event
- **THEN** `calendarUrl` SHALL return a Google Calendar URL with correct start and end times

#### Scenario: Touch drag exceeding threshold closes sheet
- **WHEN** a touch drag moves more than 100px downward
- **THEN** the sheet SHALL close

#### Scenario: Touch drag below threshold keeps sheet open
- **WHEN** a touch drag moves less than 100px
- **THEN** the sheet SHALL remain open

### Requirement: Ticket Status UI visibility

The Ticket Status UI in the event detail sheet SHALL only be rendered when the user is authenticated. Unauthenticated (guest) users SHALL NOT see the Ticket Status section.

#### Scenario: Authenticated user sees Ticket Status section

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the Ticket Status section SHALL be visible
- **AND** the user SHALL be able to select a status (TRACKING, APPLIED, LOST, UNPAID, PAID)

#### Scenario: Unauthenticated user does not see Ticket Status section

- **WHEN** an unauthenticated (guest) user opens the concert detail sheet
- **THEN** the Ticket Status section SHALL NOT be rendered
- **AND** no RPC call to `TicketJourneyService/SetStatus` SHALL be made

### Requirement: Ticket Status UI two-phase layout

The Ticket Status control in the event detail sheet SHALL present the journey statuses in two phases instead of a flat row: a **process phase** (`TRACKING ▸ APPLIED`) and an **outcome phase**. The outcome phase SHALL stack its routes vertically with the success route (`UNPAID → PAID`, grouped under a "当選" heading) above the failure route (`LOST`).

#### Scenario: Process phase shows the pre-result sequence

- **WHEN** an authenticated user opens the concert detail sheet
- **THEN** the process phase SHALL render `TRACKING` and `APPLIED` as a horizontal segmented sequence in that order

#### Scenario: Outcome phase stacks success above failure

- **WHEN** the outcome phase is rendered
- **THEN** the success route (`UNPAID` then `PAID`) SHALL appear above the failure route (`LOST`)
- **AND** `UNPAID` and `PAID` SHALL be grouped under a single "当選" heading

### Requirement: Ticket Status cumulative progress display

The Ticket Status control SHALL derive and display the user's progress through the journey from the single stored status, using the fixed journey DAG (`TRACKING → APPLIED → {LOST | UNPAID → PAID}`). States already passed SHALL be shown as completed, the current state SHALL be the only solid-filled node, and not-yet-reached states SHALL be shown as outlined.

#### Scenario: Passed states are marked completed

- **WHEN** the current status is `PAID`
- **THEN** `TRACKING`, `APPLIED`, and `UNPAID` SHALL be displayed as completed (e.g. a check cue)
- **AND** `PAID` SHALL be displayed as the current solid-filled node

#### Scenario: Future states are outlined

- **WHEN** the current status is `APPLIED`
- **THEN** `APPLIED` SHALL be the solid-filled node
- **AND** `TRACKING` SHALL be displayed as completed
- **AND** the outcome states SHALL be displayed as not-yet-reached (outlined)

#### Scenario: Exactly one solid-filled node

- **WHEN** any status is selected
- **THEN** exactly one node SHALL be solid-filled at a time

### Requirement: Ticket Status selection contrast

The currently selected status SHALL be conveyed primarily through a solid fill versus outlined unselected states, rather than through background color intensity or opacity. The selected node SHALL remain clearly distinguishable from unselected nodes for every status value, including `LOST`.

#### Scenario: Selected LOST is clearly distinguishable

- **WHEN** the current status is `LOST`
- **THEN** the `LOST` node SHALL be solid-filled
- **AND** it SHALL be visually distinct from the unselected/outlined nodes

### Requirement: Ticket Status semantic color and non-color cues

Each status SHALL carry a meaning-based color and a non-color cue (icon plus text label) so the control is understandable without relying on color alone. `UNPAID` SHALL be the highest-attention color (amber/orange) to signal a required payment action, `PAID` SHALL use a success color (green), `LOST` SHALL use a failure color (red), and `TRACKING`/`APPLIED` SHALL use neutral/in-progress colors.

#### Scenario: UNPAID is emphasized as action-required

- **WHEN** the current status is `UNPAID`
- **THEN** the `UNPAID` node SHALL use the highest-attention (amber/orange) color
- **AND** it SHALL include a non-color action cue

#### Scenario: Meaning survives without color

- **WHEN** any status node is rendered
- **THEN** it SHALL include a text label and a non-color cue (icon) in addition to color

### Requirement: Ticket Status outcome gating

The outcome phase SHALL be visually de-emphasized (dimmed, with a "結果待ち" affordance) until the `APPLIED` state has been reached, while remaining selectable at all times. Selecting the failure route SHALL de-emphasize the success route and vice-versa.

#### Scenario: Outcome dimmed before applied

- **WHEN** the current status is `TRACKING` or `APPLIED`
- **THEN** the outcome phase SHALL be displayed dimmed with a "結果待ち" affordance
- **AND** the outcome states SHALL still be selectable

#### Scenario: Mutually exclusive routes

- **WHEN** the current status is `LOST`
- **THEN** the success route (`UNPAID`/`PAID`) SHALL be dimmed
- **AND WHEN** the current status is `UNPAID` or `PAID`
- **THEN** the failure route (`LOST`) SHALL be dimmed

#### Scenario: Any status remains settable

- **WHEN** the user taps any status node, including a dimmed one
- **THEN** the control SHALL set that status via `TicketJourneyService/SetStatus`
- **AND** the UI SHALL NOT block the selection (no enforced state machine)

### Requirement: Ticket Status radiogroup accessibility

The Ticket Status control SHALL expose single-select semantics as a `role="radiogroup"` containing `role="radio"` options with `aria-checked` reflecting the current status. Each option SHALL be an accessible, ≥44px tap target.

#### Scenario: Radiogroup semantics

- **WHEN** the Ticket Status control is rendered for an authenticated user
- **THEN** it SHALL be a `radiogroup` of `radio` options
- **AND** the option matching the current status SHALL have `aria-checked="true"`
- **AND** all other options SHALL have `aria-checked="false"`

### Requirement: Ticket Journey UI is independent of ticket sales
The Ticket Journey status UI (concert-card badge and detail-sheet status control) SHALL be available to authenticated users independently of any ticket purchase, NFT minting, ZK proof generation, or ticket sales navigation features. Hiding or removing those sales-side features SHALL NOT affect the availability of the Ticket Journey UI.

#### Scenario: Journey UI visible when ticket sales nav is hidden

- **WHEN** the Tickets bottom-nav tab is hidden (ticket sales feature not yet service-ready)
- **THEN** the journey status badge SHALL still appear on event cards for users who have a journey status
- **AND** the journey selection control SHALL still appear in the event detail sheet for authenticated users

#### Scenario: Journey UI does not depend on ticket purchase flow

- **WHEN** a user has not completed any ticket purchase or NFT minting
- **THEN** the user SHALL still be able to set and view their journey status (e.g. `tracking`, `applied`, `lost`, `unpaid`, `paid`) via the UI

### Requirement: Ticket Status saving failures and double taps

When saving or removing a journey status fails, the sheet SHALL keep showing the status the fan had before and SHALL show no error message. While a change is being saved, further status selections in the sheet SHALL be ignored.

#### Scenario: Saving fails

- **WHEN** a signed-in fan picks Paid for an event whose status is Unpaid and saving fails
- **THEN** the sheet still shows Unpaid and no error message appears

#### Scenario: Second tap while saving

- **WHEN** the fan picks Applied and, before it is saved, picks Lost
- **THEN** the second pick is ignored and the sheet shows Applied once the first change is saved

### Requirement: Leaving for the source and adding to a calendar are reported

When the fan opens the concert's source link or its add-to-calendar link from the event detail sheet, the fan app SHALL send one usage analytics event naming which link, with the event and the artist.

#### Scenario: Source link
- **WHEN** the fan taps the source link of a concert in the detail sheet
- **THEN** one event is sent naming the source link, the event and the artist

### Requirement: Adding to the calendar starts tracking

When a signed-in fan with no journey for the event chooses add to calendar in the event detail sheet, the app SHALL start tracking the event as an inference (TicketJourneyService.InferTracking) at once, and every screen SHALL show Tracking for the event once it is saved. When the fan comes back to the app after the calendar opened, or at once when the app stayed in view, the sheet SHALL show a snack that reads 「チケット状況を「追跡中」にしました。」 and 「販売の情報をお知らせします。」 on two lines (EN "Ticket status set to Tracking." / "We will tell you about ticket sales."), with the action 「取り消す」 (EN "Undo"). The snack SHALL stay 10 seconds unless the fan presses the action. Pressing it SHALL remove the journey, and no screen SHALL then show a status for the event. A guest's calendar add, a fan who already has a journey for the event, and a save that fails SHALL start nothing and show no snack.

#### Scenario: Calendar add from the sheet

- **WHEN** a signed-in fan with no journey for an event chooses add to calendar, the calendar opens, and the fan comes back to the app
- **THEN** the sheet and the Dashboard show Tracking for the event and the snack offers 「取り消す」

#### Scenario: Undo

- **WHEN** the fan presses 「取り消す」 on that snack
- **THEN** neither the sheet nor the Dashboard shows a status for the event

#### Scenario: Fan already has a journey

- **WHEN** a signed-in fan whose journey for the event is Applied chooses add to calendar
- **THEN** the journey stays Applied and no snack appears

#### Scenario: Guest

- **WHEN** a guest chooses add to calendar
- **THEN** the calendar opens, no journey is requested from the server and no snack appears

### Requirement: A hype level raised by a journey change is shown with undo

When a signed-in fan's Applied, Unpaid or Paid in the event detail sheet is saved and the app raised the fan's hype level for the concert's artist as a result, the sheet SHALL show a snack that reads 「{{name}}を {{hype}} にしました。」 and 「遠方の新着ライブも通知します。」 on two lines (EN "{{name}} is now {{hype}}." / "You will also hear about distant new concerts."), where `{{hype}}` is the invariant English tier label, with the action 「取り消す」 (EN "Undo"), and the Dashboard SHALL highlight the artist's concerts the new level matches. The snack SHALL stay 10 seconds unless the fan presses the action. Pressing it SHALL set the previous level as the fan's own choice; when that save fails, the raised level stays shown and a message says the change failed. When the level was not raised, no snack SHALL appear.

#### Scenario: Applied for a distant concert raises the level

- **WHEN** a signed-in fan whose hype for ヨルシカ is Nearby set by default saves Applied for ヨルシカ's concert in the away lane
- **THEN** the snack reads 「ヨルシカを Away にしました。」 「遠方の新着ライブも通知します。」 and the concert's card on the Dashboard is highlighted

#### Scenario: Undo the raise

- **WHEN** the fan presses 「取り消す」 on that snack
- **THEN** ヨルシカ is at Nearby, set by the fan, and the away-lane card is no longer highlighted

#### Scenario: Level not raised

- **WHEN** the fan's hype for the artist was set by the fan and the fan saves Applied
- **THEN** no snack appears
