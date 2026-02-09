## ADDED Requirements

### Requirement: Cross-Platform Similarity Discovery
The system SHALL discover new artists related to a user's followed artists using external metadata providers (e.g., Last.fm).

#### Scenario: Fetching similar artists
- **WHEN** the system requests similar artists for a given artist ID
- **THEN** the system SHALL return a list of artists with high similarity scores from the metadata provider

### Requirement: AI-Driven Tour Discovery (Grounding)
The system SHALL support discovery of artist tour and live information from public web sources using LLM-based web grounding.

#### Scenario: Searching for tours not in DB
- **WHEN** the system identifies an artist with no upcoming live info in the local database
- **THEN** the system SHALL invoke Gemini with Google Search grounding to retrieve current tour dates and venues

### Requirement: Search Result Normalization
All discovered artist information SHALL be normalized to a consistent identity (MBID) before being presented to the user.

#### Scenario: Normalizing a search result
- **WHEN** a search or discovery result is returned from an external API
- **THEN** the system SHALL resolve the result to a unique MBID and check for existing records in the local database
