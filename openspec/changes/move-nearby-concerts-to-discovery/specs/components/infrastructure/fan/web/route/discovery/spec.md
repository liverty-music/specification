## ADDED Requirements

### Requirement: Swap tile switches between the artist bubbles and the All Nearby view

Discovery SHALL show a swap tile beside the orb, inside the band below the floor that bubbles never cross, so that no bubble and no part of the orb is ever drawn under the tile and the bubble field keeps the same size it has without the tile. The tile SHALL sit on the dominant-hand side of the orb, just outside the largest size the orb can grow to: on a 375 px wide screen, right-handed, its centre is between 260 px and 300 px from the left edge. In left-handed mode (the FAB menu's handedness setting) it SHALL be mirrored to the left of the orb.

The tile's icon SHALL draw two arrows in a loop, one magenta and one cyan. The glyph of the view on screen SHALL be drawn large over the arrows, and the glyph of the other view SHALL be drawn as a small badge in the tile's bottom corner: the artist bubbles are three bubbles (purple, teal and gold) with small sparkles, and the All Nearby view is a ticket marked LIVE with a white location pin. Under the tile a label SHALL name the view a tap leads to: 「近くのライブ」 on the artist bubbles and 「アーティスト」 on the All Nearby view (English: "Near you" and "Artists"); the tile's accessible name SHALL say the same.

A tap SHALL switch the view. The arrows SHALL make a half turn, always in the same direction, while the two glyphs trade places and sizes with a spring motion, and the new view SHALL appear as a circle growing out of the tile; the whole motion SHALL end within 700 ms. With a reduced-motion preference the view and the icon SHALL change at once, without motion.

#### Scenario: The tile never covers the bubble field
- **WHEN** Discovery shows the artist bubbles on a 375 px wide screen for a fan whose orb has reached its largest size
- **THEN** no bubble and no part of the orb is drawn under the swap tile
- **AND** the bubble field has the same height as it would without the tile

#### Scenario: Switching to the All Nearby view
- **WHEN** the fan taps the swap tile on the artist bubbles
- **THEN** Discovery shows the All Nearby view with its area chip, date chip and concert list
- **AND** the tile shows the ticket glyph large, the bubbles as the corner badge and the label 「アーティスト」

#### Scenario: Switching back to the artist bubbles
- **WHEN** the fan taps the swap tile on the All Nearby view
- **THEN** Discovery shows the artist bubbles, the search bar and the genre chips again
- **AND** the tile shows the bubbles large, the ticket as the corner badge and the label 「近くのライブ」

#### Scenario: Reduced motion
- **WHEN** a fan with a reduced-motion preference taps the swap tile
- **THEN** the view and the icon change at once, without the half turn or the growing circle

#### Scenario: Left-handed mode
- **WHEN** the fan has turned on left-handed mode
- **THEN** the swap tile sits to the left of the orb, mirrored

#### Scenario: A snack bar is open
- **WHEN** a snack bar opens on Discovery, for example after a follow that finds concerts
- **THEN** the swap tile moves up so that it sits above the snack bar, overlapping neither the snack bar nor the bubble field
- **AND** the tile stays tappable, and returns to its place when the snack bar closes

#### Scenario: Search mode
- **WHEN** the fan types in the search bar
- **THEN** the swap tile is hidden together with the genre chips, and returns when search mode ends

#### Scenario: The FAB menu is open
- **WHEN** the FAB action arc is open on Discovery
- **THEN** a tap on the swap tile only closes the arc, as for any page content under the arc's scrim

### Requirement: Discovery's view is addressable and remembered

Discovery SHALL open on the All Nearby view when its address carries `view=nearby`, at any onboarding state. Switching views SHALL rewrite the address (`/discovery?view=nearby` or `/discovery`) without adding a history entry. Without `view=nearby` in the address, Discovery SHALL open on the view the fan used last on the same device, except while the fan is onboarding, when it SHALL open on the artist bubbles. When the device cannot keep that choice, Discovery SHALL open on the artist bubbles.

#### Scenario: Link to the All Nearby view
- **WHEN** the fan opens `/discovery?view=nearby`
- **THEN** Discovery shows the All Nearby view

#### Scenario: Switching rewrites the address
- **WHEN** the fan switches from the artist bubbles to the All Nearby view
- **THEN** the address becomes `/discovery?view=nearby`
- **AND** going back leaves Discovery as it would have without the switch

#### Scenario: The last view is remembered
- **WHEN** a fan whose onboarding is complete leaves Discovery on the All Nearby view and later opens Discovery from the bottom navigation
- **THEN** Discovery shows the All Nearby view

#### Scenario: Onboarding opens on the artist bubbles
- **WHEN** an onboarding guest who last used the All Nearby view opens Discovery from the bottom navigation
- **THEN** Discovery shows the artist bubbles

#### Scenario: The device keeps nothing
- **WHEN** the device's storage is unavailable and the fan opens `/discovery`
- **THEN** Discovery shows the artist bubbles

### Requirement: All Nearby view uses ListByLocation

The All Nearby view on Discovery SHALL call `ConcertService.ListByLocation` and keep its result for the visit, so switching away from it and back does not fetch it again.

#### Scenario: All Nearby result cached independently

- **WHEN** the user switches to the All Nearby view and `ListByLocation` returns a result
- **THEN** the result SHALL be kept for the visit
- **AND** switching to the artist bubbles and back to the All Nearby view SHALL reuse the kept result when the area and date range have not changed

#### Scenario: Cache invalidated on filter change

- **WHEN** the user changes the area or date preset in the All Nearby view
- **THEN** the All Nearby cache SHALL be invalidated
- **AND** `ListByLocation` SHALL be called again with the new parameters

#### Scenario: The bubble field is kept while the All Nearby view is shown

- **WHEN** the fan switches from the artist bubbles to the All Nearby view and back
- **THEN** the bubble field SHALL show the same artists it showed before the switch
- **AND** no follow made before the switch SHALL be lost

### Requirement: Date Preset Selector in the All Nearby View

The All Nearby view SHALL expose its date filter as a single date chip that opens one date-range bottom sheet. The sheet SHALL offer three quick presets (今週末, 7日以内, 30日以内) and a directly-editable custom range (start/end date fields), so a custom range is adjusted without any intermediate menu or drill-down. There is no standalone "カスタム" preset chip; custom selection is simply editing the date fields.

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

### Requirement: Area Selector in the All Nearby View

The All Nearby view SHALL present the current reference area as an **area chip** in the single-row filter bar, and allow the user to override it for the duration of the session by opening the shared `user-home-selector` from that chip.

#### Scenario: Default area is user home

- **WHEN** the All Nearby view opens for an authenticated user who has set a home area
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

- **WHEN** an unauthenticated user opens the All Nearby view
- **AND** no guest home is stored in localStorage
- **THEN** the area chip SHALL prompt the user to choose an area
- **AND** the chosen area SHALL be used for the session without persisting to localStorage

### Requirement: All Nearby Concert List

The All Nearby view SHALL display concerts returned by `ConcertService.ListByLocation` using the same concert timetable as the dashboard, with HOME and NEARBY lanes only. The list SHALL build only a window of dates around where the fan is looking and keep every group aligned with the stage header, as the dashboard requirement "The timetable renders a window of dates around the fan" states for the timetable. Tapping a card SHALL open the concert the same way as on the dashboard: a first-party concert opens its Event page, a discovered concert opens the event detail sheet.

#### Scenario: HOME and NEARBY lanes rendered

- **WHEN** `ListByLocation` returns proximity groups
- **THEN** the concert timetable SHALL render HOME-tier concerts in the HOME lane and NEARBY-tier concerts in the NEARBY lane
- **AND** AWAY-tier concerts SHALL NOT be displayed

#### Scenario: Venue name shown for all lanes

- **WHEN** a concert card is rendered in the All Nearby list
- **THEN** the venue name (listed or resolved) SHALL be shown regardless of the lane (HOME or NEARBY)
- **AND** this differs from the dashboard timetable, whose HOME-lane cards leave the venue out

#### Scenario: Empty state

- **WHEN** `ListByLocation` returns an empty group list
- **THEN** Discovery SHALL display an empty-state message explaining that no concerts were found for the selected area and date range
- **AND** the empty state SHALL suggest a longer period or another area, while the area chip and the date chip stay available above it

#### Scenario: First-party concert opens its event page

- **WHEN** the fan taps the card of a concert whose Series belongs to an Organizer in the All Nearby list
- **THEN** the app SHALL navigate to `/events/<id>` and SHALL NOT open the detail sheet

#### Scenario: Closing the detail sheet returns to the list

- **WHEN** the fan opens a discovered concert from the All Nearby list and closes the detail sheet
- **THEN** Discovery SHALL still show the All Nearby view with the same area, date range and scroll position

### Requirement: Compact All Nearby Filter Bar on Discovery

The All Nearby view SHALL present its filters as a single, fixed-height row of two chips — an area chip and a date chip — in the place of the search bar and the genre chips, such that selecting or adjusting any filter never changes the height of the filter area and therefore never reduces the concert timetable's height.

#### Scenario: Filter bar is a single row of two chips

- **WHEN** the All Nearby view is active
- **THEN** the filter area SHALL render exactly two controls on one row: an area chip and a date chip
- **AND** neither chip SHALL expand the filter area inline when tapped

#### Scenario: Timetable height is unaffected by filter interaction

- **WHEN** the user opens the area sheet, opens the date sheet, or changes any filter
- **THEN** the height of the concert timetable SHALL NOT decrease as a result
- **AND** all complex input SHALL occur in a bottom sheet overlay rather than inline expansion

### Requirement: Localized All Nearby Date Display on Discovery

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

### Requirement: Natural Japanese Copy for the All Nearby View

All user-facing Japanese strings on the All Nearby surface SHALL read as natural, native Japanese; machine-translated or awkward phrasing SHALL be corrected. Japanese and English i18n keys SHALL remain at parity.

#### Scenario: All Nearby strings are natural Japanese

- **WHEN** the swap tile labels, area prompt, empty-state text, date-preset labels, and range hint are displayed in Japanese
- **THEN** each SHALL be phrased in natural Japanese
- **AND** every `allNearby.*` key present in the Japanese bundle SHALL also exist in the English bundle (and vice versa)

## MODIFIED Requirements

### Requirement: Bubble physics pauses when Discover tab is inactive
The system SHALL manage Bubble UI resources efficiently while the bubble field is not visible.

#### Scenario: Search mode pauses the simulation
- **WHEN** the user enters search mode
- **THEN** the physics simulation SHALL be paused, and it SHALL resume when search mode ends

#### Scenario: All Nearby view pauses the simulation
- **WHEN** the fan switches Discovery to the All Nearby view
- **THEN** the physics simulation SHALL be paused
- **AND** it SHALL resume when the fan switches back to the artist bubbles, unless search mode is on or the document is hidden

#### Scenario: Hidden document pauses the simulation
- **WHEN** the document becomes hidden (the app goes to the background or the browser tab is switched)
- **THEN** the physics simulation SHALL be paused, and it SHALL resume when the document is visible again

#### Scenario: Tab deactivation
- **WHEN** the user navigates away from the Discover tab
- **THEN** the physics simulation SHALL be stopped and its resources released

#### Scenario: Tab reactivation
- **WHEN** the user returns to the Discover tab
- **THEN** the bubble field SHALL be drawn again from the cached field, as "Discovery bubble pool caching on re-entry" states
