# Spec Delta

## MODIFIED Requirements

### Requirement: Deep-link auto-open of a concert sheet

When the timetable loads at `/timetable?concert=:id` (for example, from a tapped push notification), it SHALL automatically open the detail sheet for concert `:id` once the authoritative concert list has resolved, and SHALL derive the timetable's artist filter from that concert. The `concert` query parameter is the same one the detail sheet writes on manual open, so a deep-link and a manual card tap converge on the same URL and the same state.

The auto-open SHALL resolve the concert against the authoritative `listByFollower` fetch that the timetable already performs — NOT against a cache first-paint, and without any additional get-by-id RPC, timer, or optimistic pre-open. When the concert is absent from the resolved list (for example, the recipient unfollowed the artist after the notification was sent, or the concert carries an invalid date / unresolved performer), the timetable SHALL degrade gracefully: apply the artist filter if derivable and leave the sheet closed, never surfacing an error.

#### Scenario: Deep-link opens the concert after the authoritative fetch resolves

- **WHEN** the timetable loads at `/timetable?concert=<concertId>` and the `listByFollower` fetch resolves with a concert whose id is `<concertId>`
- **THEN** the system SHALL open that concert's detail sheet
- **AND** the sheet SHALL NOT be opened from a stale cache first-paint before the authoritative fetch resolves

#### Scenario: Deep-link derives the artist filter from the opened concert

- **WHEN** a concert sheet is auto-opened from a `/timetable?concert=:id` deep-link
- **THEN** the timetable's `filteredArtistIds` SHALL be set to `[concert.artistId]` so only that artist's concerts remain behind the sheet

#### Scenario: Closing the deep-linked sheet does not reload the timetable

- **WHEN** the fan closes a detail sheet that was auto-opened from a `/timetable?concert=:id` deep-link
- **THEN** the URL SHALL revert via `history.replaceState` without triggering router navigation
- **AND** the timetable already mounted behind the sheet SHALL be revealed without a re-fetch

#### Scenario: Target concert absent degrades to filter-only

- **WHEN** the timetable loads at `/timetable?concert=<concertId>` but the resolved `listByFollower` result contains no concert with id `<concertId>`
- **THEN** the system SHALL NOT open a detail sheet
- **AND** SHALL NOT surface an error
- **AND** SHALL apply the artist filter only when the artist is still derivable

### Requirement: URL-driven artist filter
The timetable SHALL accept an `artists` query parameter containing one or more artist IDs (comma-separated UUIDs). When present, only concerts belonging to the listed artists SHALL be displayed. When absent or empty, all followed-artist concerts SHALL be displayed as normal.

#### Scenario: Single artist filter from URL
- **WHEN** the user navigates to `/timetable?artists=<artistId>`
- **THEN** only concerts whose `artistId` matches `<artistId>` SHALL be shown in the concert highway

#### Scenario: Multiple artist filter from URL
- **WHEN** the user navigates to `/timetable?artists=<id1>,<id2>`
- **THEN** only concerts whose `artistId` is in `{id1, id2}` SHALL be shown in the concert highway

#### Scenario: No filter — unfiltered view preserved
- **WHEN** the user navigates to `/timetable` (no `artists` param)
- **THEN** all followed-artist concerts SHALL be displayed unchanged

#### Scenario: Unknown artist ID in filter
- **WHEN** an `artists` value contains an ID that does not match any followed artist
- **THEN** that ID SHALL be silently ignored; concerts for remaining valid IDs SHALL still be shown

#### Scenario: Filter yields empty result
- **WHEN** the filtered artist set has no upcoming concerts
- **THEN** the empty-state placeholder SHALL be displayed (same as the no-concerts state)

### Requirement: Filter state synchronised with URL
When the user changes the active filter via the UI, the timetable URL SHALL be updated to reflect the new filter state without triggering a full page reload.

#### Scenario: User adds an artist to the filter
- **WHEN** the user selects an artist in the filter bottom sheet and confirms
- **THEN** the browser URL SHALL update to `/timetable?artists=<selectedIds>` via `history.replaceState`
- **THEN** the concert highway SHALL immediately display only matching concerts

#### Scenario: Page reload preserves filter
- **WHEN** the user reloads the page while a filter is active
- **THEN** the `artists` query param SHALL be re-parsed from the URL
- **THEN** the same filtered view SHALL be restored

### Requirement: Push notification deep-link to filtered timetable

