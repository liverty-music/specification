## MODIFIED Requirements

### Requirement: Swap tile switches between the artist bubbles and the All Nearby view

Discovery SHALL show a swap tile beside the orb, inside the band below the floor that bubbles never cross, so that no bubble and no part of the orb is ever drawn under the tile and the bubble field keeps the same size it has without the tile. The tile SHALL sit on the dominant-hand side of the orb, just outside the largest size the orb can grow to: on a 375 px wide screen, right-handed, its centre is between 260 px and 300 px from the left edge. In left-handed mode (the FAB menu's handedness setting) it SHALL be mirrored to the left of the orb.

The tile's icon SHALL draw two arrows in a loop, one magenta and one cyan. The glyph of the view on screen SHALL be drawn large over the arrows, and the glyph of the other view SHALL be drawn as a small badge in the tile's bottom corner: the artist bubbles are three bubbles (purple, teal and gold) with small sparkles, and the All Nearby view is a ticket marked LIVE with a white location pin. The tile SHALL show no text label. Its accessible name SHALL name the view a tap leads to: 「近くのライブ」 on the artist bubbles and 「アーティスト」 on the All Nearby view (English: "Near you" and "Artists").

A tap SHALL switch the view. The arrows SHALL make a half turn, always in the same direction, while the two glyphs trade places and sizes with a spring motion, and the new view SHALL appear as a circle growing out of the tile; the whole motion SHALL end within 700 ms. With a reduced-motion preference the view and the icon SHALL change at once, without motion.

#### Scenario: The tile never covers the bubble field
- **WHEN** Discovery shows the artist bubbles on a 375 px wide screen for a fan whose orb has reached its largest size
- **THEN** no bubble and no part of the orb is drawn under the swap tile
- **AND** the bubble field has the same height as it would without the tile

#### Scenario: Switching to the All Nearby view
- **WHEN** the fan taps the swap tile on the artist bubbles
- **THEN** Discovery shows the All Nearby view: the stage header directly under the page header, and the concert list
- **AND** the tile shows the ticket glyph large and the bubbles as the corner badge, and its accessible name is 「アーティスト」

#### Scenario: Switching back to the artist bubbles
- **WHEN** the fan taps the swap tile on the All Nearby view
- **THEN** Discovery shows the artist bubbles, the search bar and the genre chips again
- **AND** the tile shows the bubbles large and the ticket as the corner badge, and its accessible name is 「近くのライブ」

#### Scenario: Reduced motion
- **WHEN** a fan with a reduced-motion preference taps the swap tile
- **THEN** the view and the icon change at once, without the half turn or the growing circle

#### Scenario: Left-handed mode
- **WHEN** the fan has turned on left-handed mode
- **THEN** the swap tile sits to the left of the orb, mirrored

#### Scenario: A snack bar is open
- **WHEN** a snack bar opens on Discovery, for example after a follow that finds concerts
- **THEN** the snack bar sits above the swap tile, as "Snack bars sit above the bottom navigation and any banner" states, and the tile does not move
- **AND** the tile stays tappable

#### Scenario: Search mode
- **WHEN** the fan types in the search bar
- **THEN** the swap tile is hidden together with the genre chips, and returns when search mode ends

#### Scenario: The FAB menu is open
- **WHEN** the FAB action arc is open on Discovery
- **THEN** a tap on the swap tile only closes the arc, as for any page content under the arc's scrim

### Requirement: All Nearby Concert List

The All Nearby view SHALL display concerts returned by `ConcertService.ListByLocation` using the same concert timetable as the dashboard, with HOME and NEARBY lanes only. The list SHALL build only a window of dates around where the fan is looking and keep every group aligned with the stage header, as the dashboard requirement "The timetable renders a window of dates around the fan" states for the timetable. Tapping a card SHALL open the concert the same way as on the dashboard: a first-party concert opens its Event page, a discovered concert opens the event detail sheet. A card SHALL show the matched or unmatched treatment and the journey badge by the same rules as the dashboard timetable: an artist the fan follows is matched by its hype level and the concert's lane, an artist the fan does not follow is never matched, and a concert the fan has a journey for shows its journey badge. A change of the fan's journey or hype level SHALL show on the cards without reloading the view.

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
- **AND** the empty state SHALL suggest a longer period or another area, while the filter stays one tap away in the launcher

#### Scenario: First-party concert opens its event page

- **WHEN** the fan taps the card of a concert whose Series belongs to an Organizer in the All Nearby list
- **THEN** the app SHALL navigate to `/events/<id>` and SHALL NOT open the detail sheet

#### Scenario: Closing the detail sheet returns to the list

- **WHEN** the fan opens a discovered concert from the All Nearby list and closes the detail sheet
- **THEN** Discovery SHALL still show the All Nearby view with the same area, date range and scroll position

#### Scenario: Followed artist matched by hype and lane

- **GIVEN** the fan follows an artist at hype level Home
- **WHEN** that artist's concerts appear in the HOME lane and the NEARBY lane of the All Nearby view
- **THEN** the HOME lane card SHALL render as matched
- **AND** the NEARBY lane card SHALL render as unmatched

#### Scenario: Artist the fan does not follow is never matched

- **WHEN** a concert of an artist the fan does not follow appears in either lane
- **THEN** its card SHALL render as unmatched

#### Scenario: Guest with no follows

- **WHEN** a guest who follows no artist opens the All Nearby view
- **THEN** every card SHALL render as unmatched

#### Scenario: Journey badge shown

- **GIVEN** the fan has a journey of status Tracking for a concert
- **WHEN** that concert appears in the All Nearby view, including on a first visit straight to `/discovery?view=nearby`
- **THEN** its card SHALL show the same journey badge as on the dashboard

#### Scenario: Journey or hype changed in the detail sheet

- **WHEN** the fan opens a discovered concert from the All Nearby view, sets a journey in the detail sheet and closes it
- **THEN** the card SHALL show the new journey badge without reloading the view
- **WHEN** the fan changes a followed artist's hype level elsewhere and returns to the All Nearby view
- **THEN** that artist's cards SHALL show the matched state for the new level

## ADDED Requirements

### Requirement: All Nearby dates are shown in the Japanese locale

Every user-facing date and date-range in the All Nearby filter SHALL be formatted for the Japanese locale via `Intl.DateTimeFormat('ja-JP')`; the browser's native `MM/DD/YYYY` input rendering SHALL NOT be the primary display of the selected range.

#### Scenario: Period row shows a localized range

- **WHEN** a custom range from 2026-08-12 to 2026-08-20 is applied
- **THEN** the period row of the filter sheet SHALL display the localized range `8/12〜8/20`

#### Scenario: Single-day range

- **WHEN** the applied range has `from` equal to `to`
- **THEN** the period row of the filter sheet SHALL display that single localized date (e.g. `8/10`) rather than a `〜`-joined pair

#### Scenario: Preset shows its name

- **WHEN** a quick preset (今週末 / 7日以内 / 30日以内) is applied
- **THEN** the period row of the filter sheet SHALL display that preset's name rather than a raw date range

### Requirement: The All Nearby period is chosen in a date-range sheet and its preset is kept

The All Nearby view SHALL expose its date filter as the period row of the All Nearby filter sheet (see "All Nearby filters open from the action launcher"); a tap on the row SHALL open one date-range bottom sheet. The sheet SHALL offer three quick presets (今週末, 7日以内, 30日以内) and a directly-editable custom range (start/end date fields), so a custom range is adjusted without any intermediate menu or drill-down. There is no standalone "カスタム" preset chip; custom selection is simply editing the date fields. The last quick preset the fan applied SHALL be kept on the device and applied on the fan's next visit to the All Nearby view; a custom range SHALL NOT be kept, and a visit after one starts from 7日以内. The kept preset SHALL be cleared at sign-in, sign-up and sign-out, with the area override. Without a kept preset the view SHALL start from 7日以内.

#### Scenario: Period row opens the range sheet in one tap

- **WHEN** the user taps the period row of the filter sheet
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

#### Scenario: A preset is kept for the next visit

- **WHEN** the fan applies 今週末, leaves Discovery, reloads the app and opens the All Nearby view again
- **THEN** the view SHALL load 今週末's range, computed from the new day's date

#### Scenario: A custom range is not kept

- **WHEN** the fan applies a custom range from 2026-08-12 to 2026-08-20 and opens the All Nearby view again on a later visit
- **THEN** the view SHALL load 7日以内

#### Scenario: The device keeps nothing

- **WHEN** the device's storage is unavailable and the fan opens the All Nearby view
- **THEN** the view SHALL load 7日以内

### Requirement: The All Nearby area is chosen in the filter sheet and kept on the device

The All Nearby view SHALL present the current reference area as the area row of the All Nearby filter sheet, and allow the user to override it by opening the shared `user-home-selector` from that row. The override SHALL be kept on the device, never on the user's account, and SHALL be used on the fan's next visit to the All Nearby view. Choosing the fan's own home area SHALL clear the override, so the view follows the home area again when it changes. Signing in, signing up and signing out SHALL clear the override and the kept date preset, so no one inherits another person's filter on a shared device.

#### Scenario: Default area is user home

- **WHEN** the All Nearby view opens for an authenticated user who has set a home area and the device keeps no override
- **THEN** the area row SHALL display the user's home area name (prefecture display name)
- **AND** the `GeoLocation` passed to `ListByLocation` SHALL use `user.home.centroid.latitude`, `user.home.centroid.longitude`, and `user.home.level_1` as `admin_area` (`centroid` is the nested `Coordinates` sub-message on the `Home` proto; `centroid_latitude`/`centroid_longitude` are reserved field names)

#### Scenario: Area override via UserHomeSelector

- **WHEN** the user taps the area row
- **THEN** the `user-home-selector` component SHALL open
- **AND** on selection, the view SHALL use the new ISO 3166-2 code
- **AND** `ListByLocation` SHALL be called with the new area's centroid coordinates and admin_area
- **AND** the new area SHALL NOT be saved to the user's account

#### Scenario: Area override is kept on the device

- **WHEN** the user chooses 大阪府 while their home area is 東京都, then reloads the app and opens the All Nearby view
- **THEN** the area row SHALL display 大阪府 and the concerts SHALL be those near 大阪府
- **AND** the user's home area SHALL still be 東京都

#### Scenario: Choosing the home area clears the override

- **WHEN** the user has an override of 大阪府, chooses 東京都 (their home area) and later changes their home area to 神奈川県
- **THEN** the All Nearby view SHALL use 神奈川県

#### Scenario: Signing in, signing up or signing out clears the kept filter

- **WHEN** a guest who chose 大阪府 and 今週末 signs in or signs up as a fan whose home area is 東京都
- **THEN** the All Nearby view SHALL use 東京都 and 7日以内, and the filter item SHALL be in its default state
- **WHEN** a fan who chose 大阪府 signs out and another fan signs in on the same device
- **THEN** the All Nearby view SHALL use the second fan's home area

#### Scenario: Area override for unauthenticated user

- **WHEN** an unauthenticated user opens the All Nearby view
- **AND** no guest home and no override are stored on the device
- **THEN** the view SHALL open the `user-home-selector` as its area selector before listing any concert
- **AND** until an area is chosen, the area row of the filter sheet SHALL prompt the user to choose one
- **AND** the chosen area SHALL be kept on the device as the override, not as the guest home

### Requirement: All Nearby filters open from the action launcher

The All Nearby view SHALL show no filter control above the timetable: the stage header SHALL sit directly under the page header, as on the dashboard. The FAB action launcher SHALL offer a filter item while the All Nearby view is shown (see the FAB Menu's per-route actions). The filter item SHALL open the All Nearby filter sheet, which holds two rows, the area and the period, each showing its current value and opening its own selector. The filter item SHALL show its active state while the area differs from the fan's home area or the period differs from 7日以内. Changing a filter SHALL never change the timetable's height.

#### Scenario: Stage header under the page header

- **WHEN** the All Nearby view is shown on a 375 px wide screen
- **THEN** the top edge of the stage header SHALL touch the bottom edge of the page header, with no row between them

#### Scenario: Filter item opens the filter sheet

- **WHEN** the fan opens the launcher on the All Nearby view and taps the filter item
- **THEN** the filter sheet SHALL open with an area row showing the current area and a period row showing the current period

#### Scenario: A row opens its selector

- **WHEN** the fan taps the area row of the filter sheet
- **THEN** the filter sheet SHALL close and the `user-home-selector` SHALL open, so two sheets are never open at once
- **WHEN** the fan taps the period row of the filter sheet
- **THEN** the filter sheet SHALL close and the date-range sheet SHALL open

#### Scenario: Filter item shows its active state

- **WHEN** the area is the fan's home area and the period is 7日以内
- **THEN** the filter item SHALL be in its default state
- **WHEN** the fan applies 今週末, or chooses an area other than their home area
- **THEN** the filter item SHALL be in its active state

#### Scenario: Timetable height is unaffected by filter interaction

- **WHEN** the fan opens the filter sheet, opens either selector, or changes any filter
- **THEN** the height of the concert timetable SHALL NOT change as a result

## REMOVED Requirements

### Requirement: Compact All Nearby Filter Bar on Discovery
**Reason**: The row of chips put a band above the stage header that the dashboard does not have. The filters move to the action launcher, as on the dashboard.
**Migration**: "All Nearby filters open from the action launcher" replaces it; the timetable keeps its full height because no filter control sits above it.

### Requirement: Date Preset Selector in the All Nearby View
**Reason**: The date chip it describes is gone; the period is chosen from the All Nearby filter sheet, and the applied preset is now kept for the next visit.
**Migration**: "The All Nearby period is chosen in a date-range sheet and its preset is kept" replaces it with the same presets, range rules and validation.

### Requirement: Area Selector in the All Nearby View
**Reason**: The area chip it describes is gone, and the override is no longer session-scoped: it is kept on the device.
**Migration**: "The All Nearby area is chosen in the filter sheet and kept on the device" replaces it.

### Requirement: Localized All Nearby Date Display on Discovery
**Reason**: Its first scenario names the date chip, which this change removes.
**Migration**: "All Nearby dates are shown in the Japanese locale" states the same formatting for the filter sheet's period row.
