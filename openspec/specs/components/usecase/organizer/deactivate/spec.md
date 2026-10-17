# OrganizerUseCase.Deactivate

## Purpose

OrganizerUseCase.Deactivate turns an Organizer off at an admin's request: its members can no longer sign in, its Artists are released for re-association, and the Organizer becomes deactivated.

## Requirements

### Requirement: Deactivate turns off identities, frees Artists, then marks the Organizer

Deactivate SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist. It SHALL turn off the identities in its Organization through Organization.DeactivateIdentities. The Organization is the one its provider organizer ID names or, when none is recorded, the Organization found through Organization.GetByName; the step is skipped only when GetByName reports NotFound. It SHALL then release its roster through Organizer.FreeArtists and set its status to deactivated through Organizer.SetStatus. The Organization itself is kept.

#### Scenario: Active Organizer is deactivated

- **WHEN** an active Organizer that represents Artists is deactivated
- **THEN** its members can no longer sign in, its Artists can be associated with another Organizer, and its status is deactivated

#### Scenario: Provisioning Organizer without an Organization

- **WHEN** an Organizer that is provisioning has no provider organizer ID and no Organization has its name
- **THEN** its Artists are freed and its status becomes deactivated

#### Scenario: Unlinked Organization

- **WHEN** an Organizer that is provisioning has no provider organizer ID but an Organization with its name exists
- **THEN** that Organization's identities are turned off and the Organizer becomes deactivated

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Deactivate fails with NotFound

### Requirement: Deactivate is idempotent

Deactivate SHALL succeed and change nothing when the Organizer is already deactivated.

#### Scenario: Already deactivated

- **WHEN** a deactivated Organizer is deactivated again
- **THEN** Deactivate succeeds and nothing changes

### Requirement: A failed step leaves the Organizer undeactivated for a retry

When turning off the identities or freeing the Artists fails, Deactivate SHALL fail with that error and SHALL NOT set the status to deactivated, so calling it again completes the deactivation.

#### Scenario: Identities cannot be turned off

- **WHEN** Organization.DeactivateIdentities fails
- **THEN** Deactivate fails, the Artists stay represented and the status is unchanged

#### Scenario: Retry after a failure

- **WHEN** Deactivate is called again after a failed attempt
- **THEN** the Organizer is deactivated
