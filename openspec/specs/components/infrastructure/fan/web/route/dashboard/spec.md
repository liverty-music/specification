# Dashboard

## Purpose

Presents a fan's personalized view of upcoming concerts for followed artists, with filtering by artist, date, and ticket-journey status synchronized to the URL, concert detail views, cached data loading with stale-data handling, and a broader all-nearby browsing mode.

## Requirements

### Requirement: Stale-data warning uses overlay pattern
The dashboard stale-data warning SHALL render as a fixed-position overlay, consistent with the application's notification pattern (`toast-notification`, `error-banner`).

#### Scenario: Stale banner appears as fixed overlay
- **WHEN** the dashboard data reload fails and previous data exists (`isStale === true`)
- **THEN** the stale-data warning SHALL render as a `position: fixed` element at the top of the viewport
- **AND** the warning SHALL NOT occupy a grid row in the dashboard layout
- **AND** the warning SHALL appear above page content but below top-layer elements (dialogs, popovers)

#### Scenario: Stale banner does not affect scroll behavior
- **WHEN** the stale-data warning is visible
- **THEN** the `live-highway` scroll area SHALL occupy the full `main` grid area
- **AND** scrolling the concert list SHALL NOT move the stale-data warning

---

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

### Requirement: Compact journey-status control layout

The concert detail sheet's ticket-journey status control SHALL render in a compact layout whose outcome phase is arranged horizontally in a single row, so the control's vertical footprint is roughly half of a vertically stacked outcome layout. The control SHALL preserve every journey status node, the radiogroup semantics, keyboard navigation, and the canonical per-status label, icon, and hue.

#### Scenario: Outcome routes arranged horizontally

- **WHEN** the ticket-journey status control is displayed
- **THEN** the win route nodes (`unpaid`, `paid`) and the lose route node (`lost`) SHALL be arranged horizontally in a single row rather than as vertically stacked bordered cards
- **AND** the win-route nodes SHALL be connected by the horizontal `›` flow connector (not a vertical `↓` connector)
- **AND** the win route and lose route SHALL remain visually distinguishable via a separator and their per-status hues

#### Scenario: All status nodes and behavior preserved

- **WHEN** the compact layout is rendered
- **THEN** all five status nodes (`tracking`, `applied`, `unpaid`, `paid`, `lost`) SHALL still be present and selectable
- **AND** each node SHALL retain a tap target of at least 44px
- **AND** the radiogroup role, keyboard navigation, and `data-testid` hooks SHALL be unchanged
- **AND** each node's label, icon, and hue SHALL still be sourced from the canonical journey-status presentation map

#### Scenario: Flow connector is not cramped

- **WHEN** a flow connector (`›`) is rendered between two status nodes in either the process phase or the outcome phase
- **THEN** the connector SHALL have dedicated inline spacing on both sides independent of the container gap
- **AND** the connector glyph SHALL be rendered at a size that is legible rather than hairline

#### Scenario: Narrow viewport does not overflow

- **WHEN** the control is displayed on a narrow mobile viewport where the outcome row cannot fit on one line
- **THEN** the outcome row SHALL wrap rather than overflow horizontally
- **AND** the control's vertical footprint SHALL remain smaller than the prior vertically stacked outcome layout

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
- **THEN** the URL SHALL revert via `history.replaceState` without triggering router navigation
- **AND** the dashboard already mounted behind the sheet SHALL be revealed without a re-fetch

#### Scenario: Target concert absent degrades to filter-only

- **WHEN** the dashboard loads at `/concerts/<concertId>` but the resolved `listByFollower` result contains no concert with id `<concertId>`
- **THEN** the system SHALL NOT open a detail sheet
- **AND** SHALL NOT surface an error
- **AND** SHALL apply the artist filter only when the artist is still derivable

### Requirement: URL-driven artist filter
The dashboard SHALL accept an `artists` query parameter containing one or more artist IDs (comma-separated UUIDs). When present, only concerts belonging to the listed artists SHALL be displayed. When absent or empty, all followed-artist concerts SHALL be displayed as normal.

#### Scenario: Single artist filter from URL
- **WHEN** the user navigates to `/dashboard?artists=<artistId>`
- **THEN** only concerts whose `artistId` matches `<artistId>` SHALL be shown in the concert highway

#### Scenario: Multiple artist filter from URL
- **WHEN** the user navigates to `/dashboard?artists=<id1>,<id2>`
- **THEN** only concerts whose `artistId` is in `{id1, id2}` SHALL be shown in the concert highway

#### Scenario: No filter — unfiltered view preserved
- **WHEN** the user navigates to `/dashboard` (no `artists` param)
- **THEN** all followed-artist concerts SHALL be displayed unchanged

#### Scenario: Unknown artist ID in filter
- **WHEN** an `artists` value contains an ID that does not match any followed artist
- **THEN** that ID SHALL be silently ignored; concerts for remaining valid IDs SHALL still be shown

#### Scenario: Filter yields empty result
- **WHEN** the filtered artist set has no upcoming concerts
- **THEN** the empty-state placeholder SHALL be displayed (same as the no-concerts state)

### Requirement: Filter state synchronised with URL
When the user changes the active filter via the UI, the dashboard URL SHALL be updated to reflect the new filter state without triggering a full page reload.

#### Scenario: User adds an artist to the filter
- **WHEN** the user selects an artist in the filter bottom sheet and confirms
- **THEN** the browser URL SHALL update to `/dashboard?artists=<selectedIds>` via `history.replaceState`
- **THEN** the concert highway SHALL immediately display only matching concerts

