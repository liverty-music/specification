## ADDED Requirements

### Requirement: Activation is announced with the change

When CompareAndSetStatus moves an Organizer from provisioning to active, it SHALL announce the Organizer as created, carrying it in status active, together with the change: both are stored or neither is. Any other change of status, and a call that changes nothing, SHALL announce nothing. When the announcement cannot be recorded, CompareAndSetStatus SHALL fail with Unavailable and the Organizer SHALL stay provisioning.

#### Scenario: Organizer activated

- **WHEN** a provisioning Organizer is moved from provisioning to active
- **THEN** one Organizer creation is announced, carrying the Organizer as active

#### Scenario: Status changed meanwhile

- **WHEN** an Organizer that is already deactivated is moved from provisioning to active
- **THEN** CompareAndSetStatus reports false and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** a provisioning Organizer is moved to active and the announcement cannot be recorded
- **THEN** CompareAndSetStatus fails with Unavailable and the Organizer stays provisioning
