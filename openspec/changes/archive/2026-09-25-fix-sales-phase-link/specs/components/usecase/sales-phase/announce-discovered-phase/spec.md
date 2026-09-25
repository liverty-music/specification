# Announce Discovered Phase Delta

## MODIFIED Requirements

### Requirement: The announcement is generic and links to the series

Each recipient's announcement SHALL have a title and a text in the recipient's preferred language, Japanese for `ja` and English for any other or no language, and SHALL name neither the artist, the tour, the channel nor a time. It SHALL link to the concert page of the series' earliest upcoming Event, or its earliest Event when none is upcoming, even when the phase has its own url; when the series has no Event it SHALL link to the dashboard. The link and the grouping tag do not depend on the language. Repeated deliveries of the same phase's announcement SHALL replace each other on the device.

#### Scenario: Japanese-speaking fan

- **WHEN** the recipient's preferred language is `ja`
- **THEN** the title is チケット販売情報の新着 and the text says new ticket sales information has been published

#### Scenario: Other language

- **WHEN** the recipient's preferred language is `fr` or not set
- **THEN** the title is New Ticket Sales Phase and the text is in English

#### Scenario: Phase with an application url

- **WHEN** the phase has an application url
- **THEN** the announcement still links to the concert page of the series' earliest upcoming Event, not the phase's url

#### Scenario: No upcoming event

- **WHEN** every Event of the series is in the past
- **THEN** the announcement links to the concert page of the series' earliest Event

#### Scenario: Series with no event

- **WHEN** the series has no Event
- **THEN** the announcement links to the dashboard
