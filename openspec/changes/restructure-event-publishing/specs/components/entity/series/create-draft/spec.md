# Spec Delta

## MODIFIED Requirements

### Requirement: Draft stored whole

CreateDraft SHALL store the first-party Series with its organizer, title, type, source page, description and visibility, and its Events, each DRAFT and each with the given performers, all together or none of them. It SHALL fail with FailedPrecondition when a referenced Organizer, Venue or Artist does not exist.

#### Scenario: Draft with two events
- **WHEN** a draft with two events and one performer is created
- **THEN** the Series and two DRAFT Events, each with the performer, are stored

#### Scenario: Unknown venue
- **WHEN** an event refers to a Venue that does not exist
- **THEN** CreateDraft fails with FailedPrecondition and stores nothing