#### Scenario: Page reload preserves filter
- **WHEN** the user reloads the page while a filter is active
- **THEN** the `artists` query param SHALL be re-parsed from the URL
- **THEN** the same filtered view SHALL be restored

### Requirement: Push notification deep-link to filtered dashboard

Tapping a new-concert push notification SHALL open the deep-linked concert's detail sheet on the dashboard, with the dashboard filtered to that concert's artist. The notification carries a `/concerts/<concertId>` URL (see the `concert-detail` deep-link auto-open requirement). The artist filter SHALL be **derived from the opened concert** (`filteredArtistIds = [concert.artistId]`), not carried as a `?artists=` query parameter in the notification URL.

#### Scenario: Notification tap opens the concert filtered to its artist

- **WHEN** a push notification with `data.url = "/concerts/<concertId>"` is tapped
- **THEN** the browser SHALL navigate to `/concerts/<concertId>`
- **AND** the dashboard SHALL derive the artist filter from the opened concert so only that artist's concerts remain behind the sheet

#### Scenario: Deep-link auto-open suppressed during onboarding

- **WHEN** the user is in the onboarding flow (`isOnboarding` is true)
- **THEN** the deep-link SHALL NOT auto-open a detail sheet and SHALL NOT derive an artist filter
- **AND** the manual filter trigger button SHALL remain hidden (via `if.bind="!isOnboarding"`) and any `artists` query param SHALL be ignored until onboarding is complete

### Requirement: Filter availability for guest users

The filter SHALL be available to unauthenticated (guest) users, who can follow
artists locally, via the FAB action launcher's filter item and the artist facet in
the sheet. The filter SHALL NOT be gated by authentication; only the onboarding flow
suppresses it (the filter item is not contributed to the launcher during onboarding).

#### Scenario: Guest sees the filter trigger and artist facet

- **WHEN** an unauthenticated (guest) user who has followed at least one artist views the dashboard outside of onboarding
- **THEN** the FAB action launcher SHALL include the filter item
- **AND** activating it SHALL present the artist facet with that guest's followed artists

#### Scenario: Filter still suppressed during onboarding

- **WHEN** the user (guest or authenticated) is in the onboarding flow
- **THEN** the filter item SHALL NOT be contributed to the launcher

### Requirement: listByFollower results are cached in memory for the session
The concert list store SHALL cache the result of `listByFollower()` in memory for the duration of the session, using the shared caching mechanism used by other stores rather than bespoke per-store logic. The cache SHALL use a `staleTime` of 24 hours. While the cached value is within `staleTime`, subsequent calls to `listByFollower()` SHALL return the cached value without issuing an RPC. In addition, the store SHALL revalidate the cached value in the background on Dashboard route entry and when the installed PWA returns to the foreground, so a long-lived session refreshes without a manual reload.

#### Scenario: Cache hit on Dashboard re-entry
- **WHEN** the user navigates to Dashboard a second time within 24 hours without having followed or unfollowed any artists
- **THEN** `listByFollower()` SHALL return the cached result immediately without blocking on an RPC
- **AND** the store SHALL revalidate the value in the background

#### Scenario: Cache miss on first load
- **WHEN** `listByFollower()` is called and no cached value exists
- **THEN** the RPC SHALL be issued and the result SHALL be stored in the cache with the current timestamp

#### Scenario: Cache expiry after 24 hours
- **WHEN** `listByFollower()` is called more than 24 hours after the cache was last populated
- **THEN** the cached value SHALL be served immediately and the RPC SHALL be issued in the background to refresh the cache

#### Scenario: Revalidation on PWA resume
- **WHEN** the installed PWA returns to the foreground on the Dashboard after being backgrounded
- **THEN** the store SHALL revalidate `listByFollower()` in the background
- **AND** the refreshed value SHALL replace the cached value in place without a full document reload

### Requirement: Concert cache is invalidated on follow
`ConcertServiceClient` SHALL invalidate the follower-scoped concert cache, and `FollowServiceClient`'s `follow()`, `unfollow()`, and `setHype()` methods SHALL trigger that invalidation after the RPC succeeds, so the next dashboard load fetches fresh concert data. The invalidation SHALL NOT occur when the mutation RPC fails.

#### Scenario: Cache invalidated after follow
- **WHEN** the user successfully follows or unfollows an artist, or changes an artist's hype
- **THEN** the `listByFollower()` cache SHALL be invalidated
- **AND** the next call to `listByFollower()` SHALL issue an RPC

#### Scenario: Cache not invalidated on follow RPC failure
- **WHEN** the `follow()`/`unfollow()`/`setHype()` RPC call fails with an error
- **THEN** the `listByFollower()` cache SHALL remain valid

### Requirement: listFollowed RPC provides hype data on every dashboard load
`FollowServiceClient.getFollowedArtistMap()` SHALL call `listFollowed()` on every invocation to retrieve per-artist hype levels, which are not stored in the in-memory list of followed artists.

#### Scenario: Follow state already in memory
- **WHEN** `getFollowedArtistMap()` is called and the in-memory list of followed artists already has entries
- **THEN** `listFollowed()` SHALL still be called to retrieve current hype levels

#### Scenario: Follow state not yet loaded
- **WHEN** `getFollowedArtistMap()` is called and the in-memory list of followed artists is empty
- **THEN** `listFollowed()` SHALL be called to populate the state and retrieve hype levels