Tapping a new-concert push notification SHALL open the deep-linked concert's detail sheet on the timetable, with the timetable filtered to that concert's artist. The notification carries a `/timetable?concert=<concertId>` URL (see the `concert-detail` deep-link auto-open requirement). The artist filter SHALL be **derived from the opened concert** (`filteredArtistIds = [concert.artistId]`), not carried as a `?artists=` query parameter in the notification URL.

#### Scenario: Notification tap opens the concert filtered to its artist

- **WHEN** a push notification with `data.url = "/timetable?concert=<concertId>"` is tapped
- **THEN** the browser SHALL navigate to `/timetable?concert=<concertId>`
- **AND** the timetable SHALL derive the artist filter from the opened concert so only that artist's concerts remain behind the sheet

#### Scenario: Deep-link auto-open suppressed during onboarding

- **WHEN** the user is in the onboarding flow (`isOnboarding` is true)
- **THEN** the deep-link SHALL NOT auto-open a detail sheet and SHALL NOT derive an artist filter
- **AND** the manual filter trigger button SHALL remain hidden (via `if.bind="!isOnboarding"`) and any `artists` query param SHALL be ignored until onboarding is complete

### Requirement: Default today-onward timetable

The timetable "My Timetable" SHALL, by default, display only concerts whose date is on or after the current local date. The "today" boundary SHALL be anchored to the client's local date, and the timetable SHALL request the timetable by passing that date as the `from` argument to `ConcertService.ListFollowed`.

#### Scenario: Fresh load defaults to today onward

- **WHEN** the user opens `/timetable` with no date query parameter
- **THEN** the timetable SHALL request `ConcertService.ListFollowed` with `from` set to the client's current local date
- **AND** only concerts on or after today SHALL be displayed
- **AND** past concerts of followed artists SHALL NOT be displayed

#### Scenario: Empty upcoming timetable

- **WHEN** the default (today-onward) timetable contains no upcoming concerts for the user's followed artists
- **THEN** the empty-state placeholder SHALL be displayed
- **AND** the "過去のコンサートも表示" affordance SHALL remain available so the user can look back

### Requirement: URL-driven date filter

The timetable SHALL accept a date query parameter (e.g. `from`) containing a single calendar date. When present, the timetable SHALL display concerts on or after that date, including past concerts when the date precedes today. When absent, the timetable SHALL behave as the default today-onward view.

#### Scenario: Past date from URL

- **WHEN** the user navigates to `/timetable?from=<pastDate>`
- **THEN** the timetable SHALL request `ConcertService.ListFollowed` with `from = <pastDate>`
- **AND** concerts on or after `<pastDate>` (including past ones) SHALL be displayed

#### Scenario: Invalid or malformed date value

- **WHEN** the date query parameter is missing, empty, or not a valid calendar date
- **THEN** it SHALL be ignored and the default today-onward view SHALL be shown

#### Scenario: Future date from URL

- **WHEN** the date query parameter is a date after today
- **THEN** the timetable SHALL display only concerts on or after that future date

### Requirement: URL-driven journey filter
The timetable SHALL accept a `journey` query parameter containing one or more ticket-journey status values (comma-separated, from `tracking`, `applied`, `unpaid`, `paid`, `lost`). When present, only concerts whose `journeyStatus` is in the listed set SHALL be displayed. When absent or empty, concerts SHALL NOT be constrained by journey status.

#### Scenario: Single status filter from URL
- **WHEN** the user navigates to `/timetable?journey=unpaid`
- **THEN** only concerts whose `journeyStatus` is `unpaid` SHALL be shown in the concert highway

#### Scenario: Multiple status filter from URL
- **WHEN** the user navigates to `/timetable?journey=applied,unpaid`
- **THEN** only concerts whose `journeyStatus` is in `{applied, unpaid}` SHALL be shown

#### Scenario: No journey filter — unconstrained by status
- **WHEN** the user navigates to `/timetable` with no `journey` param
- **THEN** concerts SHALL NOT be filtered by journey status (concerts with no status set SHALL still be shown)

#### Scenario: Concerts without a journey status are excluded when filtering
- **WHEN** a `journey` filter is active
- **AND** the user is authenticated
- **AND** a concert has no `journeyStatus` set
- **THEN** that concert SHALL NOT be shown

#### Scenario: Unknown status value in filter
- **WHEN** a `journey` value contains a token that is not a valid status
- **THEN** that token SHALL be silently ignored; concerts for remaining valid statuses SHALL still be shown

#### Scenario: Filter yields empty result
- **WHEN** the journey filter (combined with any artist filter) has no matching upcoming concerts
- **THEN** the empty-state placeholder SHALL be displayed (same as the no-concerts state)

### Requirement: Page identity paints independent of the timetable render

