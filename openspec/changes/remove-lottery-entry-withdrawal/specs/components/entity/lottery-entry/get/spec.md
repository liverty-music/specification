## MODIFIED Requirements

### Requirement: Get by id

Get SHALL return the entry with the given id, in any state, and SHALL fail with NotFound when none exists.

#### Scenario: Existing entry

- **WHEN** Get is called with the id of a stored entry
- **THEN** that entry is returned

#### Scenario: Unknown id

- **WHEN** no entry has the id
- **THEN** Get fails with NotFound
