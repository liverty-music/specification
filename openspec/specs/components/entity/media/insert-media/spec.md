# Media.InsertMedia

## Purpose

Records an uploaded Media for its Organizer.

## Requirements

### Requirement: Idempotent insert

InsertMedia SHALL store the Media, and SHALL succeed without change when a Media with the same id is already stored.

#### Scenario: Repeated attach
- **WHEN** the same Media id is inserted twice
- **THEN** one Media is stored and both calls succeed