### Requirement: All Nearby mode uses ListByLocation

The Dashboard concert cache SHALL support an "All Nearby" mode that calls `ConcertService.ListByLocation` and caches its result separately from the My Timetable result.

#### Scenario: All Nearby result cached independently

- **WHEN** the user switches to All Nearby mode and `ListByLocation` returns a result
- **THEN** the result SHALL be stored in route-local state separate from the My Timetable cache
- **AND** switching back to My Timetable and then to All Nearby again SHALL reuse the cached All Nearby result if the location and date range have not changed

#### Scenario: Cache invalidated on filter change

- **WHEN** the user changes the area or date preset in All Nearby mode
- **THEN** the All Nearby cache SHALL be invalidated
- **AND** `ListByLocation` SHALL be called again with the new parameters

#### Scenario: My Timetable cache unaffected by All Nearby mode

- **WHEN** the user switches between My Timetable and All Nearby mode
- **THEN** the My Timetable concert cache SHALL remain intact
- **AND** switching back to My Timetable SHALL display the previously loaded result without an additional network call

### Requirement: Default today-onward timetable

The dashboard "My Timetable" SHALL, by default, display only concerts whose date is on or after the current local date. The "today" boundary SHALL be anchored to the client's local date, and the dashboard SHALL request the timetable by passing that date as the `from` argument to `ListByFollower`.

#### Scenario: Fresh load defaults to today onward

- **WHEN** the user opens `/dashboard` with no date query parameter
- **THEN** the timetable SHALL request `ListByFollower` with `from` set to the client's current local date
- **AND** only concerts on or after today SHALL be displayed
- **AND** past concerts of followed artists SHALL NOT be displayed

#### Scenario: Empty upcoming timetable

- **WHEN** the default (today-onward) timetable contains no upcoming concerts for the user's followed artists
- **THEN** the empty-state placeholder SHALL be displayed
- **AND** the "過去のコンサートも表示" affordance SHALL remain available so the user can look back

### Requirement: URL-driven date filter

The dashboard SHALL accept a date query parameter (e.g. `from`) containing a single calendar date. When present, the timetable SHALL display concerts on or after that date, including past concerts when the date precedes today. When absent, the timetable SHALL behave as the default today-onward view.

#### Scenario: Past date from URL

- **WHEN** the user navigates to `/dashboard?from=<pastDate>`
- **THEN** the timetable SHALL request `ListByFollower` with `from = <pastDate>`
- **AND** concerts on or after `<pastDate>` (including past ones) SHALL be displayed

#### Scenario: Invalid or malformed date value

- **WHEN** the date query parameter is missing, empty, or not a valid calendar date
- **THEN** it SHALL be ignored and the default today-onward view SHALL be shown

#### Scenario: Future date from URL

- **WHEN** the date query parameter is a date after today
- **THEN** the timetable SHALL display only concerts on or after that future date

### Requirement: Date facet in the filter bottom sheet

The filter bottom sheet SHALL include a date facet presented as a collapsed affordance labelled "過去のコンサートも表示". Expanding it SHALL reveal a single date field labelled "この日付以降を表示" for choosing the earliest date to display. The facet SHALL coexist with the existing artist and journey facets in the same sheet and be committed by the same confirm action.

#### Scenario: Expanding the date facet

- **WHEN** the user taps "過去のコンサートも表示" in the filter bottom sheet
- **THEN** a single date field ("この日付以降を表示") SHALL be revealed
- **AND** the field SHALL default to the currently active `from` date (today when the default view is active)

#### Scenario: Choosing a past date and confirming

- **WHEN** the user picks a date earlier than today in the date field and taps confirm
- **THEN** the bottom sheet SHALL close
- **AND** the dashboard URL SHALL update to carry the chosen date without a full page reload
- **AND** the timetable SHALL re-fetch via `ListByFollower` with `from` set to the chosen date and display the past-inclusive result

#### Scenario: Collapsing back to today onward

- **WHEN** a past date is active and the user clears the date facet (returns it to the default) and confirms
- **THEN** the date query parameter SHALL be removed from the URL
- **AND** the timetable SHALL revert to the default today-onward view

#### Scenario: Date facet combines with artist and journey facets

- **WHEN** a past `from` date is active together with an artist and/or journey filter
- **THEN** the timetable SHALL first load all followed-artist concerts on or after `from`, then narrow that set by the active artist and journey facets
- **AND** the per-artist and journey chip counts SHALL be computed over the loaded (past-inclusive) set

### Requirement: Date filter state persistence

The active date filter SHALL survive a page reload and be shareable via the URL, consistent with the existing artist and journey filters.

#### Scenario: Reload preserves the date filter

- **WHEN** the user reloads the page while a past `from` date is active
- **THEN** the date query parameter SHALL be re-parsed from the URL
- **AND** the same past-inclusive timetable SHALL be restored

### Requirement: URL-driven journey filter
The dashboard SHALL accept a `journey` query parameter containing one or more ticket-journey status values (comma-separated, from `tracking`, `applied`, `unpaid`, `paid`, `lost`). When present, only concerts whose `journeyStatus` is in the listed set SHALL be displayed. When absent or empty, concerts SHALL NOT be constrained by journey status.

#### Scenario: Single status filter from URL
- **WHEN** the user navigates to `/dashboard?journey=unpaid`
- **THEN** only concerts whose `journeyStatus` is `unpaid` SHALL be shown in the concert highway

