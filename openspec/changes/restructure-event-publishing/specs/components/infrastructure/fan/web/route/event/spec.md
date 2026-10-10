# Spec Delta

## MODIFIED Requirements

### Requirement: Cancelled event

When the Event is CANCELLED, the Event page SHALL show a banner stating that the concert is 中止 (cancelled), that tickets are no longer sold and that purchased tickets are refunded, together with a link to the performing Artist's other concerts; it SHALL show no sale in the ticket section. The other dates of the same Series SHALL keep their own state: a PUBLISHED date shows no banner.

#### Scenario: Shared link after cancellation

- **WHEN** a fan opens the link of an event that was cancelled, on its own or with its whole Series
- **THEN** the page shows the event with the 中止 banner, the refund notice and the link to the artist's other concerts, and nothing is offered for sale

#### Scenario: Other date of a partly cancelled tour

- **WHEN** a fan opens the link of a PUBLISHED event whose Series has another, CANCELLED event
- **THEN** the page shows no 中止 banner, and the cancelled date is marked 中止 among the dates
