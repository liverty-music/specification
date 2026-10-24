## MODIFIED Requirements

### Requirement: Whole catalog, oldest first

List SHALL return every Concert in the catalog — past and upcoming, of every Series whatever its visibility, and CANCELLED ones included — ordered by local date ascending, each with its Venue, Series, performers and publish state. When an Artist is given, it SHALL return only the Concerts whose performers include that Artist, and an empty list when the Artist performs in none or no Artist has the id. ConcertCandidates and DRAFT Events are not Concerts and SHALL NOT be returned. An empty catalog SHALL yield an empty list.

#### Scenario: Cancelled Organizer concert included
- **WHEN** the catalog holds a CANCELLED Event of a first-party Series
- **THEN** List returns it as a CANCELLED Concert

#### Scenario: Concert candidate excluded
- **WHEN** a ConcertCandidate is pending review
- **THEN** List does not return it

#### Scenario: Empty catalog
- **WHEN** the catalog holds no Concert
- **THEN** List returns an empty list

#### Scenario: Draft event excluded
- **WHEN** a published Series has a DRAFT Event
- **THEN** List does not return the DRAFT Event

#### Scenario: Narrowed to one artist
- **WHEN** the Artist A performs in a PUBLISHED Concert of an UNLISTED Series and in a CANCELLED Concert, another Artist performs in a third Concert, and List is given A
- **THEN** only A's two Concerts are returned

#### Scenario: Artist without concerts
- **WHEN** List is given an Artist that performs in no Concert
- **THEN** List returns an empty list
