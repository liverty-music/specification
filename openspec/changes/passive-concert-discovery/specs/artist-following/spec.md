## ADDED Requirements

### Requirement: Follow CTA in Event Detail Sheet

When a user views a concert in the All Nearby mode, the `EventDetailSheet` SHALL provide a follow action for artists the user has not yet followed. This surfaces artist following as a natural outcome of passive concert discovery, without requiring users to navigate to the Discovery tab.

#### Scenario: Follow button visible for unfollowed artist in All Nearby context

- **WHEN** the user opens the `EventDetailSheet` for a concert in All Nearby mode
- **AND** the concert's artist is not in the user's followed artists list
- **THEN** the sheet SHALL display a "Follow this artist" button

#### Scenario: Follow button hidden in My Timetable context

- **WHEN** the user opens the `EventDetailSheet` for a concert in My Timetable mode
- **THEN** the follow button SHALL NOT be displayed regardless of follow status
- **AND** the sheet behavior SHALL be unchanged from the pre-feature state

#### Scenario: Follow action from detail sheet

- **WHEN** the user taps "Follow this artist" in the `EventDetailSheet`
- **THEN** `ArtistService.Follow` SHALL be called via `FollowStore.follow(artist)`
- **AND** the button SHALL transition to a "Following" indicator
- **AND** the DNA Orb absorption animation SHALL NOT play (reserved for the Discovery context)

#### Scenario: Follow button absent when artist data is unresolved

- **WHEN** the `EventDetailSheet` is opened for a concert whose `artist` field is `undefined` (performer not yet resolved)
- **THEN** the follow button SHALL NOT be displayed
- **AND** no error SHALL be thrown

#### Scenario: No follow button for already-followed artist

- **WHEN** the user opens the `EventDetailSheet` for a concert in All Nearby mode
- **AND** the concert's artist is already followed
- **THEN** the follow button SHALL NOT be displayed

#### Scenario: Follow prompt for unauthenticated user

- **WHEN** an unauthenticated user taps "Follow this artist" in the `EventDetailSheet`
- **THEN** the system SHALL surface the sign-up prompt banner
- **AND** `ArtistService.Follow` SHALL NOT be called
