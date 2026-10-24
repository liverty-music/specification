## MODIFIED Requirements

### Requirement: Whole catalog for admins

List SHALL take an optional Artist and return the result of Concert.List for it unchanged: the whole catalog when no Artist is given, and only that Artist's Concerts when one is given. ConcertCandidates SHALL be returned only by ListPending.

#### Scenario: Catalog and queue both populated
- **WHEN** the catalog holds Concerts and ConcertCandidates are pending
- **THEN** List returns only the Concerts

#### Scenario: Unlisted Organizer concert
- **WHEN** a Concert belongs to a PUBLISHED UNLISTED first-party Series
- **THEN** List returns it

#### Scenario: One artist's concerts
- **WHEN** List is given an Artist that performs in a CANCELLED Organizer Concert
- **THEN** List returns that Concert and no Concert the Artist does not perform in
