# intel Specification

## Purpose

The `intel` capability provides automated gathering and processing of live performance information (concerts, tickets) from artist websites. It utilizes AI-driven crawling via Vertex AI Search and structured data extraction with Gemini to maintain a comprehensive and up-to-date database of music events without manual scraping.

## Requirements

### Requirement: Live Information Crawling

The system SHALL crawl live information from artist websites using Vertex AI Search.

#### Scenario: Crawl UVERworld schedule

Given the target artist is "UVERworld"
When the intel CLI is run
Then it should query Vertex AI Search for "UVERworld live schedule"
And parse the results to JSON.
