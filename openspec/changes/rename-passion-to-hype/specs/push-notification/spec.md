## MODIFIED Requirements

### Requirement: Deliver Push Notifications for New Concerts

The system SHALL send Web Push notifications to followers of an artist when new concerts are discovered, filtered by each follower's hype level and home area. Notifications SHALL be batched per artist (one notification per artist per job run, regardless of how many concerts were found).

#### Scenario: New concerts found for an artist with followers

- **WHEN** `SearchNewConcerts` returns one or more new concerts for an artist
- **AND** the artist has followers with active push subscriptions
- **THEN** the system SHALL evaluate each follower's hype level against the concert's venue location
- **AND** SHALL only send push notifications to followers whose hype level qualifies (ANYWHERE for all concerts, HOME for home-area matches only, WATCH receives none)
- **AND** the notification payload SHALL include the artist name, the count of new concerts, and a URL to the artist's concert list

#### Scenario: New concerts found but no qualifying followers

- **WHEN** `SearchNewConcerts` returns new concerts for an artist
- **AND** no followers qualify for notification after hype filtering (all are WATCH or HOME with non-matching area)
- **THEN** the system SHALL skip notification delivery without error
