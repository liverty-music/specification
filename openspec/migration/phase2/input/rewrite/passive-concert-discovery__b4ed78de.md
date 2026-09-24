<!-- spec: passive-concert-discovery | target: components/infrastructure/fan/web/route/dashboard | flags: CLASSNAME | new_name: Follow CTA in Event Detail Sheet for All Nearby -->

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
