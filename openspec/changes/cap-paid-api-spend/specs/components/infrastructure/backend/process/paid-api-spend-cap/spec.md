## Purpose

The hard limits on paid external services that every backend process in production runs under, so that a bug that calls a paid service in a loop can cost no more than a bounded amount.

## ADDED Requirements

### Requirement: Daily request limits on the map catalog

In production, the map catalog SHALL accept at most 1,000 text searches, 100 place detail reads and 100 autocomplete requests per day across all backend processes, and no request of any other kind. The day resets at midnight Pacific Time. A Venue.SearchPlace or Venue.SearchPlaces call refused because a limit is reached SHALL fail with ResourceExhausted. The next day's calls SHALL succeed again without any manual step.

#### Scenario: Text searches beyond the daily limit

- **WHEN** 1,000 text searches have been made in production since midnight Pacific Time and a backend process calls Venue.SearchPlace
- **THEN** the call fails with ResourceExhausted and the catalog bills nothing for it

#### Scenario: Next day after the limit

- **WHEN** the text search limit was reached yesterday and a backend process calls Venue.SearchPlace after midnight Pacific Time
- **THEN** the call is served as usual

#### Scenario: Unused request kind

- **WHEN** a backend process sends the map catalog a request of a kind other than text search, place detail read or autocomplete
- **THEN** the request is refused and billed nothing

### Requirement: Monthly spend cap on generative AI

In production, the gross usage cost of the generative AI service, before any credits, SHALL be capped at ¥4,000 per calendar month. Once usage costs reach the cap, the service SHALL refuse calls from every backend process until the next calendar month begins or an admin lifts the cap. A concert search or ticket-sale search whose call is refused SHALL store no Concert and no TicketSale from it.

#### Scenario: Cap reached mid-month

- **WHEN** the generative AI usage cost of the month reaches ¥4,000 and the daily concert search runs
- **THEN** the service refuses each search call and no Concert or TicketSale is stored from the run

#### Scenario: New month after the cap

- **WHEN** the cap was reached in October and the daily concert search runs on November 1
- **THEN** the searches are served as usual

### Requirement: Project spend alerts

In production, the owner SHALL be notified by email when the month's total usage cost across all services reaches 50%, 90% and 100% of ¥10,000, and when the month's generative AI usage cost reaches 50%, 80% and 100% of its cap.

#### Scenario: Half of the project budget

- **WHEN** the month's total usage cost passes ¥5,000
- **THEN** the owner receives one email for the 50% threshold
