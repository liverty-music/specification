# Welcome Dashboard Preview

## Purpose

Displays an interactive, read-only dashboard preview on the Welcome page using live concert data from a curated popular-artist fallback list, giving new users a tangible preview of what they will build during onboarding.

## Requirements

### Requirement: Live Dashboard Preview on Welcome Page

The system SHALL display an interactive, read-only dashboard preview on the Welcome page using live concert data from a curated popular-artist fallback list.

#### Scenario: Preview loads with live data

- **WHEN** the Welcome page renders
- **THEN** the system SHALL fetch concert data for a curated list of popular Japanese artists (e.g., Mrs. GREEN APPLE, YOASOBI, Vaundy, Super Beaver, King Gnu, Official髭男dism, Ano, and others — at least 10 artists)
- **AND** the system SHALL display the real dashboard lane component with the fetched data
- **AND** the preview SHALL be scrollable

#### Scenario: Fallback when artist has no concerts

- **WHEN** a curated artist has no upcoming concerts in the database
- **THEN** that artist SHALL be excluded from the preview data
- **AND** the system SHALL continue fetching from the remaining list until at least 3 concerts are displayable

#### Scenario: Preview is read-only

- **WHEN** the user interacts with concert cards in the preview
- **THEN** tapping a card SHALL NOT navigate or open a detail sheet
- **AND** the preview SHALL serve as a visual demonstration only

#### Scenario: Guest-friendly copy shown alongside preview

- **WHEN** the Welcome page renders
- **THEN** the page SHALL display the text "アカウント不要でお試しいただけます" near the CTA buttons
