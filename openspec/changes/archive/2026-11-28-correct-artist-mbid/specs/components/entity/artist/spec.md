## ADDED Requirements

### Requirement: One MBID names one artist
An MBID SHALL be the MBID or among the other_mbids of at most one Artist, and an Artist's other_mbids SHALL not hold its own MBID. An Artist found under an MBID it was corrected from is the same Artist, with the same id.

#### Scenario: Corrected artist keeps its identity
- **WHEN** an artist's MBID is corrected from A to B
- **THEN** looking it up by A or by B finds the same artist, with the same id and followers

#### Scenario: One owner per MBID
- **WHEN** MBID A is among the other_mbids of one artist
- **THEN** no other artist has A as its MBID or among its other_mbids
