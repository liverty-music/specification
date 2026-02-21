## MODIFIED Requirements

### Requirement: Search Concerts by Artist

System must provide a way to search for future concerts of a specific artist using generative AI grounding. Error returns SHALL include contextual wrapping indicating which operation failed.

#### Scenario: Successful Search with known official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has a persisted official site record
- **THEN** the system returns a list of upcoming concerts found on the web
- **AND** each concert includes title, venue, date, and start time
- **AND** results exclude concerts that are already stored in the database

#### Scenario: Successful Search without official site

- **WHEN** `SearchNewConcerts` is called for an existing artist
- **AND** the artist has no persisted official site record
- **THEN** the system SHALL still perform the external search using the artist name
- **AND** return a list of upcoming concerts if found
- **AND** NOT return an error solely because the official site is missing

#### Scenario: Filter Past Events

- **WHEN** the search results include events with dates in the past
- **THEN** the system must filter them out and only return future events

#### Scenario: No Results

- **WHEN** no upcoming concerts are found for the artist
- **THEN** the system returns an empty list without error

#### Scenario: Error context in failures

- **WHEN** any internal operation fails (get artist, list existing concerts, search external API)
- **THEN** the error SHALL be wrapped with `fmt.Errorf` indicating which step failed
- **AND** the original error SHALL be preserved via `%w` verb
