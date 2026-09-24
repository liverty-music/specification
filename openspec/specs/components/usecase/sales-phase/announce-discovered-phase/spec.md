# Announce Discovered Phase

## Purpose

AnnounceDiscoveredPhase tells every fan who is tracking a series that a new ticket sales phase has been published for it. It runs once for each newly created sales phase and sends each recipient a short, generic message in their language that links to the series.

## Requirements

### Requirement: Runs once for each newly created sales phase

AnnounceDiscoveredPhase SHALL run when DiscoverForArtist requests the announcement of a sales phase it has just created, with that phase and its series as input. A request without a series SHALL be ignored without an error.

#### Scenario: New phase created

- **WHEN** DiscoverForArtist creates a sales phase for a series
- **THEN** AnnounceDiscoveredPhase runs once for that phase

#### Scenario: Request without a series

- **WHEN** AnnounceDiscoveredPhase receives a request that names no series
- **THEN** nothing is announced and it succeeds

### Requirement: The audience is the fans tracking the series

AnnounceDiscoveredPhase SHALL announce the phase to exactly the fans returned by TicketJourney.ListUserIDsTrackingSeries for the phase's series, and to nobody else; when that list is empty it SHALL succeed without announcing. A fan whose profile cannot be read SHALL be skipped and the others SHALL still be announced to.

#### Scenario: Tracking fan

- **WHEN** ListUserIDsTrackingSeries returns a fan for the series
- **THEN** the fan receives the announcement

#### Scenario: Nobody tracking

- **WHEN** ListUserIDsTrackingSeries returns no fan
- **THEN** nothing is announced and AnnounceDiscoveredPhase succeeds

#### Scenario: Profile unreadable

- **WHEN** one of two tracking fans' profile cannot be read
- **THEN** the other fan still receives the announcement

### Requirement: The announcement is generic and links to the series

Each recipient's announcement SHALL have a title and a text in the recipient's preferred language, Japanese for `ja` and English for any other or no language, and SHALL name neither the artist, the tour, the channel nor a time. It SHALL link to the series page, even when the phase has its own url; the link and the grouping tag do not depend on the language. Repeated deliveries of the same phase's announcement SHALL replace each other on the device.

#### Scenario: Japanese-speaking fan

- **WHEN** the recipient's preferred language is `ja`
- **THEN** the title is チケット販売情報の新着 and the text says new ticket sales information has been published

#### Scenario: Other language

- **WHEN** the recipient's preferred language is `fr` or not set
- **THEN** the title is New Ticket Sales Phase and the text is in English

#### Scenario: Phase with an application url

- **WHEN** the phase has an application url
- **THEN** the announcement still links to the series page

### Requirement: The announcement is sent immediately

AnnounceDiscoveredPhase SHALL send the announcement as soon as it runs, whatever the recipient's local time; quiet hours SHALL NOT apply.

#### Scenario: Late evening

- **WHEN** AnnounceDiscoveredPhase runs at 23:00 in a recipient's time zone
- **THEN** the recipient is sent the announcement at once

### Requirement: One sales-phase announcement notification per recipient

For each recipient AnnounceDiscoveredPhase SHALL issue one notification of type sales-phase announcement carrying that recipient's message. Whether it reaches the recipient's devices does not change the result. When a recipient's notification cannot be recorded, AnnounceDiscoveredPhase SHALL fail so the whole announcement runs again; recipients already sent may then receive it again, and the repeat replaces the earlier one on their device. The story stories/hear-about-a-new-ticket-sale covers the whole flow from discovery to the fan's device.

#### Scenario: Two recipients

- **WHEN** two fans track the series
- **THEN** one sales-phase announcement notification is created for each of them

#### Scenario: Recording fails

- **WHEN** the second of three recipients' notifications cannot be recorded
- **THEN** AnnounceDiscoveredPhase fails and runs again for all three recipients
