# concert-detail Specification

## Purpose

The Concert Detail capability provides users with a rich detail view for a selected concert, including venue information, time, and entry points for ticket purchase. It also defines the logic for assigning concerts to dashboard lanes based on the user's stored region preference.

## Requirements

### Requirement: Concert Detail View

The system SHALL provide a detail view for a selected concert using a popover-based sheet (not a modal dialog), ensuring compatibility with coach mark overlays in the top layer.

#### Scenario: Open detail from dashboard

- **WHEN** a user taps a concert card on the dashboard
- **THEN** the system SHALL open a bottom sheet displaying the concert detail
- **AND** the sheet SHALL use `popover="auto"` with `showPopover()` by default
- **AND** the sheet element SHALL be a `<dialog>` providing native dialog semantics (implicit `role="dialog"`)
- **AND** the URL SHALL update to `/concerts/:id` via `history.pushState` without triggering full page navigation
- **AND** the sheet SHALL be anchored flush to the bottom edge of the viewport

#### Scenario: Open detail during onboarding Step 4

- **WHEN** a user taps a concert card during onboarding Step 3 (advancing to Step 4)
- **THEN** the sheet SHALL use `popover="manual"` with `showPopover()` (non-dismissible per onboarding spec)
- **AND** the popover attribute SHALL be set to `"manual"` before calling `showPopover()`

#### Scenario: Display venue information

- **WHEN** the concert detail view is open
- **THEN** it SHALL display the venue name (`listed_venue_name`) and administrative area (`venue.admin_area`) if available

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

- **WHEN** the user selects a new status from the journey status controls
- **THEN** the system SHALL call `TicketJourneyService.SetStatus` with the event_id and selected status
- **AND** the displayed status SHALL update to reflect the change

#### Scenario: Start tracking from detail view

- **WHEN** the concert detail view is open
- **AND** the user has no ticket journey for this event
- **THEN** the sheet SHALL provide a control to begin tracking (set initial status)

#### Scenario: Remove ticket journey from detail view

- **WHEN** the user removes the journey status from the detail view controls
- **THEN** the system SHALL call `TicketJourneyService.Delete` with the event_id
- **AND** the status display SHALL revert to the untracked state
- **AND** the remove control's label SHALL be sourced from the `eventDetail.stopTracking` i18n key

#### Scenario: Dismiss sheet via light dismiss (non-onboarding)

- **WHEN** the user is NOT in onboarding Step 4
- **AND** the user clicks outside the sheet or presses Escape
- **THEN** the sheet SHALL be dismissed via the Popover API's native light dismiss behavior
- **AND** the URL SHALL revert to the dashboard URL via `history.replaceState`

#### Scenario: Dismiss sheet via swipe down (non-onboarding)

- **WHEN** the user is NOT in onboarding Step 4
- **AND** the user swipes down on any part of the sheet surface beyond the dismiss threshold
- **THEN** the sheet SHALL call `hidePopover()` and the URL SHALL revert to the dashboard URL

#### Scenario: Dismiss sheet via browser back button

- **WHEN** the detail sheet is open
- **AND** the user presses the browser back button (triggering a `popstate` event)
- **THEN** the sheet SHALL close via `hidePopover()`
- **AND** the sheet SHALL NOT call `history.replaceState` (the browser has already navigated back)

#### Scenario: Sheet non-dismissible during onboarding Step 4

- **WHEN** the user is at onboarding Step 4
- **THEN** the sheet SHALL NOT be dismissible (no swipe-down, no outside tap, no escape key)
- **AND** the coach mark overlay SHALL appear above the sheet in the top layer, targeting `[data-nav-my-artists]`

### Requirement: Localized Concert Detail Sheet Copy

The frontend SHALL render all user-facing text in the concert detail sheet via i18n keys under a dedicated `eventDetail.*` namespace, with parallel JA and EN translations in `frontend/src/locales/<locale>/translation.json`. No literal English (or any other language) text SHALL be embedded directly in the `event-detail-sheet.html` template.

#### Scenario: Static labels are i18n-keyed

- **WHEN** the concert detail sheet renders any static label (date/time row prefix, action button text, ticket-status section heading, removal button)
- **THEN** the label SHALL be sourced from an `eventDetail.*` i18n key
- **AND** the JA and EN translation files SHALL both contain a value for that key
- **AND** the displayed string SHALL match the locale resolved by `@aurelia/i18n`

#### Scenario: Required i18n keys

- **WHEN** the concert detail sheet is implemented
- **THEN** the following `eventDetail.*` keys SHALL be defined in both JA and EN translation files:
  - `eventDetail.ariaLabel` — the sheet's `aria-label`
  - `eventDetail.openStart` — the open/start time line with `{{open}}` and `{{start}}` interpolation placeholders. When the open time is unknown, the `{{open}}` slot SHALL be filled with the em-dash character `—` (U+2014) supplied directly by the component (locale-invariant; not routed through an i18n key).
  - `eventDetail.openInGoogleMaps` — the Google Maps link label
  - `eventDetail.ticketStatus` — the ticket-status section heading
  - `eventDetail.stopTracking` — the "remove ticket journey" button label
  - `eventDetail.viewOfficialInfo` — the official info link label
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

### Requirement: Dashboard Lane Assignment

The system SHALL assign concerts to one of three lanes — My City, My Region, Others — based on the concert's `venue.admin_area` relative to the user's stored region preference.

#### Scenario: Concert in user's city/prefecture

- **WHEN** a concert's `venue.admin_area` matches the user's stored region exactly
- **THEN** the concert SHALL be placed in the `main` (My City) lane

#### Scenario: Concert in a different prefecture

- **WHEN** a concert's `venue.admin_area` does not match the user's stored region
- **THEN** the concert SHALL be placed in the `other` lane

#### Scenario: Venue admin area not available

- **WHEN** a concert has no `venue.admin_area`
- **THEN** the concert SHALL be placed in the `other` lane
