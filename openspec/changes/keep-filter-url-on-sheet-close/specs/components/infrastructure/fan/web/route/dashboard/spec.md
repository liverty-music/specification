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

#### Scenario: Dismiss sheet via light dismiss (non-onboarding)

- **WHEN** the user is NOT in onboarding Step 4
- **AND** the user clicks outside the sheet or presses Escape
- **THEN** the sheet SHALL be dismissed via the Popover API's native light dismiss behavior
- **AND** the URL SHALL revert via `history.replaceState` to the dashboard URL the fan was on when the sheet opened

#### Scenario: Dismiss sheet via swipe down (non-onboarding)

- **WHEN** the user is NOT in onboarding Step 4
- **AND** the user swipes down on any part of the sheet surface beyond the dismiss threshold
- **THEN** the sheet SHALL call `hidePopover()` and the URL SHALL revert to the dashboard URL the fan was on when the sheet opened

#### Scenario: Closing keeps the active filters in the URL

- **WHEN** the detail sheet is opened while the dashboard is filtered (for example `/dashboard?artists=<id>`, a journey facet or a `from` date)
- **AND** the fan closes the sheet by light dismiss, swipe down or the sheet's own close control
- **THEN** the URL SHALL be that same filtered dashboard URL, query parameters included
- **AND** reloading that URL SHALL show the same filtered timetable the fan was looking at

#### Scenario: Dismiss sheet via browser back button

- **WHEN** the detail sheet is open
- **AND** the user presses the browser back button (triggering a `popstate` event)
- **THEN** the sheet SHALL close via `hidePopover()`
- **AND** the sheet SHALL NOT call `history.replaceState` (the browser has already navigated back)

#### Scenario: Sheet non-dismissible during onboarding Step 4

- **WHEN** the user is at onboarding Step 4
- **THEN** the sheet SHALL NOT be dismissible (no swipe-down, no outside tap, no escape key)
- **AND** the coach mark overlay SHALL appear above the sheet in the top layer, targeting `[data-nav-my-artists]`

### Requirement: Deep-link auto-open of a concert detail sheet

When the dashboard loads at the `/concerts/:id` route (for example, from a tapped push notification), it SHALL automatically open the detail sheet for concert `:id` once the authoritative concert list has resolved, and SHALL derive the dashboard's artist filter from that concert. This reuses the existing `/concerts/:id` URL that the detail sheet already writes on manual open, so a deep-link and a manual card tap converge on the same URL and the same state.

The auto-open SHALL resolve the concert against the authoritative `listByFollower` fetch that the dashboard already performs — NOT against a cache first-paint, and without any additional get-by-id RPC, timer, or optimistic pre-open. When the concert is absent from the resolved list (for example, the recipient unfollowed the artist after the notification was sent, or the concert carries an invalid date / unresolved performer), the dashboard SHALL degrade gracefully: apply the artist filter if derivable and leave the sheet closed, never surfacing an error.

#### Scenario: Deep-link opens the concert after the authoritative fetch resolves

- **WHEN** the dashboard loads at `/concerts/<concertId>` and the `listByFollower` fetch resolves with a concert whose id is `<concertId>`
- **THEN** the system SHALL open that concert's detail sheet
- **AND** the sheet SHALL NOT be opened from a stale cache first-paint before the authoritative fetch resolves

#### Scenario: Deep-link derives the artist filter from the opened concert

- **WHEN** a concert detail sheet is auto-opened from a `/concerts/:id` deep-link
- **THEN** the dashboard's `filteredArtistIds` SHALL be set to `[concert.artistId]` so only that artist's concerts remain behind the sheet

#### Scenario: Closing the deep-linked sheet does not reload the dashboard

- **WHEN** the fan closes a detail sheet that was auto-opened from a `/concerts/:id` deep-link
- **THEN** the URL SHALL revert via `history.replaceState` without triggering router navigation, to the dashboard URL carrying the derived artist filter (`/dashboard?artists=<concert.artistId>`)
- **AND** the dashboard already mounted behind the sheet SHALL be revealed without a re-fetch
- **AND** reloading that URL SHALL show the same filtered timetable

#### Scenario: Target concert absent degrades to filter-only

- **WHEN** the dashboard loads at `/concerts/<concertId>` but the resolved `listByFollower` result contains no concert with id `<concertId>`
- **THEN** the system SHALL NOT open a detail sheet
- **AND** SHALL NOT surface an error
- **AND** SHALL apply the artist filter only when the artist is still derivable
