## MODIFIED Requirements

### Requirement: Follow CTA in Event Detail Sheet

When a user views a concert opened from the All Nearby view on Discovery, the event detail sheet SHALL provide a follow action for artists the user has not yet followed. This makes following an artist a natural outcome of finding a concert nearby.

#### Scenario: Follow button visible for unfollowed artist in All Nearby context

- **WHEN** the user opens the event detail sheet for a concert in the All Nearby view
- **AND** the concert's artist is not in the user's followed artists list
- **THEN** the sheet SHALL display a "Follow this artist" button

#### Scenario: Follow button hidden in My Timetable context

- **WHEN** the user opens the event detail sheet for a concert in the dashboard timetable
- **THEN** the follow button SHALL NOT be displayed regardless of follow status
- **AND** the sheet behavior SHALL be unchanged from the pre-feature state

#### Scenario: Follow action from detail sheet

- **WHEN** the user taps "Follow this artist" in the event detail sheet
- **THEN** `FollowService.Follow` SHALL be called
- **AND** the button SHALL transition to a "Following" indicator
- **AND** the DNA Orb absorption animation SHALL NOT play (the bubble field and its orb are not shown while the All Nearby view is)

#### Scenario: Follow button absent when artist data is unresolved

- **WHEN** the event detail sheet is opened for a concert whose `artist` field is `undefined` (performer not yet resolved)
- **THEN** the follow button SHALL NOT be displayed
- **AND** no error SHALL be thrown

#### Scenario: No follow button for already-followed artist

- **WHEN** the user opens the event detail sheet for a concert in the All Nearby view
- **AND** the concert's artist is already followed
- **THEN** the follow button SHALL NOT be displayed

#### Scenario: Follow prompt for unauthenticated user

- **WHEN** an unauthenticated user taps "Follow this artist" in the event detail sheet
- **THEN** the system SHALL surface the sign-up prompt banner
- **AND** `FollowService.Follow` SHALL NOT be called