#### Scenario: Multiple status filter from URL
- **WHEN** the user navigates to `/dashboard?journey=applied,unpaid`
- **THEN** only concerts whose `journeyStatus` is in `{applied, unpaid}` SHALL be shown

#### Scenario: No journey filter — unconstrained by status
- **WHEN** the user navigates to `/dashboard` with no `journey` param
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

### Requirement: Journey filter combines with artist filter
When both the artist filter and the journey filter are active, a concert SHALL be shown only if it satisfies BOTH facets. Selections within a single facet SHALL combine as OR; the two facets SHALL combine as AND.

#### Scenario: Both facets active
- **WHEN** the artist filter is `{A, B}` and the journey filter is `{applied, unpaid}`
- **THEN** a concert SHALL be shown only if its `artistId` is in `{A, B}` AND its `journeyStatus` is in `{applied, unpaid}`

#### Scenario: Only journey facet active
- **WHEN** the artist filter is empty and the journey filter is `{paid}`
- **THEN** all followed-artist concerts whose `journeyStatus` is `paid` SHALL be shown regardless of artist

#### Scenario: Only artist facet active
- **WHEN** the journey filter is empty and the artist filter is `{A}`
- **THEN** all of artist A's concerts SHALL be shown regardless of journey status

### Requirement: Journey filter state synchronised with URL
When the user changes the journey filter via the UI, the dashboard URL SHALL be updated to reflect the new state without a full page reload, and the artist and journey parameters SHALL be written together in a single URL update.

#### Scenario: User changes the journey filter
- **WHEN** the user selects journey statuses in the filter sheet and confirms
- **THEN** the browser URL SHALL update to include `journey=<selectedStatuses>` via `history.replaceState`
- **AND** the concert highway SHALL immediately display only matching concerts

#### Scenario: A single URL update writes both facets
- **WHEN** a confirm commits changes to both the artist and journey selections
- **THEN** the URL SHALL be updated exactly once with both `artists` and `journey` parameters reflecting the final state

#### Scenario: Page reload preserves the journey filter
- **WHEN** the user reloads the page while a journey filter is active
- **THEN** the `journey` query param SHALL be re-parsed from the URL and the same filtered view SHALL be restored

### Requirement: Dashboard service groups concerts by date
The `DashboardService.loadDashboardEvents` method SHALL fetch followed artists, retrieve concerts for each artist in parallel, convert them to `LiveEvent` objects, and group them by date.

#### Scenario: Multiple artists with concerts
- **WHEN** the user follows 2 artists and each has concerts on different dates
- **THEN** the returned `DateGroup[]` SHALL contain entries sorted by date, each containing the corresponding `LiveEvent` objects

#### Scenario: No followed artists
- **WHEN** the user follows no artists
- **THEN** `loadDashboardEvents` SHALL return an empty `DateGroup[]`

#### Scenario: RPC call failure for one artist
- **WHEN** concert fetching fails for one artist but succeeds for another
- **THEN** the service SHALL return events from the successful artist (using `Promise.allSettled` resilience)

### Requirement: Dashboard route manages stale data on reload failure
The `Dashboard` route SHALL preserve existing data and mark it as stale when a data reload fails.

#### Scenario: Successful data load
- **WHEN** `loadData` succeeds
- **THEN** `groupedEvents` SHALL contain the returned date groups and `isStale` SHALL be `false`

#### Scenario: Reload failure preserves old data
- **WHEN** `loadData` fails after a previous successful load
- **THEN** `groupedEvents` SHALL retain the previous data and `isStale` SHALL be `true`

#### Scenario: AbortError is ignored
- **WHEN** `loadData` throws an AbortError (navigation-triggered)
- **THEN** the error SHALL NOT be set on the component

#### Scenario: Retry clears error and reloads
- **WHEN** `retry` is called
- **THEN** the error state SHALL be cleared and `loadData` SHALL be invoked again

### Requirement: Layout-preserving skeleton loading

While first-load content is pending, screens SHALL display a skeleton placeholder that preserves the final
layout, replacing bare "loading" text or a centered spinner for content regions. The skeleton SHALL be
removed when content resolves, and SHALL not introduce layout shift when replaced by real content.

#### Scenario: Content region shows a skeleton while loading

- **WHEN** a screen (e.g. the dashboard) is loading its primary content
- **THEN** it renders a skeleton matching the content's layout instead of a text-only loading state

#### Scenario: No layout shift on resolve

- **WHEN** the content finishes loading and replaces the skeleton
- **THEN** the surrounding layout does not jump (no cumulative layout shift attributable to the swap)

#### Scenario: Skeleton animation respects reduced motion

- **WHEN** `prefers-reduced-motion: reduce` is set
- **THEN** the skeleton shows a static placeholder without a shimmer animation

### Requirement: Journey-Status Presentation

The frontend SHALL define a single canonical mapping from each ticket-journey
status to its display label, icon, and semantic hue token; every component
that renders a journey status SHALL derive its label, icon, and hue from this
map rather than defining them inline. The map SHALL include an entry for each
of `tracking`, `applied`, `unpaid`, `paid`, and `lost`, each providing a label
(via the existing `eventDetail.journeyStatus.*` i18n key), an icon, and a hue
token: icons SHALL be `tracking` 👀, `applied` 📝, `unpaid` 💰, `paid` 🎟️,
`lost` 💔; hues SHALL be the shared journey-hue token for that status —
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
- **THEN** its icon SHALL be: `tracking` 👀, `applied` 📝, `unpaid` 💰, `paid` 🎟️, `lost` 💔

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

