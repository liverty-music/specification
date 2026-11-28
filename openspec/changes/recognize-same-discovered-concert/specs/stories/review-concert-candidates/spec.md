## RENAMED Requirements

- FROM: `### Requirement: Rejection is not permanent`
- TO: `### Requirement: Only a corrected listing is reviewed again`

## MODIFIED Requirements

### Requirement: Concert candidates are reviewed through the queue

A concert staged by ConcertCreationUseCase.CreateFromDiscovered SHALL appear in ConcertCandidateUseCase.List until ConcertCandidateUseCase.Approve or ConcertCandidateUseCase.Reject removes it, and SHALL appear in no fan-facing list meanwhile.

#### Scenario: Approve publishes
- **WHEN** an admin approves a ConcertCandidate with no collision
- **THEN** it leaves the queue and is a Concert in the catalog under its Series

#### Scenario: Duplicate reconciled
- **WHEN** an admin approves a colliding ConcertCandidate of the existing Concert's Artist, sees the conflict, and approves again choosing keep existing
- **THEN** it leaves the queue, the existing Concert keeps its venue name and times, a RejectedConcert entry records it, and the next discovery under the candidate's venue name stages nothing

#### Scenario: Shared bill reconciled
- **WHEN** an admin approves a ConcertCandidate of one Artist that collides with another Artist's Concert, and approves again choosing keep existing
- **THEN** it leaves the queue, the existing Concert lists both Artists as performers, and the candidate's Artist's followers are told about it

### Requirement: Only a corrected listing is reviewed again

A concert an admin settled with ConcertCandidateUseCase.Reject, or with ConcertCandidateUseCase.Approve choosing keep existing, SHALL not be staged again by ConcertUseCase.SearchNewConcerts while it is found with the same listing (see RejectedConcert, "Same listing"). Found with any other listing, it SHALL be handled like any new discovery by ConcertCreationUseCase.CreateFromDiscovered.

#### Scenario: Rejected concert found again
- **WHEN** a rejected concert whose venue could not be resolved is found again with the same venue name, date and start time
- **THEN** no ConcertCandidate is staged for it

#### Scenario: Rejected concert found with a corrected listing
- **WHEN** a rejected concert with no start time is found again at a resolvable venue with a free slot, now starting at 19:00
- **THEN** it is published as a Concert
