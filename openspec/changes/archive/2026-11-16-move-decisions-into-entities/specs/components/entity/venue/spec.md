## ADDED Requirements

### Requirement: Same listed venue

Two listed venue names SHALL name the same venue when their normalized forms (see "Listed venue name normalization") are equal once whitespace, middle-dot variants and Latin letter case are ignored. No other rule, such as a list of renamed venues or a prefecture in parentheses, SHALL make two names the same. Every comparison of two listed venue names (an Event's, a ConcertCandidate's, a discovered event's and a found place's name) SHALL use this rule; a stored lookup by listed venue name (Venue.GetByListedName) is not a comparison of two names and keeps its exact match.

#### Scenario: Spacing differs
- **WHEN** the names are "渋谷CLUB QUATTRO" and "渋谷 CLUB QUATTRO"
- **THEN** they name the same venue

#### Scenario: Letter case differs
- **WHEN** the names are "Zepp Haneda" and "ZEPP HANEDA"
- **THEN** they name the same venue

#### Scenario: Middle dot differs
- **WHEN** the names are "東京文化会館・大ホール" and "東京文化会館 大ホール"
- **THEN** they name the same venue

#### Scenario: Different venues
- **WHEN** the names are "Zepp Haneda" and "Zepp Namba"
- **THEN** they do not name the same venue
