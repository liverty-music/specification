## ADDED Requirements

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

The All Nearby mode SHALL provide four date presets for filtering the concert date range.

#### Scenario: Available presets

- **WHEN** the date-preset selector is displayed
- **THEN** it SHALL offer exactly four options: 今週末, 7日以内, 30日以内, カスタム

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

#### Scenario: カスタム preset shows date inputs

- **WHEN** the user selects カスタム
- **THEN** two date input fields SHALL appear for explicit `from` and `to` selection
- **AND** the UI SHALL prevent `to` from being set earlier than `from`
- **AND** the UI SHALL prevent the range from exceeding 30 days

---

### Requirement: Area Selector in All Nearby Mode

The All Nearby mode SHALL display the current reference area and allow the user to override it for the duration of the session.

#### Scenario: Default area is user home

- **WHEN** All Nearby mode activates for an authenticated user who has set a home area
- **THEN** the area selector SHALL display the user's home area name (prefecture display name)
- **AND** the `GeoLocation` passed to `ListByLocation` SHALL use `user.home.centroid.latitude`, `user.home.centroid.longitude`, and `user.home.level_1` as `admin_area` (`centroid` is the nested `Coordinates` sub-message on the `Home` proto; `centroid_latitude`/`centroid_longitude` are reserved field names)

#### Scenario: Area override via UserHomeSelector

- **WHEN** the user taps the area selector
- **THEN** the `user-home-selector` component SHALL open
- **AND** on selection, the route SHALL update its local area state with the new ISO 3166-2 code
- **AND** `ListByLocation` SHALL be called with the new area's centroid coordinates and admin_area
- **AND** the new area SHALL NOT be saved to the user's account

#### Scenario: Area override is session-scoped

- **WHEN** the user reloads the page or navigates away and returns
- **THEN** the area selector SHALL reset to the user's persisted home area
- **AND** any previous session override SHALL be discarded

#### Scenario: Area override for unauthenticated user

- **WHEN** an unauthenticated user opens All Nearby mode
- **AND** no guest home is stored in localStorage
- **THEN** the area selector SHALL prompt the user to choose an area
- **AND** the chosen area SHALL be used for the session without persisting to localStorage

---

### Requirement: All Nearby Concert List

The All Nearby mode SHALL display concerts returned by `ConcertService.ListByLocation` using the existing `ConcertHighway` component with HOME and NEARBY lanes.

#### Scenario: HOME and NEARBY lanes rendered

- **WHEN** `ListByLocation` returns `ProximityGroup[]`
- **THEN** the `ConcertHighway` SHALL render HOME-tier concerts in the HOME lane and NEARBY-tier concerts in the NEARBY lane
- **AND** AWAY-tier concerts SHALL NOT be displayed

#### Scenario: Venue name shown for all lanes

- **WHEN** a concert card is rendered in the All Nearby list
- **THEN** the `listed_venue_name` (or resolved venue name) SHALL be shown regardless of the lane (HOME or NEARBY)
- **AND** this overrides the current Dashboard behavior where HOME-lane cards suppress the venue label

#### Scenario: Empty state

- **WHEN** `ListByLocation` returns an empty `groups` list
- **THEN** the Dashboard SHALL display an empty-state message explaining that no concerts were found for the selected area and date range
- **AND** the empty state SHALL include a link or button navigating to the Discovery tab

---

### Requirement: Follow CTA in Event Detail Sheet for All Nearby

When viewing a concert in All Nearby mode, the `EventDetailSheet` SHALL surface a follow action for artists the user does not yet follow.

#### Scenario: Follow button visible for unfollowed artist

- **WHEN** the user opens the `EventDetailSheet` for a concert in All Nearby mode
- **AND** the concert's artist is not in the user's followed artists list
- **THEN** the sheet SHALL display a "Follow this artist" button

#### Scenario: Follow action from detail sheet

- **WHEN** the user taps "Follow this artist" in the `EventDetailSheet`
- **THEN** `ArtistService.Follow` SHALL be called
- **AND** the button SHALL change to a "Following" indicator
- **AND** the DNA Orb absorption animation SHALL NOT play (the sheet is not the Discovery context)

#### Scenario: No follow button for already-followed artist

- **WHEN** the user opens the `EventDetailSheet` for a concert in All Nearby mode
- **AND** the concert's artist is already followed
- **THEN** the follow button SHALL NOT be displayed

#### Scenario: Follow button for unauthenticated user

- **WHEN** an unauthenticated user taps "Follow this artist" in the `EventDetailSheet`
- **THEN** the system SHALL surface the sign-up prompt banner instead of calling `ArtistService.Follow`
