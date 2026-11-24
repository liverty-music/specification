## MODIFIED Requirements

### Requirement: The Concerts view's area is chosen in the filter sheet and kept on the device

The Concerts view SHALL present the current reference area as the area row of the Concerts view's filter sheet, and allow the user to override it by opening the shared `home-area-selector` from that row. The view SHALL call `ConcertService.ListByLocation` with the code of the area in use, the override when one is kept and the fan's home area otherwise, and SHALL send no coordinates: the server finds the area's reference point, so the view keeps no table of area centres. The override SHALL be kept on the device, never on the user's account, and SHALL be used on the fan's next visit to the Concerts view. Choosing the fan's own home area SHALL clear the override, so the view follows the home area again when it changes. Signing in, signing up and signing out SHALL clear the override and the kept date preset, so no one inherits another person's filter on a shared device.

#### Scenario: Default area is user home

- **WHEN** the Concerts view opens for an authenticated user who has set a home area and the device keeps no override
- **THEN** the area row SHALL display the user's home area name (prefecture display name)
- **AND** `ListByLocation` SHALL be called with the home area's code (`JP-13` for 東京都) as its area, and with no coordinates

#### Scenario: Area override via HomeAreaSelector

- **WHEN** the user taps the area row
- **THEN** the `home-area-selector` component SHALL open
- **AND** on selection, the view SHALL use the chosen area's code
- **AND** `ListByLocation` SHALL be called with that code as its area, and with no coordinates
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
