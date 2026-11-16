## RENAMED Requirements

- FROM: `### Requirement: Best match or NotFound`
- TO: `### Requirement: Places in order of relevance`

## MODIFIED Requirements

### Requirement: Places in order of relevance

SearchPlace SHALL return the places the catalog finds for the name and admin area, most relevant first, and SHALL return no place and no error when the catalog has no match. It SHALL fail with Unavailable when the catalog cannot be reached. It SHALL NOT choose among the places; Venue.SelectPlace does.

#### Scenario: Known venue
- **WHEN** "日本武道館" with JP-13 is searched
- **THEN** the places found are returned, each with its place id and canonical name, most relevant first

#### Scenario: No match
- **WHEN** the catalog has no match
- **THEN** no place is returned and there is no error
