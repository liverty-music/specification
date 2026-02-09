## ADDED Requirements

### Requirement: YouTube Data Import
The system SHALL support importing music-related data from the user's YouTube account via the Google OAuth 2.0 flow.

#### Scenario: Successful YouTube history fetch
- **WHEN** the user provides the `https://www.googleapis.com/auth/youtube.readonly` scope
- **THEN** the system SHALL retrieve the user's subscribed channels and liked videos

### Requirement: AI-Powered Artist Inference
The system SHALL use Gemini to extract and normalize artist names from unstructured YouTube engagement data.

#### Scenario: Filtering non-music content
- **WHEN** the system processes a list of YouTube channel names and video titles
- **THEN** the system SHALL output a clean list of music artists, excluding vloggers, gamers, and other non-music entities

### Requirement: Interactive Follow Flow
The system SHALL provide a multi-step UI flow where users can confirm suggested artists and discover related performers.

#### Scenario: Real-time suggestion feedback
- **WHEN** the user follows a suggested artist
- **THEN** the system SHALL immediately provide a list of similar artists based on the user's latest actions
