# Live Information Intelligence

## ADDED Requirements


### Requirement: Live Information Crawling
The system SHALL crawl live information from artist websites using Vertex AI Search.

#### Scenario: Crawl UVERworld schedule
Given the target artist is "UVERworld"
When the intel CLI is run
Then it should query Vertex AI Search for "UVERworld live schedule"
And parse the results to JSON.