### Requirement: Data-ready side effects gate on observed data arrival
Side effects that must only run once a route's data is genuinely present (e.g. the Dashboard post-signup/guest celebration and the onboarding-completion latch) SHALL be triggered by observing the arrival of that data via Aurelia reactivity (`@watch`/`@observable`), NOT by relying on the router having awaited the fetch before `attached()`.

#### Scenario: Celebration fires only once the timetable is real
- **WHEN** the Dashboard loads data non-blocking and the data arrives after the view has attached
- **THEN** the celebration decision SHALL be evaluated when the loaded data is observed to be present
- **AND** the celebration SHALL NOT be presented over a still-loading (spinner) timetable

#### Scenario: Completion latch waits for engagement data
- **WHEN** the onboarding-completion latch condition depends on loaded follow/engagement data
- **THEN** the latch SHALL be evaluated upon observed arrival of that data
- **AND** it SHALL NOT short-circuit on not-yet-loaded state when the route attaches

### Requirement: Dashboard Mode Toggle

The Dashboard SHALL provide a segment toggle control that switches between "My Timetable" mode (current behavior — concerts for followed artists) and "All Nearby" mode (new — all concerts in the DB near a given location within a date range).

#### Scenario: Default mode is My Timetable

- **WHEN** the Dashboard loads or the page is reloaded
- **THEN** the active mode SHALL default to "My Timetable"
- **AND** the toggle SHALL visually indicate My Timetable as the selected mode

#### Scenario: Mode-specific filters appear only in All Nearby

- **WHEN** the user switches to "All Nearby" mode
- **THEN** a date-preset selector and an area selector SHALL appear below the toggle
- **WHEN** the user switches back to "My Timetable" mode
- **THEN** the date-preset selector and area selector SHALL be hidden

#### Scenario: Switching modes replaces the concert list

- **WHEN** the user switches from My Timetable to All Nearby
- **THEN** the Dashboard SHALL call `ConcertService.ListByLocation` with the current location and date range
- **AND** the resulting `ProximityGroup[]` SHALL replace the concert list
- **WHEN** the user switches back to My Timetable
- **THEN** the Dashboard SHALL revert to the cached `ListByFollower` / `ListByArtists` result

---

### Requirement: Date Preset Selector

The All Nearby mode SHALL expose its date filter as a single date chip that opens one date-range bottom sheet. The sheet SHALL offer three quick presets (今週末, 7日以内, 30日以内) and a directly-editable custom range (start/end date fields), so a custom range is adjusted without any intermediate menu or drill-down. There is no standalone "カスタム" preset chip; custom selection is simply editing the date fields.

#### Scenario: Date chip opens the range sheet in one tap

- **WHEN** the user taps the date chip
- **THEN** a date-range bottom sheet SHALL open containing both the quick presets and editable start/end date fields

#### Scenario: Available quick presets

- **WHEN** the date-range sheet is displayed
- **THEN** it SHALL offer exactly three quick presets: 今週末, 7日以内, 30日以内
- **AND** it SHALL provide directly-editable start (開始) and end (終了) date fields for a custom range

#### Scenario: 今週末 preset date range

- **WHEN** the user selects 今週末
- **AND** today is Monday through Friday
- **THEN** `from` SHALL be set to the next Saturday and `to` to the next Sunday

#### Scenario: 今週末 when today is Saturday or Sunday

- **WHEN** the user selects 今週末
- **AND** today is Saturday
- **THEN** `from` SHALL be today and `to` SHALL be the next day (Sunday)
- **WHEN** the user selects 今週末
- **AND** today is Sunday
- **THEN** `from` and `to` SHALL both be today

#### Scenario: 7日以内 preset date range

- **WHEN** the user selects 7日以内
- **THEN** `from` SHALL be today and `to` SHALL be today + 6 days (inclusive 7-day window)

#### Scenario: 30日以内 preset date range

- **WHEN** the user selects 30日以内
- **THEN** `from` SHALL be today and `to` SHALL be today + 29 days (inclusive 30-day window)

#### Scenario: Quick preset applies and closes in one tap

- **WHEN** the user taps a quick preset in the sheet
- **THEN** the corresponding range SHALL be applied and the sheet SHALL close without a further confirmation tap

#### Scenario: Custom range is edited then applied

- **WHEN** the user edits the start and/or end date fields in the sheet
- **THEN** the sheet SHALL remain open for adjustment
- **AND** an apply action SHALL confirm the edited range and close the sheet

#### Scenario: Custom range validation

- **WHEN** the user edits the custom date fields
- **THEN** the UI SHALL prevent `to` from being earlier than `from`
- **AND** the UI SHALL prevent the inclusive range from exceeding 30 days
- **AND** an inline hint SHALL communicate an invalid range and block applying it

### Requirement: Area Selector in All Nearby Mode

The All Nearby mode SHALL present the current reference area as an **area chip** in the single-row filter bar, and allow the user to override it for the duration of the session by opening the shared `user-home-selector` from that chip.

#### Scenario: Default area is user home

- **WHEN** All Nearby mode activates for an authenticated user who has set a home area
- **THEN** the area chip SHALL display the user's home area name (prefecture display name)
- **AND** the `GeoLocation` passed to `ListByLocation` SHALL use `user.home.centroid.latitude`, `user.home.centroid.longitude`, and `user.home.level_1` as `admin_area` (`centroid` is the nested `Coordinates` sub-message on the `Home` proto; `centroid_latitude`/`centroid_longitude` are reserved field names)

