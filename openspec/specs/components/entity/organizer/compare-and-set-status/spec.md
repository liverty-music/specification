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
