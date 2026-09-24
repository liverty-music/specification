# OrganizerUseCase.Deactivate

## Purpose

OrganizerUseCase.Deactivate turns an Organizer off at an admin's request: its operators can no longer sign in, its Artists are released for re-association, and the Organizer becomes deactivated.

## Requirements

### Requirement: Deactivate turns off operators, frees Artists, then marks the Organizer

Deactivate SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist. When the Organizer has a tenant link, it SHALL turn off its operators through Organizer.DeactivateOperators; an Organizer still provisioning without a tenant link skips this step. It SHALL then release its roster through Organizer.FreeArtists and set its status to deactivated through Organizer.SetStatus. The tenant itself is kept.

#### Scenario: Active Organizer is deactivated

- **WHEN** an active Organizer that represents Artists is deactivated
- **THEN** its operators can no longer sign in, its Artists can be associated with another Organizer, and its status is deactivated

#### Scenario: Provisioning Organizer without a tenant

- **WHEN** an Organizer that is provisioning and has no tenant link is deactivated
- **THEN** its Artists are freed and its status becomes deactivated

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Deactivate fails with NotFound

### Requirement: Deactivate is idempotent

Deactivate SHALL succeed and change nothing when the Organizer is already deactivated.

#### Scenario: Already deactivated

- **WHEN** a deactivated Organizer is deactivated again
- **THEN** Deactivate succeeds and nothing changes

### Requirement: A failed step leaves the Organizer undeactivated for a retry

When turning off the operators or freeing the Artists fails, Deactivate SHALL fail with that error and SHALL NOT set the status to deactivated, so calling it again completes the deactivation.

#### Scenario: Operators cannot be turned off

- **WHEN** Organizer.DeactivateOperators fails
- **THEN** Deactivate fails, the Artists stay represented and the status is unchanged

#### Scenario: Retry after a failure

- **WHEN** Deactivate is called again after a failed attempt
- **THEN** the Organizer is deactivated
