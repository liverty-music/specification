## MODIFIED Requirements

### Requirement: Each search reports its outcome

Every run of SearchNewConcerts that performs the external search SHALL send one "concert search completed" signal for product analytics, under the trace of that search, carrying the Artist, what started it (the daily run, a first follow, or by hand), the outcome (failed, nothing new, or new concerts found) and the numbers of series and events it announced. A failed search SHALL also carry the kind of error that failed it (such as deadline exceeded, unavailable or permission denied), or unknown when the error states no kind, and SHALL NOT carry the error's message. A run that returns before the external search sends no signal. A failure to send it SHALL NOT change the outcome.

#### Scenario: Nothing new
- **WHEN** the daily run searches an Artist and every event found is already known
- **THEN** one signal is sent with the outcome nothing new and 0 announced events

#### Scenario: Search failed
- **WHEN** the external search fails because the caller's deadline passed
- **THEN** one signal is sent with the outcome failed and the error kind deadline exceeded, and without the error's message

#### Scenario: Failure without a kind
- **WHEN** the external search fails with an error that states no kind
- **THEN** one signal is sent with the outcome failed and the error kind unknown
