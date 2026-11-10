# Organizer.CompareAndSetStatus

## Purpose

Moves an Organizer from one expected status to another in one step, and reports whether it did.

## Requirements

### Requirement: CompareAndSetStatus changes the status only from the expected status

CompareAndSetStatus SHALL set the Organizer's status to the target status only when its current status is the expected status, checking and setting as one indivisible step, and SHALL report whether it changed the status. When the current status is not the expected one, or the Organizer does not exist, it SHALL change nothing and report false without failing.

#### Scenario: Status is as expected

- **WHEN** a provisioning Organizer is moved from provisioning to active
- **THEN** its status becomes active and CompareAndSetStatus reports true

#### Scenario: Status changed meanwhile

- **WHEN** an Organizer that is already deactivated is moved from provisioning to active
- **THEN** it stays deactivated and CompareAndSetStatus reports false

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** CompareAndSetStatus reports false and changes nothing

### Requirement: Activation is announced with the change

When CompareAndSetStatus moves an Organizer from provisioning to active, it SHALL announce the Organizer as activated (Organizer.Activated), carrying it in status active, together with the change: both are stored or neither is. Any other change of status, and a call that changes nothing, SHALL announce nothing. When the announcement cannot be recorded, CompareAndSetStatus SHALL fail with Unavailable and the Organizer SHALL stay provisioning.

#### Scenario: Organizer activated

- **WHEN** a provisioning Organizer is moved from provisioning to active
- **THEN** the Organizer is announced once as activated, carrying it as active

#### Scenario: Status changed meanwhile

- **WHEN** an Organizer that is already deactivated is moved from provisioning to active
- **THEN** CompareAndSetStatus reports false and nothing is announced

#### Scenario: Announcement cannot be recorded

- **WHEN** a provisioning Organizer is moved to active and the announcement cannot be recorded
- **THEN** CompareAndSetStatus fails with Unavailable and the Organizer stays provisioning
