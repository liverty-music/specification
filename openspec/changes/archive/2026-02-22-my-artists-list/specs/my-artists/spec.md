# My Artists

## Purpose

Provides users with a view of all followed artists and the ability to manage (unfollow) them. This is the primary artist management screen, accessible via the My Artists tab in the Bottom Navigation Bar.

## Requirements

### Requirement: Followed Artists List
The system SHALL display a list of all artists the user currently follows.

#### Scenario: List population
- **WHEN** the My Artists page is opened
- **THEN** the system SHALL call `ArtistService.ListFollowed` to retrieve the user's followed artists
- **AND** the system SHALL display each artist as a row in a vertical list
- **AND** each row SHALL show the artist name with a color accent derived from the artist name (same algorithm as Dashboard cards)

#### Scenario: Empty state
- **WHEN** the user has no followed artists
- **THEN** the system SHALL display a friendly empty state message (e.g., "No artists followed yet")
- **AND** the system SHALL provide a call-to-action linking to the Discover tab

#### Scenario: Artist count
- **WHEN** the list contains followed artists
- **THEN** the page header SHALL display the total count of followed artists

---

### Requirement: Unfollow with Undo
The system SHALL allow users to unfollow artists with a frictionless, recoverable interaction.

#### Scenario: Swipe to unfollow
- **WHEN** a user swipes left on an artist row
- **THEN** the system SHALL reveal an unfollow (delete) action zone
- **AND** completing the swipe SHALL remove the artist from the visible list immediately (optimistic removal)

#### Scenario: Long-press to unfollow (alternative)
- **WHEN** a user long-presses on an artist row
- **THEN** the system SHALL reveal an unfollow action button or menu

#### Scenario: Undo toast
- **WHEN** an artist is unfollowed
- **THEN** the system SHALL display a toast notification at the bottom of the screen
- **AND** the toast SHALL show "[Artist Name] unfollowed" with an "Undo" action button
- **AND** the toast SHALL auto-dismiss after 5 seconds
- **AND** the system SHALL NOT show a confirmation dialog before unfollowing

#### Scenario: Undo action
- **WHEN** a user taps "Undo" on the toast before it dismisses
- **THEN** the system SHALL re-add the artist to the list in its original position
- **AND** the system SHALL cancel the pending unfollow RPC call

#### Scenario: Unfollow committed
- **WHEN** the undo toast dismisses without user interaction (5 seconds elapsed)
- **THEN** the system SHALL call `ArtistService.Unfollow` with the artist's ID to persist the removal
