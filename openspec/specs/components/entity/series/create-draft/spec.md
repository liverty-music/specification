# Series.CreateDraft

## Purpose

Stores a new first-party Series in DRAFT together with its DraftEvents and draft performers.

## Requirements

### Requirement: Draft stored whole

CreateDraft SHALL store the Series as DRAFT with its organizer, title, type, source page, description and visibility, its DraftEvents and its draft performers, all together or none of them. It SHALL fail with FailedPrecondition when a referenced Organizer, Venue or Artist does not exist.

#### Scenario: Draft with two events
- **WHEN** a draft with two DraftEvents and one performer is created
- **THEN** the DRAFT Series, both DraftEvents and the performer are stored

#### Scenario: Unknown venue
- **WHEN** a DraftEvent refers to a Venue that does not exist
- **THEN** CreateDraft fails with FailedPrecondition and stores nothing
