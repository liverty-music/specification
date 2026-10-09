# Spec Delta

## MODIFIED Requirements

### Requirement: Deactivate turns off operators, frees Artists, then marks the Organizer

Deactivate SHALL load the Organizer through Organizer.Get, failing with NotFound when it does not exist. It SHALL turn off the operators of its tenant through Organizer.DeactivateOperators. The tenant is its tenant link or, when none is recorded, the tenant found through Organizer.FindTenantOrg; the step is skipped only when FindTenantOrg reports NotFound. It SHALL then release its roster through Organizer.FreeArtists and set its status to deactivated through Organizer.SetStatus. The tenant itself is kept.

#### Scenario: Active Organizer is deactivated

- **WHEN** an active Organizer that represents Artists is deactivated
- **THEN** its operators can no longer sign in, its Artists can be associated with another Organizer, and its status is deactivated

#### Scenario: Provisioning Organizer without a tenant

- **WHEN** an Organizer that is provisioning has no tenant link and no tenant has its name
- **THEN** its Artists are freed and its status becomes deactivated

#### Scenario: Unlinked tenant

- **WHEN** an Organizer that is provisioning has no tenant link but a tenant with its name exists
- **THEN** that tenant's operators are turned off and the Organizer becomes deactivated

#### Scenario: Unknown Organizer

- **WHEN** no Organizer has the id
- **THEN** Deactivate fails with NotFound
