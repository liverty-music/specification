## MODIFIED Requirements

### Requirement: Localized Concert Detail Sheet Copy

The frontend SHALL render all user-facing text in the concert detail sheet via i18n keys under a dedicated `eventDetail.*` namespace, with parallel JA and EN translations in `frontend/src/locales/<locale>/translation.json`. No literal English (or any other language) text SHALL be embedded directly in the `event-detail-sheet.html` template.

#### Scenario: Static labels are i18n-keyed

- **WHEN** the concert detail sheet renders any static label (date/time row prefix, action button text, ticket section heading, notification button)
- **THEN** the label SHALL be sourced from an `eventDetail.*` i18n key
- **AND** the JA and EN translation files SHALL both contain a value for that key
- **AND** the displayed string SHALL match the locale resolved by `@aurelia/i18n`

#### Scenario: Required i18n keys

- **WHEN** the concert detail sheet is implemented
- **THEN** the following `eventDetail.*` keys SHALL be defined in both JA and EN translation files:
  - `eventDetail.ariaLabel` — the sheet's `aria-label`
  - `eventDetail.openStart` — the open/start time line with `{{open}}` and `{{start}}` interpolation placeholders. When the open time is unknown, the `{{open}}` slot SHALL be filled with the em-dash character `—` (U+2014) supplied directly by the component (locale-invariant; not routed through an i18n key).
  - `eventDetail.openInGoogleMaps` — the Google Maps link label
  - `eventDetail.ticketSection` — the ticket section heading (「チケット」)
  - `eventDetail.notify.start`, `eventDetail.notify.next`, `eventDetail.notify.active` — the three labels of the ticket sale notification button
  - `eventDetail.pushLine.*` — the push line of each status, in its push-on and push-off forms, and the guest's line
  - `eventDetail.outOfRange.*` — the out-of-range notice, its buttons and its line after widening
  - `eventDetail.viewOfficialInfo` — the official site button label (「公式サイトでチケットを見る」)
  - `eventDetail.addToCalendar` — the add-to-calendar link label

#### Scenario: Journey status enum values are i18n-keyed

- **WHEN** the concert detail sheet renders a `TicketJourneyStatus` value as a button label or as the currently-displayed status
- **THEN** the surface form SHALL be sourced from a sub-namespace `eventDetail.journeyStatus.<value>` rather than the raw enum string
- **AND** the JA and EN translation files SHALL both contain values for every supported `TicketJourneyStatus` value (currently `tracking`, `applied`, `lost`, `unpaid`, `paid`)
- **AND** the raw enum string SHALL NOT appear in the rendered UI

#### Scenario: Adding a new TicketJourneyStatus value

- **WHEN** a new value is added to the `TicketJourneyStatus` type
- **THEN** the change SHALL add a corresponding `eventDetail.journeyStatus.<newValue>` entry to both the JA and EN translation files
- **AND** the absence of either locale value SHALL be a defect

### Requirement: Journey-Status Presentation

The frontend SHALL define a single canonical mapping from each ticket-journey
status to its display label, icon, and semantic hue token; every component
that renders a journey status SHALL derive its label, icon, and hue from this
map rather than defining them inline. The map SHALL include an entry for each
of `tracking`, `applied`, `unpaid`, `paid`, and `lost`, each providing a label
(via the existing `eventDetail.journeyStatus.*` i18n key), an icon, and a hue
token: icons SHALL be `tracking` 🔔, `applied` 📝, `unpaid` 💰, `paid` 🎟️,
`lost` 💔 (🔔 because Tracking is the fan's request for ticket sale
notifications, and 👀 already marks the Watch hype level, which pushes nothing); hues SHALL be the shared journey-hue token for that status —
process (`tracking`, `applied`) neutral, `unpaid` amber, `paid` green, `lost`
red. The icon is the primary, always-present cue and SHALL be sufficient to
distinguish the status on its own; the text label and the hue MAY both be
omitted on compact surfaces (such as the concert-card badge) where the icon
alone carries the status. Where a text label is shown, it SHALL be sourced
from the canonical `eventDetail.journeyStatus.*` i18n key. A journey status
rendered as an emoji without a visible text label SHALL carry a role that
permits an accessible name (e.g. `role="img"`) together with the canonical
label as that name (e.g. via `aria-label`); the canonical label SHALL NOT be
exposed via `aria-label` on a bare element with an implicit `generic` role,
since user agents do not reliably announce a name on such elements. A given
journey status SHALL render with a consistent identity wherever it appears —
the dashboard filter chips, the concert-card journey badge, and the
concert-detail status control: the icon SHALL be the same across all
surfaces, and the hue and visible text label SHALL appear on the filter chips
and the detail control (both MAY be omitted on the concert-card badge, which
renders the icon alone).

