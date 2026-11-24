## MODIFIED Requirements

### Requirement: Reviews carry the reviewer

Approve SHALL pass the ConcertCandidate id, the requested resolution — keep the existing Event, adopt the candidate, or none — the admin area (a code or a name) and the time zone the admin gave, each if any, and the caller's identity as reviewer to ConcertCandidateUseCase.Approve, and SHALL return the duplicate conflict the usecase reports, if any. Reject SHALL pass the ConcertCandidate id, the reason and the caller's identity as reviewer to ConcertCandidateUseCase.Reject.

#### Scenario: Approve without a resolution

- **WHEN** an admin approves a ConcertCandidate that collides with an existing Event without giving a resolution
- **THEN** the response carries the duplicate conflict and nothing is published

#### Scenario: Reject records the reviewer

- **WHEN** an admin rejects a ConcertCandidate with a reason
- **THEN** the rejection is recorded with that reason and that admin as reviewer

#### Scenario: Approve with an area and a time zone

- **WHEN** an admin approves a ConcertCandidate with the area "California" and the time zone America/Los_Angeles
- **THEN** ConcertCandidateUseCase.Approve receives the area "California" and the time zone America/Los_Angeles

### Requirement: Concert candidate requests are validated at the boundary

Approve and Reject SHALL fail with InvalidArgument when no ConcertCandidate id (`concert_candidate_id`) is given; Reject SHALL fail with InvalidArgument when the reason is empty. Approve SHALL fail with InvalidArgument when a given admin area is empty or longer than 100 characters.

#### Scenario: Reject without a reason

- **WHEN** an admin calls Reject with an empty reason
- **THEN** it fails with InvalidArgument and nothing is rejected

#### Scenario: Area text too long

- **WHEN** an admin calls Approve with an admin area of 101 characters
- **THEN** it fails with InvalidArgument and nothing is published

## ADDED Requirements

### Requirement: A listed concert candidate carries its area, time zone and resolved place

List SHALL return each ConcertCandidate with its admin area as discovered, its time zone and its resolved place id, each absent when the ConcertCandidate has none, and with no venue name or coordinates read from the map catalog.

#### Scenario: Candidate with a resolved place

- **WHEN** a ConcertCandidate in JP-13 with time zone Asia/Tokyo and resolved place id P is listed
- **THEN** it is returned with JP-13, Asia/Tokyo and P

#### Scenario: Candidate without an area

- **WHEN** a ConcertCandidate staged without an admin area, a time zone or a resolved place is listed
- **THEN** it is returned without an admin area, a time zone or a resolved place id
