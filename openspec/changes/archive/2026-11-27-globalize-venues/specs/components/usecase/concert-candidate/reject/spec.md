## MODIFIED Requirements

### Requirement: Reject logs and drops

Reject SHALL record the ConcertCandidate in the RejectedConcert (RejectedConcert.Append) with its details as discovered, its resolved place id and time zone, the Artist's current name, the reason and the reviewing admin's identity when known, and then remove it (ConcertCandidate.Delete). When the Artist cannot be read, Reject SHALL fail and change nothing.

#### Scenario: Reject with a reason
- **WHEN** an admin rejects a ConcertCandidate with reason "wrong artist"
- **THEN** a RejectedConcert entry with that reason exists and the ConcertCandidate is gone