#### Scenario: Single source of truth
- **WHEN** a journey status needs a label, icon, or hue in any component
- **THEN** the value SHALL be read from the canonical map
- **AND** no component SHALL inline its own per-status label, icon, or hue

#### Scenario: Map covers every status
- **WHEN** the canonical map is defined
- **THEN** it SHALL include an entry for each of `tracking`, `applied`, `unpaid`, `paid`, and `lost`
- **AND** each entry SHALL provide a label (via the existing `eventDetail.journeyStatus.*` i18n key), an icon, and a hue token

#### Scenario: Icon per status
- **WHEN** a journey status is rendered
- **THEN** its icon SHALL be: `tracking` 🔔, `applied` 📝, `unpaid` 💰, `paid` 🎟️, `lost` 💔

#### Scenario: Hue per status
- **WHEN** a journey status is rendered with a colour treatment (filter chip or detail-control node)
- **THEN** its hue SHALL be the shared journey-hue token for that status: process (`tracking`, `applied`) neutral, `unpaid` amber, `paid` green, `lost` red

#### Scenario: Meaning survives without colour
- **WHEN** any journey status is rendered
- **THEN** it SHALL present its icon, so the status is distinguishable without relying on colour alone
- **AND** where a text label is shown, the label SHALL be sourced from the canonical `eventDetail.journeyStatus.*` i18n key

#### Scenario: Icon-only rendering retains an accessible name
- **WHEN** a journey status is rendered as an emoji without a visible text label
- **THEN** the rendering element SHALL carry a role that permits an accessible name (e.g. `role="img"`) together with the canonical label as that name (e.g. via `aria-label`), so assistive technology announces the status
- **AND** the canonical label SHALL NOT be exposed via `aria-label` on a bare element with an implicit `generic` role (a naming-prohibited role), since user agents do not reliably announce a name on such elements

#### Scenario: Same status looks the same everywhere
- **WHEN** the same journey status appears as a filter chip, a card badge, and a detail-control node
- **THEN** all three SHALL show the same icon sourced from the canonical map
- **AND** the filter chip and the detail-control node SHALL show the same text label and hue sourced from the canonical map
- **AND** the card badge MAY show the icon alone, without the text label or hue background

### Requirement: Concert detail sheet

The system SHALL provide a detail view for a selected discovered concert using a popover-based sheet (not a modal dialog), ensuring compatibility with coach mark overlays in the top layer. A first-party concert (one whose Series belongs to an Organizer) SHALL NOT open the sheet; tapping its card opens its Event page instead (see "Dashboard routes event selection and shows its loading states").

#### Scenario: Open detail from dashboard

- **WHEN** a user taps a discovered concert's card on the dashboard
- **THEN** the system SHALL open a bottom sheet displaying the concert detail
- **AND** the sheet SHALL be shown with `showPopover()` as a non-modal `popover="manual"` sheet, so it never blocks the page behind it and coach marks can still appear above it
- **AND** the sheet element SHALL be a `<dialog>` providing native dialog semantics (implicit `role="dialog"`)
- **AND** the URL SHALL update to `/concerts/:id` via `history.pushState` without triggering full page navigation
- **AND** the sheet SHALL be anchored flush to the bottom edge of the viewport

#### Scenario: Display venue information

- **WHEN** the concert detail view is open
- **THEN** it SHALL display the venue name (`listed_venue_name`)
- **AND** when `venue.admin_area` is available it SHALL display the administrative area as the human-readable localized prefecture name (the mapped `locationLabel`), NOT the raw ISO 3166-2 subdivision code (e.g. it SHALL render `東京都`, never `JP-13`)
- **AND** when `venue.admin_area` is absent it SHALL omit the administrative-area line

