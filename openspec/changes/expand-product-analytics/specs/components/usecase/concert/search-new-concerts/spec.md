## ADDED Requirements

### Requirement: Each search reports its outcome

Every run of SearchNewConcerts that performs the external search SHALL send one "concert search completed" signal for product analytics, under the trace of that search, carrying the Artist, what started it (the daily run, a first follow, or by hand), the outcome (failed, nothing new, or new concerts found) and the numbers of series and events it announced. A run that returns before the external search sends no signal. A failure to send it SHALL NOT change the outcome.

#### Scenario: Nothing new
- **WHEN** the daily run searches an Artist and every event found is already known
- **THEN** one signal is sent with the outcome nothing new and 0 announced events

#### Scenario: Search failed
- **WHEN** the external search fails with an error
- **THEN** one signal is sent with the outcome failed
