## ADDED Requirements

### Requirement: YouTube Activity Inference
The system SHALL support inferring interest in music artists from raw YouTube account activity (channel names, video titles).

#### Scenario: Inferring artists from channel names
- **WHEN** provided with a list of YouTube channel names
- **THEN** the system SHALL return a clean list of music artists and their associated MBIDs by matching against the local database or external metadata providers

### Requirement: Google Search Grounding for Live Info
The system SHALL use Gemini with Google Search grounding to discover upcoming live information (dates, venues, ticket links) from the public web.

#### Scenario: Grounding search for tour dates
- **WHEN** searching for "UVERworld 2026 tour dates"
- **THEN** the system SHALL return a structured list of upcoming concerts parsed from search results
