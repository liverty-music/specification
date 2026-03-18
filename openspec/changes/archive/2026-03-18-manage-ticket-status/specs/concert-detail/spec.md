## MODIFIED Requirements

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

#### Scenario: Ticket / official info link

- **WHEN** the concert detail view is open and `source_url` is present
- **THEN** it SHALL render a "View Official Info" button linking to `source_url` in a new tab

#### Scenario: Display ticket journey status

- **WHEN** the concert detail view is open
- **AND** the user has a ticket journey for this event
- **THEN** the sheet SHALL display the current ticket journey status
- **AND** the sheet SHALL provide controls to change the status to any valid `TicketJourneyStatus` value

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
