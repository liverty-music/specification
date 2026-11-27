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
