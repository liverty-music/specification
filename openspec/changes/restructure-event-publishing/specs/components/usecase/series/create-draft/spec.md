# Spec Delta

## MODIFIED Requirements

### Requirement: Draft stored as DRAFT

CreateDraft SHALL store the Series, owned by the caller's Organizer, with one DRAFT Event per event — a multi-showtime day being several Events — each with the performers (Series.CreateDraft), and SHALL return the Series with its Events and performers (Series.GetAuthored). Nothing SHALL be announced.

#### Scenario: Draft for a represented artist
- **WHEN** an operator creates a draft with one event naming a represented Artist
- **THEN** a Series owned by the Organizer with one DRAFT Event is returned and no fan list or notification shows it

#### Scenario: Two showtimes
- **WHEN** the draft has 13:00 and 18:00 events on one date at one venue
- **THEN** the Series has two DRAFT Events
