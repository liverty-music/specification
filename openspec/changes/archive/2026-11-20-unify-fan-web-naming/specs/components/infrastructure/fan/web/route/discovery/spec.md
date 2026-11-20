# Spec Delta

## MODIFIED Requirements

### Requirement: Swap tile switches between the Artists view and the Concerts view

Discovery SHALL show a swap tile beside the orb, inside the band below the floor that bubbles never cross, so that no bubble and no part of the orb is ever drawn under the tile and the bubble field keeps the same size it has without the tile. The tile SHALL sit on the dominant-hand side of the orb, just outside the largest size the orb can grow to: on a 375 px wide screen, right-handed, its centre is between 260 px and 300 px from the left edge. In left-handed mode (the action menu's handedness setting) it SHALL be mirrored to the left of the orb.

The tile's icon SHALL draw two arrows in a loop, one magenta and one cyan. The glyph of the view on screen SHALL be drawn large over the arrows, and the glyph of the other view SHALL be drawn as a small badge in the tile's bottom corner: the artist bubbles are three bubbles (purple, teal and gold) with small sparkles, and the Concerts view is a ticket marked LIVE with a white location pin. The tile SHALL show no text label. Its accessible name SHALL name the view a tap leads to: 「ライブ」 on the artist bubbles and 「アーティスト」 on the Concerts view (English: "Concerts" and "Artists").

A tap SHALL switch the view. The arrows SHALL make a half turn, always in the same direction, while the two glyphs trade places and sizes with a spring motion, and the new view SHALL appear as a circle growing out of the tile; the whole motion SHALL end within 700 ms. With a reduced-motion preference the view and the icon SHALL change at once, without motion.

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

Discovery SHALL open on the Concerts view when its address carries `view=concerts`, at any onboarding state. Switching views SHALL rewrite the address (`/discovery?view=concerts` or `/discovery`) without adding a history entry. Without `view=concerts` in the address, Discovery SHALL open on the view the fan used last on the same device, except while the fan is onboarding, when it SHALL open on the artist bubbles. When the device cannot keep that choice, Discovery SHALL open on the artist bubbles.

#### Scenario: Link to the Concerts view
- **WHEN** the fan opens `/discovery?view=concerts`
- **THEN** Discovery shows the Concerts view

#### Scenario: Switching rewrites the address
- **WHEN** the fan switches from the artist bubbles to the Concerts view
- **THEN** the address becomes `/discovery?view=concerts`
- **AND** going back leaves Discovery as it would have without the switch

#### Scenario: The last view is remembered
- **WHEN** a fan whose onboarding is complete leaves Discovery on the Concerts view and later opens Discovery from the bottom navigation
- **THEN** Discovery shows the Concerts view

#### Scenario: Onboarding opens on the artist bubbles
- **WHEN** an onboarding guest who last used the Concerts view opens Discovery from the bottom navigation
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

- **WHEN** a guest who follows no artist opens the Concerts view
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
