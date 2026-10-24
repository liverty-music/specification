## ADDED Requirements

### Requirement: List narrows to one artist when asked

List SHALL accept an optional Artist id and fail with InvalidArgument, before any usecase runs, when one is given malformed. It SHALL run ConcertUseCase.List with the Artist when one is given, and without one otherwise; the Concerts come with their series and artists as on every List.

#### Scenario: Admin lists one artist's concerts

- **WHEN** a signed-in admin calls List with the id of an Artist who performs in one CANCELLED Concert
- **THEN** only that Concert is returned, with its Series and its Artists

#### Scenario: Malformed artist id

- **WHEN** an admin calls List with an Artist id that is not a UUID
- **THEN** it fails with InvalidArgument and nothing is read
