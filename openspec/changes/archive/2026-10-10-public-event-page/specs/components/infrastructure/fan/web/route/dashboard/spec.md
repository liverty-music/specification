# Spec Delta

## ADDED Requirements

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

- **WHEN** the user removes the journey status from the detail view controls and the removal is saved
- **THEN** the status display SHALL revert to the untracked state
- **AND** the remove control's label SHALL be sourced from the `eventDetail.stopTracking` i18n key

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

### Requirement: Dashboard routes event selection and shows its loading states

`dashboard-route` SHALL handle event selection and loading/empty states directly. Selecting a first-party concert SHALL navigate to its Event page (`/events/:id`); selecting a discovered concert SHALL open the `event-detail-sheet` dialog. Returning from the Event page SHALL show the timetable at the date the fan left it on.

#### Scenario: Event selection handled by dashboard
- **WHEN** a user taps a discovered concert's card in the concert list
- **THEN** `dashboard-route` SHALL handle the `event-selected` custom event and open the `event-detail-sheet` dialog

#### Scenario: First-party concert opens its event page
- **WHEN** a user taps the card of a concert whose Series belongs to an Organizer, in the timetable or the All Nearby list
- **THEN** the app SHALL navigate to `/events/<id>` and SHALL NOT open the detail sheet

#### Scenario: Back from the event page
- **WHEN** the fan opened an Event page from a card dated 2026-11-20 deep in the timetable and goes back
- **THEN** the dashboard shows the timetable at 2026-11-20

#### Scenario: Loading and empty states
- **WHEN** the fan's concerts are still loading
- **THEN** the timetable SHALL show its loading placeholder in place of the lanes, and no empty state
- **WHEN** they have loaded and none match
- **THEN** the dashboard SHALL show the empty state with a link to Discovery

## MODIFIED Requirements

### Requirement: Concert cards show the fan's journey status

Each discovered concert's card on the Dashboard SHALL show a badge with the fan's ticket journey status for that concert, and no badge when the fan has none. Each first-party concert's card SHALL instead show a purchased badge when the signed-in fan holds at least one Issued Ticket for it, and no badge otherwise; the fan's journey status is not shown on a first-party card. A guest sees no badges, as the story stories/track-ticket-journey states. When the fan's journey statuses or tickets cannot be loaded, the Dashboard SHALL still show the concerts, without the badges that depend on them and without an error message.

#### Scenario: Tracked concert

- **WHEN** a signed-in fan's journey for a discovered concert is Applied
- **THEN** that concert's card shows the Applied badge

#### Scenario: Concert without a journey

- **WHEN** the fan has no journey for a discovered concert
- **THEN** that concert's card shows no badge

#### Scenario: Statuses cannot be loaded

- **WHEN** the concerts load but the fan's journey statuses fail to load
- **THEN** the concerts are shown without badges and no error is shown

#### Scenario: Purchased first-party concert

- **WHEN** a signed-in fan holds 2 Issued Tickets for a first-party concert
- **THEN** that concert's card shows the purchased badge and no journey badge

#### Scenario: First-party concert not purchased

- **WHEN** a signed-in fan has set a journey status for a first-party concert but holds no Issued Ticket for it
- **THEN** that concert's card shows no badge

## REMOVED Requirements

### Requirement: Concert Detail View
**Reason**: Restated as "Concert detail sheet". The sheet is a non-modal `popover="manual"` sheet in every context (never `popover="auto"`), and the onboarding Step 4 non-dismissible sheet no longer exists since onboarding moved to the single-flag model.
**Migration**: None. "Concert detail sheet" carries every scenario still true, with the dismiss scenarios restated without the removed onboarding step.

### Requirement: Dashboard handles event selection directly
**Reason**: Restated as "Dashboard routes event selection and shows its loading states". The dashboard no longer uses `promise.bind` (removed in frontend `e358b1a`); the timetable owns its loading placeholder and the route shows the empty state.
**Migration**: None. The event-selection scenarios carry over unchanged, and the loading scenario describes the current placeholder and empty state.