#### Scenario: Area override via UserHomeSelector

- **WHEN** the user taps the area chip
- **THEN** the `user-home-selector` component SHALL open
- **AND** on selection, the route SHALL update its local area state with the new ISO 3166-2 code
- **AND** `ListByLocation` SHALL be called with the new area's centroid coordinates and admin_area
- **AND** the new area SHALL NOT be saved to the user's account

#### Scenario: Area override is session-scoped

- **WHEN** the user reloads the page or navigates away and returns
- **THEN** the area chip SHALL reset to the user's persisted home area
- **AND** any previous session override SHALL be discarded

#### Scenario: Area override for unauthenticated user

- **WHEN** an unauthenticated user opens All Nearby mode
- **AND** no guest home is stored in localStorage
- **THEN** the area chip SHALL prompt the user to choose an area
- **AND** the chosen area SHALL be used for the session without persisting to localStorage

### Requirement: All Nearby Concert List

The All Nearby mode SHALL display concerts returned by `ConcertService.ListByLocation` using the existing concert timetable with HOME and NEARBY lanes.

#### Scenario: HOME and NEARBY lanes rendered

- **WHEN** `ListByLocation` returns proximity groups
- **THEN** the concert timetable SHALL render HOME-tier concerts in the HOME lane and NEARBY-tier concerts in the NEARBY lane
- **AND** AWAY-tier concerts SHALL NOT be displayed

#### Scenario: Venue name shown for all lanes

- **WHEN** a concert card is rendered in the All Nearby list
- **THEN** the venue name (listed or resolved) SHALL be shown regardless of the lane (HOME or NEARBY)
- **AND** this overrides the current Dashboard behavior where HOME-lane cards suppress the venue label

#### Scenario: Empty state

- **WHEN** `ListByLocation` returns an empty group list
- **THEN** the Dashboard SHALL display an empty-state message explaining that no concerts were found for the selected area and date range
- **AND** the empty state SHALL include a link or button navigating to the Discovery tab

### Requirement: Follow CTA in Event Detail Sheet for All Nearby

When viewing a concert in All Nearby mode, the event detail sheet SHALL surface a follow action for artists the user does not yet follow.

#### Scenario: Follow button visible for unfollowed artist

- **WHEN** the user opens the event detail sheet for a concert in All Nearby mode
- **AND** the concert's artist is not in the user's followed artists list
- **THEN** the sheet SHALL display a "Follow this artist" button

#### Scenario: Follow action from detail sheet

- **WHEN** the user taps "Follow this artist" in the event detail sheet
- **THEN** `ArtistService.Follow` SHALL be called
- **AND** the button SHALL change to a "Following" indicator
- **AND** the DNA Orb absorption animation SHALL NOT play (the sheet is not the Discovery context)

#### Scenario: No follow button for already-followed artist

- **WHEN** the user opens the event detail sheet for a concert in All Nearby mode
- **AND** the concert's artist is already followed
- **THEN** the follow button SHALL NOT be displayed

#### Scenario: Follow button for unauthenticated user

- **WHEN** an unauthenticated user taps "Follow this artist" in the event detail sheet
- **THEN** the system SHALL surface the sign-up prompt banner instead of calling `ArtistService.Follow`

### Requirement: Compact All Nearby Filter Bar

The All Nearby mode SHALL present its filters as a single, fixed-height row of two chips — an area chip and a date chip — such that selecting or adjusting any filter never changes the height of the filter area and therefore never reduces the concert timetable's height.

#### Scenario: Filter bar is a single row of two chips

- **WHEN** All Nearby mode is active
- **THEN** the filter area SHALL render exactly two controls on one row: an area chip and a date chip
- **AND** neither chip SHALL expand the filter area inline when tapped

#### Scenario: Timetable height is unaffected by filter interaction

- **WHEN** the user opens the area sheet, opens the date sheet, or changes any filter
- **THEN** the height of the concert timetable SHALL NOT decrease as a result
- **AND** all complex input SHALL occur in a bottom sheet overlay rather than inline expansion

### Requirement: Localized All Nearby Date Display

Every user-facing date and date-range in the All Nearby filter SHALL be formatted for the Japanese locale via `Intl.DateTimeFormat('ja-JP')`; the browser's native `MM/DD/YYYY` input rendering SHALL NOT be the primary display of the selected range.

#### Scenario: Date chip shows a localized range

- **WHEN** a custom range from 2026-08-12 to 2026-08-20 is applied
- **THEN** the date chip SHALL display the localized range `8/12〜8/20`

#### Scenario: Single-day range

- **WHEN** the applied range has `from` equal to `to`
- **THEN** the date chip SHALL display that single localized date (e.g. `8/10`) rather than a `〜`-joined pair

#### Scenario: Preset shows its name

- **WHEN** a quick preset (今週末 / 7日以内 / 30日以内) is applied
- **THEN** the date chip SHALL display that preset's name rather than a raw date range

### Requirement: Natural Japanese Copy for All Nearby

All user-facing Japanese strings on the All Nearby surface SHALL read as natural, native Japanese; machine-translated or awkward phrasing SHALL be corrected. Japanese and English i18n keys SHALL remain at parity.

#### Scenario: All Nearby strings are natural Japanese

- **WHEN** the All Nearby mode title, mode toggle labels, area prompt, empty-state text, date-preset labels, and range hint are displayed in Japanese
- **THEN** each SHALL be phrased in natural Japanese
- **AND** every `allNearby.*` key present in the Japanese bundle SHALL also exist in the English bundle (and vice versa)