On timetable tab-switch re-entry, the page identity — the shell header title and
the active bottom-nav tab — SHALL NOT be held back by an unbounded timetable
render. The re-entry render SHALL be bounded by the rendered window, so that page
identity and the restored timetable appear in the tap's next paint within the
interaction budget, whatever the number of loaded dates. Reflecting timetable
render state SHALL NOT be performed in a pre-activation route lifecycle hook.
Re-entry SHALL NOT lose the background refresh, the data-ready
celebration/onboarding latch, or an in-flight deep-link resolution.

#### Scenario: Header and nav switch before the timetable renders

- **WHEN** an authenticated fan with a populated, previously-cached timetable taps
  the timetable navigation tab from another tab
- **THEN** the header title, the active tab and the restored timetable SHALL
  appear in the tap's next paint, with the tap's Interaction to Next Paint at
  most 200 ms on the reference profile
- **AND** the render work for that interaction SHALL be bounded by the rendered
  window, not by the full set of loaded date groups

#### Scenario: Deferring the render preserves load-path side effects

- **WHEN** the re-entry cached render is reflected from the component lifecycle
- **THEN** the background refresh SHALL still fetch and swap in fresh data
- **AND** the data-ready celebration / onboarding-completion latch SHALL still
  fire once when due, and a pending `/timetable?concert=:id` deep-link SHALL still open
  the detail sheet

### Requirement: Closing the detail sheet keeps the timetable's filters in the URL

When the concert sheet closes by the sheet's own means (light dismiss or swipe down), the URL SHALL return to the timetable URL the fan was on when the sheet opened, its query parameters included and `concert` removed, so the URL always restores the timetable the fan is looking at. A sheet auto-opened from a `/timetable?concert=:id` deep-link SHALL close to the timetable URL carrying the artist filter the deep-link derived. Closing SHALL still revert the URL via `history.replaceState` without triggering router navigation, and closing by the browser back button SHALL remain the browser's own navigation.

#### Scenario: Closing keeps the active filters in the URL

- **WHEN** the detail sheet is opened while the timetable is filtered (for example `/timetable?artists=<id>`, a journey facet or a `from` date)
- **AND** the fan closes the sheet by light dismiss or swipe down
- **THEN** the URL SHALL be that same filtered timetable URL, query parameters included
- **AND** reloading that URL SHALL show the same filtered timetable the fan was looking at

#### Scenario: Closing a deep-linked sheet returns to the filtered timetable URL

- **WHEN** the fan closes a detail sheet that was auto-opened from a `/timetable?concert=:id` deep-link
- **THEN** the URL SHALL be `/timetable?artists=<concert.artistId>`, the filter the deep-link derived
- **AND** reloading that URL SHALL show the same filtered timetable

### Requirement: Concert sheet

The system SHALL provide a detail view for a selected discovered concert using a popover-based sheet (not a modal dialog), ensuring compatibility with coach mark overlays in the top layer. A first-party concert (one whose Series belongs to an Organizer) SHALL NOT open the sheet; tapping its card opens its Concert page instead (see "Timetable routes event selection and shows its loading states").

#### Scenario: Open detail from timetable

- **WHEN** a user taps a discovered concert's card on the timetable
- **THEN** the system SHALL open a bottom sheet displaying the concert detail
- **AND** the sheet SHALL be shown with `showPopover()` as a non-modal `popover="manual"` sheet, so it never blocks the page behind it and coach marks can still appear above it
- **AND** the sheet element SHALL be a `<dialog>` providing native dialog semantics (implicit `role="dialog"`)
- **AND** the URL SHALL gain `concert=<id>` next to the timetable's other query parameters (for example `/timetable?artists=<artistId>&concert=<id>`) via `history.pushState` without triggering full page navigation
- **AND** the sheet SHALL be anchored flush to the bottom edge of the viewport

#### Scenario: Display venue information

- **WHEN** the concert detail view is open
- **THEN** it SHALL display the venue name (`listed_venue_name`)
- **AND** when `venue.admin_area` is available it SHALL display the administrative area as the human-readable localized prefecture name (the mapped `locationLabel`), NOT the raw ISO 3166-2 subdivision code (e.g. it SHALL render `東京都`, never `JP-13`)
- **AND** when `venue.admin_area` is absent it SHALL omit the administrative-area line

#### Scenario: Google Maps link

- **WHEN** the concert detail view is open
- **THEN** it SHALL render a tappable link that opens Google Maps with a query composed of venue name and admin area
- **AND** the link's visible label SHALL be sourced from the `concertSheet.openInGoogleMaps` i18n key

