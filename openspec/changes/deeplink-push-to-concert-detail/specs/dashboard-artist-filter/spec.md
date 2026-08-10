## MODIFIED Requirements

### Requirement: Push notification deep-link to filtered dashboard

Tapping a new-concert push notification SHALL open the deep-linked concert's detail sheet on the dashboard, with the dashboard filtered to that concert's artist. The notification carries a `/concerts/<concertId>` URL (see the `concert-detail` deep-link auto-open requirement). The artist filter SHALL be **derived from the opened concert** (`filteredArtistIds = [concert.artistId]`), not carried as a `?artists=` query parameter in the notification URL.

#### Scenario: Notification tap opens the concert filtered to its artist

- **WHEN** a push notification with `data.url = "/concerts/<concertId>"` is tapped
- **THEN** the browser SHALL navigate to `/concerts/<concertId>`
- **AND** the dashboard SHALL derive the artist filter from the opened concert so only that artist's concerts remain behind the sheet

#### Scenario: Deep-link auto-open suppressed during onboarding

- **WHEN** the user is in the onboarding flow (`isOnboarding` is true)
- **THEN** the deep-link SHALL NOT auto-open a detail sheet and SHALL NOT derive an artist filter
- **AND** the manual filter trigger button SHALL remain hidden (via `if.bind="!isOnboarding"`) and any `artists` query param SHALL be ignored until onboarding is complete
