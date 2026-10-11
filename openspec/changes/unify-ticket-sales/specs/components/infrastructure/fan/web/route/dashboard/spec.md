# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: listByFollower results are cached in memory for the session`
- TO: `### Requirement: ListFollowed results are cached in memory for the session`

- FROM: `### Requirement: listFollowed RPC provides hype data on every dashboard load`
- TO: `### Requirement: FollowService.List provides hype data on every dashboard load`

## MODIFIED Requirements

### Requirement: ListFollowed results are cached in memory for the session
The app SHALL cache the result of `ConcertService.ListFollowed` in memory for the duration of the session, using the shared caching mechanism used by other stores rather than bespoke per-store logic. The cache SHALL use a `staleTime` of 24 hours. While the cached value is within `staleTime`, the dashboard SHALL be served the cached value without issuing an RPC. In addition, the app SHALL revalidate the cached value in the background on Dashboard route entry and when the installed PWA returns to the foreground, so a long-lived session refreshes without a manual reload.

#### Scenario: Cache hit on Dashboard re-entry
- **WHEN** the user navigates to Dashboard a second time within 24 hours without having followed or unfollowed any artists
- **THEN** the cached `ConcertService.ListFollowed` result SHALL be returned immediately without blocking on an RPC
- **AND** the app SHALL revalidate the value in the background

#### Scenario: Cache miss on first load
- **WHEN** the dashboard needs the followed artists' concerts and no cached value exists
- **THEN** `ConcertService.ListFollowed` SHALL be called and the result SHALL be stored in the cache with the current timestamp

#### Scenario: Cache expiry after 24 hours
- **WHEN** the dashboard needs the followed artists' concerts more than 24 hours after the cache was last populated
- **THEN** the cached value SHALL be served immediately and `ConcertService.ListFollowed` SHALL be called in the background to refresh the cache

#### Scenario: Revalidation on PWA resume
- **WHEN** the installed PWA returns to the foreground on the Dashboard after being backgrounded
- **THEN** the app SHALL revalidate the `ConcertService.ListFollowed` result in the background
- **AND** the refreshed value SHALL replace the cached value in place without a full document reload

### Requirement: Concert cache is invalidated on follow
A successful `FollowService.Follow`, `FollowService.Unfollow` or `FollowService.SetHype` SHALL invalidate the cached `ConcertService.ListFollowed` result, so the next dashboard load fetches fresh concert data. The invalidation SHALL NOT occur when the mutation RPC fails.

#### Scenario: Cache invalidated after follow
- **WHEN** the user successfully follows or unfollows an artist, or changes an artist's hype
- **THEN** the cached `ConcertService.ListFollowed` result SHALL be invalidated
- **AND** the next dashboard load SHALL call `ConcertService.ListFollowed`

#### Scenario: Cache not invalidated on follow RPC failure
- **WHEN** the `FollowService.Follow`, `Unfollow` or `SetHype` call fails with an error
- **THEN** the cached `ConcertService.ListFollowed` result SHALL remain valid

### Requirement: FollowService.List provides hype data on every dashboard load
Every dashboard load SHALL call `FollowService.List` to retrieve per-artist hype levels, which are not stored in the in-memory list of followed artists.

#### Scenario: Follow state already in memory
- **WHEN** the dashboard loads and the in-memory list of followed artists already has entries
- **THEN** `FollowService.List` SHALL still be called to retrieve current hype levels

#### Scenario: Follow state not yet loaded
- **WHEN** the dashboard loads and the in-memory list of followed artists is empty
- **THEN** `FollowService.List` SHALL be called to populate the state and retrieve hype levels

### Requirement: Default today-onward timetable

The dashboard "My Timetable" SHALL, by default, display only concerts whose date is on or after the current local date. The "today" boundary SHALL be anchored to the client's local date, and the dashboard SHALL request the timetable by passing that date as the `from` argument to `ConcertService.ListFollowed`.

#### Scenario: Fresh load defaults to today onward

- **WHEN** the user opens `/dashboard` with no date query parameter
- **THEN** the timetable SHALL request `ConcertService.ListFollowed` with `from` set to the client's current local date
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
- **THEN** the timetable SHALL request `ConcertService.ListFollowed` with `from = <pastDate>`
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
- **AND** the timetable SHALL re-fetch via `ConcertService.ListFollowed` with `from` set to the chosen date and display the past-inclusive result

#### Scenario: Collapsing back to today onward

- **WHEN** a past date is active and the user clears the date facet (returns it to the default) and confirms
- **THEN** the date query parameter SHALL be removed from the URL
- **AND** the timetable SHALL revert to the default today-onward view

#### Scenario: Date facet combines with artist and journey facets

- **WHEN** a past `from` date is active together with an artist and/or journey filter
- **THEN** the timetable SHALL first load all followed-artist concerts on or after `from`, then narrow that set by the active artist and journey facets
- **AND** the per-artist and journey chip counts SHALL be computed over the loaded (past-inclusive) set

### Requirement: Dashboard Mode Toggle

The Dashboard SHALL provide a segment toggle control that switches between "My Timetable" mode (current behavior — concerts for followed artists) and "All Nearby" mode (new — all concerts in the DB near a given location within a date range). The toggle is what tells the fan which mode is active: the page header title SHALL remain the dashboard's title in both modes.

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
- **THEN** the Dashboard SHALL revert to the cached `ConcertService.ListFollowed` / `ConcertService.ListByArtists` result

#### Scenario: Header title does not change with the mode

- **WHEN** the user switches between My Timetable and All Nearby
- **THEN** the page header title SHALL stay the dashboard's title
- **AND** the toggle SHALL indicate the newly selected mode

### Requirement: Follow CTA in Event Detail Sheet for All Nearby

When viewing a concert in All Nearby mode, the event detail sheet SHALL surface a follow action for artists the user does not yet follow.

#### Scenario: Follow button visible for unfollowed artist

- **WHEN** the user opens the event detail sheet for a concert in All Nearby mode
- **AND** the concert's artist is not in the user's followed artists list
- **THEN** the sheet SHALL display a "Follow this artist" button

#### Scenario: Follow action from detail sheet

- **WHEN** the user taps "Follow this artist" in the event detail sheet
- **THEN** `FollowService.Follow` SHALL be called
- **AND** the button SHALL change to a "Following" indicator
- **AND** the DNA Orb absorption animation SHALL NOT play (the sheet is not the Discovery context)

#### Scenario: No follow button for already-followed artist

- **WHEN** the user opens the event detail sheet for a concert in All Nearby mode
- **AND** the concert's artist is already followed
- **THEN** the follow button SHALL NOT be displayed

#### Scenario: Follow button for unauthenticated user

- **WHEN** an unauthenticated user taps "Follow this artist" in the event detail sheet
- **THEN** the system SHALL surface the sign-up prompt banner instead of calling `FollowService.Follow`
