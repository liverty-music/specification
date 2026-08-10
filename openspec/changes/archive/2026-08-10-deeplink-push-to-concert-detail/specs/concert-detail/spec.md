## ADDED Requirements

### Requirement: Deep-link auto-open of a concert detail sheet

When the dashboard loads at the `/concerts/:id` route (for example, from a tapped push notification), it SHALL automatically open the detail sheet for concert `:id` once the authoritative concert list has resolved, and SHALL derive the dashboard's artist filter from that concert. This reuses the existing `/concerts/:id` URL that the detail sheet already writes on manual open, so a deep-link and a manual card tap converge on the same URL and the same state.

The auto-open SHALL resolve the concert against the authoritative `listByFollower` fetch that the dashboard already performs — NOT against a cache first-paint, and without any additional get-by-id RPC, timer, or optimistic pre-open. When the concert is absent from the resolved list (for example, the recipient unfollowed the artist after the notification was sent, or the concert carries an invalid date / unresolved performer), the dashboard SHALL degrade gracefully: apply the artist filter if derivable and leave the sheet closed, never surfacing an error.

#### Scenario: Deep-link opens the concert after the authoritative fetch resolves

- **WHEN** the dashboard loads at `/concerts/<concertId>` and the `listByFollower` fetch resolves with a concert whose id is `<concertId>`
- **THEN** the system SHALL open that concert's detail sheet
- **AND** the sheet SHALL NOT be opened from a stale cache first-paint before the authoritative fetch resolves

#### Scenario: Deep-link derives the artist filter from the opened concert

- **WHEN** a concert detail sheet is auto-opened from a `/concerts/:id` deep-link
- **THEN** the dashboard's `filteredArtistIds` SHALL be set to `[concert.artistId]` so only that artist's concerts remain behind the sheet

#### Scenario: Closing the deep-linked sheet does not reload the dashboard

- **WHEN** the fan closes a detail sheet that was auto-opened from a `/concerts/:id` deep-link
- **THEN** the URL SHALL revert via `history.replaceState` without triggering router navigation
- **AND** the dashboard already mounted behind the sheet SHALL be revealed without a re-fetch

#### Scenario: Target concert absent degrades to filter-only

- **WHEN** the dashboard loads at `/concerts/<concertId>` but the resolved `listByFollower` result contains no concert with id `<concertId>`
- **THEN** the system SHALL NOT open a detail sheet
- **AND** SHALL NOT surface an error
- **AND** SHALL apply the artist filter only when the artist is still derivable
