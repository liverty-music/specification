# Delta for bottom-sheet

## MODIFIED Requirements

### Requirement: Follow CTA in Concert Sheet

When a signed-in fan views a concert opened from the Concerts view on Discovery, the concert sheet SHALL provide a follow action for artists the fan has not yet followed, placed on the right of the artist name in the sheet's header so that it is seen without scrolling. It SHALL read 「Follow」 in both locales, stand out as the header's only filled button, and change to 「Following」 once the follow is saved. A long artist name SHALL wrap while the button keeps its size. This makes following an artist a natural outcome of finding a concert nearby.

#### Scenario: Follow button visible for unfollowed artist in Concerts view context

- **WHEN** the fan opens the concert sheet for a concert in the Concerts view
- **AND** the concert's artist is not in the fan's followed artists list
- **THEN** the sheet SHALL display a 「Follow」 button on the right of the artist name, above the date and venue

#### Scenario: Follow button hidden in My Timetable context

- **WHEN** the user opens the concert sheet for a concert in the timetable
- **THEN** the follow button SHALL NOT be displayed regardless of follow status
- **AND** the sheet behavior SHALL be unchanged from the pre-feature state

#### Scenario: Follow action from detail sheet

- **WHEN** the fan taps 「Follow」 in the concert sheet
- **THEN** `FollowService.Follow` SHALL be called
- **AND** the button SHALL read 「Following」
- **AND** the Discovery Orb absorption animation SHALL NOT play (the bubble field and its orb are not shown while the Concerts view is)

#### Scenario: Long artist name

- **WHEN** the concert's artist name does not fit on one line beside the button on a 320 px wide screen
- **THEN** the name wraps onto more lines and the 「Follow」 button keeps its size and stays on the right of the name

#### Scenario: Follow button absent when artist data is unresolved

- **WHEN** the concert sheet is opened for a concert whose `artist` field is `undefined` (performer not yet resolved)
- **THEN** the follow button SHALL NOT be displayed
- **AND** no error SHALL be thrown

#### Scenario: Follow prompt for unauthenticated user

- **WHEN** an unauthenticated user opens any concert sheet
- **THEN** no follow button SHALL be displayed, since the Concerts view is not offered to a guest
- **AND** `FollowService.Follow` SHALL NOT be called

#### Scenario: No follow button for already-followed artist

- **WHEN** the fan opens the concert sheet for a concert in the Concerts view
- **AND** the concert's artist is already followed
- **THEN** the follow button SHALL NOT be displayed
