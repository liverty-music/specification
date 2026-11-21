# Delta for discovery

## ADDED Requirements

### Requirement: The bubble field's guide moment

While the artist bubbles are shown to a fan who follows no artist (on the device for a guest, on the account for a signed-in fan), Discovery SHALL show a guide moment once the first artist name has appeared in the bubble field: the inner edge of the bubble field glows, without singling out any bubble and without lighting the orb, with the line 「気になるアーティストをタップしてフォローしよう！」 (EN "Tap an artist you like to follow!"). The fan's first follow, from a bubble or from a search result, SHALL end it and count as using it. It SHALL NOT appear over bubbles that show no name yet, and SHALL NOT appear to a fan who follows at least one artist.

#### Scenario: A new guest opens Discovery
- **WHEN** a guest who follows no artist opens Discovery and the first artist name appears
- **THEN** the bubble field's edge glows and 「気になるアーティストをタップしてフォローしよう！」 is shown

#### Scenario: Follow from search
- **WHEN** that guest follows an artist from a search result
- **THEN** the moment ends and does not appear again on this device

#### Scenario: A fan who already follows
- **WHEN** a signed-in fan who follows 20 artists opens Discovery on a new device
- **THEN** the bubble field's moment does not appear

### Requirement: The swap tile's guide moment

When a signed-in fan whose onboarding is complete opens the artist bubbles and has never switched Discovery's view on this device, Discovery SHALL show a guide moment on the swap tile with the line 「すぐに行けるライブも見てみよう！」 (EN "There are concerts you can go to soon!"). A tap on the swap tile SHALL end it and count as using it. It SHALL NOT appear to a guest or to a fan in onboarding.

#### Scenario: First visit after onboarding
- **WHEN** a signed-in fan whose onboarding is complete opens Discovery on the artist bubbles for the first time on this device
- **THEN** the swap tile glows and 「すぐに行けるライブも見てみよう！」 is shown
- **WHEN** the fan taps the swap tile
- **THEN** Discovery shows the Concerts view and the moment does not appear again on this device

#### Scenario: Fan in onboarding
- **WHEN** a signed-in fan in onboarding opens Discovery
- **THEN** the swap tile's moment does not appear

#### Scenario: Fan who switched before
- **WHEN** a signed-in fan who has switched to the Concerts view on this device opens Discovery
- **THEN** the swap tile's moment does not appear

### Requirement: The Concerts view's guide moment

The first time the Concerts view shows its list, or its empty state, on a device, Discovery SHALL show a guide moment on the action menu button with the line 「遠征するときはココを変更！」 (EN "Going somewhere? Change it here!"). Opening the action menu SHALL end it and count as using it.

#### Scenario: First visit to the Concerts view
- **WHEN** a signed-in fan opens the Concerts view for the first time on this device and its list shows
- **THEN** the action menu button glows and 「遠征するときはココを変更！」 is shown
- **WHEN** the fan opens the action menu
- **THEN** the moment ends and the menu offers 「エリアと期間を変える」

#### Scenario: Empty list
- **WHEN** a signed-in fan opens the Concerts view for the first time on this device and no concert is found
- **THEN** the moment is shown with the empty state

## MODIFIED Requirements

### Requirement: DNA Extraction UI Concept
The system SHALL provide a gamified artist discovery interface using a "DNA Extraction" metaphor with an interactive orb (glass sphere) UI that collects user preferences, with visual differentiation per artist and onboarding guidance.

#### Scenario: Initial bubble display with Discovery Orb
- **WHEN** a guest or a signed-in fan opens the Discovery screen
- **THEN** the system SHALL display up to 50 artist bubbles in the center area using physics-based animation, or up to 30 when the canvas is narrower than 390 px
- **AND** the system SHALL display a "Music Discovery Orb" (glass sphere UI) at the bottom of the screen
- **AND** the orb SHALL serve as a visual inventory for collected artists

#### Scenario: Per-artist bubble color differentiation
- **WHEN** artist bubbles are rendered
- **THEN** each bubble SHALL have a unique gradient color derived from the artist's name using a deterministic HSL-based algorithm
- **AND** the colors SHALL provide visual variety across the bubble field (not uniform purple)

