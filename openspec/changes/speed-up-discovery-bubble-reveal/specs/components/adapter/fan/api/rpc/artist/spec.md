## MODIFIED Requirements

### Requirement: Artist requests are validated at the boundary
The boundary SHALL fail with InvalidArgument, before any usecase runs, when:
- Create has no name, an empty name, or an MBID that is not a UUID;
- Search has an empty query;
- ListSimilar has no artist id, an artist id that is not a UUID, or a limit outside 0 to 50;
- ListTop has a tag longer than 50 characters or a limit outside 0 to 100.

#### Scenario: Empty search query
- **WHEN** Search is called with an empty query
- **THEN** it fails with InvalidArgument and no catalog lookup is made

#### Scenario: Limit too large
- **WHEN** ListTop is called with a limit of 101
- **THEN** it fails with InvalidArgument

#### Scenario: Similar-artist limit too large
- **WHEN** ListSimilar is called with a limit of 51
- **THEN** it fails with InvalidArgument and no usecase runs

#### Scenario: Malformed MBID
- **WHEN** Create is called with an MBID that is not a UUID
- **THEN** it fails with InvalidArgument and no artist is created
