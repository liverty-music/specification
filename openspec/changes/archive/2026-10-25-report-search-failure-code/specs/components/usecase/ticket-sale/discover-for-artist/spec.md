## MODIFIED Requirements

### Requirement: Each search reports its outcome

Every run of DiscoverForArtist that calls SearchPublishedSales SHALL send one "ticket sale search completed" signal for product analytics, under the trace of that run, carrying the artist, the number of series searched, the number of sales returned, and the number newly stored. A failed search SHALL send the signal with the outcome failed and the kind of error that failed it (such as deadline exceeded, unavailable or permission denied), or unknown when the error states no kind, and SHALL NOT carry the error's message. A failure to send it SHALL NOT change the run.

#### Scenario: One new sale
- **WHEN** the search returns 2 sales for 3 series and 1 of them is newly stored
- **THEN** one signal is sent with 3 series, 2 returned and 1 new

#### Scenario: Search failed for a spent quota
- **WHEN** the search fails because the external service refused it for a spent quota
- **THEN** one signal is sent with the outcome failed and the error kind permission denied