#### Scenario: Onboarding guidance overlay
- **WHEN** the Discovery screen is displayed for the first time during onboarding
- **THEN** the page-help sheet for Discovery SHALL NOT open on its own
- **AND** the bubble-field guide moment SHALL guide the fan, as "The bubble field's guide moment" states
- **AND** the onboarding progress row SHALL be shown under the genre chips

#### Scenario: Background visual depth
- **WHEN** the Artist Discovery screen is displayed
- **THEN** the background SHALL include subtle visual elements (e.g., particle field, starfield, or animated gradient) to create depth
- **AND** these elements SHALL NOT compete with the foreground bubbles and orb for attention

### Requirement: Swap tile switches between the Artists view and the Concerts view

Discovery SHALL show a swap tile beside the orb to a signed-in fan, and no swap tile to a guest. The tile SHALL sit inside the band below the floor that bubbles never cross, so that no bubble and no part of the orb is ever drawn under the tile and the bubble field keeps the same size it has without the tile. The tile SHALL sit on the dominant-hand side of the orb, just outside the largest size the orb can grow to: on a 375 px wide screen, right-handed, its centre is between 260 px and 300 px from the left edge. In left-handed mode (the action menu's handedness setting) it SHALL be mirrored to the left of the orb.

The tile's icon SHALL draw two arrows in a loop, one magenta and one cyan. The glyph of the view on screen SHALL be drawn large over the arrows, and the glyph of the other view SHALL be drawn as a small badge in the tile's bottom corner: the artist bubbles are three bubbles (purple, teal and gold) with small sparkles, and the Concerts view is a ticket marked LIVE with a white location pin. The tile SHALL show no text label. Its accessible name SHALL name the view a tap leads to: 「ライブ」 on the artist bubbles and 「アーティスト」 on the Concerts view (English: "Concerts" and "Artists").

A tap SHALL switch the view. The arrows SHALL make a half turn, always in the same direction, while the two glyphs trade places and sizes with a spring motion, and the new view SHALL appear as a circle growing out of the tile; the whole motion SHALL end within 700 ms. With a reduced-motion preference the view and the icon SHALL change at once, without motion.

#### Scenario: A guest sees no swap tile
- **WHEN** a guest opens Discovery
- **THEN** no swap tile is shown and the bubble field has the same size it has for a signed-in fan

#### Scenario: The tile never covers the bubble field
- **WHEN** Discovery shows the artist bubbles on a 375 px wide screen for a fan whose orb has reached its largest size
- **THEN** no bubble and no part of the orb is drawn under the swap tile
- **AND** the bubble field has the same height as it would without the tile

#### Scenario: Switching to the Concerts view
- **WHEN** the fan taps the swap tile on the artist bubbles
- **THEN** Discovery shows the Concerts view: the stage header directly under the page header, and the concert list
- **AND** the tile shows the ticket glyph large and the bubbles as the corner badge, and its accessible name is 「アーティスト」

#### Scenario: Switching back to the artist bubbles
- **WHEN** the fan taps the swap tile on the Concerts view
- **THEN** Discovery shows the artist bubbles, the search bar and the genre chips again
- **AND** the tile shows the bubbles large and the ticket as the corner badge, and its accessible name is 「ライブ」

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

#### Scenario: The action menu is open
- **WHEN** the action menu action arc is open on Discovery
- **THEN** a tap on the swap tile only closes the arc, as for any page content under the arc's scrim

### Requirement: Discovery's view is addressable and remembered

Discovery SHALL open on the Concerts view when its address carries `view=concerts` and the fan is signed in, at any onboarding state. A guest SHALL always get the artist bubbles, whatever the address carries, and the address SHALL then read `/discovery`. Switching views SHALL rewrite the address (`/discovery?view=concerts` or `/discovery`) without adding a history entry. Without `view=concerts` in the address, Discovery SHALL open on the view the fan used last on the same device, except while the fan is onboarding, when it SHALL open on the artist bubbles. When the device cannot keep that choice, Discovery SHALL open on the artist bubbles.

#### Scenario: Link to the Concerts view
- **WHEN** the fan opens `/discovery?view=concerts`
- **THEN** Discovery shows the Concerts view

#### Scenario: A guest follows a link to the Concerts view
- **WHEN** a guest opens `/discovery?view=concerts`
- **THEN** Discovery shows the artist bubbles and the address becomes `/discovery`

#### Scenario: Switching rewrites the address
- **WHEN** the fan switches from the artist bubbles to the Concerts view
- **THEN** the address becomes `/discovery?view=concerts`
- **AND** going back leaves Discovery as it would have without the switch

#### Scenario: The last view is remembered
- **WHEN** a fan whose onboarding is complete leaves Discovery on the Concerts view and later opens Discovery from the bottom navigation
- **THEN** Discovery shows the Concerts view

#### Scenario: Onboarding opens on the artist bubbles
- **WHEN** a signed-in fan in onboarding who last used the Concerts view opens Discovery from the bottom navigation
- **THEN** Discovery shows the artist bubbles

#### Scenario: The device keeps nothing
- **WHEN** the device's storage is unavailable and the fan opens `/discovery`
- **THEN** Discovery shows the artist bubbles

### Requirement: Concerts view list

The Concerts view SHALL display concerts returned by `ConcertService.ListByLocation` using the same concert timetable as the timetable, with HOME and NEARBY lanes only. The list SHALL build only a window of dates around where the fan is looking and keep every group aligned with the stage header, as the timetable requirement "The timetable renders a window of dates around the fan" states for the timetable. Tapping a card SHALL open the concert the same way as on the timetable: a first-party concert opens its Concert page, a discovered concert opens the concert sheet. A card SHALL show the matched or unmatched treatment and the journey badge by the same rules as the timetable: an artist the fan follows is matched by its hype level and the concert's lane, an artist the fan does not follow is never matched, and a concert the fan has a journey for shows its journey badge. A change of the fan's journey or hype level SHALL show on the cards without reloading the view.

#### Scenario: HOME and NEARBY lanes rendered

- **WHEN** `ListByLocation` returns proximity groups
- **THEN** the concert timetable SHALL render HOME-tier concerts in the HOME lane and NEARBY-tier concerts in the NEARBY lane
- **AND** AWAY-tier concerts SHALL NOT be displayed

#### Scenario: Venue name shown for all lanes

- **WHEN** a concert card is rendered in the Concerts view's list
- **THEN** the venue name (listed or resolved) SHALL be shown regardless of the lane (HOME or NEARBY)
- **AND** this differs from the timetable, whose HOME-lane cards leave the venue out

#### Scenario: Empty state

- **WHEN** `ListByLocation` returns an empty group list
- **THEN** Discovery SHALL display an empty-state message explaining that no concerts were found for the selected area and date range
- **AND** the empty state SHALL suggest a longer period or another area, while the filter stays one tap away in the launcher

#### Scenario: First-party concert opens its concert page

- **WHEN** the fan taps the card of a concert whose Series belongs to an Organizer in the Concerts view's list
- **THEN** the app SHALL navigate to `/concerts/<id>` and SHALL NOT open the detail sheet

#### Scenario: Closing the detail sheet returns to the list

- **WHEN** the fan opens a discovered concert from the Concerts view's list and closes the detail sheet
- **THEN** Discovery SHALL still show the Concerts view with the same area, date range and scroll position

#### Scenario: Followed artist matched by hype and lane

- **GIVEN** the fan follows an artist at hype level Home
- **WHEN** that artist's concerts appear in the HOME lane and the NEARBY lane of the Concerts view
- **THEN** the HOME lane card SHALL render as matched
- **AND** the NEARBY lane card SHALL render as unmatched

#### Scenario: Artist the fan does not follow is never matched

- **WHEN** a concert of an artist the fan does not follow appears in either lane
- **THEN** its card SHALL render as unmatched

#### Scenario: Guest with no follows

- **WHEN** a guest who follows no artist follows a link to the Concerts view
- **THEN** Discovery shows the artist bubbles and no concert card is rendered

#### Scenario: Fan with no follows

- **WHEN** a signed-in fan who follows no artist opens the Concerts view
- **THEN** every card SHALL render as unmatched

#### Scenario: Journey badge shown

- **GIVEN** the fan has a journey of status Tracking for a concert
- **WHEN** that concert appears in the Concerts view, including on a first visit straight to `/discovery?view=concerts`
- **THEN** its card SHALL show the same journey badge as on the timetable

#### Scenario: Journey or hype changed in the detail sheet

- **WHEN** the fan opens a discovered concert from the Concerts view, sets a journey in the detail sheet and closes it
- **THEN** the card SHALL show the new journey badge without reloading the view
- **WHEN** the fan changes a followed artist's hype level elsewhere and returns to the Concerts view
- **THEN** that artist's cards SHALL show the matched state for the new level

### Requirement: The Concerts view's area is chosen in the filter sheet and kept on the device

The Concerts view SHALL present the current reference area as the area row of the Concerts view's filter sheet, and allow the user to override it by opening the shared `home-area-selector` from that row. The override SHALL be kept on the device, never on the user's account, and SHALL be used on the fan's next visit to the Concerts view. Choosing the fan's own home area SHALL clear the override, so the view follows the home area again when it changes. Signing in, signing up and signing out SHALL clear the override and the kept date preset, so no one inherits another person's filter on a shared device.

#### Scenario: Default area is user home

- **WHEN** the Concerts view opens for an authenticated user who has set a home area and the device keeps no override
- **THEN** the area row SHALL display the user's home area name (prefecture display name)
- **AND** the `GeoLocation` passed to `ListByLocation` SHALL use `user.home.centroid.latitude`, `user.home.centroid.longitude`, and `user.home.level_1` as `admin_area` (`centroid` is the nested `Coordinates` sub-message on the `Home` proto; `centroid_latitude`/`centroid_longitude` are reserved field names)

#### Scenario: Area override via HomeAreaSelector

- **WHEN** the user taps the area row
- **THEN** the `home-area-selector` component SHALL open
- **AND** on selection, the view SHALL use the new ISO 3166-2 code
- **AND** `ListByLocation` SHALL be called with the new area's centroid coordinates and admin_area
- **AND** the new area SHALL NOT be saved to the user's account

#### Scenario: Area override is kept on the device

- **WHEN** the user chooses 大阪府 while their home area is 東京都, then reloads the app and opens the Concerts view
- **THEN** the area row SHALL display 大阪府 and the concerts SHALL be those near 大阪府
- **AND** the user's home area SHALL still be 東京都

#### Scenario: Choosing the home area clears the override

- **WHEN** the user has an override of 大阪府, chooses 東京都 (their home area) and later changes their home area to 神奈川県
- **THEN** the Concerts view SHALL use 神奈川県

#### Scenario: Signing in, signing up or signing out clears the kept filter

- **WHEN** a fan who chose 大阪府 and 今週末 signs out and another fan whose home area is 東京都 signs in on the same device
- **THEN** the Concerts view SHALL use 東京都 and 7日以内, and the filter item SHALL be in its default state
- **WHEN** a fan who chose 大阪府 signs out and another fan signs in on the same device
- **THEN** the Concerts view SHALL use the second fan's home area

#### Scenario: Area override for unauthenticated user

- **WHEN** an unauthenticated user follows a link to the Concerts view
- **THEN** Discovery shows the artist bubbles, no area selector opens and no area override is stored on the device

#### Scenario: Signed-in fan without a home area

- **WHEN** a signed-in fan whose account has no home area opens the Concerts view
- **AND** no override is stored on the device
- **THEN** the view SHALL open the `home-area-selector` as its area selector before listing any concert
- **AND** until an area is chosen, the area row of the filter sheet SHALL prompt the fan to choose one
- **AND** the chosen area SHALL be kept on the device as the override, not as the fan's home area

### Requirement: Concerts view's filters open from the action launcher

The Concerts view SHALL show no filter control above the timetable: the stage header SHALL sit directly under the page header, as on the timetable. The action menu SHALL offer a filter item while the Concerts view is shown (see the action menu Menu's per-route actions), labelled 「エリアと期間を変える」 (EN "Change area and dates"); the Timetable's filter item keeps its own label. The filter item SHALL open the Concerts view's filter sheet, which holds two rows, the area and the period, each showing its current value and opening its own selector. The filter item SHALL show its active state while the area differs from the fan's home area or the period differs from 7日以内. Changing a filter SHALL never change the timetable's height.

#### Scenario: Stage header under the page header

- **WHEN** the Concerts view is shown on a 375 px wide screen
- **THEN** the top edge of the stage header SHALL touch the bottom edge of the page header, with no row between them

#### Scenario: Filter item opens the filter sheet

- **WHEN** the fan opens the launcher on the Concerts view and taps 「エリアと期間を変える」
- **THEN** the filter sheet SHALL open with an area row showing the current area and a period row showing the current period

#### Scenario: A row opens its selector

- **WHEN** the fan taps the area row of the filter sheet
- **THEN** the filter sheet SHALL close and the `home-area-selector` SHALL open, so two sheets are never open at once
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
