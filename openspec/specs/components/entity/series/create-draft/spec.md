# Series.CreateDraft

## Purpose

Stores a new first-party Series together with its Events, each DRAFT and each a Concert with the given performers.

## Requirements

### Requirement: Draft stored whole

CreateDraft SHALL store the first-party Series with its Organizer, title, type, source page, description and visibility, and its Events, each DRAFT, each with its per-account limit, 4 when none is given, and each a Concert with the given performers, all together or none of them. It SHALL fail with InvalidArgument when a per-account limit breaks the Event rules, and with FailedPrecondition when a referenced Organizer, Venue or Artist does not exist.

#### Scenario: Draft with two events
- **WHEN** a draft with two events and one performer is created, one event with a per-account limit of 2 and one without
- **THEN** the Series and two DRAFT Events, each with the performer, are stored, with per-account limits of 2 and 4

#### Scenario: Limit above one admission code
- **WHEN** an event is given a per-account limit of 11
- **THEN** CreateDraft fails with InvalidArgument and stores nothing

#### Scenario: Unknown venue
- **WHEN** an event refers to a Venue that does not exist
- **THEN** CreateDraft fails with FailedPrecondition and stores nothing