#### Scenario: Google Maps link

- **WHEN** the concert detail view is open
- **THEN** it SHALL render a tappable link that opens Google Maps with a query composed of venue name and admin area
- **AND** the link's visible label SHALL be sourced from the `eventDetail.openInGoogleMaps` i18n key

#### Scenario: Ticket / official info link

- **WHEN** the concert detail view is open and `source_url` is present
- **THEN** it SHALL render a button linking to `source_url` in a new tab
- **AND** the button's visible label SHALL be sourced from the `eventDetail.viewOfficialInfo` i18n key

#### Scenario: Display ticket journey status

- **WHEN** the concert detail view is open
- **AND** the user has a ticket journey for this event
- **THEN** the sheet SHALL display the current ticket journey status
- **AND** the displayed status text SHALL be sourced from `eventDetail.journeyStatus.<value>` (not the raw enum string)
- **AND** the sheet SHALL provide controls to change the status to any valid `TicketJourneyStatus` value
- **AND** each control's label SHALL also be sourced from `eventDetail.journeyStatus.<value>`

#### Scenario: Set ticket journey status from detail view

- **WHEN** the user selects a new status from the journey status controls and the change is saved
- **THEN** the displayed status SHALL update to reflect the change, on the sheet and on the Dashboard as the story stories/track-ticket-journey describes

#### Scenario: Start tracking from detail view

- **WHEN** the concert detail view is open
- **AND** the user has no ticket journey for this event
- **THEN** the sheet SHALL provide a control to begin tracking (set initial status)

#### Scenario: Remove ticket journey from detail view

- **WHEN** the user presses the selected status button (or the notification button while it reads 「…受け取り中 ✓」) and the removal is saved
- **THEN** the status display SHALL revert to the untracked state
- **AND** the sheet SHALL show no separate control for removing the status

#### Scenario: Dismiss sheet by tapping outside it or pressing Escape

- **WHEN** the detail sheet is open
- **AND** the user taps the dimmed area above the sheet or presses Escape
- **THEN** the sheet SHALL close
- **AND** the URL SHALL revert to the dashboard URL via `history.replaceState`

#### Scenario: Dismiss sheet via swipe down

- **WHEN** the detail sheet is open
- **AND** the user swipes the sheet down until its body leaves the viewport
- **THEN** the sheet SHALL call `hidePopover()` and the URL SHALL revert to the dashboard URL

#### Scenario: Dismiss sheet via browser back button

- **WHEN** the detail sheet is open
- **AND** the user presses the browser back button (triggering a `popstate` event)
- **THEN** the sheet SHALL close via `hidePopover()`
- **AND** the sheet SHALL NOT call `history.replaceState` (the browser has already navigated back)

## REMOVED Requirements

### Requirement: Compact journey-status control layout

**Reason**: Replaced by "The ticket section shows the four statuses in one row": Tracking moved out of the row into the ticket sale notification button, and the process and outcome phases are gone.
**Migration**: None.

## ADDED Requirements

### Requirement: The ticket section shows the four statuses in one row

The concert detail sheet's ticket section SHALL show the ticket sale notification button on its own full-width row and the other four statuses as one row of compact buttons in journey order, 📝 申込済み › 💰 当選・未入金 › 🎟️ 入金済み, followed by 💔 落選 set apart by a separator. The row SHALL keep every status's canonical label, icon and hue, wrap rather than overflow on a narrow screen, and give each button a tap target of at least 44px.

#### Scenario: One row for four statuses

- **WHEN** the ticket section is displayed for a signed-in fan on a 390px-wide screen
- **THEN** the four status buttons are laid out in one row in journey order, with 落選 after a separator
- **AND** the `›` connectors sit between 申込済み, 当選・未入金 and 入金済み

#### Scenario: Narrow viewport does not overflow

- **WHEN** the row cannot fit on one line
- **THEN** the row wraps rather than overflowing horizontally

#### Scenario: Canonical presentation kept

- **WHEN** any status button is rendered
- **THEN** its label, icon and hue come from the canonical journey-status presentation map, and its tap target is at least 44px