### Requirement: Dashboard uses semantic HTML structure
The dashboard route SHALL use semantic HTML elements instead of generic `<div>` elements for its concert timeline layout.

#### Scenario: Date groups rendered as ordered list
- **WHEN** the dashboard displays concert date groups
- **THEN** date groups SHALL be rendered as `<ol>` with `<li>` elements
- **AND** date labels SHALL use `<time>` elements

#### Scenario: Stage lanes rendered as list items
- **WHEN** a date group renders its 3-lane concert grid
- **THEN** the lane grid SHALL be an `<ol>` element with 3 `<li>` children (home, near, away)

#### Scenario: Empty lanes display placeholder via CSS
- **WHEN** a lane contains no concert events
- **THEN** the lane SHALL display a dash placeholder using CSS `:empty` pseudo-element (or `[data-empty]` attribute fallback)
- **AND** no conditional template markup SHALL be used for the empty state

### Requirement: Dashboard handles event selection directly

`dashboard-route` SHALL handle event selection and loading/empty states directly.

#### Scenario: Event selection handled by dashboard
- **WHEN** a user taps an event card in the concert list
- **THEN** `dashboard-route` SHALL handle the `event-selected` custom event and open the `event-detail-sheet` dialog

#### Scenario: Loading and empty states managed by promise.bind
- **WHEN** concert data is loading or empty
- **THEN** the dashboard's `promise.bind` directive SHALL manage pending/then/catch states directly

### Requirement: Signup Banner on Dashboard

The Dashboard page SHALL display a persistent fixed banner above the bottom navigation bar prompting unauthenticated users to sign up.

#### Scenario: Banner appears on dashboard for unauthenticated users

- **WHEN** an unauthenticated user views the Dashboard
- **AND** the user has completed onboarding (onboardingStep >= 7) or has dismissed the notification dialog
- **THEN** the system SHALL display the signup-prompt-banner

#### Scenario: Banner not shown during onboarding steps 1-4

- **WHEN** the user is at onboarding steps 1 through 4
- **THEN** the dashboard signup banner SHALL NOT be rendered

#### Scenario: Banner not shown for authenticated users on dashboard

- **WHEN** an authenticated user views the Dashboard
- **THEN** the signup banner SHALL NOT be rendered

### Requirement: Dashboard auth guard for journey fetch

The Dashboard SHALL NOT call authenticated RPC endpoints when the user is unauthenticated.

#### Scenario: Journey data skipped for unauthenticated users

- **WHEN** an unauthenticated user views the Dashboard
- **THEN** the system SHALL NOT call `TicketJourneyService/ListByUser`
- **AND** the system SHALL use an empty journey map as fallback
- **AND** no 401 errors SHALL appear in the browser console

#### Scenario: Journey data fetched for authenticated users

- **WHEN** an authenticated user views the Dashboard
- **THEN** the system SHALL call `TicketJourneyService/ListByUser` to populate ticket journey statuses

### Requirement: Timetable rendering cost is bounded and must not dominate the main thread

Displaying the dashboard timetable — on first navigation and on tab-switch
re-entry — MUST NOT be dominated by browser Layout and Style-recalculation work,
and MUST NOT style or lay out off-screen content. Rendering cost is dominated by
Layout and Recalculate Style, not by network or backend latency, so this contract
constrains main-thread rendering only; the backend/RPC path is out of scope.

Measurements are taken on the reference profile — a mid-tier mobile device (e.g.
Pixel 8) or a desktop emulating it with 4× CPU throttling — against a recorded
pre-change baseline, so the contract reflects real fan devices.

The "good" Core Web Vitals thresholds (LCP ≤ 2.5 s, INP ≤ 200 ms) are the
capability's target END STATE, reached cumulatively across this and any follow-up
rendering work. A single change satisfies this requirement by delivering a
substantial, measured reduction toward that end state — not necessarily the
absolute thresholds in one step.

#### Scenario: Tab-switch re-entry does not freeze on rendering

- **WHEN** an authenticated fan with a populated timetable taps the dashboard
  navigation tab from another tab
- **THEN** the tap's Interaction to Next Paint (INP), measured on the reference
  profile, is substantially lower than the recorded pre-change baseline, and the
  Layout + Recalculate Style self-time for the interaction no longer dominates the
  main-thread cost
- **AND** the timetable content appears without a multi-second blank/skeleton gap

#### Scenario: First dashboard load render cost is reduced

- **WHEN** an authenticated fan with a populated timetable loads the dashboard
- **THEN** Largest Contentful Paint (LCP) on the reference profile is substantially
  lower than the recorded baseline, with its render-delay (main-thread) portion no
  longer dominated by Layout + Recalculate Style

#### Scenario: Off-screen timetable content is not styled or laid out eagerly

- **WHEN** the timetable contains more concert cards than fit in the viewport
- **THEN** style and layout work for cards outside the viewport does not contribute
  to the entry/re-entry main-thread cost

#### Scenario: Viewport-scoping off-screen content does not regress sticky headers or shift layout

- **WHEN** a fan scrolls across multiple date groups whose off-screen content is
  viewport-scoped (skipped when off-screen)
- **THEN** the date separator's sticky behavior is intentional and consistent
  across groups (either it persists at the top or it hands off at each group
  boundary — not a mix), and no cumulative layout shift is introduced (CLS stays 0)
  as groups scroll in and out

