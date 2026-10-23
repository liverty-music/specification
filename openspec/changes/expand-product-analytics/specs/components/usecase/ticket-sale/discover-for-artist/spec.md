## ADDED Requirements

### Requirement: Each search reports its outcome

Every run of DiscoverForArtist that calls SearchPublishedSales SHALL send one "ticket sale search completed" signal for product analytics, under the trace of that run, carrying the artist, the number of series searched, the number of sales returned, and the number newly stored. A failed search SHALL send the signal with the outcome failed. A failure to send it SHALL NOT change the run.

#### Scenario: One new sale
- **WHEN** the search returns 2 sales for 3 series and 1 of them is newly stored
- **THEN** one signal is sent with 3 series, 2 returned and 1 new
