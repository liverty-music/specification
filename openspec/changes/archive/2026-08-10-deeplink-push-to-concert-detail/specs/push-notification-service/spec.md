## MODIFIED Requirements

### Requirement: Delivery scope limited to newly created concerts

When notifying followers about newly created concerts for an artist, the system SHALL use only the set of concerts that were just created in the triggering operation — not the artist's full upcoming schedule. Hype-level filtering, notification payload content, and delivery decisions SHALL all be computed against this new-concert set.

Furthermore, for each individual recipient the system SHALL narrow the new-concert set to the recipient's **hype-matched subset** — the new concerts that satisfy that recipient's hype-level predicate (`away`/`anywhere` → all; `home` → new concerts in the recipient's home area; `nearby` → new concerts within range of the recipient's home centroid). The notification body count and the deep-link target concert SHALL both be computed from this per-recipient matched subset, never from the unfiltered new-concert set.

#### Scenario: Home filter evaluated against new concerts only

- **WHEN** a new concert is created for an artist in admin area `JP-40`
- **AND** the artist also has pre-existing upcoming concerts in admin area `JP-13`
- **AND** a follower with `hype = home` whose home area is `JP-13` exists
- **THEN** the follower SHALL NOT receive a push notification
- **AND** filtering SHALL be computed from the set `{JP-40}`, never `{JP-40, JP-13}`

#### Scenario: Nearby filter evaluated against new concerts only

- **WHEN** a new concert is created for an artist at a venue 300 km from a follower's home centroid
- **AND** the artist also has pre-existing upcoming concerts within 200 km of that follower's home centroid
- **AND** the follower's hype level is `nearby`
- **THEN** the follower SHALL NOT receive a push notification
- **AND** proximity SHALL be computed from only the new concerts

#### Scenario: Notification count reflects the recipient's matched subset

- **WHEN** 2 new concerts are created for an artist that already has 10 upcoming concerts
- **AND** a follower with `hype = away` exists
- **THEN** the notification payload SHALL report the count as `2`
- **AND** the count SHALL NOT include the pre-existing upcoming concerts

#### Scenario: Home-hype count excludes out-of-area new concerts

- **WHEN** 3 new concerts are created for an artist — 1 in admin area `JP-13` and 2 in admin area `JP-40`
- **AND** a follower with `hype = home` whose home area is `JP-13` exists
- **THEN** the follower SHALL receive a push notification
- **AND** the notification payload SHALL report the count as `1`
- **AND** the count SHALL NOT include the 2 `JP-40` concerts that did not match the recipient's home area

#### Scenario: No delivery when zero concerts are newly created

- **WHEN** the concert creation operation completes with zero newly created concerts for an artist
- **THEN** the system SHALL NOT trigger the notification pipeline for that artist
- **AND** SHALL NOT publish a `CONCERT.created` event

## ADDED Requirements

### Requirement: New-concert notification deep-links to the earliest matched concert

The new-concert push notification payload SHALL carry a `data.url` that deep-links to a specific concert: the **earliest concert in the recipient's hype-matched subset**. "Earliest" SHALL be determined by concert local date ascending, tie-broken by start time ascending. The URL SHALL take the form `/concerts/<concertId>`, reusing the frontend's canonical concert-detail URL, and SHALL NOT carry a redundant artist filter query parameter (the artist is derivable from the concert).

#### Scenario: Deep-link targets the earliest matched concert

- **WHEN** a recipient's hype-matched subset for an artist contains concerts on 2026-09-10 and 2026-09-03
- **THEN** the notification payload `data.url` SHALL be `/concerts/<id-of-2026-09-03-concert>`

#### Scenario: Same-day matched concerts tie-broken by start time

- **WHEN** a recipient's hype-matched subset contains two concerts both dated 2026-09-03, starting at 18:00 and 19:30
- **THEN** the notification payload `data.url` SHALL point to the 18:00 concert

#### Scenario: Home recipient deep-links to their in-area concert, not the globally earliest

- **WHEN** new concerts are created for an artist — one in `JP-40` on 2026-09-01 and one in `JP-13` on 2026-09-05
- **AND** a follower with `hype = home` whose home area is `JP-13` exists
- **THEN** that follower's notification `data.url` SHALL point to the `JP-13` 2026-09-05 concert
- **AND** SHALL NOT point to the earlier `JP-40` concert that did not match the recipient's home area