### Requirement: Highlighted card visuals must not drive continuous rendering work

A concert card's visual treatment MUST NOT force the browser to recompute style or
layout on every animation frame while the timetable is idle. This applies in
particular to highlighted (hype-matched) cards, whose emphasis effect must not run
a perpetual per-frame style/paint invalidation.

#### Scenario: Idle timetable does no continuous rendering work

- **WHEN** the dashboard timetable is displayed and the fan is not interacting with
  it
- **THEN** over a 3-second idle capture on the reference profile, the Recalculate
  Style and Layout self-time attributable to card visuals is negligible (no ongoing
  per-frame recalculation)

#### Scenario: Reduced motion is respected

- **WHEN** the fan's system requests reduced motion (`prefers-reduced-motion:
  reduce`)
- **THEN** the timetable presents cards without animated motion

### Requirement: The timetable frame paints without data

The dashboard timetable's data-independent structure — the stage header naming
the lanes, and the lane columns themselves — SHALL be painted as soon as the
route's view attaches, before any concert data is available. While data is
pending the view SHALL present a placeholder shaped like the timetable, and it
SHALL NOT present an empty state. An empty state SHALL be shown only once a load
has settled and genuinely returned no concerts; it SHALL NOT be derived from the
rendered group count alone, which cannot distinguish "not yet assigned" from
"genuinely zero".

#### Scenario: Frame appears before any concert data

- **WHEN** a fan navigates to the dashboard and the concert data has not arrived
- **THEN** the stage header and lane columns SHALL be visible
- **AND** a timetable-shaped loading placeholder SHALL occupy the lanes
- **AND** neither the "no concerts" empty state nor the guest empty state SHALL
  be rendered

#### Scenario: Empty state waits for a settled load

- **WHEN** a load settles and returns zero concerts
- **THEN** the empty state SHALL be rendered
- **AND** it SHALL NOT have appeared at any earlier point during that load

### Requirement: Timetable rendering is scoped to the viewport

Rendering work for the timetable SHALL be bounded by what the fan can see: date
groups outside the viewport SHALL skip style, layout and paint work, and SHALL be
rendered as they are scrolled into view. Lane alignment with the stage header
SHALL be preserved for every group, in both the three-lane and the collapsed
two-lane (All Nearby) presentations. The scroll extent SHALL remain stable enough
that scrolling does not jump and that a restored scroll position lands within one
card of where the fan left.

#### Scenario: Off-screen dates are not rendered

- **WHEN** a populated timetable is displayed
- **THEN** date groups outside the viewport SHALL NOT incur style, layout or
  paint work
- **AND** scrolling toward them SHALL render them in time to be seen

#### Scenario: Lanes stay aligned under viewport scoping

- **WHEN** any date group is rendered, on screen or newly scrolled into view
- **THEN** its lane columns SHALL align with the stage header's columns
- **AND** this SHALL hold in both the three-lane and the two-lane presentations

### Requirement: Re-entry restores the date the fan was looking at

On re-entry to a timetable the fan has already seen, the cached content SHALL be
restored showing the same date group the fan left it on, at any scroll depth.

The position SHALL be remembered as the date it identifies, not as a pixel
offset. Under viewport-scoped rendering an off-screen group's height is an
estimate until it renders, and the browser's memory of each real height does not
outlive the elements — which navigation destroys — so a pixel offset taken
before the trip denotes a different place after it, increasingly so with depth.

Restoring SHALL happen once the content is rendered: before that the anchored
group does not exist and the restore is silently lost. A date that is no longer
in the list SHALL leave the fan where they are rather than resolve to a
substitute.

#### Scenario: Re-entry restores the same date, at any depth

- **WHEN** a fan scrolls deep into the timetable, navigates to another tab, and
  returns
- **THEN** the timetable SHALL show the same date group it showed when they left
- **AND** this SHALL hold as far down the timetable as the content goes, not only
  near the top

#### Scenario: The anchored date is gone

- **WHEN** the timetable is restored but a background refresh has dropped the
  date the fan left it on
- **THEN** the view SHALL stay where it is rather than scroll to a substitute
  date

### Requirement: Page identity paints independent of the timetable render

On dashboard tab-switch re-entry, the page identity — the shell header title and
the active bottom-nav tab — SHALL NOT be held hostage to the timetable's render.
The re-entry render SHALL be bounded by what is visible, so that page identity
and timetable arrive together within an interaction budget rather than the shell
waiting on an unbounded render. Reflecting timetable render state SHALL NOT be
performed in a pre-activation route lifecycle hook. Re-entry SHALL NOT lose the
background refresh, the data-ready celebration/onboarding latch, or an in-flight
deep-link resolution.

#### Scenario: Header and nav switch before the timetable renders

- **WHEN** an authenticated fan with a populated, previously-cached timetable taps
  the dashboard navigation tab from another tab
- **THEN** the tap's Interaction to Next Paint SHALL be substantially lower than
  the pre-change baseline
- **AND** the render work for that interaction SHALL be bounded by the visible
  portion of the timetable, not by the full set of loaded date groups

#### Scenario: Deferring the render preserves load-path side effects

- **WHEN** the re-entry cached render is reflected from the component lifecycle
- **THEN** the background refresh SHALL still fetch and swap in fresh data
- **AND** the data-ready celebration / onboarding-completion latch SHALL still
  fire once when due, and a pending `/concerts/:id` deep-link SHALL still open
  the detail sheet