#### Scenario: Ticket / official info link

- **WHEN** the concert detail view is open and `source_url` is present
- **THEN** it SHALL render a button linking to `source_url` in a new tab
- **AND** the button's visible label SHALL be sourced from the `concertSheet.viewOfficialInfo` i18n key

#### Scenario: Display ticket journey status

- **WHEN** the concert detail view is open
- **AND** the user has a ticket journey for this event
- **THEN** the sheet SHALL display the current ticket journey status
- **AND** the displayed status text SHALL be sourced from `concertSheet.journeyStatus.<value>` (not the raw enum string)
- **AND** the sheet SHALL provide the ticket sale notification button for Tracking (hidden while the status is Paid, as the concert sheet surface states) and the row of the other four statuses
- **AND** each control in that row SHALL have its label sourced from `concertSheet.journeyStatus.<value>`, and the notification button SHALL take its labels from `concertSheet.notify.*`

#### Scenario: Set ticket journey status from detail view

- **WHEN** the user selects a new status from the journey status controls and the change is saved
- **THEN** the displayed status SHALL update to reflect the change, on the sheet and on the Timetable as the story stories/track-ticket-journey describes

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
- **AND** the URL SHALL revert to the timetable URL via `history.replaceState`

#### Scenario: Dismiss sheet via swipe down

- **WHEN** the detail sheet is open
- **AND** the user swipes the sheet down until its body leaves the viewport
- **THEN** the sheet SHALL call `hidePopover()` and the URL SHALL revert to the timetable URL

#### Scenario: Dismiss sheet via browser back button

- **WHEN** the detail sheet is open
- **AND** the user presses the browser back button (triggering a `popstate` event)
- **THEN** the sheet SHALL close via `hidePopover()`
- **AND** the sheet SHALL NOT call `history.replaceState` (the browser has already navigated back)

### Requirement: Timetable routes event selection and shows its loading states

`timetable-route` SHALL handle event selection and loading/empty states directly. Selecting a first-party concert SHALL navigate to its Concert page (`/concerts/:id`); selecting a discovered concert SHALL open the `concert-sheet` dialog. Returning from the Concert page SHALL show the timetable at the date the fan left it on.

#### Scenario: Event selection handled by timetable
- **WHEN** a user taps a discovered concert's card in the concert list
- **THEN** `timetable-route` SHALL handle the `event-selected` custom event and open the `concert-sheet` dialog

#### Scenario: First-party concert opens its concert page
- **WHEN** a user taps the card of a concert whose Series belongs to an Organizer, in the timetable
- **THEN** the app SHALL navigate to `/concerts/<id>` and SHALL NOT open the detail sheet

#### Scenario: Back from the concert page
- **WHEN** the fan opened a Concert page from a card dated 2026-11-20 deep in the timetable and goes back
- **THEN** the timetable shows the timetable at 2026-11-20

#### Scenario: Loading and empty states
- **WHEN** the fan's concerts are still loading
- **THEN** the timetable SHALL show its loading placeholder in place of the lanes, and no empty state
- **WHEN** they have loaded and none match
- **THEN** the timetable SHALL show the empty state with a link to Discovery

### Requirement: Empty timetable offers the Concerts view

Whenever the timetable shows an empty timetable, the empty state SHALL offer, next to its link to Discovery, a second link that opens the Concerts view on Discovery (`/discovery?view=concerts`). This holds for the guest who follows no artist and for the fan whose followed artists have no concert to show.

#### Scenario: Guest with no follows
- **WHEN** a guest who follows no artist opens the timetable
- **THEN** the empty state shows the link to Discovery and a link 「ライブを探す」
- **AND** tapping 「ライブを探す」 opens Discovery on the Concerts view

#### Scenario: Followed artists with nothing to show
- **WHEN** a fan follows artists but none of them has a concert to show
- **THEN** the empty state shows the link to Discovery and the link 「ライブを探す」

#### Scenario: Timetable with concerts
- **WHEN** the timetable shows at least one concert
- **THEN** no link to the Concerts view is shown on the timetable

## ADDED Requirements

### Requirement: The screen's address

The timetable SHALL be served at `/timetable`, with its filters and the open concert sheet carried as query parameters (`artists`, `journey`, `from`, `concert`). `/dashboard` SHALL NOT be an address of the timetable; it is an unknown address like any other.

#### Scenario: The timetable's address
- **WHEN** a fan taps the Timetable tab
- **THEN** the address bar shows `/timetable`

#### Scenario: The old address is gone
- **WHEN** a fan opens `/dashboard`
- **THEN** the app shows the not-found screen
