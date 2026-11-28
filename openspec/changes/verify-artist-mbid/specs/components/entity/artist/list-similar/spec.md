## MODIFIED Requirements

### Requirement: ListSimilar returns the catalog's similar artists
ListSimilar SHALL return the artists the listening service lists as similar to the given artist, identified by its listening_mbid, in the service's order, each with a name and, when the service knows it, an MBID. When the limit is greater than 0 it SHALL return at most that many artists; when the limit is 0 the service's default number applies (TODO(threshold)). When the service lists none, ListSimilar SHALL return an empty list.

#### Scenario: Limit given
- **WHEN** ListSimilar is called with a limit of 10
- **THEN** it returns at most 10 artists

#### Scenario: No limit
- **WHEN** ListSimilar is called with a limit of 0
- **THEN** it returns the catalog's default number of artists

#### Scenario: No similar artists
- **WHEN** the catalog lists no similar artist
- **THEN** ListSimilar returns an empty list

#### Scenario: Corrected artist
- **WHEN** ListSimilar is called for an artist whose listening_mbid is A and whose mbid was corrected to B
- **THEN** the listening service is asked for the artists similar to A
